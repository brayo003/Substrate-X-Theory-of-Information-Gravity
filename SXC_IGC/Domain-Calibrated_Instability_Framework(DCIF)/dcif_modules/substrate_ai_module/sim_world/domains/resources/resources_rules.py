from __future__ import annotations

from typing import Any, Mapping, Sequence
from .resources_events import ResourceEvent


def calculate_total_quantity(items: Sequence[Mapping[str, Any]]) -> float:
    return sum(float(item.get("quantity", 0.0)) for item in items)


def validate_inventory_capacity(items: Sequence[Mapping[str, Any]], capacity: float | None = 500.0) -> bool:
    if capacity is None:
        return True
    return calculate_total_quantity(items) <= float(capacity)


def transfer_resource_items(
    source_items: Sequence[Mapping[str, Any]],
    dest_items: Sequence[Mapping[str, Any]],
    resource_type: str,
    quantity: float,
    source_id: str,
    dest_id: str,
    dest_capacity: float = 500.0,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], float, list[ResourceEvent]]:
    src = [dict(item) for item in source_items]
    dst = [dict(item) for item in dest_items]
    events: list[ResourceEvent] = []

    dest_current_total = calculate_total_quantity(dst)
    available_capacity = max(0.0, dest_capacity - dest_current_total)

    # Available in source
    source_avail = sum(float(item.get("quantity", 0.0)) for item in src if str(item.get("identifier")) == resource_type)
    transfer_qty = min(float(quantity), source_avail, available_capacity)

    if transfer_qty <= 0.0:
        return src, dst, 0.0, []

    # Deduct from source
    remaining_to_deduct = transfer_qty
    new_src: list[dict[str, Any]] = []
    for item in src:
        if str(item.get("identifier")) == resource_type and remaining_to_deduct > 0.0:
            item_qty = float(item.get("quantity", 0.0))
            deduct = min(item_qty, remaining_to_deduct)
            remaining_to_deduct -= deduct
            new_qty = item_qty - deduct
            if new_qty > 0.0:
                new_src.append({**item, "quantity": new_qty})
        else:
            new_src.append(item)

    # Add to destination
    added = False
    new_dst: list[dict[str, Any]] = []
    for item in dst:
        if str(item.get("identifier")) == resource_type and not added:
            new_dst.append({**item, "quantity": float(item.get("quantity", 0.0)) + transfer_qty})
            added = True
        else:
            new_dst.append(item)

    if not added:
        new_dst.append({"identifier": resource_type, "quantity": transfer_qty, "properties": {}})

    events.append(ResourceEvent("ResourceTransferred", resource_type, transfer_qty, source_id, dest_id))
    return new_src, new_dst, transfer_qty, events


def deposit_resource_items(
    source_items: Sequence[Mapping[str, Any]],
    dest_items: Sequence[Mapping[str, Any]],
    resource_type: str,
    quantity: float,
    source_id: str,
    dest_id: str,
    dest_capacity: float = 500.0,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], float, list[ResourceEvent]]:
    new_src, new_dst, qty, events = transfer_resource_items(
        source_items, dest_items, resource_type, quantity, source_id, dest_id, dest_capacity
    )
    if qty > 0.0:
        events.append(ResourceEvent("ResourceDeposited", resource_type, qty, source_id, dest_id))
    return new_src, new_dst, qty, events


def withdraw_resource_items(
    source_items: Sequence[Mapping[str, Any]],
    dest_items: Sequence[Mapping[str, Any]],
    resource_type: str,
    quantity: float,
    source_id: str,
    dest_id: str,
    dest_capacity: float = 500.0,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], float, list[ResourceEvent]]:
    new_src, new_dst, qty, events = transfer_resource_items(
        source_items, dest_items, resource_type, quantity, source_id, dest_id, dest_capacity
    )
    if qty > 0.0:
        events.append(ResourceEvent("ResourceWithdrawn", resource_type, qty, source_id, dest_id))
    return new_src, new_dst, qty, events


def store_resource_items(
    source_items: Sequence[Mapping[str, Any]],
    dest_items: Sequence[Mapping[str, Any]],
    resource_type: str,
    quantity: float,
    source_id: str,
    dest_id: str,
    dest_capacity: float = 500.0,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], float, list[ResourceEvent]]:
    new_src, new_dst, qty, events = transfer_resource_items(
        source_items, dest_items, resource_type, quantity, source_id, dest_id, dest_capacity
    )
    if qty > 0.0:
        events.append(ResourceEvent("ResourceStored", resource_type, qty, source_id, dest_id))
    return new_src, new_dst, qty, events


def create_resource_item(
    dest_items: Sequence[Mapping[str, Any]],
    resource_type: str,
    quantity: float,
    dest_id: str,
    dest_capacity: float = 500.0,
) -> tuple[list[dict[str, Any]], float, list[ResourceEvent]]:
    dst = [dict(item) for item in dest_items]
    dest_current_total = calculate_total_quantity(dst)
    available_capacity = max(0.0, dest_capacity - dest_current_total)
    create_qty = min(float(quantity), available_capacity)
    if create_qty <= 0.0:
        return dst, 0.0, []

    added = False
    new_dst: list[dict[str, Any]] = []
    for item in dst:
        if str(item.get("identifier")) == resource_type and not added:
            new_dst.append({**item, "quantity": float(item.get("quantity", 0.0)) + create_qty})
            added = True
        else:
            new_dst.append(item)

    if not added:
        new_dst.append({"identifier": resource_type, "quantity": create_qty, "properties": {}})

    events = [ResourceEvent("ResourceCreated", resource_type, create_qty, None, dest_id)]
    return new_dst, create_qty, events


def consume_resource_item(
    items: Sequence[Mapping[str, Any]],
    resource_type: str,
    quantity: float,
    entity_id: str,
) -> tuple[list[dict[str, Any]], float, list[ResourceEvent]]:
    src = [dict(item) for item in items]
    events: list[ResourceEvent] = []
    available = sum(float(item.get("quantity", 0.0)) for item in src if str(item.get("identifier")) == resource_type)
    consume_qty = min(float(quantity), available)

    if consume_qty <= 0.0:
        return src, 0.0, []

    remaining_to_consume = consume_qty
    new_src: list[dict[str, Any]] = []
    for item in src:
        if str(item.get("identifier")) == resource_type and remaining_to_consume > 0.0:
            item_qty = float(item.get("quantity", 0.0))
            take = min(item_qty, remaining_to_consume)
            remaining_to_consume -= take
            left = item_qty - take
            if left > 0.0:
                new_src.append({**item, "quantity": left})
        else:
            new_src.append(item)

    events.append(ResourceEvent("ResourceConsumed", resource_type, consume_qty, entity_id, None))
    if available - consume_qty <= 0.0:
        events.append(ResourceEvent("ResourceExhausted", resource_type, available, entity_id, None))

    return new_src, consume_qty, events
