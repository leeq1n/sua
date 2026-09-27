# Daily agent Goal Control entrypoint

> L0: The daily `core.agent` command requires an explicit active Goal/Task contract and reviews each tool action before execution.

The command reads a JSON file with one active Goal Contract and one active
Task. The task title on the command line must match the file. For example:

```json
{
  "goal": {
    "goal_id": "report-1",
    "objective": "Deliver the requested report",
    "success_criteria": ["report delivered with cited evidence"],
    "non_goals": ["build a dashboard"],
    "constraints": ["use cited evidence"],
    "status": "ACTIVE",
    "version": 1
  },
  "task": {
    "task_id": "draft-report",
    "title": "Write report",
    "goal_id": "report-1",
    "criteria": ["report delivered with cited evidence"],
    "status": "ACTIVE",
    "version": 1,
    "residency": "HOT"
  }
}
```

After installing `requirements.txt` and configuring the LLM as described in
`.env.example`, run `python -m core.agent --contract goal.json "Write report"`.
`SUA_GOAL_CONTRACT` can supply the file path instead. Without a contract, the
entrypoint returns an error before contacting the model or executing a tool.

The planner receives the active goal, active task, HOT direct dependencies,
and explicitly retrieved knowledge from `ControlPlane.working_context()`.
The raw command text is used only to match the task title. Before each tool
call, a separate model review must return an exact linked success criterion;
the control plane checks the current goal checksum and action identity again
before the tool executes. A missing or malformed review rejects the action.
`ControlPlane.traces` records authorized **attempts**, not completed outcomes.
The command reports failure if any planned step is rejected or a tool fails;
a successful tool run is still not proof that the goal criterion was met.

The host or user must provide the contract. This entrypoint does not infer a
Goal Contract from natural language, classify later human feedback, prove the
model's semantic review is correct, or show reduced drift in a live agent.
Those claims require a held-out behavioral comparison. The self-upgrade
pipeline and other agent runtimes need their own explicit host adapters.

For deterministic drift and resume scenarios, see
[`GOAL_CONTROL_REGRESSION.md`](GOAL_CONTROL_REGRESSION.md).
