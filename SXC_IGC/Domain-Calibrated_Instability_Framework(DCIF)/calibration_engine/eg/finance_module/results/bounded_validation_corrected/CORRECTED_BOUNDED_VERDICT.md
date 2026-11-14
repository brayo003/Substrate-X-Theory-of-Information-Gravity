# CORRECTED BOUNDED VERDICT
## Transport OS / Q Regime System — Finance Module

**Corrected report date:** 2026-10-11  
**Git commit:** `6738ed05`  
**Scripts:** `corrected_audit.py` (this audit), `bounded_validation.py` (prior run preserved)  
**Output directory:** `results/bounded_validation_corrected/`  
**Prior output preserved at:** `results/bounded_validation/` (unchanged)

---

## Executive Verdict

**NO DEMONSTRATED EDGE — confirmed with one material correction to the prior test.**

The prior bounded validation (`bounded_validation.py`) contained a **strategy mismatch**: it tested a custom RSI+MACD+ADX signal (hours 14–21 UTC) instead of the actual `NY_Continuation` strategy deployed by Phase 2 (EMA crossover, hour 13 UTC only). When the correct strategy is used, only 7 trades are generated on 2026 data, all losing. The original 76-trade result therefore measured an untested strategy, not the one under investigation.

Under the corrected test, **the OOS result remains negative at all cost assumptions**. No evidence of trading edge was found.

---

## What Was Tested and What Was Frozen

**Frozen throughout (no changes permitted):**
- Q thresholds: q05=−0.9980, q95=1.7323 (derived from 2023–2025, checkpoint manifest)
- Transport parameters: c=1.0, τ=5.0 (transport_layer.py defaults)
- Strategy: `NY_Continuation` from `strategy_library.py` (lines 469–483)
- ATR multipliers: stop=1.5×, target=2.5×
- Hold period: 24 bars (2 hours at 5-min bars)
- Regime allocation: trade only in Strong_Coherent, risk fraction=25%

**Not changed:** strategy parameters, entry/exit rules, regime definitions, Q thresholds, or market data.

---

## Original Frozen 2026 Results (Preserved)

From `bounded_validation.py`, using the WRONG signal (RSI+MACD+ADX, 14–21h):

| Cost | Trades | PF | Win Rate | Expectancy | Sharpe |
|------|--------|----|----------|------------|--------|
| 3-pip RT | 76 | 0.469 | 36.8% | −0.000318 | −3.07 |
| 5-pip RT | 76 | 0.292 | 31.6% | −0.000518 | −5.00 |
| 7-pip RT | 76 | 0.175 | 30.3% | −0.000718 | −6.92 |

These results are preserved in `results/bounded_validation/` and are not overwritten. They are reported here for transparency but do not represent the Phase 2 strategy.

---

## Corrected 2026 Results (Correct Strategy)

Using `strategy_library.py` `NY_Continuation` (EMA crossover, hour==13 UTC):

| Cost | Trades | PF | Win Rate | Expectancy | Sharpe |
|------|--------|----|----------|------------|--------|
| 3-pip RT | 7 | 0.538 | 42.9% | −0.000268 | −0.79 |
| 5-pip RT | 7 | 0.326 | 42.9% | −0.000468 | −1.38 |
| 7-pip RT | 7 | 0.173 | 42.9% | −0.000668 | −1.98 |

**All negative. 7 trades is insufficient for statistical inference.** 95% CI on expectancy at 3-pip spans [−0.00116, +0.00063] — contains zero. PF bootstrap CI: [0.07, 2.69] — spans 1.0 entirely.

The correct strategy generates only 61 signals on 2026 data (all at hour 13), of which 7 fall in Strong_Coherent regime (~11%).

---

## Execution Timing Findings

**Same-close entry (present, low severity):** Signal at bar `i` uses `close[i]` via `ewm()`. Entry is also at `close[i]`. A realistic trader can only know `close[i]` after the bar closes; the earliest defensible execution is `open[i+1]`. For the original (wrong) signal, the next-bar-open diagnostic gives PF=0.405 at 3-pip vs 0.469 same-close — both negative, direction unchanged. For the corrected strategy with 7 trades, same-close and next-open produce identical PF (entry price difference is negligible at 5-min granularity for EMA-crossover signals).

**No same-bar stop/target issue:** Both engines check stop/target starting at bar `i+1` (p1: inner loop starts at `i+1`; p2: stop check precedes entry in loop order, so new entries cannot trigger stops in the same iteration).

**Ambiguous same-candle stop+target:** Both engines resolve in favor of stop first (conservative). This slightly underestimates winning scenarios.

**Bid-only data:** The 2026 CSV contains only bid prices. Costs modeled as flat fraction (0.0003–0.0007). True fill prices cannot be reconstructed at tick level.

---

## Cost Model Findings

- `TOTAL_COST_RT = 0.00030` = 2×(commission_per_side + slippage_per_side) = 2×(0.00010 + 0.00005)
- Represents: 2-pip spread + 1-pip commission/slippage round-trip = **3 pips total**
- Applied exactly **once** per completed trade as `net_ret = gross_ret - 0.00030`
- Not double-counted. Winning and losing trades both subject to same deduction.
- Stop fills assumed at exact stop price (no additional slippage modeled beyond TOTAL_COST_RT).

---

## Corrected Uncertainty and Resampling Analysis

**Corrected-strategy (7 trades):**
- Expectancy 95% CI [−0.00116, +0.00063] at 3-pip — contains zero
- PF bootstrap 95% CI [0.07, 2.69] — contains 1.0
- t-test p=0.49 — cannot reject H0 of zero expectancy
- Effective n ≈ 30 (AR(1) correction applied)
- **Conclusion: 7 trades is wholly insufficient for any inference.**

**Original-result (76 trades, wrong strategy):**
- Large enough for a signal but used the wrong strategy — those results cannot be attributed to Phase 2.

**Bootstrap resampling (corrected strategy):**
- Pool: 61 NY_Continuation trades on 2026 data, Q-unfiltered
- IID bootstrap p=0.37; block bootstrap (weekly) p=0.38
- Not significant. Q filter shows no measurable selection improvement over random.

**Phase 1 in-sample MWU (Strong_Coherent):**
- Verified: U=14,168, p=0.089, r_biserial=−0.126
- p > 0.05: not significant. r_biserial is **negative** — SC trades scored lower in the MWU ranking than other-regime trades despite higher PF. The apparent PF=9.8 is driven by a few large wins, not consistently superior outcomes.

**Power analysis:** To detect expectancy of 0.0001 with trade-level std=0.001 at 80% power: requires ~1,570 trades. The current corrected dataset has 7.

---

## Q and T_sys Evidence

### Q

**Formula verified:** Q = 100×(ln s[t] − ln s[t−1])² − 1. Exact match to cached values confirmed numerically.

**No look-ahead:** `grad_ln_s` uses backward difference. Forward vol window starts at t+1 — no overlap with Q computation at t.

**Predictive correlation with future volatility:** ρ ≈ −0.005 to −0.008 (negative, statistically significant, practically negligible). High Q marks stress transitions; after rapid changes the field tends to revert, reducing subsequent volatility.

**Q does not predict higher future volatility.** It identifies transition points, not sustained high-vol regimes.

### T_sys

**Reproduced:** k=12 ρ=+0.269 (matches v12_validate's ρ≈0.27). T_sys has genuine predictive power for future realized vol.

**Simple baseline comparison (new):** Past 5-bar realized volatility achieves ρ=+0.48 to +0.62 — approximately **2× stronger** than T_sys at all horizons tested. T_sys adds predictive signal above zero, but simple vol persistence is a stronger predictor.

**T_sys predictive power does not imply Q-gated trading has positive expectancy.** The trading system gates on Q (not T_sys), and Q is negatively correlated with future vol.

---

## Data Split and Reproducibility Findings

| Period | Role | Independent? |
|--------|------|-------------|
| 2023–2025 EUR/USD | Q calibration + Phase 1 strategy discovery + Phase 2 OS calibration + Phase 2 evaluation | NO — all in-sample |
| **2026 EUR/USD** | **OOS test (this audit)** | **YES — zero cache parquets before test** |

Confirmed: 0 cache parquets for 2026 before `bounded_validation.py` ran. 224,700 raw 1-minute rows (Jan 1 – Jul 21, 2026). Cache covered 210,505 bars from 2023-01-01 to 2025-10-24.

The Phase 2 "outperformance" result (PF=1.077, 43 trades, 2023–2025) is entirely in-sample: OS calibration and evaluation use the same dataset.

---

## Separation of Verified Findings, Plausible Hypotheses, and Unsupported Claims

### Verified findings

1. The `bounded_validation.py` 76-trade test used a signal not present in `strategy_library.py` — it did not test the Phase 2 strategy.
2. The corrected strategy (EMA crossover, hour 13) generates 7 OOS trades in 2026, all losing at every cost assumption.
3. Q formula matches its definition (verified numerically).
4. Q is negatively correlated with future realized vol (ρ ≈ −0.008, p < 0.001, k=12).
5. T_sys is positively correlated with future vol (ρ=+0.27, reproduced from cache).
6. Simple 5-bar vol persistence (ρ=+0.62) outperforms T_sys (ρ=+0.27) at all horizons.
7. 2026 data was genuinely untouched before the OOS test.
8. Phase 2 calibration and evaluation data are the same 2023–2025 set.
9. Cost model: 3-pip RT applied correctly once per trade, no double-counting.

### Plausible hypotheses (evidence suggestive, not conclusive)

1. T_sys contains incremental predictive information above simple vol persistence; the magnitude and sign are real but smaller than persistence alone.
2. The Strong_Coherent regime captures a genuine market state (transitions in the composite signal); it simply does not correspond to a tradeable entry opportunity under the tested strategy.
3. A T_sys-gated strategy (FIREWALL vs NOMINAL phases) might behave differently from the Q-gated Transport OS — this has not been tested.

### Claims not supported by available evidence

1. That the Transport OS has a positive trading expectancy on EUR/USD or any other instrument.
2. That the 2023–2025 in-sample PF=1.077 (43 trades) represents a genuine edge — it is circular and statistically insignificant.
3. That Q improvement over random is zero — non-significance at n=7 does not prove this; the test is underpowered.
4. That T_sys's predictive power is unique to the SXC-IGC framework — vol persistence provides a stronger baseline without any theoretical apparatus.

---

## Final Decision

**NO DEMONSTRATED EDGE — current configuration.**

**Justification:** The frozen Transport OS with the correct strategy produces 7 trades over 6.75 months of genuine OOS data, all losing at every cost assumption tested. The prior 76-trade result used a different, untested signal. No statistical test on any available sample can distinguish the current system's performance from chance.

**This is a corrected negative result, not proof that no edge is possible.** Specific paths to an honest test remain open: accumulate more OOS data with the frozen system; test T_sys-gated approaches on a separate holdout; investigate why the EMA crossover at hour 13 fires only 61 times in 6.75 months of 2026 data.

---

*All original artifacts preserved. No strategy parameters modified.*  
*Reproducible: `python3 corrected_audit.py` from `finance_module/` directory.*  
*Git commit: `6738ed05`*
