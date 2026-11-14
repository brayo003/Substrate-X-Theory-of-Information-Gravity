# Execution Audit
## Transport OS — Signal Availability, Entry/Exit Timing, Look-Ahead

**Audit date:** 2026-10-11 | **Commit:** `6738ed05`

---

## 1. Complete Code Path: Raw Data → Signal → Order → Fill → PnL

### Data loading (p1_data_stream.py)

```
_load_bi5_month() / _load_csv_2025_month()
  → ticks DataFrame (timestamp, ask, bid, mid, spread_pips, total_vol)
  → _apply_transport_pipeline(ticks)
      → build_signals_from_ticks()  [signals.py]
          → build_ohlc(ticks, freq="5min")           # resample ticks → OHLC
          → compute_raw_signals(ohlc)                # rolling windows, all backward
          → normalize_signals(raw)                   # z-score + sigmoid
          → build_composite(normalized)              # row-mean → s ∈ (0,1)
      → scale_signals_to_100(raw_sigs)              [engine_runner.py]
      → build_v12_composite(scaled_sigs)
      → run_v12(v12_composite)                       # SXCOmegaEngineStable, bar-by-bar
      → compute_transport_from_series(composite)     [transport_layer.py]
          → compute_transport_field(s)
              → s_transport (IMEX PDE)
              → grad_ln_s[t] = ln(s[t]/s[t-1])      # backward difference
              → Q[t] = 100 * grad_ln_s[t]^2 - 1
              → regime = +1 if Q>0 else -1
      → atr_14, rsi_14, macd, adx_14 computed from close
  → written to cache/ohlc_transport_YYYY_MM.parquet
```

### Phase 1 execution (p1_strategy_runner.py)

**Function:** `simulate_strategy_on_chunk(df, signals, strategy_name, family, q_regimes)`

| Line | Action | Information available? |
|------|--------|----------------------|
| 56 | `sig = signal_vals[i]` | Signal computed from close[i] via ewm — close[i] must be final |
| 57 | `entry_price = float(close[i])` | Requires close[i] to be final — same constraint as signal |
| 58–60 | ATR and direction from bar i | All from bar i close/atr — both require bar i to be complete |
| 64–67 | Compute stop_price, target_price from entry_price and atr[i] | Correct — uses only bar i values |
| **76** | `for j in range(i+1, max_j+1)` | **Stop/target checking starts at bar i+1** — no same-bar stop |
| 77–101 | Check high[j], low[j] for each future bar j | Uses only future bars — no leakage |
| 104 | `max_j = min(i + HOLD_BARS, n-1)` | 24-bar hold, truncated at chunk end |
| 105 | `exit_price = float(close[exit_j])` | Exit at close of exit bar (bar when stop/target triggered) |
| 108 | `net_ret = gross_ret - TOTAL_COST_RT` | Cost deducted once, correctly |

### Phase 2 execution (p2_execution_engine.py)

**Function:** `run_transport_os_on_chunk(df, os, strategy_registry, state, bar_offset)`

| Lines | Action | Comment |
|-------|--------|---------|
| 85–88 | Read Q[i], classify regime, call os.decide() | Decision at bar i close — same timing issue |
| 90–122 | `if state.in_trade:` manage open trade | Uses high[i]/low[i] of current bar — correct (trade entered PRIOR bar) |
| 124–150 | `if not state.in_trade:` new entry at close[i] | Entry at close[i] after signal from close[i] |

**Key structural point in p2:** The loop processes stop management BEFORE entry. If a trade was entered at bar `i-1`, its stop is checked at bar `i` using `high[i]`, `low[i]` — this is correct. A new trade entered at bar `i` CANNOT have its stop checked at bar `i` because `state.in_trade` is read before the entry block. Therefore there is **no same-bar stop/target issue in p2**.

---

## 2. Same-Close Entry Issue

### Finding

Both `p1_strategy_runner.py` and `p2_execution_engine.py` enter at `close[i]` after generating a signal that requires `close[i]` to be finalized. This is the same-bar execution assumption used throughout the backtest.

**Is it causally justified?**

For a strict real-time system: No. `close[i]` is only known at the end of bar `i`. A trader cannot place and fill a market order at `close[i]` after observing `close[i]`.

**Practical magnitude:** For a 5-minute EUR/USD bar, the difference between `close[i]` and `open[i+1]` is typically 0.1–0.3 pips. This is small relative to the 3-pip modeled cost but creates a systematic bias whose direction is unknown (can be favorable or unfavorable depending on momentum).

**Diagnostic result:** Running the original (wrong) signal with next-bar-open entry gives PF=0.405 vs PF=0.469 same-close at 3-pip RT. Both are negative. The corrected strategy (7 trades) shows identical PF under both entry modes at 5-min resolution. **The same-close issue does not change the verdict.**

---

## 3. Strategy Mismatch (Critical Finding)

### `bounded_validation.py` `generate_ny_continuation_signals()` vs `strategy_library.py` `NY_Continuation`

| | `strategy_library.py` NY_Continuation | `bounded_validation.py` custom signal |
|---|---|---|
| **Session filter** | `hour == 13` (UTC) only | `hour >= 14` and `hour < 21` |
| **Signal logic** | EMA(9) > EMA(21) crossover | RSI(14) crossing 50 + MACD > 0 + ADX > 20 |
| **2026 signal count** | 61 signals (all at hour 13) | 797 signals (hours 14–20) |
| **2026 SC trades** | 7 | 76 |

**The 76-trade 2026 result never tested the Phase 2 strategy.** Entry hours in the original result: 14–20 UTC; zero entries at 13 UTC.

This was introduced in `bounded_validation.py` during its authoring. It is not an issue in any of the production files (`p1_strategy_runner.py`, `p2_execution_engine.py`, `strategy_library.py`). The production Phase 2 run correctly used `strategy_library.py:NY_Continuation`.

---

## 4. Stop/Target Ambiguity on Same Candle

Both engines check `low <= stop_price` before `high >= target_price`. When both conditions are true within one candle, the stop is recorded. This is **conservative**: it assigns the worse outcome to ambiguous bars.

An alternative (target first) would give more favorable results. Random ordering would sit between the two. The conservative assumption is appropriate for validation purposes.

---

## 5. 24-Bar Hold Period

**p1_strategy_runner.py:** `max_j = min(i + HOLD_BARS, n - 1)`. When a signal fires near the end of a monthly chunk, the hold is truncated. This slightly reduces maximum hold time at month boundaries. Effect is small (at most 1–2 trades per month affected).

**p2_execution_engine.py:** `elapsed = i + bar_offset - state.entry_bar`. `bar_offset` accumulates across monthly chunks, so the 24-bar hold is computed correctly across boundaries. P2 handles this correctly; p1 has a minor edge case.

---

## 6. Dataset Limitation: Bid-Only Prices

**2026 CSV columns:** timestamp (Unix ms), open, high, low, close — **bid prices only**. No ask column.

**Implication:** True buy fills are at ask (bid + spread); true sell fills are at bid. The flat cost `TOTAL_COST_RT` approximates this. For a long entry: actual entry ≈ ask ≈ close + 0.5–1.5 pips above modeled entry. For a short entry: actual entry ≈ bid ≈ close (favorable). The bias direction is **slightly unfavorable for long trades, neutral for short trades**. Given the distribution of long/short entries (mixed), the overall effect on PF is small and well within the modeled cost range.

**Limitation statement:** Realistic execution cannot be fully reconstructed from bid-only data. The flat-cost approximation is standard for retail forex backtesting but does not capture intraday spread variation.

---

## 7. Future Information Leakage — Summary

| Check | Finding |
|-------|---------|
| Signal uses future close | No — all ewm/rolling use `adjust=False`, backward-looking |
| Signal uses future Q | No — Q not consulted inside strategy functions |
| Entry uses close[i] before bar close | Yes — same-close issue (low severity, see Section 2) |
| Stop/target triggered on entry bar | No — inner loop starts at i+1 (p1) / sequential structure (p2) |
| Q thresholds derived from future data | No — derived from 2023–2025 only, confirmed from manifest |
| 2026 data in calibration period | No — zero 2026 cache parquets before test |
| Strategy selection used 2026 data | No — Phase 1/2 calibration used 2023–2025 only |

---

*Audit performed via direct source reading with line-number citations.*  
*No code was modified. All findings are documented from actual function calls.*
