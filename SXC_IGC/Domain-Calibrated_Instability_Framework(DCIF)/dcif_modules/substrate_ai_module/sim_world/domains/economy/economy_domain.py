from __future__ import annotations

from typing import Any, Mapping

from ...core.contracts import TransitionProposal
from ...entities.components import InventoryComponent, ResourceDescriptor
from ...simulation.simulation_engine import SimulationEngine
from .economy_events import (
    FoodDelivered,
    ItemCrafted,
    ProductionCompleted,
    ProductionStarted,
    ShortageDetected,
    SurplusDetected,
    TradeExecuted,
)
from .economy_models import Recipe, StockLevel
from .economy_rules import (
    MIN_THRESHOLDS,
    STANDARD_RECIPES,
    TARGET_CAPACITIES,
    calculate_craft_result,
    detect_demand_signals,
    detect_supply_signals,
    evaluate_village_stock,
    validate_crafting,
)


def register(engine: SimulationEngine) -> None:
    engine.register_domain("economy", lambda engine, context: apply(context))


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


def initialize_valley_economy(kernel: Any) -> dict[str, Any]:
    world_state = dict(kernel.current_state)
    stock = evaluate_village_stock(world_state)
    demand = detect_demand_signals(stock, world_state)
    supply = detect_supply_signals(stock, world_state)

    economy_state = {
        "stock": {k: v.to_dict() for k, v in stock.items()},
        "demand": [d.to_dict() for d in demand],
        "supply": [s.to_dict() for s in supply],
        "recipes": {k: v.to_dict() for k, v in STANDARD_RECIPES.items()},
        "active_crafts": [],
        "open_trades": [],
    }

    if hasattr(kernel, "_state") and isinstance(kernel._state, dict):
        kernel._state["economy"] = economy_state

    return economy_state


def apply(context: Any) -> tuple[TransitionProposal, ...]:
    world_state = dict(context.world_state)
    tick = int(context.tick_number)

    stock = evaluate_village_stock(world_state)
    demand = detect_demand_signals(stock, world_state)
    supply = detect_supply_signals(stock, world_state)

    events: list[dict[str, Any]] = []
    for d in demand:
        if d.severity >= 0.5:
            events.append(
                ShortageDetected(
                    item_type=d.resource_type,
                    shortage_amount=d.shortage_amount,
                    location_id=d.location_id,
                    tick=tick,
                ).to_dict()
            )

    for s in supply:
        if s.available_quantity > 50.0:
            events.append(
                SurplusDetected(
                    item_type=s.resource_type,
                    surplus_amount=s.available_quantity,
                    location_id=s.location_id,
                    tick=tick,
                ).to_dict()
            )

    patch = {
        "economy": {
            "stock": {k: v.to_dict() for k, v in stock.items()},
            "demand": [d.to_dict() for d in demand],
            "supply": [s.to_dict() for s in supply],
        }
    }

    # Fix: Ensure state_revision is None when there's no current revision
    state_revision = context.committed_revision
    if state_revision == 0 and context.committed_revision is None:
        state_revision = None
    
    return (
        TransitionProposal(
            world_id=context.world_id,
            tick_id=context.tick_context.tick_id,
            state_revision=state_revision,
            correlation_id=context.tick_context.correlation_id,
            subject="domain.economy",
            patch=patch,
            description="economy domain update",
            metadata={"domain": "economy", "events": events},
        ),
    )


def craft_recipe(
    ctx: Any,
    actor_id: Any,
    recipe_name: str,
    building_id: Any = None,
) -> TransitionProposal:
    actor_key = str(actor_id.value) if hasattr(actor_id, "value") else str(actor_id)
    world_state, world_id, tick_number = _extract_context(ctx)

    recipe = STANDARD_RECIPES.get(recipe_name)
    if recipe is None:
        recipe = Recipe(
            recipe_id=recipe_name,
            name=recipe_name,
            building_type="Workshop",
            inputs=(("wood", 1.0),),
            outputs=(("tools", 1.0),),
        )

    entities = dict(world_state.get("entities", {}))
    actor_data = dict(entities.get(actor_key, {}))
    inv_comp = dict(dict(actor_data.get("components", {})).get("InventoryComponent", {}))
    items = list(inv_comp.get("items", ()))

    cap = _safe_capacity(inv_comp)
    new_items, produced, events = calculate_craft_result(
        crafter_inventory=items,
        recipe=recipe,
        crafter_id=actor_key,
        capacity=cap,
        tick=tick_number,
    )

    patch = {
        "entities": {
            actor_key: {
                "components": {
                    "InventoryComponent": {
                        "items": tuple(new_items),
                        "capacity": cap,
                        "component_type": "InventoryComponent",
                    }
                }
            }
        }
    }

    return TransitionProposal(
        world_id=world_id,
        tick_id=getattr(getattr(ctx, "tick_context", None), "tick_id", None),
        state_revision=None,
        correlation_id=f"craft:{recipe_name}:{actor_key}",
        subject="CraftProposal",
        patch=patch,
        description=f"Craft {recipe_name} by {actor_key}",
        metadata={
            "domain": "economy",
            "recipe_name": recipe_name,
            "produced": produced,
            "events": [e.to_dict() for e in events],
        },
    )


def trade_resource(
    ctx: Any,
    buyer_id: Any,
    seller_id: Any,
    item_given: str,
    qty_given: float,
    item_received: str,
    qty_received: float,
) -> TransitionProposal:
    buyer_key = str(buyer_id.value) if hasattr(buyer_id, "value") else str(buyer_id)
    seller_key = str(seller_id.value) if hasattr(seller_id, "value") else str(seller_id)
    world_state, world_id, tick_number = _extract_context(ctx)

    entities = dict(world_state.get("entities", {}))
    buyer_data = dict(entities.get(buyer_key, {}))
    seller_data = dict(entities.get(seller_key, {}))

    buyer_inv = dict(dict(buyer_data.get("components", {})).get("InventoryComponent", {}))
    seller_inv = dict(dict(seller_data.get("components", {})).get("InventoryComponent", {}))

    buyer_items = list(buyer_inv.get("items", ()))
    seller_items = list(seller_inv.get("items", ()))

    from ..resources.resources_rules import transfer_resource_items

    # Transfer item_given from buyer to seller
    b_after_give, s_after_give, give_qty, _ = transfer_resource_items(
        source_items=buyer_items,
        dest_items=seller_items,
        resource_type=item_given,
        quantity=qty_given,
        source_id=buyer_key,
        dest_id=seller_key,
        dest_capacity=_safe_capacity(seller_inv),
    )

    # Transfer item_received from seller to buyer
    s_final, b_final, rec_qty, _ = transfer_resource_items(
        source_items=s_after_give,
        dest_items=b_after_give,
        resource_type=item_received,
        quantity=qty_received,
        source_id=seller_key,
        dest_id=buyer_key,
        dest_capacity=_safe_capacity(buyer_inv),
    )

    trade_event = TradeExecuted(
        seller_id=seller_key,
        buyer_id=buyer_key,
        item_given=item_given,
        qty_given=give_qty,
        item_received=item_received,
        qty_received=rec_qty,
        tick=tick_number,
    )

    patch = {
        "entities": {
            buyer_key: {
                "components": {
                    "InventoryComponent": {
                        "items": tuple(b_final),
                        "capacity": _safe_capacity(buyer_inv),
                        "component_type": "InventoryComponent",
                    }
                }
            },
            seller_key: {
                "components": {
                    "InventoryComponent": {
                        "items": tuple(s_final),
                        "capacity": _safe_capacity(seller_inv),
                        "component_type": "InventoryComponent",
                    }
                }
            },
        }
    }

    return TransitionProposal(
        world_id=world_id,
        tick_id=getattr(getattr(ctx, "tick_context", None), "tick_id", None),
        state_revision=None,
        correlation_id=f"trade:{buyer_key}:{seller_key}",
        subject="TradeProposal",
        patch=patch,
        description=f"Trade {give_qty} {item_given} for {rec_qty} {item_received}",
        metadata={
            "domain": "economy",
            "events": [trade_event.to_dict()],
        },
    )


def deliver_resource(
    ctx: Any,
    actor_id: Any,
    source_id: Any,
    dest_id: Any,
    resource_type: str,
    quantity: float,
) -> TransitionProposal:
    actor_key = str(actor_id.value) if hasattr(actor_id, "value") else str(actor_id)
    source_key = str(source_id.value) if hasattr(source_id, "value") else str(source_id)
    dest_key = str(dest_id.value) if hasattr(dest_id, "value") else str(dest_id)
    world_state, world_id, tick_number = _extract_context(ctx)

    entities = dict(world_state.get("entities", {}))
    src_data = dict(entities.get(source_key, {}))
    dst_data = dict(entities.get(dest_key, {}))

    src_inv = dict(dict(src_data.get("components", {})).get("InventoryComponent", {}))
    dst_inv = dict(dict(dst_data.get("components", {})).get("InventoryComponent", {}))

    src_items = list(src_inv.get("items", ()))
    dst_items = list(dst_inv.get("items", ()))

    from ..resources.resources_rules import transfer_resource_items
    new_src, new_dst, qty, _ = transfer_resource_items(
        source_items=src_items,
        dest_items=dst_items,
        resource_type=resource_type,
        quantity=quantity,
        source_id=source_key,
        dest_id=dest_key,
        dest_capacity=_safe_capacity(dst_inv),
    )

    delivered_event = FoodDelivered(
        source_id=source_key,
        dest_id=dest_key,
        quantity=qty,
        tick=tick_number,
    )

    patch = {
        "entities": {
            source_key: {
                "components": {
                    "InventoryComponent": {
                        "items": tuple(new_src),
                        "capacity": _safe_capacity(src_inv),
                        "component_type": "InventoryComponent",
                    }
                }
            },
            dest_key: {
                "components": {
                    "InventoryComponent": {
                        "items": tuple(new_dst),
                        "capacity": _safe_capacity(dst_inv),
                        "component_type": "InventoryComponent",
                    }
                }
            },
        }
    }

    return TransitionProposal(
        world_id=world_id,
        tick_id=getattr(getattr(ctx, "tick_context", None), "tick_id", None),
        state_revision=None,
        correlation_id=f"deliver:{resource_type}:{source_key}:{dest_key}",
        subject="DeliverProposal",
        patch=patch,
        description=f"Deliver {qty} {resource_type} from {source_key} to {dest_key}",
        metadata={
            "domain": "economy",
            "events": [delivered_event.to_dict()],
        },
    )


def _econ_goal_pending(manager, worker_eid, recipe_name: str) -> bool:
    """Idempotency guard: is a non-terminal CraftRecipe goal for the given
    recipe already outstanding? Without it the economy re-created craft goals
    for every demanded recipe EVERY tick, flooding the planner with duplicate
    goals and slowing the sim toward a crawl."""
    for goal in manager.list_goals(include_terminal=False):
        if goal.kind != "CraftRecipe":
            continue
        if goal.entity_id is not None and goal.entity_id != worker_eid:
            continue
        rn = goal.target_state.get("recipe_name") or goal.metadata.get("recipe_name")
        if str(rn) == str(recipe_name):
            return True
    return False


def generate_economy_goals(kernel: Any) -> list[Any]:
    manager = kernel.planner_engine.goal_manager
    goals = []

    world_state = dict(kernel.current_state)
    stock = evaluate_village_stock(world_state)
    demands = detect_demand_signals(stock, world_state)

    human_entities = [e for e in kernel.entity_registry.list_entities() if getattr(e, "type", "") == "human"]
    if not human_entities:
        return goals

    # Map professions to workers
    profession_map: dict[str, Any] = {}
    for h in human_entities:
        occ = dict(getattr(h, "metadata", {})).get("occupation", "")
        if occ and occ not in profession_map:
            profession_map[occ] = h

    first_worker = human_entities[0]

    for d in demands:
        res = d.resource_type
        if res == "flour":
            worker = profession_map.get("farmer", first_worker)
            if _econ_goal_pending(manager, worker.entity_id, "wheat_to_flour"):
                continue
            goal = manager.create_goal(
                subject="Grind Wheat to Flour",
                kind="CraftRecipe",
                entity_id=worker.entity_id,
                target_state={"recipe_name": "wheat_to_flour", "action": "CraftRecipe"},
                priority=18,
                created_tick=kernel.current_tick_number,
                metadata={"recipe_name": "wheat_to_flour"},
            )
            goals.append(goal)
        elif res in ("bread", "food"):
            worker = profession_map.get("innkeeper", first_worker)
            if _econ_goal_pending(manager, worker.entity_id, "flour_to_bread"):
                continue
            goal = manager.create_goal(
                subject="Bake Bread",
                kind="CraftRecipe",
                entity_id=worker.entity_id,
                target_state={"recipe_name": "flour_to_bread", "action": "CraftRecipe"},
                priority=22,
                created_tick=kernel.current_tick_number,
                metadata={"recipe_name": "flour_to_bread"},
            )
            goals.append(goal)
        elif res == "wood":
            worker = profession_map.get("woodcutter", first_worker)
            if _econ_goal_pending(manager, worker.entity_id, "trees_to_wood"):
                continue
            goal = manager.create_goal(
                subject="Gather Wood",
                kind="CraftRecipe",
                entity_id=worker.entity_id,
                target_state={"recipe_name": "trees_to_wood", "action": "CraftRecipe"},
                priority=16,
                created_tick=kernel.current_tick_number,
                metadata={"recipe_name": "trees_to_wood"},
            )
            goals.append(goal)
        elif res == "tools":
            worker = profession_map.get("blacksmith", first_worker)
            if _econ_goal_pending(manager, worker.entity_id, "iron_to_tools"):
                continue
            goal = manager.create_goal(
                subject="Craft Tools",
                kind="CraftRecipe",
                entity_id=worker.entity_id,
                target_state={"recipe_name": "iron_to_tools", "action": "CraftRecipe"},
                priority=20,
                created_tick=kernel.current_tick_number,
                metadata={"recipe_name": "iron_to_tools"},
            )
            goals.append(goal)

    return goals
