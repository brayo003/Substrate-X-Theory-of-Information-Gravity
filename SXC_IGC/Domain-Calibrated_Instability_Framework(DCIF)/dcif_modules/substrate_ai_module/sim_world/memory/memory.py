from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Callable, Mapping, MutableSequence

from ..core.contracts import freeze_value
from ..core.ids import AssetId, EntityId, EventId, RevisionId, TickId, WorldId


@dataclass(frozen=True, slots=True)
class MemoryEvent:
    event_id: EventId
    world_id: WorldId
    memory_kind: str
    action: str
    timestamp: datetime
    reference_id: str
    revision_id: RevisionId | None = None
    tick_id: TickId | None = None
    entity_id: EntityId | None = None
    asset_id: AssetId | None = None
    relationship_id: str | None = None
    payload: Mapping[str, Any] = field(default_factory=dict)
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        object.__setattr__(self, "reference_id", str(self.reference_id))
        object.__setattr__(self, "payload", freeze_value(dict(self.payload)))
        object.__setattr__(self, "metadata", freeze_value(dict(self.metadata)))


@dataclass(frozen=True, slots=True)
class RollbackReference:
    reference_id: str
    world_id: WorldId
    from_revision: RevisionId | None
    to_revision: RevisionId
    timestamp: datetime
    reason: str = ""
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        object.__setattr__(self, "reference_id", str(self.reference_id))
        object.__setattr__(self, "reason", str(self.reason))
        object.__setattr__(self, "metadata", freeze_value(dict(self.metadata)))


EventSink = Callable[[MemoryEvent], None]


@dataclass
class BaseMemoryStore:
    world_id: WorldId
    events: list[MemoryEvent] = field(default_factory=list)
    event_sink: EventSink | None = field(default=None, repr=False, compare=False)

    def _emit(
        self,
        *,
        memory_kind: str,
        action: str,
        reference_id: str,
        revision_id: RevisionId | None = None,
        tick_id: TickId | None = None,
        entity_id: EntityId | None = None,
        asset_id: AssetId | None = None,
        relationship_id: str | None = None,
        payload: Mapping[str, Any] | None = None,
        metadata: Mapping[str, Any] | None = None,
    ) -> MemoryEvent:
        event = MemoryEvent(
            event_id=EventId.new(
                RevisionId.new(self.world_id, tick_id, len(self.events) + 1, {"memory_kind": memory_kind, "action": action, "reference_id": reference_id}),
                len(self.events) + 1,
                {"memory_kind": memory_kind, "action": action, "reference_id": reference_id},
            ),
            world_id=self.world_id,
            memory_kind=memory_kind,
            action=action,
            timestamp=datetime.now(timezone.utc),
            reference_id=reference_id,
            revision_id=revision_id,
            tick_id=tick_id,
            entity_id=entity_id,
            asset_id=asset_id,
            relationship_id=relationship_id,
            payload={} if payload is None else dict(payload),
            metadata={} if metadata is None else dict(metadata),
        )
        self.events.append(event)
        if self.event_sink is not None:
            self.event_sink(event)
        return event

    def list_events(self) -> tuple[MemoryEvent, ...]:
        return tuple(self.events)
