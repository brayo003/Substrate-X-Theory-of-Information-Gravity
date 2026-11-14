# FALSE POSITIVE / FALSE NEGATIVE REPORT

**Date:** 2026-08-22
**Source:** pre_hardware_experiment_simulation.py output

---

## 1. Summary

| ξ_c | Power (TP rate) | FP rate | Verdict |
|-----|----------------|---------|---------|
| 1 mm (plausible, not predicted) | 100% | 0.2% | Discriminable |
| 3 mm (plausible, not predicted) | 99.5% | 0.2% | Discriminable |
| 10 cm (p25 default, physically motivated) | 99.9% | 0.0% | NOT discriminable (SNR=2.0) |

---

## 2. False Positive Analysis (Type I error)

**Definition:** Conventional (exponential) data incorrectly classified as K₀.

At ξ_c = 1 mm: FP rate = 0.2% (well controlled)
At ξ_c = 3 mm: FP rate = 0.2%
At ξ_c = 10 cm: FP rate = 0.0% (model indistinguishable → no false positives
  because the test has no power; both models always accepted as "same")

**EM crosstalk false positive:**
Crosstalk with ξ_EM = 800 µm has SNR = 27 relative to K₀(1mm). These are
distinguishable — crosstalk would NOT be falsely classified as K₀ at reasonable
noise levels, provided crosstalk length scale is independently measured.

---

## 3. False Negative Analysis (Type II error)

**Definition:** True K₀ data not identified as K₀ due to noise.

At all tested ξ_c values, the false negative rate (1 − Power) is < 1%.
This appears strong, but is misleading: at ξ_c = 10 cm, the test has
essentially NO power (cannot distinguish models at all), so the FN rate is
also near 0% — because neither model wins. The test fails silently rather
than generating errors.

At physically plausible ξ_c ≤ 3 mm: power > 99.5%, FN rate < 0.5%.

---

## 4. Required Shot Count

For 95% power at 5% FP rate with SNR = 3.7 (ξ_c = 3 mm case):
Achieved with N_shots = 4096. Below this, power degrades.
Minimum recommended: N_shots = 2048 per qubit pair per time point.

---

## 5. Conclusion

The statistical test is valid and well-powered IF ξ_c ≤ 3 mm.
The fundamental limitation is not statistical power — it is the unknown ξ_c.
This must be measured before the shape test is attempted.
