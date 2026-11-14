from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable, Iterable, Mapping

from .actions import ActionDefinition, ActionRegistry
from .components import (
    MemoryReferenceComponent,
    RelationshipComponent,
    deserialize_component,
)
from ..core.contracts import freeze_value
from ..memory.agent_memory import AgentMemory
from .entity import Entity, EntityChangeSink
from ..core.events import StateEvent
from ..core.ids import EntityId, RevisionId, TickId, WorldId
from .relationships import RelationshipGraph, RelationshipRecord
from ..memory.world_memory import WorldMemory


@dataclass
class EntityRegistry:
    world_id: WorldId
    entities: dict[EntityId, Entity] = field(default_factory=dict)
    history: list[StateEvent] = field(default_factory=list)
    relationships: RelationshipGraph = field(init=False)
    agent_memories: dict[EntityId, AgentMemory] = field(default_factory=dict)
    _on_change: Callable[[], None] | None = field(default=None, repr=False, compare=False)
    _world_memory: WorldMemory | None = field(default=None, repr=False, compare=False)

    def __post_init__(self) -> None:
        self.relationships = RelationshipGraph(self.world_id)

    def bind_change_listener(self, listener: Callable[[], None] | None) -> None:
        self._on_change = listener

    def bind_world_memory(self, world_memory: WorldMemory | None) -> None:
        self._world_memory = world_memory

    def create_entity(
        self,
        *,
        entity_type: str,
        display_name: str,
        created_tick: int,
        created_revision: RevisionId | None,
        entity_id: EntityId | None = None,
        components: Iterable[Any] | None = None,
        metadata: Mapping[str, Any] | None = None,
        alive: bool = True,
        enabled: bool = True,
    ) -> Entity:
        resolved_id = entity_id or EntityId.new(self.world_id, f"{entity_type}:{display_name}:{len(self.entities)}")
        if resolved_id in self.entities:
            raise ValueError(f"entity already exists: {resolved_id}")
        entity = Entity(
            entity_id=resolved_id,
            type=entity_type,
            display_name=display_name,
            created_tick=created_tick,
            created_revision=created_revision,
            alive=alive,
            enabled=enabled,
            metadata={} if metadata is None else dict(metadata),
            relationships=RelationshipGraph(self.world_id),
            actions=ActionRegistry(),
        )
        entity.bind_change_sink(self._entity_change_sink)
        agent_memory = self._world_memory.agent_memory_for(resolved_id) if self._world_memory is not None else AgentMemory(self.world_id, owner_entity_id=resolved_id)
        self.agent_memories[resolved_id] = agent_memory
        entity.metadata.setdefault("agent_memory_id", agent_memory.memory_id)
        for component in components or ():
            entity.attach_component(component, tick=created_tick, revision=created_revision, metadata={"initial": True})
        self.entities[resolved_id] = entity
        self._record_entity_event(
            entity,
            kind="entity.create",
            subject=entity.display_name,
            patch=entity.serialize(),
            remove_paths=(),
            metadata=metadata,
            tick=created_tick,
            revision=created_revision,
        )
        self._notify_change()
        return entity

    def destroy_entity(
        self,
        entity_id: EntityId,
        *,
        tick: int | None = None,
        revision: RevisionId | None = None,
        metadata: Mapping[str, Any] | None = None,
    ) -> Entity:
        entity = self.get_entity(entity_id)
        entity.destroy(tick=tick, revision=revision, metadata=metadata)
        if entity_id not in self.agent_memories:
            self.agent_memories[entity_id] = (
                self._world_memory.agent_memory_for(entity_id)
                if self._world_memory is not None
                else AgentMemory(self.world_id, owner_entity_id=entity_id)
            )
        self._notify_change()
        return entity

    def connect_relationship(
        self,
        source_id: EntityId,
        target_id: EntityId,
        relationship_type: str,
        *,
        created_tick: int,
        created_revision: RevisionId | None = None,
        metadata: Mapping[str, Any] | None = None,
    ) -> RelationshipRecord:
        source = self.get_entity(source_id)
        target = self.get_entity(target_id)
        record = self.relationships.add(
            source_id,
            target_id,
            relationship_type,
            created_tick=created_tick,
            created_revision=created_revision,
            metadata=metadata,
        )
        source.relationships.add_record(record)
        target.relationships.add_record(record)
        self._record_entity_event(
            source,
            kind="relationship.connect",
            subject=relationship_type,
            patch={"relationships": source.relationships.serialize()},
            remove_paths=(),
            metadata={"target_id": str(target_id.value), **({} if metadata is None else dict(metadata))},
            tick=created_tick,
            revision=created_revision,
            related_entities=(target,),
        )
        self._notify_change()
        return record

    def disconnect_relationship(
        self,
        relationship_id: str,
        *,
        tick: int | None = None,
        revision: RevisionId | None = None,
        metadata: Mapping[str, Any] | None = None,
    ) -> RelationshipRecord | None:
        record = self.relationships.remove(relationship_id)
        if record is None:
            return None
        source = self.get_entity(record.source_id)
        target = self.get_entity(record.target_id)
        source.relationships.remove(relationship_id)
        target.relationships.remove(relationship_id)
        self._record_entity_event(
            source,
            kind="relationship.disconnect",
            subject=record.relationship_type,
            patch={"relationships": source.relationships.serialize()},
            remove_paths=(),
            metadata={"target_id": str(record.target_id.value), **({} if metadata is None else dict(metadata))},
            tick=tick,
            revision=revision,
            related_entities=(target,),
        )
        self._notify_change()
        return record

    def get_entity(self, entity_id: EntityId) -> Entity:
        try:
            return self.entities[entity_id]
        except KeyError as exc:
            raise KeyError(f"entity not found: {entity_id}") from exc

    def entity_exists(self, entity_id: EntityId) -> bool:
        entity = self.entities.get(entity_id)
        return entity is not None and entity.alive and entity.enabled

    def query(
        self,
        predicate: Callable[[Entity], bool] | None = None,
        *,
        include_destroyed: bool = False,
        include_disabled: bool = False,
    ) -> tuple[Entity, ...]:
        results: list[Entity] = []
        for entity in self.entities.values():
            if not include_destroyed and not entity.alive:
                continue
            if not include_disabled and not entity.enabled:
                continue
            if predicate is not None and not predicate(entity):
                continue
            results.append(entity)
        return tuple(results)

    def list_entities(self, *, include_destroyed: bool = False, include_disabled: bool = False) -> tuple[Entity, ...]:
        return self.query(
            None,
            include_destroyed=include_destroyed,
            include_disabled=include_disabled,
        )

    def find_by_component(self, component_type: type[Any] | str) -> tuple[Entity, ...]:
        key = component_type.__name__ if isinstance(component_type, type) else str(component_type)
        return self.query(lambda entity: key in entity.components)

    def find_by_type(self, entity_type: str) -> tuple[Entity, ...]:
        return self.query(lambda entity: entity.type == entity_type)

    def serialize(self) -> Mapping[str, Any]:
        return freeze_value({str(entity_id.value): entity.serialize() for entity_id, entity in sorted(self.entities.items(), key=lambda item: str(item[0].value))})

    def restore(self, serialized: Mapping[str, Any]) -> None:
        self.entities.clear()
        self.relationships = RelationshipGraph(self.world_id)
        self.history.clear()
        self.agent_memories.clear()
        for entity_state in serialized.values():
            entity = self._entity_from_state(entity_state)
            self.entities[entity.entity_id] = entity
            for record in entity.relationships.records.values():
                self.relationships.add_record(record)
            self.agent_memory_for(entity.entity_id)
        self._notify_change()

    def agent_memory_for(self, entity_id: EntityId) -> AgentMemory | None:
        memory = self.agent_memories.get(entity_id)
        if memory is not None:
            return memory
        if self._world_memory is None:
            return None
        memory = self._world_memory.agent_memory_for(entity_id)
        if memory is not None:
            self.agent_memories[entity_id] = memory
        return memory

    def agent_memory_references(self) -> Mapping[EntityId, str]:
        return freeze_value({entity_id: memory.memory_id for entity_id, memory in self.agent_memories.items()})

    def history_for(self, entity_id: EntityId) -> tuple[StateEvent, ...]:
        return tuple(event for event in self.history if event.entity_id == entity_id)

    def _entity_change_sink(
        self,
        entity: Entity,
        kind: str,
        subject: str,
        patch: Mapping[str, Any],
        remove_paths: tuple[tuple[str, ...], ...],
        metadata: Mapping[str, Any] | None,
        tick: int | None,
        revision: RevisionId | None,
    ) -> None:
        self._record_entity_event(
            entity,
            kind=kind,
            subject=subject,
            patch=patch,
            remove_paths=remove_paths,
            metadata=metadata,
            tick=tick,
            revision=revision,
        )
        self._notify_change()

    def _record_entity_event(
        self,
        entity: Entity,
        *,
        kind: str,
        subject: str,
        patch: Mapping[str, Any],
        remove_paths: tuple[tuple[str, ...], ...],
        metadata: Mapping[str, Any] | None,
        tick: int | None,
        revision: RevisionId | None,
        related_entities: tuple[Entity, ...] = (),
    ) -> StateEvent:
        event = StateEvent.from_transition(
            world_id=self.world_id,
            revision_id=revision,
            tick_id=TickId.new(self.world_id, entity.created_tick if tick is None else tick),
            subject=subject,
            patch=patch,
            remove_paths=remove_paths,
            state_before=entity.serialize(),
            index=len(self.history),
            metadata={"kind": kind, **({} if metadata is None else dict(metadata))},
            entity_id=entity.entity_id,
        )
        entity.history.append(event)
        entity.history_ref = str(event.event_id.value)
        for related in related_entities:
            related.history.append(event)
            related.history_ref = str(event.event_id.value)
        self.history.append(event)
        return event

    def _notify_change(self) -> None:
        if self._on_change is not None:
            self._on_change()

    def _entity_from_state(self, entity_state: Mapping[str, Any]) -> Entity:
        entity_id = EntityId.from_uuid(entity_state["entity_id"])
        created_revision_value = entity_state.get("created_revision")
        created_revision = None if created_revision_value is None else RevisionId.from_uuid(created_revision_value)
        entity = Entity(
            entity_id=entity_id,
            type=str(entity_state["type"]),
            display_name=str(entity_state["display_name"]),
            created_tick=int(entity_state["created_tick"]),
            created_revision=created_revision,
            alive=bool(entity_state.get("alive", True)),
            enabled=bool(entity_state.get("enabled", True)),
            metadata=dict(entity_state.get("metadata", {})),
            relationships=RelationshipGraph(self.world_id),
            actions=ActionRegistry(),
        )
        entity.bind_change_sink(self._entity_change_sink)
        for component_name, component_payload in dict(entity_state.get("components", {})).items():
            entity.components[component_name] = deserialize_component(component_name, component_payload)
        for relationship_state in entity_state.get("relationships", ()):
            record = RelationshipRecord(
                relationship_id=str(relationship_state["relationship_id"]),
                relationship_type=str(relationship_state["relationship_type"]),
                source_id=EntityId.from_uuid(relationship_state["source_id"]),
                target_id=EntityId.from_uuid(relationship_state["target_id"]),
                created_tick=int(relationship_state["created_tick"]),
                created_revision=None
                if relationship_state.get("created_revision") is None
                else RevisionId.from_uuid(relationship_state["created_revision"]),
                metadata=dict(relationship_state.get("metadata", {})),
            )
            entity.relationships.add_record(record)
        for action_state in entity_state.get("actions", ()):
            entity.actions.register(
                ActionDefinition(
                    identifier=str(action_state["identifier"]),
                    preconditions=tuple(action_state.get("preconditions", ())),
                    required_components=tuple(action_state.get("required_components", ())),
                    resource_requirements=dict(action_state.get("resource_requirements", {})),
                    cooldown=float(action_state.get("cooldown", 0.0)),
                    metadata=dict(action_state.get("metadata", {})),
                )
            )
        entity.history_ref = str(entity_state.get("history_ref", ""))
        return entity
