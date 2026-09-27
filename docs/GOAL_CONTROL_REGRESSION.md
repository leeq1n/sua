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
| Resume fidelity | Paused capsule matches identity, goal version, dependencies, next action, blocker, and named trigger after file persistence; a fresh controller can rebuild the task from the file when given the current Goal Contract | `test_resume_fidelity_and_eviction`, `test_resume_rejects_capsule_after_goal_version_changes`, `test_resume_needs_matching_named_trigger`, `test_capsule_persists_before_eviction_and_resumes_in_fresh_controller`, `test_resume_capsule_preserves_dependencies_next_action_and_blocker`, `test_resume_from_file_rehydrates_task_after_process_restart`, `test_rehydration_rejects_stale_goal_without_registering_task`, `test_rehydration_rejects_another_hot_task_without_registering_task` |
| Traceability | Action authorization binds the exact Task, Criterion, and Goal version | `test_traceability_and_dependencies`, `test_action_authorization_cannot_be_relabelled_to_another_criterion` |
| Durable daily traceability | A daily task capsule stores authorized Action→Task→Criterion→Goal links and their at-action contracts, validates criterion membership before resume, and carries them through corrected-goal replan; the CLI requires a host-keyed capsule | `test_daily_verified_run_persists_terminal_task`, `test_daily_unverified_run_can_resume_only_on_named_trigger`, `test_invalid_persisted_trace_cannot_resume_a_task`, `test_signed_capsule_rejects_forged_linked_action`, `test_corrected_goal_replan_keeps_prior_action_trace` |
| Persistence before eviction | A missing store or failed write leaves the live task in HOT; multi-task supersession does not partially evict | `test_direct_transition_requires_durable_capsule`, `test_failed_persistence_does_not_evict_task`, `test_supersession_persistence_failure_does_not_partially_evict` |
| Context admission | Explicitly retrieved knowledge stays scoped to its active task | `test_durable_knowledge_requires_explicit_retrieval`, `test_retrieved_knowledge_does_not_leak_to_another_active_task` |
| Silent goal mutation | Direct changes to a Goal Contract cannot authorize an action or enter working context | `test_direct_goal_mutation_cannot_authorize_an_action` |
| Stale feedback | A previous Goal Checksum cannot supersede a changed goal or attach a new task | `test_stale_goal_mutation_route_cannot_supersede`, `test_stale_new_task_route_cannot_attach_task` |
| Criterion correction recovery | An old capsule cannot resume after revision; explicit replan binds current criteria, dependencies, blocker, and next action, persisting before task mutation | `test_corrected_goal_requires_explicit_replan_before_resume`, `test_replan_persistence_failure_preserves_suspended_task`, `test_replan_rejects_stale_or_unlinked_criteria`, `test_replanned_capsule_resumes_in_fresh_controller`, `test_replan_updates_dependencies_and_blocker_durably` |
| v4 context and action boundary | The thinker receives only current HOT context; raw history and COLD items stay out. A dynamic plan is reviewed before execution; denied, changed-argument, or stale-goal steps stop before the delegate; a new review revokes old authorization | `test_goal_control_v4.py` |
| Task switch residency | Activation or resume cannot displace an ACTIVE/HOT task; the current task must persist and evict first, and a failed write leaves the switch blocked | `test_adding_another_active_goal_keeps_context_consistent`, `test_resume_cannot_displace_another_hot_task`, `test_failed_eviction_cannot_be_bypassed_by_switch` |

The reference implementation in `src/goal_control.py` checks explicit inputs.
It needs a durable `capsule_dir` or an explicit file path before evicting a
task. It does not classify natural language, judge whether an action satisfies
a natural-language constraint, verify that a named resume event truly occurred,
or automatically rehydrate a full task store across processes. A fresh
controller can rebuild one resumable task from a versioned persisted capsule
after the host provides the current Goal Contract. The file records the task
status so a terminal task cannot be revived; legacy list capsules can still
resume a task already reconstructed in memory. It rejects a stale goal or an
occupied HOT task before registering the recovered task. This is not a durable Goal store,
an authenticated capsule, or automatic recovery of all tasks. These tests do not prove
that a live agent follows the rules. A fresh, blinded behavioral comparison
is required before claiming drift reduction or resume improvement.
`src/goal_control_v4.py` provides opt-in wrappers for the v4 thinker and
executor. The host's review callback receives each planned Step and the
current working context, then returns its linked criterion or denies it. A
new plan review revokes prior Step authorizations. The executor wrapper
records an attempted action before calling the delegate and blocks
unauthorized steps before side effects. The thinker wrapper constructs its
prompt from the active Goal, active Task, HOT direct dependencies, and
explicitly retrieved knowledge. It discards the raw Loop prompt; the host
must first bind the current user intent into its Goal and Task contracts.
It does not automatically classify feedback or judge semantic goal alignment.
The daily `core.agent` entrypoint now uses the same ControlPlane through its
own guarded tool boundary when given an explicit contract; see
[`GOAL_CONTROL_RUNTIME.md`](GOAL_CONTROL_RUNTIME.md). The v4 adapter itself
remains opt-in. These tests demonstrate execution boundaries, not live agent
drift reduction.
Multi-task transitions prevent partial in-memory eviction after a write error;
separate capsule files do not provide a cross-file transaction after a crash.
