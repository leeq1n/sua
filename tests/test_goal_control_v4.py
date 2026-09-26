"""Exercise Goal Control at the v4 planning and execution boundary."""

import pytest

from src.goal_control import ControlPlane, DriftError, Goal, Task
from src.goal_control_v4 import GoalGuardedExecutor, GoalReviewingThinker, step_action
from src.v4_executor import MockExecutor
from src.v4_loop import Loop, LoopStatus
from src.v4_thinker import MockThinker, Step, Thinker


def setup_guarded_loop(step, *, authorize=True):
    control = ControlPlane()
    control.add_goal(Goal("G1", "Deliver report", ("report delivered",)))
    control.add_task(Task("T1", "Write report", "G1", ("report delivered",)),
                     control.goal_checksum("G1"))
    if authorize:
        control.allow_action("T1", step_action(step), "report delivered")
    delegate = MockExecutor()
    guarded = GoalGuardedExecutor(delegate, control, "T1",
                                  lambda _step: "report delivered")
    return Loop(MockThinker([step]), guarded), delegate, control


def test_authorized_step_reaches_executor_and_records_trace():
    step = Step("write", {"target": "report.md"})
    loop, delegate, control = setup_guarded_loop(step)
    result = loop.run("deliver report")
    assert result.status is LoopStatus.SUCCEEDED
    assert delegate.call_log == [step]
    assert control.traces == [(step_action(step), "T1", "report delivered", "G1")]


def test_unapproved_step_is_blocked_before_side_effect():
    step = Step("rewrite_controller", {})
    loop, delegate, control = setup_guarded_loop(step, authorize=False)
    result = loop.run("deliver report")
    assert result.status is LoopStatus.FAILED
    assert delegate.call_log == []
    assert control.traces == []


def test_step_args_are_part_of_action_identity():
    approved = Step("write", {"target": "report.md"})
    actual = Step("write", {"target": "unrelated.md"})
    loop, delegate, control = setup_guarded_loop(actual, authorize=False)
    control.allow_action("T1", step_action(approved), "report delivered")
    result = loop.run("deliver report")
    assert result.status is LoopStatus.FAILED
    assert delegate.call_log == []


def test_goal_change_invalidates_preapproved_step(tmp_path):
    step = Step("write", {"target": "report.md"})
    loop, delegate, control = setup_guarded_loop(step)
    control.capsule_dir = tmp_path
    control.revise_goal("G1", control.goal_checksum("G1"),
                        success_criteria=("revised report delivered",))
    result = loop.run("deliver report")
    assert result.status is LoopStatus.FAILED
    assert delegate.call_log == []


def test_dynamic_plan_is_reviewed_before_each_execution():
    class DynamicThinker(Thinker):
        def plan(self, prompt):
            return [Step("write", {"target": "report.md"}),
                    Step("write", {"target": "unrelated.md"})]

    control = ControlPlane()
    control.add_goal(Goal("G1", "Deliver report", ("report delivered",)))
    control.add_task(Task("T1", "Write report", "G1", ("report delivered",)),
                     control.goal_checksum("G1"))
    reviewed = []

    def review(step, context):
        reviewed.append((step.args["target"], context["goal"].goal_id))
        return "report delivered" if step.args["target"] == "report.md" else None

    thinker = GoalReviewingThinker(DynamicThinker(), control, "T1", review)
    delegate = MockExecutor()
    executor = GoalGuardedExecutor(delegate, control, "T1",
                                   lambda _step: "report delivered")
    result = Loop(thinker, executor).run("deliver report")
    assert reviewed == [("report.md", "G1"), ("unrelated.md", "G1")]
    assert result.status is LoopStatus.FAILED
    assert delegate.call_log == [Step("write", {"target": "report.md"})]
    assert len(control.traces) == 1


def test_new_plan_review_revokes_prior_step_authorization():
    step = Step("write", {"target": "report.md"})
    loop, delegate, control = setup_guarded_loop(step)
    loop.thinker = GoalReviewingThinker(MockThinker([step]), control, "T1",
                                        lambda _step, _context: None)
    result = loop.run("deliver report")
    assert result.status is LoopStatus.FAILED
    assert delegate.call_log == []


def test_thinker_receives_only_resident_context():
    class CapturingThinker(Thinker):
        def plan(self, prompt):
            self.prompt_seen = prompt
            return [Step("write", {"target": "report.md"})]

    control = ControlPlane()
    control.add_goal(Goal("G1", "Deliver report", ("report delivered",)))
    control.add_goal(Goal("G2", "OLD_GOAL_SECRET", ("old result",)))
    control.add_task(Task("T1", "Write report", "G1", ("report delivered",)),
                     control.goal_checksum("G1"))
    control.add_task(Task("T2", "COLD_TASK_SECRET", "G1", ("report delivered",),
                          status="WAITING_USER", residency="COLD"),
                     control.goal_checksum("G1"))
    control.durable_knowledge["relevant"] = "APPROVED_NOTE"
    control.durable_knowledge["unretrieved"] = "COLD_KNOWLEDGE_SECRET"
    control.retrieve_knowledge("T1", "relevant")
    delegate = CapturingThinker()
    reviewer = GoalReviewingThinker(delegate, control, "T1",
                                    lambda _step, _context: "report delivered")
    reviewer.plan("OLD_HISTORY_SECRET")
    assert "Deliver report" in delegate.prompt_seen
    assert "Write report" in delegate.prompt_seen
    assert "APPROVED_NOTE" in delegate.prompt_seen
    for excluded in ("OLD_GOAL_SECRET", "COLD_TASK_SECRET",
                     "COLD_KNOWLEDGE_SECRET", "OLD_HISTORY_SECRET"):
        assert excluded not in delegate.prompt_seen


def test_inactive_task_cannot_plan_using_another_tasks_context():
    control = ControlPlane()
    control.add_goal(Goal("G1", "Deliver report", ("report delivered",)))
    control.add_task(Task("T1", "Write report", "G1", ("report delivered",)),
                     control.goal_checksum("G1"))
    control.add_task(Task("T2", "Other task", "G1", ("report delivered",)),
                     control.goal_checksum("G1"))
    reviewer = GoalReviewingThinker(MockThinker([Step("write")]), control, "T2",
                                    lambda _step, _context: "report delivered")
    with pytest.raises(DriftError):
        reviewer.plan("anything")


def test_review_callback_cannot_mutate_live_goal_through_context():
    control = ControlPlane()
    control.add_goal(Goal("G1", "Deliver report", ("report delivered",)))
    control.add_task(Task("T1", "Write report", "G1", ("report delivered",)),
                     control.goal_checksum("G1"))

    def review(_step, context):
        context["goal"].objective = "Mutated copy"
        return "report delivered"

    reviewer = GoalReviewingThinker(MockThinker([Step("write")]), control,
                                    "T1", review)
    reviewer.plan("anything")
    assert control.goals["G1"].objective == "Deliver report"
