"""
p5b_main.py — Phase 5B Intraday Revalidation Orchestrator.

Correction of Phase 5 for the 4 markets that had data limitations:
  EURUSD — was excluded (parser bug, now fixed)
  XAUUSD — was daily bars only (now M1 → 5-min)
  USOIL  — was daily bars only (now M1 → 5-min)
  UKOIL  — was daily bars only (now M1 → 5-min)

BTC, ETH, NAS100 results are loaded from Phase 5 cache unchanged.

ABSOLUTE RULES — nothing frozen is touched:
  Q thresholds, transport equations, allocator tables, scheduler,
  stop policies, risk budgets, HOLD_BARS — all identical to Phase 4.
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

PHASE5_DIR  = _HERE / "results" / "phase5"
PHASE5B_DIR = _HERE / "results" / "phase5b"

MARKETS_5B    = ["EURUSD", "XAUUSD", "USOIL", "UKOIL"]   # rerun with M1
MARKETS_KEEP  = ["BTCUSDT", "ETHUSDT", "NAS100"]          # reuse Phase 5 cache
MARKET_ORDER  = ["EURUSD", "BTCUSDT", "ETHUSDT", "NAS100", "XAUUSD", "USOIL", "UKOIL"]


# ── logging helpers ────────────────────────────────────────────────────────
def _banner(msg, char="═", width=70):
    print(f"\n{char*width}", flush=True)
    print(f"  {msg}", flush=True)
    print(f"{char*width}", flush=True)

def _section(msg):
    print(f"\n── {msg} {'─'*max(0,65-len(msg))}", flush=True)

def _ok(msg):   print(f"  ✓ {msg}", flush=True)
def _warn(msg): print(f"  ⚠  {msg}", flush=True)
def _fail(msg): print(f"  ✗ {msg}", flush=True)


# ══════════════════════════════════════════════════════════════════════════
# STEP 1 — Load M1 data for the 4 affected markets
# ══════════════════════════════════════════════════════════════════════════

def step1_load(verbose=True):
    _section("STEP 1: Load 2026 M1 data (EURUSD, XAUUSD, USOIL, UKOIL)")
    from p5b_data_loader import load_all_markets_5b, get_q_stats_5b, ensure_dirs

    ensure_dirs()
    t0 = time.time()
    data_5b = load_all_markets_5b(verbose=verbose)

    _ok(f"Loaded {len(data_5b)} markets in {time.time()-t0:.1f}s")
    for sym, df in data_5b.items():
        s = get_q_stats_5b(df)
        print(f"    {sym:8s}: {len(df):>8,} bars | "
              f"Q_mean={s.get('q_mean',0):+.3f} | "
              f"coherent={s.get('q_coherent_frac',0):.1%}", flush=True)
    return data_5b


# ══════════════════════════════════════════════════════════════════════════
# STEP 2 — Replay frozen OS on the 4 affected markets
# ══════════════════════════════════════════════════════════════════════════

def step2_replay(data_5b, force=False, verbose=True):
    _section("STEP 2: Replay frozen OS on 4 M1 markets")
    from p5_engine import run_phase5_replay, save_replay_results

    cache_dir = PHASE5B_DIR / "cache"
    cache_dir.mkdir(parents=True, exist_ok=True)

    if not force:
        # Check if all 4 are already cached
        cached = [sym for sym in MARKETS_5B
                  if (cache_dir / f"trades_5b_{sym}.parquet").exists()]
        if len(cached) == len(MARKETS_5B):
            _ok(f"Loading {len(cached)} cached 5B replays")
            trade_logs, bar_logs = {}, {}
            for sym in MARKETS_5B:
                trade_logs[sym] = pd.read_parquet(cache_dir / f"trades_5b_{sym}.parquet")
                bar_logs[sym]   = pd.read_parquet(cache_dir / f"barlogs_5b_{sym}.parquet")
                bl = bar_logs[sym]
                nt = 100*bl["no_trade"].mean() if "no_trade" in bl.columns else 0
                print(f"    {sym:8s}: {len(trade_logs[sym]):>5} trades | "
                      f"{len(bl):>8,} bars | NoTrade={nt:.1f}% (cached)", flush=True)
            return trade_logs, bar_logs

    t0 = time.time()
    trade_logs, bar_logs = run_phase5_replay(
        data_5b, markets=MARKETS_5B, verbose=verbose
    )

    # Cache results with 5b prefix
    for sym in MARKETS_5B:
        if sym in trade_logs and len(trade_logs[sym]) > 0:
            trade_logs[sym].to_parquet(cache_dir / f"trades_5b_{sym}.parquet", index=False)
        if sym in bar_logs and len(bar_logs[sym]) > 0:
            bar_logs[sym].to_parquet(cache_dir / f"barlogs_5b_{sym}.parquet", index=False)

    total = sum(len(v) for v in trade_logs.values())
    _ok(f"Replay done in {time.time()-t0:.1f}s — {total:,} trades across {len(trade_logs)} markets")

    for sym in MARKETS_5B:
        tl = trade_logs.get(sym, pd.DataFrame())
        bl = bar_logs.get(sym, pd.DataFrame())
        nt = 100*bl["no_trade"].mean() if len(bl) and "no_trade" in bl.columns else 0
        print(f"    {sym:8s}: {len(tl):>5} trades | "
              f"{len(bl):>8,} bars | NoTrade={nt:.1f}%", flush=True)

    return trade_logs, bar_logs


# ══════════════════════════════════════════════════════════════════════════
# STEP 3 — Merge with Phase 5 cache (BTC, ETH, NAS100 unchanged)
# ══════════════════════════════════════════════════════════════════════════

def step3_merge_phase5(trade_logs_5b, bar_logs_5b, data_5b, verbose=True):
    _section("STEP 3: Merge with Phase 5 BTC/ETH/NAS100 cache")
    from p5_engine import load_cached_replay_results

    p5_trades, p5_bars = load_cached_replay_results()

    # Combined dicts: 5B markets override Phase 5 versions
    all_trades = {}
    all_bars   = {}
    all_data   = {}

    # Carry over Phase 5 unchanged markets
    for sym in MARKETS_KEEP:
        if sym in p5_trades:
            all_trades[sym] = p5_trades[sym]
            all_bars[sym]   = p5_bars.get(sym, pd.DataFrame())
            all_data[sym]   = pd.DataFrame()   # no raw OHLC needed for drift on these
            _ok(f"{sym}: Phase 5 cache loaded ({len(all_trades[sym])} trades)")
        else:
            _warn(f"{sym}: not in Phase 5 cache")

    # Add corrected 5B markets
    for sym in MARKETS_5B:
        if sym in trade_logs_5b:
            all_trades[sym] = trade_logs_5b[sym]
            all_bars[sym]   = bar_logs_5b.get(sym, pd.DataFrame())
            all_data[sym]   = data_5b.get(sym, pd.DataFrame())
            _ok(f"{sym}: Phase 5B M1 replay ({len(all_trades[sym])} trades)")

    print(f"\n  Combined: {len(all_trades)} markets, "
          f"{sum(len(v) for v in all_trades.values()):,} total trades", flush=True)

    return all_trades, all_bars, all_data


# ══════════════════════════════════════════════════════════════════════════
# STEP 4 — Compute statistics
# ══════════════════════════════════════════════════════════════════════════

def step4_stats(all_trades, all_bars, verbose=True):
    _section("STEP 4: Compute per-market statistics (2025 vs 5B)")
    from p5_statistics import (
        compute_all_stats_2026, build_comparison_table,
        load_phase4_stats, build_market_summary_csv,
        compute_regime_breakdown_2026,
    )

    t0 = time.time()
    _, stats_5b = compute_all_stats_2026(all_trades, all_bars, verbose=verbose)
    _ok(f"5B stats for {len(stats_5b)} markets")

    stats_2025 = load_phase4_stats()
    _ok(f"Phase 4 reference stats for {len(stats_2025)} markets")

    comparison_df    = build_comparison_table(stats_5b, stats_2025)
    market_summary   = build_market_summary_csv(stats_5b)
    regime_breakdown = compute_regime_breakdown_2026(all_trades, all_bars)

    _ok(f"Statistics complete in {time.time()-t0:.1f}s")

    if verbose:
        print(f"\n  {'Symbol':10s} {'PF':>6} {'Sharpe':>7} {'WinRate':>8} "
              f"{'Trades':>7} {'NoTrd%':>7} {'MaxDD':>7}", flush=True)
        print(f"  {'─'*10} {'─'*6} {'─'*7} {'─'*8} {'─'*7} {'─'*7} {'─'*7}", flush=True)
        for sym in MARKET_ORDER:
            if sym in stats_5b:
                s = stats_5b[sym]
                tag = " ←5B" if sym in MARKETS_5B else ""
                print(f"  {sym:10s} {s.get('profit_factor',0):>6.3f} "
                      f"{s.get('sharpe',0):>7.3f} "
                      f"{s.get('win_rate',0):>8.1%} "
                      f"{s.get('n_trades',0):>7} "
                      f"{s.get('no_trade_pct',0):>6.1f}% "
                      f"{s.get('max_drawdown',0):>7.4f}{tag}", flush=True)

    return stats_2025, stats_5b, comparison_df, market_summary, regime_breakdown


# ══════════════════════════════════════════════════════════════════════════
# STEP 5 — Drift analysis
# ══════════════════════════════════════════════════════════════════════════

def step5_drift(all_data, all_trades, all_bars, stats_2025, stats_5b, verbose=True):
    _section("STEP 5: Drift analysis (Phase 4 → Phase 5B)")
    from p5_drift import compute_all_drift

    t0 = time.time()
    drift = compute_all_drift(
        all_data_2026=all_data,
        all_trade_logs_2026=all_trades,
        stats_2025=stats_2025,
        stats_2026=stats_5b,
        verbose=verbose,
    )
    _ok(f"Drift analysis complete in {time.time()-t0:.1f}s")

    td = drift.get("transport_drift")
    if td is not None and len(td):
        print("\n  Transport Drift Summary:", flush=True)
        num_cols = [c for c in td.columns if c != "symbol"]
        for col in num_cols[:6]:
            vals = pd.to_numeric(td[col], errors="coerce").dropna()
            if len(vals):
                print(f"    {col:35s}: mean={vals.mean():.4f}", flush=True)
    return drift


# ══════════════════════════════════════════════════════════════════════════
# STEP 6 — Plots
# ══════════════════════════════════════════════════════════════════════════

def step6_visuals(all_data, all_trades, all_bars, stats_2025, stats_5b, drift,
                  verbose=True):
    _section("STEP 6: Generate plots")
    from p5_visuals import run_all_visuals

    # Point visuals output at phase5b/plots
    import p5_visuals as vis_mod
    orig_dir = vis_mod.PLOTS_DIR
    vis_mod.PLOTS_DIR = PHASE5B_DIR / "plots"
    vis_mod.PLOTS_DIR.mkdir(parents=True, exist_ok=True)

    try:
        run_all_visuals(
            all_data_2026=all_data,
            all_trade_logs=all_trades,
            all_bar_logs=all_bars,
            stats_2025=stats_2025,
            stats_2026=stats_5b,
            drift_results=drift,
            verbose=verbose,
        )
        n = len(list(vis_mod.PLOTS_DIR.glob("*.png")))
        _ok(f"Generated {n} plots → {vis_mod.PLOTS_DIR}")
    except Exception as e:
        _warn(f"Visuals failed: {e}")
        traceback.print_exc()
    finally:
        vis_mod.PLOTS_DIR = orig_dir


# ══════════════════════════════════════════════════════════════════════════
# STEP 7 — Write deliverables to results/phase5b/
# ══════════════════════════════════════════════════════════════════════════

def step7_deliverables(all_trades, all_bars, market_summary, comparison_df,
                       regime_breakdown, drift, stats_2025, stats_5b, verbose=True):
    _section("STEP 7: Write deliverables")
    from p5_report import save_all_deliverables
    import p5_report as rep_mod

    # Redirect report output dir to phase5b
    orig_dir = rep_mod.PHASE5_DIR
    rep_mod.PHASE5_DIR = PHASE5B_DIR
    PHASE5B_DIR.mkdir(parents=True, exist_ok=True)

    try:
        save_all_deliverables(
            all_trade_logs=all_trades,
            all_bar_logs=all_bars,
            market_summary_df=market_summary,
            comparison_df=comparison_df,
            regime_breakdown=regime_breakdown,
            drift_results=drift,
            stats_2025=stats_2025,
            stats_2026=stats_5b,
            verbose=verbose,
        )
        _ok(f"Deliverables written → {PHASE5B_DIR}")
    except Exception as e:
        _fail(f"Deliverables failed: {e}")
        traceback.print_exc()
    finally:
        rep_mod.PHASE5_DIR = orig_dir


# ══════════════════════════════════════════════════════════════════════════
# STEP 8 — Verify
# ══════════════════════════════════════════════════════════════════════════

REQUIRED = [
    "trade_log_2026.csv",
    "market_summary_2026.csv",
    "performance_2025_vs_2026.csv",
    "transport_drift.csv",
    "statistical_tests.csv",
    "phase5_summary.md",
    "scientific_questions.md",
]

def step8_verify(verbose=True):
    _section("STEP 8: Verify deliverables")
    ok = True
    for fname in REQUIRED:
        p = PHASE5B_DIR / fname
        if p.exists():
            _ok(f"{fname} ({p.stat().st_size/1024:.1f} KB)")
        else:
            _fail(f"{fname} — MISSING")
            ok = False

    plots = list((PHASE5B_DIR / "plots").glob("*.png")) if (PHASE5B_DIR/"plots").exists() else []
    print(f"\n  Plots: {len(plots)} PNG files", flush=True)
    total = len(list(PHASE5B_DIR.rglob("*")))
    print(f"  Total files in phase5b/: {total}", flush=True)
    return ok


# ══════════════════════════════════════════════════════════════════════════
# Master orchestrator
# ══════════════════════════════════════════════════════════════════════════

def run_phase5b(verbose=True, skip_visuals=False, force_replay=False):
    t_total = time.time()
    _banner("PHASE 5B — INTRADAY REVALIDATION (EURUSD + COMMODITIES)")
    print(f"  Started : {datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')}", flush=True)
    print(f"  Corrects: EURUSD (parser fix) + XAUUSD/USOIL/UKOIL (M1 vs daily)", flush=True)
    print(f"  Keeps   : BTCUSDT, ETHUSDT, NAS100 from Phase 5 cache", flush=True)
    print(f"  Rule    : NO recalibration | NO leakage | frozen OS", flush=True)

    errors = []

    # 1. Load
    try:
        data_5b = step1_load(verbose)
    except Exception as e:
        _fail(f"Step 1: {e}"); traceback.print_exc(); raise

    # 2. Replay
    try:
        trade_logs_5b, bar_logs_5b = step2_replay(data_5b, force=force_replay, verbose=verbose)
    except Exception as e:
        _fail(f"Step 2: {e}"); traceback.print_exc(); raise

    # 3. Merge
    try:
        all_trades, all_bars, all_data = step3_merge_phase5(
            trade_logs_5b, bar_logs_5b, data_5b, verbose)
    except Exception as e:
        _fail(f"Step 3: {e}"); traceback.print_exc()
        all_trades, all_bars, all_data = trade_logs_5b, bar_logs_5b, data_5b
        errors.append(("merge", str(e)))

    # 4. Stats
    stats_2025 = {}; stats_5b = {}
    comparison_df = pd.DataFrame(); market_summary = pd.DataFrame()
    regime_breakdown = pd.DataFrame()
    try:
        stats_2025, stats_5b, comparison_df, market_summary, regime_breakdown = \
            step4_stats(all_trades, all_bars, verbose)
    except Exception as e:
        _fail(f"Step 4: {e}"); traceback.print_exc(); errors.append(("stats", str(e)))

    # 5. Drift
    drift = {}
    try:
        drift = step5_drift(all_data, all_trades, all_bars, stats_2025, stats_5b, verbose)
    except Exception as e:
        _fail(f"Step 5: {e}"); traceback.print_exc(); errors.append(("drift", str(e)))

    # 6. Visuals
    if not skip_visuals:
        try:
            step6_visuals(all_data, all_trades, all_bars, stats_2025, stats_5b, drift, verbose)
        except Exception as e:
            _warn(f"Step 6: {e}"); traceback.print_exc(); errors.append(("visuals", str(e)))
    else:
        _warn("Visuals skipped")

    # 7. Deliverables
    try:
        step7_deliverables(all_trades, all_bars, market_summary, comparison_df,
                           regime_breakdown, drift, stats_2025, stats_5b, verbose)
    except Exception as e:
        _fail(f"Step 7: {e}"); traceback.print_exc(); errors.append(("deliverables", str(e)))

    # 8. Verify
    ok = step8_verify(verbose)

    # Summary
    elapsed = time.time() - t_total
    _banner(f"PHASE 5B COMPLETE — {elapsed:.0f}s")

    if errors:
        _warn(f"{len(errors)} non-fatal errors: {[e[0] for e in errors]}")
    else:
        _ok("No errors.")

    if stats_5b:
        profitable = sum(1 for s in stats_5b.values() if s.get("profit_factor", 0) >= 1.0)
        total_t    = sum(s.get("n_trades", 0) for s in stats_5b.values())
        pf_vals    = [s.get("profit_factor", 0) for s in stats_5b.values()]
        print(f"\n  Markets profitable (PF≥1): {profitable}/{len(stats_5b)}", flush=True)
        print(f"  Total trades (5B):          {total_t:,}", flush=True)
        print(f"  Mean PF:                    {np.mean(pf_vals):.3f}", flush=True)
        print(f"\n  Deliverables: {PHASE5B_DIR}", flush=True)

    return {
        "data_5b": data_5b, "all_trades": all_trades, "all_bars": all_bars,
        "stats_2025": stats_2025, "stats_5b": stats_5b,
        "comparison_df": comparison_df, "drift": drift,
        "all_ok": ok, "errors": errors,
    }


# ══════════════════════════════════════════════════════════════════════════
# CLI
# ══════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser(description="Phase 5B — Intraday Revalidation")
    ap.add_argument("--quiet",        action="store_true")
    ap.add_argument("--no-visuals",   action="store_true")
    ap.add_argument("--force-replay", action="store_true")
    args = ap.parse_args()

    res = run_phase5b(
        verbose=not args.quiet,
        skip_visuals=args.no_visuals,
        force_replay=args.force_replay,
    )
    sys.exit(0 if res["all_ok"] else 1)
