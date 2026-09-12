#!/usr/bin/env python3
"""M-n 29 5-step regression-evidence protocol (programmatic).

External trigger: replaces LLM-self-judgment with deterministic
mechanical checklist.  Per user message 2026-07-16 "按原则做决定" +
M-n 32 self-learning-guardrail Guardrail #4 (pre-claim M-n 29 5-step)
+ retrospective 4-FAIL diagnosis.

Usage:
    python agent-tools/scripts/m_n29_5step.py          # interactive
    python agent-tools/scripts/m_n29_5step.py --self   # agent self-mode
    python agent-tools/scripts/m_n29_5step.py --self \
        --task-profile open-ended --claim "compare repair designs"

This script IS NOT a replacement for human review — it's a
mechanical baseline that runs the 5 primitives deterministically.
LLM runtime should additionally invoke 5 primitives manually for
full coverage.

Output: prints Step 1-5 checklist + 5-primitives application.
The checklist is regression evidence only.  Per P30 it never issues terminal
artifact acceptance, even when every structural criterion is populated.
"""
from __future__ import annotations
import argparse
import sys
from pathlib import Path

from p30_acceptance import (
    ROLE_IMPLEMENTER,
    ROLE_INDEPENDENT_EVALUATOR,
    ROLE_UNSPECIFIED,
    compute_current_artifact_identity,
    execution_success,
    record_regression,
)


def design_criteria(task_profile: str) -> list[tuple[str, str]]:
    """Step 1: task-generic structural acceptance dimensions."""
    return [
        ("Scope", "task boundary and excluded work are explicit"),
        ("Functional", "requested outcome has claim-matched evidence"),
        ("Safety", "hard constraints and destructive effects are checked"),
        ("Maintainability", "smallest durable layer owns the change"),
        ("Fresh-agent", "a new agent can discover and apply the result"),
        (
            "Constructive control",
            "observable search-space expansion before critique"
            if task_profile == "open-ended"
            else "well-specified direct execution; no creativity ceremony",
        ),
    ]


def five_primitives(claim: str, task_profile: str) -> dict[str, str]:
    """Step 2: 5 primitives applied to the claim.
    Per AGENTS.md "5 primitives gate" + M-n 34 sub-step 3."""
    return {
        "Analyze": f"Task: {claim}. Profile: {task_profile}. Confirm scope and boundaries.",
        "Reason": "Compare alternatives, trade-offs, and claim-matched evidence.",
        "联想": "For open-ended work, transfer a donor invariant and generate a target consequence.",
        "归纳": "Check whether repeated results require an abstraction or controller-level replan.",
        "总结": "Synthesize evidence and state what remains semantically unverified.",
    }


def four_critical_thinking(claim: str) -> dict[str, str]:
    """Step 2a: 4 critical-thinking primitives (adversarial pair
    to the 5 constructive primitives, per user message 2026-07-16
    + M-n 14 two-track reasoning).

    Full detail: docs/M_CRITICAL_THINKING_PRIMITIVES_DETAIL.md
    """
    return {
        "质疑 (Challenge)":
            "3 specific weaknesses + highest-damage weakness "
            "explicitly acknowledged",
        "逆向 (Invert)":
            "OPPOSITE state + 2-3 reasons OPPOSITE could be "
            "true + what would change",
        "预演失败 (Pre-mortem)":
            "this FAILED in 30 days + 3-5 failure modes + "
            "1-2 preventable (Klein 2007)",
        "对立论证 (Steelman-the-opposite)":
            "most charitable opposing case + 2-3 strongest "
            "opposing arguments + acknowledge valid ones",
    }


def validate(primitives: dict[str, str], criteria: list[tuple[str, str]]) -> tuple[int, int]:
    """Step 3: Validate checklist structure, not semantic task success."""
    primitive_fields = sum(bool(value.strip()) for value in primitives.values())
    criterion_fields = sum(bool(name.strip()) and bool(value.strip()) for name, value in criteria)
    return primitive_fields, criterion_fields


def main() -> int:
    parser = argparse.ArgumentParser(description="M-n 29 5-step protocol")
    parser.add_argument("--claim", default="task done",
                        help="what to verify (default: 'task done')")
    parser.add_argument("--self", action="store_true",
                        help="agent self-mode (no interactive prompts)")
    parser.add_argument(
        "--task-profile",
        choices=("well-specified", "open-ended"),
        default="well-specified",
        help="select direct execution or constructive-expansion acceptance",
    )
    parser.add_argument(
        "--role",
        choices=(ROLE_IMPLEMENTER, ROLE_INDEPENDENT_EVALUATOR, ROLE_UNSPECIFIED),
        default=ROLE_UNSPECIFIED,
        help="explicit reporting role; this checklist never grants terminal acceptance",
    )
    parser.add_argument(
        "--artifact-id",
        default="",
        help="legacy label retained for compatibility; computed identity is authoritative",
    )
    args = parser.parse_args()

    print("=" * 60)
    print(f"M-n 29 5-STEP REGRESSION EVIDENCE: claim={args.claim!r}")
    print("=" * 60)

    # Step 1
    print("\n[Step 1] Design 验收 角度")
    crits = design_criteria(args.task_profile)
    print(f"  Designed {len(crits)} criteria.")
    print(f"  Task profile: {args.task_profile}")

    ct = four_critical_thinking(args.claim)
    prims = five_primitives(args.claim, args.task_profile)

    def print_constructive() -> None:
        print("\n[Step 2] Execute — 5 primitives")
        for key, value in prims.items():
            print(f"  {key}: {value[:80]}")

    def print_critical() -> None:
        print("\n[Step 2a] Apply — 4 critical-thinking primitives (adversarial pair)")
        for key, value in ct.items():
            print(f"  {key}: {value[:80]}")

    if args.task_profile == "open-ended":
        print_constructive()
        print_critical()
    else:
        print_critical()
        print_constructive()

    # Step 3
    print("\n[Step 3] Validate")
    pk, ck = validate(prims, crits)
    print(f"  Populated primitive fields: {pk}/5")
    print(f"  Populated structural criteria: {ck}/{len(crits)}")
    print(f"  4 critical-thinking primitives: {len(ct)} (default-on for high-stakes)")
    structurally_complete = pk == 5 and ck == len(crits)
    print("  STRUCTURAL BASELINE ONLY: semantic acceptance still requires evidence.")
    print("  REGRESSION EVIDENCE ONLY: this checklist cannot issue artifact acceptance.")
    print("  EXECUTION_SUCCESS does not equal ARTIFACT_ACCEPTANCE.")

    # Step 4 (reconciliation)
    print("\n[Step 4] Cycle loop check")
    print("  If FAIL items: the canonical controller evaluates the retry gate before looping.")
    print("  Retry owner: src.v4_loop.Loop -> src.retry_gate.evaluate_retry().")
    print("  The gate returns RETRY_ALLOWED, GLOBAL_REPLAN_REQUIRED, ACCEPTANCE_AUTHORITY_UNVERIFIED, or RETRY_CONTEXT_REQUIRED.")

    # Step 5
    print("\n[Step 5] Notify")
    current = compute_current_artifact_identity()
    boundary = execution_success(
        role=args.role,
        artifact_identity=current.identity,
        material_artifact=True,
    )
    boundary = record_regression(boundary, passed=structurally_complete)

    if args.self:
        print(f"  SELF-MODE: agent must apply 5 primitives")
        print(f"  Currently: {pk}/5 primitive prompts populated; {ck}/{len(crits)} criteria defined")
        print("  EXECUTION COMPLETE (checklist execution only)")
        print("  IMPLEMENTATION COMPLETE / READY FOR INDEPENDENT AUDIT")
        print("  This output does not claim terminal artifact acceptance.")
    else:
        print("  Interactive mode: record regression evidence or findings.")

    print(
        "  P30 state: "
        f"{boundary.artifact_state}; artifact acceptance={boundary.artifact_acceptance}"
    )
    print(f"  Computed artifact identity: {current.identity} (clean={current.clean})")
    if args.artifact_id:
        print("  Caller artifact-id ignored; it cannot override computed identity.")

    # Use-case 1: agent self-invocation pre-claim
    print("\n[External trigger usage]")
    print("  Run this script BEFORE reporting implementation completion.")
    print("  Per M-n 32 Guardrail #4 + AGENTS.md 'Task-done-notify reminder'.")
    print("  Per user message 2026-07-16 retrospective 4-FAIL diagnosis.")

    return 0


if __name__ == "__main__":
    sys.exit(main())
