"""
Capability-Based Planner - General planning using formal capabilities

This module implements a planner that operates on formal capability definitions
rather than hardcoded scenario handlers. It constructs dependency graphs from
world state and validates preconditions to find feasible capability chains.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Mapping
from collections import deque

from .capability import Capability, CapabilityRegistry, FeasibilityStatus, Precondition, Effect, create_default_capability_registry
from .planner_context import Goal, PlannerContext, PlanProposal
from ..simulation.simulation_context import ActionRequest
from ..core.ids import EntityId


@dataclass(frozen=True, slots=True)
class FeasibilityResult:
    """Result of feasibility checking."""
    status: FeasibilityStatus
    explanation: str
    missing_preconditions: tuple[str, ...] = field(default_factory=tuple)
    alternative_chains: tuple[tuple[str, ...], ...] = field(default_factory=tuple)


@dataclass(frozen=True, slots=True)
class CapabilityChain:
    """A chain of capabilities that achieves an objective."""
    capabilities: tuple[Capability, ...]
    total_cost: float
    total_time: int
    resource_requirements: dict[str, float] = field(default_factory=dict)
    produced_resources: dict[str, float] = field(default_factory=dict)


@dataclass
class CapabilityPlanner:
    """
    Planner that operates on formal capability definitions.
    
    This planner does not use hardcoded scenario handlers. Instead, it:
    1. Inspects current world state
    2. Inspects available capabilities
    3. Constructs dependency graphs
    4. Finds feasible chains
    5. Ranks alternatives
    6. Validates preconditions
    7. Produces PlanProposals
    """
    
    registry: CapabilityRegistry = field(default_factory=lambda: create_default_capability_registry())
    max_depth: int = 10
    max_alternatives: int = 5
    
    def plan(self, context: PlannerContext, goal: Goal) -> tuple[PlanProposal, ...]:
        """
        Generate plans using capability-based planning.
        
        Args:
            context: Planner context with world state
            goal: High-level goal to achieve
            
        Returns:
            Tuple of PlanProposals
        """
        if goal.entity_id is None:
            return ()
        
        # Extract objective from goal
        objective = goal.objective or goal.kind.lower()
        target_state = goal.target_state
        preferences = goal.preferences
        resource_limits = goal.resource_limits
        
        # Check feasibility
        feasibility = self.check_feasibility(context, goal, objective, target_state)
        
        if feasibility.status == FeasibilityStatus.UNACHIEVABLE:
            # Return empty plan with explanation in metadata
            return ()
        
        # Find capability chains
        chains = self.find_capability_chains(
            context, goal, objective, target_state, preferences, resource_limits
        )
        
        if not chains:
            return ()
        
        # Convert chains to PlanProposals
        proposals = []
        for chain in chains[:self.max_alternatives]:
            proposal = self._chain_to_proposal(context, goal, chain, feasibility)
            if proposal:
                proposals.append(proposal)
        
        return tuple(proposals)
    
    def check_feasibility(
        self, 
        context: PlannerContext, 
        goal: Goal, 
        objective: str, 
        target_state: Mapping[str, Any]
    ) -> FeasibilityResult:
        """
        Check if an objective is feasible given current world state.
        
        Returns:
            FeasibilityResult with status and explanation
        """
        entity_id = goal.entity_id
        entity_state = _entity_state(context, entity_id)
        
        if entity_state is None:
            return FeasibilityResult(
                status=FeasibilityStatus.UNACHIEVABLE,
                explanation="Entity not found in world state"
            )
        
        # Check if target state is already achieved
        if self._target_state_satisfied(context, entity_id, target_state):
            return FeasibilityResult(
                status=FeasibilityStatus.FEASIBLE,
                explanation="Target state already satisfied"
            )
        
        # Try to find a feasible chain using state-space planning
        chains = self.find_capability_chains(context, goal, objective, target_state, {}, {})
        
        if chains:
            return FeasibilityResult(
                status=FeasibilityStatus.FEASIBLE,
                explanation=f"Found {len(chains)} feasible capability chain(s)"
            )
        
        # Check if any capabilities can achieve the target state
        target_effects = self._target_state_to_effects(target_state)
        capable_capabilities = self.registry.find_by_effects(target_effects)
        
        if not capable_capabilities:
            return FeasibilityResult(
                status=FeasibilityStatus.UNACHIEVABLE,
                explanation=f"No capabilities can achieve target state: {target_state}"
            )
        
        # Check if any capable capability can ever be satisfied
        all_locations = self._get_all_locations(context)
        any_capable = False
        for capability in capable_capabilities:
            if self._capability_ever_satisfiable(capability, context, entity_id, all_locations):
                any_capable = True
                break
        
        if not any_capable:
            return FeasibilityResult(
                status=FeasibilityStatus.UNACHIEVABLE,
                explanation=f"Capabilities exist but their preconditions cannot be satisfied in current world state (missing locations or resources)"
            )
        
        # Capabilities exist and could be satisfied, but no complete chain found
        return FeasibilityResult(
            status=FeasibilityStatus.PARTIALLY_FEASIBLE,
            explanation="Capabilities exist but no complete feasible chain found (may require additional resources or different approach)"
        )
    
    def find_capability_chains(
        self,
        context: PlannerContext,
        goal: Goal,
        objective: str,
        target_state: Mapping[str, Any],
        preferences: Mapping[str, Any],
        resource_limits: Mapping[str, float]
    ) -> list[CapabilityChain]:
        """
        Find capability chains that achieve the objective.
        
        Uses state-space BFS: start from initial state, apply capabilities,
        check if goal state reached.
        """
        entity_id = goal.entity_id
        entity_state = _entity_state(context, entity_id)
        if entity_state is None:
            return []
        
        # Initialize planning state from actual world state
        initial_state = self._create_planning_state(context, entity_id)
        
        # Get all possible locations from world state
        all_locations = self._get_all_locations(context)
        
        # BFS on state space: (state, chain, cost, depth)
        queue = deque()
        visited_states = set()
        chains = []
        
        queue.append((initial_state, [], 0, 0))
        
        iterations = 0
        while queue and len(chains) < self.max_alternatives and iterations < 1000:
            iterations += 1
            current_state, current_chain, current_cost, depth = queue.popleft()
            
            if depth > self.max_depth:
                continue
            
            # Create state key for visited check
            state_key = self._state_to_key(current_state)
            if state_key in visited_states:
                continue
            visited_states.add(state_key)
            
            # Check if goal state is achieved
            goal_achieved = self._goal_state_achieved(current_state, target_state)
            if goal_achieved:
                chains.append(CapabilityChain(
                    capabilities=tuple(current_chain),
                    total_cost=current_cost,
                    total_time=current_cost,
                    resource_requirements=self._aggregate_resource_requirements(current_chain),
                    produced_resources=self._aggregate_produced_resources(current_chain)
                ))
                continue
            
            # Find applicable capabilities (preconditions satisfied in current state)
            applicable = self._find_applicable_capabilities(current_state)
            
            for capability in applicable:
                # Check resource limits
                if not self._check_resource_limits(capability, current_state, resource_limits):
                    continue
                
                # Apply capability to get new state
                new_state = self._apply_capability(current_state, capability)
                new_chain = current_chain + [capability]
                new_cost = current_cost + capability.time_cost
                
                queue.append((new_state, new_chain, new_cost, depth + 1))
            
            # Add location transitions (MOVE capability)
            for new_location in all_locations:
                if new_location != current_state.get("location"):
                    move_state = dict(current_state)
                    move_state["location"] = new_location
                    move_cap = self.registry.get("MOVE")
                    if move_cap:
                        move_state["energy"] = max(0.0, move_state["energy"] - move_cap.energy_cost)
                        move_state["time"] = move_state["time"] + move_cap.time_cost
                        move_chain = current_chain + [move_cap]
                        move_cost = current_cost + move_cap.time_cost
                        
                        # Check resource limits for move
                        if self._check_resource_limits(move_cap, current_state, resource_limits):
                            queue.append((move_state, move_chain, move_cost, depth + 1))
        
        # Sort chains by cost
        chains.sort(key=lambda c: c.total_cost)
        
        return chains
    
    def _create_planning_state(self, context: PlannerContext, entity_id: EntityId) -> dict[str, Any]:
        """Create initial planning state from actual world state."""
        entity_state = _entity_state(context, entity_id)
        if entity_state is None:
            return {}
        
        state = {
            "inventory": {},
            "location": _room(entity_state),
            "energy": 1.0,
            "time": 0,
        }
        
        # Initialize inventory
        inventory = _component_state(entity_state, "InventoryComponent") or {}
        items = inventory.get("items", ())
        for item in items:
            item_id = item.get("identifier")
            quantity = item.get("quantity", 0.0)
            if item_id:
                state["inventory"][item_id] = state["inventory"].get(item_id, 0.0) + quantity
        
        # Initialize energy from needs
        needs = _component_state(entity_state, "NeedsComponent") or {}
        needs_dict = needs.get("needs", {})
        state["energy"] = needs_dict.get("energy", 1.0)
        
        return state
    
    def _get_all_locations(self, context: PlannerContext) -> list[str]:
        """Get all possible locations from world state."""
        locations = set()
        for entity in dict(context.snapshot.state.get("entities", {})).values():
            room = dict(entity.get("components", {})).get("TransformComponent", {}).get("room")
            if room:
                locations.add(room)
        return list(locations)
    
    def _state_to_key(self, state: dict[str, Any]) -> tuple:
        """Create hashable key for state."""
        inventory_items = tuple(sorted(state.get("inventory", {}).items()))
        return (state.get("location", ""), inventory_items, state.get("energy", 0.0))
    
    def _goal_state_achieved(self, state: dict[str, Any], target_state: Mapping[str, Any]) -> bool:
        """Check if goal state is achieved."""
        for key, target_value in target_state.items():
            if key == "food_reserve":
                # Check if entity has food or fish in inventory
                food_qty = state.get("inventory", {}).get("food", 0.0)
                fish_qty = state.get("inventory", {}).get("fish", 0.0)
                if food_qty + fish_qty < target_value:
                    return False
            elif key == "water_reserve":
                water_qty = state.get("inventory", {}).get("water", 0.0)
                if water_qty < target_value:
                    return False
        return True
    
    def _find_applicable_capabilities(self, state: dict[str, Any]) -> list[Capability]:
        """Find capabilities whose preconditions are satisfied in current state."""
        applicable = []
        
        for capability in self.registry.list():
            # Skip MOVE - handle location transitions separately
            if capability.name == "MOVE":
                continue
            
            # Check location preconditions
            if capability.location_requirements:
                if state.get("location") not in capability.location_requirements:
                    continue
            
            # Check resource requirements
            resource_satisfied = True
            for resource, required_qty in capability.required_resources.items():
                if resource == "energy":
                    # Energy is tracked separately
                    if state.get("energy", 1.0) < required_qty:
                        resource_satisfied = False
                        break
                else:
                    # Other resources are in inventory
                    if state.get("inventory", {}).get(resource, 0.0) < required_qty:
                        resource_satisfied = False
                        break
            if not resource_satisfied:
                continue
            
            # Check item preconditions
            item_satisfied = True
            for precond in capability.preconditions:
                if precond.type == "entity_has_item":
                    item = precond.parameters.get("item")
                    quantity = precond.parameters.get("quantity", 1.0)
                    if state.get("inventory", {}).get(item, 0.0) < quantity:
                        item_satisfied = False
                        break
            if not item_satisfied:
                continue
            
            applicable.append(capability)
        
        return applicable
    
    def _capability_ever_satisfiable(
        self,
        capability: Capability,
        context: PlannerContext,
        entity_id: EntityId,
        all_locations: list[str]
    ) -> bool:
        """Check if a capability's preconditions can ever be satisfied in current world state."""
        # Check location requirements
        if capability.location_requirements:
            location_satisfied = any(loc in all_locations for loc in capability.location_requirements)
            if not location_satisfied:
                return False
        
        # Check if required resources could potentially be obtained
        # For now, we'll check if the resource-producing capabilities exist
        for resource, required_qty in capability.required_resources.items():
            if resource == "energy":
                # Energy is renewable, always potentially satisfiable
                continue
            # Check if any capability can produce this resource
            resource_producers = [c for c in self.registry.list() if resource in c.produced_resources]
            if not resource_producers:
                # No way to obtain this resource
                return False
        
        # Check item preconditions
        for precond in capability.preconditions:
            if precond.type == "entity_has_item":
                item = precond.parameters.get("item")
                # Check if any capability can produce this item
                item_producers = [c for c in self.registry.list() if item in c.produced_resources]
                if not item_producers:
                    # No way to obtain this item
                    return False
        
        return True
    
    def _check_resource_limits(
        self,
        capability: Capability,
        state: dict[str, Any],
        resource_limits: Mapping[str, float]
    ) -> bool:
        """Check if capability violates resource limits."""
        if not resource_limits:
            return True
        
        # Check energy limit
        if "energy" in resource_limits:
            if state.get("energy", 1.0) < capability.energy_cost:
                return False
        
        # Check other resource limits
        for resource, limit in resource_limits.items():
            if resource == "energy":
                continue
            current_qty = state.get("inventory", {}).get(resource, 0.0)
            if current_qty > limit:
                return False
        
        return True
    
    def _apply_capability(self, state: dict[str, Any], capability: Capability) -> dict[str, Any]:
        """Apply capability effects to create new state."""
        new_state = {
            "inventory": dict(state.get("inventory", {})),
            "location": state.get("location", ""),
            "energy": state.get("energy", 1.0),
            "time": state.get("time", 0),
        }
        
        # Apply effects
        for effect in capability.effects:
            if effect.type == "resource_change":
                resource = effect.parameters.get("resource")
                quantity = effect.parameters.get("quantity", 0.0)
                change = effect.parameters.get("change", "add")
                
                if change == "add":
                    new_state["inventory"][resource] = new_state["inventory"].get(resource, 0.0) + quantity
                elif change == "subtract":
                    new_state["inventory"][resource] = new_state["inventory"].get(resource, 0.0) - quantity
            elif effect.type == "location_change":
                # For MOVE capability, we need to handle this specially
                # In state-space planning, MOVE should transition to all possible locations
                # For now, we'll handle this in the applicable capabilities logic
                pass
            elif effect.type == "need_change":
                need = effect.parameters.get("need")
                change = effect.parameters.get("change", "add")
                if need == "energy":
                    if change == "add":
                        new_state["energy"] = min(1.0, new_state["energy"] + effect.parameters.get("quantity", 0.0))
                    elif change == "subtract":
                        new_state["energy"] = max(0.0, new_state["energy"] - effect.parameters.get("quantity", 0.0))
        
        # Apply resource requirements (subtract from inventory)
        for resource, qty in capability.required_resources.items():
            if resource == "energy":
                # Energy is handled separately by energy_cost
                continue
            else:
                new_state["inventory"][resource] = new_state["inventory"].get(resource, 0.0) - qty
        
        # Remove energy from inventory if it was accidentally added
        if "energy" in new_state["inventory"]:
            del new_state["inventory"]["energy"]
        
        # Apply energy cost (only once, from energy_cost field)
        new_state["energy"] = max(0.0, new_state["energy"] - capability.energy_cost)
        new_state["time"] = new_state["time"] + capability.time_cost
        
        return new_state
    
    def _add_move_capabilities_from_state(
        self,
        context: PlannerContext,
        entity_id: EntityId,
        chain: list[Capability],
        final_state: dict[str, Any]
    ) -> list[Capability]:
        """Add MOVE capabilities based on state transitions."""
        move_cap = self.registry.get("MOVE")
        if not move_cap:
            return chain
        
        enhanced_chain = []
        current_location = _room(_entity_state(context, entity_id))
        
        for capability in chain:
            # Check if capability requires a specific location
            if capability.location_requirements:
                required_room = capability.location_requirements[0] if capability.location_requirements else None
                if required_room and current_location != required_room:
                    # Add MOVE capability before this capability
                    enhanced_chain.append(move_cap)
                    current_location = required_room
            
            enhanced_chain.append(capability)
        
        return enhanced_chain
    
    def _chain_is_feasible(
        self,
        context: PlannerContext,
        entity_id: EntityId,
        chain: list[Capability]
    ) -> bool:
        """Check if a capability chain is feasible (all preconditions can be satisfied)."""
        # Simulate chain execution
        simulated_inventory = {}
        simulated_room = _room(_entity_state(context, entity_id))
        
        # Initialize with entity's actual inventory
        entity_state = _entity_state(context, entity_id)
        if entity_state:
            inventory = _component_state(entity_state, "InventoryComponent") or {}
            items = inventory.get("items", ())
            for item in items:
                item_id = item.get("identifier")
                quantity = item.get("quantity", 0.0)
                if item_id:
                    simulated_inventory[item_id] = simulated_inventory.get(item_id, 0.0) + quantity
        
        for capability in chain:
            # Check location preconditions - don't fail here, MOVE will be added later
            # if capability.location_requirements:
            #     if simulated_room not in capability.location_requirements:
            #         return False
            
            # Check resource requirements
            for resource, required_qty in capability.required_resources.items():
                if simulated_inventory.get(resource, 0.0) < required_qty:
                    return False
            
            # Check item preconditions
            for precond in capability.preconditions:
                if precond.type == "entity_has_item":
                    item = precond.parameters.get("item")
                    quantity = precond.parameters.get("quantity", 1.0)
                    if simulated_inventory.get(item, 0.0) < quantity:
                        return False
            
            # Apply effects
            for effect in capability.effects:
                if effect.type == "resource_change":
                    resource = effect.parameters.get("resource")
                    quantity = effect.parameters.get("quantity", 0.0)
                    change = effect.parameters.get("change", "add")
                    
                    if change == "add":
                        simulated_inventory[resource] = simulated_inventory.get(resource, 0.0) + quantity
                    elif change == "subtract":
                        simulated_inventory[resource] = simulated_inventory.get(resource, 0.0) - quantity
                elif effect.type == "location_change":
                    simulated_room = effect.parameters.get("destination", simulated_room)
        
        return True
    
    def _add_move_capabilities(
        self,
        context: PlannerContext,
        entity_id: EntityId,
        chain: list[Capability]
    ) -> list[Capability]:
        """Add MOVE capabilities to chain for location changes."""
        move_cap = self.registry.get("MOVE")
        if not move_cap:
            return chain
        
        enhanced_chain = []
        simulated_room = _room(_entity_state(context, entity_id))
        
        for capability in chain:
            # Check if capability requires a specific location
            if capability.location_requirements:
                required_room = capability.location_requirements[0] if capability.location_requirements else None
                if required_room and simulated_room != required_room:
                    # Add MOVE capability before this capability
                    enhanced_chain.append(move_cap)
                    simulated_room = required_room
            
            enhanced_chain.append(capability)
            
            # Update simulated room if capability changes location
            for effect in capability.effects:
                if effect.type == "location_change":
                    simulated_room = effect.parameters.get("destination", simulated_room)
        
        return enhanced_chain
    
    def _get_chain_missing_preconditions(
        self,
        context: PlannerContext,
        entity_id: EntityId,
        chain: list[Capability]
    ) -> list[str]:
        """Get missing preconditions for a capability chain."""
        missing = []
        simulated_inventory = {}
        
        # Initialize with entity's actual inventory
        entity_state = _entity_state(context, entity_id)
        if entity_state:
            inventory = _component_state(entity_state, "InventoryComponent") or {}
            items = inventory.get("items", ())
            for item in items:
                item_id = item.get("identifier")
                quantity = item.get("quantity", 0.0)
                if item_id:
                    simulated_inventory[item_id] = simulated_inventory.get(item_id, 0.0) + quantity
        
        for capability in chain:
            # Check resource requirements
            for resource, required_qty in capability.required_resources.items():
                if simulated_inventory.get(resource, 0.0) < required_qty:
                    missing.append(f"resource_{resource}")
            
            # Check item preconditions
            for precond in capability.preconditions:
                if precond.type == "entity_has_item":
                    item = precond.parameters.get("item")
                    quantity = precond.parameters.get("quantity", 1.0)
                    if simulated_inventory.get(item, 0.0) < quantity:
                        missing.append(f"item_{item}")
            
            # Apply effects
            for effect in capability.effects:
                if effect.type == "resource_change":
                    resource = effect.parameters.get("resource")
                    quantity = effect.parameters.get("quantity", 0.0)
                    change = effect.parameters.get("change", "add")
                    
                    if change == "add":
                        simulated_inventory[resource] = simulated_inventory.get(resource, 0.0) + quantity
                    elif change == "subtract":
                        simulated_inventory[resource] = simulated_inventory.get(resource, 0.0) - quantity
        
        return missing
    
    def _check_capability_preconditions(
        self, 
        context: PlannerContext, 
        entity_id: EntityId, 
        capability: Capability
    ) -> list[str]:
        """Check if entity satisfies capability preconditions."""
        entity_state = _entity_state(context, entity_id)
        if entity_state is None:
            return ["entity_not_found"]
        
        missing = []
        
        # Check each precondition using the improved _check_precondition method
        for precondition in capability.preconditions:
            if not self._check_precondition(context, entity_id, precondition):
                missing.append(f"precondition_{precondition.type}")
        
        # Check resource requirements
        inventory = _component_state(entity_state, "InventoryComponent") or {}
        items = inventory.get("items", ())
        
        for resource, required_qty in capability.required_resources.items():
            has_qty = sum(
                item.get("quantity", 0.0)
                for item in items
                if item.get("identifier") == resource
            )
            if has_qty < required_qty:
                missing.append(f"resource_{resource}")
        
        return missing
    
    def _check_chain_preconditions(
        self,
        context: PlannerContext,
        entity_id: EntityId,
        chain: list[Capability]
    ) -> list[str]:
        """Check if chain preconditions can be satisfied."""
        # Simulate chain execution
        simulated_inventory = {}
        
        for capability in chain:
            # Check if capability can be executed with current inventory
            for resource, required_qty in capability.required_resources.items():
                if simulated_inventory.get(resource, 0.0) < required_qty:
                    return [f"resource_{resource}"]
            
            # Apply effects
            for effect in capability.effects:
                if effect.type == "resource_change":
                    resource = effect.parameters.get("resource")
                    quantity = effect.parameters.get("quantity", 0.0)
                    change = effect.parameters.get("change", "add")
                    
                    if change == "add":
                        simulated_inventory[resource] = simulated_inventory.get(resource, 0.0) + quantity
                    elif change == "subtract":
                        simulated_inventory[resource] = simulated_inventory.get(resource, 0.0) - quantity
        
        return []
    
    def _check_precondition(
        self,
        context: PlannerContext,
        entity_id: EntityId,
        precondition: Precondition
    ) -> bool:
        """Check if a single precondition is satisfied."""
        entity_state = _entity_state(context, entity_id)
        if entity_state is None:
            return False
        
        if precondition.type == "entity_in_room":
            required_room = precondition.parameters.get("room")
            current_room = _room(entity_state)
            return current_room == required_room
        
        elif precondition.type == "resource_available":
            # Check if resource exists in world at specified location
            resource = precondition.parameters.get("resource")
            location = precondition.parameters.get("location")
            return self._resource_available(context, resource, location)
        
        elif precondition.type == "entity_has_item":
            item = precondition.parameters.get("item")
            quantity = precondition.parameters.get("quantity", 1.0)
            inventory = _component_state(entity_state, "InventoryComponent") or {}
            items = inventory.get("items", ())
            
            # Check if entity has at least the required quantity
            total_quantity = sum(
                item_obj.get("quantity", 0.0)
                for item_obj in items
                if item_obj.get("identifier") == item
            )
            return total_quantity >= quantity
        
        return False
    
    def _find_satisfying_capabilities(self, missing_item: str) -> list[Capability]:
        """Find capabilities that satisfy a missing precondition."""
        # Strip prefix if present (e.g., "item_fishing_rod" -> "fishing_rod")
        if missing_item.startswith("item_"):
            missing_item = missing_item[5:]
        elif missing_item.startswith("resource_"):
            missing_item = missing_item[9:]
        
        # Simplified: find capabilities that produce the missing resource
        satisfying = []
        for capability in self.registry.list():
            if missing_item in capability.produced_resources:
                satisfying.append(capability)
        return satisfying
    
    def _target_state_to_effects(self, target_state: Mapping[str, Any]) -> tuple[Effect, ...]:
        """Convert target state to desired effects."""
        effects = []
        for key, value in target_state.items():
            if key == "food_reserve":
                # Map food_reserve to fish (primary food source)
                effects.append(Effect(type="resource_change", parameters={"resource": "fish", "quantity": value, "change": "add"}))
            elif key == "water_reserve":
                effects.append(Effect(type="resource_change", parameters={"resource": "water", "quantity": value, "change": "add"}))
            elif key == "wood":
                # Map wood directly to wood resource
                effects.append(Effect(type="resource_change", parameters={"resource": "wood", "quantity": value, "change": "add"}))
        return tuple(effects)
    
    def _target_state_satisfied(
        self,
        context: PlannerContext,
        entity_id: EntityId,
        target_state: Mapping[str, Any]
    ) -> bool:
        """Check if target state is already satisfied."""
        entity_state = _entity_state(context, entity_id)
        if entity_state is None:
            return False
        
        inventory = _component_state(entity_state, "InventoryComponent") or {}
        items = inventory.get("items", ())
        
        for key, value in target_state.items():
            if key == "food_reserve":
                has_food = sum(
                    item.get("quantity", 0.0)
                    for item in items
                    if item.get("identifier") == "food"
                )
                if has_food < value:
                    return False
        
        return True
    
    def _resource_available(
        self,
        context: PlannerContext,
        resource: str,
        location: str | None = None
    ) -> bool:
        """Check if resource is available in the world."""
        for entity in dict(context.snapshot.state.get("entities", {})).values():
            entity_type = str(entity.get("type", ""))
            display_name = str(entity.get("display_name", ""))
            room = dict(entity.get("components", {})).get("TransformComponent", {}).get("room")
            
            if location and room != location:
                continue
            
            # Check if entity is the resource itself (river, forest, farm)
            if resource in display_name.lower() or resource in entity_type.lower():
                return True
            
            # Check if entity contains the resource in inventory
            inventory = dict(entity.get("components", {})).get("InventoryComponent") or {}
            items = inventory.get("items", ())
            for item in items:
                if item.get("identifier") == resource and item.get("quantity", 0.0) > 0:
                    return True
        
        return False
    
    def _location_exists(self, context: PlannerContext, location: str) -> bool:
        """Check if a location exists in the world."""
        for entity in dict(context.snapshot.state.get("entities", {})).values():
            room = dict(entity.get("components", {})).get("TransformComponent", {}).get("room")
            if room == location:
                return True
        return False
    
    def _aggregate_resource_requirements(self, chain: list[Capability]) -> dict[str, float]:
        """Aggregate resource requirements for a chain."""
        requirements = {}
        for capability in chain:
            for resource, qty in capability.required_resources.items():
                requirements[resource] = requirements.get(resource, 0.0) + qty
        return requirements
    
    def _aggregate_produced_resources(self, chain: list[Capability]) -> dict[str, float]:
        """Aggregate produced resources for a chain."""
        produced = {}
        for capability in chain:
            for resource, qty in capability.produced_resources.items():
                produced[resource] = produced.get(resource, 0.0) + qty
        return produced
    
    def _chain_to_proposal(
        self,
        context: PlannerContext,
        goal: Goal,
        chain: CapabilityChain,
        feasibility: FeasibilityResult
    ) -> PlanProposal | None:
        """Convert a capability chain to a PlanProposal."""
        action_requests = []
        
        for capability in chain.capabilities:
            if capability.action_name:
                request = self._capability_to_request(context, goal, capability)
                if request:
                    action_requests.append(request)
        
        if not action_requests:
            return None
        
        return PlanProposal(
            plan_id=f"plan_{hash(tuple(c.name for c in chain.capabilities))}",
            goal_id=goal.goal_id,
            entity_id=goal.entity_id,
            priority=goal.priority,
            estimated_cost=chain.total_cost,
            estimated_duration=chain.total_time,
            action_requests=tuple(action_requests),
            required_resources=chain.resource_requirements,
            confidence=0.7 if feasibility.status == FeasibilityStatus.FEASIBLE else 0.5,
            goal_subject=goal.subject,
            metadata={
                "capability_chain": tuple(c.name for c in chain.capabilities),
                "feasibility_status": feasibility.status.value,
                "feasibility_explanation": feasibility.explanation,
            }
        )
    
    def _capability_to_request(
        self,
        context: PlannerContext,
        goal: Goal,
        capability: Capability
    ) -> ActionRequest | None:
        """Convert a capability to an ActionRequest."""
        if not capability.action_name:
            return None
        
        return ActionRequest(
            actor_id=goal.entity_id,
            action=capability.action_name,
            parameters=dict(capability.metadata),
            priority=goal.priority,
            correlation_id=f"{goal.goal_id}:{capability.name}",
        )


# Helper functions
def _entity_state(context: PlannerContext, entity_id: EntityId) -> Mapping[str, Any] | None:
    """Get entity state from context."""
    return dict(context.snapshot.state.get("entities", {})).get(str(entity_id))


def _component_state(entity_state: Mapping[str, Any], component_name: str) -> Mapping[str, Any] | None:
    """Get component state from entity."""
    components = entity_state.get("components", {})
    return dict(components).get(component_name)


def _room(entity_state: Mapping[str, Any]) -> str | None:
    """Get entity room."""
    transform = _component_state(entity_state, "TransformComponent")
    if transform:
        return transform.get("room")
    return None
