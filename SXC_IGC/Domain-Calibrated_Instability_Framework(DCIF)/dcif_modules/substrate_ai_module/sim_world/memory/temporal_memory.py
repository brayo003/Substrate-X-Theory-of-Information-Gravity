from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Callable, Mapping, Sequence


from ..core.contracts import freeze_value
from ..core.ids import AssetId, EntityId, EventId, RevisionId, TickId, WorldId
from .memory import BaseMemoryStore

def deterministic_hash(seed: str) -> int:
    s = str(seed or "")
    val = hash(s) % (2**32)
    return abs(val)



@dataclass(frozen=True, slots=True)
class TemporalRecord:
    record_id: str
    world_id: WorldId
    payload: Any
    timestamp: datetime
    tick_id: TickId | None = None
    revision_id: RevisionId | None = None
    entity_id: EntityId | None = None
    relationship_id: str | None = None
    asset_id: AssetId | None = None
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        object.__setattr__(self, "record_id", str(self.record_id))
        object.__setattr__(self, "metadata", freeze_value(dict(self.metadata)))


def _temporal_record_id(world_id: WorldId, payload: Any, index: int) -> str:
    return str(deterministic_hash(f"{world_id.value}|{repr(payload)}|{index}"))


@dataclass
class TemporalMemory(BaseMemoryStore):
    records: list[TemporalRecord] = field(default_factory=list)
    by_tick: dict[TickId, list[TemporalRecord]] = field(default_factory=dict)
    by_revision: dict[RevisionId, list[TemporalRecord]] = field(default_factory=dict)
    by_entity: dict[EntityId, list[TemporalRecord]] = field(default_factory=dict)
    by_relationship: dict[str, list[TemporalRecord]] = field(default_factory=dict)
    by_asset: dict[AssetId, list[TemporalRecord]] = field(default_factory=dict)

    def append(
        self,
        payload: Any,
        *,
        tick_id: TickId | None = None,
        revision_id: RevisionId | None = None,
        entity_id: EntityId | None = None,
        relationship_id: str | None = None,
        asset_id: AssetId | None = None,
        metadata: Mapping[str, Any] | None = None,
    ) -> TemporalRecord:
        record = TemporalRecord(
            record_id=_temporal_record_id(self.world_id, payload, len(self.records) + 1),
            world_id=self.world_id,
            payload=payload,
            timestamp=datetime.now(timezone.utc),
            tick_id=tick_id,
            revision_id=revision_id,
            entity_id=entity_id,
            relationship_id=relationship_id,
            asset_id=asset_id,
            metadata={} if metadata is None else dict(metadata),
        )
        self.records.append(record)
        if tick_id is not None:
            self.by_tick.setdefault(tick_id, []).append(record)
        if revision_id is not None:
            self.by_revision.setdefault(revision_id, []).append(record)
        if entity_id is not None:
            self.by_entity.setdefault(entity_id, []).append(record)
        if relationship_id is not None:
            self.by_relationship.setdefault(relationship_id, []).append(record)
        if asset_id is not None:
            self.by_asset.setdefault(asset_id, []).append(record)
        self._emit(
            memory_kind="temporal",
            action="append",
            reference_id=record.record_id,
            revision_id=revision_id,
            tick_id=tick_id,
            entity_id=entity_id,
            relationship_id=relationship_id,
            asset_id=asset_id,
            payload={"payload": record.payload},
            metadata=record.metadata,
        )
        return record

    def between_ticks(self, start_tick: TickId, end_tick: TickId) -> tuple[TemporalRecord, ...]:
        start_index = next((index for index, record in enumerate(self.records) if record.tick_id == start_tick), 0)
        end_index = next(
            (index for index in range(len(self.records) - 1, -1, -1) if self.records[index].tick_id == end_tick),
            len(self.records) - 1,
        )
        if end_index < start_index:
            start_index, end_index = end_index, start_index
        return tuple(self.records[start_index : end_index + 1])

    def between_revisions(self, start_revision: RevisionId, end_revision: RevisionId) -> tuple[TemporalRecord, ...]:
        start_index = next((index for index, record in enumerate(self.records) if record.revision_id == start_revision), 0)
        end_index = next(
            (index for index in range(len(self.records) - 1, -1, -1) if self.records[index].revision_id == end_revision),
            len(self.records) - 1,
        )
        if end_index < start_index:
            start_index, end_index = end_index, start_index
        return tuple(self.records[start_index : end_index + 1])

    def latest(
        self,
        *,
        entity_id: EntityId | None = None,
        relationship_id: str | None = None,
        asset_id: AssetId | None = None,
    ) -> TemporalRecord | None:
        if entity_id is not None:
            records = self.by_entity.get(entity_id, ())
        elif relationship_id is not None:
            records = self.by_relationship.get(relationship_id, ())
        elif asset_id is not None:
            records = self.by_asset.get(asset_id, ())
        else:
            records = self.records
        return records[-1] if records else None

    def replay(
        self,
        *,
        entity_id: EntityId | None = None,
        relationship_id: str | None = None,
        asset_id: AssetId | None = None,
    ) -> tuple[TemporalRecord, ...]:
        if entity_id is not None:
            return tuple(self.by_entity.get(entity_id, ()))
        if relationship_id is not None:
            return tuple(self.by_relationship.get(relationship_id, ()))
        if asset_id is not None:
            return tuple(self.by_asset.get(asset_id, ()))
        return tuple(self.records)
