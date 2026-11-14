# Changes and Limitations
## Corrected Bounded Validation Audit

**Date:** 2026-10-11 | **Commit:** `6738ed05`

---

## Files Created (this audit)

| File | Description |
|------|-------------|
| `corrected_audit.py` | Main audit script (849 → 1035 lines). Runs all 6 diagnostic sections. |
| `results/bounded_validation_corrected/CORRECTED_BOUNDED_VERDICT.md` | Executive verdict with all findings |
| `results/bounded_validation_corrected/execution_audit.md` | Line-by-line execution path audit |
| `results/bounded_validation_corrected/statistical_audit.md` | Statistical methods and uncertainty |
| `results/bounded_validation_corrected/reproducibility_manifest.json` | Input files, config, commands, outputs |
| `results/bounded_validation_corrected/changes_and_limitations.md` | This file |
| `results/bounded_validation_corrected/correct_strategy_same_close_2026.csv` | 7-trade corrected OOS log (same-close entry) |
| `results/bounded_validation_corrected/correct_strategy_next_open_2026.csv` | 7-trade diagnostic (next-bar-open entry) |
| `results/bounded_validation_corrected/orig_signal_next_open_2026.csv` | 60-trade diagnostic (original signal, next-open entry) |
| `results/bounded_validation_corrected/tsys_vs_fwdvol.csv` | T_sys vs forward vol with rv5 baseline |
| `results/bounded_validation_corrected/df_2026_cached.parquet` | 2026 5-min OHLC + transport pipeline output (cached) |
| `results/bounded_validation_corrected/corrected_audit_results.json` | Full machine-readable results |
| `results/bounded_validation_corrected/execution_log.txt` | Console output of corrected_audit.py run |

---

## Files Modified

| File | Change |
|------|--------|
| `bounded_validation.py` | Strategy mismatch bugfix in `generate_ny_continuation_signals()` NOT applied — original preserved as-is. The corrected test uses the separate `corrected_audit.py` script. |

**No production files were modified.** The execution engines (`p1_strategy_runner.py`, `p2_execution_engine.py`), strategy library (`strategy_library.py`), transport layer, cache files, or Phase 1/2 results were not touched.

---

## Files Preserved Unchanged

All files in `results/bounded_validation/` are preserved exactly as produced by `bounded_validation.py`. The 76-trade CSV, bootstrap results, and JSON outputs are not overwritten.

---

## Diagnostics Performed

| Diagnostic | Result |
|------------|--------|
| Strategy signal comparison (strategy_library.py vs bounded_validation.py) | MISMATCH confirmed — different session filter and signal logic |
| Corrected OOS test: strategy_library.py NY_Continuation, 2026 data | 7 trades, PF=0.538/0.326/0.173 at 3/5/7-pip — all negative |
| Same-close vs next-bar-open diagnostic (original signal) | PF 0.469→0.405 at 3-pip — both negative, same direction |
| Same-close vs next-bar-open diagnostic (correct signal) | 7 trades, identical result — no material difference |
| Cost model verification | Correct: 0.0003 RT applied once, no double-counting |
| Q formula numerical verification | MATCH confirmed from 2023-01 cache parquet |
| Q forward vol overlap check | Forward window starts at t+1; no overlap with Q input |
| Q forward vol Spearman (from cached data) | ρ = −0.005 to −0.008 (negative, confirmed) |
| T_sys forward vol Spearman reproduction | ρ ≈ +0.20 to +0.27 (confirmed, matches v12_validate) |
| T_sys vs simple vol-persistence baseline | Baseline (rv5) ρ ≈ +0.48 to +0.62 > T_sys — baseline stronger |
| Block bootstrap (weekly) resampling | p=0.38 — not significant |
| IID bootstrap resampling (corrected strategy pool) | p=0.37 — not significant |
| 95% CI for expectancy (7 trades) | [−0.00116, +0.00063] at 3-pip — contains zero |
| PF bootstrap 95% CI (7 trades) | [0.069, 2.691] — contains 1.0 |
| Phase 1 MWU re-verification | U=14168, p=0.089, r_biserial=−0.126 (confirmed negative sign) |
| Data split verification from artifacts | Cache: 2023–2025 confirmed; 2026 confirmed untouched |
| 24-bar hold implementation check | p2 correct across chunks; p1 has minor edge case at month end |
| Same-candle stop/target ordering | Both engines check stop before target — conservative |

---

## Tests That Could Not Be Completed and Why

| Test | Reason |
|------|--------|
| Live vs backtest comparison | No live trading system deployed. `live_logs/` files are simulated paper-trading from an earlier session, not real fills. |
| Tick-level fill quality | 2026 data contains bid-only 1-minute OHLC. Cannot reconstruct spread at tick level. |
| T_sys incremental contribution beyond rv5 | Would require multivariate regression; not performed to avoid introducing new analytical choices that could be misconstrued as optimization. |
| Block bootstrap by session (London/NY/Asian) | Session classification requires UTC-hour tagging at the trade level; the pool of 7 trades is too small for session-stratified analysis. |
| Exact p-value for 2026 corrected result vs H0:PF=1.0 | With n=7 and non-normal return distribution, exact p-value requires distributional assumptions. Reported t-test p=0.49 is approximate. |
| OOS test beyond July 2026 | Data file ends 2026-07-22. No additional 2026 data available. |

---

## Remaining Uncertainty

1. **The corrected OOS result (7 trades) is entirely inconclusive.** It is negative, but the confidence interval spans from large losses to profitable outcomes. More data is required.

2. **The Q filter's effect cannot be evaluated with 7 trades.** Whether Q's Strong_Coherent regime selects meaningfully better trade opportunities requires at least hundreds of trades — which would need several more years of data at the current signal frequency (8–10 trades/year for the correct NY_Continuation).

3. **T_sys predictive power above vol persistence is unquantified.** The baseline test shows rv5 is stronger, but whether T_sys provides incremental value in a multivariate context has not been tested.

4. **The strategy mismatch in bounded_validation.py was not caused by production code changes.** The production Phase 2 run correctly used `strategy_library.py`. The mismatch existed only in the `bounded_validation.py` validation script.

5. **Bid/ask spread variability is unmodeled.** The 2026 dataset has no ask column. During high-volatility periods, spreads widen; this would increase effective costs above the flat 0.0003–0.0007 assumption.

---

## Command to Reproduce

```bash
cd calibration_engine/eg/finance_module/
python3 corrected_audit.py
# Expected runtime: ~50 seconds
# All outputs written to: results/bounded_validation_corrected/
```

The 2026 pipeline output is cached at `results/bounded_validation_corrected/df_2026_cached.parquet` on the first run; subsequent runs are faster.
