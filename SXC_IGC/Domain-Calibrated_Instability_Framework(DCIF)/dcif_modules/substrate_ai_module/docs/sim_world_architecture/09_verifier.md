# 9. Verifier

## Role

The renderer proposes reality; the Verifier determines how well that proposal matches the authoritative render snapshot. It does not decide acceptance, mutate the world, or generate replacement content.

## Verification pipeline

1. Bind the immutable target snapshot, render profile, asset versions, and camera/sensor scope.
2. Extract a normalized observation from renderer output: text claims, scene graph, object detections, poses, audio events, telemetry, or other renderer-specific evidence.
3. Verify object presence, attributes, counts, location/pose, state, and permitted occlusion.
4. Verify identity through canonical asset descriptors, stable markers, embeddings, and relational context.
5. Verify relationships: containment, ownership, contact, access, distance, adjacency, and temporal continuity.
6. Verify scene-level constraints: environment, lighting/time policy, causality, forbidden objects, and requested narrative facts.
7. Produce a report, never an alteration.

## Report contract

A `VerificationReport` contains target revision, output ID, extractor versions, per-claim status, evidence, confidence and uncertainty, severity, coverage, false-positive/false-negative risk, and structured discrepancy records. A discrepancy identifies expected fact, observed fact, affected entity/asset/relation, localization, and recommended correction *constraint*. A correction request tells a renderer what must be preserved or changed; it never supplies content or changes authoritative state.

Confidence is multi-level: extractor confidence, identity-match confidence, relation confidence, and aggregate coverage-weighted confidence. Unverifiable is distinct from failed. The Governor interprets these distinctions under policy.

## Public Interfaces

- Provides: state extraction, object verification, identity verification, relationship verification, scene verification, discrepancy reporting, correction requests, and confidence metrics.
- Consumes: immutable target snapshots, renderer outputs, asset descriptors, relation context, and modality-specific extraction hints.
- Emits: structured verification reports and bounded correction constraints only.

## Dependencies

- Depends on: Kernel snapshots, renderer proposal artifacts, canonical asset references, and versioned extractor logic.
- Does NOT depend on: simulation authority, governor disposition, or world mutation paths.
- Must preserve: evidence linkage, snapshot binding, and report immutability.

## Acceptance Criteria

- Object, identity, relationship, and scene verification are separated in the report.
- Unverifiable cases are distinct from mismatches.
- Every report points back to the target revision and evidence used.
- Verification can request correction constraints without generating replacement content.
