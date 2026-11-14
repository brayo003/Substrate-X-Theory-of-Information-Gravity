from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Mapping, Sequence

from ..core.contracts import TickContext, TransitionProposal, freeze_value
from ..core.ids import EntityId, RevisionId, TickId, WorldId


@dataclass(frozen=True, slots=True)
class ActionRequest:
    actor_id: EntityId
    action: str
    target_id: EntityId | None = None
    item_id: EntityId | None = None
    destination_room: str | None = None
    quantity: float | None = None
    parameters: Mapping[str, Any] = field(default_factory=dict)
    priority: int = 0
    correlation_id: str = ""
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        object.__setattr__(self, "action", str(self.action))
        object.__setattr__(self, "parameters", freeze_value(dict(self.parameters)))
        object.__setattr__(self, "priority", int(self.priority))
        object.__setattr__(self, "correlation_id", str(self.correlation_id))
        object.__setattr__(self, "metadata", freeze_value(dict(self.metadata)))


@dataclass(frozen=True, slots=True)
class ScheduledAction:
    action_id: str
    request: ActionRequest
    scheduled_tick: int
    execute_tick: int
    status: str = "future"
    interval_ticks: int | None = None
    remaining_runs: int | None = None
    created_tick: int | None = None
    cancelled_reason: str = ""
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        object.__setattr__(self, "action_id", str(self.action_id))
        object.__setattr__(self, "status", str(self.status))
        if self.interval_ticks is not None:
            object.__setattr__(self, "interval_ticks", int(self.interval_ticks))
        if self.remaining_runs is not None:
            object.__setattr__(self, "remaining_runs", int(self.remaining_runs))
        if self.created_tick is not None:
            object.__setattr__(self, "created_tick", int(self.created_tick))
        object.__setattr__(self, "cancelled_reason", str(self.cancelled_reason))
        object.__setattr__(self, "metadata", freeze_value(dict(self.metadata)))


@dataclass(frozen=True, slots=True)
class PhaseDiagnostics:
    phase: str
    proposal_count: int
    rejected_count: int = 0
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        object.__setattr__(self, "phase", str(self.phase))
        object.__setattr__(self, "proposal_count", int(self.proposal_count))
        object.__setattr__(self, "rejected_count", int(self.rejected_count))
        object.__setattr__(self, "metadata", freeze_value(dict(self.metadata)))


@dataclass(frozen=True, slots=True)
class SimulationDiagnostics:
    world_id: WorldId
    tick_id: TickId
    tick_number: int
    committed_revision: RevisionId | None
    phase_reports: tuple[PhaseDiagnostics, ...] = field(default_factory=tuple)
    executed_actions: tuple[str, ...] = field(default_factory=tuple)
    rejected_actions: tuple[Mapping[str, Any], ...] = field(default_factory=tuple)
    conflicts: tuple[Mapping[str, Any], ...] = field(default_factory=tuple)
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        object.__setattr__(self, "phase_reports", tuple(self.phase_reports))
        object.__setattr__(self, "executed_actions", tuple(str(action_id) for action_id in self.executed_actions))
        object.__setattr__(self, "rejected_actions", tuple(freeze_value(dict(item)) for item in self.rejected_actions))
        object.__setattr__(self, "conflicts", tuple(freeze_value(dict(item)) for item in self.conflicts))
        object.__setattr__(self, "metadata", freeze_value(dict(self.metadata)))


@dataclass(frozen=True, slots=True)
class SimulationContext:
    world_id: WorldId
    tick_context: TickContext
    tick_number: int
    world_state: Mapping[str, Any]
    committed_revision: RevisionId | None
    transition_proposals: tuple[TransitionProposal, ...] = field(default_factory=tuple)
    scheduled_actions: tuple[ActionRequest | ScheduledAction | TransitionProposal, ...] = field(default_factory=tuple)
    metadata: Mapping[str, Any] = field(default_factory=dict)
    # Physical field state for per-world isolation
    physical_field_state: Any = None  # Will hold InformationDensityField, PropagationParameters, RelaxationParameters

    def __post_init__(self) -> None:
        object.__setattr__(self, "world_state", freeze_value(self.world_state))
        object.__setattr__(self, "transition_proposals", tuple(self.transition_proposals))
        object.__setattr__(self, "scheduled_actions", tuple(self.scheduled_actions))
        object.__setattr__(self, "metadata", freeze_value(dict(self.metadata)))

