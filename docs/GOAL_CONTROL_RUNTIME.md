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
`.env.example`, run `python -m core.agent --contract goal.json --capsule
task-state.json --capsule-key host-owned.key "Write report"`.
`SUA_GOAL_CONTRACT` can supply the file path instead. Without a contract, the
entrypoint returns an error before contacting the model or executing a tool.

The planner receives the active goal, active task, HOT direct dependencies,
and explicitly retrieved knowledge from `ControlPlane.working_context()`.
The raw command text is used only to match the task title. Before each tool
call, a separate model review must return an exact linked success criterion;
the control plane checks the current goal checksum and action identity again
before the tool executes. A missing or malformed review rejects the action.
`ControlPlane.traces` records authorized **attempts**, not completed outcomes.
The daily command writes each task's Action→Task→Criterion→Goal links into
the durable capsule and restores them before a resumed task proceeds. The
capsule path is mandatory for the command. The returned task record path is
where a later process can audit those links; it does not certify tool outcome.
The daily command refuses to resume an older capsule without a trace field;
its past action links cannot be reconstructed.
The required `--capsule-key` file must contain at least 32 random bytes and
be kept by the host outside the repository and capsule location. The capsule
has an HMAC over its contents; changing an action, criterion, contract snapshot,
or task state without that key causes resume to fail. A lost key prevents
recovery; a copied or compromised key cannot establish independent provenance.
Programmatic `ControlPlane` use without a key remains a structural reference
contract and cannot claim authenticated persistence.
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

With the required `--capsule task-state.json`, after a run the task becomes
`DONE` only after host evidence verification, `BLOCKED`
after execution failure, or `SUSPENDED` while completion remains unverified.
The command returns a named resume trigger; a later invocation must supply
the same `--capsule` and `--resume-trigger` before the task can become HOT.
Terminal capsules cannot be resumed. The capsule stores explicit feedback
routes as well as task identity, version, dependencies, next action, and
blocker. After method feedback, only that task's latest message is explicitly
retrieved into its working context on resume.

The daily command can route a user's explicit category without contacting the
model: `--contract goal.json --capsule task-state.json --feedback-kind
method_feedback --feedback-message "try another method" --capsule-key
host-owned.key "Write report"`.
The allowed categories are `method_feedback`, `criterion_correction`,
`goal_mutation`, and `new_task`. The route persists before the task leaves HOT.
After `criterion_correction`, the old task cannot resume. Supply a revised
contract with the same objective, a higher goal version, and criteria linked
to that goal; then run `--contract revised.json --capsule task-state.json
--capsule-key host-owned.key
--replan-next-action "cite sources" --replan-trigger "replan reviewed"
"Write report"`. The command persists the revised cold task before it may
resume with `--resume-trigger "replan reviewed"`. An objective change under
the same goal identity is rejected. `goal_mutation` archives the old task;
the user must supply a new Goal Contract. The host still has to classify
feedback correctly and check that the named resume event really occurred.

The host or user must provide the contract. This entrypoint does not infer a
Goal Contract from natural language, classify human feedback, prove the
model's semantic review is correct, or show reduced drift in a live agent.
Those claims require a held-out behavioral comparison. The self-upgrade
pipeline and other agent runtimes need their own explicit host adapters.

For deterministic drift and resume scenarios, see
[`GOAL_CONTROL_REGRESSION.md`](GOAL_CONTROL_REGRESSION.md).
