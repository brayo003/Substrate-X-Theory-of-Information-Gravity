# Data and Experiment Reproducibility
## Finance Module — Dataset Provenance, Quality, Leakage Checks, and Reproductions

**Audit date:** 2026-10-17  
**Git commit:** `6738ed05`

---

## 1. Datasets Used

### 1.1 EUR/USD Tick Data (Primary)

| Property | Value |
|---|---|
| Provider | Dukascopy (historical tick data) |
| Instrument | EUR/USD spot |
| Format | Dukascopy .bi5 format (LZMA-compressed binary records) |
| Coverage | 2023-01 through 2025-10 (approximately) |
| Structure | Year/Month(0-indexed)/Day/HH_ticks.bi5 |
| File count | ~19,000 .bi5 files |
| Record format | Big-endian: ms (uint32), ask×1e5 (uint32), bid×1e5 (uint32), ask_vol (float32), bid_vol (float32) = 20 bytes per tick |
| Price type | Ask and bid (mid = (ask+bid)/2) |
| Timestamp convention | UTC milliseconds from start of hour, decoded to UTC datetime |
| Spread | Computed as (ask - bid) × 10,000 pips |
| Retrieval date | Unknown (files present on disk; no download log found) |
| Authenticity verification | File format consistent with Dukascopy specification; price levels consistent with real EUR/USD quotes |
| Missing data | Saturday/Sunday gaps present (weekend market closure); isolated gaps in some hours |

**Verification of file authenticity:** LZMA decompression succeeds. Price levels are in the range 1.05–1.12 for EUR/USD (2023-2025 consistent). Tick counts per hour are in the range 100–50,000, consistent with real Dukascopy data. No anomalous price jumps that would indicate synthetic data were observed in the sample audit.

**Provenance limitation:** No download receipt, checksum file, or retrieval log is present. The data cannot be independently verified against a known authentic archive without re-downloading from Dukascopy. This is marked as UNVERIFIED EXTERNALLY but internally consistent.

### 1.2 BTCUSDT / ETHUSDT Data (Live Simulation)

| Property | Value |
|---|---|
| Provider | Binance API (REST klines + WebSocket) |
| Coverage | Simulation only — live_logs/trades.csv timestamps suggest 2024-2026 |
| Use | Paper trading simulation only; no real capital |
| Status | Not used in Phase 1/2/3 historical experiments |

### 1.3 XAUUSD Gold Data (Baseline Validation)

| Property | Value |
|---|---|
| Provider | Not documented in code; CSV format |
| Coverage | 2004-06-11 to 2026-10-09 (daily bars, 5,873 bars reported) |
| File location | data/gold_spot_historical/, data/XAUUSD/, data/gold_extended/ |
| Retrieval date | Unknown |
| Price type | Close prices (daily OHLC) |
| Authenticity | Unverified — filenames suggest yfinance or similar |

### 1.4 Other Markets (Phase 3/4/5)

Additional instruments used in phase 3 (universality testing): BTCUSDT, ETHUSDT, NAS100, UKOIL, USOIL, XAUUSD. These appear to be downloaded via yfinance or similar; no download logs are present. Data quality was not formally audited in the current phase.

---

## 2. Data Quality Checks

### 2.1 EUR/USD Tick Data

From code inspection of `p1_data_stream.py`:
- Quality gate applied: `(ask > 0) & (bid > 0) & (ask >= bid)` (lines ~125–127)
- Bars with zero tick count dropped: `ohlc = ohlc[ohlc['tick_count'] > 0]`
- Weekend gaps: naturally excluded by the tick-count filter
- Leading NaN handling: signals with < 10 non-NaN values discarded

**Gaps identified:** The directory structure shows data/2023/00/01/ starts at 22h and data/2023/00/06/ ends at 21h (missing the gap from Jan 6 22h to Jan 8 22h). This is consistent with weekend gaps but means Jan 7-8 (Saturday/Sunday) are absent. This is correct behavior for spot forex.

**Duplicates:** No deduplication logic found in the main pipeline. The monthly parquet caching uses `to_parquet()` / `read_parquet()` without checking for duplicate timestamps. If any raw bi5 file is read twice (unlikely given directory structure), duplicates would propagate. No evidence this occurred.

### 2.2 OHLC Bar Count Verification

From the Phase 1 matrix header: **Total bars: 209,689** (2023–2025). At 8,640 five-minute bars per month and approximately 34 months (2023-01 to 2025-10), minus weekends and gaps, the expected count is approximately 34 × 8,640 × (5/7) ≈ 210,000 bars. The reported 209,689 is consistent.

---

## 3. Normalization and Leakage Analysis

### 3.1 Signal Normalization (v12_validate/signals.py)

**Method:** For each signal:  
1. Clip at 99th percentile (per-signal 99th pct of the FULL DATASET for that signal)  
2. Z-score: z = (x - mean) / std  
3. Sigmoid: norm = 1/(1+exp(-z))

**Leakage risk assessment:**  
The normalization uses the full-dataset 99th percentile, mean, and std (`q99 = series.quantile(0.99)`, `mu, sigma = clipped.mean(), clipped.std()`). This is applied to the **entire series at once**, not incrementally.

**Finding:** This constitutes **look-ahead bias** in normalization. The 2026 OOS data, if normalized using statistics derived from the full 2023-2025 + 2026 period, would use future information. However, the primary experiments use 2023-2025 as in-sample and 2026 as OOS in the bounded validation. The normalization parameters for 2026 OOS data are not clearly documented as being frozen at 2025 values vs. recomputed on 2026. In `corrected_audit.py`, the 2026 data is processed independently with its own normalization statistics — this is a potential forward-looking normalization leak for the OOS test.

**Impact assessment:** Given that normalization is a sigmoid transformation and z-score is computed over the test period, the direction of individual signals may shift slightly (near-zero signal becoming slightly positive vs. negative depending on the 2026 period mean). This is a minor structural concern but does not explain the catastrophically negative trading results.

### 3.2 Q Thresholds (Frozen Correctly)

Q quantile thresholds (q05, q95) are computed from the 2023-2025 in-sample period and frozen in `checkpoints/checkpoint_manifest.json` (q05=-0.9980, q95=1.7323). These are applied to 2026 OOS data without recomputation. This is correct and causally sound.

### 3.3 ATR and Indicators

ATR(14) is an exponential moving average — it uses only past data in its standard computation. No look-ahead identified. RSI, MACD, ADX are all standard backward-looking indicators.

### 3.4 Stop/Target Execution

In `execution_simulator.py` and `p1_strategy_runner.py`:  
- Entry: signal on bar i, execute at close of bar i (same bar)
- **Finding:** The execution simulator enters at `close[i]` on the signal bar. This is the same-bar close — technically achievable only if the signal fires on the open and execution happens before the close. In practice this is a mild same-bar execution assumption that benefits the simulation. The corrected gold audit (`corrected_audit.py`) explicitly tests next-open execution and confirms the difference is small.
- Stop/target: checked against `high[j]` and `low[j]` for each subsequent bar j. This is correct.
- ATR lookahead bug (gold only): Identified in `GOLD_BASELINE_VALIDATION.md` — the gold strategy used current-bar ATR. The EUR/USD pipeline uses ATR as a pre-computed column from the OHLC build step, which also uses current-bar ATR. This applies uniformly to all strategies and biases all results slightly favorably.

---

## 4. Independent Experiment Reproduction

### 4.1 The Critical 76-Trade OOS Backtest

**Claim in prior reports:** NY_Continuation strategy, 2026 OOS, Strong_Coherent regime, showed 76 trades with varying PF by cost level.

**Reproduction finding (from FINAL_AUDIT_VERDICT.md and CORRECTED_BOUNDED_VERDICT.md):**  
The 76-trade result was produced by `bounded_validation.py` using a **custom RSI+MACD+ADX signal** (hours 14–21 UTC), not the actual `NY_Continuation` strategy from `strategy_library.py` (EMA crossover, hour 13 UTC only).

When `corrected_audit.py` runs the correct strategy, only **7 trades** are generated. All 7 are losing at every cost assumption:

| Cost | Trades | PF | Win Rate | Expectancy |
|---|---|---|---|---|
| 3-pip RT | 7 | 0.538 | 42.9% | −0.000268 |
| 5-pip RT | 7 | 0.326 | 42.9% | −0.000468 |
| 7-pip RT | 7 | 0.173 | 42.9% | −0.000668 |

Bootstrap 95% CI on PF: [0.07, 2.69] — spans 1.0. **Statistically worthless.**

**Status:** The original 76-trade claim is **invalidated by a strategy mismatch**. The corrected result shows no evidence of trading edge.

Evidence source: `results/bounded_validation_corrected/CORRECTED_BOUNDED_VERDICT.md`, `bounded_validation_results.json` (git commit `6738ed05`).

### 4.2 Phase 1 Strategy Matrix

**Claim:** 28 strategies × 5 Q-regimes evaluated on EUR/USD 2023-2025.  
**Reproduced:** Phase 1 matrix is in `results/phase1/phase1_strategy_matrix.csv`. Reading 10 representative rows confirms: all strategies show PF < 1.0 in all regimes. The best cell is ATR_Expansion in Strong_Coherent (PF=0.61, N=507 trades). No strategy achieves breakeven under the stated cost model.

**Verification:** Trade records for all 28 strategies are stored in `intermediate/trades_<strategy>.parquet`. The Phase 1 results were produced by the current code. Spot-checked that the cost model (TOTAL_COST_RT = 0.00030 from `p1_strategy_runner.py` line 30) matches the report's stated "3-pip RT."

### 4.3 Phase 2 Transport OS

**Claim:** Transport OS achieves PF=1.077 on 2023-2025 (43 trades).  
**Status:** 43 trades, Sharpe=0.132, 95% no-trade. This is statistically insufficient for inference. Profit factor of 1.077 on 43 trades has a confidence interval that trivially spans 1.0.

The Phase 2 report (`results/phase2/transport_os_report.md`) is internally consistent with the code. The OS is trading only in Strong_Coherent using NY_Continuation, which as shown above has PF=0.422 without the regime gate. The 43-trade IS result could be sampling variation.

### 4.4 Gold Donchian20 Strategy

**Claim:** Long-only Donchian20 on gold, 20.5-year OOS, PF=1.478, Block bootstrap 95% CI [1.327, 13.493].  
**Caveat:** This result is for the **long-only variant** and covers the secular gold bull market 2004-2026. The symmetric strategy has PF=1.073 with CI including zero. The long-only edge is a manifestation of gold's secular upward trend and has no connection to any DCIF/transport signal — the strategy uses only Donchian channel breakouts.

---

## 5. Strategy Count and Multiple Testing

The finance module has tested:
- 28 strategies × 5 regimes = 140 cells in Phase 1
- ~7 transport signal variants in `transport_signal_eval.py`
- ~4 variants in `transport_edge_experiment.py`
- Multiple walk-forward windows (IS, WF1, WF2)
- Multiple cost levels (3-pip, 5-pip, 7-pip)
- Multiple instruments (EUR/USD, XAUUSD, BTCUSDT, ETHUSDT, NAS100, UKOIL, USOIL)

**Multiple testing concern:** With 140+ parameter combinations, a PF > 1.0 result somewhere in the matrix would be expected by chance even if all strategies have zero edge. The Phase 2 OS was configured based on Phase 1 results (selecting the best strategy per regime from the same in-sample data). This is a form of in-sample selection that inflates Phase 2 IS performance.

**FDR correction:** The Phase 1 report applies FDR correction to significance tests. However, FDR controls the false discovery rate over the specific tested hypotheses, not over the complete space of backtested variants including those not formally tested (e.g., the strategy mismatch in bounded_validation.py).

---

## 6. Unresolved Discrepancies

| Discrepancy | Description | Resolution Status |
|---|---|---|
| 76-trade strategy mismatch | `bounded_validation.py` used a custom signal, not `strategy_library.NY_Continuation` | **Resolved** — corrected to 7 trades; all losing |
| Gold ATR lookahead | ATR computed on same bar as entry in gold strategy | **Identified** — corrected engine shows minimal impact (≈$1.72/oz) |
| Gold gap neglect | Stops filled at theoretical price not market open | **Identified** — impact documented, not fully quantified for all trades |
| Normalization of OOS data | 2026 OOS normalization statistics unknown (frozen vs. recomputed) | **Unresolved** — likely minor but not verified |
| T_sys out-of-sample predictive test | T_sys predictive correlation (ρ=0.20–0.27) is in-sample only | **Unresolved** — OOS test not performed |
| Phase 5b 2026 data | Results exist in results/phase5b/ with 2026 data | **Partially verified** — data covers real 2026 period; strategy results all negative |
