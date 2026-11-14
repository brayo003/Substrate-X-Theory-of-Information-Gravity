# Phase 4 — Transport Scheduler Report
**Generated:** 2026-07-22T04:08:22Z

## Transport as Scheduler
Q determines regime. Regime selects execution family. The scheduler is the mapping: Q → regime → family → execution. This report documents whether the scheduler is universal or market-specific.

---
## Regime-Level Family Convergence

| regime | most_common_family | n_markets_using | n_no_trade | n_markets_total | family_diversity | families_seen |
| --- | --- | --- | --- | --- | --- | --- |
| Deep_Incoherent | Scalping | 2 | 1 | 7 | 6 | Scalping, NoTrade, Volatility, MeanReversion, Session, Momentum |
| Mod_Incoherent | NoTrade | 3 | 3 | 7 | 4 | NoTrade, PassiveLiquidity, Momentum, Trend |
| Transition | NoTrade | 5 | 5 | 7 | 3 | NoTrade, Trend, MeanReversion |
| Weak_Coherent | NoTrade | 5 | 5 | 7 | 3 | NoTrade, MeanReversion, Session |
| Strong_Coherent | MeanReversion | 3 | 1 | 7 | 5 | MeanReversion, NoTrade, Scalping, Volatility, Trend |


## Scheduler Similarity

Average pairwise scheduler similarity: **0.267**

A value near 1.0 implies universal scheduler. Near 0.0 implies fully market-specific.
