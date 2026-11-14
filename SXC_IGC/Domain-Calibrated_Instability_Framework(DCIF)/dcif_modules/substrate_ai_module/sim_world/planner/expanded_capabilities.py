"""
Expanded Capability Registry

This module defines an expanded set of capabilities/primitives for autonomous behavior.
These are designed to be expressive, composable, and executable within the WorldKernel system.
"""

from ..planner.capability import Capability, CapabilityRegistry, Precondition, Effect
from typing import Any


def create_expanded_capability_registry() -> CapabilityRegistry:
    """Create a registry with expanded capabilities for autonomous behavior."""
    
    registry = CapabilityRegistry()
    
    # === MOVEMENT/NAVIGATION CAPABILITIES ===
    
    registry.register(Capability(
        name="MOVE",
        actor_types=("human",),
        required_components=("TransformComponent",),
        preconditions=(
            Precondition(type="valid_target_location"),
        ),
        effects=(
            Effect(type="location_change"),
        ),
        time_cost=1,
        energy_cost=0.1,
        action_name="move",
        metadata={"category": "navigation", "description": "Move to a target location"}
    ))
    
    registry.register(Capability(
        name="APPROACH",
        actor_types=("human",),
        required_components=("TransformComponent",),
        preconditions=(
            Precondition(type="entity_nearby"),
        ),
        effects=(
            Effect(type="location_change"),
            Effect(type="social_interaction"),
        ),
        time_cost=1,
        energy_cost=0.05,
        action_name="approach",
        metadata={"category": "navigation", "description": "Approach a nearby entity"}
    ))
    
    registry.register(Capability(
        name="RETREAT",
        actor_types=("human",),
        required_components=("TransformComponent",),
        preconditions=(
            Precondition(type="can_move"),
        ),
        effects=(
            Effect(type="location_change"),
        ),
        time_cost=1,
        energy_cost=0.2,
        action_name="retreat",
        metadata={"category": "navigation", "description": "Retreat from current location"}
    ))
    
    # === EXPLORATION CAPABILITIES ===
    
    registry.register(Capability(
        name="EXPLORE",
        actor_types=("human",),
        required_components=("TransformComponent",),
        preconditions=(
            Precondition(type="can_move"),
        ),
        effects=(
            Effect(type="location_change"),
            Effect(type="discovery"),
        ),
        time_cost=2,
        energy_cost=0.3,
        action_name="explore",
        metadata={"category": "exploration", "description": "Explore nearby area"}
    ))
    
    registry.register(Capability(
        name="SCOUT",
        actor_types=("human",),
        required_components=("TransformComponent",),
        preconditions=(
            Precondition(type="can_move"),
        ),
        effects=(
            Effect(type="location_change"),
            Effect(type="mapping"),
        ),
        time_cost=3,
        energy_cost=0.4,
        action_name="scout",
        metadata={"category": "exploration", "description": "Scout a wider area"}
    ))
    
    # === OBSERVATION CAPABILITIES ===
    
    registry.register(Capability(
        name="OBSERVE",
        actor_types=("human",),
        required_components=(),
        preconditions=(),
        effects=(
            Effect(type="observation_update"),
        ),
        time_cost=1,
        energy_cost=0.05,
        action_name="observe",
        metadata={"category": "observation", "description": "Observe current surroundings"}
    ))
    
    registry.register(Capability(
        name="INSPECT",
        actor_types=("human",),
        required_components=(),
        preconditions=(
            Precondition(type="target_available"),
        ),
        effects=(
            Effect(type="detailed_observation"),
        ),
        time_cost=2,
        energy_cost=0.1,
        action_name="inspect",
        metadata={"category": "observation", "description": "Inspect a specific target"}
    ))
    
    # === RESOURCE INTERACTION CAPABILITIES ===
    
    registry.register(Capability(
        name="GATHER",
        actor_types=("human",),
        required_components=("InventoryComponent",),
        preconditions=(
            Precondition(type="resource_available"),
        ),
        effects=(
            Effect(type="resource_gain"),
        ),
        time_cost=2,
        energy_cost=0.3,
        action_name="gather",
        metadata={"category": "resource", "description": "Gather available resources"}
    ))
    
    registry.register(Capability(
        name="COLLECT",
        actor_types=("human",),
        required_components=("InventoryComponent",),
        preconditions=(
            Precondition(type="item_available"),
        ),
        effects=(
            Effect(type="inventory_add"),
        ),
        time_cost=1,
        energy_cost=0.1,
        action_name="collect",
        metadata={"category": "resource", "description": "Collect specific items"}
    ))
    
    registry.register(Capability(
        name="DEPOSIT",
        actor_types=("human",),
        required_components=("InventoryComponent",),
        preconditions=(
            Precondition(type="has_item"),
        ),
        effects=(
            Effect(type="inventory_remove"),
            Effect(type="storage_add"),
        ),
        time_cost=1,
        energy_cost=0.1,
        action_name="deposit",
        metadata={"category": "resource", "description": "Deposit items to storage"}
    ))
    
    # === CONSUMPTION CAPABILITIES ===
    
    registry.register(Capability(
        name="CONSUME",
        actor_types=("human",),
        required_components=("InventoryComponent", "NeedsComponent"),
        preconditions=(
            Precondition(type="has_consumable"),
        ),
        effects=(
            Effect(type="inventory_remove"),
            Effect(type="need_satisfaction"),
        ),
        time_cost=1,
        energy_cost=0.05,
        action_name="consume",
        metadata={"category": "consumption", "description": "Consume food/drink"}
    ))
    
    registry.register(Capability(
        name="EAT",
        actor_types=("human",),
        required_components=("InventoryComponent", "NeedsComponent"),
        preconditions=(
            Precondition(type="has_food"),
        ),
        effects=(
            Effect(type="inventory_remove"),
            Effect(type="hunger_reduction"),
        ),
        time_cost=1,
        energy_cost=0.05,
        action_name="eat",
        metadata={"category": "consumption", "description": "Eat food to reduce hunger"}
    ))
    
    registry.register(Capability(
        name="DRINK",
        actor_types=("human",),
        required_components=("InventoryComponent", "NeedsComponent"),
        preconditions=(
            Precondition(type="has_liquid"),
        ),
        effects=(
            Effect(type="inventory_remove"),
            Effect(type="thirst_reduction"),
        ),
        time_cost=1,
        energy_cost=0.05,
        action_name="drink",
        metadata={"category": "consumption", "description": "Drink liquid to reduce thirst"}
    ))
    
    # === ENVIRONMENTAL INTERACTION CAPABILITIES ===
    
    registry.register(Capability(
        name="INTERACT",
        actor_types=("human",),
        required_components=(),
        preconditions=(
            Precondition(type="interactive_object"),
        ),
        effects=(
            Effect(type="object_activation"),
        ),
        time_cost=1,
        energy_cost=0.1,
        action_name="interact",
        metadata={"category": "environment", "description": "Interact with environmental object"}
    ))
    
    registry.register(Capability(
        name="ACTIVATE",
        actor_types=("human",),
        required_components=(),
        preconditions=(
            Precondition(type="activatable_object"),
        ),
        effects=(
            Effect(type="object_state_change"),
        ),
        time_cost=1,
        energy_cost=0.1,
        action_name="activate",
        metadata={"category": "environment", "description": "Activate an object"}
    ))
    
    registry.register(Capability(
        name="DEACTIVATE",
        actor_types=("human",),
        required_components=(),
        preconditions=(
            Precondition(type="active_object"),
        ),
        effects=(
            Effect(type="object_state_change"),
        ),
        time_cost=1,
        energy_cost=0.1,
        action_name="deactivate",
        metadata={"category": "environment", "description": "Deactivate an object"}
    ))
    
    # === MANIPULATION CAPABILITIES ===
    
    registry.register(Capability(
        name="MANIPULATE",
        actor_types=("human",),
        required_components=(),
        preconditions=(
            Precondition(type="manipulatable_object"),
        ),
        effects=(
            Effect(type="object_property_change"),
        ),
        time_cost=2,
        energy_cost=0.2,
        action_name="manipulate",
        metadata={"category": "manipulation", "description": "Manipulate object properties"}
    ))
    
    registry.register(Capability(
        name="MODIFY",
        actor_types=("human",),
        required_components=("InventoryComponent",),
        preconditions=(
            Precondition(type="has_tool"),
        ),
        effects=(
            Effect(type="object_transformation"),
        ),
        time_cost=3,
        energy_cost=0.3,
        action_name="modify",
        metadata={"category": "manipulation", "description": "Modify object using tools"}
    ))
    
    # === SEEK/AVOID CAPABILITIES ===
    
    registry.register(Capability(
        name="SEEK",
        actor_types=("human",),
        required_components=("TransformComponent",),
        preconditions=(
            Precondition(type="target_location_known"),
        ),
        effects=(
            Effect(type="location_change"),
        ),
        time_cost=2,
        energy_cost=0.2,
        action_name="seek",
        metadata={"category": "navigation", "description": "Seek specific target"}
    ))
    
    registry.register(Capability(
        name="AVOID",
        actor_types=("human",),
        required_components=("TransformComponent",),
        preconditions=(
            Precondition(type="threat_detected"),
        ),
        effects=(
            Effect(type="location_change"),
        ),
        time_cost=1,
        energy_cost=0.3,
        action_name="avoid",
        metadata={"category": "navigation", "description": "Avoid threat or danger"}
    ))
    
    # === MEMORY/ACCESS CAPABILITIES ===
    
    registry.register(Capability(
        name="RECALL",
        actor_types=("human",),
        required_components=(),
        preconditions=(),
        effects=(
            Effect(type="memory_access"),
        ),
        time_cost=1,
        energy_cost=0.05,
        action_name="recall",
        metadata={"category": "cognitive", "description": "Recall from memory"}
    ))
    
    registry.register(Capability(
        name="REMEMBER",
        actor_types=("human",),
        required_components=(),
        preconditions=(),
        effects=(
            Effect(type="memory_store"),
        ),
        time_cost=1,
        energy_cost=0.05,
        action_name="remember",
        metadata={"category": "cognitive", "description": "Store to memory"}
    ))
    
    # === TEMPORAL CAPABILITIES ===
    
    registry.register(Capability(
        name="WAIT",
        actor_types=("human",),
        required_components=(),
        preconditions=(),
        effects=(
            Effect(type="time_passage"),
        ),
        time_cost=1,
        energy_cost=0.0,
        action_name="wait",
        metadata={"category": "temporal", "description": "Wait for conditions to change"}
    ))
    
    registry.register(Capability(
        name="RETURN",
        actor_types=("human",),
        required_components=("TransformComponent",),
        preconditions=(
            Precondition(type="previous_location_known"),
        ),
        effects=(
            Effect(type="location_change"),
        ),
        time_cost=2,
        energy_cost=0.2,
        action_name="return",
        metadata={"category": "navigation", "description": "Return to previous location"}
    ))
    
    registry.register(Capability(
        name="REVISIT",
        actor_types=("human",),
        required_components=("TransformComponent",),
        preconditions=(
            Precondition(type="visited_location_known"),
        ),
        effects=(
            Effect(type="location_change"),
        ),
        time_cost=2,
        energy_cost=0.2,
        action_name="revisit",
        metadata={"category": "navigation", "description": "Revisit a known location"}
    ))
    
    # === EXPERIMENTAL CAPABILITIES ===
    
    registry.register(Capability(
        name="COMPARE",
        actor_types=("human",),
        required_components=(),
        preconditions=(
            Precondition(type="multiple_targets"),
        ),
        effects=(
            Effect(type="comparison_result"),
        ),
        time_cost=2,
        energy_cost=0.1,
        action_name="compare",
        metadata={"category": "cognitive", "description": "Compare multiple options"}
    ))
    
    registry.register(Capability(
        name="EXPERIMENT",
        actor_types=("human",),
        required_components=(),
        preconditions=(
            Precondition(type="hypothesis"),
        ),
        effects=(
            Effect(type="experimental_result"),
        ),
        time_cost=3,
        energy_cost=0.3,
        action_name="experiment",
        metadata={"category": "cognitive", "description": "Test a hypothesis"}
    ))
    
    # === STRATEGY CAPABILITIES ===
    
    registry.register(Capability(
        name="REVISE_STRATEGY",
        actor_types=("human",),
        required_components=(),
        preconditions=(
            Precondition(type="current_strategy"),
        ),
        effects=(
            Effect(type="strategy_change"),
        ),
        time_cost=2,
        energy_cost=0.1,
        action_name="revise_strategy",
        metadata={"category": "cognitive", "description": "Revise current strategy"}
    ))
    
    registry.register(Capability(
        name="REPEAT",
        actor_types=("human",),
        required_components=(),
        preconditions=(
            Precondition(type="successful_action_memory"),
        ),
        effects=(
            Effect(type="action_repetition"),
        ),
        time_cost=1,
        energy_cost=0.1,
        action_name="repeat",
        metadata={"category": "cognitive", "description": "Repeat successful action"}
    ))
    
    # === CONSTRUCTION CAPABILITIES ===
    
    registry.register(Capability(
        name="CONSTRUCT",
        actor_types=("human",),
        required_components=("InventoryComponent",),
        preconditions=(
            Precondition(type="has_materials"),
        ),
        effects=(
            Effect(type="object_creation"),
            Effect(type="inventory_remove"),
        ),
        time_cost=5,
        energy_cost=0.5,
        action_name="construct",
        metadata={"category": "construction", "description": "Construct new object"}
    ))
    
    registry.register(Capability(
        name="TRANSFORM",
        actor_types=("human",),
        required_components=("InventoryComponent",),
        preconditions=(
            Precondition(type="has_transformable"),
        ),
        effects=(
            Effect(type="object_transformation"),
            Effect(type="inventory_change"),
        ),
        time_cost=3,
        energy_cost=0.3,
        action_name="transform",
        metadata={"category": "construction", "description": "Transform existing object"}
    ))
    
    return registry
