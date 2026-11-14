from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Mapping

from .contracts import freeze_value
from .events import StateEvent
from .ids import RevisionId, SnapshotId, TickId, WorldId


def _state_hash(state: Mapping[str, Any]) -> str:
    return repr(freeze_value(dict(state)))


@dataclass(frozen=True, slots=True)
class Revision:
    world_id: WorldId
    revision_id: RevisionId
    tick_id: TickId | None
    timestamp: datetime
    parent_revision: RevisionId | None
    events: tuple[StateEvent, ...] = field(default_factory=tuple)
    state: Mapping[str, Any] = field(default_factory=dict)
    metadata: Mapping[str, Any] = field(default_factory=dict)
    state_hash: str = ""

    def __post_init__(self) -> None:
        object.__setattr__(self, "events", tuple(self.events))
        object.__setattr__(self, "state", freeze_value(dict(self.state)))
        object.__setattr__(self, "metadata", freeze_value(dict(self.metadata)))
        if not self.state_hash:
            object.__setattr__(self, "state_hash", _state_hash(self.state))

    @property
    def snapshot_id(self) -> SnapshotId:
        tick_id = self.tick_id or TickId.new(self.world_id, 0)
        return SnapshotId.new(self.revision_id, tick_id)

    def replay(self, base_state: Mapping[str, Any] | None = None) -> dict[str, Any]:
        state = dict(base_state or {})
        for event in self.events:
            state = event.apply_to(state)
        return state
