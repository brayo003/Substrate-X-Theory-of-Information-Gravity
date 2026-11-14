# Phase 3 — Summary
**Generated:** 2026-07-22T03:43:21Z  
**Elapsed:** 28.5s  

## Objective
Determine whether the Phase 2 Transport Operating System is domain-agnostic across independent financial markets. No parameters were changed. Zero recalibration. Identical OS applied to every market.

## Overall Universality Confidence
**Unsupported** (mean score: 0.286)

- High: 1 markets
- Moderate: 0 markets
- Weak: 0 markets
- Unsupported: 6 markets

## Performance Summary
| Market | PF | Sharpe | MaxDD | Trades | NoTrade_pct |
| --- | --- | --- | --- | --- | --- |
| EURUSD | 1.0766 | 0.2212 | 0.0022 | 43 | 95.1200 |
| BTCUSDT | 0.8404 | -0.8996 | 0.0260 | 156 | 61.8400 |
| ETHUSDT | 1.0173 | 0.0860 | 0.0191 | 131 | 60.9800 |
| XAUUSD | 1.4945 | 0.4982 | 0.0194 | 7 | 59.7400 |
| NAS100 | 2.6091 | 0.9735 | 0.0070 | 5 | 63.2600 |
| USOIL | 0.2867 | -2.1622 | 0.0714 | 12 | 71.2500 |
| UKOIL | 0.2539 | -2.3218 | 0.0761 | 12 | 69.0100 |


## Universality Scores
| Market | PF | NoTrade_pct | Score | Rating |
| --- | --- | --- | --- | --- |
| EURUSD | 1.0766 | 95.1200 | 1.0000 | High |
| BTCUSDT | 0.8404 | 61.8400 | 0.0000 | Unsupported |
| ETHUSDT | 1.0173 | 60.9800 | 0.2000 | Unsupported |
| XAUUSD | 1.4945 | 59.7400 | 0.2000 | Unsupported |
| NAS100 | 2.6091 | 63.2600 | 0.2000 | Unsupported |
| USOIL | 0.2867 | 71.2500 | 0.2000 | Unsupported |
| UKOIL | 0.2539 | 69.0100 | 0.2000 | Unsupported |


## Key Conclusions
- **Moderate**: Does Q generalise across markets?
- **Weak**: Is transport market-agnostic?
- **High**: Which markets exhibit strongest transport behaviour?
- **Weak**: Does the allocator converge to similar behaviour?
- **Weak**: Does transport continue to suppress trading in noisy markets?
- **High**: Is the Transport Operating System reproducible without recalibration?
- **Unsupported**: Can transport be interpreted as a universal market operating system?
- **Moderate**: Does this strengthen the hypothesis that Q measures a property of info

*Full details in transport_universality_report.md*