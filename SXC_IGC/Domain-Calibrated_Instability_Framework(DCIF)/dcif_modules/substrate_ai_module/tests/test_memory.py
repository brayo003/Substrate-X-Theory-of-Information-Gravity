from __future__ import annotations

import unittest

from sim_world import KernelConfig, TickId, TransitionProposal, WorldKernel


class MemorySubsystemTests(unittest.TestCase):
    def setUp(self) -> None:
        self.kernel = WorldKernel(
            KernelConfig(
                world_name="memory_world",
                seed="memory-seed",
                initial_state={"counter": 0, "status": "seed"},
            )
        )

    def _proposal(self, counter_value: int) -> TransitionProposal:
        return TransitionProposal(
            world_id=self.kernel.world_id,
            tick_id=None,
            state_revision=None,
            correlation_id=f"memory-tick-{counter_value}",
            subject="counter",
            patch={"counter": counter_value, "status": f"tick-{counter_value}"},
            description="advance counter",
            metadata={"counter_value": counter_value},
        )

    def test_world_history_and_timeline_replay(self) -> None:
        first = self.kernel.advance_tick([self._proposal(1)])
        second = self.kernel.advance_tick([self._proposal(2)])
        third = self.kernel.advance_tick([self._proposal(3)])

        history = self.kernel.world_memory.history()
        self.assertEqual(len(history), 3)
        self.assertEqual(history[-1].revision_id, third.revision_id)

        timeline = self.kernel.world_memory.temporal_memory.replay()
        self.assertEqual(len(timeline), 3)
        self.assertEqual(timeline[0].revision_id, first.revision_id)
        self.assertEqual(timeline[1].revision_id, second.revision_id)
        self.assertEqual(timeline[2].revision_id, third.revision_id)

        between = self.kernel.world_memory.temporal_memory.between_revisions(first.revision_id, third.revision_id)
        self.assertEqual(len(between), 3)
        self.assertEqual(between[0].revision_id, first.revision_id)
        self.assertEqual(between[-1].revision_id, third.revision_id)

        looked_up = self.kernel.world_memory.revision(second.revision_id)
        self.assertIsNotNone(looked_up)
        self.assertEqual(looked_up.state["counter"], 2)

    def test_agent_memory_remember_forget_search_and_latest(self) -> None:
        alice = self.kernel.entity_registry.create_entity(
            entity_type="human",
            display_name="Alice",
            created_tick=0,
            created_revision=None,
        )
        memory = self.kernel.world_memory.agent_memory_for(alice.entity_id)
        self.assertIsNotNone(memory)
        assert memory is not None

        first = memory.remember("fact", "Alice likes tea", tags=("preference",), metadata={"source": "conversation"})
        second = memory.remember("goal", "Buy tea", tags=("shopping",), metadata={"priority": "high"})

        self.assertEqual(memory.latest().record_id, second.record_id)
        self.assertEqual(memory.recall(kind="fact")[0].content, "Alice likes tea")
        self.assertEqual(memory.search("tea")[0].record_id, first.record_id)

        forgotten = memory.forget(first.record_id)
        self.assertEqual(forgotten[0].record_id, first.record_id)
        self.assertEqual(memory.recall(kind="fact"), ())
        self.assertEqual(memory.recall(kind="fact", include_forgotten=True)[0].record_id, first.record_id)
        self.assertEqual(memory.latest("goal").record_id, second.record_id)

    def test_asset_identity_persistence_and_snapshot_visibility(self) -> None:
        bottle = self.kernel.entity_registry.create_entity(
            entity_type="object",
            display_name="Bottle",
            created_tick=0,
            created_revision=None,
        )
        asset = self.kernel.world_memory.record_asset(
            canonical_name="Green bottle",
            descriptors={"color": "green", "size_ml": 600, "material": "glass"},
            serial_number="GB-600",
            manufacturer="SimWorks",
            creation_metadata={"origin": "lab"},
            provenance={"source": "catalog"},
            entity_id=bottle.entity_id,
            created_tick=0,
            created_revision=None,
        )

        looked_up = self.kernel.world_memory.asset_memory.lookup(asset.asset_id)
        self.assertIsNotNone(looked_up)
        self.assertEqual(looked_up.asset_id, asset.asset_id)
        self.assertEqual(self.kernel.world_memory.asset_memory.find_by_entity(bottle.entity_id).asset_id, asset.asset_id)

        self.kernel.advance_tick([self._proposal(1)])
        self.assertEqual(self.kernel.world_memory.asset_memory.latest(asset.asset_id).asset_id, asset.asset_id)

        snapshot = self.kernel.create_snapshot()
        memory_refs = snapshot.metadata["memory_refs"]
        self.assertIn("asset_memory", memory_refs)
        self.assertGreaterEqual(memory_refs["asset_memory"]["count"], 1)

    def test_relationship_evolution_and_replay(self) -> None:
        alice = self.kernel.entity_registry.create_entity(
            entity_type="human",
            display_name="Alice",
            created_tick=0,
            created_revision=None,
        )
        bob = self.kernel.entity_registry.create_entity(
            entity_type="human",
            display_name="Bob",
            created_tick=0,
            created_revision=None,
        )
        tick_one = TickId.new(self.kernel.world_id, 1)
        tick_two = TickId.new(self.kernel.world_id, 2)
        tick_three = TickId.new(self.kernel.world_id, 3)

        first = self.kernel.world_memory.record_relationship(
            alice.entity_id,
            bob.entity_id,
            "friend",
            "friend",
            tick_id=tick_one,
            revision_id=None,
        )
        second = self.kernel.world_memory.record_relationship(
            alice.entity_id,
            bob.entity_id,
            "friend",
            "enemy",
            tick_id=tick_two,
            revision_id=None,
        )
        third = self.kernel.world_memory.record_relationship(
            alice.entity_id,
            bob.entity_id,
            "friend",
            "married",
            tick_id=tick_three,
            revision_id=None,
        )

        latest = self.kernel.world_memory.relationship_memory.latest(source_id=alice.entity_id, target_id=bob.entity_id)
        self.assertIsNotNone(latest)
        self.assertEqual(latest.state, "married")

        replay = self.kernel.world_memory.relationship_memory.replay(source_id=alice.entity_id, target_id=bob.entity_id)
        self.assertEqual([record.state for record in replay], ["friend", "enemy", "married"])

        between = self.kernel.world_memory.relationship_memory.between_ticks(tick_one, tick_three)
        self.assertEqual(len(between), 3)
        self.assertEqual(second.state, "enemy")

    def test_knowledge_lookup_and_rollback_references(self) -> None:
        fact = self.kernel.world_memory.record_knowledge("Trees burn.", kind="fact", categories=("ecology",), tags=("fire",))
        rule = self.kernel.world_memory.record_knowledge("Water extinguishes fire.", kind="rule", categories=("physics",), tags=("water",))
        category = self.kernel.world_memory.record_knowledge("Organic matter", kind="category", categories=("matter",), tags=("life",))

        self.assertEqual(self.kernel.world_memory.knowledge_memory.lookup(fact.knowledge_id).statement, "Trees burn.")
        self.assertEqual(len(self.kernel.world_memory.knowledge_memory.query("fire")), 2)
        self.assertEqual(self.kernel.world_memory.knowledge_memory.rules()[0].knowledge_id, rule.knowledge_id)
        self.assertEqual(self.kernel.world_memory.knowledge_memory.categories()[0].knowledge_id, category.knowledge_id)

        first = self.kernel.advance_tick([self._proposal(1)])
        second = self.kernel.advance_tick([self._proposal(2)])
        self.kernel.rollback(first.revision_id)

        rollback_refs = self.kernel.world_memory.rollback_references()
        self.assertGreaterEqual(len(rollback_refs), 1)
        latest_ref = rollback_refs[-1]
        self.assertEqual(latest_ref.to_revision, first.revision_id)
        self.assertEqual(latest_ref.from_revision, second.revision_id)


if __name__ == "__main__":
    unittest.main()
