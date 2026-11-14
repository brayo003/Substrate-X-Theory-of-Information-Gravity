#!/usr/bin/env python3
"""
run_validation.py — Main orchestration script.

Executes the complete V12/SXCOmega validation pipeline:
    1. Load historical EUR/USD data
    2. Build OHLC + raw signals (reusing forex_pipeline definitions)
    3. Scale signals to [0,100] and build V12 composite
    4. Run SXCOmegaEngine over the full history
    5. Compute independent market labels (no V12 dependency)
    6. Statistical validation  (contemporaneous + predictive)
    7. Stability analysis
    8. Visualisation
    9. Write report

Usage:
    python run_validation.py [--max-files N]

    --max-files N  : limit BI5 files per year (None = all).
                     Use --max-files 500 for a fast smoke test (~3 months).
"""

import argparse
import sys
import time
from pathlib import Path

# --- path setup -----------------------------------------------------------
HERE     = Path(__file__).resolve().parent
DATA_DIR = HERE.parent / "data"
OUT_DIR  = HERE / "results"
OUT_DIR.mkdir(parents=True, exist_ok=True)

if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

from loader        import load_all_ticks, summarise_ticks
from signals       import build_ohlc, compute_raw_signals
from engine_runner import (scale_signals_to_100, build_v12_composite,
                            run_v12, extract_transitions)
from labels        import build_all_labels
from stats         import (compare_phases, predictive_correlation,
                            lead_lag_correlation, permutation_test,
                            stability_by_year, stability_by_session,
                            forward_window_analysis)
from plots         import generate_all_figures
from report        import write_report

import warnings
warnings.filterwarnings('ignore')

# ---------------------------------------------------------------------------
LABEL_COLS  = [
    'realized_vol', 'atr', 'adx', 'spread_norm', 'spread_abs',
    'tick_density', 'range_pct', 'breakout', 'trend_persist',
    'drawdown', 'abs_return',
]
PERM_LABELS = ['realized_vol', 'atr', 'spread_abs', 'adx', 'abs_return']


def main(max_files: int = None):
    t0 = time.time()

    # ------------------------------------------------------------------
    # STEP 1 — Load data
    # ------------------------------------------------------------------
    print('\n[1/9] Loading EUR/USD historical data …')
    ticks = load_all_ticks(DATA_DIR, max_files_per_year=max_files,
                           include_2025=True)
    data_summary = summarise_ticks(ticks)
    print(f'  Loaded {data_summary["total_ticks"]:,} ticks  '
          f'[{data_summary["start"]} → {data_summary["end"]}]')

    # ------------------------------------------------------------------
    # STEP 2 — OHLC + raw signals
    # ------------------------------------------------------------------
    print('\n[2/9] Building OHLC bars and raw signals …')
    ohlc = build_ohlc(ticks)
    raw  = compute_raw_signals(ohlc)
    print(f'  OHLC bars  : {len(ohlc):,}')
    del ticks   # free tick memory

    # ------------------------------------------------------------------
    # STEP 3 — Scale to [0,100] and build V12 composite
    # ------------------------------------------------------------------
    print('\n[3/9] Scaling signals to [0, 100] and building V12 composite …')
    scaled, scale_params = scale_signals_to_100(raw)
    composite, scale_factor = build_v12_composite(scaled, target_median=8.0)
    print(f'  Composite pts   : {len(composite):,}')
    print(f'  Scale factor    : {scale_factor:.4f}  (median → 8.0 for engine boundary at 10.3)')
    print(f'  Composite range : [{composite.min():.2f}, {composite.max():.2f}]  '
          f'mean={composite.mean():.2f}  median={composite.median():.2f}')
    for name, p in scale_params.items():
        print(f'    {name:<22}  lo={p["lo"]:.5f}  hi={p["hi"]:.5f}')

    # ------------------------------------------------------------------
    # STEP 4 — Run V12 engine
    # ------------------------------------------------------------------
    print('\n[4/9] Running SXCOmegaEngine over full history …')
    v12         = run_v12(composite)
    transitions = extract_transitions(v12)
    fw_bars = (v12['phase'] == 'FIREWALL').sum()
    nm_bars = (v12['phase'] == 'NOMINAL').sum()
    print(f'  V12 bars processed  : {len(v12):,}')
    print(f'  FIREWALL bars       : {fw_bars:,}  ({fw_bars/len(v12)*100:.1f} %)')
    print(f'  NOMINAL  bars       : {nm_bars:,}  ({nm_bars/len(v12)*100:.1f} %)')
    print(f'  T_sys range         : [{v12["T_sys"].min():.3f}, {v12["T_sys"].max():.3f}]')
    print(f'  Transitions total   : {len(transitions):,}')
    fw_eps = transitions[transitions['phase'] == 'FIREWALL']
    nm_eps = transitions[transitions['phase'] == 'NOMINAL']
    if not fw_eps.empty:
        print(f'  FIREWALL episodes   : {len(fw_eps):,}  '
              f'median dur={fw_eps["duration_min"].median():.0f} min')
    if not nm_eps.empty:
        print(f'  NOMINAL  episodes   : {len(nm_eps):,}  '
              f'median dur={nm_eps["duration_min"].median():.0f} min')

    v12.to_csv(OUT_DIR / 'v12_history.csv')
    transitions.to_csv(OUT_DIR / 'transitions.csv', index=False)

    # ------------------------------------------------------------------
    # STEP 5 — Independent market labels
    # ------------------------------------------------------------------
    print('\n[5/9] Computing independent market labels …')
    labels_df = build_all_labels(ohlc)
    avail_labels = [c for c in LABEL_COLS if c in labels_df.columns]
    print(f'  Labels computed: {avail_labels}')
    labels_df.to_csv(OUT_DIR / 'market_labels.csv')

    # ------------------------------------------------------------------
    # STEP 6 — Merge and contemporaneous comparison
    # ------------------------------------------------------------------
    print('\n[6/9] Merging V12 with labels and running phase comparison …')
    merged = v12.join(labels_df, how='inner')
    print(f'  Merged rows : {len(merged):,}')

    compare_df = compare_phases(merged, avail_labels)
    print('\n  FIREWALL vs NOMINAL (Mann-Whitney, rank-biserial r):')
    print(compare_df[['label', 'FIREWALL_mean', 'NOMINAL_mean',
                       'rank_biserial_r', 'p_value', 'significant']]
          .to_string(index=False))
    compare_df.to_csv(OUT_DIR / 'compare_phases.csv', index=False)

    # ------------------------------------------------------------------
    # STEP 7 — Predictive + lead-lag
    # ------------------------------------------------------------------
    print('\n[7/9] Predictive validation …')
    pred_df = predictive_correlation(merged, avail_labels, horizons=[1, 3, 6, 12])
    pred_df.to_csv(OUT_DIR / 'predictive_correlations.csv', index=False)

    xcorr = lead_lag_correlation(merged, target_col='realized_vol', max_lag=24)
    xcorr.to_csv(OUT_DIR / 'lead_lag_xcorr.csv')
    peak_lag = int(xcorr.abs().idxmax())
    print(f'  Lead/lag peak: r={xcorr.iloc[xcorr.index.get_loc(peak_lag)]:.3f} '
          f'at lag={peak_lag} bars ({peak_lag*5} min)')

    # ------------------------------------------------------------------
    # STEP 8 — Permutation tests + stability
    # ------------------------------------------------------------------
    print('\n[8/9] Permutation tests and stability analysis …')
    perm_results = []
    for lbl in PERM_LABELS:
        if lbl not in merged.columns:
            continue
        res = permutation_test(merged, lbl, n_permutations=1000)
        perm_results.append(res)
        print(f'  {lbl:<22}  r={res["observed_r"]:+.4f}  '
              f'p_perm={res["p_permutation"]:.4f}')

    stab_year = stability_by_year(merged, avail_labels)
    stab_sess = stability_by_session(merged, avail_labels)
    stab_year.to_csv(OUT_DIR / 'stability_by_year.csv',    index=False)
    stab_sess.to_csv(OUT_DIR / 'stability_by_session.csv', index=False)

    fwd_df = forward_window_analysis(v12, labels_df, transitions,
                                     horizons_bars=[1, 3, 6, 12])
    if not fwd_df.empty:
        fwd_df.to_csv(OUT_DIR / 'forward_window.csv', index=False)

    # ------------------------------------------------------------------
    # STEP 9 — Figures + report
    # ------------------------------------------------------------------
    print('\n[9/9] Generating figures and writing report …')
    generate_all_figures(
        v12=v12, ohlc=ohlc, merged=merged, transitions=transitions,
        xcorr=xcorr, pred_df=pred_df, fwd_df=fwd_df,
        stab_year=stab_year, stab_sess=stab_sess,
        label_cols=avail_labels, out_dir=OUT_DIR,
    )

    report_path = write_report(
        out_dir=OUT_DIR,
        data_summary=data_summary,
        v12=v12, transitions=transitions,
        compare_df=compare_df, pred_df=pred_df,
        perm_results=perm_results,
        stab_year=stab_year, stab_sess=stab_sess,
        fwd_df=fwd_df, xcorr=xcorr,
    )

    elapsed = time.time() - t0
    print(f'\nDone in {elapsed/60:.1f} min.  Results in: {OUT_DIR}')
    print(f'Report  : {report_path}')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--max-files', type=int, default=None,
                        help='Cap BI5 files per year (None = all files)')
    args = parser.parse_args()
    main(max_files=args.max_files)
