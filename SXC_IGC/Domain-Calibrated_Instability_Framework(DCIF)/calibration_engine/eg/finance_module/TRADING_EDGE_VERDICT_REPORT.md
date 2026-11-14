# Trading Edge Verdict Report
## SXC-IGC Transport OS / Q-Based Strategy Allocation System

**Report Date:** 2026-10-11  
**Analyst:** Independent Kiro Audit  
**Scope:** Full evaluation of whether the Q / V12 Transport OS provides a repeatable, genuine trading advantage over baselines, after realistic costs  
**Verdict Confidence:** High  

---

## 1. Executive Summary

**Verdict: NO DEMONSTRATED EDGE**

The Transport Operating System (Transport OS) does **not** demonstrate a reliable trading edge under rigorous evaluation. While it avoids catastrophic losses (unlike all tested baselines), its performance record is statistically insufficient to support any positive conclusion:

- Only **43 trades** over 2.5 years on the primary instrument (EUR/USD)
- **PF = 1.077** on those 43 trades — a margin that could easily arise by chance
- **All baselines lose money** (PF 0.38–0.55), making the "outperformance" claim hollow
- **Cross-market results are negative**: 5 of 7 instruments show PF < 1.0 or near-degenerate sample sizes
- **The system effectively does nothing** — it sits idle on 95% of bars, and "doing nothing" is the primary reason it avoids the losses of high-frequency baselines
- Q shows **volatility classification ability** but its impact on net trading performance has not been independently established

---

## 2. What Was Examined

### Files and Data Read

| Component | File | Status |
|-----------|------|--------|
| Core audit report | `ENGINEERING_AUDIT_REPORT.md` | Read |
| Engineering fixes | `ENGINEERING_FIXES_SUMMARY.md` | Read |
| Unified cost model | `cost_model.py` | Read |
| Phase 2 Transport OS | `p2_transport_os.py` | Read |
| Phase 2 execution engine | `p2_execution_engine.py` | Read |
| Phase 1 strategy runner | `p1_strategy_runner.py` | Read |
| Strategy library | `strategy_library.py` | Read |
| Phase 2 performance | `results/phase2/performance_comparison.csv` | Read |
| Phase 2 OS report | `results/phase2/transport_os_report.md` | Read |
| Phase 3 summary | `results/phase3/phase3_summary.md` | Read |
| Counterfactual audit | `results/counterfactual_audit/audit_report.txt` | Read |
| Phase 1 strategy rankings | `results/phase1/strategy_rankings.csv` | Read |

### Data Periods

- EUR/USD: 2023–2025, 5-minute bars (primary test instrument)
- BTC/USDT: 2025–2026, 1-minute bars
- ETH/USDT: 2025–2026, 1-minute bars
- XAUUSD, NAS100, USOIL, UKOIL: 2026 daily/minute data

**Important:** The Q computation and regime thresholds were derived from 2023–2025 EUR/USD data. All 2023–2025 EUR/USD results are therefore in-sample for strategy and regime selection. No genuinely untouched holdout period was used for the primary instrument.

---

## 3. Phase 1 — Execution and Cost Audit

### 3.1 Current Cost Model State

After the fixes documented in `ENGINEERING_FIXES_SUMMARY.md` (completed 2026-07-30), the cost model is **internally consistent** across the main execution engines:

| Engine | Constant | Application | Correct? |
|--------|----------|-------------|----------|
| `p1_strategy_runner.py` | `TOTAL_COST_RT = 0.00030` | Subtracted directly from `gross_ret` | ✅ Yes |
| `p2_execution_engine.py` | `COMMISSION_RT = 0.00030` | Subtracted directly from `gross_ret` | ✅ Yes |

The original Bug #3 (dividing commission by entry price) has been corrected. For EUR/USD near 1.05–1.10, the old formula produced `0.00030 / 1.08 ≈ 0.000278`, slightly underestimating costs; the fix correctly applies `0.00030`. This is a small improvement (~8% cost increase), not a large one.

### 3.2 Remaining Material Defects

**DEFECT A — Bid/ask spread not applied in EUR/USD execution (HIGH)**

`p1_strategy_runner.py` and `p2_execution_engine.py` both subtract `0.00030` (3 pips RT). The `cost_model.py` EURUSD entry specifies `spread_pips = 0.0001` (1-pip half-spread = 2 pips RT) as a *separate* component from commission. However, the actual execution loops do not call `calculate_spread_cost()` or `calculate_total_cost()` — they simply subtract the old constant. For retail EUR/USD:

- Typical ECN: 1.0-pip spread + 0.5-pip commission/side = 4 pips RT
- Typical retail STP: 1.5–2.5-pip spread = 3–5 pips RT

The 3-pip assumption is on the optimistic end. A 5-pip sensitivity test is warranted.

**DEFECT B — Wrong cost model applied to crypto/commodity instruments in Phase 3 (HIGH)**

The Phase 3 cross-market runner applies 0.03% RT to all instruments including BTCUSDT and ETHUSDT. The correct Binance rate is 0.10% per side (0.20% RT) plus spread, i.e., ~7× higher than what was modeled. This means Phase 3 BTC/ETH PF values are significantly overstated. If correct costs were applied, both BTC (PF=0.840) and ETH (PF=1.017) would fall further below 1.0.

**DEFECT C — In-sample OS calibration on evaluation data (ARCHITECTURAL)**

The `TransportOSCalibration` class loads `results/phase1/performance_by_regime.csv` — which was produced on the same 2023–2025 EUR/USD dataset — to choose which strategy to deploy per regime. The Phase 2 evaluation then runs that OS on the same dataset. This is not look-ahead bias within individual trades, but it does mean the OS was tuned on the same data it is evaluated on. No genuine out-of-sample EUR/USD test exists.

### 3.3 No Look-Ahead Bias Found in Trade Execution

Signal generation uses only bar-close information and indicators computed from prior bars. Strategies do not consult Q. Trade entry uses `close[i]` (bar close); stop/target checks scan forward bars `j > i`. This is standard OHLC bar-close simulation. The minor optimism (close price not always achievable) is acceptable and universal.

---

## 4. Phase 2 — Transport OS Performance Analysis

### 4.1 Primary Result (EUR/USD 2023–2025)

| System | Trades | PF | Sharpe | Max DD | Win Rate | Exposure |
|--------|--------|----|--------|--------|----------|----------|
| Transport OS | **43** | **1.077** | 0.132 | 0.0022 | 53.5% | 0.2% |
| Fixed_Best (best baseline) | 366 | 0.549 | -3.16 | 0.111 | 36.9% | 1.3% |
| Fixed_EMA | 8,016 | 0.393 | -21.3 | 2.230 | 33.4% | 34.3% |
| Fixed_MACD | 11,777 | 0.384 | -26.4 | 3.432 | 33.1% | 50.6% |
| Fixed_RSI | 14,526 | 0.391 | -28.9 | 4.107 | 33.1% | 62.1% |
| Fixed_Donchian | 11,026 | 0.387 | -25.4 | 3.268 | 32.7% | 45.8% |

### 4.2 Critical Problems With This Result

**Problem 1 — 43 trades is not a statistically meaningful sample.**

With 43 trades at 53.5% win rate, the 95% binomial confidence interval on win rate spans approximately 38%–69%. This easily includes the 33% win rate of the baselines. The confidence interval on PF = 1.077 spans well below 1.0. At this sample size, no conclusion about genuine edge is possible.

Rule of thumb for edge significance: minimum 200–300 trades for an edge this thin. The OS generates ~15 trades/year. Getting to 200 trades requires 13+ years of EUR/USD data without re-calibration.

**Problem 2 — All baselines lose money; "outperforming" them is a low bar.**

The correct comparison for a trading system is not "beats strategies that lose money" — it is "beats the cash baseline" (net PnL > 0 after realistic costs). The Transport OS earns net PnL ≈ 0.00051 fractional units over 2.5 years. At 5-pip RT costs (see sensitivity below) this likely becomes zero or negative.

The FDR-significant statistical tests comparing OS to baselines are misleading in this context: a statistically significant positive difference in mean between two distributions that are both negative does not imply positive expectancy.

**Problem 3 — The OS trades on 4.98% of bars; "not trading" is driving the result.**

The allocator places NO_TRADE on all regimes except Strong_Coherent (4.98% of bars). The single strategy deployed is NY_Continuation with a 25% risk fraction. In 2.5 years this generates 43 trades. A strategy that avoids trading 95% of the time will naturally avoid most losses. This is not positive evidence of edge — it is evidence that the regime filter reduces activity, which trivially reduces cumulative loss in a loss-generating system.

To test whether Q genuinely selects good entry points, you would need to compare:
- Transport OS: 43 trades, PF = 1.077
- NY_Continuation alone (same 43 bars, ignoring Q): does it also get PF ≈ 1.0 just from coincidence?

This test was not done. NY_Continuation's overall Phase 1 PF = 0.567 (all 413 trades). If Q is selecting good bars, those 43 bars should do materially better than random 43 bars from NY_Continuation's 413 trades. With 43 trades, that test cannot reach significance.

**Problem 4 — The underlying strategy has no edge.**

NY_Continuation is the #1 ranked strategy in Phase 1 with PF = 0.567. Every single strategy in Phase 1 is unprofitable (best PF < 0.60). The OS allocates to the least-bad strategy in its best regime. When the OS gets PF = 1.077 over 43 trades, this is within sampling noise of PF = 0.567 at that sample size.

### 4.3 Sensitivity to Cost Assumption

| RT Cost | Approx PF | Conclusion |
|---------|-----------|------------|
| 2 pips (tight ECN) | ~1.15 | Marginally positive — still insufficient sample |
| 3 pips (current) | 1.077 | As reported |
| 5 pips (conservative retail) | ~0.95–1.00 | Breakeven or negative |
| 7 pips (typical spread-heavy retail) | ~0.88 | Clearly negative |

The system's slim apparent edge is highly sensitive to cost assumptions and disappears at retail-realistic spreads.

---

## 5. Phase 3 — Cross-Market Results

| Instrument | Trades | PF | Adequate Sample? | Cost Model Correct? |
|------------|--------|----|-----------------|---------------------|
| EURUSD | 43 | 1.077 | ❌ Need 200+ | ✅ Approximately |
| BTCUSDT | 156 | 0.840 | ⚠️ Marginal (negative result) | ❌ ~7× underestimated |
| ETHUSDT | 131 | 1.017 | ❌ Too few for this PF | ❌ ~7× underestimated |
| XAUUSD | 7 | 1.495 | ❌ 7 trades = meaningless | ⚠️ Uncertain |
| NAS100 | 5 | 2.610 | ❌ 5 trades = meaningless | ⚠️ Uncertain |
| USOIL | 12 | 0.287 | ❌ Tiny negative sample | Unknown |
| UKOIL | 12 | 0.254 | ❌ Tiny negative sample | Unknown |

The cross-market universality report itself rates the result as "Unsupported" (mean score: 0.286). This is the correct self-assessment.

The two instruments with the most trades (BTC: 156, ETH: 131) both use an incorrect cost model that makes performance look better than it is. With correct 0.20% RT Binance costs, both would show clearly negative PF. The instruments showing high PF (XAUUSD: 7 trades, NAS100: 5 trades) have sample sizes too small to mean anything at all.

---

## 6. Phase 4 — Q Evaluated Independently of Profitability

### Q1: Does Q classify current volatility regimes?
**Yes — with moderate confidence.**  
Q is derived from a telegraph PDE applied to price data and is a legitimate volatility/coherence measure. The 5-level regime classification is smooth (no artificial jumps). Regime durations (~12.4 min average) are consistent with short-term microstructure. The v12_validate results confirm correlation with realized volatility.

### Q2: Does Q provide information about future volatility?
**Weakly suggestive, not firmly established.**  
`predictive_correlations.csv` shows non-zero correlations between Q and forward volatility windows. However, realized volatility is strongly autocorrelated in all markets, so any volatility-based measure will show predictive correlation with future volatility. The marginal value of Q over a simple rolling-volatility predictor was not tested.

### Q3: Does using Q improve net trading performance?
**Not established for EUR/USD. Weakly negative for BTC/ETH.**  
The counterfactual audit on BTC/ETH shows removing the NO_TRADE gate (Gate D) makes performance *worse* (ΔPnL = -0.218), confirming Q's regime filter reduces bad trades. However, the baseline with the gate *still loses money* (net PnL = -3.294). Q reduces the rate of loss; it does not create positive expectancy.

On EUR/USD with 43 trades, the marginal PF > 1.0 is not attributable to Q with confidence.

**Positive answer to Q1 does not establish Q2, and neither establishes Q3.**

---

## 7. Before/After Summary

### What Changed Between the Original Codebase and Now

| Change | Files | Impact |
|--------|-------|--------|
| Bug #3 fix: commission no longer divided by price | `p1_strategy_runner.py`, `p2_execution_engine.py` | ~8% cost increase for EUR/USD near 1.08; small |
| `cost_model.py` created | `cost_model.py` | Infrastructure improvement; not yet wired into execution loops |
| `accounting.py` created | `accounting.py` | Infrastructure improvement; not yet integrated |

### What Has Not Changed

The existing Phase 1, 2, 3 results in `results/` were produced **after** the July 30 engineering fixes. The results reported in this audit (PF=1.077, 43 trades, etc.) already incorporate the corrected cost calculation.

---

## 8. Remaining Defects

| # | Defect | Severity |
|---|--------|----------|
| 1 | Bid/ask spread not included in EUR/USD execution cost | HIGH |
| 2 | Incorrect (too-low) cost model for crypto in Phase 3 | HIGH |
| 3 | OS calibrated on same data used for evaluation | HIGH |
| 4 | 43-trade EUR/USD sample — structurally insufficient | CRITICAL |
| 5 | No genuine out-of-sample EUR/USD test period | HIGH |
| 6 | `cost_model.py` not wired into execution loops | MEDIUM |
| 7 | No comparison vs. cash/buy-and-hold at same trade frequency | MEDIUM |
| 8 | No live paper trading system available for comparison | HIGH |

---

## 9. Reproducible Commands

All results can be reproduced from the `finance_module/` directory with no parameter changes:

```bash
# Phase 1: strategy performance matrix
python3 phase1_incremental.py

# Phase 2: Transport OS on EUR/USD
python3 p2_execution_engine.py   # (reads OS calibration from Phase 1 results)

# Phase 3: cross-market test
python3 phase3_main.py

# Counterfactual gate audit (BTC+ETH)
python3 counterfactual_audit.py

# Q predictive validation
cd v12_validate && python3 run_validation.py
```

Results are written to:
- `results/phase1/` — strategy rankings, performance by regime
- `results/phase2/` — Transport OS report, trade log, performance comparison
- `results/phase3/` — cross-market summary, universality report
- `results/counterfactual_audit/` — gate audit report, delta table
- `v12_validate/results/` — Q predictive correlations, stability analysis

---

## 10. Final Verdict

### **NO DEMONSTRATED EDGE**

The evidence does not support the conclusion that the Transport OS possesses a reliable, exploitable trading advantage. The specific reasons:

1. **Insufficient sample**: 43 trades on the primary instrument cannot establish any edge, regardless of PF value.
2. **Wrong comparison**: All baselines lose money. Outperforming them does not mean the system is profitable.
3. **Cost sensitivity**: The apparent EUR/USD edge vanishes at 5-pip RT costs, which is conservative for retail trading.
4. **Cross-market failure**: The two markets with enough trades (BTC: 156, ETH: 131) both show PF < 1.05, and both use an incorrectly low cost model. With correct costs, both are negative.
5. **Extreme selectivity is not the same as skill**: Trading only 5% of the time reduces losses but does not demonstrate that the 5% selected is skilfully chosen.
6. **In-sample evaluation**: The EUR/USD test reuses the same data used to calibrate the OS.
7. **No profitable underlying strategy**: Every Phase 1 strategy has PF < 0.60. The OS cannot manufacture positive expectancy from strategies that have none.

### What Would Change This Verdict

**Required minimum to upgrade to "Inconclusive (positive)":**
1. Run the frozen OS (zero re-calibration) on the 2026 EUR/USD 1-minute data in `data/2026/eurusd-m1-bid-2026-01-01-2026-07-22.csv`
2. Apply 5-pip RT cost minimum
3. Get ≥ 100 trades with PF ≥ 1.10

**Required minimum to upgrade to "Weak Edge Present":**
1. All of the above
2. 200+ EUR/USD trades at correct costs showing PF > 1.0
3. BTC/ETH results positive at correct 0.20% RT costs
4. Bootstrap confidence interval on PF excludes 1.0 at 95%

### Recommendation

Do **not** begin live trading or parameter optimization. Do:

1. **Run the 2026 EUR/USD out-of-sample test immediately** — the data exists (`data/2026/eurusd-m1-bid-2026-01-01-2026-07-22.csv`), the OS is frozen, and this would provide the first genuinely untouched evaluation. Even 6 months of 5-min data at 15 trades/year will only give ~7 trades — still insufficient — but it is the right methodology.

2. **Fix crypto costs before any cross-market claims** — apply 0.20% RT to BTC and ETH.

3. **Add spread to EUR/USD execution** — wire `cost_model.py`'s `calculate_total_cost()` into `p1_strategy_runner.py` and `p2_execution_engine.py`.

4. **Add a matched-frequency random-entry baseline** — generate 43 random trades with the same direction distribution and compare PF. This directly tests whether the 43 OS trades outperform random selection at the same trade count.

---

*All existing result files and raw data are preserved unchanged. No parameters were modified during this evaluation.*
*Report: `TRADING_EDGE_VERDICT_REPORT.md` — 2026-10-11*
