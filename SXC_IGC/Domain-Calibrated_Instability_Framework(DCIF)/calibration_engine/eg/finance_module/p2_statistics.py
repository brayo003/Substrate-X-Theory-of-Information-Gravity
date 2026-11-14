"""
p2_statistics.py — Full metrics suite + statistical tests for Phase 2.

Metrics per portfolio (OS or baseline):
  PF, Sharpe, Sortino, Expectancy, Max Drawdown, Recovery Factor,
  Ulcer Index, Average Trade, Trade Duration, Exposure, Trades, Win Rate,
  Target %, Stop %, Calmar Ratio.

Statistical tests (OS vs each baseline):
  Bootstrap CI, Permutation test, Mann-Whitney U, Wilcoxon signed-rank,
  Effect size (Cohen's d), BH-FDR correction.
"""

import sys
import warnings
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import numpy as np
import pandas as pd

warnings.filterwarnings("ignore")

_HERE = Path(__file__).resolve().parent
_CE   = _HERE.parents[1]
for p in [str(_CE), str(_HERE)]:
    if p not in sys.path:
        sys.path.insert(0, p)

BARS_PER_YEAR = 252 * 96   # 5-min bars (252 trading days × 8h × 12 bars/h)


# ═══════════════════════════════════════════════════════════════════════════
# Core metrics
# ═══════════════════════════════════════════════════════════════════════════

def compute_metrics(trades_df: pd.DataFrame, label: str = "") -> dict:
    """Compute full metrics for one portfolio of trades."""
    if trades_df is None or len(trades_df) == 0:
        return _empty_metrics(label)

    # Use scaled_net if available (risk-adjusted), else net_ret
    ret_col = "scaled_net" if "scaled_net" in trades_df.columns else "net_ret"
    returns = trades_df[ret_col].values.astype(float)
    returns = returns[~np.isnan(returns)]

    if len(returns) == 0:
        return _empty_metrics(label)

    n         = len(returns)
    wins      = returns > 0
    losses    = returns <= 0
    n_wins    = int(wins.sum())
    n_losses  = int(losses.sum())
    win_rate  = n_wins / n

    gross_wins = float(returns[wins].sum())  if n_wins   > 0 else 0.0
    gross_loss = float(-returns[losses].sum()) if n_losses > 0 else 1e-12
    pf         = gross_wins / (gross_loss + 1e-12)

    avg_trade  = float(returns.mean())
    avg_win    = float(returns[wins].mean())    if n_wins   > 0 else 0.0
    avg_loss_v = float(returns[losses].mean())  if n_losses > 0 else 0.0
    expectancy = avg_trade

    # Sharpe (annualised on trade returns — approximate)
    std_r = float(returns.std()) if n > 1 else 1e-12
    # Per-trade Sharpe: sqrt(N_per_year) normalisation
    try:
        if "exit_ts" in trades_df.columns and len(trades_df) > 1:
            t0 = pd.to_datetime(trades_df["exit_ts"].iloc[0],  utc=True, errors="coerce")
            t1 = pd.to_datetime(trades_df["exit_ts"].iloc[-1], utc=True, errors="coerce")
            span_years = max((t1 - t0).days / 365.0, 0.001) if pd.notna(t0) and pd.notna(t1) else 1.0
            trades_per_year = n / span_years
        else:
            trades_per_year = float(n)
    except Exception:
        trades_per_year = float(n)
    sharpe  = (avg_trade / (std_r + 1e-12)) * np.sqrt(max(trades_per_year, 1))

    # Sortino
    down    = returns[returns < 0]
    dstd    = float(down.std()) if len(down) > 1 else 1e-12
    sortino = (avg_trade / (dstd + 1e-12)) * np.sqrt(max(trades_per_year, 1))

    # Drawdown on cumulative return curve
    equity  = np.cumsum(returns)
    running = np.maximum.accumulate(equity)
    dd_arr  = running - equity
    max_dd  = float(dd_arr.max()) if len(dd_arr) > 0 else 0.0

    # Ulcer Index: RMS of percentage drawdowns from peaks
    if running.max() > 0:
        pct_dd     = dd_arr / (running + 1e-12) * 100.0
        ulcer      = float(np.sqrt(np.mean(pct_dd ** 2)))
    else:
        ulcer      = 0.0

    # Recovery Factor: total return / max_dd
    total_ret      = float(equity[-1]) if len(equity) > 0 else 0.0
    recovery_factor= total_ret / (max_dd + 1e-12)

    # Calmar
    calmar  = avg_trade / (max_dd + 1e-12) * trades_per_year

    # Duration stats
    if "duration_bars" in trades_df.columns:
        avg_dur = float(trades_df["duration_bars"].mean())
        med_dur = float(trades_df["duration_bars"].median())
    else:
        avg_dur = med_dur = 0.0

    # Stop / target frequency
    stop_freq   = float(trades_df["stop_hit"].mean())   if "stop_hit"   in trades_df.columns else np.nan
    target_freq = float(trades_df["target_hit"].mean()) if "target_hit" in trades_df.columns else np.nan
    timeout_freq= float(trades_df["timeout"].mean())    if "timeout"    in trades_df.columns else np.nan

    # Exposure: fraction of total bars where a trade was open
    if "duration_bars" in trades_df.columns:
        exposure_bars = float(trades_df["duration_bars"].sum())
    else:
        exposure_bars = n * avg_dur
    # Total bars estimated from decision log is not available here;
    # we mark exposure as trades×avg_dur / total_analysis_bars
    # This is approximated as 209689 (from Phase 1 execution profile)
    TOTAL_BARS_APPROX = 209_689
    exposure = min(1.0, exposure_bars / TOTAL_BARS_APPROX)

    return {
        "label"           : label,
        "trade_count"     : n,
        "win_rate"        : win_rate,
        "profit_factor"   : pf,
        "sharpe"          : sharpe,
        "sortino"         : sortino,
        "expectancy"      : expectancy,
        "avg_trade"       : avg_trade,
        "avg_win"         : avg_win,
        "avg_loss"        : avg_loss_v,
        "total_return"    : total_ret,
        "max_drawdown"    : max_dd,
        "recovery_factor" : recovery_factor,
        "ulcer_index"     : ulcer,
        "calmar"          : calmar,
        "avg_duration_bars": avg_dur,
        "med_duration_bars": med_dur,
        "stop_freq"       : stop_freq,
        "target_freq"     : target_freq,
        "timeout_freq"    : timeout_freq,
        "exposure"        : exposure,
        "trades_per_year" : trades_per_year,
    }


def _empty_metrics(label: str) -> dict:
    keys = ["label","trade_count","win_rate","profit_factor","sharpe","sortino",
            "expectancy","avg_trade","avg_win","avg_loss","total_return",
            "max_drawdown","recovery_factor","ulcer_index","calmar",
            "avg_duration_bars","med_duration_bars","stop_freq","target_freq",
            "timeout_freq","exposure","trades_per_year"]
    d = {k: np.nan for k in keys}
    d["label"] = label
    d["trade_count"] = 0
    return d


# ═══════════════════════════════════════════════════════════════════════════
# Build full comparison table
# ═══════════════════════════════════════════════════════════════════════════

def build_comparison_table(
    os_trades: pd.DataFrame,
    baseline_trades: Dict[str, pd.DataFrame],
) -> pd.DataFrame:
    """Compute metrics for OS + all baselines, return comparison DataFrame."""
    rows = []
    rows.append(compute_metrics(os_trades, label="Transport_OS"))
    for bname, df in baseline_trades.items():
        rows.append(compute_metrics(df, label=bname))
    return pd.DataFrame(rows)


# ═══════════════════════════════════════════════════════════════════════════
# Statistical tests: OS vs each baseline
# ═══════════════════════════════════════════════════════════════════════════

def _bh_correction(pvals: np.ndarray) -> np.ndarray:
    n = len(pvals)
    if n == 0:
        return np.array([])
    order = np.argsort(pvals)
    ranks = np.empty(n, dtype=int)
    ranks[order] = np.arange(1, n + 1)
    corrected = np.minimum(1.0, pvals * n / ranks)
    for i in range(n - 2, -1, -1):
        corrected[i] = min(corrected[i], corrected[i + 1])
    return corrected


def _bootstrap_ci(data: np.ndarray, stat_fn, n_boot: int = 1000) -> Tuple[float, float, float]:
    if len(data) < 5:
        return np.nan, np.nan, np.nan
    rng = np.random.default_rng(42)
    boot = np.array([stat_fn(data[rng.integers(0, len(data), len(data))]) for _ in range(n_boot)])
    return float(stat_fn(data)), float(np.percentile(boot, 2.5)), float(np.percentile(boot, 97.5))


def run_statistical_tests(
    os_trades: pd.DataFrame,
    baseline_trades: Dict[str, pd.DataFrame],
    n_boot: int = 1000,
) -> pd.DataFrame:
    """
    For each baseline: test whether OS net returns differ (OS > baseline).

    Tests:
      - Bootstrap 95% CI on mean return difference
      - Permutation test (1000 shuffles)
      - Mann-Whitney U (OS > baseline)
      - Wilcoxon signed-rank (matched-pairs if possible, else falls back to MW)
      - Cohen's d
      - BH-FDR on all MW p-values
    """
    from scipy.stats import mannwhitneyu, wilcoxon

    ret_col = "scaled_net" if "scaled_net" in os_trades.columns else "net_ret"
    if len(os_trades) == 0:
        return pd.DataFrame()

    os_ret = os_trades[ret_col].dropna().values.astype(float)

    rows = []
    pvals_raw = []

    for bname, bdf in baseline_trades.items():
        if len(bdf) == 0:
            rows.append({"baseline": bname, "mw_pval": np.nan})
            pvals_raw.append(1.0)
            continue

        b_ret_col = "scaled_net" if "scaled_net" in bdf.columns else "net_ret"
        b_ret = bdf[b_ret_col].dropna().values.astype(float)

        # Mean difference + bootstrap CI
        obs_diff = float(os_ret.mean()) - float(b_ret.mean())
        combined = np.concatenate([os_ret, b_ret])
        n_os = len(os_ret)
        rng = np.random.default_rng(42)
        perm_count = 0
        n_perm = n_boot
        for _ in range(n_perm):
            shuf = rng.permutation(combined)
            diff = shuf[:n_os].mean() - shuf[n_os:].mean()
            if diff >= obs_diff:
                perm_count += 1
        perm_pval = perm_count / n_perm

        # Mann-Whitney
        try:
            mw_stat, mw_pval = mannwhitneyu(os_ret, b_ret, alternative="greater")
        except Exception:
            mw_stat, mw_pval = np.nan, np.nan

        # Wilcoxon (only if same length; otherwise skip)
        wc_pval = np.nan
        if len(os_ret) == len(b_ret):
            try:
                _, wc_pval = wilcoxon(os_ret, b_ret, alternative="greater")
            except Exception:
                pass

        # Bootstrap CI on difference
        def diff_fn(r): return r[:n_os].mean() - r[n_os:].mean()
        _, diff_lo, diff_hi = _bootstrap_ci(combined, lambda r: r[:n_os].mean() - r[n_os:].mean(), n_boot)

        # Cohen's d
        pool_std = np.sqrt((os_ret.var() + b_ret.var()) / 2.0 + 1e-12)
        cohen_d  = obs_diff / pool_std

        pvals_raw.append(float(mw_pval) if not np.isnan(mw_pval) else 1.0)
        rows.append({
            "baseline"            : bname,
            "os_mean_ret"         : float(os_ret.mean()),
            "baseline_mean_ret"   : float(b_ret.mean()),
            "mean_diff"           : obs_diff,
            "diff_ci_lo"          : diff_lo,
            "diff_ci_hi"          : diff_hi,
            "perm_pval"           : perm_pval,
            "mw_pval"             : float(mw_pval) if not np.isnan(mw_pval) else np.nan,
            "mw_stat"             : float(mw_stat) if not np.isnan(mw_stat) else np.nan,
            "wilcoxon_pval"       : wc_pval,
            "cohen_d"             : cohen_d,
            "n_os"                : n_os,
            "n_baseline"          : len(b_ret),
            "os_pf"               : float(os_ret[os_ret > 0].sum()) / (float(-os_ret[os_ret <= 0].sum()) + 1e-12),
            "baseline_pf"         : float(b_ret[b_ret > 0].sum()) / (float(-b_ret[b_ret <= 0].sum()) + 1e-12),
        })

    if not rows:
        return pd.DataFrame()

    df = pd.DataFrame(rows)
    valid = df["mw_pval"].notna()
    if valid.sum() > 0:
        raw_p = df.loc[valid, "mw_pval"].values
        corrected = _bh_correction(raw_p)
        df.loc[valid, "mw_pval_fdr"] = corrected
        df.loc[valid, "mw_reject_fdr"] = corrected < 0.05
    else:
        df["mw_pval_fdr"] = np.nan
        df["mw_reject_fdr"] = False

    return df
