"""Executable checks for task-scoped grounded-experience persistence."""

import pytest

from src.retry_gate import (
    AcceptanceAuthority,
    AuthorityBasis,
    CausalLayer,
    CriterionClass,
    ExperienceMapping,
    ExperienceSource,
    FailureClass,
    GroundedExperienceAnchor,
    RetryDecision,
    RetryProposal,
    RetryState,
    evaluate_retry,
)


def make_anchor() -> GroundedExperienceAnchor:
    return GroundedExperienceAnchor(
        parent_objective="make the workflow usable",
        consumer="a person completing the workflow",
        evidence_sources=(
            ExperienceSource(
                source_id="source-a",
                title="Representative source A",
                locator="https://example.test/a",
                observation="the affected item is connected to its correction",
                function="preserve a discoverable correction relationship",
            ),
            ExperienceSource(
                source_id="source-b",
                title="Representative source B",
                locator="https://example.test/b",
                observation="the presentation can vary while the relation remains",
                function="separate function from surface treatment",
            ),
        ),
        evidence_backed_invariants=("affected-item-to-correction",),
        tentative_hypotheses=("the consumer may prefer a summary first",),
        non_binding_variants=("summary-plus-inline",),
        negative_knowledge_anti_patterns=("color-alone",),
        current_constraint_to_artifact_or_action_mapping=(
            ExperienceMapping(
                constraint="affected-item-to-correction",
                artifact_or_action="validation response",
                function_mapping="point each problem to its correction",
            ),
        ),
    )


def make_state(anchor=None) -> RetryState:
    return RetryState(
        parent_objective="make the workflow usable",
        failed_acceptance_criterion="the correction path is discoverable",
        criterion_class=CriterionClass.USER_FACING,
        acceptance_authority=AcceptanceAuthority.USER,
        authority_basis=AuthorityBasis.EXPLICIT_USER_REJECTION,
        failure_class=FailureClass.USER_REJECTION,
        representation_family="form response",
        production_substrate="html",
        causal_layer=CausalLayer.LOCAL_PARAMETER,
        causal_delta="",
        prior_local_pass=True,
        grounded_experience_anchor=anchor,
    )


def make_proposal(anchor=None, **overrides) -> RetryProposal:
    values = {
        "parent_objective": "make the workflow usable",
        "failed_acceptance_criterion": "the correction path is discoverable",
        "criterion_class": CriterionClass.USER_FACING,
        "acceptance_authority": AcceptanceAuthority.USER,
        "authority_basis": AuthorityBasis.EXPLICIT_USER_REJECTION,
        "failure_class": FailureClass.USER_REJECTION,
        "representation_family": "single-column form response",
        "production_substrate": "html",
        "causal_layer": CausalLayer.REPRESENTATION_FRAMING,
        "causal_delta": "move from a cosmetic patch to a relationship-preserving representation",
        "grounded_experience_anchor": anchor,
    }
    values.update(overrides)
    return RetryProposal(**values)


def test_anchor_round_trip_preserves_provenance_and_classification_boundaries():
    anchor = make_anchor()

    restored = GroundedExperienceAnchor.from_json(anchor.to_json())

    assert restored == anchor
    assert restored.evidence_sources[0].locator == "https://example.test/a"
    assert "affected-item-to-correction" in restored.evidence_backed_invariants
    assert "summary-plus-inline" not in restored.evidence_backed_invariants


def test_reconsume_updates_current_mapping_without_reclassifying_experience():
    anchor = make_anchor()

    reconsumed = anchor.reconsume(
        "representation changed from page to stepper",
        mapping=ExperienceMapping(
            constraint="affected-item-to-correction",
            artifact_or_action="stepper error summary",
            function_mapping="keep the field relationship after representation change",
        ),
    )

    assert reconsumed.last_reanchor_reason == "representation changed from page to stepper"
    assert len(reconsumed.current_constraint_to_artifact_or_action_mapping) == 2
    assert reconsumed.evidence_backed_invariants == anchor.evidence_backed_invariants
    assert reconsumed.evidence_sources == anchor.evidence_sources


def test_classification_update_requires_new_provenance():
    anchor = make_anchor()

    with pytest.raises(ValueError, match="new evidence"):
        anchor.update_from_evidence(
            "attempted reclassification without evidence",
            evidence_sources=(),
            evidence_backed_invariants=("new-invariant",),
        )

    updated = anchor.update_from_evidence(
        "new representative observation changed the hypothesis",
        evidence_sources=(
            ExperienceSource(
                source_id="source-c",
                title="Representative source C",
                locator="https://example.test/c",
                observation="a new target constraint is explicit",
                function="support a bounded update",
            ),
        ),
        tentative_hypotheses=("the new target may require a second correction route",),
    )
    assert {item.source_id for item in updated.evidence_sources} == {"source-a", "source-b", "source-c"}


def test_retry_state_carries_anchor_through_serialized_retry_boundary():
    anchor = make_anchor()
    prior = make_state(anchor)

    result = evaluate_retry(prior, make_proposal())

    assert result.decision is RetryDecision.RETRY_ALLOWED
    assert result.state.grounded_experience_anchor == anchor
    reloaded = RetryState.from_json(result.state.to_json())
    assert reloaded.grounded_experience_anchor == anchor
    assert reloaded.to_dict()["GROUNDED_EXPERIENCE_ANCHOR"]["EVIDENCE_SOURCES"][0]["LOCATOR"] == "https://example.test/a"


def test_legacy_retry_state_without_anchor_remains_valid():
    state = make_state()

    restored = RetryState.from_json(state.to_json())

    assert restored.grounded_experience_anchor is None
