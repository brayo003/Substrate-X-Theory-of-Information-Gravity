from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Mapping, Sequence

from ..simulation.action_validator import DEFAULT_ACTIONS
from ..entities.components import component_key
from ..core.ids import EntityId
from .planner_context import Goal, PlanProposal, PlannerContext


@dataclass(frozen=True, slots=True)
class PlanValidationFailure:
    code: str
    message: str
    plan_id: str
    goal_id: str
    entity_id: EntityId | None = None
    step_index: int | None = None
    details: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        object.__setattr__(self, "code", str(self.code))
        object.__setattr__(self, "message", str(self.message))
        object.__setattr__(self, "plan_id", str(self.plan_id))
        object.__setattr__(self, "goal_id", str(self.goal_id))
        object.__setattr__(self, "details", dict(self.details))


@dataclass(frozen=True, slots=True)
class PlanValidationResult:
    valid: bool
    plan: PlanProposal
    failures: tuple[PlanValidationFailure, ...] = field(default_factory=tuple)
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        object.__setattr__(self, "failures", tuple(self.failures))
        object.__setattr__(self, "metadata", dict(self.metadata))


def _entity_key(entity_id: EntityId) -> str:
    return str(entity_id.value)


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


@dataclass
class PlanValidator:
    def validate(self, context: PlannerContext, plan: PlanProposal, goal: Goal | None = None) -> PlanValidationResult:
        goal = goal or next((item for item in context.outstanding_goals if item.goal_id == plan.goal_id), None)
        failures: list[PlanValidationFailure] = []
        actor = _entity_state(context, plan.entity_id)
        if actor is None:
            failures.append(PlanValidationFailure("entity_missing", "actor does not exist", plan.plan_id, plan.goal_id, plan.entity_id))
            return PlanValidationResult(False, plan, tuple(failures))
        if not bool(actor.get("alive", True)):
            failures.append(PlanValidationFailure("entity_dead", "dead entities cannot plan", plan.plan_id, plan.goal_id, plan.entity_id))
        if not bool(actor.get("enabled", True)):
            failures.append(PlanValidationFailure("entity_disabled", "disabled entities cannot plan", plan.plan_id, plan.goal_id, plan.entity_id))
        if not plan.action_requests:
            failures.append(PlanValidationFailure("empty_plan", "plan must contain at least one action request", plan.plan_id, plan.goal_id, plan.entity_id))

        actor_actions = {
            str(action.get("identifier"))
            for action in actor.get("actions", ())
            if isinstance(action, Mapping)
        }
        seen_actions: list[str] = []
        for index, request in enumerate(plan.action_requests):
            if request.actor_id != plan.entity_id:
                failures.append(PlanValidationFailure("actor_mismatch", "action request actor does not match plan entity", plan.plan_id, plan.goal_id, plan.entity_id, index))
            if request.action not in DEFAULT_ACTIONS:
                if request.action not in actor_actions:
                    failures.append(
                        PlanValidationFailure(
                            "capability_missing",
                            "actor cannot perform requested action",
                            plan.plan_id,
                            plan.goal_id,
                            plan.entity_id,
                            index,
                            {"action": request.action},
                        )
                    )
            if request.action in seen_actions and request.action in {"Walk", "PickUp", "Open", "Talk", "Follow"}:
                failures.append(PlanValidationFailure("duplicate_action", "duplicate action request in plan", plan.plan_id, plan.goal_id, plan.entity_id, index, {"action": request.action}))
            seen_actions.append(request.action)
            if request.action == "Walk":
                destination = request.destination_room
                if destination is None and request.target_id is not None:
                    target = _entity_state(context, request.target_id)
                    destination = _room(target)
                if destination is None:
                    failures.append(PlanValidationFailure("missing_destination", "walk request requires a destination", plan.plan_id, plan.goal_id, plan.entity_id, index))
                elif _room(actor) == destination:
                    failures.append(PlanValidationFailure("no_op", "walk destination matches current room", plan.plan_id, plan.goal_id, plan.entity_id, index))
            elif request.action == "PickUp":
                target = _entity_state(context, request.target_id)
                if target is None:
                    failures.append(PlanValidationFailure("target_missing", "pickup target does not exist", plan.plan_id, plan.goal_id, plan.entity_id, index))
                elif _room(target) != _room(actor):
                    failures.append(PlanValidationFailure("distance", "pickup target is not reachable", plan.plan_id, plan.goal_id, plan.entity_id, index))
            elif request.action == "Drop":
                item = _entity_state(context, request.item_id or request.target_id)
                if item is None:
                    failures.append(PlanValidationFailure("target_missing", "drop target does not exist", plan.plan_id, plan.goal_id, plan.entity_id, index))
            elif request.action in {"Open", "Close", "Talk", "Follow"}:
                target = _entity_state(context, request.target_id or request.item_id)
                if target is None:
                    failures.append(PlanValidationFailure("target_missing", f"{request.action} target does not exist", plan.plan_id, plan.goal_id, plan.entity_id, index))
                elif request.action in {"Open", "Close", "Talk"} and _room(target) != _room(actor):
                    failures.append(PlanValidationFailure("distance", f"{request.action} target is not in the same room", plan.plan_id, plan.goal_id, plan.entity_id, index))
            elif request.action == "Eat":
                inventory = _component_state(actor, "InventoryComponent") or {}
                items = [dict(item) for item in inventory.get("items", ())]
                if not any(str(item.get("identifier")) == "food" and float(item.get("quantity", 0.0)) > 0 for item in items):
                    failures.append(PlanValidationFailure("resource_missing", "actor has no food available", plan.plan_id, plan.goal_id, plan.entity_id, index))
            elif request.action == "Drink":
                inventory = _component_state(actor, "InventoryComponent") or {}
                items = [dict(item) for item in inventory.get("items", ())]
                if not any(str(item.get("identifier")) == "water" and float(item.get("quantity", 0.0)) > 0 for item in items):
                    failures.append(PlanValidationFailure("resource_missing", "actor has no water available", plan.plan_id, plan.goal_id, plan.entity_id, index))

        for dependency in plan.dependencies:
            if dependency not in {request.correlation_id for request in plan.action_requests}:
                failures.append(PlanValidationFailure("dependency_missing", "dependency is not present in the plan", plan.plan_id, plan.goal_id, plan.entity_id, details={"dependency": dependency}))

        if goal is not None:
            knowledge_query = goal.metadata.get("knowledge_query") or plan.metadata.get("knowledge_query")
            if knowledge_query is not None and not context.world_memory.knowledge_memory.query(str(knowledge_query)):
                failures.append(PlanValidationFailure("knowledge_missing", "required knowledge is unavailable", plan.plan_id, plan.goal_id, plan.entity_id, details={"query": knowledge_query}))

        return PlanValidationResult(not failures, plan, tuple(failures))

    def validate_many(self, context: PlannerContext, plans: Sequence[PlanProposal], goals: Sequence[Goal] | None = None) -> tuple[PlanValidationResult, ...]:
        goal_map = {goal.goal_id: goal for goal in (goals or context.outstanding_goals)}
        return tuple(self.validate(context, plan, goal_map.get(plan.goal_id)) for plan in plans)
