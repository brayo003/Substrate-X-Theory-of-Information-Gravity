from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Mapping

from ..entities.components import ResourceDescriptor
from ..core.contracts import TransitionProposal, freeze_value
from ..core.ids import EntityId, WorldId
from .simulation_context import ActionRequest, SimulationContext
from .action_validator import ActionValidationResult


def _entity_key(entity_id: EntityId) -> str:
    return str(entity_id.value)


def _entity_state(world_state: Mapping[str, Any], entity_id: EntityId) -> dict[str, Any] | None:
    return dict(dict(world_state.get("entities", {})).get(_entity_key(entity_id), {})) or None


def _component_state(entity_state: Mapping[str, Any] | None, name: str) -> dict[str, Any] | None:
    if entity_state is None:
        return None
    payload = dict(entity_state.get("components", {})).get(name)
    if payload is None:
        return None
    return dict(payload)


def _entity_patch(entity_id: EntityId, payload: Mapping[str, Any]) -> Mapping[str, Any]:
    return {"entities": {_entity_key(entity_id): payload}}


# ACTION HANDLERS FOR WORLD MUTATION
def _handle_eat_action(action: ActionRequest, context: SimulationContext) -> TransitionProposal:
    """Handle eat action: reduces inventory, reduces hunger"""
    entity_id = str(action.actor_id.value)
    quantity = action.quantity or 1
    
    # DOMAIN-LOCKED: This should mutate inventory (Resources domain) and needs (Needs domain)
    # For now, create action signals for domains to process
    return TransitionProposal(
        world_id=context.world_id,
        tick_id=context.tick_context.tick_id,
        state_revision=None,
        correlation_id=f"action.eat.{entity_id}",
        subject="action.eat",
        patch={
            "action_eat_signals": [{
                "entity_id": entity_id,
                "item_id": str(action.item_id),
                "quantity": quantity
            }]
        },
        description=f"eat action: {entity_id} eats {quantity} food",
        metadata={"action": "eat", "entity_id": entity_id, "quantity": quantity}
    )


def _handle_harvest_action(action: ActionRequest, context: SimulationContext) -> TransitionProposal:
    """Handle harvest action: reduces farm resources, increases inventory"""
    entity_id = str(action.actor_id.value)
    target_id = str(action.target_id)
    item_id = str(action.item_id)
    quantity = action.quantity or 1
    
    # DOMAIN-LOCKED: This should mutate resources (Resources domain) and inventory (Resources domain)
    return TransitionProposal(
        world_id=context.world_id,
        tick_id=context.tick_context.tick_id,
        state_revision=None,
        correlation_id=f"action.harvest.{entity_id}",
        subject="action.harvest",
        patch={
            "action_harvest_signals": [{
                "entity_id": entity_id,
                "target_id": target_id,
                "item_id": item_id,
                "quantity": quantity
            }]
        },
        description=f"harvest action: {entity_id} harvests {quantity} {item_id} from {target_id}",
        metadata={"action": "harvest", "entity_id": entity_id, "target_id": target_id, "item_id": item_id, "quantity": quantity}
    )


def _resource_state(items: list[dict[str, Any]]) -> tuple[dict[str, Any], ...]:
    return tuple(
        dict(ResourceDescriptor(identifier=item["identifier"], quantity=item.get("quantity", 0.0), properties=item.get("properties", {})).to_state())
        for item in items
    )


@dataclass(frozen=True, slots=True)
class ActionExecutionReport:
    action: str
    proposal_count: int
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        object.__setattr__(self, "action", str(self.action))
        object.__setattr__(self, "proposal_count", int(self.proposal_count))
        object.__setattr__(self, "metadata", freeze_value(dict(self.metadata)))


@dataclass
class ActionExecutor:
    def execute(self, validation: ActionValidationResult, context: SimulationContext) -> tuple[TransitionProposal, ...]:
        if not validation.valid:
            return ()
        request = validation.request
        world_state = context.world_state
        actor = _entity_state(world_state, request.actor_id)
        if actor is None:
            return ()
        action = request.action
        proposals: list[TransitionProposal] = []

        if action == "Walk":
            proposals.append(self._walk(request, actor, context))
        elif action == "Sit":
            proposals.append(self._status(request, context, "sitting"))
        elif action == "Stand":
            proposals.append(self._status(request, context, "standing"))
        elif action == "PickUp":
            proposals.append(self._pickup(request, context, world_state, actor))
        elif action == "Drop":
            proposals.append(self._drop(request, context, world_state, actor))
        elif action == "Open":
            proposals.append(self._door(request, context, True))
        elif action == "Close":
            proposals.append(self._door(request, context, False))
        elif action == "Eat":
            proposals.append(self._consume(request, context, actor, "food", "hunger", 0.35))
        elif action == "Drink":
            proposals.append(self._consume(request, context, actor, "water", "thirst", 0.35))
        elif action == "Sleep":
            proposals.append(self._sleep(request, context, actor))
        elif action == "Talk":
            proposals.append(self._talk(request, context, actor))
        elif action == "Follow":
            proposals.append(self._follow(request, context, world_state, actor))
        elif action in {"Deposit", "Store"}:
            proposals.append(self._deposit(request, context, world_state, actor))
        elif action == "Withdraw":
            proposals.append(self._withdraw(request, context, world_state, actor))
        elif action == "Transfer":
            proposals.append(self._transfer(request, context, world_state, actor))
        elif action == "Consume":
            res_type = str(request.parameters.get("resource_type") or request.metadata.get("resource_type") or "food")
            need_key = "hunger" if res_type == "food" else ("thirst" if res_type == "water" else "")
            proposals.append(self._consume(request, context, actor, res_type, need_key, 0.35))
        elif action in {"PlantCrop", "PlantField"}:
            field_id = str(request.parameters.get("field_id") or request.metadata.get("field_id") or "field_1")
            crop_type = str(request.parameters.get("crop_type") or request.metadata.get("crop_type") or "Wheat")
            from ..domains.agriculture.agriculture_domain import plant_crop
            proposals.append(plant_crop(context, request.actor_id, field_id, crop_type))
        elif action in {"WaterCrop", "WaterField", "IncreaseMoisture"}:
            field_id = str(request.parameters.get("field_id") or request.metadata.get("field_id") or "field_1")
            from ..domains.agriculture.agriculture_domain import water_crop
            proposals.append(water_crop(context, request.actor_id, field_id))
        elif action in {"HarvestCrop", "HarvestField"}:
            field_id = str(request.parameters.get("field_id") or request.metadata.get("field_id") or "field_1")
            from ..domains.agriculture.agriculture_domain import harvest_crop
            proposals.append(harvest_crop(context, request.actor_id, field_id))
        elif action in {"CraftRecipe", "CraftItem", "Craft"}:
            recipe_name = str(request.parameters.get("recipe_name") or request.metadata.get("recipe_name") or "wheat_to_flour")
            from ..domains.economy.economy_domain import craft_recipe
            proposals.append(craft_recipe(context, request.actor_id, recipe_name))
        elif action in {"TradeResource", "Trade"}:
            item_given = str(request.parameters.get("item_given", "wood"))
            qty_given = float(request.parameters.get("qty_given", 1.0))
            item_received = str(request.parameters.get("item_received", "food"))
            qty_received = float(request.parameters.get("qty_received", 1.0))
            target_id = request.target_id or request.actor_id
            from ..domains.economy.economy_domain import trade_resource
            proposals.append(trade_resource(context, request.actor_id, target_id, item_given, qty_given, item_received, qty_received))
        elif action in {"DeliverResource", "Deliver", "DeliverFood", "StoreHarvest", "StoreResources"}:
            src_id = request.actor_id
            dst_id = request.target_id or request.actor_id
            res_type = str(request.parameters.get("resource_type") or request.metadata.get("resource_type") or "food")
            qty = float(request.quantity or request.parameters.get("quantity") or 1.0)
            from ..domains.economy.economy_domain import deliver_resource
            proposals.append(deliver_resource(context, request.actor_id, src_id, dst_id, res_type, qty))
        elif action in {"Talk", "TalkTo", "Help", "Helped", "Share", "Teach", "WorkTogether", "Visit"}:
            target_id = request.target_id or request.parameters.get("target_id") or request.metadata.get("target_id") or "Joren"
            interaction_type = "Talk" if action in {"Talk", "TalkTo", "Visit"} else ("Helped" if action in {"Help", "Helped"} else action)
            from ..domains.relationships.relationships_domain import record_social_interaction
            proposals.append(record_social_interaction(context, request.actor_id, target_id, interaction_type))
        else:
            proposals.append(
                TransitionProposal(
                    world_id=context.world_id,
                    tick_id=context.tick_context.tick_id,
                    state_revision=context.committed_revision,
                    correlation_id=request.correlation_id or context.tick_context.correlation_id,
                    subject=request.action,
                    patch={},
                    description="unsupported action passthrough",
                    metadata={"entity_id": str(request.actor_id.value), **dict(request.metadata)},
                )
            )

        return tuple(proposals)

    def _walk(self, request: ActionRequest, actor: Mapping[str, Any], context: SimulationContext) -> TransitionProposal:
        transform = _component_state(actor, "TransformComponent") or {}
        destination = request.destination_room
        if destination is None and request.target_id is not None:
            target = _entity_state(context.world_state, request.target_id)
            if target is not None:
                target_transform = _component_state(target, "TransformComponent") or {}
                destination = target_transform.get("room")
        patch = _entity_patch(
            request.actor_id,
            {
                "components": {
                    "TransformComponent": {
                        "position": tuple(transform.get("position", (0.0, 0.0, 0.0))),
                        "rotation": tuple(transform.get("rotation", (0.0, 0.0, 0.0, 1.0))),
                        "room": destination,
                        "component_type": "TransformComponent",
                    }
                },
                "metadata": {
                    **dict(actor.get("metadata", {})),
                    "last_action": "Walk",
                    "last_destination_room": destination,
                },
            },
        )
        return self._proposal("WalkAction", request, context, patch, {"entity_id": str(request.actor_id.value), "action": "Walk", "destination_room": destination})

    def _status(self, request: ActionRequest, context: SimulationContext, status: str) -> TransitionProposal:
        return self._proposal(
            f"{request.action}Action",
            request,
            context,
            _entity_patch(request.actor_id, {"metadata": {"status": status}}),
            {"entity_id": str(request.actor_id.value), "action": request.action, "status": status},
        )

    def _pickup(self, request: ActionRequest, context: SimulationContext, world_state: Mapping[str, Any], actor: Mapping[str, Any]) -> TransitionProposal:
        target = _entity_state(world_state, request.target_id) if request.target_id is not None else None
        actor_transform = _component_state(actor, "TransformComponent") or {}
        target_transform = _component_state(target, "TransformComponent") or {} if target is not None else {}
        actor_room = actor_transform.get("room")
        actor_metadata = dict(actor.get("metadata", {}))
        holding = set(str(item) for item in actor_metadata.get("holding", ()))
        if request.target_id is not None:
            holding.add(_entity_key(request.target_id))
        patch: dict[str, Any] = {
            "entities": {
                _entity_key(request.actor_id): {
                    "metadata": {
                        **actor_metadata,
                        "holding": tuple(sorted(holding)),
                    }
                }
            }
        }
        if request.target_id is not None and target is not None:
            target_meta = dict(target.get("metadata", {}))
            target_meta["held_by"] = str(request.actor_id.value)
            patch["entities"][_entity_key(request.target_id)] = {
                "components": {
                    "TransformComponent": {
                        "position": tuple(target_transform.get("position", (0.0, 0.0, 0.0))),
                        "rotation": tuple(target_transform.get("rotation", (0.0, 0.0, 0.0, 1.0))),
                        "room": None,
                        "component_type": "TransformComponent",
                    }
                },
                "metadata": target_meta,
            }
        return self._proposal("PickUpAction", request, context, patch, {"entity_id": str(request.actor_id.value), "action": "PickUp", "room": actor_room})

    def _drop(self, request: ActionRequest, context: SimulationContext, world_state: Mapping[str, Any], actor: Mapping[str, Any]) -> TransitionProposal:
        target = _entity_state(world_state, request.item_id) if request.item_id is not None else _entity_state(world_state, request.target_id) if request.target_id is not None else None
        actor_transform = _component_state(actor, "TransformComponent") or {}
        actor_room = actor_transform.get("room")
        actor_metadata = dict(actor.get("metadata", {}))
        actor_metadata["holding"] = tuple()
        patch: dict[str, Any] = {
            "entities": {
                _entity_key(request.actor_id): {
                    "metadata": actor_metadata,
                }
            }
        }
        if target is not None and (request.item_id is not None or request.target_id is not None):
            target_transform = _component_state(target, "TransformComponent") or {}
            target_meta = dict(target.get("metadata", {}))
            target_meta["held_by"] = None
            patch["entities"][_entity_key(request.item_id or request.target_id)] = {
                "components": {
                    "TransformComponent": {
                        "position": tuple(target_transform.get("position", (0.0, 0.0, 0.0))),
                        "rotation": tuple(target_transform.get("rotation", (0.0, 0.0, 0.0, 1.0))),
                        "room": actor_room,
                        "component_type": "TransformComponent",
                    }
                },
                "metadata": target_meta,
            }
        return self._proposal("DropAction", request, context, patch, {"entity_id": str(request.actor_id.value), "action": "Drop", "room": actor_room})

    def _door(self, request: ActionRequest, context: SimulationContext, open_state: bool) -> TransitionProposal:
        target_id = request.target_id or request.item_id
        metadata = {"entity_id": str(request.actor_id.value), "action": request.action, "open": open_state}
        if target_id is None:
            return self._proposal(f"{request.action}Action", request, context, _entity_patch(request.actor_id, {"metadata": {"door_state": open_state}}), metadata)
        return self._proposal(
            f"{request.action}Action",
            request,
            context,
            _entity_patch(target_id, {"metadata": {"open": open_state}}),
            {**metadata, "target_id": str(target_id.value)},
        )

    def _consume(self, request: ActionRequest, context: SimulationContext, actor: Mapping[str, Any], identifier: str, need_name: str, need_delta: float) -> TransitionProposal:
        inventory_component = _component_state(actor, "InventoryComponent")
        inventory = [dict(item) for item in inventory_component.get("items", ())] if inventory_component else []
        remaining: list[dict[str, Any]] = []
        quantity = 1.0 if request.quantity is None else float(request.quantity)
        consumed = 0.0
        for item in inventory:
            if item.get("identifier") != identifier or consumed >= quantity:
                remaining.append(item)
                continue
            available = float(item.get("quantity", 0.0))
            take = min(available, quantity - consumed)
            consumed += take
            left = available - take
            if left > 0:
                remaining.append({**item, "quantity": left})
        last_action = "Eat" if identifier == "food" else ("Drink" if identifier == "water" else str(request.action or "Consume"))
        patch = {
            "entities": {
                _entity_key(request.actor_id): {
                    "components": {
                        "InventoryComponent": {
                            "items": _resource_state(remaining),
                            "capacity": (_component_state(actor, "InventoryComponent") or {}).get("capacity"),
                            "component_type": "InventoryComponent",
                        },
                    },
                    "metadata": {
                        **dict(actor.get("metadata", {})),
                        "last_action": last_action,
                    },
                }
            }
        }
        return self._proposal(f"{request.action}Action", request, context, patch, {"entity_id": str(request.actor_id.value), "action": request.action, "consumed": consumed})

    def _sleep(self, request: ActionRequest, context: SimulationContext, actor: Mapping[str, Any]) -> TransitionProposal:
        health = dict(_component_state(actor, "HealthComponent") or {})
        if health:
            health["status"] = "resting"
        patch = {
            "entities": {
                _entity_key(request.actor_id): {
                    **({"components": {"HealthComponent": {**health, "component_type": "HealthComponent"}}} if health else {}),
                    "metadata": {
                        **dict(actor.get("metadata", {})),
                        "status": "sleeping",
                        "last_action": "Sleep",
                    },
                }
            }
        }
        return self._proposal("SleepAction", request, context, patch, {"entity_id": str(request.actor_id.value), "action": "Sleep"})

    def _talk(self, request: ActionRequest, context: SimulationContext, actor: Mapping[str, Any]) -> TransitionProposal:
        metadata = dict(actor.get("metadata", {}))
        if request.target_id is not None:
            metadata["last_talk_target"] = str(request.target_id.value)
        return self._proposal("TalkAction", request, context, _entity_patch(request.actor_id, {"metadata": metadata}), {"entity_id": str(request.actor_id.value), "action": "Talk"})

    def _follow(self, request: ActionRequest, context: SimulationContext, world_state: Mapping[str, Any], actor: Mapping[str, Any]) -> TransitionProposal:
        metadata = dict(actor.get("metadata", {}))
        metadata["following"] = None if request.target_id is None else str(request.target_id.value)
        target = _entity_state(world_state, request.target_id) if request.target_id is not None else None
        target_room = None
        if target is not None:
            target_room = (_component_state(target, "TransformComponent") or {}).get("room")
        patch = {
            "entities": {
                _entity_key(request.actor_id): {
                    "metadata": metadata,
                    **(
                        {
                            "components": {
                                "TransformComponent": {
                                    **(_component_state(actor, "TransformComponent") or {}),
                                    "room": target_room,
                                    "component_type": "TransformComponent",
                                }
                            }
                        }
                        if target_room is not None
                        else {}
                    ),
                }
            }
        }
        return self._proposal("FollowAction", request, context, patch, {"entity_id": str(request.actor_id.value), "action": "Follow"})

    def _deposit(self, request: ActionRequest, context: SimulationContext, world_state: Mapping[str, Any], actor: Mapping[str, Any]) -> TransitionProposal:
        target_id = request.target_id or request.item_id
        target = _entity_state(world_state, target_id) if target_id is not None else None
        res_type = str(request.parameters.get("resource_type") or request.metadata.get("resource_type") or "food")
        qty = 1.0 if request.quantity is None else float(request.quantity)

        src_inv = _component_state(actor, "InventoryComponent") or {}
        dst_inv = _component_state(target, "InventoryComponent") or {} if target else {}
        src_items = [dict(i) for i in src_inv.get("items", ())]
        dst_items = [dict(i) for i in dst_inv.get("items", ())]
        dst_cap = float(dst_inv.get("capacity", 500.0))

        from ..domains.resources.resources_rules import deposit_resource_items
        new_src, new_dst, dep_qty, events = deposit_resource_items(
            src_items, dst_items, res_type, qty, _entity_key(request.actor_id), _entity_key(target_id) if target_id else "world", dst_cap
        )

        patch: dict[str, Any] = {
            "entities": {
                _entity_key(request.actor_id): {
                    "components": {
                        "InventoryComponent": {
                            "items": _resource_state(new_src),
                            "capacity": src_inv.get("capacity", 500.0),
                            "component_type": "InventoryComponent",
                        }
                    }
                }
            }
        }
        if target_id is not None:
            patch["entities"][_entity_key(target_id)] = {
                "components": {
                    "InventoryComponent": {
                        "items": _resource_state(new_dst),
                        "capacity": dst_cap,
                        "component_type": "InventoryComponent",
                    }
                }
            }

        return self._proposal(
            f"{request.action}Action",
            request,
            context,
            patch,
            {"entity_id": str(request.actor_id.value), "action": request.action, "resource_type": res_type, "quantity": dep_qty, "events": [e.to_dict() for e in events]},
        )

    def _withdraw(self, request: ActionRequest, context: SimulationContext, world_state: Mapping[str, Any], actor: Mapping[str, Any]) -> TransitionProposal:
        target_id = request.target_id or request.item_id
        target = _entity_state(world_state, target_id) if target_id is not None else None
        res_type = str(request.parameters.get("resource_type") or request.metadata.get("resource_type") or "food")
        qty = 1.0 if request.quantity is None else float(request.quantity)

        src_inv = _component_state(target, "InventoryComponent") or {} if target else {}
        dst_inv = _component_state(actor, "InventoryComponent") or {}
        src_items = [dict(i) for i in src_inv.get("items", ())]
        dst_items = [dict(i) for i in dst_inv.get("items", ())]
        dst_cap = float(dst_inv.get("capacity", 500.0))

        from ..domains.resources.resources_rules import withdraw_resource_items
        new_src, new_dst, w_qty, events = withdraw_resource_items(
            src_items, dst_items, res_type, qty, _entity_key(target_id) if target_id else "world", _entity_key(request.actor_id), dst_cap
        )

        patch: dict[str, Any] = {
            "entities": {
                _entity_key(request.actor_id): {
                    "components": {
                        "InventoryComponent": {
                            "items": _resource_state(new_dst),
                            "capacity": dst_cap,
                            "component_type": "InventoryComponent",
                        }
                    }
                }
            }
        }
        if target_id is not None:
            patch["entities"][_entity_key(target_id)] = {
                "components": {
                    "InventoryComponent": {
                        "items": _resource_state(new_src),
                        "capacity": float(src_inv.get("capacity", 500.0)),
                        "component_type": "InventoryComponent",
                    }
                }
            }

        return self._proposal(
            f"{request.action}Action",
            request,
            context,
            patch,
            {"entity_id": str(request.actor_id.value), "action": request.action, "resource_type": res_type, "quantity": w_qty, "events": [e.to_dict() for e in events]},
        )

    def _transfer(self, request: ActionRequest, context: SimulationContext, world_state: Mapping[str, Any], actor: Mapping[str, Any]) -> TransitionProposal:
        target_id = request.target_id
        item_id = request.item_id
        src_entity = _entity_state(world_state, target_id) if target_id else actor
        dst_entity = _entity_state(world_state, item_id) if item_id else None
        res_type = str(request.parameters.get("resource_type") or request.metadata.get("resource_type") or "food")
        qty = 1.0 if request.quantity is None else float(request.quantity)

        src_inv = _component_state(src_entity, "InventoryComponent") or {}
        dst_inv = _component_state(dst_entity, "InventoryComponent") or {} if dst_entity else {}
        src_items = [dict(i) for i in src_inv.get("items", ())]
        dst_items = [dict(i) for i in dst_inv.get("items", ())]
        dst_cap = float(dst_inv.get("capacity", 500.0))

        from ..domains.resources.resources_rules import transfer_resource_items
        new_src, new_dst, tr_qty, events = transfer_resource_items(
            src_items, dst_items, res_type, qty, _entity_key(target_id or request.actor_id), _entity_key(item_id) if item_id else "world", dst_cap
        )

        patch: dict[str, Any] = {
            "entities": {
                _entity_key(target_id or request.actor_id): {
                    "components": {
                        "InventoryComponent": {
                            "items": _resource_state(new_src),
                            "capacity": float(src_inv.get("capacity", 500.0)),
                            "component_type": "InventoryComponent",
                        }
                    }
                }
            }
        }
        if item_id is not None:
            patch["entities"][_entity_key(item_id)] = {
                "components": {
                    "InventoryComponent": {
                        "items": _resource_state(new_dst),
                        "capacity": dst_cap,
                        "component_type": "InventoryComponent",
                    }
                }
            }

        return self._proposal(
            f"{request.action}Action",
            request,
            context,
            patch,
            {"entity_id": str(request.actor_id.value), "action": request.action, "resource_type": res_type, "quantity": tr_qty, "events": [e.to_dict() for e in events]},
        )

    def _proposal(
        self,
        subject: str,
        request: ActionRequest,
        context: SimulationContext,
        patch: Mapping[str, Any],
        metadata: Mapping[str, Any],
    ) -> TransitionProposal:
        tick_id = context.tick_context.tick_id
        revision = context.committed_revision
        return TransitionProposal(
            world_id=context.world_id,
            tick_id=tick_id,
            state_revision=revision,
            correlation_id=request.correlation_id or context.tick_context.correlation_id,
            subject=subject,
            patch=patch,
            description=request.action,
            metadata={**dict(request.metadata), **dict(metadata)},
        )
