from __future__ import annotations

from typing import Any, Dict

from ...core.contracts import TransitionProposal
from ...core.ids import EntityId
from ...simulation.simulation_engine import SimulationEngine
from ...simulation.simulation_context import SimulationContext

VILLAGER_SPECS = [
    ("Aria", "farmer", "house_1", "farm"),
    ("Bram", "carpenter", "house_2", "workshop"),
    ("Cora", "healer", "house_3", "clinic"),
    ("Doran", "farmer", "house_1", "farm"),
    ("Elara", "merchant", "house_4", "market"),
    ("Finn", "carpenter", "house_2", "workshop"),
    ("Gwen", "farmer", "house_1", "farm"),
    ("Haldor", "blacksmith", "house_5", "forge"),
    ("Isla", "healer", "house_3", "clinic"),
    ("Joren", "merchant", "house_4", "market"),
]

def register(engine: SimulationEngine) -> None:
    engine.register_domain("population", lambda engine, context: (apply(context),))

def apply(context: SimulationContext) -> TransitionProposal:
    """
    Population domain: Manage villager lifecycle, decision-making, and social interactions.
    Domain-locked: VillagerComponent, PerceptionComponent, GoalComponent
    MINIMAL: Return empty patch to avoid hanging
    """
    return TransitionProposal(
        world_id=context.world_id,
        tick_id=context.tick_context.tick_id,
        state_revision=context.committed_revision,
        correlation_id=context.tick_context.correlation_id,
        subject="domain.population",
        patch={
            "population": {"villagers": []},
            "goals": {},
            "perceptions": {},
            "pending_actions": [],
            "action_harvest_signals": [],
            "action_eat_signals": []
        },
        description="population domain minimal",
        metadata={"domain": "population", "villager_count": 0, "goals_count": 0, "perceptions_count": 0, "actions_count": 0},
    )

# Helper function to get current hour from world state
def get_current_hour(world_state: Dict[str, Any]) -> int:
    """Extract current hour from world state for time-based decision making.

    The time domain (domains/time) writes world_state["time"]["hour"] (a
    top-level key per PROTOCOL.md §4); fall back to 6 only when truly absent.
    """
    return int(world_state.get("time", {}).get("hour", 6))


def generate_population_driven_goals(kernel: Any) -> list[Any]:
    """Generate goals from Population domain decisions via GoalManager."""
    manager = kernel.planner_engine.goal_manager
    goals = []

    entities = kernel.current_state.get("entities", {})
    for entity_id_str, entity_data in sorted(entities.items()):
        if str(entity_data.get("type")) != "human":
            continue

        entity_id = EntityId.from_uuid(entity_id_str)
        components = dict(entity_data.get("components", {}))
        metadata = dict(entity_data.get("metadata", {}))

        # Extract needs - READ FROM CANONICAL ENTITIES
        needs_comp = dict(components.get("NeedsComponent", {}))
        canonical_needs = dict(needs_comp.get("needs", {}))
        hunger = canonical_needs.get("hunger", 0.5) * 100  # Convert to percentage

        # Extract position from canonical TransformComponent
        transform_comp = dict(components.get("TransformComponent", {}))
        current_room = transform_comp.get("room", "home")

        # Extract inventory - READ FROM CANONICAL ENTITIES
        inventory_comp = dict(components.get("InventoryComponent", {}))
        items = list(inventory_comp.get("items", []))
        has_food = any(item.get("identifier") == "food" for item in items if isinstance(item, dict)) or \
                 any(item.identifier == "food" for item in items if hasattr(item, 'identifier'))

        # Threshold check for decision making
        if hunger >= 50:  # High hunger threshold
            if has_food:
                # Eat action if hungry and has food - no goal needed, direct action
                pass
            elif current_room == "farm":
                # Harvest action if at farm and hungry - no goal needed, direct action
                pass
            else:
                # Move to farm if hungry and not at farm - create movement goal
                if not manager.has_outstanding_goal(entity_id, "movement", "seek food"):
                    goals.append(
                        manager.create_goal(
                            subject=f"{metadata.get('name', 'Villager')} seek food",
                            kind="movement",
                            entity_id=entity_id,
                            target_state={"room": "farm"},
                            priority=15,
                            created_tick=kernel.current_tick_number,
                            metadata={"reason": "high_hunger_food_search"},
                        )
                    )
        elif get_current_hour(kernel.current_state) == 6:
            # Time-based work schedule: walk to the villager's OWN workplace
            # (metadata.workplace from VILLAGER_SPECS), not a hardcoded "farm".
            workplace = str(metadata.get("workplace", "farm"))
            if current_room != workplace:
                if not manager.has_outstanding_goal(entity_id, "movement", "go to work"):
                    goals.append(
                        manager.create_goal(
                            subject=f"{metadata.get('name', 'Villager')} go to work",
                            kind="movement",
                            entity_id=entity_id,
                            target_state={"room": workplace},
                            priority=10,
                            created_tick=kernel.current_tick_number,
                            metadata={"reason": "daily_work_schedule"},
                        )
                    )

    return goals

def initialize_valley_population(kernel: Any) -> dict[str, Any]:
    """Initialize valley population data and create canonical human entities."""
    registry = kernel.entity_registry
    entities = {}

    from ...entities.components import (
        HealthComponent,
        InventoryComponent,
        NeedsComponent,
        TransformComponent,
        ResourceDescriptor,
    )

    for index, (name, occupation, home, workplace) in enumerate(VILLAGER_SPECS, start=1):
        if not any(e.display_name == name for e in registry.list_entities()):
            ent = registry.create_entity(
                entity_type="human",
                display_name=name,
                created_tick=0,
                created_revision=None,
                metadata={
                    "villager_id": f"villager-{index}",
                    "name": name,
                    "occupation": occupation,
                    "home": home,
                    "workplace": workplace,
                    "status": "awake",
                },
            )
            ent.attach_component(TransformComponent(room=home), tick=0)
            ent.attach_component(NeedsComponent(needs={"hunger": 0.4, "thirst": 0.3, "energy": 0.8, "warmth": 1.0, "comfort": 0.8, "social": 0.7}), tick=0)
            ent.attach_component(HealthComponent(current=10.0, maximum=10.0, status="healthy"), tick=0)
            ent.attach_component(
                InventoryComponent(
                    items=(
                        ResourceDescriptor(identifier="food", quantity=10.0, properties={"fresh": True}),
                        ResourceDescriptor(identifier="water", quantity=10.0, properties={"cold": True}),
                    )
                ),
                tick=0,
            )
            entities[name] = ent
        else:
            for e in registry.list_entities():
                if e.display_name == name:
                    entities[name] = e

    return entities

def build_villagers() -> list[dict[str, Any]]:
    return [
        {
            "id": f"villager-{index}",
            "name": name,
            "home": home,
            "workplace": workplace,
            "occupation": occupation,
            "location": home,
            "inventory": [],
            "needs": {"hunger": 0.4, "thirst": 0.3, "energy": 0.8},
            "memory": [],
            "relationships": {},
            "goals": [],
            "schedule": {"day_phase": "morning"},
        }
        for index, (name, occupation, home, workplace) in enumerate(VILLAGER_SPECS, start=1)
    ]