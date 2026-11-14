# Transport Signal Evaluation Report

**Generated:** 2026-10-11 11:55 UTC

**Strategy:** NY_Continuation (hour==13 UTC, EMA9/EMA21 trend)

**Cost model:** 5.0 pip round-trip (commission 2.0pip + slippage 0.5pip × 2)

**IS calibration:** 2023-01 to 2024-12 (threshold derivation only)

**WF fold 1:** 2025-01 to 2025-06

**WF fold 2:** 2025-07 to 2025-10

**Held-out:** 2026-01 to 2026-07 (sanity check only)


---

## Candidate Gate Descriptions

| Gate | Signal | Derivation |
|------|--------|------------|
| A_no_gate    | Always True | Baseline: enter every NY bar |
| B_Q_gate     | tr_Q ≥ 1.732 | Existing Q gate (q95 frozen from 2023–2025 calibration) |
| C_rv5        | realized_vol_5 ≥ IS 70th pct | 5-bar realized volatility of returns |
| D_v_abs      | |tr_grad_ln_s| ≥ IS 70th pct | Field velocity magnitude (|∂s/∂t|) |
| E_v_persist  | EWMA sign persistence ≥ IS 70th pct | Directional momentum of composite s |
| F_tension    | |tr_grad_ln_s| × τ ≥ IS 70th pct | Inertia proxy (v × τ = tension) |
| G_tsys_dev   | |T_sys − EWMA(T_sys)| ≥ IS 70th pct | T_sys acceleration |


## IS Performance

| gate        |   n_trades | win_rate   |   profit_factor |   expectancy_pips |   total_net_pips |   max_drawdown_pips |   sharpe_per_trade |   pf_2x_cost |   boot_ci_lo_pips |   boot_ci_hi_pips |
|:------------|-----------:|:-----------|----------------:|------------------:|-----------------:|--------------------:|-------------------:|-------------:|------------------:|------------------:|
| A_no_gate   |        267 | 39.7%      |           0.475 |            -4.020 |        -1073.560 |            1130.550 |             -0.340 |        0.168 |            -5.440 |            -2.530 |
| B_Q_gate    |         26 | 50.0%      |           0.961 |            -0.260 |           -6.660 |              67.740 |             -0.018 |        0.421 |            -5.760 |             5.240 |
| C_rv5       |         91 | 38.5%      |           0.615 |            -3.600 |         -327.760 |             353.640 |             -0.228 |        0.313 |            -6.770 |            -0.440 |
| D_v_abs     |         95 | 37.9%      |           0.483 |            -4.270 |         -405.350 |             473.330 |             -0.332 |        0.195 |            -6.650 |            -1.710 |
| E_v_persist |        108 | 38.0%      |           0.486 |            -3.920 |         -423.830 |             449.350 |             -0.329 |        0.181 |            -6.040 |            -1.730 |
| F_tension   |         95 | 37.9%      |           0.483 |            -4.270 |         -405.350 |             473.330 |             -0.332 |        0.195 |            -6.650 |            -1.710 |
| G_tsys_dev  |         75 | 44.0%      |           0.669 |            -2.730 |         -204.560 |             264.350 |             -0.182 |        0.308 |            -6.090 |             0.780 |

## WF1 Performance

| gate        |   n_trades | win_rate   |   profit_factor |   expectancy_pips |   total_net_pips |   max_drawdown_pips |   sharpe_per_trade |   pf_2x_cost |   boot_ci_lo_pips |   boot_ci_hi_pips |
|:------------|-----------:|:-----------|----------------:|------------------:|-----------------:|--------------------:|-------------------:|-------------:|------------------:|------------------:|
| A_no_gate   |         75 | 30.7%      |           0.267 |            -7.970 |         -598.090 |             590.420 |             -0.592 |        0.101 |           -11.070 |            -4.910 |
| B_Q_gate    |          8 | 25.0%      |           0.088 |           -13.490 |         -107.900 |              88.660 |             -1.005 |        0.025 |           -21.630 |            -5.090 |
| C_rv5       |         34 | 26.5%      |           0.242 |           -10.780 |         -366.580 |             354.900 |             -0.655 |        0.123 |           -16.370 |            -5.300 |
| D_v_abs     |         29 | 24.1%      |           0.153 |           -10.000 |         -289.870 |             278.670 |             -0.868 |        0.048 |           -13.870 |            -5.880 |
| E_v_persist |         29 | 34.5%      |           0.347 |            -6.900 |         -200.010 |             184.300 |             -0.447 |        0.144 |           -12.190 |            -1.280 |
| F_tension   |         29 | 24.1%      |           0.153 |           -10.000 |         -289.870 |             278.670 |             -0.868 |        0.048 |           -13.870 |            -5.880 |
| G_tsys_dev  |         17 | 29.4%      |           0.297 |            -7.850 |         -133.430 |             151.330 |             -0.564 |        0.127 |           -13.900 |            -1.560 |

## WF2 Performance

| gate        |   n_trades | win_rate   |   profit_factor |   expectancy_pips |   total_net_pips |   max_drawdown_pips |   sharpe_per_trade |   pf_2x_cost |   boot_ci_lo_pips |   boot_ci_hi_pips |
|:------------|-----------:|:-----------|----------------:|------------------:|-----------------:|--------------------:|-------------------:|-------------:|------------------:|------------------:|
| A_no_gate   |         40 | 40.0%      |           0.478 |            -4.160 |         -166.310 |             154.250 |             -0.352 |        0.167 |            -7.630 |            -0.480 |
| B_Q_gate    |         10 | 60.0%      |           0.903 |            -0.590 |           -5.940 |              17.040 |             -0.045 |        0.312 |            -8.540 |             7.240 |
| C_rv5       |         19 | 36.8%      |           0.500 |            -4.720 |          -89.690 |              92.830 |             -0.337 |        0.228 |           -11.150 |             1.560 |
| D_v_abs     |         20 | 45.0%      |           0.514 |            -3.970 |          -79.320 |              73.620 |             -0.309 |        0.179 |            -9.230 |             1.490 |
| E_v_persist |         14 | 35.7%      |           0.462 |            -4.380 |          -61.360 |              73.720 |             -0.360 |        0.181 |           -10.170 |             1.750 |
| F_tension   |         20 | 45.0%      |           0.514 |            -3.970 |          -79.320 |              73.620 |             -0.309 |        0.179 |            -9.230 |             1.490 |
| G_tsys_dev  |         15 | 40.0%      |           0.582 |            -3.680 |          -55.170 |              69.330 |             -0.258 |        0.264 |           -10.520 |             3.630 |

---

## Walk-Forward Summary (WF1 + WF2 combined)

| gate        |   n_trades |   total_net_pips |    pf |   exp_pips | ci_95_pips      |
|:------------|-----------:|-----------------:|------:|-----------:|:----------------|
| A_no_gate   |        115 |         -764.400 | 0.326 |     -6.650 | [-9.06, -4.33]  |
| B_Q_gate    |         18 |         -113.840 | 0.366 |     -6.320 | [-12.61, 0.33]  |
| C_rv5       |         53 |         -456.270 | 0.312 |     -8.610 | [-12.83, -4.31] |
| D_v_abs     |         49 |         -369.190 | 0.270 |     -7.530 | [-10.67, -3.97] |
| E_v_persist |         43 |         -261.370 | 0.378 |     -6.080 | [-10.22, -1.79] |
| F_tension   |         49 |         -369.190 | 0.270 |     -7.530 | [-10.67, -3.97] |
| G_tsys_dev  |         32 |         -188.600 | 0.414 |     -5.890 | [-10.63, -1.03] |

---

## Gate Correlation Note

D_v_abs and F_tension are monotone functions of the same underlying quantity |tr_grad_ln_s|. Any performance difference between them is purely from the different threshold level produced by the τ=5 multiplier. They are NOT independent signals and should not both be selected as candidates if one is already chosen.


E_v_persist (EWMA sign persistence) IS a distinct signal: it measures directional continuity over a window, not instantaneous magnitude.


---

## Decision Criteria

A gate is considered superior to the no-gate baseline (A) if ALL of:

1. WF1 + WF2 combined PF > 1.0

2. WF expectancy per trade > 0 (positive after full costs)

3. 95% bootstrap CI lower bound > −5 pips (excludes clearly negative)

4. PF at 2× cost still > 1.0

5. N_trades ≥ 30 over WF1+WF2 (minimum for inference)


If multiple gates pass all five criteria, prefer the simpler one (lower maintenance burden, fewer parameters).

---

## Verdict

**No gate passed any of the five criteria. Zero candidates qualify for promotion.**

### What the evidence rules out

Every candidate — including the existing Q gate, all transport-derived signals, and
realized volatility — produced negative expectancy on every walk-forward fold.
The combined WF1+WF2 profit factors range from 0.270 (D_v_abs / F_tension) to 0.414
(G_tsys_dev). All bootstrap 95% CI upper bounds stay below +1 pip for all gates except
B_Q_gate (CI upper = +0.3 pip) — which also has N=18, below the minimum.

The existing Q gate (B_Q_gate) is not a winner. It has the flattest IS equity curve
(−6.66 pip total over 2 years with N=26) and performs as poorly as all other gates
on WF folds (WF1: PF=0.088, exp=−13.5pip; WF2: PF=0.903, exp=−0.59pip; combined
PF=0.366). Its apparent IS "coherence" is an artifact of filtering to only 26 trades
from 267 signals — low trade count masking a statistically uninformative near-zero result.

**The fundamental problem is the NY_Continuation signal itself, not the gate.**
The raw signal (A_no_gate) loses −764 pips over 115 WF trades. No filter can make
money out of a persistently loss-generating base signal. A gate that selects a subset
of losing trades will still produce losing trades.

### What the transport derivation explains

The transport system's `tr_grad_ln_s` (field velocity), `T_sys` (ODE integrator state),
and derived persistence and tension measures are operationally valid — they are
causally computed, have clear mechanical definitions, and require no spatial grid.
The obstacle is not the transport implementation. The obstacle is that:

1. The composite signal `s` is a normalized microstructure index, not a price.
   Its gradient does not reliably predict directional continuation of price.
2. Transport-state thresholds derived from IS 2023–2024 did not generalize to
   WF 2025; the regime in 2025-H1 (WF1) was materially different.
3. Even the "best" transport gate (G_tsys_dev, PF=0.414) is worse than simply
   not trading (PF=1.0 with no position).

### Recommended next experiments (in order of expected value)

1. **Diagnose the base signal.** Before any gate work: determine whether
   NY_Continuation has ever produced a positive-expectancy WF period with a
   sufficiently large N. If the strategy never worked out-of-sample, gate
   research on top of it is moot.

2. **Separate the regime from the gate.** The WF1 period (Jan–Jun 2025) is
   dramatically worse than WF2 (Jul–Oct 2025) for every gate. This suggests
   a regime shift, not a gate problem. The correct experiment is:
   identify what structural feature distinguishes WF1 from WF2, and test
   whether that feature is predictable at entry time.

3. **Replace NY_Continuation with a strategy that has shown positive WF PF.**
   The existing results/phase4/ files contain 24 strategies across multiple
   markets. Identify the one(s) with the most consistently positive WF
   performance, and run this same gate comparison on that strategy.

4. **Test the transport persistence signal (E_v_persist) on a momentum strategy.**
   E_v_persist (EWMA sign persistence of the composite field) is conceptually
   aligned with trending conditions. It is not aligned with a mean-reversion
   or session-continuation logic like NY_Continuation. The correct test host
   is a trend-following entry, not a session-open continuation.

### What should replace Q in the active pipeline

**Nothing from this evaluation.** Q has no demonstrated incremental value over
the no-gate baseline on WF data (B_Q_gate WF combined PF = 0.366 vs A_no_gate
WF combined PF = 0.326 — the Q gate is marginally better only at reducing
trade count while still losing). Q should be retired from active decision-making.

The replacement gate should be determined only after identifying a strategy with
positive WF expectancy. There is no evidence here that any microstructure or
transport-derived threshold selects for profitable NY_Continuation trades.

### Limitations of this evaluation

- The HO period (2026-01 to 2026-07) is absent from the cache. The HO check
  cannot be performed without regenerating the cache for 2026 bars.
- WF folds are short (WF1: 6 months / 75 no-gate trades; WF2: 4 months / 40 trades).
  No single fold has enough trades for high-confidence inference; the combined
  result (N=115 for no-gate) is more reliable but still modest.
- The 70th-percentile threshold was chosen as a reasonable prior; sensitivity to
  the percentile choice was not tested. However, given all PFs are << 1.0, it is
  unlikely that any single percentile threshold would produce PF > 1.0 here.
