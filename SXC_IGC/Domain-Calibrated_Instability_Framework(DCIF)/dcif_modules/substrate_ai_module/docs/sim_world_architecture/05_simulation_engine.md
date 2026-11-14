# 5. Simulation Engine

## Role

The Simulation Engine advances the world whether or not anyone is connected. It owns no canonical state store; each domain system computes lawful transition proposals for the Kernel to commit.

## Tick pipeline and priority

```text
clock/calendar → weather/environment → physics/hazards → resources
→ needs/health → movement/navigation → economy → social interaction
→ goal progress → cleanup/derived diagnostics
```

This ordering makes causes available before dependent effects: weather affects hazards and resources; those affect needs and movement; movement changes co-location; co-location enables economy and social interactions; resulting facts determine goal progress. Each system may declare same-tick inputs or next-tick-only effects to avoid hidden cycles.

## Domain systems

- Environment: terrain, day/night, season, ecology, weather, fire, water.
- Physics: motion, collision, structural change, heat and hazard propagation.
- Resources: production, consumption, inventories, depletion, regeneration.
- Needs and health: biological/operational state, damage, recovery, satisfaction.
- Navigation and movement: route feasibility, occupancy, arrival, access.
- Economy: offers, exchange, prices, labor, accounts, supply chains.
- Social: perception, communication, relationship effects, institutions.
- Goals: evaluates plan progress and generates status—not plans.
- Time: calendar, timers, schedules, and catch-up policies.

## Dependency and parallelism

The scheduler builds a DAG from declared reads, writes, spatial partitions, and action claims. Independent shards and non-overlapping entity sets run in parallel. Within a phase, systems may execute concurrently only when their proposed writes commute or are partition-isolated. Cross-shard actions use deterministic barriers. Randomness is explicit, seeded per world/tick/system/entity so replay yields the same outcome. The engine never uses renderer completion as a simulation dependency.

## Public Interfaces

- Provides: tick-phase execution, domain system scheduling, transition proposal generation, dependency graph construction, and per-phase diagnostics.
- Consumes: authoritative kernel views, validated action claims, entity/component state, and memory or planner signals that affect simulation inputs.
- Emits: lawful transition proposals, subsystem diagnostics, and deterministic replay metadata.

## Dependencies

- Depends on: Kernel, Entity System, action claims, storage-backed authoritative reads, and deterministic randomness primitives.
- Does NOT depend on: renderer completion, verifier approval, or governor disposition as inputs to physical simulation.
- Must preserve: causal ordering, phase barriers, and commutative parallel execution where possible.

## Acceptance Criteria

- The world advances when no human is connected.
- The same tick input set produces the same output under the same seeds.
- Independent shards can run in parallel without hidden write conflicts.
- No renderer or verification result can alter simulation truth.
