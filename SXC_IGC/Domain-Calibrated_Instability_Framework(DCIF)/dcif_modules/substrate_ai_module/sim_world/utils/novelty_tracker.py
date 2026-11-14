"""
Novelty Detection Module

Operational novelty measurement system for the open-ended artificial-life simulation.
Tracks four levels of novelty:
1. Action novelty
2. State-transition novelty
3. Environmental-consequence novelty
4. Trajectory novelty
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Set, Tuple
from datetime import datetime
import json
import hashlib


@dataclass(frozen=True, slots=True)
class CanonicalAction:
    """Canonical representation of an executed action"""
    action_type: str
    parameters: Tuple[Tuple[str, Any], ...]  # Sorted key-value pairs
    entity_id: str
    
    def __hash__(self) -> int:
        return hash((self.action_type, self.parameters, self.entity_id))
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "action_type": self.action_type,
            "parameters": dict(self.parameters),
            "entity_id": self.entity_id
        }


@dataclass(frozen=True, slots=True)
class StateTransition:
    """Canonical representation of a state transition"""
    entity_id: str
    pre_state: Tuple[Tuple[str, Any], ...]  # Sorted key-value pairs for hashability
    post_state: Tuple[Tuple[str, Any], ...]  # Sorted key-value pairs for hashability
    tick_number: int
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "entity_id": self.entity_id,
            "pre_state": dict(self.pre_state),
            "post_state": dict(self.post_state),
            "tick_number": self.tick_number
        }


@dataclass(frozen=True, slots=True)
class EnvironmentalConsequence:
    """Canonical representation of an environmental consequence"""
    consequence_type: str
    affected_entities: Tuple[str, ...]
    world_changes: Tuple[Tuple[str, Any], ...]  # Sorted key-value pairs for hashability
    tick_number: int
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "consequence_type": self.consequence_type,
            "affected_entities": self.affected_entities,
            "world_changes": dict(self.world_changes),
            "tick_number": self.tick_number
        }


@dataclass(frozen=True, slots=True)
class Trajectory:
    """Canonical representation of a behavioral trajectory"""
    entity_id: str
    action_sequence: Tuple[CanonicalAction, ...]
    state_sequence: Tuple[StateTransition, ...]
    consequence_sequence: Tuple[EnvironmentalConsequence, ...]
    start_tick: int
    end_tick: int
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "entity_id": self.entity_id,
            "action_sequence": [a.to_dict() for a in self.action_sequence],
            "state_sequence": [s.to_dict() for s in self.state_sequence],
            "consequence_sequence": [c.to_dict() for c in self.consequence_sequence],
            "start_tick": self.start_tick,
            "end_tick": self.end_tick
        }


class NoveltyTracker:
    """Tracks novelty across multiple simulation dimensions"""
    
    def __init__(self):
        self.action_history: Set[CanonicalAction] = set()
        self.state_transition_history: Set[StateTransition] = set()
        self.environmental_consequence_history: Set[EnvironmentalConsequence] = set()
        self.trajectory_history: Set[Trajectory] = set()
        
        self.action_novelty_events: List[Dict[str, Any]] = []
        self.state_transition_novelty_events: List[Dict[str, Any]] = []
        self.environmental_consequence_novelty_events: List[Dict[str, Any]] = []
        self.trajectory_novelty_events: List[Dict[str, Any]] = []
    
    def canonicalize_action(self, action: Dict[str, Any]) -> CanonicalAction:
        """Convert raw action to canonical representation"""
        action_type = action.get("action", "UNKNOWN")
        parameters = action.get("parameters", {})
        entity_id = action.get("entity_id", "UNKNOWN")
        
        # Sort parameters for canonical representation
        sorted_params = tuple(sorted(parameters.items()))
        
        return CanonicalAction(
            action_type=action_type,
            parameters=sorted_params,
            entity_id=entity_id
        )
    
    def canonicalize_state_transition(self, entity_id: str, pre_state: Dict[str, Any], 
                                     post_state: Dict[str, Any], tick_number: int) -> StateTransition:
        """Convert state change to canonical representation"""
        # Extract scientifically relevant variables
        relevant_keys = ["position", "inventory", "needs", "holding", "status"]
        
        pre_relevant = {k: pre_state.get(k) for k in relevant_keys if k in pre_state}
        post_relevant = {k: post_state.get(k) for k in relevant_keys if k in post_state}
        
        # Convert lists to tuples for hashability
        pre_relevant = {k: tuple(v) if isinstance(v, list) else v for k, v in pre_relevant.items()}
        post_relevant = {k: tuple(v) if isinstance(v, list) else v for k, v in post_relevant.items()}
        
        # Convert to sorted tuples for hashability
        pre_tuple = tuple(sorted(pre_relevant.items()))
        post_tuple = tuple(sorted(post_relevant.items()))
        
        return StateTransition(
            entity_id=entity_id,
            pre_state=pre_tuple,
            post_state=post_tuple,
            tick_number=tick_number
        )
    
    def canonicalize_environmental_consequence(self, consequence: Dict[str, Any]) -> EnvironmentalConsequence:
        """Convert environmental consequence to canonical representation"""
        consequence_type = consequence.get("type", "UNKNOWN")
        affected_entities = tuple(consequence.get("affected_entities", []))
        world_changes = consequence.get("world_changes", {})
        tick_number = consequence.get("tick_number", 0)
        
        # Convert world_changes to hashable form
        world_changes_clean = {}
        for k, v in world_changes.items():
            if isinstance(v, list):
                v = tuple(v)
            elif isinstance(v, dict):
                v = tuple(sorted(v.items()))
            world_changes_clean[k] = v
        
        # Convert to sorted tuple for hashability
        world_changes_tuple = tuple(sorted(world_changes_clean.items()))
        
        return EnvironmentalConsequence(
            consequence_type=consequence_type,
            affected_entities=affected_entities,
            world_changes=world_changes_tuple,
            tick_number=tick_number
        )
    
    def canonicalize_trajectory(self, entity_id: str, actions: List[Dict[str, Any]],
                               states: List[Dict[str, Any]], consequences: List[Dict[str, Any]],
                               start_tick: int, end_tick: int) -> Trajectory:
        """Convert behavioral trajectory to canonical representation"""
        canonical_actions = tuple(self.canonicalize_action(a) for a in actions)
        
        canonical_states = tuple(
            self.canonicalize_state_transition(
                entity_id, 
                states[i].get("pre_state", states[i].get("pre", {})), 
                states[i].get("post_state", states[i].get("post", {})), 
                start_tick + i
            )
            for i in range(len(states))
        )
        
        canonical_consequences = tuple(
            self.canonicalize_environmental_consequence(c) for c in consequences
        )
        
        return Trajectory(
            entity_id=entity_id,
            action_sequence=canonical_actions,
            state_sequence=canonical_states,
            consequence_sequence=canonical_consequences,
            start_tick=start_tick,
            end_tick=end_tick
        )
    
    def track_action(self, action: Dict[str, Any], tick_number: int) -> bool:
        """Track action and return whether it is novel"""
        canonical = self.canonicalize_action(action)
        
        is_novel = canonical not in self.action_history
        
        if is_novel:
            self.action_history.add(canonical)
            self.action_novelty_events.append({
                "tick_number": tick_number,
                "canonical_action": canonical.to_dict(),
                "timestamp": datetime.now().isoformat()
            })
        
        return is_novel
    
    def track_state_transition(self, entity_id: str, pre_state: Dict[str, Any],
                              post_state: Dict[str, Any], tick_number: int) -> bool:
        """Track state transition and return whether it is novel"""
        canonical = self.canonicalize_state_transition(entity_id, pre_state, post_state, tick_number)
        
        is_novel = canonical not in self.state_transition_history
        
        if is_novel:
            self.state_transition_history.add(canonical)
            self.state_transition_novelty_events.append({
                "tick_number": tick_number,
                "canonical_transition": canonical.to_dict(),
                "timestamp": datetime.now().isoformat()
            })
        
        return is_novel
    
    def track_environmental_consequence(self, consequence: Dict[str, Any], tick_number: int) -> bool:
        """Track environmental consequence and return whether it is novel"""
        canonical = self.canonicalize_environmental_consequence(consequence)
        
        is_novel = canonical not in self.environmental_consequence_history
        
        if is_novel:
            self.environmental_consequence_history.add(canonical)
            self.environmental_consequence_novelty_events.append({
                "tick_number": tick_number,
                "canonical_consequence": canonical.to_dict(),
                "timestamp": datetime.now().isoformat()
            })
        
        return is_novel
    
    def track_trajectory(self, entity_id: str, actions: List[Dict[str, Any]],
                        states: List[Dict[str, Any]], consequences: List[Dict[str, Any]],
                        start_tick: int, end_tick: int) -> bool:
        """Track trajectory and return whether it is novel"""
        canonical = self.canonicalize_trajectory(entity_id, actions, states, consequences, start_tick, end_tick)
        
        is_novel = canonical not in self.trajectory_history
        
        if is_novel:
            self.trajectory_history.add(canonical)
            self.trajectory_novelty_events.append({
                "start_tick": start_tick,
                "end_tick": end_tick,
                "canonical_trajectory": canonical.to_dict(),
                "timestamp": datetime.now().isoformat()
            })
        
        return is_novel
    
    def get_novelty_summary(self) -> Dict[str, Any]:
        """Get summary of novelty detection"""
        return {
            "total_actions_tracked": len(self.action_history),
            "total_state_transitions_tracked": len(self.state_transition_history),
            "total_environmental_consequences_tracked": len(self.environmental_consequence_history),
            "total_trajectories_tracked": len(self.trajectory_history),
            "action_novelty_events": len(self.action_novelty_events),
            "state_transition_novelty_events": len(self.state_transition_novelty_events),
            "environmental_consequence_novelty_events": len(self.environmental_consequence_novelty_events),
            "trajectory_novelty_events": len(self.trajectory_novelty_events),
        }
    
    def export_novelty_data(self) -> Dict[str, Any]:
        """Export all novelty data for analysis"""
        return {
            "summary": self.get_novelty_summary(),
            "action_novelty_events": self.action_novelty_events,
            "state_transition_novelty_events": self.state_transition_novelty_events,
            "environmental_consequence_novelty_events": self.environmental_consequence_novelty_events,
            "trajectory_novelty_events": self.trajectory_novelty_events,
        }
