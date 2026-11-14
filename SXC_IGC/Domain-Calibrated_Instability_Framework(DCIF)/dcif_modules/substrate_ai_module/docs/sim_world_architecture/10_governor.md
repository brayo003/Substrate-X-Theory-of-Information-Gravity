# 10. Governor

## Role

The Governor is a bounded control-policy subsystem. It consumes Transport Q observations, verifier reports, simulation diagnostics, and planner diagnostics. It never generates content, performs simulation, writes world state, or reinterprets a renderer output as truth.

## Decision pipeline

```text
ingest evidence → validate provenance/freshness → normalize confidence
→ apply hard safety/integrity rules → evaluate calibrated policy
→ choose disposition → emit auditable decision to Kernel
```

Inputs are revision-bound. Conflicting or stale evidence reduces decision confidence and may select conservative handling. Policies are declarative, versioned, scoped by world/domain/renderer, and tested in shadow mode before activation.

| Disposition | Meaning |
|---|---|
| Accept | mark a render proposal/presentation task accepted; no world mutation implied |
| Reject | stop the proposal and report why |
| Retry | request a bounded new renderer attempt with verification constraints |
| Slow down | reduce simulation/render cadence, increase observation density, or require checkpoints |
| Branch | create an explicitly labelled speculative presentation or simulation branch |
| Rollback | request Kernel restoration to a named checkpoint under strict authority/policy |

## Policy ordering

Hard integrity violations (wrong snapshot, missing provenance, unauthorized target) reject first. Then safety constraints, state consistency, identity/relationship failures, confidence coverage, Q trend and threshold bands, simulation invariant failures, and planner feasibility diagnostics are evaluated. Q is evidence of a transition condition; it cannot alone rewrite a world fact. Rollback is exceptional: it requires an auditable checkpoint, bounded impact scope, and a policy reason stronger than ordinary presentation mismatch. Every decision includes its input IDs, applied policy version, rationale, alternative dispositions considered, limits, and expiry.

## Public Interfaces

- Provides: disposition decisions, policy evaluation results, control commands to the Kernel, and auditable decision records.
- Consumes: Transport Q observations, verifier reports, simulation diagnostics, planner diagnostics, and checkpoint references.
- Emits: `accept`, `reject`, `retry`, `slow down`, `branch`, or `rollback` dispositions with rationale and expiry.

## Dependencies

- Depends on: versioned policy definitions, diagnostic inputs from Transport and Verifier, and Kernel checkpoint metadata.
- Does NOT depend on: renderer content generation, simulation state mutation, or planner execution authority.
- Must preserve: bounded control only, never content creation or truth rewriting.

## Acceptance Criteria

- The Governor never generates simulation or renderer content.
- Decision ordering is stable, versioned, and auditable.
- Rollback is only available through explicit checkpoint policy.
- Every disposition names the evidence and policy version that justified it.
