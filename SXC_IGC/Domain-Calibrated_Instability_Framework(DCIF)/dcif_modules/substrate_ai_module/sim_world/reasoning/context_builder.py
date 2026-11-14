"""
Entity Context Builder - Build prompts from simulation state

This module builds prompts for LLM reasoning based on simulation state.
Each entity receives:
- identity, role, occupation, inventory, relationships
- current goals, needs, location, nearby entities, recent events
- environment
- transport regime (legacy Q)
- substrate_state: full multidimensional SubstrateState (Phase 4+)

The substrate_state exposes C_spectral, f_prop, f_over, coordination_capacity,
decay_timescale and other physically meaningful quantities.  Agents use these
to modulate the quality of their information and coordination, not to hardcode
behaviour switches.

Never fabricates information — only uses actual simulation state.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Mapping
from datetime import datetime, timezone

from ..core.ids import EntityId, TickId, WorldId
from ..memory.agent_memory import AgentMemory


@dataclass(frozen=True, slots=True)
class EntityContext:
    """Context for a single entity's reasoning."""
    entity_id: str
    name: str
    entity_type: str
    role: str
    occupation: str
    location: str
    inventory: Mapping[str, Any]
    relationships: Mapping[str, Any]
    current_goals: tuple[str, ...]
    needs: Mapping[str, float]
    nearby_entities: tuple[str, ...]
    recent_events: tuple[str, ...]
    environment: Mapping[str, Any]
    transport_regime: str
    q_regime: str
    # --- Legacy single-string spectral fields (kept for compat) ---
    spectral_regime: str
    spectral_dominant_k: float
    # --- Full multidimensional substrate state (Phase 4) ---
    substrate: Mapping[str, Any]      # from SubstrateState.to_agent_context()
    coordination_capacity: float      # 0..1 derived from C_spectral
    memory_persistence_factor: float  # 0..1 derived from decay_timescale
    current_tick: int
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class ContextBuilder:
    """Build entity contexts from simulation state."""

    def build_context(
        self,
        entity_id: EntityId,
        entity_data: Mapping[str, Any],
        world_state: Mapping[str, Any],
        agent_memory: AgentMemory | None = None,
        transport_observation: Any = None,
        spectral_observable: Any = None,
        current_tick: int = 0,
    ) -> EntityContext:
        """
        Build context for a single entity.

        Args:
            entity_id:            Entity ID
            entity_data:          Entity data from world state
            world_state:          Full world state
            agent_memory:         Agent's memory for recent events
            transport_observation: Legacy Q transport observation
            spectral_observable:  SpectralTransportObservable from physical field
            current_tick:         Current simulation tick

        Returns:
            EntityContext with all relevant information including full substrate state.
        """
        # Extract entity information
        entity_type = str(entity_data.get("type", "unknown"))
        name        = str(entity_data.get("display_name", entity_data.get("name", "Unknown")))
        metadata    = dict(entity_data.get("metadata", {}))

        role       = str(metadata.get("role", "villager"))
        occupation = str(metadata.get("occupation", "farmer"))

        components    = dict(entity_data.get("components", {}))
        transform_comp = dict(components.get("TransformComponent", {}))
        location       = str(transform_comp.get("room", "unknown"))

        inventory_comp = dict(components.get("InventoryComponent", {}))
        items_data = inventory_comp.get("items", [])
        if isinstance(items_data, list):
            inventory = {str(i): 1 for i in items_data}
        elif isinstance(items_data, dict):
            inventory = dict(items_data)
        else:
            inventory = {}

        needs_comp = dict(components.get("NeedsComponent", {}))
        needs      = {k: float(v) for k, v in dict(needs_comp.get("needs", {})).items()}

        relationship_comp  = dict(components.get("RelationshipComponent", {}))
        relationships_data = relationship_comp.get("relationships", {})
        relationships      = dict(relationships_data) if isinstance(relationships_data, dict) else {}

        current_goals   = tuple(metadata.get("current_goals", []))
        nearby_entities = self._find_nearby_entities(entity_id, location, world_state.get("entities", {}))
        recent_events   = self._extract_recent_events(agent_memory, limit=5)
        environment     = self._extract_environment(location, world_state)

        # --- Legacy transport regime ---
        transport_regime = "unknown"
        q_regime         = "unknown"
        if transport_observation is not None:
            transport_regime = str(getattr(transport_observation, "regime", "unknown"))
            q_regime         = transport_regime

        # --- Legacy spectral single-string fields ---
        spectral_regime    = "unknown"
        spectral_dominant_k = 0.0
        if spectral_observable is not None:
            spectral_regime     = str(getattr(spectral_observable, "dominant_regime", "unknown"))
            spectral_dominant_k = float(getattr(spectral_observable, "dominant_k", 0.0))

        # --- Full multidimensional SubstrateState (Phase 4) ---
        substrate_ctx         = {}
        coordination_capacity = 0.5     # neutral default
        memory_persist        = 0.5     # neutral default

        if spectral_observable is not None:
            try:
                from ..domains.physical_field.substrate_state import SubstrateState
                sub = SubstrateState.from_spectral_observable(spectral_observable)
                substrate_ctx         = sub.to_agent_context()
                coordination_capacity = sub.coordination_capacity
                memory_persist        = min(1.0, sub.decay_timescale / 6.0)
            except Exception:
                # Fall back to minimal extraction from the observable directly
                fp = float(getattr(spectral_observable, "propagating_power_fraction", 0.0))
                fo = float(getattr(spectral_observable, "overdamped_power_fraction", 1.0))
                c_s = fp - fo
                substrate_ctx = {
                    "substrate_c_spectral":      round(c_s, 4),
                    "substrate_f_prop":          round(fp, 4),
                    "substrate_f_over":          round(fo, 4),
                    "substrate_dominant_regime": spectral_regime,
                    "substrate_coordination":    round(0.5 * (1.0 + c_s), 4),
                }
                coordination_capacity = 0.5 * (1.0 + c_s)

        return EntityContext(
            entity_id=str(entity_id.value),
            name=name,
            entity_type=entity_type,
            role=role,
            occupation=occupation,
            location=location,
            inventory=inventory,
            relationships=relationships,
            current_goals=current_goals,
            needs=needs,
            nearby_entities=nearby_entities,
            recent_events=recent_events,
            environment=environment,
            transport_regime=transport_regime,
            q_regime=q_regime,
            spectral_regime=spectral_regime,
            spectral_dominant_k=spectral_dominant_k,
            substrate=substrate_ctx,
            coordination_capacity=coordination_capacity,
            memory_persistence_factor=memory_persist,
            current_tick=current_tick,
        )

    def build_prompt(self, context: EntityContext) -> str:
        """Build a prompt for LLM reasoning from entity context."""
        prompt = f"""You are {context.name}, a {context.role} and {context.occupation} in a simulation world.

Current Situation:
- Location: {context.location}
- Current tick: {context.current_tick}

Your Needs:
"""
        for need_name, need_value in context.needs.items():
            prompt += f"- {need_name}: {need_value:.2f}\n"

        prompt += "\nYour Inventory:\n"
        if context.inventory:
            for item_name in context.inventory:
                prompt += f"- {item_name}\n"
        else:
            prompt += "- Empty\n"

        prompt += "\nNearby Entities:\n"
        for ent in (context.nearby_entities or ()):
            prompt += f"- {ent}\n"
        if not context.nearby_entities:
            prompt += "- None\n"

        prompt += "\nCurrent Goals:\n"
        for g in (context.current_goals or ()):
            prompt += f"- {g}\n"
        if not context.current_goals:
            prompt += "- None\n"

        prompt += "\nRecent Events:\n"
        for ev in (context.recent_events or ()):
            prompt += f"- {ev}\n"
        if not context.recent_events:
            prompt += "- None\n"

        prompt += "\nEnvironment:\n"
        for key, val in context.environment.items():
            prompt += f"- {key}: {val}\n"

        # Substrate state block — give agent a physical reading of the world
        c_s   = context.substrate.get("substrate_c_spectral", 0.0)
        coord = context.substrate.get("substrate_coordination", 0.5)
        regime = context.substrate.get("substrate_dominant_regime", context.spectral_regime)
        prompt += f"""
Substrate State:
- Coherence score (C_spectral): {c_s:.3f}  [-1=overdamped, +1=coherent]
- Propagating fraction: {context.substrate.get("substrate_f_prop", 0.0):.3f}
- Overdamped fraction:  {context.substrate.get("substrate_f_over", 1.0):.3f}
- Dominant regime: {regime}
- Coordination capacity: {coord:.3f}  [0=low, 1=high]
- Memory persistence factor: {context.memory_persistence_factor:.3f}

"""
        prompt += "Based on your situation and substrate conditions, what do you want to do?\n"
        prompt += "Provide a single sentence describing your intent and reasoning.\n"
        return prompt

    # ------------------------------------------------------------------

    def _find_nearby_entities(self, entity_id, location, entities):
        nearby = []
        for ek, ed in entities.items():
            if ek == str(entity_id.value):
                continue
            loc = str(dict(ed.get("components", {})).get("TransformComponent", {}).get("room", ""))
            if loc == location:
                nearby.append(str(ed.get("display_name", ed.get("name", "Unknown"))))
        return tuple(nearby)

    def _extract_recent_events(self, agent_memory, limit=5):
        if agent_memory is None:
            return ()
        records = sorted(agent_memory.records.values(), key=lambda r: r.timestamp, reverse=True)
        return tuple(str(r.content) for r in records[:limit])

    def _extract_environment(self, location, world_state):
        env = {"location": location}
        agriculture = dict(world_state.get("agriculture", {}))
        if location in agriculture:
            env["agriculture"] = agriculture[location]
        production = dict(world_state.get("production_facilities", {}))
        if location in production:
            env["production"] = production[location]
        return env


@dataclass
class ContextBuilder:
    """Build entity contexts from simulation state."""
    
    def build_context(
        self,
        entity_id: EntityId,
        entity_data: Mapping[str, Any],
        world_state: Mapping[str, Any],
        agent_memory: AgentMemory | None = None,
        transport_observation: Any = None,
        spectral_observable: Any = None,
        current_tick: int = 0,
    ) -> EntityContext:
        """
        Build context for a single entity.

        Args:
            entity_id: Entity ID
            entity_data: Entity data from world state
            world_state: Full world state
            agent_memory: Agent's memory for recent events
            transport_observation: Q transport observation
            spectral_observable: Spectral transport observable from physical field
            current_tick: Current simulation tick

        Returns:
            EntityContext with all relevant information
        """
        # Extract entity information
        entity_type = str(entity_data.get("type", "unknown"))
        name = str(entity_data.get("display_name", entity_data.get("name", "Unknown")))
        metadata = dict(entity_data.get("metadata", {}))
        
        # Extract role and occupation
        role = str(metadata.get("role", "villager"))
        occupation = str(metadata.get("occupation", "farmer"))
        
        # Extract location
        components = dict(entity_data.get("components", {}))
        transform_comp = dict(components.get("TransformComponent", {}))
        location = str(transform_comp.get("room", "unknown"))
        
        # Extract inventory
        inventory_comp = dict(components.get("InventoryComponent", {}))
        items_data = inventory_comp.get("items", [])
        # Handle both list and dict formats for items
        if isinstance(items_data, list):
            inventory = {str(i): 1 for i in items_data}  # Convert list to dict with counts
        elif isinstance(items_data, dict):
            inventory = dict(items_data)
        else:
            inventory = {}
        
        # Extract needs
        needs_comp = dict(components.get("NeedsComponent", {}))
        needs_dict = dict(needs_comp.get("needs", {}))
        needs = {k: float(v) for k, v in needs_dict.items()}
        
        # Extract relationships
        relationship_comp = dict(components.get("RelationshipComponent", {}))
        relationships_data = relationship_comp.get("relationships", {})
        # Handle different relationship data formats
        if isinstance(relationships_data, dict):
            relationships = dict(relationships_data)
        else:
            relationships = {}
        
        # Extract current goals (from entity metadata or world state)
        current_goals = tuple(metadata.get("current_goals", []))
        
        # Find nearby entities
        nearby_entities = self._find_nearby_entities(
            entity_id,
            location,
            world_state.get("entities", {})
        )
        
        # Extract recent events from memory
        recent_events = self._extract_recent_events(agent_memory, limit=5)
        
        # Extract environment
        environment = self._extract_environment(location, world_state)
        
        # Extract transport regime
        transport_regime = "unknown"
        q_regime = "unknown"
        if transport_observation is not None:
            transport_regime = str(getattr(transport_observation, "regime", "unknown"))
            q_regime = str(getattr(transport_observation, "regime", "unknown"))

        # Extract spectral regime from physical field
        spectral_regime = "unknown"
        spectral_dominant_k = 0.0
        if spectral_observable is not None:
            spectral_regime = str(getattr(spectral_observable, "dominant_regime", "unknown"))
            spectral_dominant_k = float(getattr(spectral_observable, "dominant_k", 0.0))

        return EntityContext(
            entity_id=str(entity_id.value),
            name=name,
            entity_type=entity_type,
            role=role,
            occupation=occupation,
            location=location,
            inventory=inventory,
            relationships=relationships,
            current_goals=current_goals,
            needs=needs,
            nearby_entities=nearby_entities,
            recent_events=recent_events,
            environment=environment,
            transport_regime=transport_regime,
            q_regime=q_regime,
            spectral_regime=spectral_regime,
            spectral_dominant_k=spectral_dominant_k,
            current_tick=current_tick,
        )
    
    def build_prompt(self, context: EntityContext) -> str:
        """
        Build a prompt for LLM reasoning from entity context.
        
        Args:
            context: EntityContext with all relevant information
            
        Returns:
            Prompt string for LLM
        """
        prompt = f"""You are {context.name}, a {context.role} and {context.occupation} in a simulation world.

Current Situation:
- Location: {context.location}
- Current tick: {context.current_tick}

Your Needs:
"""
        for need_name, need_value in context.needs.items():
            prompt += f"- {need_name}: {need_value:.2f}\n"
        
        prompt += f"\nYour Inventory:\n"
        if context.inventory:
            for item_name, item_data in context.inventory.items():
                prompt += f"- {item_name}\n"
        else:
            prompt += "- Empty\n"
        
        prompt += f"\nNearby Entities:\n"
        if context.nearby_entities:
            for entity_name in context.nearby_entities:
                prompt += f"- {entity_name}\n"
        else:
            prompt += "- None\n"
        
        prompt += f"\nCurrent Goals:\n"
        if context.current_goals:
            for goal in context.current_goals:
                prompt += f"- {goal}\n"
        else:
            prompt += "- None\n"
        
        prompt += f"\nRecent Events:\n"
        if context.recent_events:
            for event in context.recent_events:
                prompt += f"- {event}\n"
        else:
            prompt += "- None\n"
        
        prompt += f"\nEnvironment:\n"
        for key, value in context.environment.items():
            prompt += f"- {key}: {value}\n"

        prompt += f"\nTransport Regime: {context.transport_regime}\n"
        prompt += f"Q Regime: {context.q_regime}\n"
        prompt += f"Spectral Regime: {context.spectral_regime}\n"
        prompt += f"Spectral Dominant K: {context.spectral_dominant_k:.4f}\n"

        prompt += """
Based on your current situation, needs, and environment, what do you want to do?

Provide your response as a single sentence describing your intent and reasoning.
"""
        return prompt
    
    def _find_nearby_entities(
        self,
        entity_id: EntityId,
        location: str,
        entities: Mapping[str, Any]
    ) -> tuple[str, ...]:
        """Find entities in the same location."""
        nearby = []
        for entity_key, entity_data in entities.items():
            if entity_key == str(entity_id.value):
                continue
            entity_location = str(
                dict(entity_data.get("components", {}))
                .get("TransformComponent", {})
                .get("room", "unknown")
            )
            if entity_location == location:
                name = str(entity_data.get("name", "Unknown"))
                nearby.append(name)
        return tuple(nearby)
    
    def _extract_recent_events(
        self,
        agent_memory: AgentMemory | None,
        limit: int = 5
    ) -> tuple[str, ...]:
        """Extract recent events from agent memory."""
        if agent_memory is None:
            return ()
        records = list(agent_memory.records.values())
        # Sort by timestamp descending
        records.sort(key=lambda r: r.timestamp, reverse=True)
        # Take most recent
        recent = records[:limit]
        return tuple(str(r.content) for r in recent)
    
    def _extract_environment(
        self,
        location: str,
        world_state: Mapping[str, Any]
    ) -> Mapping[str, Any]:
        """Extract environment information for location."""
        # Extract location-specific information from world state
        environment = {
            "location": location,
        }
        
        # Add agriculture data if available
        agriculture = dict(world_state.get("agriculture", {}))
        if location in agriculture:
            environment["agriculture"] = agriculture[location]
        
        # Add production data if available
        production = dict(world_state.get("production_facilities", {}))
        if location in production:
            environment["production"] = production[location]
        
        return environment
