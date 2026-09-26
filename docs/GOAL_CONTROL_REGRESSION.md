# Goal control regression baseline

> L0: Frozen structural scenarios for task drift and context eviction; live-agent behavior remains unmeasured.

Baseline before this change: `M-context-snapshot` described capture and restore
but no admission/eviction; `M-task-lifecycle` had four work phases without
stable task identity or paused/superseded statuses; `PROJECT_STATE.md` and
`HANDOFF.md` loaded old Phase A and P30 narrative by default. A task title
could therefore carry revision/feedback history while unfinished work stayed
in the hot path. These are repository observations, not a measured agent
failure rate.

| Scenario | Invariant checked | Reference test |
|---|---|---|
| Proxy drift | A method is not promoted to the objective | `test_action_requires_goal_trace` |
| Subtask drift | Unlinked work cannot execute as active task action | `test_action_requires_goal_trace` |
| Feedback drift | Method feedback retains goal; mutations require versioned update | `test_feedback_does_not_silently_mutate_goal`, `test_goal_checksum_rejects_stale_feedback_and_suspends_old_criterion` |
| Superseded goal leakage | Old goal/task absent from working context | `test_superseded_goal_is_not_resident` |
| Meta drift | Improving the controller requires its own authorized link | `test_action_requires_goal_trace` |
| Resume fidelity | Paused capsule matches current identity and goal | `test_resume_fidelity_and_eviction` |
| Traceability | Every recorded action has Task, Criterion, Goal IDs | `test_traceability_and_dependencies` |

The reference implementation in `src/goal_control.py` checks explicit inputs.
It does not classify natural language, persist capsules across processes, or
prove that a live agent follows the rules. A fresh, blinded behavioral
comparison is required before claiming drift reduction or resume improvement.
