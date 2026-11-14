from __future__ import annotations

import random
from typing import Any

from ...core.contracts import TransitionProposal
from ...core.ids import TickId, WorldId
from ...simulation.simulation_engine import SimulationEngine


def _get_room_coordinates(room_name: str) -> tuple[int, int]:
    """Simple room coordinate mapping for movement"""
    room_coords = {
        "house_1": (100, 100),
        "house_2": (200, 100),
        "house_3": (300, 100),
        "house_4": (400, 100),
        "tavern": (150, 200),
        "blacksmith": (250, 200),
        "farm": (150, 300),
        "forest": (350, 300),
        "village_square": (250, 150),
        "farmland": (200, 250),
        "river": (100, 350),
        "bridge": (250, 350),
        "barn": (300, 300),
        "storage": (350, 200),
        "well": (200, 200),
    }
    return room_coords.get(room_name, (250, 150))  # Default to village square


def register(engine: SimulationEngine) -> None:
    engine.register_domain("physics", lambda engine, context: (apply(context),))


def build_movement_proposal(world_id: WorldId, tick_id: TickId | None, *, tick_number: int, entity_movements: dict[str, dict[str, float]]) -> TransitionProposal:
    return TransitionProposal(
        world_id=world_id,
        tick_id=tick_id,
        state_revision=None,
        correlation_id=f"domain.physics.{tick_number}",
        subject="domain.physics",
        patch={"entity_movements": entity_movements},
        description="physics domain entity movement",
        metadata={"domain": "physics", "movements_count": len(entity_movements)},
    )


def apply(context: Any) -> TransitionProposal:
    # Process movement goals with proper lifecycle and canonical UUIDs
    current_state = context.world_state if hasattr(context, 'world_state') else {}
    entities = dict(current_state.get("entities") or {})
    
    # print(f"AUDIT IDENTITY: Physics processing {len(entities)} entities")
    
    entity_movements = {}
    completed_goals = []
    
    # Check for movement goals in state
    goals = dict(current_state.get("goals") or {})
    active_goals = []
    
    for goal_id, goal in goals.items():
        if goal.get("kind") == "movement" and goal.get("status") == "pending":
            active_goals.append((goal_id, goal))
            # print(f"AUDIT LIFECYCLE: Found pending movement goal {goal_id} for entity {goal.get('entity_id')}")
    
    # print(f"AUDIT LIFECYCLE: Found {len(active_goals)} pending movement goals")
    
    # Process movement goals with canonical UUIDs
    for goal_id, goal in active_goals:
        entity_id = goal.get("entity_id")
        target_state = goal.get("target_state", {})
        target_room = target_state.get("room")
        
        if entity_id and target_room and entity_id in entities:
            # Get current entity position
            entity = entities[entity_id]
            components = dict(entity.get("components") or {})
            transform = dict(components.get("TransformComponent") or {})
            current_room = transform.get("room")
            
            # Calculate movement toward target room
            room_coords = _get_room_coordinates(target_room)
            current_coords = _get_room_coordinates(current_room) if current_room else (100, 100)
            
            # Move toward target (simple linear interpolation)
            dx = (room_coords[0] - current_coords[0]) * 0.1  # 10% of distance per tick
            dy = (room_coords[1] - current_coords[1]) * 0.1
            
            # Check if reached destination (distance < 10 units)
            distance = ((room_coords[0] - current_coords[0])**2 + (room_coords[1] - current_coords[1])**2)**0.5
            if distance < 10:  # Reached destination
                completed_goals.append(goal_id)
                entity_movements[str(entity_id)] = {
                    "dx": 0,
                    "dy": 0,
                    "target_room": target_room,
                    "arrived": True
                }
                # print(f"AUDIT LIFECYCLE: Goal {goal_id} COMPLETED - entity {entity_id} reached {target_room} (distance: {distance:.2f})")
            else:
                entity_movements[str(entity_id)] = {
                    "dx": dx,
                    "dy": dy,
                    "target_room": target_room,
                    "arrived": False
                }
                # print(f"AUDIT LIFECYCLE: Moving {entity_id} from {current_room} to {target_room}: ({dx}, {dy}) distance: {distance:.2f}")
    
    # No fallback random movement - only process genuine goals
    # print(f"AUDIT LIFECYCLE: Generated {len(entity_movements)} movements, {len(completed_goals)} goals completed")
    
    # Return both movements and completed goals for cleanup
    return build_movement_proposal(
        context.world_id,
        context.tick_context.tick_id,
        tick_number=context.tick_number,
        entity_movements=entity_movements,
        completed_goals=completed_goals,
    )


def build_movement_proposal(world_id: WorldId, tick_id: TickId | None, *, tick_number: int, entity_movements: dict[str, dict[str, float]], completed_goals: list[str] = []) -> TransitionProposal:
    # DOMAIN-LOCKED PROPERTY OWNERSHIP: Physics domain only mutates TransformComponent
    # Never mutate other domains' properties - use domain-specific namespace for signaling
    return TransitionProposal(
        world_id=world_id,
        tick_id=tick_id,
        state_revision=None,
        correlation_id=f"domain.physics.{tick_number}",
        subject="domain.physics",
        patch={
            "entity_transform_components": entity_movements,  # Domain-specific namespace
            "physics_goal_completion_signals": completed_goals  # Physics namespace for signaling
        },
        description="physics domain entity movement (domain-locked: TransformComponent only)",
        metadata={"domain": "physics", "movements_count": len(entity_movements), "completed_goals": len(completed_goals), "owned_properties": ["TransformComponent"]},
    )
