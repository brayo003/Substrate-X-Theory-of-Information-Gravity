from __future__ import annotations

import unittest
from sim_world import ActionRequest, KernelConfig, NeedsComponent, WorldKernel
from sim_world.domains import register_all
from sim_world.domains.needs import (
    evaluate_villager_needs,
    generate_needs_driven_goals,
    run_needs_driven_step,
)
from sim_world.domains.population import initialize_valley_population
from sim_world.domains.terrain import initialize_valley_terrain


def get_needs(kernel: WorldKernel, entity_id: str) -> dict[str, float]:
    entities = kernel.current_state.get("entities", {})
    entity_data = entities.get(entity_id, {})
    components = entity_data.get("components", {})
    needs_comp = components.get("NeedsComponent", {})
    return dict(needs_comp.get("needs", {}))


class Loop2NeedsTests(unittest.TestCase):
    def setUp(self) -> None:
        self.config = KernelConfig(
            world_name="valley_world_needs",
            seed="needs-seed-001",
            initial_state={"mode": "needs_simulation"},
        )
        self.kernel = WorldKernel(self.config)
        register_all(self.kernel.simulation_engine)
        self.terrain_entities = initialize_valley_terrain(self.kernel)
        self.villager_entities = initialize_valley_population(self.kernel)

    def test_need_decay_and_evolution(self) -> None:
        mira = self.villager_entities["Mira"]
        mira_id = str(mira.entity_id.value)

        initial_needs = get_needs(self.kernel, mira_id)
        self.assertIn("hunger", initial_needs)
        self.assertIn("thirst", initial_needs)
        self.assertIn("energy", initial_needs)

        # Advance 5 ticks without eating/drinking
        for _ in range(5):
            self.kernel.advance_tick()

        updated_needs = get_needs(self.kernel, mira_id)
        self.assertGreater(updated_needs["hunger"], initial_needs["hunger"])
        self.assertGreater(updated_needs["thirst"], initial_needs["thirst"])
        self.assertLess(updated_needs["energy"], initial_needs["energy"])

    def test_need_recovery_and_action_effects(self) -> None:
        mira = self.villager_entities["Mira"]
        mira_id = str(mira.entity_id.value)

        # Set high hunger & thirst, low energy
        patch = {
            "entities": {
                mira_id: {
                    "components": {
                        "NeedsComponent": {
                            "needs": {"hunger": 0.8, "thirst": 0.8, "energy": 0.2, "warmth": 0.5, "comfort": 0.5, "social": 0.2},
                            "component_type": "NeedsComponent",
                        }
                    }
                }
            }
        }

        # Schedule Eat action
        scheduler = self.kernel.simulation_engine.scheduler
        # Attach food item to inventory first
        from sim_world.entities.components import InventoryComponent, ResourceDescriptor
        mira.attach_component(
            InventoryComponent(items=(ResourceDescriptor("food", 2, {}), ResourceDescriptor("water", 2, {}))),
            tick=0,
        )
        self.kernel._sync_entity_state()

        # Execute Eat
        scheduler.schedule_future_tick(ActionRequest(actor_id=mira.entity_id, action="Eat", quantity=1), execute_tick=1, tick_number=0)
        self.kernel.advance_tick()

        eaten_needs = get_needs(self.kernel, mira_id)
        self.assertLess(eaten_needs["hunger"], 0.8)

        # Execute Sleep
        scheduler.schedule_future_tick(ActionRequest(actor_id=mira.entity_id, action="Sleep"), execute_tick=2, tick_number=1)
        self.kernel.advance_tick()

        slept_needs = get_needs(self.kernel, mira_id)
        self.assertGreater(slept_needs["energy"], 0.2)

    def test_planner_generates_need_driven_goals(self) -> None:
        mira = self.villager_entities["Mira"]
        mira_id = str(mira.entity_id.value)

        # Set critical needs
        self.kernel.entity_registry.get_entity(mira.entity_id).attach_component(
            NeedsComponent(needs={"hunger": 0.85, "thirst": 0.85, "energy": 0.15, "social": 0.15, "warmth": 0.2}),
            tick=self.kernel.current_tick_number,
        )
        self.kernel._sync_entity_state()

        goals = generate_needs_driven_goals(self.kernel)
        self.assertGreaterEqual(len(goals), 4)

        kinds = {g.kind for g in goals if g.entity_id == mira.entity_id}
        self.assertIn("hunger", kinds)
        self.assertIn("thirst", kinds)
        self.assertIn("sleep", kinds)

        plans = self.kernel.plan(goals=goals)
        self.assertGreaterEqual(len(plans), 1)

    def test_critical_needs_interrupt_routine(self) -> None:
        mira = self.villager_entities["Mira"]
        mira_id = str(mira.entity_id.value)

        # High hunger during workday
        self.kernel.entity_registry.get_entity(mira.entity_id).attach_component(
            NeedsComponent(needs={"hunger": 0.9, "thirst": 0.2, "energy": 0.8}),
            tick=self.kernel.current_tick_number,
        )
        self.kernel._sync_entity_state()

        goals = generate_needs_driven_goals(self.kernel)
        eat_goal = [g for g in goals if g.kind == "hunger" and g.entity_id == mira.entity_id][0]

        self.assertEqual(eat_goal.priority, 100)  # Priority 100 overrides routine work priority 8

    def test_replay_determinism_and_proposal_generation(self) -> None:
        kernel_a = WorldKernel(self.config)
        register_all(kernel_a.simulation_engine)
        initialize_valley_terrain(kernel_a)
        initialize_valley_population(kernel_a)

        kernel_b = WorldKernel(self.config)
        register_all(kernel_b.simulation_engine)
        initialize_valley_terrain(kernel_b)
        initialize_valley_population(kernel_b)

        for _ in range(24):
            run_needs_driven_step(kernel_a)
            run_needs_driven_step(kernel_b)

        self.assertEqual(kernel_a.current_state, kernel_b.current_state)
        history_a = tuple(r.revision_id for r in kernel_a.storage.list_history())
        history_b = tuple(r.revision_id for r in kernel_b.storage.list_history())
        self.assertEqual(history_a, history_b)


if __name__ == "__main__":
    unittest.main()
