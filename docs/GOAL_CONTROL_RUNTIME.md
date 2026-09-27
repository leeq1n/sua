# Daily agent Goal Control entrypoint

> L0: The daily `core.agent` command requires an explicit active Goal/Task contract and reviews each tool action before execution.
> Last P20-verified: 2026-09-27

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
The runtime distinguishes `execution_succeeded` from `goal_complete`. A host
can provide `verify_completion` to judge evidence against the current goal.
The command accepts `--verifier path/to/check.py`; that host-owned file must
define `verify_completion(context, logs)` and return a dictionary with
`passed: true` plus a nonempty `evidence` string for every current goal success
criterion. The checker should inspect actual artifacts or external results;
the model's answer and a tool's successful exit are insufficient. The command
loads and executes this Python file with the user's privileges, so only a
trusted host-owned checker should be supplied. Without a verifier,
`goal_complete` is unknown and `success` remains false.
The command exits nonzero on a rejected action, failed tool, or unverified
goal. A successful tool run is not proof that the goal criterion was met.
The built-in shell tool treats a nonzero process exit code as a failed tool
invocation, even when the command prints no output.

The host or user must provide the contract. This entrypoint does not infer a
Goal Contract from natural language, classify later human feedback, prove the
model's semantic review is correct, or show reduced drift in a live agent.
Those claims require a held-out behavioral comparison. The self-upgrade
pipeline and other agent runtimes need their own explicit host adapters.

For deterministic drift and resume scenarios, see
[`GOAL_CONTROL_REGRESSION.md`](GOAL_CONTROL_REGRESSION.md).
