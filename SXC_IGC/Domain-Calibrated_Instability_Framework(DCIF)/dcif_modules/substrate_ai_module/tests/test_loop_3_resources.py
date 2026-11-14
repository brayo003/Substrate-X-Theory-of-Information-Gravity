from __future__ import annotations

import unittest
from datetime import datetime, timezone
from typing import Any

from sim_world import KernelConfig, WorldKernel
from sim_world.core.contracts import TickContext, TransitionProposal
from sim_world.core.ids import EntityId, TickId
from sim_world.domains import register_all
from sim_world.domains.population import initialize_valley_population
from sim_world.domains.resources import (
    CORE_RESOURCES,
    ResourceEvent,
    ResourceItem,
    calculate_total_quantity,
    consume_resource,
    consume_resource_item,
    deposit_resource,
    deposit_resource_items,
    initialize_valley_resources,
    pickup_resource,
    store_resource,
    transfer_resource,
    transfer_resource_items,
    validate_inventory_capacity,
    withdraw_resource,
    withdraw_resource_items,
)
from sim_world.domains.terrain import initialize_valley_terrain
from sim_world.entities.components import InventoryComponent, ResourceDescriptor
from sim_world.simulation.simulation_context import ActionRequest


class Loop3ResourcesTests(unittest.TestCase):
    def setUp(self) -> None:
        self.config = KernelConfig(
            world_name="valley_world_resources",
            seed="resources-seed-001",
            initial_state={"mode": "valley_resources_simulation"},
        )
        self.kernel = WorldKernel(self.config)
        register_all(self.kernel.simulation_engine)
        self.terrain_entities = initialize_valley_terrain(self.kernel)
        self.villager_entities = initialize_valley_population(self.kernel)
        self.building_entities = initialize_valley_resources(self.kernel)

    def _create_tick_context(self, correlation_id: str = "test_correlation") -> TickContext:
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

    def test_core_resource_types_and_models(self) -> None:
        self.assertEqual(
            CORE_RESOURCES,
            ("food", "water", "wood", "stone", "iron", "fuel", "tools", "seeds"),
        )
        item = ResourceItem.create(
            resource_type="food",
            quantity=10.0,
            owner_id="villager_1",
            location_id="house_1",
            container_id="inv_1",
            quality=0.9,
            maximum_capacity=100.0,
        )
        self.assertEqual(item.resource_type, "food")
        self.assertEqual(item.quantity, 10.0)
        self.assertEqual(item.owner, "villager_1")
        self.assertEqual(item.location, "house_1")
        self.assertEqual(item.container, "inv_1")
        self.assertEqual(item.quality, 0.9)
        self.assertEqual(item.maximum_capacity, 100.0)

    def test_resource_initialization_and_inventory_ownership(self) -> None:
        farm = self.building_entities["Farm"]
        storage = self.building_entities["Storage"]
        well = self.building_entities["Well"]

        state = self.kernel.current_state
        entities = state.get("entities", {})

        farm_inv = entities.get(str(farm.entity_id.value), {}).get("components", {}).get("InventoryComponent", {})
        storage_inv = entities.get(str(storage.entity_id.value), {}).get("components", {}).get("InventoryComponent", {})
        well_inv = entities.get(str(well.entity_id.value), {}).get("components", {}).get("InventoryComponent", {})

        self.assertIsNotNone(farm_inv)
        self.assertIsNotNone(storage_inv)
        self.assertIsNotNone(well_inv)

        farm_items = {i["identifier"]: i["quantity"] for i in farm_inv.get("items", ())}
        self.assertIn("seeds", farm_items)
        self.assertIn("food", farm_items)

        storage_items = {i["identifier"]: i["quantity"] for i in storage_inv.get("items", ())}
        self.assertIn("food", storage_items)
        self.assertIn("wood", storage_items)
        self.assertIn("tools", storage_items)

        well_items = {i["identifier"]: i["quantity"] for i in well_inv.get("items", ())}
        self.assertIn("water", well_items)

    def test_pickup_and_drop_resources(self) -> None:
        mira = self.villager_entities["Mira"]
        mira_id = mira.entity_id
        storage = self.building_entities["Storage"]
        storage_id = storage.entity_id

        # Attach initial inventory to Mira
        mira.attach_component(
            InventoryComponent(items=(ResourceDescriptor("food", 5.0, {}),), capacity=50.0),
            tick=0,
        )
        self.kernel._sync_entity_state()

        # Execute Deposit resource action proposal
        prop = deposit_resource(self.kernel, mira_id, storage_id, "food", 2.0)
        self.assertEqual(prop.subject, "DepositResource")
        self.assertIn("entities", prop.patch)

        self.kernel.commit_state(self._create_tick_context("deposit"), [prop])

        state = self.kernel.current_state
        mira_inv = state["entities"][str(mira_id.value)]["components"]["InventoryComponent"]["items"]
        mira_food = sum(i["quantity"] for i in mira_inv if i["identifier"] == "food")
        self.assertEqual(mira_food, 3.0)

        # Execute Withdraw resource action proposal
        w_prop = withdraw_resource(self.kernel, storage_id, mira_id, "food", 1.0)
        self.kernel.commit_state(self._create_tick_context("withdraw"), [w_prop])

        state_2 = self.kernel.current_state
        mira_inv_2 = state_2["entities"][str(mira_id.value)]["components"]["InventoryComponent"]["items"]
        mira_food_2 = sum(i["quantity"] for i in mira_inv_2 if i["identifier"] == "food")
        self.assertEqual(mira_food_2, 4.0)

    def test_transfer_deposit_withdraw_resource_proposals(self) -> None:
        storage = self.building_entities["Storage"]
        barn = self.building_entities["Barn"]

        storage_id = storage.entity_id
        barn_id = barn.entity_id

        initial_storage_wood = sum(
            i["quantity"]
            for i in self.kernel.current_state["entities"][str(storage_id.value)]["components"]["InventoryComponent"]["items"]
            if i["identifier"] == "wood"
        )

        # Generate proposal only (no direct mutation)
        prop = transfer_resource(self.kernel, storage_id, barn_id, "wood", 10.0)
        self.assertEqual(prop.subject, "TransferResource")
        self.assertIn("entities", prop.patch)

        # Commit via kernel
        rev = self.kernel.commit_state(self._create_tick_context("transfer"), [prop])
        self.assertIsNotNone(rev)

        # Verify exact conservation after transfer
        new_storage_wood = sum(
            i["quantity"]
            for i in self.kernel.current_state["entities"][str(storage_id.value)]["components"]["InventoryComponent"]["items"]
            if i["identifier"] == "wood"
        )
        new_barn_wood = sum(
            i["quantity"]
            for i in self.kernel.current_state["entities"][str(barn_id.value)]["components"]["InventoryComponent"]["items"]
            if i["identifier"] == "wood"
        )

        self.assertEqual(new_storage_wood, initial_storage_wood - 10.0)
        self.assertEqual(new_barn_wood, 10.0)

    def test_capacity_enforcement_and_conservation(self) -> None:
        src = [{"identifier": "wood", "quantity": 100.0}]
        dst = [{"identifier": "wood", "quantity": 490.0}]

        # Dest capacity 500.0, available space 10.0
        new_src, new_dst, transfer_qty, events = transfer_resource_items(
            source_items=src,
            dest_items=dst,
            resource_type="wood",
            quantity=50.0,  # Request 50, but only 10 fits
            source_id="src_1",
            dest_id="dst_1",
            dest_capacity=500.0,
        )

        self.assertEqual(transfer_qty, 10.0)
        self.assertEqual(calculate_total_quantity(new_dst), 500.0)
        self.assertEqual(calculate_total_quantity(new_src), 90.0)
        # Total conservation: 100 + 490 = 590 before, 90 + 500 = 590 after
        self.assertEqual(calculate_total_quantity(new_src) + calculate_total_quantity(new_dst), 590.0)

    def test_resource_consumption_and_exhaustion(self) -> None:
        items = [{"identifier": "food", "quantity": 5.0}]
        new_items, consumed, events = consume_resource_item(
            items=items,
            resource_type="food",
            quantity=5.0,
            entity_id="house_1",
        )

        self.assertEqual(consumed, 5.0)
        self.assertEqual(calculate_total_quantity(new_items), 0.0)

        event_types = [e.event_type for e in events]
        self.assertIn("ResourceConsumed", event_types)
        self.assertIn("ResourceExhausted", event_types)

    def test_planner_resource_lookup_and_shortage_handling(self) -> None:
        mira = self.villager_entities["Mira"]
        mira_id = mira.entity_id

        # Set high hunger
        mira_key = str(mira_id.value)
        patch = {
            "entities": {
                mira_key: {
                    "components": {
                        "NeedsComponent": {
                            "needs": {"hunger": 0.9, "thirst": 0.1, "energy": 0.8},
                            "component_type": "NeedsComponent",
                        }
                    }
                }
            }
        }
        tick_ctx = self._create_tick_context("set_hunger")
        prop = TransitionProposal(
            world_id=self.kernel.world_id,
            tick_id=tick_ctx.tick_id,
            state_revision=self.kernel.current_revision.revision_id if self.kernel.current_revision else None,
            correlation_id="set_hunger",
            subject="SetHunger",
            patch=patch,
        )
        self.kernel.commit_state(tick_ctx, [prop])

        # Plan with existing food sources
        plans = self.kernel.plan()
        self.assertTrue(len(plans) > 0)
        first_plan = plans[0]
        self.assertTrue(len(first_plan.steps) > 0)

    def test_replay_determinism(self) -> None:
        kernel_a = WorldKernel(self.config)
        register_all(kernel_a.simulation_engine)
        initialize_valley_terrain(kernel_a)
        initialize_valley_population(kernel_a)
        initialize_valley_resources(kernel_a)

        kernel_b = WorldKernel(self.config)
        register_all(kernel_b.simulation_engine)
        initialize_valley_terrain(kernel_b)
        initialize_valley_population(kernel_b)
        initialize_valley_resources(kernel_b)

        for _ in range(10):
            kernel_a.advance_tick()
            kernel_b.advance_tick()

        state_a = kernel_a.current_state
        state_b = kernel_b.current_state

        self.assertEqual(state_a, state_b)


if __name__ == "__main__":
    unittest.main()
