# Substrate Memory Characterization

**Date:** 2026-11-13  
**Status:** Complete  
**Scope:** Distinguishability decay across field (s), velocity (v), and joint (s,v) observation modalities

---

## Overview

This document characterizes the substrate's ability to retain memory of distinct perturbation histories. Memory is operationalized as the distinguishability between two states that received spatially separated perturbations. Three observation modalities are tested: field-only, velocity-only, and joint field+velocity.

**Setup:**
- Grid: 30×30, dx=1m, dt=0.05s, tau=3.0, c=1.0 m/s
- Two perturbation histories: Gaussian bump at (15,15) vs Gaussian bump at (35,35)
- Perturbation: amplitude=3, width=2m, applied at t=0 to otherwise identical ICs
- Distinguishability metric: normalized L2 distance = ‖state_A − state_B‖ / (‖state_A‖ + ‖state_B‖)/2

---

## Experiment A — Field-Only (s) Observation

The two histories differ only in the spatial location of the initial Gaussian perturbation. We track the normalized L2 distance in the s-field over time.

| Time (units) | Normalized L2 distance (s-space) | Notes                        |
|--------------|----------------------------------|------------------------------|
| 0.0          | 0.277                            | Initial separation            |
| ~4.55        | ~0.139 (half-life point)         | Half of initial distance      |
| 15.0         | 0.055                            | Still distinguishable         |

**Key results:**
- Initial distance: **0.277**
- Half-life: **4.55 time units**
- Final distance at t=15: **0.055** (~20% of initial)

The two states remain distinguishable throughout the simulation window (0–15 time units), though distinguishability decays steadily. Field memory is **genuine but time-limited** — the spatial signature of the perturbation decays as the field relaxes toward its equilibrium.

The half-life of ~4.5 time units is set by the damping rate of the dominant contributing modes. For tau=3, propagating modes decay at γ = 1/(2τ) = 1/6 per time unit; the energy half-life is ln(2)/γ ≈ 4.16 time units, consistent with the observed 4.55.

---

## Experiment B — Velocity-Only (v) Observation

We track the normalized L2 distance in the velocity field (v = ∂s/∂t) between the two histories.

| Time (units) | Normalized L2 distance (v-space) | C_spectral difference | Notes                            |
|--------------|----------------------------------|-----------------------|----------------------------------|
| 0 – 10       | **1.414** (constant)             | **0.000**             | Maximum distance, no convergence |
| 10 – 15      | Slowly decreasing from 1.414     | 0.000                 | Very gradual                     |

**Key results:**
- Velocity distance is **constant at 1.414** for the first 10 time units
- Half-life of velocity distinguishability: **> 15 time units** (not observed within simulation window)
- C_spectral difference: **0.000 throughout**

The constant L2 distance of 1.414 is the maximum possible normalized distance (achieved when two unit-norm vectors point in opposite directions in the high-dimensional velocity space). This indicates the velocity fields of the two histories remain orthogonal — they carry entirely different phase information — for an extended period.

**Critical finding:** The global C_spectral observable shows zero difference between the two histories at all times. C_spectral encodes the global fraction of power in propagating vs overdamped modes — a spectral property that is identical for two Gaussian perturbations of the same amplitude and width, regardless of spatial location. **C_spectral cannot distinguish spatial location of a perturbation.**

---

## Experiment C — Joint (s, v) Observation

The joint state vector concatenates the s-field and v-field: `[s, v]`. Normalized L2 distance is computed over this extended state space.

| Time (units) | Joint normalized L2 distance | Notes                               |
|--------------|------------------------------|-------------------------------------|
| 0.0          | (s and v combined)           | Maximum separation in joint space   |
| ~5.05        | Half-life point              | Marginally longer than s-only       |
| 15.0         | Partial decay                | Remains distinguishable             |

**Key results:**
- Joint half-life: **5.05 time units**
- Improvement over s-only half-life (4.55): **+0.50 time units (11% improvement)**
- The velocity contribution adds marginal benefit to distinguishability

The marginal improvement from including velocity is explained by the fact that velocity carries phase information from oscillating propagating modes. These oscillations maintain the velocity distance at 1.414 for t<10, so the joint state benefits slightly from this persistence — but only after the s-distance has decayed significantly.

---

## Summary of Modality Comparison

| Modality    | Initial distance | Half-life (time units) | t=15 distance | C_diff distinguishable? |
|-------------|-----------------|------------------------|---------------|-------------------------|
| s only      | 0.277           | 4.55                   | 0.055         | N/A                     |
| v only      | 1.414           | > 15                   | ~1.4          | N/A                     |
| s + v joint | (combined)      | 5.05                   | (combined)    | N/A                     |
| C_spectral  | 0.000           | —                      | 0.000         | **NO**                  |

---

## Key Findings and Implications

### Finding 1 — C_spectral cannot distinguish spatial location
The global C_spectral observable produces **zero difference** between two histories that differ only in spatial location of an equal-amplitude perturbation. This is a **fundamental limitation** of the scalar spectral observable: it encodes global spectral character, not spatial structure. Any agent observing only C_spectral cannot distinguish where in the substrate a perturbation occurred.

### Finding 2 — Field memory decays at the modal damping rate
The s-field carries spatial information with a half-life of ~4.5 time units, consistent with the propagating mode decay rate γ = 1/(2τ) for tau=3. Memory is genuine — the perturbation history is recoverable from the spatial field — but is bounded in time.

### Finding 3 — Velocity memory is long-lived but spatially opaque
The velocity field maintains maximum distinguishability (L2 = 1.414) for t < 10 time units, indicating persistent phase information. However, this information is encoded in the phase structure of individual modes, not in any scalar summary. An agent with access to the full velocity field can distinguish histories for longer, but this requires spatial field access.

### Finding 4 — Joint observation provides marginal benefit
The joint (s,v) half-life (5.05) is only marginally longer than s-only (4.55). For practical purposes, s-field observation captures nearly all accessible memory at the timescales considered.

---

## Limitations

1. All results are for tau=3.0 specifically. Memory half-life scales approximately as τ — shorter tau reduces memory lifetime.
2. The two perturbations are spatially well-separated (20m apart on a 30m grid equivalent). For closer perturbations, overlap of Gaussian tails would reduce initial distance and accelerate convergence.
3. These experiments use identical perturbation amplitudes and widths. Amplitude differences would make C_spectral distinguishable (C_spectral encodes amplitude globally); spatial separation alone is invisible to C_spectral.
