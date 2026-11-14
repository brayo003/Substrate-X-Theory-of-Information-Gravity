# FINAL DESIGN SEARCH
## SXC-IGC Spatial Correlation Experiment — Complete Feasibility Map

**Date:** 2026-08-22
**Script:** final_design_search.py + two_stage_test.py + adversarial_diagnosis.py
**Conclusion:** NO FEASIBLE DESIGN EXISTS within current constraints

---

## 1. Test Configuration

| Item | Value |
|------|-------|
| Estimator | Corrected parity-based meas_joint (v2) |
| Test statistic | LLR = ll(K0+xtalk) − ll(best null from full family) |
| Full null family | M0, M2, M5, M7(×3), M8, M9, M10, M11 |
| Threshold | 1.289 (frozen, derived from M7_pow0.5 calibration, 600 trials) |
| Phase-1 screen | ξ_est ≤ 2 mm (data-dependent) |
| Geometry | 12-qubit linear chain, 200 µm spacing, r = 200–2200 µm |
| Null trials | 300 per model (validation set, independent seed) |
| Power trials | 300 per (ξ_c, sub_frac) configuration |

---

## 2. Null Gate Results

| Model | FP (300 trials) | CP95 Upper | Status |
|-------|-----------------|------------|--------|
| M0 | 0.0% | 1.0% | PASS |
| M2_exp | 4.7% | 7.2% | PASS |
| M5_xtalk | 0.0% | 1.0% | PASS |
| **M7_pow0.5** | **13.3%** | **17.0%** | **FAIL** |
| **M7_pow1.0** | **19.7%** | **23.8%** | **FAIL** |
| M8_gauss | 0.0% | 1.0% | PASS |
| **M9_twobath** | **15.3%** | **19.2%** | **FAIL** |
| M10_stretch | 1.3% | 3.0% | PASS |
| M11_matern | 0.3% | 1.6% | PASS |

**Global worst-case FP: 19.7% (M7_pow1.0)**
**Required: ≤ 10%**
**Null gate: FAIL**

---

## 3. LLR Distribution Analysis (Definitive Finding)

Direct measurement of the LLR distribution for K0 and M7 data (30 trials):

| Data source | LLR mean | LLR std | P(LLR > 1.289) |
|------------|----------|---------|----------------|
| K0, ξ_c=0.5mm, sub_frac=0.20 | +0.177 | 0.392 | 0.000 |
| M7_pow0.5 | −0.240 | 0.263 | 0.000 |

**Both distributions fail to reach the threshold 1.289.**
**Power = 0%, FP = 0% simultaneously.**

This is not a threshold calibration problem. The LLR distributions for K0 and
M7 data barely differ from each other. The separation between them (~0.4 units)
is far below the noise width (~0.35 std). The test has no discriminating power.

---

## 4. Why the Test is Non-Discriminating

The corrected fitter competes K0 against M7, M9, and all other conventional
models. When M7 data is provided, the best-null fitter fits it nearly as well
as K0 does — so the LLR is small and negative (null wins marginally).
When K0 data is provided, the best-null fitter (especially M7 or M9)
fits it nearly as well as the K0 model — so the LLR is small and positive.

The fundamental reason: over 11 unique separation bins spanning 0.2–2.2 ξ_c,
both K0 and power-law covariance are approximately logarithmic. The shape
difference (normalised L2 distance = 0.073) is smaller than the noise per
pair (~0.036), giving SNR ≈ 2.0 for the shape discrimination task.
With 11 bins and an SNR of 2, there are insufficient degrees of freedom to
resolve the curvature difference between K0 and a logarithm-equivalent power law.

---

## 5. Power Grid (All Failed)

All 32 tested (ξ_c, sub_frac, shots) combinations yield power = 0.000
under the frozen threshold 1.289. This is consistent with the LLR analysis:
the LLR for K0 data does not reach 1.289 regardless of signal amplitude.

Even at sub_frac = 0.30 and 16384 shots, power = 0.000.
The failure is not due to insufficient signal or shot noise.
It is due to the K0 model being absorbed by the flexible null family.

---

## 6. Feasible Region: Empty

No design passes both gates simultaneously:
- Gate 1 (null FP ≤ 10%): requires excluding M7 and M9
- Gate 2 (power ≥ 80%): requires LLR to reach threshold

Under the corrected fitter and frozen threshold, the intersection of
{FP ≤ 10%, power ≥ 80%} is the empty set over the searched parameter space.

---

## 7. What Evidence Would Change This Conclusion

The conclusion would change if any of the following were established:

**A. Physical exclusion of M7 and M9 for IBM Brisbane:**
If independent measurements of the spatial noise structure on IBM Brisbane
showed that power-law and two-bath spatial correlations are absent or negligible
(e.g., via cross-correlation measurements at known separations with
independently calibrated null correlation), M7 and M9 could be excluded from
the null family. This would revert the null gate to its prior state where only
M0, M2, M5 need to be controlled — which all pass.

**B. Extended spatial range:**
If qubit pairs spanning 0.1–10 ξ_c were accessible, the K0 vs power-law
shape difference would increase from SNR ≈ 2 to SNR ≈ 5–10. This would
require a device with ×4 larger inter-qubit spacing or a relay-measurement
protocol, neither of which fits the current budget.

**C. Independent prediction of ξ_c:**
If C2 independently predicted ξ_c ≈ 0.5 mm (a specific value with uncertainty
< 50%), the experiment could be designed as a parameter-free prediction test
at a fixed spatial scale. The shape comparison at that specific scale would have
higher power. Currently c is free (GAP-7) so ξ_c is unconstrained.

**D. A different theoretical observable:**
If SXC-IGC predicted a non-decaying or oscillatory spatial correlation
structure (rather than K0 Bessel), the conventional null family would have
no matching model and the experiment would be more discriminating.

---

## 8. Conclusion

**FINAL DESIGN SEARCH: NO FEASIBLE DESIGN**

The SXC-IGC spatial K0 correlation experiment is not experimentally viable
on IBM Brisbane with 12 qubits and 10-minute QPU budget, given the requirement
to control FP against the full physically-motivated conventional null family.

The failure is correctly classified as:
**D — INCONCLUSIVE / NOT IDENTIFIABLE**

The measurement is physically legitimate, the observable mapping is valid,
and the circuit is implementable. But the available hardware geometry cannot
distinguish K0 from physically plausible conventional spatial covariance
(power-law, two-bath) at the SNR achievable within the current budget.

**FINAL STATUS: STOP**
