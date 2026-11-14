# TLS_PREDICTION_TABLE.md
## Complete Parameter and Prediction Table for TLS Substrate

**Date:** 2026-08-22
**Sources:** TLS_SUBSTRATE_DERIVATION.md, GAP7_TLS_CLOSURE.md, TLS_PERSISTENCE_AUDIT.md
**Classification:** DERIVED | INDEPENDENTLY MEASURABLE | FREE | FAILED | UNKNOWN

---

## Parameter Table

| Parameter | Symbol | Expression | Classification | Value range |
|-----------|--------|-----------|----------------|-------------|
| TLS spatial density | ρ_TLS | — | INDEP. MEASURABLE | 10²⁰–10²¹ m⁻³ |
| Inter-TLS spacing | d_TLS | ρ_TLS^{-1/3} | DERIVED | 1–3 nm |
| TLS asymmetry energy | ε | — | INDEP. MEASURABLE | 0.01–10 GHz |
| TLS tunneling amplitude | Δ | — | INDEP. MEASURABLE | 0.01–10 GHz |
| TLS splitting | E | √(ε²+Δ²) | DERIVED | 0.01–15 GHz |
| TLS dephasing rate | Γ₂ | — | INDEP. MEASURABLE | 10⁴–10⁷ s⁻¹ |
| TLS relaxation rate | Γ₁ | — | INDEP. MEASURABLE | 10³–10⁶ s⁻¹ |
| TLS dipole moment | p | — | INDEP. MEASURABLE | ~10⁻³⁰ C·m |
| Dielectric constant | ε_r | — | INDEP. MEASURABLE | ~4 (SiO₂) |
| TLS-TLS coupling | V_ij | p²/(4πε₀ε_r d³) | DERIVED | 0.01–1 MHz |
| Hop rate | γ_hop | V_ij²/Γ₂ | DERIVED | 10²–10⁵ s⁻¹ |
| Hop speed | c_hop | d_TLS × γ_hop | DERIVED | 10⁻⁶–10⁻⁴ m/s |
| Persistence reversal rate | γ_rev | — | **FREE/FAILED** | unknown |
| PRW correlation time | τ_B | 1/(2γ_rev) | **FREE/FAILED** | unknown |
| Correlation length | ξ_c | c_hop/γ_rev | **FREE/FAILED** | unknown |

Parameters marked FREE/FAILED are free because the persistence mechanism does not
exist in standard TLS physics (TLS_PERSISTENCE_AUDIT.md). Without γ_rev, τ_B and
ξ_c cannot be predicted.

---

## Predicted Observables

### Observable P1: Propagation speed c

```
c_hop = d_TLS × γ_hop = d_TLS × V_ij² / Γ₂
```

Numerical range (from independent TLS parameters):

| Scenario | d_TLS | γ_hop | c_hop |
|----------|-------|-------|-------|
| Low density | 3.2 nm | 10³ s⁻¹ | 3×10⁻⁶ m/s |
| Mid density | 2.0 nm | 10⁴ s⁻¹ | 2×10⁻⁵ m/s |
| High density | 1.0 nm | 10⁵ s⁻¹ | 10⁻⁴ m/s |

Classification: DERIVED from independently measurable parameters.
Status: c_hop ≪ v_s confirmed across full range.
But: c_hop is the DIFFUSIVE hop speed, not the PRW propagation speed.
The PRW speed = c_hop only if persistence exists (it does not).

### Observable P2: Correlation time τ_B

```
τ_B = 1/(2γ_rev)
```

Classification: FREE. γ_rev has no physical determination from standard TLS.
Sensitivity: τ_B spans 10⁻⁷ s to >10³ s depending on γ_rev.
Status: UNDETERMINED. Theory remains underconstrained here.

### Observable P3: Correlation length ξ_c

```
ξ_c = c_hop / γ_rev = d × V²/(Γ₂ γ_rev)
```

For chip-scale ξ_c ~ 1 mm and c_hop ~ 2×10⁻⁵ m/s:
  γ_rev = c_hop/ξ_c = 2×10⁻⁵/10⁻³ = 0.02 s⁻¹ → τ_B = 25 s

This is unphysical. No TLS relaxation process has τ_B = 25 s at mK.
Typical TLS T₂ ~ 0.1–100 µs. Physical γ_rev ~ Γ₂ ~ 10⁴–10⁷ s⁻¹.

For physical γ_rev ~ 10⁴ s⁻¹: ξ_c ~ 2×10⁻⁹ m = 2 nm (sub-qubit, undetectable).

Classification: FAILS numerically. Chip-scale ξ_c impossible for physical TLS.

### Observable P4: Decoherence rate Γ_φ

```
Γ_φ = g² S₀ / ℏ²
S₀ = 2 n_TLS p²_eff / (4πε₀ ε_r)²  [effective noise amplitude]
```

This is standard TLS-induced dephasing. It is INDISTINGUISHABLE from conventional
TLS bath prediction. No new parameter is predicted by the PRW structure.

Classification: CONVENTIONAL. Same prediction as standard TLS bath.

### Observable P5: Spatial decoherence correlation C_Γ(r)

Under PRW assumption: C_Γ(r) = K₀(r/ξ_c)/K₀(a/ξ_c)

But ξ_c ~ 2 nm (from physical γ_rev). At qubit separation r ~ 1 mm:
  r/ξ_c ~ 5×10⁵ → K₀(5×10⁵) ≈ 0 (exponentially suppressed)

The spatial correlation between any two qubits on a chip would be ZERO under
physical TLS parameters. There is nothing to measure.

Classification: FAILS numerically. Correlation negligible at chip scale.

---

## Sensitivity Analysis

Varying TLS parameters across their literature range:

| Parameter varied | c_hop range | ξ_c range (physical γ_rev) |
|-----------------|-------------|--------------------------|
| ρ_TLS: 10²⁰–10²¹ m⁻³ | 3×10⁻⁶–10⁻⁴ m/s | 0.3 nm – 10 nm |
| Γ₂: 10⁴–10⁷ s⁻¹ | 10⁻⁷–10⁻⁴ m/s | 0.01 nm – 10 nm |
| V_ij: 0.01–1 MHz | 10⁻⁸–10⁻³ m/s | 0.001 nm – 100 nm |

Conclusion: Across the full plausible TLS parameter range, ξ_c remains below 100 nm.
No combination of physical TLS parameters produces chip-scale (mm) correlations.

The result spans ~8 orders of magnitude in c_hop but all values remain ≪ v_s AND
all give ξ_c well below the qubit separation scale. The theory is not just
underconstrained — its predictions in the observable range are numerically zero.

---

## Classification Summary

| Quantity | Forward predicted? | Constrained? | Observable? | Conventional? |
|---------|-------------------|-------------|------------|---------------|
| c_hop | YES | YES | NOT DIRECTLY | YES (= diffusion speed) |
| τ_B | NO (γ_rev free) | NO | N/A | N/A |
| ξ_c | NO | NO | NO (sub-nm) | N/A |
| Γ_φ | YES | YES | YES | YES (standard TLS) |
| C_Γ(r) | ~0 numerically | N/A | NO (too small) | N/A |

**No parameter-free, non-conventional, observable prediction survives.**
