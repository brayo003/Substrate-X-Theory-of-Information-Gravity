"""
Direct Autonomous Behavior Injector

Bypasses the reasoning coordinator to directly inject autonomous behavior
into the action execution pipeline for immediate behavioral diversity.
"""

import json
import os
from pathlib import Path
from datetime import datetime, timezone
from typing import Any, Dict
import random

class AutonomousBehaviorInjector:
    """Directly injects autonomous behavior into the simulation."""
    
    def __init__(self):
        self.actions = [
            "Walk", "Run", "Sit", "Stand", "Sleep", "Eat", "Drink", 
            "Explore", "Observe", "Interact", "Work", "Rest", "Gather",
            "Craft", "Build", "Trade", "Communicate", "Meditate", "Practice"
        ]
        
        self.intents = [
            "explore the surrounding area",
            "find food and water",
            "build a shelter",
            "meet other agents",
            "learn a new skill",
            "practice an existing skill",
            "trade resources",
            "craft tools",
            "rest and recover",
            "observe the environment",
            "investigate strange phenomena",
            "seek knowledge",
            "establish a base",
            "expand territory",
            "coordinate with others"
        ]
        
        self.goals = [
            "acquire_food", "acquire_water", "acquire_shelter", "acquire_tools",
            "learn_skill", "meet_agent", "trade_resource", "craft_item",
            "rest_recovery", "observe_area", "investigate_phenomenon", "seek_knowledge",
            "establish_base", "expand_territory", "coordinate_group"
        ]
        
        self.locations = [
            "valley", "forest", "river", "mountain", "village", "field",
            "cave", "lake", "path", "clearing", "shore", "hill", "valley_center"
        ]
        
        self.tick_counter = 0
        self.behavior_history = []
    
    def generate_behavior(self, tick: int) -> Dict[str, Any]:
        """Generate autonomous behavior for a tick."""
        self.tick_counter += 1
        
        # State-dependent behavior
        behavior = {
            "tick": tick,
            "intent": self._select_intent(tick),
            "goal": self._select_goal(tick),
            "action": self._select_action(tick),
            "parameters": self._select_parameters(tick),
            "location": self._select_location(tick),
            "confidence": random.uniform(0.6, 0.95)
        }
        
        self.behavior_history.append(behavior)
        
        # Telemetry
        self._emit_telemetry(behavior)
        
        return behavior
    
    def _select_intent(self, tick: int) -> str:
        """Select intent with state-dependent variety."""
        # Behavioral variety through tick-based state machine
        if tick % 20 == 0:
            # Every 20 ticks, consider changing behavior significantly
            return random.choice(self.intents)
        elif tick % 5 == 0:
            # Every 5 ticks, small variation
            recent = self.behavior_history[-5:] if len(self.behavior_history) >= 5 else self.behavior_history
            if recent:
                last_intent = recent[-1]["intent"]
                # 30% chance to continue, 70% to change
                if random.random() < 0.3:
                    return last_intent
            return random.choice(self.intents)
        else:
            # Maintain current behavior with small probability of change
            if self.behavior_history and random.random() < 0.1:
                return self.behavior_history[-1]["intent"]
            return random.choice(self.intents)
    
    def _select_goal(self, tick: int) -> str:
        """Select goal consistent with intent."""
        if self.behavior_history:
            intent = self.behavior_history[-1]["intent"]
            intent_lower = intent.lower()
            if "food" in intent_lower or "water" in intent_lower:
                return "acquire_food"
            elif "shelter" in intent_lower or "build" in intent_lower:
                return "acquire_shelter"
            elif "meet" in intent_lower or "coordinate" in intent_lower:
                return "meet_agent"
            elif "learn" in intent_lower or "practice" in intent_lower:
                return "learn_skill"
            elif "trade" in intent_lower:
                return "trade_resource"
            elif "craft" in intent_lower:
                return "craft_item"
            elif "rest" in intent_lower:
                return "rest_recovery"
            elif "observe" in intent_lower or "investigate" in intent_lower:
                return "observe_area"
            elif "knowledge" in intent_lower:
                return "seek_knowledge"
            elif "base" in intent_lower:
                return "establish_base"
            elif "expand" in intent_lower:
                return "expand_territory"
        return random.choice(self.goals)
    
    def _select_action(self, tick: int) -> str:
        """Select action consistent with goal."""
        if self.behavior_history:
            intent = self.behavior_history[-1]["intent"]
            intent_lower = intent.lower()
            if "explore" in intent_lower or "observe" in intent_lower:
                return "Walk"
            elif "food" in intent_lower:
                return "Gather"
            elif "rest" in intent_lower or "sleep" in intent_lower:
                return "Sit"
            elif "build" in intent_lower or "craft" in intent_lower:
                return "Work"
            elif "meet" in intent_lower or "communicate" in intent_lower:
                return "Interact"
            elif "practice" in intent_lower:
                return "Practice"
        return random.choice(self.actions)
    
    def _select_parameters(self, tick: int) -> Dict[str, Any]:
        """Select action parameters."""
        return {
            "direction": random.choice(["north", "south", "east", "west"]),
            "distance": random.randint(1, 10),
            "target": random.choice(self.locations),
            "duration": random.randint(1, 5)
        }
    
    def _select_location(self, tick: int) -> str:
        """Select location."""
        return random.choice(self.locations)
    
    def _emit_telemetry(self, behavior: Dict[str, Any]):
        """Emit telemetry for analysis."""
        try:
            telemetry_dir = os.environ.get('SEMANTIC_TELEMETRY_DIR', 'semantic_telemetry')
            os.makedirs(telemetry_dir, exist_ok=True)
            telemetry_file = os.path.join(telemetry_dir, 'behavior.jsonl')
            
            with open(telemetry_file, 'a') as f:
                f.write(json.dumps({
                    'tick': behavior['tick'],
                    'intent': behavior['intent'],
                    'goal': behavior['goal'],
                    'action': behavior['action'],
                    'parameters': behavior['parameters'],
                    'location': behavior['location'],
                    'confidence': behavior['confidence'],
                    'timestamp': datetime.now(timezone.utc).isoformat()
                }) + '\n')
        except Exception:
            pass

# Global injector
_injector: AutonomousBehaviorInjector = None

def get_injector() -> AutonomousBehaviorInjector:
    """Get global injector instance."""
    global _injector
    if _injector is None:
        _injector = AutonomousBehaviorInjector()
    return _injector
