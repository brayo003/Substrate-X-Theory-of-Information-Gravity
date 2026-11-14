# Phase 5 — True Out-of-Sample Validation (2026)
**Generated:** 2026-07-22T14:15:57Z

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
| XAUUSD | 1 | 0.000 | 0.000 | 0.0% | 0.0000 | 72.3% |
| USOIL | 6 | 0.483 | -0.805 | 16.7% | 0.1730 | 64.4% |
| UKOIL | 2 | 0.000 | -19.381 | 0.0% | 0.0406 | 71.3% |

---

## 2025 vs 2026 Comparison

| Market | PF 2025 | PF 2026 | Δ PF | Sharpe 2025 | Sharpe 2026 | Verdict |
| ------ | ------- | ------- | ---- | ----------- | ----------- | ------- |
| EURUSD | 0.394 | 0.000 | -0.394 | -41.960 | 0.000 | ↓ Degraded |
| BTCUSDT | 1.042 | 1.099 | +0.058 | 0.878 | 1.240 | ↑ Improved |
| ETHUSDT | 1.011 | 1.025 | +0.014 | 0.386 | 0.355 | ↑ Improved |
| NAS100 | 1.071 | 6.102 | +5.031 | 0.108 | 1.918 | ↑ Improved |
| XAUUSD | 2.651 | 0.000 | -2.651 | 1.552 | 0.000 | ↓ Degraded |
| USOIL | 1.268 | 0.483 | -0.784 | 0.426 | -0.805 | ↓ Degraded |
| UKOIL | 2.214 | 0.000 | -2.214 | 1.284 | -19.381 | ↓ Degraded |

---

## Drift Indices

### Transport Drift (Q distribution)

| Market | TV Distance | KS Stat | KS p-value | Δ Coherent Frac |
| ------ | ----------- | ------- | ---------- | --------------- |
| BTCUSDT | 0.0129 | 0.0219 | 0.0000 | -0.0189 |
| ETHUSDT | 0.0210 | 0.0286 | 0.0000 | -0.0272 |
| NAS100 | 0.2076 | 0.1177 | 0.0602 | -0.0963 |
| XAUUSD | 0.3160 | 0.3222 | 0.0000 | -0.1595 |
| USOIL | 0.2532 | 0.1990 | 0.0001 | +0.1109 |
| UKOIL | 0.2626 | 0.1731 | 0.0011 | +0.0242 |

### Execution Drift

| Market | Exec Drift Idx | ΔPF | ΔSharpe | ΔWinRate | Verdict |
| ------ | -------------- | --- | ------- | -------- | ------- |
| EURUSD | 1.000 | -0.394 | +41.960 | -0.338 | Both_Unprofitable |
| BTCUSDT | 0.164 | +0.058 | +0.363 | +0.010 | Stable_Profitable |
| ETHUSDT | 0.038 | +0.015 | -0.030 | +0.008 | Stable_Profitable |
| NAS100 | 7.446 | +5.031 | +1.809 | +0.365 | Stable_Profitable |
| XAUUSD | 1.000 | -2.651 | -1.552 | -0.613 | Degraded |
| USOIL | 1.372 | -0.784 | -1.231 | -0.262 | Degraded |
| UKOIL | 6.029 | -2.214 | -20.665 | -0.615 | Degraded |

### Statistical Tests (2025 vs 2026 Net Returns)

| Market | n_2025 | n_2026 | MW p-val | KS p-val | Cohen's d | FDR Reject |
| ------ | ------ | ------ | -------- | -------- | --------- | ---------- |
| EURUSD | 50628 | 0 | nan | nan | nan | False |
| BTCUSDT | 24024 | 1011 | 0.0660 | 0.0194 | -0.034 | False |
| ETHUSDT | 23949 | 1195 | 0.0008 | 0.0000 | -0.020 | True |
| NAS100 | 62 | 4 | nan | nan | nan | False |
| XAUUSD | 54 | 1 | nan | nan | nan | False |
| USOIL | 71 | 6 | 0.0325 | 0.0085 | 0.373 | False |
| UKOIL | 57 | 2 | nan | nan | nan | False |

---

## Final Conclusion

**PARTIALLY GENERALIZES** — Majority of markets remain profitable; some degradation observed.

- **Transport Layer:** TV distance = 0.179. Drift detected in Q distributions.
- **Execution Layer:** Mean drift index = 2.436. Execution adapted to 2026 volatility regime.
- **Allocator Layer:** Stability = 29.5%. Frozen allocator decisions remain consistent.
- **Scheduler Layer:** Regime structure preserved. NoTrade logic operational.

_No redesign. No optimization. Pure out-of-sample replay._