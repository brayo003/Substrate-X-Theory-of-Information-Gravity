"""
Capability Model - Formal capability definitions for planning

This module defines the Capability data structure and CapabilityRegistry
for formal capability-based planning. Capabilities represent primitive
operations with formal preconditions, effects, costs, and constraints.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Mapping
from enum import Enum


class FeasibilityStatus(Enum):
    """Feasibility status for capability chains."""
    FEASIBLE = "feasible"
    PARTIALLY_FEASIBLE = "partially_feasible"
    UNACHIEVABLE = "unachievable"


@dataclass(frozen=True, slots=True)
class Precondition:
    """A condition that must be true for a capability to execute."""
    type: str  # e.g., "entity_in_room", "resource_available", "entity_has_item"
    parameters: Mapping[str, Any] = field(default_factory=dict)


@dataclass(frozen=True, slots=True)
class Effect:
    """A state change produced by a capability."""
    type: str  # e.g., "resource_change", "location_change", "need_change"
    parameters: Mapping[str, Any] = field(default_factory=dict)


@dataclass(frozen=True, slots=True)
class Capability:
    """
    A primitive executable operation with formal preconditions and effects.
    
    Capabilities are the building blocks for planning. The planner composes
    capabilities to achieve high-level objectives by constructing dependency
    chains and validating preconditions.
    """
    # Identification
    name: str  # e.g., "MOVE", "GATHER_WOOD", "CRAFT_FISHING_ROD", "FISH"
    
    # Actor requirements
    actor_types: tuple[str, ...] = ()  # e.g., ("human",)
    required_components: tuple[str, ...] = ()  # e.g., ("TransformComponent", "InventoryComponent")
    
    # Preconditions
    preconditions: tuple[Precondition, ...] = ()
    
    # Effects
    effects: tuple[Effect, ...] = ()
    
    # Resource requirements
    required_resources: dict[str, float] = field(default_factory=dict)  # e.g., {"energy": 1.0}
    
    # Produced resources
    produced_resources: dict[str, float] = field(default_factory=dict)  # e.g., {"wood": 5.0}
    
    # Cost
    time_cost: int = 1  # ticks
    energy_cost: float = 0.0
    
    # Location requirements
    location_requirements: tuple[str, ...] = ()  # e.g., ("farm", "crafting_station")
    
    # Dependencies
    required_capabilities: tuple[str, ...] = ()  # e.g., ("has_fishing_rod",)
    
    # Action mapping
    action_name: str | None = None  # Maps to existing action in action_executor
    
    # Metadata
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class CapabilityRegistry:
    """Registry of available capabilities."""
    
    capabilities: dict[str, Capability] = field(default_factory=dict)
    
    def register(self, capability: Capability) -> Capability:
        """Register a capability."""
        self.capabilities[capability.name] = capability
        return capability
    
    def get(self, name: str) -> Capability | None:
        """Get a capability by name."""
        return self.capabilities.get(name)
    
    def list(self) -> tuple[Capability, ...]:
        """List all registered capabilities."""
        return tuple(self.capabilities.values())
    
    def find_by_preconditions(self, context: Mapping[str, Any], preconditions: tuple[Precondition, ...]) -> tuple[Capability, ...]:
        """Find capabilities that satisfy given preconditions."""
        matching = []
        for capability in self.capabilities.values():
            if self._check_preconditions(context, capability, preconditions):
                matching.append(capability)
        return tuple(matching)
    
    def find_by_effects(self, desired_effects: tuple[Effect, ...]) -> tuple[Capability, ...]:
        """Find capabilities that produce desired effects."""
        matching = []
        for capability in self.capabilities.values():
            if self._check_effects_match(capability, desired_effects):
                matching.append(capability)
        return tuple(matching)
    
    def find_by_location(self, location: str) -> tuple[Capability, ...]:
        """Find capabilities that can be executed at a given location."""
        matching = []
        for capability in self.capabilities.values():
            if not capability.location_requirements or location in capability.location_requirements:
                matching.append(capability)
        return tuple(matching)
    
    def _check_preconditions(self, context: Mapping[str, Any], capability: Capability, 
                           required_preconditions: tuple[Precondition, ...]) -> bool:
        """Check if capability satisfies required preconditions."""
        # Simplified implementation - full implementation would check against world state
        for req in required_preconditions:
            if req not in capability.preconditions:
                return False
        return True
    
    def _check_effects_match(self, capability: Capability, desired_effects: tuple[Effect, ...]) -> bool:
        """Check if capability produces desired effects."""
        # Check if capability produces at least one of the desired resources
        for desired in desired_effects:
            if desired.type == "resource_change":
                desired_resource = desired.parameters.get("resource")
                for effect in capability.effects:
                    if effect.type == "resource_change":
                        produced_resource = effect.parameters.get("resource")
                        if produced_resource == desired_resource:
                            return True
        return False


# Default capability registry with standard capabilities
def create_default_capability_registry() -> CapabilityRegistry:
    """Create a registry with standard capabilities mapped to existing actions."""
    registry = CapabilityRegistry()
    
    # Movement capability
    registry.register(Capability(
        name="MOVE",
        actor_types=("human",),
        required_components=("TransformComponent",),
        preconditions=(),  # No preconditions - can move from anywhere
        effects=(
            Effect(type="location_change", parameters={"destination": "target_room"}),
        ),
        required_resources={"energy": 0.1},
        time_cost=1,
        energy_cost=0.1,
        location_requirements=(),  # No location requirements - can move to anywhere
        action_name="Walk",
    ))
    
    # Wood gathering capability
    registry.register(Capability(
        name="GATHER_WOOD",
        actor_types=("human",),
        required_components=("TransformComponent", "InventoryComponent"),
        preconditions=(
            Precondition(type="entity_in_room", parameters={"room": "forest"}),
            Precondition(type="resource_available", parameters={"resource": "wood", "location": "forest"}),
        ),
        effects=(
            Effect(type="resource_change", parameters={"resource": "wood", "quantity": 1.0, "change": "add"}),
        ),
        required_resources={"energy": 0.5},
        produced_resources={"wood": 1.0},
        time_cost=2,
        energy_cost=0.5,
        location_requirements=("forest",),
        action_name="PickUp",
    ))
    
    # Fishing rod crafting capability
    registry.register(Capability(
        name="CRAFT_FISHING_ROD",
        actor_types=("human",),
        required_components=("TransformComponent", "InventoryComponent"),
        preconditions=(
            Precondition(type="entity_in_room", parameters={"room": "crafting_station"}),
            Precondition(type="resource_available", parameters={"resource": "wood", "quantity": 2.0}),
        ),
        effects=(
            Effect(type="resource_change", parameters={"resource": "wood", "quantity": 2.0, "change": "subtract"}),
            Effect(type="resource_change", parameters={"resource": "fishing_rod", "quantity": 1.0, "change": "add"}),
        ),
        required_resources={"wood": 2.0, "energy": 0.5},
        produced_resources={"fishing_rod": 1.0},
        time_cost=3,
        energy_cost=0.5,
        location_requirements=("crafting_station",),
        action_name="CraftRecipe",
    ))
    
    # Fishing capability
    registry.register(Capability(
        name="FISH",
        actor_types=("human",),
        required_components=("TransformComponent", "InventoryComponent"),
        preconditions=(
            Precondition(type="entity_in_room", parameters={"room": "river"}),
            Precondition(type="entity_has_item", parameters={"item": "fishing_rod"}),
            Precondition(type="resource_available", parameters={"resource": "fish", "location": "river"}),
        ),
        effects=(
            Effect(type="resource_change", parameters={"resource": "fish", "quantity": 3.0, "change": "add"}),
            Effect(type="resource_change", parameters={"resource": "energy", "quantity": 0.3, "change": "subtract"}),
        ),
        required_resources={"energy": 0.3},
        required_capabilities=("has_fishing_rod",),
        produced_resources={"fish": 3.0},
        time_cost=5,
        energy_cost=0.3,
        location_requirements=("river",),
        action_name="HarvestCrop",
    ))
    
    # Eating capability
    registry.register(Capability(
        name="EAT",
        actor_types=("human",),
        required_components=("TransformComponent", "InventoryComponent", "NeedsComponent"),
        preconditions=(
            Precondition(type="entity_has_item", parameters={"item": "food"}),
        ),
        effects=(
            Effect(type="resource_change", parameters={"resource": "food", "quantity": 1.0, "change": "subtract"}),
            Effect(type="need_change", parameters={"need": "hunger", "change": "reduce", "amount": 0.35}),
        ),
        required_resources={"food": 1.0},
        time_cost=1,
        action_name="Eat",
    ))
    
    # Storage capability
    registry.register(Capability(
        name="STORE",
        actor_types=("human",),
        required_components=("TransformComponent", "InventoryComponent"),
        preconditions=(
            Precondition(type="entity_has_item", parameters={"item": "resource"}),
            Precondition(**{"type": "entity_in_room", "parameters": {"room": "storage"}}),
        ),
        effects=(
            Effect(type="resource_change", parameters={"resource": "food", "quantity": 1.0, "change": "add"}),
        ),
        time_cost=1,
        location_requirements=("storage",),
        action_name="StoreHarvest",
    ))
    
    return registry
