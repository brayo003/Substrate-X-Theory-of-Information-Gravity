"""
run_transport_validation_v2.py — SXC-IGC Transport Regime Validation V2
Usage: python run_transport_validation_v2.py [--max-files N] [--max-ticks-2025 N]
"""
import sys, argparse, time, warnings
warnings.filterwarnings('ignore')
from pathlib import Path

_HERE = Path(__file__).resolve().parent
_CE   = _HERE.parents[1]
for p in [str(_CE), str(_HERE)]:
    if p not in sys.path:
        sys.path.insert(0, p)

from v12_validate.loader               import load_all_ticks
from v12_validate.transport_integration import build_full_pipeline
from v12_validate.v2_phase1_2          import phase1_regime_persistence, phase2_volatility_cluster_origin
from v12_validate.v2_phase3            import phase3_lead_lag_comparison
from v12_validate.v2_phase4            import phase4_strategy_regime_matrix
from v12_validate.v2_phase5_6          import phase5_position_sizing, phase6_risk_management
from v12_validate.v2_phase7_8          import phase7_execution_quality, phase8_microstructure
from v12_validate.v2_phase9_10         import phase9_explainability, phase10_practical_value
from v12_validate.v2_report            import (
    ensure_dirs, save_all_csvs,
    plot_regime_durations, plot_markov, plot_volatility_event_profile,
    plot_lead_lag_comparison, plot_strategy_regime_matrix,
    plot_sizing_comparison, plot_microstructure, plot_capability_table,
    build_v2_report, build_market_state_report, build_summary_dashboard,
)


def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument('--max-files',      type=int, default=None)
    p.add_argument('--max-ticks-2025', type=int, default=2_000_000)
    p.add_argument('--data-dir',       type=str, default=str(_HERE / 'data'))
    return p.parse_args()


def main():
    args = parse_args()
    t0   = time.perf_counter()
    out  = ensure_dirs(_HERE)

    print("=" * 60)
    print("SXC-IGC Transport Regime Validation V2")
    print("=" * 60)

    # ── 1. Load ───────────────────────────────────────────────────────────
    print("\n[Load]")
    ticks = load_all_ticks(args.data_dir,
                           max_files_per_year=args.max_files,
                           include_2025=True,
                           max_rows_2025=args.max_ticks_2025)
    print(f"  {len(ticks):,} ticks  "
          f"{ticks['timestamp'].min().date()} → {ticks['timestamp'].max().date()}")

    # ── 2. Pipeline ───────────────────────────────────────────────────────
    print("\n[Pipeline]")
    df, meta = build_full_pipeline(ticks, verbose=True)
    df['year'] = df.index.year

    # ── Phase I ───────────────────────────────────────────────────────────
    print("\n[Phase I] Regime persistence")
    p1  = phase1_regime_persistence(df)
    pp  = p1['persistence']
    print(f"  P(stay COH)={pp['P_stay_coherent']:.3f}  "
          f"P(stay INCOH)={pp['P_stay_incoherent']:.3f}  verdict={pp['verdict']}")

    # ── Phase II ──────────────────────────────────────────────────────────
    print("\n[Phase II] Volatility cluster origin")
    p2  = phase2_volatility_cluster_origin(df)
    s2  = p2['summary']
    print(f"  events={s2['n_events']}  ratio={s2['vol_expansion_ratio']:.3f}  p={s2['mw_p']:.4f}")

    # ── Phase III ─────────────────────────────────────────────────────────
    print("\n[Phase III] Lead-lag vs indicators")
    p3  = phase3_lead_lag_comparison(df)
    ll  = p3['lead_lag_df']
    if len(ll) > 0:
        print(ll[['indicator', 'mean_lead_bars', 'pct_Q_leads']].to_string(index=False))

    # ── Phase IV ──────────────────────────────────────────────────────────
    print("\n[Phase IV] Strategy suitability matrix")
    p4  = phase4_strategy_regime_matrix(df)
    all_trades = p4['all_trades']
    print(f"  total trades={len(all_trades)}")
    if len(p4['summary']) > 0:
        print(p4['summary'][['strategy', 'best_regime', 'pf_difference',
                              'sharpe_difference']].to_string(index=False))

    # ── Phase V ───────────────────────────────────────────────────────────
    print("\n[Phase V] Position sizing")
    p5  = phase5_position_sizing(all_trades)
    if 'comparison' in p5 and len(p5['comparison']) > 0:
        print(p5['comparison'][['label', 'pf', 'sharpe', 'total_ret',
                                 'max_dd']].to_string(index=False))

    # ── Phase VI ──────────────────────────────────────────────────────────
    print("\n[Phase VI] Risk management")
    p6  = phase6_risk_management(df, all_trades)
    if 'rm_summary' in p6 and len(p6['rm_summary']) > 0:
        print(p6['rm_summary'].to_string(index=False))

    # ── Phase VII ─────────────────────────────────────────────────────────
    print("\n[Phase VII] Execution quality")
    p7  = phase7_execution_quality(df)
    print(f"  MW spread p={p7['mw_spread_p']:.4f}")
    if 'exec_df' in p7:
        print(p7['exec_df'].to_string(index=False))

    # ── Phase VIII ────────────────────────────────────────────────────────
    print("\n[Phase VIII] Microstructure")
    p8  = phase8_microstructure(df)
    ms  = p8['micro_summary']
    print(f"  transitions={ms.get('n_transitions',0)}  "
          f"INCOH→COH spread ratio={ms.get('INCOH_COH_spread_ratio',float('nan')):.3f}")

    # ── Phase IX ──────────────────────────────────────────────────────────
    print("\n[Phase IX] Explainability reports")
    p9  = phase9_explainability(df)
    print(f"  {len(p9)} transition reports generated")

    # ── Phase X ───────────────────────────────────────────────────────────
    print("\n[Phase X] Practical value assessment")
    p10 = phase10_practical_value(
        phase1=p1['persistence'],
        phase2=p2,
        phase3=p3,
        phase4=p4,
        phase5=p5,
        phase6=p6,
        phase7=p7,
        phase8={'micro_summary': ms},
        all_trades=all_trades,
        df=df,
    )
    print(f"  Score={p10['avg_score']:.2f}/4  "
          f"Verdict {p10['verdict']}: {p10['verdict_text']}")
    print(p10['capability_table'][['capability', 'rating',
                                    'effect_size']].to_string(index=False))

    # ── Collect ───────────────────────────────────────────────────────────
    results = {
        'p1_run_stats'     : p1['run_stats'],
        'p1_markov'        : p1['markov'],
        'p1_transitions'   : p1['transition_df'],
        'p1_persistence'   : p1['persistence'],
        'p2_profiles'      : p2['event_profiles'],
        'p2_summary'       : p2['summary'],
        'p3_lead_lag'      : p3['lead_lag_df'],
        'p3_detection'     : p3['detection_df'],
        'p4_matrix'        : p4['matrix'],
        'p4_summary'       : p4['summary'],
        'p5_comparison'    : p5.get('comparison'),
        'p5_buckets'       : p5.get('bucket_stats'),
        'p6_rm_summary'    : p6.get('rm_summary'),
        'p7_exec'          : p7.get('exec_df'),
        'p7_exec_dict'     : p7,
        'p8_micro'         : p8['micro_df'],
        'p8_micro_summary' : ms,
        'p9_explain'       : p9,
        'p10_table'        : p10['capability_table'],
        'p10_result'       : p10,
    }

    # ── Write outputs ─────────────────────────────────────────────────────
    print("\n[Output] CSVs …")
    save_all_csvs(results, out)

    print("[Output] Plots …")
    plot_regime_durations(p1['run_stats'], out)
    plot_markov(p1['markov'], out)
    plot_volatility_event_profile(p2['event_profiles'], out)
    plot_lead_lag_comparison(p3['lead_lag_df'], out)
    plot_strategy_regime_matrix(p4['matrix'], out)
    if 'comparison' in p5 and p5['comparison'] is not None:
        plot_sizing_comparison(p5['comparison'], out)
    plot_microstructure(p8['micro_df'], out)
    plot_capability_table(p10['capability_table'],
                          p10['verdict'], p10['verdict_text'], out)

    print("[Output] Reports …")
    build_v2_report(results, out)
    build_market_state_report(results, out)
    build_summary_dashboard(results, df, out)

    print(f"\n{'='*60}")
    print(f"V2 complete in {time.perf_counter()-t0:.1f} s  |  Results: {out}")
    print("=" * 60)


if __name__ == '__main__':
    main()
