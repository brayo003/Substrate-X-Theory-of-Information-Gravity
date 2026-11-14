# COSMOLOGICAL_LIMIT
## Gate 6 — Taking the Cosmological Limit

---

### Status Notice

**TEMPLATE — Gate 5 not yet passed.**

This file defines the tests any derived dynamics must pass when applied to the cosmological context.

---

## Section 1: Purpose of This File

Any dynamics derived from a primitive must be tested against the observed cosmological evolution. This file specifies what "passing the cosmological test" means.

The cosmological limit serves two purposes:
1. **Verification:** The standard picture (ΛCDM + inflation) must be recovered as a limit or approximation. If it is not, the theory is ruled out by all the observations that ΛCDM correctly describes.
2. **Deviation identification:** The region where the primitive produces observable deviations from ΛCDM must be identified. These are the targets for Gate 7 (discrimination).

---

## Section 2: Required Recovery Tests

When the primitive's dynamics is derived, apply the following recovery tests:

### Test 1 — Friedmann Equations in the Late Universe
At z ≪ z_inflation, the modified evolution must reduce to:
```
H² = (8πG/3)(ρ_m + ρ_r + ρ_Λ) - k/a²
```
The primitive's contribution T^P_μν must be negligible at late times.

**Criterion:** |T^P_μν / T^matter_μν| ≪ 1 for z < 10³

### Test 2 — CMB Power Spectrum
The primordial power spectrum generated (or selected) by the primitive must be consistent with Planck 2018 constraints:
- n_s = 0.9649 ± 0.0042
- ln(10^10 A_s) = 3.044 ± 0.014
- r < 0.036 (95% CL, BICEP/Keck 2023)

**Criterion:** Predicted power spectrum within 2σ of measured values (or explicitly predicting deviations at currently unconstrained scales).

### Test 3 — BBN Nucleosynthesis
The thermal history of the universe must be compatible with observed light element abundances.

**Criterion:** The primitive must not significantly alter the expansion rate at T ~ 1–10 MeV (BBN epoch) unless a specific, testable prediction of that alteration is made.

### Test 4 — Structure Formation
The growth of structure from initial perturbations must be consistent with observed LSS.

**Criterion:** The matter power spectrum and σ_8 must be within observational bounds, or deviations must be specific testable predictions.

---

## Section 3: Identifying the Deviation Epoch

The region where the primitive deviates from standard ΛCDM is the primary experimental target. Based on the nature of the candidates, the most likely deviation epoch is:

| Candidate | Expected deviation epoch | Observable |
|---|---|---|
| A (D-constraint) | Pre-inflationary / inflationary | Primordial power spectrum at large scales (low ℓ CMB) |
| B (Q-bound) | Inflationary / Planck scale | CMB non-Gaussianity, r (tensor-to-scalar ratio) |
| D (C-constraint) | Pre-inflationary | Primordial gravitational wave background |

The deviations must be computed from the derived dynamics, not assumed.

---

## Section 4: The Minimum Observable Requirement

For Gate 6 to pass, the cosmological limit must produce:

**At minimum:** A prediction of the form δO = f(primitive parameters) where:
- O is a measurable CMB or LSS observable
- f is derivable from the primitive dynamics
- δO ≠ 0 for any physical value of the primitive parameters
- δO is distinguishable from adjusting existing ΛCDM free parameters

This is the minimum to proceed to Gate 7 (discrimination). Without a specific prediction, the program cannot construct a null model comparison.

---

*Document status: TEMPLATE — awaiting Gate 5 clearance and derivation in DYNAMICS.md*
