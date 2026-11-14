# TLS_EXTENSION_GATE.md
## TLS Extension — Frozen Decision Gate

**Date:** 2026-08-22
**Based on:** TLS_SUBSTRATE_DERIVATION.md, TLS_PERSISTENCE_AUDIT.md,
  GAP7_TLS_CLOSURE.md, TLS_CONVENTIONAL_NULL_AUDIT.md,
  TLS_PREDICTION_TABLE.md, NEXT_EXPERIMENT_FROM_TLS.md

---

## FINAL CLASSIFICATION

**T-D: TLS persistence mechanism fails physically.**

Supported by T-B additionally: even if persistence existed, all observables
are reproduced by conventional physics.

The full failure chain:

1. Physical persistence mechanism: FAILED
   Standard TLS hopping in amorphous SiO₂ is a simple random walk.
   Isotropy of the amorphous solid destroys directional memory.
   Anderson localization suppresses coherent directed transport.
   No known physical mechanism generates spatial directional persistence in TLS.

2. C5 closure: FAILED
   Standard TLS gives diffusion, not telegrapher. Diffusion has no n±
   factorization. C5 cannot be satisfied by diffusion.

3. c derivable from material parameters: PARTIAL
   c_hop = d_TLS × γ_hop IS derivable from TLS literature parameters.
   c_hop ~ 10⁻⁵ m/s ≪ v_s = 6000 m/s (confirmed anomalously slow).
   BUT: c_hop is the diffusive hop speed, not the PRW propagation speed.
   The PRW structure needed to make c_hop into the substrate speed does not exist.

4. Forward prediction: FAILED
   τ_B and ξ_c both require γ_rev, which is FREE (no physical determination).
   No parameter-free prediction of τ_B, ξ_c, or C_Γ(r) is possible.

5. Chip-scale correlations: FAILED NUMERICALLY
   For physical TLS parameters: ξ_c ~ 1–100 nm. Qubit separation ~ 1 mm.
   C_Γ(r = 1mm) ≈ 0 exponentially. Nothing to measure.

6. Conventional equivalence: ALL PREDICTIONS REPRODUCED
   Lorentzian S(ω): reproduced by standard TLS bath.
   K₀ spatial shape: reproduced by 2D screened diffusion (new finding).
   Gaussian NM onset: reproduced by any Gaussian bath.
   Causal wavefront: inaccessible at c_TLS (wavefront at t ~ 100 s >> T₂).

---

## GATE STATUS: EXTENSION B CLOSED

The TLS route is the strongest candidate for Extension B (c ≪ v_s with physical
motivation). It fails at multiple independent levels. No other candidate was found
in SUBSTRATE_CANDIDATE_AUDIT.md.

**Extension B is closed.** No physically credible substrate satisfying C2/C5 with
c ≪ v_s has been identified. The TLS route, the only plausible candidate, fails
because:

- Standard TLS hopping is diffusive, not persistent
- Even if persistence were postulated, all predictions are conventionally equivalent
- The correlation length ξ_c is sub-nm for physical parameters — undetectable

---

## NEW FINDING FROM THIS ANALYSIS

The K₀ correlator is NOT unique to the telegrapher/PRW model. It is also the
Green's function of the 2D screened diffusion equation:

  (∇² − ξ_c⁻²)G(r) = −δ(r)  →  G(r) = K₀(r/ξ_c)/(2π)

This means: even if IBM qubit data showed a K₀ spatial correlation profile,
this would be consistent with BOTH the C2 telegrapher substrate AND a conventional
2D diffusion bath with screening. The K₀ shape has zero discriminating power
even against diffusion-type models in 2D.

This finding supersedes the earlier assessment in DISCRIMINATOR_RECONSTRUCTION.md
which classified K₀ as "conditionally revisable." It is now classified REJECTED
even against the 2D screened diffusion null.

---

## OVERALL PROJECT STATUS AS OF 2026-08-22

Combining THEORY_EXTENSION_GATE.md (Extension A/B analysis) with this gate:

| Extension | Status | Reason |
|-----------|--------|--------|
| Extension A (c = v_s) | CLOSED AS DISCRIMINATOR | Phonon bath gives identical predictions |
| Extension B via FPUT | CLOSED | C5 forces c = v_s |
| Extension B via TLS | CLOSED | Persistence fails; ξ_c too small; all predictions conventional |
| Extension B via quasiparticles | CLOSED | Diffusion dynamics, not telegrapher |
| Extension B via polaritons | NOT APPLICABLE | Wrong chip material |
| Extension B via SAW | NOT APPLICABLE | Requires engineered hardware; still conventional |

All currently known Extension B routes are closed.

---

## REQUIRED CONDITIONS TO REOPEN

The project can reopen ONLY if one of the following is externally produced and
documented with a physical derivation (not a mathematical ansatz):

**Condition R1:** A new substrate is identified in standard SC qubit chip materials
  (Si, SiO₂, Al, Nb, or their interfaces) that:
  - Propagates at c ≪ v_s
  - Has PRW/telegrapher dynamics derivable from microscopic physics
  - Has c, τ_B, ξ_c all derivable from material parameters WITHOUT free fitting
  - Produces at least one observable not reproduced by a conventional bath

**Condition R2:** A rigorous theoretical argument is found showing that a
  class of amorphous solid excitations MUST exhibit directional persistence,
  with the persistence rate derivable from material properties.

**Condition R3 (weak, Extension A only):** A discriminating test is identified
  that distinguishes c = v_s (phonon) from c = v_s (C2 telegrapher). The two
  models must differ in some measurable way. This has not been found; if found,
  Step T1 in THEORY_EXTENSION_GATE.md can proceed.

---

## HARDWARE STATUS

**HARDWARE AUTHORIZED: NO.**

All gates remain frozen:
- RESCUE_GATE: FROZEN (theoretical precondition unmet)
- THEORY_EXTENSION_GATE: FROZEN (Extension A conventional, Extension B closed)
- TLS_EXTENSION_GATE: FROZEN (TLS route closed — T-D/T-B)

No IBM QPU work is authorized.

---

## SCIENTIFIC SUMMARY

The SXC-IGC/C2 theory, after exhaustive analysis including:
- Full prediction ladder (PREDICTION_LADDER.md)
- Extension A/B search (THEORY_EXTENSION_SEARCH.md)
- Substrate candidate audit (SUBSTRATE_CANDIDATE_AUDIT.md)
- TLS substrate derivation and three independent failure audits

...has not produced a single parameter-free, non-conventional, measurable prediction.

The theory is mathematically consistent and internally correct. It describes
real physics (telegrapher-type substrate transport). But the substrate is not
identified with a physical degree of freedom that is:
- Present in standard SC qubit chips
- Propagating at anomalously slow speed c ≪ v_s
- Derivable from material parameters
- Producing predictions not reproduced by phonon bath or standard TLS bath

Until this identification is made, SXC-IGC remains a mathematical framework
without an empirical program.

*Gate frozen: 2026-08-22*
*Not revisable without documented satisfaction of Condition R1, R2, or R3 above.*
