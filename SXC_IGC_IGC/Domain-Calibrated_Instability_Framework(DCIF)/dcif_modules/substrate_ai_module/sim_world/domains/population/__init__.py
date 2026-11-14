from __future__ import annotations

from typing import Any, Dict

from ...core.contracts import TransitionProposal
from ...core.ids import EntityId
from ...simulation.simulation_engine import SimulationEngine
from ...simulation.simulation_context import SimulationContext

VILLAGER_SPECS = [
    ("Mira", "farmer", "house_1", "farm"),
    ("Joren", "blacksmith", "house_1", "blacksmith"),
    ("Lina", "innkeeper", "house_2", "tavern"),
    ("Tomas", "merchant", "house_2", "village_square"),
    ("Edda", "woodcutter", "house_3", "forest"),
    ("Pell", "child", "house_3", "village_square"),
    ("Hara", "elder", "house_4", "village_square"),
    ("Niko", "hunter", "house_4", "forest"),
    ("Sera", "traveler", "house_4", "tavern"),
    ("Oren", "village leader", "house_4", "village_square"),
]



def register(engine: SimulationEngine) -> None:
    engine.register_domain("population", lambda engine, context: (apply(context),))


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


def initialize_valley_population(kernel: Any) -> dict[str, Any]:
    registry = kernel.entity_registry
    entities = {}

    from ...entities.components import (
        HealthComponent,
        InventoryComponent,
        NeedsComponent,
        TransformComponent,
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
            from ...entities.components import ResourceDescriptor
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


def generate_daily_life_goals(kernel: Any) -> list[Any]:
    hour = kernel.current_tick_number % 24
    manager = kernel.planner_engine.goal_manager
    goals = []

    human_entities = [e for e in kernel.entity_registry.list_entities() if e.type == "human"]

    for human in human_entities:
        home = human.metadata.get("home", "house_1")
        workplace = human.metadata.get("workplace", "village_square")

        if hour == 6:
            # Morning: Wake and walk to workplace
            goal = manager.create_goal(
                subject=f"{human.display_name} go to work",
                kind="movement",
                entity_id=human.entity_id,
                target_state={"room": workplace},
                priority=10,
                created_tick=kernel.current_tick_number,
            )
            goals.append(goal)
        elif hour == 12:
            # Afternoon: Work at workplace
            goal = manager.create_goal(
                subject=f"{human.display_name} work",
                kind="custom",
                entity_id=human.entity_id,
                target_state={"actions": [{"action": "Stand", "metadata": {"activity": "working"}}]},
                priority=8,
                created_tick=kernel.current_tick_number,
            )
            goals.append(goal)
        elif hour == 18:
            # Evening: Return home
            goal = manager.create_goal(
                subject=f"{human.display_name} return home",
                kind="movement",
                entity_id=human.entity_id,
                target_state={"room": home},
                priority=10,
                created_tick=kernel.current_tick_number,
            )
            goals.append(goal)
        elif hour == 22:
            # Night: Sleep at home
            goal = manager.create_goal(
                subject=f"{human.display_name} sleep",
                kind="sleep",
                entity_id=human.entity_id,
                target_state={"status": "sleeping"},
                priority=12,
                created_tick=kernel.current_tick_number,
            )
            goals.append(goal)

    return goals


def run_daily_life_step(kernel: Any) -> Any:
    goals = generate_daily_life_goals(kernel)
    if goals:
        plans = kernel.plan(goals=goals)
        kernel.schedule_plans(plans)
    return kernel.advance_tick()


def apply(context: SimulationContext) -> TransitionProposal:
    """
    Population domain: Manage villager lifecycle, decision-making, and social interactions.
    Domain-locked: VillagerComponent, PerceptionComponent, GoalComponent
    """
    world_state = context.world_state
    tick_context = context.tick_context
    state_revision = context.committed_revision
    
    # Extract entities (domain-locked: only VillagerComponent, PerceptionComponent, GoalComponent)
    entities = dict(world_state.get("entities", {}))
    
    # Extract population-specific data
    population_data = dict(world_state.get("population", {}))
    villagers_data = list(population_data.get("villagers", []))
    goals_data = dict(world_state.get("goals", {}))
    perceptions_data = dict(world_state.get("perceptions", {}))
    
    # Clean up completed goals (domain-locked: GoalComponent)
    cleaned_goals = {}
    for goal_id, goal in goals_data.items():
        if goal.get("status") != "completed":
            cleaned_goals[goal_id] = goal
    
    # Read physics goal completion signals
    completion_signals = list(world_state.get("physics_goal_completion_signals", []))
    
    # Process completed movement goals to generate follow-up harvest goals
    for goal_id in completion_signals:
        # Get the goal data to check if it was a movement to farm for food seeking
        completed_goal = goals_data.get(goal_id, {})
        if completed_goal.get("kind") == "movement":
            target_state = completed_goal.get("target_state", {})
            if target_state.get("room") == "farm":
                # This was a movement to farm - check if it was for food seeking
                reason = completed_goal.get("reason", "")
                if "food" in reason.lower() or "hunger" in reason.lower():
                    # Extract entity_id from the goal
                    entity_id = completed_goal.get("entity_id")
                    if entity_id:
                        # Generate HarvestField goal
                        cleaned_goals[f"harvest_{tick_context.tick_id}_{entity_id}"] = {
                            "kind": "harvestfield",
                            "entity_id": entity_id,
                            "target_state": {"field_id": "farm", "action": "HarvestCrop"},
                            "priority": 20,
                            "status": "pending",
                            "reason": "movement_to_farm_completed_harvest_food"
                        }
    
    # Build entity patches (domain-locked: VillagerComponent, PerceptionComponent, GoalComponent)
    entity_patches = {}
    
    # Build new goals and actions
    new_goals = {}
    new_actions = []
    entity_perceptions = {}
    
    # Process each entity for decision-making
    villager_count = 0
    for entity_id, entity_data in entities.items():
        # Skip if not a villager - IDENTIFY BY ENTITY TYPE
        entity_type = str(entity_data.get("type"))
        if entity_type != "human":
            continue
        
        villager_count += 1
        
        # Extract villager properties - SIMPLIFIED IDENTIFICATION
        name = entity_data.get("name", "Unknown")
        age = 25  # Default age
        health = 100  # Default health
        mood = 0.5  # Default mood
        
        # Extract position from canonical TransformComponent
        transform_comp = dict(entity_data.get("components", {}).get("TransformComponent", {}))
        # TransformComponent stores room as a separate field, not inside position dict
        current_room = transform_comp.get("room", "home")
        
        # Extract needs - READ FROM CANONICAL ENTITIES
        needs_comp = dict(entity_data.get("components", {}).get("NeedsComponent", {}))
        canonical_needs = dict(needs_comp.get("needs", {}))
        hunger = canonical_needs.get("hunger", 0.5) * 100  # Convert to percentage
        energy = canonical_needs.get("energy", 0.8) * 100
        social = canonical_needs.get("social", 0.6) * 100
        
        # Extract inventory - READ FROM CANONICAL ENTITIES
        inventory_comp = dict(entity_data.get("components", {}).get("InventoryComponent", {}))
        items = list(inventory_comp.get("items", []))
        has_food = any(item.get("identifier") == "food" for item in items if isinstance(item, dict)) or \
                 any(item.identifier == "food" for item in items if hasattr(item, 'identifier'))
        
        # Build perception object for decision-making
        hunger_from_needs = canonical_needs.get("hunger", 0.5) * 100
        perception_object = {
            "hunger": hunger_from_needs,
            "has_food": has_food,
            "current_room": current_room
        }
        entity_perceptions[entity_id] = perception_object
        
        # Threshold check for decision making
        if hunger >= 50:  # High hunger threshold
            if has_food:
                # Eat action if hungry and has food
                new_actions.append({
                    "entity_id": entity_id,
                    "action": "eat",
                    "item_id": "food",
                    "quantity": 1,
                    "reason": "high_hunger_self_treatment"
                })
            elif current_room == "farm":
                # Harvest action if at farm and hungry
                new_actions.append({
                    "entity_id": entity_id,
                    "action": "harvest",
                    "target_id": "farm",
                    "item_id": "wheat",
                    "quantity": 1,
                    "reason": "high_hunger_food_acquisition"
                })
            else:
                # Move to farm if hungry and not at farm
                new_goals[f"seek_food_{tick_context.tick_id}_{entity_id}"] = {
                    "kind": "movement",
                    "entity_id": entity_id,
                    "target_state": {"room": "farm"},
                    "priority": 15,
                    "status": "pending",
                    "reason": "high_hunger_food_search"
                }
        elif get_current_hour(world_state) == 6 and current_room != "farm":
            # Time-based work schedule (fallback)
            new_goals[f"work_schedule_{tick_context.tick_id}_{entity_id}"] = {
                "kind": "movement",
                "entity_id": entity_id,
                "target_state": {"room": "farm"},
                "priority": 10,
                "status": "pending",
                "reason": "daily_work_schedule"
            }
    
    # Return domain-locked transition proposal
    return TransitionProposal(
        world_id=context.world_id,
        tick_id=context.tick_context.tick_id,
        state_revision=state_revision,
        correlation_id=context.tick_context.correlation_id,
        subject="domain.population",
        patch={
            "population": {"villagers": villagers_data},
            "goals": {**cleaned_goals, **new_goals},
            "perceptions": entity_perceptions,  # Store perceptions for memory/future decisions
            "pending_actions": new_actions,  # Actions for world mutation
            # ACTION SIGNAL BRIDGE: Convert pending_actions to domain-specific signal namespaces
            "action_harvest_signals": [action for action in new_actions if action.get("action") == "harvest"],
            "action_eat_signals": [action for action in new_actions if action.get("action") == "eat"]
        },
        description="population domain with action causality loop",
        metadata={"domain": "population", "villager_count": len(villagers_data), "goals_count": len(new_goals), "perceptions_count": len(entity_perceptions), "actions_count": len(new_actions)},
    )

# Helper function to get current hour from world state
def get_current_hour(world_state: Dict[str, Any]) -> int:
    """Extract current hour from world state for time-based decision making."""
    # Default to hour 6 (morning) if not available
    return world_state.get("world", {}).get("time", {}).get("hour", 6)


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
        elif get_current_hour(kernel.current_state) == 6 and current_room != "farm":
            # Time-based work schedule (fallback)
            goals.append(
                manager.create_goal(
                    subject=f"{metadata.get('name', 'Villager')} go to work",
                    kind="movement",
                    entity_id=entity_id,
                    target_state={"room": "farm"},
                    priority=10,
                    created_tick=kernel.current_tick_number,
                    metadata={"reason": "daily_work_schedule"},
                )
            )

    return goals
