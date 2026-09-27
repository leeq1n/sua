"""
Self-Upgrade Agent 核心 —— 可被自主改进的推理引擎。

架构：
  agent.py   — 主推理循环 (run)
  tools.py   — 工具调用接口
  planner.py — 任务规划模块 (可被 patch 改进)

每个模块都是独立的 .py 文件，patchgen 可以单独修改任意模块。
"""
__version__ = "1.3.0"
import os, json, time
import importlib.util
from dataclasses import asdict
from pathlib import Path
from core.planner import plan_task
from typing import List, Dict, Optional, Callable



# ── 配置 ──────────────────────────────────────────
MAX_TURNS = 10
MAX_TOOL_CALLS = 5

# ── 工具注册表 ─────────────────────────────────────
_TOOLS: dict = {}

def register_tool(name: str, fn, description: str = ""):
    _TOOLS[name] = fn
    fn.__tool_description__ = description

def list_tools():
    return [{"name": n, "description": getattr(f, "__tool_description__", "")} for n, f in _TOOLS.items()]

def call_tool(name: str, *args, **kwargs):
    if name not in _TOOLS:
        return f"Tool '{name}' not registered. Available: {list(_TOOLS.keys())}"
    try:
        return str(_TOOLS[name](*args, **kwargs))
    except Exception as e:
        return f"Tool error: {e}"


# ── 推理循环 ────────────────────────────────────────

def run(
    task: str,
    llm_call: Callable,
    max_turns: int = MAX_TURNS,
    verbose: bool = False,
    *,
    control=None,
    review_action: Optional[Callable] = None,
    verify_completion: Optional[Callable] = None,
) -> Dict:
    """
    主推理循环：规划 → 执行 → 反思。
    
    返回值包含执行结果、耗时、步数等指标。
    """
    # Auto-register built-in tools
    from core.tools import tool_shell, tool_read_file, tool_calculate
    register_tool("shell", tool_shell, "Run a shell command")
    register_tool("read", tool_read_file, "Read a file")
    register_tool("calc", tool_calculate, "Evaluate a math expression")
    
    t0 = time.time()
    results = []

    # A controlled run plans from the active resident context, never from an
    # unbound raw prompt. The host supplies the reviewed criterion per action.
    planning_input = task
    bound_task_id = None
    if control is not None:
        from src.goal_control import DriftError
        context = control.working_context()
        if (review_action is None or context["goal"] is None
                or control.active_task_id not in context["tasks"]):
            raise DriftError("controlled run needs a HOT task and action reviewer")
        bound_task_id = control.active_task_id
        planning_input = json.dumps({
            "goal": asdict(context["goal"]),
            "tasks": {key: asdict(value) for key, value in context["tasks"].items()},
            "knowledge": context["knowledge"],
        }, ensure_ascii=False, sort_keys=True)

    # 1. 规划
    plan_result = plan_task(planning_input, llm_call)
    plan = plan_result.steps
    if verbose:
        print(f"  Plan: {len(plan)} steps")

    # 2. 执行
    success_count = 0
    execution_failure = False
    for i, step in enumerate(plan[: max_turns]):
        if verbose:
            print(f"  Step {i+1}: {step[:60]}")

        # 尝试使用工具
        tool_result = None
        tool_names = list(_TOOLS.keys())
        if tool_names and i < MAX_TOOL_CALLS:
            tool_prompt = (
                f"Task step: {step}\n"
                f"Available tools: {', '.join(tool_names)}\n"
                f"Reply with tool_name: args (or 'none' if no tool needed)"
            )
            tool_result = llm_call(tool_prompt)
            if tool_result and tool_result.lower() != "none":
                try:
                    parts = tool_result.split(":", 1)
                    name = parts[0].strip()
                    body = parts[1].strip() if len(parts) > 1 else ""
                    if name not in _TOOLS:
                        execution_failure = True
                        results.append({"step": step, "tool_used": None,
                                        "error": f"unknown tool: {name}"})
                        break
                    if control is not None:
                        action = json.dumps({"step": step, "tool": name, "query": body},
                                            ensure_ascii=False, sort_keys=True)
                        try:
                            criterion = review_action(action, control.working_context())
                            control.allow_action(bound_task_id, action, criterion)
                            control.record_action(action, bound_task_id, criterion)
                        except Exception as exc:
                            execution_failure = True
                            results.append({"step": step, "tool_used": None,
                                            "error": f"goal guard rejected action: {exc}"})
                            break
                    result = call_tool(name, body)
                    if verbose:
                        print(f"    Tool {name}: {str(result)[:60]}")
                    error_prefixes = ("Tool error:", "Shell error:", "Read error:",
                                      "Calc error:", "Write error:")
                    tool_failed = (str(result).startswith(error_prefixes)
                                   if control is not None else
                                   "error" in str(result).lower())
                    if not tool_failed:
                        success_count += 1
                    else:
                        execution_failure = True
                        results.append({"step": step, "tool_used": tool_result,
                                        "error": str(result)})
                        break
                except Exception as e:
                    if verbose:
                        print(f"    Tool error: {e}")
                    execution_failure = True
                    results.append({"step": step, "tool_used": tool_result,
                                    "error": str(e)})
                    break

            results.append({"step": step, "tool_used": tool_result if "tool_result" in dir() else None})

    execution_succeeded = (success_count > 0 and not execution_failure
                           and len(results) == len(plan))
    goal_complete = None
    if control is not None:
        current = control.working_context()
        if current["goal"] is None or bound_task_id not in current["tasks"]:
            execution_succeeded = False
        if execution_succeeded and verify_completion is not None:
            try:
                goal_complete = bool(verify_completion(current, results))
            except Exception:
                goal_complete = False
    elapsed = time.time() - t0
    return {
        "success": (execution_succeeded if control is None
                    else goal_complete is True),
        "execution_succeeded": execution_succeeded,
        "goal_complete": goal_complete,
        "task": task,
        "steps_planned": len(plan),
        "steps_executed": len(results),
        "tools_used": success_count,
        "elapsed": round(elapsed, 3),
        "logs": results,
    }


# ── 快捷入口 ────────────────────────────────────────

def _load_control_contract(path, task_title: str, *, capsule_path=None,
                           resume_trigger=None, capsule_key_path=None):
    """Load an explicit current Goal/Task contract for the daily entrypoint."""
    from src.goal_control import ControlPlane, FeedbackRoute, Goal, Task, DriftError

    data = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError("goal contract must be a JSON object")
    goal_data, task_data = data["goal"], data["task"]
    if not isinstance(goal_data, dict) or not isinstance(task_data, dict):
        raise ValueError("goal and task must be JSON objects")
    goal_data = dict(goal_data)
    task_data = dict(task_data)
    for key in ("success_criteria", "non_goals", "constraints"):
        if key in goal_data:
            if (not isinstance(goal_data[key], list)
                    or any(not isinstance(item, str) for item in goal_data[key])):
                raise ValueError(f"goal {key} must be a list of strings")
            goal_data[key] = tuple(goal_data[key])
    for key in ("criteria", "dependencies"):
        if key in task_data:
            if (not isinstance(task_data[key], list)
                    or any(not isinstance(item, str) for item in task_data[key])):
                raise ValueError(f"task {key} must be a list of strings")
            task_data[key] = tuple(task_data[key])
    goal, linked_task = Goal(**goal_data), Task(**task_data)
    if (linked_task.title != task_title or not linked_task.task_id
            or linked_task.goal_id != goal.goal_id
            or not linked_task.criteria or goal.version < 1 or linked_task.version < 1
            or goal.status != "ACTIVE" or linked_task.status != "ACTIVE"
            or linked_task.residency != "HOT"):
        raise DriftError("contract must bind this task to an active HOT goal")
    key = Path(capsule_key_path).read_bytes() if capsule_key_path else None
    control = ControlPlane(capsule_key=key)
    control.add_goal(goal)
    control.add_task(linked_task, control.goal_checksum(goal.goal_id))
    if capsule_path is not None:
        capsule_file = Path(capsule_path)
        if capsule_file.exists():
            if not resume_trigger:
                raise DriftError("persisted task needs its named resume trigger")
            envelope = json.loads(capsule_file.read_text(encoding="utf-8"))
            control._authenticate_capsule(envelope)
            if not isinstance(envelope, dict) or "traces" not in envelope:
                raise DriftError("persisted task lacks an auditable action trace field")
            routes = envelope.get("feedback_routes", []) if isinstance(envelope, dict) else []
            raw_capsule = envelope.get("capsule") if isinstance(envelope, dict) else None
            if not isinstance(raw_capsule, list) or len(raw_capsule) != 11:
                raise DriftError("invalid persisted task capsule")
            if not isinstance(routes, list) or any(not isinstance(item, dict) for item in routes):
                raise DriftError("invalid persisted feedback routes")
            if (routes and routes[-1].get("kind") == "criterion_correction"
                    and raw_capsule[10] == "criterion_correction reviewed"):
                raise DriftError("criterion correction needs a revised goal and explicit replan")
            control.tasks.pop(linked_task.task_id)
            control.active_task_id = ""
            control.resume_from_file(linked_task.task_id, capsule_file,
                                     resume_trigger)
            resumed = control.tasks[linked_task.task_id]
            if (resumed.title != linked_task.title
                    or resumed.goal_id != linked_task.goal_id
                    or resumed.criteria != linked_task.criteria):
                raise DriftError("resumed task differs from the current contract")
            for raw in routes:
                route = FeedbackRoute(**raw)
                if (route.task_id != resumed.task_id or route.goal_id != goal.goal_id
                        or not route.goal_checksum):
                    raise DriftError("persisted feedback targets another goal or task")
                control.feedback_routes.append(route)
            if (routes and control.feedback_routes[-1].kind == "method_feedback"
                    and control.feedback_routes[-1].goal_checksum
                    == control.goal_checksum(goal.goal_id)):
                key = f"feedback:{resumed.task_id}:{resumed.version}"
                control.durable_knowledge[key] = control.feedback_routes[-1].message
                control.retrieve_knowledge(resumed.task_id, key)
        elif resume_trigger:
            raise DriftError("no persisted task matches the resume trigger")
    return control


def route_daily_feedback(task: str, contract_path, capsule_path, kind: str,
                         message: str, *, resume_trigger=None,
                         capsule_key_path=None) -> Dict:
    """Route explicit human feedback and persist task state before eviction."""
    if not capsule_path:
        raise ValueError("feedback needs a durable capsule path")
    control = _load_control_contract(contract_path, task,
                                     capsule_path=capsule_path,
                                     resume_trigger=resume_trigger,
                                     capsule_key_path=capsule_key_path)
    task_id = control.active_task_id
    route = control.route_feedback(task_id, message, kind)
    status = "SUPERSEDED" if kind == "goal_mutation" else "SUSPENDED"
    trigger = f"{kind} reviewed"
    control.transition_task(task_id, status, trigger, capsule_path)
    return {"kind": route.kind, "contract_action": route.contract_action,
            "task_status": status, "resume_trigger": trigger,
            "goal_checksum": route.goal_checksum}


def replan_daily_corrected_task(task: str, contract_path, capsule_path,
                                next_action: str, trigger: str,
                                *, capsule_key_path=None) -> Dict:
    """Rebind a persisted criterion correction to an explicit revised goal."""
    control = _load_control_contract(contract_path, task,
                                     capsule_key_path=capsule_key_path)
    linked = control.tasks.pop(control.active_task_id)
    control.active_task_id = ""
    capsule = control.replan_corrected_task_from_file(
        linked.task_id, capsule_path, criteria=linked.criteria,
        next_action=next_action, trigger=trigger,
        dependencies=linked.dependencies, expected_title=linked.title)
    return {"task_status": "SUSPENDED", "resume_trigger": trigger,
            "task_version": capsule[4], "goal_version": capsule[2]}


def _load_completion_verifier(path):
    """Load a host-owned evidence checker; model text cannot certify completion."""
    source = Path(path).resolve(strict=True)
    spec = importlib.util.spec_from_file_location("sua_host_completion_verifier", source)
    if spec is None or spec.loader is None:
        raise ValueError("completion verifier must be a readable Python file")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    checker = getattr(module, "verify_completion", None)
    if not callable(checker):
        raise ValueError("completion verifier needs verify_completion(context, logs)")

    def verified(context, logs):
        verdict = checker(context, logs)
        if not isinstance(verdict, dict) or verdict.get("passed") is not True:
            return False
        evidence = verdict.get("evidence")
        criteria = context["goal"].success_criteria
        return (isinstance(evidence, dict)
                and all(isinstance(evidence.get(criterion), str)
                        and evidence[criterion].strip() for criterion in criteria))

    return verified


def quick_test(task: str, stream: bool = True, goal_contract_path=None,
               verifier_path=None, capsule_path=None, resume_trigger=None,
               capsule_key_path=None) -> Dict:
    """使用默认 LLM 快速测试 agent。

    v1.8.1: 默认 stream=True (本地模型慢,streaming 让用户看到进度)。
    流式输出直接 print 到 stdout,每行一步。
    """
    contract_path = goal_contract_path or os.environ.get("SUA_GOAL_CONTRACT")
    if not contract_path:
        return {
            "success": False, "task": task, "steps_planned": 0,
            "steps_executed": 0, "tools_used": 0, "elapsed": 0,
            "logs": [], "error": "Goal Contract required: pass --contract <JSON file> or set SUA_GOAL_CONTRACT."
        }
    try:
        control = _load_control_contract(contract_path, task,
                                         capsule_path=capsule_path,
                                         resume_trigger=resume_trigger,
                                         capsule_key_path=capsule_key_path)
    except (OSError, ValueError, TypeError, KeyError) as exc:
        return {
            "success": False, "task": task, "steps_planned": 0,
            "steps_executed": 0, "tools_used": 0, "elapsed": 0,
            "logs": [], "error": f"Invalid Goal Contract: {exc}"
        }
    try:
        verifier = _load_completion_verifier(verifier_path) if verifier_path else None
    except (OSError, ValueError, ImportError) as exc:
        return {
            "success": False, "task": task, "steps_planned": 0,
            "steps_executed": 0, "tools_used": 0, "elapsed": 0,
            "logs": [], "error": f"Invalid completion verifier: {exc}"
        }

    try:
        from src.llm import LLMConfig, chat_simple
    except ImportError as exc:
        return {
            "success": False, "task": task, "steps_planned": 0,
            "steps_executed": 0, "tools_used": 0, "elapsed": 0,
            "logs": [], "error": f"LLM runtime unavailable; install requirements.txt: {exc}"
        }
    lc = LLMConfig.from_env()

    if not lc.ready:
        return {
            "success": False, "task": task, "steps_planned": 0,
            "steps_executed": 0, "tools_used": 0, "elapsed": 0,
            "logs": [],
            "error": "LLM 未配置。请创建 .env 文件并设置 LLM_API_KEY 和 LLM_MODEL。\n"
                     "参考 .env.example。"
        }

    def _review_action(action, context):
        review_prompt = (
            "Review this proposed tool action against the current Goal Contract. "
            "Return only JSON with allow (boolean) and criterion (an exact success "
            "criterion, or empty string). Deny uncertain, unrelated, forbidden, or "
            "constraint-violating actions.\n"
            + json.dumps({"goal": asdict(context["goal"]),
                          "task": asdict(context["tasks"][control.active_task_id]),
                          "action": action}, ensure_ascii=False, sort_keys=True)
        )
        try:
            response = chat_simple(review_prompt, config=lc)
            decision = json.loads(response)
        except (ValueError, TypeError):
            return None
        if isinstance(decision, dict) and decision.get("allow") is True:
            return decision.get("criterion")
        return None

    if stream:
        # v1.8.1: streaming path — prints tokens as they arrive
        from src.llm_stream import chat_stream

        def _stream_call(prompt: str) -> str:
            """Stream a chat completion; return the assembled text."""
            try:
                chunks = []
                print(f"    [llm] ", end="", flush=True)
                for chunk in chat_stream(
                    messages=[{"role": "user", "content": prompt}],
                    config=lc,
                    timeout=lc.timeout,
                ):
                    chunks.append(chunk)
                    print(chunk, end="", flush=True)
                print()  # newline after streaming
                return "".join(chunks)
            except Exception as e:
                print(f"\n    [llm error: {e}]")
                return ""

        result = run(task, _stream_call, verbose=True, control=control,
                     review_action=_review_action, verify_completion=verifier)
    else:
        # Non-streaming path (faster for benchmarks)
        def _call(prompt):
            return chat_simple(prompt, config=lc) or ""

        result = run(task, _call, control=control, review_action=_review_action,
                     verify_completion=verifier)

    if capsule_path is not None:
        status = ("DONE" if result["goal_complete"] is True else
                  "BLOCKED" if not result["execution_succeeded"] else "SUSPENDED")
        trigger = ("verified completion" if status == "DONE" else
                   "execution repaired" if status == "BLOCKED" else
                   "continue with evidence")
        try:
            control.transition_task(control.active_task_id, status, trigger,
                                    capsule_path)
        except (OSError, ValueError) as exc:
            result["success"] = False
            result["error"] = f"Task state could not be persisted: {exc}"
        else:
            result["task_status"] = status
            result["resume_trigger"] = trigger
            result["capsule_path"] = str(Path(capsule_path).resolve())
    return result


def report_cli_result(result: Dict) -> int:
    """Print a daily run and return its process status without masking failure."""
    print(f"\n{'='*50}")
    if result.get("error"):
        print(f"Error: {result['error']}")
        return 2
    print(f"Steps planned: {result['steps_planned']}")
    print(f"Tools used:    {result['tools_used']}")
    print(f"Time:          {result['elapsed']}s")
    print(f"Execution:     {result['execution_succeeded']}")
    print(f"Goal verified: {result['goal_complete']}")
    if result.get("capsule_path"):
        print(f"Task record:   {result['capsule_path']}")
    print("\nPlan:")
    for i, log in enumerate(result.get("logs", [])):
        print(f"  {i+1}. {log.get('step', '?')[:80]}")
    return 0 if result["success"] else 3


if __name__ == "__main__":
    """使用入口：python -m core.agent --contract goal.json "任务标题"

    这是 agent 的日常使用入口，与自我升级入口 (python -m self_upgrade) 分开。
    Goal Contract 的任务标题必须与命令参数相同。
    """
    # Load .env so users don't need to `export $(cat .env)` first.
    # Mirrors the loader in tests/conftest.py.
    _ENV_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".env")

    def _load_env_file(path: str) -> None:
        if not os.path.exists(path):
            return
        try:
            with open(path, encoding="utf-8-sig") as f:
                for line in f:
                    line = line.strip()
                    if not line or line.startswith("#") or "=" not in line:
                        continue
                    k, v = line.split("=", 1)
                    k = k.strip()
                    v = v.strip()
                    if " #" in v:
                        v = v.split(" #", 1)[0].rstrip()
                    v = v.strip('"').strip("'")
                    if k and k not in os.environ:
                        os.environ[k] = v
        except Exception:
            pass

    _load_env_file(_ENV_PATH)

    import argparse
    parser = argparse.ArgumentParser(description="Run the daily agent with a Goal Contract")
    parser.add_argument("--contract", help="JSON file containing the active goal and task")
    parser.add_argument("--verifier", help="Host-owned Python evidence checker for goal completion")
    parser.add_argument("--capsule", required=True,
                        help="Durable task state file for pause and resume")
    parser.add_argument("--capsule-key", required=True,
                        help="Host-owned 32-byte minimum key file outside the capsule")
    parser.add_argument("--resume-trigger", help="Named trigger matching a persisted task")
    parser.add_argument("--feedback-kind", choices=("method_feedback", "criterion_correction",
                                                     "goal_mutation", "new_task"))
    parser.add_argument("--feedback-message", help="Explicit human feedback to route")
    parser.add_argument("--replan-next-action", help="Next action under a corrected goal")
    parser.add_argument("--replan-trigger", help="Named trigger for the revised task")
    parser.add_argument("task", nargs="+", help="Task title matching the contract")
    args = parser.parse_args()
    task = " ".join(args.task)
    print(f"\nTask: {task}\n{'='*50}")
    if args.feedback_kind or args.feedback_message:
        if not (args.feedback_kind and args.feedback_message and args.capsule
                and args.contract):
            parser.error("feedback needs --feedback-kind, --feedback-message, --capsule, and --contract")
        try:
            route = route_daily_feedback(task, args.contract, args.capsule,
                                         args.feedback_kind, args.feedback_message,
                                         resume_trigger=args.resume_trigger,
                                         capsule_key_path=args.capsule_key)
        except (OSError, ValueError, KeyError) as exc:
            parser.error(str(exc))
        print(json.dumps(route, ensure_ascii=False, sort_keys=True))
        raise SystemExit(0)
    if args.replan_next_action or args.replan_trigger:
        if not (args.replan_next_action and args.replan_trigger and args.capsule
                and args.contract):
            parser.error("replan needs --replan-next-action, --replan-trigger, --capsule, and --contract")
        try:
            replanned = replan_daily_corrected_task(
                task, args.contract, args.capsule, args.replan_next_action,
                args.replan_trigger, capsule_key_path=args.capsule_key)
        except (OSError, ValueError, KeyError) as exc:
            parser.error(str(exc))
        print(json.dumps(replanned, ensure_ascii=False, sort_keys=True))
        raise SystemExit(0)
    result = quick_test(task, goal_contract_path=args.contract,
                        verifier_path=args.verifier, capsule_path=args.capsule,
                        resume_trigger=args.resume_trigger,
                        capsule_key_path=args.capsule_key)
    raise SystemExit(report_cli_result(result))
