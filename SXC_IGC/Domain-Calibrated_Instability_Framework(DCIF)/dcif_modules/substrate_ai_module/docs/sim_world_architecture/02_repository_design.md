# 2. Repository Design

Repository name: `sim_world/`. The tree is organized around architectural ownership, not technology choice. Public contracts live at each boundary; implementation-specific dependencies remain behind adapters.

```text
sim_world/
├── docs/
│   ├── architecture/          # normative architecture and ADRs
│   ├── contracts/             # versioned message/schema specifications
│   └── operations/            # deployment, observability, recovery runbooks
├── kernel/                    # authoritative tick, commit, scheduling, checkpoints
├── simulation/                # environment, physics, economy, social, time systems
├── planner/                   # goals, plans, task graphs, replanning policy
├── memory/                    # agent, temporal, relationship, knowledge retrieval
├── entities/                  # entity identity, components, relations, serialization
├── actions/                   # action definitions, preconditions, effects, arbitration
├── transport/                 # Q adapters, observation, calibration, diagnostics only
├── verification/              # extraction, matching, confidence, correction reports
├── rendering/                 # renderer-neutral contracts and renderer adapters
│   ├── llm/                   # text/story/dialogue adapter
│   ├── diffusion/             # image/video proposal adapter
│   ├── game_engine/           # real-time scene adapter
│   ├── robotics/              # physical actuation representation adapter
│   └── audio/                 # audio proposal adapter
├── networking/                # clients, sessions, replication, API edge adapters
├── storage/                   # event log, snapshots, blobs, indices, migrations
├── plugins/                   # isolated extension points and plugin manifests
├── observability/             # metrics, traces, audit projections, diagnostic sinks
├── tools/                     # non-runtime world import/export and operator tooling
├── examples/                  # declarative demo-world content and walkthroughs
└── tests/
    ├── contract/              # producer/consumer compatibility
    ├── unit/                  # pure subsystem tests
    ├── integration/           # cross-boundary tests
    ├── determinism/           # replay and reproducibility tests
    ├── scale/                 # million-entity partitions and load behavior
    ├── simulation/            # invariant/property scenarios
    ├── verification/          # known scene/output matching cases
    └── fixtures/              # immutable test worlds and renderer proposals
```

## Folder rules

`kernel/` may depend on contracts and narrow ports, but never renderer implementations. `simulation/` may read authoritative input and emit proposals, but cannot commit. `planner/` cannot depend on rendering or Q decisions. `transport/`, `verification/`, and `rendering/` are consumers of immutable snapshots and diagnostics. `storage/` supplies persistence ports, not domain policy. `networking/` cannot mutate state except by submitting kernel commands. `plugins/` extend declared ports only and run with explicitly granted capabilities.

## Scale structure

World state is partitioned by spatial shard and/or entity ownership domain. Each partition has a local ordered event stream; cross-partition actions use a Kernel transaction protocol with deterministic ordering. Snapshots are materialized projections, not the source of truth. Asset blobs use content addressing; entity state, history, and memory records use stable IDs and versioned schemas. No renderer payload is placed in the authoritative event stream.

## Public Interfaces

- Provides: a `sim_world/` package root, architecture docs, versioned contracts, runtime modules, and test suites at stable boundary paths.
- Consumes: shared schema definitions, storage abstractions, and architecture decisions as the source of truth for folder ownership.
- Exposes: module boundaries that map directly to kernel, simulation, planner, memory, entity, action, transport, verification, rendering, networking, storage, plugins, and tests responsibilities.

## Dependencies

- Depends on: the architecture contract set, versioned schema files, and storage/networking adapter layers.
- Does NOT depend on: a specific engine, framework, language runtime, renderer vendor, or deployment topology.
- Must preserve: one clear owner per folder and no cyclic ownership between runtime layers.

## Acceptance Criteria

- The tree can scale to millions of entities through partitioning and storage layout alone.
- Every major subsystem has a dedicated folder with a single responsibility.
- Contract and implementation files stay separated.
- Boundary tests can be added without changing folder ownership.
