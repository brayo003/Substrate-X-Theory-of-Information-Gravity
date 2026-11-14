"""
Reasoning Cycle Tracker - Store and analyze LLM reasoning cycles

This module implements comprehensive tracking of every reasoning cycle with:
- Latency measurements
- Token statistics (input/output)
- Cost statistics
- Full context storage
- Replay capability
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Mapping
from datetime import datetime, timezone
from collections import OrderedDict
import json


def deterministic_hash(seed: str) -> int:
    s = str(seed or "")
    val = hash(s) % (2**32)
    return abs(val)


@dataclass(frozen=True, slots=True)
class ReasoningCycle:
    """Complete record of a single reasoning cycle."""
    cycle_id: str
    entity_id: str
    tick_id: int
    timestamp: datetime
    
    # Context
    context_size: int  # Characters in context
    prompt_size: int  # Characters in prompt
    world_state_snapshot: Mapping[str, Any]  # Relevant world state
    
    # LLM Interaction
    model: str
    temperature: float
    max_tokens: int
    
    # Performance
    latency_ms: float  # Total latency in milliseconds
    context_build_ms: float  # Time to build context
    llm_call_ms: float  # Time for LLM call
    translation_ms: float  # Time to translate intent to goal
    
    # Token Statistics
    input_tokens: int  # Estimated input tokens
    output_tokens: int  # Estimated output tokens
    total_tokens: int
    
    # Cost Statistics
    input_cost: float  # Estimated input cost
    output_cost: float  # Estimated output cost
    total_cost: float
    
    # Results
    intent_text: str
    reasoning_text: str
    confidence: float
    goal_kind: str | None
    goal_target_state: Mapping[str, Any] | None
    
    # Execution
    executed: bool
    succeeded: bool
    rejected: bool
    rejection_reason: str | None
    
    # Long-term Outcomes
    outcome_after_10_ticks: Mapping[str, Any] | None
    outcome_after_100_ticks: Mapping[str, Any] | None
    
    # Metadata
    metadata: Mapping[str, Any]
    
    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "cycle_id": self.cycle_id,
            "entity_id": self.entity_id,
            "tick_id": self.tick_id,
            "timestamp": self.timestamp.isoformat(),
            "context_size": self.context_size,
            "prompt_size": self.prompt_size,
            "world_state_snapshot": dict(self.world_state_snapshot),
            "model": self.model,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
            "latency_ms": self.latency_ms,
            "context_build_ms": self.context_build_ms,
            "llm_call_ms": self.llm_call_ms,
            "translation_ms": self.translation_ms,
            "input_tokens": self.input_tokens,
            "output_tokens": self.output_tokens,
            "total_tokens": self.total_tokens,
            "input_cost": self.input_cost,
            "output_cost": self.output_cost,
            "total_cost": self.total_cost,
            "intent_text": self.intent_text,
            "reasoning_text": self.reasoning_text,
            "confidence": self.confidence,
            "goal_kind": self.goal_kind,
            "goal_target_state": dict(self.goal_target_state) if self.goal_target_state else None,
            "executed": self.executed,
            "succeeded": self.succeeded,
            "rejected": self.rejected,
            "rejection_reason": self.rejection_reason,
            "outcome_after_10_ticks": dict(self.outcome_after_10_ticks) if self.outcome_after_10_ticks else None,
            "outcome_after_100_ticks": dict(self.outcome_after_100_ticks) if self.outcome_after_100_ticks else None,
            "metadata": dict(self.metadata),
        }
    
    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "ReasoningCycle":
        """Reconstruct from dictionary."""
        return cls(
            cycle_id=data["cycle_id"],
            entity_id=data["entity_id"],
            tick_id=data["tick_id"],
            timestamp=datetime.fromisoformat(data["timestamp"]),
            context_size=data["context_size"],
            prompt_size=data["prompt_size"],
            world_state_snapshot=data["world_state_snapshot"],
            model=data["model"],
            temperature=data["temperature"],
            max_tokens=data["max_tokens"],
            latency_ms=data["latency_ms"],
            context_build_ms=data["context_build_ms"],
            llm_call_ms=data["llm_call_ms"],
            translation_ms=data["translation_ms"],
            input_tokens=data["input_tokens"],
            output_tokens=data["output_tokens"],
            total_tokens=data["total_tokens"],
            input_cost=data["input_cost"],
            output_cost=data["output_cost"],
            total_cost=data["total_cost"],
            intent_text=data["intent_text"],
            reasoning_text=data["reasoning_text"],
            confidence=data["confidence"],
            goal_kind=data["goal_kind"],
            goal_target_state=data["goal_target_state"],
            executed=data["executed"],
            succeeded=data["succeeded"],
            rejected=data["rejected"],
            rejection_reason=data["rejection_reason"],
            outcome_after_10_ticks=data["outcome_after_10_ticks"],
            outcome_after_100_ticks=data["outcome_after_100_ticks"],
            metadata=data["metadata"],
        )


@dataclass
class ReasoningCycleTracker:
    """Track and analyze reasoning cycles."""
    
    world_id: str
    cycles: OrderedDict[str, ReasoningCycle] = field(default_factory=OrderedDict)
    max_cycles: int = 10000  # Maximum cycles to store
    
    # Token cost estimates (adjust based on actual model pricing)
    input_cost_per_1k_tokens: float = 0.0001  # $0.0001 per 1K input tokens
    output_cost_per_1k_tokens: float = 0.0002  # $0.0002 per 1K output tokens
    
    def record_cycle(self, cycle: ReasoningCycle) -> None:
        """Record a reasoning cycle."""
        self.cycles[cycle.cycle_id] = cycle
        
        # Enforce max limit with LRU eviction
        if len(self.cycles) > self.max_cycles:
            self.cycles.popitem(last=False)
    
    def get_cycle(self, cycle_id: str) -> ReasoningCycle | None:
        """Get a specific reasoning cycle."""
        return self.cycles.get(cycle_id)
    
    def get_cycles_for_entity(self, entity_id: str) -> tuple[ReasoningCycle, ...]:
        """Get all reasoning cycles for a specific entity."""
        return tuple(cycle for cycle in self.cycles.values() if cycle.entity_id == entity_id)
    
    def get_cycles_for_tick(self, tick_id: int) -> tuple[ReasoningCycle, ...]:
        """Get all reasoning cycles for a specific tick."""
        return tuple(cycle for cycle in self.cycles.values() if cycle.tick_id == tick_id)
    
    def estimate_tokens(self, text: str) -> int:
        """Estimate token count from text (rough approximation)."""
        # Rough approximation: ~4 characters per token
        return len(text) // 4
    
    def calculate_cost(self, input_tokens: int, output_tokens: int) -> tuple[float, float, float]:
        """Calculate cost for tokens."""
        input_cost = (input_tokens / 1000) * self.input_cost_per_1k_tokens
        output_cost = (output_tokens / 1000) * self.output_cost_per_1k_tokens
        total_cost = input_cost + output_cost
        return input_cost, output_cost, total_cost
    
    def get_statistics(self) -> dict[str, Any]:
        """Get overall reasoning statistics."""
        if not self.cycles:
            return {}
        
        cycles_list = list(self.cycles.values())
        
        # Latency statistics
        latencies = [cycle.latency_ms for cycle in cycles_list]
        avg_latency = sum(latencies) / len(latencies)
        max_latency = max(latencies)
        min_latency = min(latencies)
        
        # Token statistics
        input_tokens = [cycle.input_tokens for cycle in cycles_list]
        output_tokens = [cycle.output_tokens for cycle in cycles_list]
        total_tokens = [cycle.total_tokens for cycle in cycles_list]
        
        avg_input_tokens = sum(input_tokens) / len(input_tokens)
        avg_output_tokens = sum(output_tokens) / len(output_tokens)
        avg_total_tokens = sum(total_tokens) / len(total_tokens)
        
        # Cost statistics
        total_cost = sum(cycle.total_cost for cycle in cycles_list)
        
        # Execution statistics
        executed_count = sum(1 for cycle in cycles_list if cycle.executed)
        succeeded_count = sum(1 for cycle in cycles_list if cycle.succeeded)
        rejected_count = sum(1 for cycle in cycles_list if cycle.rejected)
        
        reasoning_success_rate = succeeded_count / len(cycles_list) if cycles_list else 0.0
        execution_rate = executed_count / len(cycles_list) if cycles_list else 0.0
        rejection_rate = rejected_count / len(cycles_list) if cycles_list else 0.0
        
        return {
            "total_cycles": len(cycles_list),
            "latency": {
                "avg_ms": avg_latency,
                "max_ms": max_latency,
                "min_ms": min_latency,
            },
            "tokens": {
                "avg_input_tokens": avg_input_tokens,
                "avg_output_tokens": avg_output_tokens,
                "avg_total_tokens": avg_total_tokens,
            },
            "cost": {
                "total_cost": total_cost,
                "avg_cost_per_cycle": total_cost / len(cycles_list),
            },
            "execution": {
                "reasoning_success_rate": reasoning_success_rate,
                "execution_rate": execution_rate,
                "rejection_rate": rejection_rate,
                "abandoned_plans": executed_count - succeeded_count,
            },
        }
    
    def export_cycles(self, entity_id: str | None = None, tick_id: int | None = None) -> str:
        """Export cycles as JSON."""
        cycles_to_export = []
        
        for cycle in self.cycles.values():
            if entity_id is not None and cycle.entity_id != entity_id:
                continue
            if tick_id is not None and cycle.tick_id != tick_id:
                continue
            cycles_to_export.append(cycle.to_dict())
        
        return json.dumps(cycles_to_export, indent=2)
    
    def import_cycles(self, json_data: str) -> int:
        """Import cycles from JSON."""
        data = json.loads(json_data)
        count = 0
        
        for cycle_data in data:
            cycle = ReasoningCycle.from_dict(cycle_data)
            self.record_cycle(cycle)
            count += 1
        
        return count
    
    def replay_cycle(self, cycle_id: str) -> dict[str, Any]:
        """Get cycle data for replay."""
        cycle = self.get_cycle(cycle_id)
        if cycle is None:
            return {"error": f"Cycle {cycle_id} not found"}
        
        return {
            "cycle": cycle.to_dict(),
            "replay_instructions": {
                "entity_id": cycle.entity_id,
                "world_state": cycle.world_state_snapshot,
                "model": cycle.model,
                "temperature": cycle.temperature,
                "prompt_size": cycle.prompt_size,
                "expected_intent": cycle.intent_text,
                "expected_reasoning": cycle.reasoning_text,
            },
        }
    
    def clear(self) -> None:
        """Clear all cycles."""
        self.cycles.clear()


def _cycle_id(world_id: str, entity_id: str, tick_id: int, timestamp: datetime) -> str:
    """Generate unique cycle ID."""
    seed = f"{world_id}|{entity_id}|{tick_id}|{timestamp.isoformat()}"
    return f"cycle_{deterministic_hash(seed)}"