from __future__ import annotations

from datetime import datetime, timezone
import unittest

from sim_world import (
    ActionRequest,
    InventoryComponent,
    KernelConfig,
    NeedsComponent,
    HealthComponent,
    SimulationContext,
    TickContext,
    TickId,
    TransformComponent,
    TransitionProposal,
    ResourceDescriptor,
    WorldKernel,
)


class SimulationEngineTests(unittest.TestCase):
    def _build_kernel(self, *, door_open: bool = False) -> tuple[WorldKernel, object, object, object]:
        kernel = WorldKernel(KernelConfig(world_name="sim_world", seed="sim-seed", initial_state={}))
        registry = kernel.entity_registry
        alice = registry.create_entity(entity_type="human", display_name="Alice", created_tick=0, created_revision=None)
        door = registry.create_entity(
            entity_type="door",
            display_name="Kitchen Door",
            created_tick=0,
            created_revision=None,
            metadata={"connects": ("Kitchen", "Hall"), "open": door_open},
        )
        bottle = registry.create_entity(entity_type="object", display_name="Bottle", created_tick=0, created_revision=None)

        alice.attach_component(TransformComponent(room="Kitchen"), tick=0)
        alice.attach_component(
            InventoryComponent(items=(ResourceDescriptor("food", 2, {"fresh": True}), ResourceDescriptor("water", 1, {"cold": True}))),
            tick=0,
        )
        alice.attach_component(NeedsComponent(needs={"hunger": 0.8, "thirst": 0.7, "energy": 0.4}), tick=0)
        alice.attach_component(HealthComponent(current=10, maximum=10, status="healthy"), tick=0)
        door.attach_component(TransformComponent(room="Kitchen"), tick=0)
        bottle.attach_component(TransformComponent(room="Kitchen"), tick=0)
        return kernel, alice, door, bottle

    def _schedule_sequence(self, kernel: WorldKernel, alice, door, bottle) -> None:
        scheduler = kernel.simulation_engine.scheduler
        scheduler.schedule_future_tick(
            ActionRequest(actor_id=alice.entity_id, action="Open", target_id=door.entity_id),
            execute_tick=1,
            tick_number=0,
        )
        scheduler.schedule_future_tick(
            ActionRequest(actor_id=alice.entity_id, action="Close", target_id=door.entity_id),
            execute_tick=2,
            tick_number=0,
        )
        scheduler.schedule_future_tick(
            ActionRequest(actor_id=alice.entity_id, action="Open", target_id=door.entity_id),
            execute_tick=3,
            tick_number=0,
        )
        scheduler.schedule_future_tick(
            ActionRequest(actor_id=alice.entity_id, action="PickUp", target_id=bottle.entity_id),
            execute_tick=4,
            tick_number=0,
        )
        scheduler.schedule_future_tick(
            ActionRequest(actor_id=alice.entity_id, action="Walk", destination_room="Hall"),
            execute_tick=5,
            tick_number=0,
        )
        scheduler.schedule_future_tick(
            ActionRequest(actor_id=alice.entity_id, action="Drop", item_id=bottle.entity_id),
            execute_tick=6,
            tick_number=0,
        )
        scheduler.schedule_future_tick(
            ActionRequest(actor_id=alice.entity_id, action="Eat", quantity=1),
            execute_tick=7,
            tick_number=0,
        )
        scheduler.schedule_future_tick(
            ActionRequest(actor_id=alice.entity_id, action="Drink", quantity=1),
            execute_tick=8,
            tick_number=0,
        )

    def test_movement_pickup_drop_open_close_and_resource_consumption(self) -> None:
        kernel, alice, door, bottle = self._build_kernel()
        self._schedule_sequence(kernel, alice, door, bottle)

        door_id = str(door.entity_id.value)
        alice_id = str(alice.entity_id.value)
        bottle_id = str(bottle.entity_id.value)

        state = kernel.advance_tick().state
        self.assertTrue(state["entities"][door_id]["metadata"]["open"])

        state = kernel.advance_tick().state
        self.assertFalse(state["entities"][door_id]["metadata"]["open"])

        state = kernel.advance_tick().state
        self.assertTrue(state["entities"][door_id]["metadata"]["open"])

        state = kernel.advance_tick().state
        self.assertEqual(state["entities"][bottle_id]["metadata"]["held_by"], alice_id)
        self.assertIsNone(state["entities"][bottle_id]["components"]["TransformComponent"]["room"])
        self.assertIn(bottle_id, tuple(state["entities"][alice_id]["metadata"]["holding"]))

        state = kernel.advance_tick().state
        self.assertEqual(state["entities"][alice_id]["components"]["TransformComponent"]["room"], "Hall")
        self.assertEqual(state["entities"][bottle_id]["metadata"]["held_by"], alice_id)

        state = kernel.advance_tick().state
        self.assertIsNone(state["entities"][bottle_id]["metadata"].get("held_by"))
        self.assertEqual(state["entities"][bottle_id]["components"]["TransformComponent"]["room"], "Hall")

        state = kernel.advance_tick().state
        inventory = state["entities"][alice_id]["components"]["InventoryComponent"]["items"]
        self.assertAlmostEqual(inventory[0]["quantity"], 1.0)
        self.assertAlmostEqual(state["entities"][alice_id]["components"]["NeedsComponent"]["needs"]["hunger"], 0.45)

        state = kernel.advance_tick().state
        inventory = state["entities"][alice_id]["components"]["InventoryComponent"]["items"]
        self.assertEqual(len(inventory), 1)
        self.assertAlmostEqual(inventory[0]["quantity"], 1.0)
        self.assertAlmostEqual(state["entities"][alice_id]["components"]["NeedsComponent"]["needs"]["thirst"], 0.35)

    def test_proposal_generation_is_deterministic_and_read_only(self) -> None:
        kernel, alice, door, _ = self._build_kernel(door_open=True)
        tick_context = TickContext(
            world_id=kernel.world_id,
            tick_id=TickId.new(kernel.world_id, 1),
            state_revision=None,
            parent_revision=None,
            timestamp=datetime.now(timezone.utc),
            correlation_id="proposal-generation",
            metadata={},
        )
        simulation_context = SimulationContext(
            world_id=kernel.world_id,
            tick_context=tick_context,
            tick_number=1,
            world_state=kernel.current_state,
            committed_revision=None,
            scheduled_actions=(
                ActionRequest(actor_id=alice.entity_id, action="Walk", destination_room="Hall"),
            ),
            metadata={},
        )
        result = kernel.simulation_engine.advance(simulation_context)
        self.assertEqual(len(result.proposals), 1)
        proposal = result.proposals[0]
        self.assertEqual(proposal.subject, "WalkAction")
        self.assertEqual(
            proposal.patch["entities"][str(alice.entity_id.value)]["components"]["TransformComponent"]["room"],
            "Hall",
        )
        self.assertEqual(kernel.current_state["entities"][str(alice.entity_id.value)]["components"]["TransformComponent"]["room"], "Kitchen")

    def test_conflict_rejection_keeps_one_write_per_entity(self) -> None:
        kernel, alice, _, _ = self._build_kernel(door_open=True)
        scheduler = kernel.simulation_engine.scheduler
        scheduler.schedule_future_tick(
            ActionRequest(actor_id=alice.entity_id, action="Walk", destination_room="Hall", correlation_id="a"),
            execute_tick=1,
            tick_number=0,
        )
        scheduler.schedule_future_tick(
            ActionRequest(actor_id=alice.entity_id, action="Walk", destination_room="Hall", correlation_id="b"),
            execute_tick=1,
            tick_number=0,
        )

        revision = kernel.advance_tick()
        self.assertEqual(revision.state["entities"][str(alice.entity_id.value)]["components"]["TransformComponent"]["room"], "Hall")
        self.assertEqual(len(kernel.simulation_engine.last_diagnostics.conflicts), 1)
        self.assertEqual(len(kernel.simulation_engine.last_diagnostics.rejected_actions), 0)

    def test_deterministic_replay_matches_across_kernels(self) -> None:
        kernel_a, alice_a, door_a, bottle_a = self._build_kernel()
        kernel_b, alice_b, door_b, bottle_b = self._build_kernel()

        self._schedule_sequence(kernel_a, alice_a, door_a, bottle_a)
        self._schedule_sequence(kernel_b, alice_b, door_b, bottle_b)

        for _ in range(8):
            kernel_a.advance_tick()
            kernel_b.advance_tick()

        self.assertEqual(kernel_a.current_state, kernel_b.current_state)
        self.assertEqual(
            tuple(revision.revision_id for revision in kernel_a.storage.list_history()),
            tuple(revision.revision_id for revision in kernel_b.storage.list_history()),
        )


if __name__ == "__main__":
    unittest.main()
