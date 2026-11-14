"""
Simple Behavioral Generator

Rule-based autonomous behavior generator for immediate behavioral diversity.
This replaces the LLM backend to produce actual autonomous behavior now.
"""

from dataclasses import dataclass
from typing import Any, Dict, List
import random

@dataclass
class GeneratedIntent:
    """Generated intent from rule-based system."""
    intent: str
    reasoning: str
    confidence: float
    possible_target: str = None
    possible_destination: str = None
    possible_interaction: str = None

class SimpleBehavioralGenerator:
    """Rule-based behavioral generator for autonomous diversity."""
    
    def __init__(self):
        self.action_types = [
            "Walk", "Run", "Sit", "Stand", "Sleep", "Eat", "Drink", 
            "Explore", "Observe", "Interact", "Work", "Rest", "Gather",
            "Craft", "Build", "Trade", "Communicate", "Meditate", "Practice"
        ]
        
        self.locations = [
            "valley", "forest", "river", "mountain", "village", "field",
            "cave", "lake", "path", "clearing", "shore", "hill", "valley_center"
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
        
        self.tick_counter = 0
        self.last_action = None
        self.last_location = None
    
    def generate(self, entity_id: str, tick: int, context: Dict[str, Any]) -> GeneratedIntent:
        """Generate autonomous behavior based on context and history."""
        self.tick_counter += 1
        
        # Introduce behavioral variety through state-dependent decisions
        needs = context.get("needs", {})
        location = context.get("location", "valley")
        
        # Behavioral state machine
        if self.tick_counter % 10 == 0:
            # Every 10 ticks, consider changing behavior
            intent = random.choice(self.intents)
            reasoning = f"Decided to {intent} after consideration"
        elif needs.get("hunger", 0) > 0.7:
            intent = "find food and water"
            reasoning = "Feeling hungry, need to acquire food"
        elif needs.get("energy", 1.0) < 0.3:
            intent = "rest and recover"
            reasoning = "Low energy, need to rest"
        elif self.last_action and random.random() < 0.3:
            # Sometimes continue previous action
            intent = self.last_action
            reasoning = f"Continuing previous activity: {intent}"
        else:
            # Explore new possibilities
            intent = random.choice(self.intents)
            reasoning = f"Exploring new opportunity: {intent}"
        
        # Generate corresponding goal
        goal = self._intent_to_goal(intent)
        
        # Select action
        action = self._intent_to_action(intent, location)
        
        self.last_action = intent
        self.last_location = location
        
        return GeneratedIntent(
            intent=intent,
            reasoning=reasoning,
            confidence=random.uniform(0.6, 0.9),
            possible_target=goal,
            possible_destination=random.choice(self.locations) if location != random.choice(self.locations) else None,
            possible_interaction=action
        )
    
    def _intent_to_goal(self, intent: str) -> str:
        """Map intent to goal."""
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
        else:
            return random.choice(self.goals)
    
    def _intent_to_action(self, intent: str, location: str) -> str:
        """Map intent to action."""
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
        else:
            return random.choice(self.action_types)

# Global generator
_generator: SimpleBehavioralGenerator = None

def get_generator() -> SimpleBehavioralGenerator:
    """Get global generator instance."""
    global _generator
    if _generator is None:
        _generator = SimpleBehavioralGenerator()
    return _generator
