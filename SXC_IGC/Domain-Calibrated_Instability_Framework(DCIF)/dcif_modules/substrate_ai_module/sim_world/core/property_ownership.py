"""
Domain-Locked Property Ownership System

CRITICAL INVARIANT: Every state mutation must have exactly one causal producer.

This registry enforces that each property is owned by exactly one domain.
No domain may mutate properties it does not own.
This prevents synchronization bugs and ensures predictable state evolution.
"""

# Property Ownership Registry
# Format: {property_path: owning_domain}
PROPERTY_OWNERSHIP = {
    # Entity Transform (position, rotation, room)
    "entities.*.components.TransformComponent": "domain.physics",
    "entity_transform_components": "domain.physics",
    "physics_goal_completion_signals": "domain.physics",
    
    # Entity Needs (hunger, energy, health)
    "entities.*.components.NeedsComponent": "domain.needs",
    "entity_needs_components": "domain.needs",
    
    # Hunger reduction signals (from eat actions)
    "hunger_reduction_signals": "domain.needs",
    
    # Entity Inventory (items, resources)
    "entities.*.components.InventoryComponent": "domain.resources",
    "entity_inventory_components": "domain.resources",
    
    # Entity Health (hit points, conditions)
    "entities.*.components.HealthComponent": "domain.health",
    "entity_health_components": "domain.health",
    "health_states": "domain.health",
    
    # Entity Relationships (social bonds, alliances)
    "entities.*.components.RelationshipComponent": "domain.relationships",
    "entity_relationship_components": "domain.relationships",
    "relationships": "domain.relationships",
    "_relationships_prior_keys": "domain.relationships",
    
    # Entity Memory (beliefs, experiences)
    "entities.*.components.MemoryComponent": "domain.memory",
    "entity_memory_components": "domain.memory",
    
    # Global Resources (world-level food, wood, water)
    "resources": "domain.resources",
    
    # Terrain and Environment
    "terrain": "domain.terrain",
    "world.conditions.terrain": "domain.terrain",
    
    # Goals and Planning
    "goals": "domain.population",
    "completed_goals": "domain.population",
    
    # Perceptions (entity sensory data)
    "perceptions": "domain.population",
    "pending_actions": "domain.population",
    
    # Action Signals (cross-domain communication)
    "action_eat_signals": "domain.population",  # Created by Population, consumed by Resources
    "action_harvest_signals": "domain.population",  # Created by Population, consumed by Resources
    "hunger_reduction_signals": "domain.resources",  # Created by Resources, consumed by Needs
    
    # Social Structure (village, households, leadership)
    "society": "domain.society",
    "world.conditions.society": "domain.society",
    "entity_society_component": "domain.society",
    
    # Economy (trade, prices, markets)
    "economy": "domain.economy",
    "world.conditions.economy": "domain.economy",
    
    # Learning and AI
    "learning": "domain.learning",
    "world.conditions.learning": "domain.learning",
    
    # Production (farming, crafting, building)
    "production": "domain.production",
    "agriculture": "domain.agriculture",
    "entity_production_components": "domain.production",
    
    # Time and Weather
    "time": "domain.time",
    "weather": "domain.weather",
    "world.conditions.weather": "domain.weather",
    "world.conditions.time": "domain.time",
    
    # Wildcard for world conditions (fallback for any unregistered conditions)
    "world.conditions.*": "domain.world",
    
    # Population and Demographics
    "population": "domain.population",
    
    # World-level fallback for unregistered properties
    "world": "domain.world",
    "world.conditions": "domain.world",
    
    # Conversation and Communication
    "conversations": "domain.conversation",
    "conversation_memories": "domain.conversation",
    "_conversation_prior_keys": "domain.conversation",
    
    # Health and Wellness
    "health_states": "domain.health",
}

def get_property_owner(property_path: str) -> str | None:
    """Get the owning domain for a given property path."""
    # Check exact matches first
    if property_path in PROPERTY_OWNERSHIP:
        return PROPERTY_OWNERSHIP[property_path]
    
    # Check pattern matches
    for pattern, owner in PROPERTY_OWNERSHIP.items():
        if "*" in pattern:
            pattern_regex = pattern.replace("*", ".*")
            import re
            if re.match(pattern_regex, property_path):
                return owner
    
    return None

def validate_property_mutation(property_path: str, mutating_domain: str) -> bool:
    """Validate that a domain owns the property it's trying to mutate."""
    owner = get_property_owner(property_path)
    if owner is None:
        # Unregistered property - this is a design error
        raise ValueError(f"Property {property_path} is not registered in ownership registry")
    
    if owner != mutating_domain:
        # Domain trying to mutate property it doesn't own
        raise PermissionError(
            f"Domain {mutating_domain} attempted to mutate {property_path} "
            f"which is owned by {owner}. This violates the single-producer invariant."
        )
    
    return True

def list_domain_properties(domain: str) -> list[str]:
    """List all properties owned by a specific domain."""
    return [prop for prop, owner in PROPERTY_OWNERSHIP.items() if owner == domain]