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
| Feedback drift | Router separates method, criterion, goal mutation, and new-task feedback; criterion correction suspends task plans; objective mutation needs a successor goal | `test_feedback_does_not_silently_mutate_goal`, `test_feedback_router_distinguishes_contract_updates`, `test_method_feedback_cannot_modify_inactive_task`, `test_objective_mutation_requires_successor_goal` |
| Superseded goal leakage | Old goal/task absent from working context; adding another ACTIVE goal cannot mix goal and task identities | `test_superseded_goal_is_not_resident`, `test_adding_another_active_goal_keeps_context_consistent` |
| Meta drift | Improving the controller requires its own authorized link | `test_action_requires_goal_trace` |
| Resume fidelity | Paused capsule matches identity, goal version, dependencies, next action, blocker, and named trigger after file persistence | `test_resume_fidelity_and_eviction`, `test_resume_rejects_capsule_after_goal_version_changes`, `test_resume_needs_matching_named_trigger`, `test_capsule_persists_before_eviction_and_resumes_in_fresh_controller`, `test_resume_capsule_preserves_dependencies_next_action_and_blocker` |
| Traceability | Action authorization binds the exact Task, Criterion, and Goal version | `test_traceability_and_dependencies`, `test_action_authorization_cannot_be_relabelled_to_another_criterion` |
| Persistence before eviction | A missing store or failed write leaves the live task in HOT; multi-task supersession does not partially evict | `test_direct_transition_requires_durable_capsule`, `test_failed_persistence_does_not_evict_task`, `test_supersession_persistence_failure_does_not_partially_evict` |
| Context admission | Explicitly retrieved knowledge stays scoped to its active task | `test_durable_knowledge_requires_explicit_retrieval`, `test_retrieved_knowledge_does_not_leak_to_another_active_task` |
| Silent goal mutation | Direct changes to a Goal Contract cannot authorize an action or enter working context | `test_direct_goal_mutation_cannot_authorize_an_action` |
| Stale feedback | A previous Goal Checksum cannot supersede a changed goal or attach a new task | `test_stale_goal_mutation_route_cannot_supersede`, `test_stale_new_task_route_cannot_attach_task` |

The reference implementation in `src/goal_control.py` checks explicit inputs.
It needs a durable `capsule_dir` or an explicit file path before evicting a
task. It does not classify natural language, judge whether an action satisfies
a natural-language constraint, verify that a named resume event truly occurred,
or automatically rehydrate a full task store across processes. A fresh
controller can import a persisted capsule after its goal and task contracts
are reconstructed with the task in COLD; the fresh-controller test reads the
original capsule without creating a replacement. These tests do not prove
that a live agent follows the rules. A fresh, blinded behavioral comparison
is required before claiming drift reduction or resume improvement.
Multi-task transitions prevent partial in-memory eviction after a write error;
separate capsule files do not provide a cross-file transaction after a crash.
