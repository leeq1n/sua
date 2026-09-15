"""Canonical, runtime-neutral retry gate and serializable failure state.

The controller owns retry execution; this module owns the deterministic
decision boundary.  It deliberately does not infer authority or causal
layers from natural language.  Callers must classify those facts explicitly.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, replace
from enum import Enum
from typing import Any, Mapping, Optional, Sequence, Type, TypeVar


class _ValueEnum(str, Enum):
    """String-valued enum with stable JSON values."""


class CriterionClass(_ValueEnum):
    USER_FACING = "USER_FACING"
    OBJECTIVE_SCIENTIFIC = "OBJECTIVE_SCIENTIFIC"
    OBJECTIVE_TECHNICAL = "OBJECTIVE_TECHNICAL"
    MIXED = "MIXED"
    UNKNOWN = "UNKNOWN"


class AcceptanceAuthority(_ValueEnum):
    USER = "USER"
    OBJECTIVE_EVIDENCE = "OBJECTIVE_EVIDENCE"
    MIXED = "MIXED"
    UNRESOLVED = "UNRESOLVED"


class AuthorityBasis(_ValueEnum):
    EXPLICIT_USER_REJECTION = "EXPLICIT_USER_REJECTION"
    INDEPENDENT_VERIFIED_EVIDENCE = "INDEPENDENT_VERIFIED_EVIDENCE"
    UNSUPPORTED_USER_ASSERTION = "UNSUPPORTED_USER_ASSERTION"
    EXPLICIT_ACCEPTANCE_OWNER = "EXPLICIT_ACCEPTANCE_OWNER"
    UNKNOWN = "UNKNOWN"


class FailureClass(_ValueEnum):
    USER_REJECTION = "USER_REJECTION"
    OBJECTIVE_FAILURE = "OBJECTIVE_FAILURE"
    AUTHORITY_DISPUTE = "AUTHORITY_DISPUTE"
    IMPLEMENTATION_FAILURE = "IMPLEMENTATION_FAILURE"
    UNKNOWN = "UNKNOWN"


class CausalLayer(_ValueEnum):
    LOCAL_PARAMETER = "LOCAL_PARAMETER"
    IMPLEMENTATION = "IMPLEMENTATION"
    SUBSTRATE_TOOL = "SUBSTRATE_TOOL"
    REPRESENTATION_FRAMING = "REPRESENTATION_FRAMING"
    ARTIFACT_ROLE_PLACEMENT = "ARTIFACT_ROLE_PLACEMENT"
    PARENT_OBJECTIVE = "PARENT_OBJECTIVE"
    UNKNOWN = "UNKNOWN"


class RetryDecision(_ValueEnum):
    RETRY_ALLOWED = "RETRY_ALLOWED"
    GLOBAL_REPLAN_REQUIRED = "GLOBAL_REPLAN_REQUIRED"
    ACCEPTANCE_AUTHORITY_UNVERIFIED = "ACCEPTANCE_AUTHORITY_UNVERIFIED"
    RETRY_CONTEXT_REQUIRED = "RETRY_CONTEXT_REQUIRED"


E = TypeVar("E", bound=_ValueEnum)


def _enum_value(value: E | str, enum_type: Type[E]) -> E:
    if isinstance(value, enum_type):
        return value
    try:
        return enum_type(str(value).strip().upper().replace("-", "_"))
    except ValueError as exc:
        choices = ", ".join(item.value for item in enum_type)
        raise ValueError(f"invalid {enum_type.__name__} {value!r}; expected {choices}") from exc


def _text(value: Any, field_name: str, *, required: bool = False) -> str:
    result = "" if value is None else str(value).strip()
    if required and not result:
        raise ValueError(f"{field_name} must not be empty")
    return result


def _text_tuple(value: Optional[Sequence[Any] | str]) -> tuple[str, ...]:
    if value is None:
        return ()
    if isinstance(value, str):
        return (value,) if value.strip() else ()
    return tuple(str(item).strip() for item in value if str(item).strip())


def _optional_text(value: Any, field_name: str) -> Optional[str]:
    if value is None:
        return None
    result = _text(value, field_name)
    return result or None


def _normalized(value: str) -> str:
    return " ".join(value.casefold().split())


def _dedupe_text(values: Optional[Sequence[Any] | str]) -> tuple[str, ...]:
    seen: set[str] = set()
    result: list[str] = []
    for value in _text_tuple(values):
        normalized = _normalized(value)
        if normalized not in seen:
            seen.add(normalized)
            result.append(value)
    return tuple(result)


@dataclass(frozen=True)
class ExperienceSource:
    """One provenance-preserving observation used by a task-scoped anchor."""

    source_id: str
    title: str
    locator: str
    observation: str
    function: str

    def __post_init__(self) -> None:
        for field_name in ("source_id", "title", "locator", "observation", "function"):
            object.__setattr__(
                self,
                field_name,
                _text(getattr(self, field_name), field_name, required=True),
            )

    def to_dict(self) -> dict[str, str]:
        return {
            "SOURCE_ID": self.source_id,
            "TITLE": self.title,
            "LOCATOR": self.locator,
            "OBSERVATION": self.observation,
            "FUNCTION": self.function,
        }

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> "ExperienceSource":
        def get(name: str) -> Any:
            return data[name] if name in data else data.get(name.lower())

        return cls(
            source_id=get("SOURCE_ID"),
            title=get("TITLE"),
            locator=get("LOCATOR") or get("URL"),
            observation=get("OBSERVATION"),
            function=get("FUNCTION"),
        )


@dataclass(frozen=True)
class ExperienceMapping:
    """Relate an evidence-backed constraint to the current work."""

    constraint: str
    artifact_or_action: str
    function_mapping: str

    def __post_init__(self) -> None:
        for field_name in ("constraint", "artifact_or_action", "function_mapping"):
            object.__setattr__(
                self,
                field_name,
                _text(getattr(self, field_name), field_name, required=True),
            )

    def to_dict(self) -> dict[str, str]:
        return {
            "CONSTRAINT": self.constraint,
            "ARTIFACT_OR_ACTION": self.artifact_or_action,
            "FUNCTION_MAPPING": self.function_mapping,
        }

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> "ExperienceMapping":
        def get(name: str) -> Any:
            return data[name] if name in data else data.get(name.lower())

        return cls(
            constraint=get("CONSTRAINT"),
            artifact_or_action=get("ARTIFACT_OR_ACTION"),
            function_mapping=get("FUNCTION_MAPPING"),
        )


def _coerce_source(value: ExperienceSource | Mapping[str, Any]) -> ExperienceSource:
    return value if isinstance(value, ExperienceSource) else ExperienceSource.from_dict(value)


def _coerce_mapping(value: ExperienceMapping | Mapping[str, Any]) -> ExperienceMapping:
    return value if isinstance(value, ExperienceMapping) else ExperienceMapping.from_dict(value)


@dataclass(frozen=True)
class GroundedExperienceAnchor:
    """Compact, task-scoped memory for externally grounded open-ended work.

    This is deliberately a value object. It has no database, global ledger, or
    retrieval policy. A caller creates it after grounding and carries it on an
    existing task/acceptance state surface.
    """

    parent_objective: str
    consumer: str
    evidence_sources: tuple[ExperienceSource, ...] | Sequence[ExperienceSource | Mapping[str, Any]]
    evidence_backed_invariants: tuple[str, ...] | Sequence[str]
    tentative_hypotheses: tuple[str, ...] | Sequence[str] = ()
    non_binding_variants: tuple[str, ...] | Sequence[str] = ()
    negative_knowledge_anti_patterns: tuple[str, ...] | Sequence[str] = ()
    current_constraint_to_artifact_or_action_mapping: tuple[ExperienceMapping, ...] | Sequence[ExperienceMapping | Mapping[str, Any]] = ()
    last_reanchor_reason: str = "initial grounding"

    def __post_init__(self) -> None:
        object.__setattr__(self, "parent_objective", _text(self.parent_objective, "parent_objective", required=True))
        object.__setattr__(self, "consumer", _text(self.consumer, "consumer", required=True))
        sources = tuple(_coerce_source(item) for item in self.evidence_sources)
        if not sources:
            raise ValueError("evidence_sources must contain provenance")
        if len({item.source_id for item in sources}) != len(sources):
            raise ValueError("evidence_sources must have unique source_id values")
        object.__setattr__(self, "evidence_sources", sources)
        invariants = _dedupe_text(self.evidence_backed_invariants)
        if not invariants:
            raise ValueError("evidence_backed_invariants must not be empty")
        hypotheses = _dedupe_text(self.tentative_hypotheses)
        variants = _dedupe_text(self.non_binding_variants)
        accidents = _dedupe_text(self.negative_knowledge_anti_patterns)
        if set(map(_normalized, invariants)) & (set(map(_normalized, hypotheses)) | set(map(_normalized, variants))):
            raise ValueError("tentative hypotheses and variants cannot become invariants")
        object.__setattr__(self, "evidence_backed_invariants", invariants)
        object.__setattr__(self, "tentative_hypotheses", hypotheses)
        object.__setattr__(self, "non_binding_variants", variants)
        object.__setattr__(self, "negative_knowledge_anti_patterns", accidents)
        mappings = tuple(_coerce_mapping(item) for item in self.current_constraint_to_artifact_or_action_mapping)
        if not mappings:
            raise ValueError("current constraint-to-artifact mapping must not be empty")
        object.__setattr__(self, "current_constraint_to_artifact_or_action_mapping", mappings)
        object.__setattr__(self, "last_reanchor_reason", _text(self.last_reanchor_reason, "last_reanchor_reason", required=True))

    def to_dict(self) -> dict[str, Any]:
        return {
            "PARENT_OBJECTIVE": self.parent_objective,
            "CONSUMER": self.consumer,
            "EVIDENCE_SOURCES": [item.to_dict() for item in self.evidence_sources],
            "EVIDENCE_BACKED_INVARIANTS": list(self.evidence_backed_invariants),
            "TENTATIVE_HYPOTHESES": list(self.tentative_hypotheses),
            "NON_BINDING_VARIANTS": list(self.non_binding_variants),
            "NEGATIVE_KNOWLEDGE_ANTI_PATTERNS": list(self.negative_knowledge_anti_patterns),
            "CURRENT_CONSTRAINT_TO_ARTIFACT_OR_ACTION_MAPPING": [
                item.to_dict() for item in self.current_constraint_to_artifact_or_action_mapping
            ],
            "LAST_REANCHOR_REASON": self.last_reanchor_reason,
        }

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> "GroundedExperienceAnchor":
        def get(name: str, default: Any = None) -> Any:
            return data[name] if name in data else data.get(name.lower(), default)

        return cls(
            parent_objective=get("PARENT_OBJECTIVE"),
            consumer=get("CONSUMER"),
            evidence_sources=tuple(_coerce_source(item) for item in get("EVIDENCE_SOURCES", ())),
            evidence_backed_invariants=get("EVIDENCE_BACKED_INVARIANTS", ()),
            tentative_hypotheses=get("TENTATIVE_HYPOTHESES", ()),
            non_binding_variants=get("NON_BINDING_VARIANTS", ()),
            negative_knowledge_anti_patterns=get("NEGATIVE_KNOWLEDGE_ANTI_PATTERNS", ()),
            current_constraint_to_artifact_or_action_mapping=tuple(
                _coerce_mapping(item)
                for item in get("CURRENT_CONSTRAINT_TO_ARTIFACT_OR_ACTION_MAPPING", ())
            ),
            last_reanchor_reason=get("LAST_REANCHOR_REASON", "initial grounding"),
        )

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), sort_keys=True)

    @classmethod
    def from_json(cls, value: str) -> "GroundedExperienceAnchor":
        return cls.from_dict(json.loads(value))

    def reconsume(
        self,
        reason: str,
        *,
        mapping: Optional[ExperienceMapping | Mapping[str, Any]] = None,
    ) -> "GroundedExperienceAnchor":
        """Re-read the compact anchor at a meaningful boundary.

        Re-consumption changes only the current action mapping and boundary
        reason. Evidence-backed classifications remain frozen until explicit
        new evidence is supplied through ``update_from_evidence``.
        """
        mappings = self.current_constraint_to_artifact_or_action_mapping
        if mapping is not None:
            mappings = (*mappings, _coerce_mapping(mapping))
        return replace(
            self,
            current_constraint_to_artifact_or_action_mapping=mappings,
            last_reanchor_reason=_text(reason, "reason", required=True),
        )

    def update_from_evidence(
        self,
        reason: str,
        *,
        evidence_sources: Sequence[ExperienceSource | Mapping[str, Any]],
        evidence_backed_invariants: Optional[Sequence[str]] = None,
        tentative_hypotheses: Optional[Sequence[str]] = None,
        non_binding_variants: Optional[Sequence[str]] = None,
        negative_knowledge_anti_patterns: Optional[Sequence[str]] = None,
        mapping: Optional[ExperienceMapping | Mapping[str, Any]] = None,
    ) -> "GroundedExperienceAnchor":
        """Update classifications only when new provenance is supplied."""
        new_sources = tuple(_coerce_source(item) for item in evidence_sources)
        if not new_sources:
            raise ValueError("new evidence is required to update the anchor")
        sources_by_id = {item.source_id: item for item in self.evidence_sources}
        sources_by_id.update({item.source_id: item for item in new_sources})
        mappings = self.current_constraint_to_artifact_or_action_mapping
        if mapping is not None:
            mappings = (*mappings, _coerce_mapping(mapping))
        return GroundedExperienceAnchor(
            parent_objective=self.parent_objective,
            consumer=self.consumer,
            evidence_sources=tuple(sources_by_id.values()),
            evidence_backed_invariants=(
                self.evidence_backed_invariants
                if evidence_backed_invariants is None else evidence_backed_invariants
            ),
            tentative_hypotheses=(
                self.tentative_hypotheses
                if tentative_hypotheses is None else tentative_hypotheses
            ),
            non_binding_variants=(
                self.non_binding_variants
                if non_binding_variants is None else non_binding_variants
            ),
            negative_knowledge_anti_patterns=(
                self.negative_knowledge_anti_patterns
                if negative_knowledge_anti_patterns is None else negative_knowledge_anti_patterns
            ),
            current_constraint_to_artifact_or_action_mapping=mappings,
            last_reanchor_reason=_text(reason, "reason", required=True),
        )


@dataclass(frozen=True)
class RetryState:
    """Failure/rejection state that a caller can persist and reload."""

    parent_objective: str
    failed_acceptance_criterion: str
    criterion_class: CriterionClass | str
    acceptance_authority: AcceptanceAuthority | str
    authority_basis: AuthorityBasis | str
    failure_class: FailureClass | str
    representation_family: str
    production_substrate: str
    causal_layer: CausalLayer | str
    causal_delta: str
    negative_knowledge: tuple[str, ...] | Sequence[str] = ()
    unchanged_assumptions: tuple[str, ...] | Sequence[str] = ()
    prior_local_pass: bool = False
    artifact_role_placement: Optional[str] = None
    representation_variant: Optional[str] = None
    causal_layer_changed: bool = False
    grounded_experience_anchor: Optional[GroundedExperienceAnchor | Mapping[str, Any]] = None

    def __post_init__(self) -> None:
        object.__setattr__(
            self, "parent_objective",
            _text(self.parent_objective, "parent_objective", required=True),
        )
        object.__setattr__(
            self, "failed_acceptance_criterion",
            _text(self.failed_acceptance_criterion, "failed_acceptance_criterion", required=True),
        )
        object.__setattr__(
            self, "criterion_class", _enum_value(self.criterion_class, CriterionClass)
        )
        object.__setattr__(
            self, "acceptance_authority",
            _enum_value(self.acceptance_authority, AcceptanceAuthority),
        )
        object.__setattr__(self, "authority_basis", _enum_value(self.authority_basis, AuthorityBasis))
        object.__setattr__(
            self, "failure_class", _enum_value(self.failure_class, FailureClass)
        )
        object.__setattr__(
            self, "representation_family",
            _text(self.representation_family, "representation_family", required=True),
        )
        object.__setattr__(
            self, "production_substrate",
            _text(self.production_substrate, "production_substrate", required=True),
        )
        object.__setattr__(
            self, "causal_layer", _enum_value(self.causal_layer, CausalLayer)
        )
        object.__setattr__(self, "causal_delta", _text(self.causal_delta, "causal_delta"))
        object.__setattr__(self, "negative_knowledge", _text_tuple(self.negative_knowledge))
        object.__setattr__(self, "unchanged_assumptions", _text_tuple(self.unchanged_assumptions))
        object.__setattr__(self, "prior_local_pass", bool(self.prior_local_pass))
        object.__setattr__(
            self, "artifact_role_placement",
            _optional_text(self.artifact_role_placement, "artifact_role_placement"),
        )
        object.__setattr__(
            self, "representation_variant",
            _optional_text(self.representation_variant, "representation_variant"),
        )
        object.__setattr__(self, "causal_layer_changed", bool(self.causal_layer_changed))
        if self.grounded_experience_anchor is not None and not isinstance(
            self.grounded_experience_anchor, GroundedExperienceAnchor
        ):
            object.__setattr__(
                self,
                "grounded_experience_anchor",
                GroundedExperienceAnchor.from_dict(self.grounded_experience_anchor),
            )

    def to_dict(self) -> dict[str, Any]:
        """Return the stable, uppercase field schema used by runtimes."""
        return {
            "PARENT_OBJECTIVE": self.parent_objective,
            "FAILED_ACCEPTANCE_CRITERION": self.failed_acceptance_criterion,
            "CRITERION_CLASS": self.criterion_class.value,
            "ACCEPTANCE_AUTHORITY": self.acceptance_authority.value,
            "AUTHORITY_BASIS": self.authority_basis.value,
            "FAILURE_CLASS": self.failure_class.value,
            "REPRESENTATION_FAMILY": self.representation_family,
            "PRODUCTION_SUBSTRATE": self.production_substrate,
            "CAUSAL_LAYER": self.causal_layer.value,
            "CAUSAL_DELTA": self.causal_delta,
            "NEGATIVE_KNOWLEDGE": list(self.negative_knowledge),
            "UNCHANGED_ASSUMPTIONS": list(self.unchanged_assumptions),
            "PRIOR_LOCAL_PASS": self.prior_local_pass,
            "ARTIFACT_ROLE_PLACEMENT": self.artifact_role_placement,
            "REPRESENTATION_VARIANT": self.representation_variant,
            "CAUSAL_LAYER_CHANGED": self.causal_layer_changed,
            "GROUNDED_EXPERIENCE_ANCHOR": (
                self.grounded_experience_anchor.to_dict()
                if self.grounded_experience_anchor is not None else None
            ),
        }

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), sort_keys=True)

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> "RetryState":
        """Load the canonical schema, accepting snake-case aliases too."""
        def get(name: str, default: Any = None) -> Any:
            return data[name] if name in data else data.get(name.lower(), default)

        return cls(
            parent_objective=get("PARENT_OBJECTIVE"),
            failed_acceptance_criterion=get("FAILED_ACCEPTANCE_CRITERION"),
            criterion_class=get("CRITERION_CLASS"),
            acceptance_authority=get("ACCEPTANCE_AUTHORITY"),
            authority_basis=get("AUTHORITY_BASIS"),
            failure_class=get("FAILURE_CLASS"),
            representation_family=get("REPRESENTATION_FAMILY"),
            production_substrate=get("PRODUCTION_SUBSTRATE"),
            causal_layer=get("CAUSAL_LAYER"),
            causal_delta=get("CAUSAL_DELTA", ""),
            negative_knowledge=get("NEGATIVE_KNOWLEDGE", ()),
            unchanged_assumptions=get("UNCHANGED_ASSUMPTIONS", ()),
            prior_local_pass=get("PRIOR_LOCAL_PASS", False),
            artifact_role_placement=get("ARTIFACT_ROLE_PLACEMENT", None),
            representation_variant=get("REPRESENTATION_VARIANT", None),
            causal_layer_changed=get("CAUSAL_LAYER_CHANGED", False),
            grounded_experience_anchor=get("GROUNDED_EXPERIENCE_ANCHOR", None),
        )

    @classmethod
    def from_json(cls, value: str) -> "RetryState":
        return cls.from_dict(json.loads(value))

    # Uppercase aliases make the schema inspectable without changing Python
    # naming conventions used by the rest of the repository.
    PARENT_OBJECTIVE = property(lambda self: self.parent_objective)
    FAILED_ACCEPTANCE_CRITERION = property(lambda self: self.failed_acceptance_criterion)
    CRITERION_CLASS = property(lambda self: self.criterion_class)
    ACCEPTANCE_AUTHORITY = property(lambda self: self.acceptance_authority)
    AUTHORITY_BASIS = property(lambda self: self.authority_basis)
    FAILURE_CLASS = property(lambda self: self.failure_class)
    REPRESENTATION_FAMILY = property(lambda self: self.representation_family)
    PRODUCTION_SUBSTRATE = property(lambda self: self.production_substrate)
    CAUSAL_LAYER = property(lambda self: self.causal_layer)
    CAUSAL_DELTA = property(lambda self: self.causal_delta)
    NEGATIVE_KNOWLEDGE = property(lambda self: self.negative_knowledge)
    UNCHANGED_ASSUMPTIONS = property(lambda self: self.unchanged_assumptions)
    PRIOR_LOCAL_PASS = property(lambda self: self.prior_local_pass)
    ARTIFACT_ROLE_PLACEMENT = property(lambda self: self.artifact_role_placement)
    REPRESENTATION_VARIANT = property(lambda self: self.representation_variant)
    CAUSAL_LAYER_CHANGED = property(lambda self: self.causal_layer_changed)
    GROUNDED_EXPERIENCE_ANCHOR = property(lambda self: self.grounded_experience_anchor)


@dataclass(frozen=True)
class RetryProposal:
    """Explicit classification of a proposed next attempt."""

    parent_objective: str
    failed_acceptance_criterion: str
    criterion_class: CriterionClass | str
    acceptance_authority: AcceptanceAuthority | str
    authority_basis: AuthorityBasis | str
    failure_class: FailureClass | str
    representation_family: str
    production_substrate: str
    causal_layer: CausalLayer | str
    causal_delta: str
    unchanged_assumptions: tuple[str, ...] | Sequence[str] = ()
    artifact_role_placement: Optional[str] = None
    representation_variant: Optional[str] = None
    causal_layer_changed: Optional[bool] = None
    grounded_experience_anchor: Optional[GroundedExperienceAnchor | Mapping[str, Any]] = None

    def __post_init__(self) -> None:
        object.__setattr__(
            self, "parent_objective",
            _text(self.parent_objective, "parent_objective", required=True),
        )
        object.__setattr__(
            self, "failed_acceptance_criterion",
            _text(self.failed_acceptance_criterion, "failed_acceptance_criterion", required=True),
        )
        object.__setattr__(
            self, "criterion_class", _enum_value(self.criterion_class, CriterionClass)
        )
        object.__setattr__(
            self, "acceptance_authority",
            _enum_value(self.acceptance_authority, AcceptanceAuthority),
        )
        object.__setattr__(self, "authority_basis", _enum_value(self.authority_basis, AuthorityBasis))
        object.__setattr__(
            self, "failure_class", _enum_value(self.failure_class, FailureClass)
        )
        object.__setattr__(
            self, "representation_family",
            _text(self.representation_family, "representation_family", required=True),
        )
        object.__setattr__(
            self, "production_substrate",
            _text(self.production_substrate, "production_substrate", required=True),
        )
        object.__setattr__(
            self, "causal_layer", _enum_value(self.causal_layer, CausalLayer)
        )
        object.__setattr__(self, "causal_delta", _text(self.causal_delta, "causal_delta"))
        object.__setattr__(self, "unchanged_assumptions", _text_tuple(self.unchanged_assumptions))
        object.__setattr__(
            self, "artifact_role_placement",
            _optional_text(self.artifact_role_placement, "artifact_role_placement"),
        )
        object.__setattr__(
            self, "representation_variant",
            _optional_text(self.representation_variant, "representation_variant"),
        )
        if self.causal_layer_changed is not None:
            object.__setattr__(self, "causal_layer_changed", bool(self.causal_layer_changed))
        if self.grounded_experience_anchor is not None and not isinstance(
            self.grounded_experience_anchor, GroundedExperienceAnchor
        ):
            object.__setattr__(
                self,
                "grounded_experience_anchor",
                GroundedExperienceAnchor.from_dict(self.grounded_experience_anchor),
            )

    def to_dict(self) -> dict[str, Any]:
        return {
            "PARENT_OBJECTIVE": self.parent_objective,
            "FAILED_ACCEPTANCE_CRITERION": self.failed_acceptance_criterion,
            "CRITERION_CLASS": self.criterion_class.value,
            "ACCEPTANCE_AUTHORITY": self.acceptance_authority.value,
            "AUTHORITY_BASIS": self.authority_basis.value,
            "FAILURE_CLASS": self.failure_class.value,
            "REPRESENTATION_FAMILY": self.representation_family,
            "PRODUCTION_SUBSTRATE": self.production_substrate,
            "CAUSAL_LAYER": self.causal_layer.value,
            "CAUSAL_DELTA": self.causal_delta,
            "UNCHANGED_ASSUMPTIONS": list(self.unchanged_assumptions),
            "ARTIFACT_ROLE_PLACEMENT": self.artifact_role_placement,
            "REPRESENTATION_VARIANT": self.representation_variant,
            "CAUSAL_LAYER_CHANGED": self.causal_layer_changed,
            "GROUNDED_EXPERIENCE_ANCHOR": (
                self.grounded_experience_anchor.to_dict()
                if self.grounded_experience_anchor is not None else None
            ),
        }

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> "RetryProposal":
        def get(name: str, default: Any = None) -> Any:
            return data[name] if name in data else data.get(name.lower(), default)

        return cls(
            parent_objective=get("PARENT_OBJECTIVE"),
            failed_acceptance_criterion=get("FAILED_ACCEPTANCE_CRITERION"),
            criterion_class=get("CRITERION_CLASS"),
            acceptance_authority=get("ACCEPTANCE_AUTHORITY"),
            authority_basis=get("AUTHORITY_BASIS"),
            failure_class=get("FAILURE_CLASS"),
            representation_family=get("REPRESENTATION_FAMILY"),
            production_substrate=get("PRODUCTION_SUBSTRATE"),
            causal_layer=get("CAUSAL_LAYER"),
            causal_delta=get("CAUSAL_DELTA", ""),
            unchanged_assumptions=get("UNCHANGED_ASSUMPTIONS", ()),
            artifact_role_placement=get("ARTIFACT_ROLE_PLACEMENT", None),
            representation_variant=get("REPRESENTATION_VARIANT", None),
            causal_layer_changed=get("CAUSAL_LAYER_CHANGED"),
            grounded_experience_anchor=get("GROUNDED_EXPERIENCE_ANCHOR", None),
        )


RetryAttempt = RetryProposal


@dataclass(frozen=True)
class RetryGateResult:
    decision: RetryDecision
    state: RetryState
    reason: str
    prior_local_pass_invalidated: bool = False
    structural_delta_valid: bool = False

    def to_dict(self) -> dict[str, Any]:
        return {
            "DECISION": self.decision.value,
            "STATE": self.state.to_dict(),
            "REASON": self.reason,
            "PRIOR_LOCAL_PASS_INVALIDATED": self.prior_local_pass_invalidated,
            "STRUCTURAL_DELTA_VALID": self.structural_delta_valid,
        }


def _coerce_state(value: RetryState | Mapping[str, Any]) -> RetryState:
    return value if isinstance(value, RetryState) else RetryState.from_dict(value)


def _coerce_proposal(value: RetryProposal | Mapping[str, Any]) -> RetryProposal:
    return value if isinstance(value, RetryProposal) else RetryProposal.from_dict(value)


def _authority_resolved(state: RetryState | RetryProposal) -> bool:
    if state.authority_basis is AuthorityBasis.UNSUPPORTED_USER_ASSERTION:
        return False
    if state.criterion_class is CriterionClass.USER_FACING:
        return (
            state.acceptance_authority is AcceptanceAuthority.USER
            and state.authority_basis is AuthorityBasis.EXPLICIT_USER_REJECTION
            and state.failure_class is FailureClass.USER_REJECTION
        )
    if state.criterion_class in {
        CriterionClass.OBJECTIVE_SCIENTIFIC,
        CriterionClass.OBJECTIVE_TECHNICAL,
    }:
        return (
            state.acceptance_authority is AcceptanceAuthority.OBJECTIVE_EVIDENCE
            and state.authority_basis is AuthorityBasis.INDEPENDENT_VERIFIED_EVIDENCE
            and state.failure_class is FailureClass.OBJECTIVE_FAILURE
        )
    return False


def _same_core_criterion(prior: RetryState, proposal: RetryProposal) -> bool:
    return (
        _normalized(prior.parent_objective) == _normalized(proposal.parent_objective)
        and _normalized(prior.failed_acceptance_criterion)
        == _normalized(proposal.failed_acceptance_criterion)
        and prior.criterion_class is proposal.criterion_class
    )


def _structural_delta_is_coherent(
    prior: RetryState, proposal: RetryProposal
) -> bool:
    """Require an explicit delta and at least one changed causal field."""
    if not proposal.causal_delta:
        return False
    return any(
        (
            prior.parent_objective != proposal.parent_objective,
            prior.representation_family != proposal.representation_family,
            prior.production_substrate != proposal.production_substrate,
            prior.causal_layer is not proposal.causal_layer,
            proposal.artifact_role_placement is not None
            and prior.artifact_role_placement != proposal.artifact_role_placement,
        )
    )


def _carry_failure_forward(
    prior: RetryState, proposal: RetryProposal
) -> RetryState:
    facts = list(prior.negative_knowledge)
    for fact in (
        f"REJECTED_REPRESENTATION_FAMILY={prior.representation_family}",
        f"REJECTED_PRODUCTION_SUBSTRATE={prior.production_substrate}",
    ):
        if fact not in facts:
            facts.append(fact)
    for assumption in prior.unchanged_assumptions:
        if assumption not in facts:
            facts.append(f"UNCHANGED_ASSUMPTION={assumption}")
    assumptions = list(prior.unchanged_assumptions)
    for assumption in proposal.unchanged_assumptions:
        if assumption not in assumptions:
            assumptions.append(assumption)
    return RetryState(
        parent_objective=proposal.parent_objective,
        failed_acceptance_criterion=proposal.failed_acceptance_criterion,
        criterion_class=proposal.criterion_class,
        acceptance_authority=proposal.acceptance_authority,
        authority_basis=proposal.authority_basis,
        failure_class=proposal.failure_class,
        representation_family=proposal.representation_family,
        production_substrate=proposal.production_substrate,
        causal_layer=proposal.causal_layer,
        causal_delta=proposal.causal_delta,
        negative_knowledge=facts,
        unchanged_assumptions=assumptions,
        prior_local_pass=False,
        artifact_role_placement=(
            proposal.artifact_role_placement
            if proposal.artifact_role_placement is not None
            else prior.artifact_role_placement
        ),
        representation_variant=(
            proposal.representation_variant
            if proposal.representation_variant is not None
            else prior.representation_variant
        ),
        causal_layer_changed=(prior.causal_layer is not proposal.causal_layer),
        grounded_experience_anchor=(
            proposal.grounded_experience_anchor
            if proposal.grounded_experience_anchor is not None
            else prior.grounded_experience_anchor
        ),
    )


def evaluate_retry(
    prior_state: RetryState | Mapping[str, Any] | None,
    proposed_state: RetryProposal | Mapping[str, Any] | None,
) -> RetryGateResult:
    """Return the only retry decisions the canonical controller may use.

    Authority is fail-closed.  Same-core, same-class failures require a
    coherent causal delta; the rule never examines a rejection count.
    """
    if prior_state is None:
        if proposed_state is None:
            raise ValueError("a proposed state is required when no prior state exists")
        proposal = _coerce_proposal(proposed_state)
        if not _authority_resolved(proposal):
            state = RetryState.from_dict(proposal.to_dict())
            return RetryGateResult(
                RetryDecision.ACCEPTANCE_AUTHORITY_UNVERIFIED,
                state,
                "acceptance authority or evidence basis is unresolved",
            )
        state = RetryState.from_dict(proposal.to_dict())
        return RetryGateResult(
            RetryDecision.RETRY_ALLOWED,
            state,
            "no prior failure state; proposed authority is resolved",
        )

    prior = _coerce_state(prior_state)
    if proposed_state is None:
        return RetryGateResult(
            RetryDecision.ACCEPTANCE_AUTHORITY_UNVERIFIED,
            prior,
            "proposed next-attempt state is missing",
        )
    proposal = _coerce_proposal(proposed_state)

    if not _authority_resolved(prior) or not _authority_resolved(proposal):
        return RetryGateResult(
            RetryDecision.ACCEPTANCE_AUTHORITY_UNVERIFIED,
            prior,
            "acceptance authority or evidence basis is unresolved; prior evidence is unchanged",
        )

    carried = _carry_failure_forward(prior, proposal)
    invalidated = prior.prior_local_pass or prior.failure_class is FailureClass.USER_REJECTION

    if not _same_core_criterion(prior, proposal):
        return RetryGateResult(
            RetryDecision.RETRY_ALLOWED,
            carried,
            "criterion or parent objective changed; this is not a repeated same-core retry",
            prior_local_pass_invalidated=invalidated,
            structural_delta_valid=False,
        )

    structural = _structural_delta_is_coherent(prior, proposal)
    same_failure_class = prior.failure_class is proposal.failure_class
    if same_failure_class and not structural:
        return RetryGateResult(
            RetryDecision.GLOBAL_REPLAN_REQUIRED,
            carried,
            "same-core failure has no coherent causal delta; local retry is stopped",
            prior_local_pass_invalidated=invalidated,
            structural_delta_valid=False,
        )

    return RetryGateResult(
        RetryDecision.RETRY_ALLOWED,
        carried,
        "authority is resolved and the proposal contains a coherent causal delta",
        prior_local_pass_invalidated=invalidated,
        structural_delta_valid=structural,
    )


RETRY_ALLOWED = RetryDecision.RETRY_ALLOWED
GLOBAL_REPLAN_REQUIRED = RetryDecision.GLOBAL_REPLAN_REQUIRED
ACCEPTANCE_AUTHORITY_UNVERIFIED = RetryDecision.ACCEPTANCE_AUTHORITY_UNVERIFIED
RETRY_CONTEXT_REQUIRED = RetryDecision.RETRY_CONTEXT_REQUIRED


__all__ = [
    "AcceptanceAuthority",
    "AuthorityBasis",
    "CausalLayer",
    "CriterionClass",
    "FailureClass",
    "ExperienceMapping",
    "ExperienceSource",
    "GroundedExperienceAnchor",
    "GLOBAL_REPLAN_REQUIRED",
    "ACCEPTANCE_AUTHORITY_UNVERIFIED",
    "RETRY_CONTEXT_REQUIRED",
    "RETRY_ALLOWED",
    "RetryAttempt",
    "RetryDecision",
    "RetryGateResult",
    "RetryProposal",
    "RetryState",
    "evaluate_retry",
]
