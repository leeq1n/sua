"""Canonical, runtime-neutral retry gate and serializable failure state.

The controller owns retry execution; this module owns the deterministic
decision boundary.  It deliberately does not infer authority or causal
layers from natural language.  Callers must classify those facts explicitly.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
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


def _normalized(value: str) -> str:
    return " ".join(value.casefold().split())


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
    causal_layer_changed: bool = False

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
        if self.artifact_role_placement is not None:
            object.__setattr__(
                self, "artifact_role_placement",
                _text(self.artifact_role_placement, "artifact_role_placement"),
            )
        object.__setattr__(self, "causal_layer_changed", bool(self.causal_layer_changed))

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
            "CAUSAL_LAYER_CHANGED": self.causal_layer_changed,
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
            artifact_role_placement=get("ARTIFACT_ROLE_PLACEMENT", ""),
            causal_layer_changed=get("CAUSAL_LAYER_CHANGED", False),
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
    CAUSAL_LAYER_CHANGED = property(lambda self: self.causal_layer_changed)


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
    artifact_role_placement: str = ""
    causal_layer_changed: Optional[bool] = None

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
            _text(self.artifact_role_placement, "artifact_role_placement"),
        )
        if self.causal_layer_changed is not None:
            object.__setattr__(self, "causal_layer_changed", bool(self.causal_layer_changed))

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
            "CAUSAL_LAYER_CHANGED": self.causal_layer_changed,
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
            artifact_role_placement=get("ARTIFACT_ROLE_PLACEMENT", ""),
            causal_layer_changed=get("CAUSAL_LAYER_CHANGED"),
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
        causal_layer_changed=(prior.causal_layer is not proposal.causal_layer),
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


__all__ = [
    "AcceptanceAuthority",
    "AuthorityBasis",
    "CausalLayer",
    "CriterionClass",
    "FailureClass",
    "GLOBAL_REPLAN_REQUIRED",
    "ACCEPTANCE_AUTHORITY_UNVERIFIED",
    "RETRY_ALLOWED",
    "RetryAttempt",
    "RetryDecision",
    "RetryGateResult",
    "RetryProposal",
    "RetryState",
    "evaluate_retry",
]
