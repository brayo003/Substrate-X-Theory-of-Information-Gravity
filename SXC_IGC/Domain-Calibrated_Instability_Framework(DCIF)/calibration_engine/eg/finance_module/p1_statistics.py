"""
p1_statistics.py — Statistical analysis for Phase 1 Transport Strategy Matrix.

Reads from intermediate trade parquet files.
Outputs:
  - strategy × regime performance matrix (phase1_strategy_matrix.csv)
  - bootstrap confidence intervals (bootstrap_statistics.csv)
  - significance tests: Mann-Whitney + BH-FDR + permutation (significance_tests.csv)
  - performance by regime (performance_by_regime.csv)
  - strategy rankings (strategy_rankings.csv)

All computations are stream-friendly: operates on per-strategy trade files,
never loads the entire trade log at once.
"""

import sys
import gc
import warnings
from pathlib import Path
from typing import Dict, List, Optional

import numpy as np
import pandas as pd

warnings.filterwarnings("ignore")

_HERE = Path(__file__).resolve().parent
_CE   = _HERE.parents[1]
for p in [str(_CE), str(_HERE)]:
    if p not in sys.path:
        sys.path.insert(0, p)

from p1_checkpoint import (
    INTERMEDIATE_DIR, RESULTS_DIR,
    intermediate_path_for_strategy,
    mark_stats_complete,
)

REGIMES_5 = [
    "Deep_Incoherent",
    "Mod_Incoherent",
    "Transition",
    "Weak_Coherent",
    "Strong_Coherent",
]

MIN_TRADES_FOR_STATS = 10  # minimum trades per cell


# ═══════════════════════════════════════════════════════════════════════════
# Per-cell metrics
# ═══════════════════════════════════════════════════════════════════════════

def _cell_metrics(trades: pd.DataFrame, strategy: str, family: str, regime: str) -> dict:
    """Compute performance metrics for one (strategy, regime) cell."""
    n = len(trades)
    if n == 0:
        return None

    returns = trades["net_ret"].values.astype(float)
    wins    = returns > 0
    losses  = returns <= 0

    gross_wins  = returns[wins].sum()   if wins.sum()   > 0 else 0.0
    gross_loss  = -returns[losses].sum() if losses.sum() > 0 else 1e-12
    pf          = gross_wins / (gross_loss + 1e-12)
    win_rate    = float(wins.sum()) / n
    avg_trade   = float(returns.mean())
    avg_win     = float(returns[wins].mean())  if wins.sum()  > 0 else 0.0
    avg_loss    = float(returns[losses].mean()) if losses.sum() > 0 else 0.0
    expectancy  = avg_trade

    # Sharpe (annualised, assuming 5-min bars, ~252 trading days × 8h × 12 bars)
    std_r = float(returns.std()) if n > 1 else 1e-12
    sharpe = (avg_trade / (std_r + 1e-12)) * np.sqrt(252 * 96)

    # Sortino
    down   = returns[returns < 0]
    dstd   = float(down.std()) if len(down) > 1 else 1e-12
    sortino = (avg_trade / (dstd + 1e-12)) * np.sqrt(252 * 96)

    # Max drawdown on equity curve
    equity  = np.cumsum(returns)
    running = np.maximum.accumulate(equity)
    dd_arr  = running - equity
    max_dd  = float(dd_arr.max()) if len(dd_arr) > 0 else 0.0

    # Duration
    if "duration_bars" in trades.columns:
        avg_dur = float(trades["duration_bars"].mean())
    else:
        avg_dur = 0.0

    stop_freq   = float(trades["stop_hit"].mean())   if "stop_hit"   in trades.columns else np.nan
    target_freq = float(trades["target_hit"].mean()) if "target_hit" in trades.columns else np.nan

    return {
        "strategy"     : strategy,
        "family"       : family,
        "regime"       : regime,
        "trade_count"  : n,
        "win_rate"     : win_rate,
        "profit_factor": pf,
        "sharpe"       : sharpe,
        "sortino"      : sortino,
        "expectancy"   : expectancy,
        "avg_trade"    : avg_trade,
        "avg_win"      : avg_win,
        "avg_loss"     : avg_loss,
        "max_drawdown" : max_dd,
        "avg_duration" : avg_dur,
        "stop_freq"    : stop_freq,
        "target_freq"  : target_freq,
    }


# ═══════════════════════════════════════════════════════════════════════════
# Matrix builder
# ═══════════════════════════════════════════════════════════════════════════

def build_performance_matrix(strategy_registry: Dict) -> pd.DataFrame:
    """
    Build strategy × regime performance matrix.
    Loads one strategy at a time from intermediate files.
    """
    rows = []

    for strategy_name, meta in strategy_registry.items():
        family = meta["family"]
        p = intermediate_path_for_strategy(strategy_name)
        if not p.exists():
            continue
        try:
            trades = pd.read_parquet(p)
        except Exception as e:
            print(f"  WARNING: could not read {p}: {e}")
            continue

        if len(trades) == 0:
            continue

        # Per-regime metrics
        for regime in REGIMES_5:
            sub = trades[trades["entry_regime"] == regime]
            if len(sub) < MIN_TRADES_FOR_STATS:
                # Still record with 0 trades so the matrix is complete
                rows.append({
                    "strategy": strategy_name, "family": family, "regime": regime,
                    "trade_count": len(sub), "win_rate": np.nan,
                    "profit_factor": np.nan, "sharpe": np.nan, "sortino": np.nan,
                    "expectancy": np.nan, "avg_trade": np.nan,
                    "avg_win": np.nan, "avg_loss": np.nan,
                    "max_drawdown": np.nan, "avg_duration": np.nan,
                    "stop_freq": np.nan, "target_freq": np.nan,
                })
                continue
            cell = _cell_metrics(sub, strategy_name, family, regime)
            if cell:
                rows.append(cell)

        # ALL-regime aggregate
        cell_all = _cell_metrics(trades, strategy_name, family, "ALL")
        if cell_all:
            rows.append(cell_all)

        del trades
        gc.collect()

    return pd.DataFrame(rows) if rows else pd.DataFrame()


# ═══════════════════════════════════════════════════════════════════════════
# Bootstrap confidence intervals
# ═══════════════════════════════════════════════════════════════════════════

def _bootstrap_ci(data: np.ndarray, stat_fn, n_boot: int = 1000,
                  ci: float = 0.95) -> tuple:
    """Bootstrap confidence interval for a statistic."""
    if len(data) < 5:
        return np.nan, np.nan, np.nan
    boot_stats = np.empty(n_boot)
    n = len(data)
    rng = np.random.default_rng(42)
    for i in range(n_boot):
        sample = data[rng.integers(0, n, n)]
        boot_stats[i] = stat_fn(sample)
    lo = (1 - ci) / 2 * 100
    hi = (1 + ci) / 2 * 100
    return float(stat_fn(data)), float(np.percentile(boot_stats, lo)), float(np.percentile(boot_stats, hi))


def build_bootstrap_statistics(strategy_registry: Dict, n_boot: int = 1000) -> pd.DataFrame:
    """Compute bootstrap CIs for mean return and profit factor per strategy × regime."""
    rows = []
    for strategy_name, meta in strategy_registry.items():
        family = meta["family"]
        p = intermediate_path_for_strategy(strategy_name)
        if not p.exists():
            continue
        try:
            trades = pd.read_parquet(p)
        except Exception:
            continue
        if len(trades) == 0:
            continue

        for regime in REGIMES_5 + ["ALL"]:
            sub = trades if regime == "ALL" else trades[trades["entry_regime"] == regime]
            if len(sub) < MIN_TRADES_FOR_STATS:
                continue
            ret = sub["net_ret"].values.astype(float)
            ret = ret[~np.isnan(ret)]
            if len(ret) < 5:
                continue

            mean_est, mean_lo, mean_hi = _bootstrap_ci(ret, np.mean, n_boot)
            # Profit factor bootstrap
            def pf_fn(r):
                w = r[r > 0].sum()
                l = -r[r <= 0].sum()
                return w / (l + 1e-12)
            pf_est, pf_lo, pf_hi = _bootstrap_ci(ret, pf_fn, n_boot)

            rows.append({
                "strategy"         : strategy_name,
                "family"           : family,
                "regime"           : regime,
                "trade_count"      : len(sub),
                "mean_net_ret"     : mean_est,
                "mean_ret_ci_lo"   : mean_lo,
                "mean_ret_ci_hi"   : mean_hi,
                "profit_factor"    : pf_est,
                "pf_ci_lo"         : pf_lo,
                "pf_ci_hi"         : pf_hi,
                "ci_level"         : 0.95,
                "n_bootstrap"      : n_boot,
            })

        del trades
        gc.collect()

    return pd.DataFrame(rows) if rows else pd.DataFrame()


# ═══════════════════════════════════════════════════════════════════════════
# Significance tests: Mann-Whitney + permutation + BH-FDR
# ═══════════════════════════════════════════════════════════════════════════

def _bh_correction(pvals: np.ndarray, alpha: float = 0.05) -> np.ndarray:
    """Benjamini-Hochberg FDR correction. Returns corrected p-values."""
    n = len(pvals)
    if n == 0:
        return np.array([])
    order  = np.argsort(pvals)
    ranks  = np.empty(n, dtype=int)
    ranks[order] = np.arange(1, n + 1)
    corrected = np.minimum(1.0, pvals * n / ranks)
    # Make monotone: corrected[i] = min(corrected[i:])
    for i in range(n - 2, -1, -1):
        corrected[i] = min(corrected[i], corrected[i + 1])
    return corrected


def run_significance_tests(strategy_registry: Dict) -> pd.DataFrame:
    """
    For each strategy: test whether net returns differ across regimes.

    Tests:
      - Mann-Whitney U (best regime vs worst regime)
      - Permutation test (mean return, 1000 shuffles)
      - Cohen's d effect size
      - BH-FDR corrected p-values
    """
    from scipy.stats import mannwhitneyu

    rows = []
    for strategy_name, meta in strategy_registry.items():
        family = meta["family"]
        p = intermediate_path_for_strategy(strategy_name)
        if not p.exists():
            continue
        try:
            trades = pd.read_parquet(p)
        except Exception:
            continue
        if len(trades) == 0:
            continue

        # Group returns by regime
        regime_returns = {}
        for regime in REGIMES_5:
            sub = trades[trades["entry_regime"] == regime]
            if len(sub) >= MIN_TRADES_FOR_STATS:
                regime_returns[regime] = sub["net_ret"].values.astype(float)

        if len(regime_returns) < 2:
            rows.append({
                "strategy": strategy_name, "family": family,
                "n_regimes_tested": len(regime_returns),
                "mw_pval_raw": np.nan, "mw_statistic": np.nan,
                "perm_pval": np.nan, "cohen_d": np.nan,
                "best_regime": "—", "worst_regime": "—",
                "best_mean_ret": np.nan, "worst_mean_ret": np.nan,
                "mw_reject_fdr": False,
            })
            del trades
            gc.collect()
            continue

        # Find best and worst regimes by mean return
        means = {r: float(v.mean()) for r, v in regime_returns.items()}
        best_r  = max(means, key=means.get)
        worst_r = min(means, key=means.get)
        best_v  = regime_returns[best_r]
        worst_v = regime_returns[worst_r]

        # Mann-Whitney U test (best > worst)
        try:
            stat, pval = mannwhitneyu(best_v, worst_v, alternative="greater")
        except Exception:
            stat, pval = np.nan, np.nan

        # Permutation test: mean(best) - mean(worst) under H0: no difference
        perm_pval = np.nan
        if len(best_v) >= 5 and len(worst_v) >= 5:
            obs_diff = float(best_v.mean()) - float(worst_v.mean())
            combined = np.concatenate([best_v, worst_v])
            n_b = len(best_v)
            rng = np.random.default_rng(42)
            count = 0
            n_perm = 1000
            for _ in range(n_perm):
                shuf = rng.permutation(combined)
                diff = shuf[:n_b].mean() - shuf[n_b:].mean()
                if diff >= obs_diff:
                    count += 1
            perm_pval = float(count) / n_perm

        # Cohen's d
        pooled_std = np.sqrt((best_v.var() + worst_v.var()) / 2.0 + 1e-12)
        cohen_d    = (float(best_v.mean()) - float(worst_v.mean())) / pooled_std

        rows.append({
            "strategy"         : strategy_name,
            "family"           : family,
            "n_regimes_tested" : len(regime_returns),
            "mw_pval_raw"      : float(pval) if not np.isnan(pval) else np.nan,
            "mw_statistic"     : float(stat) if not np.isnan(stat) else np.nan,
            "perm_pval"        : float(perm_pval),
            "cohen_d"          : float(cohen_d),
            "best_regime"      : best_r,
            "worst_regime"     : worst_r,
            "best_mean_ret"    : float(best_v.mean()),
            "worst_mean_ret"   : float(worst_v.mean()),
            "mw_reject_fdr"    : False,  # filled in after BH correction
        })
        del trades
        gc.collect()

    if not rows:
        return pd.DataFrame()

    df = pd.DataFrame(rows)

    # BH-FDR correction on valid p-values
    valid_mask = df["mw_pval_raw"].notna()
    if valid_mask.sum() > 0:
        raw_pvals = df.loc[valid_mask, "mw_pval_raw"].values
        corrected = _bh_correction(raw_pvals)
        df.loc[valid_mask, "mw_pval_fdr"] = corrected
        df.loc[valid_mask, "mw_reject_fdr"] = corrected < 0.05
    else:
        df["mw_pval_fdr"]   = np.nan
        df["mw_reject_fdr"] = False

    return df


# ═══════════════════════════════════════════════════════════════════════════
# Main entry point
# ═══════════════════════════════════════════════════════════════════════════

def run_full_statistics(
    strategy_registry: Dict,
    manifest: Dict,
    n_boot: int = 1000,
    verbose: bool = True,
) -> tuple:
    """
    Compute and save all statistics. Returns (matrix_df, bootstrap_df, sig_df).
    """
    if verbose:
        print("  Building performance matrix …", flush=True)
    matrix_df = build_performance_matrix(strategy_registry)

    if verbose:
        print(f"  Matrix rows: {len(matrix_df)}")
        valid_cells = matrix_df[matrix_df["trade_count"] >= MIN_TRADES_FOR_STATS]
        print(f"  Cells with ≥{MIN_TRADES_FOR_STATS} trades: {len(valid_cells)}", flush=True)

    if verbose:
        print("  Running bootstrap CI …", flush=True)
    boot_df = build_bootstrap_statistics(strategy_registry, n_boot=n_boot)

    if verbose:
        print("  Running significance tests …", flush=True)
    sig_df = run_significance_tests(strategy_registry)

    n_sig = int(sig_df["mw_reject_fdr"].sum()) if "mw_reject_fdr" in sig_df.columns else 0
    if verbose:
        print(f"  FDR-significant strategies: {n_sig}/{len(sig_df)}", flush=True)

    # Save outputs
    matrix_df.to_csv(RESULTS_DIR / "phase1_strategy_matrix.csv", index=False)
    boot_df.to_csv(RESULTS_DIR / "bootstrap_statistics.csv", index=False)
    sig_df.to_csv(RESULTS_DIR / "significance_tests.csv", index=False)

    perf_by_regime = matrix_df[matrix_df["regime"] != "ALL"].copy()
    perf_by_regime.to_csv(RESULTS_DIR / "performance_by_regime.csv", index=False)

    # Strategy rankings by composite score across all regimes
    rankings = _build_rankings(matrix_df, sig_df)
    rankings.to_csv(RESULTS_DIR / "strategy_rankings.csv", index=False)

    mark_stats_complete(manifest)
    if verbose:
        print("  Statistics complete. All CSVs saved.", flush=True)

    return matrix_df, boot_df, sig_df


def _build_rankings(matrix_df: pd.DataFrame, sig_df: pd.DataFrame) -> pd.DataFrame:
    """Rank strategies by composite score across all trades (ALL regime)."""
    all_rows = matrix_df[matrix_df["regime"] == "ALL"].copy()
    if len(all_rows) == 0:
        return pd.DataFrame()

    # Normalise components
    def _norm(s):
        mn, mx = s.min(), s.max()
        if mx == mn:
            return pd.Series(0.5, index=s.index)
        return (s - mn) / (mx - mn + 1e-12)

    all_rows = all_rows.copy()
    all_rows["pf_n"]  = _norm(all_rows["profit_factor"].fillna(0))
    all_rows["sr_n"]  = _norm(all_rows["sharpe"].fillna(-10))
    all_rows["wr_n"]  = _norm(all_rows["win_rate"].fillna(0))
    all_rows["exp_n"] = _norm(all_rows["expectancy"].fillna(0))

    all_rows["composite"] = (
        0.40 * all_rows["pf_n"] +
        0.30 * all_rows["sr_n"] +
        0.20 * all_rows["wr_n"] +
        0.10 * all_rows["exp_n"]
    )

    # FDR bonus
    if sig_df is not None and len(sig_df) > 0 and "mw_reject_fdr" in sig_df.columns:
        sig_map = dict(zip(sig_df["strategy"], sig_df["mw_reject_fdr"]))
        all_rows["sig_bonus"] = all_rows["strategy"].map(sig_map).fillna(False).astype(float) * 0.20
        all_rows["composite"] += all_rows["sig_bonus"]

    all_rows = all_rows.sort_values("composite", ascending=False).reset_index(drop=True)
    all_rows["rank"] = all_rows.index + 1

    cols = ["rank","strategy","family","composite","profit_factor","sharpe",
            "win_rate","expectancy","trade_count"]
    cols = [c for c in cols if c in all_rows.columns]
    return all_rows[cols]
