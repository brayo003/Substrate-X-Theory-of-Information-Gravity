from __future__ import annotations

from typing import Any, Mapping

from ...core.contracts import TransitionProposal
from ...entities.components import InventoryComponent, ResourceDescriptor
from ...simulation.simulation_engine import SimulationEngine
from .resources_rules import (
    calculate_total_quantity,
    consume_resource_item,
    transfer_resource_items,
    validate_inventory_capacity,
)


def register(engine: SimulationEngine) -> None:
    engine.register_domain("resources", lambda engine, context: apply(context))


def apply(context: Any) -> tuple[TransitionProposal, ...]:
    world_state = context.world_state
    entities = dict(world_state.get("entities", {}))

    entity_patches: dict[str, Any] = {}
    events: list[dict[str, Any]] = []
    
    # Process harvest signals - decrease farm stock
    harvest_signals = list(world_state.get("action_harvest_signals", []))
    farm_stock_updates: dict[str, dict[str, float]] = {}
    
    for signal in harvest_signals:
        target_id = signal.get("target_id")
        item_id = signal.get("item_id")
        quantity = signal.get("quantity", 1)
        
        if target_id not in farm_stock_updates:
            farm_stock_updates[target_id] = {}
        
        if item_id not in farm_stock_updates[target_id]:
            farm_stock_updates[target_id][item_id] = 0.0
        
        farm_stock_updates[target_id][item_id] += quantity

    for entity_id_str, entity_data in sorted(entities.items()):
        components = dict(entity_data.get("components", {}))
        inv_comp = dict(components.get("InventoryComponent", {}))
        metadata = dict(entity_data.get("metadata", {}))
        
        # Handle farm stock tracking (conservation and regrowth)
        entity_name = metadata.get("name", entity_id_str)
        entity_type = str(entity_data.get("type", ""))
        
        current_stock = dict(metadata.get("farm_stock", {}))
        stock_changed = False
        
        is_farm = entity_type == "farm" or entity_name == "Farm" or "farm" in entity_name.lower() or bool(current_stock)
        
        # Decrease stock on harvest
        if entity_name in farm_stock_updates:
            for item_id, harvested_qty in farm_stock_updates[entity_name].items():
                current_qty = current_stock.get(item_id, 0.0)
                new_qty = max(0.0, current_qty - harvested_qty)
                current_stock[item_id] = new_qty
                stock_changed = True
        
        # Regrowth for farms
        if is_farm and current_stock:
            regrowth_rates = {"wheat": 0.02, "seeds": 0.01}
            for item_id, current_qty in current_stock.items():
                rate = regrowth_rates.get(item_id, 0.0)
                regrowth = current_qty * rate
                new_qty = current_qty + regrowth
                if new_qty != current_qty:
                    current_stock[item_id] = new_qty
                    stock_changed = True
        
        if stock_changed:
            if entity_id_str not in entity_patches:
                entity_patches[entity_id_str] = {}
            entity_patches[entity_id_str]["metadata"] = {**metadata, "farm_stock": current_stock}
        
        # Handle inventory sanitization
        if not inv_comp:
            continue
        items = list(inv_comp.get("items", ()))
        capacity = inv_comp.get("capacity", 500.0)

        sanitized_items = []
        modified = False
        for item in items:
            qty = max(0.0, float(item.get("quantity", 0.0)))
            if qty != float(item.get("quantity", 0.0)):
                modified = True
            sanitized_items.append({**item, "quantity": qty})

        if modified:
            if entity_id_str not in entity_patches:
                entity_patches[entity_id_str] = {}
            if "components" not in entity_patches[entity_id_str]:
                entity_patches[entity_id_str]["components"] = {}
            entity_patches[entity_id_str]["components"]["InventoryComponent"] = {
                "items": tuple(sanitized_items),
                "capacity": capacity,
                "component_type": "InventoryComponent",
            }

    if not entity_patches:
        return ()

    return (
        TransitionProposal(
            world_id=context.world_id,
            tick_id=context.tick_context.tick_id,
            state_revision=context.committed_revision,
            correlation_id=context.tick_context.correlation_id,
            subject="domain.resources",
            patch={"entity_inventory_components": entity_patches},
            description="resources domain update (with farm stock conservation and regrowth)",
            metadata={"domain": "resources", "events": events, "farm_stock_updates": farm_stock_updates},
        ),
    )


def initialize_valley_resources(kernel: Any) -> dict[str, Any]:
    registry = kernel.entity_registry

    building_resources: dict[str, list[ResourceDescriptor]] = {
        "Farm": [ResourceDescriptor("seeds", 50.0, {}), ResourceDescriptor("food", 20.0, {})],
        "Well": [ResourceDescriptor("water", 100.0, {})],
        "Forest": [ResourceDescriptor("wood", 100.0, {})],
        "River": [ResourceDescriptor("water", 100.0, {})],
        "Storage": [
            ResourceDescriptor("food", 50.0, {}),
            ResourceDescriptor("wood", 50.0, {}),
            ResourceDescriptor("stone", 30.0, {}),
            ResourceDescriptor("iron", 20.0, {}),
            ResourceDescriptor("tools", 10.0, {}),
            ResourceDescriptor("fuel", 40.0, {}),
        ],
        "Blacksmith": [ResourceDescriptor("iron", 30.0, {}), ResourceDescriptor("tools", 15.0, {})],
        "Barn": [ResourceDescriptor("seeds", 30.0, {}), ResourceDescriptor("food", 30.0, {})],
        "Tavern": [ResourceDescriptor("food", 30.0, {}), ResourceDescriptor("water", 20.0, {})],
        "House 1": [ResourceDescriptor("food", 10.0, {}), ResourceDescriptor("water", 10.0, {})],
        "House 2": [ResourceDescriptor("food", 10.0, {}), ResourceDescriptor("water", 10.0, {})],
        "House 3": [ResourceDescriptor("food", 10.0, {}), ResourceDescriptor("water", 10.0, {})],
        "House 4": [ResourceDescriptor("food", 10.0, {}), ResourceDescriptor("water", 10.0, {})],
    }
    
    # Farm stock initialization (for conservation tracking)
    farm_stock_initial: dict[str, dict[str, float]] = {
        "Farm": {"wheat": 1000.0, "seeds": 100.0},
    }

    initialized: dict[str, Any] = {}
    for entity in registry.list_entities():
        display = str(entity.display_name)
        if display in building_resources:
            # Check if entity already has InventoryComponent
            if "InventoryComponent" not in entity.components:
                items = tuple(building_resources[display])
                entity.attach_component(InventoryComponent(items=items, capacity=500.0), tick=0)
            
            # Initialize farm stock for conservation tracking
            if display in farm_stock_initial:
                entity.metadata = {**(entity.metadata or {}), "farm_stock": farm_stock_initial[display]}
            
            initialized[display] = entity

    kernel._sync_entity_state()
    return initialized


def transfer_resource(
    kernel: Any,
    source_entity_id: Any,
    dest_entity_id: Any,
    resource_type: str,
    quantity: float,
) -> TransitionProposal:
    source_key = str(source_entity_id.value) if hasattr(source_entity_id, "value") else str(source_entity_id)
    dest_key = str(dest_entity_id.value) if hasattr(dest_entity_id, "value") else str(dest_entity_id)

    entities = dict(kernel.current_state.get("entities", {}))
    src_data = dict(entities.get(source_key, {}))
    dst_data = dict(entities.get(dest_key, {}))

    src_inv = dict(dict(src_data.get("components", {})).get("InventoryComponent", {}))
    dst_inv = dict(dict(dst_data.get("components", {})).get("InventoryComponent", {}))

    src_items = list(src_inv.get("items", ()))
    dst_items = list(dst_inv.get("items", ()))
    dst_cap = float(dst_inv.get("capacity", 500.0))

    new_src, new_dst, qty, events = transfer_resource_items(
        source_items=src_items,
        dest_items=dst_items,
        resource_type=resource_type,
        quantity=quantity,
        source_id=source_key,
        dest_id=dest_key,
        dest_capacity=dst_cap,
    )

    patch = {
        "entities": {
            source_key: {
                "components": {
                    "InventoryComponent": {
                        "items": tuple(new_src),
                        "capacity": src_inv.get("capacity", 500.0),
                        "component_type": "InventoryComponent",
                    }
                }
            },
            dest_key: {
                "components": {
                    "InventoryComponent": {
                        "items": tuple(new_dst),
                        "capacity": dst_cap,
                        "component_type": "InventoryComponent",
                    }
                }
            },
        }
    }

    return TransitionProposal(
        world_id=kernel.world_id,
        tick_id=None,
        state_revision=kernel.current_revision.revision_id if kernel.current_revision else None,
        correlation_id=f"transfer:{resource_type}:{source_key}:{dest_key}",
        subject="TransferResource",
        patch=patch,
        description=f"Transfer {quantity} {resource_type} from {source_key} to {dest_key}",
        metadata={"domain": "resources", "events": [e.to_dict() for e in events], "transferred_quantity": qty},
    )


def deposit_resource(
    kernel: Any,
    source_entity_id: Any,
    dest_entity_id: Any,
    resource_type: str,
    quantity: float,
) -> TransitionProposal:
    proposal = transfer_resource(kernel, source_entity_id, dest_entity_id, resource_type, quantity)
    source_key = str(source_entity_id.value) if hasattr(source_entity_id, "value") else str(source_entity_id)
    dest_key = str(dest_entity_id.value) if hasattr(dest_entity_id, "value") else str(dest_entity_id)
    qty = proposal.metadata.get("transferred_quantity", 0.0)
    events = [e for e in proposal.metadata.get("events", [])]
    if qty > 0.0:
        events.append({"event_type": "ResourceDeposited", "resource_type": resource_type, "quantity": qty, "source_id": source_key, "destination_id": dest_key, "metadata": {}})
    return TransitionProposal(
        world_id=proposal.world_id,
        tick_id=proposal.tick_id,
        state_revision=proposal.state_revision,
        correlation_id=f"deposit:{resource_type}:{source_key}:{dest_key}",
        subject="DepositResource",
        patch=proposal.patch,
        description=f"Deposit {quantity} {resource_type} into {dest_key}",
        metadata={"domain": "resources", "events": events, "deposited_quantity": qty},
    )


def withdraw_resource(
    kernel: Any,
    source_entity_id: Any,
    dest_entity_id: Any,
    resource_type: str,
    quantity: float,
) -> TransitionProposal:
    proposal = transfer_resource(kernel, source_entity_id, dest_entity_id, resource_type, quantity)
    source_key = str(source_entity_id.value) if hasattr(source_entity_id, "value") else str(source_entity_id)
    dest_key = str(dest_entity_id.value) if hasattr(dest_entity_id, "value") else str(dest_entity_id)
    qty = proposal.metadata.get("transferred_quantity", 0.0)
    events = [e for e in proposal.metadata.get("events", [])]
    if qty > 0.0:
        events.append({"event_type": "ResourceWithdrawn", "resource_type": resource_type, "quantity": qty, "source_id": source_key, "destination_id": dest_key, "metadata": {}})
    return TransitionProposal(
        world_id=proposal.world_id,
        tick_id=proposal.tick_id,
        state_revision=proposal.state_revision,
        correlation_id=f"withdraw:{resource_type}:{source_key}:{dest_key}",
        subject="WithdrawResource",
        patch=proposal.patch,
        description=f"Withdraw {quantity} {resource_type} from {source_key}",
        metadata={"domain": "resources", "events": events, "withdrawn_quantity": qty},
    )


def store_resource(
    kernel: Any,
    source_entity_id: Any,
    dest_entity_id: Any,
    resource_type: str,
    quantity: float,
) -> TransitionProposal:
    proposal = deposit_resource(kernel, source_entity_id, dest_entity_id, resource_type, quantity)
    source_key = str(source_entity_id.value) if hasattr(source_entity_id, "value") else str(source_entity_id)
    dest_key = str(dest_entity_id.value) if hasattr(dest_entity_id, "value") else str(dest_entity_id)
    qty = proposal.metadata.get("deposited_quantity", 0.0)
    events = [e for e in proposal.metadata.get("events", [])]
    if qty > 0.0:
        events.append({"event_type": "ResourceStored", "resource_type": resource_type, "quantity": qty, "source_id": source_key, "destination_id": dest_key, "metadata": {}})
    return TransitionProposal(
        world_id=proposal.world_id,
        tick_id=proposal.tick_id,
        state_revision=proposal.state_revision,
        correlation_id=f"store:{resource_type}:{source_key}:{dest_key}",
        subject="StoreResource",
        patch=proposal.patch,
        description=f"Store {quantity} {resource_type} in {dest_key}",
        metadata={"domain": "resources", "events": events, "stored_quantity": qty},
    )


def pickup_resource(
    kernel: Any,
    source_entity_id: Any,
    dest_entity_id: Any,
    resource_type: str,
    quantity: float,
) -> TransitionProposal:
    return withdraw_resource(kernel, source_entity_id, dest_entity_id, resource_type, quantity)


def consume_resource(
    kernel: Any,
    entity_id: Any,
    resource_type: str,
    quantity: float,
) -> TransitionProposal:
    key = str(entity_id.value) if hasattr(entity_id, "value") else str(entity_id)
    entities = dict(kernel.current_state.get("entities", {}))
    ent_data = dict(entities.get(key, {}))
    inv_comp = dict(dict(ent_data.get("components", {})).get("InventoryComponent", {}))
    items = list(inv_comp.get("items", ()))

    new_items, consumed_qty, events = consume_resource_item(
        items=items,
        resource_type=resource_type,
        quantity=quantity,
        entity_id=key,
    )

    patch = {
        "entities": {
            key: {
                "components": {
                    "InventoryComponent": {
                        "items": tuple(new_items),
                        "capacity": inv_comp.get("capacity", 500.0),
                        "component_type": "InventoryComponent",
                    }
                }
            }
        }
    }

    return TransitionProposal(
        world_id=kernel.world_id,
        tick_id=None,
        state_revision=kernel.current_revision.revision_id if kernel.current_revision else None,
        correlation_id=f"consume:{resource_type}:{key}",
        subject="ConsumeResource",
        patch=patch,
        description=f"Consume {consumed_qty} {resource_type} by {key}",
        metadata={"domain": "resources", "events": [e.to_dict() for e in events], "consumed_quantity": consumed_qty},
    )
