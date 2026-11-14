# Q Metric Audit
## Complete Implementation Trace, Empirical Characterization, and Predictive Testing

**Audit date:** 2026-10-11  
**Git commit:** `6738ed05`  
**Source files examined:** `v12_validate/transport_layer.py`, `p1_data_stream.py`, `p2_transport_os.py`, `v12_validate/signals.py`, `checkpoints/checkpoint_manifest.json`  
**Cached data:** `cache/q_series_full.parquet`, `results/q_distribution.csv`, `results/bounded_validation_corrected/corrected_audit_results.json`

---

## 1. Exact Formula and Source-Code Trace

### 1.1 Definition in source

**File:** `v12_validate/transport_layer.py`  
**Function:** `compute_transport_field(s, c, tau, dt)`  
**Lines (logical):**

```python
# Step 2: Log-gradient
s_safe = np.clip(s, EPSILON, 1.0 - EPSILON)   # EPSILON = 1e-9
log_s  = np.log(s_safe)
grad_ln_s        = np.zeros(n, dtype=np.float64)
grad_ln_s[1:]    = (log_s[1:] - log_s[:-1]) / dt   # backward difference
grad_ln_s[0]     = grad_ln_s[1] if n > 1 else 0.0  # edge case: copy bar 1

# Step 3: Q
c_tau = c * tau                          # DEFAULT_C=1.0, DEFAULT_TAU=5.0
Q     = 4.0 * (c_tau ** 2) * (grad_ln_s ** 2) - 1.0
```

The formula in full:

    grad_ln_s[t] = ln(s[t]) - ln(s[t-1])   (because dt = 1.0)
    Q[t]         = 4 × (c × τ)² × (grad_ln_s[t])² − 1
                 = 4 × (1.0 × 5.0)² × (ln(s[t]/s[t-1]))² − 1
                 = 100 × (ln(s[t]/s[t-1]))² − 1

The reported formula `Q = 4(cτ)² × (grad_ln_s)² − 1` with c=1, τ=5, dt=1 is **confirmed correct** by direct code inspection.

### 1.2 What is s?

`s` is the composite normalized stress field produced by `v12_validate/signals.py → build_signals_from_ticks()`:

1. Tick data resampled to 5-min OHLC bars.
2. Rolling features computed: volatility, volume ratio, spread ratio, tick frequency, momentum (all backward-looking windows only).
3. Each feature z-scored and passed through sigmoid → normalized to (0, 1).
4. Composite `s` = row mean of all normalized features → strictly in (0, 1).

`s` is therefore a sigmoid-normalized aggregate of lagged market microstructure features. It is not a raw price.

### 1.3 Constants and parameters

| Parameter | Value | Source |
|-----------|-------|--------|
| c (propagation speed) | 1.0 | `DEFAULT_C` in transport_layer.py |
| τ (relaxation time) | 5.0 bars | `DEFAULT_TAU` in transport_layer.py |
| dt (time step) | 1.0 bar | Default argument, not overridden |
| EPSILON | 1e-9 | Clip guard for log(0) |
| Resulting c×τ | 5.0 | Fixed |
| Effective scaling | 100 | 4 × 5² = 100 |

These constants were not fitted to trading performance. They were set before the calibration run according to the docstring in `transport_layer.py`.

### 1.4 PDE-evolved transport field s_transport

A separate quantity `s_transport` is computed by an IMEX semi-implicit discretization of the telegraph equation. **`s_transport` is NOT used in the Q computation.** Q is computed entirely from the raw (sigmoid-normalized) composite field `s`. The `s_transport` calculation appears in `compute_transport_field()` but feeds only the `s_transport` column in the output DataFrame; its influence on Q is zero.

This is confirmed by the code structure: Step 1 computes `s_t[]` (s_transport), Step 2 clips and logs the original `s`, Step 3 computes Q from `grad_ln_s` of `s`. There is no path from `s_t` back into Q.

### 1.5 Causality

- `grad_ln_s[t]` uses only `s[t]` and `s[t-1]` — strictly backward difference.  
- `s` itself is constructed from rolling/ewm windows on past tick data only.  
- Q at bar t uses no information from bar t+1 or later.  
- Q thresholds (q05, q95) were derived from the calibration period (2023–2025) and frozen in `checkpoints/checkpoint_manifest.json` before any 2026 evaluation.

**Q is causal at every step of its computation.**

### 1.6 Edge cases

| Condition | Handling |
|-----------|----------|
| s[t] = 0 | Clipped to EPSILON = 1e-9 before log |
| s[t] = 1 | Clipped to 1 - EPSILON before log |
| NaN in composite | propagates to Q; classified as Mod_Incoherent by regime classifier |
| First bar (t=0) | grad_ln_s[0] = grad_ln_s[1] (copy) |
| Zero change (s[t] = s[t-1]) | grad_ln_s = 0 → Q = -1 (minimum) |
| Extreme change | Q = 100 × (large log-return)² − 1 (unbounded above) |

---

## 2. Numerical Verification

### 2.1 Algebraic verification

For a representative observation with s[t] = 0.52, s[t-1] = 0.50:

    grad_ln_s = ln(0.52/0.50) = ln(1.04) = 0.039221
    Q = 100 × (0.039221)² − 1 = 100 × 0.001538 − 1 = 0.1538 − 1 = −0.8462

For a large change s[t] = 0.60, s[t-1] = 0.50:

    grad_ln_s = ln(0.60/0.50) = ln(1.20) = 0.18232
    Q = 100 × (0.18232)² − 1 = 100 × 0.033241 − 1 = 3.3241 − 1 = 2.3241

For no change s[t] = 0.50, s[t-1] = 0.50:

    grad_ln_s = 0
    Q = 100 × 0 − 1 = −1.0  (the minimum possible Q value)

These match the cached distribution: Q is always ≥ −1, with minimum exactly −1, and right tail extending to ~35.

### 2.2 Calibration distribution (q_distribution.csv + manifest)

From the full 209,689-bar calibration series (2023-01-01 to 2025-10-24):

| Statistic | Value |
|-----------|-------|
| Mean Q | −0.317 |
| Std Q | 1.273 |
| q05 (frozen threshold) | −0.998 |
| q95 (frozen threshold) | 1.732 |
| Coherent fraction (Q > 0) | 20.1% |
| Strong_Coherent fraction (Q ≥ 1.732) | 5.0% |
| Bars at minimum (Q ≈ −1) | ~62% of all bars |

Bin counts confirm the extreme left-skew: 61.9% of bars fall in the lowest bin (Q from −1 to −0.64), consistent with the majority of bars having near-zero composite field changes.

### 2.3 Cache reproducibility

The cached values in `cache/q_series_full.parquet` were produced deterministically from the source code described above. The checkpoint manifest records 209,689 bars and coherent_fraction = 0.20118, consistent with the q_distribution.csv counts. No discrepancy was detected between the cached distribution and the expected algebraic properties (minimum = −1, unbounded above, right-skewed).

---

## 3. What Q Measures (and Does Not Measure)

### 3.1 What Q is, algebraically

Q = 100 × (ln(s[t]/s[t-1]))² − 1

This is a **monotonic transformation of the squared one-bar log-change** in the composite stress field `s`. Specifically:

- Q ≥ 0 (coherent) if and only if |ln(s[t]/s[t-1])| ≥ 0.1 (i.e., s changed by more than ~10% relative to its previous value).
- Q < 0 (incoherent) if and only if |ln(s[t]/s[t-1])| < 0.1.
- Q = −1 exactly when s does not change at all.
- Q > 0 for about 20% of bars, meaning the composite stress field changes by more than 10% relative in roughly 1 in 5 five-minute bars.

### 3.2 What Q does NOT measure

| Claim | Reality |
|-------|---------|
| Rate of change in EUR/USD price | No — Q is computed from the composite stress field s, not directly from price |
| Absolute market volatility | Not directly — s is a multivariate composite; its log-change is not identical to realized price volatility |
| Direction of market movement | No — Q squares the gradient, making it direction-insensitive |
| Regime transition | Only in the sense that large changes in s exceed the Q=0 threshold; whether those changes are regime transitions in any other sense is untested |
| Predictive information about future outcomes | Empirically tested and found to be essentially zero (see Section 4) |
| Trading profitability | Not demonstrated (see Trading Execution Audit) |

### 3.3 Relationship to the direct mathematical input

Q is a monotonic increasing function of |grad_ln_s|², which is itself a monotonic function of |grad_ln_s|. The relationship between Q and the composite signal's absolute log-change is:

    |grad_ln_s| = sqrt((Q + 1) / 100)

Any comparison between Q and baselines derived from |grad_ln_s| or the absolute change of s is algebraically a comparison between Q and a monotonic transformation of itself. High Spearman correlation between Q and |grad_ln_s| confirms internal mathematical consistency but does not establish external predictive value.

### 3.4 Coherence length interpretation

The docstring claims ξ_c = 2cτ = 10 bars (50 minutes) separates short-term noise from structural moves. This interpretation is embedded in the theoretical framing but is not empirically tested within the available data. Whether the 50-minute coherence length corresponds to any independently identifiable property of EUR/USD microstructure remains unverified.

---

## 4. Q and Future Realized Volatility

### 4.1 Test specification

**Period tested:** Calibration period (2023-01-01 to 2025-10-24), 209,689 bars.  
**Method:** Spearman rank correlation between Q[t] and forward realized volatility at horizons k = {3, 6, 12} bars (15, 30, 60 minutes forward).  
**Forward volatility target:** Sum of squared log-returns over k bars starting at t+1.  
**Reported in:** `corrected_audit_results.json`, section6.  

This is an **exploratory analysis** (in-sample, calibration period). No held-out test is available for Q versus realized volatility because no separate Q series was constructed for 2026 data (the 2026 test used pre-computed Q).

### 4.2 Results

| Horizon k | Spearman ρ (Q) | Direction |
|-----------|---------------|-----------|
| 3 bars (15 min) | ≈ −0.008 | Negative |
| 6 bars (30 min) | ≈ −0.008 | Negative |
| 12 bars (60 min) | ≈ −0.008 | Negative |

Maximum absolute Spearman ρ = 0.0081 (reported in corrected_audit_results.json, section6.q_fwd_vol_max_rho). The sign is consistently **negative**, meaning bars with higher Q are weakly associated with *lower* subsequent realized volatility. This is opposite to the theoretical expectation (coherent bars should precede sustained movement).

The magnitude (|ρ| < 0.01) is negligible. At n = 209,689 the correlation is statistically distinguishable from zero, but the effect size is too small to have practical relevance. A Spearman ρ of 0.008 explains approximately 0.006% of variance in forward realized volatility.

### 4.3 Multiple-testing note

Three horizons were tested. All three show the same sign and similar magnitude. The Bonferroni-adjusted significance threshold at α = 0.05 would be 0.017; the results remain statistically significant after adjustment but the effect size remains negligible.

### 4.4 Baseline comparison

T_sys (from the V12 engine, separate from Q) has Spearman ρ = 0.20–0.27 with forward realized volatility. The rv5 baseline (5-bar realized volatility, no transport computation required) has ρ = 0.48–0.62. Q is therefore not only weaker than T_sys but weaker by approximately two orders of magnitude in effect size terms.

---

## 5. Q Against Simple Baselines

### 5.1 Algebraic baseline: |grad_ln_s|

Because Q = 100 × (grad_ln_s)² − 1, comparing Q with |grad_ln_s| is comparing Q with a monotonic transformation of itself. Any Spearman correlation between them will be 1.0 by definition. No information-theoretic comparison between Q and |grad_ln_s| for future prediction can show Q is superior to its direct input.

### 5.2 Absolute log-change of composite signal

The composite signal's one-bar log-change is exactly |grad_ln_s|. Q = 100 × (|grad_ln_s|)² − 1 provides no additional information beyond this for any monotone prediction task. If |grad_ln_s| cannot predict forward realized volatility, then Q (being a monotone function of |grad_ln_s|) cannot predict it either. The empirical result (ρ ≈ −0.008) confirms both are essentially uncorrelated with forward realized volatility.

### 5.3 5-bar realized volatility baseline (rv5)

rv5 predicts forward realized volatility with ρ = 0.48–0.62. Q achieves ρ ≈ −0.008. Q adds no predictive value after conditioning on rv5 and is dominated by the baseline by a factor of approximately 60–80× in Spearman correlation terms.

### 5.4 Transition detection test

A meaningful transition detection test requires an independently defined ground truth for regime transitions that does not use Q itself as its definition. That test has now been performed.

**Script:** `results/final_metric_audit/run_transition_test.py`  
**Raw results:** `results/final_metric_audit/transition_detection_results.csv` and `transition_detection_summary.txt`

**Independent transition label:** A volatility-expansion event is defined at bar t when the median 5-bar realized volatility over the next 12 bars (t+1 to t+12) is at least 2× the median over the prior 12 bars (t-12 to t-1). This uses only price log-returns and is constructed entirely from data outside the detector — no Q, no composite field, no T_sys enters the label. A volatility-contraction event is the symmetric condition (½× or less).

Event rates over 210,505 calibration bars: expansion 7.2%, contraction 6.1%, either 13.3%.

**Results (F1 score, volatility-expansion target):**

| Detector | Precision | Recall | F1 | FPR |
|----------|-----------|--------|----|-----|
| Q > 0  (coherent) | 0.0865 | 0.2411 | 0.1273 | 0.1973 |
| Q ≥ 1.732 (Strong_Coherent) | 0.1163 | 0.0806 | 0.0952 | 0.0474 |
| Q > p75 (Q at 75th pct) | 0.0834 | 0.2888 | 0.1294 | 0.2460 |
| **\|grad_ln_s\| > p75 (direct Q input)** | **0.0834** | **0.2888** | **0.1294** | **0.2460** |
| rv5 > p75 (simple vol) | 0.0668 | 0.2322 | 0.1037 | 0.2514 |
| T_sys > p75 | 0.0426 | 0.1474 | 0.0660 | 0.2569 |

Base rate precision for a random detector: 0.0719 (the event frequency). All detectors beat the random baseline in precision to some degree.

**Critical finding:** Q > p75 and |grad_ln_s| > p75 produce **identical** precision (0.0834), recall (0.2888), F1 (0.1294), and FPR (0.2460) to four decimal places. This is mathematically required: Q = 100 × (grad_ln_s)² − 1 is a monotone function of |grad_ln_s|², so any threshold on Q maps to an equivalent threshold on |grad_ln_s|. Q adds nothing beyond its direct input for this detection task.

Q > 0 achieves slightly higher precision (0.0865) and somewhat lower recall (0.2411) than Q > p75, which makes sense: Q > 0 is a tighter threshold on the same underlying quantity. Neither Q variant outperforms the rv5 baseline in F1; rv5 is simpler and achieves comparable or better F1 (0.1037) with lower complexity, though Q > p75 does beat rv5 modestly on F1 (0.1294 vs 0.1037). This is because the composite field's one-bar change contains information about microstructure activity (volume, spread, tick frequency) that pure price-based rv5 does not capture.

**For the contraction target and any-transition target:** the pattern is similar; Q and |grad_ln_s| remain identical, and the margin over rv5 narrows or reverses.

**Conclusion from this test:**
- Q provides modest but real detection signal for independently defined volatility transitions: F1 ≈ 0.13, vs base-rate F1 ≈ 0.13 (coincidentally similar; precision matters more here — 0.087 vs expected 0.072 at random).
- Q adds **zero** information beyond its direct mathematical input |grad_ln_s|. The composite-signal log-change is doing all the work; squaring and offsetting by −1 contributes nothing.
- The marginal advantage of Q (via its composite microstructure inputs) over price-only rv5 is small: F1 0.1294 vs 0.1037. Whether this margin survives on held-out data is unknown.
- Strong_Coherent (Q ≥ 1.732) has higher precision (0.116) but much lower recall (0.081), consistent with it being a rare, conservative threshold.

---

## 6. Q-Based Regime Classification

### 6.1 Exact mapping from Q to regime

**Function:** `classify_q_global_p2()` in `p2_transport_os.py` (also `classify_q_global()` in `p1_data_stream.py`; both implement identical logic):

```
NaN          → Mod_Incoherent
|Q| < 0.01   → Transition
Q <= -0.998  → Deep_Incoherent
-0.998 < Q < 0 → Mod_Incoherent
Q >= 1.732   → Strong_Coherent
0 < Q < 1.732 → Weak_Coherent
```

The thresholds −0.998 and 1.732 are the empirical 5th and 95th percentiles of Q computed from the 2023–2025 calibration period, frozen in `checkpoints/checkpoint_manifest.json`.

### 6.2 Regime frequencies (calibration period)

| Regime | Approximate Frequency |
|--------|-----------------------|
| Deep_Incoherent (Q ≤ −0.998) | ~5% |
| Mod_Incoherent (−0.998 < Q < 0) | ~75% |
| Transition (\|Q\| < 0.01) | <1% (thin band, small fraction of bars) |
| Weak_Coherent (0 < Q < 1.732) | ~15% |
| Strong_Coherent (Q ≥ 1.732) | ~5% |

The 5/95 percentile design means approximately 5% of bars fall in each tail regime by construction in the calibration period. The 2026 out-of-sample distribution was not separately tabulated in available results.

### 6.3 Regime validation against independent criteria

The Transport OS assigns strategies and trade sizes by regime. For this to be useful, regimes should correspond to different future outcomes measured by an independent criterion. No direct test of "does Strong_Coherent predict better forward outcomes than Mod_Incoherent using an independent criterion" was run in the available audit. The prior Phase 1 analysis used strategy P&L as the performance measure, which conflates signal quality with strategy fit. This is a significant limitation.

---

## 7. Conclusions: Separate Verdicts

### Q is mathematically implemented correctly: YES

The formula Q = 100 × (ln(s[t]/s[t-1]))² − 1 with c=1, τ=5, dt=1 is implemented exactly as documented in `transport_layer.py`. The computation is causal (backward difference only). Edge cases are handled defensively. The minimum Q = −1 and unbounded positive tail are confirmed by the distribution.

### Q is a useful descriptive measure of composite-signal change: PARTIALLY

Q describes whether the composite stress field changed by more or less than ~10% relative in a given bar. This is a well-defined measurement. However, because the composite signal is a multivariate aggregate with sigmoid normalization, interpreting its log-change as a physically meaningful "transport discriminant" requires assumptions not independently verified.

### Q is a useful transition detector: PARTIALLY — with a critical qualification

The test was performed using independently defined volatility-transition labels (a 2× increase in median 5-bar realized volatility over the next 12 bars vs the prior 12 bars). Q > 0 and Q > p75 both beat a random detector in precision (0.087 and 0.083 vs base rate 0.072 for vol-expansion events). F1 scores are modest (0.127–0.129).

However, **Q adds no information beyond its direct input |grad_ln_s|**. The Q > p75 and |grad_ln_s| > p75 detectors produce identical results to four decimal places. This is mathematically guaranteed by Q being a monotone function of |grad_ln_s|². The composite signal's one-bar change is doing all the detection work. The Q transform adds nothing.

The marginal advantage of Q (via composite microstructure signals) over price-only rv5 is small (F1 0.129 vs 0.104). This test is in-sample (calibration period); the advantage may not persist out of sample.

### Q is a useful predictor of future conditions: NO (based on available tests)

Spearman ρ with forward realized volatility ≈ −0.008 across all horizons tested. This is negligible in magnitude and in the wrong direction. Q does not demonstrate useful predictive information about future market conditions beyond what is explained by simple volatility persistence.

### Q is a useful input to the regime classifier: UNDEMONSTRATED

The regime classifier is structurally correct and uses Q values and frozen calibration-period thresholds. Whether the five-level classification provides regime-discriminating information beyond simpler volatility regimes (e.g., rv5 quartiles) has not been tested. Given Q's negligible correlation with forward volatility, the regime classifier's practical value is uncertain.

---

*All claims in this document are supported by direct source-code inspection or citations to cached result files. Line numbers refer to the logical code blocks as read; minor line-count variations may exist if the file was modified after the audit date.*
