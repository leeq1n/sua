"""Structural guard for the unmeasured mechanism-space regression proposal."""

import json
from pathlib import Path


FIXTURE = Path(__file__).resolve().parents[1] / "benchmarks" / "mechanism_space_v0.json"


def test_mechanism_space_v0_has_balanced_failure_surfaces():
    data = json.loads(FIXTURE.read_text(encoding="utf-8"))
    cases = data["cases"]
    assert data["status"] == "draft-design-candidate; no model outcomes"
    assert len(cases) == 8
    assert len({case["id"] for case in cases}) == len(cases)
    assert {case["kind"] for case in cases} == {"pair", "sequence"}
    assert {case["failure_mode"] for case in cases} == {
        "surface_renaming",
        "cross_domain_equivalence",
        "false_merge_from_shared_vocabulary",
        "missing_discriminator",
        "family_saturation",
        "novelty_proxy",
        "irreducible_delta",
        "goal_drift",
    }
    assert {case["expected_decision"] for case in cases if case["kind"] == "pair"} == {
        "SAME_MECHANISM", "DIFFERENT_MECHANISM", "UNCERTAIN"
    }
    for case in cases:
        assert case["task"].strip()
        assert case["expected_decision"].strip()
        assert len(case["rubric"]) >= 2
        assert len(set(case["rubric"])) == len(case["rubric"])
