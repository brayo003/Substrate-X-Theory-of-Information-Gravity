# Data and Statistical Audit
## Provenance, Split, Leakage Review, Statistical Assumptions, and Limitations

**Audit date:** 2026-10-11  
**Git commit:** `6738ed05`  
**Source files examined:** `p1_data_stream.py`, `checkpoints/checkpoint_manifest.json`, `corrected_audit_results.json` (section7), `p1_checkpoint.py`  
**Data files:** `data/2023/`, `data/2024/`, `data/2025/eurusd_ticks_2025.csv`, `data/2026/eurusd-m1-bid-2026-01-01-2026-07-22.csv`  
**Cache files:** `cache/ohlc_transport_YYYY_MM.parquet` (34 monthly files, no 2026 entries)

---

## 1. Data Provenance and Split

### 1.1 Calibration period

**Source:** EUR/USD tick data in BI5 format (2023, 2024) and CSV format (2025).  
**Data directories:**
- `data/2023/` — BI5 ticks organized as `YYYY/MM/DD/HH_ticks.bi5`
- `data/2024/` — same structure
- `data/2025/eurusd_ticks_2025.csv` — tick-level CSV (~1.1 GB)

**Period covered:** 2023-01-01 22:00 UTC to 2025-10-24 20:55 UTC (from `corrected_audit_results.json` section7).  
**Bars processed:** 209,689 5-minute OHLC bars (34 months, confirmed by checkpoint manifest: `months_processed: 34`).  
**Bar frequency:** 5-minute aggregation from ticks.

**Note:** The directory structure for 2023 includes `data/2023/00/` through `data/2023/11/` (zero-based month indexing), meaning month 00 = January 2023. This is consistent with the pipeline's `month_0` indexing.

### 1.2 Out-of-sample period

**Source:** `data/2026/eurusd-m1-bid-2026-01-01-2026-07-22.csv`  
**Period covered:** 2026-01-01 to 2026-07-21 (from corrected_audit_results.json section7).  
**Format:** 1-minute bid OHLC (not tick data), 224,700 rows, aggregated to 44,940 5-minute bars.  
**Important distinction:** 2026 data is already pre-aggregated to 1-minute bars (not ticks), whereas the calibration data was tick-level. The 5-minute aggregation is applied to 1-minute bars for the 2026 dataset.

**Gap between calibration and OOS:** Approximately October 25, 2025 to December 31, 2025. This two-month gap is present and was not filled. The 2026 OOS period therefore begins approximately 2 months after the calibration period ends.

### 1.3 Cache state before OOS evaluation

The directory listing shows cache files:
- `cache/ohlc_transport_2023_01.parquet` through `cache/ohlc_transport_2025_10.parquet` — 34 monthly files.
- No `cache/ohlc_transport_2026_*.parquet` files exist.

The checkpoint manifest records `data_cache_complete: true` and `q_series_complete: true` for the calibration period. The absence of 2026 cache files is consistent with the claim that 2026 data was not preprocessed before the OOS evaluation run.

**Caveat:** The absence of 2026 cache files is evidence that the 2026 *transport pipeline output* had not been previously cached. It does not establish that the raw 2026 CSV was never opened, examined, or consulted informally before any design decisions were made. No git history analysis was performed to verify this. The independence of 2026 data from design choices can be claimed but not fully proved from file artifacts alone.

---

## 2. What Each Period Was Used For

| Use | Period | Notes |
|-----|--------|-------|
| Q threshold computation (q05, q95) | 2023-01-01 to 2025-10-24 | Frozen in manifest before OOS test |
| Strategy performance matrix (Phase 1) | 2023-01-01 to 2025-10-24 | Used to select strategy per regime |
| OS calibration (Layers 1–3) | 2023-01-01 to 2025-10-24 | Risk/stop/target allocation |
| T_sys predictive correlation | 2023-01-01 to 2025-10-24 | Exploratory, in-sample |
| Q predictive correlation | 2023-01-01 to 2025-10-24 | Exploratory, in-sample |
| Transport OS trading evaluation | 2026-01-01 to 2026-07-21 | OOS, held out |

The 2025 data is included in calibration (through October 2025). The gap (October–December 2025) was not used for anything.

---

## 3. Leakage Review

### 3.1 Q computation leakage

Q[t] = 100 × (ln(s[t]/s[t-1]))² − 1.

- Uses only s[t] and s[t-1] — no future information.
- s[t] is computed from rolling/ewm windows with no future bars.
- **No leakage in Q computation.**

### 3.2 Q threshold leakage

q05 and q95 are the 5th and 95th percentiles of the calibration-period Q distribution. They were:
1. Computed from 2023–2025 data.
2. Saved in `checkpoints/checkpoint_manifest.json` with timestamp `2026-10-11T01:36:05`.
3. Loaded by `p2_transport_os.py` from the manifest at runtime.
4. Applied to 2026 data without modification.

**No leakage: 2026 data did not influence the thresholds.**

### 3.3 Strategy selection leakage

Phase 1 strategy selection used `results/phase1/performance_by_regime.csv`, which records in-sample (2023–2025) strategy performance. The corrected audit uses `strategy_library.py:NY_Continuation` which was the Phase 2–selected strategy for the Strong_Coherent regime.

The selection of NY_Continuation was made from Phase 1 calibration-period results, not from 2026 data. **No leakage in strategy selection.**

### 3.4 Same-close entry (minor leakage)

Entry at close[t] after observing close[t] is a form of look-ahead at the bar level — the bar must be complete to know close[t], but by the time close[t] is known, the bar is over and a fill at that exact price is not mechanically achievable. This is standard backtest approximation, not information from the future in the usual sense (the signal uses only past bars). It introduces a small, direction-uncertain fill bias. Magnitude: 0.1–0.3 pip at 5-min resolution. This is documented but is not classified as a structural leakage risk.

### 3.5 2026 raw data inspection (unverifiable)

The absence of 2026 cache files proves the 2026 transport pipeline was not previously run. It does not prove the 2026 CSV was never opened or that informal knowledge of 2026 market behavior did not influence design choices made in 2025 or earlier. This is a standard limitation of any time-series backtest: the analyst knows roughly what happened in a future period. No formal blinding procedure was in place. **The independence of 2026 data from prior design choices cannot be fully established from artifacts alone.**

---

## 4. Statistical Assumptions

### 4.1 Independence assumption violations

Time-series observations at 5-minute frequency are strongly autocorrelated. The following analyses are affected:

**T_sys and Q versus forward volatility:**  
- Nominal p-values (reported as 0.0) assume independent observations.  
- Effective sample size ≈ 30,000–50,000 after AR(1) correction (rather than 209,000).  
- The qualitative findings (T_sys has modest positive correlation; Q has negligible correlation) are robust to this correction.  
- The dominance of rv5 over T_sys is robust.

**Bootstrap for trading performance:**  
- Block bootstrap with weekly blocks was used to address temporal clustering.  
- Weekly blocks are appropriate given the session-specific strategy (NY open).  
- Block bootstrap p-values (0.37–0.38) are appropriate; iid bootstrap (0.37) converges to similar values because the 7-trade sample is small enough that block structure has limited impact.

### 4.2 Multiple comparisons

The following multiple comparisons were made:
- T_sys vs forward volatility at k = 1, 3, 6, 12 horizons (4 tests).
- Q vs forward volatility at k = 1, 3, 6, 12 horizons (4 tests).
- Trading performance at 3, 5, 7-pip cost scenarios (3 tests per strategy variant).
- Bootstrap comparison using iid and block methods (2 approaches).

**For Q vs volatility:** All horizons show the same sign and similar magnitude. Bonferroni correction at α = 0.05 would require individual test α = 0.0125. All Q correlations remain negligible in magnitude after correction.

**For T_sys vs volatility:** All horizons show positive correlation. Bonferroni correction does not change the qualitative finding.

**For trading performance:** Cost scenarios are not independent tests — they use the same trades. Reporting three cost scenarios is not multiple testing of independent hypotheses; it is sensitivity analysis. No Bonferroni correction is needed.

### 4.3 Multiple testing in Phase 1 strategy selection

Phase 1 tested 22+ strategies across 5 regimes, producing ≥ 110 strategy-regime combinations. The best strategy per regime was selected and used in Phase 2. This is a form of multiple comparison that inflates the apparent performance of the selected strategy on the calibration data.

The corrected audit partially addresses this by evaluating the selected strategy on held-out 2026 data. However, the very small number of OOS trades (7) means the OOS test has very low power to detect inflation from Phase 1 multiple testing.

### 4.4 The 7-trade sample: power analysis implications

A power analysis for detecting a PF of 1.5 (a modest trading edge) at 80% power and α = 0.05 (one-sided):

- Approximate required n: (zα + zβ)² × var(pf) / effect² ≈ 200–400 trades depending on win-rate variance assumptions.
- Observed n: 7 trades.
- Power of the 7-trade test: approximately 5–15% to detect a PF of 1.5 using a standard t-test.

**The 7-trade OOS test is severely underpowered.** A non-significant result (which is what was observed) does not establish absence of edge. It establishes only that the available sample is too small to detect a realistic effect size.

Conversely, the point estimates (PF = 0.17–0.54 at various cost scenarios) are all below 1.0, providing mild evidence against a large positive edge, though this evidence is weak given the sample size.

---

## 5. Random-Selection Comparison

### 5.1 Design

The bootstrap compared the observed 7-trade corrected strategy against random draws of 7 trades from the pool of 61 hour-13 NY_Continuation signals on 2026 data.

**Null hypothesis:** The 7 Strong_Coherent trades are drawn from the same performance distribution as any other 7 hour-13 trades.  
**Statistic:** Profit factor.  
**Simulation:** 10,000 iid resamples; 10,000 block (weekly) resamples.  
**n_bootstrap:** 10,000 (reported in corrected_audit_results.json section4).

### 5.2 Results

| Method | Mean PF under null | p95 under null | Observed PF | p-value |
|--------|-------------------|----------------|-------------|---------|
| iid bootstrap | 0.343 | 0.964 | 0.326 | 0.372 |
| Block bootstrap | 0.346 | 0.923 | 0.326 | 0.380 |

The observed PF (0.326 at 5-pip) is not significantly different from random selection within the hour-13 pool. Both p-values are far above conventional thresholds. The regime gate (Strong_Coherent) does not select trades with significantly different performance from the full hour-13 sample.

### 5.3 Limitations of this comparison

The pool of 61 hour-13 trades is itself a small sample. The bootstrap distribution of PF under the null (simulated from 61 trades) has high variance. A non-significant result could mean: (a) the regime gate genuinely adds no value, or (b) the pool is too small to detect meaningful selection. The bootstrap also uses only 2026 data and the effect of the regime gate may differ across market conditions.

Do not interpret this null result as proof that Q-based regime gating provides no edge. It establishes only that this comparison cannot detect one.

### 5.4 The correct comparison for the original (wrong) signal

The prior audit compared 76 trades (original signal) against random draws from a pool of 797 hour-14-to-21 trades. This comparison is invalid for evaluating Phase 2 because the signal was wrong. The 797-trade pool should not be compared with 7 corrected-strategy trades. The corrected comparison (61 vs 7, both from hour-13) is reported above.

---

## 6. Summary of What Can and Cannot Be Established

| Claim | Status | Basis |
|-------|--------|-------|
| Calibration period is 2023-01-01 to 2025-10-24 | Confirmed | Manifest, data file timestamps |
| OOS period is 2026-01-01 to 2026-07-21 | Confirmed | corrected_audit_results.json section7 |
| Q thresholds derived only from calibration | Confirmed | Manifest timestamps, no 2026 cache |
| 2026 data not used in design choices | Not provable | File artifacts only show cache absence |
| Q is computed causally | Confirmed | Source code (backward difference) |
| T_sys is computed causally | Confirmed | Code structure (bar-by-bar state machine) |
| Strategy selection used only calibration data | Confirmed | Phase 1 results from 2023–2025 |
| T_sys predicts forward volatility | Confirmed (in-sample, modest effect) | ρ = 0.20–0.27 in calibration period |
| T_sys outperforms rv5 baseline | Not confirmed | rv5 dominates T_sys by 2.3× |
| Q predicts forward volatility | Not confirmed | ρ ≈ −0.008, negligible |
| Trading edge exists | Not confirmed | 7 trades, all cost scenarios PF < 1.0, CI contains zero |
| Trading edge is absent | Not confirmed | Sample too small for this claim |
| Regime gate improves trade selection | Not confirmed | Non-significant bootstrap comparison |
