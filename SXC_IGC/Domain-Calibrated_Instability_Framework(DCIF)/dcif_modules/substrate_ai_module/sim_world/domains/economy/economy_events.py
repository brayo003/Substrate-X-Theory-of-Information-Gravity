from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True, slots=True)
class ProductionStarted:
    crafter_id: str
    recipe_name: str
    building_id: str | None = None
    tick: int = 0
    event_type: str = field(default="ProductionStarted", init=False)

    def to_dict(self) -> dict[str, Any]:
        return {
            "event_type": self.event_type,
            "crafter_id": self.crafter_id,
            "recipe_name": self.recipe_name,
            "building_id": self.building_id,
            "tick": self.tick,
        }


@dataclass(frozen=True, slots=True)
class ProductionCompleted:
    crafter_id: str
    recipe_name: str
    output_resource: str
    output_quantity: float
    tick: int = 0
    event_type: str = field(default="ProductionCompleted", init=False)

    def to_dict(self) -> dict[str, Any]:
        return {
            "event_type": self.event_type,
            "crafter_id": self.crafter_id,
            "recipe_name": self.recipe_name,
            "output_resource": self.output_resource,
            "output_quantity": self.output_quantity,
            "tick": self.tick,
        }


@dataclass(frozen=True, slots=True)
class ItemCrafted:
    item_type: str
    quantity: float
    crafter_id: str
    tick: int = 0
    event_type: str = field(default="ItemCrafted", init=False)

    def to_dict(self) -> dict[str, Any]:
        return {
            "event_type": self.event_type,
            "item_type": self.item_type,
            "quantity": self.quantity,
            "crafter_id": self.crafter_id,
            "tick": self.tick,
        }


@dataclass(frozen=True, slots=True)
class ItemConsumed:
    item_type: str
    quantity: float
    consumer_id: str
    tick: int = 0
    event_type: str = field(default="ItemConsumed", init=False)

    def to_dict(self) -> dict[str, Any]:
        return {
            "event_type": self.event_type,
            "item_type": self.item_type,
            "quantity": self.quantity,
            "consumer_id": self.consumer_id,
            "tick": self.tick,
        }


@dataclass(frozen=True, slots=True)
class TradeExecuted:
    seller_id: str
    buyer_id: str
    item_given: str
    qty_given: float
    item_received: str
    qty_received: float
    tick: int = 0
    event_type: str = field(default="TradeExecuted", init=False)

    def to_dict(self) -> dict[str, Any]:
        return {
            "event_type": self.event_type,
            "seller_id": self.seller_id,
            "buyer_id": self.buyer_id,
            "item_given": self.item_given,
            "qty_given": self.qty_given,
            "item_received": self.item_received,
            "qty_received": self.qty_received,
            "tick": self.tick,
        }


@dataclass(frozen=True, slots=True)
class StorageFilled:
    building_id: str
    item_type: str
    current_qty: float
    max_capacity: float
    tick: int = 0
    event_type: str = field(default="StorageFilled", init=False)

    def to_dict(self) -> dict[str, Any]:
        return {
            "event_type": self.event_type,
            "building_id": self.building_id,
            "item_type": self.item_type,
            "current_qty": self.current_qty,
            "max_capacity": self.max_capacity,
            "tick": self.tick,
        }


@dataclass(frozen=True, slots=True)
class StorageEmpty:
    building_id: str
    item_type: str
    tick: int = 0
    event_type: str = field(default="StorageEmpty", init=False)

    def to_dict(self) -> dict[str, Any]:
        return {
            "event_type": self.event_type,
            "building_id": self.building_id,
            "item_type": self.item_type,
            "tick": self.tick,
        }


@dataclass(frozen=True, slots=True)
class ShortageDetected:
    item_type: str
    shortage_amount: float
    location_id: str | None = None
    tick: int = 0
    event_type: str = field(default="ShortageDetected", init=False)

    def to_dict(self) -> dict[str, Any]:
        return {
            "event_type": self.event_type,
            "item_type": self.item_type,
            "shortage_amount": self.shortage_amount,
            "location_id": self.location_id,
            "tick": self.tick,
        }


@dataclass(frozen=True, slots=True)
class SurplusDetected:
    item_type: str
    surplus_amount: float
    location_id: str | None = None
    tick: int = 0
    event_type: str = field(default="SurplusDetected", init=False)

    def to_dict(self) -> dict[str, Any]:
        return {
            "event_type": self.event_type,
            "item_type": self.item_type,
            "surplus_amount": self.surplus_amount,
            "location_id": self.location_id,
            "tick": self.tick,
        }


@dataclass(frozen=True, slots=True)
class ToolBroken:
    tool_id: str
    owner_id: str
    tick: int = 0
    event_type: str = field(default="ToolBroken", init=False)

    def to_dict(self) -> dict[str, Any]:
        return {
            "event_type": self.event_type,
            "tool_id": self.tool_id,
            "owner_id": self.owner_id,
            "tick": self.tick,
        }


@dataclass(frozen=True, slots=True)
class ToolCrafted:
    crafter_id: str
    tool_type: str
    quantity: float
    tick: int = 0
    event_type: str = field(default="ToolCrafted", init=False)

    def to_dict(self) -> dict[str, Any]:
        return {
            "event_type": self.event_type,
            "crafter_id": self.crafter_id,
            "tool_type": self.tool_type,
            "quantity": self.quantity,
            "tick": self.tick,
        }


@dataclass(frozen=True, slots=True)
class FoodDelivered:
    source_id: str
    dest_id: str
    quantity: float
    tick: int = 0
    event_type: str = field(default="FoodDelivered", init=False)

    def to_dict(self) -> dict[str, Any]:
        return {
            "event_type": self.event_type,
            "source_id": self.source_id,
            "dest_id": self.dest_id,
            "quantity": self.quantity,
            "tick": self.tick,
        }
