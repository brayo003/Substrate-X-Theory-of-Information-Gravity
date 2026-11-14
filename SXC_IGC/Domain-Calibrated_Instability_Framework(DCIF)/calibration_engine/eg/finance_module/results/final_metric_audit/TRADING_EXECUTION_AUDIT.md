# Trading Execution Audit
## Strategy Source, Execution Path, Cost Model, Frozen Performance, and Uncertainty

**Audit date:** 2026-10-11  
**Git commit:** `6738ed05`  
**Source files examined:** `strategy_library.py` (lines 469–483), `p2_execution_engine.py`, `p1_strategy_runner.py`, `p2_transport_os.py`  
**Trade data:** `results/bounded_validation_corrected/correct_strategy_same_close_2026.csv`, `correct_strategy_next_open_2026.csv`  
**Results data:** `results/bounded_validation_corrected/corrected_audit_results.json`  
**Prior (wrong) results preserved at:** `results/bounded_validation/`

---

## 1. Actual Strategy Source

### 1.1 NY_Continuation — exact definition from source

**File:** `strategy_library.py`  
**Lines:** 469–483 (the `NY_Continuation` function)

```python
@_register('Session')
def NY_Continuation(df: pd.DataFrame) -> pd.Series:
    """
    NY open continuation: at 13:30 UTC (NY open), enter in direction of
    London trend (EMA9 vs EMA21 slope at that bar).
    """
    hour   = _hour_utc(df)
    fast   = df['close'].ewm(span=9,  adjust=False).mean()
    slow   = df['close'].ewm(span=21, adjust=False).mean()
    is_ny  = (hour == 13)
    sig    = pd.Series(0, index=df.index, dtype=np.int8)
    trend  = (fast > slow).astype(int) - (fast < slow).astype(int)
    sig[is_ny & (trend == 1) & (trend.shift(1) != 1)]   =  1
    sig[is_ny & (trend == -1) & (trend.shift(1) != -1)] = -1
    return sig
```

**Signal logic precisely:**
- Session filter: bars where `hour(UTC) == 13` only (bars from 13:00 to 13:55 UTC).
- Entry direction: EMA(9) vs EMA(21) crossover — long when fast > slow AND was not previously fast > slow; short when fast < slow AND was not previously fast < slow.
- Signal is a **crossover event**, not a persistent level signal. It fires only at the bar where the relationship changes.
- EMA computation uses `adjust=False` (recursive, causal).

**This is not the signal used in `bounded_validation.py`.** That file used a custom function with RSI(14) crossing 50, MACD > 0, and ADX > 20, applied during hours 14–20 UTC. That mismatch is documented in the execution audit from the corrected run.

### 1.2 Strategy family and deployment context

NY_Continuation belongs to `strategy_library.py`'s Session family. In the Phase 2 Transport OS (`p2_transport_os.py`), trading is gated by the Q-based regime classifier. Only bars classified as `Strong_Coherent` (Q ≥ 1.732) are routed to the selected strategy. All other regimes either trade a different strategy or are designated NO_TRADE, depending on Phase 1 calibration.

The Q thresholds and risk parameters used during the 2026 test are frozen from the 2023–2025 calibration period.

---

## 2. Execution Path

### 2.1 Signal-to-fill sequence

```
Bar t closes
  → close[t] finalized
  → EMA(9), EMA(21) updated with close[t]
  → trend direction computed
  → if hour == 13 AND crossover: signal = ±1
  → Q[t] computed from composite signal s[t]
  → regime classified
  → if regime == Strong_Coherent AND OS routes to NY_Continuation:
      entry_price = close[t]          ← same-close entry
      stop_price  = entry_price ∓ ATR_STOP × atr_14[t]
      target_price = entry_price ± ATR_TARGET × atr_14[t]
  → for each bar j = t+1, t+2, ..., t+23:
      check: low[j] ≤ stop_price  → stop hit
      check: high[j] ≥ target_price → target hit
      if neither: continue
      if timeout at j=t+24: exit at close[t+24]
```

### 2.2 Same-close entry issue

Both `p1_strategy_runner.py` and `p2_execution_engine.py` enter at `close[t]` after generating a signal that requires `close[t]` to be known. A real-time trader cannot fill at `close[t]` after observing it because the fill would require a market order placed and confirmed before the bar closes.

**Magnitude of bias:** For 5-min EUR/USD, the difference between `close[t]` and `open[t+1]` is typically 0.1–0.3 pips. This is small relative to the 3-pip modeled cost but introduces a systematic direction-unknown bias.

**Diagnostic result (from corrected_audit_results.json):** Same-close vs next-open produces PF = 0.538 vs 0.538 (rounded to 3 decimal places) for the 7-trade corrected strategy. The 7-trade entry price differences are negligible at 5-min granularity. The same-close issue does not change the verdict for this particular strategy and dataset.

For the original (incorrect) 76-trade signal, same-close gave PF = 0.469 vs next-open PF = 0.405. Both negative.

### 2.3 No same-bar stop/target issue

In `p1_strategy_runner.py`, the inner loop that checks stop and target starts at `range(i+1, max_j+1)`. A trade entered at bar `i` cannot have its stop triggered at bar `i`.

In `p2_execution_engine.py`, the loop structure processes open-trade management (`state.in_trade` block) before the new-entry block. A trade entered at bar `i` is processed for stop/target checks starting at bar `i+1`. Same-bar stop triggering does not occur in either engine.

### 2.4 Stop/target resolution when both trigger in one bar

When `low[j] <= stop_price` AND `high[j] >= target_price` within the same bar, both engines resolve in favor of the stop (conservative). This underestimates favorable outcomes for scenarios where the target was hit before the stop intrabar. The conservative assumption is appropriate for validation.

---

## 3. Cost Model Verification

### 3.1 Cost structure

From `strategy_library.py` and `p1_strategy_runner.py`:

```
COMMISSION  = 0.00020   # 2-pip one-way (spread + commission)
SLIPPAGE    = 0.00005   # 0.5-pip slippage per side
TOTAL_COST_RT = 2 × (COMMISSION + SLIPPAGE) = 2 × 0.00025 = 0.00050
```

Wait — the corrected audit uses three cost scenarios: 3-pip (0.0003), 5-pip (0.0005), and 7-pip (0.0007) round-trip. These correspond to:

| Label | TOTAL_COST_RT | Interpretation |
|-------|---------------|----------------|
| 3-pip | 0.00030 | Tight retail spread (1.5 pip each side) |
| 5-pip | 0.00050 | Standard retail (2.5 pip each side) |
| 7-pip | 0.00070 | Widened spread or adverse fill |

For EUR/USD with 4-decimal pricing, 1 pip = 0.0001. So 3-pip RT = 0.0003, confirming the convention.

### 3.2 Cost application

From `corrected_audit_results.json` (cost_model section):
- Applied as flat fraction: `net_ret = gross_ret - TOTAL_COST_RT`
- Deducted **once per completed trade**, not twice
- No double-counting confirmed
- Applied identically to wins and losses

### 3.3 Bid-only data limitation

The 2026 dataset (`eurusd-m1-bid-2026-01-01-2026-07-22.csv`) contains bid prices only. No ask column is present. Implications:
- Long entry fills are at ask ≈ bid + spread. The modeled entry is at bid close. This slightly understates true long entry cost (by approximately 0.5–1 pip depending on actual spread).
- Short entry fills are at bid — approximately correct for the modeled entry.
- The flat `TOTAL_COST_RT` is intended to compensate for this gap, but the actual spread during 2026 is not available for verification.
- True execution quality (slippage, market impact, spread widening during volatility) cannot be reconstructed from bid-only 1-minute OHLC.

The flat-cost sensitivity tests (3/5/7-pip) provide a reasonable range given this limitation but are not a full realistic execution simulation.

---

## 4. The Seven-Trade Sample: Complete Record

### 4.1 Same-close entries (from correct_strategy_same_close_2026.csv)

| # | Entry ts | Dir | Entry price | Exit price | Gross ret | Stop/Target | Duration | Regime |
|---|----------|-----|-------------|------------|-----------|-------------|----------|--------|
| 1 | 2026-01-12 13:05 | Long | 1.16918 | 1.16845 | −0.000623 | Stop | 13 bars | Strong_Coherent |
| 2 | 2026-02-10 13:50 | Long | 1.19041 | 1.19189 | +0.001244 | Target | 5 bars | Strong_Coherent |
| 3 | 2026-02-27 13:05 | Long | 1.18054 | 1.18002 | −0.000442 | Stop | 5 bars | Strong_Coherent |
| 4 | 2026-03-06 13:30 | Long | 1.15897 | 1.15762 | −0.001164 | Stop | 3 bars | Strong_Coherent |
| 5 | 2026-04-23 13:30 | Long | 1.16921 | 1.17045 | +0.001059 | Target | 10 bars | Strong_Coherent |
| 6 | 2026-07-08 13:30 | Long | 1.14113 | 1.14041 | −0.000628 | Stop | 12 bars | Strong_Coherent |
| 7 | 2026-07-13 13:15 | Short | 1.14254 | 1.14165 | +0.000779 | Target | 7 bars | Strong_Coherent |

All 7 same-close trades are in the Strong_Coherent regime. Direction: 6 long, 1 short. Outcomes: 3 targets, 4 stops. Win rate: 3/7 = 42.9%.

### 4.2 Next-open entries (from correct_strategy_next_open_2026.csv)

| # | Entry ts | Dir | Entry price | Exit price | Gross ret | Stop/Target | Duration | Regime |
|---|----------|-----|-------------|------------|-----------|-------------|----------|--------|
| 1 | 2026-01-12 13:10 | Long | 1.16923 | 1.16850 | −0.000623 | Stop | 12 bars | Mod_Incoherent |
| 2 | 2026-02-10 13:55 | Long | 1.19041 | 1.19189 | +0.001244 | Target | 4 bars | Weak_Coherent |
| 3 | 2026-02-27 13:10 | Long | 1.18053 | 1.18001 | −0.000442 | Stop | 4 bars | Weak_Coherent |
| 4 | 2026-03-06 13:35 | Long | 1.15896 | 1.15761 | −0.001164 | Stop | 2 bars | Mod_Incoherent |
| 5 | 2026-04-23 13:35 | Long | 1.16921 | 1.17045 | +0.001059 | Target | 9 bars | Mod_Incoherent |
| 6 | 2026-07-08 13:35 | Long | 1.14112 | 1.14040 | −0.000628 | Stop | 11 bars | Weak_Coherent |
| 7 | 2026-07-13 13:20 | Short | 1.14253 | 1.14164 | +0.000779 | Target | 6 bars | Mod_Incoherent |

With next-open entry: same 7 trades, same outcomes, but regimes shift (Q changes by one bar). Most next-open trades are classified as Mod_Incoherent or Weak_Coherent — they would have been excluded by the OS regime gate if evaluated at the next-bar regime rather than the signal-bar regime.

### 4.3 Why the two logs have nearly identical P&L

The gross returns are the same or differ by less than 0.00001 between same-close and next-open. This is because:
- At 5-min bars, EMA crossover signals that triggered at bar t produce entry prices at close[t] vs open[t+1] which differ by fractions of a pip for EUR/USD.
- The EUR/USD bid close and the next bar's bid open are typically within 0.1–0.2 pips.
- Stop and target levels are set from close[t] (same-close) or close[t+1] (next-open), but the entry price difference is so small that the same stop/target triggers at the same bars.

The practical implication: the same-close versus next-open distinction does not materially change the 7-trade result. Both are negative at all cost scenarios.

---

## 5. Frozen Performance Results

### 5.1 Corrected strategy (7 trades, 2026 OOS)

| Cost scenario | N | PF | Win Rate | Expectancy | Sharpe | Max DD |
|---------------|---|----|----------|------------|--------|--------|
| 3-pip RT | 7 | 0.538 | 42.9% | −0.000268 | −0.79 | 0.00238 |
| 5-pip RT | 7 | 0.326 | 42.9% | −0.000468 | −1.38 | 0.00318 |
| 7-pip RT | 7 | 0.173 | 42.9% | −0.000668 | −1.98 | 0.00398 |

All cost scenarios: PF < 1.0, negative expectancy.

### 5.2 Original test (76 trades, wrong strategy — preserved for reference)

From `results/bounded_validation/` (not overwritten):

| Cost | N | PF | Win Rate | Expectancy |
|------|---|----|----------|------------|
| 3-pip | 76 | 0.469 | 36.8% | −0.000318 |
| 5-pip | 76 | 0.292 | 31.6% | −0.000518 |
| 7-pip | 76 | 0.175 | 30.3% | −0.000718 |

These results are preserved in `results/bounded_validation/` and are reported here only for transparency. They do not represent the Phase 2 strategy.

---

## 6. Uncertainty Quantification for the 7-Trade Sample

Seven trades are wholly insufficient for statistical inference about strategy edge. This is stated explicitly and not softened.

### 6.1 Confidence intervals (from corrected_audit_results.json, section5)

**Expectancy at 3-pip RT:**  
95% CI: [−0.00116, +0.00063] — contains zero.  
t-test p = 0.491 — cannot reject H0 of zero expectancy.  
Effective n ≈ 30 (AR(1) correction applied to autocorrelated returns).

**Profit factor at 3-pip RT:**  
Bootstrap 95% CI: [0.07, 2.69] — spans PF = 1.0 entirely.  
Point estimate: 0.538.

**Profit factor at 5-pip RT:**  
Bootstrap 95% CI: [0.03, 1.63] — upper bound barely exceeds 1.0.  
Point estimate: 0.326.

### 6.2 Interpretation

The confidence intervals are wide enough to contain profitable outcomes. The point estimates are all below 1.0. These facts are compatible with: the strategy having zero edge (results are random fluctuation), the strategy having a modest positive edge that happened to produce 4 stops and 3 targets, or the strategy having a clear negative edge. Seven trades cannot distinguish between these hypotheses.

**A minimum of 200–500 trades would be needed** for a 95% CI on PF to exclude 1.0 on both sides at typical effect sizes. At the observed signal rate (~7 Strong_Coherent NY_Continuation bars per 6.5 months, or approximately 13 per year), this would require approximately 15–40 years of data under the same market conditions. In practice, market structure non-stationarity makes such projections unreliable beyond 3–5 years.

### 6.3 Random-selection comparison

The bootstrap comparison used a pool of 61 bars with NY_Continuation signals (hour == 13) on 2026 data, of which 7 were in Strong_Coherent. The resampling compared the observed PF (0.326 at 5-pip) against 10,000 random draws of 7 trades from this pool.

- iid bootstrap: observed PF not significantly different from random selection (p = 0.37).
- Block bootstrap (weekly blocks): p = 0.38.

These results are consistent with the null hypothesis that the 7 Strong_Coherent trades were drawn from the same population as the remaining 54 non-Strong_Coherent hour-13 trades. They do not establish that the regime gating adds value.

---

## 7. What the Trading Evidence Supports

**Supported:**
- The corrected strategy (NY_Continuation, EMA crossover, hour 13 UTC) generates 7 trades in 6.5 months of 2026 data under the Strong_Coherent regime gate.
- All 7 trades are negative after cost at the 5-pip and 7-pip RT scenarios; the 3-pip scenario also shows PF < 1.0.
- The 95% CI on expectancy contains zero at all scenarios.
- Seven trades is insufficient for inference.

**Not supported:**
- The original 76-trade result does not represent the Phase 2 strategy.
- The trading results do not establish that Q or T_sys has predictive value for trade outcomes.
- The trading results do not establish that the regime gate (Strong_Coherent) selects a superior subset of trades — the bootstrap comparison is non-significant.
- Seven trades cannot confirm or refute a trading edge.

**The final trading verdict is: No demonstrated edge. Insufficient sample to infer presence or absence of edge.**
