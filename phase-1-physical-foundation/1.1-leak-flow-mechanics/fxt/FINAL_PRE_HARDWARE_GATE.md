# FINAL PRE-HARDWARE GATE
## SXC-IGC Spatial Correlation Experiment

**Date:** 2026-08-22
**Audit version:** 3 (complete 12-part audit)

---

## WHAT IS BEING TESTED

The surviving SXC-IGC prediction: the spatial decoherence correlator follows
a modified Bessel function K₀:

```
C_Γ(r) = K₀(r/ξ_c) / K₀(a/ξ_c)
```

where ξ_c = 2c·τ_B and a = 200 µm. The claim is that the spatial shape of
decoherence correlation is K₀ rather than exponential or power-law.

---

## WHAT IS ACTUALLY MEASURED

```
C_ij(t) = ⟨σ_{x,i}(t)·σ_{x,j}(t)⟩ / (⟨σ_{x,i}(t)⟩·⟨σ_{x,j}(t)⟩)
```

Extracted via the parity estimator from simultaneous two-qubit X-basis measurement,
using the corrected formula: C_Γ(r) = ln[C_ij(t)] / (Γ_φ·t).

---

## WHY THEY ARE MATHEMATICALLY CONNECTED

Fully derived (observable_mapping_audit.md, ESTIMATOR_AUDIT_FINAL.md).
The mapping is valid under: Gaussian substrate noise, pure dephasing (T₁ >> T₂),
spatial stationarity, pre-measured Γ_φ. The estimator bias is < 0.1%.

---

## WHAT THE NULL MODELS ARE

Full conventional null family:

| Model | Description | FP vs K0 test |
|-------|-------------|---------------|
| M0 | Independent Markovian | 0.0% — PASS |
| M2 | Single exponential / OU | 4.7% — PASS |
| M5 | EM/circuit crosstalk | 0.0% — PASS |
| **M7_pow0.5** | **Power-law alpha=0.5** | **13.3% — FAIL** |
| **M7_pow1.0** | **Power-law alpha=1.0** | **19.7% — FAIL** |
| M8 | Gaussian covariance | 0.0% — PASS |
| **M9** | **Two-bath exponential** | **15.3% — FAIL** |
| M10 | Stretched exponential | 1.3% — PASS |
| M11 | Matérn (nu=1.5) | 0.3% — PASS |

Three models fail. All three are physically motivated for superconducting chips.

---

## WHAT THE SXC-IGC MODEL PREDICTS

The K₀ shape is distinguishable from exponential (M2) but NOT from power-law
(M7) or two-bath (M9) over the accessible spatial range (r = 200–2200 µm).

LLR distributions (corrected fitter, K0 vs best-null):
- K0 data: LLR mean = +0.18, std = 0.39
- M7 data: LLR mean = −0.24, std = 0.26
- Separation: 0.42 units, far below noise width

The test cannot discriminate K0 from M7/M9 at any shot count or ξ_c value.

---

## WHAT PARAMETERS ARE FREE

| Parameter | Status |
|-----------|--------|
| ξ_c = 2c·τ_B | FREE — c not predicted by C2 (GAP-7) |
| sub_frac (amplitude) | FREE — coupling g unknown |
| Γ_φ | Pre-measured |
| T₁, T₂ | Pre-measured |
| EM crosstalk | Pre-measured |

Neither ξ_c nor the amplitude is independently predicted. The test is a
conditional shape test, not a parameter-free prediction.

---

## WHAT PARAMETERS ARE INDEPENDENT

None. Both free parameters (ξ_c, sub_frac) must be estimated from the data.

---

## WHAT REALISTIC NOISE DOES

After correcting the estimator bug (+0.137 bias from wrong single-qubit model):
- Estimator bias: < 0.001 (acceptable)
- Shot noise at N=8192: σ ≈ 0.012 per pair per time point (acceptable)
- Shape SNR (K0 vs M7): ≈ 2.0 (insufficient)

The binding constraint is shape SNR, not shot noise.

---

## WHETHER THE EFFECT IS IDENTIFIABLE

**No.** The K₀ spatial signature is not identifiable against the physically
motivated conventional null family on the 12-qubit Brisbane geometry.

Root cause: over r = 200–2200 µm with 11 unique separation bins, K₀ and
power-law covariance are both approximately logarithmic. The normalised L2
shape distance between them is 0.073, giving SNR ≈ 2.0 against measurement
noise. With only 11 data points, this is insufficient to resolve the
curvature difference.

**The effect may be identifiable on a device with:**
- Qubit separations spanning 0.1–10 ξ_c (requires ×4 larger chip or relay protocol)
- OR an independent physical prediction of ξ_c from C2 theory (currently impossible, GAP-7)
- OR experimental exclusion of M7 and M9 from the null family by independent measurement

None of these are available within the current constraints.

---

## WHETHER 10 MINUTES OF QPU TIME IS SUFFICIENT

Runtime is not the blocker. The proposed experiment fits in ~1.5 minutes.
However, the statistical test has no discriminating power regardless of runtime.

---

## WHETHER THE EXPERIMENT IS SCIENTIFICALLY LEGITIMATE

The observable mapping is valid. The circuit is implementable. The estimator
is correct after the bug fix. The null models are physically motivated.

**But the experiment is not scientifically valid as a test of K₀ vs conventional
covariance**, because the discriminating power is zero against M7 and M9.

Classification: **D — INCONCLUSIVE / NOT IDENTIFIABLE**

The measurement is physically legitimate but the available hardware/noise/geometry
cannot distinguish the hypotheses.

---

## 12-CONDITION GATE CHECKLIST

| # | Condition | Status |
|---|-----------|--------|
| 1 | Correct joint estimator verified | ✓ PASS — bias < 0.001 |
| 2 | Synthetic generator independently verified | ✓ PASS |
| 3 | No unresolved estimator bias | ✓ PASS — bug fixed |
| 4 | M0,M2,M5,M7,M9 and full null family tested | ✓ PASS — 9 models tested |
| 5 | **Global/worst-case FP ≤ 10%** | **✗ FAIL — worst FP = 19.7%** |
| 6 | Phase-1 conditioning correctly handled | ✓ PASS — bootstrap calibrated |
| 7 | Threshold fixed independently of power | ✓ PASS — threshold = 1.289 |
| 8 | **Power ≥ 80% in target regime** | **✗ FAIL — power = 0% (non-discriminating)** |
| 9 | **Adversarial search does not defeat FP control** | **✗ FAIL — M7 defeats FP** |
| 10 | Held-out validation succeeds | ✗ FAIL — power = 0% on validation set |
| 11 | QPU runtime ≤ 10 minutes | ✓ PASS — 1.5 min |
| 12 | All criteria frozen before hardware | N/A — STOP reached |

**Gates failed: 5 (conditions 5, 8, 9, 10 fail; condition 12 not applicable)**

---

## SCIENTIFIC CLAIM CLASSIFICATION

**C — EXPLORATORY SIGNAL SEARCH**

The experiment can detect that *some* spatial correlation exists that is
better described by K₀ than by a single exponential. But it cannot
distinguish K₀ from power-law or two-bath covariance, which are physically
plausible conventional mechanisms on this hardware. Therefore it cannot be
used as evidence for the substrate model.

A positive result would establish:
> K₀ fits the measured spatial correlation better than a single exponential.

It would NOT establish:
> The spatial correlation is inconsistent with conventional physics.
> SXC-IGC is correct.

---

## WHAT EVIDENCE WOULD BE REQUIRED TO CHANGE THIS CONCLUSION

1. **Physical exclusion of M7 and M9:** Independent measurements showing
   that power-law and multi-scale spatial correlations are absent on Brisbane.
   This requires cross-correlation measurements at known separations using
   a non-decoherence observable (e.g., ZZ coupling spectroscopy).

2. **Independent prediction of ξ_c:** C2 theory must independently predict
   ξ_c to within a factor of 2. This requires resolving GAP-7 (c is free).

3. **Extended geometry:** Qubit pairs spanning at least 0.1–10 ξ_c with
   ≥ 20 unique separation bins. Not available on Brisbane without relay circuits.

4. **Replication across devices:** The same spatial pattern on two chips with
   different lattice spacings would break the power-law degeneracy.

---

## FINAL STATUS: STOP

**Do not submit any IBM QPU job.**

The current experimental route is not presently viable as a test of K₀
spatial substrate correlation against a physically complete null family.

This is not evidence against the SXC-IGC theoretical framework. It is
evidence that the IBM Brisbane 12-qubit geometry is insufficient to
uniquely attribute a spatial decoherence signature to the K₀ prediction
in the presence of conventional power-law and multi-scale correlations.

The QPU allocation is preserved for a future experiment that satisfies
the geometric and theoretical requirements identified above.

Do not search for another experiment merely because this one failed.
Do not alter the hypothesis to rescue the experiment.

---

*Gate frozen: 2026-08-22*
*All criteria established before hardware.*
*Not revisable post-hoc.*
