"""
Comprehensive Behavioral Telemetry

Captures all semantic behavioral data required for open-endedness analysis.
"""

import json
import os
from pathlib import Path
from datetime import datetime, timezone
from typing import Any, Dict, List
from dataclasses import dataclass, asdict

@dataclass
class BehavioralTick:
    """Complete semantic behavioral record for one tick."""
    tick: int
    timestamp: str
    
    # Substrate
    field_mean: float
    field_std: float
    spectral_regime: str
    spectral_dominant_k: float
    spectral_dominant_D: float
    
    # Entity
    entity_id: str
    entity_type: str
    entity_location: str
    entity_needs: Dict[str, float]
    
    # Context
    context_summary: str
    
    # Reasoning
    reasoning_prompt: str
    reasoning_response: str
    reasoning_model: str
    
    # Intent
    intent_text: str
    intent_reasoning: str
    intent_confidence: float
    
    # Goal
    goal_subject: str
    goal_kind: str
    goal_priority: str
    
    # Plan
    plan_capabilities: List[str]
    plan_depth: int
    plan_total_cost: float
    
    # Action
    action_type: str
    action_parameters: Dict[str, Any]
    action_success: bool
    
    # World mutation
    world_changes: List[str]
    
    # Memory
    memory_writes: List[str]
    memory_recalls: List[str]

class BehavioralTelemetry:
    """Captures and stores behavioral telemetry."""
    
    def __init__(self, output_dir: Path):
        self.output_dir = output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.current_file = self.output_dir / f"behavioral_trace_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}.jsonl"
        self.ticks: List[BehavioralTick] = []
    
    def record_tick(self, tick: BehavioralTick):
        """Record a behavioral tick."""
        self.ticks.append(tick)
        # Append to file immediately for durability
        with open(self.current_file, 'a') as f:
            f.write(json.dumps(asdict(tick)) + '\n')
    
    def save_summary(self):
        """Save summary statistics."""
        summary = {
            "total_ticks": len(self.ticks),
            "unique_intents": len(set(t.intent_text for t in self.ticks)),
            "unique_goals": len(set(t.goal_subject for t in self.ticks)),
            "unique_actions": len(set(t.action_type for t in self.ticks)),
            "intent_diversity": self._diversity([t.intent_text for t in self.ticks]),
            "goal_diversity": self._diversity([t.goal_subject for t in self.ticks]),
            "action_diversity": self._diversity([t.action_type for t in self.ticks]),
        }
        
        summary_file = self.output_dir / "behavioral_summary.json"
        with open(summary_file, 'w') as f:
            json.dump(summary, f, indent=2)
    
    def _diversity(self, sequence: List[str]) -> float:
        """Calculate Shannon entropy of sequence."""
        if not sequence:
            return 0.0
        
        from collections import Counter
        import math
        
        counts = Counter(sequence)
        total = len(sequence)
        entropy = 0.0
        
        for count in counts.values():
            p = count / total
            if p > 0:
                entropy -= p * math.log2(p)
        
        # Normalize by log of alphabet size
        max_entropy = math.log2(len(counts)) if len(counts) > 1 else 1.0
        return entropy / max_entropy if max_entropy > 0 else 0.0

# Global telemetry instance
_telemetry: BehavioralTelemetry = None

def init_telemetry(output_dir: Path):
    """Initialize global telemetry."""
    global _telemetry
    _telemetry = BehavioralTelemetry(output_dir)

def get_telemetry() -> BehavioralTelemetry:
    """Get global telemetry instance."""
    return _telemetry
