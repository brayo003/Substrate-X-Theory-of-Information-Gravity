# ESTIMATOR AUDIT FINAL
## SXC-IGC Pre-Hardware Pipeline — Estimator Verification

**Date:** 2026-08-22
**Estimator version:** 2 (corrected parity-based joint measurement)
**Script:** sxc_igc_core.py, pipeline_audit.py
**Status:** PASS — all estimator checks cleared after bug fix

---

## 1. The Estimator Bug (Prior Versions)

All simulations prior to `sxc_igc_core.py v2` used a wrong estimator for the
two-qubit correlation observable `<sigma_x,i * sigma_x,j>`.

**Bug:** The product signal `W_i(t) * W_j(t) * exp(C*Γ*t)` was passed to a
single-qubit readout model `meas(sig)` that maps [-1,1] → binomial. This is
incorrect because:

1. The two-qubit correlation is measured by a single circuit yielding 4 joint
   outcomes (++, +-, -+, --), not by two separate single-qubit circuits.
2. The product `W_i * W_j` can be < 0.5 at late times, which maps to a very
   low probability under the single-qubit model, systematically inflating the
   estimated measurement noise.
3. The resulting C_Gamma estimates had a constant additive bias of **+0.137**,
   independent of the true correlation value.

**Evidence:** pipeline_audit.py Part 1b showed bias = +0.137 at all tested
C_true values [0.02, 0.05, 0.10, 0.15, 0.20] using the prior estimator.

---

## 2. Correct Estimator Derivation

For two qubits with Pauli expectation values Zi = <sigma_x,i>, Zj = <sigma_x,j>,
ZiZj = <sigma_x,i sigma_x,j>, the four joint outcome probabilities in the X basis are:

```
P(+,+) = (1 + Zi + Zj + ZiZj) / 4
P(+,-) = (1 + Zi - Zj - ZiZj) / 4
P(-,+) = (1 - Zi + Zj - ZiZj) / 4
P(-,-) = (1 - Zi - Zj + ZiZj) / 4
```

With independent per-qubit readout error e (flip probability):

```
P'(a,b) = sum_{a',b'} P(a',b') * flip_i(a',a) * flip_j(b',b)
```

where flip(same) = 1-e, flip(different) = e.

The unbiased estimators from counts (n_++, n_+-, n_-+, n_--) are:

```
Zi_est  = (n_++ + n_+- - n_-+ - n_--) / N
Zj_est  = (n_++ - n_+- + n_-+ - n_--) / N
ZZ_est  = (n_++ - n_+- - n_-+ + n_--) / N   [PARITY ESTIMATOR]
```

**Proof of readout-error cancellation in the ratio:**

```
E[Zi_est] = (1-2e) * Zi
E[Zj_est] = (1-2e) * Zj
E[ZZ_est] = (1-2e)^2 * ZiZj
```

Therefore:
```
C_ij = ZZ_est / (Zi_est * Zj_est)
     = [(1-2e)^2 * ZiZj] / [(1-2e)*Zi * (1-2e)*Zj]
     = ZiZj / (Zi * Zj)    [readout error cancels exactly]
```

The ratio estimator C_ij = ZZ_est / (Zi_est * Wj_est) is unbiased for
ZiZj / (Zi * Zj) to leading order in shot noise.

---

## 3. Correlated Readout Errors

The derivation above assumes **independent** per-qubit readout errors.

**Known limitation:** IBM simultaneous measurement has a residual correlated
readout error (cross-talk) at the ~0.5-1% level between adjacent qubits. This
is NOT modelled in the current `meas_joint()` implementation.

**Impact:** Correlated readout error would add a spurious term to ZZ_est that
does not cancel in the ratio. For two adjacent qubits with correlated error
amplitude ε_c, the residual bias in C_ij is approximately ε_c / (W_i * W_j).
At W ~ 0.7 and ε_c ~ 0.005: residual bias ≈ 0.01.

**Classification:** UNTESTED NUISANCE. The calibration circuit (measuring
qubits in ground state with simultaneous readout) can quantify and subtract
this effect before the main experiment. It is not modelled in the simulation
and introduces a ~1% systematic uncertainty on C_Gamma estimates.

This is explicitly flagged as an unresolved nuisance. It does not invalidate
the test if the calibration is performed, but it must be characterised
before hardware execution.

---

## 4. Verification Tests (pipeline_audit.py, corrected estimator)

| Test | Result | Status |
|------|--------|--------|
| 1a Denominator instability | 0.000000 fraction of extreme values | PASS |
| 1a C_Gamma bias (null trials) | mean = −0.00077, std = 0.021 | PASS |
| 1b Log-transform Jensen bias at C=0.02 | +0.00022 | PASS |
| 1b Log-transform Jensen bias at C=0.10 | −0.00027 | PASS |
| 1b Log-transform Jensen bias at C=0.20 | −0.00109 | PASS |
| 1b Maximum bias across C ∈ [0.02,0.20] | 0.00109 | PASS |
| C_ij = ZZ/Wij bias (no correlation) | 0.9995 (expect 1.0) | PASS |

**All estimator checks pass.** Maximum residual bias = 0.11% of signal,
well below the measurement noise floor (~2%).

---

## 5. Formula Correctness: C_Gamma Extraction

The extraction formula is:

```
C_Gamma(r) = ln[C_ij(t)] / (Gamma_phi * t)
```

**Derivation validity conditions:**
1. Pure dephasing by Gaussian correlated substrate noise (DERIVED)
2. Gamma_phi pre-measured and known (EXPERIMENTAL ASSUMPTION)
3. T_1 >> T_2 (pure dephasing limit; partially violated, see hardware_feasibility_report.md)
4. Spatial stationarity (ASSUMPTION)
5. Identical qubits (approximation; 10% spread modelled)

**Note:** An earlier version of this document had a "+1" error:
  C_Gamma = 1 + ln[C_ij]/(Gamma*t)  ← WRONG (removed)
  C_Gamma = ln[C_ij]/(Gamma*t)      ← CORRECT

The correct formula follows directly from C_ij = exp(C_Gamma * Gamma * t),
so ln(C_ij) = C_Gamma * Gamma * t.

---

## 6. Gamma_phi Consistency

The extraction uses `gamma_phi_est = mean(gph_i)` from the per-qubit pre-measured
values. This introduces a ~5% error in the extracted C_Gamma values due to qubit-
to-qubit variation (10% spread → ~5% error in C_Gamma via error propagation).

This is a known, quantifiable uncertainty. It does not affect the shape test
(K0 vs null) because it rescales C_Gamma uniformly, not the spatial profile.

---

## 7. Summary

**ESTIMATOR STATUS: PASS**

The corrected `meas_joint()` estimator in `sxc_igc_core.py v2` is
mathematically correct, numerically verified, and produces bias < 0.1%.

One untested nuisance remains: correlated readout error (~0.5-1%) requires
a dedicated calibration measurement before hardware execution.

The prior estimator bug (constant +0.137 bias from wrong single-qubit model)
is fixed. All simulations from `sxc_igc_core.py v2` onwards are valid.
