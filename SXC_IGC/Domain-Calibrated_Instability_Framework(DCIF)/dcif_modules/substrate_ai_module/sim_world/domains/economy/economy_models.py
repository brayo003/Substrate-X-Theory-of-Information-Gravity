from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Mapping


@dataclass(frozen=True, slots=True)
class Recipe:
    recipe_id: str
    name: str
    building_type: str
    inputs: tuple[tuple[str, float], ...]
    outputs: tuple[tuple[str, float], ...]
    labor_ticks: int = 1
    profession_required: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "recipe_id": self.recipe_id,
            "name": self.name,
            "building_type": self.building_type,
            "inputs": [list(item) for item in self.inputs],
            "outputs": [list(item) for item in self.outputs],
            "labor_ticks": self.labor_ticks,
            "profession_required": self.profession_required,
        }

    @staticmethod
    def from_dict(data: Mapping[str, Any]) -> Recipe:
        return Recipe(
            recipe_id=str(data.get("recipe_id", "recipe_1")),
            name=str(data.get("name", "Craft")),
            building_type=str(data.get("building_type", "Workshop")),
            inputs=tuple(tuple((str(item[0]), float(item[1]))) for item in data.get("inputs", ())),
            outputs=tuple(tuple((str(item[0]), float(item[1]))) for item in data.get("outputs", ())),
            labor_ticks=int(data.get("labor_ticks", 1)),
            profession_required=data.get("profession_required"),
        )


@dataclass(slots=True)
class StockLevel:
    resource_type: str
    current_quantity: float
    target_capacity: float = 500.0
    min_threshold: float = 10.0

    def to_dict(self) -> dict[str, Any]:
        return {
            "resource_type": self.resource_type,
            "current_quantity": self.current_quantity,
            "target_capacity": self.target_capacity,
            "min_threshold": self.min_threshold,
        }

    @staticmethod
    def from_dict(data: Mapping[str, Any]) -> StockLevel:
        return StockLevel(
            resource_type=str(data.get("resource_type", "food")),
            current_quantity=float(data.get("current_quantity", 0.0)),
            target_capacity=float(data.get("target_capacity", 500.0)),
            min_threshold=float(data.get("min_threshold", 10.0)),
        )


@dataclass(frozen=True, slots=True)
class DemandSignal:
    resource_type: str
    severity: float
    shortage_amount: float
    location_id: str | None = None
    rationale: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "resource_type": self.resource_type,
            "severity": self.severity,
            "shortage_amount": self.shortage_amount,
            "location_id": self.location_id,
            "rationale": self.rationale,
        }


@dataclass(frozen=True, slots=True)
class SupplySignal:
    resource_type: str
    available_quantity: float
    location_id: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "resource_type": self.resource_type,
            "available_quantity": self.available_quantity,
            "location_id": self.location_id,
        }


@dataclass(slots=True)
class TradeRequest:
    trade_id: str
    requester_id: str
    offer_resource: str
    offer_quantity: float
    want_resource: str
    want_quantity: float
    status: str = "open"

    def to_dict(self) -> dict[str, Any]:
        return {
            "trade_id": self.trade_id,
            "requester_id": self.requester_id,
            "offer_resource": self.offer_resource,
            "offer_quantity": self.offer_quantity,
            "want_resource": self.want_resource,
            "want_quantity": self.want_quantity,
            "status": self.status,
        }


@dataclass(slots=True)
class CraftRequest:
    craft_id: str
    crafter_id: str
    recipe_name: str
    building_id: str | None = None
    status: str = "pending"

    def to_dict(self) -> dict[str, Any]:
        return {
            "craft_id": self.craft_id,
            "crafter_id": self.crafter_id,
            "recipe_name": self.recipe_name,
            "building_id": self.building_id,
            "status": self.status,
        }


@dataclass(frozen=True, slots=True)
class ProductionChain:
    chain_id: str
    name: str
    steps: tuple[str, ...]

    def to_dict(self) -> dict[str, Any]:
        return {
            "chain_id": self.chain_id,
            "name": self.name,
            "steps": list(self.steps),
        }
