# Strategy Allocator Report — Phase 1 Transport Validation (EUR/USD)

## Methodology
Best strategy per regime selected by composite score:
  composite = 0.4×PF + 0.3×Sharpe + 0.2×WinRate + 0.1×Expectancy
  All scores normalised globally. +20% bonus for FDR-significant strategies.
  Minimum 10 trades required for eligibility.

## Q Quantile Thresholds (global, from full dataset)
  Q05 (Deep_Incoherent boundary): -0.997996
  Q95 (Strong_Coherent boundary): 1.732289
  Total bars analysed: 209,689
  Coherent fraction: 0.2012

## Best Strategy Per Regime

Regime                 Strategy                     Family               PF   Sharpe     WR     N Confidence
--------------------------------------------------------------------------------------------------------------
Deep_Incoherent        NO_TRADE                     —                 0.426  -53.055  0.324   463  Weak
Mod_Incoherent         NO_TRADE                     —                 0.396  -57.548  0.323  7008  Weak
Transition             NO_TRADE                     —                 0.437  -49.638  0.341    41  Weak
Weak_Coherent          NO_TRADE                     —                 0.405  -56.391  0.329  1659  Weak
Strong_Coherent        NY_Continuation              Session           0.946   -3.495  0.500    44  Unsupported

## Regime Stability Summary

  Total bars      : 210,505
  Entropy         : 1.1853 bits (normalised: 0.510)
  Transitions/hr  : 4.8481

  Regime                 Fraction  Mean bars  P(stay)
  -------------------------------------------------------
  Deep_Incoherent          0.0498       1.06   0.0562
  Mod_Incoherent           0.7478       4.08   0.7551
  Transition               0.0040       1.01   0.0059
  Weak_Coherent            0.1486       1.20   0.1634
  Strong_Coherent          0.0498       1.09   0.0851

## Statistical Significance

Strategy                       MW p (raw)   MW p (FDR)   Sig    Cohen d
---------------------------------------------------------------------------
Donchian_Trend                     0.0098       0.1075    no      0.294
Turtle_Breakout                    0.0098       0.1075    no      0.294
ATR_Expansion                      0.0125       0.1167    no      0.867
EMA_Micro_Trend                    0.0154       0.1075    no      0.169
Volatility_Contraction             0.0378       0.2116    no      0.414
ZScore_Reversion                   0.0399       0.1075    no      0.246
Volatility_Scalp                   0.0567       0.1167    no      0.256
EMA_Crossover                      0.0687       0.1075    no      0.070
ROC_Momentum                       0.0807       0.1075    no      0.117
Supertrend                         0.0920       0.1075    no      0.077
VWAP_Scalp                         0.1029       0.1167    no      0.184
RSI_Reversal                       0.1178       0.1075    no      0.210
ATR_Breakout                       0.1180       0.1075    no      0.135
Keltner_Reversion                  0.1314       0.1075    no      0.139
Squeeze_Expansion                  0.1670       0.3047    no      0.153
RSI_Momentum                       0.1688       0.1075    no      0.085
London_Breakout                    0.1850       0.3047    no      0.168
ADX_Trend                          0.2060       0.1075    no      0.071
Donchian_Breakout                  0.2107       0.1075    no      0.110
SMA_Crossover                      0.2302       0.1075    no      0.084
CCI_Momentum                       0.2519       0.1075    no      0.065
Bollinger_Reversion                0.2626       0.1075    no      0.112
Bollinger_Squeeze_Breakout         0.2908       0.1075    no      0.056
NY_Continuation                    0.3615       0.4218    no      0.270
Asian_Range                        0.3870       0.4334    no      0.052
MACD_Trend                         0.4022       0.1075    no      0.032
VWAP_Reversion                     0.4110       0.1075    no      0.075
Stochastic_Momentum                0.5811       0.1075    no      0.015
Range_Breakout                        N/A          N/A    no        N/A

## Conclusions

1. 0/29 strategies show statistically significant regime-dependent performance (FDR p<0.05).
2. 4 regime(s) designated NO_TRADE: Deep_Incoherent, Mod_Incoherent, Transition, Weak_Coherent.
3. Top overall strategy: NY_Continuation (Session) — mean score 0.1269, best in Strong_Coherent.
