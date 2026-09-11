"""Baseline/treatment collector for AI4S scientific-state regressions.

This adapter reuses ``benchmarks/tasks.json`` and SUA's configured LLM. It
collects full research responses because the legacy planner benchmark retains
only plan steps. Rubric ratings remain explicit external judgments: the runner
never turns subjective scientific criteria into regex pass/fail claims.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import sys
from pathlib import Path
from typing import Callable, Dict, Iterable, List, Mapping, Optional


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.benchmark import load_tasks  # noqa: E402
from src.llm import LLMConfig, chat_simple  # noqa: E402


TASK_PATH = ROOT / "benchmarks" / "tasks.json"
ARMS = ("baseline", "treatment")
SUITES = {
    "ai4s": {
        "category": "ai4s_regression",
        "guides": {
            "baseline": [ROOT / "docs" / "RESEARCH_USAGE.md"],
            "treatment": [
                ROOT / "docs" / "RESEARCH_USAGE.md",
                ROOT / "docs" / "AI4S_RESEARCH_MODE.md",
                ROOT / "docs" / "AI4S_RESEARCH_MODE_DETAIL.md",
            ],
        },
        "instruction": (
            "Decide the current evidence state, the next scientific operation, "
            "whether implementation may proceed, and what decision knowledge "
            "must be recorded."
        ),
    },
    "specialization": {
        "category": "specialization_regression",
        "guides": {
            "baseline": [
                ROOT / "docs" / "OPERATING_RULES.md",
                ROOT / "docs" / "M_SELF_APPLICATION.md",
                ROOT / "docs" / "SKILL_DESIGN.md",
            ],
            "treatment": [
                ROOT / "docs" / "OPERATING_RULES.md",
                ROOT / "docs" / "M_SELF_APPLICATION.md",
                ROOT / "docs" / "SKILL_DESIGN.md",
                ROOT / "docs" / "DOMAIN_SPECIALIZATION_BOOTSTRAP.md",
                ROOT / "docs" / "DOMAIN_SPECIALIZATION_BOOTSTRAP_DETAIL.md",
            ],
        },
        "instruction": (
            "Audit whether generic SUA is methodologically adequate for the "
            "recurring task family. Decide whether to retain generic SUA, "
            "collect evidence, or propose only a bounded adapter experiment."
        ),
    },
    "global_progress": {
        "category": "global_progress_regression",
        "guides": {
            "baseline": [ROOT / "docs" / "OPERATING_RULES.md"],
            "treatment": [
                ROOT / "docs" / "OPERATING_RULES.md",
                ROOT / "docs" / "M_ACCEPTANCE_PROTOCOL_DETAIL.md",
                ROOT / "docs" / "CROSS_RUNTIME_SKILL_BRIDGE.md",
            ],
        },
        "instruction": (
            "Decide whether a repeated user rejection permits another local "
            "retry. Track the failed criterion and causal layer, preserve "
            "negative knowledge, and state whether global replanning is required."
        ),
    },
}


def load_ai4s_tasks(path: Path = TASK_PATH) -> List[dict]:
    """Filter AI4S fixtures from the repository's canonical task source."""
    return [
        task for task in load_tasks(str(path))
        if task.get("category") in {
            "ai4s_regression", "ai4s_pre_agent_regression"
        }
    ]


def load_specialization_tasks(path: Path = TASK_PATH) -> List[dict]:
    """Filter domain-specialization fixtures from the canonical task source."""
    return [
        task for task in load_tasks(str(path))
        if task.get("category") == "specialization_regression"
    ]


def load_global_progress_tasks(path: Path = TASK_PATH) -> List[dict]:
    """Filter generic repeated-rejection fixtures from the task source."""
    return [
        task for task in load_tasks(str(path))
        if task.get("category") == "global_progress_regression"
    ]


def build_guide(arm: str, *, suite: str = "ai4s") -> tuple[str, List[str]]:
    """Return the controlled guide text and repository-relative sources."""
    if suite not in SUITES:
        raise ValueError(f"unknown suite: {suite}")
    if arm not in ARMS:
        raise ValueError(f"unknown arm: {arm}")
    paths = SUITES[suite]["guides"][arm]
    text = "\n\n".join(path.read_text(encoding="utf-8") for path in paths)
    files = [path.relative_to(ROOT).as_posix() for path in paths]
    return text, files


def _default_llm(prompt: str, *, system: str, config: LLMConfig) -> str:
    return chat_simple(prompt, system=system, config=config) or ""


def run_arm(
    arm: str,
    *,
    suite: str = "ai4s",
    llm_call: Callable[..., str] = _default_llm,
    tasks: Optional[Iterable[dict]] = None,
    config: Optional[LLMConfig] = None,
) -> dict:
    """Collect one response per fixture; leave every rubric item unscored."""
    guide, files = build_guide(arm, suite=suite)
    config = config or LLMConfig.from_env()
    if not getattr(config, "ready", True):
        raise RuntimeError("LLM configuration is not ready")
    system = (
        "You are a fresh agent. Apply only the provided SUA guide. "
        + SUITES[suite]["instruction"]
        + " Do not assume access to repository files beyond this guide."
        + "\n\nGUIDE:\n"
        + guide
    )
    results = []
    default_tasks = {
        "ai4s": load_ai4s_tasks,
        "specialization": load_specialization_tasks,
        "global_progress": load_global_progress_tasks,
    }[suite]()
    for task in list(tasks) if tasks is not None else default_tasks:
        response = llm_call(task["task"], system=system, config=config)
        if not response or not response.strip():
            raise RuntimeError(
                f"LLM returned an empty response for {task['id']}; arm invalid"
            )
        rubric = [
            {**item, "rating": None, "note": ""}
            for item in task["rubric"]
        ]
        results.append({
            "id": task["id"],
            "case": task["case"],
            "prompt": task["task"],
            "expected_decision": task["expected_decision"],
            "response": response,
            "rubric": rubric,
        })
    return {
        "schema_version": 1,
        "suite": suite,
        "arm": arm,
        "guide_files": files,
        "guide_sha256": hashlib.sha256(guide.encode("utf-8")).hexdigest(),
        "model": getattr(config, "model", "unknown"),
        "scoring": "explicit_binary_rubric_unscored",
        "results": results,
    }


def score_run(raw: dict, ratings: Mapping[str, Mapping[str, int]]) -> dict:
    """Attach complete external 0/1 ratings and compute transparent totals."""
    scored = copy.deepcopy(raw)
    expected_tasks = {result["id"] for result in scored["results"]}
    if set(ratings) != expected_tasks:
        raise ValueError("ratings must exactly match run task ids")

    earned = 0
    possible = 0
    by_criterion: Dict[str, Dict[str, int]] = {}
    for result in scored["results"]:
        task_ratings = ratings[result["id"]]
        expected = {item["id"] for item in result["rubric"]}
        if set(task_ratings) != expected:
            raise ValueError(
                f"ratings must exactly match rubric ids for {result['id']}"
            )
        task_earned = 0
        for item in result["rubric"]:
            value = task_ratings[item["id"]]
            if value not in (0, 1):
                raise ValueError("rubric ratings must be binary 0 or 1")
            item["rating"] = value
            task_earned += value
            earned += value
            possible += 1
            bucket = by_criterion.setdefault(
                item["id"], {"earned": 0, "possible": 0}
            )
            bucket["earned"] += value
            bucket["possible"] += 1
        result["score"] = {
            "earned": task_earned,
            "possible": len(result["rubric"]),
        }
    scored["scoring"] = "explicit_binary_rubric_scored"
    scored["score"] = {
        "earned": earned,
        "possible": possible,
        "rate": earned / possible if possible else 0.0,
        "by_criterion": by_criterion,
    }
    return scored


def compare_scored_runs(baseline: dict, treatment: dict) -> dict:
    """Compare equal-size scored arms without a significance claim."""
    if baseline.get("arm") != "baseline" or treatment.get("arm") != "treatment":
        raise ValueError("comparison requires baseline and treatment arms")
    b_score = baseline["score"]
    t_score = treatment["score"]
    if b_score["possible"] != t_score["possible"]:
        raise ValueError("arms have different rubric denominators")
    b_rate = b_score.get("rate", b_score["earned"] / b_score["possible"])
    t_rate = t_score.get("rate", t_score["earned"] / t_score["possible"])
    return {
        "baseline": b_score,
        "treatment": t_score,
        "score_delta": t_score["earned"] - b_score["earned"],
        "rate_delta": t_rate - b_rate,
        "interpretation": "directional_only_not_significance",
    }


def _read_json(path: str) -> dict:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def _write_json(path: str, payload: dict) -> None:
    Path(path).write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)

    run_parser = sub.add_parser("run", help="collect an unscored arm")
    run_parser.add_argument("--suite", choices=sorted(SUITES), default="ai4s")
    run_parser.add_argument("--arm", choices=ARMS, required=True)
    run_parser.add_argument("--output", required=True)

    score_parser = sub.add_parser("score", help="attach explicit ratings")
    score_parser.add_argument("--input", required=True)
    score_parser.add_argument("--ratings", required=True)
    score_parser.add_argument("--output", required=True)

    compare_parser = sub.add_parser("compare", help="compare scored arms")
    compare_parser.add_argument("--baseline", required=True)
    compare_parser.add_argument("--treatment", required=True)
    compare_parser.add_argument("--output", required=True)

    args = parser.parse_args(argv)
    if args.command == "run":
        payload = run_arm(args.arm, suite=args.suite)
    elif args.command == "score":
        payload = score_run(_read_json(args.input), _read_json(args.ratings))
    else:
        payload = compare_scored_runs(
            _read_json(args.baseline), _read_json(args.treatment)
        )
    _write_json(args.output, payload)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
