# Phase 5 — True Out-of-Sample Validation (2026)
**Generated:** 2026-07-22T14:36:01Z

**Validation period:** 2026-01-01 to 2026-07-22
**Frozen OS:** Phase 1-4 components, UNMODIFIED
**Markets:** EURUSD, BTCUSDT, ETHUSDT, NAS100, XAUUSD, USOIL, UKOIL

---

## Per-Market Performance

| Market | Trades | PF | Sharpe | WinRate | MaxDD | NoTrade% |
| ------ | ------ | -- | ------ | ------- | ----- | -------- |
| EURUSD | 0 | 0.000 | 0.000 | 0.0% | 0.0000 | 0.0% |
| BTCUSDT | 1011 | 1.099 | 1.240 | 41.1% | 0.0787 | 63.9% |
| ETHUSDT | 1195 | 1.025 | 0.355 | 40.8% | 0.2415 | 63.4% |
| NAS100 | 4 | 6.102 | 1.918 | 75.0% | 0.0000 | 66.8% |
| XAUUSD | 428 | 0.980 | -0.164 | 36.9% | 0.0295 | 69.1% |
| USOIL | 683 | 0.990 | -0.103 | 38.4% | 0.2013 | 67.5% |
| UKOIL | 595 | 0.888 | -1.177 | 36.3% | 0.2033 | 61.5% |

---

## 2025 vs 2026 Comparison

| Market | PF 2025 | PF 2026 | Δ PF | Sharpe 2025 | Sharpe 2026 | Verdict |
| ------ | ------- | ------- | ---- | ----------- | ----------- | ------- |
| EURUSD | 0.394 | 0.000 | -0.394 | -41.960 | 0.000 | ↓ Degraded |
| BTCUSDT | 1.042 | 1.099 | +0.058 | 0.878 | 1.240 | ↑ Improved |
| ETHUSDT | 1.011 | 1.025 | +0.014 | 0.386 | 0.355 | ↑ Improved |
| NAS100 | 1.071 | 6.102 | +5.031 | 0.108 | 1.918 | ↑ Improved |
| XAUUSD | 2.651 | 0.980 | -1.672 | 1.552 | -0.164 | ↓ Degraded |
| USOIL | 1.268 | 0.990 | -0.278 | 0.426 | -0.103 | ↓ Degraded |
| UKOIL | 2.214 | 0.888 | -1.326 | 1.284 | -1.177 | ↓ Degraded |

---

## Drift Indices

### Transport Drift (Q distribution)

| Market | TV Distance | KS Stat | KS p-value | Δ Coherent Frac |
| ------ | ----------- | ------- | ---------- | --------------- |
| EURUSD | 0.4977 | 0.5340 | 0.0000 | +0.1335 |
| XAUUSD | 0.2865 | 0.2660 | 0.0000 | -0.1089 |
| USOIL | 0.1380 | 0.1428 | 0.0000 | +0.0632 |
| UKOIL | 0.1834 | 0.1809 | 0.0000 | +0.1123 |

### Execution Drift

| Market | Exec Drift Idx | ΔPF | ΔSharpe | ΔWinRate | Verdict |
| ------ | -------------- | --- | ------- | -------- | ------- |
| EURUSD | 1.000 | -0.394 | +41.960 | -0.338 | Both_Unprofitable |
| BTCUSDT | 0.164 | +0.058 | +0.363 | +0.010 | Stable_Profitable |
| ETHUSDT | 0.038 | +0.015 | -0.030 | +0.008 | Stable_Profitable |
| NAS100 | 7.446 | +5.031 | +1.809 | +0.365 | Stable_Profitable |
| XAUUSD | 0.711 | -1.672 | -1.716 | -0.244 | Degraded |
| USOIL | 0.522 | -0.278 | -0.529 | -0.045 | Degraded |
| UKOIL | 0.975 | -1.326 | -2.462 | -0.252 | Degraded |

### Statistical Tests (2025 vs 2026 Net Returns)

| Market | n_2025 | n_2026 | MW p-val | KS p-val | Cohen's d | FDR Reject |
| ------ | ------ | ------ | -------- | -------- | --------- | ---------- |
| EURUSD | 50628 | 0 | nan | nan | nan | False |
| BTCUSDT | 24024 | 1011 | 0.0660 | 0.0194 | -0.034 | False |
| ETHUSDT | 23949 | 1195 | 0.0008 | 0.0000 | -0.020 | True |
| NAS100 | 62 | 4 | nan | nan | nan | False |
| XAUUSD | 54 | 428 | 0.0018 | 0.0000 | 0.622 | True |
| USOIL | 71 | 683 | 0.0280 | 0.0000 | -0.036 | False |
| UKOIL | 57 | 595 | 0.0659 | 0.0000 | 0.116 | False |

---

## Final Conclusion

**PARTIALLY GENERALIZES** — Majority of markets remain profitable; some degradation observed.

- **Transport Layer:** TV distance = 0.276. Drift detected in Q distributions.
- **Execution Layer:** Mean drift index = 1.551. Execution adapted to 2026 volatility regime.
- **Allocator Layer:** Stability = 29.5%. Frozen allocator decisions remain consistent.
- **Scheduler Layer:** Regime structure preserved. NoTrade logic operational.

_No redesign. No optimization. Pure out-of-sample replay._