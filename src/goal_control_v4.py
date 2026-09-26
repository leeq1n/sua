"""Optional Goal Control adapter for the v4 Thinker/Executor loop.

The host reviews a concrete Step and calls ControlPlane.allow_action with
step_action(step) and a goal criterion before the executor receives it.
"""

import json
from copy import deepcopy
from dataclasses import asdict
from typing import Callable

from src.goal_control import ControlPlane, DriftError
from src.v4_executor import Executor, Result
from src.v4_thinker import Plan, Step, Thinker


def step_action(step: Step) -> str:
    """Stable identity for the whole planned action, including its arguments."""
    return json.dumps(step.to_dict(), ensure_ascii=False, sort_keys=True,
                      separators=(",", ":"))


class GoalReviewingThinker(Thinker):
    """Plan from HOT context, then let the host review each planned step.

    The raw Loop prompt is deliberately not forwarded. The host must first
    reflect current user intent in its Goal and Task contracts.
    """

    def __init__(self, delegate: Thinker, control: ControlPlane, task_id: str,
                 review_step: Callable[[Step, dict], str | None]):
        super().__init__()
        self.delegate = delegate
        self.control = control
        self.task_id = task_id
        self.review_step = review_step

    def plan(self, prompt: str) -> Plan:
        self.control.allowed_actions.pop(self.task_id, None)
        context = deepcopy(self.control.working_context())
        if context["goal"] is None or self.task_id not in context["tasks"]:
            raise DriftError("planning needs the current HOT goal and task")
        resident_prompt = (
            "Plan actions for the current task using only this context. "
            "Return a JSON array of {\"name\": string, \"args\": object} steps.\n"
            + json.dumps({
                "goal": asdict(context["goal"]),
                "tasks": {key: asdict(task) for key, task in context["tasks"].items()},
                "knowledge": context["knowledge"],
            }, ensure_ascii=False, sort_keys=True)
        )
        plan = self.delegate.plan(resident_prompt)
        for step in plan:
            criterion = self.review_step(step, context)
            if criterion:
                try:
                    self.control.allow_action(self.task_id, step_action(step), criterion)
                except DriftError:
                    # The execution wrapper still rejects this step. The
                    # reviewer cannot authorize a stale or unlinked action.
                    pass
        return plan


class GoalGuardedExecutor(Executor):
    """Reject an unapproved step before delegating any side effect."""

    def __init__(self, delegate: Executor, control: ControlPlane, task_id: str,
                 criterion_for_step: Callable[[Step], str]):
        super().__init__()
        self.delegate = delegate
        self.control = control
        self.task_id = task_id
        self.criterion_for_step = criterion_for_step

    def execute(self, step: Step) -> Result:
        self.call_log.append(step)
        try:
            criterion = self.criterion_for_step(step)
            self.control.record_action(step_action(step), self.task_id, criterion)
        except Exception as exc:
            return Result(success=False, error=f"goal guard rejected step: {exc}",
                          step_name=step.name)
        return self.delegate.execute(step)
