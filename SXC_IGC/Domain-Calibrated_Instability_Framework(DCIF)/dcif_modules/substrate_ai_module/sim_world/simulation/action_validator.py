from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Mapping, Sequence

from ..entities.actions import ActionDefinition
from ..entities.components import component_key
from ..core.contracts import freeze_value
from ..core.ids import EntityId
from .simulation_context import ActionRequest, SimulationContext


@dataclass(frozen=True, slots=True)
class ActionValidationFailure:
    code: str
    message: str
    actor_id: EntityId | None = None
    target_id: EntityId | None = None
    item_id: EntityId | None = None
    details: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        object.__setattr__(self, "code", str(self.code))
        object.__setattr__(self, "message", str(self.message))
        object.__setattr__(self, "details", freeze_value(dict(self.details)))


@dataclass(frozen=True, slots=True)
class ActionValidationResult:
    valid: bool
    request: ActionRequest
    definition: ActionDefinition | None
    failures: tuple[ActionValidationFailure, ...] = field(default_factory=tuple)
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        object.__setattr__(self, "failures", tuple(self.failures))
        object.__setattr__(self, "metadata", freeze_value(dict(self.metadata)))


def _entity_key(entity_id: EntityId) -> str:
    return str(entity_id.value)


def _world_entity(world_state: Mapping[str, Any], entity_id: EntityId) -> Mapping[str, Any] | None:
    return dict(world_state.get("entities", {})).get(_entity_key(entity_id))


def _component_state(entity_state: Mapping[str, Any] | None, name: str) -> Mapping[str, Any] | None:
    if entity_state is None:
        return None
    components = dict(entity_state.get("components", {}))
    payload = components.get(name)
    if payload is None:
        return None
    return dict(payload)


def _inventory_items(entity_state: Mapping[str, Any] | None) -> list[dict[str, Any]]:
    component = _component_state(entity_state, "InventoryComponent")
    if component is None:
        return []
    return [dict(item) for item in component.get("items", ())]


DEFAULT_ACTIONS: dict[str, ActionDefinition] = {
    "Walk": ActionDefinition("Walk", preconditions=("alive", "enabled"), required_components=("TransformComponent",)),
    "Sit": ActionDefinition("Sit", preconditions=("alive", "enabled"), required_components=("TransformComponent",)),
    "Stand": ActionDefinition("Stand", preconditions=("alive", "enabled"), required_components=("TransformComponent",)),
    "PickUp": ActionDefinition("PickUp", preconditions=("alive", "enabled", "same_room"), required_components=("TransformComponent",)),
    "Drop": ActionDefinition("Drop", preconditions=("alive", "enabled"), required_components=("TransformComponent",)),
    "Open": ActionDefinition("Open", preconditions=("alive", "enabled", "same_room"), required_components=("TransformComponent",)),
    "Close": ActionDefinition("Close", preconditions=("alive", "enabled", "same_room"), required_components=("TransformComponent",)),
    "Eat": ActionDefinition("Eat", preconditions=("alive", "enabled"), required_components=("InventoryComponent",)),
    "Drink": ActionDefinition("Drink", preconditions=("alive", "enabled"), required_components=("InventoryComponent",)),
    "Sleep": ActionDefinition("Sleep", preconditions=("alive", "enabled"), required_components=("HealthComponent",)),
    "Talk": ActionDefinition("Talk", preconditions=("alive", "enabled", "same_room"), required_components=("TransformComponent",)),
    "Follow": ActionDefinition("Follow", preconditions=("alive", "enabled"), required_components=("TransformComponent",)),
    "Deposit": ActionDefinition("Deposit", preconditions=("alive", "enabled"), required_components=("InventoryComponent",)),
    "Withdraw": ActionDefinition("Withdraw", preconditions=("alive", "enabled"), required_components=("InventoryComponent",)),
    "Store": ActionDefinition("Store", preconditions=("alive", "enabled"), required_components=("InventoryComponent",)),
    "Transfer": ActionDefinition("Transfer", preconditions=("alive", "enabled"), required_components=("InventoryComponent",)),
    "Consume": ActionDefinition("Consume", preconditions=("alive", "enabled"), required_components=("InventoryComponent",)),
    # Emergent-production / economy actions. These are produced by the
    # agriculture, production and economy goal generators and executed by the
    # ActionExecutor, so the plan validator must recognize them as default
    # actions -- otherwise every PlantCrop/HarvestCrop/CraftRecipe/Trade plan
    # is rejected with "capability_missing" and fields never get planted,
    # harvests never refill food, and the village starves to static equilibrium.
    "PlantCrop": ActionDefinition("PlantCrop", preconditions=("alive", "enabled"), required_components=("InventoryComponent",)),
    "PlantField": ActionDefinition("PlantField", preconditions=("alive", "enabled"), required_components=("InventoryComponent",)),
    "WaterCrop": ActionDefinition("WaterCrop", preconditions=("alive", "enabled"), required_components=("InventoryComponent",)),
    "WaterField": ActionDefinition("WaterField", preconditions=("alive", "enabled"), required_components=("InventoryComponent",)),
    "IncreaseMoisture": ActionDefinition("IncreaseMoisture", preconditions=("alive", "enabled"), required_components=("InventoryComponent",)),
    "HarvestCrop": ActionDefinition("HarvestCrop", preconditions=("alive", "enabled"), required_components=("InventoryComponent",)),
    "HarvestField": ActionDefinition("HarvestField", preconditions=("alive", "enabled"), required_components=("InventoryComponent",)),
    "CraftRecipe": ActionDefinition("CraftRecipe", preconditions=("alive", "enabled"), required_components=("InventoryComponent",)),
    "CraftItem": ActionDefinition("CraftItem", preconditions=("alive", "enabled"), required_components=("InventoryComponent",)),
    "Craft": ActionDefinition("Craft", preconditions=("alive", "enabled"), required_components=("InventoryComponent",)),
    "TradeResource": ActionDefinition("TradeResource", preconditions=("alive", "enabled"), required_components=("InventoryComponent",)),
    "Trade": ActionDefinition("Trade", preconditions=("alive", "enabled"), required_components=("InventoryComponent",)),
    "DeliverResource": ActionDefinition("DeliverResource", preconditions=("alive", "enabled"), required_components=("InventoryComponent",)),
    "Deliver": ActionDefinition("Deliver", preconditions=("alive", "enabled"), required_components=("InventoryComponent",)),
    "DeliverFood": ActionDefinition("DeliverFood", preconditions=("alive", "enabled"), required_components=("InventoryComponent",)),
    "StoreHarvest": ActionDefinition("StoreHarvest", preconditions=("alive", "enabled"), required_components=("InventoryComponent",)),
    "StoreResources": ActionDefinition("StoreResources", preconditions=("alive", "enabled"), required_components=("InventoryComponent",)),
}


@dataclass
class ActionValidator:
    definitions: dict[str, ActionDefinition] = field(default_factory=lambda: dict(DEFAULT_ACTIONS))

    def definition_for(self, action_name: str, world_state: Mapping[str, Any], actor_id: EntityId | None = None) -> ActionDefinition | None:
        if actor_id is not None:
            actor = _world_entity(world_state, actor_id)
            if actor is not None:
                for action_state in actor.get("actions", ()):
                    if str(action_state.get("identifier")) == action_name:
                        return ActionDefinition(
                            identifier=action_name,
                            preconditions=tuple(action_state.get("preconditions", ())),
                            required_components=tuple(action_state.get("required_components", ())),
                            resource_requirements=dict(action_state.get("resource_requirements", {})),
                            cooldown=float(action_state.get("cooldown", 0.0)),
                            metadata=dict(action_state.get("metadata", {})),
                        )
        return self.definitions.get(action_name)

    def validate(self, request: ActionRequest, context: SimulationContext) -> ActionValidationResult:
        world_state = context.world_state
        actor = _world_entity(world_state, request.actor_id)
        definition = self.definition_for(request.action, world_state, request.actor_id)
        failures: list[ActionValidationFailure] = []

        if actor is None:
            failures.append(ActionValidationFailure("entity_missing", "actor does not exist", actor_id=request.actor_id))
            return ActionValidationResult(False, request, definition, tuple(failures))

        if not bool(actor.get("alive", True)):
            failures.append(ActionValidationFailure("entity_dead", "dead entities cannot act", actor_id=request.actor_id))
        if not bool(actor.get("enabled", True)):
            failures.append(ActionValidationFailure("entity_disabled", "disabled entities cannot act", actor_id=request.actor_id))

        required_components = tuple(definition.required_components) if definition is not None else ()
        for component_name in required_components:
            if component_name not in dict(actor.get("components", {})):
                failures.append(
                    ActionValidationFailure(
                        "missing_component",
                        f"missing required component: {component_name}",
                        actor_id=request.actor_id,
                        details={"component": component_name},
                    )
                )

        if definition is not None:
            for resource_name, required_quantity in dict(definition.resource_requirements).items():
                available = self._resource_quantity(actor, resource_name)
                if available < float(required_quantity):
                    failures.append(
                        ActionValidationFailure(
                            "insufficient_resources",
                            f"missing required resource: {resource_name}",
                            actor_id=request.actor_id,
                            details={"resource": resource_name, "required": float(required_quantity), "available": available},
                        )
                    )

        action = request.action
        actor_room = self._room(actor)
        target = _world_entity(world_state, request.target_id) if request.target_id is not None else None
        item = _world_entity(world_state, request.item_id) if request.item_id is not None else None

        if action == "Walk":
            destination_room = self._destination_room(request, target)
            if destination_room is None:
                failures.append(ActionValidationFailure("destination_missing", "walk requires a destination room", actor_id=request.actor_id))
            elif actor_room == destination_room:
                failures.append(ActionValidationFailure("no_op", "entity is already in the destination room", actor_id=request.actor_id))
            elif self._door_blocks_movement(world_state, actor_room, destination_room):
                failures.append(
                    ActionValidationFailure(
                        "door_closed",
                        "door is closed between the rooms",
                        actor_id=request.actor_id,
                        target_id=request.target_id,
                        details={"from_room": actor_room, "to_room": destination_room},
                    )
                )
        elif action in {"PickUp", "Drop", "Talk", "Follow", "Open", "Close", "Eat", "Drink"}:
            if action == "Drop":
                if target is None and item is None:
                    failures.append(ActionValidationFailure("target_missing", "Drop requires an item or target entity", actor_id=request.actor_id))
            elif action in {"PickUp", "Talk", "Follow", "Open", "Close"} and target is None:
                failures.append(ActionValidationFailure("target_missing", f"{action} requires a target entity", actor_id=request.actor_id))

        if action == "PickUp" and target is not None:
            if self._room(target) != actor_room:
                failures.append(ActionValidationFailure("distance", "target is not in the same room", actor_id=request.actor_id, target_id=request.target_id))
            if target.get("metadata", {}).get("held_by") is not None:
                failures.append(ActionValidationFailure("already_held", "target is already held", actor_id=request.actor_id, target_id=request.target_id))
        if action == "Drop" and item is not None:
            if self._room(item) is not None and item.get("metadata", {}).get("held_by") != str(request.actor_id.value):
                failures.append(ActionValidationFailure("ownership", "actor does not hold the target item", actor_id=request.actor_id, item_id=request.item_id))
        if action in {"Open", "Close"} and target is not None:
            if self._room(target) != actor_room:
                failures.append(ActionValidationFailure("distance", "door is not in the same room", actor_id=request.actor_id, target_id=request.target_id))
        if action in {"Talk", "Follow"} and target is not None and self._room(target) != actor_room:
            failures.append(ActionValidationFailure("distance", "target is not in the same room", actor_id=request.actor_id, target_id=request.target_id))
        if action in {"Eat", "Drink"} and not self._has_consumable(actor, action, request.quantity):
            failures.append(ActionValidationFailure("resource_missing", f"no consumable resource for {action.lower()}", actor_id=request.actor_id))

        valid = not failures
        return ActionValidationResult(valid, request, definition, tuple(failures))

    def _room(self, entity_state: Mapping[str, Any]) -> str | None:
        transform = _component_state(entity_state, "TransformComponent")
        if transform is None:
            return None
        room = transform.get("room")
        return None if room is None else str(room)

    def _resource_quantity(self, entity_state: Mapping[str, Any], resource_name: str) -> float:
        inventory = _inventory_items(entity_state)
        return sum(float(item.get("quantity", 0.0)) for item in inventory if str(item.get("identifier")) == resource_name)

    def _has_consumable(self, entity_state: Mapping[str, Any], action: str, quantity: float | None) -> bool:
        inventory = _inventory_items(entity_state)
        identifier = "food" if action == "Eat" else "water"
        required = 1.0 if quantity is None else float(quantity)
        available = sum(float(item.get("quantity", 0.0)) for item in inventory if str(item.get("identifier")) == identifier)
        return available >= required

    def _destination_room(self, request: ActionRequest, target: Mapping[str, Any] | None) -> str | None:
        if request.destination_room is not None:
            return str(request.destination_room)
        if target is None:
            return None
        return self._room(target)

    def _door_blocks_movement(self, world_state: Mapping[str, Any], from_room: str | None, to_room: str | None) -> bool:
        if from_room is None or to_room is None:
            return False
        if from_room == to_room:
            return False
        for entity_state in dict(world_state.get("entities", {})).values():
            if str(entity_state.get("type")) != "door":
                continue
            metadata = dict(entity_state.get("metadata", {}))
            connects = metadata.get("connects") or metadata.get("rooms")
            if not connects or len(connects) != 2:
                continue
            rooms = {str(connects[0]), str(connects[1])}
            if {from_room, to_room} == rooms and not bool(metadata.get("open", False)):
                return True
        return False
