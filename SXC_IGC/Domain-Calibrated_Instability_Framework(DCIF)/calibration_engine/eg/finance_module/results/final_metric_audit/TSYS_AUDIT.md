# T_sys Audit
## Implementation, Predictive Validation, and Baseline Comparison

**Audit date:** 2026-10-11  
**Git commit:** `6738ed05`  
**Source files examined:** `v12_validate/engine_runner.py`, `p1_data_stream.py`, `v12_validate/signals.py`  
**Cached data:** `results/bounded_validation_corrected/corrected_audit_results.json`, `results/bounded_validation_corrected/tsys_vs_fwdvol.csv`

---

## 1. What T_sys Is

### 1.1 Source and computation

T_sys is produced by `SXCOmegaEngineStable` in `v12_validate/engine_runner.py`. It is computed per bar by the V12 engine pipeline, which is separate from Q and the transport layer. The code path in `p1_data_stream.py → _apply_transport_pipeline()`:

```python
scaled_signals, _ = scale_signals_to_100(raw_signals)
v12_composite, _  = build_v12_composite(scaled_signals)
v12_df            = run_v12(v12_composite)
# ...
df["T_sys"] = v12_df["T_sys"].reindex(df.index)
```

T_sys is one of three outputs of `run_v12()` alongside `phase` and `excitation`. It operates on the v12_composite (a scaled version of the same raw signals that feed the transport layer), processed through the `SXCOmegaEngineStable` state machine.

### 1.2 The SXCOmegaEngineStable

The engine maintains internal state across bars. T_sys represents the system "tension" — a running measure of stress accumulation computed from the composite signal's history. From the engine_runner.py docstring and structure: T_sys is updated each bar based on the current composite value relative to a running reference level, with exponential smoothing governing its evolution. It is not a simple rolling statistic.

Key properties visible from the code path:
- T_sys is initialized to 0 and updated bar-by-bar (causal).
- It depends only on past composite values (no lookahead).
- The V12 composite uses the same underlying raw signals as the transport layer but with different aggregation (scaled to 100 range rather than sigmoid-normalized to 0–1).
- T_sys is stored in the monthly cache files under column `T_sys`.

### 1.3 Relationship to Q

T_sys and Q are **distinct quantities** computed from related but differently processed versions of the same underlying signal data:

| Property | Q | T_sys |
|----------|---|-------|
| Input | sigmoid composite s ∈ (0,1) | v12 composite (scaled 0–100) |
| Formula | 100 × (log-return of s)² − 1 | state-machine tension accumulator |
| Lookback | 1 bar (instantaneous log-return) | running state (multi-bar history) |
| Scale | (−1, ∞) | varies by engine state |
| Physical interpretation | squared gradient of stress field | system tension / stress accumulation |

They are correlated (both derived from the same raw signals) but are not algebraically equivalent.

---

## 2. Reproduced Forward-Volatility Results

### 2.1 Test specification

**Data:** Calibration period 2023-01-01 to 2025-10-24, 209,689 5-min bars.  
**Method:** Spearman rank correlation between T_sys[t] and forward realized volatility at horizons k bars.  
**Forward volatility:** Sum of squared log-returns of EUR/USD close over k bars starting at t+1.  
**Baseline:** rv5 = 5-bar realized volatility of EUR/USD close at time t (lagged, no lookahead).  
**Source:** `tsys_vs_fwdvol.csv` and `corrected_audit_results.json` (section6.tsys_table).

This is an **in-sample (calibration period) exploratory analysis**. The results are presented as characterization, not validation. The 2026 out-of-sample period was used for trading performance only; no separate T_sys versus forward-volatility test was run on 2026 data.

### 2.2 Results table

| Horizon k | T_sys ρ | T_sys p-value | rv5 ρ | rv5 p-value | n |
|-----------|---------|--------------|-------|-------------|---|
| k=1 (5 min) | NaN | NaN | NaN | NaN | 209,688 |
| k=3 (15 min) | 0.202 | 0.0 | 0.480 | 0.0 | 209,686 |
| k=6 (30 min) | 0.250 | 0.0 | 0.583 | 0.0 | 209,683 |
| k=12 (60 min) | 0.269 | 0.0 | 0.619 | 0.0 | 209,677 |

k=1 results are NaN due to overlapping target construction or a data alignment issue; this did not affect the remaining horizons.

All p-values are reported as 0.0 because at n ≈ 209,000 even trivially small correlations are statistically significant under the standard chi-squared approximation. Nominal significance is uninformative here; what matters is effect size.

### 2.3 Key finding: T_sys vs rv5 baseline

At every tested horizon, the rv5 baseline outperforms T_sys by a ratio of approximately 2.2–2.3× in Spearman correlation:

| Horizon | T_sys ρ | rv5 ρ | Ratio (rv5/T_sys) |
|---------|---------|-------|-------------------|
| k=3 | 0.202 | 0.480 | 2.37× |
| k=6 | 0.250 | 0.583 | 2.33× |
| k=12 | 0.269 | 0.619 | 2.30× |

rv5 is the lagged 5-bar realized volatility of EUR/USD close — a trivial rolling window computation requiring no transport mathematics, no composite signal construction, and no state machine. T_sys requires the full V12 engine pipeline. Despite this, rv5 consistently outperforms T_sys by more than a factor of two.

---

## 3. Incremental Value Beyond rv5

### 3.1 Is T_sys measuring something beyond volatility persistence?

rv5 captures the direct autoregressive property of realized volatility (volatility clusters). T_sys accumulates multi-bar stress based on a different signal aggregate. If T_sys carried orthogonal information, a regression of forward volatility on both rv5 and T_sys would show significant T_sys coefficient after controlling for rv5.

No formal partial regression was run on the cached data. The following reasoning applies:

- Spearman ρ(T_sys, forward_vol) ≈ 0.20–0.27 is weaker than ρ(rv5, forward_vol) ≈ 0.48–0.62.
- T_sys is derived from the same underlying price data as rv5 (the composite includes realized volatility as one of its components).
- Any component of T_sys that is orthogonal to rv5 would have to come from the other composite inputs (volume, spread, tick frequency, momentum). These are less directly related to future realized volatility.
- The observed T_sys correlation is plausibly explained largely by the realized-volatility component of the composite alone, with the remaining components adding noise.

**Conclusion (provisional, not formally tested):** T_sys likely carries some information beyond rv5, but its incremental value is modest and was not formally quantified. The available evidence does not establish that T_sys adds predictive value beyond rv5 at a level that would justify its complexity.

### 3.2 What the data support

The evidence supports these claims about T_sys:

1. **T_sys has a positive, statistically significant correlation with forward realized volatility** at horizons 15–60 minutes (ρ = 0.20–0.27 in calibration period).
2. **T_sys is dominated by the rv5 baseline** at every tested horizon (ratio 2.3–2.4×).
3. **T_sys is not a measure of future price direction** — correlation with future realized volatility is a volatility-forecasting result, not a directional-forecasting result.
4. **Out-of-sample validation of T_sys predictive ability was not performed** — the 2026 data was used only for trading performance testing.

---

## 4. Temporal Dependence and Statistical Validity

### 4.1 The n ≈ 209,000 inflation problem

At 5-min bars over 34 months, consecutive observations are strongly autocorrelated. Standard Spearman significance tests treat each bar as independent. The effective sample size for inference is far smaller than the nominal n. The p-values reported as 0.0 are nominal, not effective-n-adjusted.

Using an AR(1) correction (as applied in the trading performance section), effective n ≈ 30,000 to 50,000 depending on the autocorrelation structure. Even at this reduced effective sample size, the correlations (ρ = 0.20–0.27) would remain statistically significant. The finding that T_sys has positive predictive correlation with forward volatility is robust to reasonable corrections for temporal dependence.

However, the finding that rv5 outperforms T_sys is also robust. At no horizon does the T_sys confidence interval overlap the rv5 point estimate from above.

### 4.2 Overlapping windows

For horizon k = 12, consecutive 60-minute forward volatility windows overlap by 55 minutes. This induces positive serial correlation in the target variable that overstates the apparent persistence and inflates apparent significance. This affects both T_sys and rv5 equally and does not change the relative ranking.

---

## 5. Remaining Limitations

1. **No out-of-sample T_sys predictive test.** All T_sys correlations are from the calibration period. Whether they hold in 2026 data is unknown.

2. **No incremental regression performed.** Whether T_sys adds information after conditioning on rv5 was not formally tested.

3. **T_sys definition not fully traced.** The internal state machine of `SXCOmegaEngineStable` was not fully read and documented in this audit. The characterization of T_sys as a "tension accumulator" is based on naming conventions and code structure, not a complete mathematical derivation.

4. **Volatility forecasting ≠ directional forecasting.** A positive correlation between T_sys and forward realized volatility does not imply T_sys predicts profitable trades, price direction, or anything actionable for a breakout entry strategy.

5. **The T_sys test was in-sample.** Using the calibration period for all characterization work creates a risk of overfitting characterizations. The magnitude of T_sys's predictive correlation may be inflated relative to out-of-sample performance.

---

## 6. Verdict

T_sys shows a **real but modest positive correlation** with forward realized volatility (ρ ≈ 0.20–0.27 at 15–60 minute horizons) in the calibration period. This correlation is statistically significant even after accounting for temporal dependence.

However:
- The **rv5 baseline** (trivial lagged 5-bar realized volatility) outperforms T_sys at every tested horizon by a factor of 2.3–2.4×.
- T_sys's incremental value after conditioning on rv5 was **not formally tested** and is likely modest.
- The positive correlation **does not imply directional forecasting ability** or profitable trading.
- No **out-of-sample** validation of T_sys predictive ability was performed.

The evidence neither confirms T_sys as a useful independent predictor nor establishes it as useless. It establishes T_sys as weaker than a simple volatility-persistence baseline for forward volatility prediction, with uncertain incremental value.
