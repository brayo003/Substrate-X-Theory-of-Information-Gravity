# End-to-End Data Flow
## Finance Module — From Raw Input to Final Decision

**Audit date:** 2026-10-17  
**Git commit:** `6738ed05`

---

## 1. Data Flow Diagram

```
Dukascopy .bi5 tick files
(data/2023/00/DD/HHh_ticks.bi5)
        │
        │ lzma.decompress() + struct.unpack()
        ▼
Tick DataFrame [timestamp, ask, bid, ask_vol, bid_vol, mid, spread_pips, total_vol]
        │
        │ build_ohlc(freq='5min')  [signals.py, lines 19-34]
        ▼
5-minute OHLC bars [open, high, low, close, volume, spread, tick_count, returns]
        │
        │ compute_raw_signals()  [signals.py, lines 37-63]
        ▼
6 Raw Signals:
  - volatility = rolling(20).std(returns)
  - volume_ratio = volume / MA(volume, 50)
  - spread_ratio = spread / MA(spread, 50)
  - tick_frequency = rolling(20).mean(tick_count)
  - momentum_20min = pct_change(4) of close
  - momentum_1hr = pct_change(12) of close
        │
        │ normalize_signals()  [signals.py, lines 65-90]
        │ z-score with 99th-pct clip, then sigmoid → (0,1)
        ▼
6 Normalized Signals (all in 0,1 range)
        │
        │ build_composite()  [signals.py, lines 92-109]
        │ row-mean of all 6 normalized signals
        ▼
composite_norm  [pd.Series, values in (0,1), 5-min indexed]
        │
        ├─────────────────────────────┐
        │                             │
        │ scale_signals_to_100()      │ compute_transport_from_series()
        │ [engine_runner.py, 50-67]   │ [transport_layer.py, 157-196]
        ▼                             ▼
scaled signals [0,100]          transport DataFrame:
        │                         - s: raw composite field
        │ build_v12_composite()   - s_transport: PDE-evolved field
        │ rescale median→8.0      - grad_ln_s: ∇ln(s) = ln(s_t/s_{t-1})
        ▼                         - Q = 4(cτ)²|∇ln(s)|² − 1
v12_composite  [0,~30]           - regime: +1 COHERENT / -1 INCOHERENT
        │                         - regime_str
        │ run_v12()               - Q_abs
        │ [engine_runner.py, 102] - xi_c = 2cτ = 10 bars
        ▼
V12 DataFrame per bar:               │
  - T_sys  [0,∞ clipped in practice] │
  - phase  [NOMINAL / FIREWALL]      │
  - excitation                       │
  - inflow = E×β                     │
  - outflow = γ_eff×γ×T_sys          │
  - gamma                            │
        │                             │
        └─────────────┬───────────────┘
                      │ _apply_transport_pipeline()  [p1_data_stream.py]
                      │ Merge into OHLC + add indicators:
                      │   ATR(14), RSI(14), MACD, ADX(14), realized_vol_20
                      ▼
Complete bar DataFrame (columns: open,high,low,close,volume,spread,
  tick_count, returns, T_sys, phase, excitation, composite_norm,
  tr_Q, tr_regime, tr_s_transport, tr_grad_ln_s, tr_Q_abs, tr_xi_c,
  atr_14, rsi_14, macd, macd_signal, macd_hist, adx_14,
  realized_vol_20, realized_vol_5, vol_norm)
        │
        │ Cached to: cache/ohlc_transport_YYYY_MM.parquet
        │
        ▼
═══════════════════════════════════════════════════════════════════
  PHASE 1: Strategy × Regime Performance Mapping
═══════════════════════════════════════════════════════════════════
        │
        │ For each of 28 strategies:
        │   generate_signals(df)  [strategy_library.py]
        │   ← STRATEGIES DO NOT CONSULT Q OR T_sys ←
        │   Output: signal Series {-1, 0, +1} based on price/indicators
        │
        │ classify_q_global(tr_Q, q05, q95)  [p1_data_stream.py]
        │ Assigns 5-level regime label to each bar using frozen thresholds
        │
        │ simulate_strategy_on_chunk()  [p1_strategy_runner.py]
        │ Executes strategy under uniform ATR stop/target/cost
        │ Records entry_regime (the Q regime at trade entry)
        ▼
Trade records with columns:
  entry_time, exit_time, direction, entry_price, exit_price,
  gross_ret, net_ret, duration_bars, stop_hit, target_hit, timeout,
  entry_Q, entry_regime [Deep/Mod/Trans/Weak/Strong], strategy, family
        │
        │ Aggregated into Phase 1 matrix:
        │ 28 strategies × 5 regimes = 140 cells
        ▼
performance_by_regime.csv  [results/phase1/]
phase1_strategy_matrix.csv/md
        │
═══════════════════════════════════════════════════════════════════
  PHASE 2: Transport Operating System
═══════════════════════════════════════════════════════════════════
        │
        │ TransportOSCalibration.calibrate()  [p2_transport_os.py]
        │ Reads Phase 1 matrix → derives 3 layers:
        │   Layer 1: best strategy per regime (or NO_TRADE)
        │   Layer 2: risk fraction per regime
        │   Layer 3: stop/target ATR multipliers per regime
        │
        │ At each bar: classify_q_global_p2(Q, q05, q95)
        │   → regime name
        │   → TransportOSCalibration.decide(regime)
        │   → {trading_allowed, strategy, risk_fraction, stop/target mults}
        ▼
Phase 2 result (2023-2025):
  43 trades, PF=1.077, Sharpe=0.132, 95% no-trade
  (Statistically insufficient for inference)
```

---

## 2. Explicit Path for Every Claimed DCIF/Substrate Quantity

### 2.1 T_sys
- **Computed:** `v12_validate/engine_runner.py` `run_v12()` lines 102–132
- **Input:** `v12_composite` (rescaled mean of 6 price-microstructure signals)
- **Equation:** `T_sys += (E×β - γ_eff×γ×T_sys) × dt` — differential form of SXCOmegaEngine
- **Stored in:** column `T_sys` in cached parquet files
- **Used in:** V12 validation plots, predictive correlation tests
- **Does T_sys affect trade entries or exits?** **NO.** T_sys is recorded as a column but is not consulted by any strategy signal generator or the Phase 2 OS decision function.
- **What would change if T_sys removed?** Nothing in the trading pipeline. Descriptive metrics only.

### 2.2 Q (Transport Discriminant)
- **Computed:** `v12_validate/transport_layer.py` `compute_transport_field()` lines 135–141
- **Input:** `composite_norm` (mean of 6 normalized signals)
- **Equation:** `Q = 4(cτ)²|ln(s_t/s_{t-1})|² − 1` (with c=1, τ=5: `Q = 100×log-return² − 1`)
- **Stored in:** column `tr_Q` in cached parquet files
- **Used in (Phase 1):** Post-hoc regime label for trade records. Strategies do NOT receive Q as input.
- **Used in (Phase 2):** Q is classified into 5 regimes; regime determines which strategy is allowed and at what size.
- **Does Q affect trade entries in Phase 1?** **NO.** Q is applied retroactively to label which regime a trade occurred in.
- **Does Q affect trade entries in Phase 2?** **YES.** The OS uses Q regime to determine whether to trade. 95% of bars → NO_TRADE. The 5% that trade use conventional strategies.
- **What would change if Q removed?** Phase 2 would need a different regime classifier. Phase 1 results would be identical (just unsliced).

### 2.3 s_transport (PDE-evolved field)
- **Computed:** `v12_validate/transport_layer.py` IMEX loop lines 93–133
- **Stored in:** column `tr_s_transport` in cached parquet files
- **Used in:** Nowhere in the trading pipeline. It is stored but never read by any strategy, OS, or decision function.
- **Status: UNUSED output.** The transport PDE is solved but its output is discarded.

### 2.4 grad_ln_s
- **Computed:** `v12_validate/transport_layer.py` lines 135–141
- **Stored in:** column `tr_grad_ln_s` in cached parquet files
- **Used in:** As the sole input to Q (monotone relationship). Also tested as a standalone signal in `transport_signal_eval.py`.
- **Transport signal eval result:** Standalone grad_ln_s gate (Strategy D) FAILS walk-forward. PF=0.400 WF combined.

### 2.5 DCII Index (src/ layer)
- **Computed:** `src/dcii_core.py` `DCIIEquation.compute()` lines 20–44
- **Input:** Simulated signals (numpy random seed 42)
- **Used in:** `src/finance_module.py` tutorial pipeline only
- **Does it affect any real experiment?** **NO.** The `src/` layer is tutorial code that has never been run on real market data in the active pipeline.

---

## 3. Unused Outputs and Disconnected Components

| Component | Computed | Used in decisions | Notes |
|---|---|---|---|
| `s_transport` (PDE output) | Yes, every bar | **NO** | Stored in parquet; never read by any strategy or OS |
| `xi_c` (coherence length) | Yes, constant=10 | **NO** | Documented but no trading use |
| `src/dcii_core.py` DCIIEquation | Yes (demo) | **NO** | Tutorial only, simulated data |
| `src/finance_module.py` FinanceDCIIModule | Yes (demo) | **NO** | Never imported by active pipeline |
| `src/forex_pipeline.py` | Imported by monitor_forex.py | Reporting only | Offline analysis, not trading |
| `T_sys` state variable | Yes, every bar | **NO** in trading | Predictive correlation study only |
| Live logs (live_logs/) | Yes, sim paper trades | Monitoring only | Simulation, not live broker |

---

## 4. Key Structural Problem: Strategy Independence from Framework

The central structural problem is not a code bug. It is a design choice:

**All 28 trading strategies are explicitly designed to be independent of Q and T_sys.**

The strategies in `strategy_library.py` use: EMA crossovers, SMA crossovers, MACD histograms, Donchian channels, RSI, Bollinger Bands, ATR expansion, Stochastic oscillators, session hour filters — all conventional technical analysis.

Q is used only to:
1. Label which market regime a trade occurred in (Phase 1 — retrospective labeling)
2. Gate whether trading is allowed at all (Phase 2 — the OS)

This means removing Q from Phase 2 and replacing it with any other volatility-based gate would produce a structurally identical system. The transport mathematics is not the source of any trading signal. It is only a classifier.

The decisive question — does the transport/DCIF classification perform better than a simple volatility-based classifier? — has not been tested with sufficient statistical power. 43 in-sample trades (Phase 2 IS) and 7 out-of-sample trades do not allow this question to be answered.
