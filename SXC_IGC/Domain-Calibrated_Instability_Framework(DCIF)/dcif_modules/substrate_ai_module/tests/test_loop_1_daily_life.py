from __future__ import annotations

import unittest
from sim_world import KernelConfig, WorldKernel
from sim_world.domains import register_all
from sim_world.domains.population import (
    initialize_valley_population,
    run_daily_life_step,
)
from sim_world.domains.terrain import initialize_valley_terrain


def get_room(kernel: WorldKernel, entity_id: Any) -> str:
    key = str(entity_id.value)
    entities = kernel.current_state.get("entities", {})
    entity_data = entities.get(key, {})
    transform = entity_data.get("components", {}).get("TransformComponent", {})
    return transform.get("room")


class Loop1DailyLifeTests(unittest.TestCase):
    def setUp(self) -> None:
        self.config = KernelConfig(
            world_name="valley_world",
            seed="valley-seed-001",
            initial_state={"mode": "valley_simulation"},
        )
        self.kernel = WorldKernel(self.config)
        register_all(self.kernel.simulation_engine)
        self.terrain_entities = initialize_valley_terrain(self.kernel)
        self.villager_entities = initialize_valley_population(self.kernel)

    def test_valley_world_initialization(self) -> None:
        entities = self.kernel.entity_registry.list_entities()
        villagers = [e for e in entities if e.type == "human"]
        buildings = [e for e in entities if e.type == "building"]
        locations = [e for e in entities if e.type == "location"]

        self.assertEqual(len(villagers), 10)
        self.assertEqual(len(buildings), 10)
        self.assertEqual(len(locations), 6)

        villager_names = {v.display_name for v in villagers}
        expected_villagers = {
            "Mira",
            "Joren",
            "Lina",
            "Tomas",
            "Edda",
            "Pell",
            "Hara",
            "Niko",
            "Sera",
            "Oren",
        }
        self.assertEqual(villager_names, expected_villagers)

        building_names = {b.display_name for b in buildings}
        expected_buildings = {
            "House 1",
            "House 2",
            "House 3",
            "House 4",
            "Farm",
            "Barn",
            "Well",
            "Blacksmith",
            "Storage",
            "Tavern",
        }
        self.assertEqual(building_names, expected_buildings)

    def test_loop_1_daily_life_causal_cycle(self) -> None:
        mira = self.villager_entities["Mira"]  # Farmer: home house_1, workplace farm

        # Ticks 0 to 5 (Night): sleeping at home
        for _ in range(6):
            run_daily_life_step(self.kernel)
        self.assertEqual(get_room(self.kernel, mira.entity_id), "house_1")

        # Tick 6 (Morning): Goal generated at tick 6, scheduled for tick 7
        run_daily_life_step(self.kernel)  # tick 6 -> 7
        run_daily_life_step(self.kernel)  # tick 7 executes Walk action to farm
        self.assertEqual(get_room(self.kernel, mira.entity_id), "farm")

        # Workday at workplace
        for _ in range(10):
            run_daily_life_step(self.kernel)
        self.assertEqual(get_room(self.kernel, mira.entity_id), "farm")

        # Evening: Goal generated at tick 18, scheduled for tick 19
        run_daily_life_step(self.kernel)  # tick 18 -> 19
        run_daily_life_step(self.kernel)  # tick 19 executes Walk home action
        self.assertEqual(get_room(self.kernel, mira.entity_id), "house_1")

        # Night: back home
        for _ in range(4):
            run_daily_life_step(self.kernel)
        self.assertEqual(get_room(self.kernel, mira.entity_id), "house_1")

        # Day 2 repeats deterministically
        for _ in range(6):
            run_daily_life_step(self.kernel)

        run_daily_life_step(self.kernel)
        run_daily_life_step(self.kernel)
        self.assertEqual(get_room(self.kernel, mira.entity_id), "farm")

        # Verify history of state revisions was recorded
        history = self.kernel.storage.list_history()
        self.assertGreaterEqual(len(history), 24)

    def test_loop_1_determinism_and_replay(self) -> None:
        kernel_a = WorldKernel(self.config)
        register_all(kernel_a.simulation_engine)
        initialize_valley_terrain(kernel_a)
        initialize_valley_population(kernel_a)

        kernel_b = WorldKernel(self.config)
        register_all(kernel_b.simulation_engine)
        initialize_valley_terrain(kernel_b)
        initialize_valley_population(kernel_b)

        for _ in range(24):
            run_daily_life_step(kernel_a)
            run_daily_life_step(kernel_b)

        self.assertEqual(kernel_a.current_state, kernel_b.current_state)
        history_a = tuple(r.revision_id for r in kernel_a.storage.list_history())
        history_b = tuple(r.revision_id for r in kernel_b.storage.list_history())
        self.assertEqual(history_a, history_b)


if __name__ == "__main__":
    unittest.main()

