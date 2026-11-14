from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Iterable, Mapping


from ..core.contracts import freeze_value
from ..core.ids import EntityId, RevisionId, TickId, WorldId

def deterministic_hash(seed: str) -> int:
    s = str(seed or "")
    val = hash(s) % (2**32)
    return abs(val)



@dataclass(frozen=True, slots=True)
class RelationshipRecord:
    relationship_id: str
    relationship_type: str
    source_id: EntityId
    target_id: EntityId
    created_tick: int
    created_revision: RevisionId | None
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        object.__setattr__(self, "relationship_type", str(self.relationship_type))
        object.__setattr__(self, "metadata", freeze_value(dict(self.metadata)))


def _relationship_id(world_id: WorldId, source_id: EntityId, target_id: EntityId, relationship_type: str, created_tick: int) -> str:
    seed = f"{world_id.value}|{source_id.value}|{target_id.value}|{relationship_type}|{created_tick}"
    return f"id_{deterministic_hash(seed)}"


@dataclass
class RelationshipGraph:
    world_id: WorldId | None = None
    records: dict[str, RelationshipRecord] = field(default_factory=dict)

    def add(
        self,
        source_id: EntityId,
        target_id: EntityId,
        relationship_type: str,
        *,
        created_tick: int,
        created_revision: RevisionId | None = None,
        metadata: Mapping[str, Any] | None = None,
    ) -> RelationshipRecord:
        if self.world_id is None:
            raise ValueError("relationship graph requires a world_id")
        relationship_id = _relationship_id(self.world_id, source_id, target_id, relationship_type, created_tick)
        record = RelationshipRecord(
            relationship_id=relationship_id,
            relationship_type=relationship_type,
            source_id=source_id,
            target_id=target_id,
            created_tick=created_tick,
            created_revision=created_revision,
            metadata={} if metadata is None else dict(metadata),
        )
        self.records[relationship_id] = record
        return record

    def add_record(self, record: RelationshipRecord) -> RelationshipRecord:
        self.records[record.relationship_id] = record
        return record

    def remove(self, relationship_id: str) -> RelationshipRecord | None:
        return self.records.pop(relationship_id, None)

    def incoming(self, entity_id: EntityId, relationship_type: str | None = None) -> tuple[RelationshipRecord, ...]:
        return tuple(
            record
            for record in self.records.values()
            if record.target_id == entity_id and (relationship_type is None or record.relationship_type == relationship_type)
        )

    def outgoing(self, entity_id: EntityId, relationship_type: str | None = None) -> tuple[RelationshipRecord, ...]:
        return tuple(
            record
            for record in self.records.values()
            if record.source_id == entity_id and (relationship_type is None or record.relationship_type == relationship_type)
        )

    def typed_lookup(self, relationship_type: str, *, entity_id: EntityId | None = None) -> tuple[RelationshipRecord, ...]:
        return tuple(
            record
            for record in self.records.values()
            if record.relationship_type == relationship_type
            and (entity_id is None or record.source_id == entity_id or record.target_id == entity_id)
        )

    def for_entity(self, entity_id: EntityId) -> tuple[RelationshipRecord, ...]:
        return tuple(
            record for record in self.records.values() if record.source_id == entity_id or record.target_id == entity_id
        )

    def serialize(self) -> tuple[Mapping[str, Any], ...]:
        return tuple(
            freeze_value(
                {
                    "relationship_id": record.relationship_id,
                    "relationship_type": record.relationship_type,
                    "source_id": str(record.source_id.value),
                    "target_id": str(record.target_id.value),
                    "created_tick": record.created_tick,
                    "created_revision": None if record.created_revision is None else str(record.created_revision.value),
                    "metadata": record.metadata,
                }
            )
            for record in sorted(self.records.values(), key=lambda record: record.relationship_id)
        )
