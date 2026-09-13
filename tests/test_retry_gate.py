"""Executable acceptance tests for the canonical retry gate."""

from unittest.mock import patch

import pytest

from src.retry_gate import (
    AcceptanceAuthority,
    AuthorityBasis,
    CausalLayer,
    CriterionClass,
    EndUseStatus,
    FailureClass,
    LifecycleAction,
    LifecycleEvidence,
    ParentTaskState,
    RetryDecision,
    RetryProposal,
    RetryState,
    evaluate_lifecycle,
    evaluate_retry,
)
from src.v4_executor import MockExecutor
from src.v4_loop import Loop, LoopStatus
from src.v4_thinker import Step, Thinker
from src.v2_agent import Paper
from src.v2_round import RoundResult, run_one_round_with_harness


def user_state(**overrides):
    values = {
        "parent_objective": "make the artifact usable",
        "failed_acceptance_criterion": "the layout is readable",
        "criterion_class": CriterionClass.USER_FACING,
        "acceptance_authority": AcceptanceAuthority.USER,
        "authority_basis": AuthorityBasis.EXPLICIT_USER_REJECTION,
        "failure_class": FailureClass.USER_REJECTION,
        "representation_family": "two-column layout",
        "production_substrate": "reportlab",
        "causal_layer": CausalLayer.LOCAL_PARAMETER,
        "causal_delta": "",
        "negative_knowledge": ("keep the failed layout out of the next attempt",),
        "unchanged_assumptions": ("the artifact must remain printable",),
        "prior_local_pass": True,
        "artifact_role_placement": "main report body",
    }
    values.update(overrides)
    return RetryState(**values)


def proposal(**overrides):
    values = {
        "parent_objective": "make the artifact usable",
        "failed_acceptance_criterion": "the layout is readable",
        "criterion_class": CriterionClass.USER_FACING,
        "acceptance_authority": AcceptanceAuthority.USER,
        "authority_basis": AuthorityBasis.EXPLICIT_USER_REJECTION,
        "failure_class": FailureClass.USER_REJECTION,
        "representation_family": "two-column layout",
        "production_substrate": "reportlab",
        "causal_layer": CausalLayer.LOCAL_PARAMETER,
        "causal_delta": "change spacing between paragraphs",
        "unchanged_assumptions": ("the artifact must remain printable",),
        "artifact_role_placement": "main report body",
    }
    values.update(overrides)
    return RetryProposal(**values)


def test_user_facing_cosmetic_retry_requires_global_replan_and_invalidates_pass():
    result = evaluate_retry(user_state(), proposal())

    assert result.decision is RetryDecision.GLOBAL_REPLAN_REQUIRED
    assert result.prior_local_pass_invalidated is True
    assert result.state.prior_local_pass is False
    assert any(
        "reportlab" in item
        for item in result.state.to_dict()["NEGATIVE_KNOWLEDGE"]
    )


def test_user_facing_substrate_change_allows_retry():
    result = evaluate_retry(
        user_state(),
        proposal(
            production_substrate="weasyprint",
            causal_layer=CausalLayer.SUBSTRATE_TOOL,
            causal_delta="replace reportlab with a paged-media renderer",
        ),
    )

    assert result.decision is RetryDecision.RETRY_ALLOWED
    assert result.structural_delta_valid is True
    assert result.state.prior_local_pass is False


def test_unsupported_user_disagreement_does_not_overwrite_objective_evidence():
    prior = RetryState(
        parent_objective="measure the validated system result",
        failed_acceptance_criterion="the measured result matches the protocol",
        criterion_class=CriterionClass.OBJECTIVE_SCIENTIFIC,
        acceptance_authority=AcceptanceAuthority.OBJECTIVE_EVIDENCE,
        authority_basis=AuthorityBasis.INDEPENDENT_VERIFIED_EVIDENCE,
        failure_class=FailureClass.OBJECTIVE_FAILURE,
        representation_family="validated experiment",
        production_substrate="canonical simulator",
        causal_layer=CausalLayer.IMPLEMENTATION,
        causal_delta="verified result recorded",
        negative_knowledge=("do not discard the verified measurement",),
        unchanged_assumptions=("protocol and seed are fixed",),
        prior_local_pass=True,
    )
    user_disagreement = RetryProposal(
        parent_objective=prior.parent_objective,
        failed_acceptance_criterion=prior.failed_acceptance_criterion,
        criterion_class=CriterionClass.OBJECTIVE_SCIENTIFIC,
        acceptance_authority=AcceptanceAuthority.UNRESOLVED,
        authority_basis=AuthorityBasis.UNSUPPORTED_USER_ASSERTION,
        failure_class=FailureClass.AUTHORITY_DISPUTE,
        representation_family=prior.representation_family,
        production_substrate=prior.production_substrate,
        causal_layer=prior.causal_layer,
        causal_delta="the user says the verified result is wrong",
    )

    result = evaluate_retry(prior, user_disagreement)

    assert result.decision is RetryDecision.ACCEPTANCE_AUTHORITY_UNVERIFIED
    assert result.prior_local_pass_invalidated is False
    assert result.state.prior_local_pass is True


def test_changed_user_preference_is_not_a_repeated_same_core_rejection():
    result = evaluate_retry(
        user_state(),
        proposal(
            failed_acceptance_criterion="use a more compact layout",
            causal_delta="start a new preference-controlled layout task",
        ),
    )

    assert result.decision is RetryDecision.RETRY_ALLOWED


def test_representation_layer_change_allows_structurally_coherent_retry():
    result = evaluate_retry(
        user_state(),
        proposal(
            representation_family="single-column editorial layout",
            causal_layer=CausalLayer.REPRESENTATION_FRAMING,
            causal_delta="change the representation family to remove the readability failure",
        ),
    )

    assert result.decision is RetryDecision.RETRY_ALLOWED


def test_serialized_state_preserves_failure_and_blocks_cosmetic_retry():
    failed = evaluate_retry(user_state(), proposal())
    reloaded = RetryState.from_json(failed.state.to_json())
    fresh_invocation = evaluate_retry(reloaded, proposal())

    assert reloaded.negative_knowledge == failed.state.negative_knowledge
    assert reloaded.unchanged_assumptions == failed.state.unchanged_assumptions
    assert reloaded.prior_local_pass is False
    assert fresh_invocation.decision is RetryDecision.GLOBAL_REPLAN_REQUIRED


def test_claimed_delta_with_unchanged_structure_is_rejected():
    result = evaluate_retry(
        user_state(),
        proposal(
            causal_delta="structural redesign",
            causal_layer=CausalLayer.LOCAL_PARAMETER,
        ),
    )

    assert result.decision is RetryDecision.GLOBAL_REPLAN_REQUIRED
    assert result.structural_delta_valid is False


@pytest.mark.parametrize("rejection_count", [0, 1, 2, 17, 1000])
def test_decision_does_not_depend_on_a_fixed_rejection_count(rejection_count):
    state = user_state(
        negative_knowledge=tuple(
            ["keep the failed layout out of the next attempt"]
            + [f"observed rejection {i}" for i in range(rejection_count)]
        )
    )
    result = evaluate_retry(state, proposal())

    assert result.decision is RetryDecision.GLOBAL_REPLAN_REQUIRED
    assert rejection_count >= 0  # the gate has no rejection-count trigger


def test_existing_loop_controller_enforces_gate_before_retry():
    calls = []

    class FlakyThinker(Thinker):
        def plan(self, prompt):
            calls.append(prompt)
            return [Step("bad" if len(calls) == 1 else "good")]

    loop = Loop(FlakyThinker(), MockExecutor(fail_on=["bad"]))
    result = loop.run(
        "retry through the canonical controller",
        max_retries=2,
        retry_state=user_state(),
        retry_proposal=proposal(
            production_substrate="weasyprint",
            causal_layer=CausalLayer.SUBSTRATE_TOOL,
            causal_delta="replace the renderer",
        ),
    )

    assert result.status is LoopStatus.SUCCEEDED
    assert result.attempts == 2
    assert result.retry_decision is RetryDecision.RETRY_ALLOWED


def test_existing_loop_controller_stops_when_gate_requires_replan():
    calls = []

    class AlwaysBad(Thinker):
        def plan(self, prompt):
            calls.append(prompt)
            return [Step("bad")]

    loop = Loop(AlwaysBad(), MockExecutor(fail_on=["bad"]))
    result = loop.run(
        "do not polish the same failed structure",
        max_retries=2,
        retry_state=user_state(),
        retry_proposal=proposal(),
    )

    assert result.status is LoopStatus.FAILED
    assert result.attempts == 1
    assert len(calls) == 1
    assert result.retry_decision is RetryDecision.GLOBAL_REPLAN_REQUIRED


def test_default_canonical_retry_requires_context_and_stops_before_second_attempt():
    calls = []

    class AlwaysBad(Thinker):
        def plan(self, prompt):
            calls.append(prompt)
            return [Step("bad")]

    loop = Loop(AlwaysBad(), MockExecutor(fail_on=["bad"]))
    result = loop.run(
        "default canonical retry path",
        max_retries=2,
        retry_state=None,
        retry_proposal=None,
    )

    assert result.attempts == 1
    assert len(calls) == 1
    assert result.retry_decision is RetryDecision.RETRY_CONTEXT_REQUIRED


def test_omitted_artifact_role_does_not_create_structural_delta():
    result = evaluate_retry(
        user_state(),
        proposal(
            artifact_role_placement=None,
            causal_delta="a claimed redesign without a changed structural identity",
        ),
    )

    assert result.decision is RetryDecision.GLOBAL_REPLAN_REQUIRED
    assert result.structural_delta_valid is False


def test_representation_variant_rename_is_not_a_family_change():
    prior = user_state(
        representation_family="two-column-layout",
        representation_variant="A",
        causal_layer=CausalLayer.REPRESENTATION_FRAMING,
    )
    result = evaluate_retry(
        prior,
        proposal(
            representation_family="two-column-layout",
            representation_variant="B",
            causal_layer=CausalLayer.REPRESENTATION_FRAMING,
            causal_delta="rename the display variant only",
        ),
    )

    assert result.decision is RetryDecision.GLOBAL_REPLAN_REQUIRED
    assert result.structural_delta_valid is False


def test_representation_family_change_is_a_valid_structural_delta():
    prior = user_state(
        representation_family="two-column-layout",
        representation_variant="A",
    )
    result = evaluate_retry(
        prior,
        proposal(
            representation_family="matrix-centered-evidence-architecture",
            representation_variant="A",
            causal_layer=CausalLayer.REPRESENTATION_FRAMING,
            causal_delta="replace the canonical representation family",
        ),
    )

    assert result.decision is RetryDecision.RETRY_ALLOWED
    assert result.structural_delta_valid is True


def test_existing_round_harness_forwards_gate_to_controller():
    def round_result(decision):
        return RoundResult(
            decision=decision,
            paper=Paper(arxiv_id="x", title="x", abstract="x"),
            target_module="core/planner.py",
        )

    with patch(
        "src.v2_round.run_one_round_multi",
        side_effect=[round_result("NO_PATCH"), round_result("KEPT")],
    ) as run_round:
        result = run_one_round_with_harness(
            target_module="core/planner.py",
            max_retries=2,
            retry_state=user_state(),
            retry_proposal=proposal(
                production_substrate="weasyprint",
                causal_layer=CausalLayer.SUBSTRATE_TOOL,
                causal_delta="replace the renderer",
            ),
        )

    assert run_round.call_count == 2
    assert result.decision == "KEPT"
    assert result.retry_decision is RetryDecision.RETRY_ALLOWED


def test_default_round_harness_cannot_retry_without_context():
    no_patch = RoundResult(
        decision="NO_PATCH",
        paper=Paper(arxiv_id="x", title="x", abstract="x"),
        target_module="core/planner.py",
    )

    with patch("src.v2_round.run_one_round_multi", return_value=no_patch) as run_round:
        result = run_one_round_with_harness(
            target_module="core/planner.py",
            max_retries=2,
            retry_state=None,
            retry_proposal=None,
        )

    assert run_round.call_count == 1
    assert result.retry_decision is RetryDecision.RETRY_CONTEXT_REQUIRED


def test_direct_parent_completion_can_stop_without_forced_continuation():
    result = evaluate_lifecycle(
        LifecycleEvidence(
            parent_objective="deliver a usable artifact",
            current_candidate_identity="candidate-complete",
            parent_objective_complete=True,
            end_use_status=EndUseStatus.SATISFIED,
        )
    )

    assert result.parent_task_state is ParentTaskState.COMPLETE
    assert result.next_action is LifecycleAction.STOP
    assert result.last_known_valid_candidate == "candidate-complete"


def test_local_success_keeps_parent_open_and_checkpoints_valid_candidate():
    result = evaluate_lifecycle(
        LifecycleEvidence(
            parent_objective="deliver a usable artifact",
            current_candidate_identity="candidate-local",
            local_success=True,
            end_use_status=EndUseStatus.UNRESOLVED,
            unresolved_condition="deployment integration is pending",
            unresolved_reason="the local regression passed but the consumer path is unverified",
        )
    )

    assert result.local_candidate_success is True
    assert result.parent_task_state is ParentTaskState.OPEN
    assert result.last_known_valid_candidate == "candidate-local"
    assert result.end_use_status is EndUseStatus.UNRESOLVED
    assert result.next_action is LifecycleAction.CHECKPOINT
    assert result.unresolved_condition == "deployment integration is pending"


def test_last_known_valid_candidate_survives_unresolved_parent_continuation():
    result = evaluate_lifecycle(
        LifecycleEvidence(
            parent_objective="deliver a usable artifact",
            current_candidate_identity="candidate-failed",
            last_known_valid_candidate="candidate-prior",
            end_use_status=EndUseStatus.UNRESOLVED,
            unresolved_condition="dependency evidence is missing",
            unresolved_reason="the next parent-level check has not run",
        )
    )

    assert result.parent_task_state is ParentTaskState.OPEN
    assert result.last_known_valid_candidate == "candidate-prior"
    assert result.next_action is LifecycleAction.CONTINUE_PARENT


def test_concrete_local_defect_uses_bounded_local_continuation():
    result = evaluate_lifecycle(
        LifecycleEvidence(
            parent_objective="deliver a usable artifact",
            current_candidate_identity="candidate-local",
            last_known_valid_candidate="candidate-local",
            local_defect_identified=True,
            representation_causally_viable=True,
            unresolved_condition="one bounded defect remains",
            unresolved_reason="the defect is isolated to the current local representation",
        )
    )

    assert result.parent_task_state is ParentTaskState.OPEN
    assert result.last_known_valid_candidate == "candidate-local"
    assert result.next_action is LifecycleAction.CONTINUE_LOCAL


def test_same_core_without_causal_delta_selects_broader_replan():
    result = evaluate_lifecycle(
        LifecycleEvidence(
            parent_objective="deliver a usable artifact",
            last_known_valid_candidate="candidate-prior",
            same_core_no_causal_delta=True,
            unresolved_condition="the same representation failed again",
            unresolved_reason="the proposed attempt changes no causal layer",
        )
    )

    assert result.parent_task_state is ParentTaskState.OPEN
    assert result.last_known_valid_candidate == "candidate-prior"
    assert result.next_action is LifecycleAction.GLOBAL_REPLAN


def test_local_construction_success_does_not_infer_parent_acceptance():
    result = evaluate_lifecycle(
        LifecycleEvidence(
            parent_objective="deliver a usable artifact",
            current_candidate_identity="candidate-local",
            local_success=True,
            end_use_status=EndUseStatus.SATISFIED,
            parent_objective_complete=False,
        )
    )

    assert result.local_candidate_success is True
    assert result.parent_task_state is ParentTaskState.OPEN
    assert result.parent_objective_complete is False
    assert result.next_action is LifecycleAction.CONTINUE_PARENT


def test_lifecycle_state_round_trip_preserves_explicit_next_action():
    result = evaluate_lifecycle(
        LifecycleEvidence(
            parent_objective="deliver a usable artifact",
            current_candidate_identity="candidate-local",
            local_success=True,
            unresolved_condition="acceptance remains open",
            unresolved_reason="independent end-use evidence is pending",
        )
    )

    reloaded = result.from_dict(result.to_dict())

    assert reloaded == result
    assert reloaded.next_action is LifecycleAction.CHECKPOINT
