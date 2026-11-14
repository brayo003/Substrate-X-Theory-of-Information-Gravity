# EXPERIMENTAL RESCUE AUDIT
## SXC-IGC / C2 — Can the Experimental Program Be Scientifically Rescued?

**Date:** 2026-08-22
**Status:** COMPLETE — STATE 4 (see Phase H)
**Context:** Follows FINAL_DESIGN_SEARCH.md, ADVERSARIAL_NULL_AUDIT.md,
  TWO_STAGE_STATISTICS_AUDIT.md, ESTIMATOR_AUDIT_FINAL.md, GAP7_THEORY_AUDIT.md,
  DISCRIMINATOR_SEARCH.md

**Central question:**
Is there a physically derived consequence of SXC-IGC that is:
  (a) genuinely different from conventional mechanisms,
  (b) measurable with realistic superconducting-qubit hardware,
  (c) identifiable against an adversarial conventional null family,
  (d) sufficiently constrained by the existing theory to count as a real test?

**Answer:** Not currently. See Phase H.

---

## PHASE A — THEORY INVENTORY

### A.1 Source Material Reviewed

- 01_foundations/C2_FOUNDATIONS.md (63 kB)
- 01_foundations/C2_FRONTIER_MAP.md (28 kB)
- 01_foundations/C2_MISSING_PRINCIPLES.md (18 kB)
- 02_derivations/substrate_transport_derivation.md (34 kB)
- 02_derivations/interaction_hamiltonian_derivation.md (22 kB)
- 02_derivations/effective_master_equation_derivation.md (19 kB)
- 03_audits/C2_final_prediction_audit.md (45 kB)
- 03_audits/C2_prediction_audit.md (50 kB)
- 09_spatiotemporal_c2_test/00_THEORY_AUDIT.md (45 kB)
- 09_spatiotemporal_c2_test/01_PREDICTION_DERIVATION.md (12 kB)
- 09_spatiotemporal_c2_test/02_2D_CORRELATION_DERIVATION.md (19 kB)
- 09_spatiotemporal_c2_test/FOUNDATIONAL_ADVERSARIAL_FINAL_AUDIT.md (22 kB)
- 11_v02_extension/NM_PREDICTION_AUDIT.md (9 kB)

### A.2 Complete Observable Inventory

| # | Observable | SXC-IGC prediction | Free params | Derivation | Conventional alternatives | Discriminating? | Class |
|---|-----------|-------------------|-------------|-----------|--------------------------|----------------|-------|
| 1 | Spatial K₀ covariance | C_Γ(r) = K₀(r/ξ_c)/K₀(a/ξ_c) | ξ_c, amp | Yes — 2D telegrapher Green function | Power-law (M7), two-bath (M9), Matérn (M11) | **No** — K₀ ≈ log ≈ power-law at r < 2ξ_c; SNR ≈ 2 over 11 bins | **D** |
| 2 | Spatial exponential (1D) | C_Γ(r) = A·exp(−r/ξ_c) | ξ_c, amp | Yes — 1D telegrapher limit | Any OU bath | **No** — identical form | **D** |
| 3 | Temporal ω² Ramsey | Γ_φ = Γ₀ + k_rot·ω² (low ω) | k_rot, Γ₀ | Yes — PSD Taylor expansion | Any bath with S_JJ(0) finite; any sub-Ohmic bath; any filter-function bath | **No** — proved non-unique (C2_final_prediction_audit, p25_discrimination_test.py) | **D** |
| 4 | Non-Markovian (NM) Ramsey onset | W(t) ~ exp(−Γt − Gt²/2) for t < τ_B | τ_B | Yes — short-time expansion of telegrapher propagator | Any bath with finite τ_B; any NM Lindblad model | **No** — shape indistinguishable from generic NM bath | **C** |
| 5 | Lorentzian spectral rolloff | S_JJ(ω) = 2S₀τ_B/(1+ω²τ_B²); Γ_φ ∝ 1/ω² above ω_c = 1/τ_B | τ_B, S₀ | Yes — PRW PSD derivation | Any bath with Lorentzian spectrum (OU process, RC filter) | **No** — identical spectral form | **C** |
| 6 | Multi-qubit Γ_φ fluctuation spatial correlation | Cov(δΓ_i, δΓ_j) = g²S₀K₀(r_ij/ξ_c) | ξ_c, amp | Yes (same spatial kernel) | EM crosstalk, phonon bath, substrate phonon | **No** — same K₀ degeneracy applies | **D** |
| 7 | Joint spatial + NM temporal structure | C_Γ(r,τ) = K₀(r/ξ_c) · exp(−τ/τ_B) · [1 + τ²/τ_B² for small τ] | ξ_c, τ_B, amp | Derived (2D spatiotemporal correlator) | Two independent conventional baths each with respective τ, ξ | **No** — conventional two-bath M9 matches; no fixed ratio constraint | **C** |
| 8 | **P3 self-consistency:** c = ξ_c/(2τ_B) | Both τ_B and ξ_c set by same substrate speed v | none (given measured pair) | Yes — ξ_c = v/λ = 2vτ_B | Phonon bath: c = v_sound (~5000 m/s); EM: c = c_light; independent defects: no link | **Conditional** — if c_measured ≪ v_sound, anomalous | **B** |
| 9 | c(T) = ξ_c(T)/(2τ_B(T)) constant vs temperature | Both ratios track the same substrate material property | none | Yes — v is material property, T-independent | 1/f flux noise: τ_B(T) and ξ_c(T) may change independently; no constraint | **Conditional** — valid discriminator if T-variation accessible | **A*** |
| 10 | Γ_φ amplitude–scale relation | g²S₀ and ξ_c both set by same substrate density and coupling | g, ρ, ξ_c | Not derived from first principles | Any bath with independent amplitude and length scale | **No** — two free parameters, no constraint | **D** |
| 11 | Cross-qubit echo / DD response | Phase-echo refocusing of spatial correlations | ξ_c, τ_B | Implied but not derived | Standard DD theory for any correlated bath | **No** — form identical to generic correlated bath | **C** |
| 12 | Anisotropy of spatial correlations | Substrate isotropic → C_Γ(r) isotropic | none | Yes — PRW is isotropic | Any isotropic noise source | **No** — isotropy is not distinctive | **C** |

*A* = theory-correct but hardware-inaccessible at present.

### A.3 Classification Summary

| Class | Count | Candidates |
|-------|-------|-----------|
| A (discriminating, but hardware-inaccessible) | 1 | c(T) = const vs temperature |
| B (theory-derived, conditionally discriminating) | 1 | P3: c = ξ_c/(2τ_B) |
| C (measurable, not uniquely SXC-IGC) | 5 | NM onset, Lorentzian rolloff, spatiotemporal joint, anisotropy, echo |
| D (rejected — degenerate or non-unique) | 5 | K₀ shape, exp shape, ω² temporal, amplitude–scale, Γ_φ fluctuation |

No class-A observable is currently executable. One class-B observable (P3) is
the strongest available discriminator but is also not executable on current hardware
(NMP = 0.033 << 0.1 required for τ_B extraction).

---

## PHASE B — ADVERSARIAL NULL CONSTRUCTION

### B.1 For the K₀ Spatial Experiment (primary route, now failed)

The adversarial null family that defeats the K₀ test:

| Model | Physical basis | Why plausible on IBM chips | FP rate (300 trials) |
|-------|----------------|---------------------------|----------------------|
| M0: Independent Markovian | No spatial correlation | Baseline | 0.0% |
| M2: Exponential / OU | 1/f flux noise with short correlation | Standard qubit noise | 4.7% |
| M5: EM crosstalk | Control-line coupling, readout | IBM documented at ~0.5–1% | 0.0% |
| **M7_pow0.5: Power-law α=0.5** | 1/f flux noise diffusing from distributed defects | Well-documented for SC qubits | **13.3%** |
| **M7_pow1.0: Power-law α=1.0** | 1/f flux noise with steeper spatial decay | Same physical origin | **19.7%** |
| M8_gauss: Gaussian | Thermal phonon bath with short correlation | Low-T thermal | 0.0% |
| **M9_twobath: Two-bath exponential** | Two simultaneous OU noise sources with different ξ | Independent TLS populations + EM | **15.3%** |
| M10_stretch: Stretched exponential | Heterogeneous defect distribution | Multi-TLS | 1.3% |
| M11_matern: Matérn (ν=1.5) | Spatially correlated defect cluster | Impurity clusters | 0.3% |

Three models fail at FP > 10%. All three are physically motivated for superconducting chips.
Worst-case FP = 19.7%. Required: ≤ 10%. The null gate fails.

### B.2 For the P3 Self-Consistency Test

If P3 could be executed, the adversarial null family would need to include:

| Mechanism | Predicted c | Would it defeat P3? |
|-----------|-------------|---------------------|
| Phonon bath (Si bulk acoustic) | ~5000–8000 m/s | Only if c_measured ≈ v_sound |
| EM coupling through control lines | ~2×10⁸ m/s | No — very different |
| Independent TLS population | No finite-speed propagation | N/A — no ξ_c |
| Quasiparticle diffusion | ~10⁴–10⁶ m/s | Distinguishable from slow c |
| Phonon-mediated two-TLS coupling | ~v_sound | Only if c_measured ≈ v_sound |

If the measured c were, for example, 10–500 m/s, no conventional mechanism
predicts this specific ratio, and P3 would be genuinely discriminating. However,
at NMP = 0.033, τ_B cannot be reliably extracted from Ramsey curvature, so the
P3 test cannot be attempted on Brisbane.

### B.3 Null Family for All Other Candidates

All class-C observables (NM onset, Lorentzian rolloff, spatiotemporal joint,
anisotropy, echo) are defeated by the same adversarial family. The conventional
bath matching argument applies to each: any observable that depends only on the
autocorrelation function of the noise (or its spatial analog) can be matched by
a conventional bath model with the appropriate PSD and length scale.

The PRW substrate produces a specific functional form for S_JJ(ω) and C_JJ(r).
Both are Lorentzian in frequency and K₀/exponential in space. Both forms appear
in standard classical noise models. This is the fundamental identifiability limit.

---

## PHASE C — IDENTIFIABILITY ANALYSIS

### C.1 K₀ Spatial Experiment — Quantitative Failure Analysis

**Shape distance (K₀ vs power-law, α=0.5):**
Over r/ξ_c ∈ [0.2, 2.2] with 11 bins:
```
||K₀(r/ξ_c) − (r/ξ_c)^{−α}||₂ / ||K₀||₂ = 0.073
```

**Shot noise per bin:**
At N = 8192 shots, 10 time points, σ_C ≈ 0.012 per bin.

**Shape discrimination SNR:**
```
SNR = shape_distance × signal_amplitude / shot_noise
    = 0.073 × 0.20 / 0.012 ≈ 1.2
```

This is below the threshold SNR ≈ 3 needed for reliable discrimination.

**LLR distributions (directly measured, 30 trials each):**

| Data | LLR mean | LLR std | P(LLR > threshold) |
|------|----------|---------|---------------------|
| K₀ data (ξ_c=0.5mm, sub_frac=0.20) | +0.177 | 0.392 | 0.000 |
| M7_pow0.5 data | −0.240 | 0.263 | 0.000 |

Separation: 0.42 units. Noise width: ~0.35 std. The distributions overlap strongly.
The test has zero discriminating power at the frozen threshold 1.289.

**Can more shots fix this?**
No. The failure is geometric, not shot-noise limited.

Proof: the LLR separation scales as √N × shape_distance × amplitude.
At N = 8192 shots, LLR separation ≈ 0.42 (measured).
To reach separation > 3 (required for reliable discrimination):
```
N_required = 8192 × (3/0.42)² ≈ 420,000 shots per configuration
```
This is 51× more shots. At 5 µs per shot, 420k shots ≈ 2.1 s per pair,
times 66 pairs = 139 s per time point, times 10 time points = 23 minutes.
This already exceeds the 10-minute budget, and it assumes the null models
remain fixed rather than absorbing the additional signal with additional DoF.

In practice, with more shots the best-null fitter also fits better, so the
LLR separation does not scale as cleanly as the above estimate. The fundamental
issue is shape degeneracy, not shot count.

**Can a different fitter resolve the degeneracy?**
No. Any fitter that includes a power-law or two-bath null model will fit the
K₀ signal nearly as well as the K₀ model itself, because the shapes are
geometrically close over the available spatial range. Increasing the flexibility
of the null fitter improves its K₀-fitting ability, which reduces the LLR.

**Can extending the spatial range fix this?**
Yes — this is the only fix. The shape distance increases rapidly at r > 2ξ_c:
```
At r = 5ξ_c: K₀(5) ≈ 0.0037 vs powerlaw(5) ≈ much larger
The shape difference is logarithmic beyond r = 2ξ_c
```
With pairs spanning 0.1–10 ξ_c (≥ 30 bins), the shape SNR would reach ≈ 5–8,
which would be sufficient. But this requires qubit separations of 0.1–10 × 0.5 mm
= 50 µm – 5 mm. Brisbane maximum separation is 3.7 mm and the minimum is 200 µm.
A ×4–×8 larger chip, or a relay-measurement protocol, would be needed.

### C.2 P3 Self-Consistency Test — Identifiability

**τ_B measurement from NM Ramsey curvature:**
The Gaussian onset W(t) ≈ exp(−Γ_φt − G·t²/2) where G = g²S₀ × τ_B.
The curvature term G requires measuring the t² deviation from exponential decay.

The NMP (Non-Markovianity Parameter) quantifies this:
```
NMP = G / Γ_φ² = τ_B · Γ_φ
```
On Brisbane: τ_B ≈ 5 µs, Γ_φ = 1/T₂ ≈ 1/(150 µs) = 6667 s⁻¹.
```
NMP = 5×10⁻⁶ × 6667 = 0.033
```

For reliable τ_B extraction, NMP > 0.1 is required (from 11_v02_extension/NM_PREDICTION_AUDIT.md).
The fractional deviation from pure exponential Ramsey is ~NMP²/8 ≈ 0.014% — below
noise at any realistic shot count.

To reach NMP = 0.1, we need τ_B × Γ_φ = 0.1.
Given Γ_φ is fixed by T₂, this requires τ_B ≥ 15 µs.
Current estimate: τ_B ≈ 5 µs. Factor of 3 shortfall.
No hardware adjustment within IBM Open Plan can change this.

**ξ_c measurement with P3:**
Even if τ_B were measurable, the ξ_c measurement from spatial K₀ covariance faces
the K₀/power-law degeneracy described in C.1. The extracted ξ_c would be uncertain
because the fit cannot determine whether the spatial decay is K₀ or power-law.

Therefore P3 has two simultaneous hardware blockers:
1. τ_B not measurable at NMP = 0.033
2. ξ_c not measurable at SNR ≈ 2 over available spatial range

### C.3 Fisher Information Analysis (K₀ experiment)

For a single-parameter test (ξ_c), the Fisher information from 11 separation bins:
```
I(ξ_c) = Σ_r (∂C_Γ/∂ξ_c)² / σ²(r)
```
At ξ_c = 0.5 mm, sub_frac = 0.20, σ_C = 0.012:
```
I(ξ_c) ≈ 0.20² × 11 × (0.073/0.5)² / 0.012² ≈ 540 mm⁻²
Δξ_c (1σ) ≈ 1/√540 ≈ 0.043 mm
```
This looks precise. But the problem is that the power-law α and amplitude are
also free parameters, and the power-law curve has similar Fisher information.
The joint fit has degenerate directions: changing ξ_c while adjusting α and
amplitude gives nearly the same predicted C_Γ(r). The Fisher matrix has
near-singular directions, so the Cramér-Rao bound is not the binding constraint.
The binding constraint is the inter-model shape distance = 0.073, which cannot
be increased by improving the estimator.

---

## PHASE D — IS THE K₀ FAILURE FUNDAMENTAL?

### D.1 Classification of the Failure

The K₀ spatial experiment fails for reason 7: **fundamental identifiability
degeneracy**. To confirm this and rule out other causes:

| Failure mode | Evidence | Status |
|---|---|---|
| 1. Estimator failure | Estimator bias < 0.001 (ESTIMATOR_AUDIT_FINAL.md) | **NOT the cause** |
| 2. Statistical test failure | Correct LLR formulation; threshold independently calibrated | **NOT the cause** |
| 3. Insufficient null modelling | Original null set was insufficient; extended to 9 models | Was a cause, now corrected |
| 4. Insufficient geometry | Only 11 bins over 0.2–2.2ξ_c; K₀/powerlaw separation requires >2ξ_c | **CONTRIBUTING** |
| 5. Insufficient signal amplitude | Power = 0 even at sub_frac=0.30 and 16384 shots | **NOT the cause** |
| 6. Missing theoretical constraint | c is free (GAP-7); ξ_c is free | **CONTRIBUTING** |
| 7. Fundamental identifiability degeneracy | Shape distance = 0.073 << noise; LLR separation = 0.42 units | **PRIMARY CAUSE** |

The primary failure is geometric degeneracy: over the accessible spatial range
(0.2–2.2 ξ_c), K₀ and power-law are both approximately logarithmic. This is
not a consequence of any finite-sample statistical issue. It is the geometry of
the two functions over the specific interval.

### D.2 Proof That the Failure Is Geometric, Not Statistical

At r/ξ_c ∈ [0.2, 2.2], both K₀ and (r/ξ_c)^{−α} have the asymptotic form:
```
K₀(x) ≈ −ln(x/2) − γ_E  for x << 1 (Euler-Mascheroni γ_E = 0.5772)
K₀(x) ≈ √(π/2x)·exp(−x) for x >> 1
```
In the intermediate regime [0.2, 2.2], K₀ transitions from logarithmic to
exponential. Over the same range, a power-law (r/ξ_c)^{−0.5} also decreases
from ~2.2 to ~0.67, closely tracking the K₀ curve.

The normalised L2 distance was measured at 0.073. This means 92.7% of the
K₀ shape variance is shared with the best-fit power-law. The remaining 7.3%
is distinctive K₀ content. At measurement noise of ~0.012 per bin and signal
amplitude 0.20, the distinctive signal is:
```
distinctive_signal = 0.073 × 0.20 = 0.0146
noise_per_bin = 0.012
SNR_per_bin = 0.0146 / 0.012 = 1.22
```
With 11 bins, the global SNR = 1.22 × √11 ≈ 4.0.

This appears sufficient, but:
- The null model has its own free parameters (α, amplitude) which absorb ~2 DoF
- After marginalising over these, the effective SNR ≈ 2.0
- The LLR test statistic has mean separation 0.42 ≈ SNR_eff²/2 as expected

This is consistent with the directly measured LLR separation.

**Conclusion:** The geometric degeneracy is real, quantified, and fundamental.
It cannot be resolved by any statistical technique without changing the geometry
(more bins, longer baseline) or the theory (constraining ξ_c independently).

---

## PHASE E — SEARCH FOR A REAL DISCRIMINATOR

### E.1 Search Strategy

Searched for any observable satisfying all four criteria:
(a) derivable from C2 theory
(b) not reproduced by conventional noise models
(c) measurable on realistic superconducting hardware
(d) sufficiently constrained to constitute a real test

Specifically searched for:
- Fixed relations between spatial and temporal scales
- Observables with no free conventional counterpart
- Scaling laws with theory-determined exponents
- Multi-point correlations that break degeneracy
- Controlled-perturbation responses
- Cross-frequency or cross-device predictions

### E.2 Results

**Fixed spatial-temporal relation (P3):**
C2 predicts ξ_c = 2c·τ_B. This links two independently measurable quantities
via the substrate speed c. If both are measured and c is found to differ from
all known propagation speeds, this is genuinely anomalous.

Status: Class B — conditionally discriminating. Requires NMP > 0.1 (not currently
available on Brisbane) and ξ_c measurable (blocked by K₀/power-law degeneracy).

**Frequency-dependent spatial cross-correlation:**
C2 predicts that the spatial correlation is the same kernel at all frequencies
(K₀ shape is frequency-independent because the substrate is spatially stationary).
A conventional multi-bath model might predict different spatial kernels at
different frequencies (each bath has its own ξ). This is potentially discriminating.

However, measuring C_Γ(r, ω) — the spatial correlation as a function of both
qubit separation and Ramsey frequency — requires a 2D sweep. This would require
>>10 minutes of QPU time and is not feasible within the current allocation.
Furthermore, a sufficiently flexible two-bath model with identical spatial kernels
at all frequencies would match the C2 prediction, so the discriminating power
is conditional on the null family not including frequency-independent multi-bath.

Status: Class C — in principle testable but not currently executable.

**Spatial correlation under dynamical decoupling:**
Under pulse sequences that filter low frequencies, the spatial correlation should
be suppressed proportional to the spectral filter function. C2 predicts a specific
dependence through the Lorentzian PSD. This is the same dependence any Lorentzian
bath would predict, so it is not uniquely SXC-IGC.

Status: Class C — not uniquely SXC-IGC.

**Three-qubit or higher multi-point correlations:**
C2 predicts:
```
C_ijk(r_i, r_j, r_k) ∝ K₀(r_ij/ξ_c) · K₀(r_ik/ξ_c) · (triangle closure relation)
```
In the Gaussian substrate approximation, higher-order correlations factorise
into products of two-point correlations. This means any Gaussian noise source
with the same two-point spatial kernel would produce the same three-point
correlations. A non-Gaussian substrate would be distinctive — but C2 is
formulated as a Gaussian substrate (linear coupling, Gaussian PSD).

Status: Class C for Gaussian C2. Would require non-Gaussian extension of C2
that is not in the existing theory.

**Amplitude-scale consistency (g² and ξ_c from same substrate):**
C2 predicts that both the amplitude (g²S₀) and the scale (ξ_c) are determined
by the substrate parameters. In principle, measuring both and comparing to the
relation g²S₀ ∝ ρ²v²/λ (substrate density × speed / reversal rate) would test
C2. But this relation introduces the substrate density ρ as an additional free
parameter. With g, ρ, v, and λ all free, the amplitude-scale relation adds no
constraint.

Status: Class D — too many free parameters.

**Conclusion of Phase E:**
No discriminator was found that satisfies all four criteria simultaneously.
The P3 relation is the strongest candidate, but it requires hardware conditions
not currently available. No other theoretical structure in C2 produces an
observable that conventional noise cannot match while preserving all the same
two-point statistical properties.

---

## PHASE F — HARDWARE REALITY

### F.1 Current Hardware (IBM Brisbane, Open Plan)

| Constraint | Value | Implication |
|-----------|-------|------------|
| Qubit count | 127 | Sufficient for any proposed experiment |
| Min. separation | 200 µm | Sets UV cutoff |
| Max. separation | 3688 µm | Limits ξ_c reach to ≤ ~750 µm |
| T₂ median | 150 µs | Limits Ramsey range |
| T₁/T₂ ratio | 1.55 | Marginal; pure dephasing approximation strained |
| NMP = τ_B·Γ_φ | 0.033 | τ_B not extractable from Ramsey curvature |
| QPU budget | 10 min | Circuit execution time |
| Queue access | Open Plan, hours–days queue | Not blocking |
| Temperature control | None | Δc(T) test impossible |

### F.2 What Would Be Required for P3 (Strongest Discriminator)

| Requirement | Current situation | Gap |
|------------|-------------------|-----|
| NMP ≥ 0.1 for τ_B extraction | NMP = 0.033 | Factor of 3× |
| Spatial range 0.1–10 ξ_c for ξ_c extraction | 0.2–2.2 ξ_c (11 bins) | Factor of ~5× extension needed |
| No M7/M9 confounds on ξ_c measurement | M7 and M9 defeat the test | Need independent null exclusion |
| Independent prediction of c or ξ_c | GAP-7; c not predicted | Theory incomplete |

### F.3 What Would Be Required for c(T) Discriminator (Class A)

| Requirement | Current situation | Gap |
|------------|-------------------|-----|
| Two different dilution fridge temperatures | IBM Open Plan: fixed T | No access |
| Same qubits at both T | Requires dedicated QPU session | No access |
| τ_B extractable at both T | NMP = 0.033 | As above |

The c(T) discriminator requires equipment not available through IBM Open Plan.
It would require dedicated access to a dilution fridge with controllable base
temperature, such as a local lab cryostat or a specialized QPU provider with
temperature control.

### F.4 Relay Circuits (Alternative for Spatial Range Extension)

A relay-measurement protocol would use intermediate ancilla qubits to transfer
entanglement to distant qubit pairs, effectively measuring correlation at
separations beyond the native geometry. This requires multi-step SWAP or teleportation
circuits, which:
- Add gate error at each hop (~0.1–0.3% per CNOT)
- Require additional circuit depth (~40–80 gates per relay step)
- Reduce coherence of the correlated state being measured
- Were not validated against the adversarial null family

No relay protocol has been designed or validated for this experiment. This is a
speculative path that would require significant new circuit design and validation
work, and does not solve the null family problem (M7 and M9 would still defeat
any relay-extended spatial measurement).

---

## PHASE G — GAP-7 ANALYSIS

Full analysis in GAP7_THEORY_AUDIT.md. Summary:

**The substrate propagation speed c cannot be derived from the C2 theory.**

C2 introduces a persistent random walk (PRW) with speed v = h/Δt and reversal
rate λ. The derived observables are:
- τ_B = 1/(2λ)
- ξ_c = v/λ = 2vτ_B
- PSD S_JJ(ω) = 2S₀τ_B/(1+ω²τ_B²)
- Spatial kernel K₀(r/ξ_c) (2D)

v appears in every result but is never constrained by any equation in the theory.
No dispersion relation, no equilibrium condition, no thermodynamic argument, and
no dimensional constraint selects a value for v.

**Consequence for falsifiability:**
- The theory predicts: "spatial correlations have K₀ shape at some scale ξ_c"
- The theory does NOT predict: "ξ_c has a specific value"
- Therefore, any observation of K₀-shaped spatial correlation at any ξ_c is
  "consistent with the theory" — but so is any other observation, since ξ_c
  can always be adjusted post-hoc.

This is a weak form of falsifiability. The theory would be falsified by:
1. Observation that C_Γ(r) is NOT K₀-shaped for any ξ_c (while spatial
   correlation definitely exists)
2. Violation of the self-consistency: measured ξ_c/(2τ_B) changes across
   experimental conditions in a way inconsistent with a fixed substrate speed

Neither falsification route is currently accessible on Brisbane.

**What must be solved before the experiment becomes falsifying:**

GAP-7 requires one of:
A. External physical identification of the substrate medium (determines c)
B. Additional dynamical principle in C2 that constrains v (new theory)
C. Experimental measurement of c = ξ_c/(2τ_B) at NMP ≥ 0.1 (requires new hardware)

---

## PHASE H — DECISION TREE

### H.1 Assessment of Each State

**STATE 1 — RESCUABLE NOW:**
A valid discriminator exists, is theory-derived, survives adversarial nulls,
and is implementable with realistic hardware.

**Assessment: NO.**

No discriminator satisfying all four criteria simultaneously exists on IBM
Brisbane Open Plan within the 10-minute budget. The K₀ spatial test fails
the adversarial null gate (FP = 19.7% > 10% against M7_pow1.0). The P3
self-consistency test fails the hardware gate (NMP = 0.033 < 0.1). No other
class-A observable was found.

**STATE 2 — RESCUABLE WITH THEORETICAL WORK:**
The experimental concept has a plausible route, but one or more missing
theoretical derivations must first constrain currently free quantities.

**Assessment: PARTIALLY YES — but insufficient alone.**

The key missing derivation is c from first principles. If C2 theory could
be extended to predict c (e.g., by identifying the physical substrate and
its propagation speed), then ξ_c would become a parameter-free prediction,
the P3 test would become a genuine quantitative test, and the K₀ experiment
would gain discriminating power by testing at a specific (predicted) ξ_c.

However, theoretical work alone is insufficient — it must be accompanied by:
- Hardware with NMP ≥ 0.1 for τ_B extraction (STATE 3 requirement)
- Spatial range 0.1–10 ξ_c for K₀/power-law resolution (STATE 3 requirement)

**STATE 3 — RESCUABLE WITH HARDWARE/GEOMETRY:**
The theory contains a valid discriminator, but current Brisbane geometry/hardware
cannot resolve it.

**Assessment: PARTIALLY YES — but insufficient alone.**

If the spatial range were extended to 0.1–10 ξ_c and if τ_B were measurable
(NMP ≥ 0.1), the P3 self-consistency test would be executable. The hardware
gap is:
- Spatial range: factor of ~5 extension needed (5 mm vs 3.7 mm max)
- NMP: factor of 3 shortfall (need τ_B ≈ 15 µs vs current 5 µs)

However, hardware improvement alone is insufficient — the theory must also
predict c (or at least constrain ξ_c) to produce a parameter-free test rather
than a post-hoc measurement. Without theoretical constraint, measuring c from
ξ_c/(2τ_B) is informative but not a controlled test of the theory.

**STATE 4 — NOT CURRENTLY RESCUABLE:**
The theory does not currently provide a sufficiently constrained observable
that can distinguish SXC-IGC from conventional physics.

**Assessment: YES — this is the correct state.**

The conjunction of GAP-7 (c is free), the K₀/power-law geometric degeneracy,
and the NMP = 0.033 hardware limitation means that no currently available
experimental route can distinguish SXC-IGC from physically plausible
conventional mechanisms, using existing theory and existing IBM Brisbane hardware.

### H.2 Final Classification

**STATE 4 — NOT CURRENTLY RESCUABLE**

Both theoretical and hardware conditions must improve before the experimental
program can produce a scientifically defensible result. The required improvements
are:

**Theoretical (necessary precondition):**
- GAP-7 must be resolved: c must be independently predicted or identified
- Without this, any spatial measurement is a post-hoc measurement of ξ_c,
  not a test of the theory

**Hardware (necessary precondition, parallel):**
- NMP ≥ 0.1 for τ_B extraction: requires τ_B ≈ 15–50 µs or T₂ << T₂_Brisbane
- Spatial range 0.1–10 ξ_c with ≥ 20 unique bins
- Independent exclusion of M7/M9 spatial correlation on the specific chip

**Neither condition alone is sufficient. Both are required.**

Until both conditions are satisfied, no hardware execution is authorized.

---

## Summary Table

| Phase | Finding | Status |
|-------|---------|--------|
| A: Theory inventory | 12 candidates evaluated; 1 class-A (hardware-inaccessible), 1 class-B (conditionally discriminating, hardware-blocked), 5 class-C, 5 class-D | Complete |
| B: Null construction | Full adversarial null family; K₀ test defeated by M7/M9 (FP 13–20%) | Complete |
| C: Identifiability | K₀/powerlaw SNR ≈ 2; P3 blocked by NMP = 0.033; quantified in detail | Complete |
| D: Failure mode | Primary cause is geometric degeneracy (shape distance 0.073); not shot noise, not estimator | Complete |
| E: Discriminator search | No new discriminator found; P3 is strongest existing candidate | Complete |
| F: Hardware reality | NMP shortfall ×3; spatial range shortfall ×5; T-variation inaccessible | Complete |
| G: GAP-7 | c fundamentally free; structural incompleteness; not resolvable from existing theory | Complete |
| H: Decision | **STATE 4 — NOT CURRENTLY RESCUABLE** | **Final** |

---

*Audit completed: 2026-08-22*
*All findings frozen. Not revisable post-hoc.*
*This document supersedes FINAL_PRE_HARDWARE_GATE.md (v3) for the rescue decision.*
