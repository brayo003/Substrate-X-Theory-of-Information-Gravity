# C2_PARAMETER_IDENTIFIABILITY_FINAL.md
## Parameter Identifiability and Forward Prediction Analysis

**Date:** 2026-08-22

---

## Parameter Vector

θ = (c, λ, g, S₀)

All four are FREE PARAMETERS (classification E from CURRENT_C2_ONTOLOGY_MAP.md).
None is derivable from the C2 axioms without specifying a physical substrate.

---

## Observable Vector

Observables accessible in a Ramsey + spatial correlation experiment:

o = (Γ_φ, τ_B, ξ_c, k_rot)

Relations:
```
τ_B = 1/(2λ)                    [DERIVED from λ]
ξ_c = 2cτ_B = c/λ              [DERIVED from c, λ]
k_rot = 8g²S₀r_q²τ_B/(3ℏ²)    [DERIVED from g, S₀, τ_B]
Γ_φ = k_rot · ω_rot²           [DERIVED from k_rot, ω_rot]
```

The Jacobian ∂o/∂θ has rank 3. Only 3 independent observable combinations
exist from 4 parameters.

The null space has dimension 1: the combination g²S₀ is not independently
resolvable into g and S₀ from decoherence measurements alone.

---

## Forward Prediction Analysis

A forward prediction requires: independently known inputs → numerical prediction
before measurement.

| Quantity | Is it a forward prediction? | Why not? |
|---------|----------------------------|----------|
| Γ_φ = k_rot·ω_rot² | NO | k_rot contains g·S₀ — both free |
| τ_B from Ramsey curvature | NO — measurement, not prediction | τ_B = 1/(2λ), λ is free |
| ξ_c from spatial data | NO — measurement, not prediction | ξ_c = c/λ, both free |
| c = ξ_c/(2τ_B) | NO — tautology | c is defined as ξ_c/(2τ_B) |
| ξ_c = 2v_s·τ_B [Ext A] | CONDITIONAL | requires adopting c=v_s as axiom |
| k_rot [numerical value] | NO | contains g and S₀, both free |

**Not one quantity is forward-predicted from independently known inputs.**

---

## What "Consistency Check" Means vs. "Prediction"

The quantity c = ξ_c/(2τ_B) is often presented as a prediction.
It is NOT. Analysis:

Step 1: Measure τ_B from Ramsey curvature → get a number.
Step 2: Measure ξ_c from spatial correlation → get a number.
Step 3: Compute c = ξ_c/(2τ_B) → get a number.
Step 4: Claim this c is the substrate propagation speed.

This is a CONSISTENCY CHECK (the ratio is internally consistent with the
telegrapher model) and PARAMETER ESTIMATION (c is extracted from data).
It is NOT a prediction because:
- C2 does not predict what value c will take before measurement
- Any measured value of c is consistent with C2 (c is free)
- The check cannot be falsified by any measured value of c

---

## Falsifiability Analysis

For a statement to be falsifiable, there must exist at least one outcome
that would contradict C2.

| Statement | Falsifiable? | Falsification condition |
|-----------|-------------|------------------------|
| Γ_φ ∝ ω_rot² | YES | If Γ_φ ∝ ω_rot^n with n≠2 observed |
| W(t) has Gaussian onset | YES | If onset is non-Gaussian |
| C(r) has K₀ shape | YES | If C(r) is clearly non-K₀ |
| c = ξ_c/(2τ_B) = const | YES | If the ratio varies across conditions |
| Single Lorentzian S(ω) | YES (already falsified) | IBM data shows 1/f, not Lorentzian |

**Falsifiable ≠ distinctive.** All falsifiable predictions are also produced
by conventional models (OU bath, phonon bath, screened diffusion). Falsification
of C2 would equally falsify those conventional models — it would not isolate C2.

---

## The g·S₀ Non-Identifiability

From decoherence measurements: k_rot = 8g²S₀r_q²τ_B/(3ℏ²) is measured.
This gives the combination g²S₀ but not g and S₀ separately.

An independent measurement of S₀ (the substrate noise amplitude) would be
needed to determine g. But S₀ requires direct substrate measurement — which
is inaccessible (Cat 1, NON_DECOHERENCE_OBSERVABLE_SEARCH.md).

**g remains unresolvable from any accessible measurement.**

---

## Conclusion

C2 has 4 free parameters and produces 3 independent observable combinations.
None of those observables constitutes a forward prediction.
All observables are either:
- Parameter estimates (measuring free parameters, not testing predictions)
- Consistency checks (tautological relations between free parameters)
- Falsifiable but conventionally degenerate (same predictions from OU/phonon/screened diffusion)

The identifiability rank deficit (4 parameters, 3 observables, plus g non-resolvable)
means the theory is structurally underdetermined even if all available measurements
are performed.
