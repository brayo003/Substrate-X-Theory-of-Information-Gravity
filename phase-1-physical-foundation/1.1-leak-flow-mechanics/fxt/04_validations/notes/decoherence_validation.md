# Substrate-X Decoherence Validation Report

**Generated:** 2026-07-20T14:49:46Z  
**Backend:** ibm_marrakesh (Eagle r2, qubit 0)  
**Pipeline:** `decoherence_prediction.py`  
**Data source:** `nunu/ramsey_dataset/experiment_results.npz`

---

## Executive Summary

This report presents an empirical validation of the Substrate-X macro
decoherence model against seven Ramsey spectroscopy experiments executed on
IBM Quantum hardware (`ibm_marrakesh`, qubit 0).

The model predicts:

```
Γ(ω) = Γ₀ + k_rot · ω² / (1 + (ω/ω_max)²)
```

with fixed parameters k_rot = 4.5×10⁻⁷ s and ω_max = 1×10⁶ rad/s.

**Key finding:** The model as currently parameterised does not describe the
experimental data. At all seven measured oscillation frequencies
(Ω ∈ [0.69, 50.3] Mrad/s), the k_rot term alone evaluates to values in the
range 72,000–91,000 s⁻¹, whereas the measured Γ values lie consistently in
the range 27,000–38,000 s⁻¹. Forcing a one-parameter WLS fit for Γ₀ yields
Γ₀ = −358,702 ± 1,139 s⁻¹, a physically inadmissible negative value.

This is not a numerical error; it is a direct quantitative statement about
model–data compatibility:

- The model over-predicts dephasing by a factor of ~3× across the entire
  frequency range.
- R² = −977.6 (predictions are far worse than predicting the mean).
- Reduced χ² = 983.7 (ideal = 1.0).
- MAPE = 276%.

The experimental Γ values show no statistically significant frequency
dependence (Pearson r = 0.39, p = 0.38; Spearman ρ = 0.25, p = 0.59),
consistent with frequency-independent dephasing at the level observed
(T2* ≈ 27–36 µs).

These results are fully reproducible from the supplied IBM Quantum dataset.
No synthetic or simulated data were used.

---

## 1. Method

### 1.1 Data acquisition (not repeated here)

Ramsey spectroscopy was performed on qubit 0 of ibm_marrakesh using the
standard √X – delay – Rz(φ) – √X – measure sequence. Seven detuning
frequencies (100 kHz – 8 MHz) were used with 256 shots each and 15 delay
points per experiment (0 – 120 µs, linearly spaced in delay cycles).

### 1.2 Fitted Ramsey signal model

Each experiment's P(|1⟩) vs delay curve was fitted to:

```
P(t) = A · exp(−Γ·t) · cos(Ω·t + Φ) + 0.5
```

Four free parameters: amplitude A, dephasing rate Γ (s⁻¹), oscillation
frequency Ω (rad/s), and phase Φ. All seven fits converged with `fit_success`
status and were accepted based on convergence and physical plausibility criteria.

### 1.3 Validation procedure

1. Load all accepted experiments from `experiment_results.npz`.
2. Extract Γ, σ_Γ, Ω, σ_Ω, detuning, R², T2* for each experiment.
3. Verify internal consistency: fitted Ω vs 2π·detuning.
4. Compute Γ_pred(Ω) using the Substrate-X model with k_rot and ω_max fixed.
5. Estimate Γ₀ via weighted least squares (weights = 1/σ_Γ²).
6. Compute full residual statistics, uncertainty propagation, and information
   criteria.
7. Perform statistical tests on residuals (normality, zero mean, autocorrelation).
8. Execute sensitivity analysis for k_rot ± 5%, ±10%, ±20%.
9. Generate five publication-quality figures.

---

## 2. Dataset Description

| detuning (MHz) | Ω_fit (Mrad/s) | Ω_2π·f (Mrad/s) | Δ (%) | Γ_exp (s⁻¹) | σ_Γ (s⁻¹) | T2* (µs) | R²     |
|:--------------:|:--------------:|:----------------:|:-----:|:-----------:|:---------:|:--------:|:------:|
| 0.1            | 0.694          | 0.628            | 10.4  | 28,067      | 3,800     | 35.6     | 0.9637 |
| 0.2            | 1.322          | 1.257            |  5.2  | 32,446      | 3,747     | 30.8     | 0.9686 |
| 0.5            | 3.204          | 3.142            |  2.0  | 27,563      | 1,660     | 36.3     | 0.9911 |
| 1.0            | 6.341          | 6.283            |  0.9  | 37,511      | 6,108     | 26.7     | 0.9397 |
| 2.0            | 12.630         | 12.566           |  0.5  | 35,024      | 4,762     | 28.6     | 0.9577 |
| 5.0            | 31.481         | 31.416           |  0.2  | 28,930      | 2,905     | 34.6     | 0.9824 |
| 8.0            | 50.324         | 50.265           |  0.1  | 31,678      | 3,574     | 31.6     | 0.9694 |

**Observations:**

- The Ω discrepancy vs 2π·f decreases monotonically from 10.4% at 0.1 MHz to
  0.1% at 8 MHz. This is consistent with the fitting prior being initialised
  at exactly 2π·detuning; at low detuning the oscillation completes fewer
  cycles within the delay window, making Ω harder to pin down precisely.
- Γ values scatter around a mean of ~31,600 s⁻¹ with no statistically
  significant trend vs Ω.
- All Ramsey fits have R² ≥ 0.94 and reduced χ² ≤ 0.002, confirming
  high-quality individual fits to the hardware data.
- T2* values range 26.7–36.3 µs, consistent with typical ibm_marrakesh
  performance.

---

## 3. Model and Parameter Estimation

### 3.1 Substrate-X macro decoherence model

```
Γ(ω) = Γ₀ + k_rot · ω² / (1 + (ω/ω_max)²)
```

| Parameter | Value        | Status    | Interpretation                          |
|-----------|-------------:|:---------:|:----------------------------------------|
| k_rot     | 4.5×10⁻⁷ s  | Fixed     | Rotational coupling coefficient         |
| ω_max     | 1×10⁶ rad/s | Fixed     | Saturation/rolloff frequency            |
| Γ₀        | fitted       | Free (×1) | Baseline (frequency-independent) dephasing |

### 3.2 Model behaviour at experimental frequencies

The Lorentzian saturation term `ω²/(1+(ω/ω_max)²)` saturates to
`ω_max² = (1×10⁶)² = 10¹² rad²/s²` as ω → ∞. At ω = ω_max it equals
ω_max²/2. For all measured Ω ≫ ω_max, the term is effectively saturated:

```
f(ω) ≈ k_rot · ω_max² = 4.5×10⁻⁷ × (1×10⁶)² = 4.5×10⁵ s⁻¹
```

This means the model predicts Γ ≈ Γ₀ + 450,000 s⁻¹ for essentially
**all** measured frequencies, while the data show Γ ≈ 27,000–38,000 s⁻¹.
The model term alone exceeds the measured values by ~12–16×.

### 3.3 Γ₀ estimation (weighted least squares)

The model is linear in Γ₀, so WLS has a closed-form solution:

```
Γ₀_WLS = Σ(w_i · (Γ_exp,i − f(Ω_i))) / Σ(w_i)
```

where w_i = 1/σ_Γ,i² and f(Ω_i) = k_rot · Ω_i² / (1 + (Ω_i/ω_max)²).

**Result:**

| Quantity           | Value (s⁻¹)   |
|:-------------------|:-------------:|
| Γ₀ (WLS)          | −358,702      |
| σ(Γ₀)             |    1,139      |
| 95% CI lower       | −360,934      |
| 95% CI upper       | −356,470      |
| curve_fit check    | −358,702      |

The WLS and `scipy.optimize.curve_fit` estimates agree exactly (as expected
for a 1-parameter linear problem). The estimate is unambiguously negative,
with a 95% confidence interval entirely below zero. This is the unique
least-squares solution given the fixed model parameters; it is not a
numerical artifact.

**Physical interpretation:** A negative Γ₀ is unphysical. It indicates that
the fixed k_rot term contributes ~450,000 s⁻¹ to the predicted Γ, while the
data require a total Γ of only ~31,600 s⁻¹. The model, in its current
parameterisation, cannot simultaneously satisfy k_rot = 4.5×10⁻⁷ s,
ω_max = 1×10⁶ rad/s, and Γ₀ ≥ 0.

---

## 4. Statistical Validation

### 4.1 Global fit quality metrics

| Metric                 | Value        | Interpretation                         |
|:-----------------------|:------------:|:---------------------------------------|
| RMSE                   | 107,905 s⁻¹ | Very large vs Γ range (27k–38k s⁻¹)   |
| MAE                    |  83,852 s⁻¹ |                                        |
| Bias                   |  14,858 s⁻¹ | Model over-predicts on average         |
| MAPE                   |   276.5 %    | Severe systematic over-prediction      |
| R²                     |  −977.62     | Model far worse than mean baseline     |
| χ²                     | 5,902.3      |                                        |
| Reduced χ²             |   983.7      | Ideal = 1.0; grossly inconsistent      |
| AIC                    | 6,031.6      |                                        |
| BIC                    | 6,031.6      |                                        |
| Pearson r              |    0.392     | Weak positive; p = 0.384 (NS)          |
| Spearman ρ             |    0.250     | Weak positive; p = 0.589 (NS)          |

### 4.2 Residual analysis

Per-experiment breakdown:

| detuning (MHz) | Γ_pred (s⁻¹) | residual (s⁻¹) | norm. residual |
|:--------------:|:------------:|:--------------:|:--------------:|
| 0.1            | −212,482     |  +240,549      |  +63.3         |
| 0.2            |  −72,490     |  +104,936      |  +28.0         |
| 0.5            |  +51,350     |   −23,787      |  −14.3         |
| 1.0            |  +80,379     |   −42,868      |   −7.0         |
| 2.0            |  +88,495     |   −53,471      |  −11.2         |
| 5.0            |  +90,845     |   −61,914      |  −21.3         |
| 8.0            |  +91,121     |   −59,442      |  −16.6         |

The residuals are not random: the model severely under-predicts Γ at low Ω
and severely over-predicts at high Ω. The sign reversal around Ω ≈ 3 Mrad/s
(0.5 MHz detuning) reflects the Lorentzian saturation boundary of the model
at ω_max = 1 Mrad/s.

### 4.3 Residual normality and independence tests

| Test                   | Statistic  | p-value | Interpretation              |
|:-----------------------|:----------:|:-------:|:----------------------------|
| Shapiro-Wilk           | —          | 0.0089  | Reject normality (α = 0.05) |
| t-test (zero mean)     | —          | 0.745   | Cannot reject zero mean     |
| Durbin-Watson          | 0.436      | —       | Strong positive autocorr.   |
| Runs test (obs/exp)    | 3 / 4.4    | —       | Slight run deficit          |

The residuals are non-Gaussian (Shapiro-Wilk p = 0.009) and show positive
autocorrelation (DW = 0.44, far below 2). The zero-mean t-test is
non-significant (p = 0.75), but this is a consequence of cancellation between
large positive and negative values, not of a well-fitting model.

### 4.4 Sensitivity analysis (k_rot ±5%, ±10%, ±20%)

Varying k_rot does not improve model–data agreement. All perturbations still
produce predictions far from the measured Γ range. The sensitivity curves
(see `sensitivity_analysis.png`) are all displaced from the data band by
>50,000 s⁻¹.

| k_rot perturbation | k_rot (s)     | Γ_pred range at data Ω (s⁻¹)  |
|:-----------------:|:-------------:|:-----------------------------:|
| −20%              | 3.60×10⁻⁷     | [−241,726 , +1,156]           |
| −10%              | 4.05×10⁻⁷     | [−227,104 , +46,138]          |
| −5%               | 4.275×10⁻⁷    | [−219,793 , +68,629]          |
|   0% (nominal)    | 4.50×10⁻⁷     | [−212,482 , +91,121]          |
| +5%               | 4.725×10⁻⁷    | [−205,171 , +113,612]         |
| +10%              | 4.95×10⁻⁷     | [−197,860 , +136,103]         |
| +20%              | 5.40×10⁻⁷     | [−183,238 , +181,085]         |

---

## 5. Uncertainty Propagation

Prediction uncertainty was propagated via:

```
σ_pred² = σ_Γ₀² + (∂Γ_pred/∂ω · σ_Ω)²

∂Γ_pred/∂ω = k_rot · 2ω · ω_max⁴ / (ω_max² + ω²)²
```

| detuning (MHz) | σ_pred (s⁻¹) | σ_exp (s⁻¹) | σ_pred/σ_exp |
|:--------------:|:------------:|:-----------:|:------------:|
| 0.1            | 2,432        | 3,800       | 0.64         |
| 0.2            | 1,387        | 3,747       | 0.37         |
| 0.5            | 1,140        | 1,660       | 0.69         |
| 1.0            | 1,139        | 6,108       | 0.19         |
| 2.0            | 1,139        | 4,762       | 0.24         |
| 5.0            | 1,139        | 2,905       | 0.39         |
| 8.0            | 1,139        | 3,574       | 0.32         |

The propagated prediction uncertainty (~1,139 s⁻¹) is dominated by σ_Γ₀
(the WLS uncertainty on the baseline). The Ω-derivative contribution is
negligible at large Ω because the Lorentzian is fully saturated. In all
cases σ_pred < σ_exp, meaning the experimental uncertainties exceed the
model's propagated uncertainties; the misfit is systematic, not statistical.

---

## 6. Limitations

1. **Model parameterisation mismatch.** The most significant limitation is
   that the fixed values k_rot = 4.5×10⁻⁷ s and ω_max = 1×10⁶ rad/s produce
   a k_rot term that saturates at ~450,000 s⁻¹, orders of magnitude larger
   than the observed Γ (~30,000 s⁻¹). This likely indicates that the physical
   interpretation of k_rot and/or ω_max in the Substrate-X model applies at
   a different frequency scale or energy scale than the Ramsey oscillation
   frequencies measured here.

2. **Single qubit, single backend.** All data were collected from qubit 0 of
   ibm_marrakesh. Backend-specific noise characteristics (cross-talk, residual
   ZZ coupling, charge noise) may differ from other devices. No claim about
   universality is made.

3. **Small sample (N = 7).** Statistical tests (especially normality) have
   limited power. The Shapiro-Wilk test is reliable for small N, but
   conclusions should be interpreted with appropriate caution.

4. **Fitted Ω ≠ 2π·detuning exactly.** Discrepancies up to 10.4% are seen at
   low detuning (0.1 MHz). This is expected: the fit uses a free oscillation
   frequency Ω, which absorbs any systematic frequency shift from residual
   calibration offsets. The analysis uses the fitted Ω as the physically
   relevant variable (it is what the qubit actually oscillated at).

5. **No temporal drift correction.** All seven experiments were run within a
   ~57-second window (14:21:29 to 14:22:18 UTC). Short-term drift is unlikely
   to be significant over this timescale, but cannot be excluded.

6. **Shots per point.** With 256 shots per delay, shot noise contributes
   ~1/√256 = 6.25% statistical uncertainty per point. This is correctly
   propagated through the curve_fit covariance matrices and reflected in
   σ_Γ.

---

## 7. Conclusion

The Substrate-X macro decoherence model

```
Γ(ω) = Γ₀ + k_rot · ω² / (1 + (ω/ω_max)²)
```

with k_rot = 4.5×10⁻⁷ s and ω_max = 1×10⁶ rad/s **does not quantitatively
describe** the IBM Quantum Ramsey dephasing data as measured.

The empirical findings are:

- Measured Γ is approximately frequency-independent at ~28,000–38,000 s⁻¹
  across Ω ∈ [0.69, 50.3] Mrad/s.
- The model's rotational term, evaluated at the experimental frequencies,
  contributes ~72,000–450,000 s⁻¹ — between 2.3× and 14× the total measured Γ.
- The only physically admissible reconciliation requires k_rot ≪ 4.5×10⁻⁷ s
  or ω_max ≫ 1×10⁶ rad/s, or both.
- Under the fixed-parameter constraint, the WLS-estimated Γ₀ = −358,702 s⁻¹
  is unphysical, confirming model–data incompatibility.

**Recommended next steps:**

1. Revisit the physical derivation of k_rot and ω_max to determine whether
   the ω in the model refers to the Ramsey oscillation frequency Ω, or to some
   higher-energy spectral quantity.
2. Consider whether the model was designed for a different frequency domain
   (e.g., optical or microwave cavity frequencies vs qubit Larmor frequencies).
3. If the model is intended to describe qubit dephasing, re-derive k_rot
   dimensionally and physically for the qubit context: the current value would
   require ω_max ≳ 10⁸ rad/s to keep the model term below the observed Γ.

The raw data are of high quality (R² ≥ 0.94 on individual Ramsey fits,
consistent T2* values, all 7/7 experiments accepted). The issue is entirely
in the model parameterisation, not in the experimental data.

---

## Appendix: Output Files

| File                           | Description                                          |
|:-------------------------------|:-----------------------------------------------------|
| `decoherence_results.csv`      | Per-experiment Γ_exp, Γ_pred, residuals, uncertainties |
| `decoherence_results.npz`      | Full results archive (arrays + statistics dict)      |
| `gamma_prediction.png`         | Γ vs Ω: data + model curve                          |
| `gamma_residuals.png`          | Residuals, normalised residuals, histogram           |
| `qq_plot.png`                  | Q-Q plot of normalised residuals                     |
| `prediction_vs_measurement.png`| Γ_pred vs Γ_exp scatter                             |
| `sensitivity_analysis.png`     | k_rot sensitivity curves ±5%, ±10%, ±20%            |

All figures generated by `decoherence_prediction.py` from the original IBM
Quantum dataset. No synthetic data.

---

*End of report.*
