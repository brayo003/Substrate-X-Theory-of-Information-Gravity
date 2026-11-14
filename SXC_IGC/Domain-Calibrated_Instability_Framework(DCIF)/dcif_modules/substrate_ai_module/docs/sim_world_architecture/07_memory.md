# 7. Memory

Memory stores information with different ownership and retention semantics. It is not a substitute for authoritative current state.

| Memory kind | Owner and contents | Lifetime / retrieval |
|---|---|---|
| Persistent World | Kernel-owned event stream and snapshots of committed truth | permanent/retention-policy; revision and entity queries |
| Agent Memory | agent-owned perceptions, beliefs, experiences, preferences | agent lifecycle; permission-checked episodic/semantic retrieval |
| Asset Memory | canonical visual/physical identity of a specific asset | asset lifecycle; ID, attribute, embedding, and provenance lookup |
| Temporal Memory | append-only historical sequences and causal timelines | retention tiers; time/range/causation queries |
| Relationship Memory | relationship facts, interactions, trust/obligation history | relation lifecycle; pair, graph, and time queries |
| Knowledge Memory | sourced, versioned facts/rules available to agents/systems | provenance-aware semantic and structured retrieval |

Persistent World answers “what is true now?” Asset Memory answers “which bottle is this: green glass, cracked, 600 ml, with this canonical identity?” Temporal and relationship history preserve past truth without overwriting current state. Agent memory may be incomplete or false from the agent's perspective and must never be mistaken for world truth.

## Storage, versioning, and serialization

Every record includes stable ID, owner, schema version, validity interval, creation revision, provenance, access policy, and integrity hash. Event logs are append-only; mutable read models are rebuildable projections. Large binary assets and embeddings are content-addressed with metadata references in records. Retrieval returns records plus version/provenance and confidence where applicable. Schema migration is additive first; incompatible changes require adapters and explicit archival policy. Memory writes are commands routed through the owning subsystem and causally linked to Kernel events where they claim world facts.

## Public Interfaces

- Provides: persistent world history lookup, agent memory storage and retrieval, asset identity lookup, temporal query, relationship query, and knowledge retrieval APIs.
- Consumes: owner-scoped write commands, access policies, stable IDs, and provenance metadata.
- Emits: versioned records, indexed references, query results, and provenance/confidence metadata where applicable.

## Dependencies

- Depends on: Kernel-owned truth, Storage, entity and asset identifiers, and permission or access control policy.
- Does NOT depend on: renderer authority, simulation execution timing, or governor decisions for memory truth.
- Must preserve: distinct ownership for world, agent, asset, temporal, relationship, and knowledge memory.

## Acceptance Criteria

- Persistent world, agent memory, asset memory, temporal memory, relationship memory, and knowledge memory remain separately owned.
- Retrieval returns records with version and provenance information.
- Memory can preserve history without confusing it with current truth.
- Permission and lifecycle rules prevent unauthorized writes or accidental overwrites.
