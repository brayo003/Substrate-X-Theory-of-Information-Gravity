from __future__ import annotations

import json
import unittest

from sim_world import (
    ASCIIRenderer,
    DebugRenderer,
    InventoryComponent,
    JsonRenderer,
    KernelConfig,
    RenderProfileRegistry,
    RenderRequest,
    RendererContext,
    RendererEngine,
    TextRenderer,
    TransformComponent,
    WorldKernel,
)


class RendererSubsystemTests(unittest.TestCase):
    def setUp(self) -> None:
        self.kernel = WorldKernel(
            KernelConfig(
                world_name="renderer_world",
                seed="renderer-seed",
                initial_state={"mode": "renderer"},
            )
        )
        self.registry = self.kernel.entity_registry
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
        self.room = self.registry.create_entity(
            entity_type="room",
            display_name="Kitchen",
            created_tick=0,
            created_revision=None,
        )
        self.alice.attach_component(TransformComponent(room="Kitchen"), tick=0)
        self.alice.attach_component(
            InventoryComponent(items=()),
            tick=0,
        )
        self.bob.attach_component(TransformComponent(room="Kitchen"), tick=0)

    def _context(self, profile: str | None = "text", renderer_type: str | None = None) -> RendererContext:
        snapshot = self.kernel.create_snapshot()
        return RendererContext(
            world_id=self.kernel.world_id,
            snapshot=snapshot,
            render_profile=profile,
            renderer_type=renderer_type,
            requested_output="scene summary",
            configuration={"theme": "clean"},
            user_parameters={"camera": "static"},
            correlation_id="renderer-test",
            metadata={"source": "test"},
        )

    def test_snapshot_immutability_and_request_creation(self) -> None:
        snapshot = self.kernel.create_snapshot()
        with self.assertRaises(TypeError):
            snapshot.state["mode"] = "changed"  # type: ignore[index]

        profile = self.kernel.renderer_engine.lookup_profile("text")
        request = RenderRequest.create(
            world_id=self.kernel.world_id,
            snapshot=snapshot,
            render_profile=profile,
            renderer_type="text",
            requested_output="scene summary",
            configuration={"theme": "clean"},
            metadata={"source": "test"},
        )

        self.assertEqual(request.snapshot_id, snapshot.snapshot_id)
        self.assertEqual(request.render_profile.name, "text")
        self.assertEqual(request.renderer_type, "text")
        self.assertEqual(request.requested_output, "scene summary")

    def test_text_json_and_debug_renderers(self) -> None:
        snapshot = self.kernel.create_snapshot()
        profile_registry = RenderProfileRegistry()
        profile = profile_registry.select("text")
        request = RenderRequest.create(
            world_id=self.kernel.world_id,
            snapshot=snapshot,
            render_profile=profile,
            renderer_type="text",
            requested_output="scene summary",
            configuration={},
            metadata={},
        )

        text_result = TextRenderer().render(request)
        json_result = JsonRenderer().render(
            RenderRequest.create(
                world_id=self.kernel.world_id,
                snapshot=snapshot,
                render_profile=profile_registry.select("structured_json"),
                renderer_type="json",
                requested_output="scene summary",
            )
        )
        debug_result = DebugRenderer().render(
            RenderRequest.create(
                world_id=self.kernel.world_id,
                snapshot=snapshot,
                render_profile=profile_registry.select("debug"),
                renderer_type="debug",
                requested_output="scene summary",
            )
        )
        ascii_result = ASCIIRenderer().render(
            RenderRequest.create(
                world_id=self.kernel.world_id,
                snapshot=snapshot,
                render_profile=profile_registry.select("ascii"),
                renderer_type="ascii",
                requested_output="scene summary",
            )
        )

        self.assertIsInstance(text_result.output_payload, str)
        self.assertIn("Alice", text_result.output_payload)
        self.assertIsInstance(json_result.output_payload, str)
        self.assertEqual(json.loads(json_result.output_payload)["profile"], "structured_json")
        self.assertIn("snapshot", debug_result.output_payload)
        self.assertEqual(debug_result.output_payload["snapshot"]["world_id"], str(self.kernel.world_id.value))
        self.assertIsInstance(ascii_result.output_payload, str)
        self.assertIn("Kitchen", ascii_result.output_payload)

    def test_profile_selection_adapter_registry_and_capabilities(self) -> None:
        engine = RendererEngine()
        self.assertEqual(engine.lookup_profile("text").name, "text")
        self.assertEqual(engine.lookup_profile("structured_json").output_format, "json")
        self.assertEqual(engine.lookup_adapter("text").renderer_type, "text")
        self.assertEqual(engine.lookup_adapter("json").renderer_type, "json")
        self.assertIn("profiles", engine.capability_report())

    def test_deterministic_rendering_and_multiple_adapters(self) -> None:
        engine = RendererEngine()
        context = self._context(profile="text")

        first = engine.render(context)
        second = engine.render(context)

        self.assertEqual(first, second)
        self.assertEqual(first.renderer_type, "text")
        self.assertEqual(first.output_format, "text")

        json_context = self._context(profile="structured_json")
        json_result = engine.render(json_context)
        debug_context = self._context(profile="debug")
        debug_result = engine.render(debug_context)
        self.assertNotEqual(first.output_payload, json_result.output_payload)
        self.assertNotEqual(json_result.output_format, debug_result.output_format)

    def test_kernel_integration_and_history(self) -> None:
        before_history = len(self.kernel.render_history)
        result = self.kernel.render(render_profile="text", requested_output="scene summary")
        after_history = self.kernel.render_history

        self.assertEqual(len(after_history), before_history + 1)
        self.assertEqual(after_history[-1], result)
        self.assertEqual(self.kernel.last_render_result, result)
        self.assertEqual(result.renderer_type, "text")
        self.assertIn("Alice", result.output_payload)

    def test_renderer_never_mutates_world_state_or_snapshot(self) -> None:
        engine = RendererEngine()
        snapshot = self.kernel.create_snapshot()
        before_state = self.kernel.current_state
        before_snapshot = snapshot.state

        result = engine.render(self._context(profile="text"))

        self.assertEqual(self.kernel.current_state, before_state)
        self.assertEqual(snapshot.state, before_snapshot)
        self.assertEqual(result.profile.name, "text")


if __name__ == "__main__":
    unittest.main()
