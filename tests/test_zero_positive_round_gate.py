"""Generic regression tests for the zero-positive-test round gate."""

import pytest

from src import v2_round
from src.llm import LLMConfig
from src.v2_agent import Paper, Patch
from src.v2_apply import ApplyResult


@pytest.mark.parametrize(
    ("passed", "failed", "returncode", "expected"),
    [
        (0, 0, 0, "REVERTED"),
        (1, 0, 0, "KEPT"),
        (0, 1, 1, "REVERTED"),
    ],
)
def test_public_run_one_round_requires_positive_test_evidence(
    monkeypatch, tmp_path, passed, failed, returncode, expected
):
    target = tmp_path / "planner.py"
    target.write_text("def plan_task(task):\n    return [task]\n", encoding="utf-8")
    fixed_patch = Patch(
        function="def plan_task(task):\n    return [task]\n",
        test="def test_fixture_patch():\n    assert True\n",
        module=str(target),
    )
    snapshot = str(tmp_path / "planner.py.snapshot")

    monkeypatch.setattr(v2_round, "improve", lambda *args, **kwargs: fixed_patch)
    monkeypatch.setattr(
        v2_round,
        "apply_patch",
        lambda *args, **kwargs: ApplyResult(
            status="APPLIED", target=str(target), snapshot_path=snapshot
        ),
    )
    monkeypatch.setattr(
        v2_round,
        "run_project_tests",
        lambda *args, **kwargs: (passed, failed, returncode, ""),
    )
    monkeypatch.setattr(v2_round, "revert", lambda *args, **kwargs: None)
    monkeypatch.setattr(v2_round, "cleanup_snapshot", lambda *args, **kwargs: None)
    monkeypatch.setattr(v2_round, "log_failure", lambda *args, **kwargs: None)

    result = v2_round.run_one_round(
        paper=Paper(arxiv_id="fixture-paper", title="fixture", abstract="fixture"),
        target_module=str(target),
        project_root=str(tmp_path),
        config=LLMConfig(),
        keep_snapshot_on_kept=False,
        test_path="tests/test_control.py",
    )

    assert result.decision == expected
