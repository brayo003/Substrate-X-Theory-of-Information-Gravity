"""
p4_main.py — Phase 4 Master Orchestrator.

Usage:
    python p4_main.py [--force] [--skip-plots] [--markets M1,M2] [--bootstrap 500]

Stages:
  1. Run all 34 strategies on each market (cached per market)
  2. Compute allocator discovery (best family per market×regime)
  3. Compute full statistics (bootstrap, MW, permutation, BH-FDR)
  4. Compute PL-specific statistics
  5. Generate visualizations
  6. Write all reports and CSVs

Output: results/phase4/
"""

import sys
import argparse
import gc
import json
import time
import warnings
from pathlib import Path
from typing import Dict, List

import numpy as np
import pandas as pd

warnings.filterwarnings("ignore")

_HERE = Path(__file__).resolve().parent
for p in [str(_HERE), str(_HERE/"v12_validate")]:
    if p not in sys.path:
        sys.path.insert(0, p)

from p4_strategy_runner    import (run_all_strategies_for_market, load_cached_metrics,
                                    load_cached_pl_trades, MARKET_ORDER, PHASE4_DIR)
from p4_allocator_discovery import (discover_all_markets, build_cross_market_allocator_table,
                                    build_allocator_transition_matrix, compute_allocator_entropy,
                                    build_scheduler_similarity_matrix, build_family_rankings)
from p4_statistics          import run_all_pairwise_tests, compute_pl_statistics
from p4_visuals             import run_all_visuals
from p4_report              import (save_all_csvs, write_allocator_report, write_pl_report,
                                    write_scheduler_report, write_scientific_summary)
from p4_passive_liquidity   import simulate_pl_inventory, compute_adverse_selection_stats

CHKPT = PHASE4_DIR / "p4_checkpoint.json"


def _load_cp():
    PHASE4_DIR.mkdir(parents=True, exist_ok=True)
    if CHKPT.exists():
        try: return json.loads(CHKPT.read_text())
        except: pass
    return {"done": []}


def _save_cp(cp):
    tmp = CHKPT.with_suffix(".tmp")
    tmp.write_text(json.dumps(cp, indent=2, default=str))
    tmp.replace(CHKPT)


def _done(cp, k): return k in cp["done"]
def _mark(cp, k):
    if k not in cp["done"]: cp["done"].append(k)
    _save_cp(cp)


def _banner(t):
    print(f"\n{'='*70}\n  {t}\n{'='*70}", flush=True)


def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument("--force",       action="store_true")
    p.add_argument("--skip-plots",  action="store_true")
    p.add_argument("--bootstrap",   type=int, default=500)
    p.add_argument("--markets",     type=str, default="")
    return p.parse_args()


def main():
    args = parse_args()
    t0   = time.perf_counter()

    _banner("Phase 4 — Market-Specific Allocator Discovery + Passive Liquidity Validation")

    PHASE4_DIR.mkdir(parents=True, exist_ok=True)
    (PHASE4_DIR / "plots").mkdir(exist_ok=True)
    (PHASE4_DIR / "runs").mkdir(exist_ok=True)

    cp = _load_cp()
    if args.force:
        print("  --force: resetting checkpoint")
        cp = {"done": []}; _save_cp(cp)

    markets = ([m.strip().upper() for m in args.markets.split(",") if m.strip()]
               if args.markets else MARKET_ORDER)
    print(f"  Markets: {markets}")

    # ── Stage 1: Run strategies ───────────────────────────────────────────
    _banner("Stage 1: Running All 34 Strategies on Every Market")
    all_metrics:   Dict[str, pd.DataFrame] = {}
    all_pl_trades: Dict[str, pd.DataFrame] = {}

    for sym in markets:
        key = f"run_{sym}"
        if not args.force and _done(cp, key):
            df  = load_cached_metrics(sym)
            plt = load_cached_pl_trades(sym)
            if df is not None:
                all_metrics[sym]   = df
                all_pl_trades[sym] = plt if plt is not None else pd.DataFrame()
                print(f"  [{sym}] Loaded from cache ({len(df)} metric rows)", flush=True)
                continue

        print(f"\n  [{sym}] Running strategies …", flush=True)
        metrics_df, pl_df = run_all_strategies_for_market(sym, verbose=True)
        all_metrics[sym]   = metrics_df
        all_pl_trades[sym] = pl_df
        _mark(cp, key)
        gc.collect()

    # ── Stage 2: Allocator Discovery ─────────────────────────────────────
    _banner("Stage 2: Allocator Discovery")
    allocator_df, regime_df, confidence_df = discover_all_markets(all_metrics)
    cross_market_df  = build_cross_market_allocator_table(allocator_df)
    transition_df    = build_allocator_transition_matrix(allocator_df)
    entropy_df       = compute_allocator_entropy(allocator_df)
    sim_matrix       = build_scheduler_similarity_matrix(allocator_df)
    family_rankings  = build_family_rankings(all_metrics)

    print(f"  Allocator rows: {len(allocator_df)}")
    print(f"  Families discovered: {allocator_df['best_family'].nunique() if len(allocator_df)>0 else 0}")
    if len(allocator_df) > 0:
        for sym in markets:
            sub = allocator_df[allocator_df["symbol"]==sym]
            print(f"  {sym}: " + ", ".join(f"{row['regime'][:4]}→{row['best_family'][:6]}" for _,row in sub.iterrows()))

    # ── Stage 3: Statistical tests ────────────────────────────────────────
    _banner("Stage 3: Statistical Tests (Bootstrap, MW, Permutation, BH-FDR)")
    pairwise_tests = run_all_pairwise_tests(all_metrics, n_boot=min(args.bootstrap, 200))
    print(f"  Pairwise tests: {len(pairwise_tests)} comparisons")
    if "mw_reject_fdr" in pairwise_tests.columns:
        print(f"  FDR-significant: {int(pairwise_tests['mw_reject_fdr'].sum())}/{len(pairwise_tests)}")
    pairwise_tests.to_csv(PHASE4_DIR / "pairwise_family_tests.csv", index=False)
    print("  Saved pairwise_family_tests.csv")

    # ── Stage 4: Passive Liquidity statistics ─────────────────────────────
    _banner("Stage 4: Passive Liquidity Analysis")
    pl_stats = compute_pl_statistics(all_metrics, n_boot=min(args.bootstrap, 200))
    print(f"  PL stats rows: {len(pl_stats)}")
    if len(pl_stats) > 0:
        pl_wins = int(pl_stats["pl_wins"].sum())
        print(f"  PL beats field: {pl_wins}/{len(pl_stats)} cells")

    # Combine all PL trade logs
    pl_frames = [df for df in all_pl_trades.values() if df is not None and len(df) > 0]
    pl_trades_all = pd.concat(pl_frames, ignore_index=True) if pl_frames else pd.DataFrame()
    print(f"  Total PL trades: {len(pl_trades_all)}")

    # Inventory simulation
    pl_inv_frames = []
    for sym, pl_df in all_pl_trades.items():
        if pl_df is not None and len(pl_df) > 0:
            inv = simulate_pl_inventory(pl_df)
            if len(inv) > 0:
                inv["symbol"] = sym
                pl_inv_frames.append(inv)
    pl_inventory_all = pd.concat(pl_inv_frames, ignore_index=True) if pl_inv_frames else pd.DataFrame()

    # ── Stage 5: Visualizations ───────────────────────────────────────────
    if not args.skip_plots:
        _banner("Stage 5: Generating Visualizations")
        try:
            run_all_visuals(cross_market_df, sim_matrix, pl_stats, family_rankings, verbose=True)
        except Exception as e:
            print(f"  WARNING visualization: {e}")
    else:
        print("  [SKIP] Visualizations")

    # ── Stage 6: Reports and CSVs ─────────────────────────────────────────
    _banner("Stage 6: Writing Reports and CSVs")
    elapsed = time.perf_counter() - t0

    save_all_csvs(
        allocator_df, regime_df, confidence_df, cross_market_df,
        sim_matrix, transition_df, entropy_df, family_rankings,
        pl_stats, pl_trades_all, pl_inventory_all, verbose=True,
    )

    write_allocator_report(allocator_df, cross_market_df, regime_df, entropy_df,
                           sim_matrix, elapsed_s=elapsed, verbose=True)
    write_pl_report(pl_stats, pl_trades_all, all_metrics, verbose=True)
    write_scheduler_report(cross_market_df, sim_matrix, regime_df, verbose=True)
    write_scientific_summary(allocator_df, cross_market_df, regime_df, pl_stats,
                             sim_matrix, entropy_df, family_rankings, verbose=True)

    # ── Deliverables check ────────────────────────────────────────────────
    _banner("Phase 4 Complete")
    elapsed = time.perf_counter() - t0
    print(f"  Elapsed: {elapsed:.1f}s ({elapsed/60:.1f} min)")
    print(f"  Output:  {PHASE4_DIR}\n")

    required = [
        "phase4_allocator_discovery.md",
        "allocator_by_market.csv",
        "allocator_by_regime.csv",
        "allocator_heatmap.png" if not args.skip_plots else None,
        "allocator_confidence.csv",
        "transport_scheduler_report.md",
        "scheduler_similarity_matrix.csv",
        "scheduler_similarity_heatmap.png" if not args.skip_plots else None,
        "passive_liquidity_statistics.csv",
        "passive_liquidity_report.md",
        "passive_liquidity_trade_log.csv",
        "passive_liquidity_inventory.csv",
        "passive_liquidity_drawdown.csv",
        "cross_market_allocator.csv",
        "allocator_transition_matrix.csv",
        "allocator_markov.csv",
        "allocator_entropy.csv",
        "strategy_family_rankings.csv",
        "scientific_summary.md",
    ]
    required = [r for r in required if r is not None]
    all_ok = True
    print("  Deliverables:")
    for d in required:
        exists = (PHASE4_DIR / d).exists() or (PHASE4_DIR / "plots" / d).exists()
        mark = "✓" if exists else "✗ MISSING"
        print(f"    {mark}  {d}")
        if not exists: all_ok = False

    print(f"\n  Status: {'ALL DELIVERABLES PRESENT' if all_ok else 'SOME MISSING'}\n")


if __name__ == "__main__":
    main()
