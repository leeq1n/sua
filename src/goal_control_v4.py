"""Optional Goal Control adapter for the v4 Thinker/Executor loop.

The host reviews a concrete Step and calls ControlPlane.allow_action with
step_action(step) and a goal criterion before the executor receives it.
"""

import json
from typing import Callable

from src.goal_control import ControlPlane
from src.v4_executor import Executor, Result
from src.v4_thinker import Step


def step_action(step: Step) -> str:
    """Stable identity for the whole planned action, including its arguments."""
    return json.dumps(step.to_dict(), ensure_ascii=False, sort_keys=True,
                      separators=(",", ":"))


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
