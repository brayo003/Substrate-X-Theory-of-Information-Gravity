# Go / No-Go Decision
## DCIF Finance Module

**Date:** 2026-10-17  
**Git commit:** `6738ed05`

---

## Decision

**NO-GO FOR THIS FINANCE MODULE IN ITS CURRENT FORM**

---

## The Decisive Evidence

Three findings close the door on the current design:

**1. The primary OOS backtest was invalidated by a strategy mismatch.**  
The 76-trade 2026 out-of-sample result — already showing PF=0.47, a clear loss — was produced using a custom signal (RSI+MACD+ADX, hours 14–21 UTC) that is not the strategy deployed by Phase 2. The actual deployed strategy (`NY_Continuation`, EMA crossover, hour 13 UTC) generates 7 OOS trades, all losing. 7 trades support no inference. The module has no valid OOS trading result to defend.  
Evidence: `results/bounded_validation_corrected/CORRECTED_BOUNDED_VERDICT.md`

**2. All 28 strategies lose in all 5 Q-regimes in-sample.**  
The Phase 1 matrix across 2023–2025 EUR/USD shows no profitable strategy-regime combination under realistic costs. The Transport OS selects the best available strategy per regime, but "best" means least-bad among uniformly losing options. No filter — transport-based or otherwise — can create positive expectancy from inputs that have none.  
Evidence: `results/phase1/phase1_strategy_matrix.csv` — best cell PF=0.61 (ATR_Expansion, Strong_Coherent)

**3. Q adds no information beyond a simple volatility threshold.**  
Q = 100×(log-return of composite)² − 1. Q>0 is algebraically identical to |composite log-return| > 10%. The transport PDE's deeper output (s_transport) is never used. The module's own audit confirms identical empirical results for Q>0 and the raw gradient threshold.  
Evidence: `FINAL_AUDIT_VERDICT.md` §1.3 — "Q>0 and |grad_ln_s|>p75 produce identical F1 scores to four decimal places"

---

## What This Decision Does and Does Not Mean

**This does not mean the Substrate-X theory is wrong.** The theory's failure to produce a working finance module may reflect the wrong domain, wrong instrument, wrong timeframe, or a fundamental mismatch between the theory's spatial-field assumptions and the 1D temporal structure of a financial time series. Those are distinct questions.

**This does not mean the transport mathematics are invalid.** The PDE is implemented correctly. Q is computed correctly. T_sys is computed correctly. The infrastructure is sound. The problem is that neither produces a demonstrated advantage over simpler alternatives on this instrument at this timeframe.

**This does mean the current design cannot be incrementally improved.** The core problem is not a parameter, not a cost assumption, not a missing indicator. It is that the DCIF framework's output (T_sys, Q, regime) plays no causal role in the strategies' profitability, and the strategies themselves have no edge. Fixing one without fixing the other does nothing.

---

## What Would Constitute a Valid Restart (If One Is Attempted)

Only three paths could justify restarting this finance module. Each has a concrete acceptance criterion and a stopping condition.

---

### Task 1: Demonstrate that Q outperforms a volatility baseline as a regime classifier

**What to do:**  
Construct a head-to-head comparison:  
- Classifier A: 5-bar realized volatility threshold (standard, no DCIF)  
- Classifier B: Q-based 5-regime classification (current system)  

Apply both classifiers to **unseen data** (a completely held-out instrument or period not touched during any prior experiment). Compare the two classifiers on their ability to predict one of: (a) regime transitions (defined by a pre-specified volatility expansion criterion), (b) forward realized volatility level, or (c) strategy win-rate differences across classified periods.

**Acceptance criterion:**  
Q classifier produces a statistically significant improvement (p < 0.05 after Bonferroni correction for the two classifiers tested) with a measurable effect size (e.g., AUC improvement > 0.03, or precision-recall F1 improvement > 0.05) on the held-out data.

**Stopping condition:**  
If Q does not outperform the rv5 threshold on the held-out set, the Q regime classifier has no demonstrated advantage and further development of the regime-gating architecture is not justified.

---

### Task 2: Find a strategy with positive IS expectancy in at least one Q-regime

**What to do:**  
Identify at least one strategy (from the 28 existing, or a new one) that achieves positive gross expectancy (before costs) in at least one Q-regime on the 2023–2025 EUR/USD data, with N ≥ 100 trades in that cell. Then verify: (a) the strategy survives a 5-pip RT cost assumption, (b) the result holds on at least one other instrument or year.

**Acceptance criterion:**  
One strategy-regime cell with PF > 1.20, N ≥ 100 trades, cost-adjusted positive expectancy, confirmed on one additional instrument with N ≥ 50 trades.

**Stopping condition:**  
If no such cell exists after a systematic search across instruments (EUR/USD, GBP/USD, NAS100, Gold at appropriate timeframes), the regime-gating approach cannot be validated and the architecture should be abandoned.

---

### Task 3: Connect T_sys to a trading decision and test it out-of-sample

**What to do:**  
Design a specific, pre-registered experiment where T_sys (not Q, not regime) directly determines a trading decision — e.g., position size scales with T_sys level, or entries are permitted only when T_sys crosses a defined threshold. Run this experiment on 2026 data with N ≥ 100 trades. Compare performance to the same strategy without T_sys involvement.

**Acceptance criterion:**  
T_sys-gated system achieves PF > 1.10 OOS with N ≥ 100 trades, and Mann-Whitney test vs. baseline rejects H0 (p < 0.05). T_sys must be the *only* change between compared systems.

**Stopping condition:**  
If T_sys gating does not improve the baseline strategy in the OOS test, T_sys should be removed from the trading pipeline and its role (if any) limited to research/monitoring.

---

## What Not to Do

- Do not expand the strategy library further before completing Task 1 or Task 2.
- Do not add more instruments, phases, or reporting layers before one of the three tasks above produces a positive result.
- Do not treat s_transport as a future research direction without first establishing whether Q or T_sys has any trading value — s_transport is a more complex output of the same PDE that already failed.
- Do not restart the full DCII calibration (T = α|∇ρ| + βE - γF with real market events) until Tasks 1–3 are resolved. That calibration requires a working signal chain to evaluate against.

---

## Summary

The finance module is **no-go in its current form** because it has no valid OOS result, all strategies lose in all regimes, and the transport framework's outputs either reduce to volatility thresholds or are not used in decisions. Continuing in the current configuration will produce more experiments with the same structural problem.

If any of the three tasks above produces a positive result, the module can resume with a targeted, hypothesis-driven design. If all three fail, the conclusion is that the DCIF/Substrate framework, as implemented for 5-minute EUR/USD trading, does not contribute measurable value. That is a legitimate scientific finding, not a failure of the theory itself.
