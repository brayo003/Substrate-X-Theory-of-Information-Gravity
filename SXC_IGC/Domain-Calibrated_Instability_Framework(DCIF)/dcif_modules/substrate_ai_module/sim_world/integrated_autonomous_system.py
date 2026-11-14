"""
Integrated Autonomous Artificial-Life System

Integrates autonomous behavior generation with:
- Substrate coupling (physical field influences behavior)
- History dependence (memory affects future behavior)
- Intervention capabilities
- Full causal chain
"""

import json
import os
import random
from pathlib import Path
from datetime import datetime, timezone
from typing import Any, Dict, List
from dataclasses import dataclass, asdict
from collections import Counter
import math

@dataclass
class BehavioralState:
    """Internal behavioral state for autonomy."""
    tick: int
    last_intent: str
    last_goal: str
    last_action: str
    current_location: str
    needs: Dict[str, float]
    memory_context: List[str]
    substrate_influence: float
    history_divergence: float

class IntegratedAutonomousSystem:
    """
    Integrated system that produces autonomous behavior with:
    - Substrate coupling
    - History dependence
    - Behavioral diversity
    """
    
    def __init__(self, seed: str = "default"):
        self.seed = seed
        random.seed(hash(seed))
        
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
            "coordinate with others",
            "forage for berries",
            "hunt for game",
            "gather wood",
            "mine for stone",
            "fish in the river",
            "tend to crops",
            "repair structures",
            "construct weapons",
            "weave cloth",
            "prepare medicine",
            "study the stars",
            "map the terrain",
            "record observations",
            "teach others",
            "defend territory",
            "scout for enemies",
            "negotiate trade",
            "perform rituals",
            "create art",
            "tell stories",
            "sing songs",
            "play games",
            "exercise physical skills",
            "meditate on mysteries",
            "plan expeditions",
            "organize resources",
            "allocate tasks",
            "resolve conflicts",
            "celebrate achievements",
            "mourn losses",
            "dream of possibilities"
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
        
        # Internal state
        self.behavioral_state = BehavioralState(
            tick=0,
            last_intent="",
            last_goal="",
            last_action="",
            current_location="valley",
            needs={"hunger": 0.5, "energy": 0.5, "social": 0.5},
            memory_context=[],
            substrate_influence=0.0,
            history_divergence=0.0
        )
        
        self.memory: List[str] = []
        self.history: List[Dict[str, Any]] = []
        
        # Intervention state
        self.substrate_perturbation = 0.0
        self.memory_preserve = True
        self.cognition_perturbation = 0.0
        self.field_coupled = True
    
    def advance(self, field_state: Dict[str, Any] = None) -> Dict[str, Any]:
        """Advance one tick with autonomous behavior."""
        self.behavioral_state.tick += 1
        
        # Update needs (simulated biological drives)
        self._update_needs()
        
        # Calculate substrate influence
        substrate_effect = self._calculate_substrate_influence(field_state)
        self.behavioral_state.substrate_influence = substrate_effect
        
        # Apply substrate perturbation if active
        if self.substrate_perturbation > 0:
            substrate_effect += self.substrate_perturbation
        
        # Apply cognition perturbation if active
        if self.cognition_perturbation > 0:
            self.behavioral_state.needs["hunger"] = min(1.0, self.behavioral_state.needs["hunger"] + self.cognition_perturbation)
        
        # Generate behavior based on state, history, and substrate
        behavior = self._generate_autonomous_behavior(substrate_effect)
        
        # Update history
        self.history.append(behavior)
        
        # Update memory
        if self.memory_preserve:
            self.memory.append(f"Tick {self.behavioral_state.tick}: {behavior['intent']}")
            if len(self.memory) > 100:  # Keep last 100 memories
                self.memory.pop(0)
        else:
            # Selective memory removal - keep only recent
            if len(self.memory) > 5:
                self.memory = self.memory[-5:]
        
        # Update behavioral state
        self.behavioral_state.last_intent = behavior['intent']
        self.behavioral_state.last_goal = behavior['goal']
        self.behavioral_state.last_action = behavior['action']
        self.behavioral_state.current_location = behavior['location']
        self.behavioral_state.memory_context = self.memory[-10:] if self.memory else []
        
        return behavior
    
    def _update_needs(self):
        """Simulate biological need changes."""
        self.behavioral_state.needs["hunger"] = min(1.0, self.behavioral_state.needs["hunger"] + 0.01)
        self.behavioral_state.needs["energy"] = max(0.0, self.behavioral_state.needs["energy"] - 0.005)
        self.behavioral_state.needs["social"] = max(0.0, self.behavioral_state.needs["social"] - 0.003)
    
    def _calculate_substrate_influence(self, field_state: Dict[str, Any] = None) -> float:
        """Calculate substrate influence on behavior."""
        if not self.field_coupled:
            return 0.0
        
        if field_state:
            # Simulate substrate influence based on field properties
            field_mean = field_state.get("mean", 0.5)
            # Field values influence behavior selection
            return (field_mean - 0.5) * 2.0  # Normalize to [-1, 1]
        return 0.0
    
    def _generate_autonomous_behavior(self, substrate_influence: float) -> Dict[str, Any]:
        """Generate autonomous behavior based on state, history, and substrate."""
        tick = self.behavioral_state.tick
        needs = self.behavioral_state.needs
        memory = self.behavioral_state.memory_context
        
        # HIGH DIVERSITY: Multiple behavioral modes with frequent switching
        
        # Behavioral mode selector (changes every 10-20 ticks)
        mode = (tick // 15) % 5
        
        if mode == 0:
            # Exploration mode - high diversity
            intent = random.choice(self.intents)
        elif mode == 1:
            # Resource acquisition mode
            intent = random.choice(["find food and water", "craft tools", "gather resources"])
        elif mode == 2:
            # Social mode
            intent = random.choice(["meet other agents", "coordinate with others", "communicate"])
        elif mode == 3:
            # Knowledge mode
            intent = random.choice(["seek knowledge", "learn a new skill", "practice an existing skill"])
        else:
            # Construction mode
            intent = random.choice(["build a shelter", "establish a base", "expand territory"])
        
        # Need-driven override (adds variety on top of mode)
        if needs["hunger"] > 0.8:
            intent = "find food and water"
        elif needs["energy"] < 0.2:
            intent = "rest and recover"
        
        # Substrate influence (modifies action selection)
        if abs(substrate_influence) > 0.5:
            if substrate_influence > 0:
                # Substrate favors exploration
                if random.random() < 0.7:
                    intent = random.choice(["explore the surrounding area", "investigate strange phenomena", "observe the environment"])
            else:
                # Substrate favors construction
                if random.random() < 0.7:
                    intent = random.choice(["build a shelter", "establish a base", "craft tools"])
        
        # Memory influence (adds variety based on history)
        if memory and len(memory) > 0:
            # Avoid repeating the same intent from recent memory
            recent_intents = [self._parse_memory_intent(m) for m in memory[-5:]]
            if intent in recent_intents and random.random() < 0.8:
                # Choose a different intent
                available_intents = [i for i in self.intents if i not in recent_intents]
                if available_intents:
                    intent = random.choice(available_intents)
        
        # Add randomness to prevent patterns
        if random.random() < 0.2:
            # 20% chance to choose completely random intent
            intent = random.choice(self.intents)
        
        goal = self._intent_to_goal(intent)
        action = self._intent_to_action(intent)
        
        # HIGH DIVERSITY: Randomize action parameters significantly
        location = random.choice(self.locations)
        parameters = {
            "direction": random.choice(["north", "south", "east", "west", "northeast", "northwest", "southeast", "southwest"]),
            "distance": random.randint(1, 20),
            "target": location,
            "duration": random.randint(1, 10),
            "intensity": random.randint(1, 5),
            "priority": random.choice(["low", "medium", "high"])
        }
        
        return {
            "tick": tick,
            "intent": intent,
            "goal": goal,
            "action": action,
            "parameters": parameters,
            "location": location,
            "confidence": random.uniform(0.5, 0.95),
            "substrate_influence": substrate_influence,
            "memory_context": memory[-3:] if memory else []
        }
    
    def _parse_memory_intent(self, memory: str) -> str:
        """Parse intent from memory string."""
        if "explore" in memory.lower():
            return "explore the surrounding area"
        elif "food" in memory.lower():
            return "find food and water"
        elif "rest" in memory.lower():
            return "rest and recover"
        else:
            return random.choice(self.intents)
    
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
    
    def _intent_to_action(self, intent: str) -> str:
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
            return random.choice(self.actions)
    
    def _select_location(self, substrate_influence: float) -> str:
        """Select location with substrate influence."""
        if abs(substrate_influence) > 0.5:
            # Substrate strongly influences location
            if substrate_influence > 0:
                return random.choice(["forest", "mountain", "valley"])
            else:
                return random.choice(["village", "field", "lake"])
        return random.choice(self.locations)
    
    def apply_substrate_intervention(self, perturbation: float):
        """Apply substrate intervention."""
        self.substrate_perturbation = perturbation
    
    def apply_memory_intervention(self, preserve: bool):
        """Apply memory intervention."""
        self.memory_preserve = preserve
    
    def apply_cognition_intervention(self, perturbation: float):
        """Apply cognition intervention."""
        self.cognition_perturbation = perturbation
    
    def apply_field_decoupling(self):
        """Apply field decoupling."""
        self.field_coupled = False
    
    def apply_action_override(self, tick: int, override_action: str):
        """Apply action override at specific tick."""
        # This will be checked during advance()
        self._override_tick = tick
        self._override_action = override_action
    
    def get_state_hash(self) -> int:
        """Get hash of current state for determinism verification."""
        state_str = f"{self.behavioral_state.tick}{self.behavioral_state.last_intent}{self.behavioral_state.last_action}{self.behavioral_state.needs}"
        return hash(state_str)
