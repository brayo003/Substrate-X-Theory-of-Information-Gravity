# Bounded Validation Report: Transport OS / Q Regime System
## SXC-IGC Finance Module — Complete Trading Edge Investigation

**Report Date:** 2026-10-11  
**Git Commit at Run Time:** `6738ed05`  
**Script:** `bounded_validation.py` (reproducible, no parameters changed)  
**Output directory:** `results/bounded_validation/`  
**Total run time:** 22.8 seconds  

---

## 1. Pipeline Trace (Phase 1 — Complete)

### 1.1 Q Calculation — Step by Step

**Input:** Raw BI5 ticks (2023–2024) or 1-minute CSV (2025, 2026)  
**Output:** 5-minute OHLC bars with `tr_Q`, `T_sys`, `phase`, and technical indicators  
**Code path:** `p1_data_stream.py → v12_validate/signals.py → engine_runner.py → transport_layer.py`

| Step | Operation | Look-ahead? |
|------|-----------|-------------|
| 1 | Ticks → 5-min OHLC via `build_ohlc()` | No |
| 2 | 6 signals: volatility (rolling 20), volume_ratio (MA50), spread_ratio (MA50), tick_freq (rolling 20), momentum_20min (pct_change(4)), momentum_1hr (pct_change(12)) | No — all backward-looking |
| 3 | Normalize: z-score with 99th-percentile clipping → sigmoid → (0,1) | No |
| 4 | Composite s = row-mean of normalized signals | No |
| 5 | V12: scale raw signals to [0,100] via 2nd/98th percentile; build composite; rescale to median=8 | No |
| 6 | `SXCOmegaEngineStable.step()`: advances T_sys, phase (NOMINAL/FIREWALL) bar by bar | No |
| 7 | Transport layer: `Q = 4(cτ)² * (grad_ln_s)² − 1` where `grad_ln_s = ln(s[t]/s[t-1])` | **No — backward difference only** |
| 8 | 5-level classification using frozen thresholds q05=−0.998, q95=1.732 | No |

**Leakage verdict: NONE FOUND.** Every signal uses rolling windows of past data. `grad_ln_s` is a backward difference using only `s[t]` and `s[t-1]`.

### 1.2 What Q Actually Measures

Q is defined as:
```
Q = 4(cτ)² · (d/dt ln(s))² − 1
  = 100 · (d/dt ln(s))² − 1    [with c=1.0, τ=5.0]
```

Q > 0 when `|d/dt ln(s)| > 0.1` — the stress composite is changing rapidly (transitions)  
Q < 0 when `|d/dt ln(s)| < 0.1` — the stress composite is near-flat (stable or subdued)

**Critical distinction:** Q measures the **rate of change** of the composite, not its **level**. Strong_Coherent (Q ≥ 1.73) fires during abrupt stress transitions, not during sustained high-stress periods. This is different from T_sys, which measures cumulative stress level.

### 1.3 Execution Path (P1 Strategy Runner)

```
bar i close → strategy_fn(df) → signal ∈ {-1, 0, +1}
entry_price = close[i]
stop_price  = entry_price − direction × 1.5 × atr[i]
target_price = entry_price + direction × 2.5 × atr[i]
exit: check high/low bars j > i (no bar-i information used)
max hold = 24 bars (2 hours at 5-min bars)
cost: TOTAL_COST_RT = 0.00030 subtracted directly from gross_ret ✓ (correct post-fix)
```

### 1.4 Data Split — Confirmed Circular for EUR/USD

| Period | Used for |
|--------|----------|
| 2023–2025 EUR/USD | Q threshold calibration (q05, q95) |
| 2023–2025 EUR/USD | Phase 1 strategy performance matrix |
| 2023–2025 EUR/USD | Phase 2 OS calibration (reads Phase 1 results) |
| 2023–2025 EUR/USD | Phase 2 evaluation (SAME as calibration) |
| **2026 EUR/USD** | **Genuinely untouched — used only in this report** |

---

## 2. Test Results

### TEST A — Frozen OS on 2026 EUR/USD (Genuinely Out-of-Sample)

**Data:** `data/2026/eurusd-m1-bid-2026-01-01-2026-07-22.csv`  
**Parameters:** Frozen OS — no re-calibration, same q05/q95, same strategy (NY_Continuation), same ATR multipliers  
**Period:** Jan 1 – Jul 21, 2026 (≈ 6.75 months)  
**5-min bars processed:** 44,940  
**Strong_Coherent fraction:** 4.7% (consistent with 2023–2025's 4.98%)

| Cost Assumption | Trades | PF | Win Rate | Expectancy | Sharpe | Max DD |
|----------------|--------|-----|----------|------------|--------|--------|
| 3-pip RT (original) | 76 | **0.469** | 36.8% | −0.000318 | −3.07 | 2.67% |
| 5-pip RT (conservative retail) | 76 | **0.292** | 31.6% | −0.000518 | −5.00 | 4.11% |
| 7-pip RT (wide retail) | 76 | **0.175** | 30.3% | −0.000718 | −6.92 | 5.55% |

**Result: The frozen OS LOSES money on genuinely unseen 2026 data at every cost assumption tested, including the most optimistic (3-pip RT).**

The PF=1.077 reported for 2023–2025 is not reproduced. The 2026 result shows PF=0.469 at identical costs. This is the definitive test.

### TEST B — Matched-Frequency Random-Entry Bootstrap

**Method:** 10,000 bootstrap replications, each sampling 76 trades (same n as OS) without replacement from the full pool of 797 NY_Continuation trades on 2026 data, ignoring Q filter entirely.  
**Cost:** 5-pip RT

| Metric | Value |
|--------|-------|
| OS PF (5-pip RT) | 0.292 |
| Random bootstrap mean PF | 0.237 |
| Random bootstrap p95 | 0.370 |
| p-value (OS PF ≥ random PF) | **0.2077** |
| Fraction of random samples with PF ≥ 1.0 | **0.0%** |

**Result: The OS result (PF=0.292) is NOT significantly better than randomly selecting 76 trades from the same pool (p=0.21). The Q filter provides no measurable improvement in 2026.**

Importantly, 0% of bootstrap samples achieve PF ≥ 1.0, confirming that NY_Continuation itself has no edge in 2026 regardless of filtering.

### TEST C — Q Regime-Conditioned Trade Outcomes (In-Sample Characterization)

**Data:** Phase 1 trade log — `results/phase1/trade_log_full.csv` (655 trades, 2023–2025 in-sample)  
**Cost:** 3-pip RT

| Regime | N trades | PF | Win Rate | Expectancy |
|--------|----------|----|----------|------------|
| Deep_Incoherent | 25 | 0.132 | 20.0% | −0.000539 |
| Mod_Incoherent | 563 | 0.601 | 33.2% | −0.000230 |
| Transition | 0 | — | — | — |
| Weak_Coherent | 26 | 0.823 | 61.5% | −0.000044 |
| **Strong_Coherent** | **41** | **9.805** | **51.2%** | **+0.003373** |

**Mann-Whitney U test: Strong_Coherent vs all others**  
U=14,168 · p=0.0889 · r_biserial=−0.126

**Result: The PF=9.8 for Strong_Coherent (41 trades in-sample) is NOT statistically significant (p=0.089, above 5% threshold). This is the in-sample overfitting artifact that the 2026 OOS test directly refutes.**

The dramatic PF difference visible in the in-sample data (PF=9.8 vs PF=0.6) does not replicate on 2026 data (TEST A shows uniform loss regardless of regime quality).

### TEST D — Q vs Future Volatility (Non-Circular Spearman Check)

**Data:** Full Q series from cache (209,689 bars, 2023–2025)  
**Target:** Forward realized volatility at horizons k=1,3,6,12 bars  
**Causality check:** Q uses `s[t]` and `s[t-1]`. Forward window starts at `t+1`. **No overlap confirmed.**

| Lag k | Spearman ρ | p-value | Sig |
|-------|-----------|---------|-----|
| 1 | NaN | NaN | — (first bar undefined, expected) |
| 3 | −0.0054 | 0.013 | * |
| 6 | −0.0074 | 0.001 | *** |
| 12 | −0.0081 | 0.0002 | *** |

**Result: Q is NEGATIVELY correlated with future realized volatility (ρ ≈ −0.005 to −0.008).** This is statistically significant but economically tiny, and the sign is negative.

**This appears to contradict the V12 validation results** (where T_sys positively predicts future realized vol at ρ=+0.27). The resolution:
- **T_sys** (the SXCOmega engine state) accumulates stress over time → high T_sys = currently high-stress → next period likely still high-stress → **positive** predictive correlation
- **Q** (the transport discriminant) fires when the composite is changing *rapidly* → marks transition points → after a fast change, the composite tends to revert → next period's volatility tends to be lower → **negative** predictive correlation

These are different quantities measuring different properties. The trading system uses Q (not T_sys) for regime gating. T_sys's predictive power does not transfer to Q.

---

## 3. Assessment Against the Five Hypotheses

| Hypothesis | Verdict | Evidence |
|-----------|---------|----------|
| **H1:** Signal contains useful information that improves trading decisions | **Not supported** | TEST A: PF=0.469 OOS. TEST B: p=0.21, Q provides no selection benefit |
| **H2:** Signal classifies current conditions but has little incremental predictive value | **Partially supported** | Q classifies transition points validly (TEST D, causal). But T_sys — not Q — has the useful predictive signal |
| **H3:** Signal has useful info but strategy/execution fails to monetize it | **Not supported** | TEST D shows Q negatively predicts vol; the signal itself is oriented wrong for the strategy |
| **H4:** Results explained by selection bias, costs, insufficient data | **Supported** | In-sample PF=9.8 (41 trades) is pure small-sample overfitting; not reproduced OOS; circular data split |
| **H5:** Available data cannot resolve the question | **Partially supported** | 76 OOS trades cannot prove the negative definitively, but directional evidence is strongly against |

---

## 4. What Changed and Why

### Changes Made During This Validation

**`bounded_validation.py` (new file)** — Self-contained validation script. Frozen parameters, no optimization. Reproducible.

**No changes to strategy logic, Q thresholds, cost constants, or any existing pipeline file.** The execution engine `p1_strategy_runner.py` and `p2_execution_engine.py` already had the cost-division-by-price bug fixed (July 30, 2026) and use `TOTAL_COST_RT = 0.00030` subtracted directly.

**The Phase 2 results (PF=1.077, 43 trades) were already produced with the corrected cost model.** They reflect the in-sample performance with correct costs, not a bug artifact.

### What the Phase 2 "Outperformance" Actually Was

The Phase 2 report showed Transport OS PF=1.077 vs all baselines PF < 0.55. This comparison was misleading:
1. All baselines are high-frequency losers (8,000–14,000 trades/year) whose losses compound
2. The OS generates 43 trades over 2.5 years — effectively close to a no-trade strategy
3. Avoiding trading in a loss-generating system is not the same as finding an edge
4. The 43-trade in-sample result has a 95% confidence interval on PF that spans well below 1.0

---

## 5. Exact Data Periods and Costs

| Test | Data Period | Bars | Cost Assumption |
|------|------------|------|-----------------|
| Phase 1 (existing) | Jan 2023 – Oct 2025 | 209,689 | 0.0003 RT (3-pip) |
| Phase 2 (existing) | Jan 2023 – Oct 2025 | Same | 0.0003 RT (3-pip) |
| **TEST A (this report)** | Jan 1 – Jul 21, 2026 | 44,940 | 0.0003 / 0.0005 / 0.0007 |
| TEST B bootstrap | Jan 1 – Jul 21, 2026 | 44,940 | 0.0005 |
| TEST C characterization | Jan 2023 – Oct 2025 | 655 trades | 0.0003 |
| TEST D Q vs vol | Jan 2023 – Oct 2025 | 209,689 | N/A |

---

## 6. Remaining Validity Concerns

1. **76 OOS trades is still a small sample.** The 2026 result (PF=0.469 at 3-pip) is conclusive in sign but not tight in magnitude. Accumulating more OOS data would narrow the confidence interval.

2. **The 2026 data has no separate bid column** — costs were modeled as a flat fraction, not tick-level bid/ask. This slightly underestimates slippage but does not change the sign of results.

3. **NY_Continuation strategy was selected in-sample** from 29 strategies. Its poor OOS performance (PF=0.469 even before Q filter benefits) suggests the strategy selection itself is overfit. A Q-based filter cannot improve a strategy with no underlying edge.

4. **T_sys (V12) has genuine predictive signal** (ρ=+0.27 for future realized vol). This is validated robustly. However the current trading system gates on Q (transport discriminant), not T_sys. A system built around T_sys regime detection rather than Q might have different properties — but this has not been tested and would require fresh OOS data to evaluate.

5. **Crypto cost model in Phase 3** was confirmed too low (~7× below actual Binance costs). Phase 3 cross-market results for BTC/ETH are misleading and should not be cited.

---

## 7. Reproducible Commands

```bash
# All four tests in one run (22.8 seconds):
cd calibration_engine/eg/finance_module/
python3 bounded_validation.py

# Output:
#   results/bounded_validation/bounded_validation_results.json
#   results/bounded_validation/test_a_trade_log_2026.csv
#   results/bounded_validation/test_c_regime_outcomes.csv
#   results/bounded_validation/test_d_q_vs_fwd_vol.csv
```

---

## 8. Final Verdict

### The system has **NO DEMONSTRATED TRADING EDGE**.

The evidence addresses each hypothesis directly:

**The in-sample result (PF=1.077 / 43 trades) is not real.** On genuinely unseen 2026 data with the identical frozen OS, the system loses money at every cost assumption: PF=0.469 (3-pip), PF=0.292 (5-pip), PF=0.175 (7-pip). The apparent in-sample performance was an artifact of (a) circular data use and (b) small-sample variance on 41 Strong_Coherent trades.

**Q does not improve trade selection in 2026.** The bootstrap test (p=0.21) shows no significant difference between Q-filtered entries and randomly selected entries from the same pool. Neither the OS nor unfiltered random entry achieves PF ≥ 1.0 in 2026 (0% of 10,000 bootstrap samples did).

**Q measures the wrong quantity for this strategy.** Q is negatively correlated with future volatility (TEST D), meaning it fires at transition points after which conditions tend to calm. T_sys — not Q — is the quantity with demonstrated positive predictive power for future volatility, but T_sys is not what gates trading decisions in the current OS.

**The underlying strategy (NY_Continuation) has no edge.** Phase 1 PF=0.567 (in-sample, all 413 trades). In 2026, even without the Q filter, NY_Continuation achieves mean PF=0.237 across 10,000 bootstrap samples. No filter can generate positive expectancy from a strategy with none.

### This is NOT proof that Q-based regime detection is useless in principle.

T_sys has real, replicated, cross-session predictive power for future realized volatility (r=0.788 contemporaneous, ρ=+0.27 predictive, stable across 2023–2025). The V12/SXCOmega system is detecting genuine market stress regimes. The failure is in how that information is connected to trading decisions: the current system uses Q (rate of change of the stress composite) rather than T_sys (absolute stress level), and it builds on a losing underlying strategy.

### What would be needed to test whether the genuine T_sys signal can generate edge:

1. Build a strategy that explicitly trades differently during FIREWALL vs NOMINAL phases (T_sys, not Q)
2. Verify no in-sample optimization by using 2026 data exclusively for evaluation
3. Use instrument-appropriate costs (5+ pip RT for EUR/USD retail)
4. Target at minimum 200 trades per condition
5. Only claim edge if OOS PF > 1.0 with bootstrap CI excluding 1.0

---

*All source data preserved. All original results preserved. No parameters were optimized.*  
*Reproducible: `python3 bounded_validation.py` from `finance_module/` directory.*  
*Git commit: `6738ed05`*
