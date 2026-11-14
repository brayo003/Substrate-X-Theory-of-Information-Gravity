from __future__ import annotations

from typing import Any, Mapping

from .economy_events import (
    ItemCrafted,
    ProductionCompleted,
    ShortageDetected,
    SurplusDetected,
)
from .economy_models import DemandSignal, Recipe, StockLevel, SupplySignal

STANDARD_RECIPES: dict[str, Recipe] = {
    "wheat_to_flour": Recipe(
        recipe_id="r1",
        name="wheat_to_flour",
        building_type="Mill",
        inputs=(("wheat", 2.0),),
        outputs=(("flour", 2.0),),
        labor_ticks=1,
        profession_required="farmer",
    ),
    "flour_to_bread": Recipe(
        recipe_id="r2",
        name="flour_to_bread",
        building_type="Bakery",
        inputs=(("flour", 1.0), ("water", 1.0)),
        outputs=(("bread", 2.0), ("food", 2.0)),
        labor_ticks=1,
        profession_required="innkeeper",
    ),
    "trees_to_wood": Recipe(
        recipe_id="r3",
        name="trees_to_wood",
        building_type="Forest",
        inputs=(("trees", 1.0),),
        outputs=(("wood", 2.0),),
        labor_ticks=1,
        profession_required="woodcutter",
    ),
    "wood_to_planks": Recipe(
        recipe_id="r4",
        name="wood_to_planks",
        building_type="Workshop",
        inputs=(("wood", 1.0),),
        outputs=(("planks", 2.0),),
        labor_ticks=1,
        profession_required="woodcutter",
    ),
    "planks_to_tools": Recipe(
        recipe_id="r5",
        name="planks_to_tools",
        building_type="Blacksmith",
        inputs=(("planks", 2.0), ("iron", 1.0)),
        outputs=(("tools", 1.0),),
        labor_ticks=1,
        profession_required="blacksmith",
    ),
    "ore_to_iron": Recipe(
        recipe_id="r6",
        name="ore_to_iron",
        building_type="Blacksmith",
        inputs=(("iron_ore", 1.0), ("fuel", 1.0)),
        outputs=(("iron", 1.0),),
        labor_ticks=1,
        profession_required="blacksmith",
    ),
    "iron_to_tools": Recipe(
        recipe_id="r7",
        name="iron_to_tools",
        building_type="Blacksmith",
        inputs=(("iron", 2.0), ("wood", 1.0)),
        outputs=(("tools", 1.0),),
        labor_ticks=1,
        profession_required="blacksmith",
    ),
    "raw_meat_to_meal": Recipe(
        recipe_id="r8",
        name="raw_meat_to_meal",
        building_type="Tavern",
        inputs=(("meat", 1.0), ("fuel", 1.0)),
        outputs=(("food", 2.0),),
        labor_ticks=1,
        profession_required="innkeeper",
    ),
}

MIN_THRESHOLDS: dict[str, float] = {
    "food": 25.0,
    "water": 20.0,
    "wood": 15.0,
    "seeds": 15.0,
    "tools": 5.0,
    "fuel": 10.0,
    "iron": 5.0,
    "flour": 10.0,
    "bread": 10.0,
    "planks": 10.0,
}

TARGET_CAPACITIES: dict[str, float] = {
    "food": 200.0,
    "water": 200.0,
    "wood": 200.0,
    "seeds": 100.0,
    "tools": 50.0,
    "fuel": 100.0,
    "iron": 50.0,
    "flour": 100.0,
    "bread": 100.0,
    "planks": 100.0,
}


def evaluate_village_stock(world_state: Mapping[str, Any]) -> dict[str, StockLevel]:
    entities = dict(world_state.get("entities", {}))
    stock_totals: dict[str, float] = {key: 0.0 for key in MIN_THRESHOLDS}

    for entity_id, entity_data in entities.items():
        components = dict(entity_data.get("components", {}))
        inv_comp = dict(components.get("InventoryComponent", {}))
        items = list(inv_comp.get("items", ()))
        for item in items:
            identifier = str(item.get("identifier", "food"))
            qty = max(0.0, float(item.get("quantity", 0.0)))
            stock_totals[identifier] = stock_totals.get(identifier, 0.0) + qty

    result: dict[str, StockLevel] = {}
    for res_type, qty in sorted(stock_totals.items()):
        min_t = MIN_THRESHOLDS.get(res_type, 10.0)
        target_cap = TARGET_CAPACITIES.get(res_type, 100.0)
        result[res_type] = StockLevel(
            resource_type=res_type,
            current_quantity=qty,
            target_capacity=target_cap,
            min_threshold=min_t,
        )

    return result


def detect_demand_signals(
    stock_levels: dict[str, StockLevel],
    world_state: Mapping[str, Any],
) -> list[DemandSignal]:
    signals: list[DemandSignal] = []

    for res_type, stock in sorted(stock_levels.items()):
        if stock.current_quantity < stock.min_threshold:
            shortage = stock.min_threshold - stock.current_quantity
            severity = min(1.0, shortage / max(1.0, stock.min_threshold))
            signals.append(
                DemandSignal(
                    resource_type=res_type,
                    severity=severity,
                    shortage_amount=shortage,
                    rationale=f"Village stock of {res_type} ({stock.current_quantity:.1f}) is below minimum threshold ({stock.min_threshold:.1f})",
                )
            )

    entities = dict(world_state.get("entities", {}))
    for entity_id, entity_data in sorted(entities.items()):
        meta = dict(entity_data.get("metadata", {}))
        if meta.get("occupation") == "farmer":
            inv_comp = dict(dict(entity_data.get("components", {})).get("InventoryComponent", {}))
            items = list(inv_comp.get("items", ()))
            seed_qty = sum(float(i.get("quantity", 0.0)) for i in items if str(i.get("identifier")) == "seeds")
            if seed_qty < 2.0:
                signals.append(
                    DemandSignal(
                        resource_type="seeds",
                        severity=0.8,
                        shortage_amount=5.0 - seed_qty,
                        location_id=entity_id,
                        rationale="Farmer is short on seeds",
                    )
                )

    return signals


def detect_supply_signals(
    stock_levels: dict[str, StockLevel],
    world_state: Mapping[str, Any],
) -> list[SupplySignal]:
    signals: list[SupplySignal] = []
    entities = dict(world_state.get("entities", {}))

    for entity_id, entity_data in sorted(entities.items()):
        components = dict(entity_data.get("components", {}))
        inv_comp = dict(components.get("InventoryComponent", {}))
        items = list(inv_comp.get("items", ()))
        for item in items:
            identifier = str(item.get("identifier"))
            qty = float(item.get("quantity", 0.0))
            if qty > 5.0:
                signals.append(
                    SupplySignal(
                        resource_type=identifier,
                        available_quantity=qty,
                        location_id=entity_id,
                    )
                )

    return signals


def validate_crafting(crafter_inventory: list[dict[str, Any]], recipe: Recipe) -> tuple[bool, str]:
    available: dict[str, float] = {}
    for item in crafter_inventory:
        ident = str(item.get("identifier"))
        qty = float(item.get("quantity", 0.0))
        available[ident] = available.get(ident, 0.0) + qty

    for input_name, required_qty in recipe.inputs:
        if available.get(input_name, 0.0) < required_qty:
            return False, f"Missing required input {input_name} (need {required_qty}, have {available.get(input_name, 0.0)})"

    return True, "Valid"


def calculate_craft_result(
    crafter_inventory: list[dict[str, Any]],
    recipe: Recipe,
    crafter_id: str,
    capacity: float = 500.0,
    tick: int = 0,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[Any]]:
    valid, reason = validate_crafting(crafter_inventory, recipe)
    if not valid:
        return crafter_inventory, [], []

    from ..resources.resources_rules import consume_resource_item, deposit_resource_items

    current_items = list(crafter_inventory)
    events: list[Any] = []

    # Deduct exact inputs
    for input_name, input_qty in recipe.inputs:
        current_items, consumed, res_events = consume_resource_item(
            items=current_items,
            resource_type=input_name,
            quantity=input_qty,
            entity_id=crafter_id,
        )

    # Add exact outputs
    from ..resources.resources_rules import create_resource_item

    produced_descriptors = []
    for output_name, output_qty in recipe.outputs:
        current_items, create_qty, res_events = create_resource_item(
            dest_items=current_items,
            resource_type=output_name,
            quantity=output_qty,
            dest_id=crafter_id,
            dest_capacity=capacity,
        )
        produced_descriptors.append({"identifier": output_name, "quantity": create_qty})
        events.append(ItemCrafted(item_type=output_name, quantity=create_qty, crafter_id=crafter_id, tick=tick))
        events.append(
            ProductionCompleted(
                crafter_id=crafter_id,
                recipe_name=recipe.name,
                output_resource=output_name,
                output_quantity=create_qty,
                tick=tick,
            )
        )

    return current_items, produced_descriptors, events
