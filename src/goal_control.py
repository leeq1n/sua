"""Small, runtime-neutral reference contract for goal and context control.

This is a deterministic control surface, not a classifier of natural language.
The caller must supply explicit action/criterion links and feedback categories.
"""

from dataclasses import asdict, dataclass, field
from hashlib import sha256
import hmac
import json
import os
from pathlib import Path
import tempfile
from typing import Dict, Tuple


class DriftError(ValueError):
    """The proposed operation lacks a valid current goal link."""


TASK_STATUSES = frozenset({"ACTIVE", "WAITING_USER", "BLOCKED", "SUSPENDED",
                           "SUPERSEDED", "DONE", "ABANDONED"})
RESIDENCIES = frozenset({"HOT", "COLD", "ARCHIVED"})


@dataclass
class Goal:
    goal_id: str
    objective: str
    success_criteria: Tuple[str, ...]
    non_goals: Tuple[str, ...] = ()
    constraints: Tuple[str, ...] = ()
    status: str = "ACTIVE"
    version: int = 1


@dataclass
class Task:
    task_id: str
    title: str
    goal_id: str
    criteria: Tuple[str, ...]
    status: str = "ACTIVE"
    version: int = 1
    dependencies: Tuple[str, ...] = ()
    residency: str = "HOT"
    resume_trigger: str = ""
    next_action: str = ""
    blocker: str = ""


@dataclass(frozen=True)
class FeedbackRoute:
    kind: str
    message: str
    task_id: str
    goal_id: str
    goal_checksum: str
    contract_action: str


@dataclass
class ControlPlane:
    goals: Dict[str, Goal] = field(default_factory=dict)
    goal_baselines: Dict[str, str] = field(default_factory=dict)
    tasks: Dict[str, Task] = field(default_factory=dict)
    active_goal_id: str = ""
    active_task_id: str = ""
    durable_knowledge: Dict[str, str] = field(default_factory=dict)
    retrieved_knowledge: Dict[str, set] = field(default_factory=dict)
    allowed_actions: Dict[str, set] = field(default_factory=dict)
    traces: list = field(default_factory=list)
    trace_contracts: list = field(default_factory=list)
    feedback_routes: list = field(default_factory=list)
    capsules: Dict[str, tuple] = field(default_factory=dict)
    capsule_dir: Path | None = None
    capsule_key: bytes | None = field(default=None, repr=False)

    def __post_init__(self):
        if self.capsule_key is not None and (
                not isinstance(self.capsule_key, bytes)
                or len(self.capsule_key) < 32):
            raise ValueError("capsule authentication key needs at least 32 bytes")

    def _authenticate_capsule(self, envelope):
        """Require host-keyed integrity for capsules created in keyed mode."""
        if not isinstance(envelope, dict):
            if self.capsule_key is not None:
                raise DriftError("authenticated capsule envelope required")
            return envelope
        auth = envelope.get("auth")
        if self.capsule_key is None:
            if auth is not None:
                raise DriftError("host capsule key required for signed state")
            return envelope
        if (not isinstance(auth, dict) or auth.get("alg") != "HMAC-SHA256"
                or not isinstance(auth.get("tag"), str)):
            raise DriftError("authenticated capsule required")
        payload = {key: value for key, value in envelope.items() if key != "auth"}
        encoded = json.dumps(payload, ensure_ascii=False, sort_keys=True,
                             separators=(",", ":")).encode("utf-8")
        expected = hmac.new(self.capsule_key, encoded, sha256).hexdigest()
        if not hmac.compare_digest(auth["tag"], expected):
            raise DriftError("capsule authentication failed")
        return envelope

    @staticmethod
    def _validated_traces(envelope, task_id: str, goal_id: str):
        """Read task-local action links before admitting persisted state."""
        if not isinstance(envelope, dict):
            return [], []
        raw = envelope.get("traces", [])
        contexts = envelope.get("trace_contracts", [])
        if (not isinstance(raw, list)
                or not isinstance(contexts, list) or len(contexts) != len(raw)
                or any(not isinstance(item, list) or len(item) != 4
                       or any(not isinstance(value, str) or not value
                              for value in item)
                       or item[1] != task_id or item[3] != goal_id
                       for item in raw)):
            raise DriftError("invalid persisted action trace")
        for trace, context in zip(raw, contexts):
            if (not isinstance(context, dict)
                    or context.get("goal_id") != goal_id
                    or context.get("status") != "ACTIVE"
                    or not isinstance(context.get("version"), int)
                    or not isinstance(context.get("success_criteria"), list)
                    or trace[2] not in context["success_criteria"]
                    or not all(isinstance(context.get(key), str)
                               for key in ("objective",))
                    or not all(isinstance(context.get(key), list)
                               for key in ("non_goals", "constraints"))):
                raise DriftError("invalid persisted action trace contract")
        return [tuple(item) for item in raw], contexts

    def goal_checksum(self, goal_id: str):
        goal = self.goals[goal_id]
        payload = (goal.goal_id, goal.objective, goal.success_criteria,
                   goal.non_goals, goal.constraints, goal.status, goal.version)
        return sha256(json.dumps(payload, ensure_ascii=False).encode()).hexdigest()

    def add_goal(self, goal: Goal):
        if not goal.goal_id or not goal.objective or not goal.success_criteria:
            raise ValueError("goal needs identity, objective, and criteria")
        if goal.goal_id in self.goals:
            raise ValueError("goal identity already exists")
        self.goals[goal.goal_id] = goal
        self.goal_baselines[goal.goal_id] = self.goal_checksum(goal.goal_id)
        if goal.status == "ACTIVE" and not self.active_goal_id:
            self.active_goal_id = goal.goal_id

    def add_task(self, task: Task, expected_goal_checksum: str):
        goal = self.goals.get(task.goal_id)
        if (goal is None or goal.status != "ACTIVE"
                or expected_goal_checksum != self.goal_checksum(task.goal_id)
                or expected_goal_checksum != self.goal_baselines[task.goal_id]
                or not set(task.criteria) <= set(goal.success_criteria)):
            raise DriftError("task criteria must link to its goal")
        if task.task_id in self.tasks or task.status not in TASK_STATUSES:
            raise ValueError("invalid or duplicate task identity/status")
        required_residency = ("HOT" if task.status == "ACTIVE" else
                              "ARCHIVED" if task.status in {"SUPERSEDED", "DONE", "ABANDONED"}
                              else "COLD")
        if task.residency != required_residency:
            raise ValueError("task status and residency disagree")
        self.tasks[task.task_id] = task
        if (task.status == "ACTIVE" and task.goal_id == self.active_goal_id
                and not self.active_task_id):
            self.active_task_id = task.task_id

    def allow_action(self, task_id: str, action: str, criterion: str):
        """Bind a reviewed action to one criterion and current goal version."""
        task = self.tasks[task_id]
        goal = self.goals[task.goal_id]
        checksum = self.goal_checksum(goal.goal_id)
        if (task_id != self.active_task_id or task.goal_id != self.active_goal_id
                or task.status != "ACTIVE" or task.residency != "HOT"
                or goal.status != "ACTIVE" or checksum != self.goal_baselines[goal.goal_id]
                or criterion not in task.criteria or criterion not in goal.success_criteria
                or action in goal.non_goals):
            raise DriftError("action plan lacks a current task, criterion, and goal")
        self.allowed_actions.setdefault(task_id, set()).add((action, criterion, checksum))

    def activate_task(self, task_id: str):
        task = self.tasks[task_id]
        if (task.status != "ACTIVE" or task.residency != "HOT"
                or self.goals[task.goal_id].status != "ACTIVE"
                or self.goal_checksum(task.goal_id) != self.goal_baselines[task.goal_id]):
            raise DriftError("task is not active and resident")
        self._require_previous_task_evicted(task_id)
        if self.active_task_id != task_id:
            self.retrieved_knowledge.pop(self.active_task_id, None)
        self.active_goal_id, self.active_task_id = task.goal_id, task_id

    def _require_previous_task_evicted(self, next_task_id: str):
        if self.active_task_id and self.active_task_id != next_task_id:
            previous = self.tasks[self.active_task_id]
            if previous.status == "ACTIVE" and previous.residency == "HOT":
                raise DriftError("persist and evict the current task before switching")

    def retrieve_knowledge(self, task_id: str, key: str):
        """Admit one durable item for the currently active task only."""
        task = self.tasks[task_id]
        goal = self.goals[task.goal_id]
        if (task_id != self.active_task_id or task.goal_id != self.active_goal_id
                or task.status != "ACTIVE" or task.residency != "HOT"
                or goal.status != "ACTIVE" or key not in self.durable_knowledge
                or self.goal_checksum(goal.goal_id) != self.goal_baselines[goal.goal_id]):
            raise DriftError("knowledge retrieval needs a current task and item")
        self.retrieved_knowledge.setdefault(task_id, set()).add(key)

    def record_action(self, action: str, task_id: str, criterion: str):
        task = self.tasks.get(task_id)
        if (task is None or task.status != "ACTIVE" or task.residency != "HOT"
                or task_id != self.active_task_id or task.goal_id != self.active_goal_id):
            raise DriftError("action has no active task and goal")
        goal = self.goals[task.goal_id]
        if (goal.status != "ACTIVE" or criterion not in task.criteria
                or criterion not in goal.success_criteria or action in goal.non_goals
                or (action, criterion, self.goal_checksum(goal.goal_id))
                not in self.allowed_actions.get(task_id, set())
                or self.goal_checksum(goal.goal_id) != self.goal_baselines[goal.goal_id]):
            raise DriftError("action is not authorized by task and criterion")
        trace = (action, task_id, criterion, goal.goal_id)
        self.traces.append(trace)
        self.trace_contracts.append(asdict(goal))
        return trace

    def route_feedback(self, task_id: str, message: str, kind: str):
        if task_id not in self.tasks:
            raise KeyError(task_id)
        actions = {"method_feedback": "REPLAN_METHOD",
                   "criterion_correction": "REVISE_GOAL",
                   "goal_mutation": "SUPERSEDE_GOAL",
                   "new_task": "CREATE_TASK"}
        if kind not in actions or not message.strip():
            raise ValueError("feedback needs a known category and message")
        task = self.tasks[task_id]
        goal = self.goals[task.goal_id]
        checksum = self.goal_checksum(goal.goal_id)
        if goal.status != "ACTIVE" or checksum != self.goal_baselines[goal.goal_id]:
            raise DriftError("feedback cannot target a stale goal")
        if kind == "method_feedback":
            if (task_id != self.active_task_id or task.goal_id != self.active_goal_id
                    or task.status != "ACTIVE" or task.residency != "HOT"):
                raise DriftError("method feedback needs the current active task")
            task.version += 1
            self.allowed_actions.pop(task_id, None)
            self.retrieved_knowledge.pop(task_id, None)
        route = FeedbackRoute(kind, message, task_id, goal.goal_id,
                              checksum, actions[kind])
        self.feedback_routes.append(route)
        return route

    def revise_goal(self, goal_id: str, expected_checksum: str, *, objective=None,
                    success_criteria=None, non_goals=None, constraints=None):
        goal = self.goals[goal_id]
        if (expected_checksum != self.goal_checksum(goal_id)
                or expected_checksum != self.goal_baselines[goal_id]
                or goal.status != "ACTIVE"):
            raise DriftError("goal changed since feedback was classified")
        if objective is not None and objective != goal.objective:
            raise DriftError("objective mutation needs a successor goal identity")
        changes = (("objective", objective), ("success_criteria", success_criteria),
                   ("non_goals", non_goals), ("constraints", constraints))
        if not any(value is not None and value != getattr(goal, key) for key, value in changes):
            raise ValueError("goal revision needs a changed contract field")
        affected = [task.task_id for task in self.tasks.values()
                    if (task.goal_id == goal_id
                        and task.status not in {"SUPERSEDED", "DONE", "ABANDONED"})]
        self._transition_batch(affected, "SUSPENDED", "goal contract changed")
        for key, value in changes:
            if value is not None:
                setattr(goal, key, value)
        goal.version += 1
        self.goal_baselines[goal_id] = self.goal_checksum(goal_id)
        self.allowed_actions.clear()
        self.retrieved_knowledge.clear()

    def replan_suspended_task(self, task_id: str, expected_goal_checksum: str, *,
                              criteria: Tuple[str, ...], next_action: str,
                              trigger: str, dependencies=None, blocker=None,
                              path=None):
        """Bind a suspended task to the revised goal before it may resume."""
        task = self.tasks[task_id]
        goal = self.goals[task.goal_id]
        if (task.status != "SUSPENDED" or task.residency != "COLD"
                or goal.status != "ACTIVE"
                or expected_goal_checksum != self.goal_checksum(goal.goal_id)
                or expected_goal_checksum != self.goal_baselines[goal.goal_id]
                or not criteria or not set(criteria) <= set(goal.success_criteria)
                or not next_action.strip() or not trigger.strip()):
            raise DriftError("replan needs a suspended task and current goal criteria")
        new_dependencies = task.dependencies if dependencies is None else tuple(dependencies)
        new_blocker = task.blocker if blocker is None else blocker
        capsule = (task.task_id, task.goal_id, goal.version,
                   expected_goal_checksum, task.version + 1, task.title,
                   tuple(criteria), new_dependencies, next_action,
                   new_blocker, trigger)
        self._persist_capsule(task_id, capsule, path, status="SUSPENDED")
        task.criteria, task.next_action = tuple(criteria), next_action
        task.dependencies, task.blocker = new_dependencies, new_blocker
        task.version += 1
        task.resume_trigger = trigger
        self.capsules[task_id] = capsule
        self.allowed_actions.pop(task_id, None)
        self.retrieved_knowledge.pop(task_id, None)
        return capsule

    def replan_corrected_task_from_file(self, task_id: str, path, *,
                                        criteria: Tuple[str, ...],
                                        next_action: str, trigger: str,
                                        dependencies=(), expected_title=None):
        """Rebuild a corrected cold task against a newer Goal Contract."""
        with Path(path).open("r", encoding="utf-8") as stream:
            envelope = json.load(stream)
        envelope = self._authenticate_capsule(envelope)
        if (not isinstance(envelope, dict) or envelope.get("schema") != 1
                or envelope.get("status") != "SUSPENDED"
                or "traces" not in envelope
                or task_id in self.tasks or self.active_task_id):
            raise DriftError("replan needs a suspended persisted task")
        raw = envelope.get("capsule")
        routes = envelope.get("feedback_routes", [])
        old_goal = envelope.get("goal_contract")
        if (not isinstance(raw, list) or len(raw) != 11
                or not isinstance(raw[6], list) or not isinstance(raw[7], list)
                or not isinstance(raw[2], int) or not isinstance(raw[4], int)
                or any(not isinstance(item, str) for item in
                       (*raw[:2], raw[3], raw[5], *raw[6], *raw[7], *raw[8:]))
                or not isinstance(old_goal, dict)
                or not isinstance(routes, list) or not routes
                or any(not isinstance(item, dict) for item in routes)
                or routes[-1].get("kind") != "criterion_correction"):
            raise DriftError("invalid criterion-correction capsule")
        (stored_id, goal_id, old_version, old_checksum, task_version,
         title, old_criteria, old_dependencies, old_next, blocker,
         old_trigger) = raw
        old_traces, old_trace_contracts = self._validated_traces(
            envelope, task_id, goal_id)
        goal = self.goals.get(goal_id)
        if (stored_id != task_id or not title
                or (expected_title is not None and title != expected_title)
                or task_version < 1
                or old_version < 1 or not old_checksum or not old_criteria
                or old_trigger != "criterion_correction reviewed"
                or goal is None or goal.status != "ACTIVE"
                or goal.version <= old_version
                or old_goal.get("goal_id") != goal_id
                or old_goal.get("version") != old_version
                or old_goal.get("objective") != goal.objective
                or self.goal_checksum(goal_id) != self.goal_baselines[goal_id]
                or routes[-1].get("task_id") != task_id
                or routes[-1].get("goal_id") != goal_id
                or routes[-1].get("goal_checksum") != old_checksum):
            raise DriftError("corrected task needs a newer authorized goal")
        from_file = tuple(raw[:6]) + (tuple(old_criteria),
                                       tuple(old_dependencies), *raw[8:])
        task = Task(task_id, title, goal_id, tuple(old_criteria),
                    status="SUSPENDED", version=task_version,
                    dependencies=tuple(old_dependencies), residency="COLD",
                    resume_trigger=old_trigger, next_action=old_next,
                    blocker=blocker)
        self.tasks[task_id] = task
        self.capsules[task_id] = from_file
        previous_traces = self.traces
        previous_trace_contracts = self.trace_contracts
        self.traces = old_traces
        self.trace_contracts = old_trace_contracts
        try:
            self.feedback_routes = [FeedbackRoute(**item) for item in routes]
            return self.replan_suspended_task(
                task_id, self.goal_checksum(goal_id), criteria=tuple(criteria),
                next_action=next_action, trigger=trigger,
                dependencies=tuple(dependencies), path=path)
        except Exception:
            self.tasks.pop(task_id, None)
            self.capsules.pop(task_id, None)
            self.feedback_routes.clear()
            self.traces = previous_traces
            self.trace_contracts = previous_trace_contracts
            raise

    def supersede_goal(self, old_id: str, new_id: str, expected_checksum: str):
        if old_id not in self.goals or new_id not in self.goals:
            raise KeyError("goal not found")
        if (old_id == new_id or self.goals[old_id].status != "ACTIVE"
                or self.goals[new_id].status != "ACTIVE"
                or expected_checksum != self.goal_checksum(old_id)
                or self.goal_checksum(old_id) != self.goal_baselines[old_id]
                or self.goal_checksum(new_id) != self.goal_baselines[new_id]):
            raise DriftError("supersession needs distinct active goal contracts")
        affected = [task.task_id for task in self.tasks.values()
                    if (task.goal_id == old_id
                        and task.status not in {"SUPERSEDED", "DONE", "ABANDONED"})]
        self._transition_batch(affected, "SUPERSEDED", "goal superseded")
        self.goals[old_id].status = "SUPERSEDED"
        self.goal_baselines[old_id] = self.goal_checksum(old_id)
        self.active_goal_id = new_id
        if self.active_task_id and self.tasks[self.active_task_id].goal_id == old_id:
            self.active_task_id = ""
        self.allowed_actions.clear()
        self.retrieved_knowledge.clear()

    def wait_for_user(self, task_id: str, trigger: str, path=None):
        self.transition_task(task_id, "WAITING_USER", trigger, path)

    def transition_task(self, task_id: str, status: str, trigger: str = "", path=None):
        if status not in TASK_STATUSES or status == "ACTIVE":
            raise ValueError("use resume or activate_task for ACTIVE")
        if status in {"WAITING_USER", "BLOCKED", "SUSPENDED"} and not trigger:
            raise ValueError("resumable transition needs a named trigger")
        task = self.tasks[task_id]
        if task.status in {"SUPERSEDED", "DONE", "ABANDONED"}:
            raise DriftError("terminal task cannot transition")
        capsule = self.capture(task_id)[:-1] + (trigger,)
        self._persist_capsule(task_id, capsule, path, status=status)
        self._apply_transition(task_id, status, trigger, capsule)
        return capsule

    def _transition_batch(self, task_ids, status: str, trigger: str):
        """Persist every capsule before changing any task in a multi-task edit."""
        prepared = []
        for task_id in task_ids:
            capsule = self.capture(task_id)[:-1] + (trigger,)
            self._persist_capsule(task_id, capsule, status=status)
            prepared.append((task_id, capsule))
        for task_id, capsule in prepared:
            self._apply_transition(task_id, status, trigger, capsule)

    def _apply_transition(self, task_id: str, status: str, trigger: str, capsule: tuple):
        task = self.tasks[task_id]
        task.status, task.resume_trigger = status, trigger
        task.residency = "ARCHIVED" if status in {"SUPERSEDED", "DONE", "ABANDONED"} else "COLD"
        if task.residency == "COLD":
            self.capsules[task_id] = capsule
        else:
            self.capsules.pop(task_id, None)
        self.allowed_actions.pop(task_id, None)
        self.retrieved_knowledge.pop(task_id, None)
        if self.active_task_id == task_id:
            self.active_task_id = ""

    def capture(self, task_id: str):
        task = self.tasks[task_id]
        return (task.task_id, task.goal_id, self.goals[task.goal_id].version,
                self.goal_checksum(task.goal_id), task.version, task.title,
                task.criteria, task.dependencies, task.next_action,
                task.blocker, task.resume_trigger)

    def pause_and_persist(self, task_id: str, status: str, path, trigger: str = ""):
        """Write a task capsule atomically before moving it out of HOT."""
        if status not in {"WAITING_USER", "BLOCKED", "SUSPENDED"}:
            raise ValueError("only resumable statuses can be persisted")
        task = self.tasks[task_id]
        if task.status != "ACTIVE" or task.residency != "HOT":
            raise DriftError("only an active task can be paused")
        return self.transition_task(task_id, status, trigger, path)

    def _persist_capsule(self, task_id: str, capsule: tuple, path=None, *, status: str):
        if path is None:
            if self.capsule_dir is None:
                raise DriftError("durable capsule destination required before eviction")
            destination = Path(self.capsule_dir) / (sha256(task_id.encode()).hexdigest() + ".json")
        else:
            destination = Path(path)
        temporary = None
        try:
            with tempfile.NamedTemporaryFile("w", encoding="utf-8", dir=destination.parent,
                                             prefix=destination.name + ".", suffix=".tmp",
                                             delete=False) as stream:
                temporary = Path(stream.name)
                envelope = {
                    "schema": 1, "status": status, "capsule": capsule,
                    "goal_contract": asdict(self.goals[self.tasks[task_id].goal_id]),
                    "traces": [list(trace) for trace in self.traces
                               if trace[1] == task_id],
                    "trace_contracts": [context for trace, context in
                                        zip(self.traces, self.trace_contracts)
                                        if trace[1] == task_id],
                    "feedback_routes": [asdict(route) for route in self.feedback_routes
                                        if route.task_id == task_id],
                }
                if self.capsule_key is not None:
                    encoded = json.dumps(envelope, ensure_ascii=False,
                                         sort_keys=True, separators=(",", ":")).encode("utf-8")
                    envelope["auth"] = {
                        "alg": "HMAC-SHA256",
                        "tag": hmac.new(self.capsule_key, encoded, sha256).hexdigest(),
                    }
                json.dump(envelope, stream, ensure_ascii=False)
                stream.flush()
                os.fsync(stream.fileno())
            os.replace(temporary, destination)
        except Exception:
            if temporary is not None:
                temporary.unlink(missing_ok=True)
            raise

    def resume_from_file(self, task_id: str, path, trigger: str):
        """Re-admit a capsule against the current goal, rebuilding a missing task."""
        with Path(path).open("r", encoding="utf-8") as stream:
            raw = json.load(stream)
        raw = self._authenticate_capsule(raw)
        persisted_status = None
        if isinstance(raw, dict):
            if (raw.get("schema") != 1 or raw.get("status") not in TASK_STATUSES):
                raise DriftError("invalid capsule envelope")
            persisted_status = raw["status"]
            raw_capsule = raw.get("capsule")
            persisted_goal_id = (raw_capsule[1] if isinstance(raw_capsule, list)
                                 and len(raw_capsule) >= 2 else "")
            persisted_traces, persisted_trace_contracts = self._validated_traces(
                raw, task_id, persisted_goal_id)
            raw = raw.get("capsule")
        else:
            persisted_traces = []
            persisted_trace_contracts = []
        if (not isinstance(raw, list) or len(raw) != 11
                or not isinstance(raw[6], list) or not isinstance(raw[7], list)
                or any(not isinstance(value, str) for value in
                       (*raw[:2], raw[3], raw[5], *raw[6], *raw[7], *raw[8:]))
                or not isinstance(raw[2], int) or not isinstance(raw[4], int)):
            raise DriftError("invalid capsule")
        capsule = tuple(raw[:6]) + (tuple(raw[6]), tuple(raw[7]), *raw[8:])
        if task_id not in self.tasks:
            (stored_task_id, goal_id, goal_version, goal_checksum,
             task_version, title, criteria, dependencies, next_action,
             blocker, resume_trigger) = capsule
            goal = self.goals.get(goal_id)
            if (persisted_status not in {"WAITING_USER", "BLOCKED", "SUSPENDED"}
                    or stored_task_id != task_id or not title or task_version < 1
                    or not criteria or not trigger or trigger != resume_trigger
                    or goal is None or goal.status != "ACTIVE"
                    or goal_version != goal.version
                    or goal_checksum != self.goal_checksum(goal_id)
                    or goal_checksum != self.goal_baselines[goal_id]
                    or not set(criteria) <= set(goal.success_criteria)):
                raise DriftError("persisted capsule does not match current goal")
            self._require_previous_task_evicted(task_id)
            task = Task(task_id, title, goal_id, criteria,
                        status=persisted_status, version=task_version,
                        dependencies=dependencies, residency="COLD",
                        resume_trigger=resume_trigger, next_action=next_action,
                        blocker=blocker)
            self.add_task(task, goal_checksum)
            self.capsules[task_id] = capsule
            try:
                self.resume(task_id, capsule, trigger)
            except Exception:
                self.capsules.pop(task_id, None)
                self.tasks.pop(task_id, None)
                raise
            self.traces = persisted_traces
            self.trace_contracts = persisted_trace_contracts
        else:
            if (capsule != self.capture(task_id)
                    or (persisted_status is not None
                        and persisted_status != self.tasks[task_id].status)):
                raise DriftError("persisted capsule does not match current contracts")
            self.capsules[task_id] = capsule
            self.resume(task_id, capsule, trigger)
            self.traces = persisted_traces
            self.trace_contracts = persisted_trace_contracts

    def resume(self, task_id: str, capsule, trigger: str):
        task = self.tasks[task_id]
        if (capsule != self.capsules.get(task_id) or capsule != self.capture(task_id)
                or task.status not in {"WAITING_USER", "BLOCKED", "SUSPENDED"}
                or task.residency != "COLD"
                or self.goals[task.goal_id].status != "ACTIVE"
                or self.goal_checksum(task.goal_id) != self.goal_baselines[task.goal_id]
                or not trigger or trigger != task.resume_trigger):
            raise DriftError("resume capsule or goal is stale")
        self._require_previous_task_evicted(task_id)
        task.status, task.residency = "ACTIVE", "HOT"
        del self.capsules[task_id]
        self.retrieved_knowledge.pop(self.active_task_id, None)
        self.active_goal_id, self.active_task_id = task.goal_id, task_id

    def working_context(self):
        goal = self.goals.get(self.active_goal_id)
        task = self.tasks.get(self.active_task_id)
        visible = {}
        goal_valid = bool(goal and goal.status == "ACTIVE" and
                          self.goal_checksum(goal.goal_id) == self.goal_baselines[goal.goal_id])
        task_valid = bool(goal_valid and task and task.status == "ACTIVE"
                          and task.residency == "HOT" and task.goal_id == goal.goal_id)
        if task_valid:
            visible[task.task_id] = task
            for dep_id in task.dependencies:
                dep = self.tasks.get(dep_id)
                if dep and dep.goal_id == goal.goal_id and dep.residency == "HOT":
                    visible[dep_id] = dep
        retrieved = self.retrieved_knowledge.get(task.task_id, set()) if task_valid else set()
        return {"goal": goal if goal_valid else None,
                "tasks": visible,
                "knowledge": {key: self.durable_knowledge[key]
                              for key in retrieved if key in self.durable_knowledge}}
