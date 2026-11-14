# Phase 2 — Transport Operating System Validation Report
## EUR/USD 2023–2025 | 5-Minute Bars | SXC-IGC Q Transport Layer

**Generated:** 2026-07-22T05:50:15Z
**Elapsed:** 408.6s (6.8 min)

---

## Transport OS Configuration

**Layer 1 — Strategy Allocation (inferred from Phase 1 matrix):**

| Regime | Strategy | Family | Confidence |
| ------ | -------- | ------ | ---------- |
| Deep_Incoherent | NO_TRADE | — | Weak |
| Mod_Incoherent | NO_TRADE | — | Weak |
| Transition | NO_TRADE | — | Weak |
| Weak_Coherent | NO_TRADE | — | Weak |
| Strong_Coherent | NY_Continuation | — | Weak |

**Layer 2 — Risk Allocation (inferred from Phase 1 median PF per regime):**

| Regime | Risk Fraction | Position Size |
| ------ | ------------- | ------------- |
| Deep_Incoherent | 0.000 | 0.00% of base |
| Mod_Incoherent | 0.000 | 0.00% of base |
| Transition | 0.000 | 0.00% of base |
| Weak_Coherent | 0.000 | 0.00% of base |
| Strong_Coherent | 0.250 | 25.00% of base |

**Layer 3 — Stop/Target Allocation (inferred from stop_freq + regime persistence):**

| Regime | Stop×ATR | Target×ATR | Trailing |
| ------ | -------- | ---------- | -------- |
| Deep_Incoherent | 1.50 | 2.50 | No |
| Mod_Incoherent | 1.50 | 2.50 | No |
| Transition | 1.50 | 2.50 | No |
| Weak_Coherent | 1.50 | 2.50 | No |
| Strong_Coherent | 1.88 | 2.50 | No |

---

## Performance Summary

| System | PF | Sharpe | Sortino | MaxDD | WinRate | Trades | Exposure |
| ------ | -- | ------ | ------- | ----- | ------- | ------ | -------- |
| Transport_OS ◄ | 1.077 | 0.132 | 0.334 | 0.0022 | 0.535 | 43 | 0.002 |
| Fixed_EMA | 0.393 | -21.311 | -44.646 | 2.2298 | 0.334 | 8016 | 0.343 |
| Fixed_MACD | 0.384 | -26.419 | -54.145 | 3.4318 | 0.331 | 11777 | 0.506 |
| Fixed_RSI | 0.391 | -28.867 | -59.817 | 4.1067 | 0.331 | 14526 | 0.621 |
| Fixed_Donchian | 0.386 | -25.445 | -52.776 | 3.2682 | 0.327 | 11026 | 0.458 |
| Fixed_Turtle | 0.386 | -25.445 | -52.776 | 3.2682 | 0.327 | 11026 | 0.458 |
| Fixed_Best | 0.549 | -3.160 | -8.435 | 0.1106 | 0.369 | 366 | 0.013 |

---

## Allocator Behaviour

- No-trade fraction: **95.02%** of all bars
- Strategy switches: 19,186 total
- Switch rate: 1.0937 per hour
- Average regime duration: 12.4 minutes
- Risk utilisation: 4.98%
- Active strategies: NY_Continuation

**Time allocation per strategy:**

  - NO_TRADE: 95.02%
  - NY_Continuation: 4.98%

---

## Statistical Tests (OS vs Baselines)

| Baseline | Mean Diff | Perm p | MW p | FDR p | Reject | Cohen d |
| -------- | --------- | ------ | ---- | ----- | ------ | ------- |
| Fixed_EMA | 0.000290 | 0.002 | 0.000 | 0.000 | YES | 0.526 |
| Fixed_MACD | 0.000303 | 0.005 | 0.000 | 0.000 | YES | 0.539 |
| Fixed_RSI | 0.000294 | 0.001 | 0.000 | 0.000 | YES | 0.530 |
| Fixed_Donchian | 0.000308 | 0.006 | 0.000 | 0.000 | YES | 0.539 |
| Fixed_Turtle | 0.000308 | 0.006 | 0.000 | 0.000 | YES | 0.539 |
| Fixed_Best | 0.000310 | 0.027 | 0.002 | 0.002 | YES | 0.387 |

FDR-significant results: 6/6

---

## Research Questions — Evidence and Conclusions

### Q1. Does transport allocation outperform fixed allocation?

**Conclusion:** Yes (OS PF=1.077 vs best baseline PF=0.549)
**Confidence:** High

**Evidence:**
- Transport OS profit factor: 1.077  vs  best fixed baseline (Fixed_Best): 0.549
- FDR-significant MW tests: 6/6

### Q2. Does transport reduce drawdown?

**Conclusion:** Yes  **Confidence:** Weak

**Evidence:**
- OS max drawdown: 0.0022
  - Transport_OS: 0.0022
  - Fixed_Best: 0.1106
  - Fixed_EMA: 2.2298
  - Fixed_Donchian: 3.2682
  - Fixed_Turtle: 3.2682
  - Fixed_MACD: 3.4318
  - Fixed_RSI: 4.1067

### Q3. Does transport improve risk-adjusted returns?

**Conclusion:** Moderate evidence  **Confidence:** Moderate

**Evidence:**
- OS Sharpe: 0.132  Sortino: 0.334
- OS Ulcer Index: 64.1994  Recovery Factor: 0.2265

### Q4. Does transport spend more time not trading?

**Conclusion:** Yes  **Confidence:** High

**Evidence:**
- No-trade fraction: 95.02%
- No-trade regimes: Weak_Coherent, Deep_Incoherent, Transition, Mod_Incoherent
- OS trades: 43 vs average fixed: 9456

### Q5. How frequently does transport change strategies?

**Conclusion:** 1.0937 switches/hour  **Confidence:** High (directly measured)

**Evidence:**
- Total strategy switches: 19,186
- Switch rate: 1.0937 per hour
- Average regime duration: 12.4 minutes

### Q6. Does transport naturally converge toward a small set of strategy families?

**Conclusion:** Yes  **Confidence:** High

**Evidence:**
- Active strategies (non-NO_TRADE): 1
- Selected: NY_Continuation

### Q7. Can the transport layer be interpreted as a market operating system?

**Conclusion:** Yes, with Moderate confidence.  **Confidence:** Moderate

**Evidence:**
- Transport OS manages strategy selection, position sizing, stop policy — all OS functions
- Q is derived from the telegraph PDE (SXC-IGC transport layer), not from price
- 4/5 regimes trigger automatic no-trade (kernel-level blocking)
- Risk budget dynamically scaled per regime (range: 0.00–0.25)
- Analogous to OS scheduler: Q = scheduler state → selects process (strategy) + resource allocation (risk)

### Q8. Does transport allocate capital more intelligently than fixed rules?

**Conclusion:** Evidence supports yes  **Confidence:** Moderate

**Evidence:**
- Risk-weighted OS PF (1.077) vs best fixed baseline (0.549)
- OS reduces exposure to unfavourable regimes by 95.02%
- OS dynamically adjusts stops (range: 1.50–1.88×ATR)

---

## Confidence Summary

| # | Question | Confidence | Key Metric |
| - | -------- | ---------- | ---------- |
| Q1 | OS outperforms fixed | High | PF 1.077 vs 0.549 |
| Q2 | Reduces drawdown | Weak | OS DD=0.0022 |
| Q3 | Improves risk-adjusted | Moderate | Sharpe=0.132 |
| Q4 | More time not trading | High | No-trade=95.02% |
| Q5 | Switch frequency | High | Directly measured |
| Q6 | Converges to few families | High | 1 active strategies |
| Q7 | Functions as market OS | Moderate | Telegraph PDE architecture |
| Q8 | Smarter capital allocation | Moderate | PF + exposure control |
