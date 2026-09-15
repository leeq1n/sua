"""Freeze and exercise the E4-A benchmark/scoring contract before implementation."""

from benchmarks.e4_a_grounded_experience_eval import load_manifest, score


def _passing_open_response(challenge):
    source_ids = [item["id"] for item in challenge["representative_ecosystem_examples"]]
    invariant = challenge["shared_relational_function_invariant"]
    variant = challenge["legitimate_variant"]
    accident = challenge["tempting_accidental_surface_feature"]
    return {
        "task_id": challenge["id"],
        "source_inspection": [
            {"source_id": source_id, "observation": "observed representative relationship"}
            for source_id in source_ids
        ],
        "classifications": {
            "invariants": [{"id": invariant["id"], "source_ids": source_ids, "statement": invariant["statement"]}],
            "hypotheses": [{"id": "hypothesis-1", "statement": "tentative local hypothesis"}],
            "variants": [{"id": variant["id"], "statement": variant["statement"]}],
            "accidents": [{"id": accident["id"], "statement": accident["statement"]}],
        },
        "relational_mappings": [{
            "invariant_id": invariant["id"],
            "artifact_or_action": challenge["initial_artifact_or_action"],
            "function_preserved": "preserve the consumer-facing relationship",
        }],
        "anchor": {
            "PARENT_OBJECTIVE": challenge["parent_objective"],
            "CONSUMER": challenge["consumer"],
            "EVIDENCE_SOURCES": source_ids,
            "EVIDENCE_BACKED_INVARIANTS": [invariant["id"]],
            "TENTATIVE_HYPOTHESES": ["hypothesis-1"],
            "NON_BINDING_VARIANTS": [variant["id"]],
            "NEGATIVE_KNOWLEDGE_ANTI_PATTERNS": [accident["id"]],
            "CURRENT_CONSTRAINT_TO_ARTIFACT_OR_ACTION_MAPPING": [{
                "constraint": invariant["id"],
                "mapping": challenge["initial_artifact_or_action"],
            }],
            "LAST_REANCHOR_REASON": "initial grounding and boundary re-consumption",
        },
        "iterations": [
            {
                "boundary_id": boundary["id"],
                "anchor_reconsumed": True,
                "mapping_preserved": True,
                "local_checks_pass": True,
                "drift_detected": boundary["id"] in {"target-drift", "contradicts-invariant"},
                "replanned": boundary["id"] == "contradicts-invariant",
                "reason": boundary["signal"],
            }
            for boundary in challenge["boundaries"]
        ],
    }


def _passing_responses(manifest):
    responses = [
        _passing_open_response(challenge)
        for challenge in manifest["challenges"]
    ]
    responses.extend(
        {
            "task_id": control["id"],
            "grounding_triggered": False,
            "action": control["required_action"],
            "anchor_created": False,
        }
        for control in manifest["direct_controls"]
    )
    return responses


def test_manifest_is_frozen_domain_neutral_and_has_held_out_case():
    manifest = load_manifest()

    assert manifest["candidate_base_commit"] == "a45de1b73ca4a959da0b7abf78e703f293a74427"
    assert len(manifest["challenges"]) == 3
    assert {item["split"] for item in manifest["challenges"]} == {"development", "held_out"}
    assert all(len(item["representative_ecosystem_examples"]) >= 3 for item in manifest["challenges"])
    assert all(len(item["boundaries"]) >= 5 for item in manifest["challenges"])
    assert len(manifest["direct_controls"]) == 2
    assert manifest["scoring_rule"]["mode"] == "mechanical_structural_only"


def test_frozen_structural_fixture_supports_retain_verdict():
    manifest = load_manifest()

    result = score(manifest, _passing_responses(manifest))

    assert result["status"] == "RETAIN_FOR_HELD_OUT"
    assert result["verdict"].startswith("E4-A RETAIN_FOR_HELD_OUT")


def test_missing_boundary_is_measurement_failure_or_failed_score_not_silent_pass():
    manifest = load_manifest()
    responses = _passing_responses(manifest)
    open_response = responses[0]
    open_response["iterations"] = open_response["iterations"][:-1]

    result = score(manifest, responses)

    assert result["status"] == "REVERT"
    assert result["tasks"][manifest["challenges"][0]["id"]]["failures"]
