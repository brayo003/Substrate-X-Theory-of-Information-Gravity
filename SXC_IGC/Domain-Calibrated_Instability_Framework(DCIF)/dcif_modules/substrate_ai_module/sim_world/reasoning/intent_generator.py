from __future__ import annotations

"""
Intent Generator - Generate intentions using LLM

This module uses the LLM service and context builder to generate
intentions for entities. Intentions are high-level descriptions
of what entities want to do, which must be translated into Goals.
"""

import json
import time
from dataclasses import dataclass, field
from typing import Any, Mapping
from datetime import datetime, timezone


def deterministic_hash(seed: str) -> int:
    s = str(seed or "")
    val = hash(s) % (2**32)
    return abs(val)


from ..core.ids import EntityId, TickId, WorldId, RevisionId
from .llm_service import LLMService, LLMRequest
from .context_builder import ContextBuilder, EntityContext
from .intent_schema import Intent, IntentBatch
from .reasoning_cycle_tracker import ReasoningCycle, ReasoningCycleTracker


def _intent_id(world_id: WorldId, entity_id: EntityId, timestamp: datetime) -> str:
    """Generate unique intent ID."""
    seed = f"{world_id.value}|{entity_id.value}|{timestamp.isoformat()}"
    return f"id_{deterministic_hash(seed)}"


def _cycle_id(world_id: WorldId, entity_id: EntityId, tick_id: int, timestamp: datetime) -> str:
    """Generate unique cycle ID."""
    seed = f"{world_id.value}|{entity_id.value}|{tick_id}|{timestamp.isoformat()}"
    return f"cycle_{deterministic_hash(seed)}"


@dataclass
class IntentGenerator:
    """Generate intentions for entities using LLM."""
    
    world_id: WorldId
    llm_service: LLMService = field(default_factory=LLMService)
    context_builder: ContextBuilder = field(default_factory=ContextBuilder)
    cycle_tracker: ReasoningCycleTracker | None = None
    
    def generate_for_entity(
        self,
        entity_id: EntityId,
        entity_data: Mapping[str, Any],
        world_state: Mapping[str, Any],
        agent_memory: Any = None,
        transport_observation: Any = None,
        spectral_observable: Any = None,
        current_tick: int = 0,
    ) -> Intent | None:
        """
        Generate intention for a single entity with full cycle tracking.

        Args:
            entity_id: Entity ID
            entity_data: Entity data from world state
            world_state: Full world state
            agent_memory: Agent's memory
            transport_observation: Q transport observation
            spectral_observable: Spectral transport observable from physical field
            current_tick: Current simulation tick

        Returns:
            Intent if generation successful, None otherwise
        """
        cycle_start = time.time()
        timestamp = datetime.now(timezone.utc)

        # Build context
        context_build_start = time.time()
        context = self.context_builder.build_context(
            entity_id=entity_id,
            entity_data=entity_data,
            world_state=world_state,
            agent_memory=agent_memory,
            transport_observation=transport_observation,
            spectral_observable=spectral_observable,
            current_tick=current_tick,
        )
        context_build_ms = (time.time() - context_build_start) * 1000
        
        # Build prompt
        prompt = self.context_builder.build_prompt(context)
        prompt_size = len(prompt)
        
        # Invoke LLM
        request = LLMRequest(
            prompt=prompt,
            model="qwen2.5-coder:1.5b",
            temperature=0.7,
            max_tokens=512,
            timeout=120,  # Increased from 30 to 120 for longer prompts
        )
        
        llm_call_start = time.time()
        response = self.llm_service.invoke(request)
        llm_call_ms = (time.time() - llm_call_start) * 1000
        
        if not response.success:
            # Log error and record failed cycle
            print(f"LLM invocation failed for entity {entity_id}: {response.error}")
            
            if self.cycle_tracker is not None:
                cycle = ReasoningCycle(
                    cycle_id=_cycle_id(self.world_id, entity_id, current_tick, timestamp),
                    entity_id=str(entity_id.value),
                    tick_id=current_tick,
                    timestamp=timestamp,
                    context_size=len(str(context)),
                    prompt_size=prompt_size,
                    world_state_snapshot={"error": "LLM invocation failed"},
                    model=request.model,
                    temperature=request.temperature,
                    max_tokens=request.max_tokens,
                    latency_ms=(time.time() - cycle_start) * 1000,
                    context_build_ms=context_build_ms,
                    llm_call_ms=llm_call_ms,
                    translation_ms=0.0,
                    input_tokens=self.cycle_tracker.estimate_tokens(prompt),
                    output_tokens=0,
                    total_tokens=self.cycle_tracker.estimate_tokens(prompt),
                    input_cost=0.0,
                    output_cost=0.0,
                    total_cost=0.0,
                    intent_text="",
                    reasoning_text="",
                    confidence=0.0,
                    goal_kind=None,
                    goal_target_state=None,
                    executed=False,
                    succeeded=False,
                    rejected=True,
                    rejection_reason=response.error,
                    outcome_after_10_ticks=None,
                    outcome_after_100_ticks=None,
                    metadata={"error": response.error},
                )
                self.cycle_tracker.record_cycle(cycle)
            
            return None
        
        # Parse response with timing
        translation_start = time.time()
        
        try:
            # Handle simple text response (no JSON)
            text = response.text.strip()
            
            # Try to parse as JSON first (for backward compatibility)
            try:
                if text.startswith("```json"):
                    text = text[7:]
                if text.startswith("```"):
                    text = text[3:]
                if text.endswith("```"):
                    text = text[:-3]
                text = text.strip()
                
                intent_data = json.loads(text)
                
                intent = Intent(
                    intent_id=_intent_id(self.world_id, entity_id, context.timestamp),
                    entity_id=str(entity_id.value),
                    intent=str(intent_data.get("intent", "")),
                    reasoning=str(intent_data.get("reasoning", "")),
                    confidence=float(intent_data.get("confidence", 0.5)),
                    possible_target=intent_data.get("possible_target"),
                    possible_destination=intent_data.get("possible_destination"),
                    possible_interaction=intent_data.get("possible_interaction"),
                    timestamp=context.timestamp,
                    metadata={
                        "model": response.model,
                        "temperature": request.temperature,
                        "location": context.location,
                        "needs": dict(context.needs),
                    },
                )
            except json.JSONDecodeError:
                # If not JSON, treat the entire response as the intent with reasoning
                intent = Intent(
                    intent_id=_intent_id(self.world_id, entity_id, context.timestamp),
                    entity_id=str(entity_id.value),
                    intent=text,
                    reasoning="Generated from natural language response",
                    confidence=0.7,  # Default confidence for NL responses
                    possible_target=None,
                    possible_destination=None,
                    possible_interaction=None,
                    timestamp=context.timestamp,
                    metadata={
                        "model": response.model,
                        "temperature": request.temperature,
                        "location": context.location,
                        "needs": dict(context.needs),
                        "response_format": "natural_language",
                    },
                )
            
            translation_ms = (time.time() - translation_start) * 1000
            total_latency_ms = (time.time() - cycle_start) * 1000
            
            # Calculate token statistics
            input_tokens = self.cycle_tracker.estimate_tokens(prompt) if self.cycle_tracker else len(prompt) // 4
            output_tokens = self.cycle_tracker.estimate_tokens(text) if self.cycle_tracker else len(text) // 4
            total_tokens = input_tokens + output_tokens
            
            # Calculate cost statistics
            if self.cycle_tracker:
                input_cost, output_cost, total_cost = self.cycle_tracker.calculate_cost(input_tokens, output_tokens)
            else:
                input_cost, output_cost, total_cost = 0.0, 0.0, 0.0
            
            # Record reasoning cycle
            if self.cycle_tracker is not None:
                cycle = ReasoningCycle(
                    cycle_id=_cycle_id(self.world_id, entity_id, current_tick, timestamp),
                    entity_id=str(entity_id.value),
                    tick_id=current_tick,
                    timestamp=timestamp,
                    context_size=len(str(context)),
                    prompt_size=prompt_size,
                    world_state_snapshot={"location": context.location, "needs": dict(context.needs)},
                    model=request.model,
                    temperature=request.temperature,
                    max_tokens=request.max_tokens,
                    latency_ms=total_latency_ms,
                    context_build_ms=context_build_ms,
                    llm_call_ms=llm_call_ms,
                    translation_ms=translation_ms,
                    input_tokens=input_tokens,
                    output_tokens=output_tokens,
                    total_tokens=total_tokens,
                    input_cost=input_cost,
                    output_cost=output_cost,
                    total_cost=total_cost,
                    intent_text=intent.intent,
                    reasoning_text=intent.reasoning,
                    confidence=intent.confidence,
                    goal_kind=None,  # Will be set by translator
                    goal_target_state=None,  # Will be set by translator
                    executed=False,  # Will be updated by executor
                    succeeded=False,  # Will be updated by executor
                    rejected=False,
                    rejection_reason=None,
                    outcome_after_10_ticks=None,
                    outcome_after_100_ticks=None,
                    metadata={"intent_id": intent.intent_id},
                )
                self.cycle_tracker.record_cycle(cycle)
            
            # Store intention in agent memory
            if agent_memory is not None:
                try:
                    agent_memory.remember(
                        kind="intention",
                        content={
                            "intent": intent.intent,
                            "reasoning": intent.reasoning,
                            "confidence": intent.confidence,
                        },
                        tick_id=TickId.new(self.world_id, current_tick),
                        revision_id=None,
                        tags=("llm", "reasoning"),
                        confidence=intent.confidence,
                        metadata={"intent_id": intent.intent_id, "cycle_id": _cycle_id(self.world_id, entity_id, current_tick, timestamp) if self.cycle_tracker else None},
                    )
                except Exception as e:
                    print(f"Failed to store intention in memory: {e}")
            
            return intent
        except json.JSONDecodeError as e:
            print(f"Failed to parse LLM response for entity {entity_id}: {e}")
            print(f"Response text: {response.text}")
            
            # Record failed parse cycle
            if self.cycle_tracker is not None:
                cycle = ReasoningCycle(
                    cycle_id=_cycle_id(self.world_id, entity_id, current_tick, timestamp),
                    entity_id=str(entity_id.value),
                    tick_id=current_tick,
                    timestamp=timestamp,
                    context_size=len(str(context)),
                    prompt_size=prompt_size,
                    world_state_snapshot={"error": "JSON parse failed"},
                    model=request.model,
                    temperature=request.temperature,
                    max_tokens=request.max_tokens,
                    latency_ms=(time.time() - cycle_start) * 1000,
                    context_build_ms=context_build_ms,
                    llm_call_ms=llm_call_ms,
                    translation_ms=(time.time() - translation_start) * 1000,
                    input_tokens=self.cycle_tracker.estimate_tokens(prompt),
                    output_tokens=0,
                    total_tokens=self.cycle_tracker.estimate_tokens(prompt),
                    input_cost=0.0,
                    output_cost=0.0,
                    total_cost=0.0,
                    intent_text="",
                    reasoning_text="",
                    confidence=0.0,
                    goal_kind=None,
                    goal_target_state=None,
                    executed=False,
                    succeeded=False,
                    rejected=True,
                    rejection_reason=f"JSON parse error: {e}",
                    outcome_after_10_ticks=None,
                    outcome_after_100_ticks=None,
                    metadata={"error": str(e), "response_text": response.text},
                )
                self.cycle_tracker.record_cycle(cycle)
            
            return None
        except Exception as e:
            print(f"Error creating intent for entity {entity_id}: {e}")
            
            # Record error cycle
            if self.cycle_tracker is not None:
                cycle = ReasoningCycle(
                    cycle_id=_cycle_id(self.world_id, entity_id, current_tick, timestamp),
                    entity_id=str(entity_id.value),
                    tick_id=current_tick,
                    timestamp=timestamp,
                    context_size=len(str(context)),
                    prompt_size=prompt_size,
                    world_state_snapshot={"error": "Intent creation failed"},
                    model=request.model,
                    temperature=request.temperature,
                    max_tokens=request.max_tokens,
                    latency_ms=(time.time() - cycle_start) * 1000,
                    context_build_ms=context_build_ms,
                    llm_call_ms=llm_call_ms,
                    translation_ms=(time.time() - translation_start) * 1000,
                    input_tokens=self.cycle_tracker.estimate_tokens(prompt),
                    output_tokens=0,
                    total_tokens=self.cycle_tracker.estimate_tokens(prompt),
                    input_cost=0.0,
                    output_cost=0.0,
                    total_cost=0.0,
                    intent_text="",
                    reasoning_text="",
                    confidence=0.0,
                    goal_kind=None,
                    goal_target_state=None,
                    executed=False,
                    succeeded=False,
                    rejected=True,
                    rejection_reason=f"Intent creation error: {e}",
                    outcome_after_10_ticks=None,
                    outcome_after_100_ticks=None,
                    metadata={"error": str(e)},
                )
                self.cycle_tracker.record_cycle(cycle)
            
            return None
    
    def generate_batch(
        self,
        entities: Mapping[EntityId, Mapping[str, Any]],
        world_state: Mapping[str, Any],
        agent_memories: Mapping[EntityId, Any] | None = None,
        transport_observation: Any = None,
        spectral_observable: Any = None,
        current_tick: int = 0,
    ) -> IntentBatch:
        """
        Generate intentions for multiple entities.

        Args:
            entities: Mapping of entity IDs to entity data
            world_state: Full world state
            agent_memories: Mapping of entity IDs to agent memories
            transport_observation: Q transport observation
            spectral_observable: Spectral transport observable from physical field
            current_tick: Current simulation tick

        Returns:
            IntentBatch with all generated intentions
        """
        intents = []

        for entity_id, entity_data in entities.items():
            agent_memory = None
            if agent_memories is not None:
                agent_memory = agent_memories.get(entity_id)

            intent = self.generate_for_entity(
                entity_id=entity_id,
                entity_data=entity_data,
                world_state=world_state,
                agent_memory=agent_memory,
                transport_observation=transport_observation,
                spectral_observable=spectral_observable,
                current_tick=current_tick,
            )

            if intent is not None:
                intents.append(intent)

        return IntentBatch(
            intents=tuple(intents),
            timestamp=datetime.now(timezone.utc),
            metadata={
                "total_entities": len(entities),
                "successful_intents": len(intents),
                "current_tick": current_tick,
            },
        )
