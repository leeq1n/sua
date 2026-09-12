"""src/v4_loop.py - Loop controller (Think -> Execute -> Observe).

Per LITERATURE:
  - Self-Harness 40->62%: iterative harness (re-plan on failure)
  - Nate Berkopec: 'verifiable + looped' agent architecture
  - Signal-to-Fix Loop (Droid 2026): telemetry -> signal -> fix
  - Lilian Weng: harness as important as model

This module is step 2.3 of v3.0.2.  Thinker (2.1) produces a Plan.
Executor (2.2) runs each Step.  Loop (2.3) drives them together:
  1. Thinker.plan(prompt) -> Plan
  2. for each Step: Executor.execute(Step) -> Result
  3. Observe: collect all Results into LoopResult
  4. Decision: all success -> SUCCEEDED, any fail -> FAILED
  5. Optional: gate-authorized re-plan on failure; max_retries is only a
     quantity ceiling

Public API:
  LoopStatus(Enum)         : SUCCEEDED | FAILED | PARTIAL
  LoopResult               : status + plan + per-step results
  Loop(thinker, executor)  : orchestrate Think -> Execute -> Observe
    .run(prompt, max_retries=0) -> LoopResult
"""
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Callable, List, Optional

from src.v4_thinker import Thinker, Plan
from src.v4_executor import Executor, Result
from src.retry_gate import RetryDecision, RetryGateResult, RetryProposal, RetryState, evaluate_retry


class LoopStatus(Enum):
    """Outcome of a Loop.run()."""
    SUCCEEDED = "SUCCEEDED"  # all steps succeeded
    FAILED = "FAILED"        # at least one step failed
    PARTIAL = "PARTIAL"      # some succeeded, some failed


@dataclass
class LoopResult:
    """One Loop.run() outcome.  Per P19: intermediate state observable."""
    status: LoopStatus
    plan: Plan
    results: List[Result] = field(default_factory=list)
    attempts: int = 1
    elapsed_s: float = 0.0
    retry_decision: Optional[RetryDecision] = None
    retry_state: Optional[RetryState] = None
    retry_reason: Optional[str] = None

    def to_dict(self) -> dict:
        return {
            "status": self.status.value,
            "attempts": self.attempts,
            "elapsed_s": self.elapsed_s,
            "plan": [s.to_dict() for s in self.plan],
            "results": [r.to_dict() for r in self.results],
            "retry_decision": (
                self.retry_decision.value if self.retry_decision else None
            ),
            "retry_state": self.retry_state.to_dict() if self.retry_state else None,
            "retry_reason": self.retry_reason,
        }


# ── Loop controller ─────────────────────────────────────────────

class Loop:
    """Orchestrate Thinker -> Executor -> Observe.

    Args:
      thinker:  a Thinker (MockThinker / JsonThinker / custom)
      executor: an Executor (MockExecutor / FunctionExecutor / custom)
    """

    def __init__(self, thinker: Thinker, executor: Executor):
        self.thinker = thinker
        self.executor = executor
        # Per P19: log every loop run for observability
        self.history: List[LoopResult] = []

    def run(
        self,
        prompt: str,
        max_retries: int = 0,
        *,
        retry_state: Optional[RetryState] = None,
        retry_proposal: Optional[RetryProposal] = None,
        retry_proposal_factory: Optional[
            Callable[[RetryState, int], RetryProposal]
        ] = None,
    ) -> LoopResult:
        """Run the loop.  Returns LoopResult.

        Args:
          prompt: input to Thinker
          max_retries: hard quantity ceiling for re-plans (default 0); it does
            not authorize a retry without retry_state plus retry_proposal

        Per P7 奥卡姆: default no retry.  A positive ceiling still requires
        explicit retry context for every gate-authorized re-plan.
        """
        t0 = time.time()
        attempt = 0
        last_plan: Plan = []
        last_results: List[Result] = []
        last_gate_result: Optional[RetryGateResult] = None
        last_retry_decision: Optional[RetryDecision] = None
        last_retry_reason: Optional[str] = None

        while attempt <= max_retries:
            attempt += 1
            plan = self.thinker.plan(prompt)
            last_plan = plan
            results: List[Result] = []
            for step in plan:
                r = self.executor.execute(step)
                results.append(r)
                # Fail-fast: stop on first failure (P9 hard rule)
                if not r.success:
                    break
            last_results = results
            # If all succeeded, we're done
            if all(r.success for r in results) and len(results) == len(plan):
                break

            if attempt > max_retries:
                break

            # A canonical retry is never authorized by max_retries alone.
            # max_retries is only the quantity ceiling; admissibility must
            # have an explicit prior state and proposal for the one gate.
            if retry_state is None:
                last_retry_decision = RetryDecision.RETRY_CONTEXT_REQUIRED
                last_retry_reason = (
                    "retry context is required before a canonical retry; "
                    "max_retries is only a quantity ceiling"
                )
                break
            if retry_proposal is None and retry_proposal_factory is None:
                last_retry_decision = RetryDecision.RETRY_CONTEXT_REQUIRED
                last_retry_reason = (
                    "retry proposal is required before a canonical retry; "
                    "max_retries is only a quantity ceiling"
                )
                break

            proposed = (
                retry_proposal_factory(retry_state, attempt)
                if retry_proposal_factory
                else retry_proposal
            )
            if proposed is None:
                last_retry_decision = RetryDecision.RETRY_CONTEXT_REQUIRED
                last_retry_reason = "retry proposal factory returned no retry context"
                break
            last_gate_result = evaluate_retry(retry_state, proposed)
            retry_state = last_gate_result.state
            last_retry_decision = last_gate_result.decision
            last_retry_reason = last_gate_result.reason
            if last_gate_result.decision is not RetryDecision.RETRY_ALLOWED:
                break

        # Decide status
        # Per P9 + fail-fast: strict.  Fail-fast means we stopped early,
        # so any failure during execution is FAILED (not PARTIAL).
        if not last_results:
            status = LoopStatus.FAILED
        elif (all(r.success for r in last_results)
              and len(last_results) == len(last_plan)):
            status = LoopStatus.SUCCEEDED
        else:
            # Any failure (whether fail-fast or all-then-decide) is FAILED.
            status = LoopStatus.FAILED

        result = LoopResult(
            status=status,
            plan=last_plan,
            results=last_results,
            attempts=attempt,
            elapsed_s=time.time() - t0,
            retry_decision=(
                last_gate_result.decision
                if last_gate_result
                else last_retry_decision
            ),
            retry_state=(last_gate_result.state if last_gate_result else retry_state),
            retry_reason=(
                last_gate_result.reason if last_gate_result else last_retry_reason
            ),
        )
        self.history.append(result)
        return result
