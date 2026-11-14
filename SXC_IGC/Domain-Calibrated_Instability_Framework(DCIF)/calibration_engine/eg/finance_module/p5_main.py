"""
p5_main.py — Phase 5 Master Orchestrator.

TRUE OUT-OF-SAMPLE VALIDATION (2026)

Runs the complete Phase 5 pipeline in strict sequence:
  1. Load 2026 data for all 7 markets
  2. Execute frozen Transport OS (no recalibration, no leakage)
  3. Compute per-market statistics + Phase 4 vs Phase 5 comparison
  4. Run drift analysis with statistical tests
  5. Generate all plots
  6. Write all deliverable files (CSVs + Markdown reports)

FROZEN COMPONENTS — used WITHOUT modification:
  Transport equations, Q calculation, DCII, regime thresholds,
  Transport OS, allocator tables, risk allocation, stop policies,
  scheduler, NoTrade logic, everything.

2026 is PURE OUT-OF-SAMPLE.
"""

import sys
import time
import warnings
import traceback
from pathlib import Path
from datetime import datetime

import pandas as pd
import numpy as np

warnings.filterwarnings("ignore")

_HERE = Path(__file__).resolve().parent
for p in [str(_HERE), str(_HERE / "v12_validate")]:
    if p not in sys.path:
        sys.path.insert(0, p)

PHASE5_DIR = _HERE / "results" / "phase5"
MARKET_ORDER = ["EURUSD", "BTCUSDT", "ETHUSDT", "NAS100", "XAUUSD", "USOIL", "UKOIL"]


# ──────────────────────────────────────────────────────────────────────────
# Logging helpers
# ──────────────────────────────────────────────────────────────────────────

def _banner(msg: str, char: str = "═", width: int = 70):
    print(f"\n{char * width}", flush=True)
    print(f"  {msg}", flush=True)
    print(f"{char * width}", flush=True)


def _section(msg: str):
    print(f"\n── {msg} {'─' * max(0, 65 - len(msg))}", flush=True)


def _ok(msg: str):
    print(f"  ✓ {msg}", flush=True)


def _warn(msg: str):
    print(f"  ⚠  {msg}", flush=True)


def _fail(msg: str):
    print(f"  ✗ {msg}", flush=True)


# ──────────────────────────────────────────────────────────────────────────
# Step 1 — Load 2026 data
# ──────────────────────────────────────────────────────────────────────────

def step1_load_data(verbose: bool = True):
    _section("STEP 1: Load 2026 out-of-sample data")
    from p5_data_loader import load_all_markets_2026, ensure_dirs, get_q_stats_2026

    ensure_dirs()
    t0 = time.time()
    data = load_all_markets_2026(verbose=verbose)
    elapsed = time.time() - t0

    if not data:
        raise RuntimeError("No 2026 data loaded — check data directory")

    _ok(f"Loaded {len(data)} markets in {elapsed:.1f}s")
    for sym, df in data.items():
        q_stats = get_q_stats_2026(df)
        print(f"    {sym:10s}: {len(df):>8,} bars | "
              f"Q_mean={q_stats.get('q_mean', 0):+.3f} | "
              f"coherent={q_stats.get('q_coherent_frac', 0):.1%}", flush=True)

    return data


# ──────────────────────────────────────────────────────────────────────────
# Step 2 — Replay frozen OS
# ──────────────────────────────────────────────────────────────────────────

def step2_replay(data: dict, force_replay: bool = False, verbose: bool = True):
    _section("STEP 2: Replay frozen Transport OS on 2026 data")
    from p5_engine import (
        run_phase5_replay,
        save_replay_results,
        load_cached_replay_results,
    )

    # Check for cached replay
    cache_dir = PHASE5_DIR / "cache"
    cached_trades = list(cache_dir.glob("trades_2026_*.parquet")) if cache_dir.exists() else []

    if not force_replay and len(cached_trades) >= len(data):
        _ok(f"Found {len(cached_trades)} cached replay files — loading from cache")
        trade_logs, bar_logs = load_cached_replay_results()
        all_cached = all(sym in trade_logs for sym in data)
        if all_cached:
            for sym in MARKET_ORDER:
                if sym in trade_logs:
                    n_trades = len(trade_logs[sym])
                    bl = bar_logs.get(sym, pd.DataFrame())
                    n_bars = len(bl)
                    no_trade_pct = 0.0
                    if len(bl) > 0 and "no_trade" in bl.columns:
                        no_trade_pct = 100.0 * bl["no_trade"].mean()
                    print(f"    {sym:10s}: {n_trades:>5} trades | {n_bars:>8,} bars | "
                          f"NoTrade={no_trade_pct:.1f}% (cached)", flush=True)
            return trade_logs, bar_logs
        _warn("Cache incomplete — running full replay")

    # Clear cache if forcing
    if force_replay and cache_dir.exists():
        for f in cache_dir.glob("trades_2026_*.parquet"):
            f.unlink()
        for f in cache_dir.glob("barlogs_2026_*.parquet"):
            f.unlink()

    t0 = time.time()
    trade_logs, bar_logs = run_phase5_replay(data, markets=MARKET_ORDER, verbose=verbose)
    elapsed = time.time() - t0

    save_replay_results(trade_logs, bar_logs)

    total_trades = sum(len(v) for v in trade_logs.values())
    _ok(f"Replay complete in {elapsed:.1f}s — {total_trades:,} total trades across {len(trade_logs)} markets")

    for sym in MARKET_ORDER:
        tl = trade_logs.get(sym)
        bl = bar_logs.get(sym)
        n_trades = len(tl) if tl is not None else 0
        n_bars   = len(bl) if bl is not None else 0
        no_trade_pct = 0.0
        if bl is not None and len(bl) > 0 and "no_trade" in bl.columns:
            no_trade_pct = 100.0 * bl["no_trade"].mean()
        print(f"    {sym:10s}: {n_trades:>5} trades | {n_bars:>8,} bars | "
              f"NoTrade={no_trade_pct:.1f}%", flush=True)

    return trade_logs, bar_logs


# ──────────────────────────────────────────────────────────────────────────
# Step 3 — Compute statistics
# ──────────────────────────────────────────────────────────────────────────

def step3_statistics(trade_logs: dict, bar_logs: dict, verbose: bool = True):
    _section("STEP 3: Compute per-market statistics (2025 vs 2026)")
    from p5_statistics import (
        compute_all_stats_2026,
        build_comparison_table,
        load_phase4_stats,
        build_market_summary_csv,
        compute_regime_breakdown_2026,
    )

    t0 = time.time()

    # 2026 stats: returns (summary_df, stats_dict)
    stats_df_2026, stats_2026 = compute_all_stats_2026(
        trade_logs, bar_logs, verbose=verbose
    )
    _ok(f"2026 stats computed for {len(stats_2026)} markets")

    # 2025 stats (loaded from Phase 4 files — no recalculation)
    stats_2025 = load_phase4_stats()
    if not stats_2025:
        _warn("Phase 4 stats not found — 2025 column will be empty in comparison")
    else:
        _ok(f"2025 stats loaded for {len(stats_2025)} markets")

    # Build comparison and market summary
    comparison_df    = build_comparison_table(stats_2026, stats_2025)
    market_summary_df = build_market_summary_csv(stats_2026)
    regime_breakdown  = compute_regime_breakdown_2026(trade_logs, bar_logs)

    elapsed = time.time() - t0
    _ok(f"Statistics pipeline complete in {elapsed:.1f}s")

    if verbose:
        print("\n  2026 Per-Market Summary:", flush=True)
        print(f"  {'Symbol':10s} {'PF':>6} {'Sharpe':>7} {'WinRate':>8} "
              f"{'Trades':>7} {'NoTrd%':>7} {'MaxDD':>7}", flush=True)
        print(f"  {'─'*10} {'─'*6} {'─'*7} {'─'*8} {'─'*7} {'─'*7} {'─'*7}", flush=True)
        for sym in MARKET_ORDER:
            if sym in stats_2026:
                s = stats_2026[sym]
                print(f"  {sym:10s} {s.get('profit_factor', 0):>6.3f} "
                      f"{s.get('sharpe', 0):>7.3f} "
                      f"{s.get('win_rate', 0):>8.1%} "
                      f"{s.get('n_trades', 0):>7} "
                      f"{s.get('no_trade_pct', 0):>6.1f}% "
                      f"{s.get('max_drawdown', 0):>7.4f}", flush=True)

    return stats_2025, stats_2026, comparison_df, market_summary_df, regime_breakdown


# ──────────────────────────────────────────────────────────────────────────
# Step 4 — Drift analysis
# ──────────────────────────────────────────────────────────────────────────

def step4_drift(
    data: dict,
    trade_logs: dict,
    bar_logs: dict,
    stats_2025: dict,
    stats_2026: dict,
    verbose: bool = True,
):
    _section("STEP 4: Drift analysis (2025 → 2026)")
    from p5_drift import compute_all_drift

    t0 = time.time()
    drift_results = compute_all_drift(
        all_data_2026=data,
        all_trade_logs_2026=trade_logs,
        stats_2025=stats_2025,
        stats_2026=stats_2026,
        verbose=verbose,
    )
    elapsed = time.time() - t0

    _ok(f"Drift analysis complete in {elapsed:.1f}s")

    # Print drift indices summary
    transport_drift = drift_results.get("transport_drift")
    if transport_drift is not None and len(transport_drift) > 0:
        print("\n  Drift Index Summary:", flush=True)
        numeric_cols = [c for c in transport_drift.columns if c != "symbol"]
        for col in numeric_cols[:8]:
            vals = pd.to_numeric(transport_drift[col], errors="coerce").dropna()
            if len(vals) > 0:
                print(f"    {col:35s}: mean={vals.mean():.4f} | max={vals.max():.4f}", flush=True)

    return drift_results


# ──────────────────────────────────────────────────────────────────────────
# Step 5 — Generate plots
# ──────────────────────────────────────────────────────────────────────────

def step5_visuals(
    data: dict,
    trade_logs: dict,
    bar_logs: dict,
    stats_2025: dict,
    stats_2026: dict,
    drift_results: dict,
    verbose: bool = True,
):
    _section("STEP 5: Generate all plots")
    from p5_visuals import run_all_visuals

    t0 = time.time()
    try:
        run_all_visuals(
            all_data_2026=data,
            all_trade_logs=trade_logs,
            all_bar_logs=bar_logs,
            stats_2025=stats_2025,
            stats_2026=stats_2026,
            drift_results=drift_results,
            verbose=verbose,
        )
        elapsed = time.time() - t0
        plots_dir = PHASE5_DIR / "plots"
        n_plots = len(list(plots_dir.glob("*.png"))) if plots_dir.exists() else 0
        _ok(f"Generated {n_plots} plots in {elapsed:.1f}s → {plots_dir}")
    except Exception as e:
        _warn(f"Visuals failed: {e}")
        traceback.print_exc()


# ──────────────────────────────────────────────────────────────────────────
# Step 6 — Write deliverables
# ──────────────────────────────────────────────────────────────────────────

def step6_deliverables(
    trade_logs: dict,
    bar_logs: dict,
    market_summary_df: pd.DataFrame,
    comparison_df: pd.DataFrame,
    regime_breakdown: pd.DataFrame,
    drift_results: dict,
    stats_2025: dict,
    stats_2026: dict,
    verbose: bool = True,
):
    _section("STEP 6: Write all deliverable files")
    from p5_report import save_all_deliverables

    t0 = time.time()
    save_all_deliverables(
        all_trade_logs=trade_logs,
        all_bar_logs=bar_logs,
        market_summary_df=market_summary_df,
        comparison_df=comparison_df,
        regime_breakdown=regime_breakdown,
        drift_results=drift_results,
        stats_2025=stats_2025,
        stats_2026=stats_2026,
        verbose=verbose,
    )
    elapsed = time.time() - t0
    _ok(f"All deliverables written in {elapsed:.1f}s → {PHASE5_DIR}")


# ──────────────────────────────────────────────────────────────────────────
# Step 7 — Verify deliverables
# ──────────────────────────────────────────────────────────────────────────

REQUIRED_CSVS = [
    "trade_log_2026.csv",
    "market_summary_2026.csv",
    "performance_2025_vs_2026.csv",
    "transport_drift.csv",
    "statistical_tests.csv",
]

REQUIRED_MDS = [
    "phase5_summary.md",
    "scientific_questions.md",
]

REQUIRED_PLOTS = [
    "equity_curves.png",
    "regime_comparison.png",
    "pf_comparison.png",
    "drawdown_comparison.png",
    "notrade_comparison.png",
]


def step7_verify(verbose: bool = True) -> bool:
    _section("STEP 7: Verify deliverables")

    all_ok = True
    plots_dir = PHASE5_DIR / "plots"

    print("\n  CSVs:", flush=True)
    for fname in REQUIRED_CSVS:
        p = PHASE5_DIR / fname
        if p.exists():
            size_kb = p.stat().st_size / 1024
            _ok(f"{fname} ({size_kb:.1f} KB)")
        else:
            _fail(f"{fname} — MISSING")
            all_ok = False

    print("\n  Markdown reports:", flush=True)
    for fname in REQUIRED_MDS:
        p = PHASE5_DIR / fname
        if p.exists():
            lines = len(p.read_text().splitlines())
            _ok(f"{fname} ({lines} lines)")
        else:
            _fail(f"{fname} — MISSING")
            all_ok = False

    print("\n  Plots:", flush=True)
    for fname in REQUIRED_PLOTS:
        p = plots_dir / fname
        if p.exists():
            size_kb = p.stat().st_size / 1024
            _ok(f"plots/{fname} ({size_kb:.1f} KB)")
        else:
            _warn(f"plots/{fname} — not found (optional)")

    # List all files actually produced
    all_files = sorted(PHASE5_DIR.rglob("*")) if PHASE5_DIR.exists() else []
    n_files = len([f for f in all_files if f.is_file()])
    print(f"\n  Total files in {PHASE5_DIR.name}/: {n_files}", flush=True)

    if all_ok:
        _ok("All required deliverables verified.")
    else:
        _warn("Some deliverables are missing — check logs above.")

    return all_ok


# ──────────────────────────────────────────────────────────────────────────
# Master orchestrator
# ──────────────────────────────────────────────────────────────────────────

def run_phase5(
    verbose: bool = True,
    skip_visuals: bool = False,
    force_replay: bool = False,
) -> dict:
    """
    Execute the full Phase 5 pipeline.

    Args:
        verbose:       Print detailed progress
        skip_visuals:  Skip plot generation (useful for headless environments)
        force_replay:  Force re-replay even if cache exists
    """
    t_total = time.time()
    ts = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")

    _banner("PHASE 5 — TRUE OUT-OF-SAMPLE VALIDATION (2026)")
    print(f"  Started: {ts}", flush=True)
    print(f"  Purpose: Validate frozen Transport OS on unseen 2026 data", flush=True)
    print(f"  Markets: {', '.join(MARKET_ORDER)}", flush=True)
    print(f"  Rule:    NO recalibration | NO leakage | NO lookahead", flush=True)

    errors = []

    # ── Step 1: Load data ──────────────────────────────────────────────────
    try:
        data = step1_load_data(verbose=verbose)
    except Exception as e:
        _fail(f"Step 1 failed: {e}")
        traceback.print_exc()
        raise

    # ── Step 2: Replay ────────────────────────────────────────────────────
    try:
        trade_logs, bar_logs = step2_replay(
            data, force_replay=force_replay, verbose=verbose
        )
    except Exception as e:
        _fail(f"Step 2 failed: {e}")
        traceback.print_exc()
        raise

    # ── Step 3: Statistics ────────────────────────────────────────────────
    stats_2025 = {}
    stats_2026 = {}
    comparison_df     = pd.DataFrame()
    market_summary_df = pd.DataFrame()
    regime_breakdown  = pd.DataFrame()
    try:
        stats_2025, stats_2026, comparison_df, market_summary_df, regime_breakdown = \
            step3_statistics(trade_logs, bar_logs, verbose=verbose)
    except Exception as e:
        _fail(f"Step 3 failed: {e}")
        traceback.print_exc()
        errors.append(("statistics", str(e)))

    # ── Step 4: Drift ─────────────────────────────────────────────────────
    drift_results = {}
    try:
        drift_results = step4_drift(
            data, trade_logs, bar_logs, stats_2025, stats_2026, verbose=verbose
        )
    except Exception as e:
        _fail(f"Step 4 failed: {e}")
        traceback.print_exc()
        errors.append(("drift", str(e)))

    # ── Step 5: Visuals ───────────────────────────────────────────────────
    if not skip_visuals:
        try:
            step5_visuals(
                data, trade_logs, bar_logs, stats_2025, stats_2026,
                drift_results, verbose=verbose
            )
        except Exception as e:
            _warn(f"Step 5 (visuals) failed: {e}")
            traceback.print_exc()
            errors.append(("visuals", str(e)))
    else:
        _warn("Visuals skipped (skip_visuals=True)")

    # ── Step 6: Deliverables ──────────────────────────────────────────────
    try:
        step6_deliverables(
            trade_logs, bar_logs, market_summary_df, comparison_df,
            regime_breakdown, drift_results, stats_2025, stats_2026,
            verbose=verbose,
        )
    except Exception as e:
        _fail(f"Step 6 failed: {e}")
        traceback.print_exc()
        errors.append(("deliverables", str(e)))

    # ── Step 7: Verify ────────────────────────────────────────────────────
    all_ok = step7_verify(verbose=verbose)

    # ── Final summary ─────────────────────────────────────────────────────
    elapsed_total = time.time() - t_total
    _banner(f"PHASE 5 COMPLETE — {elapsed_total:.0f}s total", char="═")

    if errors:
        _warn(f"Completed with {len(errors)} non-fatal errors:")
        for stage, msg in errors:
            print(f"    [{stage}] {msg}", flush=True)
    else:
        _ok("Pipeline completed with no errors.")

    # Quick results summary
    _section("Quick Results Summary")
    if stats_2026:
        profitable = sum(
            1 for s in stats_2026.values()
            if s.get("profit_factor", 0) >= 1.0
        )
        total_trades = sum(s.get("n_trades", 0) for s in stats_2026.values())
        pf_vals  = [s.get("profit_factor", 0) for s in stats_2026.values()]
        shr_vals = [s.get("sharpe", 0) for s in stats_2026.values()]
        avg_pf   = float(np.mean(pf_vals)) if pf_vals else 0.0
        avg_shr  = float(np.mean(shr_vals)) if shr_vals else 0.0
        print(f"  Markets profitable (PF≥1): {profitable}/{len(stats_2026)}", flush=True)
        print(f"  Total trades (2026):        {total_trades:,}", flush=True)
        print(f"  Mean PF (2026):             {avg_pf:.3f}", flush=True)
        print(f"  Mean Sharpe (2026):         {avg_shr:.3f}", flush=True)

    print(f"\n  Deliverables at: {PHASE5_DIR}", flush=True)
    print(f"  Phase 5 validation complete: {datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')}", flush=True)

    return {
        "data"             : data,
        "trade_logs"       : trade_logs,
        "bar_logs"         : bar_logs,
        "stats_2025"       : stats_2025,
        "stats_2026"       : stats_2026,
        "comparison_df"    : comparison_df,
        "market_summary_df": market_summary_df,
        "regime_breakdown" : regime_breakdown,
        "drift_results"    : drift_results,
        "all_ok"           : all_ok,
        "errors"           : errors,
    }


# ──────────────────────────────────────────────────────────────────────────
# CLI entry point
# ──────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Phase 5 — True Out-of-Sample Validation (2026)"
    )
    parser.add_argument(
        "--quiet", action="store_true",
        help="Suppress verbose output"
    )
    parser.add_argument(
        "--no-visuals", action="store_true",
        help="Skip plot generation (faster, headless-safe)"
    )
    parser.add_argument(
        "--force-replay", action="store_true",
        help="Force fresh replay even if cache exists"
    )
    args = parser.parse_args()

    results = run_phase5(
        verbose=not args.quiet,
        skip_visuals=args.no_visuals,
        force_replay=args.force_replay,
    )

    # Exit code: 0 if all ok, 1 if errors
    sys.exit(0 if results["all_ok"] else 1)
