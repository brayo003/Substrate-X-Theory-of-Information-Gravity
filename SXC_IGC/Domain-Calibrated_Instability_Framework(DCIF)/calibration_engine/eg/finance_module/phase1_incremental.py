"""
phase1_incremental.py — Master orchestrator for Phase 1 Transport Strategy Matrix Validation.

Usage:
    python phase1_incremental.py [--data-dir PATH] [--years 2023 2024 2025]
                                 [--force-rebuild] [--bootstrap-iters N]
                                 [--status]

Resume behaviour:
    - Reads checkpoints/checkpoint_manifest.json
    - Skips every already-completed stage
    - For strategies: skips individual strategies that are already done
    - Can be interrupted at any point and safely re-run

Memory target: < 2 GB RAM
  - One month of data at a time (cache layer)
  - One strategy at a time (strategy runner)
  - Intermediate results on disk (parquet)

Pipeline:
  Stage 0 — Ensure directories + load/create manifest
  Stage 1 — Build monthly OHLC+transport cache (one month at a time)
  Stage 2 — Build Q series and compute global quantile thresholds
  Stage 3 — Run all strategies incrementally (one strategy × one month at a time)
  Stage 4 — Statistical analysis (bootstrap CI, significance tests)
  Stage 5 — Regime analysis (Markov, entropy, persistence)
  Stage 6 — Strategy allocator (best per regime)
  Stage 7 — Visualizations (heatmaps, Markov, durations)
  Stage 8 — Final report (phase1_strategy_matrix.md, all 8 questions)
"""

import sys
import argparse
import time
import warnings
import gc
from pathlib import Path

warnings.filterwarnings("ignore")

_HERE = Path(__file__).resolve().parent
_CE   = _HERE.parents[1]
for p in [str(_CE), str(_HERE), str(_HERE / "v12_validate")]:
    if p not in sys.path:
        sys.path.insert(0, p)

# ── Pipeline modules ──────────────────────────────────────────────────────
from p1_checkpoint import (
    ensure_dirs,
    load_manifest, save_manifest,
    mark_cache_complete, mark_q_series_complete,
    pipeline_status,
    CACHE_DIR, RESULTS_DIR,
)
from p1_data_stream import (
    iter_months,
    build_q_series,
    compute_global_q_quantiles,
)
from p1_strategy_runner import run_all_strategies_incremental
from p1_statistics import run_full_statistics
from p1_regime_analysis import run_regime_analysis
from p1_allocator import run_allocator
from p1_visualize import run_visualizations
from p1_report import run_report

# ── Strategy library (immutable existing code) ────────────────────────────
from strategy_library import get_all_strategies, get_families


# ═══════════════════════════════════════════════════════════════════════════
# CLI
# ═══════════════════════════════════════════════════════════════════════════

def parse_args():
    p = argparse.ArgumentParser(
        description="Phase 1 Transport Strategy Matrix Validation — incremental pipeline"
    )
    p.add_argument("--data-dir", type=str, default=str(_HERE / "data"),
                   help="Path to data/ directory")
    p.add_argument("--years", type=int, nargs="+", default=[2023, 2024, 2025],
                   help="Years to process (default: 2023 2024 2025)")
    p.add_argument("--force-rebuild", action="store_true",
                   help="Ignore all caches and recompute from scratch")
    p.add_argument("--bootstrap-iters", type=int, default=1000,
                   help="Bootstrap iterations for CI (default: 1000)")
    p.add_argument("--status", action="store_true",
                   help="Print pipeline status and exit")
    p.add_argument("--skip-plots", action="store_true",
                   help="Skip visualization stage")
    return p.parse_args()


# ═══════════════════════════════════════════════════════════════════════════
# Stage helpers
# ═══════════════════════════════════════════════════════════════════════════

def _banner(text: str):
    print(f"\n{'='*70}")
    print(f"  {text}")
    print(f"{'='*70}", flush=True)


def _stage(n: int, total: int, name: str):
    print(f"\n[{n}/{total}] {name}", flush=True)


# ═══════════════════════════════════════════════════════════════════════════
# Main
# ═══════════════════════════════════════════════════════════════════════════

def main():
    args     = parse_args()
    t_start  = time.perf_counter()
    data_dir = Path(args.data_dir)
    STAGES   = 8

    _banner("Phase 1 — Transport Strategy Matrix Validation (EUR/USD)")
    print(f"  Data dir  : {data_dir}")
    print(f"  Years     : {args.years}")
    print(f"  Bootstrap : {args.bootstrap_iters} iterations")
    print(f"  Force     : {args.force_rebuild}", flush=True)

    # ── Stage 0: Initialise ───────────────────────────────────────────────
    ensure_dirs()
    manifest = load_manifest()

    if args.force_rebuild:
        print("  Force-rebuild: resetting manifest pipeline flags …")
        manifest["pipeline"] = {
            "data_cache_complete": False,
            "q_series_complete": False,
            "q_quantiles": None,
            "strategies_complete": [],
            "stats_complete": False,
            "regime_analysis_complete": False,
            "allocator_complete": False,
            "heatmap_complete": False,
            "report_complete": False,
        }
        save_manifest(manifest)

    if args.status:
        print("\nPipeline status:")
        print(pipeline_status(manifest))
        return

    print("\nCurrent pipeline status:")
    print(pipeline_status(manifest))

    # ── Stage 1: Build monthly cache ──────────────────────────────────────
    _stage(1, STAGES, "Building monthly OHLC + transport cache")
    if not manifest["pipeline"]["data_cache_complete"] or args.force_rebuild:
        month_count = 0
        bar_count   = 0
        for year, month_1, df in iter_months(
            data_dir, years=args.years,
            force_rebuild=args.force_rebuild, verbose=True
        ):
            month_count += 1
            bar_count   += len(df)
            del df
            gc.collect()

        stats = {"months_processed": month_count, "total_bars_approx": bar_count}
        mark_cache_complete(manifest, stats)
        print(f"  Cache complete: {month_count} months, ~{bar_count:,} bars total", flush=True)
    else:
        cached = list(CACHE_DIR.glob("ohlc_transport_*.parquet"))
        print(f"  [SKIP] Cache already built ({len(cached)} month files)", flush=True)

    # ── Stage 2: Q series + quantile thresholds ───────────────────────────
    _stage(2, STAGES, "Building Q series + global quantile thresholds")
    if not manifest["pipeline"]["q_series_complete"] or args.force_rebuild:
        q_series = build_q_series(
            data_dir, years=args.years,
            force_rebuild=args.force_rebuild, verbose=True
        )
        q_quantiles = compute_global_q_quantiles(q_series)
        del q_series
        gc.collect()
        mark_q_series_complete(manifest, q_quantiles)
        print(f"  Q quantiles: q05={q_quantiles['q05']:.6f}  "
              f"q95={q_quantiles['q95']:.6f}  "
              f"coherent={q_quantiles['coherent_fraction']:.4f}", flush=True)
    else:
        q_quantiles = manifest["pipeline"]["q_quantiles"]
        print(f"  [SKIP] Q series already built. "
              f"q05={q_quantiles['q05']:.6f}  q95={q_quantiles['q95']:.6f}", flush=True)

    # ── Stage 3: Strategy execution ───────────────────────────────────────
    _stage(3, STAGES, "Running all strategies incrementally")
    strategy_registry = get_all_strategies()
    print(f"  Strategy registry: {len(strategy_registry)} strategies across "
          f"{len(get_families())} families")

    for fam, names in sorted(get_families().items()):
        print(f"    {fam:<16}: {', '.join(names)}")
    print(flush=True)

    run_all_strategies_incremental(
        strategy_registry=strategy_registry,
        data_dir=data_dir,
        manifest=manifest,
        q_quantiles=q_quantiles,
        years=tuple(args.years),
        verbose=True,
    )

    total_trades = sum(manifest["strategy_trade_counts"].values())
    print(f"\n  Total trades across all strategies: {total_trades:,}", flush=True)

    # ── Stage 4: Statistical analysis ────────────────────────────────────
    _stage(4, STAGES, "Statistical analysis (bootstrap CI + significance tests)")
    if not manifest["pipeline"]["stats_complete"] or args.force_rebuild:
        matrix_df, boot_df, sig_df = run_full_statistics(
            strategy_registry=strategy_registry,
            manifest=manifest,
            n_boot=args.bootstrap_iters,
            verbose=True,
        )
    else:
        print("  [SKIP] Stats already computed", flush=True)

    # ── Stage 5: Regime analysis ──────────────────────────────────────────
    _stage(5, STAGES, "Regime analysis (Markov, entropy, persistence)")
    if not manifest["pipeline"]["regime_analysis_complete"] or args.force_rebuild:
        stab_df, markov_df, catalog_df = run_regime_analysis(
            q_quantiles=q_quantiles,
            manifest=manifest,
            verbose=True,
        )
    else:
        print("  [SKIP] Regime analysis already complete", flush=True)

    # ── Stage 6: Allocator ────────────────────────────────────────────────
    _stage(6, STAGES, "Strategy allocator (best per regime)")
    if not manifest["pipeline"]["allocator_complete"] or args.force_rebuild:
        best_df = run_allocator(manifest=manifest, verbose=True)
    else:
        print("  [SKIP] Allocator already complete", flush=True)

    # ── Stage 7: Visualizations ───────────────────────────────────────────
    _stage(7, STAGES, "Generating visualizations")
    if not args.skip_plots and (
        not manifest["pipeline"]["heatmap_complete"] or args.force_rebuild
    ):
        run_visualizations(manifest=manifest, verbose=True)
    else:
        reason = "skip-plots flag" if args.skip_plots else "already complete"
        print(f"  [SKIP] Visualizations ({reason})", flush=True)

    # ── Stage 8: Final report ─────────────────────────────────────────────
    _stage(8, STAGES, "Generating final report")
    elapsed = time.perf_counter() - t_start
    if not manifest["pipeline"]["report_complete"] or args.force_rebuild:
        run_report(manifest=manifest, elapsed_sec=elapsed, verbose=True)
    else:
        print("  [SKIP] Report already complete", flush=True)

    # ── Completion summary ────────────────────────────────────────────────
    elapsed = time.perf_counter() - t_start
    _banner("Phase 1 Complete")
    print(f"  Elapsed: {elapsed:.1f}s ({elapsed/60:.1f} min)")
    print(f"  Results: {RESULTS_DIR}")
    print()
    print("  Deliverables:")
    deliverables = [
        "phase1_strategy_matrix.md",
        "phase1_strategy_matrix.csv",
        "strategy_rankings.csv",
        "best_strategy_per_regime.csv",
        "performance_by_regime.csv",
        "bootstrap_statistics.csv",
        "significance_tests.csv",
        "regime_transition_statistics.csv",
        "regime_transitions_catalog.csv",
        "markov_matrix.csv",
        "strategy_allocator_report.md",
        "execution_profile.md",
        "plots/strategy_regime_heatmap.png",
        "plots/strategy_regime_heatmap_sharpe.png",
        "plots/regime_markov.png",
        "plots/regime_durations.png",
        "plots/regime_q_distribution.png",
    ]
    for d in deliverables:
        path = RESULTS_DIR / d
        status = "✓" if path.exists() else "✗ MISSING"
        print(f"    {status}  {d}")

    # Checkpoint manifest
    import shutil
    import json
    manifest_src = Path(__file__).parent / "checkpoints" / "checkpoint_manifest.json"
    if manifest_src.exists():
        shutil.copy(manifest_src, RESULTS_DIR / "checkpoint_manifest.json")
        print(f"    ✓  checkpoint_manifest.json")

    print(flush=True)


if __name__ == "__main__":
    main()
