"""
phase2_transport_os.py — Master orchestrator for Phase 2 Transport OS Validation.

Usage:
    python phase2_transport_os.py [--force] [--status] [--skip-plots]

Stages:
  1. Calibrate Transport OS from Phase 1 statistics
  2. Replay Transport OS over all cached monthly data
  3. Replay all fixed baselines
  4. Compute statistics and run significance tests
  5. Generate visualizations
  6. Write reports

Checkpoint/resume:
  Reads/writes results/phase2/p2_checkpoint.json
  Each stage is idempotent — re-run safely.
"""

import sys
import argparse
import json
import time
import gc
import warnings
from pathlib import Path

warnings.filterwarnings("ignore")

_HERE = Path(__file__).resolve().parent
_CE   = _HERE.parents[1]
for p in [str(_CE), str(_HERE), str(_HERE / "v12_validate")]:
    if p not in sys.path:
        sys.path.insert(0, p)

from p2_transport_os  import build_os, PHASE2_DIR
from p2_execution_engine import replay_transport_os, compute_allocator_analytics
from p2_baselines     import replay_all_baselines, BASELINE_STRATEGIES
from p2_statistics    import build_comparison_table, run_statistical_tests
from p2_visualize     import run_all_visualizations
from p2_report        import write_reports
from strategy_library import get_all_strategies

CACHE_DIR      = _HERE / "cache"
P2_CHKPT       = PHASE2_DIR / "p2_checkpoint.json"

STAGES = 6


# ═══════════════════════════════════════════════════════════════════════════
# Checkpoint helpers
# ═══════════════════════════════════════════════════════════════════════════

def _load_checkpoint() -> dict:
    PHASE2_DIR.mkdir(parents=True, exist_ok=True)
    (PHASE2_DIR / "plots").mkdir(exist_ok=True)
    if P2_CHKPT.exists():
        try:
            return json.loads(P2_CHKPT.read_text())
        except Exception:
            pass
    return {"stages_complete": [], "os_config": None}


def _save_checkpoint(cp: dict):
    PHASE2_DIR.mkdir(parents=True, exist_ok=True)
    tmp = P2_CHKPT.with_suffix(".tmp")
    tmp.write_text(json.dumps(cp, indent=2, default=str))
    tmp.replace(P2_CHKPT)


def _stage_done(cp: dict, name: str) -> bool:
    return name in cp.get("stages_complete", [])


def _mark_done(cp: dict, name: str):
    if name not in cp["stages_complete"]:
        cp["stages_complete"].append(name)
    _save_checkpoint(cp)


def _banner(text: str):
    print(f"\n{'='*70}\n  {text}\n{'='*70}", flush=True)


def _stage(n: int, name: str):
    print(f"\n[{n}/{STAGES}] {name}", flush=True)


# ═══════════════════════════════════════════════════════════════════════════
# Main
# ═══════════════════════════════════════════════════════════════════════════

def parse_args():
    p = argparse.ArgumentParser(description="Phase 2 Transport OS Validation")
    p.add_argument("--force",       action="store_true", help="Ignore checkpoints and rerun all")
    p.add_argument("--status",      action="store_true", help="Print status and exit")
    p.add_argument("--skip-plots",  action="store_true", help="Skip visualization stage")
    p.add_argument("--bootstrap",   type=int, default=1000, help="Bootstrap iterations")
    return p.parse_args()


def main():
    args    = parse_args()
    t_start = time.perf_counter()

    _banner("Phase 2 — Transport Operating System Validation (EUR/USD)")

    cp = _load_checkpoint()
    if args.force:
        print("  Force flag: resetting all checkpoint stages …")
        cp = {"stages_complete": [], "os_config": None}
        _save_checkpoint(cp)

    if args.status:
        print(f"  Completed stages: {cp.get('stages_complete', [])}")
        return

    strategy_registry = get_all_strategies()
    print(f"  Strategy registry: {len(strategy_registry)} strategies")
    print(f"  Cache dir: {CACHE_DIR} ({len(list(CACHE_DIR.glob('ohlc_transport_*.parquet')))} files)")
    print(f"  Phase 2 output: {PHASE2_DIR}", flush=True)

    # ── Stage 1: Calibrate OS ─────────────────────────────────────────────
    _stage(1, "Calibrating Transport Operating System from Phase 1 statistics")
    if not _stage_done(cp, "calibrate") or args.force:
        os = build_os(verbose=True)
        cp["os_config"] = os.summary_dict()
        _mark_done(cp, "calibrate")
    else:
        print("  [SKIP] OS already calibrated", flush=True)
        from p2_transport_os import TransportOSCalibration
        os = TransportOSCalibration()
        os.calibrate(verbose=False)

    # ── Stage 2: Replay Transport OS ──────────────────────────────────────
    _stage(2, "Replaying Transport OS over full dataset")
    os_trades_path  = PHASE2_DIR / "trade_log_transport.csv"
    dec_path        = PHASE2_DIR / "allocator_decisions.csv"

    if not _stage_done(cp, "os_replay") or args.force:
        os_trades, dec_df = replay_transport_os(
            os, CACHE_DIR, strategy_registry, verbose=True
        )
        os_trades.to_csv(os_trades_path, index=False)
        dec_df.to_csv(dec_path, index=False)
        print(f"  Saved: {os_trades_path.name} ({len(os_trades)} trades)")
        print(f"  Saved: {dec_path.name} ({len(dec_df)} rows)", flush=True)
        _mark_done(cp, "os_replay")
        del os_trades, dec_df
        gc.collect()
    else:
        print(f"  [SKIP] OS replay already done ({os_trades_path.name} exists)", flush=True)

    # ── Stage 3: Replay Baselines ─────────────────────────────────────────
    _stage(3, "Replaying fixed baselines")
    baselines_path = PHASE2_DIR / "trade_log_fixed.csv"

    if not _stage_done(cp, "baselines") or args.force:
        baseline_trades = replay_all_baselines(CACHE_DIR, strategy_registry, verbose=True)
        # Save combined + per-baseline
        frames = []
        for bname, df in baseline_trades.items():
            if len(df) > 0:
                df["label"] = bname
                frames.append(df)
                df.to_csv(PHASE2_DIR / f"trade_log_{bname}.csv", index=False)
        if frames:
            import pandas as pd
            pd.concat(frames, ignore_index=True).to_csv(baselines_path, index=False)
        print(f"  Saved: {baselines_path.name}", flush=True)
        _mark_done(cp, "baselines")
        del baseline_trades
        gc.collect()
    else:
        print(f"  [SKIP] Baselines already done", flush=True)

    # ── Stage 4: Statistics ───────────────────────────────────────────────
    _stage(4, "Computing statistics and significance tests")
    comp_path = PHASE2_DIR / "performance_comparison.csv"
    sig_path  = PHASE2_DIR / "transport_vs_fixed.csv"

    if not _stage_done(cp, "statistics") or args.force:
        import pandas as pd
        os_trades = pd.read_csv(os_trades_path) if os_trades_path.exists() else pd.DataFrame()
        baseline_trades = {}
        for bname in BASELINE_STRATEGIES:
            p = PHASE2_DIR / f"trade_log_{bname}.csv"
            if p.exists():
                baseline_trades[bname] = pd.read_csv(p)
            else:
                baseline_trades[bname] = pd.DataFrame()

        comp_df = build_comparison_table(os_trades, baseline_trades)
        comp_df.to_csv(comp_path, index=False)
        print(f"  Performance comparison:\n{comp_df[['label','profit_factor','sharpe','max_drawdown','trade_count']].to_string(index=False)}", flush=True)

        print("  Running significance tests …", flush=True)
        sig_df = run_statistical_tests(os_trades, baseline_trades, n_boot=args.bootstrap)
        sig_df.to_csv(sig_path, index=False)
        print(f"  FDR-significant: {int(sig_df['mw_reject_fdr'].sum()) if 'mw_reject_fdr' in sig_df.columns else 0}/{len(sig_df)}", flush=True)

        _mark_done(cp, "statistics")
        del os_trades, baseline_trades
        gc.collect()
    else:
        print(f"  [SKIP] Statistics already computed", flush=True)

    # ── Stage 5: Visualizations ───────────────────────────────────────────
    _stage(5, "Generating visualizations")
    if not args.skip_plots and (not _stage_done(cp, "plots") or args.force):
        import pandas as pd
        os_trades       = pd.read_csv(os_trades_path) if os_trades_path.exists() else pd.DataFrame()
        dec_df          = pd.read_csv(dec_path)        if dec_path.exists()        else pd.DataFrame()
        if "timestamp" in dec_df.columns:
            dec_df["timestamp"] = pd.to_datetime(dec_df["timestamp"], utc=True, errors="coerce")
        comp_df         = pd.read_csv(comp_path)       if comp_path.exists()       else pd.DataFrame()
        baseline_trades = {}
        for bname in BASELINE_STRATEGIES:
            p = PHASE2_DIR / f"trade_log_{bname}.csv"
            if p.exists():
                baseline_trades[bname] = pd.read_csv(p)
            else:
                baseline_trades[bname] = pd.DataFrame()

        run_all_visualizations(os_trades, baseline_trades, dec_df, comp_df, verbose=True)
        _mark_done(cp, "plots")
        del os_trades, dec_df, comp_df, baseline_trades
        gc.collect()
    else:
        reason = "skip-plots" if args.skip_plots else "already done"
        print(f"  [SKIP] Visualizations ({reason})", flush=True)

    # ── Stage 6: Reports ──────────────────────────────────────────────────
    _stage(6, "Writing reports")
    if not _stage_done(cp, "reports") or args.force:
        import pandas as pd
        comp_df  = pd.read_csv(comp_path) if comp_path.exists() else pd.DataFrame()
        sig_df   = pd.read_csv(sig_path)  if sig_path.exists()  else pd.DataFrame()
        dec_df   = pd.read_csv(dec_path)  if dec_path.exists()  else pd.DataFrame()
        if "timestamp" in dec_df.columns:
            dec_df["timestamp"] = pd.to_datetime(dec_df["timestamp"], utc=True, errors="coerce")

        alloc_analytics = compute_allocator_analytics(dec_df) if len(dec_df) > 0 else {}
        elapsed = time.perf_counter() - t_start

        # Save allocator CSVs
        if len(dec_df) > 0:
            dec_df.to_csv(PHASE2_DIR / "allocator_decisions.csv", index=False)

        # Strategy switch log
        if len(dec_df) > 0:
            switches = dec_df[["timestamp","regime","selected_strategy","risk_fraction","Q"]].copy()
            switch_mask = switches["selected_strategy"] != switches["selected_strategy"].shift(1)
            switches[switch_mask].to_csv(PHASE2_DIR / "strategy_switches.csv", index=False)

        # Risk budget log (hourly sample)
        if len(dec_df) > 0:
            dec_df.iloc[::12][["timestamp","regime","risk_fraction","stop_mult","target_mult"]].to_csv(
                PHASE2_DIR / "risk_budget.csv", index=False
            )

        # Stop policy log
        if len(dec_df) > 0:
            dec_df[["timestamp","regime","stop_mult","target_mult"]].drop_duplicates().to_csv(
                PHASE2_DIR / "stop_policy.csv", index=False
            )

        write_reports(
            cp.get("os_config", {}),
            comp_df, sig_df, alloc_analytics, elapsed,
            verbose=True,
        )
        _mark_done(cp, "reports")
    else:
        print("  [SKIP] Reports already written", flush=True)

    # ── Final summary ─────────────────────────────────────────────────────
    elapsed = time.perf_counter() - t_start
    _banner("Phase 2 Complete")
    print(f"  Elapsed: {elapsed:.1f}s ({elapsed/60:.1f} min)")
    print(f"  Results: {PHASE2_DIR}\n")
    print("  Deliverables:")

    deliverables = [
        "transport_os_report.md",
        "transport_operating_system.md",
        "transport_vs_fixed.csv",
        "allocator_decisions.csv",
        "strategy_switches.csv",
        "risk_budget.csv",
        "stop_policy.csv",
        "trade_log_transport.csv",
        "trade_log_fixed.csv",
        "performance_comparison.csv",
        "plots/allocator_heatmap.png",
        "plots/strategy_switch_timeline.png",
        "plots/risk_budget_timeline.png",
        "plots/equity_curves.png",
        "plots/performance_comparison.png",
    ]
    for d in deliverables:
        exists = (PHASE2_DIR / d).exists()
        print(f"    {'✓' if exists else '✗ MISSING'}  {d}")
    print(flush=True)


if __name__ == "__main__":
    main()
