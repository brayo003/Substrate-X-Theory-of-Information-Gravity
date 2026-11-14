from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Mapping, Sequence


from ..core.ids import EntityId, RevisionId, TickId, WorldId
from .planner_context import Goal, PlanProposal, PlannerContext
from ..simulation.simulation_context import ActionRequest
from .capability_planner import CapabilityPlanner

def deterministic_hash(seed: str) -> int:
    s = str(seed or "")
    val = hash(s) % (2**32)
    return abs(val)



_ACTION_COSTS: dict[str, float] = {
    "Walk": 1.5,
    "PickUp": 0.5,
    "Drop": 0.4,
    "Open": 0.3,
    "Close": 0.3,
    "Eat": 0.4,
    "Drink": 0.4,
    "Sleep": 0.2,
    "Talk": 0.2,
    "Follow": 0.2,
    "Sit": 0.1,
    "Stand": 0.1,
}


def _entity_key(entity_id: EntityId) -> str:
    return str(entity_id.value)


def _resolve_target_id(context: PlannerContext, target) -> EntityId | None:
    """Resolve a goal target (EntityId, uuid string, or display name) to an EntityId."""
    if target is None:
        return None
    if isinstance(target, EntityId):
        return target
    if isinstance(target, str):
        for entity_id, ent in dict(context.snapshot.state.get("entities", {})).items():
            if str(ent.get("display_name")) == target or str(ent.get("entity_id")) == target:
                try:
                    return EntityId.from_uuid(entity_id)
                except Exception:
                    return None
    return None


def _entity_state(context: PlannerContext, entity_id: EntityId | None) -> Mapping[str, Any] | None:
    if entity_id is None:
        return None
    return dict(context.snapshot.state.get("entities", {})).get(_entity_key(entity_id))


def _component_state(entity_state: Mapping[str, Any] | None, name: str) -> Mapping[str, Any] | None:
    if entity_state is None:
        return None
    payload = dict(entity_state.get("components", {})).get(name)
    if payload is None:
        return None
    return dict(payload)


def _room(entity_state: Mapping[str, Any] | None) -> str | None:
    transform = _component_state(entity_state, "TransformComponent")
    if transform is None:
        return None
    room = transform.get("room")
    return None if room is None else str(room)


def _deterministic_id(world_id: WorldId, *parts: Any) -> str:
    return str(deterministic_hash("|".join(str(part) for part in (world_id.value, *parts))))


@dataclass
class PlanGenerator:
    """Generate plans from goals using capability-based planning."""
    
    world_id: WorldId
    capability_planner: CapabilityPlanner = field(default_factory=CapabilityPlanner)

    def generate(self, context: PlannerContext, goals: Sequence[Goal]) -> tuple[PlanProposal, ...]:
        plans: list[PlanProposal] = []
        for goal in goals:
            plans.extend(self._generate_goal(context, goal))
        return tuple(plans)

    def _generate_goal(self, context: PlannerContext, goal: Goal) -> list[PlanProposal]:
        if goal.entity_id is None:
            return []
        if self._goal_satisfied(context, goal):
            return []
        
        kind = goal.kind.lower().replace(" ", "_")
        
        # NEW: Use capability-based planner for high-level LLM objectives
        if goal.objective or kind in {
            "establish_food_supply",
            "secure_water_supply",
            "prepare_for_winter",
            "improve_food_reserves",
            "acquire_required_materials",
            "establish_storage",
        }:
            # Use general capability-based planning instead of hardcoded handlers
            return list(self.capability_planner.plan(context, goal))
        
        # Existing deterministic handlers (preserve these)
        if kind in {"survival", "hunger", "thirst", "sleep"}:
            return self._plan_needs(context, goal)
        if kind in {"movement", "move"}:
            return self._plan_movement(context, goal)
        if kind in {"conversation", "talk"}:
            return self._plan_talk(context, goal)
        if kind in {"follow_target", "follow"}:
            return self._plan_follow(context, goal)
        if kind in {"acquire_item", "acquire"}:
            return self._plan_acquire_item(context, goal)
        if kind in {"open_door", "open"}:
            return self._plan_open_door(context, goal)
        if kind in {"explore"}:
            return self._plan_explore(context, goal)
        if kind in {"plantfield", "plant_field", "plantcrop", "plant"}:
            return self._plan_agriculture(context, goal, "PlantCrop")
        if kind in {"waterfield", "water_field", "watercrop", "water"}:
            return self._plan_agriculture(context, goal, "WaterCrop")
        if kind in {"harvestfield", "harvest_field", "harvestcrop", "harvest"}:
            return self._plan_agriculture(context, goal, "HarvestCrop")
        if kind in {"storeharvest", "store_harvest", "deliverfood", "deliver_food", "storeresources", "store_resources"}:
            return self._plan_agriculture(context, goal, "StoreHarvest")
        if kind in {"craftrecipe", "craft_recipe", "craft", "smeltiron", "smelt_iron", "cutwood", "cut_wood"}:
            return self._plan_economy(context, goal, "CraftRecipe")
        if kind in {"trade"}:
            return self._plan_economy(context, goal, "TradeResource")
        if kind in {"talk", "talkto", "talk_to", "help", "share", "teach", "visit"}:
            return self._plan_relationship(context, goal)
        return self._plan_custom(context, goal)

    def _goal_satisfied(self, context: PlannerContext, goal: Goal) -> bool:
        actor = _entity_state(context, goal.entity_id)
        if actor is None:
            return False
        desired = dict(goal.target_state)
        if not desired:
            return False
        actor_room = _room(actor)
        if "room" in desired and actor_room == desired["room"]:
            return True
        metadata = dict(actor.get("metadata", {}))
        if "held_item" in desired:
            held = set(str(item) for item in metadata.get("holding", ()))
            if str(desired["held_item"]) in held:
                return True
        if "status" in desired and metadata.get("status") == desired["status"]:
            return True
        # Sleep goal completes once energy recovers to wake threshold (0.5);
        # the needs-domain wakes the villager then, so status=="sleeping" alone
        # would orphan the goal (blocking future sleep goals via dedup).
        if "status" in desired and desired["status"] == "sleeping":
            needs = _component_state(actor, "NeedsComponent") or {}
            if float(dict(needs.get("needs", {})).get("energy", 0.0)) >= 0.5:
                return True
        if desired.get("open") is not None and metadata.get("open") == desired["open"]:
            return True
        kind = str(goal.kind).lower()
        if kind in {"conversation", "talk", "approach", "socialize", "social"}:
            if str(metadata.get("last_action", "")) == "Talk":
                return True
        if goal.kind.lower() in {"hunger", "thirst"}:
            needs = _component_state(actor, "NeedsComponent") or {}
            need_key = "hunger" if goal.kind.lower() == "hunger" else "thirst"
            threshold = float(desired.get("threshold", 0.25))
            if float(dict(needs.get("needs", {})).get(need_key, 1.0)) <= threshold:
                return True
        return False

    def _plan_needs(self, context: PlannerContext, goal: Goal) -> list[PlanProposal]:
        goal_kind = goal.kind.lower()
        if goal_kind == "sleep":
            request = self._request(context, goal, "Sleep")
            return [self._build_plan(context, goal, [request], confidence=0.92, required_resources={})]
        if goal_kind in {"hunger", "thirst", "survival"}:
            actor = _entity_state(context, goal.entity_id)
            if actor is None:
                return []
            inventory = _component_state(actor, "InventoryComponent") or {}
            items = [dict(item) for item in inventory.get("items", ())]
            need_action = "Eat" if goal_kind != "thirst" else "Drink"
            resource_name = "food" if need_action == "Eat" else "water"
            if any(str(item.get("identifier")) == resource_name and float(item.get("quantity", 0.0)) > 0 for item in items):
                return [self._build_plan(context, goal, [self._request(context, goal, need_action)], confidence=0.95, required_resources={resource_name: 1.0})]
            locate = self._locate_resource(context, resource_name)
            if locate is None:
                return []
            walk = self._request(context, goal, "Walk", destination_room=locate["room"])
            pickup = self._request(context, goal, "PickUp", target_id=locate["entity_id"])
            consume = self._request(context, goal, need_action, quantity=1)
            return [self._build_plan(context, goal, [walk, pickup, consume], confidence=0.8, required_resources={resource_name: 1.0})]
        return []

    def _plan_movement(self, context: PlannerContext, goal: Goal) -> list[PlanProposal]:
        destination = goal.target_state.get("room") or goal.metadata.get("destination_room")
        if destination is None:
            return []
        walk = self._request(context, goal, "Walk", destination_room=str(destination))
        return [self._build_plan(context, goal, [walk], confidence=0.9, required_resources={"energy": 1.0})]

    def _plan_talk(self, context: PlannerContext, goal: Goal) -> list[PlanProposal]:
        target_id = goal.target_state.get("target_id") or goal.metadata.get("target_id")
        if target_id is None:
            return []
        request = self._request(context, goal, "Talk", target_id=EntityId.from_uuid(target_id) if not isinstance(target_id, EntityId) else target_id)
        return [self._build_plan(context, goal, [request], confidence=0.9)]

    def _plan_follow(self, context: PlannerContext, goal: Goal) -> list[PlanProposal]:
        target_id = goal.target_state.get("target_id") or goal.metadata.get("target_id")
        if target_id is None:
            return []
        request = self._request(context, goal, "Follow", target_id=EntityId.from_uuid(target_id) if not isinstance(target_id, EntityId) else target_id)
        return [self._build_plan(context, goal, [request], confidence=0.88)]

    def _plan_acquire_item(self, context: PlannerContext, goal: Goal) -> list[PlanProposal]:
        target = self._resolve_item(context, goal)
        if target is None:
            return []
        actor = _entity_state(context, goal.entity_id)
        if actor is None:
            return []
        actor_room = _room(actor)
        target_room = target["room"]
        if target_room is None or actor_room is None:
            return []
        if actor_room == target_room:
            requests = [self._request(context, goal, "PickUp", target_id=target["entity_id"])]
            return [self._build_plan(context, goal, requests, confidence=0.9, required_resources={})]
        walk = self._request(context, goal, "Walk", destination_room=target_room)
        pickup = self._request(context, goal, "PickUp", target_id=target["entity_id"])
        return [self._build_plan(context, goal, [walk, pickup], confidence=0.84, required_resources={"energy": 1.0})]

    def _plan_open_door(self, context: PlannerContext, goal: Goal) -> list[PlanProposal]:
        target_id = goal.target_state.get("target_id") or goal.metadata.get("target_id")
        if target_id is None:
            return []
        entity_id = EntityId.from_uuid(target_id) if not isinstance(target_id, EntityId) else target_id
        target = _entity_state(context, entity_id)
        if target is None:
            return []
        actor = _entity_state(context, goal.entity_id)
        if actor is None:
            return []
        actor_room = _room(actor)
        target_room = _room(target)
        if actor_room != target_room and target_room is not None:
            walk = self._request(context, goal, "Walk", destination_room=target_room)
            open_request = self._request(context, goal, "Open", target_id=entity_id)
            return [self._build_plan(context, goal, [walk, open_request], confidence=0.82)]
        return [self._build_plan(context, goal, [self._request(context, goal, "Open", target_id=entity_id)], confidence=0.92)]

    def _plan_explore(self, context: PlannerContext, goal: Goal) -> list[PlanProposal]:
        actor = _entity_state(context, goal.entity_id)
        if actor is None:
            return []
        current_room = _room(actor)
        rooms = sorted(
            {
                str(entity.get("display_name"))
                for entity in dict(context.snapshot.state.get("entities", {})).values()
                if str(entity.get("type")) == "room"
            }
        )
        candidates = [room for room in rooms if room != current_room]
        if not candidates:
            return []
        destination = candidates[0]
        return [self._build_plan(context, goal, [self._request(context, goal, "Walk", destination_room=destination)], confidence=0.7)]

    def _plan_custom(self, context: PlannerContext, goal: Goal) -> list[PlanProposal]:
        actions = goal.metadata.get("actions") or goal.target_state.get("actions")
        if not actions:
            return []
        requests: list[ActionRequest] = []
        for index, action in enumerate(actions):
            payload = dict(action)
            requests.append(
                ActionRequest(
                    actor_id=goal.entity_id,
                    action=str(payload.get("action")),
                    target_id=payload.get("target_id"),
                    item_id=payload.get("item_id"),
                    destination_room=payload.get("destination_room"),
                    quantity=payload.get("quantity"),
                    parameters=dict(payload.get("parameters", {})),
                    priority=int(payload.get("priority", goal.priority)),
                    correlation_id=str(payload.get("correlation_id", f"{goal.goal_id}:{index}")),
                    metadata=dict(payload.get("metadata", {})),
                )
            )
        return [self._build_plan(context, goal, requests, confidence=0.75)]

    def _locate_resource(self, context: PlannerContext, resource_name: str) -> Mapping[str, Any] | None:
        for entity in dict(context.snapshot.state.get("entities", {})).values():
            inventory = _component_state(entity, "InventoryComponent") or {}
            for item in inventory.get("items", ()):
                if str(item.get("identifier")) == resource_name and float(item.get("quantity", 0.0)) > 0:
                    return {"entity_id": EntityId.from_uuid(entity["entity_id"]), "room": _room(entity), "item": dict(item)}
        assets = context.world_memory.asset_memory.search(text=resource_name)
        for asset in assets:
            if asset.entity_id is not None:
                entity_state = _entity_state(context, asset.entity_id)
                if entity_state is not None:
                    return {"entity_id": asset.entity_id, "room": _room(entity_state), "item": {"identifier": resource_name, "quantity": 1.0}}
        return None

    def _resolve_item(self, context: PlannerContext, goal: Goal) -> Mapping[str, Any] | None:
        if "asset_id" in goal.target_state:
            asset = context.world_memory.asset_memory.lookup(goal.target_state["asset_id"])
            if asset is not None and asset.entity_id is not None:
                entity_state = _entity_state(context, asset.entity_id)
                if entity_state is not None:
                    return {"entity_id": asset.entity_id, "room": _room(entity_state), "asset": asset}
        if "entity_id" in goal.target_state:
            entity_id = goal.target_state["entity_id"]
            if not isinstance(entity_id, EntityId):
                entity_id = EntityId.from_uuid(entity_id)
            entity_state = _entity_state(context, entity_id)
            if entity_state is not None:
                return {"entity_id": entity_id, "room": _room(entity_state), "asset": None}
        item_name = goal.target_state.get("item_name") or goal.metadata.get("item_name") or goal.subject
        for entity in dict(context.snapshot.state.get("entities", {})).values():
            if str(entity.get("display_name")) == str(item_name) or str(entity.get("type")) == str(item_name).lower():
                return {"entity_id": EntityId.from_uuid(entity["entity_id"]), "room": _room(entity), "asset": None}
        return None

    def _request(
        self,
        context: PlannerContext,
        goal: Goal,
        action: str,
        *,
        target_id: EntityId | None = None,
        item_id: EntityId | None = None,
        destination_room: str | None = None,
        quantity: float | None = None,
        index: int = 0,
        extra_parameters: Mapping[str, Any] | None = None,
        extra_metadata: Mapping[str, Any] | None = None,
    ) -> ActionRequest:
        correlation_id = _deterministic_id(context.world_id, goal.goal_id, action, index, destination_room, None if target_id is None else target_id.value, None if item_id is None else item_id.value)
        params = {"goal_id": goal.goal_id, "goal_kind": goal.kind}
        if extra_parameters:
            params.update(extra_parameters)
        meta = {"goal_id": goal.goal_id, "goal_kind": goal.kind}
        if extra_metadata:
            meta.update(extra_metadata)
        return ActionRequest(
            actor_id=goal.entity_id,
            action=action,
            target_id=target_id,
            item_id=item_id,
            destination_room=destination_room,
            quantity=quantity,
            priority=goal.priority,
            correlation_id=correlation_id,
            parameters=params,
            metadata=meta,
        )

    def _build_plan(
        self,
        context: PlannerContext,
        goal: Goal,
        action_requests: Sequence[ActionRequest],
        *,
        confidence: float,
        required_resources: Mapping[str, float] | None = None,
    ) -> PlanProposal:
        requests = tuple(action_requests)
        dependencies = tuple(request.correlation_id for request in requests[:-1])
        cost = sum(_ACTION_COSTS.get(request.action, 1.0) for request in requests)
        duration = max(1, len(requests))
        plan_id = _deterministic_id(context.world_id, goal.goal_id, context.current_tick.value, goal.priority, [request.action for request in requests])
        return PlanProposal(
            plan_id=plan_id,
            goal_id=goal.goal_id,
            entity_id=goal.entity_id,
            priority=self._priority(goal, cost, context),
            estimated_cost=cost,
            estimated_duration=duration,
            action_requests=requests,
            dependencies=dependencies,
            required_resources={} if required_resources is None else dict(required_resources),
            confidence=confidence,
            creation_tick=context.current_tick_number,
            planning_revision=context.committed_revision,
            status="proposed",
            goal_subject=goal.subject,
            metadata={
                "goal_kind": goal.kind,
                "target_state": dict(goal.target_state),
                "estimated_start_tick": context.current_tick_number + 1,
                "estimated_end_tick": context.current_tick_number + duration,
            },
        )

    def _priority(self, goal: Goal, estimated_cost: float, context: PlannerContext) -> int:
        bias = {
            "survival": 10000,
            "hunger": 9000,
            "thirst": 8800,
            "sleep": 8400,
            "movement": 5000,
            "move": 5000,
            "conversation": 3600,
            "talk": 3600,
            "follow_target": 3400,
            "follow": 3400,
            "acquire_item": 3000,
            "acquire": 3000,
            "open_door": 2500,
            "open": 2500,
            "explore": 1200,
        }.get(goal.kind.lower().replace(" ", "_"), 1000)
        deadline_bonus = 0
        if goal.deadline_tick is not None:
            deadline_bonus = max(0, 1000 - max(0, goal.deadline_tick - context.current_tick_number))
        return int(goal.priority + bias + deadline_bonus - estimated_cost * 10)

    def _plan_agriculture(self, context: PlannerContext, goal: Goal, default_action: str) -> list[PlanProposal]:
        field_id = goal.target_state.get("field_id") or goal.metadata.get("field_id") or "field_1"
        crop_type = goal.metadata.get("crop_type", "Wheat")
        action_name = str(goal.target_state.get("action") or default_action)
        req = self._request(
            context, goal, action_name, index=0,
            extra_parameters={"field_id": field_id, "crop_type": crop_type},
            extra_metadata={"field_id": field_id, "crop_type": crop_type},
        )
        return [self._build_plan(context, goal, [req], confidence=0.8)]
    def _plan_economy(self, context: PlannerContext, goal: Goal, default_action: str) -> list[PlanProposal]:
        recipe_name = goal.target_state.get("recipe_name") or goal.metadata.get("recipe_name") or "wheat_to_flour"
        action_name = str(goal.target_state.get("action") or default_action)
        req = self._request(
            context, goal, action_name, index=0,
            extra_parameters={"recipe_name": recipe_name},
            extra_metadata={"recipe_name": recipe_name},
        )
        return [self._build_plan(context, goal, [req], confidence=0.8)]
    def _plan_relationship(self, context: PlannerContext, goal: Goal) -> list[PlanProposal]:
        target_id = goal.target_state.get("target_id") or goal.metadata.get("target_id") or "Joren"
        action_name = str(goal.target_state.get("action") or "Talk")
        target_id_ent = _resolve_target_id(context, target_id)
        req = self._request(
            context, goal, action_name, index=0,
            target_id=target_id_ent,
            extra_parameters={"target_id": target_id},
            extra_metadata={"target_id": target_id},
        )
        return [self._build_plan(context, goal, [req], confidence=0.9)]



