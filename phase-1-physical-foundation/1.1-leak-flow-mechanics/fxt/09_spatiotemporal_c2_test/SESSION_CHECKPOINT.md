# SESSION CHECKPOINT
## Phase 9 — Spatiotemporal + Frequency-Domain + Observable Discrimination Audit

**Date:** 2026-08-21 (updated — Phase 9c complete)  
**Hard verdict:** C2/OU IDENTIFIABILITY FAILURE — THEORY REQUIRES REVISION

---

## Phase 9c — Observable Discrimination Audit

**Document:** 30_OBSERVABLE_DISCRIMINATION_AUDIT.md  
**Script:** scripts/p25_discrimination_test.py  
**Data:** outputs/data/discrimination_results.json

### Summary

11 candidate observables tested analytically and numerically. Result is definitive.

| Observable | C2 == OU? | Discriminating? |
|------------|-----------|----------------|
| Ramsey C(t) | YES | NO |
| Single-qubit PSD | YES | NO |
| DD filter responses (all) | YES | NO |
| Multi-time correlations | YES | NO |
| Cross-spectral density (d≪ξ_c) | YES | NO |
| Spectral phase delay | NO | IMPRACTICAL (SNR~1) |
| K₀ vs exp spatial shape | NO | BLOCKED (needs ξ_c~chip) |
| ξ_c/τ_B = const(T) | NO | BLOCKED (needs T-variable) |
| Non-Gaussianity κ_3 | NO | CONDITIONAL (N_part unknown) |
| Fourth cumulant κ_4 | NO | IMPRACTICAL (10¹² shots) |
| Non-Markovian R(t1,t2) | YES | NO |

**Verdict: C — C2/OU IDENTIFIABILITY FAILURE**

The C2 quantum layer generates an OU process at the observable level.
This is a mathematical consequence of the PRW structure, not a hardware limitation.

### Root cause

```
c_C2 = FREE PARAMETER (not independently derived in C2 theory)
```

The one genuine discriminator (K₀ vs exp spatial shape, or joint ξ_c = 2cτ_B test)
requires c to be independently predicted. Without this, all tests are circular.

### What needs to happen before re-opening the experimental branch

1. **Derive c from C2 first principles** — theoretical task, not experimental
2. If c ~ 10²–10³ m/s: ξ_c ~ mm-cm → testable on large chip with QPU access
3. If c cannot be derived: quantum layer is permanently non-falsifiable in Ramsey channel

### QPU justified? NO

No experiment on any available or foreseeable platform will add discriminatory
information until c is independently predicted.

---

---

## Phase 9b — Frequency-Domain Cross-Spectral Experiment

**New documents added:** 24, 25, 26, 27, 28, 29

### Summary of new findings

| Finding | Result |
|---------|--------|
| Provider audit | No QPU access. Qiskit 2.3.1 StatevectorSampler only |
| Frequency-domain CSD diagnostic? | **NO — mathematically identical to OU** |
| Lorentzian f_c extractable? | NO — f_max/f_c = 1.57 (insufficient range) |
| Phase delay detectable? | NO — 12.6 mrad at SNR~1.1 |
| Spatial coherence variation? | NO — d/ξ_c = 0.006 |
| New experiment type changes verdict? | **NO — EXPERIMENT NON-DIAGNOSTIC** |

### Hard verdict remains: COMPATIBLE / UNDERDETERMINED

The frequency-domain experiment was mathematically proven non-diagnostic before
execution (Doc 24) and computationally confirmed non-diagnostic after execution (Doc 25).

No new evidence was produced for or against C2.

---

## Hard Verdict

```
C2 QUANTUM LAYER STATUS: COMPATIBLE / UNDERDETERMINED
```

Not: FALSIFIED  
Not: DISFAVORED  
Not: JOINTLY SUPPORTED  
Not: TECHNICALLY INCONCLUSIVE (the experiment ran; the geometry is the blocker)

---

## What Was Done This Session

All 6 scripts executed successfully. All 8 output documents produced. All figures generated.

| Script | Status | Key output |
|--------|--------|------------|
| p17_ramsey_sim.py | ✓ PASS | 7-qubit synthetic Ramsey data, NMP=1.0–2.4 |
| p18_ramsey_fit.py | ✓ PASS | τ_B fitted 7/7 qubits, CV=0.10, bias=+7% |
| p19_spatial_correlator.py | ✓ PASS | d_c NOT measurable; null model preferred |
| p20_joint_c2_test.py | ✓ PASS | c_C2 off by 4700×; 1923% uncertainty |
| p21_null_tests.py | ✓ PASS | OU ≡ C2-exact; common-mode explains all |
| p22_synthetic_recovery.py | ✓ PASS | Recovery 0% at c=10⁴ m/s, NMP~1.6 |

---

## Evidence Summary

### Confirmed

- τ_B is measurable in simulation at NMP ~ 1–2 (NM_PREDICTION_AUDIT remains valid)
- Non-Markovian Ramsey decay is present and significant (ΔBIC > 6000 vs exponential)
- C2-exact model wins by BIC over all other temporal models (simulation self-consistency)
- τ_B recovered with bias < 7%, CV = 0.10 — within pre-registered thresholds

### Not confirmed

- d_c is not extractable on a 7-qubit chip (ξ_c = 100,000 µm >> chip = 632 µm)
- The joint test c_C2 = d_c/τ_B cannot be completed
- Spatial signal is dominated by common-mode; null model preferred
- C2 is structurally indistinguishable from OU on all temporal observables

### Not falsified

- C2 spatial prediction is not tested — the geometry prevents the test
- C2 temporal prediction is compatible with data (but so is OU)
- No negative result has been obtained against C2 specifically

---

## The One Remaining Test

The decisive unresolved question is:

```
c_C2 = d_c / τ_B    (same chip, same conditions)
```

**This requires:** QPU with qubit separations spanning d ~ ξ_c, i.e., distances of order centimeters — unavailable on current superconducting chips.

**OR:** A reformulated prediction with smaller ξ_c (requires either c << 10⁴ m/s or τ_B << µs).

**OR:** Frequency-domain cross-correlation spectroscopy (avoids the spatial flatness problem by measuring the noise spectrum rather than the Ramsey shape).

---

## Project Decision

**FREEZE maintained.**

Rationale:
1. Further Ramsey experiments of the same type add no discriminatory information
2. The spatial test is geometrically blocked on all current QPUs
3. The structural OU ≡ C2 degeneracy prevents temporal-only confirmation
4. The hypothesis is not falsified and remains coherent

**Condition for re-opening:**  
A platform providing either (a) qubit spacings ≥ 1 cm, or (b) cross-noise frequency spectroscopy with resolved Lorentzian peak at f = 1/(2πτ_B), or (c) a C2 prediction with ξ_c < 1 mm.

---

## Files Produced This Session

```
fxt/09_spatiotemporal_c2_test/
├── 17_EXPERIMENT_DESIGN.md
├── 18_RAMSEY_RESULTS_SIM.md
├── 19_SPATIAL_RESULTS_SIM.md
├── 20_JOINT_C2_TEST_SIM.md
├── 21_CONVENTIONAL_NULL_TESTS_SIM.md
├── 22_SYNTHETIC_RECOVERY_SIM.md
├── 23_DECISION_AND_VERDICT.md
├── SESSION_CHECKPOINT.md  ← this file
├── scripts/
│   ├── p17_ramsey_sim.py
│   ├── p18_ramsey_fit.py
│   ├── p19_spatial_correlator.py
│   ├── p20_joint_c2_test.py
│   ├── p21_null_tests.py
│   └── p22_synthetic_recovery.py
└── outputs/
    ├── data/
    │   ├── ramsey_sim.npz
    │   ├── ramsey_sim_meta.json
    │   ├── ramsey_fit_results.npz
    │   ├── ramsey_fit_results.json
    │   ├── spatial_results.npz
    │   ├── spatial_results.json
    │   ├── joint_c2_results.json
    │   ├── null_test_results.json
    │   └── synthetic_recovery_results.json
    └── figures/
        ├── fig_ramsey_traces.png
        ├── fig_tau_b_distribution.png
        ├── fig_spatial_corr_matrix.png
        ├── fig_spatial_corr_vs_dist.png
        ├── fig_c2_joint_test.png
        ├── fig_null_model_comparison.png
        └── fig_synthetic_recovery.png
```

---

## Phase 9d — c Derivation Audit

**Document:** 31_C_DERIVATION_AUDIT.md  
**Script:** scripts/p26_c_derivation_audit.py  
**Classification:** C_PARAMETER_DEPENDENT

| Finding | Result |
|---------|--------|
| c = v (PRW speed) | ASSUMED [A-PRW1] — not derived |
| c ≤ v_s = a√(K/m) | DERIVED from FPUT + C3 constraint |
| c = v_s (saturation) | Requires extra postulate — NOT in current theory |
| Previously assumed c = 10⁴ m/s | NO derivation; VIOLATES C3 (> v_s(Si) = 6000 m/s) |
| ξ_c at c = v_s = 6000 m/s, τ_B=5µs | 6.0 cm >> chip (632 µm) |
| c required for resolvable test | < 100 m/s — physically implausible |
| QPU experiment justified | NO |

To upgrade from C_PARAMETER_DEPENDENT → C_PREDICTED: prove from FPUT-3 that PRW speed = v_s (currently open problem).


---

## Phase 9e — c First-Principles Derivation + Variance Audit

**Documents:** 32, 33, 34  
**Scripts:** p27_c_first_principles.py, p28_variance_audit.py  
**Classification:** C_CONDITIONALLY_PREDICTED (upgraded from C_PARAMETER_DEPENDENT)

### Key revision

Previous audit (31) concluded c is a free parameter (C_PARAMETER_DEPENDENT).

**This audit revises that conclusion.**

Source: `projection_classification_audit.md`, P1(a) governing equations:

```
∂ₜn⁺ + vₛ ∂ₓn⁺ = −γ(n⁺ − n⁻)
```

The P1 transport speed IS vₛ. The ± split comes from the sign of ∂ωₖ/∂k. The long-wavelength group velocity = vₛ = a√(K/m). Therefore:

```
c = v_PRW = vₛ = a√(K/m)   DERIVED (conditional on k→0 coarse-graining)
```

For Si: c = 6000 m/s. The k→0 condition is standard and already embedded in the P1 construction — not an additional postulate.

### ξ_c consequence

| τ_B | ξ_c | Eagle d/ξ_c | Test accessible? |
|-----|-----|-------------|-----------------|
| 0.5 µs | 0.6 cm | 0.023 | NO |
| 1.0 µs | 1.2 cm | 0.12 | MARGINAL |
| 1.2 µs | 1.44 cm | 1.0 | YES (Eagle) |
| 5.0 µs | 6.0 cm | 0.0023 | NO |

At τ_B ~ 1.2 µs: ξ_c ~ 14mm = Eagle chip size. **K₀ vs exp shape test becomes accessible on IBM Eagle (127-qubit).**

### c = 10⁴ m/s invalidated

No derivation. Violates C3 (> v_s(Si) = 6000 m/s). Must be removed from predictions.

### Current hard status

```
Theoretical:   C_CONDITIONALLY_PREDICTED
               c = a√(K/m) derived from FPUT acoustic branch (P1)
Experimental:  FROZEN — QPU access required (Eagle-scale)
Decisive test: K₀(r/ξ_c) vs exp(−r/ξ_c) on 127-qubit chip at τ_B ~ 1 µs
Condition:     IBM Eagle credentials or equivalent
```

### Variance audit result

- Steps 1–2 of variance chain: DERIVED (no CA-3)
- Step 3 (Γφ coupling): ASSUMED [CA-3]
- Γφ ∝ ω_rot²: confirmed, not C2-specific
- Variance does not constrain c
- No independent test from variance currently established


---

## PHASE 9e — C / PRW SPEED + VARIANCE DERIVATION AUDIT

**Date:** 2026-08-21
**Scripts:** p27_c_prw_speed_audit.py, p28_correlation_length_audit.py, p29_variance_coupling_audit.py
**Documents:** 32_C_PRW_SPEED_DERIVATION_AUDIT.md, 33_C_CORRELATION_LENGTH_CONSEQUENCE.md, 34_VARIANCE_TO_C_DECOHERENCE_AUDIT.md

### What is genuinely derived

| Result | Status | Basis |
|--------|--------|-------|
| v_s = a√(K/m) = 6000 m/s | DERIVED | Long-wavelength limit of FPUT dispersion |
| ωₖ = 2√(K/m)\|sin(πk/N)\| | DERIVED | Fourier diagonalization of harmonic chain |
| nₖ = const (actions conserved) | DERIVED | Harmonic chain integrability |
| C3: signal speed ≤ v_s | DERIVED | C3 admissibility constraint + FPUT acoustics |
| FPUT-3: evolution is telegrapher type | DERIVED | C1 locality + action-variable uniqueness |
| τ_B = 1/(2γ) | DERIVED | PRW relaxation algebra |
| ξ_c = 2cτ_B | DERIVED | given c |
| <\|δJ\|²> = (2/3)s₀²ω_rot²r² | DERIVED | Isotropic angular average, no CA-3 needed |

### What is conditional

| Result | Condition | Label |
|--------|-----------|-------|
| c = v_s = 6000 m/s | [PHON]: PRW particles identified with FPUT acoustic phonons | CONDITIONALLY DERIVED |
| v_PRW = v_s | Same [PHON] condition | CONDITIONALLY DERIVED |
| ξ_c (numerical value) | Requires c via [PHON] | CONDITIONALLY DERIVED |

**[PHON] is:** physically natural, implicitly used throughout the project, but NOT stated as an
explicit postulate and NOT proved as a theorem within the existing files.

### What is assumed

| Assumption | Label |
|------------|-------|
| FPUT Hamiltonian as substrate model | ASSUMED [A-FPUT1] |
| n± defined as right/left phonon densities at speed v_s | ASSUMED / DEFINITIONAL |
| Γφ ∝ <\|δJ\|²> | ASSUMED [CA-3] — constitutive postulate, not derived |

### Whether c is numerically predicted

**c = 6000 m/s — CONDITIONALLY PREDICTED** under [PHON].

Without [PHON] explicitly accepted: c ∈ (0, 6000] m/s (C3 upper bound only) → C_PARAMETER_DEPENDENT.

FPUT-3 does NOT specify c. C3 gives only an inequality. The equality c = v_s enters through the P1
phonon construction, which embeds v_s by definition of n±.

### Whether ξ_c is numerically predicted

**CONDITIONALLY PREDICTED** under [PHON]:

- At τ_B = 5 µs (measured on Tuna-17): ξ_c = 6.0 cm — blocked on all current chips
- At τ_B = 1.17 µs (Eagle-matched): ξ_c = 1.4 cm — conditionally accessible on Eagle

τ_B = 1.17 µs has NOT been measured on real hardware. Choosing it to make the experiment
feasible would be circular. The measured τ_B ~ 5 µs gives ξ_c >> chip size → blocked.

### Whether the K₀ spatial discriminator is experimentally actionable

**CONDITIONALLY OPEN** — three conditions required simultaneously:

1. [PHON] accepted as a named postulate
2. τ_B ~ 1.2 µs confirmed on real hardware (not assumed)
3. Eagle-class chip access obtained

Currently conditions (2) and (3) are unmet. The branch is **BLOCKED in practice**.

### Whether the variance provides an independent constraint on c

**NO.** The complete variance chain

    δJ → <|δJ|²> → [CA-3] → Γφ = k_rot·ω_rot²

contains no c, v_s, or ξ_c. The variance parameters are {s₀, ω_rot, r}.
k_rot contains τ_B but not c. The variance provides no independent constraint on c.

### Whether CA-3 remains an unresolved constitutive postulate

**YES.** CA-3 (Γφ ∝ <|δJ|²>) has not been derived from the C2 Lagrangian, from a
Lindblad master equation, or from any first-principles calculation in the project files.
CA-3 has no hidden dependence on c, v_s, τ_B, or ξ_c.

### Whether QPU access is justified

**NO.** The discriminating observable (K₀ spatial shape) requires ξ_c ~ chip span, which
requires τ_B ~ 1.2 µs on Eagle hardware. Neither condition is currently met. No QPU
experiment will add discriminatory information until both are confirmed independently.

### Final verdict

```
B. C_CONDITIONALLY_PREDICTED

c = v_s = a√(K/m) ≈ 6000 m/s (Si substrate)
Condition: [PHON] — PRW particles identified with FPUT acoustic phonons
This condition is implicit in P1 but is not a proved theorem.
```

