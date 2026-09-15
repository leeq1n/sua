"""Collect fresh-agent responses for the frozen E4-A benchmark.

This module collects responses only. It never assigns subjective ratings and
never changes the frozen manifest or scorer. A configured provider is required
for a behavioral run; the structural fixture in the tests is not a substitute.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from pathlib import Path
from typing import Any, Callable, Iterable, Mapping, Optional


ROOT = Path(__file__).resolve().parents[1]
BASE_COMMIT = "a45de1b73ca4a959da0b7abf78e703f293a74427"
MANIFEST_PATH = ROOT / "benchmarks" / "e4_a_grounded_experience.json"
GUIDE_FILES = (
    "docs/PRINCIPLES_DETAIL_DETAIL.md",
    "docs/M_TWO_TRACK_REASONING_DETAIL.md",
    "docs/ADD_THEN_REDUCE.md",
    "docs/M_ACCEPTANCE_PROTOCOL_DETAIL.md",
)


def _git_source(path: str) -> str:
    result = subprocess.run(
        ["git", "show", f"{BASE_COMMIT}:{path}"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        encoding="utf-8",
        check=False,
    )
    if result.returncode != 0:
        raise RuntimeError(f"cannot read baseline guide {path}: {result.stderr.strip()}")
    return result.stdout


def build_guide(arm: str) -> tuple[str, list[str]]:
    """Build a revision-qualified guide for a fresh agent."""
    if arm not in {"baseline", "treatment"}:
        raise ValueError("arm must be baseline or treatment")
    chunks: list[str] = []
    sources: list[str] = []
    for path in GUIDE_FILES:
        if arm == "baseline":
            content = _git_source(path)
            label = f"{BASE_COMMIT}:{path}"
        else:
            content = (ROOT / path).read_text(encoding="utf-8")
            label = path
        chunks.append(content)
        sources.append(label)
    return "\n\n".join(chunks), sources


def _response_contract(manifest: Mapping[str, Any]) -> str:
    return json.dumps(manifest["response_contract"], ensure_ascii=False, indent=2)


def _task_prompt(task: Mapping[str, Any], manifest: Mapping[str, Any]) -> str:
    return (
        "Return exactly one JSON object, with no markdown fences. Use the response "
        "contract below. For an open-ended task, inspect the supplied representative "
        "observations, classify them, map the relational/function invariant to the "
        "current artifact or action, create the compact anchor, and explicitly "
        "re-consume it at every listed boundary. Preserve grounded constraints even "
        "when local checks pass; detect the target-drift signal and re-plan on the "
        "contradiction. For a direct control, execute directly and set the grounding "
        "flags false.\n\nRESPONSE CONTRACT:\n"
        + _response_contract(manifest)
        + "\n\nTASK PACKET:\n"
        + json.dumps(task, ensure_ascii=False, indent=2)
    )


def _default_llm(prompt: str, *, system: str, config: Any) -> str:
    from src.llm import chat_simple

    return chat_simple(prompt, system=system, config=config) or ""


def collect(
    arm: str,
    *,
    llm_call: Callable[..., str] = _default_llm,
    config: Optional[Any] = None,
    manifest: Optional[Mapping[str, Any]] = None,
) -> dict[str, Any]:
    """Collect one JSON response for every frozen challenge/control."""
    manifest = manifest or json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    guide, guide_sources = build_guide(arm)
    if config is None:
        from src.llm import LLMConfig

        config = LLMConfig.from_env()
    if not getattr(config, "ready", False):
        raise RuntimeError("LLM configuration is not ready")
    system = (
        "You are a fresh agent. Apply only the supplied guide and task packet. "
        "Do not assume access to repository files beyond the guide and packet. "
        "The task is scored mechanically for structure and provenance, not style.\n\n"
        "GUIDE:\n"
        + guide
    )
    tasks: Iterable[Mapping[str, Any]] = (
        *manifest["challenges"],
        *manifest["direct_controls"],
    )
    responses: list[dict[str, Any]] = []
    for task in tasks:
        raw = llm_call(_task_prompt(task, manifest), system=system, config=config)
        if not raw or not raw.strip():
            raise RuntimeError(f"empty fresh-agent response for {task['id']}")
        try:
            response = json.loads(raw)
        except json.JSONDecodeError as exc:
            raise RuntimeError(f"non-JSON fresh-agent response for {task['id']}") from exc
        if not isinstance(response, dict):
            raise RuntimeError(f"fresh-agent response for {task['id']} is not an object")
        responses.append(response)
    return {
        "schema_version": 1,
        "benchmark_id": manifest["benchmark_id"],
        "manifest_sha256": hashlib.sha256(MANIFEST_PATH.read_bytes()).hexdigest(),
        "arm": arm,
        "base_commit": BASE_COMMIT,
        "guide_sources": guide_sources,
        "responses": responses,
    }


def main(argv: Optional[list[str]] = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--arm", choices=("baseline", "treatment"), required=True)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args(argv)
    payload = collect(args.arm)
    args.output.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
