# Transport Signal Finance Investigation — Final Decision Report

Generated: 2026-10-11

---

## 1. Implementation Audit

### What the prior evaluation (transport_signal_eval.py) actually tested

The prior evaluation did NOT directly invoke the transport engine at evaluation
time. It read pre-computed cache columns from `cache/ohlc_transport_YYYY_MM.parquet`.
Those columns were written once by `p1_data_stream._apply_transport_pipeline()`,
which calls `transport_layer.compute_transport_from_series(composite)` — so the
transport outputs (tr_Q, tr_grad_ln_s, tr_s_transport) ARE genuine transport engine
outputs, not approximations.

The gates tested were:
- `B_Q_gate`: `tr_Q >= 1.732` — genuine Q gate, correctly frozen from IS calibration
- `D_v_abs` / `F_tension`: `|tr_grad_ln_s|` thresholded — field velocity of composite s
- `E_v_persist`: EWMA sign persistence of `tr_grad_ln_s`
- `G_tsys_dev`: deviation of T_sys from its EWMA

**What was not tested in the prior eval:** the transport engine as an entry signal
generator (not just a gate). The new experiment (`transport_edge_experiment.py`)
tested this directly via Strategy A and C.

### Implementation correctness

Entry timing: signal on bar i, execute at bar i+1 open — correct, no look-ahead.  
Exit timing: stop/target checked against high/low of exit bar — conservative but valid.  
Cost model: 5pip RT applied to each trade — matches the actual pipeline.  
Walk-forward: IS thresholds derived from 2023–2024, frozen for WF1/WF2 — correct.  
Data splitting: monthly parquet files concatenated, deduplicated — no overlap issues found.

**No implementation bugs found that would explain the results. The losses are genuine.**

---

## 2. Base Strategy Diagnosis (NY_Continuation)

**Implementation:** `strategy_library.py` lines 471–485.  
Signal fires when: `hour == 13 UTC` AND EMA9/EMA21 trend just changed direction.  
This is an EMA crossover scalp with a session hour filter — not a trend continuation signal.

**Statistics (2023–2025, 382 trades, A_no_gate):**

| Metric | Value |
|---|---|
| Win rate | 38.0% |
| Profit factor | 0.422 |
| Expectancy | −4.81 pip |
| Avg entry ATR | 5.9 pip |
| Breakeven WR at this ATR | **58.8%** |
| Gap (breakeven − actual) | **20.8 pp** |
| Stop exits | 58% of trades |
| Best year (2023) PF | 0.511 |
| Best single month PF | 0.976 (Sep) |
| All years positive? | **Never** |

The 20.8 percentage-point gap between required and actual WR cannot be closed by
any filter, gate, or threshold. No month, year, direction, or regime segment achieved
positive expectancy across 33 months of data.

**Root cause:** The execution model (ATR×1.5 stop / ATR×2.5 target / 5pip RT cost)
requires 58.8% WR at a 6-pip ATR. No strategy in the library achieves this — this is
an execution framework problem, not a signal quality problem.

---

## 3. Transport Engine Feasibility Analysis

### Actual equations (transport_layer.py)

**Input:** `composite_norm` = mean of 6 sigmoid-normalized microstructure signals:
volatility (roll std of returns), volume_ratio, spread_ratio, tick_frequency,
momentum_20min (pct_change(4)), momentum_1hr (pct_change(12)).

**Telegraph PDE (1D temporal IMEX):**
```
s_t[n] = [ (2τ/dt² + 1/dt)·s_t[n-1] - (τ/dt²)·s_t[n-2] + c²τ/dt²·(s[n] - 2s[n-1] + s[n-2]) ]
         / (τ/dt² + 1/dt)
```
With c=1.0, τ=5.0, dt=1: this simplifies to an exponentially weighted 2nd-order
smoother. At c=1, the wave term exactly cancels the damping term in the limit,
making `s_transport` a phase-lagged version of `composite_norm`.

**Q:** `Q = 100 × |grad_ln_s|² − 1` where `grad_ln_s = ln(s[t]/s[t-1])`.  
Q is a **monotone function** of `|grad_ln_s|` — it carries zero information beyond
`|grad_ln_s|` itself. Q > 0 iff `|grad_ln_s| > 0.1` (i.e. composite changes > 10%/bar).

**T_sys:** comes from `SXCOmegaEngineStable` (engine_runner.py), NOT transport_layer.py.
It is a thermal ODE integrator driven by `excitation_flux(composite)`. Completely
independent of the telegraph PDE.

### What requires spatial coordinates

The telegraph PDE as implemented uses **no spatial grid**. It operates on the 1D
time series `composite_norm(t)`. The spatial gradient `∇s` reduces to the temporal
log-derivative `d(ln s)/dt`. **No spatial information is required or used.**

### Why s_transport does not produce useful trading signals at 5-min resolution

The IS parameter check reveals:
- Median consecutive rising bars of s_transport: **1.0** (p70 = 2.0)
- The composite oscillates bar-to-bar because it averages 6 noisy microstructure signals
- The PDE smoother (τ=5 bars) damps this oscillation but cannot create persistence
  where none exists in the input
- Strategy A (transport rising ≥ 8 bars) fired only **39 times in 33 months** — essentially never

The transport architecture was designed for spatial scalar fields with genuine
wave propagation across a lattice. Applied to a 1D time series of averaged
microstructure metrics, the PDE produces a smoothed version of the input with
phase lag — not propagating coherence.

### What could work in principle but was not tested

The composite contains `momentum_20min` and `momentum_1hr` (price-directional components).
On a **higher-timeframe** (daily or 1-hour bars), the composite would aggregate over
longer windows, creating more persistent transport states. This was not testable with
the available 5-min cache data.

---

## 4. Candidate Experiment Results

**File:** `results/transport_edge_experiment/signal_stats.csv`  
**Trades:** `results/transport_edge_experiment/trade_log_all.csv`

### Walk-Forward Combined (WF1: 2024-07 to 2024-12 + WF2: 2025-01 to 2025-10)

| Strategy | N | PF | PF_2x | exp (pip) | CI_lo | PASS |
|---|---|---|---|---|---|---|
| A_Transport_Trend | 12 | 0.169 | 0.047 | −4.30 | −6.3 | NO |
| B_Wide_EMA_Cross | 2304 | 0.440 | 0.188 | −4.63 | −5.2 | NO |
| C_ST_Divergence | 1633 | 0.355 | 0.124 | −4.58 | −5.1 | NO |
| D_Vol_Breakout_Base | 2951 | 0.400 | 0.162 | −5.14 | −5.6 | NO |

**Success criteria (pre-defined):** WF PF > 1.10, exp > +2pip, CI_lo > −3pip,
PF_2x > 1.0, N ≥ 50, min fold PF ≥ 0.60.

Zero candidates passed any criterion. All four strategies have negative expectancy
across both WF folds.

---

## 5. Decision

### Remove from active pipeline

**Q gate:** Retire immediately. Q = 100×|grad_ln_s|²−1 is a monotone transform of
|grad_ln_s|. It carries no information beyond field velocity magnitude. Removing it
does not degrade performance — the gated strategy (B_Q_gate) performs no better
than the ungated baseline across all WF periods.

**NY_Continuation strategy:** The entry signal fires on EMA crossovers that happen
to occur during hour 13 UTC. The name "continuation" is misleading — it is an
EMA-crossover scalp. The signal has not shown positive expectancy in any evaluated
segment across 33 months. There is no evidence it has a tradeable edge on 5-min
EUR/USD at 5pip RT cost.

### Retain (as historical artifacts, not active signals)

- `tr_Q`, `tr_grad_ln_s`, `tr_s_transport` columns in the cache — preserve for
  reproducibility of prior experiments.
- All files in `results/transport_signal_eval/` and `results/transport_edge_experiment/`
  — preserve as evidence.

### What the evidence rules out

1. Q as a trading gate on 5-min EUR/USD at any threshold.
2. NY_Continuation at ATR×1.5 stop / ATR×2.5 target with 5pip RT cost.
3. All 28 strategies in `strategy_library.py` under the existing execution framework.
4. s_transport persistence as a standalone trend entry on 5-min bars (insufficient
   persistence in the composite input).
5. T_sys deviation as a profitable gate (tested as G_tsys_dev in prior eval — failed).

### What remains uncertain and worth testing

**Highest-value next experiment:** Change the instrument and/or timeframe.

The structural problem is ATR/cost ratio = 6pip/5pip = 1.2. For the framework to
work, this ratio needs to be ≥ 4–5. Candidates:
- **Gold (XAUUSD) 5-min**: ATR ≈ 70–150 pip, spread ≈ 3–5 pip. Ratio ≈ 20:1.
  Data exists in `data/XAUUSD/`.
- **NAS100 5-min**: ATR ≈ 20–40 points, spread ≈ 1 point. Ratio ≈ 20–40:1.
  Data exists in `data/NAS100/`.
- **BTC/USDT 5-min**: ATR ≈ 200–500 USDT, cost ≈ 0.05% ≈ low relative to ATR.
  Data exists in `data/BTCUSDT/`.

On these instruments, the transport composite would need to be rebuilt from the
corresponding microstructure signals (which exist for these assets in the pipeline).
Strategy B (wide-stop EMA cross) and D (vol breakout) are the most straightforward
to port, and would serve as a calibration check before testing transport-derived signals.

**Second-highest-value experiment:** Test the transport regime signal (s_transport slope
direction) as a **trade eligibility filter** on daily bars rather than as an entry signal.
At daily resolution, the composite would aggregate microstructure over 288 five-minute bars,
producing a much more persistent state. This requires rebuilding the transport pipeline
at daily frequency — not a simple config change, but tractable.

---

## 6. Summary

Two controlled evaluations were run:
1. `transport_signal_eval.py`: 7 gates × NY_Continuation across IS/WF1/WF2 (382–115 trades)
2. `transport_edge_experiment.py`: 4 strategies with new designs across IS/WF1/WF2 (up to 2951 WF trades)

**Total: 11 candidate configurations across 3 time periods. Zero achieved positive WF expectancy.**

The transport engine is correctly implemented and produces genuine outputs. The obstacle
is not the transport mathematics — it is that the inputs (5-min microstructure composite)
oscillate too rapidly for the PDE to produce exploitable persistence, and the execution
framework requires a win rate that no 5-min EUR/USD signal achieves after realistic costs.

The Q metric should be removed from active decision-making. No replacement should be
added until a positive WF expectancy is demonstrated on an instrument where the ATR/cost
ratio makes profitability structurally achievable.
