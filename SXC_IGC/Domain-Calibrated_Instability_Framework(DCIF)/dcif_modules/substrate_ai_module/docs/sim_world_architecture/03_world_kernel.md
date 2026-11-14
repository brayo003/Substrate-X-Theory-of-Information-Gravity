# 3. World Kernel

## Role

The World Kernel is the simulation operating system. It owns the authoritative event log, revision sequence, tick clock, action admission, deterministic conflict resolution, checkpoint policy, and module scheduling. It contains no rendering logic and has no renderer-specific dependencies.

## Conceptual core classes

| Class | Responsibility |
|---|---|
| `WorldRuntime` | lifecycle of one world and its module registry |
| `WorldStateStore` | read current revision and commit atomically |
| `TickScheduler` | issue ordered ticks and phase barriers |
| `ActionDispatcher` | route admitted actions to the responsible simulation system |
| `ActionValidator` | validate schema, authority, preconditions, and resource claims |
| `ConflictResolver` | choose a deterministic outcome for incompatible proposals |
| `SnapshotService` | create immutable point-in-time read models |
| `CheckpointManager` | create and restore auditable rollback points |
| `ModulePort` | contract boundary for simulation, planner, memory, Q, verifier, governor, renderer |

## Tick lifecycle

```text
OPEN → INGEST → VALIDATE → PLAN-ADMIT → SIMULATE → RESOLVE
     → COMMIT → PUBLISH → OBSERVE → PRESENT → GOVERN → CLOSE
```

- `OPEN`: bind the parent revision and deterministic clock.
- `INGEST`: collect client intents, system events, and due plan steps.
- `VALIDATE`: reject invalid actions before simulation.
- `PLAN-ADMIT`: turn eligible planned steps into normal actions; plans get no special authority.
- `SIMULATE`: systems emit transition proposals from the same read revision.
- `RESOLVE`: settle conflicts by declared precedence, not execution timing.
- `COMMIT`: apply the accepted batch atomically, assign revision, append events.
- `PUBLISH`: update projections and notify subscribers.
- `OBSERVE`: request diagnostics, including Q, against immutable inputs.
- `PRESENT`: create optional render jobs from committed snapshots.
- `GOVERN`: process governance outcomes as bounded commands for future work.
- `CLOSE`: persist tick audit and release resources.

## Message flow

Calls into the Kernel are commands; results leaving it are events or read-only snapshots. A subsystem may return a proposal, report, or decision, never a mutable world object. The Kernel records causal links from a render proposal and verification report back to the snapshot revision, entity IDs, asset versions, plan ID, action IDs, and Q calibration version.

## Ownership and mutation rules

1. Only `WorldStateStore` commits authoritative entity/component changes.
2. Every mutation is an action effect carried by an event with prior revision and causation metadata.
3. Simulation systems operate from an immutable tick view and produce proposals; they never partially mutate shared state.
4. A state read is revision-scoped. Stale commands are rejected, rebased, or made conditional by explicit policy.
5. Rollback restores a checkpoint through a new auditable control event; history is not erased.
6. Renderer, verifier, Q, and governor outputs are external evidence. They cannot silently rewrite entity state.
