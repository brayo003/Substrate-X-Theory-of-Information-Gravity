# NEXT_EXPERIMENT_FROM_TLS.md
## Experimental Consequence of the TLS Substrate Analysis

**Date:** 2026-08-22
**Condition for writing this document:** A genuine forward prediction must survive.
**Status check:** From TLS_PREDICTION_TABLE.md and TLS_CONVENTIONAL_NULL_AUDIT.md:
  NO genuine forward prediction survives. The TLS route produces zero
  parameter-constrained, non-conventional, observable predictions.

---

## Result: No Experiment Authorized

The TLS substrate analysis (Parts I–IX) produced the following chain of failures:

1. Persistence mechanism fails (TLS_PERSISTENCE_AUDIT.md):
   Standard TLS hopping is a simple random walk — no directional memory.
   No physical process in amorphous SiO₂ generates spatial persistence.

2. τ_B and ξ_c remain free (GAP7_TLS_CLOSURE.md):
   Even if persistence were assumed, γ_rev is a new free parameter.
   τ_B and ξ_c cannot be predicted from TLS material parameters.

3. Chip-scale correlations are numerically zero (TLS_PREDICTION_TABLE.md):
   For physical γ_rev ~ Γ₂ ~ 10⁴–10⁷ s⁻¹: ξ_c ~ 1–100 nm.
   At qubit separation r ~ 1 mm: C_Γ(r) ≈ K₀(r/ξ_c) → 0 exponentially.
   Nothing is measurable.

4. All surviving observables are conventional (TLS_CONVENTIONAL_NULL_AUDIT.md):
   Lorentzian S(ω), Gaussian NM onset, K₀ shape, T-dependence are all
   reproduced by standard TLS bath or phonon bath.

5. The causal wavefront is inaccessible:
   c_TLS ~ 10⁻⁵ m/s → wavefront for r = 1 mm arrives at t ~ 100 s > T₂.

Therefore: NO experiment is designed in this document.

The instructions required a forward prediction before designing an experiment.
No such prediction exists from the TLS substrate.

---

## What Would Unlock This Document

An experiment becomes designable only if one of the following is achieved:

**Condition E1:** A physical mechanism for directional persistence in TLS is
  identified and justified from first principles. It must:
  - Derive γ_rev from material parameters (not a free parameter)
  - Produce ξ_c > 0.1 mm (chip-detectable scale)
  - Not reduce to conventional phonon or OU bath physics

**Condition E2:** A different physical substrate is found that satisfies C5 with
  c ≪ v_s and has chip-scale ξ_c derivable from material properties.
  (No such substrate was found in SUBSTRATE_CANDIDATE_AUDIT.md.)

**Condition E3:** Extension A (c = v_s) is formally adopted, in which case
  the experiment from EXPERIMENTAL_TARGET_REDESIGN.md (causal onset measurement)
  becomes the appropriate design — but it would not discriminate C2 from a
  phonon bath.

Until one of E1, E2, or E3 is explicitly satisfied and documented, no
QPU hardware experiment is designed or authorized.

---

## Note on Experiment-Free Tests

There ARE theory-only tests that can proceed without hardware:

T-Test 1: TLS spectral density measurement (condensed matter, not QPU).
  Measure S(ω) and spatial correlations in TLS-rich amorphous films directly
  using microwave spectroscopy. This characterizes the TLS bath and could
  determine whether ξ_c is nm-scale or larger.
  Platform: microwave resonator spectroscopy on amorphous SiO₂ films.
  Status: conventional condensed matter experiment — tests TLS physics,
  not SXC-IGC specifically.

T-Test 2: TLS correlation length measurement.
  Direct measurement of spatial correlations between coupled TLS sites using
  near-field microwave probing. Determines ξ_c directly.
  If ξ_c ~ nm: confirms TLS PRW cannot provide chip-scale correlations.
  If ξ_c ~ mm: anomalous — would require explanation.
  Status: LEGITIMATE pre-QPU experiment. Does not require IBM hardware.
  Does not test SXC-IGC but would resolve whether the TLS route is viable.

Neither test authorizes QPU use.
