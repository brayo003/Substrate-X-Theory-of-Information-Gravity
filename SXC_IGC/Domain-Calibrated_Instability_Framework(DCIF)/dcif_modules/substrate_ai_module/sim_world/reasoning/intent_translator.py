"""
Intent Translator - Convert LLM intentions to Goal objects

This module translates high-level intentions from the LLM into
executable Goal objects that can be processed by the existing
PlannerEngine. It reuses the existing GoalManager and Goal system.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any, Mapping
from datetime import datetime, timezone

from ..core.ids import EntityId, RevisionId, TickId, WorldId
from ..planner.planner_context import Goal
from ..planner.goal_manager import _goal_id
from .intent_schema import Intent


@dataclass
class IntentTranslator:
    """Translate LLM intentions to Goal objects."""
    
    world_id: WorldId
    
    def translate(self, intent: Intent, current_tick: int, current_revision: RevisionId | None = None) -> Goal | None:
        """
        Translate a single intent to a Goal.
        """
        # If intent has structured objective, use it directly for high-level goal planning
        if intent.structured_objective:
            obj = intent.structured_objective
            
            # Extract structured fields
            objective = obj.get("objective")
            desired_outcome = obj.get("desired_outcome", intent.intent)
            priority = int(obj.get("priority", 0.5) * 100)
            constraints = obj.get("constraints", [])
            preferences = obj.get("preferences", {})
            resource_limits = obj.get("resource_limits", {})
            deadline_tick = obj.get("deadline_tick")
            
            # Map objective to target state
            target_state = self._objective_to_target_state(objective, obj)
            
            print(f"[INTENT_TRANSLATOR] Using structured objective: objective={objective}, desired_outcome={desired_outcome}")
            
            return Goal.create(
                world_id=self.world_id,
                subject=desired_outcome,
                kind=objective or "custom",
                entity_id=EntityId.from_uuid(intent.entity_id),
                target_state=target_state,
                priority=priority,
                rationale=intent.reasoning,
                confidence=intent.confidence,
                constraints=constraints,
                deadline_tick=deadline_tick,
                created_tick=current_tick,
                objective=objective,
                desired_outcome=desired_outcome,
                preferences=preferences,
                resource_limits=resource_limits,
                metadata={
                    "intent_id": intent.intent_id,
                    "llm_generated": True,
                    "structured_objective": True,
                    "possible_target": intent.possible_target,
                    "possible_destination": intent.possible_destination,
                }
            )
        
        # Otherwise, use existing keyword-based translation
        goal_kind, target_state, priority = self._analyze_intent(intent)
        
        if goal_kind is None:
            print(f"[INTENT_TRANSLATOR] Failed to translate intent: {intent.intent}")
            return None
        
        print(f"[INTENT_TRANSLATOR] Translated intent to goal_kind={goal_kind}, priority={priority}: {intent.intent}")
        
        return Goal.create(
            world_id=self.world_id,
            subject=intent.intent,
            kind=goal_kind,
            entity_id=EntityId.from_uuid(intent.entity_id),
            target_state=target_state,
            priority=priority,
            rationale=intent.reasoning,
            window_start_tick=None,
            window_end_tick=None,
            horizon_ticks=10,  # Default planning horizon
            provenance={
                "source": "llm",
                "intent_id": intent.intent_id,
                "confidence": intent.confidence,
                "model": intent.metadata.get("model", "unknown"),
            },
            confidence=intent.confidence,
            constraints=(),
            interruption_policy="suspend",
            status="pending",
            created_tick=current_tick,
            created_revision=current_revision,
            metadata={
                "possible_target": intent.possible_target,
                "possible_destination": intent.possible_destination,
                "possible_interaction": intent.possible_interaction,
                "llm_generated": True,
                "intent": intent.intent,
                "reasoning": intent.reasoning,
            },
        )
    
    def _analyze_intent(self, intent: Intent) -> tuple[str | None, Mapping[str, Any], int]:
        """
        Analyze intent to determine goal kind and target state.
        
        Args:
            intent: Intent from LLM
            
        Returns:
            Tuple of (goal_kind, target_state, priority) or (None, {}, 0) if untranslatable
        """
        intent_lower = intent.intent.lower()
        
        # Movement intents
        if any(word in intent_lower for word in ["go to", "move to", "visit", "travel to", "head to"]):
            destination = intent.possible_destination or self._extract_destination(intent_lower)
            if destination:
                return ("movement", {"room": destination}, 10)
        
        # Gathering/harvesting intents
        if any(word in intent_lower for word in ["gather", "harvest", "collect", "pick"]):
            resource = intent.possible_target or self._extract_resource(intent_lower)
            if resource:
                return ("custom", {"action": "harvest", "target": resource}, 15)
        
        # Eating/hunger intents
        if any(word in intent_lower for word in ["eat", "consume", "have food", "hungry", "hunger"]):
            return ("custom", {"action": "eat", "item": "food"}, 12)
        
        # Thirst/drinking intents
        if any(word in intent_lower for word in ["drink", "thirst", "thirsty", "water"]):
            return ("custom", {"action": "drink", "item": "water"}, 12)
        
        # Social intents
        if any(word in intent_lower for word in ["talk to", "speak with", "converse", "meet", "social"]):
            target = intent.possible_target or self._extract_entity(intent)
            if target:
                return ("custom", {"action": "interact", "target": target}, 8)
        
        # Working intents
        if any(word in intent_lower for word in ["work", "job", "task", "maintain", "check"]):
            return ("custom", {"action": "work"}, 9)
        
        # Resting/sleeping intents
        if any(word in intent_lower for word in ["rest", "sleep", "take a break", "replenish", "refuel", "relax"]):
            return ("sleep", {"status": "sleeping"}, 11)
        
        # Content/status intents (accept as valid low-priority goals)
        if any(word in intent_lower for word in ["content", "continue", "will", "satisfied", "feeling"]):
            return ("custom", {"action": "continue"}, 5)
        
        # Warmth/comfort intents
        if any(word in intent_lower for word in ["warmth", "warm", "comfort", "comfortable"]):
            return ("custom", {"action": "maintain_warmth"}, 6)
        
        # Default: accept as generic continue goal (fallback to prevent rejection)
        return ("custom", {"action": "continue"}, 5)
    
    def _extract_destination(self, intent_lower: str) -> str | None:
        """Extract destination from intent text."""
        # Common location keywords
        locations = ["farm", "house", "home", "workshop", "market", "clinic", "forge", "village"]
        for loc in locations:
            if loc in intent_lower:
                return loc
        return None
    
    def _extract_resource(self, intent_lower: str) -> str | None:
        """Extract resource from intent text."""
        # Common resource keywords
        resources = ["food", "wheat", "wood", "stone", "water", "tools"]
        for res in resources:
            if res in intent_lower:
                return res
        return None
    
    def _extract_entity(self, intent: Intent) -> str | None:
        """Extract entity name from intent text."""
        # Try to extract proper nouns (capitalized words)
        words = re.findall(r'\b[A-Z][a-z]+\b', intent.intent)
        if words:
            return words[0]
        return None
    
    def _objective_to_target_state(self, objective: str | None, obj: Mapping[str, Any]) -> Mapping[str, Any]:
        """Map high-level objective to target state."""
        if objective is None:
            return {}
        
        # Map objectives to target states
        objective_mappings = {
            "establish_food_supply": {"food_reserve": obj.get("target_quantity", 50.0)},
            "secure_water_supply": {"water_reserve": obj.get("target_quantity", 30.0)},
            "prepare_for_winter": {
                "warmth": obj.get("warmth_target", 0.8),
                "food_reserve": obj.get("food_target", 100.0)
            },
            "improve_food_reserves": {"food_reserve": obj.get("target_quantity", 75.0)},
            "acquire_required_materials": obj.get("materials", {}),
            "establish_storage": {"storage_capacity": obj.get("capacity", 500.0)},
        }
        
        return objective_mappings.get(objective, {})
    
    def translate_batch(
        self,
        intents: tuple[Intent, ...],
        current_tick: int,
        current_revision: RevisionId | None = None,
    ) -> tuple[Goal, ...]:
        """
        Translate a batch of intents to Goals.
        
        Args:
            intents: Tuple of Intents
            current_tick: Current simulation tick
            current_revision: Current revision ID
            
        Returns:
            Tuple of Goals (untranslatable intents are filtered out)
        """
        goals = []
        
        for intent in intents:
            goal = self.translate(intent, current_tick, current_revision)
            if goal is not None:
                goals.append(goal)
        
        return tuple(goals)
