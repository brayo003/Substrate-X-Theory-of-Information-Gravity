from __future__ import annotations

from typing import Any, Dict, List, Mapping
import sys
from pathlib import Path

# Add parent directory to path for imports
parent_dir = Path(__file__).resolve().parents[1]
if str(parent_dir) not in sys.path:
    sys.path.insert(0, str(parent_dir))

from core.contracts import RenderSnapshot

# Import models directly
from snapshot_models import WorldSnapshot, VillagerModel, BuildingModel, EnvironmentModel



def _safe_int(v: Any, default: int = 0) -> int:
    try:
        return int(v)
    except Exception:
        return default


def _safe_float(v: Any, default: float = 1.0) -> float:
    try:
        return float(v)
    except Exception:
        return default


def _extract_needs(components: dict) -> dict:
    """Real NeedsComponent values (0..1, higher = more urgent). Never faked."""
    nd = components.get("NeedsComponent")
    if not isinstance(nd, Mapping):
        return {}
    needs = nd.get("needs")
    if not isinstance(needs, Mapping):
        return {}
    out = {}
    for k, v in needs.items():
        try:
            out[str(k)] = round(float(v), 3)
        except Exception:
            pass
    return out


def _extract_inventory(components: dict) -> dict:
    """Real InventoryComponent resource counts as {item_id: quantity}."""
    inv = components.get("InventoryComponent")
    if not isinstance(inv, Mapping):
        return {}
    items = inv.get("items")
    if items is None:
        return {}
    out = {}
    for item in items:
        if not isinstance(item, dict) and not isinstance(item, Mapping):
            continue
        ident = item.get("identifier")
        qty = item.get("quantity")
        if ident is None:
            continue
        try:
            out[str(ident)] = round(float(qty), 3)
        except Exception:
            out[str(ident)] = 0.0
    if not out:
        return {}
    return out


def _derive_state(needs: dict) -> str:
    """Derive a truthful current-state label from REAL needs thresholds.

    This is not a fabricated task: it is a direct statement about the villager's
    real, backend-computed needs (higher = more urgent). Where no need is
    pressing, the villager is idle.
    """
    thresholds = [
        ("hunger", 0.75, "seeking food"),
        ("thirst", 0.75, "seeking water"),
        ("energy", 0.25, "resting"),
        ("warmth", 0.30, "seeking warmth"),
        ("comfort", 0.30, "seeking comfort"),
        ("social", 0.75, "seeking company"),
    ]
    for key, thresh, label in thresholds:
        val = needs.get(key)
        if val is not None:
            try:
                if float(val) >= thresh:
                    return label
            except Exception:
                pass
    return "idle"


# Simple room name to coordinate mapping for positioning
# Room name -> cell-scale GRID coordinates (PROTOCOL.md v1.0.0).
# x/y on the wire are grid cells within the authored world (0..20, 0..15),
# NOT pixel offsets. Values must stay in that cell range.
_ROOM_COORDINATES = {
    "house_1": (13, 5),
    "house_2": (14, 5),
    "house_3": (15, 5),
    "house_4": (15, 6),
    "house_5": (16, 5),
    "tavern": (13, 6),
    "blacksmith": (14, 6),
    "workshop": (14, 4),
    "clinic": (15, 4),
    "market": (12, 6),
    "forge": (16, 6),
    "farm": (10, 12),
    "forest": (4, 4),
    "village_square": (12, 6),
    "farmland": (11, 12),
    "river": (8, 9),
    "bridge": (9, 11),
    "barn": (12, 12),
    "storage": (14, 7),
    "well": (12, 7),
    "dirt_road": (11, 7),
}

# Store accumulated entity positions for movement
_entity_positions = {}


def _extract_position(components: dict, data: dict) -> tuple[int, int]:
    """Extract (x, y) position from entity components."""
    # Try PositionComponent first
    if "PositionComponent" in components:
        posc = dict(components.get("PositionComponent") or {})
        return (_safe_int(posc.get("x")), _safe_int(posc.get("y")))
    
    # Try TransformComponent.position (3D tuple)
    if "TransformComponent" in components:
        tc = dict(components.get("TransformComponent") or {})
        pos = tc.get("position")
        if isinstance(pos, (tuple, list)) and len(pos) >= 2:
            x = _safe_int(pos[0])
            y = _safe_int(pos[1])
            # If position is (0, 0, 0), try room name mapping instead
            if x == 0 and y == 0:
                room = tc.get("room")
                if room:
                    room_lower = room.lower()
                    if room_lower in _ROOM_COORDINATES:
                        return _ROOM_COORDINATES[room_lower]
            return (x, y)
        # Fallback to room name mapping
        room = tc.get("room")
        if room:
            room_lower = room.lower()
            if room_lower in _ROOM_COORDINATES:
                return _ROOM_COORDINATES[room_lower]
    
    # Try position dict
    if "position" in data:
        p = data.get("position")
        if isinstance(p, dict):
            return (_safe_int(p.get("x")), _safe_int(p.get("y")))
        if isinstance(p, (tuple, list)) and len(p) >= 2:
            return (_safe_int(p[0]), _safe_int(p[1]))
    
    # Try root-level x,y
    if "x" in data and "y" in data:
        return (_safe_int(data.get("x")), _safe_int(data.get("y")))
    
    return (0, 0)


def build_from_render_snapshot(render_snapshot: RenderSnapshot, tick_number: int | None = None) -> dict:
    """Build a transport-safe WorldSnapshot dict from a RenderSnapshot.

    This function carefully extracts only primitive data and constructs
    plain dataclasses/dicts. It MUST NOT expose Revision or internal objects.
    """
    global _entity_positions
    state = dict(render_snapshot.state or {})

    # tick: prefer explicit tick_number if available
    tick = tick_number if tick_number is not None else 0

    # time and weather are optional
    time = dict(state.get("time") or {})
    weather = dict(state.get("weather") or {})

    # print(f"AUDIT Q4: Entity count before SnapshotBuilder: {len(state.get('entities', {}))}")

    villagers: List[VillagerModel] = []
    buildings: List[BuildingModel] = []
    environment: List[EnvironmentModel] = []

    # entities may contain actors and buildings
    entities = dict(state.get("entities") or {})
    
    # DOMAIN-LOCKED PROPERTY INTEGRATION: Read from domain-specific namespaces
    entity_transform_components = dict(state.get("entity_transform_components") or {})
    
    # Apply physics domain movements to accumulated positions
    for entity_id, movement in entity_transform_components.items():
        if entity_id not in _entity_positions:
            _entity_positions[entity_id] = [0, 0]  # default cell (grid origin)
        
        dx = movement.get("dx", 0)
        dy = movement.get("dy", 0)
        _entity_positions[entity_id][0] += dx
        _entity_positions[entity_id][1] += dy
    
    for entity_key, entity in entities.items():
        try:
            data = dict(entity or {})
            components = dict(data.get("components") or {})
        except Exception:
            continue

        # Check if this entity has accumulated movement
        entity_id = str(entity_key)
        # PROTOCOL CONFORMANCE (v1.0.0): always extract the entity's CURRENT
        # position from its live components every snapshot. The cached
        # _entity_positions accumulator froze coordinates at the first
        # snapshot, so villagers walked (room changed) but the wire never
        # reflected it. Position must track the entity's present room/cell.
        #
        # _entity_positions now holds only *delta* offsets accumulated from
        # the (future/optional) physics movement domain; v1.0.0 domains never
        # emit movement deltas, so it stays [0,0] and pos = live extraction.
        pos = _extract_position(components, data)
        delta = _entity_positions.get(entity_id, [0, 0])
        pos = (pos[0] + delta[0], pos[1] + delta[1])
        # print(f"DEBUG: Live position for {entity_id}: {pos}")

        entity_type = str(data.get("type") or data.get("display_name") or data.get("entity_type") or "entity")

        # Heuristic: villagers/agents may have an ActorComponent or AgentComponent, or be type="human"
        if ("ActorComponent" in components or "AgentComponent" in components or 
            entity_type.lower().startswith("vill") or 
            entity_key.lower().startswith("vill") or
            entity_type.lower() == "human"):
            vid = str(entity_key)
            name = str(data.get("display_name") or data.get("name") or vid)
            x = pos[0] if pos else 0
            y = pos[1] if pos else 0
            
            # Extract rendering parameters
            texture = str(data.get("texture") or data.get("sprite") or "villager")  # Default to villager texture
            scale = _safe_float(data.get("scale"), 1.0)
            
            facing = None
            animation = None
            activity = None
            emotion = None
            state_field = None
            # extract lightweight fields if present
            actor = components.get("ActorComponent") or components.get("AgentComponent") or {}
            if isinstance(actor, dict):
                facing = actor.get("facing")
                animation = actor.get("animation")
                activity = actor.get("activity")
                emotion = actor.get("emotion")
                state_field = actor.get("state")

            # v1.1.0 observability: expose REAL per-villager needs/inventory and
            # derive an honest current-state label from them. Requires a
            # VillagerModel that carries these fields; see snapshot_models.py.
            _needs = _extract_needs(components)
            _inv = _extract_inventory(components)
            _vstate = state_field if state_field is not None else _derive_state(_needs)
            villagers.append(VillagerModel(
                id=vid, name=name, x=x, y=y, texture=texture, scale=scale,
                facing=facing, animation=animation, activity=activity,
                emotion=emotion, state=_vstate,
                needs=_needs, inventory=_inv,
            ))
            continue

        # Heuristic: building
        if entity_type.lower() in {"building", "farm", "house", "barn", "tavern", "well"} or entity_key.lower().startswith("building") or entity_key.lower().startswith("farm") or data.get("is_building"):
            bid = str(entity_key)
            btype = str(entity_type)
            x = pos[0] if pos else 0
            y = pos[1] if pos else 0
            
            # Extract rendering parameters
            texture = str(data.get("texture") or data.get("sprite") or btype.lower())  # Use type as texture fallback
            scale = _safe_float(data.get("scale"), 1.0)
            
            buildings.append(BuildingModel(id=bid, type=btype, x=x, y=y, texture=texture, scale=scale))
            continue
        
        # Heuristic: environment objects (trees, rocks, roads)
        if entity_type.lower() in {"tree", "rock", "road"} or entity_key.lower().startswith("tree") or entity_key.lower().startswith("rock") or entity_key.lower().startswith("road"):
            eid = str(entity_key)
            etype = str(entity_type)
            x = pos[0] if pos else 0
            y = pos[1] if pos else 0
            
            # Extract rendering parameters
            texture = str(data.get("texture") or data.get("sprite") or etype.lower())
            scale = _safe_float(data.get("scale"), 1.0)
            
            environment.append(EnvironmentModel(id=eid, type=etype, x=x, y=y, texture=texture, scale=scale))
            continue

    # Construct snapshot
    ws = WorldSnapshot(
        tick=(tick or 0),
        time=time,
        weather=weather,
        villagers=villagers,
        buildings=buildings,
        environment=environment,
    )

    return ws.to_dict()
