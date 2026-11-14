from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping


CROP_TYPES: tuple[str, ...] = ("Wheat", "Potatoes", "Vegetables")

GROWTH_STAGES: tuple[str, ...] = (
    "Seed",
    "Sprout",
    "Growing",
    "Mature",
    "Harvestable",
    "Dead",
)


@dataclass(slots=True)
class CropField:
    field_id: str
    crop_type: str | None = None
    growth_stage: str = "Seed"
    soil_quality: float = 1.0
    soil_moisture: float = 0.5
    fertility: float = 1.0
    weed_level: float = 0.0
    last_watered_tick: int = 0
    last_harvest_tick: int = 0
    occupied: bool = False

    def __post_init__(self) -> None:
        self.field_id = str(self.field_id)
        if self.crop_type is not None:
            self.crop_type = str(self.crop_type)
        self.growth_stage = str(self.growth_stage)
        self.soil_quality = max(0.0, min(1.0, float(self.soil_quality)))
        self.soil_moisture = max(0.0, min(1.0, float(self.soil_moisture)))
        self.fertility = max(0.0, min(1.0, float(self.fertility)))
        self.weed_level = max(0.0, min(1.0, float(self.weed_level)))
        self.last_watered_tick = int(self.last_watered_tick)
        self.last_harvest_tick = int(self.last_harvest_tick)
        self.occupied = bool(self.occupied)

    def to_dict(self) -> dict[str, Any]:
        return {
            "field_id": self.field_id,
            "crop_type": self.crop_type,
            "growth_stage": self.growth_stage,
            "soil_quality": self.soil_quality,
            "soil_moisture": self.soil_moisture,
            "fertility": self.fertility,
            "weed_level": self.weed_level,
            "last_watered_tick": self.last_watered_tick,
            "last_harvest_tick": self.last_harvest_tick,
            "occupied": self.occupied,
        }

    @staticmethod
    def from_dict(data: Mapping[str, Any]) -> CropField:
        return CropField(
            field_id=str(data.get("field_id", "field_1")),
            crop_type=data.get("crop_type"),
            growth_stage=str(data.get("growth_stage", "Seed")),
            soil_quality=float(data.get("soil_quality", 1.0)),
            soil_moisture=float(data.get("soil_moisture", 0.5)),
            fertility=float(data.get("fertility", 1.0)),
            weed_level=float(data.get("weed_level", 0.0)),
            last_watered_tick=int(data.get("last_watered_tick", 0)),
            last_harvest_tick=int(data.get("last_harvest_tick", 0)),
            occupied=bool(data.get("occupied", False)),
        )
