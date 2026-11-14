"""
run_transport_validation.py — Orchestrate the full SXC-IGC transport validation.

Usage:
    python run_transport_validation.py [--max-files N] [--c FLOAT] [--tau FLOAT]

Produces results/ with all CSVs, plots, and transport_validation_report.md.
"""
import sys
import argparse
import time
from pathlib import Path

# ── path setup ────────────────────────────────────────────────────────────
_HERE = Path(__file__).resolve().parent          # finance_module/
_CE   = _HERE.parents[1]                         # calibration_engine/
if str(_CE) not in sys.path:
    sys.path.insert(0, str(_CE))
if str(_HERE) not in sys.path:
    sys.path.insert(0, str(_HERE))

# ── imports ───────────────────────────────────────────────────────────────
from v12_validate.loader import load_all_ticks
from v12_validate.transport_integration import build_full_pipeline
from v12_validate.historical_validation import (
    run_strategy, compute_strategy_metrics, compare_strategies,
)
from v12_validate.statistical_analysis import run_all_analyses
from v12_validate.performance_profiler import (
    profile_transport_layer, profile_full_pipeline,
)
from v12_validate.report_generator import generate_all_outputs


def parse_args():
    p = argparse.ArgumentParser(description="SXC-IGC Transport Validation")
    p.add_argument("--max-files", type=int, default=None,
                   help="Max BI5 files per year (None = all)")
    p.add_argument("--max-ticks-2025", type=int, default=2_000_000,
                   help="Max rows from 2025 CSV (default 2M)")
    p.add_argument("--c",   type=float, default=1.0, help="Transport speed c")
    p.add_argument("--tau", type=float, default=5.0, help="Relaxation time tau (bars)")
    p.add_argument("--data-dir", type=str,
                   default=str(_HERE / "data"),
                   help="Path to data/ directory")
    return p.parse_args()


def main():
    args = parse_args()
    t_start = time.perf_counter()

    print("=" * 60)
    print("SXC-IGC Transport Validation")
    print(f"  c={args.c}  tau={args.tau}  data={args.data_dir}")
    print("=" * 60)

    # ── 1. Load data ──────────────────────────────────────────────────────
    print("\n[1/6] Loading tick data …")
    data_dir = Path(args.data_dir)
    ticks = load_all_ticks(
        data_dir,
        max_files_per_year=args.max_files,
        include_2025=True,
        max_rows_2025=args.max_ticks_2025,
    )
    print(f"  Loaded {len(ticks):,} ticks  "
          f"({ticks['timestamp'].min().date()} → {ticks['timestamp'].max().date()})")

    # ── 2. Build full pipeline ────────────────────────────────────────────
    print("\n[2/6] Running transport pipeline …")
    df, meta = build_full_pipeline(
        ticks, c=args.c, tau=args.tau, verbose=True
    )
    df['year'] = df.index.year

    # ── 3. Strategy A + B ─────────────────────────────────────────────────
    print("\n[3/6] Running strategies A and B …")
    trade_log, strategy_comparison, equity_df = compare_strategies(df)
    print(f"  Strategy A: {(strategy_comparison.loc[0,'n_trades'] if len(strategy_comparison)>0 else 0)} trades")
    print(f"  Strategy B: {(strategy_comparison.loc[1,'n_trades'] if len(strategy_comparison)>0 else 0)} trades")

    # Split logs for analysis
    log_A = trade_log[trade_log['strategy'] == 'A'] if len(trade_log) > 0 else trade_log
    log_B = trade_log[trade_log['strategy'] == 'B'] if len(trade_log) > 0 else trade_log

    # ── 4. Statistical analysis ───────────────────────────────────────────
    print("\n[4/6] Running statistical analyses …")
    stats = run_all_analyses(df, log_A, log_B, verbose=True)

    # ── 5. Performance profiling ──────────────────────────────────────────
    print("\n[5/6] Profiling performance …")
    from v12_validate.signals import build_signals_from_ticks
    _, _, _, composite = build_signals_from_ticks(ticks)
    perf_layer = profile_transport_layer(composite, c=args.c, tau=args.tau)
    perf_full  = profile_full_pipeline(ticks, c=args.c, tau=args.tau)
    print(f"  Transport layer: {perf_layer['full_pipeline_per_bar_us']:.2f} μs/bar  "
          f"({perf_layer['full_pipeline_bars_per_sec']:,.0f} bars/s)")
    print(f"  Peak memory    : {perf_layer['peak_memory_mb']:.2f} MB")
    print(f"  Live practical : {'YES' if perf_full['practical_for_live_trading'] else 'NO'}")

    # ── 6. Generate all outputs ───────────────────────────────────────────
    print("\n[6/6] Generating outputs …")
    generate_all_outputs(
        df=df,
        meta=meta,
        stats=stats,
        trade_log=trade_log if len(trade_log) > 0 else None,
        strategy_comparison=strategy_comparison if len(strategy_comparison) > 0 else None,
        equity_df=equity_df if len(equity_df) > 0 else None,
        perf_full=perf_full,
        perf_layer=perf_layer,
        base_dir=_HERE,
        verbose=True,
    )

    elapsed = time.perf_counter() - t_start
    print(f"\n{'='*60}")
    print(f"Validation complete in {elapsed:.1f} s")
    print(f"Results in: {_HERE / 'results'}")
    print("=" * 60)


if __name__ == "__main__":
    main()
