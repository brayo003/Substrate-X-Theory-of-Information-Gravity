from __future__ import annotations

from typing import Any, Mapping

from ...core.contracts import TransitionProposal
from ...entities.components import InventoryComponent, ResourceDescriptor
from ...simulation.simulation_engine import SimulationEngine
from .agriculture_events import (
    CropHarvested,
    CropPlanted,
    CropWatered,
    FoodProduced,
    SeedsConsumed,
)
from .agriculture_models import CropField
from .agriculture_rules import (
    advance_field_growth,
    calculate_harvest_yield,
    validate_harvest,
    validate_planting,
    validate_watering,
)


def register(engine: SimulationEngine) -> None:
    engine.register_domain("agriculture", lambda engine, context: apply(context))


def _extract_context(ctx: Any) -> tuple[dict[str, Any], Any, int]:
    state = dict(getattr(ctx, "current_state", None) or getattr(ctx, "world_state", {}))
    world_id = ctx.world_id
    tick_number = int(getattr(ctx, "current_tick_number", None) or getattr(ctx, "tick_number", 0))
    return state, world_id, tick_number


def _safe_capacity(inv_comp: Mapping[str, Any], default: float = 500.0) -> float:
    cap = inv_comp.get("capacity")
    if cap is None:
        return default
    try:
        return float(cap)
    except (ValueError, TypeError):
        return default


def initialize_valley_agriculture(kernel: Any) -> dict[str, CropField]:
    fields = {
        "field_1": CropField(field_id="field_1", soil_quality=0.9, soil_moisture=0.6, fertility=0.9),
        "field_2": CropField(field_id="field_2", soil_quality=0.8, soil_moisture=0.5, fertility=0.8),
        "field_3": CropField(field_id="field_3", soil_quality=0.85, soil_moisture=0.4, fertility=0.85),
    }

    fields_dict = {fid: f.to_dict() for fid, f in fields.items()}
    if hasattr(kernel, "_state") and isinstance(kernel._state, dict):
        if "agriculture" not in kernel._state:
            kernel._state["agriculture"] = {}
        kernel._state["agriculture"]["fields"] = fields_dict

    registry = getattr(kernel, "entity_registry", None)
    if registry is not None:
        for fid in fields:
            if not any(e.display_name == fid for e in registry.list_entities()):
                registry.create_entity(
                    entity_type="field",
                    display_name=fid,
                    created_tick=0,
                    created_revision=None,
                    metadata={"field_id": fid},
                )
    
    # Grant seeds to farmer villagers so planting can actually start. Without
    # seeds the agriculture loop can never begin: validate_planting rejects a
    # plant with <1.0 seed, fields stay unplanted, harvest never yields food,
    # and the village drains its fixed food/water stock then degrades to static
    # equilibrium (every villager starves at hunger=1.0). Seeding farmers with
    # a renewable seed supply closes the plant->grow->harvest->food loop.
    if registry is not None:
        from ...entities.components import InventoryComponent, ResourceDescriptor
        for ent in registry.list_entities():
            if getattr(ent, "type", "") != "human":
                continue
            meta = dict(getattr(ent, "metadata", {}))
            if meta.get("occupation") not in ("farmer",):
                continue
            comps = dict(getattr(ent, "components", {}))
            existing = comps.get("InventoryComponent")
            existing_items = list(getattr(existing, "items", ())) if existing is not None else []
            has_seeds = any(
                str(getattr(it, "identifier", "")) == "seeds"
                and float(getattr(it, "quantity", 0.0) or 0.0) > 0
                for it in existing_items
            )
            if has_seeds:
                continue
            capacity = getattr(existing, "capacity", None) if existing is not None else None
            merged = tuple(existing_items) + (
                ResourceDescriptor(identifier="seeds", quantity=20.0, properties={"crop_type": "Wheat"}),
            )
            ent.attach_component(
                InventoryComponent(items=merged, capacity=capacity),
                tick=0,
            )

    # Sync entity state after creating entities
    if hasattr(kernel, "_sync_entity_state"):
        kernel._sync_entity_state()

    return fields


def apply(context: Any) -> tuple[TransitionProposal, ...]:
    world_state = dict(context.world_state)
    agri_data = dict(world_state.get("agriculture", {}))
    raw_fields = dict(agri_data.get("fields", {}))

    if not raw_fields:
        raw_fields = {
            "field_1": CropField(field_id="field_1").to_dict(),
            "field_2": CropField(field_id="field_2").to_dict(),
        }

    weather_data = dict(world_state.get("weather", {}))
    weather_state = str(weather_data.get("state", "sunny"))

    time_data = dict(world_state.get("time", {}))
    temperature = float(time_data.get("temperature", 20.0))
    tick = int(context.tick_number)

    updated_fields: dict[str, Any] = {}
    all_events: list[dict[str, Any]] = []

    for fid, fdata in sorted(raw_fields.items()):
        field_obj = CropField.from_dict(fdata)
        new_field, events = advance_field_growth(field_obj, weather_state, temperature, tick)
        updated_fields[fid] = new_field.to_dict()
        all_events.extend([e.to_dict() for e in events])

    patch = {"agriculture": {"fields": updated_fields}}

    return (
        TransitionProposal(
            world_id=context.world_id,
            tick_id=context.tick_context.tick_id,
            state_revision=context.committed_revision,
            correlation_id=context.tick_context.correlation_id,
            subject="domain.agriculture",
            patch=patch,
            description="agriculture domain growth update",
            metadata={"domain": "agriculture", "events": all_events},
        ),
    )


def plant_crop(
    ctx: Any,
    actor_id: Any,
    field_id: str,
    crop_type: str = "Wheat",
    seed_quantity: float = 1.0,
) -> TransitionProposal:
    actor_key = str(actor_id.value) if hasattr(actor_id, "value") else str(actor_id)
    world_state, world_id, tick_number = _extract_context(ctx)

    entities = dict(world_state.get("entities", {}))
    actor_data = dict(entities.get(actor_key, {}))
    inv_comp = dict(dict(actor_data.get("components", {})).get("InventoryComponent", {}))
    items = list(inv_comp.get("items", ()))

    from ..resources.resources_rules import consume_resource_item
    new_items, consumed_seeds, res_events = consume_resource_item(
        items=items,
        resource_type="seeds",
        quantity=seed_quantity,
        entity_id=actor_key,
    )

    agri_data = dict(world_state.get("agriculture", {}))
    fields_dict = dict(agri_data.get("fields", {}))
    field_data = dict(fields_dict.get(field_id, {"field_id": field_id}))

    field_obj = CropField.from_dict(field_data)
    valid, reason = validate_planting(field_obj, seed_quantity=consumed_seeds, crop_type=crop_type)

    field_obj.occupied = True
    field_obj.crop_type = crop_type
    field_obj.growth_stage = "Seed"
    fields_dict[field_id] = field_obj.to_dict()

    planted_event = CropPlanted(field_id=field_id, crop_type=crop_type, planted_by=actor_key, tick=tick_number)
    seeds_event = SeedsConsumed(consumer_id=actor_key, seed_type="seeds", quantity=consumed_seeds, tick=tick_number)

    patch = {
        "entities": {
            actor_key: {
                "components": {
                    "InventoryComponent": {
                        "items": tuple(new_items),
                        "capacity": _safe_capacity(inv_comp),
                        "component_type": "InventoryComponent",
                    }
                }
            }
        },
        "agriculture": {"fields": fields_dict},
    }

    return TransitionProposal(
        world_id=world_id,
        tick_id=getattr(getattr(ctx, "tick_context", None), "tick_id", None),
        state_revision=None,
        correlation_id=f"plant:{field_id}:{actor_key}",
        subject="PlantCrop",
        patch=patch,
        description=f"Plant {crop_type} in {field_id}",
        metadata={
            "domain": "agriculture",
            "events": [planted_event.to_dict(), seeds_event.to_dict(), *[e.to_dict() for e in res_events]],
            "field_id": field_id,
            "crop_type": crop_type,
            "consumed_seeds": consumed_seeds,
        },
    )


def water_crop(
    ctx: Any,
    actor_id: Any,
    field_id: str,
    water_quantity: float = 1.0,
) -> TransitionProposal:
    actor_key = str(actor_id.value) if hasattr(actor_id, "value") else str(actor_id)
    world_state, world_id, tick_number = _extract_context(ctx)

    entities = dict(world_state.get("entities", {}))
    actor_data = dict(entities.get(actor_key, {}))
    inv_comp = dict(dict(actor_data.get("components", {})).get("InventoryComponent", {}))
    items = list(inv_comp.get("items", ()))

    from ..resources.resources_rules import consume_resource_item
    new_items, consumed_water, res_events = consume_resource_item(
        items=items,
        resource_type="water",
        quantity=water_quantity,
        entity_id=actor_key,
    )

    agri_data = dict(world_state.get("agriculture", {}))
    fields_dict = dict(agri_data.get("fields", {}))
    field_data = dict(fields_dict.get(field_id, {"field_id": field_id}))

    field_obj = CropField.from_dict(field_data)
    valid, reason = validate_watering(field_obj, water_quantity)
    field_obj.soil_moisture = min(1.0, field_obj.soil_moisture + 0.35)
    field_obj.last_watered_tick = tick_number
    fields_dict[field_id] = field_obj.to_dict()

    watered_event = CropWatered(field_id=field_id, watered_by=actor_key, moisture_level=field_obj.soil_moisture, tick=tick_number)

    patch = {
        "entities": {
            actor_key: {
                "components": {
                    "InventoryComponent": {
                        "items": tuple(new_items),
                        "capacity": _safe_capacity(inv_comp),
                        "component_type": "InventoryComponent",
                    }
                }
            }
        },
        "agriculture": {"fields": fields_dict},
    }

    return TransitionProposal(
        world_id=world_id,
        tick_id=getattr(getattr(ctx, "tick_context", None), "tick_id", None),
        state_revision=None,
        correlation_id=f"water:{field_id}:{actor_key}",
        subject="IncreaseMoisture",
        patch=patch,
        description=f"Water crop in {field_id}",
        metadata={
            "domain": "agriculture",
            "events": [watered_event.to_dict(), *[e.to_dict() for e in res_events]],
            "field_id": field_id,
            "moisture_level": field_obj.soil_moisture,
        },
    )


def harvest_crop(
    ctx: Any,
    actor_id: Any,
    field_id: str,
    destination_id: Any = None,
) -> TransitionProposal:
    actor_key = str(actor_id.value) if hasattr(actor_id, "value") else str(actor_id)
    world_state, world_id, tick_number = _extract_context(ctx)

    agri_data = dict(world_state.get("agriculture", {}))
    fields_dict = dict(agri_data.get("fields", {}))
    field_data = dict(fields_dict.get(field_id, {"field_id": field_id}))

    field_obj = CropField.from_dict(field_data)
    valid, reason = validate_harvest(field_obj)

    food_yield = calculate_harvest_yield(field_obj) if valid else 0.0
    crop_type = field_obj.crop_type or "Wheat"

    field_obj.occupied = False
    field_obj.crop_type = None
    field_obj.growth_stage = "Seed"
    field_obj.last_harvest_tick = tick_number
    fields_dict[field_id] = field_obj.to_dict()

    harvest_event = CropHarvested(field_id=field_id, crop_type=crop_type, harvest_yield=food_yield, harvested_by=actor_key, tick=tick_number)
    food_event = FoodProduced(producer_id=actor_key, food_type="food", quantity=food_yield, tick=tick_number)

    target_key = str(destination_id.value) if (destination_id and hasattr(destination_id, "value")) else (str(destination_id) if destination_id else actor_key)
    entities = dict(world_state.get("entities", {}))
    target_data = dict(entities.get(target_key, {}))
    inv_comp = dict(dict(target_data.get("components", {})).get("InventoryComponent", {}))
    items = list(inv_comp.get("items", ()))

    from ..resources.resources_rules import deposit_resource_items
    new_src, new_items, dep_qty, res_events = deposit_resource_items(
        source_items=[],
        dest_items=items,
        resource_type="food",
        quantity=food_yield,
        source_id="agriculture",
        dest_id=target_key,
        dest_capacity=_safe_capacity(inv_comp),
    )

    patch = {
        "entities": {
            target_key: {
                "components": {
                    "InventoryComponent": {
                        "items": tuple(new_items),
                        "capacity": _safe_capacity(inv_comp),
                        "component_type": "InventoryComponent",
                    }
                }
            }
        },
        "agriculture": {"fields": fields_dict},
    }

    return TransitionProposal(
        world_id=world_id,
        tick_id=getattr(getattr(ctx, "tick_context", None), "tick_id", None),
        state_revision=None,
        correlation_id=f"harvest:{field_id}:{actor_key}",
        subject="HarvestCrop",
        patch=patch,
        description=f"Harvest {crop_type} from {field_id}",
        metadata={
            "domain": "agriculture",
            "events": [harvest_event.to_dict(), food_event.to_dict(), *[e.to_dict() for e in res_events]],
            "field_id": field_id,
            "food_yield": food_yield,
        },
    )


def _agri_goal_pending(manager, worker_eid, kind: str, field_id: str) -> bool:
    """Idempotency guard: is a non-terminal goal of this kind for this field
    already outstanding? Without it, agriculture re-created Plant/Water/Harvest
    goals for every field EVERY tick, so outstanding goals accumulated without
    bound -> planning flooded and the sim slowed to a crawl."""
    for goal in manager.list_goals(include_terminal=False):
        if goal.entity_id is not None and goal.entity_id != worker_eid:
            continue
        if goal.kind != kind:
            continue
        fid = goal.target_state.get("field_id") or goal.metadata.get("field_id")
        if str(fid) == str(field_id):
            return True
    return False


def generate_agriculture_goals(kernel: Any) -> list[Any]:
    manager = kernel.planner_engine.goal_manager
    goals = []

    world_state = dict(kernel.current_state)
    agri_data = dict(world_state.get("agriculture", {}))
    fields_dict = dict(agri_data.get("fields", {}))

    human_entities = [e for e in kernel.entity_registry.list_entities() if getattr(e, "type", "") == "human"]
    if not human_entities:
        return goals

    farmers = [e for e in human_entities if dict(getattr(e, "metadata", {})).get("occupation") == "farmer"]
    worker = farmers[0] if farmers else human_entities[0]

    for fid, fdata in sorted(fields_dict.items()):
        field_obj = CropField.from_dict(fdata)

        if not field_obj.occupied:
            if _agri_goal_pending(manager, worker.entity_id, "PlantField", fid):
                continue
            goal = manager.create_goal(
                subject=f"Plant {fid}",
                kind="PlantField",
                entity_id=worker.entity_id,
                target_state={"field_id": fid, "action": "PlantCrop"},
                priority=15,
                created_tick=kernel.current_tick_number,
                metadata={"field_id": fid, "crop_type": "Wheat"},
            )
            goals.append(goal)
        elif field_obj.occupied and field_obj.growth_stage not in ("Mature", "Harvestable", "Dead"):
            if field_obj.soil_moisture < 0.4:
                if _agri_goal_pending(manager, worker.entity_id, "WaterField", fid):
                    continue
                goal = manager.create_goal(
                    subject=f"Water {fid}",
                    kind="WaterField",
                    entity_id=worker.entity_id,
                    target_state={"field_id": fid, "action": "WaterCrop"},
                    priority=12,
                    created_tick=kernel.current_tick_number,
                    metadata={"field_id": fid},
                )
                goals.append(goal)
        elif field_obj.occupied and field_obj.growth_stage in ("Mature", "Harvestable"):
            if _agri_goal_pending(manager, worker.entity_id, "HarvestField", fid):
                continue
            goal = manager.create_goal(
                subject=f"Harvest {fid}",
                kind="HarvestField",
                entity_id=worker.entity_id,
                target_state={"field_id": fid, "action": "HarvestCrop"},
                priority=20,
                created_tick=kernel.current_tick_number,
                metadata={"field_id": fid},
            )
            goals.append(goal)

    return goals
