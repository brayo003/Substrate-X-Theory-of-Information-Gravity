# SXC-IGC Transport Regime Validation V2

## Phase I — Regime Persistence

- P(stay COHERENT)   = **0.212**
- P(stay INCOHERENT) = **0.849**
- Mean COHERENT run  = **1.3 bars (6 min)**
- Mean INCOHERENT run= **6.6 bars**
- Verdict: **PERSISTENT**

---

## Phase II — Volatility Cluster Origin

- N transition events = 1058
- Pre-event ATR (norm) = 1.000
- Post-event ATR (norm)= 1.217
- Vol expansion ratio  = **1.217**
- MW p-value           = 0.0000
- Statistically significant: True

---

## Phase III — Lead/Lag vs Existing Indicators

| indicator      | description   |   n_paired |   mean_lead_bars |   median_lead_bars |   std_lead_bars |   mean_lead_min |   pct_Q_leads |
|:---------------|:--------------|-----------:|-----------------:|-------------------:|----------------:|----------------:|--------------:|
| ADX_14         | ADX>75pct     |        975 |       -0.0328205 |                  0 |         20.6816 |       -0.164103 |      0.498462 |
| ATR_14         | ATR>75pct     |        701 |       -0.308131  |                  0 |         22.3895 |       -1.54066  |      0.473609 |
| HistVol_20     | HV>75pct      |        685 |       -0.483212  |                  0 |         22.2461 |       -2.41606  |      0.445255 |
| BollWidth_20   | BW>75pct      |        871 |       -2.46613   |                 -3 |         21.4826 |      -12.3307   |      0.428243 |
| RealizedVol_20 | RV20>75pct    |        685 |       -0.483212  |                  0 |         22.2461 |       -2.41606  |      0.445255 |

---

## Phase IV — Strategy Suitability Matrix

| strategy      | best_regime   |   coherent_pf |   incoherent_pf |   pf_difference |   coherent_sharpe |   incoherent_sharpe |   sharpe_difference |
|:--------------|:--------------|--------------:|----------------:|----------------:|------------------:|--------------------:|--------------------:|
| EMA_Trend     | COHERENT      |      0.797867 |        0.529668 |       0.2682    |         -0.759222 |            -3.85183 |           3.0926    |
| MeanReversion | INCOHERENT    |      0.519075 |        0.603404 |      -0.0843295 |         -2.98072  |            -2.99751 |           0.0167962 |
| Breakout      | INCOHERENT    |      0.492664 |        0.839359 |      -0.346694  |         -4.2493   |            -1.3541  |          -2.8952    |
| VolCompBreak  | INCOHERENT    |      0.334973 |        0.412797 |      -0.0778239 |         -2.62652  |            -5.32869 |           2.70217   |

---

## Phase V — Position Sizing

| label       |    n |   total_ret |      avg_ret |       pf |   sharpe |    max_dd |   win_rate |
|:------------|-----:|------------:|-------------:|---------:|---------:|----------:|-----------:|
| FLAT_100pct | 3169 |   -0.471774 | -0.000199865 | 0.631142 | -6.46427 | -0.471487 |   0.273588 |
| Q_SIZED     | 3169 |   -0.310377 | -0.000116834 | 0.58429  | -7.14727 | -0.309914 |   0.273588 |

---

## Phase VI — Risk Management

| Q_bucket   |    n |   stop_rate |   target_rate |   avg_reward |     avg_loss |       pf |   avg_rr |
|:-----------|-----:|------------:|--------------:|-------------:|-------------:|---------:|---------:|
| deep       | 2046 |    0.559629 |      0.435484 |  0.000388842 | -0.000514021 | 0.43227  |      1.5 |
| high       |  327 |    0.51682  |      0.155963 |  0.00118389  | -0.00103651  | 0.603117 |      2   |
| low        |  460 |    0.569565 |      0.369565 |  0.000548349 | -0.000677617 | 0.534618 |      1.5 |
| med        |  336 |    0.520833 |      0.223214 |  0.0010228   | -0.000911345 | 0.583999 |      2   |

---

## Phase VII — Execution Quality

- MW spread p-value (COHERENT vs INCOHERENT): 0.0000
| regime     |   n_bars |   mean_spread |   median_spread |   p95_spread |   mean_vol_norm |    mean_iae |   median_iae |
|:-----------|---------:|--------------:|----------------:|-------------:|----------------:|------------:|-------------:|
| COHERENT   |     1351 |      0.668811 |        0.44045  |      2.20856 |         1.28812 | 0.000442771 |   0.00028491 |
| INCOHERENT |     7036 |      0.601413 |        0.430225 |      1.57775 |         1.02721 | 0.000197693 |   0.00013    |

---

## Phase VIII — Microstructure

- N transitions: 2128
- INCOH→COH spread ratio (post/pre): 0.925
- COH→INCOH spread ratio (post/pre): 0.916

---

## Phase IX — Explainability

See explainability_reports.csv for per-transition human-readable reports.

---

## Phase X — Practical Value Assessment

| capability             | rating   |   effect_size | evidence                                                                     |
|:-----------------------|:---------|--------------:|:-----------------------------------------------------------------------------|
| strategy_selection     | Weak     |  -0.060162    | Mean PF diff (coh-incoh) = -0.060 across 4 strategies                        |
| position_sizing        | None     |  -0.046852    | Q-sized PF - flat PF = -0.047                                                |
| risk_management        | Moderate |   0.170848    | PF(high-Q) - PF(deep-Q) = 0.171                                              |
| execution              | Moderate |   0.999991    | MW spread COHERENT vs INCOHERENT p=0.0000                                    |
| volatility_forecasting | Strong   |   0.217221    | Post/pre ATR ratio=1.217, MW p=0.0000, n_events=1058                         |
| trade_filtering        | None     |  -0.000118964 | Mean ret COHERENT - INCOHERENT = -0.00012                                    |
| portfolio_allocation   | None     |   0           | P(stay coherent) = 0.000; regime persistence enables regime-aware allocation |

**Average score: 1.14 / 4.0**

## Final Scientific Conclusion

**Verdict A: Q is only another technical indicator.**

### Supporting evidence:
- Regime persistence: P(stay coherent) = 0.212
- Volatility prediction: expansion ratio = 1.217
- Strategy differentiation: mean PF diff = -0.060
- Execution: MW spread p = 0.0000