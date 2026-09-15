"""Frozen mechanical scorer for the E4-A grounded-experience benchmark.

The scorer deliberately checks only structure, provenance, boundary handling,
and the direct-task exemption. It does not judge aesthetic quality, wording,
or whether a response is persuasive. The manifest is frozen before the runtime
candidate is implemented; changing it after scoring invalidates the run.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any, Iterable, Mapping


ROOT = Path(__file__).resolve().parents[1]
MANIFEST_PATH = ROOT / "benchmarks" / "e4_a_grounded_experience.json"


OPEN_ANCHOR_KEYS = {
    "PARENT_OBJECTIVE",
    "CONSUMER",
    "EVIDENCE_SOURCES",
    "EVIDENCE_BACKED_INVARIANTS",
    "TENTATIVE_HYPOTHESES",
    "NON_BINDING_VARIANTS",
    "NEGATIVE_KNOWLEDGE_ANTI_PATTERNS",
    "CURRENT_CONSTRAINT_TO_ARTIFACT_OR_ACTION_MAPPING",
    "LAST_REANCHOR_REASON",
}


def load_manifest(path: Path = MANIFEST_PATH) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def manifest_sha256(path: Path = MANIFEST_PATH) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _as_list(value: Any) -> list[Any]:
    return value if isinstance(value, list) else []


def _nonempty_text(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _source_ids(challenge: Mapping[str, Any]) -> set[str]:
    return {
        item["id"]
        for item in challenge["representative_ecosystem_examples"]
    }


def _find_challenge(manifest: Mapping[str, Any], task_id: str) -> Mapping[str, Any]:
    for challenge in manifest["challenges"]:
        if challenge["id"] == task_id:
            return challenge
    raise KeyError(f"unknown open task {task_id!r}")


def _score_open_task(
    challenge: Mapping[str, Any], response: Mapping[str, Any]
) -> tuple[dict[str, bool], list[str]]:
    expected_sources = _source_ids(challenge)
    invariant = challenge["shared_relational_function_invariant"]
    variant = challenge["legitimate_variant"]
    accident = challenge["tempting_accidental_surface_feature"]
    inspected = {
        item.get("source_id")
        for item in _as_list(response.get("source_inspection"))
        if isinstance(item, Mapping) and _nonempty_text(item.get("observation"))
    }
    classifications = response.get("classifications")
    if not isinstance(classifications, Mapping):
        classifications = {}
    invariant_rows = _as_list(classifications.get("invariants"))
    hypothesis_rows = _as_list(classifications.get("hypotheses"))
    variant_rows = _as_list(classifications.get("variants"))
    accident_rows = _as_list(classifications.get("accidents"))
    ids = lambda rows: {row.get("id") for row in rows if isinstance(row, Mapping)}
    mapping_rows = _as_list(response.get("relational_mappings"))
    anchor = response.get("anchor")
    if not isinstance(anchor, Mapping):
        anchor = {}
    anchor_sources = set(anchor.get("EVIDENCE_SOURCES", []))
    anchor_invariants = set(anchor.get("EVIDENCE_BACKED_INVARIANTS", []))
    anchor_variants = set(anchor.get("NON_BINDING_VARIANTS", []))
    anchor_anti = set(anchor.get("NEGATIVE_KNOWLEDGE_ANTI_PATTERNS", []))
    mappings = {
        row.get("invariant_id")
        for row in mapping_rows
        if isinstance(row, Mapping)
        and _nonempty_text(row.get("artifact_or_action"))
        and _nonempty_text(row.get("function_preserved"))
    }
    boundaries = {item["id"] for item in challenge["boundaries"]}
    iteration_rows = _as_list(response.get("iterations"))
    iterations = {
        row.get("boundary_id"): row
        for row in iteration_rows
        if isinstance(row, Mapping)
    }
    all_iterations_reconsumed = (
        set(iterations) == boundaries
        and all(row.get("anchor_reconsumed") is True for row in iterations.values())
    )
    drift_row = iterations.get("target-drift", {})
    contradiction_row = iterations.get("contradicts-invariant", {})
    invariant_source_linked = any(
        row.get("id") == invariant["id"]
        and set(row.get("source_ids", [])) >= expected_sources
        and _nonempty_text(row.get("statement"))
        for row in invariant_rows
        if isinstance(row, Mapping)
    )
    structural = {
        "representative_source_inspection": inspected >= expected_sources,
        "conditional_multi_example_use": len(inspected) >= 2,
        "invariant_hypothesis_variant_accident_separation": (
            invariant["id"] in ids(invariant_rows)
            and bool(ids(hypothesis_rows))
            and variant["id"] in ids(variant_rows)
            and accident["id"] in ids(accident_rows)
            and not ({variant["id"], accident["id"]} & ids(invariant_rows))
        ),
        "source_provenance": invariant_source_linked and anchor_sources >= expected_sources,
        "relational_function_transfer": invariant["id"] in mappings,
        "anchor_creation_with_required_fields": (
            set(anchor) == OPEN_ANCHOR_KEYS
            and all(_nonempty_text(anchor.get(key)) for key in ("PARENT_OBJECTIVE", "CONSUMER", "LAST_REANCHOR_REASON"))
            and bool(anchor_sources)
            and bool(anchor_invariants)
            and bool(anchor_variants)
            and bool(anchor_anti)
        ),
        "anchor_reconsumption_at_later_boundaries": all_iterations_reconsumed,
        "explicit_target_drift_detection": (
            drift_row.get("local_checks_pass") is True
            and drift_row.get("drift_detected") is True
        ),
        "preservation_of_grounded_constraints_when_local_checks_pass": all(
            row.get("mapping_preserved") is True
            for row in iterations.values()
            if row.get("local_checks_pass") is True
        ) and bool(iterations),
        "re_ground_and_replan_on_invariant_contradiction": (
            contradiction_row.get("anchor_reconsumed") is True
            and contradiction_row.get("drift_detected") is True
            and contradiction_row.get("replanned") is True
        ),
    }
    failures = [name for name, passed in structural.items() if not passed]
    return structural, failures


def _score_control(
    control: Mapping[str, Any], response: Mapping[str, Any]
) -> tuple[bool, list[str]]:
    failures: list[str] = []
    if response.get("task_id") != control["id"]:
        failures.append("task_id")
    if response.get("grounding_triggered") is not False:
        failures.append("grounding_triggered")
    if response.get("anchor_created") is not False:
        failures.append("anchor_created")
    if not _nonempty_text(response.get("action")):
        failures.append("action")
    return not failures, failures


def score(manifest: Mapping[str, Any], responses: Iterable[Mapping[str, Any]]) -> dict[str, Any]:
    by_id = {response.get("task_id"): response for response in responses}
    expected_ids = {
        challenge["id"] for challenge in manifest["challenges"]
    } | {control["id"] for control in manifest["direct_controls"]}
    if set(by_id) != expected_ids:
        return {
            "status": "MEASUREMENT_FAILURE",
            "failures": ["response_set_does_not_match_manifest"],
            "manifest_sha256": manifest_sha256(),
        }
    task_scores: dict[str, Any] = {}
    all_pass = True
    for challenge in manifest["challenges"]:
        checks, failures = _score_open_task(challenge, by_id[challenge["id"]])
        task_scores[challenge["id"]] = {"checks": checks, "failures": failures}
        all_pass = all_pass and not failures
    for control in manifest["direct_controls"]:
        passed, failures = _score_control(control, by_id[control["id"]])
        task_scores[control["id"]] = {"checks": {"no_unnecessary_direct_control_ceremony": passed}, "failures": failures}
        all_pass = all_pass and passed
    status = (
        "RETAIN_FOR_HELD_OUT"
        if all_pass
        else "REVERT"
    )
    return {
        "status": status,
        "verdict": manifest["scoring_rule"]["terminal_mapping"][
            "all_required_checks_pass" if all_pass else "one_or_more_structural_checks_fail"
        ],
        "manifest_sha256": manifest_sha256(),
        "tasks": task_scores,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--responses", required=True, type=Path)
    parser.add_argument("--manifest", type=Path, default=MANIFEST_PATH)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args(argv)
    manifest = load_manifest(args.manifest)
    responses = json.loads(args.responses.read_text(encoding="utf-8"))
    result = score(manifest, responses)
    payload = json.dumps(result, ensure_ascii=False, indent=2) + "\n"
    if args.output:
        args.output.write_text(payload, encoding="utf-8")
    else:
        print(payload, end="")
    return 0 if result["status"] != "MEASUREMENT_FAILURE" else 2


if __name__ == "__main__":
    raise SystemExit(main())
