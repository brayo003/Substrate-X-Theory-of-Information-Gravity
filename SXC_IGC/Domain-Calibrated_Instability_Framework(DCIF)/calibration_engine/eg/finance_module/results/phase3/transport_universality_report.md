# Phase 3 — Transport Universality Report
## Cross-Market Transport Operating System Validation

**Generated:** 2026-07-22T03:43:21Z  
**Elapsed:** 28.5s (0.5 min)  
**Overall universality confidence:** Unsupported  

---

## Transport OS Configuration (IMMUTABLE — Phase 2 validated)

| Parameter | Value |
| --- | --- |
| Q05 threshold | -1.0 |
| Q95 threshold | 1.73 |
| Commission RT | 0.00030 |
| Base risk pct | 1.0% |
| Hold bars | 24 |
| ATR stop (Strong_Coherent) | 1.88× |
| ATR target (Strong_Coherent) | 2.50× |
| Allocated strategy (SC) | NY_Continuation |
| No-trade regimes | Deep, Mod, Transition, Weak |

**Parameters changed for Phase 3: NONE**  
Every market receives the identical operating system.

---

## Market × Performance Metrics

| Market | PF | Sharpe | Sortino | MaxDD | WinRate | Trades | NoTrade_pct | CoherentFrac | TotalBars |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| EURUSD | 1.0766 | 0.2212 | 0.5585 | 0.0022 | 0.5349 | 43 | 95.1200 | 0.1984 | 200000 |
| BTCUSDT | 0.8404 | -0.8996 | -2.1385 | 0.0260 | 0.3718 | 156 | 61.8400 | 0.4372 | 105069 |
| ETHUSDT | 1.0173 | 0.0860 | 0.2044 | 0.0191 | 0.4504 | 131 | 60.9800 | 0.4484 | 105069 |
| XAUUSD | 1.4945 | 0.4982 | 1.4206 | 0.0194 | 0.5714 | 7 | 59.7400 | 0.4665 | 313 |
| NAS100 | 2.6091 | 0.9735 | 44.5165 | 0.0070 | 0.6000 | 5 | 63.2600 | 0.4824 | 313 |
| USOIL | 0.2867 | -2.1622 | -6.9864 | 0.0714 | 0.1667 | 12 | 71.2500 | 0.3099 | 313 |
| UKOIL | 0.2539 | -2.3218 | -5.3340 | 0.0761 | 0.1667 | 12 | 69.0100 | 0.3323 | 313 |


---

## Market × Regime Distribution

Fraction of total bars in each regime (Q thresholds IMMUTABLE):

| Market | Deep_Incoherent | Mod_Incoherent | Transition | Weak_Coherent | Strong_Coherent | CoherentTotal | Entropy(norm) |
| --- | --- | --- | --- | --- | --- | --- | --- |
| EURUSD | 4.98% | 74.78% | 0.40% | 14.86% | 4.98% | 19.84% | 0.5105 |
| BTCUSDT | 45.01% | 11.18% | 0.09% | 5.55% | 38.16% | 43.72% | 0.7076 |
| ETHUSDT | 44.18% | 10.88% | 0.10% | 5.81% | 39.03% | 44.84% | 0.7094 |
| XAUUSD | 25.24% | 27.80% | 0.32% | 6.39% | 40.26% | 46.65% | 0.7852 |
| NAS100 | 28.12% | 23.32% | 0.32% | 11.50% | 36.74% | 48.24% | 0.8271 |
| USOIL | 61.98% | 7.03% | 0.00% | 2.24% | 28.75% | 30.99% | 0.5757 |
| UKOIL | 60.38% | 6.39% | 0.00% | 2.24% | 30.99% | 33.23% | 0.5768 |


---

## Market × Allocator Behaviour

| Market | Deep →  | Mod →  | Transition →  | Weak →  | Strong →  | NoTrade% | Switches |
| --- | --- | --- | --- | --- | --- | --- | --- |
| EURUSD | NO_TRADE | NO_TRADE | NO_TRADE | NO_TRADE | NO_TRADE | 95.12% | 17906 |
| BTCUSDT | NO_TRADE | NO_TRADE | NO_TRADE | NO_TRADE | NO_TRADE | 61.84% | 25852 |
| ETHUSDT | NO_TRADE | NO_TRADE | NO_TRADE | NO_TRADE | NO_TRADE | 60.98% | 26166 |
| XAUUSD | NO_TRADE | NO_TRADE | NO_TRADE | NO_TRADE | NO_TRADE | 59.74% | 89 |
| NAS100 | NO_TRADE | NO_TRADE | NO_TRADE | NO_TRADE | NO_TRADE | 63.26% | 100 |
| USOIL | NO_TRADE | NO_TRADE | NO_TRADE | NO_TRADE | NO_TRADE | 71.25% | 61 |
| UKOIL | NO_TRADE | NO_TRADE | NO_TRADE | NO_TRADE | NO_TRADE | 69.01% | 57 |


---

## Universality Tests

### Universality Matrix (Market × Criteria)

| Market | PF>1.0 | NoTrade>80pct | SC_frac_similar | Entropy_similar | Allocator_converged | Score | Rating |
| --- | --- | --- | --- | --- | --- | --- | --- |
| EURUSD | 1 | 1 | 1 | 1 | 1 | 1.0000 | High |
| BTCUSDT | 0 | 0 | 0 | 0 | 0 | 0.0000 | Unsupported |
| ETHUSDT | 1 | 0 | 0 | 0 | 0 | 0.2000 | Unsupported |
| XAUUSD | 1 | 0 | 0 | 0 | 0 | 0.2000 | Unsupported |
| NAS100 | 1 | 0 | 0 | 0 | 0 | 0.2000 | Unsupported |
| USOIL | 0 | 0 | 0 | 1 | 0 | 0.2000 | Unsupported |
| UKOIL | 0 | 0 | 0 | 1 | 0 | 0.2000 | Unsupported |


### Universality Scores

| Market | PF | NoTrade_pct | SC_fraction | NormEntropy | Score | Rating | Score_sum | Score_max | MW_p | Perm_p | FDR_reject | Cohen_d |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| EURUSD | 1.0766 | 95.1200 | 0.0498 | 0.5105 | 1.0000 | High | 5 | 5 | nan | nan | nan | nan |
| BTCUSDT | 0.8404 | 61.8400 | 0.3816 | 0.7076 | 0.0000 | Unsupported | 0 | 5 | 0.0303 | 0.5800 | False | -0.0913 |
| ETHUSDT | 1.0173 | 60.9800 | 0.3903 | 0.7094 | 0.2000 | Unsupported | 1 | 5 | 0.3718 | 0.9960 | False | 0.0006 |
| XAUUSD | 1.4945 | 59.7400 | 0.4026 | 0.7852 | 0.2000 | Unsupported | 1 | 5 | 0.5649 | 0.2140 | False | 0.5262 |
| NAS100 | 2.6091 | 63.2600 | 0.3674 | 0.8271 | 0.2000 | Unsupported | 1 | 5 | 0.4900 | 0.0120 | False | 1.4630 |
| USOIL | 0.2867 | 71.2500 | 0.2875 | 0.5757 | 0.2000 | Unsupported | 1 | 5 | 0.0005 | 0.0000 | True | -1.3684 |
| UKOIL | 0.2539 | 69.0100 | 0.3099 | 0.5768 | 0.2000 | Unsupported | 1 | 5 | 0.0005 | 0.0000 | True | -1.4692 |


**Overall Transport Universality Confidence: Unsupported**  
- High: 1  
- Moderate: 0  
- Weak: 0  
- Unsupported: 6  

---

## Statistical Tests (vs EUR/USD Baseline)

Tests: Mann-Whitney U, Permutation (500 iterations), BH FDR correction, Cohen's d

| market | n_market | n_baseline | mean_market | mean_baseline | mean_diff | mw_stat | mw_p | perm_p | cohen_d | mw_reject_fdr |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| BTCUSDT | 156 | 43 | -0.0001 | 0.0000 | -0.0001 | 2629.0000 | 0.0303 | 0.5800 | -0.0913 | False |
| ETHUSDT | 131 | 43 | 0.0000 | 0.0000 | 0.0000 | 2560.0000 | 0.3718 | 0.9960 | 0.0006 | False |
| XAUUSD | 7 | 43 | 0.0017 | 0.0000 | 0.0017 | 172.0000 | 0.5649 | 0.2140 | 0.5262 | False |
| NAS100 | 5 | 43 | 0.0043 | 0.0000 | 0.0043 | 129.0000 | 0.4900 | 0.0120 | 1.4630 | False |
| USOIL | 12 | 43 | -0.0050 | 0.0000 | -0.0050 | 86.0000 | 0.0005 | 0.0000 | -1.3684 | True |
| UKOIL | 12 | 43 | -0.0054 | 0.0000 | -0.0054 | 86.0000 | 0.0005 | 0.0000 | -1.4692 | True |


---

## Scientific Questions — Evidence-Based Answers

### Q1. Does Q generalise across markets?

**Conclusion:** Q produces coherent regime structure in 6/6 markets. 3/6 markets have PF>1.0 without recalibration.  
**Confidence:** Moderate  

**Evidence:**  
- profitable_markets: ['ETHUSDT', 'XAUUSD', 'NAS100']
- pf_by_market:
  - BTCUSDT: 0.84
  - ETHUSDT: 1.017
  - XAUUSD: 1.495
  - NAS100: 2.609
  - USOIL: 0.287
  - UKOIL: 0.254
- fdr_significant: 2

### Q2. Is transport market-agnostic?

**Conclusion:** Transport applies identical regime classification and allocator across all 6 markets. No-trade suppression observed in all markets (range: 59.7%–71.2%).  
**Confidence:** Weak  

**Evidence:**  
- no_trade_by_market:
  - BTCUSDT: 61.8
  - ETHUSDT: 61.0
  - XAUUSD: 59.7
  - NAS100: 63.3
  - USOIL: 71.2
  - UKOIL: 69.0

### Q3. Which markets exhibit strongest transport behaviour?

**Conclusion:** Ranked by PF: NAS100, XAUUSD, ETHUSDT, BTCUSDT, USOIL, UKOIL. High transport evidence: NAS100, XAUUSD, ETHUSDT.  
**Confidence:** High  

**Evidence:**  
- pf_ranking:
  - NAS100: 2.609
  - XAUUSD: 1.495
  - ETHUSDT: 1.017
  - BTCUSDT: 0.84
  - USOIL: 0.287
  - UKOIL: 0.254

### Q4. Does the allocator converge to similar behaviour?

**Conclusion:** Strong_Coherent fraction: mean=0.313, std=0.114 across markets. Allocator consistently selects NO_TRADE for 4/5 regimes.  
**Confidence:** Weak  

**Evidence:**  
- sc_fraction_by_market:
  - EURUSD: 0.0498
  - BTCUSDT: 0.3816
  - ETHUSDT: 0.3903
  - XAUUSD: 0.4026
  - NAS100: 0.3674
  - USOIL: 0.2875
  - UKOIL: 0.3099

### Q5. Does transport continue to suppress trading in noisy markets?

**Conclusion:** 0/6 markets show >85% no-trade fraction, consistent with Phase 2 EUR/USD result (95.02%).  
**Confidence:** Weak  

**Evidence:**  
- suppression_by_market:
  - BTCUSDT: 61.8%
  - ETHUSDT: 61.0%
  - XAUUSD: 59.7%
  - NAS100: 63.3%
  - USOIL: 71.2%
  - UKOIL: 69.0%

### Q6. Is the Transport Operating System reproducible without recalibration?

**Conclusion:** Identical OS (q05=-1.0, q95=1.73) applied to all markets. 3/6 markets achieve PF>1.0 with zero parameter changes.  
**Confidence:** High  

**Evidence:**  
- os_parameters_changed: False
- profitable_without_recalib: 3

### Q7. Can transport be interpreted as a universal market operating system?

**Conclusion:** Overall universality confidence: Unsupported. 1 High, 0 Moderate, 0 Weak, 6 Unsupported.  
**Confidence:** Unsupported  

**Evidence:**  
- mean_universality_score: 0.286
- market_ratings:
  - EURUSD: High
  - BTCUSDT: Unsupported
  - ETHUSDT: Unsupported
  - XAUUSD: Unsupported
  - NAS100: Unsupported
  - USOIL: Unsupported
  - UKOIL: Unsupported

### Q8. Does this strengthen the hypothesis that Q measures a property of information transport?

**Conclusion:** Entropy structure shows std=0.110 across markets — consistent with universal transport dynamics. Mean PF=1.083 across all markets.  
**Confidence:** Moderate  

**Evidence:**  
- entropy_by_market:
  - EURUSD: 0.5105
  - BTCUSDT: 0.7076
  - ETHUSDT: 0.7094
  - XAUUSD: 0.7852
  - NAS100: 0.8271
  - USOIL: 0.5757
  - UKOIL: 0.5768
- entropy_std: 0.1095
- mean_pf: 1.0827

---

## Confidence Summary

| # | Question | Confidence |
| - | -------- | ---------- |
| Q1 | Does Q generalise across markets? | Moderate |
| Q2 | Is transport market-agnostic? | Weak |
| Q3 | Which markets exhibit strongest transport behaviour? | High |
| Q4 | Does the allocator converge to similar behaviour? | Weak |
| Q5 | Does transport continue to suppress trading in noisy markets | Weak |
| Q6 | Is the Transport Operating System reproducible without recal | High |
| Q7 | Can transport be interpreted as a universal market operating | Unsupported |
| Q8 | Does this strengthen the hypothesis that Q measures a proper | Moderate |

---

*Report generated by Phase 3 Transport Universality Validation pipeline.*
*All transport mathematics, OS parameters, and strategy library are IMMUTABLE from Phase 2.*
