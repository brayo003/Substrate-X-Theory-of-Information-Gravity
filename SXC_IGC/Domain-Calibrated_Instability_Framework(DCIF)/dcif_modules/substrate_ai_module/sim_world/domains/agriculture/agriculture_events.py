from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True, slots=True)
class CropPlanted:
    field_id: str
    crop_type: str
    planted_by: str | None = None
    tick: int = 0
    event_type: str = field(default="CropPlanted", init=False)

    def to_dict(self) -> dict[str, Any]:
        return {
            "event_type": self.event_type,
            "field_id": self.field_id,
            "crop_type": self.crop_type,
            "planted_by": self.planted_by,
            "tick": self.tick,
        }


@dataclass(frozen=True, slots=True)
class CropWatered:
    field_id: str
    watered_by: str | None = None
    moisture_level: float = 0.0
    tick: int = 0
    event_type: str = field(default="CropWatered", init=False)

    def to_dict(self) -> dict[str, Any]:
        return {
            "event_type": self.event_type,
            "field_id": self.field_id,
            "watered_by": self.watered_by,
            "moisture_level": self.moisture_level,
            "tick": self.tick,
        }


@dataclass(frozen=True, slots=True)
class CropGrowthAdvanced:
    field_id: str
    crop_type: str
    old_stage: str
    new_stage: str
    tick: int = 0
    event_type: str = field(default="CropGrowthAdvanced", init=False)

    def to_dict(self) -> dict[str, Any]:
        return {
            "event_type": self.event_type,
            "field_id": self.field_id,
            "crop_type": self.crop_type,
            "old_stage": self.old_stage,
            "new_stage": self.new_stage,
            "tick": self.tick,
        }


@dataclass(frozen=True, slots=True)
class CropHarvested:
    field_id: str
    crop_type: str
    harvest_yield: float
    harvested_by: str | None = None
    tick: int = 0
    event_type: str = field(default="CropHarvested", init=False)

    def to_dict(self) -> dict[str, Any]:
        return {
            "event_type": self.event_type,
            "field_id": self.field_id,
            "crop_type": self.crop_type,
            "harvest_yield": self.harvest_yield,
            "harvested_by": self.harvested_by,
            "tick": self.tick,
        }


@dataclass(frozen=True, slots=True)
class CropFailed:
    field_id: str
    crop_type: str
    reason: str
    tick: int = 0
    event_type: str = field(default="CropFailed", init=False)

    def to_dict(self) -> dict[str, Any]:
        return {
            "event_type": self.event_type,
            "field_id": self.field_id,
            "crop_type": self.crop_type,
            "reason": self.reason,
            "tick": self.tick,
        }


@dataclass(frozen=True, slots=True)
class SeedsConsumed:
    consumer_id: str
    seed_type: str
    quantity: float
    tick: int = 0
    event_type: str = field(default="SeedsConsumed", init=False)

    def to_dict(self) -> dict[str, Any]:
        return {
            "event_type": self.event_type,
            "consumer_id": self.consumer_id,
            "seed_type": self.seed_type,
            "quantity": self.quantity,
            "tick": self.tick,
        }


@dataclass(frozen=True, slots=True)
class FoodProduced:
    producer_id: str
    food_type: str
    quantity: float
    tick: int = 0
    event_type: str = field(default="FoodProduced", init=False)

    def to_dict(self) -> dict[str, Any]:
        return {
            "event_type": self.event_type,
            "producer_id": self.producer_id,
            "food_type": self.food_type,
            "quantity": self.quantity,
            "tick": self.tick,
        }
