from __future__ import annotations

from typing import Any

from ...core.contracts import TransitionProposal
from ...simulation.simulation_engine import SimulationEngine


def register(engine: SimulationEngine) -> None:
    engine.register_domain("terrain", lambda engine, context: (apply(context),))


def build_region_map() -> dict[str, Any]:
    return {
        "regions": {
            "valley": {
                "name": "small valley",
                "terrain": ["forest", "river", "farmland", "village_square"],
                "roads": ["dirt_road", "bridge"],
                "buildings": [
                    "house_1",
                    "house_2",
                    "house_3",
                    "house_4",
                    "farm",
                    "barn",
                    "well",
                    "blacksmith",
                    "storage",
                    "tavern",
                ],
            }
        },
        "locations": {
            "forest": {"walkable": True, "kind": "forest"},
            "river": {"walkable": False, "kind": "river"},
            "farmland": {"walkable": True, "kind": "farmland"},
            "village_square": {"walkable": True, "kind": "village_square"},
            "bridge": {"walkable": True, "kind": "bridge"},
            "dirt_road": {"walkable": True, "kind": "road"},
            "house_1": {"walkable": True, "kind": "building", "building_type": "house"},
            "house_2": {"walkable": True, "kind": "building", "building_type": "house"},
            "house_3": {"walkable": True, "kind": "building", "building_type": "house"},
            "house_4": {"walkable": True, "kind": "building", "building_type": "house"},
            "farm": {"walkable": True, "kind": "building", "building_type": "farm"},
            "barn": {"walkable": True, "kind": "building", "building_type": "barn"},
            "well": {"walkable": True, "kind": "building", "building_type": "well"},
            "blacksmith": {"walkable": True, "kind": "building", "building_type": "blacksmith"},
            "storage": {"walkable": True, "kind": "building", "building_type": "storage"},
            "tavern": {"walkable": True, "kind": "building", "building_type": "tavern"},
        },
    }


def initialize_valley_terrain(kernel: Any) -> dict[str, Any]:
    registry = kernel.entity_registry
    entities = {}

    from ...entities.components import TransformComponent

    locations = [
        ("forest", "Forest", "location", "forest"),
        ("river", "River", "location", "river"),
        ("farmland", "Farmland", "location", "farmland"),
        ("village_square", "Village Square", "location", "village_square"),
        ("bridge", "Bridge", "location", "bridge"),
        ("dirt_road", "Dirt Road", "location", "road"),
    ]
    for loc_id, display, entity_type, kind in locations:
        if not any(e.display_name == display for e in registry.list_entities()):
            ent = registry.create_entity(
                entity_type=entity_type,
                display_name=display,
                created_tick=0,
                created_revision=None,
                metadata={"location_id": loc_id, "kind": kind, "walkable": kind != "river"},
            )
            ent.attach_component(TransformComponent(room=loc_id), tick=0)
            entities[loc_id] = ent

    buildings = [
        ("house_1", "House 1", "house"),
        ("house_2", "House 2", "house"),
        ("house_3", "House 3", "house"),
        ("house_4", "House 4", "house"),
        ("farm", "Farm", "farm"),
        ("barn", "Barn", "barn"),
        ("well", "Well", "well"),
        ("blacksmith", "Blacksmith", "blacksmith"),
        ("storage", "Storage", "storage"),
        ("tavern", "Tavern", "tavern"),
    ]
    for b_id, display, b_type in buildings:
        if not any(e.display_name == display for e in registry.list_entities()):
            ent = registry.create_entity(
                entity_type="building",
                display_name=display,
                created_tick=0,
                created_revision=None,
                metadata={"building_id": b_id, "building_type": b_type, "walkable": True},
            )
            ent.attach_component(TransformComponent(room=b_id), tick=0)
            entities[b_id] = ent

    return entities


def apply(context: Any) -> TransitionProposal:
    # Fix: Ensure state_revision is None when there's no current revision
    state_revision = context.committed_revision
    if state_revision == 0 and context.committed_revision is None:
        state_revision = None
    
    return TransitionProposal(
        world_id=context.world_id,
        tick_id=context.tick_context.tick_id,
        state_revision=state_revision,
        correlation_id=context.tick_context.correlation_id,
        subject="domain.terrain",
        patch={"terrain": build_region_map()},
        description="terrain domain update",
        metadata={"domain": "terrain"},
    )

