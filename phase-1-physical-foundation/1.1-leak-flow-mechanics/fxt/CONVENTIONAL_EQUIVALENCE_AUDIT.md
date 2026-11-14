# CONVENTIONAL_EQUIVALENCE_AUDIT.md
## Strongest Conventional Nulls for Every C2/SXC-IGC Prediction

**Date:** 2026-08-22
**Method:** For each C2 prediction, construct the strongest physically
  plausible conventional mechanism that reproduces the same observable.
**Sources:** C2_FOUNDATIONS.md, ADVERSARIAL_NULL_AUDIT.md,
  THEORY_CLOSURE_AUDIT.md, PARAMETER_OBSERVABLE_RANK.md

**Rule:** A prediction is conventionally equivalent if a conventional
mechanism can reproduce it with free parameters of comparable or fewer
count. A prediction is NOT conventionally equivalent only if conventional
physics cannot reproduce it without violating established physics or
introducing implausible assumptions.

---

## Prediction P1: Lorentzian Power Spectral Density

**C2 prediction:**
```
S_JJ(ω) = 2S₀τ_B / (1 + ω²τ_B²)
```
Derived from C_JJ(t) = S₀·exp(−t/τ_B) via Wiener-Khinchin theorem.
Source: substrate_transport_derivation.md §1.4, proved [T].

**Strongest conventional null:**
Any Ornstein-Uhlenbeck (OU) process with correlation time τ_OU and
amplitude S_OU has exactly the same PSD:
```
S_OU(ω) = 2S_OU·τ_OU / (1 + ω²τ_OU²)
```
The OU process is the unique stationary Gaussian Markov process with
exponential autocorrelation. It arises from:
- Flux noise in Josephson junctions (Yoshihara et al. 2006)
- Charge fluctuators with single relaxation rate (Paladino et al. 2014)
- 1/f noise with a Lorentzian spectral component at finite τ
- Any RC-filtered white noise

Free parameters of the conventional null: (S_OU, τ_OU) — same count as C2's (S₀, τ_B).

**Equivalence verdict: FULLY EQUIVALENT.**
The Lorentzian PSD is the mathematical signature of an exponentially
correlated Gaussian process. Any physical mechanism producing such a
process gives the same observable. C2 provides a substrate interpretation
but not a unique prediction.

---

## Prediction P2: Γ_φ = k_rot · ω_rot²

**C2 prediction:**
```
Γ_φ = k_rot · ω_rot²
k_rot = 8g²S₀r_q²τ_B / (3ℏ²)
```
Derived from rotating-frame current variance ⟨(δJ)²⟩ ∝ ω_rot².
Source: C2_FOUNDATIONS.md §Subsystem 4, Theorem HC-2 [T conditional].

**Strongest conventional null:**
Any environment with a power spectral density S(ω) such that:
```
Γ_φ(ω_rot) = ∫ dω S(ω) F(ω/ω_rot)
```
produces Γ_φ ∝ ω_rot² when the filter function F peaks at ω = ω_rot and
S(ω) ≈ S(0) (white noise at low frequencies).

Specifically: a sub-Ohmic bath with S(ω) ∝ ω^α (α > 0) filtered through
a rotating frame gives Γ_φ ∝ ω_rot^(1+α). At α = 1 (Ohmic bath): Γ_φ ∝ ω_rot².
More precisely, for a Lorentzian bath: S(ω) = 2S₀τ/(1+ω²τ²), the
second-order filter function for rotation gives ⟨(δJ_rot)²⟩ ∝ ω_rot² in
the limit ω_rot·τ << 1 — identical to C2's prediction.

Additional null: Any qubit noise model with angular-momentum-like coupling
to a low-frequency classical field (e.g., magnetic flux noise from nearby
circuits with ω_rot-dependent coupling geometry) gives the same scaling.

**Verdict from C2_FOUNDATIONS.md:**
"Theorem EXP-1: The measured Γ_φ ∝ ω_rot² scaling is consistent with the
prediction but is not unique to the substrate framework."

**Equivalence verdict: FULLY EQUIVALENT.**
The ω_rot² scaling follows from the rotating-frame current variance.
Any classical noise source with flat PSD at the relevant frequencies and
geometric (r_q) coupling to the qubit produces the same scaling.
C2 provides a specific mechanism but the observable is generic.

---

## Prediction P3: Gaussian Non-Markovian Ramsey Onset

**C2 prediction:**
```
W(t) ≈ exp(−Γ_φ·t − G·t²/2)  for t << τ_B
G = Γ_Markov · τ_B⁻¹ = 2g²S₀/ℏ²
```
Derived from the exact dephasing function Φ(t) (proven [T]).

**Strongest conventional null:**
For ANY stationary Gaussian noise source with autocorrelation C(t) and
PSD S(ω), the short-time dephasing is:
```
W(t) ≈ exp(−∫₀ᵗ ∫₀ᵗ' C(t'−t'') dt' dt'')
     ≈ exp(−Γt − C(0)·t²/2 + O(t³))
```
This is the universal short-time behavior for any Gaussian noise with
finite variance C(0) = S_total. The Gaussian correction G = C(0) is not
a signature of the PRW substrate — it is the variance of the noise process
at t=0.

Every 1/f flux noise model, every finite-temperature quantum bath, and every
OU process has this Gaussian onset with G = ∫S(ω)dω/(π) = total noise power.

**Equivalence verdict: FULLY EQUIVALENT.**
The Gaussian NM onset is a universal feature of any Gaussian noise with
finite variance. C2's prediction is simply that the substrate noise is
Gaussian, which any conventional bath model also satisfies.

---

## Prediction P4: K₀ Spatial Decoherence Covariance

**C2 prediction:**
```
C_Γ(r) = K₀(r/ξ_c) / K₀(a/ξ_c)
```
Derived from 2D telegrapher Green's function (analytic step incomplete,
numerically verified, 02_2D_CORRELATION_DERIVATION.md).

**Strongest conventional nulls (adversarial family):**

| Model | Form | Physical basis |
|-------|------|----------------|
| M7 power-law (α=0.5) | A·(r/r₀)^{−0.5} | 1/f flux noise from distributed defects |
| M7 power-law (α=1.0) | A·(r/r₀)^{−1.0} | 1/f noise with steeper spatial decay |
| M9 two-bath exponential | A₁·exp(−r/ξ₁) + A₂·exp(−r/ξ₂) | EM crosstalk + long-range flux noise |
| M11 Matérn (ν=1.5) | A·(1+√3r/ξ)·exp(−√3r/ξ) | Spatially correlated TLS clusters |

**Why these defeat K₀:**
Over r/ξ_c ∈ [0.2, 2.2] (the accessible Brisbane range), K₀(x) ≈ −ln(x/2) − γ_E
(logarithmic). Power-law r^{−α} also decreases approximately logarithmically
over this range. The normalised L2 shape distance = 0.073 (measured).
This means 92.7% of the K₀ shape is shared with best-fit power-law.

FP rates measured (ADVERSARIAL_NULL_AUDIT.md, 300 trials each):
- M7_pow0.5: 13.3% FP — FAILS gate
- M7_pow1.0: 19.7% FP — FAILS gate
- M9_twobath: 15.3% FP — FAILS gate

**Physical mechanism for power-law spatial correlations in SC qubits:**
1/f charge/flux noise in superconducting qubits arises from two-level
fluctuators (TLS) near the qubit junctions. When TLS positions are
distributed according to a scale-free process (e.g., fractal disorder),
the resulting spatial covariance is power-law. This is independently
established in the literature (Müller et al. 2019, Klimov et al. 2018).

**Equivalence verdict: PARTIALLY EQUIVALENT** (shape degenerate on current hardware).
K₀ is not identical in form to power-law — they differ in curvature at
r > 2ξ_c. But on the accessible spatial range (0.2–2.2 ξ_c) with 11 bins,
the shape difference (SNR ≈ 2) is not statistically resolvable. The conventional
null defeats the current test. Equivalence would be broken at r > 5ξ_c.

---

## Prediction P5: P3 Self-Consistency c = ξ_c/(2τ_B)

**C2 prediction:**
Both τ_B and ξ_c arise from the same substrate with speed v = c.
Therefore: c = ξ_c/(2τ_B) must be constant across experimental conditions.

This is an exact derived relation (ξ_c = v/λ, τ_B = 1/(2λ), therefore
ξ_c = 2v·τ_B = 2c·τ_B). Source: exact algebra [T].

**Strongest conventional nulls:**

| Mechanism | Predicted c | Would defeat P3? |
|-----------|-------------|-----------------|
| Acoustic phonons (Si) | v_sound ≈ 5000–8500 m/s | Yes if c_measured ≈ v_sound |
| Surface acoustic waves | ~3000–5000 m/s | Yes if c_measured in this range |
| EM coupling through lines | ~2×10⁸ m/s | No — very different from any c_meas < 1000 m/s |
| Independent OU processes | No finite speed | N/A — no ξ_c/τ_B link |
| Two-bath M9 | Each bath has own speed | No fixed ratio |
| 1/f flux noise diffusion | Diffusion: D = ξ²/2τ, no finite v | Not a propagation speed |

**Key analysis:**
If the measured c = ξ_c/(2τ_B) ≈ 5000 m/s: consistent with phonon bath → P3 is
not discriminating. If c ≈ 10–500 m/s: no conventional mechanism predicts
this ratio → P3 would be anomalous. If c ≈ 10⁸ m/s: consistent with EM.

The P3 relation is NOT reproduced by conventional independent baths: an OU
bath with spatial correlation ξ and temporal correlation τ_OU has no
mechanism that forces ξ/(2τ_OU) to equal any physical velocity. The two
parameters (ξ, τ_OU) are set by different physical processes in the
conventional picture. Only the PRW substrate gives them a common origin.

**Equivalence verdict: CONDITIONALLY NOT EQUIVALENT.**
If c_measured is anomalous (≪ v_sound), no conventional mechanism produces
the specific ratio. If c_measured ≈ v_sound, phonon bath explains it.
The discriminating power depends on the measured value of c.

---

## Summary

| Prediction | C2 derivation | Conventional equivalent | Verdict |
|-----------|---------------|------------------------|---------|
| P1: Lorentzian S_JJ(ω) | Derived [T] | OU process (identical form) | FULLY EQUIVALENT |
| P2: Γ_φ ∝ ω_rot² | Derived [T conditional] | Rotating-frame bath (same scaling) | FULLY EQUIVALENT |
| P3: Gaussian NM onset | Derived [T] | Any Gaussian bath (universal) | FULLY EQUIVALENT |
| P4: K₀ spatial shape | Derived [T, partial] | M7/M9 (shape degenerate on hardware) | EQUIVALENT on current hardware |
| P5: P3 consistency c = ξ_c/(2τ_B) | Derived [exact] | Independent baths: no forced ratio | CONDITIONALLY NOT EQUIVALENT |

**The only prediction that is not trivially reproduced by conventional
mechanisms is P5 (P3 consistency), and only if c_measured is anomalous.**
All other predictions are fully equivalent to standard stochastic bath models.
