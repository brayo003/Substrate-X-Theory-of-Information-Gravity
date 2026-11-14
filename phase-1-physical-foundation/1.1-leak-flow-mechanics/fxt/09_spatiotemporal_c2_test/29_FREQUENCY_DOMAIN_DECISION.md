# Document 29 — Frequency-Domain Decision and Verdict
## Phase 9 Final Report

**Date:** 2026-08-21

---

## Classification

**EXPERIMENT NON-DIAGNOSTIC**

The frequency-domain cross-spectral density experiment cannot distinguish C2 from
conventional OU colored-noise, for reasons proven mathematically (not merely empirically).

The C2 quantum layer status remains: **COMPATIBLE / UNDERDETERMINED**

---

## WHAT ACTUALLY HAPPENED

### 1. What physical quantity was measured
A synthetic simulation of repeated Ramsey phase measurements, Fourier-transformed to
produce power spectral densities (PSD) and cross-spectral densities (CSD) across 7
simulated qubits on a heavy-hex geometry.

### 2. What the hardware actually did
No hardware was used. Qiskit 2.3.1 StatevectorSampler (pure statevector simulation)
was the only available quantum execution environment. No QPU credentials exist for
any provider. The simulation used correlated OU noise processes, not a quantum circuit.

### 3. What was successfully extracted
- PSDs for 6 noise models (C2, OU, quasistatic, white, common-mode, independent)
- Cross-spectral coherences for all 21 qubit pairs
- Confirmed: C2 and OU are indistinguishable in every computed observable
- Confirmed: phase delay (12.6 mrad) is below shot-noise floor (11 mrad at 8192 shots)
- Confirmed: spatial coherence variation (0.6%) is undetectable at d/ξ_c = 0.006

### 4. What was not measurable
- Lorentzian corner frequency (f_max/f_c = 1.57 — insufficient dynamic range)
- Cross-spectral phase delay (SNR ~ 1.1)
- Spatial decay of coherence with distance (d << ξ_c)
- Any C2-specific prediction

### 5. Is this real hardware evidence or simulation?
**Simulation only.** All results are synthetic. No QPU data exists.

### 6. Did C2 gain evidence?
**No.** The simulation is self-consistent (generated data fits the generating model).
Self-consistency in simulation is not evidence.

### 7. Did C2 lose evidence?
**No.** The degeneracy finding is a mathematical statement about the model, not about
data quality. C2 is not falsified; the experiment simply has no discriminatory power.

### 8. Was the OU degeneracy broken?
**No.** The frequency-domain CSD is mathematically identical to the temporal coherence
function under Fourier transform. Moving to the frequency domain preserves the
C2/OU degeneracy exactly. This was proven algebraically (Doc 24) and confirmed
computationally (Doc 25).

### 9. Was c_C2 constrained?
**No.** d_c is not extractable from spatial coherence on a 7-qubit chip when ξ_c >> chip.

### 10. Does this change the project verdict?
**No.** The verdict was COMPATIBLE/UNDERDETERMINED. It remains so. The frequency-domain
experiment adds a new confirmed observation: the degeneracy extends to the spectral domain.

---

## CAN THE PROJECT RECOVER FROM THIS?

**Honest answer: Not with any currently available or foreseeable near-term resource.**

The C2 quantum layer requires a decisive test of:
```
c_C2 = d_c / τ_B
```
with `d_c` and `τ_B` measured independently under identical conditions.

This requires qubit separations comparable to ξ_c = 2·c·τ_B.

| If c_C2 = | And τ_B = | Then ξ_c = | Required chip size |
|-----------|-----------|------------|-------------------|
| 10⁴ m/s  | 5 µs      | 10 cm      | >> 10 cm |
| 10³ m/s  | 5 µs      | 1 cm       | >> 1 cm (achievable?) |
| 10² m/s  | 5 µs      | 1 mm       | >> 1 mm (achievable on current chips) |

**If C2 predicts c ~ 10² m/s** (substrate propagation ~100 m/s), then ξ_c ~ 1 mm
and the test becomes possible on a large current chip (e.g., 127-qubit IBM Eagle
with ~14mm chip dimensions). However:
- The C2 theory does not give a sharp numerical prediction for c
- Choosing c post-hoc to make the test feasible would be circular
- This requires a first-principles derivation of c from C2 parameters

**If C2 cannot predict c independently**, the joint test is underdetermined even if
executed: fitting c from the data is not falsification-relevant because c is a free parameter.

### What would actually help

1. **Derive c from C2 first principles.** If C2 gives a specific numerical prediction
   for c (not a free parameter), then a chip-geometry test becomes meaningful.

2. **Use a larger chip with IBM credentials.** 127-qubit or 433-qubit chips span ~14mm.
   If c ~ 700 m/s, ξ_c ~ 7mm — testable. But IBM credentials are unavailable.

3. **Higher-order cumulants.** C2 substrate noise is from discrete PRW particles —
   possibly non-Gaussian. Measuring bispectrum <S_ij(f1)·S_ij(f2)·S_ij(f3)> could
   distinguish from Gaussian OU. Requires ~10⁸ shots. Not practical near-term.

4. **Different physical platform.** NV centers in diamond allow ~10µm spacing
   with tunable geometry. If c ~ 10 m/s and τ_B ~ 10µs, ξ_c ~ 0.2mm — potentially
   testable. But NV center equipment is not available here.

**Current recommendation: Maintain FREEZE on the quantum branch.**

The quantum C2 layer has reached the limit of what can be tested without either:
(a) a first-principles numerical prediction of c_C2, or
(b) QPU access to a large chip, or
(c) a fundamentally different experimental platform

---

## Decision Tree Result

```
EXPERIMENT NON-DIAGNOSTIC
  ↓
C2 vs OU: mathematically identical (proven, confirmed)
  ↓
No C2-specific observable in frequency domain
  ↓
No hardware access to execute decisive test
  ↓
C2 COMPATIBLE / UNDERDETERMINED   (unchanged from Phase 8)
```

---

## Executive Summary

```
PROVIDER:                   None — no QPU credentials available
REAL QPU:                   NO — pure simulation only
EXPERIMENT:                 Frequency-domain cross-spectral density (simulated)
DIAGNOSTIC OR NON-DIAGNOSTIC: NON-DIAGNOSTIC
τ_B:                        Not extracted (Lorentzian fit failed; f_max/f_c=1.57)
SPATIAL/CROSS-SPECTRAL:     Coherence flat (d/ξ_c=0.006; no spatial variation detectable)
C2-SPECIFIC DISCRIMINATOR:  NONE FOUND
C2 vs NULL:                 Mathematically identical (C2 == OU in all observables)
c_C2 CONSTRAINED:           NO
FINAL VERDICT:              EXPERIMENT NON-DIAGNOSTIC
PROJECT STATUS:             C2 QUANTUM LAYER — COMPATIBLE / UNDERDETERMINED — FREEZE
```
