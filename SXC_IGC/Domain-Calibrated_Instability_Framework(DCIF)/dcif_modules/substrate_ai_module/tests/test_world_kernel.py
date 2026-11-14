from __future__ import annotations

import unittest

from sim_world import KernelConfig, TransitionProposal, WorldKernel


class WorldKernelTests(unittest.TestCase):
    def setUp(self) -> None:
        self.kernel = WorldKernel(
            KernelConfig(
                world_name="demo_world",
                seed="test-seed",
                initial_state={"counter": 0, "status": "seed"},
            )
        )

    def _proposal(self, counter_value: int) -> TransitionProposal:
        return TransitionProposal(
            world_id=self.kernel.world_id,
            tick_id=None,
            state_revision=None,
            correlation_id=f"tick-{counter_value}",
            subject="counter",
            patch={"counter": counter_value, "status": f"tick-{counter_value}"},
            description="increment counter",
            metadata={"counter_value": counter_value},
        )

    def test_world_lifecycle_and_replay(self) -> None:
        first = self.kernel.advance_tick([self._proposal(1)])
        second = self.kernel.advance_tick([self._proposal(2)])
        third = self.kernel.advance_tick([self._proposal(3)])

        self.assertEqual(first.state["counter"], 1)
        self.assertEqual(second.state["counter"], 2)
        self.assertEqual(third.state["counter"], 3)
        self.assertEqual(first.parent_revision, None)
        self.assertEqual(second.parent_revision, first.revision_id)
        self.assertEqual(third.parent_revision, second.revision_id)

        snapshot = self.kernel.create_snapshot()
        self.assertEqual(snapshot.state["counter"], 3)
        self.assertEqual(snapshot.state_revision, third.revision_id)
        self.assertEqual(snapshot.tick_id, third.tick_id)
        with self.assertRaises(TypeError):
            snapshot.state["counter"] = 99  # type: ignore[index]

        restored = self.kernel.rollback(first.revision_id)
        self.assertEqual(restored.state["counter"], 1)
        self.assertEqual(self.kernel.current_revision.state["counter"], 1)

        replayed = self.kernel.replay_history()
        self.assertEqual(replayed["counter"], 1)
        self.assertEqual(replayed["status"], "tick-1")

        history = self.kernel.storage.list_history()
        self.assertEqual(len(history), 4)
        self.assertEqual(history[-1].state["counter"], 1)


if __name__ == "__main__":
    unittest.main()
