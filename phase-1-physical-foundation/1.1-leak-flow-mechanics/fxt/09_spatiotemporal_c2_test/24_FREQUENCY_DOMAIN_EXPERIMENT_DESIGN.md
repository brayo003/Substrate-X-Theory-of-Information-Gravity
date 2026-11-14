# Document 24 — Frequency-Domain Experiment Design
## Phase 9: Cross-Spectral Noise Correlation Protocol

**Date:** 2026-08-21  
**Status:** PREREGISTERED — written before simulation execution  
**Critical task:** Determine whether frequency-domain CSD distinguishes C2 from OU

---

## 1. The Central Question

The previous experiment established that the temporal coherence function C(t) is
mathematically identical for C2 and OU:

```
C_C2(t) = C_OU(t) = exp(-Γ·τ_B·[t/τ_B - 1 + exp(-t/τ_B)])
```

Does moving to the frequency domain break this degeneracy?

---

## 2. Mathematical Degeneracy Analysis (Frequency Domain)

### 2.1 From Ramsey coherence to noise power spectrum

The Ramsey coherence at delay t is related to the phase noise by:

```
C(t) = exp(-Φ(t))    where   Φ(t) = ∫₀ᵗ dt'(t-t') S_φ(t')
```

where S_φ(t') is the two-time noise correlation function. For a stationary Gaussian process:

```
Φ(t) = ∫₀^∞ S_φ(ω) F(ω,t) dω/π
```

where F(ω,t) = sin²(ωt/2)/(ω/2)² is the Ramsey filter function.

The noise power spectral density (PSD) is the Fourier transform of the noise autocorrelation:

```
S_φ(ω) = ∫₋∞^∞ R(τ) e^{-iωτ} dτ
```

### 2.2 C2 noise autocorrelation

From C2 theory (NM_PREDICTION_AUDIT.md, [EXACT-PHI]):

```
R_C2(τ) = (Γ_M / τ_B) · exp(-|τ| / τ_B)
```

This is an exponential decay with correlation time τ_B.

### 2.3 OU noise autocorrelation

The Ornstein-Uhlenbeck process has exactly:

```
R_OU(τ) = σ² · exp(-|τ| / τ_c)
```

with σ² = Γ_M/τ_B and τ_c = τ_B.

**These are identical: R_C2(τ) = R_OU(τ) when σ² = Γ_M/τ_B and τ_c = τ_B.**

### 2.4 Fourier transform → PSD

The Fourier transform of an exponential autocorrelation is a Lorentzian:

```
S_C2(ω) = S_OU(ω) = (2 Γ_M / τ_B²) · 1/(ω² + (1/τ_B)²)
                  = (2 Γ_M / τ_B²) · 1/(ω² + ω_c²)
```

where ω_c = 1/τ_B.

**CONCLUSION: The single-qubit PSD is IDENTICAL for C2 and OU.**

A Lorentzian spectrum with corner frequency f_c = 1/(2πτ_B) is predicted by both.
Measuring it constrains τ_B but does NOT distinguish C2 from OU.

---

## 3. Does the Cross-Spectral Density (CSD) Break the Degeneracy?

### 3.1 Single-qubit PSD — degenerate (proven above)

### 3.2 Cross-spectral density S_ij(ω) — analysis

The cross-spectral density between qubits i and j is the Fourier transform of the
cross-correlation R_ij(τ) = <δφ_i(t) δφ_j(t+τ)>:

```
S_ij(ω) = ∫₋∞^∞ R_ij(τ) e^{-iωτ} dτ
```

**Under C2:** The cross-noise comes from the same PRW substrate field. At separation d:

```
R_ij^C2(τ) = exp(-d/ξ_c) · (Γ_M/τ_B) · exp(-|τ|/τ_B)
```

i.e., the spatial factor exp(-d/ξ_c) **multiplies** the same Lorentzian autocorrelation.

The CSD is:

```
S_ij^C2(ω) = exp(-d/ξ_c) · S_ii(ω)     [C2]
```

**Under OU (independent baths):** Each qubit has its own independent OU bath.

```
R_ij^OU-indep(τ) = 0   for i ≠ j
```

So S_ij^OU-indep(ω) = 0.

**Under common-mode OU:** Both qubits share a single OU bath (common-mode noise):

```
R_ij^CM(τ) = f_cm · (Γ_M/τ_B) · exp(-|τ|/τ_B)
```

where f_cm is the common-mode fraction. This gives:

```
S_ij^CM(ω) = f_cm · S_ii(ω)             [common-mode]
```

### 3.3 Can CSD distinguish C2 from common-mode OU?

The C2 prediction: `S_ij = exp(-d/ξ_c) · S_ii`  
The CM-OU prediction: `S_ij = f_cm · S_ii`

These are **identical in form** — both predict S_ij proportional to S_ii.

The only difference:
- C2 predicts the proportionality constant **depends on qubit separation d**: `~ exp(-d/ξ_c)`
- CM-OU predicts it is **constant across all pairs**: `= f_cm`

**This is the SAME geometric test as the spatial correlation test in phase 8.**

The frequency domain adds NO new information for distinguishing C2 from CM-OU beyond
what spatial correlation already provided — unless we can measure the variation of
`S_ij(ω)/S_ii(ω)` with qubit separation d.

---

## 4. Is There Any Frequency-Domain Observable That IS C2-Specific?

### 4.1 Frequency-dependent spatial coherence

C2 makes a specific joint prediction:

```
γ_ij(ω) = S_ij(ω) / sqrt(S_ii(ω) · S_jj(ω)) = exp(-d_ij / ξ_c)
```

where ξ_c = 2cτ_B **is frequency-independent**.

For a conventional noise model with spatially extended correlations, ξ_c could be
frequency-dependent. C2 predicts **frequency-independent ξ_c** because the spatial
decay comes from the PRW propagator, which has a frequency-independent correlation length
in the relevant limit (d << ξ_c → spatial correlation is determined by τ_B, not ω).

**However:** At ξ_c >> chip size, this prediction reduces to γ_ij(ω) ≈ 1 for all pairs —
same problem as before.

### 4.2 Cross-spectral phase (frequency-domain propagation delay)

C2 predicts that the cross-spectral density carries a **phase delay**:

```
phase(S_ij(ω)) = ω · d_ij / c_C2
```

This arises because the substrate fluctuation propagates at finite speed c_C2 from
qubit i to qubit j, arriving after a time lag τ_prop = d_ij / c_C2.

**This is potentially C2-specific.** OU with common-mode noise predicts:
- If truly common-mode: phase(S_ij) = 0 (simultaneous)
- If causal propagation at speed c: phase(S_ij) = ω · d/c (same as C2)

But ANY correlated noise source with finite propagation speed would produce this phase.
It is not uniquely C2.

### 4.3 The propagation delay as potential discriminator

The propagation delay τ_prop = d/c_C2 is the only quantity that could in principle
constrain c_C2 from frequency-domain data. It requires:

1. Measuring the cross-spectral phase reliably
2. d/c_C2 >> 1/(sampling bandwidth) — the time delay must be resolvable
3. At d = 200 µm and c = 10⁴ m/s: τ_prop = 20 ns
4. For a 20 ns delay to be visible, need frequency resolution < 50 MHz
   and qubit coherence >> 20 ns (satisfied: T2* ~ 5 µs)
5. The phase must be measurable above shot noise — requires many repetitions

**Feasibility check:**

```
Δφ_prop = ω · d/c = 2π·f · 20ns
At f = 1 MHz:  Δφ = 2π × 20×10⁻³ = 0.126 rad
At f = 10 kHz: Δφ = 2π × 2×10⁻⁴ = 0.001 rad
```

The relevant noise bandwidth is set by τ_B: f_c = 1/(2πτ_B) = 32 kHz.
At the corner frequency, Δφ_prop = 2π × 32×10³ × 20ns = 4×10⁻³ rad.

**This is 0.004 rad — unmeasurable at realistic shot counts (would require ~10⁶ shots
per frequency bin).**

### 4.4 Summary: Does frequency domain break C2/OU degeneracy?

| Observable | C2 | OU (common-mode) | Distinguishable? |
|------------|-----|-----------------|-----------------|
| S_ii(ω) shape | Lorentzian | Lorentzian | **NO** |
| S_ij(ω)/S_ii(ω) magnitude | exp(-d/ξ_c) | f_cm (const) | Only if d ~ ξ_c |
| phase(S_ij(ω)) | ω·d/c | 0 or ω·d/c | NO (noise ~10⁻³ rad) |
| ξ_c(ω) frequency dependence | constant | possibly f-dep | Marginal |
| Cross-spectrum at d << ξ_c | ≈ S_ii | ≈ f_cm·S_ii | NO |

**Conclusion: The frequency-domain cross-spectral experiment is NON-DIAGNOSTIC for
distinguishing C2 from OU in the accessible parameter regime (d << ξ_c).**

The frequency domain does NOT break the C2/OU degeneracy.

---

## 5. What WOULD Break the Degeneracy

For completeness, these observables could in principle distinguish C2 from OU:

### 5.1 Spatial variation of CSD coherence with frequency-independent ξ_c
Requires d ~ ξ_c. At c = 10⁴ m/s, τ_B = 5µs: ξ_c = 10 cm. Chip must be ~10 cm.
**Not available.**

### 5.2 Higher-order cumulants (non-Gaussian noise)
C2 substrate noise comes from discrete PRW particles — potentially non-Gaussian.
OU is Gaussian by construction. A bispectral measurement could distinguish.
**Requires ~10⁸ shots per qubit; not practical.**

### 5.3 Transient cross-correlation after preparation
Prepare qubit i, measure correlations on qubit j as function of d and t.
Requires long-range entanglement-sensitive circuits.
**Requires full quantum gate fidelity on distant pairs; not achievable on simulation.**

### 5.4 Direct c_C2 measurement via delay
Measure δφ_ij(t) = φ_i(t) - φ_j(t + d/c) for varying d.
Requires d/c ~ ns resolution in timing.
**Not achievable: d/c = 20 ns at d = 200 µm, c = 10⁴ m/s. Shot noise >> signal.**

---

## 6. Experiment Design (Despite Non-Diagnostic Status)

The experiment is designed and simulated below to rigorously confirm the non-diagnostic
finding. This is required by the protocol — we do not merely assert non-diagnosticity,
we demonstrate it quantitatively.

### 6.1 Protocol: Repeated Phase Estimation (RPE)

**Observable:** Time series of Ramsey-estimated phases {φ_k(t)} at fixed delay t = t_probe,
repeated N_rep times, across Q qubits simultaneously.

**Procedure:**
1. Set Ramsey delay to t_probe (chosen to maximize phase sensitivity: t_probe ~ τ_B/2)
2. Execute Ramsey circuit on all Q qubits simultaneously
3. Record bit outcomes → estimate phase φ_i for each qubit
4. Repeat N_rep = 1024 times under identical conditions
5. Compute PSD: S_i(f) = |FFT({φ_i(k)})|² / N_rep
6. Compute CSD: S_ij(f) = FFT({φ_i(k)}) · conj(FFT({φ_j(k)})) / N_rep
7. Compute coherence: γ_ij(f) = |S_ij(f)| / sqrt(S_ii(f) · S_jj(f))
8. Fit S_ii(f) to Lorentzian: S(f) = A/(f² + f_c²), extract f_c → τ_B = 1/(2πf_c)
9. Fit |S_ij(f)/S_ii(f)| vs. d_ij: exponential → ξ_c

### 6.2 Sampling Parameters

| Parameter | Value | Justification |
|-----------|-------|---------------|
| t_probe | 2.5 µs (= τ_B/2) | Max phase sensitivity |
| N_rep | 1024 | 2¹⁰ for clean FFT |
| Repetition interval | 10 µs | >> τ_B for stationarity |
| Total acquisition | 10.24 ms per run | 1024 × 10 µs |
| Frequency resolution | 1/10.24ms = 98 Hz | << f_c = 32 kHz |
| Maximum frequency | 1/(2×10µs) = 50 kHz | covers f_c |
| Qubits | 7 (same heavy-hex) | |

### 6.3 C2 and OU Predictions

Both predict: **S_ii(f) = Lorentzian(f_c = 1/(2πτ_B))**

C2 additionally predicts: **γ_ij(f) = exp(-d_ij/ξ_c)** (frequency-independent)

OU + common-mode predicts: **γ_ij(f) = f_cm** (frequency-independent, constant)

The difference is whether γ_ij varies with d_ij.

**Both predictions are non-diagnostic at d << ξ_c:** γ_ij ≈ 1 for all pairs.

### 6.4 Preregistered Decision Criteria

| Condition | Result |
|-----------|--------|
| S_ii(f) well-fit by Lorentzian | Neither C2 nor OU confirmed |
| γ_ij varies exponentially with d | C2-compatible (not confirmed) |
| γ_ij constant across all d | Common-mode (neither C2 nor OU) |
| ξ_c extracted within factor 3 of C2 prediction | C2-compatible (not confirmed) |
| OU explains all observables equally | NON-DIAGNOSTIC |

### 6.5 Rejection Criterion

**The experiment is declared non-diagnostic if:** ΔAIC between C2 and OU+common-mode
models on the full set of S_ij(f) observables is < 6 on a pre-specified joint likelihood.

---

## 7. Hypothesis and Null Hypothesis

**H_C2:** The noise power spectrum S_ii(f) is Lorentzian with corner f_c = 1/(2πτ_B),
AND the cross-spectral coherence γ_ij(f) decays exponentially with qubit separation d
with length scale ξ_c = 2c_C2·τ_B.

**H_0 (OU common-mode):** S_ii(f) is Lorentzian AND γ_ij(f) = f_cm (constant, independent of d).

**Test:** Whether γ_ij(d) has exponential decay with ξ_c comparable to C2 prediction.

**Pre-registered failure condition:** d_max << ξ_c → test has no power (expected outcome
given chip geometry).

---

## 8. Power Analysis

At d/ξ_c = 0.006 (max qubit pair, c = 10⁴ m/s):

```
Δγ = γ(0) - γ(d_max) = 1 - exp(-0.006) = 0.006
```

To detect Δγ = 0.006 above noise requires:
- N_rep × N_qubits >> 1/Δγ² = 28,000 effective measurements
- With 7 qubits and 21 pairs: N_rep >> 1,300
- Shot noise per phase estimate: σ_φ ~ 1/sqrt(shots) ~ 0.011 rad (at 8192 shots)
- Phase noise in correlation: σ_γ ~ σ_φ²/sqrt(N_rep) ~ 10⁻⁶ (at N_rep=1024)

The noise floor on γ is ~10⁻⁶. The signal is ~10⁻³.  
**The signal IS above noise for the correlation coefficient.**

However, the reference common-mode level is 0.997 (from previous experiment). We need
to fit a 0.6% variation on top of a 99.7% common-mode. The relative precision needed is:

```
Δγ/γ = 0.006 / 0.997 = 0.006 = 0.6%
```

This is achievable in principle but requires careful common-mode subtraction.

**The limiting factor remains: ξ_c >> chip. Even if detected, the extracted ξ_c
will have > 1000% uncertainty (same problem as Document 19).**

---

*Simulation follows in Document 25 / script p24_freq_domain_sim.py.*
