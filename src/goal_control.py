"""Small, runtime-neutral reference contract for goal and context control.

This is a deterministic control surface, not a classifier of natural language.
The caller must supply explicit action/criterion links and feedback categories.
"""

from dataclasses import dataclass, field
from hashlib import sha256
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


@dataclass
class ControlPlane:
    goals: Dict[str, Goal] = field(default_factory=dict)
    tasks: Dict[str, Task] = field(default_factory=dict)
    active_goal_id: str = ""
    active_task_id: str = ""
    durable_knowledge: Dict[str, str] = field(default_factory=dict)
    retrieved_knowledge: Tuple[str, ...] = ()
    allowed_actions: Dict[str, set] = field(default_factory=dict)
    traces: list = field(default_factory=list)
    capsules: Dict[str, tuple] = field(default_factory=dict)

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
        if goal.status == "ACTIVE":
            self.active_goal_id = goal.goal_id

    def add_task(self, task: Task):
        goal = self.goals.get(task.goal_id)
        if goal is None or not set(task.criteria) <= set(goal.success_criteria):
            raise DriftError("task criteria must link to its goal")
        if task.task_id in self.tasks or task.status not in TASK_STATUSES:
            raise ValueError("invalid or duplicate task identity/status")
        self.tasks[task.task_id] = task
        if task.status == "ACTIVE" and not self.active_task_id:
            self.active_task_id = task.task_id

    def allow_action(self, task_id: str, action: str):
        """Record a reviewed action plan; free text is never self-authorizing."""
        self.allowed_actions.setdefault(task_id, set()).add(action)

    def activate_task(self, task_id: str):
        task = self.tasks[task_id]
        if task.status != "ACTIVE" or task.residency != "HOT" or self.goals[task.goal_id].status != "ACTIVE":
            raise DriftError("task is not active and resident")
        self.active_goal_id, self.active_task_id = task.goal_id, task_id

    def record_action(self, action: str, task_id: str, criterion: str):
        task = self.tasks.get(task_id)
        if (task is None or task.status != "ACTIVE" or task.residency != "HOT"
                or task_id != self.active_task_id or task.goal_id != self.active_goal_id):
            raise DriftError("action has no active task and goal")
        goal = self.goals[task.goal_id]
        if (goal.status != "ACTIVE" or criterion not in task.criteria
                or criterion not in goal.success_criteria or action in goal.non_goals
                or action not in self.allowed_actions.get(task_id, set())):
            raise DriftError("action is not authorized by task and criterion")
        trace = (action, task_id, criterion, goal.goal_id)
        self.traces.append(trace)
        return trace

    def route_feedback(self, task_id: str, message: str, kind: str):
        if task_id not in self.tasks:
            raise KeyError(task_id)
        if kind == "method_feedback":
            self.tasks[task_id].version += 1
            self.allowed_actions.pop(task_id, None)
            return task_id
        if kind in {"criterion_correction", "goal_mutation", "new_task"}:
            raise DriftError(f"{kind} needs an explicit goal/task contract update")
        raise ValueError("unknown feedback category")

    def revise_goal(self, goal_id: str, expected_checksum: str, *, objective=None,
                    success_criteria=None, non_goals=None, constraints=None):
        goal = self.goals[goal_id]
        if expected_checksum != self.goal_checksum(goal_id) or goal.status != "ACTIVE":
            raise DriftError("goal changed since feedback was classified")
        for key, value in (("objective", objective), ("success_criteria", success_criteria),
                           ("non_goals", non_goals), ("constraints", constraints)):
            if value is not None:
                setattr(goal, key, value)
        goal.version += 1
        for task in self.tasks.values():
            if task.goal_id == goal_id and not set(task.criteria) <= set(goal.success_criteria):
                task.status, task.residency = "SUSPENDED", "COLD"
        self.allowed_actions.clear()

    def supersede_goal(self, old_id: str, new_id: str):
        if old_id not in self.goals or new_id not in self.goals:
            raise KeyError("goal not found")
        self.goals[old_id].status = "SUPERSEDED"
        self.active_goal_id = new_id
        for task in self.tasks.values():
            if task.goal_id == old_id and task.status == "ACTIVE":
                task.status, task.residency = "SUPERSEDED", "ARCHIVED"
        self.allowed_actions.clear()

    def wait_for_user(self, task_id: str, trigger: str):
        self.transition_task(task_id, "WAITING_USER", trigger)

    def transition_task(self, task_id: str, status: str, trigger: str = ""):
        if status not in TASK_STATUSES or status == "ACTIVE":
            raise ValueError("use resume or activate_task for ACTIVE")
        task = self.tasks[task_id]
        task.status, task.resume_trigger = status, trigger
        task.residency = "ARCHIVED" if status in {"SUPERSEDED", "DONE", "ABANDONED"} else "COLD"
        if task.residency == "COLD":
            self.capsules[task_id] = self.capture(task_id)
        else:
            self.capsules.pop(task_id, None)
        self.allowed_actions.pop(task_id, None)

    def capture(self, task_id: str):
        task = self.tasks[task_id]
        return (task.task_id, task.goal_id, self.goals[task.goal_id].version,
                self.goal_checksum(task.goal_id), task.version, task.title,
                task.criteria, task.resume_trigger)

    def pause_and_persist(self, task_id: str, status: str, path, trigger: str = ""):
        """Write a task capsule atomically before moving it out of HOT."""
        if status not in {"WAITING_USER", "BLOCKED", "SUSPENDED"}:
            raise ValueError("only resumable statuses can be persisted")
        task = self.tasks[task_id]
        if task.status != "ACTIVE" or task.residency != "HOT":
            raise DriftError("only an active task can be paused")
        previous_trigger = task.resume_trigger
        task.resume_trigger = trigger
        capsule = self.capture(task_id)
        destination = Path(path)
        temporary = None
        try:
            with tempfile.NamedTemporaryFile("w", encoding="utf-8", dir=destination.parent,
                                             prefix=destination.name + ".", suffix=".tmp",
                                             delete=False) as stream:
                temporary = Path(stream.name)
                json.dump(capsule, stream, ensure_ascii=False)
                stream.flush()
                os.fsync(stream.fileno())
            os.replace(temporary, destination)
        except Exception:
            task.resume_trigger = previous_trigger
            if temporary is not None:
                temporary.unlink(missing_ok=True)
            raise
        self.transition_task(task_id, status, trigger)
        return capsule

    def resume_from_file(self, task_id: str, path):
        """Re-admit a persisted capsule only when the live contracts match."""
        with Path(path).open("r", encoding="utf-8") as stream:
            raw = json.load(stream)
        if not isinstance(raw, list) or len(raw) != 8 or not isinstance(raw[6], list):
            raise DriftError("invalid capsule")
        capsule = tuple(raw[:6]) + (tuple(raw[6]), raw[7])
        if capsule != self.capture(task_id):
            raise DriftError("persisted capsule does not match current contracts")
        self.capsules[task_id] = capsule
        self.resume(task_id, capsule)

    def resume(self, task_id: str, capsule):
        task = self.tasks[task_id]
        if (capsule != self.capsules.get(task_id) or capsule != self.capture(task_id)
                or task.status not in {"WAITING_USER", "BLOCKED", "SUSPENDED"}
                or self.goals[task.goal_id].status != "ACTIVE"):
            raise DriftError("resume capsule or goal is stale")
        task.status, task.residency = "ACTIVE", "HOT"
        del self.capsules[task_id]
        self.active_goal_id, self.active_task_id = task.goal_id, task_id

    def working_context(self):
        goal = self.goals.get(self.active_goal_id)
        task = self.tasks.get(self.active_task_id)
        visible = {}
        if goal and goal.status == "ACTIVE" and task and task.status == "ACTIVE":
            visible[task.task_id] = task
            for dep_id in task.dependencies:
                dep = self.tasks.get(dep_id)
                if dep and dep.goal_id == goal.goal_id and dep.residency == "HOT":
                    visible[dep_id] = dep
        return {"goal": goal if goal and goal.status == "ACTIVE" else None,
                "tasks": visible,
                "knowledge": {key: self.durable_knowledge[key]
                              for key in self.retrieved_knowledge if key in self.durable_knowledge}}
