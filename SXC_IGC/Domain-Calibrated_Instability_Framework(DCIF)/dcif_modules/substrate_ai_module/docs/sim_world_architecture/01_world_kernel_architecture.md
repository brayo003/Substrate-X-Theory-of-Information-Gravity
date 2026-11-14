# 1. World Kernel Architecture

## System boundary

SimWorld is an operating system for a continuously advancing, persistent world. A world may run with no connected human and may publish simultaneous representations through many renderers. The kernel manages truth; renderers produce representations of that truth.

## Subsystems and single responsibilities

| Subsystem | Sole responsibility | Owns |
|---|---|---|
| World Kernel | Commit legal, ordered world transitions | authoritative state revision and tick ledger |
| Entity System | Describe identifiable world participants | entity schemas, components, relationships |
| Simulation | Derive lawful changes through time | deterministic simulation work products |
| Planner | Propose intended future actions/events | plans and planning diagnostics |
| Memory | Retain and retrieve non-current information | memory records and indices |
| Asset Memory | Preserve identity-defining asset facts | canonical asset descriptors and references |
| Transport | Evaluate Q over supplied transition representations | immutable Q observations and calibration metadata |
| Verifier | Compare a proposed representation with a target snapshot | verification reports |
| Governor | Decide a control disposition from diagnostics | decisions, policy version, audit record |
| Renderer | Transform a render request into an output proposal | ephemeral renderer job state/output |

No subsystem writes another subsystem's owned state. The Kernel is the only committer of authoritative state; it may request work from all others.

## Core interfaces

All messages carry `world_id`, `tick_id`, `state_revision`, `correlation_id`, schema version, producer, and timestamp. Commands are idempotent; events are immutable.

| Producer → consumer | Contract |
|---|---|
| Kernel → Planner | `PlanningContext` → `PlanProposal` |
| Kernel → Simulation | `TickContext`, admitted actions → `TransitionProposal[]` |
| Kernel → Transport | previous/current or proposed state representations → `QObservation` |
| Kernel → Renderer | immutable `RenderSnapshot`, render profile → `RenderProposal` |
| Kernel → Verifier | render proposal + target snapshot → `VerificationReport` |
| Kernel → Governor | Q, verification, simulation, planner diagnostics → `GovernanceDecision` |
| Governor → Kernel | disposition only; never direct state mutation |

## Execution flow and feedback loop

```text
External intents / scheduled plans
             │
             ▼
Kernel admission ──► Simulation ──► proposed transition ──► Kernel commit
     ▲                    │                                      │
     │                    └──── diagnostics                       ▼
Planner ── plan proposals                              immutable render snapshot
                                                                  │
                      Q observes transition ◄────────────────────┤
                                                                  ▼
Renderer proposal ──► Verifier ──► Governor ──► accept/retry/branch/rollback
                                                │
                                                └── control commands to Kernel
```

The visual feedback loop never edits the simulation directly. A failed render can cause a retry or a branch of presentation work; it can request rollback only under an explicitly configured policy and only through Kernel-owned checkpoints.

## Update cycle

1. Open tick from an immutable world revision.
2. Admit external intents, scheduled actions, and due plan steps.
3. Validate rights, preconditions, resources, timing, and concurrency conflicts.
4. Run simulation phases to create transition proposals.
5. Resolve conflicts deterministically and commit a new authoritative revision atomically.
6. Record temporal history and publish change events.
7. Evaluate Q for configured committed and proposed transitions; Q records, never alters.
8. Generate snapshots for subscribed render profiles; render and verify asynchronously.
9. Governor evaluates diagnostics and sends bounded control decisions to the Kernel.
10. Kernel schedules approved control effects for a subsequent tick or presentation job.

## Dependency graph

```text
entities ─┬─► actions ─► kernel ◄─ simulation
memory ───┤                  │
planner ──┘                  ├─► storage
                             ├─► transport (read-only)
                             ├─► rendering ─► verification
                             └─► governor ◄──── diagnostics
networking and plugins are adapters around these contracts, never alternate authorities.

## Public Interfaces

- Provides: tick admission, action validation, deterministic commit, immutable snapshots, render job publication, diagnostic publication, and governance command intake.
- Consumes: planning proposals, simulation transition proposals, memory lookups, transport observations, verification reports, and renderer proposals as read-only inputs.
- Emits: authoritative revision changes, event records, snapshots, and bounded control outcomes.

## Dependencies

- Depends on: Entity System, Simulation Engine, Memory, Transport, Verifier, Governor, Storage, and narrow networking adapters.
- Does NOT depend on: renderer implementations, planner internals, or governor policy internals for its own truth-making authority.
- Must preserve: single-writer authority over committed world state and revision ordering.

## Acceptance Criteria

- Every committed mutation is atomic, revisioned, and audit-linked.
- Every tick is replayable with the same inputs and seeds.
- No renderer logic appears in the Kernel.
- No subsystem can bypass Kernel-owned admission, commit, or rollback rules.
```
