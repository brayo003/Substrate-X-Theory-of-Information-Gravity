from __future__ import annotations

import unittest
from datetime import datetime, timezone

from sim_world import KernelConfig, WorldKernel
from sim_world.core.contracts import TickContext, TransitionProposal
from sim_world.core.ids import TickId
from sim_world.domains import register_all
from sim_world.domains.agriculture import initialize_valley_agriculture
from sim_world.domains.economy import (
    MIN_THRESHOLDS,
    STANDARD_RECIPES,
    CraftRequest,
    DemandSignal,
    FoodDelivered,
    ItemCrafted,
    ProductionChain,
    Recipe,
    ShortageDetected,
    StockLevel,
    SupplySignal,
    TradeRequest,
    calculate_craft_result,
    craft_recipe,
    deliver_resource,
    detect_demand_signals,
    detect_supply_signals,
    evaluate_village_stock,
    generate_economy_goals,
    initialize_valley_economy,
    trade_resource,
    validate_crafting,
)
from sim_world.domains.population import initialize_valley_population
from sim_world.domains.resources import initialize_valley_resources
from sim_world.domains.terrain import initialize_valley_terrain
from sim_world.entities.components import InventoryComponent, ResourceDescriptor


class Loop5EconomyTests(unittest.TestCase):
    def setUp(self) -> None:
        self.config = KernelConfig(
            world_name="valley_world_economy",
            seed="economy-seed-001",
            initial_state={"mode": "valley_economy_simulation"},
        )
        self.kernel = WorldKernel(self.config)
        register_all(self.kernel.simulation_engine)
        self.terrain_entities = initialize_valley_terrain(self.kernel)
        self.villager_entities = initialize_valley_population(self.kernel)
        self.building_entities = initialize_valley_resources(self.kernel)
        self.crop_fields = initialize_valley_agriculture(self.kernel)
        self.economy_state = initialize_valley_economy(self.kernel)

    def _create_tick_context(self, correlation_id: str = "test_economy_correlation") -> TickContext:
        tick_id = TickId.new(self.kernel.world_id, self.kernel.current_tick_number)
        rev = self.kernel.current_revision.revision_id if self.kernel.current_revision else None
        return TickContext(
            world_id=self.kernel.world_id,
            tick_id=tick_id,
            state_revision=rev,
            parent_revision=rev,
            timestamp=datetime.now(timezone.utc),
            correlation_id=correlation_id,
        )

    def test_economy_models_and_recipes(self) -> None:
        self.assertIn("wheat_to_flour", STANDARD_RECIPES)
        self.assertIn("flour_to_bread", STANDARD_RECIPES)
        self.assertIn("wood_to_planks", STANDARD_RECIPES)
        self.assertIn("planks_to_tools", STANDARD_RECIPES)
        self.assertIn("ore_to_iron", STANDARD_RECIPES)

        recipe = STANDARD_RECIPES["wheat_to_flour"]
        self.assertEqual(recipe.name, "wheat_to_flour")
        self.assertEqual(recipe.building_type, "Mill")

        stock = StockLevel(resource_type="wheat", current_quantity=10.0, target_capacity=100.0, min_threshold=5.0)
        self.assertEqual(stock.resource_type, "wheat")
        self.assertEqual(stock.current_quantity, 10.0)

        chain = ProductionChain(chain_id="c1", name="BreadChain", steps=("Wheat", "Flour", "Bread"))
        self.assertEqual(chain.steps, ("Wheat", "Flour", "Bread"))

    def test_storage_accounting_and_stock_evaluation(self) -> None:
        stock = evaluate_village_stock(self.kernel.current_state)
        self.assertIn("food", stock)
        self.assertIn("water", stock)
        self.assertIn("wood", stock)
        self.assertGreaterEqual(stock["food"].current_quantity, 0.0)

    def test_demand_and_supply_signals(self) -> None:
        stock = evaluate_village_stock(self.kernel.current_state)
        # Create artificial shortage of bread and tools
        stock["bread"] = StockLevel(resource_type="bread", current_quantity=0.0, min_threshold=10.0)
        stock["tools"] = StockLevel(resource_type="tools", current_quantity=1.0, min_threshold=5.0)

        demands = detect_demand_signals(stock, self.kernel.current_state)
        demand_types = [d.resource_type for d in demands]
        self.assertIn("bread", demand_types)
        self.assertIn("tools", demand_types)

        supplies = detect_supply_signals(stock, self.kernel.current_state)
        self.assertTrue(isinstance(supplies, list))

    def test_crafting_and_resource_conservation(self) -> None:
        mira = self.villager_entities["Mira"]
        mira_id = mira.entity_id

        # Attach wheat to Mira for crafting flour
        mira.attach_component(
            InventoryComponent(items=(ResourceDescriptor("wheat", 10.0, {}),), capacity=100.0),
            tick=0,
        )
        self.kernel._sync_entity_state()

        prop = craft_recipe(self.kernel, mira_id, "wheat_to_flour")
        self.assertEqual(prop.subject, "CraftProposal")
        self.kernel.commit_state(self._create_tick_context("craft"), [prop])

        state = self.kernel.current_state
        mira_items = state["entities"][str(mira_id.value)]["components"]["InventoryComponent"]["items"]
        wheat_qty = sum(i["quantity"] for i in mira_items if i["identifier"] == "wheat")
        flour_qty = sum(i["quantity"] for i in mira_items if i["identifier"] == "flour")

        self.assertEqual(wheat_qty, 8.0)
        self.assertEqual(flour_qty, 2.0)

    def test_trade_proposals_and_exchange(self) -> None:
        mira = self.villager_entities["Mira"]
        joren = self.villager_entities["Joren"]

        mira.attach_component(InventoryComponent(items=(ResourceDescriptor("food", 10.0, {}),), capacity=100.0), tick=0)
        joren.attach_component(InventoryComponent(items=(ResourceDescriptor("tools", 2.0, {}),), capacity=100.0), tick=0)
        self.kernel._sync_entity_state()

        prop = trade_resource(self.kernel, mira.entity_id, joren.entity_id, "food", 5.0, "tools", 1.0)
        self.assertEqual(prop.subject, "TradeProposal")
        self.kernel.commit_state(self._create_tick_context("trade"), [prop])

        state = self.kernel.current_state
        mira_inv = state["entities"][str(mira.entity_id.value)]["components"]["InventoryComponent"]["items"]
        joren_inv = state["entities"][str(joren.entity_id.value)]["components"]["InventoryComponent"]["items"]

        mira_tools = sum(i["quantity"] for i in mira_inv if i["identifier"] == "tools")
        joren_food = sum(i["quantity"] for i in joren_inv if i["identifier"] == "food")

        self.assertEqual(mira_tools, 1.0)
        self.assertEqual(joren_food, 5.0)

    def test_resource_delivery(self) -> None:
        farm = self.building_entities["Farm"]
        storage = self.building_entities["Storage"]

        prop = deliver_resource(self.kernel, farm.entity_id, farm.entity_id, storage.entity_id, "food", 10.0)
        self.assertEqual(prop.subject, "DeliverProposal")
        self.kernel.commit_state(self._create_tick_context("deliver"), [prop])

        state = self.kernel.current_state
        storage_inv = state["entities"][str(storage.entity_id.value)]["components"]["InventoryComponent"]["items"]
        storage_food = sum(i["quantity"] for i in storage_inv if i["identifier"] == "food")
        self.assertGreaterEqual(storage_food, 60.0)

    def test_planner_economy_goal_generation(self) -> None:
        goals = generate_economy_goals(self.kernel)
        self.assertTrue(isinstance(goals, list))

    def test_proposal_generation(self) -> None:
        tick_ctx = self._create_tick_context("econ_tick")
        from sim_world.simulation.simulation_context import SimulationContext

        sim_ctx = SimulationContext(
            world_id=self.kernel.world_id,
            tick_context=tick_ctx,
            tick_number=self.kernel.current_tick_number,
            world_state=self.kernel.current_state,
            committed_revision=self.kernel.current_revision.revision_id if self.kernel.current_revision else None,
        )
        res = self.kernel.simulation_engine.advance(context=sim_ctx)
        econ_props = [p for p in res.proposals if p.subject == "domain.economy"]
        self.assertEqual(len(econ_props), 1)

    def test_deterministic_replay(self) -> None:
        kernel_a = WorldKernel(self.config)
        register_all(kernel_a.simulation_engine)
        initialize_valley_terrain(kernel_a)
        initialize_valley_population(kernel_a)
        initialize_valley_resources(kernel_a)
        initialize_valley_agriculture(kernel_a)
        initialize_valley_economy(kernel_a)

        kernel_b = WorldKernel(self.config)
        register_all(kernel_b.simulation_engine)
        initialize_valley_terrain(kernel_b)
        initialize_valley_population(kernel_b)
        initialize_valley_resources(kernel_b)
        initialize_valley_agriculture(kernel_b)
        initialize_valley_economy(kernel_b)

        mira_a = kernel_a.entity_registry.list_entities()[0].entity_id
        mira_b = kernel_b.entity_registry.list_entities()[0].entity_id

        prop_a = craft_recipe(kernel_a, mira_a, "wheat_to_flour")
        prop_b = craft_recipe(kernel_b, mira_b, "wheat_to_flour")

        tick_id_a = TickId.new(kernel_a.world_id, kernel_a.current_tick_number)
        tick_id_b = TickId.new(kernel_b.world_id, kernel_b.current_tick_number)
        rev_a = kernel_a.current_revision.revision_id if kernel_a.current_revision else None
        rev_b = kernel_b.current_revision.revision_id if kernel_b.current_revision else None

        ctx_a = TickContext(world_id=kernel_a.world_id, tick_id=tick_id_a, state_revision=rev_a, parent_revision=rev_a, timestamp=datetime.now(timezone.utc), correlation_id="replay_econ")
        ctx_b = TickContext(world_id=kernel_b.world_id, tick_id=tick_id_b, state_revision=rev_b, parent_revision=rev_b, timestamp=datetime.now(timezone.utc), correlation_id="replay_econ")

        kernel_a.commit_state(ctx_a, [prop_a])
        kernel_b.commit_state(ctx_b, [prop_b])

        self.assertEqual(kernel_a.current_state, kernel_b.current_state)


if __name__ == "__main__":
    unittest.main()
