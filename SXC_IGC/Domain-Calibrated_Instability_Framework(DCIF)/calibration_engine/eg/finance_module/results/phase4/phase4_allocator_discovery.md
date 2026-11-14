# Phase 4 — Allocator Discovery Report
**Generated:** 2026-07-22T04:08:22Z  **Elapsed:** 49.6s

## Objective
Discover the natural execution policy that emerges from the transport kernel for each market, without transferring or reusing the EUR/USD allocator. Transport is IMMUTABLE. Allocation is discovered from measured statistics.

---

## Cross-Market Allocator (Best Family per Market × Regime)

| Market | Deep_Incoherent | Mod_Incoherent | Transition | Weak_Coherent | Strong_Coherent |
| --- | --- | --- | --- | --- | --- |
| EURUSD | NoTrade | NoTrade | NoTrade | NoTrade | NoTrade |
| BTCUSDT | Volatility | PassiveLiquidity | Trend | MeanReversion | Scalping |
| ETHUSDT | Scalping | Momentum | MeanReversion | Session | MeanReversion |
| XAUUSD | MeanReversion | PassiveLiquidity | NoTrade | NoTrade | Volatility |
| NAS100 | Scalping | Trend | NoTrade | NoTrade | Trend |
| USOIL | Session | NoTrade | NoTrade | NoTrade | MeanReversion |
| UKOIL | Momentum | NoTrade | NoTrade | NoTrade | MeanReversion |


---

## Detailed Allocator by Market

### EURUSD
| regime | best_family | best_strategy | profit_factor | sharpe | trade_count | confidence |
| --- | --- | --- | --- | --- | --- | --- |
| Deep_Incoherent | NoTrade | NO_TRADE | 0.000 | 0.000 | 0 | Weak |
| Mod_Incoherent | NoTrade | NO_TRADE | 0.000 | 0.000 | 0 | Weak |
| Transition | NoTrade | NO_TRADE | 0.000 | 0.000 | 0 | Weak |
| Weak_Coherent | NoTrade | NO_TRADE | 0.000 | 0.000 | 0 | Weak |
| Strong_Coherent | NoTrade | NO_TRADE | 0.000 | 0.000 | 0 | Weak |


### BTCUSDT
| regime | best_family | best_strategy | profit_factor | sharpe | trade_count | confidence |
| --- | --- | --- | --- | --- | --- | --- |
| Deep_Incoherent | Volatility | ATR_Expansion | 1.058 | 0.425 | 383 | Moderate |
| Mod_Incoherent | PassiveLiquidity | PL_TightQuote | 1.226 | 2.100 | 681 | High |
| Transition | Trend | MACD_Trend | 3.881 | 1.326 | 5 | Moderate |
| Weak_Coherent | MeanReversion | Bollinger_Reversion | 1.678 | 2.277 | 117 | High |
| Strong_Coherent | Scalping | Volatility_Scalp | 1.113 | 1.850 | 1699 | Moderate |


### ETHUSDT
| regime | best_family | best_strategy | profit_factor | sharpe | trade_count | confidence |
| --- | --- | --- | --- | --- | --- | --- |
| Deep_Incoherent | Scalping | VWAP_Scalp | 1.116 | 1.488 | 1237 | Moderate |
| Mod_Incoherent | Momentum | RSI_Momentum | 1.181 | 1.112 | 265 | Moderate |
| Transition | MeanReversion | Keltner_Reversion | 9.588 | 2.763 | 5 | Moderate |
| Weak_Coherent | Session | London_Breakout | 2.513 | 1.168 | 8 | Moderate |
| Strong_Coherent | MeanReversion | Bollinger_Reversion | 1.075 | 1.447 | 2300 | Moderate |


### XAUUSD
| regime | best_family | best_strategy | profit_factor | sharpe | trade_count | confidence |
| --- | --- | --- | --- | --- | --- | --- |
| Deep_Incoherent | MeanReversion | RSI_Reversal | 99.000 | 8.289 | 6 | Moderate |
| Mod_Incoherent | PassiveLiquidity | PL_TightQuote | 2.442 | 1.000 | 7 | Moderate |
| Transition | NoTrade | NO_TRADE | 0.000 | 0.000 | 0 | Weak |
| Weak_Coherent | NoTrade | NO_TRADE | 0.000 | 0.000 | 0 | Weak |
| Strong_Coherent | Volatility | Volatility_Contraction | 2.300 | 0.924 | 5 | Moderate |


### NAS100
| regime | best_family | best_strategy | profit_factor | sharpe | trade_count | confidence |
| --- | --- | --- | --- | --- | --- | --- |
| Deep_Incoherent | Scalping | EMA_Micro_Trend | 1.898 | 0.618 | 5 | Moderate |
| Mod_Incoherent | Trend | MACD_Trend | 1.140 | 0.139 | 5 | Moderate |
| Transition | NoTrade | NO_TRADE | 0.000 | 0.000 | 0 | Weak |
| Weak_Coherent | NoTrade | NO_TRADE | 0.000 | 0.000 | 0 | Weak |
| Strong_Coherent | Trend | Donchian_Trend | 2.830 | 1.050 | 6 | Moderate |


### USOIL
| regime | best_family | best_strategy | profit_factor | sharpe | trade_count | confidence |
| --- | --- | --- | --- | --- | --- | --- |
| Deep_Incoherent | Session | NY_Continuation | 2.489 | 1.268 | 10 | Moderate |
| Mod_Incoherent | NoTrade | NO_TRADE | 0.000 | 0.000 | 0 | Weak |
| Transition | NoTrade | NO_TRADE | 0.000 | 0.000 | 0 | Weak |
| Weak_Coherent | NoTrade | NO_TRADE | 0.000 | 0.000 | 0 | Weak |
| Strong_Coherent | MeanReversion | Bollinger_Reversion | 2.156 | 1.089 | 8 | Moderate |


### UKOIL
| regime | best_family | best_strategy | profit_factor | sharpe | trade_count | confidence |
| --- | --- | --- | --- | --- | --- | --- |
| Deep_Incoherent | Momentum | ADX_Trend | 1.955 | 0.860 | 8 | Moderate |
| Mod_Incoherent | NoTrade | NO_TRADE | 0.000 | 0.000 | 0 | Weak |
| Transition | NoTrade | NO_TRADE | 0.000 | 0.000 | 0 | Weak |
| Weak_Coherent | NoTrade | NO_TRADE | 0.000 | 0.000 | 0 | Weak |
| Strong_Coherent | MeanReversion | ZScore_Reversion | 4.905 | 1.937 | 5 | Moderate |


---

## Regime-Level Patterns (Cross-Market)

| regime | most_common_family | n_markets_using | n_no_trade | n_markets_total | family_diversity | families_seen |
| --- | --- | --- | --- | --- | --- | --- |
| Deep_Incoherent | Scalping | 2 | 1 | 7 | 6 | Scalping, NoTrade, Volatility, MeanReversion, Session, Momentum |
| Mod_Incoherent | NoTrade | 3 | 3 | 7 | 4 | NoTrade, PassiveLiquidity, Momentum, Trend |
| Transition | NoTrade | 5 | 5 | 7 | 3 | NoTrade, Trend, MeanReversion |
| Weak_Coherent | NoTrade | 5 | 5 | 7 | 3 | NoTrade, MeanReversion, Session |
| Strong_Coherent | MeanReversion | 3 | 1 | 7 | 5 | MeanReversion, NoTrade, Scalping, Volatility, Trend |


---

## Scheduler Entropy (Family Diversity per Market)

| symbol | n_families_used | entropy | norm_entropy | families |
| --- | --- | --- | --- | --- |
| EURUSD | 1 | -0.000 | 0.000 | NoTrade |
| BTCUSDT | 5 | 1.609 | 1.000 | Volatility, PassiveLiquidity, Trend, MeanReversion, Scalping |
| ETHUSDT | 4 | 1.332 | 0.961 | MeanReversion, Scalping, Momentum, Session |
| XAUUSD | 4 | 1.332 | 0.961 | NoTrade, MeanReversion, PassiveLiquidity, Volatility |
| NAS100 | 3 | 1.055 | 0.960 | Trend, NoTrade, Scalping |
| USOIL | 3 | 0.950 | 0.865 | NoTrade, Session, MeanReversion |
| UKOIL | 3 | 0.950 | 0.865 | NoTrade, Momentum, MeanReversion |


---

## Scheduler Similarity Matrix

| Market | EURUSD | BTCUSDT | ETHUSDT | XAUUSD | NAS100 | USOIL | UKOIL |
| --- | --- | --- | --- | --- | --- | --- | --- |
| EURUSD | 1.000 | 0.000 | 0.000 | 0.400 | 0.400 | 0.600 | 0.600 |
| BTCUSDT | 0.000 | 1.000 | 0.000 | 0.200 | 0.000 | 0.000 | 0.000 |
| ETHUSDT | 0.000 | 0.000 | 1.000 | 0.000 | 0.200 | 0.200 | 0.200 |
| XAUUSD | 0.400 | 0.200 | 0.000 | 1.000 | 0.400 | 0.400 | 0.400 |
| NAS100 | 0.400 | 0.000 | 0.200 | 0.400 | 1.000 | 0.400 | 0.400 |
| USOIL | 0.600 | 0.000 | 0.200 | 0.400 | 0.400 | 1.000 | 0.800 |
| UKOIL | 0.600 | 0.000 | 0.200 | 0.400 | 0.400 | 0.800 | 1.000 |

