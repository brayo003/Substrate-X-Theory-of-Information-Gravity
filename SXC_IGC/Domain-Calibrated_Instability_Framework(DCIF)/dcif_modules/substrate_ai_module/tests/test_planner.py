from __future__ import annotations

import unittest

from sim_world import (
    Goal,
    InventoryComponent,
    KernelConfig,
    NeedsComponent,
    PlanProposal,
    PlanValidationResult,
    ResourceDescriptor,
    TransformComponent,
    WorldKernel,
)


class PlannerSubsystemTests(unittest.TestCase):
    def setUp(self) -> None:
        self.kernel = WorldKernel(
            KernelConfig(
                world_name="planner_world",
                seed="planner-seed",
                initial_state={"mode": "planner"},
            )
        )
        self.registry = self.kernel.entity_registry
        self.kitchen = self.registry.create_entity(
            entity_type="room",
            display_name="Kitchen",
            created_tick=0,
            created_revision=None,
        )
        self.hall = self.registry.create_entity(
            entity_type="room",
            display_name="Hall",
            created_tick=0,
            created_revision=None,
        )
        self.alice = self.registry.create_entity(
            entity_type="human",
            display_name="Alice",
            created_tick=0,
            created_revision=None,
        )
        self.bob = self.registry.create_entity(
            entity_type="human",
            display_name="Bob",
            created_tick=0,
            created_revision=None,
        )
        self.door = self.registry.create_entity(
            entity_type="door",
            display_name="Hall Door",
            created_tick=0,
            created_revision=None,
            metadata={"connects": ("Kitchen", "Hall"), "open": True},
        )
        self.food = self.registry.create_entity(
            entity_type="object",
            display_name="Food Plate",
            created_tick=0,
            created_revision=None,
        )
        self.bottle = self.registry.create_entity(
            entity_type="object",
            display_name="Green Bottle",
            created_tick=0,
            created_revision=None,
        )
        self.alice.attach_component(TransformComponent(room="Kitchen"), tick=0)
        self.alice.attach_component(
            InventoryComponent(items=(ResourceDescriptor("food", 2, {"fresh": True}), ResourceDescriptor("water", 1, {"cold": True}))),
            tick=0,
        )
        self.alice.attach_component(NeedsComponent(needs={"hunger": 0.9, "thirst": 0.8, "energy": 0.3}), tick=0)
        self.bob.attach_component(TransformComponent(room="Kitchen"), tick=0)
        self.door.attach_component(TransformComponent(room="Kitchen"), tick=0)
        self.food.attach_component(TransformComponent(room="Kitchen"), tick=0)
        self.bottle.attach_component(TransformComponent(room="Kitchen"), tick=0)
        self.kernel.world_memory.record_asset(
            canonical_name="Green bottle",
            descriptors={"color": "green", "size_ml": 600, "material": "glass"},
            serial_number="GB-600",
            manufacturer="SimWorks",
            creation_metadata={"origin": "lab"},
            provenance={"source": "catalog"},
            entity_id=self.bottle.entity_id,
            created_tick=0,
            created_revision=None,
        )
        self.bottle_asset = self.kernel.world_memory.asset_memory.find_by_entity(self.bottle.entity_id)
        assert self.bottle_asset is not None

    def _build_goal(self, subject: str, kind: str, *, target_state: dict[str, object] | None = None, priority: int = 0) -> Goal:
        return self.kernel.planner_engine.goal_manager.create_goal(
            subject=subject,
            kind=kind,
            entity_id=self.alice.entity_id,
            target_state={} if target_state is None else target_state,
            priority=priority,
            created_tick=self.kernel.current_tick_number,
            created_revision=self.kernel.current_revision.revision_id if self.kernel.current_revision else None,
        )

    def test_goal_creation_and_lifecycle(self) -> None:
        goal = self._build_goal("Eat lunch", "hunger", priority=3)
        manager = self.kernel.planner_engine.goal_manager

        self.assertEqual(goal.status, "pending")
        self.assertIsNotNone(manager.get_goal(goal.goal_id))

        active = manager.activate(goal.goal_id, tick=1)
        self.assertIsNotNone(active)
        assert active is not None
        self.assertEqual(active.status, "active")

        completed = manager.complete(goal.goal_id, tick=2, reason="satisfied")
        self.assertIsNotNone(completed)
        assert completed is not None
        self.assertEqual(completed.status, "completed")

        cancelled_goal = self._build_goal("Drop task", "custom", priority=1)
        cancelled = manager.cancel(cancelled_goal.goal_id, tick=3, reason="superseded")
        self.assertIsNotNone(cancelled)
        assert cancelled is not None
        self.assertEqual(cancelled.status, "cancelled")

        blocked_goal = self._build_goal("Blocked task", "custom", priority=1)
        blocked = manager.block(blocked_goal.goal_id, tick=4, reason="waiting on dependency")
        self.assertIsNotNone(blocked)
        assert blocked is not None
        self.assertEqual(blocked.status, "blocked")

        expired_goal = self._build_goal("Expired task", "custom", priority=1)
        expired = manager.expire(expired_goal.goal_id, tick=5, reason="deadline passed")
        self.assertIsNotNone(expired)
        assert expired is not None
        self.assertEqual(expired.status, "expired")

        event_types = [event.event_type for event in manager.history()]
        self.assertIn("GoalCreated", event_types)
        self.assertIn("GoalActive", event_types)
        self.assertIn("GoalCompleted", event_types)
        self.assertIn("GoalCancelled", event_types)
        self.assertIn("GoalBlocked", event_types)
        self.assertIn("GoalExpired", event_types)

    def test_plan_generation_validation_and_priority_ordering(self) -> None:
        hunger_goal = self._build_goal("Eat lunch", "hunger", priority=1)
        explore_goal = self._build_goal("Explore hall", "explore", target_state={"room": "Hall"}, priority=1)

        before_state = self.kernel.current_state
        before_revision = self.kernel.current_revision

        plans = self.kernel.plan(goals=[explore_goal, hunger_goal])

        self.assertTrue(all(isinstance(plan, PlanProposal) for plan in plans))
        self.assertEqual(self.kernel.current_state, before_state)
        self.assertEqual(self.kernel.current_revision, before_revision)
        self.assertIsNotNone(self.kernel.last_planning_diagnostics)

        self.assertGreaterEqual(len(plans), 2)
        self.assertEqual(plans[0].goal_id, hunger_goal.goal_id)
        self.assertGreater(plans[0].priority, plans[1].priority)

        validation = self.kernel.planner_engine.plan_validator.validate(
            self.kernel.planner_context(goals=[hunger_goal]),
            plans[0],
            hunger_goal,
        )
        self.assertIsInstance(validation, PlanValidationResult)
        self.assertTrue(validation.valid)

    def test_dependency_handling_and_memory_informed_planning(self) -> None:
        acquire_goal = self._build_goal("Acquire bottle", "acquire_item", target_state={"asset_id": self.bottle_asset.asset_id}, priority=2)
        plans = self.kernel.plan(goals=[acquire_goal])
        self.assertGreaterEqual(len(plans), 1)
        plan = plans[0]

        self.assertEqual(plan.action_requests[0].action, "PickUp")
        self.assertEqual(plan.action_requests[0].target_id, self.bottle.entity_id)

        invalid_plan = PlanProposal(
            plan_id=plan.plan_id,
            goal_id=plan.goal_id,
            entity_id=plan.entity_id,
            priority=plan.priority,
            estimated_cost=plan.estimated_cost,
            estimated_duration=plan.estimated_duration,
            action_requests=plan.action_requests,
            dependencies=("missing-dependency",),
            required_resources=plan.required_resources,
            confidence=plan.confidence,
            creation_tick=plan.creation_tick,
            planning_revision=plan.planning_revision,
            status=plan.status,
            goal_subject=plan.goal_subject,
            metadata=plan.metadata,
        )
        validation = self.kernel.planner_engine.plan_validator.validate(self.kernel.planner_context(goals=[acquire_goal]), invalid_plan, acquire_goal)
        self.assertFalse(validation.valid)
        self.assertTrue(any(failure.code == "dependency_missing" for failure in validation.failures))

    def test_plan_scheduling_and_kernel_integration(self) -> None:
        move_goal = self._build_goal("Go to hall", "movement", target_state={"room": "Hall"}, priority=5)
        plans = self.kernel.plan(goals=[move_goal])
        self.assertGreaterEqual(len(plans), 1)

        scheduled = self.kernel.schedule_plans(plans)
        self.assertGreaterEqual(len(scheduled), 1)
        self.assertTrue(all(hasattr(item, "request") for item in scheduled))

        revision = self.kernel.advance_tick()
        alice_room = revision.state["entities"][str(self.alice.entity_id.value)]["components"]["TransformComponent"]["room"]
        self.assertEqual(alice_room, "Hall")
        self.assertNotEqual(self.kernel.current_state["entities"][str(self.alice.entity_id.value)]["components"]["TransformComponent"]["room"], "Kitchen")

    def test_deterministic_planning_replay(self) -> None:
        kernel_a = WorldKernel(
            KernelConfig(
                world_name="planner_world",
                seed="planner-seed",
                initial_state={"mode": "planner"},
            )
        )
        kernel_b = WorldKernel(
            KernelConfig(
                world_name="planner_world",
                seed="planner-seed",
                initial_state={"mode": "planner"},
            )
        )

        def populate(kernel: WorldKernel) -> Goal:
            alice = kernel.entity_registry.create_entity(
                entity_type="human",
                display_name="Alice",
                created_tick=0,
                created_revision=None,
            )
            alice.attach_component(TransformComponent(room="Kitchen"), tick=0)
            alice.attach_component(NeedsComponent(needs={"hunger": 0.8, "thirst": 0.9, "energy": 0.5}), tick=0)
            return kernel.planner_engine.goal_manager.create_goal(
                subject="Eat lunch",
                kind="hunger",
                entity_id=alice.entity_id,
                priority=2,
                created_tick=0,
                created_revision=None,
            )

        goal_a = populate(kernel_a)
        goal_b = populate(kernel_b)

        plans_a = kernel_a.plan(goals=[goal_a])
        plans_b = kernel_b.plan(goals=[goal_b])

        self.assertEqual(tuple(plan.plan_id for plan in plans_a), tuple(plan.plan_id for plan in plans_b))
        self.assertEqual(tuple(request.correlation_id for plan in plans_a for request in plan.action_requests), tuple(request.correlation_id for plan in plans_b for request in plan.action_requests))

    def test_planner_emits_only_plan_proposals_and_does_not_mutate_world_state(self) -> None:
        goal = self._build_goal("Eat lunch", "hunger", priority=2)
        before_snapshot = self.kernel.create_snapshot()
        before_world_state = self.kernel.current_state
        before_history = tuple(self.kernel.world_memory.history())

        plans = self.kernel.plan(goals=[goal])

        self.assertTrue(all(isinstance(plan, PlanProposal) for plan in plans))
        self.assertEqual(self.kernel.create_snapshot().state, before_snapshot.state)
        self.assertEqual(self.kernel.current_state, before_world_state)
        self.assertEqual(tuple(self.kernel.world_memory.history()), before_history)


if __name__ == "__main__":
    unittest.main()
