from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Mapping, Sequence


from ..core.contracts import freeze_value
from ..core.ids import EntityId, RevisionId, TickId, WorldId
from .memory import BaseMemoryStore

def deterministic_hash(seed: str) -> int:
    s = str(seed or "")
    val = hash(s) % (2**32)
    return abs(val)



@dataclass(frozen=True, slots=True)
class RelationshipTimelineRecord:
    record_id: str
    world_id: WorldId
    source_id: EntityId
    target_id: EntityId
    relationship_type: str
    state: str
    version: int
    timestamp: datetime
    tick_id: TickId | None = None
    revision_id: RevisionId | None = None
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        object.__setattr__(self, "relationship_type", str(self.relationship_type))
        object.__setattr__(self, "state", str(self.state))
        object.__setattr__(self, "metadata", freeze_value(dict(self.metadata)))


def _relationship_record_id(
    world_id: WorldId,
    source_id: EntityId,
    target_id: EntityId,
    relationship_type: str,
    state: str,
    version: int,
) -> str:
    seed = f"{world_id.value}|{source_id.value}|{target_id.value}|{relationship_type}|{state}|{version}"
    return f"id_{deterministic_hash(seed)}"


@dataclass
class RelationshipMemory(BaseMemoryStore):
    records: list[RelationshipTimelineRecord] = field(default_factory=list)
    by_pair: dict[tuple[EntityId, EntityId], list[RelationshipTimelineRecord]] = field(default_factory=dict)
    by_relationship_type: dict[str, list[RelationshipTimelineRecord]] = field(default_factory=dict)
    by_relationship_id: dict[str, list[RelationshipTimelineRecord]] = field(default_factory=dict)

    def append(
        self,
        source_id: EntityId,
        target_id: EntityId,
        relationship_type: str,
        state: str,
        *,
        tick_id: TickId | None = None,
        revision_id: RevisionId | None = None,
        metadata: Mapping[str, Any] | None = None,
    ) -> RelationshipTimelineRecord:
        pair = (source_id, target_id)
        version = len(self.by_pair.get(pair, ())) + 1
        record = RelationshipTimelineRecord(
            record_id=_relationship_record_id(self.world_id, source_id, target_id, relationship_type, state, version),
            world_id=self.world_id,
            source_id=source_id,
            target_id=target_id,
            relationship_type=relationship_type,
            state=state,
            version=version,
            timestamp=datetime.now(timezone.utc),
            tick_id=tick_id,
            revision_id=revision_id,
            metadata={} if metadata is None else dict(metadata),
        )
        self.records.append(record)
        self.by_pair.setdefault(pair, []).append(record)
        self.by_relationship_type.setdefault(relationship_type, []).append(record)
        self.by_relationship_id.setdefault(record.record_id, []).append(record)
        self._emit(
            memory_kind="relationship",
            action="append",
            reference_id=record.record_id,
            revision_id=revision_id,
            tick_id=tick_id,
            entity_id=source_id,
            relationship_id=record.record_id,
            payload={
                "source_id": str(source_id.value),
                "target_id": str(target_id.value),
                "relationship_type": relationship_type,
                "state": state,
                "version": version,
            },
            metadata=record.metadata,
        )
        return record

    def between_ticks(self, start_tick: TickId, end_tick: TickId) -> tuple[RelationshipTimelineRecord, ...]:
        start_index = next((index for index, record in enumerate(self.records) if record.tick_id == start_tick), 0)
        end_index = next(
            (index for index in range(len(self.records) - 1, -1, -1) if self.records[index].tick_id == end_tick),
            len(self.records) - 1,
        )
        if end_index < start_index:
            start_index, end_index = end_index, start_index
        return tuple(self.records[start_index : end_index + 1])

    def between_revisions(self, start_revision: RevisionId, end_revision: RevisionId) -> tuple[RelationshipTimelineRecord, ...]:
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
        source_id: EntityId | None = None,
        target_id: EntityId | None = None,
        relationship_type: str | None = None,
    ) -> RelationshipTimelineRecord | None:
        records = self.records
        if source_id is not None or target_id is not None:
            records = [
                record
                for record in records
                if (source_id is None or record.source_id == source_id)
                and (target_id is None or record.target_id == target_id)
            ]
        if relationship_type is not None:
            records = [record for record in records if record.relationship_type == relationship_type]
        return records[-1] if records else None

    def replay(self, *, source_id: EntityId | None = None, target_id: EntityId | None = None) -> tuple[RelationshipTimelineRecord, ...]:
        if source_id is not None and target_id is not None:
            return tuple(self.by_pair.get((source_id, target_id), ()))
        if source_id is not None:
            return tuple(record for record in self.records if record.source_id == source_id)
        if target_id is not None:
            return tuple(record for record in self.records if record.target_id == target_id)
        return tuple(self.records)
