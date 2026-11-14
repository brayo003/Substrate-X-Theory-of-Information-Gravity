from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from types import MappingProxyType
from typing import Any, Mapping, Sequence, Tuple

from .ids import RevisionId, SnapshotId, TickId, WorldId


def freeze_value(value: Any) -> Any:
    if isinstance(value, MappingProxyType):
        return value
    if isinstance(value, dict):
        return MappingProxyType({key: freeze_value(inner) for key, inner in value.items()})
    if isinstance(value, list):
        return tuple(freeze_value(inner) for inner in value)
    if isinstance(value, tuple):
        return tuple(freeze_value(inner) for inner in value)
    if isinstance(value, set):
        return frozenset(freeze_value(inner) for inner in value)
    return value


def _freeze_mapping(mapping: Mapping[str, Any] | None) -> Mapping[str, Any]:
    return MappingProxyType({} if mapping is None else {key: freeze_value(value) for key, value in mapping.items()})


def _freeze_sequence(sequence: Sequence[Any] | None) -> tuple[Any, ...]:
    return tuple(freeze_value(item) for item in (sequence or ()))


@dataclass(frozen=True, slots=True)
class PlanningContext:
    world_id: WorldId
    tick_id: TickId | None
    state_revision: RevisionId | None
    correlation_id: str
    world_state: Mapping[str, Any] = field(default_factory=dict)
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        object.__setattr__(self, "world_state", _freeze_mapping(self.world_state))
        object.__setattr__(self, "metadata", _freeze_mapping(self.metadata))


@dataclass(frozen=True, slots=True)
class PlanProposal:
    world_id: WorldId
    tick_id: TickId | None
    state_revision: RevisionId | None
    correlation_id: str
    goal_id: str
    steps: tuple[Any, ...] = field(default_factory=tuple)
    priority: int = 0
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        object.__setattr__(self, "steps", _freeze_sequence(self.steps))
        object.__setattr__(self, "metadata", _freeze_mapping(self.metadata))


@dataclass(frozen=True, slots=True)
class TickContext:
    world_id: WorldId
    tick_id: TickId
    state_revision: RevisionId | None
    parent_revision: RevisionId | None
    timestamp: datetime
    correlation_id: str
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        object.__setattr__(self, "metadata", _freeze_mapping(self.metadata))


@dataclass(frozen=True, slots=True)
class TransitionProposal:
    world_id: WorldId
    tick_id: TickId | None
    state_revision: RevisionId | None
    correlation_id: str
    subject: str
    patch: Mapping[str, Any] = field(default_factory=dict)
    remove_paths: tuple[tuple[str, ...], ...] = field(default_factory=tuple)
    description: str = ""
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        object.__setattr__(self, "patch", _freeze_mapping(self.patch))
        object.__setattr__(self, "remove_paths", tuple(tuple(path) for path in self.remove_paths))
        object.__setattr__(self, "metadata", _freeze_mapping(self.metadata))


@dataclass(frozen=True, slots=True)
class RenderSnapshot:
    world_id: WorldId
    snapshot_id: SnapshotId
    tick_id: TickId | None
    state_revision: RevisionId | None
    parent_revision: RevisionId | None
    timestamp: datetime
    state: Mapping[str, Any] = field(default_factory=dict)
    events: tuple[Any, ...] = field(default_factory=tuple)
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        object.__setattr__(self, "state", _freeze_mapping(self.state))
        object.__setattr__(self, "events", _freeze_sequence(self.events))
        object.__setattr__(self, "metadata", _freeze_mapping(self.metadata))


@dataclass(frozen=True, slots=True)
class RenderProposal:
    world_id: WorldId
    snapshot_id: SnapshotId
    tick_id: TickId | None
    state_revision: RevisionId | None
    correlation_id: str
    renderer_type: str
    output: Any
    evidence: Mapping[str, Any] = field(default_factory=dict)
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        object.__setattr__(self, "evidence", _freeze_mapping(self.evidence))
        object.__setattr__(self, "metadata", _freeze_mapping(self.metadata))


@dataclass(frozen=True, slots=True)
class VerificationReport:
    world_id: WorldId
    snapshot_id: SnapshotId
    output_id: str
    tick_id: TickId | None
    state_revision: RevisionId | None
    passed: bool
    confidence: float
    discrepancies: tuple[Any, ...] = field(default_factory=tuple)
    evidence: Mapping[str, Any] = field(default_factory=dict)
    metadata: Mapping[str, Any] = field(default_factory=dict)
    extractor_versions: Mapping[str, str] = field(default_factory=dict)
    claim_statuses: tuple[Any, ...] = field(default_factory=tuple)
    uncertainty: float = 0.0
    severity: str = "unknown"
    coverage: float = 0.0
    false_positive_risk: float = 0.0
    false_negative_risk: float = 0.0
    correction_requests: tuple[Any, ...] = field(default_factory=tuple)

    def __post_init__(self) -> None:
        object.__setattr__(self, "discrepancies", _freeze_sequence(self.discrepancies))
        object.__setattr__(self, "evidence", _freeze_mapping(self.evidence))
        object.__setattr__(self, "metadata", _freeze_mapping(self.metadata))
        object.__setattr__(self, "extractor_versions", _freeze_mapping(self.extractor_versions))
        object.__setattr__(self, "claim_statuses", _freeze_sequence(self.claim_statuses))
        object.__setattr__(self, "uncertainty", float(self.uncertainty))
        object.__setattr__(self, "severity", str(self.severity))
        object.__setattr__(self, "coverage", float(self.coverage))
        object.__setattr__(self, "false_positive_risk", float(self.false_positive_risk))
        object.__setattr__(self, "false_negative_risk", float(self.false_negative_risk))
        object.__setattr__(self, "correction_requests", _freeze_sequence(self.correction_requests))


@dataclass(frozen=True, slots=True)
class GovernanceDecision:
    world_id: WorldId
    tick_id: TickId | None
    state_revision: RevisionId | None
    correlation_id: str
    disposition: str
    policy_version: str
    rationale: str
    limits: Mapping[str, Any] = field(default_factory=dict)
    metadata: Mapping[str, Any] = field(default_factory=dict)
    policy_name: str = ""
    input_ids: Mapping[str, Any] = field(default_factory=dict)
    alternatives: tuple[str, ...] = field(default_factory=tuple)
    expiry: datetime | None = None
    confidence: float = 1.0

    def __post_init__(self) -> None:
        object.__setattr__(self, "policy_name", str(self.policy_name))
        object.__setattr__(self, "limits", _freeze_mapping(self.limits))
        object.__setattr__(self, "metadata", _freeze_mapping(self.metadata))
        object.__setattr__(self, "input_ids", _freeze_mapping(self.input_ids))
        object.__setattr__(self, "alternatives", _freeze_sequence(self.alternatives))
        object.__setattr__(self, "confidence", float(self.confidence))


@dataclass(frozen=True, slots=True)
class QObservation:
    world_id: WorldId
    tick_id: TickId | None
    state_revision: RevisionId | None
    correlation_id: str
    q_value: float
    regime: str
    uncertainty: float
    observed_pair: Mapping[str, Any] = field(default_factory=dict)
    thresholds: Mapping[str, Any] = field(default_factory=dict)
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        object.__setattr__(self, "observed_pair", _freeze_mapping(self.observed_pair))
        object.__setattr__(self, "thresholds", _freeze_mapping(self.thresholds))
        object.__setattr__(self, "metadata", _freeze_mapping(self.metadata))
