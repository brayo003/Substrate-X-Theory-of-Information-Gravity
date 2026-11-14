#!/usr/bin/env python3
import sys
from pathlib import Path

PARENT_DIR = Path(__file__).resolve().parents[2]
SIM_WORLD_DIR = Path(__file__).resolve().parents[1]

if str(PARENT_DIR) not in sys.path:
    sys.path.insert(0, str(PARENT_DIR))
if str(SIM_WORLD_DIR) not in sys.path:
    sys.path.insert(0, str(SIM_WORLD_DIR))

from sim_world.kernel.world_kernel import WorldKernel
from sim_world.domains import register_all, bootstrap_all
from sim_world.core.revision import Revision
from sim_world.core.errors import ValidationError
from sim_world.core.contracts import freeze_value
from sim_world.core.ids import RevisionId

TARGET_ENTITY_ID = "00501c9e-9c3b-5b81-a0d3-9f78d5c05fa8"

original_commit_state = WorldKernel.commit_state

def instrumented_commit_state(self, tick_context, transition_proposals=None, metadata=None):
    previous_snapshot = self.create_snapshot()
    proposals = tuple(transition_proposals or ())
    normalized = []
    
    for proposal in proposals:
        if proposal.world_id != self.config.world_id:
            raise AssertionError("world_id mismatch")
        outcome = self.validate_action(proposal)
        if not outcome.valid:
            raise ValidationError(outcome.reason)
        normalized.append(outcome.normalized)
    
    print(f"=== STAGE: Entity IDs in world_state before event application ===")
    entities_before = dict(self.current_state.get("entities", {}))
    print(f"Total entities: {len(entities_before)}")
    print(f"Human entities: {sum(1 for e in entities_before.values() if str(e.get('type')) == 'human')}")
    print(f"Target entity {TARGET_ENTITY_ID} in world_state: {TARGET_ENTITY_ID in entities_before}")
    if TARGET_ENTITY_ID in entities_before:
        print(f"Target entity data: {entities_before[TARGET_ENTITY_ID].get('name')}")
    
    next_state = dict(self.current_state)
    events = []
    
    for index, proposal in enumerate(normalized):
        if 'entity_needs_components' in dict(proposal.patch):
            print(f"\n=== Processing needs proposal {index} ===")
            needs_components = dict(proposal.patch['entity_needs_components'])
            print(f"Entity IDs in needs patch: {list(needs_components.keys())}")
            print(f"Target entity {TARGET_ENTITY_ID} in needs patch: {TARGET_ENTITY_ID in needs_components}")
    
        event = self._event_from_proposal(
            proposal,
            world_id=self.world_id,
            revision_id=None,
            tick_id=tick_context.tick_id,
            state_before=next_state,
            index=index,
            metadata=metadata,
        )
        
        next_state = event.apply_to(next_state)
        events.append(event)
    
    print(f"\n=== STAGE: Entity IDs in world_state after event application ===")
    print(f"Total entities: {len(next_state)}")
    print(f"Human entities: {sum(1 for e in next_state.values() if str(e.get('type')) == 'human')}")
    print(f"Target entity {TARGET_ENTITY_ID} in next_state: {TARGET_ENTITY_ID in next_state}")
    
    revision_sequence = self._clock.tick_number if self._clock.tick_number else len(self.storage.list_history()) + 1
    revision = Revision(
        world_id=self.world_id,
        revision_id=RevisionId.new(
            self.world_id,
            tick_context.tick_id,
            revision_sequence,
            {"events": [str(event.event_id.value) for event in events], "state_hash": repr(freeze_value(next_state))},
        ),
        tick_id=tick_context.tick_id,
        timestamp=tick_context.timestamp,
        parent_revision=None if self._current_revision is None or self._is_genesis_revision(self._current_revision) else self._current_revision.revision_id,
        events=tuple(events),
        state=next_state,
        metadata={} if metadata is None else dict(metadata),
    )
    self._state = next_state
    self._current_revision = self.world_memory.record_revision(
        revision,
        entity_refs=self.entity_registry.agent_memory_references(),
    )
    
    return revision

WorldKernel.commit_state = instrumented_commit_state

kernel = WorldKernel()
register_all(kernel.simulation_engine)
bootstrap_all(kernel)

print()
print("=" * 80)
print("Running 1 tick...")
print("=" * 80)
print()

kernel.advance_tick()

print()
print("=" * 80)
print("Final canonical entities state")
print("=" * 80)
print()

entities = dict(kernel.current_state.get("entities", {}))
print(f"Total entities: {len(entities)}")
print(f"Human entities: {sum(1 for e in entities.values() if str(e.get('type')) == 'human')}")
print(f"Target entity {TARGET_ENTITY_ID} in final state: {TARGET_ENTITY_ID in entities}")

if TARGET_ENTITY_ID in entities:
    entity = entities[TARGET_ENTITY_ID]
    print(f"Entity: {entity.get('name')} (type: {entity.get('type')})")
else:
    print("Target entity not found")
    print(f"Available human entity IDs: {[eid for eid, e in entities.items() if str(e.get('type')) == 'human']}")
