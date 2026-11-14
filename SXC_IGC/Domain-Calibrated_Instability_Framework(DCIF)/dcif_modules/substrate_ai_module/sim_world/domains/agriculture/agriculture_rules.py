from __future__ import annotations

from typing import Any

from .agriculture_events import (
    CropFailed,
    CropGrowthAdvanced,
)
from .agriculture_models import CROP_TYPES, GROWTH_STAGES, CropField


def validate_planting(field: CropField, seed_quantity: float, crop_type: str = "Wheat") -> tuple[bool, str]:
    if field.occupied:
        return False, "Field is already occupied by a crop"
    if crop_type not in CROP_TYPES:
        return False, f"Invalid crop type: {crop_type}"
    if seed_quantity < 1.0:
        return False, "Insufficient seeds for planting"
    return True, "Valid"


def validate_harvest(field: CropField) -> tuple[bool, str]:
    if not field.occupied:
        return False, "Field is not occupied"
    if field.growth_stage not in ("Mature", "Harvestable"):
        return False, f"Crop is not harvestable (current stage: {field.growth_stage})"
    if field.growth_stage == "Dead":
        return False, "Dead crops produce nothing"
    return True, "Valid"


def validate_watering(field: CropField, water_quantity: float) -> tuple[bool, str]:
    if water_quantity <= 0.0:
        return False, "Water quantity must be positive"
    return True, "Valid"


def calculate_harvest_yield(field: CropField) -> float:
    if not field.occupied or field.growth_stage == "Dead":
        return 0.0
    if field.growth_stage not in ("Mature", "Harvestable"):
        return 0.0

    base_yield = 10.0
    if field.crop_type == "Potatoes":
        base_yield = 12.0
    elif field.crop_type == "Vegetables":
        base_yield = 8.0

    multiplier = field.soil_quality * field.fertility * max(0.1, 1.0 - 0.5 * field.weed_level)
    return max(1.0, round(base_yield * multiplier, 2))


def advance_field_growth(
    field: CropField,
    weather: str,
    temperature: float,
    tick: int,
) -> tuple[CropField, list[Any]]:
    events: list[Any] = []

    moisture = field.soil_moisture
    weed = field.weed_level
    stage = field.growth_stage
    crop_type = field.crop_type or "Wheat"
    occupied = field.occupied

    if weather in ("rain", "storm"):
        moisture = min(1.0, moisture + 0.25)
    elif weather in ("drought", "sunny", "clear"):
        moisture = max(0.0, moisture - 0.15)

    if weather == "storm":
        weed = min(1.0, weed + 0.2)
        if occupied and stage != "Dead" and moisture < 0.1:
            stage = "Dead"
            events.append(CropFailed(field_id=field.field_id, crop_type=crop_type, reason="Storm damage", tick=tick))

    if occupied and stage != "Dead":
        if moisture <= 0.0 or weed >= 0.95:
            old_stage = stage
            stage = "Dead"
            events.append(CropFailed(field_id=field.field_id, crop_type=crop_type, reason="Drought or weed infestation", tick=tick))
            events.append(CropGrowthAdvanced(field_id=field.field_id, crop_type=crop_type, old_stage=old_stage, new_stage="Dead", tick=tick))

    if occupied and stage != "Dead" and stage != "Harvestable":
        is_cold = temperature < 5.0 or weather in ("cold", "snow")
        is_favorable = moisture >= 0.2 and weed < 0.8 and not is_cold

        if is_favorable:
            current_index = GROWTH_STAGES.index(stage) if stage in GROWTH_STAGES else 0
            if current_index < GROWTH_STAGES.index("Harvestable"):
                next_stage = GROWTH_STAGES[current_index + 1]
                events.append(
                    CropGrowthAdvanced(
                        field_id=field.field_id,
                        crop_type=crop_type,
                        old_stage=stage,
                        new_stage=next_stage,
                        tick=tick,
                    )
                )
                stage = next_stage

    new_field = CropField(
        field_id=field.field_id,
        crop_type=crop_type if occupied else None,
        growth_stage=stage,
        soil_quality=field.soil_quality,
        soil_moisture=moisture,
        fertility=field.fertility,
        weed_level=weed,
        last_watered_tick=field.last_watered_tick,
        last_harvest_tick=field.last_harvest_tick,
        occupied=occupied,
    )
    return new_field, events
