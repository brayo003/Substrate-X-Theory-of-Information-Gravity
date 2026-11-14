# Final Audit Verdict
## Q Metric, T_sys, Regime Classifier, and Transport OS Trading Configuration

**Audit date:** 2026-10-11  
**Git commit:** `6738ed05`  
**Audit scope:** Independent evidence-based evaluation of all claimed properties.  
**Output directory:** `results/final_metric_audit/`  
**Prior results preserved at:** `results/bounded_validation/` and `results/bounded_validation_corrected/`

This document states what the evidence supports, what is provisional, and what is unsupported. It does not optimize for a favorable conclusion and does not declare the system functional or nonfunctional beyond what the data can establish.

---

## Executive Summary

The audit found one material correction to the prior validation: the original 76-trade backtest used the wrong signal. The actual `NY_Continuation` strategy from `strategy_library.py` (EMA crossover, hour 13 UTC only) generates 7 trades on 2026 OOS data, all showing PF < 1.0 at every cost assumption. Seven trades are wholly insufficient for statistical inference and neither confirm nor refute the existence of a trading edge.

The Q metric is mathematically implemented correctly but has negligible predictive correlation with forward realized volatility (|ρ| < 0.01). T_sys has a real positive correlation with forward volatility (ρ ≈ 0.20–0.27) but is outperformed by a trivial 5-bar realized-volatility baseline by a factor of 2.3×. Neither Q nor T_sys has demonstrated useful predictive value beyond simple baselines.

---

## 1. Separate Verdict: Q Metric

### 1.1 Is Q mathematically correct? YES

The formula Q = 100 × (ln(s[t]/s[t-1]))² − 1, with c=1, τ=5, dt=1 bar, is implemented exactly as documented in `v12_validate/transport_layer.py`. The computation uses a backward difference (causal). Edge cases are handled defensively. Q = −1 at no-change bars and is unbounded above for large changes. The implementation matches the stated formula.

### 1.2 Is Q a useful descriptive measure? PARTIALLY

Q measures whether the composite stress field `s` changed by more than ~10% relative in a given 5-minute bar. This is a well-defined measurement of the instantaneous volatility of the composite field. The composite field is a sigmoid-normalized multivariate aggregate of rolling price microstructure features. Q's relationship to EUR/USD price volatility is indirect and mediated by the composite construction.

The distribution is severely left-skewed: 62% of bars have Q in the range [−1, −0.64], meaning the composite field barely moves for the majority of bars. Only 20% of bars have Q > 0 (coherent). The regime classifier's design (10th and 90th percentile thresholds by design) assigns Strong_Coherent to the top 5% of bars. This is a reasonable descriptive classification of relative composite-field activity.

### 1.3 Is Q a useful transition detector? PARTIALLY — with a critical qualification

A transition-detection test was performed using independently defined labels: a volatility-expansion event at bar t if the median 5-bar realized vol over the next 12 bars is ≥ 2× the prior 12 bars (7.2% event rate). Results from `run_transition_test.py` over 210,505 calibration bars:

Q > 0 achieves precision 0.087 (vs base rate 0.072), recall 0.241, F1 0.127 — a modest but real detection signal over a random baseline. Q ≥ 1.732 (Strong_Coherent) achieves higher precision (0.116) at the cost of lower recall (0.081).

**Critical finding:** Q > p75 and |grad_ln_s| > p75 produce identical results (F1 0.1294, precision 0.0834, recall 0.2888) to four decimal places. This is not a coincidence — it is mathematically guaranteed because Q is a monotone function of |grad_ln_s|². **Q adds zero information beyond its own input, the absolute one-bar log-change of the composite field.**

The margin of Q over the price-only rv5 baseline in F1 is small (0.129 vs 0.104). Whether the composite-signal microstructure information driving this gap is stable out of sample is unknown. The transition detection finding is in-sample only.

### 1.4 Is Q a useful predictor of future conditions? NO (within available tests)

Spearman ρ between Q and forward realized volatility at all tested horizons (15–60 minutes forward): ρ ≈ −0.008. Magnitude is negligible; the sign is negative (opposite to theoretical expectation). Q adds essentially no predictive information about future realized volatility compared to a constant predictor, let alone compared to rv5 (ρ = 0.48–0.62).

**Note:** These tests are in-sample (calibration period). Out-of-sample Q predictive testing was not performed.

### 1.5 Is Q a useful input to the regime classifier for trading? NOT DEMONSTRATED

The regime classifier correctly applies frozen Q thresholds from the calibration period to 2026 data. Whether the regime classification improves trading outcomes is a separate empirical question. The available evidence (7 OOS trades, non-significant bootstrap comparison) cannot establish this claim. The correlation between Q and forward price volatility is too small to expect regime-based filtering to add value unless the effect operates through a different mechanism not tested here.

---

## 2. Separate Verdict: T_sys

### 2.1 Does T_sys have predictive correlation with forward volatility? YES (in-sample, modest)

Spearman ρ = 0.20–0.27 at 15–60 minute horizons in the calibration period (209,689 bars). This is a real, statistically significant correlation. It survives temporal-dependence correction (effective n still large enough for significance).

### 2.2 Does T_sys outperform a simple baseline? NO

The rv5 baseline (5-bar realized volatility) achieves ρ = 0.48–0.62 at the same horizons — approximately 2.3× the T_sys correlation. rv5 requires no composite signal, no state machine, and no transport mathematics. T_sys is dominated by this baseline at every tested horizon.

### 2.3 Does T_sys add incremental value beyond rv5? NOT ESTABLISHED

No partial regression or controlled comparison was performed. T_sys likely shares substantial variance with rv5 (realized volatility is a component of the composite signal). Whether T_sys adds orthogonal information was not formally tested. The evidence does not support or reject this claim.

### 2.4 Does T_sys predictive ability hold out-of-sample? NOT TESTED

All T_sys predictive correlations are from the calibration period. No 2026 T_sys predictive test was run. Out-of-sample performance is unknown.

### 2.5 Does T_sys imply directional forecasting or profitable trading? NO

A correlation between T_sys and forward realized volatility is a volatility-forecasting result. It implies T_sys may provide some signal about whether the market will be more or less volatile in the next 15–60 minutes. It does not imply directional forecasting, and it does not imply the seven OOS trades have positive expectancy.

---

## 3. Separate Verdict: Q-Based Regime Classifier

### 3.1 Is the classifier correctly implemented? YES

The five-level classification (Deep_Incoherent, Mod_Incoherent, Transition, Weak_Coherent, Strong_Coherent) correctly applies frozen calibration-period quantile thresholds. The code in `p2_transport_os.py:classify_q_global_p2()` and `p1_data_stream.py:classify_q_global()` are consistent. The thresholds are loaded from the checkpoint manifest (not recomputed from 2026 data).

### 3.2 Does the classifier produce interpretable regime labels? YES, with caveats

The five regimes provide a consistent partitioning of Q into ranked categories. Because Q is a monotone function of the composite field's absolute log-change, the regimes are effectively ordinal buckets of composite-field volatility intensity. The names (Coherent, Incoherent) are imported from the theoretical framework but their empirical correspondence to the named concepts has not been tested independently.

### 3.3 Does regime classification improve trading outcomes? NOT DEMONSTRATED

The bootstrap comparison (p = 0.37–0.38) found no significant difference between the 7 Strong_Coherent trades and randomly selected hour-13 trades. This is consistent with the null hypothesis that the regime gate adds no value. It is also consistent with the test having insufficient power (only 61 total hour-13 trades). The evidence is insufficient to decide this question.

### 3.4 Is out-of-sample regime stability established? PARTIAL

The calibration period produced q05 = −0.998 and q95 = 1.732 from 209,689 bars. Whether the 2026 Q distribution has the same shape (i.e., whether the frozen thresholds still correspond to the intended 5th and 95th percentiles in 2026) was not formally tested. The 2026 test had only 44,940 bars from which a Q distribution could be estimated. No 2026 Q distribution was tabulated in the available results.

---

## 4. Separate Verdict: Transport OS Trading Configuration

### 4.1 Does the configuration correctly implement the intended strategy? YES (after correction)

After correcting the strategy mismatch (wrong RSI/MACD/ADX signal replaced with the correct `strategy_library.py:NY_Continuation`), the configuration correctly gates trades to Strong_Coherent regime only, applies frozen Q thresholds, and executes EMA crossover entries at hour 13 UTC.

### 4.2 Has the configuration demonstrated a trading edge on OOS data? NO

Seven out-of-sample trades with PF = 0.17–0.54 (all cost scenarios), all below 1.0. 95% CI on expectancy contains zero. Bootstrap comparison vs random selection: non-significant. The configuration has not demonstrated an edge.

### 4.3 Can the configuration be declared definitively unprofitable? NO

Seven trades is insufficient to rule out a modest positive edge. Power to detect PF = 1.5 is approximately 5–15%. The OOS result is consistent with both zero edge and moderate negative edge. Approximately 200–500 OOS trades would be needed to make a reliable inference, requiring several years of continuation data under similar market conditions.

### 4.4 Is the original 76-trade result valid? NO

The 76 trades were generated by a custom RSI+MACD+ADX signal during hours 14–20 UTC. This signal is not defined in `strategy_library.py` and is not the Phase 2 strategy. Those results measure an undefined strategy and cannot be attributed to the Transport OS configuration.

---

## 5. What Has Been Established

The following are factual findings supported by direct source-code inspection or cached numerical results:

1. **Q formula:** Verified as Q = 100 × (ln(s[t]/s[t-1]))² − 1 with c=1, τ=5, computed from backward difference of causal sigmoid composite. Correct.

2. **Q is direction-insensitive:** Confirmed by the squaring operation. Equal positive and negative changes of s give identical Q values.

3. **Q has a minimum of −1:** Confirmed algebraically and by the distribution (minimum bin at −1).

4. **Q accounts for ~20% coherent bars:** Confirmed (q_distribution.csv, 209,689 calibration bars, coherent fraction 0.201).

5. **Q predictive correlation with forward volatility is negligible:** Confirmed (|ρ| < 0.01 at all horizons).

6. **T_sys has positive but modest predictive correlation with forward volatility:** Confirmed (ρ = 0.20–0.27 in calibration period).

7. **rv5 dominates T_sys at every tested horizon:** Confirmed (rv5 ρ = 0.48–0.62 vs T_sys 0.20–0.27).

8. **Corrected OOS strategy generates 7 trades with PF < 1.0:** Confirmed (all cost scenarios, CSV trade logs verified).

9. **Original 76-trade result used the wrong signal:** Confirmed by comparing strategy source code against bounded_validation.py's custom function.

10. **Q thresholds were derived from calibration data and not from 2026 data:** Confirmed (manifest timestamps, absence of 2026 cache files).

---

## 6. What Remains Provisional or Unresolved

1. **Whether T_sys adds incremental value beyond rv5:** Not formally tested. Remains unresolved.

2. **Whether the regime gate adds trading value in larger samples:** The 7-trade test has insufficient power. The question is open.

3. **Whether Q identifies meaningful market transitions:** No independent transition labels were available. Unresolved.

4. **Out-of-sample T_sys predictive ability:** Not tested. Unknown.

5. **Whether the Q distribution is stable in 2026:** Not tabulated. Unknown.

6. **Whether the 2026 raw data was informally known during design:** Cannot be established from file artifacts alone. Minor unresolvable uncertainty.

---

## 7. What Is Not Supported

1. **The claim that Q is a useful predictor of future market conditions** — contradicted by empirical tests (ρ ≈ −0.008).

2. **The claim that T_sys outperforms simple baselines** — contradicted by rv5 comparison (rv5 achieves 2.3× higher ρ).

3. **The claim that the trading configuration has demonstrated an OOS edge** — not supported (PF < 1.0 at all scenarios, CI contains zero).

4. **The 76-trade trading result as evidence for Phase 2 strategy performance** — that result used the wrong signal.

5. **Statistical significance (in the T_sys vs volatility test) as evidence of practical usefulness** — at n = 209,000, even negligible effects are statistically significant. Effect size matters; ρ = 0.20–0.27 is real but modest.

---

## 8. Files in This Audit Package

| File | Contents |
|------|----------|
| `FINAL_AUDIT_VERDICT.md` | This document — executive verdicts and summary |
| `Q_METRIC_AUDIT.md` | Q formula trace, distribution, predictive tests, baseline comparisons |
| `TSYS_AUDIT.md` | T_sys implementation, forward-volatility results, baseline comparison |
| `TRADING_EXECUTION_AUDIT.md` | Strategy source, execution path, 7-trade record, cost model, uncertainty |
| `DATA_AND_STATISTICAL_AUDIT.md` | Data provenance, split, leakage review, statistical assumptions |

All prior results are preserved at their original locations and were not modified:
- `results/bounded_validation/` — original (wrong signal) backtest
- `results/bounded_validation_corrected/` — corrected audit
