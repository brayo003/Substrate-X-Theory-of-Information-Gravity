from __future__ import annotations

import unittest
from datetime import datetime, timezone

from sim_world import KernelConfig, WorldKernel
from sim_world.core.contracts import TickContext, TransitionProposal
from sim_world.core.ids import TickId
from sim_world.domains import register_all
from sim_world.domains.agriculture import (
    CROP_TYPES,
    GROWTH_STAGES,
    CropFailed,
    CropField,
    CropGrowthAdvanced,
    CropHarvested,
    CropPlanted,
    CropWatered,
    FoodProduced,
    SeedsConsumed,
    advance_field_growth,
    calculate_harvest_yield,
    generate_agriculture_goals,
    harvest_crop,
    initialize_valley_agriculture,
    plant_crop,
    validate_harvest,
    validate_planting,
    validate_watering,
    water_crop,
)
from sim_world.domains.population import initialize_valley_population
from sim_world.domains.resources import initialize_valley_resources
from sim_world.domains.terrain import initialize_valley_terrain
from sim_world.entities.components import InventoryComponent, ResourceDescriptor


class Loop4AgricultureTests(unittest.TestCase):
    def setUp(self) -> None:
        self.config = KernelConfig(
            world_name="valley_world_agriculture",
            seed="agriculture-seed-001",
            initial_state={"mode": "valley_agriculture_simulation"},
        )
        self.kernel = WorldKernel(self.config)
        register_all(self.kernel.simulation_engine)
        self.terrain_entities = initialize_valley_terrain(self.kernel)
        self.villager_entities = initialize_valley_population(self.kernel)
        self.building_entities = initialize_valley_resources(self.kernel)
        self.crop_fields = initialize_valley_agriculture(self.kernel)

    def _create_tick_context(self, correlation_id: str = "test_agri_correlation") -> TickContext:
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

    def test_field_creation_and_models(self) -> None:
        self.assertEqual(CROP_TYPES, ("Wheat", "Potatoes", "Vegetables"))
        self.assertEqual(
            GROWTH_STAGES,
            ("Seed", "Sprout", "Growing", "Mature", "Harvestable", "Dead"),
        )
        field = CropField(
            field_id="field_100",
            crop_type="Wheat",
            growth_stage="Seed",
            soil_quality=0.9,
            soil_moisture=0.8,
            fertility=0.95,
            weed_level=0.1,
            occupied=True,
        )
        self.assertEqual(field.field_id, "field_100")
        self.assertEqual(field.crop_type, "Wheat")
        self.assertEqual(field.growth_stage, "Seed")
        self.assertEqual(field.soil_quality, 0.9)
        self.assertEqual(field.soil_moisture, 0.8)
        self.assertEqual(field.fertility, 0.95)
        self.assertEqual(field.weed_level, 0.1)
        self.assertTrue(field.occupied)

        as_dict = field.to_dict()
        reconstructed = CropField.from_dict(as_dict)
        self.assertEqual(field, reconstructed)

    def test_planting_and_seed_consumption(self) -> None:
        mira = self.villager_entities["Mira"]
        mira_id = mira.entity_id

        mira.attach_component(
            InventoryComponent(
                items=(
                    ResourceDescriptor("seeds", 10.0, {}),
                    ResourceDescriptor("water", 10.0, {}),
                ),
                capacity=100.0,
            ),
            tick=0,
        )
        self.kernel._sync_entity_state()

        prop = plant_crop(self.kernel, mira_id, "field_1", crop_type="Wheat", seed_quantity=1.0)
        self.assertEqual(prop.subject, "PlantCrop")
        self.kernel.commit_state(self._create_tick_context("plant"), [prop])

        state = self.kernel.current_state
        agri_fields = state["agriculture"]["fields"]
        self.assertTrue(agri_fields["field_1"]["occupied"])
        self.assertEqual(agri_fields["field_1"]["crop_type"], "Wheat")
        self.assertEqual(agri_fields["field_1"]["growth_stage"], "Seed")

        mira_inv = state["entities"][str(mira_id.value)]["components"]["InventoryComponent"]["items"]
        mira_seeds = sum(i["quantity"] for i in mira_inv if i["identifier"] == "seeds")
        self.assertEqual(mira_seeds, 9.0)

    def test_watering_crop(self) -> None:
        mira = self.villager_entities["Mira"]
        mira_id = mira.entity_id

        mira.attach_component(
            InventoryComponent(items=(ResourceDescriptor("water", 5.0, {}),), capacity=100.0),
            tick=0,
        )
        self.kernel._sync_entity_state()

        prop = water_crop(self.kernel, mira_id, "field_1", water_quantity=1.0)
        self.assertEqual(prop.subject, "IncreaseMoisture")
        self.kernel.commit_state(self._create_tick_context("water"), [prop])

        state = self.kernel.current_state
        agri_fields = state["agriculture"]["fields"]
        self.assertGreater(agri_fields["field_1"]["soil_moisture"], 0.6)

    def test_growth_progression(self) -> None:
        field = CropField(field_id="f1", crop_type="Wheat", growth_stage="Seed", occupied=True, soil_moisture=0.8)
        stages = ["Seed"]
        current = field

        for t in range(1, 6):
            current, events = advance_field_growth(current, weather="rain", temperature=20.0, tick=t)
            stages.append(current.growth_stage)

        self.assertIn("Sprout", stages)
        self.assertIn("Growing", stages)
        self.assertIn("Mature", stages)
        self.assertIn("Harvestable", stages)

    def test_weather_effects(self) -> None:
        field = CropField(field_id="f_w", crop_type="Wheat", growth_stage="Seed", occupied=True, soil_moisture=0.5)

        rain_field, _ = advance_field_growth(field, weather="rain", temperature=20.0, tick=1)
        self.assertGreater(rain_field.soil_moisture, 0.5)

        drought_field, _ = advance_field_growth(field, weather="drought", temperature=20.0, tick=1)
        self.assertLess(drought_field.soil_moisture, 0.5)

        cold_field, _ = advance_field_growth(field, weather="cold", temperature=-5.0, tick=1)
        self.assertEqual(cold_field.growth_stage, "Seed")

        storm_field, events = advance_field_growth(field, weather="storm", temperature=20.0, tick=1)
        self.assertGreater(storm_field.weed_level, 0.0)

    def test_harvesting_and_food_production(self) -> None:
        mira = self.villager_entities["Mira"]
        mira_id = mira.entity_id

        agri_state = dict(self.kernel.current_state.get("agriculture", {}))
        fields = dict(agri_state.get("fields", {}))
        fields["field_1"] = CropField(
            field_id="field_1", crop_type="Wheat", growth_stage="Harvestable", occupied=True, soil_quality=1.0, fertility=1.0
        ).to_dict()
        agri_state["fields"] = fields

        prop_setup = TransitionProposal(
            world_id=self.kernel.world_id,
            tick_id=None,
            state_revision=None,
            correlation_id="setup_harvestable",
            subject="SetupField",
            patch={"agriculture": agri_state},
        )
        self.kernel.commit_state(self._create_tick_context("setup"), [prop_setup])

        prop_harvest = harvest_crop(self.kernel, mira_id, "field_1")
        self.assertEqual(prop_harvest.subject, "HarvestCrop")
        self.kernel.commit_state(self._create_tick_context("harvest"), [prop_harvest])

        state = self.kernel.current_state
        self.assertFalse(state["agriculture"]["fields"]["field_1"]["occupied"])

        mira_inv = state["entities"][str(mira_id.value)]["components"]["InventoryComponent"]["items"]
        mira_food = sum(i["quantity"] for i in mira_inv if i["identifier"] == "food")
        self.assertGreater(mira_food, 0.0)

    def test_planner_goal_generation(self) -> None:
        goals = generate_agriculture_goals(self.kernel)
        self.assertTrue(len(goals) > 0)
        goal_kinds = [g.kind for g in goals]
        self.assertIn("PlantField", goal_kinds)

    def test_proposal_generation(self) -> None:
        tick_ctx = self._create_tick_context("adv_tick")
        sim_context = self.kernel._simulation_context(tick_ctx) if hasattr(self.kernel, "_simulation_context") else None
        if sim_context is None:
            from sim_world.simulation.simulation_context import SimulationContext
            sim_context = SimulationContext(
                world_id=self.kernel.world_id,
                tick_context=tick_ctx,
                tick_number=self.kernel.current_tick_number,
                world_state=self.kernel.current_state,
                committed_revision=self.kernel.current_revision.revision_id if self.kernel.current_revision else None,
            )
        res = self.kernel.simulation_engine.advance(context=sim_context)
        agri_props = [p for p in res.proposals if p.subject == "domain.agriculture"]
        self.assertEqual(len(agri_props), 1)

    def test_rules_enforcement(self) -> None:
        empty_field = CropField(field_id="f_empty", occupied=False)
        valid, msg = validate_harvest(empty_field)
        self.assertFalse(valid)

        dead_field = CropField(field_id="f_dead", occupied=True, growth_stage="Dead")
        valid_h, msg_h = validate_harvest(dead_field)
        self.assertFalse(valid_h)
        self.assertEqual(calculate_harvest_yield(dead_field), 0.0)

        occupied_field = CropField(field_id="f_occ", occupied=True, growth_stage="Sprout")
        valid_p, msg_p = validate_planting(occupied_field, seed_quantity=1.0)
        self.assertFalse(valid_p)

    def test_deterministic_replay(self) -> None:
        kernel_a = WorldKernel(self.config)
        register_all(kernel_a.simulation_engine)
        initialize_valley_terrain(kernel_a)
        initialize_valley_population(kernel_a)
        initialize_valley_resources(kernel_a)
        initialize_valley_agriculture(kernel_a)

        kernel_b = WorldKernel(self.config)
        register_all(kernel_b.simulation_engine)
        initialize_valley_terrain(kernel_b)
        initialize_valley_population(kernel_b)
        initialize_valley_resources(kernel_b)
        initialize_valley_agriculture(kernel_b)

        mira_a = kernel_a.entity_registry.list_entities()[0].entity_id
        mira_b = kernel_b.entity_registry.list_entities()[0].entity_id

        prop_a = plant_crop(kernel_a, mira_a, "field_1", "Wheat")
        prop_b = plant_crop(kernel_b, mira_b, "field_1", "Wheat")

        tick_id_a = TickId.new(kernel_a.world_id, kernel_a.current_tick_number)
        tick_id_b = TickId.new(kernel_b.world_id, kernel_b.current_tick_number)

        rev_a = kernel_a.current_revision.revision_id if kernel_a.current_revision else None
        rev_b = kernel_b.current_revision.revision_id if kernel_b.current_revision else None

        ctx_a = TickContext(world_id=kernel_a.world_id, tick_id=tick_id_a, state_revision=rev_a, parent_revision=rev_a, timestamp=datetime.now(timezone.utc), correlation_id="replay")
        ctx_b = TickContext(world_id=kernel_b.world_id, tick_id=tick_id_b, state_revision=rev_b, parent_revision=rev_b, timestamp=datetime.now(timezone.utc), correlation_id="replay")

        kernel_a.commit_state(ctx_a, [prop_a])
        kernel_b.commit_state(ctx_b, [prop_b])

        state_a = kernel_a.current_state
        state_b = kernel_b.current_state

        self.assertEqual(state_a, state_b)


if __name__ == "__main__":
    unittest.main()
