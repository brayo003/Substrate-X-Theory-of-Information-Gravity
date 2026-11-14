from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Mapping, Sequence


from .agent_memory import AgentMemory
from .asset_memory import AssetIdentityRecord, AssetMemory
from ..core.contracts import freeze_value
from ..core.ids import AssetId, EntityId, RevisionId, TickId, WorldId
from .knowledge_memory import KnowledgeMemory, KnowledgeRecord
from .memory import BaseMemoryStore, MemoryEvent, RollbackReference
from .relationship_memory import RelationshipMemory, RelationshipTimelineRecord
from ..core.revision import Revision
from ..core.storage import InMemoryStorage
from .temporal_memory import TemporalMemory, TemporalRecord

def deterministic_hash(seed: str) -> int:
    s = str(seed or "")
    val = hash(s) % (2**32)
    return abs(val)



def _diff_values(left: Any, right: Any) -> Any:
    if isinstance(left, Mapping) and isinstance(right, Mapping):
        return _diff_mappings(left, right)
    if left != right:
        return {"from": left, "to": right}
    return {}


def _diff_mappings(left: Mapping[str, Any], right: Mapping[str, Any]) -> dict[str, Any]:
    added = {key: right[key] for key in right.keys() - left.keys()}
    removed = {key: left[key] for key in left.keys() - right.keys()}
    changed: dict[str, Any] = {}
    for key in left.keys() & right.keys():
        diff = _diff_values(left[key], right[key])
        if diff:
            changed[key] = diff
    return {"added": added, "removed": removed, "changed": changed}


@dataclass
class WorldMemory(BaseMemoryStore):
    storage: InMemoryStorage = field(default_factory=InMemoryStorage)
    initial_state: Mapping[str, Any] = field(default_factory=dict)
    agent_memories: dict[EntityId, AgentMemory] = field(default_factory=dict)
    asset_memory: AssetMemory = field(init=False)
    temporal_memory: TemporalMemory = field(init=False)
    relationship_memory: RelationshipMemory = field(init=False)
    knowledge_memory: KnowledgeMemory = field(init=False)
    _revision_entity_index: dict[EntityId, list[RevisionId]] = field(default_factory=dict, init=False, repr=False)
    _revision_tick_index: dict[TickId, list[RevisionId]] = field(default_factory=dict, init=False, repr=False)
    _revision_time_index: list[tuple[datetime, RevisionId]] = field(default_factory=list, init=False, repr=False)
    _rollback_refs: list[RollbackReference] = field(default_factory=list, init=False, repr=False)

    def __post_init__(self) -> None:
        self.initial_state = freeze_value(dict(self.initial_state))
        self.asset_memory = AssetMemory(self.world_id, event_sink=self._record_event)
        self.temporal_memory = TemporalMemory(self.world_id, event_sink=self._record_event)
        self.relationship_memory = RelationshipMemory(self.world_id, event_sink=self._record_event)
        self.knowledge_memory = KnowledgeMemory(self.world_id, event_sink=self._record_event)

    def record_revision(
        self,
        revision: Revision,
        *,
        entity_refs: Mapping[EntityId, str] | None = None,
    ) -> Revision:
        self.storage.save_revision(revision)
        if revision.tick_id is not None:
            self._revision_tick_index.setdefault(revision.tick_id, []).append(revision.revision_id)
        self._revision_time_index.append((revision.timestamp, revision.revision_id))
        for event in revision.events:
            if event.entity_id is not None:
                self._revision_entity_index.setdefault(event.entity_id, []).append(revision.revision_id)
        self.temporal_memory.append(
            {
                "revision_id": str(revision.revision_id.value),
                "state_hash": revision.state_hash,
                "entity_refs": {} if entity_refs is None else {str(entity_id.value): memory_ref for entity_id, memory_ref in entity_refs.items()},
            },
            tick_id=revision.tick_id,
            revision_id=revision.revision_id,
            metadata={"kind": "world_revision"},
        )
        self._emit(
            memory_kind="world",
            action="record_revision",
            reference_id=str(revision.revision_id.value),
            revision_id=revision.revision_id,
            tick_id=revision.tick_id,
            payload={"state_hash": revision.state_hash, "event_count": len(revision.events)},
            metadata={"parent_revision": None if revision.parent_revision is None else str(revision.parent_revision.value)},
        )
        return revision

    def current_state(self) -> Mapping[str, Any]:
        latest = self.storage.latest_revision()
        if latest is None:
            return freeze_value(dict(self.initial_state))
        return freeze_value(dict(latest.state))

    def revision(self, revision_id: RevisionId | None = None) -> Revision | None:
        if revision_id is None:
            return self.storage.latest_revision()
        try:
            return self.storage.load_revision(revision_id)
        except Exception:
            return None

    def history(self, entity_id: EntityId | None = None) -> tuple[Revision, ...]:
        revisions = self.storage.list_history()
        if entity_id is None:
            return revisions
        return tuple(revision for revision in revisions if any(event.entity_id == entity_id for event in revision.events))

    def lookup(
        self,
        *,
        entity_id: EntityId | None = None,
        revision_id: RevisionId | None = None,
        tick_id: TickId | None = None,
        timestamp: datetime | None = None,
        relationship_id: str | None = None,
        asset_id: AssetId | None = None,
    ) -> tuple[Any, ...]:
        results: list[Any] = []
        if revision_id is not None:
            revision = self.revision(revision_id)
            if revision is not None:
                results.append(revision)
        if entity_id is not None:
            results.extend(self.history(entity_id))
            agent_memory = self.agent_memories.get(entity_id)
            if agent_memory is not None:
                results.append(agent_memory)
        if tick_id is not None:
            results.extend(self.storage.load_revision(revision_key) for revision_key in self._revision_tick_index.get(tick_id, ()))
        if timestamp is not None:
            results.extend(self.storage.load_revision(revision_key) for recorded_time, revision_key in self._revision_time_index if recorded_time == timestamp)
        if relationship_id is not None:
            results.extend(record for record in self.relationship_memory.records if record.record_id == relationship_id)
        if asset_id is not None:
            asset_record = self.asset_memory.lookup(asset_id)
            if asset_record is not None:
                results.append(asset_record)
        return tuple(results)

    def diff(self, left_revision_id: RevisionId, right_revision_id: RevisionId) -> Mapping[str, Any]:
        left = self.revision(left_revision_id)
        right = self.revision(right_revision_id)
        if left is None or right is None:
            return freeze_value({"added": {}, "removed": {}, "changed": {}})
        return freeze_value(_diff_mappings(left.state, right.state))

    def rollback_reference(
        self,
        to_revision_id: RevisionId,
        *,
        from_revision_id: RevisionId | None = None,
        reason: str = "",
        metadata: Mapping[str, Any] | None = None,
    ) -> RollbackReference:
        reference = RollbackReference(
            reference_id=str(deterministic_hash(f"{self.world_id.value}|rollback|{to_revision_id.value}|{len(self._rollback_refs) + 1}")),
            world_id=self.world_id,
            from_revision=from_revision_id,
            to_revision=to_revision_id,
            timestamp=datetime.now(timezone.utc),
            reason=reason,
            metadata={} if metadata is None else dict(metadata),
        )
        self._rollback_refs.append(reference)
        self._emit(
            memory_kind="world",
            action="rollback_reference",
            reference_id=reference.reference_id,
            revision_id=to_revision_id,
            payload={
                "from_revision": None if from_revision_id is None else str(from_revision_id.value),
                "to_revision": str(to_revision_id.value),
            },
            metadata=reference.metadata,
        )
        return reference

    def rollback_references(self) -> tuple[RollbackReference, ...]:
        return tuple(self._rollback_refs)

    def agent_memory_for(
        self,
        entity_id: EntityId,
        *,
        create: bool = True,
        metadata: Mapping[str, Any] | None = None,
    ) -> AgentMemory | None:
        memory = self.agent_memories.get(entity_id)
        if memory is not None or not create:
            return memory
        memory = AgentMemory(self.world_id, owner_entity_id=entity_id, event_sink=self._record_event)
        self.agent_memories[entity_id] = memory
        self._emit(
            memory_kind="agent",
            action="create_reference",
            reference_id=memory.memory_id,
            entity_id=entity_id,
            payload={"owner_entity_id": str(entity_id.value)},
            metadata={} if metadata is None else dict(metadata),
        )
        return memory

    def agent_memory_reference(self, entity_id: EntityId) -> str | None:
        memory = self.agent_memories.get(entity_id)
        return None if memory is None else memory.memory_id

    def agent_memory_references(self) -> Mapping[EntityId, str]:
        return freeze_value({entity_id: memory.memory_id for entity_id, memory in self.agent_memories.items()})

    def record_relationship(
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
        return self.relationship_memory.append(
            source_id,
            target_id,
            relationship_type,
            state,
            tick_id=tick_id,
            revision_id=revision_id,
            metadata=metadata,
        )

    def record_asset(
        self,
        *,
        canonical_name: str,
        descriptors: Mapping[str, Any] | None = None,
        visual_embedding_placeholder: str = "",
        serial_number: str = "",
        manufacturer: str = "",
        creation_metadata: Mapping[str, Any] | None = None,
        provenance: Mapping[str, Any] | None = None,
        entity_id: EntityId | None = None,
        created_tick: int | None = None,
        created_revision: RevisionId | None = None,
        asset_id: AssetId | None = None,
    ) -> AssetIdentityRecord:
        return self.asset_memory.remember(
            canonical_name=canonical_name,
            descriptors=descriptors,
            visual_embedding_placeholder=visual_embedding_placeholder,
            serial_number=serial_number,
            manufacturer=manufacturer,
            creation_metadata=creation_metadata,
            provenance=provenance,
            entity_id=entity_id,
            created_tick=created_tick,
            created_revision=created_revision,
            asset_id=asset_id,
        )

    def record_knowledge(self, *args: Any, **kwargs: Any) -> KnowledgeRecord:
        kind = kwargs.pop("kind", "fact")
        if kind == "rule":
            return self.knowledge_memory.add_rule(*args, **kwargs)
        if kind == "category":
            return self.knowledge_memory.add_category(*args, **kwargs)
        return self.knowledge_memory.add_fact(*args, **kwargs)

    def snapshot_references(self) -> Mapping[str, Any]:
        return freeze_value(
            {
                "agent_memories": {str(entity_id.value): memory.memory_id for entity_id, memory in self.agent_memories.items()},
                "asset_memory": self.asset_memory.references(),
                "temporal_memory": {"count": len(self.temporal_memory.records)},
                "relationship_memory": {
                    "count": len(self.relationship_memory.records),
                    "latest_reference": None
                    if not self.relationship_memory.records
                    else self.relationship_memory.records[-1].record_id,
                },
                "knowledge_memory": {
                    "count": len(self.knowledge_memory.records),
                    "latest_reference": None if not self.knowledge_memory.records else self.knowledge_memory.records[-1].knowledge_id,
                },
                "rollback_references": [reference.reference_id for reference in self._rollback_refs],
            }
        )

    def _record_event(self, event: MemoryEvent) -> None:
        self.events.append(event)
