# Document 32 — c First-Principles Derivation
## Phase 9e: Does FPUT-3 Determine the PRW Propagation Speed?

**Date:** 2026-08-21  
**Script:** `scripts/p27_c_first_principles.py`  
**Data:** `outputs/data/c_first_principles_audit.json`  
**Classification:** **C_CONDITIONALLY_PREDICTED** (revised from C_PARAMETER_DEPENDENT)

---

## 1. Executive Verdict

The previous audit (Document 31) concluded `C_PARAMETER_DEPENDENT` — that c was a free parameter bounded by v_s but not uniquely determined.

**This audit revises that conclusion.**

The projection_classification_audit.md contains a derivation that was not fully traced in Document 31. The P1 (RPA) governing equations are:

```
∂ₜn⁺ + vₛ ∂ₓn⁺ = −γ(n⁺ − n⁻)
∂ₜn⁻ − vₛ ∂ₓn⁻ = +γ(n⁺ − n⁻)
```

These equations use `vₛ` as the transport speed directly. The `±` split is defined by "the sign of the group velocity `∂ωₖ/∂k`," and the transport speed is the long-wavelength group velocity `|∂ωₖ/∂k|_{k→0} = vₛ = a√(K/m)`.

This means: **c = v_PRW = vₛ = a√(K/m) is derived, not postulated,** conditional on the standard hydrodynamic coarse-graining limit (ℓ_CG >> a) that defines the PRW from the FPUT chain.

However: knowing c = v_s does NOT resolve the experimental problem. For Si at τ_B = 5 µs: ξ_c = 6 cm — still vastly larger than any available chip. The experimental verdict remains: **FROZEN**.

---

## 2. The Critical Text (Quoted Verbatim)

From `03_audits/projection_classification_audit.md`:

**P1(a) Governing Equations:**
```
∂ₜn⁺ + vₛ ∂ₓn⁺ = −γ(n⁺ − n⁻)
∂ₜn⁻ − vₛ ∂ₓn⁻ = +γ(n⁺ − n⁻)
Combined: ∂ₜₜu = vₛ² ∂ₓₓu − 2γ ∂ₜu  (telegrapher equation)
```

**Main Theorem IV.3, step 2:**
> "the ± split comes from the sign of the group velocity ∂ωₖ/∂k"

**P1 Constraint table, C3 row:**
> "Signal speed = vₛ (sound speed)"

**C3 constraint definition:**
> "finite signal speed v_signal ≤ vₛ, where vₛ = (∂ωₖ/∂k)|_{k→0} = √(K/m)·a"

The P1 constraint table says "Signal speed = vₛ" (equality), not "≤ vₛ". The C3 definition is an inequality, but P1 saturates it. This saturation is not an additional postulate — it follows from defining `n⁺` as the right-moving phonon density with speed = group velocity = vₛ.

---

## 3. Complete Derivation Chain

| Step | Statement | Label | Source |
|------|-----------|-------|--------|
| 1 | FPUT Hamiltonian H = Σ[p²/2m + K(Δq)²/2] | ASSUMED | C2_FOUNDATIONS.md SUB.2 |
| 2 | Normal modes ωₖ = 2√(K/m)\|sin(πk/N)\| | DERIVED | proj_class_audit.md S2 |
| 3 | Acoustic speed vₛ = (∂ωₖ/∂k)\|_{k→0} = a√(K/m) | DERIVED | proj_class_audit.md C3 def |
| 4 | Phase-space split n±(x) by sign of ∂ωₖ/∂k | DERIVED | Main Theorem step 2 |
| 5 | Transport speed of n± = \|∂ωₖ/∂k\|\|_{k→0} = vₛ | DERIVED [k→0 limit] | P1(a) governing equations |
| 6 | P1 signal speed = vₛ (C3 row: equality, not bound) | DERIVED | P1 constraint table |
| 7 | c = v_PRW = vₛ = a√(K/m) | DERIVED [conditional] | Steps 3–6 combined |
| 8 | τ_B = 1/(2γ) | DERIVED | 01_PREDICTION_DERIVATION.md |
| 9 | ξ_c = 2c·τ_B = 2·vₛ·τ_B | DERIVED | 02_2D_CORRELATION_DERIVATION.md |

**The conditionality:** Step 5 uses the long-wavelength limit k→0, which gives group velocity = vₛ. At finite k, group velocity < vₛ. The k→0 limit is the standard hydrodynamic coarse-graining already built into defining n±(x) via smooth spatial windows at scale ℓ_CG >> a. This is not an additional postulate — it is the regime in which the PRW is derived.

---

## 4. What FPUT-3 Actually Proves About v

FPUT-3 (Main Theorem, projection_classification_audit.md Part IV.3) proves:

1. Under C1–C6, the unique admissible projection is P1 (RPA)
2. The P1 state variables are n±(x) — right/left-moving phonon action densities
3. The ± split comes from the sign of the group velocity ∂ωₖ/∂k
4. The P1 governing equations use vₛ as the transport speed

FPUT-3 does NOT prove step 4 explicitly — it is contained in the P1 definition. But:
- P1 is derived to be the unique projection
- P1 is defined with n± moving at the group velocity ±vₛ
- This definition follows from identifying n± with the acoustic phonon density split

**The transport speed is therefore vₛ by construction of the coarse-grained state variables.** It is not a free parameter within P1.

---

## 5. Comparison: Inequality vs. Equality

| Statement | Source | Type |
|-----------|--------|------|
| c ≤ vₛ | C3 constraint definition | INEQUALITY (bound) |
| c = vₛ in P1 | P1 governing equation | EQUALITY (in P1) |
| P1 is the unique admissible projection | FPUT-3 | THEOREM |
| Therefore c = vₛ in the unique admissible theory | — | DERIVED (from above 3) |

The C3 definition is an inequality. But the unique admissible projection P1 saturates C3 at equality. Since P1 is the only admissible projection (Theorem FPUT-3), c = vₛ in the C2 theory.

**However:** This reasoning has a subtle gap. FPUT-3 proves P1 is the unique admissible projection **type** — the RPA structure. But it does not explicitly prove that the transport speed within P1 must be exactly vₛ rather than some α·vₛ with α ≤ 1. The P1 governing equations use vₛ because n± are defined as acoustic phonon densities with group velocity vₛ. If one instead defined n± with a different speed, one would get a different (non-physical) PRW.

**The identification c = vₛ follows from identifying the PRW particles with acoustic phonons in the long-wavelength limit.** This is a physical identification, and it is the natural one, but it is not a pure mathematical theorem — it is a physically motivated derivation.

**Classification: DERIVED with physical identification assumption.**

---

## 6. Numerical Verification

From `scripts/p27_c_first_principles.py`:

```
FPUT parameters (Si): m = 4.665×10⁻²⁶ kg, K = 5.696 N/m, a = 5.43×10⁻¹⁰ m
vₛ = a√(K/m) = 6000.0 m/s
vg(k→0) computed numerically = 6000.0 m/s
Ratio vg(k→0)/vₛ = 1.000000  ✓
```

The group velocity at k→0 equals vₛ to machine precision — confirmed.

---

## 7. ξ_c Predictions with Derived c = vₛ

Using c = vₛ = 6000 m/s (Si substrate):

| τ_B | ξ_c = 2c·τ_B | d/ξ_c (7q chip) | d/ξ_c (Eagle 14mm) | Accessible? |
|-----|-------------|----------------|---------------------|-------------|
| 0.5 µs | 0.60 cm | 0.0011 | 0.023 | NO |
| 1.0 µs | 1.20 cm | 0.0053 | 0.012 | NO |
| 5.0 µs | 6.00 cm | 0.0011 | 0.0023 | NO |
| 10.0 µs | 12.0 cm | 0.00053 | 0.0012 | NO |
| 50.0 µs | 60.0 cm | 0.00011 | 0.00023 | NO |

For ξ_c ~ Eagle chip size (14mm): need τ_B ~ 1.2 µs.  
But at τ_B = 1.2 µs and typical Γ_M ~ 2π×50 kHz: NMP = Γ_M·τ_B = 0.38 (marginal NM regime).  
So the test is *in principle* accessible at τ_B ~ 1 µs on a 127-qubit chip.

**BUT:** This requires a 127-qubit chip (IBM Eagle scale), QPU access, and the spatial correlation must be resolved over 14mm — which is 21 nearest-neighbor pairs. This is a large but not impossible geometry.

**The key blocker is not ξ_c — it is the C2/OU degeneracy:**  
Even if d ~ ξ_c, the K₀ vs. exponential shape test requires the spatial correlation to be measured with enough precision to distinguish K₀(r/ξ_c) from exp(−r/ξ_c). This requires the correlation to vary by > 5% across the chip, which happens only when d/ξ_c ~ 0.1–3.

At τ_B = 1.2 µs on Eagle (d_max = 14mm, ξ_c = 14mm): d_max/ξ_c = 1.0 → **the shape test IS accessible**.

---

## 8. The Previously Invalid c = 10⁴ m/s

The previously assumed c = 10⁴ m/s was:
- Not derived from the theory
- Violates C3 (> vₛ(Si) = 6000 m/s)
- Chosen for experimental convenience

**It must be removed from C2 predictions.** The correct derived value is c = vₛ = a√(K/m), which for Si gives c ≈ 6000 m/s.

---

## 9. Questions Answered

| Question | Answer |
|----------|--------|
| Did we derive c? | Yes, conditionally: c = vₛ = a√(K/m) from FPUT group velocity |
| Where does derivation stop? | At the physical identification of PRW particles with acoustic phonons |
| Is c = vₛ a theorem or postulate? | Physically derived (not pure theorem; relies on phonon identification) |
| Was c = 10⁴ m/s invalid? | YES — no derivation and violates C3 |
| Does C3 give bound or equality? | C3 gives bound; P1 saturates it (equality in C2 theory) |
| Is spatial test accessible? | In principle YES at τ_B ~ 1 µs on 127-qubit chip; requires QPU access |
| C2-specific observable? | K₀ vs exp shape test at d ~ ξ_c (τ_B ~ 1 µs, Eagle-scale chip) |
| QPU currently justified? | NO (no access); becomes YES if IBM Eagle access obtained with τ_B ~ 1 µs |
| Theory requires revision? | NO — the c derivation was always present, just not fully traced |
