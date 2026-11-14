from __future__ import annotations

from dataclasses import FrozenInstanceError
import unittest

from sim_world import (
    CalibrationProfile,
    InventoryComponent,
    HealthComponent,
    KernelConfig,
    NeedsComponent,
    RenderSnapshot,
    ResourceDescriptor,
    TickId,
    TransformComponent,
    TransitionProposal,
    TransportContext,
    TransportEngine,
    WorldKernel,
)


class TransportSubsystemTests(unittest.TestCase):
    def setUp(self) -> None:
        self.kernel = WorldKernel(
            KernelConfig(
                world_name="transport_world",
                seed="transport-seed",
                initial_state={"mode": "transport"},
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
        self.item = self.registry.create_entity(
            entity_type="object",
            display_name="Bottle",
            created_tick=0,
            created_revision=None,
        )

        self.alice.attach_component(TransformComponent(room="Kitchen"), tick=0)
        self.alice.attach_component(
            InventoryComponent(items=(ResourceDescriptor("food", 1, {"fresh": True}),)),
            tick=0,
        )
        self.alice.attach_component(NeedsComponent(needs={"hunger": 0.8, "thirst": 0.7}), tick=0)
        self.bob.attach_component(TransformComponent(room="Kitchen"), tick=0)
        self.door.attach_component(TransformComponent(room="Kitchen"), tick=0)
        self.item.attach_component(TransformComponent(room="Kitchen"), tick=0)

    def _context(
        self,
        previous_snapshot: RenderSnapshot,
        current_snapshot: RenderSnapshot,
        *,
        previous_revision=None,
        current_revision=None,
        tick_number: int = 0,
        profile: CalibrationProfile | str | None = "default",
        representation_type: str = "snapshot_transition",
    ) -> TransportContext:
        return TransportContext(
            world_id=self.kernel.world_id,
            previous_snapshot=previous_snapshot,
            current_snapshot=current_snapshot,
            previous_revision=previous_revision,
            current_revision=current_revision,
            transition_proposals=(),
            configuration={"transport_mode": "test"},
            calibration_profile=profile,
            representation_type=representation_type,
            domain_adapter_id="kernel",
            correlation_id="transport-test",
            tick_number=tick_number,
            metadata={"source": "test"},
        )

    def test_identical_snapshots_produce_deterministic_observations(self) -> None:
        snapshot = self.kernel.create_snapshot()
        context = self._context(snapshot, snapshot, tick_number=self.kernel.current_tick_number)
        engine = TransportEngine()

        first = engine.observe(context)
        second = engine.observe(context)

        self.assertEqual(first, second)
        self.assertEqual(first.q_value, 1.0)
        self.assertEqual(first.metric_values["state_distance"], 0.0)
        self.assertEqual(first.metric_values["identity_preservation"], 1.0)
        self.assertEqual(first.metric_values["topology_preservation"], 1.0)
        self.assertEqual(snapshot.state["entities"][str(self.alice.entity_id.value)]["components"]["TransformComponent"]["room"], "Kitchen")

    def test_movement_relationship_and_component_changes_affect_metrics(self) -> None:
        engine = TransportEngine()

        before = self.kernel.create_snapshot()
        self.alice.attach_component(TransformComponent(room="Hall"), tick=1)
        after_movement = self.kernel.create_snapshot()
        movement = engine.observe(self._context(before, after_movement))

        self.assertGreater(movement.metric_values["state_distance"], 0.0)
        self.assertEqual(movement.metric_values["identity_preservation"], 1.0)
        self.assertLess(movement.metric_values["topology_preservation"], 1.0)

        before_relationship = after_movement
        self.registry.connect_relationship(
            self.alice.entity_id,
            self.bob.entity_id,
            "friend",
            created_tick=2,
            metadata={"strength": "high"},
        )
        after_relationship = self.kernel.create_snapshot()
        relationship = engine.observe(self._context(before_relationship, after_relationship))
        self.assertLess(relationship.metric_values["relationship_preservation"], 1.0)

        before_component = after_relationship
        self.alice.attach_component(HealthComponent(current=8, maximum=10, status="fair"), tick=3)
        after_component = self.kernel.create_snapshot()
        component = engine.observe(self._context(before_component, after_component))
        self.assertLess(component.metric_values["component_preservation"], 1.0)

    def test_calibration_profile_application(self) -> None:
        engine = TransportEngine()
        profile = CalibrationProfile(
            name="sensitive",
            version="2.0",
            representation_type="snapshot_transition",
            metric_weights={
                "state_distance": 2.0,
                "representation_distance": 1.0,
                "identity_preservation": 1.0,
                "topology_preservation": 1.0,
                "component_preservation": 1.0,
                "relationship_preservation": 1.0,
                "transition_magnitude": 1.5,
                "structural_consistency": 1.0,
                "temporal_consistency": 1.0,
            },
            provenance={"source": "test"},
            metadata={"purpose": "sensitivity"},
        )
        engine.calibrator.register_profile(profile)

        before = self.kernel.create_snapshot()
        self.alice.attach_component(TransformComponent(room="Hall"), tick=1)
        after = self.kernel.create_snapshot()

        default_obs = engine.observe(self._context(before, after, profile="default"))
        custom_obs = engine.observe(self._context(before, after, profile="sensitive"))

        self.assertNotEqual(default_obs.q_value, custom_obs.q_value)
        self.assertEqual(custom_obs.calibration_metadata.profile_name, "sensitive")
        self.assertEqual(custom_obs.calibration_metadata.version, "2.0")
        self.assertIn("state_distance", custom_obs.calibration_metadata.metric_weights)

    def test_deterministic_replay_and_immutability(self) -> None:
        def build_kernel() -> WorldKernel:
            kernel = WorldKernel(
                KernelConfig(
                    world_name="transport_world",
                    seed="transport-seed",
                    initial_state={"mode": "transport"},
                )
            )
            registry = kernel.entity_registry
            alice = registry.create_entity(
                entity_type="human",
                display_name="Alice",
                created_tick=0,
                created_revision=None,
            )
            alice.attach_component(TransformComponent(room="Kitchen"), tick=0)
            alice.attach_component(InventoryComponent(items=(ResourceDescriptor("food", 1, {"fresh": True}),)), tick=0)
            alice.attach_component(NeedsComponent(needs={"hunger": 0.8, "thirst": 0.7}), tick=0)
            before = kernel.create_snapshot()
            alice.attach_component(TransformComponent(room="Hall"), tick=1)
            after = kernel.create_snapshot()
            return kernel, before, after

        kernel_a, before_a, after_a = build_kernel()
        kernel_b, before_b, after_b = build_kernel()
        engine = TransportEngine()

        obs_a = engine.observe(self._context(before_a, after_a))
        obs_b = engine.observe(self._context(before_b, after_b))

        self.assertEqual(obs_a, obs_b)
        with self.assertRaises(FrozenInstanceError):
            obs_a.q_value = 0.0  # type: ignore[misc]
        with self.assertRaises(TypeError):
            before_a.state["mode"] = "changed"  # type: ignore[index]

        self.assertEqual(kernel_a.current_state, kernel_b.current_state)

    def test_kernel_integration_and_history(self) -> None:
        before_history = len(self.kernel.transport_history)
        revision = self.kernel.advance_tick(
            [
                TransitionProposal(
                    world_id=self.kernel.world_id,
                    tick_id=None,
                    state_revision=None,
                    correlation_id="transport-commit",
                    subject="counter",
                    patch={"counter": 1, "mode": "transport"},
                    description="advance counter",
                    metadata={},
                )
            ]
        )

        after_history = self.kernel.transport_history
        self.assertEqual(len(after_history), before_history + 1)
        self.assertIsNotNone(self.kernel.last_transport_observation)
        self.assertEqual(after_history[-1], self.kernel.last_transport_observation)
        self.assertEqual(after_history[-1].current_revision, revision.revision_id)
        self.assertEqual(self.kernel.current_state["counter"], 1)

    def test_q_does_not_mutate_world_state_or_snapshots(self) -> None:
        engine = TransportEngine()
        snapshot = self.kernel.create_snapshot()
        before_state = self.kernel.current_state
        context = self._context(snapshot, snapshot)

        observation = engine.observe(context)

        self.assertEqual(self.kernel.current_state, before_state)
        self.assertEqual(snapshot.state, before_state)
        self.assertEqual(observation.metric_values["state_distance"], 0.0)


if __name__ == "__main__":
    unittest.main()
