from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Mapping, Sequence


from ..core.contracts import RenderSnapshot, freeze_value
from ..core.ids import EntityId, EventId, RevisionId, TickId, WorldId
from ..simulation.simulation_context import ActionRequest

def deterministic_hash(seed: str) -> int:
    s = str(seed or "")
    val = hash(s) % (2**32)
    return abs(val)



def _deterministic_text(*parts: Any) -> str:
    return str(deterministic_hash("|".join(str(part) for part in parts)))


@dataclass(frozen=True, slots=True)
class Goal:
    goal_id: str
    subject: str
    kind: str
    entity_id: EntityId | None
    target_state: Mapping[str, Any] = field(default_factory=dict)
    priority: int = 0
    utility: float = 0.0
    rationale: str = ""
    deadline_tick: int | None = None
    window_start_tick: int | None = None
    window_end_tick: int | None = None
    horizon_ticks: int = 1
    provenance: Mapping[str, Any] = field(default_factory=dict)
    confidence: float = 1.0
    constraints: tuple[str, ...] = field(default_factory=tuple)
    interruption_policy: str = "suspend"
    status: str = "pending"
    created_tick: int = 0
    created_revision: RevisionId | None = None
    metadata: Mapping[str, Any] = field(default_factory=dict)
    # LLM-specific fields for high-level objectives
    objective: str | None = None  # High-level objective name (e.g., "establish_food_supply")
    desired_outcome: str | None = None  # Human-readable outcome description
    preferences: Mapping[str, Any] = field(default_factory=dict)  # Structured preferences (e.g., source_preference, distance_limit)
    resource_limits: Mapping[str, float] = field(default_factory=dict)  # Resource constraints (e.g., wood, energy)

    def __post_init__(self) -> None:
        object.__setattr__(self, "goal_id", str(self.goal_id))
        object.__setattr__(self, "subject", str(self.subject))
        object.__setattr__(self, "kind", str(self.kind))
        object.__setattr__(self, "priority", int(self.priority))
        object.__setattr__(self, "utility", float(self.utility))
        object.__setattr__(self, "rationale", str(self.rationale))
        object.__setattr__(self, "horizon_ticks", int(self.horizon_ticks))
        object.__setattr__(self, "confidence", float(self.confidence))
        object.__setattr__(self, "constraints", tuple(str(item) for item in self.constraints))
        object.__setattr__(self, "interruption_policy", str(self.interruption_policy))
        object.__setattr__(self, "status", str(self.status))
        object.__setattr__(self, "created_tick", int(self.created_tick))
        object.__setattr__(self, "target_state", freeze_value(dict(self.target_state)))
        object.__setattr__(self, "provenance", freeze_value(dict(self.provenance)))
        object.__setattr__(self, "metadata", freeze_value(dict(self.metadata)))
        object.__setattr__(self, "objective", None if self.objective is None else str(self.objective))
        object.__setattr__(self, "desired_outcome", None if self.desired_outcome is None else str(self.desired_outcome))
        object.__setattr__(self, "preferences", freeze_value(dict(self.preferences)))
        object.__setattr__(self, "resource_limits", freeze_value({k: float(v) for k, v in dict(self.resource_limits).items()}))

    @classmethod
    def create(
        cls,
        *,
        world_id: WorldId,
        subject: str,
        kind: str,
        entity_id: EntityId | None = None,
        target_state: Mapping[str, Any] | None = None,
        priority: int = 0,
        utility: float = 0.0,
        rationale: str = "",
        deadline_tick: int | None = None,
        window_start_tick: int | None = None,
        window_end_tick: int | None = None,
        horizon_ticks: int = 1,
        provenance: Mapping[str, Any] | None = None,
        confidence: float = 1.0,
        constraints: Sequence[str] | None = None,
        interruption_policy: str = "suspend",
        status: str = "pending",
        created_tick: int = 0,
        created_revision: RevisionId | None = None,
        metadata: Mapping[str, Any] | None = None,
        objective: str | None = None,
        desired_outcome: str | None = None,
        preferences: Mapping[str, Any] | None = None,
        resource_limits: Mapping[str, float] | None = None,
    ) -> "Goal":
        goal_id = _deterministic_text(
            world_id.value,
            subject,
            kind,
            None if entity_id is None else entity_id.value,
            created_tick,
            priority,
            deadline_tick,
        )
        return cls(
            goal_id=goal_id,
            subject=subject,
            kind=kind,
            entity_id=entity_id,
            target_state={} if target_state is None else dict(target_state),
            priority=priority,
            utility=utility,
            rationale=rationale,
            deadline_tick=deadline_tick,
            window_start_tick=window_start_tick,
            window_end_tick=window_end_tick,
            horizon_ticks=horizon_ticks,
            provenance={} if provenance is None else dict(provenance),
            confidence=confidence,
            constraints=tuple(constraints or ()),
            interruption_policy=interruption_policy,
            status=status,
            created_tick=created_tick,
            created_revision=created_revision,
            metadata={} if metadata is None else dict(metadata),
            objective=objective,
            desired_outcome=desired_outcome,
            preferences={} if preferences is None else dict(preferences),
            resource_limits={} if resource_limits is None else dict(resource_limits),
        )


@dataclass(frozen=True, slots=True)
class PlanProposal:
    plan_id: str
    goal_id: str
    entity_id: EntityId | None
    priority: int
    estimated_cost: float
    estimated_duration: int
    action_requests: tuple[ActionRequest, ...] = field(default_factory=tuple)
    dependencies: tuple[str, ...] = field(default_factory=tuple)
    required_resources: Mapping[str, float] = field(default_factory=dict)
    confidence: float = 1.0
    creation_tick: int = 0
    planning_revision: RevisionId | None = None
    status: str = "proposed"
    goal_subject: str = ""
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        object.__setattr__(self, "plan_id", str(self.plan_id))
        object.__setattr__(self, "goal_id", str(self.goal_id))
        object.__setattr__(self, "priority", int(self.priority))
        object.__setattr__(self, "estimated_cost", float(self.estimated_cost))
        object.__setattr__(self, "estimated_duration", int(self.estimated_duration))
        object.__setattr__(self, "action_requests", tuple(self.action_requests))
        object.__setattr__(self, "dependencies", tuple(str(item) for item in self.dependencies))
        object.__setattr__(self, "required_resources", freeze_value({key: float(value) for key, value in dict(self.required_resources).items()}))
        object.__setattr__(self, "confidence", float(self.confidence))
        object.__setattr__(self, "creation_tick", int(self.creation_tick))
        object.__setattr__(self, "status", str(self.status))
        object.__setattr__(self, "goal_subject", str(self.goal_subject))
        object.__setattr__(self, "metadata", freeze_value(dict(self.metadata)))


@dataclass(frozen=True, slots=True)
class PlanningEvent:
    event_id: EventId
    world_id: WorldId
    event_type: str
    timestamp: datetime
    tick_id: TickId | None
    revision_id: RevisionId | None
    goal_id: str | None = None
    plan_id: str | None = None
    payload: Mapping[str, Any] = field(default_factory=dict)
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        object.__setattr__(self, "event_type", str(self.event_type))
        object.__setattr__(self, "goal_id", None if self.goal_id is None else str(self.goal_id))
        object.__setattr__(self, "plan_id", None if self.plan_id is None else str(self.plan_id))
        object.__setattr__(self, "payload", freeze_value(dict(self.payload)))
        object.__setattr__(self, "metadata", freeze_value(dict(self.metadata)))


@dataclass(frozen=True, slots=True)
class PlanningPhaseReport:
    phase: str
    candidate_count: int
    accepted_count: int = 0
    rejected_count: int = 0
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        object.__setattr__(self, "phase", str(self.phase))
        object.__setattr__(self, "candidate_count", int(self.candidate_count))
        object.__setattr__(self, "accepted_count", int(self.accepted_count))
        object.__setattr__(self, "rejected_count", int(self.rejected_count))
        object.__setattr__(self, "metadata", freeze_value(dict(self.metadata)))


@dataclass(frozen=True, slots=True)
class PlanningDiagnostics:
    world_id: WorldId
    tick_id: TickId
    tick_number: int
    committed_revision: RevisionId | None
    goals_evaluated: int
    plans_generated: int
    plans_validated: int
    plans_rejected: int
    phase_reports: tuple[PlanningPhaseReport, ...] = field(default_factory=tuple)
    future_action_requests: tuple[ActionRequest, ...] = field(default_factory=tuple)
    events: tuple[PlanningEvent, ...] = field(default_factory=tuple)
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        object.__setattr__(self, "phase_reports", tuple(self.phase_reports))
        object.__setattr__(self, "future_action_requests", tuple(self.future_action_requests))
        object.__setattr__(self, "events", tuple(self.events))
        object.__setattr__(self, "metadata", freeze_value(dict(self.metadata)))


@dataclass(frozen=True, slots=True)
class PlannerContext:
    world_id: WorldId
    snapshot: RenderSnapshot
    current_tick: TickId
    current_tick_number: int
    committed_revision: RevisionId | None
    entity_registry: Any
    world_memory: Any
    outstanding_goals: tuple[Goal, ...] = field(default_factory=tuple)
    scheduled_plans: tuple[Any, ...] = field(default_factory=tuple)
    spectral_observable: Any = None
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        object.__setattr__(self, "outstanding_goals", tuple(self.outstanding_goals))
        object.__setattr__(self, "scheduled_plans", tuple(self.scheduled_plans))
        object.__setattr__(self, "metadata", freeze_value(dict(self.metadata)))

