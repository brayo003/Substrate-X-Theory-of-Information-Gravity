"""
p5_statistics.py — Phase 5 Trading Statistics Engine.

Computes all per-market metrics for the 2026 out-of-sample replay:
  - Profit Factor, Sharpe, Win Rate, Expectancy, Max Drawdown
  - Trade count, NoTrade%, Regime occupancy, Risk usage
  - Allocator usage, Family usage
  - Bootstrap CIs (1000 resamples)

Also computes Phase 4 (2025) stats for side-by-side comparison.
"""

import sys
import warnings
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import numpy as np
import pandas as pd

warnings.filterwarnings("ignore")

_HERE = Path(__file__).resolve().parent
for p in [str(_HERE), str(_HERE / "v12_validate")]:
    if p not in sys.path:
        sys.path.insert(0, p)

PHASE4_DIR = _HERE / "results" / "phase4"
PHASE5_DIR = _HERE / "results" / "phase5"

REGIMES_5  = ["Deep_Incoherent", "Mod_Incoherent", "Transition", "Weak_Coherent", "Strong_Coherent"]
MARKET_ORDER = ["EURUSD", "BTCUSDT", "ETHUSDT", "NAS100", "XAUUSD", "USOIL", "UKOIL"]


# ═══════════════════════════════════════════════════════════════════════════
# Core metric computations
# ═══════════════════════════════════════════════════════════════════════════

def _profit_factor(rets: np.ndarray) -> float:
    wins   = rets[rets > 0]
    losses = rets[rets < 0]
    w = wins.sum()
    l = abs(losses.sum())
    if l == 0:
        return 99.0 if w > 0 else 0.0
    return float(w / l)


def _sharpe(rets: np.ndarray) -> float:
    if len(rets) < 2:
        return 0.0
    mu  = rets.mean()
    std = rets.std()
    return float(mu / (std + 1e-12) * np.sqrt(len(rets)))


def _sortino(rets: np.ndarray) -> float:
    if len(rets) < 2:
        return 0.0
    mu   = rets.mean()
    dstd = rets[rets < 0].std() if (rets < 0).any() else 1e-12
    return float(mu / (dstd + 1e-12) * np.sqrt(len(rets)))


def _max_drawdown(rets: np.ndarray) -> float:
    eq = np.cumsum(rets)
    peak = np.maximum.accumulate(eq)
    dd   = peak - eq
    return float(dd.max()) if len(dd) > 0 else 0.0


def _calmar(rets: np.ndarray) -> float:
    ann = float(rets.sum()) * 252 / max(len(rets), 1)
    mdd = _max_drawdown(rets)
    return ann / (mdd + 1e-12) if mdd > 0 else 0.0


def compute_market_stats(
    trade_log:   pd.DataFrame,
    bar_log:     pd.DataFrame,
    symbol:      str,
    n_boot:      int = 1000,
) -> Dict:
    """Compute full stats for one market's 2026 replay."""
    if trade_log is None or len(trade_log) == 0:
        return _empty_stats(symbol)

    rets   = trade_log["net_ret"].dropna().values
    n      = len(rets)
    if n == 0:
        return _empty_stats(symbol)

    wins   = rets[rets > 0]
    losses = rets[rets < 0]

    # Core metrics
    pf      = _profit_factor(rets)
    sharpe  = _sharpe(rets)
    sortino = _sortino(rets)
    wr      = len(wins) / n
    expect  = float(rets.mean())
    mdd     = _max_drawdown(rets)
    calmar  = _calmar(rets)
    total_r = float(rets.sum())
    avg_win  = float(wins.mean())   if len(wins)   > 0 else 0.0
    avg_loss = float(losses.mean()) if len(losses) > 0 else 0.0
    payoff   = abs(avg_win / (avg_loss + 1e-12)) if avg_loss != 0 else 0.0

    # NoTrade%
    n_bars      = len(bar_log) if bar_log is not None else 0
    no_trade_n  = int(bar_log["no_trade"].sum()) if bar_log is not None and "no_trade" in bar_log.columns else 0
    no_trade_pct = no_trade_n / max(n_bars, 1)

    # Regime occupancy (from bar log)
    regime_occ = {}
    if bar_log is not None and "regime" in bar_log.columns:
        for regime in REGIMES_5:
            cnt = int((bar_log["regime"] == regime).sum())
            regime_occ[regime] = cnt / max(n_bars, 1)

    # Trades per regime
    trades_by_regime = {}
    if "regime" in trade_log.columns:
        for regime in REGIMES_5:
            sub = trade_log[trade_log["regime"] == regime]
            trades_by_regime[regime] = len(sub)

    # Family usage
    family_usage = {}
    if "family" in trade_log.columns:
        for fam, cnt in trade_log["family"].value_counts().items():
            family_usage[str(fam)] = int(cnt)

    # Allocator usage
    allocator_usage = {}
    if "strategy" in trade_log.columns:
        for strat, cnt in trade_log["strategy"].value_counts().items():
            allocator_usage[str(strat)] = int(cnt)

    # Bootstrap CIs
    boot_pf, boot_sh, boot_wr = _bootstrap_cis(rets, n_boot)

    # Average trade duration
    avg_dur = float(trade_log["duration_bars"].mean()) if "duration_bars" in trade_log.columns else 0.0

    # Stop / target / timeout rates
    stop_rate   = float(trade_log["stop_hit"].mean())   if "stop_hit"   in trade_log.columns else 0.0
    target_rate = float(trade_log["target_hit"].mean()) if "target_hit" in trade_log.columns else 0.0
    timeout_rate= float(trade_log["timeout"].mean())    if "timeout"    in trade_log.columns else 0.0

    return {
        "symbol"           : symbol,
        "n_bars"           : n_bars,
        "n_trades"         : n,
        "profit_factor"    : round(pf, 4),
        "sharpe"           : round(sharpe, 4),
        "sortino"          : round(sortino, 4),
        "calmar"           : round(calmar, 4),
        "win_rate"         : round(wr, 4),
        "expectancy"       : round(expect, 6),
        "total_return"     : round(total_r, 6),
        "max_drawdown"     : round(mdd, 6),
        "avg_win"          : round(avg_win, 6),
        "avg_loss"         : round(avg_loss, 6),
        "payoff_ratio"     : round(payoff, 4),
        "avg_duration_bars": round(avg_dur, 2),
        "stop_rate"        : round(stop_rate, 4),
        "target_rate"      : round(target_rate, 4),
        "timeout_rate"     : round(timeout_rate, 4),
        "no_trade_pct"     : round(no_trade_pct, 4),
        "no_trade_n"       : no_trade_n,
        "regime_occupancy" : regime_occ,
        "trades_by_regime" : trades_by_regime,
        "family_usage"     : family_usage,
        "allocator_usage"  : allocator_usage,
        "boot_pf_ci_lo"    : round(boot_pf[0], 4),
        "boot_pf_ci_hi"    : round(boot_pf[1], 4),
        "boot_sharpe_ci_lo": round(boot_sh[0], 4),
        "boot_sharpe_ci_hi": round(boot_sh[1], 4),
        "boot_wr_ci_lo"    : round(boot_wr[0], 4),
        "boot_wr_ci_hi"    : round(boot_wr[1], 4),
    }


def _bootstrap_cis(rets: np.ndarray, n_boot: int = 1000, ci: float = 0.95) -> Tuple:
    """Bootstrap 95% CIs for PF, Sharpe, WinRate."""
    if len(rets) < 5:
        z = (0.0, 0.0)
        return z, z, z
    rng = np.random.default_rng(42)
    pf_bs = np.zeros(n_boot)
    sh_bs = np.zeros(n_boot)
    wr_bs = np.zeros(n_boot)
    for i in range(n_boot):
        sample = rng.choice(rets, size=len(rets), replace=True)
        pf_bs[i] = _profit_factor(sample)
        sh_bs[i] = _sharpe(sample)
        wr_bs[i] = float((sample > 0).mean())
    lo = (1 - ci) / 2
    hi = 1 - lo
    return (
        (float(np.percentile(pf_bs, lo*100)), float(np.percentile(pf_bs, hi*100))),
        (float(np.percentile(sh_bs, lo*100)), float(np.percentile(sh_bs, hi*100))),
        (float(np.percentile(wr_bs, lo*100)), float(np.percentile(wr_bs, hi*100))),
    )


def _empty_stats(symbol: str) -> Dict:
    return {
        "symbol": symbol, "n_bars": 0, "n_trades": 0,
        "profit_factor": 0.0, "sharpe": 0.0, "sortino": 0.0, "calmar": 0.0,
        "win_rate": 0.0, "expectancy": 0.0, "total_return": 0.0,
        "max_drawdown": 0.0, "avg_win": 0.0, "avg_loss": 0.0, "payoff_ratio": 0.0,
        "avg_duration_bars": 0.0, "stop_rate": 0.0, "target_rate": 0.0, "timeout_rate": 0.0,
        "no_trade_pct": 0.0, "no_trade_n": 0,
        "regime_occupancy": {r: 0.0 for r in REGIMES_5},
        "trades_by_regime": {r: 0 for r in REGIMES_5},
        "family_usage": {}, "allocator_usage": {},
        "boot_pf_ci_lo": 0.0, "boot_pf_ci_hi": 0.0,
        "boot_sharpe_ci_lo": 0.0, "boot_sharpe_ci_hi": 0.0,
        "boot_wr_ci_lo": 0.0, "boot_wr_ci_hi": 0.0,
    }


# ═══════════════════════════════════════════════════════════════════════════
# All-market statistics
# ═══════════════════════════════════════════════════════════════════════════

def compute_all_stats_2026(
    all_trade_logs: Dict[str, pd.DataFrame],
    all_bar_logs:   Dict[str, pd.DataFrame],
    n_boot: int = 1000,
    verbose: bool = True,
) -> Tuple[pd.DataFrame, Dict[str, Dict]]:
    """
    Compute stats for all 2026 markets.
    Returns (summary_df, full_stats_dict).
    """
    full_stats = {}
    rows = []

    for sym in MARKET_ORDER:
        tl = all_trade_logs.get(sym, pd.DataFrame())
        bl = all_bar_logs.get(sym, pd.DataFrame())
        stats = compute_market_stats(tl, bl, sym, n_boot=n_boot)
        full_stats[sym] = stats

        if verbose:
            print(f"  [{sym}] trades={stats['n_trades']:>4} "
                  f"PF={stats['profit_factor']:.3f} "
                  f"Sharpe={stats['sharpe']:.3f} "
                  f"WR={stats['win_rate']:.1%} "
                  f"MDD={stats['max_drawdown']:.4f} "
                  f"NoTrade%={stats['no_trade_pct']:.1%}", flush=True)

        row = {k: v for k, v in stats.items()
               if not isinstance(v, (dict, list))}
        rows.append(row)

    return pd.DataFrame(rows), full_stats


# ═══════════════════════════════════════════════════════════════════════════
# Phase 4 (2025) stats reader for comparison
# ═══════════════════════════════════════════════════════════════════════════

def load_phase4_stats() -> Dict[str, Dict]:
    """
    Load Phase 4 (2025) per-market statistics from the Phase 4 runs parquets.
    Returns {symbol: stats_dict} with same keys as compute_market_stats.
    """
    stats = {}
    for sym in MARKET_ORDER:
        metrics_path = PHASE4_DIR / "runs" / f"metrics_{sym}.parquet"
        pl_trades    = PHASE4_DIR / "runs" / f"pl_trades_{sym}.parquet"
        if not metrics_path.exists():
            stats[sym] = _empty_stats(sym)
            continue
        try:
            metrics_df = pd.read_parquet(metrics_path)
            # Get ALL-regime rows
            sub = metrics_df[metrics_df["regime"] == "ALL"] if "regime" in metrics_df.columns else metrics_df

            # Compute aggregate stats from per-strategy regime rows
            # We need trade log from pl_trades + reconstruct
            # Use best strategy from allocator
            allocator_path = PHASE4_DIR / "allocator_by_market.csv"
            if allocator_path.exists():
                alloc = pd.read_csv(allocator_path)
                alloc_sym = alloc[alloc["symbol"] == sym]
            else:
                alloc_sym = pd.DataFrame()

            # Find ALL-regime best strategy stats
            if len(alloc_sym) > 0 and len(sub) > 0:
                best_strategies = alloc_sym[alloc_sym["best_strategy"] != "NO_TRADE"]["best_strategy"].tolist()
                active_rows = sub[sub["strategy"].isin(best_strategies)] if best_strategies else sub
            else:
                active_rows = sub

            if len(active_rows) == 0:
                stats[sym] = _empty_stats(sym)
                continue

            # Aggregate metrics across active strategies
            pf_vals     = active_rows["profit_factor"].values
            sh_vals     = active_rows["sharpe"].values
            wr_vals     = active_rows["win_rate"].values
            tc_vals     = active_rows["trade_count"].values
            ret_vals    = active_rows["total_return"].values
            dd_vals     = active_rows["max_drawdown"].values
            exp_vals    = active_rows["expectancy"].values

            # Weighted by trade count
            total_tc    = tc_vals.sum()
            w           = tc_vals / max(total_tc, 1)
            pf_agg      = float(np.average(pf_vals,  weights=w+1e-12))
            sh_agg      = float(np.average(sh_vals,  weights=w+1e-12))
            wr_agg      = float(np.average(wr_vals,  weights=w+1e-12))
            exp_agg     = float(np.average(exp_vals, weights=w+1e-12))
            dd_agg      = float(dd_vals.max())
            ret_agg     = float(ret_vals.sum())

            # Regime occupancy from metrics
            regime_occ = {}
            for regime in REGIMES_5:
                regime_rows = metrics_df[metrics_df["regime"] == regime]
                if len(regime_rows) > 0:
                    regime_occ[regime] = float(regime_rows["trade_count"].mean()) / max(total_tc, 1)
                else:
                    regime_occ[regime] = 0.0

            stats[sym] = {
                "symbol"           : sym,
                "n_bars"           : 0,   # not available from metrics parquet
                "n_trades"         : int(total_tc),
                "profit_factor"    : round(pf_agg, 4),
                "sharpe"           : round(sh_agg, 4),
                "sortino"          : 0.0,
                "calmar"           : 0.0,
                "win_rate"         : round(wr_agg, 4),
                "expectancy"       : round(exp_agg, 6),
                "total_return"     : round(ret_agg, 6),
                "max_drawdown"     : round(dd_agg, 6),
                "avg_win"          : 0.0,
                "avg_loss"         : 0.0,
                "payoff_ratio"     : 0.0,
                "avg_duration_bars": 0.0,
                "stop_rate"        : 0.0,
                "target_rate"      : 0.0,
                "timeout_rate"     : 0.0,
                "no_trade_pct"     : 0.0,
                "no_trade_n"       : 0,
                "regime_occupancy" : regime_occ,
                "trades_by_regime" : {r: 0 for r in REGIMES_5},
                "family_usage"     : {},
                "allocator_usage"  : {},
            }
        except Exception as e:
            print(f"  [{sym}] WARNING loading P4 stats: {e}", flush=True)
            stats[sym] = _empty_stats(sym)

    return stats


# ═══════════════════════════════════════════════════════════════════════════
# Comparison table: 2025 vs 2026
# ═══════════════════════════════════════════════════════════════════════════

def build_comparison_table(
    stats_2026: Dict[str, Dict],
    stats_2025: Dict[str, Dict],
) -> pd.DataFrame:
    """Side-by-side 2025 vs 2026 performance comparison."""
    rows = []
    metrics = ["profit_factor", "sharpe", "win_rate", "expectancy",
               "max_drawdown", "n_trades", "no_trade_pct"]

    for sym in MARKET_ORDER:
        s25 = stats_2025.get(sym, _empty_stats(sym))
        s26 = stats_2026.get(sym, _empty_stats(sym))

        row = {"symbol": sym}
        for m in metrics:
            v25 = s25.get(m, 0.0)
            v26 = s26.get(m, 0.0)
            row[f"2025_{m}"] = v25
            row[f"2026_{m}"] = v26
            if isinstance(v25, (int, float)) and isinstance(v26, (int, float)):
                if abs(v25) > 1e-12:
                    row[f"delta_{m}"] = round(float(v26) - float(v25), 4)
                    row[f"pct_chg_{m}"] = round((float(v26) - float(v25)) / (abs(float(v25)) + 1e-12) * 100, 2)
                else:
                    row[f"delta_{m}"] = 0.0
                    row[f"pct_chg_{m}"] = 0.0
        rows.append(row)

    return pd.DataFrame(rows)


# ═══════════════════════════════════════════════════════════════════════════
# Per-regime breakdown table
# ═══════════════════════════════════════════════════════════════════════════

def compute_regime_breakdown_2026(
    all_trade_logs: Dict[str, pd.DataFrame],
    all_bar_logs:   Dict[str, pd.DataFrame],
) -> pd.DataFrame:
    """Per-market × per-regime statistics for 2026."""
    rows = []
    for sym in MARKET_ORDER:
        tl = all_trade_logs.get(sym)
        bl = all_bar_logs.get(sym)
        if tl is None:
            continue

        for regime in REGIMES_5:
            sub = tl[tl["regime"] == regime] if "regime" in tl.columns else pd.DataFrame()
            rets = sub["net_ret"].dropna().values if len(sub) > 0 else np.array([])

            # Bar count for regime
            if bl is not None and "regime" in bl.columns:
                n_bars_regime = int((bl["regime"] == regime).sum())
            else:
                n_bars_regime = 0

            rows.append({
                "symbol"        : sym,
                "regime"        : regime,
                "n_bars"        : n_bars_regime,
                "n_trades"      : len(sub),
                "profit_factor" : _profit_factor(rets) if len(rets) > 0 else 0.0,
                "sharpe"        : _sharpe(rets) if len(rets) > 0 else 0.0,
                "win_rate"      : float((rets > 0).mean()) if len(rets) > 0 else 0.0,
                "expectancy"    : float(rets.mean()) if len(rets) > 0 else 0.0,
                "max_drawdown"  : _max_drawdown(rets) if len(rets) > 0 else 0.0,
                "total_return"  : float(rets.sum()) if len(rets) > 0 else 0.0,
            })

    return pd.DataFrame(rows)


# ═══════════════════════════════════════════════════════════════════════════
# Market summary CSV builder
# ═══════════════════════════════════════════════════════════════════════════

def build_market_summary_csv(
    stats_2026: Dict[str, Dict],
) -> pd.DataFrame:
    """Flat CSV row per market for market_summary_2026.csv."""
    rows = []
    for sym in MARKET_ORDER:
        s = stats_2026.get(sym, _empty_stats(sym))
        row = {
            "symbol"           : sym,
            "n_bars"           : s.get("n_bars", 0),
            "n_trades"         : s.get("n_trades", 0),
            "profit_factor"    : s.get("profit_factor", 0.0),
            "sharpe"           : s.get("sharpe", 0.0),
            "sortino"          : s.get("sortino", 0.0),
            "calmar"           : s.get("calmar", 0.0),
            "win_rate"         : s.get("win_rate", 0.0),
            "expectancy"       : s.get("expectancy", 0.0),
            "total_return"     : s.get("total_return", 0.0),
            "max_drawdown"     : s.get("max_drawdown", 0.0),
            "payoff_ratio"     : s.get("payoff_ratio", 0.0),
            "avg_duration_bars": s.get("avg_duration_bars", 0.0),
            "stop_rate"        : s.get("stop_rate", 0.0),
            "target_rate"      : s.get("target_rate", 0.0),
            "no_trade_pct"     : s.get("no_trade_pct", 0.0),
            "boot_pf_ci_lo"    : s.get("boot_pf_ci_lo", 0.0),
            "boot_pf_ci_hi"    : s.get("boot_pf_ci_hi", 0.0),
            "boot_sharpe_ci_lo": s.get("boot_sharpe_ci_lo", 0.0),
            "boot_sharpe_ci_hi": s.get("boot_sharpe_ci_hi", 0.0),
            "boot_wr_ci_lo"    : s.get("boot_wr_ci_lo", 0.0),
            "boot_wr_ci_hi"    : s.get("boot_wr_ci_hi", 0.0),
        }
        # Regime occupancy columns
        occ = s.get("regime_occupancy", {})
        for regime in REGIMES_5:
            row[f"occ_{regime[:4]}"] = round(occ.get(regime, 0.0), 4)

        rows.append(row)

    return pd.DataFrame(rows)
