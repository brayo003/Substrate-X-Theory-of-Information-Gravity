# Phase 4 — Passive Liquidity Report
**Generated:** 2026-07-22T04:08:22Z

## Overview
Transport-Aware Passive Liquidity Provision is evaluated as the 8th strategy family. Five strategies (PL_TightQuote, PL_WideQuote, PL_RegimeAdaptive, PL_AntiAdverse, PL_InventorySkew) use Q and regime labels to govern quote aggressiveness. No preferential treatment — evaluated identically to all other families.

---

## PL vs Field (Median PF per Market × Regime)

| symbol | regime | pl_median_pf | other_median_pf | pl_vs_other_diff | pl_wins | best_other_family | mw_p |
| --- | --- | --- | --- | --- | --- | --- | --- |
| EURUSD | Mod_Incoherent | 0.390 | 0.385 | 0.005 | 1 | Session | 0.720 |
| EURUSD | Transition | 0.000 | 0.354 | -0.354 | 0 | MeanReversion | nan |
| EURUSD | Weak_Coherent | 0.000 | 0.402 | -0.402 | 0 | Session | nan |
| EURUSD | Strong_Coherent | 0.000 | 0.449 | -0.449 | 0 | Session | nan |
| BTCUSDT | Deep_Incoherent | 0.984 | 0.976 | 0.008 | 1 | Volatility | 0.804 |
| BTCUSDT | Mod_Incoherent | 1.095 | 0.881 | 0.214 | 1 | Momentum | 0.082 |
| BTCUSDT | Transition | 0.000 | 0.705 | -0.705 | 0 | Trend | nan |
| BTCUSDT | Weak_Coherent | 0.000 | 0.850 | -0.850 | 0 | MeanReversion | nan |
| BTCUSDT | Strong_Coherent | 0.000 | 1.021 | -1.021 | 0 | Scalping | nan |
| ETHUSDT | Deep_Incoherent | 0.974 | 1.011 | -0.037 | 0 | Scalping | 0.181 |
| ETHUSDT | Mod_Incoherent | 0.998 | 0.941 | 0.056 | 1 | Momentum | 0.476 |
| ETHUSDT | Transition | 0.000 | 1.591 | -1.591 | 0 | MeanReversion | nan |
| ETHUSDT | Weak_Coherent | 0.000 | 1.060 | -1.060 | 0 | Session | nan |
| ETHUSDT | Strong_Coherent | 0.000 | 1.000 | -1.000 | 0 | MeanReversion | nan |
| XAUUSD | Deep_Incoherent | 4.749 | 0.301 | 4.448 | 1 | MeanReversion | 0.183 |
| XAUUSD | Mod_Incoherent | 1.339 | 1.286 | 0.053 | 1 | Momentum | nan |
| XAUUSD | Strong_Coherent | 0.000 | 1.567 | -1.567 | 0 | Volatility | nan |
| NAS100 | Deep_Incoherent | 0.450 | 0.797 | -0.347 | 0 | Scalping | 0.267 |
| NAS100 | Mod_Incoherent | 0.000 | 0.913 | -0.913 | 0 | Trend | nan |
| NAS100 | Strong_Coherent | 0.000 | 0.892 | -0.892 | 0 | Trend | nan |
| USOIL | Deep_Incoherent | 0.914 | 1.017 | -0.102 | 0 | Session | 1.000 |
| USOIL | Strong_Coherent | 0.000 | 0.957 | -0.957 | 0 | MeanReversion | nan |
| UKOIL | Deep_Incoherent | 0.925 | 0.967 | -0.042 | 0 | Momentum | 0.670 |
| UKOIL | Strong_Coherent | 0.000 | 1.141 | -1.141 | 0 | MeanReversion | nan |


---

## Where PL Outperforms
PL beats the field in 6 out of 24 (market, regime) cells.

| symbol | regime | pl_median_pf | best_other_family | pl_vs_other_diff |
| --- | --- | --- | --- | --- |
| EURUSD | Mod_Incoherent | 0.390 | Session | 0.005 |
| BTCUSDT | Deep_Incoherent | 0.984 | Volatility | 0.008 |
| BTCUSDT | Mod_Incoherent | 1.095 | Momentum | 0.214 |
| ETHUSDT | Mod_Incoherent | 0.998 | Momentum | 0.056 |
| XAUUSD | Deep_Incoherent | 4.749 | MeanReversion | 4.448 |
| XAUUSD | Mod_Incoherent | 1.339 | Momentum | 0.053 |


---

## Passive Liquidity Trade Statistics
| strategy | n_trades | win_rate | mean_ret | total_return |
| --- | --- | --- | --- | --- |
| PL_AntiAdverse | 23626 | 0.362 | -0.000 | -4.287 |
| PL_InventorySkew | 28019 | 0.376 | -0.000 | -3.365 |
| PL_RegimeAdaptive | 23611 | 0.364 | -0.000 | -4.263 |
| PL_TightQuote | 11906 | 0.344 | -0.000 | -2.555 |
| PL_WideQuote | 11683 | 0.391 | -0.000 | -0.428 |

