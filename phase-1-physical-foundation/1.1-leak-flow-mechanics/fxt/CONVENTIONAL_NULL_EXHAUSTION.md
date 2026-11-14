# CONVENTIONAL_NULL_EXHAUSTION.md
## Exhaustive Conventional Null Coverage for Every C2 Observable

**Date:** 2026-08-22
**Method:** For each C2 observable, identify the strongest conventional null
  that reproduces it without adopting the SXC-IGC ontology.

---

## Observable 1: Lorentzian Temporal PSD S(ω) = 2S₀τ/(1+ω²τ²)

Strongest null: Ornstein-Uhlenbeck (OU) bath.
OU autocorrelation: C(t) = S₀ exp(−|t|/τ) → S(ω) = 2S₀τ/(1+ω²τ²). Identical.
Structural reason: Any Markovian Gaussian bath with single relaxation time τ
gives a Lorentzian PSD. This is a model-independent consequence of the
Wiener-Khinchin theorem applied to exponential autocorrelation.
Verdict: FULLY REPRODUCED. Null is structural, not coincidental.

---

## Observable 2: K₀(r/ξ_c) Spatial Correlator

Strongest null A: 2D acoustic phonon bath with screening.
Phonon bath 2D Green's function for screened propagation: K₀(r/ξ) exactly.

Strongest null B: 2D screened diffusion equation.
(∇² − ξ_c⁻²)G(r) = −δ(r) → G(r) = K₀(r/ξ_c)/(2π). Exact identity.
This is a MATHEMATICAL fact: K₀ is the fundamental solution of the 2D modified
Helmholtz equation, shared by diffusion with exponential decay AND telegrapher.

Structural reason: K₀ emerges from any 2D field with a characteristic decay
length ξ_c, regardless of whether the dynamics are telegrapher or diffusion.
Verdict: FULLY REPRODUCED by 2D screened diffusion. Not unique to telegrapher.

---

## Observable 3: Gaussian Non-Markovian Onset W(t)≈exp(−Γt−Gt²/2)

Strongest null: Kubo cumulant expansion.
For ANY zero-mean Gaussian stochastic process coupled to a qubit:
W(t) = exp(−∫₀ᵗ (t−s) C(s) ds) where C(s) is the noise autocorrelation.
Short-time expansion gives exactly exp(−Γt − Gt²/2) with G = C(0).
This is model-independent — it requires only Gaussian statistics and finite C(0).
Verdict: FULLY REPRODUCED. Universal for any Gaussian bath.

---

## Observable 4: ω_rot² Ramsey Scaling Γ_φ = k_rot·ω_rot²

Strongest null: filter function argument (any bath).
For a qubit rotating at ω_rot with Lorentzian PSD S(ω):
Γ_φ = ∫ S(ω) |F(ω,ω_rot)|² dω where F peaks at ω = ω_rot.
For S(ω) ≈ const near ω_rot: Γ_φ ∝ S(ω_rot) · ω_rot² (from rotating-frame geometry).
This holds for ANY bath with finite PSD at ω_rot and the same qubit rotation geometry.
Verdict: FULLY REPRODUCED. Geometric consequence of rotating-frame coupling.

---

## Observable 5: Causal Wavefront C(r,t)=0 for t < r/c

Strongest null A (diffusion): No wavefront. C(r,t) > 0 ∀ t > 0. DOES NOT reproduce.
Strongest null B (phonon bath): Phonon bath has wavefront at t = r/v_s.
Under Extension A (c=v_s): FULLY REPRODUCED by phonon bath.
Under Extension B (c≪v_s): Wavefront at t = r/c ≫ T₂. INACCESSIBLE.

Structural reason: Any substrate with finite propagation speed (phonons, EM) has
a causal front. The wavefront is not unique to the C2 telegrapher.
Verdict: PARTIALLY REPRODUCED. Discriminates vs. diffusion-only models.
Does NOT discriminate vs. phonon bath (the dominant physical null).

---

## Observable 6: T₂ ≤ 2T₁ Bound

Strongest null: standard quantum channel / Lindblad theory.
T₂ ≤ 2T₁ follows from the positivity of the Lindblad dissipator for any
dephasing + relaxation combination. This is a property of CPTP maps, not of
the substrate.
Verdict: FULLY REPRODUCED. Standard quantum information result.

---

## Observable 7: Telegrapher Dispersion ω(k)

Strongest null: phonon bath with Debye cutoff.
Acoustic phonons: ω = v_s k (linear). At high k: Debye cutoff.
Telegrapher: ω(k) = √(c²k²−1/(4τ²)) − i/(2τ).
These are structurally different at k ~ 1/ξ_c.
BUT: the crossover scale ξ_c = 2cτ is FREE in C2.
Without a prior prediction of ξ_c (from material parameters), measuring the
crossover gives ξ_c but cannot test C2 vs. phonon bath.
Verdict: UNDETERMINED. Would require prior prediction of ξ_c.

---

## Observable 8: Material Dependence ξ_c ∝ v_s(material) [Extension A]

Strongest null: acoustic phonon bath.
A phonon bath with ξ_corr ∝ v_s(material)·τ_B gives the same material scaling.
This is conventional phonon transport.
Verdict: FULLY REPRODUCED by phonon bath.

---

## Observable 9: Single Lorentzian per Qubit

C2 predicts a single Lorentzian (single τ_B) at each qubit.
Null: Standard TLS bath with uniform density → approximately Lorentzian.
Reality: IBM qubit spectra show 1/f component (distribution of τ_B values).
The single-Lorentzian prediction is SIMPLER than conventional physics (which has
multiple TLS with different τ_B) and INCONSISTENT with measured IBM noise.
Verdict: REFUTED by existing data. Not merely reproduced by null — the null
(full TLS bath) is MORE accurate.

---

## Observable 10: Entropy Production σ ≥ 0

Strongest null: any irreversible thermodynamic process.
This is the second law. Not distinctive.
Verdict: FULLY REPRODUCED.

---

## Null Coverage Table

| Observable | Strongest null | Reproduced? |
|-----------|---------------|-------------|
| Lorentzian S(ω) | OU bath | FULLY |
| K₀ spatial | 2D screened diffusion | FULLY |
| Gaussian NM onset | Kubo expansion (any Gaussian bath) | FULLY |
| ω_rot² Ramsey | Filter function (any Lorentzian bath) | FULLY |
| Causal wavefront | Phonon bath | FULLY under Ext A; INACCESSIBLE under Ext B |
| T₂≤2T₁ | Standard CPTP | FULLY |
| Telegrapher dispersion | Phonon + Debye | UNDETERMINED (ξ_c free) |
| Material ξ_c scaling | Phonon bath | FULLY |
| Single Lorentzian | TLS bath (multiple) | REFUTED by IBM data |
| Entropy production | Thermodynamics | FULLY |

---

## Conclusion

Every C2 observable is either:
1. Fully reproduced by a standard conventional null (OU, phonon, screened diffusion,
   Kubo, CPTP)
2. Undetermined because a free parameter (ξ_c, c) is not predicted
3. Refuted by existing data (single Lorentzian vs. observed 1/f)

The conventional null coverage is EXHAUSTED. No C2 observable escapes.

The causal wavefront is the sole partial exception — it discriminates C2 from
diffusion-type baths but not from phonon baths. Since phonon baths are the
physically dominant null for SC qubits, this is not a useful discriminator.
