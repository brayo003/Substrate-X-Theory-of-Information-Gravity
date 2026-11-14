# ADVERSARIAL NULL AUDIT
## SXC-IGC Spatial Correlation Experiment

**Date:** 2026-08-22
**Script:** adversarial_diagnosis.py, two_stage_test.py
**Conclusion:** NULL GATE FAILS — M7 and M9 produce unacceptable FP rates

---

## 1. Prior Null Family (Insufficient)

The original bounded_design_search.py only tested K0 against:
- M0: independent Markovian (no correlation)
- M2: single exponential
- M5: EM crosstalk (exponential, short range)

These all passed (FP < 2%). But they are all members of the same functional
class: monotonically decaying exponential functions. The K0 Bessel function
also decays monotonically, so a simple LLR test vs an exponential null
was never going to control FP against heavier-tailed models.

---

## 2. Adversarial Models and Physical Motivations

### M7: Power-law covariance
```
C(r) = A * (r/r₀)^{-alpha}
```
**Physical motivation:** 1/f noise in superconducting qubits has been
extensively documented (Yoshihara et al. 2006, Bylander et al. 2011).
The spatial version arises from charge/flux noise with long-range
correlations from nearby two-level systems or trapped charges. Power-law
spatial correlations are a natural consequence of a distribution of
defect positions with no characteristic length scale.

Alpha values tested: 0.5, 0.8 (diagnosis), 1.0 (two_stage_test).

**Diagnosis result (adversarial_diagnosis.py):**
- M7_alpha=0.5: FP = 54.3% under prior K0 vs exp fitter
- M7_alpha=1.0: FP = 33.7%
- Root cause: power-law has heavier tail than exponential at large r.
  K0 also has a heavier tail than exponential (logarithmic behaviour).
  The K0 fitter absorbs power-law data by choosing xi_c → minimum
  bound (0.1 mm), fitting the short-range shape with K0's inner region.

**Two-stage test result (corrected K0 vs best-null fitter):**
- M7_alpha=0.5: FP = 13.3% — FAIL
- M7_alpha=1.0: FP = 19.7% — FAIL

Power-law cannot be controlled even when the null fitter explicitly
includes a power-law competitor. The K0 model remains too flexible.

### M9: Two-bath / multi-scale covariance
```
C(r) = A₁·exp(-r/ξ₁) + A₂·exp(-r/ξ₂)
```
with ξ₁ = 250 µm, ξ₂ = 1500 µm, A₁ = 0.08, A₂ = 0.05.

**Physical motivation:** Two independent noise sources with different
spatial ranges: (1) short-range EM crosstalk from neighbouring circuit
elements (ξ ~ 250-500 µm); (2) longer-range correlated flux noise or
thermal vibrations from the dilution refrigerator cold finger (ξ ~ 1-3 mm).
Both are known sources in superconducting qubit experiments.

**Diagnosis result:**
- FP = 25.3% under prior fitter
- Root cause: the slow component (ξ₂ = 1.5 mm) mimics K0's long tail
  in the 200-2200 µm range. K0 cannot be distinguished from a sum of
  two exponentials with similar length scales over only 11 unique r bins.

**Two-stage test result:**
- M9: FP = 15.3% — FAIL

### M8: Gaussian covariance — PASSES
```
C(r) = A * exp(-(r/sigma)^2)
```
FP = 0.0% (diagnosis), 0.0% (two-stage). Gaussian decays faster at
large r than K0, so the best-null fitter correctly identifies it.

### M10: Stretched exponential — PASSES
```
C(r) = A * exp(-(r/xi)^beta), beta = 0.7
```
FP = 6.7% (diagnosis), 1.3% (two-stage). Marginal but passes.

### M11: Matérn (nu=1.5) — PASSES
```
C(r) = A * (1 + sqrt(3)*r/xi) * exp(-sqrt(3)*r/xi)
```
FP = 0.7% (diagnosis), 0.3% (two-stage). Passes.

---

## 3. Root Cause Analysis

### Why does K0 not separate from power-law over the chip?

The 12-qubit chain provides separations r = 200–2200 µm with only
**11 unique separation bins** (in 200 µm steps). At ξ_c = 1 mm:
- Pairs span 0.2–2.2 in units of ξ_c
- In this regime, K0(r/ξ_c) ≈ −ln(r/ξ_c) + const (logarithmic)
- Power-law r^{-alpha} can be approximated locally by −alpha*ln(r) + const

**Both K0 and power-law are approximately logarithmic over the accessible range.**
They differ in their curvature (second derivative of log) but 11 noisy
data points cannot resolve this curvature reliably.

Quantitative evidence:
- Normalised L2 distance (K0 vs M7_alpha=1.0): **0.073** over 66 pairs
- Measurement noise: 0.036 per pair
- SNR: 0.073/0.036 = **2.0**

An SNR of 2.0 is marginal for shape discrimination. With 11 unique bins,
the effective discriminating degrees of freedom are ~5–8, insufficient to
resolve the K0/power-law distinction at this noise level.

### Why does K0 not separate from two-bath over the chip?

A sum of two exponentials at scales 250 µm and 1500 µm, when sampled
at the 11 bins of the 12-qubit chain, looks very similar to K0(r/1mm):

- Short component: rises steeply near r=0, decays by r=1mm
- Long component: provides a slow background across the full range
- Combined: creates a "fast decay + slow tail" that mimics K0

The K0 fitter chooses xi_c such that K0's transition region coincides
with the scale of the short component, fitting the composite effectively.

---

## 4. Full Null Family (Updated)

| Model | Description | FP (two-stage) | Status |
|-------|-------------|----------------|--------|
| M0 | Independent Markovian | 0.0% | PASS |
| M2 | Single exponential | 4.7% | PASS |
| M5 | EM crosstalk (exp) | 0.0% | PASS |
| **M7_pow0.5** | **Power-law alpha=0.5** | **13.3%** | **FAIL** |
| **M7_pow1.0** | **Power-law alpha=1.0** | **19.7%** | **FAIL** |
| M8 | Gaussian | 0.0% | PASS |
| **M9** | **Two-bath exponential** | **15.3%** | **FAIL** |
| M10 | Stretched exponential | 1.3% | PASS |
| M11 | Matérn (nu=1.5) | 0.3% | PASS |

Three models fail the FP gate (>10%). All three represent physically
plausible conventional mechanisms for superconducting qubit experiments.

---

## 5. What Would Fix This?

Option A — More qubits / different geometry:
  If qubit separations spanned 0.1–10 ξ_c (instead of 0.2–2.2 ξ_c),
  the K0 vs power-law distinction would be clearer. This requires
  qubits separated by 10× more — not available on Brisbane without
  relay measurements that add circuit depth and noise.

Option B — Fixed physical constraint on c (and hence ξ_c):
  If the theory independently predicted ξ_c ≈ 0.5 mm (a specific value,
  not a range), the experiment would be a parameter-free test. Currently
  c is free (GAP-7), so ξ_c is unconstrained.

Option C — Different observable that breaks the degeneracy:
  The K0 correlation function at imaginary arguments (temporal structure)
  differs from power-law more strongly. But the temporal channel is
  non-discriminating vs OU noise (proved, p25 test1).

Option D — Multiple devices / geometries:
  If the same measurement were repeated on chips with different lattice
  spacings, the ξ_c/a ratio would vary, breaking the K0/power-law
  degeneracy. Not available with the current 10-min budget.

**None of these options are available within the current experimental
constraints. The null gate failure is therefore persistent.**

---

## 6. Conclusion

**ADVERSARIAL NULL AUDIT STATUS: FAIL**

The K0 spatial correlation signature cannot be distinguished from
power-law covariance (M7) or two-bath exponential covariance (M9) with
FP ≤ 10% on the 12-qubit Brisbane geometry at the tested parameter ranges.

This is a fundamental shape-similarity problem arising from:
1. Only 11 unique separation bins in the 0.2–2.2 ξ_c range
2. Both K0 and power-law are approximately logarithmic in this range
3. SNR ≈ 2 for K0 vs M7 shape discrimination
4. Insufficient geometric range to access the distinctive curvature regime

This finding does not kill the theoretical prediction. It establishes that
the current hardware geometry and qubit count are insufficient to uniquely
attribute the signal to K0 vs physically plausible conventional mechanisms.
