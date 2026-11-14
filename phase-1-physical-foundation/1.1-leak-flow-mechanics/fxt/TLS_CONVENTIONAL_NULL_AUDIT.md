# TLS_CONVENTIONAL_NULL_AUDIT.md
## Adversarial Conventional-Equivalence Analysis for TLS Substrate

**Date:** 2026-08-22
**Premise:** Even assuming the TLS PRW substrate is physically valid, test whether
  any conventional mechanism reproduces the same observables.
**Sources:** TLS_SUBSTRATE_DERIVATION.md, TLS_PERSISTENCE_AUDIT.md, GAP7_TLS_CLOSURE.md

---

## Observable 1: Lorentzian S_JJ(ω)

TLS PRW prediction: S(ω) = 2S₀τ_B / (1 + ω²τ_B²)

Conventional null: Standard single TLS bath gives identical Lorentzian (Makhlin et al.
2001). OU bath gives identical Lorentzian. This is the generic form for any
single-exponential bath.

Verdict: NOT A DISCRIMINATOR. Conventional equivalent exists.

---

## Observable 2: Gaussian Non-Markovian Onset

TLS PRW prediction: W(t) ≈ exp(−Γt − Gt²/2) for t ≪ τ_B

Conventional null: Universal Kubo cumulant expansion to second order for any
Gaussian bath. Reproduced by standard TLS noise exactly.

Verdict: NOT A DISCRIMINATOR.

---

## Observable 3: K₀ Spatial Shape

TLS PRW prediction: C_Γ(r) = K₀(r/ξ_c)

Conventional null: The 2D screened diffusion equation (∇² − κ²)G = −δ(r) gives
G(r) = K₀(κr)/(2π) exactly. A conventional 2D diffusing TLS bath with screening
length ξ_c produces IDENTICAL K₀ spatial correlations. No PRW needed.

Critical: K₀ is not unique to telegrapher/PRW. It is the fundamental solution of
the 2D modified Helmholtz equation, shared by diffusion with a decay term.

Verdict: NOT A DISCRIMINATOR. 2D screened diffusion reproduces K₀.

---

## Observable 4: Causal Wavefront

TLS PRW prediction: C_Γ(r,t) = 0 for t < r/c_TLS

From GAP7_TLS_CLOSURE.md: c_TLS ~ 10⁻⁵ m/s. For r = 1 mm:
  t_wavefront = r/c_TLS = 10⁻³/10⁻⁵ = 100 s

Qubit T₂ ~ 150 µs on Brisbane. The wavefront arrives 100 s after the experiment
ends. This prediction is EXPERIMENTALLY INACCESSIBLE.

Even if observable, a phonon bath wavefront at v_s would arrive at t = 0.17 µs —
also a causal front, just faster. The TLS front cannot be distinguished from "no
correlation" on any accessible timescale.

Verdict: NOT A DISCRIMINATOR (inaccessible; prediction lives beyond T₂ by 6 orders
of magnitude).

---

## Observable 5: Temperature Dependence

TLS PRW prediction: Γ_φ ∝ n_TLS(T) ∝ T at low T.

Conventional null: Standard TLS decoherence gives Γ_φ ∝ T. Well-confirmed for
SC qubits (Paladino et al. 2014, Müller et al. 2019).

Verdict: NOT A DISCRIMINATOR.

---

## Observable 6: Single Lorentzian per Qubit

TLS PRW prediction: Each qubit sees a single Lorentzian noise component.

Reality check: IBM qubit noise spectra show 1/f behavior + discrete TLS peaks —
multi-component. A single Lorentzian is INCONSISTENT with measured IBM noise.
The TLS PRW is simpler than the actual physics.

Verdict: REFUTED by existing data on real chips. Not merely non-discriminating.

---

## Observable 7: Chip-Scale Correlation Length ξ_c

TLS PRW prediction: ξ_c = c_TLS / γ_rev

For c_TLS ~ 10⁻⁵ m/s and physically motivated γ_rev ~ γ_hop ~ 10⁴ s⁻¹:
  ξ_c ~ 10⁻⁵/10⁴ = 10⁻⁹ m = 1 nm

For ξ_c ~ 1 mm (chip scale), need γ_rev ~ 0.01 s⁻¹ → τ_B = 50 s.
No TLS relaxation process has τ_B = 50 s at mK.

Verdict: FAILS numerically. Chip-scale ξ_c requires unphysical TLS parameters.

---

## Summary Table

| Observable | Conventional null | Discriminating? |
|-----------|------------------|----------------|
| Lorentzian S(ω) | Standard TLS bath: identical | NO |
| Gaussian NM onset | Any Gaussian bath: identical | NO |
| K₀ spatial shape | 2D screened diffusion: identical | NO |
| Causal wavefront | Inaccessible (t >> T₂ by 10⁶×) | NO |
| T-dependence | Standard TLS: identical | NO |
| Single Lorentzian | Refuted by IBM 1/f data | REFUTED |
| Chip-scale ξ_c | Requires τ_B = 50 s — unphysical | FAILS |

---

## Conclusion

Zero discriminating predictions survive the conventional-equivalence attack,
even under the hypothetical assumption that TLS persistence exists.

Every TLS PRW observable is reproduced by a standard TLS bath, phonon bath,
or 2D screened diffusion. The one potentially distinctive prediction
(causal wavefront) is inaccessible by 6 orders of magnitude.

The K₀ spatial shape — previously thought to be characteristic of the telegrapher —
is ALSO produced by 2D screened diffusion. This is a new finding that further
collapses the discriminating content of C2.

Classification confirmed: T-D (persistence fails) and T-B (even if it succeeded,
conventional physics reproduces the observables).
