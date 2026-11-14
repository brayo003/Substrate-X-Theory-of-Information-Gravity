# TWO-STAGE STATISTICS AUDIT
## SXC-IGC Pre-Hardware Gate

**Date:** 2026-08-22
**Script:** two_stage_test.py (corrected K0 vs best-null from full family)
**Status:** FAIL — null gate not satisfied

---

## 1. Procedure Design

### Stage 1: Data-dependent spatial scale screening
Screen trials using a simple exponential fit to the C_Gamma(r) data.
- If estimated scale ξ_est > 2 mm: STOP (experiment not informative)
- If ξ_est ≤ 2 mm: proceed to Stage 2

This is correctly labelled as **data-dependent selection, not a prediction test**.
The hypothesis test in Stage 2 is conditional on the screening result.

### Stage 2: K0 vs best-null LLR test
The corrected test statistic is:
```
LLR = ll(K0+xtalk) - max over {M2, M7×3, M9, M10, M11}[ll(null)]
```
This forces K0 to outperform **any** tested conventional model, not just
the exponential. The threshold is calibrated by bootstrap under the worst
null model (M7_pow0.5) conditioned on passing Stage 1.

### Key improvement over prior fitter
Prior: LLR = ll(K0) - ll(exp-only)  → M7 and M9 always win (heavy tail)
New:   LLR = ll(K0) - ll(best null) → M7 and M9 compete directly

---

## 2. Calibration (Development Set, RNG seed 271828)

Calibration uses 600 trials of the worst-case null (M7_pow0.5) with the
development random seed — completely separate from the validation seed.

| Metric | Value |
|--------|-------|
| Null model used | M7_pow0.5 (worst adversarial case) |
| Trials | 600 |
| Passed Stage-1 screen | 600/600 (100%) |
| Null LLR mean | 0.547 |
| Null LLR std | 0.616 |
| 90th percentile (FP = 0.10) | **1.289** |

**Threshold 1.289 is frozen.** It was derived from the null distribution
before the validation step and cannot be revised post-hoc.

---

## 3. Validation Results (Held-out Set, RNG seed 141421)

N = 300 trials per model. FP rate = FP_count / 300 (not normalised to screened-in trials).

| Model | FP Count | FP Rate | CP95 Upper | Screened In | Status |
|-------|----------|---------|------------|-------------|--------|
| M0 | 0/300 | 0.000 | 0.010 | 40/300 | PASS |
| M2_exp | 14/300 | 0.047 | 0.072 | 300/300 | PASS |
| M5_xtalk | 0/300 | 0.000 | 0.010 | 44/300 | PASS |
| **M7_pow0.5** | **40/300** | **0.133** | **0.170** | 299/300 | **FAIL** |
| **M7_pow1.0** | **59/300** | **0.197** | **0.238** | 300/300 | **FAIL** |
| M8_gauss | 0/300 | 0.000 | 0.010 | 300/300 | PASS |
| **M9_twobath** | **46/300** | **0.153** | **0.192** | 300/300 | **FAIL** |
| M10_stretch | 4/300 | 0.013 | 0.030 | 300/300 | PASS |
| M11_matern | 1/300 | 0.003 | 0.016 | 300/300 | PASS |

**Worst-case FP: 0.197 (M7_pow1.0)**
**Global null gate: FAIL**

---

## 4. Power Results (K0 signal, held-out set)

| ξ_c | sub_frac | Power | Status |
|-----|----------|-------|--------|
| 0.5 mm | 0.15 | 0.717 | FAIL |
| 0.5 mm | 0.20 | **0.847** | **PASS** |
| 0.5 mm | 0.30 | **0.993** | **PASS** |
| 1.0 mm | 0.15 | 0.430 | FAIL |
| 1.0 mm | 0.20 | 0.563 | FAIL |
| 1.0 mm | 0.30 | 0.753 | FAIL |
| 2.0 mm | 0.15 | 0.233 | FAIL |
| 2.0 mm | 0.20 | 0.257 | FAIL |

Power ≥ 0.80 is achievable at ξ_c = 0.5 mm and sub_frac ≥ 0.20.
However, the null gate fails regardless of the power result.

**The experiment cannot be declared valid because FP is not controlled
against M7 and M9 at the required ≤ 10% level.**

---

## 5. Why M7 and M9 Still Fail After the Corrected Fitter

The corrected fitter explicitly competes K0 against M7 and M9. Yet M7 still
produces 13–20% FP and M9 produces 15% FP. The reason is not the fitter —
it is the data geometry.

Over the 12-qubit linear chain (r = 200–2200 µm, 11 unique bins):
- K0 at ξ_c = 0.5–2 mm is approximately logarithmic
- Power-law r^{-0.5 to -1.0} is also approximately logarithmic
- The shape difference (normalised L2 distance) is only 0.07–0.17
- At noise level σ = 0.036, the SNR for K0 vs M7 is only **2.0**

The best-null fitter finds that M7 fits the K0 data almost as well as K0
itself, keeping the LLR small. In Stage 2, the LLR falls below the threshold
1.289 for both genuine K0 and conventional M7 data at similar rates —
hence the 13–20% FP despite the corrected test.

This is a **fundamental geometric underpowering**, not a statistical procedure
failure. More data (more shots) does not help because the problem is shape
similarity, not shot noise. More qubits with larger spatial range would help,
but are not available in the current budget.

---

## 6. Type-I Error Summary

| Scope | FP Rate | Bound |
|-------|---------|-------|
| Against tested exponential/OU nulls (M0, M2, M5, M8, M10, M11) | 0–5% | CP95 < 7% |
| Against power-law M7_pow0.5 | 13.3% | CP95 < 17% |
| Against power-law M7_pow1.0 | 19.7% | CP95 < 24% |
| Against two-bath M9 | 15.3% | CP95 < 19% |
| **Worst-case (global)** | **19.7%** | **CP95 < 24%** |

The global worst-case FP is approximately 2× the required maximum of 10%.

---

## 7. Verdict

**TWO-STAGE STATISTICS GATE: FAIL**

The corrected two-stage test with full null family competition does not
control FP ≤ 10% against power-law (M7) and two-bath (M9) spatial
covariance. These are physically motivated conventional mechanisms.

**Required to change this verdict:**
Either show that M7 and M9 are physically implausible for the IBM Brisbane
chip (requires independent experimental or theoretical argument), or
increase the geometric range to make K0 distinguishable from logarithmic-
equivalent functions. Neither is achievable within the current constraints.

FINAL STATUS: **STOP**
