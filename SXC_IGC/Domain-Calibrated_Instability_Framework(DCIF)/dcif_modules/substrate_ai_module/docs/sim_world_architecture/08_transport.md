# 8. Transport Subsystem: Q

## Role and boundary

Q already exists mathematically and is not redesigned here. The Transport subsystem applies that observable to selected representations of state transitions. It is strictly read-only: it does not plan, store world or asset memory, render, validate actions, or mutate the world.

## Observation points

Q may be evaluated at: (1) pre-commit simulation proposals against their parent state, (2) committed state-to-state transitions, (3) render proposal versus target snapshot representations, (4) verifier correction/retry trajectories, and (5) configured subsystem diagnostic trajectories. Each observation names its domain and representation; Q values from unlike representations are never silently compared.

## Inputs and output

The Kernel supplies immutable paired representations, domain adapter ID, calibration profile, sampling/window metadata, and correlation IDs. A representation may be spatial field data, entity/component change vectors, semantic embeddings, scene graphs, or a robotics state estimate. The subsystem returns an immutable `QObservation`: Q value, regime classification, uncertainty, input revisions, sampling method, adapter/calibration versions, thresholds consulted, and diagnostic features. Raw sensitive inputs need not be retained by Q; its audit record holds stable references.

## Governor interaction and thresholds

The Governor consumes Q as one diagnostic signal—not a command and not a truth claim. The Transport subsystem can label values with configured warning/boundary/critical bands, but the Governor owns the action policy. Threshold profiles are domain-, representation-, and renderer-specific; they are versioned, calibrated from held-out data or declared expert policy, and may be shadow-evaluated before activation. AI-3's distinction matters here: retrospective Q and prospective Q must be labelled separately, with no claim that a post-output score predicted an event beforehand.

## Diagnostics

Transport emits per-observation data, trend/window summaries, missing-input notices, calibration coverage, uncertainty, and comparability warnings. It reports no “fix”; it only reports the observed transition regime and evidence. All Q diagnostics are reproducible from retained revision references and calibration metadata.

## Public Interfaces

- Provides: Q evaluation over paired representations, threshold classification, calibration binding, regime labeling, and diagnostic emission.
- Consumes: immutable state-transition pairs, domain adapter IDs, calibration profiles, sampling windows, and revision references.
- Emits: immutable `QObservation` records with value, regime, uncertainty, provenance, and threshold metadata.

## Dependencies

- Depends on: Kernel-supplied immutable inputs, representation adapters, calibration data, and audit metadata.
- Does NOT depend on: planner logic, memory ownership, rendering authority, or world mutation paths.
- Must preserve: read-only observation and strict comparability discipline across representation domains.

## Acceptance Criteria

- Q is evaluated only on explicitly supplied transitions or representations.
- Retrospective and prospective Q observations are labeled separately.
- Thresholds are versioned and calibrated per domain/representation.
- Q never stores memory, plans actions, renders output, or modifies state.
