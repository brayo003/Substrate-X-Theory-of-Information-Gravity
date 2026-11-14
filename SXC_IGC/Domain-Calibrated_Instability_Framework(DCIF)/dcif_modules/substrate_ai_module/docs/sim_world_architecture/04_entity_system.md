# 4. Entity System

## Entity model

Everything in SimWorld is an entity: people, animals, buildings, trees, food, fire, water, doors, roads, and cities. An entity is a durable identity plus an extensible composition of components; it is not an inheritance tree of object behavior.

| Entity record | Meaning |
|---|---|
| `entity_id` | immutable, globally unique identity |
| `kind` | semantic class or archetype; never a source of behavior by itself |
| `component_refs` | versioned state components owned by the world |
| `capabilities` | legal action types it may initiate or receive |
| `relationship_refs` | typed links to other entities |
| `history_ref` | append-only temporal record pointer |
| `lifecycle` | created, active, dormant, destroyed/tombstoned |

## Components

Components are independently versioned state units such as transform, geometry, material identity, inventory, metabolism, health, needs, ownership, access control, weather exposure, market account, occupancy, navigation, and social profile. Systems declare the components they read and the effects they may propose. Components contain state, not orchestration. Component schemas support unknown-field preservation during migration.

## Action system and ownership

An action definition declares actor/target types, required capabilities, required components, preconditions, claims, effect vocabulary, failure modes, and observability requirements. The Kernel validates an action against authoritative state. Its responsible system proposes effects; the Kernel arbitrates and commits them.

Entity ownership is logical, not necessarily physical: a `World` owns existence and current state, a `SimulationSystem` owns evolution rules, an `AssetMemory` record owns canonical identity descriptors, and an `Agent` may hold rights but never direct write access. Relationships are first-class, typed, directional or symmetric, cardinality-constrained, versioned records rather than unvalidated IDs embedded in arbitrary components.

## Serialization and registration

Entity envelopes, components, actions, relations, and historical events use explicit schema versions and stable IDs. Serialization separates canonical simulation state from derived render state and external asset blobs. World registration validates identity uniqueness, required archetype components, referenced asset versions, relation integrity, and spawn permissions. De-registration produces a tombstone and preserves historical references; it does not erase history.

## Public Interfaces

- Provides: entity identity records, component registration, action capability declarations, relationship records, lifecycle transitions, and serialization envelopes.
- Consumes: world authority from the Kernel, asset identity from memory, and action definitions from the actions layer.
- Emits: registrable entity records, component deltas, relation updates, and versioned historical references.

## Dependencies

- Depends on: Kernel authority, asset memory, action schemas, and storage for versioned serialization.
- Does NOT depend on: renderer implementations, governor policy, or transport/Q outputs for entity truth.
- Must preserve: stable IDs, typed relations, and schema-versioned state.

## Acceptance Criteria

- Every entity has an immutable identity and a versioned state envelope.
- Components can be added, migrated, and serialized without losing canonical identity.
- Relationships remain typed, validated, and queryable.
- Registration and deregistration are reversible in history, but not by erasing records.
