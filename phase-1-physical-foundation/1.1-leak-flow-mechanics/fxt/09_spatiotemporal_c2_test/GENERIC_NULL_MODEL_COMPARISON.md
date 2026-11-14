# GENERIC NULL MODEL COMPARISON
## C2 vs the Strongest Generic Open-Quantum-System Alternatives

**Date:** 2026-08-21

---

## Null Model Family

**NM-1:** Spin-boson pure-dephasing model with arbitrary spectral density J_B(ω).
Free parameters: J_B(ω), cutoff, coupling g. Can produce any single-qubit decay shape.

**NM-2:** 2D Ornstein-Uhlenbeck scalar field: τ∂_t ψ = D∇²ψ - ψ + noise.
Spatial correlator: K₀(r/ξ) with ξ = √(Dτ). Free parameters: D, τ.

**NM-3:** Exponentially correlated classical noise: C(t) = σ²exp(-|t|/τ_B).
Produces Lorentzian PSD. Free parameters: σ, τ_B.

**NM-4 (strongest):** 2D stationary Gaussian random field B(x,t) with arbitrary
power spectrum S_B(k,ω). Two independent free parameters: spatial scale ξ,
temporal scale τ. No constraint between them.

---

## Observable Comparison

| Observable | C2 prediction | NM reproduces? | Verdict |
|------------|--------------|---------------|---------|
| Single-qubit Ramsey C(t) | exp(-Γt), Γ = k_rot ω_rot² | NM-3 exactly | NON-DISCRIMINATING |
| Single-qubit PSD | Lorentzian τ_B/(1+ω²τ_B²) | NM-3 exactly | NON-DISCRIMINATING |
| DD filter responses | F(ω)·S_JJ(ω), same Lorentzian | NM-3 exactly | NON-DISCRIMINATING |
| Multi-qubit cross-Γ amplitude | Γ_i = Γ_j (homogeneous) | NM-4 (homogeneous) | NON-DISCRIMINATING |
| K₀(r/ξ_c) functional shape | K₀ in 2D | NM-2 exactly | NON-DISCRIMINATING (shape only) |
| **ξ_c/τ_B = 2c = const** | Joint constraint c ≤ v_s | **NM-4 cannot** (ξ, τ independent) | **POTENTIALLY DISCRIMINATING** |
| **Ballistic front r = ct at t < τ_B** | Strict causal cone | **NM-2 cannot** (diffusive) | **POTENTIALLY DISCRIMINATING** |

---

## Details on the Two Surviving Discriminators

### D-1: The joint constraint ξ_c = 2c τ_B

C2 predicts that spatial correlation length and temporal correlation time are NOT
independent. They are linked by a single substrate parameter c:

    ξ_c / τ_B = 2c,   where c ≤ v_s = a√(K/m)

The null model NM-4 has ξ and τ as independent free parameters. Measuring both
on the same substrate and finding ξ/(2τ) = const = c (and further finding c consistent
with the known lattice parameters) would be a result NM-4 cannot mimic without
imposing the constraint by hand.

**Why this is currently blocked:** ξ_c cannot be measured because the chip span
is << ξ_c at measured τ_B ~ 5 µs. Not blocked by theory — blocked by hardware scale.

**Classification: C2-SPECIFIC STRUCTURAL PREDICTION. Currently inaccessible.**

### D-2: Ballistic causal front at t < τ_B

The telegrapher equation has a strict causal cone: the Green's function G(r,t) = 0
for r > ct. An OU bath does not — its correlations spread instantaneously.

This is a genuine mathematical distinction between the telegrapher and diffusion.

**Why this is currently inaccessible:** Detecting the ballistic front requires
time-resolved two-qubit cross-correlations at sub-τ_B timescales AND qubit
separations r < cτ_B ~ 6000 × 5×10⁻⁶ m = 3 cm. On a chip of size < 1.5 cm,
the front would require ~τ_B/3 ~ 1.7 µs time resolution in spatial cross-correlation.
This is not achievable with Ramsey spectroscopy.

**Classification: C2-SPECIFIC CAUSAL PREDICTION. Currently inaccessible.**

---

## K₀ Is NOT a Discriminator at Functional Form Level

This needs to be stated precisely. The 2D OU field (NM-2) produces K₀(r/ξ) because
both it and the 2D telegrapher are instances of the SAME mathematical object:
the massive scalar Green's function in 2D, (-∇² + m²)G = δ, with m = 1/ξ.

Knowing the spatial correlator is K₀ tells you: "there is a 2D massive scalar field
with mass m here." It does NOT tell you whether the mass comes from a PRW reversal
rate λ (C2) or from a diffusive decay rate (OU). Both have the same equal-time
static Green's function.

**The K₀ functional form is a property of 2D massive scalar fields in general,
not of the C2 telegrapher specifically.**

---

## Conclusion

NM-4 can reproduce every currently measurable C2 observable.

C2 makes two genuine structural predictions not reproducible by NM-4:
(1) the joint constraint ξ_c = 2cτ_B (a relation between independently measurable scales)
(2) a strict ballistic causal front at r = ct for t < τ_B

Both require hardware capabilities not currently available.
The null model cannot be ruled out with current data.
