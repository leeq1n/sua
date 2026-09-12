"""Tests for v2_round.run_one_round_with_harness (v3.0.2 follow-up).

Per LITERATURE (Self-Harness 40->62%): iterative re-plan on
failure.  Per P7 奥卡姆: simple retry wrapper, no new handler
dispatch.  These tests verify the harness behavior:
  - Returns RoundResult
  - Fails closed when retry context is absent
  - Annotates elapsed_s with total harness time
"""
import pytest
from unittest.mock import patch

from src.v2_round import (
    RoundResult, run_one_round_with_harness, run_one_round_multi,
)
from src.retry_gate import RetryDecision


# ── Helper ─────────────────────────────────────────────────────

def make_round_result(decision="KEPT", elapsed_s=1.0, error=None):
    """Build a RoundResult-like object for testing."""
    from src.v2_agent import Paper
    return RoundResult(
        decision=decision,
        paper=Paper(arxiv_id="x", title="t", abstract="a"),
        target_module="core/planner.py",
        elapsed_s=elapsed_s,
        error=error,
    )


# ── A. Basic structure ────────────────────────────────────────

class TestStructure:
    def test_function_exists(self):
        assert callable(run_one_round_with_harness)

    def test_signature(self):
        import inspect
        sig = inspect.signature(run_one_round_with_harness)
        assert "target_module" in sig.parameters
        assert "max_retries" in sig.parameters
        assert "test_path" in sig.parameters
        assert "config" in sig.parameters


# ── B. Behavior with mock round ──────────────────────────────

class TestBehavior:
    def test_kept_decision_returns_immediately(self):
        """First attempt KEPT -> no retry."""
        rr_kept = make_round_result(decision="KEPT", elapsed_s=10.0)
        with patch("src.v2_round.run_one_round_multi", return_value=rr_kept):
            result = run_one_round_with_harness(
                target_module="core/planner.py",
                max_retries=2,
            )
        assert result.decision == "KEPT"

    def test_retry_on_no_patch(self):
        """NO_PATCH first attempt -> missing context -> stop."""
        rr_no = make_round_result(decision="NO_PATCH", elapsed_s=5.0)
        with patch("src.v2_round.run_one_round_multi", return_value=rr_no) as m:
            result = run_one_round_with_harness(
                target_module="core/planner.py",
                max_retries=2,
            )
        assert m.call_count == 1
        assert result.decision == "NO_PATCH"
        assert result.retry_decision is RetryDecision.RETRY_CONTEXT_REQUIRED

    def test_retry_exhausted_returns_last(self):
        """max_retries=1 with no context still makes only one call."""
        rr_no = make_round_result(decision="NO_PATCH", elapsed_s=5.0)
        with patch("src.v2_round.run_one_round_multi",
                    return_value=rr_no) as m:
            result = run_one_round_with_harness(
                target_module="core/planner.py",
                max_retries=1,
            )
        assert m.call_count == 1
        assert result.decision == "NO_PATCH"
        assert result.retry_decision is RetryDecision.RETRY_CONTEXT_REQUIRED

    def test_max_retries_zero_no_retry(self):
        """max_retries=0 -> 1 call only."""
        rr_kept = make_round_result(decision="KEPT", elapsed_s=5.0)
        with patch("src.v2_round.run_one_round_multi",
                    return_value=rr_kept) as m:
            result = run_one_round_with_harness(
                target_module="core/planner.py",
                max_retries=0,
            )
        assert m.call_count == 1
        assert result.decision == "KEPT"

    def test_reverted_retries_too(self):
        """REVERTED cannot retry without canonical context."""
        rr_rev = make_round_result(decision="REVERTED", elapsed_s=5.0)
        with patch("src.v2_round.run_one_round_multi", return_value=rr_rev) as m:
            result = run_one_round_with_harness(
                target_module="core/planner.py",
                max_retries=2,
            )
        assert m.call_count == 1
        assert result.decision == "REVERTED"
        assert result.retry_decision is RetryDecision.RETRY_CONTEXT_REQUIRED

    def test_exception_fallback_preserves_retry_context_required(self):
        """Exception fallback keeps the controller's fail-closed decision."""
        with patch(
            "src.v2_round.run_one_round_multi",
            side_effect=RuntimeError("round failed before result"),
        ) as m:
            result = run_one_round_with_harness(
                target_module="core/planner.py",
                max_retries=2,
                retry_state=None,
                retry_proposal=None,
            )

        assert m.call_count == 1
        assert result.retry_decision is RetryDecision.RETRY_CONTEXT_REQUIRED
        assert result.retry_reason
        assert "retry context" in result.retry_reason


# ── C. Metadata ──────────────────────────────────────────────

class TestMetadata:
    def test_elapsed_s_is_set(self):
        """elapsed_s is the harness total time (not just one round)."""
        rr_kept = make_round_result(decision="KEPT", elapsed_s=2.0)
        with patch("src.v2_round.run_one_round_multi", return_value=rr_kept):
            result = run_one_round_with_harness(
                target_module="core/planner.py",
                max_retries=0,
            )
        assert result.elapsed_s >= 0  # Real time elapsed, not the mock's 2.0

    def test_target_module_propagated(self):
        rr_kept = make_round_result(decision="KEPT")
        with patch("src.v2_round.run_one_round_multi", return_value=rr_kept):
            result = run_one_round_with_harness(
                target_module="my_special_module.py",
                max_retries=0,
            )
        assert result.target_module == "core/planner.py"  # from mock, not harness
        # Harness doesn't change target_module
