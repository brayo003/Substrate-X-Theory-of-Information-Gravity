from __future__ import annotations

from typing import Any, Mapping

from ...core.contracts import TransitionProposal
from ...core.ids import EntityId
from ...simulation.simulation_engine import SimulationEngine
from .needs_rules import evaluate_villager_needs


def register(engine: SimulationEngine) -> None:
    engine.register_domain("needs", lambda engine, context: (apply(context),))


def apply(context: Any) -> TransitionProposal:
    world_state = context.world_state
    weather_info = dict(world_state.get("weather", {}))
    weather = str(weather_info.get("state", "sunny"))
    entities = dict(world_state.get("entities", {}))

    entity_patches: dict[str, Any] = {}
    all_events: list[dict[str, Any]] = []

    for entity_id_str, entity_data in sorted(entities.items()):
        if str(entity_data.get("type")) != "human":
            continue

        components = dict(entity_data.get("components", {}))
        metadata = dict(entity_data.get("metadata", {}))

        transform = dict(components.get("TransformComponent", {}))
        location = transform.get("room")

        needs_comp = dict(components.get("NeedsComponent", {}))
        current_needs = dict(needs_comp.get("needs", {}))

        occupation = str(metadata.get("occupation", "villager"))
        status = metadata.get("status")
        last_action = metadata.get("last_action")

        updated_needs, events = evaluate_villager_needs(
            villager_id=entity_id_str,
            occupation=occupation,
            current_needs=current_needs,
            location=location,
            weather=weather,
            status=status,
            last_action=last_action,
        )

        # WAKE MECHANISM: a sleeping villager whose energy has recovered
        # returns to an awake state. This is the companion to the Sleep goal
        # so villagers are not permanently frozen in a sleep status (the
        # second driver of static equilibrium).
        new_status = status
        if status == "sleeping" and float(updated_needs.get("energy", 1.0)) >= 0.5:
            new_status = "awake"
        elif status in (None, "awake") and float(updated_needs.get("energy", 1.0)) < 0.3:
            new_status = "sleeping"

        meta_patch: dict[str, Any] = {}
        if new_status != status:
            meta_patch["status"] = new_status
            if new_status == "awake":
                meta_patch["last_action"] = "Wake"

        entity_patch: dict[str, Any] = {
            "components": {
                "NeedsComponent": {
                    "needs": updated_needs,
                    "component_type": "NeedsComponent",
                }
            }
        }
        if meta_patch:
            entity_patch["metadata"] = meta_patch
        entity_patches[entity_id_str] = entity_patch
        all_events.extend(event.to_dict() for event in events)

    return TransitionProposal(
        world_id=context.world_id,
        tick_id=context.tick_context.tick_id,
        state_revision=context.committed_revision,
        correlation_id=context.tick_context.correlation_id,
        subject="domain.needs",
        patch={"entities": entity_patches},
        description="needs domain update",
        metadata={"domain": "needs", "events": all_events},
    )


def _has_goal(manager, eid, kind: str, subject_phrase: str = "") -> bool:
    """Check if entity already has an outstanding goal of this type (idempotent).

    Without this check, every tick re-creates goals (hunger > 0.6 → Eat goal,
    thirst > 0.6 → Drink, energy < 0.3 → Sleep) for ALL villagers, and each
    old goal stays outstanding forever → all goals get replanned every tick →
    degenerate Eat/Drink/Sleep loops that freeze the simulation.

    Matches on `kind` and, when a phrase is supplied, on the phrase occurring
    in the subject (subject is "{name} {verb} {noun}", e.g. "Aria drink water",
    so the phrase is matched by containment, not startswith).
    """
    for goal in manager.list_goals(include_terminal=False):
        if goal.kind != kind:
            continue
        if goal.entity_id is not None and goal.entity_id == eid:
            if not subject_phrase or (subject_phrase in goal.subject):
                return True
    return False


def generate_needs_driven_goals(kernel: Any) -> list[Any]:
    manager = kernel.planner_engine.goal_manager
    goals = []

    entities = kernel.current_state.get("entities", {})
    for entity_id_str, entity_data in sorted(entities.items()):
        if str(entity_data.get("type")) != "human":
            continue

        entity_id = EntityId.from_uuid(entity_id_str)
        components = dict(entity_data.get("components", {}))
        metadata = dict(entity_data.get("metadata", {}))

        needs = dict(dict(components.get("NeedsComponent", {})).get("needs", {}))
        home = str(metadata.get("home", "house_1"))
        workplace = str(metadata.get("workplace", "farm"))

        hunger = float(needs.get("hunger", 0.0))
        thirst = float(needs.get("thirst", 0.0))
        energy = float(needs.get("energy", 1.0))
        warmth = float(needs.get("warmth", 1.0))
        social = float(needs.get("social", 1.0))

        # Critical hunger (> 0.6): High priority Eat goal
        if hunger > 0.6:
            if not _has_goal(manager, entity_id, "hunger", "eat"):
                goals.append(
                    manager.create_goal(
                        subject=f"{metadata.get('name', 'Villager')} eat food",
                        kind="hunger",
                        entity_id=entity_id,
                        target_state={"threshold": 0.25},
                        priority=100,
                        created_tick=kernel.current_tick_number,
                    )
                )

        # Critical thirst (> 0.6): High priority Drink goal
        if thirst > 0.6:
            if not _has_goal(manager, entity_id, "thirst", "drink"):
                goals.append(
                    manager.create_goal(
                        subject=f"{metadata.get('name', 'Villager')} drink water",
                        kind="thirst",
                        entity_id=entity_id,
                        target_state={"threshold": 0.25},
                        priority=95,
                        created_tick=kernel.current_tick_number,
                    )
                )

        # Critical energy (< 0.3): High priority Sleep goal
        if energy < 0.3:
            if not _has_goal(manager, entity_id, "sleep", "sleep"):
                goals.append(
                    manager.create_goal(
                        subject=f"{metadata.get('name', 'Villager')} sleep rest",
                        kind="sleep",
                        entity_id=entity_id,
                        target_state={"status": "sleeping"},
                        priority=90,
                        created_tick=kernel.current_tick_number,
                    )
                )

        # Cold (< 0.3): Seek shelter goal
        if warmth < 0.3:
            if not _has_goal(manager, entity_id, "movement", "seek shelter"):
                goals.append(
                    manager.create_goal(
                        subject=f"{metadata.get('name', 'Villager')} seek shelter",
                        kind="movement",
                        entity_id=entity_id,
                        target_state={"room": home},
                        priority=85,
                        created_tick=kernel.current_tick_number,
                    )
                )

        # Social (< 0.3): Socialize goal with target villager
        if social < 0.3:
            if not _has_goal(manager, entity_id, "conversation", "socialize"):
                other_entities = [e_id for e_id in entities if e_id != entity_id_str and entities[e_id].get("type") == "human"]
                target_id = EntityId.from_uuid(other_entities[0]) if other_entities else entity_id
                goals.append(
                    manager.create_goal(
                        subject=f"{metadata.get('name', 'Villager')} socialize",
                        kind="conversation",
                        entity_id=entity_id,
                        target_state={"target_id": target_id, "room": "tavern"},
                        priority=70,
                        created_tick=kernel.current_tick_number,
                    )
                )

    return goals



def run_needs_driven_step(kernel: Any) -> Any:
    goals = generate_needs_driven_goals(kernel)
    if goals:
        plans = kernel.plan(goals=goals)
        kernel.schedule_plans(plans)
    return kernel.advance_tick()
