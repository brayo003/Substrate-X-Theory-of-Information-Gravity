from __future__ import annotations

import unittest

from sim_world import (
    ActionDefinition,
    HealthComponent,
    InventoryComponent,
    NeedsComponent,
    RelationshipComponent,
    RelationshipGraph,
    ResourceDescriptor,
    TransformComponent,
    WorldKernel,
)


class EntitySystemTests(unittest.TestCase):
    def setUp(self) -> None:
        self.kernel = WorldKernel()
        self.registry = self.kernel.entity_registry

    def test_entity_creation_component_attachment_relationships_and_snapshot_visibility(self) -> None:
        alice = self.registry.create_entity(
            entity_type="human",
            display_name="Alice",
            created_tick=0,
            created_revision=None,
        )
        bob = self.registry.create_entity(
            entity_type="human",
            display_name="Bob",
            created_tick=0,
            created_revision=None,
        )

        alice.attach_component(TransformComponent(position=(1.0, 2.0, 3.0), room="kitchen"), tick=1)
        alice.attach_component(HealthComponent(current=75, maximum=100, status="stable"), tick=1)
        alice.attach_component(
            InventoryComponent(items=(ResourceDescriptor("food", 2, {"fresh": True}),), capacity=10),
            tick=1,
        )
        alice.attach_component(NeedsComponent(needs={"hunger": 0.2, "energy": 0.9}), tick=1)
        alice.attach_component(RelationshipComponent(relationships=("friend",)), tick=1)

        alice.register_action(
            ActionDefinition(
                identifier="Walk",
                preconditions=("awake",),
                required_components=("TransformComponent",),
                resource_requirements={"energy": 1},
                cooldown=1.5,
            ),
            tick=1,
        )

        relation = self.registry.connect_relationship(
            alice.entity_id,
            bob.entity_id,
            "friend",
            created_tick=2,
            metadata={"strength": "high"},
        )

        self.assertTrue(self.registry.entity_exists(alice.entity_id))
        self.assertEqual(self.registry.get_entity(alice.entity_id).display_name, "Alice")
        self.assertEqual(self.registry.find_by_type("human"), (alice, bob))
        self.assertIn(alice, self.registry.find_by_component("TransformComponent"))
        self.assertEqual(self.registry.list_entities(), (alice, bob))
        self.assertEqual(self.registry.query(lambda entity: entity.display_name == "Alice"), (alice,))

        self.assertTrue(alice.actions.has("Walk"))
        self.assertIsNotNone(alice.actions.get("Walk"))

        outgoing = self.registry.relationships.outgoing(alice.entity_id, "friend")
        incoming = self.registry.relationships.incoming(bob.entity_id, "friend")
        typed = self.registry.relationships.typed_lookup("friend", entity_id=alice.entity_id)
        self.assertEqual(outgoing, (relation,))
        self.assertEqual(incoming, (relation,))
        self.assertEqual(typed, (relation,))

        snapshot = self.kernel.create_snapshot()
        entities_state = snapshot.state["entities"]
        alice_state = entities_state[str(alice.entity_id.value)]
        self.assertEqual(alice_state["display_name"], "Alice")
        self.assertIn("TransformComponent", alice_state["components"])
        self.assertTrue(any(record["relationship_type"] == "friend" for record in alice_state["relationships"]))
        self.assertTrue(any(record["identifier"] == "Walk" for record in alice_state["actions"]))

        self.assertGreater(len(alice.history), 1)
        self.assertEqual(alice.history_ref, str(alice.history[-1].event_id.value))
        self.assertTrue(all(event.entity_id == alice.entity_id for event in self.registry.history_for(alice.entity_id)))

        removed_component = alice.remove_component("NeedsComponent", tick=3)
        self.assertIsNotNone(removed_component)
        self.assertNotIn("NeedsComponent", alice.components)

        destroyed = self.registry.destroy_entity(alice.entity_id, tick=4)
        self.assertFalse(destroyed.alive)
        self.assertFalse(self.registry.entity_exists(alice.entity_id))
        self.assertEqual(destroyed.lifecycle, "destroyed_tombstoned")

        snapshot_after_destroy = self.kernel.create_snapshot()
        destroyed_state = snapshot_after_destroy.state["entities"][str(alice.entity_id.value)]
        self.assertFalse(destroyed_state["alive"])
        self.assertFalse(destroyed_state["enabled"])


if __name__ == "__main__":
    unittest.main()
