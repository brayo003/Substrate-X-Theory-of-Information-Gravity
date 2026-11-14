# 12. Implementation Roadmap

Implementation begins only after this architecture set is accepted. Each layer is additive and may not bypass the ownership boundaries above.

| Layer | Deliverables and estimated structure | Dependencies | Tests | Acceptance criteria |
|---|---|---|---|---|
| 1. World Kernel | `kernel/{runtime,tick,store,scheduler,checkpoint,contracts}` | contracts/storage ports | tick order, atomic commit, replay | one revision authority; deterministic tick replay |
| 2. Entity System | `entities/{identity,components,relations,serialization,registry}` and `actions/{definitions,validation}` | Layer 1 | schema, lifecycle, relation integrity | all world objects register/serialize/version correctly |
| 3. Simulation Engine | `simulation/{clock,environment,physics,needs,movement,resources,economy,social}` | 1–2 | invariants, deterministic seeds, partition tests | offline world advances lawfully and reproducibly |
| 4. Memory | `memory/{world,agent,asset,temporal,relationship,knowledge,retrieval}` | 1–2, storage | provenance, permissions, migration | current truth, asset identity, and histories remain distinct |
| 5. Planner | `planner/{goals,task_graph,horizon,replan,diagnostics}` | 1–4 | interruption, stale preconditions, priority | plans propose legal candidate actions only |
| 6. Transport | `transport/{adapters,observation,calibration,diagnostics}` | 1–5 | formula adapter, no-write boundary, reproducibility | Q observations are revision-bound/read-only/calibrated |
| 7. Verifier | `verification/{extractors,object,identity,relations,scene,reports}` | 1–4, render contracts | fixture scenes, confidence, discrepancy localization | reports detect required mismatches with evidence |
| 8. Governor | `governor/{policy,decision,controls,audit}` | 1, 5–7 | policy precedence, rollback gates, shadow mode | only allowed dispositions; complete audit trail |
| 9. Renderer | `rendering/{contracts,adapters,orchestrator}` | 1, 4, 7–8 | adapter conformance, replaceability, no-memory | two renderer types pass same contract without authority leak |
| 10. Demo World | `examples/demo_world/{content,scenarios,profiles}` | all prior layers | end-to-end, recovery, scale smoke | persistent multi-entity world continues offline; rendered output is verified/governed |

## Layer gates

Before the next layer begins, publish its contracts, tests, observability hooks, and architecture-decision record. Load/scale validation starts in Layer 1 and expands at each layer; million-entity readiness is a partitioning and storage property, not a late renderer benchmark. No layer may introduce rendering logic into the Kernel, direct writes from simulation/planner/plugins, or Q-driven mutations.

## Final integration scenario

Start a world containing a person, home, door, refrigerator, food, cat, road, weather, and time schedule. The planner proposes a day; simulation advances entities while no user is connected; asset memory preserves a particular bottle's identity; a renderer produces a scene; verifier reports whether it matches the committed snapshot; Q observes the transition; Governor issues only a bounded disposition; Kernel records the decision and continues from authoritative history.

## Public Interfaces

- Provides: layer-by-layer deliverables, repository placement guidance, test gates, and the implementation sequence.
- Consumes: the frozen architecture contracts in documents 1 through 11.
- Emits: ordered implementation milestones with acceptance criteria for each layer.

## Dependencies

- Depends on: all prior architecture documents and their published interfaces.
- Does NOT depend on: implementation details that have not yet been contractually defined.
- Must preserve: build order, architectural boundaries, and incremental verifiability.

## Acceptance Criteria

- No implementation layer begins before its architecture contract and tests are defined.
- Each layer is verified before the next layer starts.
- The roadmap keeps the implementation aligned with the frozen contracts.
- The end-to-end demo still honors the same authority boundaries as the core architecture.
