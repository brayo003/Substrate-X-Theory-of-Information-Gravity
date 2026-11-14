from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable, Mapping

from .actions import ActionDefinition, ActionRegistry
from .components import component_key, component_state
from ..core.contracts import freeze_value
from ..core.ids import EntityId, RevisionId
from .relationships import RelationshipGraph, RelationshipRecord


EntityChangeSink = Callable[
    [
        "Entity",
        str,
        str,
        Mapping[str, Any],
        tuple[tuple[str, ...], ...],
        Mapping[str, Any] | None,
        int | None,
        RevisionId | None,
    ],
    None,
]


@dataclass
class Entity:
    entity_id: EntityId
    type: str
    display_name: str
    created_tick: int
    created_revision: RevisionId | None
    alive: bool = True
    enabled: bool = True
    components: dict[str, Any] = field(default_factory=dict)
    relationships: RelationshipGraph = field(default_factory=RelationshipGraph)
    actions: ActionRegistry = field(default_factory=ActionRegistry)
    metadata: dict[str, Any] = field(default_factory=dict)
    history: list[Any] = field(default_factory=list)
    history_ref: str = ""
    _change_sink: EntityChangeSink | None = field(default=None, repr=False, compare=False)

    def __post_init__(self) -> None:
        self.type = str(self.type)
        self.display_name = str(self.display_name)
        self.created_tick = int(self.created_tick)
        self.metadata = dict(self.metadata)
        self.components = dict(self.components)

    @property
    def lifecycle(self) -> str:
        if not self.alive:
            return "destroyed_tombstoned"
        if not self.enabled:
            return "dormant"
        return "active"

    def bind_change_sink(self, sink: EntityChangeSink | None) -> None:
        self._change_sink = sink

    def attach_component(
        self,
        component: Any,
        *,
        tick: int | None = None,
        revision: RevisionId | None = None,
        metadata: Mapping[str, Any] | None = None,
    ) -> Any:
        key = component_key(component)
        self.components[key] = component
        self._emit_change(
            kind="component.attach",
            subject=key,
            patch={"components": {key: component_state(component)}},
            remove_paths=(),
            metadata=metadata,
            tick=tick,
            revision=revision,
        )
        return component

    def remove_component(
        self,
        component_type: type[Any] | str,
        *,
        tick: int | None = None,
        revision: RevisionId | None = None,
        metadata: Mapping[str, Any] | None = None,
    ) -> Any | None:
        key = component_type.__name__ if isinstance(component_type, type) else str(component_type)
        removed = self.components.pop(key, None)
        if removed is not None:
            self._emit_change(
                kind="component.remove",
                subject=key,
                patch={},
                remove_paths=(("components", key),),
                metadata=metadata,
                tick=tick,
                revision=revision,
            )
        return removed

    def get_component(self, component_type: type[Any] | str, default: Any = None) -> Any:
        key = component_type.__name__ if isinstance(component_type, type) else str(component_type)
        return self.components.get(key, default)

    def has_component(self, component_type: type[Any] | str) -> bool:
        return self.get_component(component_type, None) is not None

    def add_relationship(
        self,
        record: RelationshipRecord,
        *,
        tick: int | None = None,
        revision: RevisionId | None = None,
        metadata: Mapping[str, Any] | None = None,
    ) -> RelationshipRecord:
        self.relationships.add_record(record)
        self._emit_change(
            kind="relationship.add",
            subject=record.relationship_type,
            patch={"relationships": {record.relationship_id: self._relationship_payload(record)}},
            remove_paths=(),
            metadata=metadata,
            tick=tick,
            revision=revision,
        )
        return record

    def remove_relationship(
        self,
        relationship_id: str,
        *,
        tick: int | None = None,
        revision: RevisionId | None = None,
        metadata: Mapping[str, Any] | None = None,
    ) -> RelationshipRecord | None:
        removed = self.relationships.remove(relationship_id)
        if removed is not None:
            self._emit_change(
                kind="relationship.remove",
                subject=removed.relationship_type,
                patch={},
                remove_paths=(("relationships", relationship_id),),
                metadata=metadata,
                tick=tick,
                revision=revision,
            )
        return removed

    def register_action(
        self,
        action: ActionDefinition,
        *,
        tick: int | None = None,
        revision: RevisionId | None = None,
        metadata: Mapping[str, Any] | None = None,
    ) -> ActionDefinition:
        self.actions.register(action)
        self._emit_change(
            kind="action.register",
            subject=action.identifier,
            patch={"actions": {action.identifier: self._action_payload(action)}},
            remove_paths=(),
            metadata=metadata,
            tick=tick,
            revision=revision,
        )
        return action

    def unregister_action(
        self,
        identifier: str,
        *,
        tick: int | None = None,
        revision: RevisionId | None = None,
        metadata: Mapping[str, Any] | None = None,
    ) -> ActionDefinition | None:
        removed = self.actions.unregister(identifier)
        if removed is not None:
            self._emit_change(
                kind="action.unregister",
                subject=removed.identifier,
                patch={},
                remove_paths=(("actions", removed.identifier),),
                metadata=metadata,
                tick=tick,
                revision=revision,
            )
        return removed

    def destroy(
        self,
        *,
        tick: int | None = None,
        revision: RevisionId | None = None,
        metadata: Mapping[str, Any] | None = None,
    ) -> None:
        self.alive = False
        self.enabled = False
        self._emit_change(
            kind="entity.destroy",
            subject=self.display_name,
            patch={"alive": False, "enabled": False, "lifecycle": "destroyed_tombstoned"},
            remove_paths=(),
            metadata=metadata,
            tick=tick,
            revision=revision,
        )

    def serialize(self) -> Mapping[str, Any]:
        return freeze_value(
            {
                "entity_id": str(self.entity_id.value),
                "type": self.type,
                "display_name": self.display_name,
                "created_tick": self.created_tick,
                "created_revision": None if self.created_revision is None else str(self.created_revision.value),
                "alive": self.alive,
                "enabled": self.enabled,
                "lifecycle": self.lifecycle,
                "components": {key: component_state(value) for key, value in self.components.items()},
                "relationships": self.relationships.serialize(),
                "actions": self.actions.serialize(),
                "metadata": self.metadata,
                "history_ref": self.history_ref,
                "history": tuple(str(event.event_id.value) for event in self.history),
            }
        )

    def _relationship_payload(self, record: RelationshipRecord) -> Mapping[str, Any]:
        return {
            "relationship_id": record.relationship_id,
            "relationship_type": record.relationship_type,
            "source_id": str(record.source_id.value),
            "target_id": str(record.target_id.value),
            "created_tick": record.created_tick,
            "created_revision": None if record.created_revision is None else str(record.created_revision.value),
            "metadata": record.metadata,
        }

    def _action_payload(self, action: ActionDefinition) -> Mapping[str, Any]:
        return {
            "identifier": action.identifier,
            "preconditions": action.preconditions,
            "required_components": action.required_components,
            "resource_requirements": action.resource_requirements,
            "cooldown": action.cooldown,
            "metadata": action.metadata,
        }

    def _emit_change(
        self,
        *,
        kind: str,
        subject: str,
        patch: Mapping[str, Any],
        remove_paths: tuple[tuple[str, ...], ...],
        metadata: Mapping[str, Any] | None,
        tick: int | None,
        revision: RevisionId | None,
    ) -> None:
        if self._change_sink is not None:
            self._change_sink(
                self,
                kind,
                subject,
                patch,
                remove_paths,
                metadata,
                self.created_tick if tick is None else tick,
                revision,
            )
