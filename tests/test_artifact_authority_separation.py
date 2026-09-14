"""Frozen, domain-neutral regressions for E3-M4 authority separation."""

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
GUIDE = ROOT / "docs" / "ARTIFACT_FINALIZATION.md"
DETAIL = ROOT / "docs" / "ARTIFACT_FINALIZATION_DETAIL.md"
CASES = ROOT / "benchmarks" / "e3_m4_authority_cases.json"


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_five_frozen_domain_neutral_cases_are_present():
    cases = json.loads(read(CASES))
    assert {case["id"] for case in cases} == {
        "reference-style-trap",
        "composition-trap",
        "semantic-preservation",
        "multi-authority-artifact",
        "direct-simple-artifact",
    }
    assert all(case["expected_decision"] for case in cases)
    assert all(case["rubric"] for case in cases)
    fixture_text = read(CASES).lower()
    for forbidden in ("scientific", "paper", "figure", "figma", "powerpoint", "svg", "python", "draw.io"):
        assert forbidden not in fixture_text


def test_detail_surface_is_reachable_from_artifact_finalization():
    guide = read(GUIDE)
    assert "ARTIFACT_FINALIZATION_DETAIL.md" in guide
    assert DETAIL.exists()


def test_detail_surface_defines_four_surface_scoped_authorities():
    text = read(DETAIL)
    normalized = " ".join(text.split()).lower()
    for phrase in (
        "surface-scoped",
        "semantic/content authority",
        "information/composition authority",
        "style authority",
        "end-use/consumer authority",
        "reference artifact is not the universal optimization target",
        "style/reference similarity cannot establish semantic correctness",
        "composition similarity cannot establish end-use success",
        "end-use failure cannot silently rewrite established semantic truth",
        "parent objective",
        "actual target interface",
    ):
        assert phrase.lower() in normalized


def test_detail_surface_limits_conflicts_to_the_affected_dimension():
    normalized = " ".join(read(DETAIL).split()).lower()
    assert "holds only the affected acceptance dimension" in normalized
    assert "may not override" in normalized
    assert "authority ambiguity" in normalized
    assert "no unnecessary authority ceremony" in normalized


def test_candidate_does_not_add_substrate_selection():
    candidate_text = read(DETAIL).lower()
    for forbidden in (
        "structured connectivity",
        "free-layout",
        "edit stability",
        "versionability",
        "export stability",
        "consumer compatibility",
        "automation reliability",
        "human takeover cost",
        "substrate selection",
    ):
        assert forbidden not in candidate_text
