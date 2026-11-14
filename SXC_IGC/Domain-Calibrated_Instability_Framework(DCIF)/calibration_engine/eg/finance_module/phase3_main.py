"""
phase3_main.py — Phase 3 Master Orchestrator: Cross-Market Transport Universality Validation.

Usage:
    python phase3_main.py [--force] [--skip-plots] [--markets EURUSD,BTC,ETH] [--bootstrap 500]

Stages:
  1. Build Transport OS from Phase 1 statistics (IMMUTABLE)
  2. For each market: load data, apply transport pipeline, run OS
  3. Load EUR/USD baseline from Phase 2 results
  4. Compute per-market statistics
  5. Build cross-market comparison tables
  6. Run statistical tests
  7. Generate visualizations
  8. Write reports

Output: results/phase3/
  market_summary.csv, market_comparison.csv, market_regime_statistics.csv,
  market_allocator.csv, universality_matrix.csv, universality_score.csv,
  cross_market_heatmap.png, cross_market_pf.png, cross_market_regimes.png,
  transport_universality_report.md, phase3_summary.md
"""

import sys
import argparse
import gc
import json
import time
import warnings
from pathlib import Path
from typing import Dict, List, Optional

import numpy as np
import pandas as pd

warnings.filterwarnings("ignore")

_HERE = Path(__file__).resolve().parent
_CE   = _HERE.parents[1]
for p in [str(_CE), str(_HERE), str(_HERE / "v12_validate")]:
    if p not in sys.path:
        sys.path.insert(0, p)

# Phase 2 immutable imports
from p2_transport_os       import build_os, PHASE2_DIR
from strategy_library      import get_all_strategies

# Phase 3 imports
from phase3_runner         import (
    load_and_prepare_market,
    run_transport_os_on_market,
    compute_regime_statistics,
    MARKET_CONFIG,
    PHASE3_DIR,
    Q05_GLOBAL,
    Q95_GLOBAL,
)
from phase3_statistics     import (
    compute_trade_metrics,
    compute_allocator_metrics,
    compute_bootstrap_stats,
    run_pairwise_tests,
    run_within_market_tests,
    compute_universality_score,
    compute_overall_universality_confidence,
)
from phase3_universality   import (
    build_market_summary_table,
    build_regime_distribution_table,
    build_allocator_table,
    build_markov_tables,
    build_universality_matrix,
    build_universality_scores,
    answer_scientific_questions,
    save_all_tables,
    MARKET_ORDER,
)
from phase3_visuals        import run_all_visuals
from phase3_report         import write_full_report, write_summary

CHKPT_PATH = PHASE3_DIR / "phase3_checkpoint.json"


# ═══════════════════════════════════════════════════════════════════════════
# Checkpoint helpers
# ═══════════════════════════════════════════════════════════════════════════

def _load_cp():
    PHASE3_DIR.mkdir(parents=True, exist_ok=True)
    if CHKPT_PATH.exists():
        try:
            return json.loads(CHKPT_PATH.read_text())
        except Exception:
            pass
    return {"done": [], "market_bars": {}}


def _save_cp(cp):
    PHASE3_DIR.mkdir(parents=True, exist_ok=True)
    tmp = CHKPT_PATH.with_suffix(".tmp")
    tmp.write_text(json.dumps(cp, indent=2, default=str))
    tmp.replace(CHKPT_PATH)


def _done(cp, key):
    return key in cp.get("done", [])


def _mark(cp, key):
    if key not in cp["done"]:
        cp["done"].append(key)
    _save_cp(cp)


def _banner(txt):
    print(f"\n{'='*70}\n  {txt}\n{'='*70}", flush=True)


# ═══════════════════════════════════════════════════════════════════════════
# EUR/USD baseline loader (from Phase 2 results)
# ═══════════════════════════════════════════════════════════════════════════

def load_eurusd_baseline() -> Dict:
    """Load EUR/USD Phase 2 results as the baseline."""
    trade_path = PHASE2_DIR / "trade_log_transport.csv"
    dec_path   = PHASE2_DIR / "allocator_decisions.csv"
    perf_path  = PHASE2_DIR / "performance_comparison.csv"

    trades = pd.read_csv(trade_path) if trade_path.exists() else pd.DataFrame()
    dec_df = pd.DataFrame()
    if dec_path.exists():
        dec_df = pd.read_csv(dec_path, nrows=200_000)  # sample for stats

    # Load Phase 1 Markov for EURUSD regime stats
    markov_path = _HERE / "results" / "phase1" / "markov_matrix.csv"
    trans_path  = _HERE / "results" / "phase1" / "regime_transition_statistics.csv"

    regime_stats = {}
    if trans_path.exists():
        ts_df = pd.read_csv(trans_path)
        for _, row in ts_df.iterrows():
            r = row["regime"]
            regime_stats[r] = {
                "time_fraction": float(row.get("time_fraction", 0)),
            }

    # Build regime fractions from Phase 1 stats
    fracs = {}
    if trans_path.exists():
        ts_df = pd.read_csv(trans_path)
        total = ts_df["time_fraction"].sum()
        for _, row in ts_df.iterrows():
            fracs[row["regime"]] = float(row["time_fraction"])

    coherent = fracs.get("Strong_Coherent", 0) + fracs.get("Weak_Coherent", 0)
    incoherent = fracs.get("Deep_Incoherent", 0) + fracs.get("Mod_Incoherent", 0)

    # Shannon entropy
    p_vals = np.array([v for v in fracs.values() if v > 0])
    entropy = float(-np.sum(p_vals * np.log(p_vals))) if len(p_vals) > 0 else 0.0
    norm_entropy = entropy / np.log(5)

    rs = {
        "regime_fractions": fracs,
        "coherent_frac"   : coherent,
        "incoherent_frac" : incoherent,
        "entropy"         : entropy,
        "norm_entropy"    : norm_entropy,
        "markov"          : {},
        "persistence"     : {},
        "mean_duration"   : {},
        "median_duration" : {},
        "n_bars"          : int(dec_df["bar_idx"].max()) if "bar_idx" in dec_df.columns else 210_000,
    }

    tm = compute_trade_metrics(trades, "EURUSD")
    am = compute_allocator_metrics(dec_df, "EURUSD")

    return {"trades": trades, "dec_df": dec_df, "trade_metrics": tm,
            "alloc_metrics": am, "regime_stats": rs}


# ═══════════════════════════════════════════════════════════════════════════
# Per-market execution
# ═══════════════════════════════════════════════════════════════════════════

def run_single_market(
    symbol: str,
    os,
    strategy_registry: Dict,
    cp: dict,
    force: bool = False,
    verbose: bool = True,
) -> Dict:
    """Run the full pipeline for one market. Caches results to parquet."""
    cache_trades = PHASE3_DIR / f"trades_{symbol}.parquet"
    cache_dec    = PHASE3_DIR / f"decisions_{symbol}.parquet"
    cache_df     = PHASE3_DIR / f"prepared_{symbol}.parquet"

    # Load from cache if available
    if not force and _done(cp, f"market_{symbol}"):
        if verbose:
            print(f"  [{symbol}] Loading from cache …", flush=True)
        trades = pd.read_parquet(cache_trades) if cache_trades.exists() else pd.DataFrame()
        dec_df = pd.read_parquet(cache_dec)    if cache_dec.exists()    else pd.DataFrame()
        prep   = pd.read_parquet(cache_df)     if cache_df.exists()     else pd.DataFrame()
        if len(prep) > 0:
            rs = compute_regime_statistics(prep)
        else:
            rs = {}
        tm = compute_trade_metrics(trades, symbol)
        am = compute_allocator_metrics(dec_df, symbol)
        return {"symbol": symbol, "trades": trades, "dec_df": dec_df,
                "prepared_df": prep, "trade_metrics": tm,
                "alloc_metrics": am, "regime_stats": rs}

    print(f"\n  [{symbol}] Starting market pipeline …", flush=True)

    # 1. Load and prepare
    try:
        prep_df = load_and_prepare_market(symbol)
    except Exception as e:
        print(f"  [{symbol}] ERROR loading data: {e}", flush=True)
        return {"symbol": symbol, "trades": pd.DataFrame(), "dec_df": pd.DataFrame(),
                "prepared_df": pd.DataFrame(), "trade_metrics": {},
                "alloc_metrics": {}, "regime_stats": {}}

    # 2. Run Transport OS (IDENTICAL engine)
    try:
        trades, dec_df = run_transport_os_on_market(
            prep_df, os, strategy_registry, symbol, verbose=verbose
        )
    except Exception as e:
        print(f"  [{symbol}] ERROR running OS: {e}", flush=True)
        trades = pd.DataFrame()
        dec_df = pd.DataFrame()

    # 3. Compute statistics
    rs = compute_regime_statistics(prep_df)
    tm = compute_trade_metrics(trades, symbol)
    am = compute_allocator_metrics(dec_df, symbol)

    # 4. Cache
    PHASE3_DIR.mkdir(parents=True, exist_ok=True)
    if len(trades) > 0:
        trades.to_parquet(cache_trades, index=False)
    if len(dec_df) > 0:
        dec_df.to_parquet(cache_dec, index=False)
    prep_df.to_parquet(cache_df)
    _mark(cp, f"market_{symbol}")

    if verbose:
        pf = tm.get("profit_factor", 0)
        nt = am.get("no_trade_fraction", 1.0) * 100
        sc = rs.get("regime_fractions", {}).get("Strong_Coherent", 0) * 100
        print(f"  [{symbol}] PF={pf:.3f}  NoTrade={nt:.1f}%  SC={sc:.2f}%  Trades={tm.get('trade_count',0)}")

    return {"symbol": symbol, "trades": trades, "dec_df": dec_df,
            "prepared_df": prep_df, "trade_metrics": tm,
            "alloc_metrics": am, "regime_stats": rs}


# ═══════════════════════════════════════════════════════════════════════════
# Main
# ═══════════════════════════════════════════════════════════════════════════

def parse_args():
    p = argparse.ArgumentParser(description="Phase 3 Transport Universality Validation")
    p.add_argument("--force",       action="store_true", help="Rerun all stages")
    p.add_argument("--skip-plots",  action="store_true", help="Skip visualization")
    p.add_argument("--bootstrap",   type=int, default=500, help="Bootstrap iterations")
    p.add_argument("--markets",     type=str, default="",  help="Comma-separated market list")
    return p.parse_args()


def main():
    args  = parse_args()
    t0    = time.perf_counter()

    _banner("Phase 3 — Cross-Market Transport Universality Validation")

    PHASE3_DIR.mkdir(parents=True, exist_ok=True)
    (PHASE3_DIR / "plots").mkdir(exist_ok=True)

    cp = _load_cp()
    if args.force:
        print("  Force flag: resetting checkpoint …")
        cp = {"done": [], "market_bars": {}}
        _save_cp(cp)

    # Determine markets to run
    if args.markets:
        run_markets = [m.strip().upper() for m in args.markets.split(",") if m.strip()]
    else:
        run_markets = [m for m in MARKET_ORDER if m != "EURUSD"]

    print(f"  Markets: {run_markets}", flush=True)

    # ── Stage 1: Build OS (IMMUTABLE from Phase 1) ────────────────────────
    _banner("Stage 1: Building Transport OS (IMMUTABLE)")
    os = build_os(verbose=True)
    strategy_registry = get_all_strategies()
    print(f"  Strategy registry: {len(strategy_registry)} strategies")

    # ── Stage 2: EUR/USD baseline ─────────────────────────────────────────
    _banner("Stage 2: Loading EUR/USD Baseline (Phase 2 results)")
    eurusd = load_eurusd_baseline()
    print(f"  EUR/USD: {eurusd['trade_metrics'].get('trade_count',0)} trades  "
          f"PF={eurusd['trade_metrics'].get('profit_factor',0):.3f}")

    # ── Stage 3: Run each market ──────────────────────────────────────────
    _banner("Stage 3: Running Transport OS on All Markets")

    all_results: Dict[str, dict] = {"EURUSD": eurusd}
    all_trade_metrics = {"EURUSD": eurusd["trade_metrics"]}
    all_alloc_metrics = {"EURUSD": eurusd["alloc_metrics"]}
    all_regime_stats  = {"EURUSD": eurusd["regime_stats"]}
    all_trades_dfs    = {"EURUSD": eurusd["trades"]}

    for sym in run_markets:
        result = run_single_market(sym, os, strategy_registry, cp, args.force)
        all_results[sym]       = result
        all_trade_metrics[sym] = result["trade_metrics"]
        all_alloc_metrics[sym] = result["alloc_metrics"]
        all_regime_stats[sym]  = result["regime_stats"]
        all_trades_dfs[sym]    = result["trades"]
        gc.collect()

    # ── Stage 4: Cross-market statistics ─────────────────────────────────
    _banner("Stage 4: Computing Cross-Market Statistics")

    # Bootstrap stats
    boot_rows = []
    for sym in MARKET_ORDER:
        trades = all_trades_dfs.get(sym, pd.DataFrame())
        if trades is not None and len(trades) > 0:
            bs = compute_bootstrap_stats(trades, sym, n_boot=args.bootstrap)
            boot_rows.append(bs)
    bootstrap_df = pd.DataFrame(boot_rows) if boot_rows else pd.DataFrame()

    # Pairwise statistical tests vs EURUSD
    stat_tests = run_pairwise_tests(
        all_trades_dfs, baseline_symbol="EURUSD", n_boot=args.bootstrap
    )
    print(f"  Statistical tests: {len(stat_tests)} comparisons")
    if "mw_reject_fdr" in stat_tests.columns:
        n_sig = int(stat_tests["mw_reject_fdr"].sum())
        print(f"  FDR-significant: {n_sig}/{len(stat_tests)}")

    # Within-market tests
    within_rows = []
    for sym in MARKET_ORDER:
        trades = all_trades_dfs.get(sym, pd.DataFrame())
        dec_df = all_results.get(sym, {}).get("dec_df", pd.DataFrame())
        wt = run_within_market_tests(trades, dec_df, sym, n_boot=min(200, args.bootstrap))
        within_rows.append(wt)
    within_tests_df = pd.DataFrame(within_rows) if within_rows else pd.DataFrame()
    if len(within_tests_df) > 0:
        within_tests_df.to_csv(PHASE3_DIR / "within_market_tests.csv", index=False)
        print(f"  Saved within_market_tests.csv")

    # ── Stage 5: Build comparison tables ─────────────────────────────────
    _banner("Stage 5: Building Cross-Market Comparison Tables")

    market_summary    = build_market_summary_table(all_trade_metrics, all_alloc_metrics, all_regime_stats)
    regime_dist       = build_regime_distribution_table(all_regime_stats)
    allocator_table   = build_allocator_table(all_alloc_metrics)
    markov_tables     = build_markov_tables(all_regime_stats)
    universality_matrix = build_universality_matrix(all_trade_metrics, all_alloc_metrics, all_regime_stats)
    universality_scores = build_universality_scores(
        all_trade_metrics, all_alloc_metrics, all_regime_stats,
        stat_test_results=stat_tests
    )

    # Compute overall confidence
    scores_list = universality_scores.to_dict("records") if universality_scores is not None else []
    overall_confidence = compute_overall_universality_confidence(scores_list)
    print(f"  Overall universality confidence: {overall_confidence.get('overall_confidence','—')}")

    save_all_tables(
        market_summary, regime_dist, allocator_table,
        universality_matrix, universality_scores,
        markov_tables, stat_tests, bootstrap_df,
        verbose=True,
    )

    # ── Stage 6: Scientific Q&A ───────────────────────────────────────────
    _banner("Stage 6: Answering Scientific Questions")

    scientific_qa = answer_scientific_questions(
        all_trade_metrics, all_alloc_metrics, all_regime_stats,
        stat_tests, {s: {} for s in MARKET_ORDER},
        universality_scores, overall_confidence,
    )
    for qa in scientific_qa:
        print(f"  {qa['question'][:60]} → [{qa['confidence']}]")

    # ── Stage 7: Visualizations ───────────────────────────────────────────
    if not args.skip_plots:
        _banner("Stage 7: Generating Visualizations")
        try:
            run_all_visuals(
                market_summary, all_regime_stats, all_alloc_metrics,
                markov_tables, universality_scores, verbose=True,
            )
        except Exception as e:
            print(f"  WARNING visualization error: {e}")
    else:
        print("  [SKIP] Visualizations (--skip-plots)")

    # ── Stage 8: Reports ──────────────────────────────────────────────────
    _banner("Stage 8: Writing Reports")
    elapsed = time.perf_counter() - t0

    write_full_report(
        market_summary, regime_dist, allocator_table,
        universality_matrix, universality_scores,
        stat_tests, bootstrap_df,
        scientific_qa, overall_confidence,
        all_regime_stats, all_trade_metrics, all_alloc_metrics,
        elapsed_s=elapsed, verbose=True,
    )

    write_summary(
        overall_confidence, market_summary, universality_scores,
        scientific_qa, elapsed_s=elapsed, verbose=True,
    )

    # ── Final deliverables check ──────────────────────────────────────────
    _banner("Phase 3 Complete")
    elapsed = time.perf_counter() - t0
    print(f"  Elapsed: {elapsed:.1f}s ({elapsed/60:.1f} min)")
    print(f"  Results: {PHASE3_DIR}\n")

    deliverables = [
        "market_summary.csv",
        "market_comparison.csv",
        "market_regime_statistics.csv",
        "market_allocator.csv",
        "universality_matrix.csv",
        "universality_score.csv",
        "statistical_tests.csv",
        "bootstrap_statistics.csv",
        "transport_universality_report.md",
        "phase3_summary.md",
        "plots/cross_market_heatmap.png",
        "plots/cross_market_pf.png",
        "plots/cross_market_regimes.png",
        "plots/cross_market_notradeq.png",
        "plots/universality_scores.png",
        "plots/cross_market_markov.png",
    ]
    print("  Deliverables:")
    all_ok = True
    for d in deliverables:
        exists = (PHASE3_DIR / d).exists()
        mark = "✓" if exists else "✗ MISSING"
        print(f"    {mark}  {d}")
        if not exists:
            all_ok = False

    print(f"\n  Status: {'ALL DELIVERABLES PRESENT' if all_ok else 'SOME MISSING'}")
    print(f"  Overall universality confidence: {overall_confidence.get('overall_confidence','—')}\n")


if __name__ == "__main__":
    main()
