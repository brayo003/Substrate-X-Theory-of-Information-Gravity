"""
Reasoning Coordinator - Integrates LLM reasoning with performance optimizations

This module coordinates the LLM reasoning process with:
- Reasoning cooldown (don't query every entity every tick)
- Event-triggered reasoning (only reason when necessary)
- Importance thresholds (only reason for important entities/situations)
- Prompt caching (reuse prompts for similar contexts)
- Response caching (reuse LLM responses)
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Mapping
from datetime import datetime, timezone, timedelta
from collections import OrderedDict

from ..core.ids import EntityId, RevisionId, TickId, WorldId
from .llm_service import LLMService
from .context_builder import ContextBuilder
from .intent_generator import IntentGenerator
from .intent_translator import IntentTranslator
from .intent_schema import Intent, IntentBatch
from .reasoning_cycle_tracker import ReasoningCycle, ReasoningCycleTracker


@dataclass(frozen=True, slots=True)
class ReasoningCooldown:
    """Cooldown settings for entity reasoning."""
    entity_id: str
    last_reasoned_tick: int
    last_reasoned_time: datetime
    cooldown_ticks: int = 10  # Minimum ticks between reasoning
    cooldown_seconds: float = 60.0  # Minimum seconds between reasoning


@dataclass
class ReasoningCoordinator:
    """Coordinate LLM reasoning with performance optimizations."""
    
    world_id: WorldId
    llm_service: LLMService = field(default_factory=LLMService)
    context_builder: ContextBuilder = field(default_factory=ContextBuilder)
    
    # Caching
    prompt_cache: OrderedDict[str, str] = field(default_factory=OrderedDict)
    response_cache: OrderedDict[str, Intent] = field(default_factory=OrderedDict)
    max_cache_size: int = 100
    
    # Cooldown tracking
    cooldowns: dict[str, ReasoningCooldown] = field(default_factory=dict)
    
    # Reasoning cycle tracking
    cycle_tracker: ReasoningCycleTracker = field(init=False, repr=False)
    
    def __post_init__(self):
        self.cycle_tracker = ReasoningCycleTracker(world_id=str(self.world_id.value))
        self.intent_generator = IntentGenerator(self.world_id, cycle_tracker=self.cycle_tracker)
        self.intent_translator = IntentTranslator(self.world_id)
        
        # Performance settings (instance variables)
        self.reasoning_cooldown_ticks = 20  # 20 ticks between reasoning for production
        self.reasoning_cooldown_seconds = 60.0  # 60 seconds between reasoning for production
        self.max_entities_per_tick = 5  # Limit concurrent LLM calls
        self.importance_threshold = 0.5  # Only reason if needs/importance exceeds threshold
    
    def set_importance_threshold(self, threshold: float) -> None:
        """Set the importance threshold for entity reasoning."""
        self.importance_threshold = threshold
    
    def should_reason_entity(
        self,
        entity_id: EntityId,
        entity_data: Mapping[str, Any],
        current_tick: int,
    ) -> bool:
        """
        Determine if an entity should reason this tick.
        
        Args:
            entity_id: Entity ID
            entity_data: Entity data
            current_tick: Current simulation tick
            
        Returns:
            True if entity should reason, False otherwise
        """
        entity_key = str(entity_id.value)
        
        # Check cooldown
        if entity_key in self.cooldowns:
            cooldown = self.cooldowns[entity_key]
            ticks_since = current_tick - cooldown.last_reasoned_tick
            time_since = (datetime.now(timezone.utc) - cooldown.last_reasoned_time).total_seconds()
            
            if ticks_since < self.reasoning_cooldown_ticks or time_since < self.reasoning_cooldown_seconds:
                return False
        
        # Check importance threshold
        components = dict(entity_data.get("components", {}))
        needs_comp = dict(components.get("NeedsComponent", {}))
        needs_dict = dict(needs_comp.get("needs", {}))
        
        # Calculate importance based on needs
        importance = 0.0
        for need_name, need_value in needs_dict.items():
            # Higher needs = higher importance
            if need_name in ["hunger", "thirst"]:
                importance += need_value
            elif need_name in ["energy", "warmth", "social"]:
                importance += (1.0 - need_value)  # Lower = more important
        
        importance = importance / len(needs_dict) if needs_dict else 0.0
        
        if importance < self.importance_threshold:
            return False
        
        return True
    
    def update_cooldown(self, entity_id: EntityId, current_tick: int) -> None:
        """Update cooldown for an entity after reasoning."""
        entity_key = str(entity_id.value)
        self.cooldowns[entity_key] = ReasoningCooldown(
            entity_id=entity_key,
            last_reasoned_tick=current_tick,
            last_reasoned_time=datetime.now(timezone.utc),
            cooldown_ticks=self.reasoning_cooldown_ticks,
            cooldown_seconds=self.reasoning_cooldown_seconds,
        )
    
    def generate_intents_for_tick(
        self,
        entities: Mapping[EntityId, Mapping[str, Any]],
        world_state: Mapping[str, Any],
        agent_memories: Mapping[EntityId, Any] | None = None,
        transport_observation: Any = None,
        spectral_observable: Any = None,
        current_tick: int = 0,
        current_revision: RevisionId | None = None,
    ) -> tuple[Any, ...]:
        """
        Generate intentions for entities that should reason this tick.

        Args:
            entities: Mapping of entity IDs to entity data
            world_state: Full world state
            agent_memories: Mapping of entity IDs to agent memories
            transport_observation: Q transport observation
            spectral_observable: Spectral transport observable from physical field
            current_tick: Current simulation tick
            current_revision: Current revision ID

        Returns:
            Tuple of Goals generated from LLM intentions
        """
        # Filter entities that should reason
        entities_to_reason = []
        for entity_id, entity_data in entities.items():
            if self.should_reason_entity(entity_id, entity_data, current_tick):
                entities_to_reason.append((entity_id, entity_data))

        # Limit concurrent LLM calls
        entities_to_reason = entities_to_reason[:self.max_entities_per_tick]

        if not entities_to_reason:
            return ()

        # Generate intentions
        entity_map = {eid: data for eid, data in entities_to_reason}
        intent_batch = self.intent_generator.generate_batch(
            entities=entity_map,
            world_state=world_state,
            agent_memories=agent_memories,
            transport_observation=transport_observation,
            spectral_observable=spectral_observable,
            current_tick=current_tick,
        )

        # Update cooldowns for entities that reasoned
        for entity_id, _ in entities_to_reason:
            self.update_cooldown(entity_id, current_tick)

        # Translate intentions to goals
        translator = IntentTranslator(self.world_id)
        goals = translator.translate_batch(
            intents=intent_batch.intents,
            current_tick=current_tick,
            current_revision=current_revision,
        )

        return goals
    
    def _get_cached_prompt(self, cache_key: str) -> str | None:
        """Get cached prompt."""
        return self.prompt_cache.get(cache_key)
    
    def _cache_prompt(self, cache_key: str, prompt: str) -> None:
        """Cache prompt with LRU eviction."""
        self.prompt_cache[cache_key] = prompt
        if len(self.prompt_cache) > self.max_cache_size:
            self.prompt_cache.popitem(last=False)
    
    def _get_cached_response(self, cache_key: str) -> Intent | None:
        """Get cached response."""
        return self.response_cache.get(cache_key)
    
    def _cache_response(self, cache_key: str, intent: Intent) -> None:
        """Cache response with LRU eviction."""
        self.response_cache[cache_key] = intent
        if len(self.response_cache) > self.max_cache_size:
            self.response_cache.popitem(last=False)
    
    def clear_cache(self) -> None:
        """Clear all caches."""
        self.prompt_cache.clear()
        self.response_cache.clear()
