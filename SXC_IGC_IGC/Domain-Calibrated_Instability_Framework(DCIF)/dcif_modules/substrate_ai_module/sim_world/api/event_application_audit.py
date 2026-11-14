#!/usr/bin/env python3
import sys
from pathlib import Path

PARENT_DIR = Path(__file__).resolve().parents[2]
SIM_WORLD_DIR = Path(__file__).resolve().parents[1]

if str(PARENT_DIR) not in sys.path:
    sys.path.insert(0, str(PARENT_DIR))
if str(SIM_WORLD_DIR) not in sys.path:
    sys.path.insert(0, str(SIM_WORLD_DIR))

# Instrument kernel.commit_state to see event application
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
    
    print(f"=== STAGE: Before event application ===")
    print(f"Normalized proposals: {len(normalized)}")
    
    # Find needs proposal
    needs_proposal = None
    for i, proposal in enumerate(normalized):
        if 'entity_needs_components' in dict(proposal.patch):
            needs_proposal = proposal
            print(f"Needs proposal found at index {i}")
            print(f"Patch keys: {list(dict(proposal.patch).keys())}")
            needs_components = dict(proposal.patch['entity_needs_components'])
            if TARGET_ENTITY_ID in needs_components:
                entity_patch = dict(needs_components[TARGET_ENTITY_ID])
                print(f"Target entity in needs patch: {list(entity_patch.keys())}")
                if 'components' in entity_patch:
                    components_patch = dict(entity_patch['components'])
                    if 'NeedsComponent' in components_patch:
                        needs_patch = dict(components_patch['NeedsComponent'])
                        if 'needs' in needs_patch:
                            needs_data = dict(needs_patch['needs'])
                            print(f"Hunger in needs patch: {needs_data.get('hunger')}")
    
    next_state = dict(self.current_state)
    events = []
    
    for index, proposal in enumerate(normalized):
        print(f"\n=== Processing proposal {index} ===")
        print(f"Patch keys: {list(dict(proposal.patch).keys())}")
        
        event = self._event_from_proposal(
            proposal,
            world_id=self.world_id,
            revision_id=None,
            tick_id=tick_context.tick_id,
            state_before=next_state,
            index=index,
            metadata=metadata,
        )
        
        print(f"Event created: {type(event)}")
        print(f"Event will apply to {len(next_state)} entities")
        
        next_state = event.apply_to(next_state)
        events.append(event)
        
        print(f"After event.apply_to: {len(next_state)} entities")
        
        # Check if target entity exists in next_state
        if TARGET_ENTITY_ID in next_state:
            entity = next_state[TARGET_ENTITY_ID]
            if 'components' in dict(entity):
                components = dict(entity['components'])
                if 'NeedsComponent' in components:
                    needs_comp = dict(components['NeedsComponent'])
                    if 'needs' in needs_comp:
                        needs = dict(needs_comp['needs'])
                        print(f"Hunger in next_state after event {index}: {needs.get('hunger')}")
    
    # Continue with rest of commit
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
entity = entities.get(TARGET_ENTITY_ID)

if entity:
    print(f"Entity: {entity.get('name')} (type: {entity.get('type')})")
    components = dict(entity.get("components", {}))
    needs_comp = dict(components.get("NeedsComponent", {}))
    needs = dict(needs_comp.get("needs", {}))
    hunger = needs.get("hunger", 0.0)
    print(f"Hunger in canonical entity: {hunger:.2%}")
else:
    print("Entity not found in canonical state")
