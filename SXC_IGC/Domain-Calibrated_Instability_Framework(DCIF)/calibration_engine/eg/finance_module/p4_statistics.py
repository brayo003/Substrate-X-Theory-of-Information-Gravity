"""
p4_statistics.py — Full statistical tests for Phase 4.

Covers:
  - Bootstrap CI (PF, Sharpe, mean return)
  - Permutation test (mean difference)
  - Mann-Whitney U
  - Wilcoxon signed-rank
  - Cohen's d effect size
  - Benjamini-Hochberg FDR correction
"""

import warnings
from typing import Dict, List, Tuple, Optional

import numpy as np
import pandas as pd
from scipy import stats

warnings.filterwarnings("ignore")

REGIMES_5 = ["Deep_Incoherent","Mod_Incoherent","Transition","Weak_Coherent","Strong_Coherent"]
MIN_TRADES = 5
N_BOOT_DEFAULT = 500


# ── BH-FDR ───────────────────────────────────────────────────────────────

def bh_fdr(p_values: List[float], alpha: float = 0.05) -> List[bool]:
    n = len(p_values)
    if n == 0:
        return []
    idx  = np.argsort(p_values)
    sp   = np.array(p_values)[idx]
    thr  = [(i+1)/n * alpha for i in range(n)]
    rej  = np.array([p <= t for p, t in zip(sp, thr)])
    last = -1
    for i in range(n-1, -1, -1):
        if rej[i]:
            last = i; break
    result = np.zeros(n, dtype=bool)
    if last >= 0:
        result[idx[:last+1]] = True
    return result.tolist()


# ── Bootstrap ────────────────────────────────────────────────────────────

def bootstrap_ci(
    rets: np.ndarray,
    metric_fn,
    n_boot: int = N_BOOT_DEFAULT,
    ci: float = 0.95,
    seed: int = 42,
) -> Tuple[float, float, float]:
    if len(rets) == 0:
        return 0.0, 0.0, 0.0
    pt  = metric_fn(rets)
    rng = np.random.default_rng(seed)
    boots = [metric_fn(rng.choice(rets, size=len(rets), replace=True)) for _ in range(n_boot)]
    a = (1 - ci) / 2
    return float(pt), float(np.percentile(boots, a*100)), float(np.percentile(boots, (1-a)*100))


def _pf(rets):
    w = rets[rets>0].sum(); l = abs(rets[rets<0].sum())
    return w/(l+1e-12) if l>0 else (99.0 if w>0 else 0.0)


def _sharpe(rets):
    if len(rets)<2: return 0.0
    return float(rets.mean()/(rets.std()+1e-12)*np.sqrt(len(rets)))


# ── Per-strategy full stats ───────────────────────────────────────────────

def compute_full_stats(
    trades: pd.DataFrame,
    symbol: str,
    strategy: str,
    family: str,
    regime: str,
    n_boot: int = N_BOOT_DEFAULT,
) -> dict:
    """Compute full statistical suite for one (market, strategy, regime) cell."""
    if trades is None or len(trades) == 0:
        return _empty(symbol, strategy, family, regime)

    rets = trades["net_ret"].dropna().values
    if len(rets) == 0:
        return _empty(symbol, strategy, family, regime)

    wins   = rets[rets>0]; losses = rets[rets<0]
    n      = len(rets)
    pf     = _pf(pd.Series(wins), pd.Series(losses))
    wr     = len(wins)/n
    expect = float(rets.mean())
    std_r  = float(rets.std())  if n>1 else 1e-12
    sharpe = expect/(std_r+1e-12)*np.sqrt(n)
    dstd   = float(losses.std()) if len(losses)>1 else 1e-12
    sortino= expect/(dstd+1e-12)*np.sqrt(n)
    equity = np.cumsum(rets)
    dd     = float((np.maximum.accumulate(equity)-equity).max()) if len(equity)>0 else 0.0

    # Bootstrap
    pf_est, pf_lo, pf_hi       = bootstrap_ci(rets, _pf,     n_boot)
    sr_est, sr_lo, sr_hi       = bootstrap_ci(rets, _sharpe,  n_boot)
    mn_est, mn_lo, mn_hi       = bootstrap_ci(rets, np.mean,  n_boot) if n>0 else (0.,0.,0.)

    # Wilcoxon signed-rank vs zero (H0: median return = 0)
    wil_stat = wil_p = np.nan
    if n >= 10:
        try:
            wil_stat, wil_p = stats.wilcoxon(rets)
        except Exception:
            pass

    return {
        "symbol": symbol, "strategy": strategy, "family": family, "regime": regime,
        "n": n, "win_rate": wr, "profit_factor": pf, "sharpe": sharpe,
        "sortino": sortino, "expectancy": expect, "max_drawdown": dd,
        "total_return": float(equity[-1]) if len(equity)>0 else 0.0,
        "pf_ci_lo": pf_lo, "pf_ci_hi": pf_hi,
        "sharpe_ci_lo": sr_lo, "sharpe_ci_hi": sr_hi,
        "mean_ret_ci_lo": mn_lo, "mean_ret_ci_hi": mn_hi,
        "wilcoxon_stat": float(wil_stat) if not np.isnan(wil_stat) else np.nan,
        "wilcoxon_p": float(wil_p) if not np.isnan(wil_p) else np.nan,
    }


def _empty(symbol, strategy, family, regime):
    return {"symbol": symbol, "strategy": strategy, "family": family, "regime": regime,
            "n": 0, "win_rate": 0., "profit_factor": 0., "sharpe": 0., "sortino": 0.,
            "expectancy": 0., "max_drawdown": 0., "total_return": 0.,
            "pf_ci_lo": 0., "pf_ci_hi": 0., "sharpe_ci_lo": 0., "sharpe_ci_hi": 0.,
            "mean_ret_ci_lo": 0., "mean_ret_ci_hi": 0.,
            "wilcoxon_stat": np.nan, "wilcoxon_p": np.nan}


# ── Cross-family pairwise tests ───────────────────────────────────────────

def run_family_pairwise_tests(
    metrics_df: pd.DataFrame,
    symbol: str,
    regime: str,
    n_boot: int = N_BOOT_DEFAULT,
    seed: int = 42,
) -> pd.DataFrame:
    """
    For one (market, regime), run MW and permutation tests between
    each pair of strategy families.
    Returns DataFrame of pairwise test results with BH-FDR applied.
    """
    sub = metrics_df[
        (metrics_df["regime"] == regime) &
        (metrics_df["trade_count"] >= MIN_TRADES)
    ]
    if len(sub) == 0:
        return pd.DataFrame()

    families = sub["family"].unique().tolist()
    rng = np.random.default_rng(seed)
    rows = []

    for i, f1 in enumerate(families):
        for j, f2 in enumerate(families):
            if j <= i:
                continue
            pf1 = float(sub[sub["family"]==f1]["profit_factor"].median())
            pf2 = float(sub[sub["family"]==f2]["profit_factor"].median())
            diff = pf1 - pf2

            # Mann-Whitney on PF values
            vals1 = sub[sub["family"]==f1]["profit_factor"].dropna().values
            vals2 = sub[sub["family"]==f2]["profit_factor"].dropna().values
            mw_stat = mw_p = np.nan
            if len(vals1) >= 3 and len(vals2) >= 3:
                try:
                    mw_stat, mw_p = stats.mannwhitneyu(vals1, vals2, alternative="two-sided")
                except Exception:
                    pass

            # Permutation test on median PF difference
            combined = np.concatenate([vals1, vals2])
            perm_diffs = []
            for _ in range(min(n_boot, 200)):
                perm = rng.permutation(combined)
                perm_diffs.append(np.median(perm[:len(vals1)]) - np.median(perm[len(vals1):]))
            perm_p = float(np.mean(np.abs(perm_diffs) >= abs(diff))) if perm_diffs else np.nan

            # Cohen's d on PF
            pooled = np.sqrt((vals1.std()**2*(len(vals1)-1) + vals2.std()**2*(len(vals2)-1))
                             / (len(vals1)+len(vals2)-2+1e-12))
            cohen_d = diff / (pooled + 1e-12)

            rows.append({
                "symbol": symbol, "regime": regime,
                "family_a": f1, "family_b": f2,
                "pf_a": pf1, "pf_b": pf2, "pf_diff": diff,
                "mw_stat": float(mw_stat) if not np.isnan(mw_stat) else np.nan,
                "mw_p": float(mw_p)       if not np.isnan(mw_p)    else np.nan,
                "perm_p": perm_p,
                "cohen_d": float(cohen_d),
                "mw_reject_fdr": False,
            })

    df = pd.DataFrame(rows)
    if len(df) > 0 and "mw_p" in df.columns:
        pvals = df["mw_p"].fillna(1.0).tolist()
        df["mw_reject_fdr"] = bh_fdr(pvals)
    return df


def run_all_pairwise_tests(
    all_metrics: Dict[str, pd.DataFrame],
    n_boot: int = N_BOOT_DEFAULT,
) -> pd.DataFrame:
    """Run family pairwise tests for every (market, regime) combination."""
    frames = []
    for symbol, metrics_df in all_metrics.items():
        if metrics_df is None or len(metrics_df) == 0:
            continue
        for regime in REGIMES_5:
            df = run_family_pairwise_tests(metrics_df, symbol, regime, n_boot)
            if len(df) > 0:
                frames.append(df)
    if not frames:
        return pd.DataFrame()
    return pd.concat(frames, ignore_index=True)


# ── PL-specific stats ─────────────────────────────────────────────────────

def compute_pl_statistics(
    all_metrics: Dict[str, pd.DataFrame],
    n_boot: int = N_BOOT_DEFAULT,
) -> pd.DataFrame:
    """
    For each (market, regime), compare PassiveLiquidity family vs all others.
    Does PL outperform or underperform the field?
    """
    rows = []
    for symbol, metrics_df in all_metrics.items():
        if metrics_df is None or len(metrics_df) == 0:
            continue
        for regime in REGIMES_5:
            sub = metrics_df[
                (metrics_df["regime"] == regime) &
                (metrics_df["trade_count"] >= MIN_TRADES)
            ]
            if len(sub) == 0:
                continue

            pl_sub    = sub[sub["family"] == "PassiveLiquidity"]
            other_sub = sub[sub["family"] != "PassiveLiquidity"]

            pl_pf    = float(pl_sub["profit_factor"].median())    if len(pl_sub)>0 else 0.0
            other_pf = float(other_sub["profit_factor"].median()) if len(other_sub)>0 else 0.0

            # MW test
            pl_vals    = pl_sub["profit_factor"].dropna().values
            other_vals = other_sub["profit_factor"].dropna().values
            mw_p = np.nan
            if len(pl_vals) >= 2 and len(other_vals) >= 2:
                try:
                    _, mw_p = stats.mannwhitneyu(pl_vals, other_vals, alternative="two-sided")
                except Exception:
                    pass

            # Best non-PL family
            best_other_fam = ""
            best_other_pf  = 0.0
            if len(other_sub) > 0:
                fam_pf = other_sub.groupby("family")["profit_factor"].median()
                best_other_fam = str(fam_pf.idxmax())
                best_other_pf  = float(fam_pf.max())

            rows.append({
                "symbol"          : symbol,
                "regime"          : regime,
                "pl_median_pf"    : pl_pf,
                "other_median_pf" : other_pf,
                "pl_vs_other_diff": pl_pf - other_pf,
                "pl_wins"         : int(pl_pf > other_pf),
                "mw_p"            : float(mw_p) if not np.isnan(mw_p) else np.nan,
                "best_other_family": best_other_fam,
                "best_other_pf"   : best_other_pf,
                "pl_n_strategies" : len(pl_sub),
                "other_n_strategies": len(other_sub),
            })

    df = pd.DataFrame(rows)
    if len(df) > 0 and "mw_p" in df.columns:
        pvals = df["mw_p"].fillna(1.0).tolist()
        df["mw_reject_fdr"] = bh_fdr(pvals)
    return df
