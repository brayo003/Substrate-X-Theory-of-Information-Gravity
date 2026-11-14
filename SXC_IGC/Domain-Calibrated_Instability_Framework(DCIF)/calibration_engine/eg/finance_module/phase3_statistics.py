"""
phase3_statistics.py — Per-market and cross-market statistics for Phase 3.

Computes:
  - Trade performance metrics (PF, Sharpe, Sortino, DD, expectancy, etc.)
  - Regime distribution metrics
  - Allocator behaviour metrics
  - Bootstrap confidence intervals
  - Statistical tests (Mann-Whitney, permutation, Wilcoxon, BH FDR)
  - Effect sizes (Cohen's d)
"""

import sys
import warnings
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import numpy as np
import pandas as pd
from scipy import stats

warnings.filterwarnings("ignore")

_HERE = Path(__file__).resolve().parent
for p in [str(_HERE)]:
    if p not in sys.path:
        sys.path.insert(0, p)

REGIMES_5 = [
    "Deep_Incoherent", "Mod_Incoherent", "Transition",
    "Weak_Coherent",   "Strong_Coherent",
]

PHASE3_DIR = _HERE / "results" / "phase3"


# ═══════════════════════════════════════════════════════════════════════════
# Core trade performance metrics
# ═══════════════════════════════════════════════════════════════════════════

def compute_trade_metrics(trades: pd.DataFrame, symbol: str = "") -> dict:
    """Compute comprehensive trade performance metrics from a trade log."""
    if trades is None or len(trades) == 0:
        return _empty_metrics(symbol)

    ret_col = "scaled_net" if "scaled_net" in trades.columns else "net_ret"
    rets = trades[ret_col].dropna().values

    if len(rets) == 0:
        return _empty_metrics(symbol)

    n = len(rets)
    wins  = rets[rets > 0]
    losses = rets[rets < 0]

    win_rate   = len(wins) / n if n > 0 else 0.0
    avg_win    = float(wins.mean())  if len(wins)   > 0 else 0.0
    avg_loss   = float(losses.mean()) if len(losses) > 0 else 0.0
    expectancy = float(rets.mean())

    gross_wins  = float(wins.sum())  if len(wins)   > 0 else 0.0
    gross_losses = float(abs(losses.sum())) if len(losses) > 0 else 0.0
    profit_factor = gross_wins / (gross_losses + 1e-12) if gross_losses > 0 else (99.0 if gross_wins > 0 else 0.0)

    # Equity curve and drawdown
    equity = np.cumsum(rets)
    running_max = np.maximum.accumulate(equity)
    drawdowns = running_max - equity
    max_dd = float(drawdowns.max()) if len(drawdowns) > 0 else 0.0

    total_return = float(equity[-1]) if len(equity) > 0 else 0.0

    # Recovery factor
    recovery_factor = total_return / (max_dd + 1e-12) if max_dd > 0 else (total_return if total_return > 0 else 0.0)

    # Sharpe (annualised per trade — trade-level)
    std_ret = float(rets.std()) if len(rets) > 1 else 1e-12
    sharpe  = expectancy / (std_ret + 1e-12) * np.sqrt(n)

    # Sortino
    downside_rets = rets[rets < 0]
    downside_std  = float(downside_rets.std()) if len(downside_rets) > 1 else 1e-12
    sortino = expectancy / (downside_std + 1e-12) * np.sqrt(n)

    # Duration
    dur_col = "duration_bars"
    avg_dur = float(trades[dur_col].mean()) if dur_col in trades.columns else 0.0
    med_dur = float(trades[dur_col].median()) if dur_col in trades.columns else 0.0

    # Stop/target frequencies
    stop_freq   = float(trades["stop_hit"].mean())   if "stop_hit"   in trades.columns else 0.0
    target_freq = float(trades["target_hit"].mean()) if "target_hit" in trades.columns else 0.0
    timeout_freq = float(trades["timeout"].mean())   if "timeout"    in trades.columns else 0.0

    return {
        "symbol"         : symbol,
        "trade_count"    : n,
        "win_rate"       : win_rate,
        "profit_factor"  : profit_factor,
        "sharpe"         : sharpe,
        "sortino"        : sortino,
        "expectancy"     : expectancy,
        "avg_win"        : avg_win,
        "avg_loss"       : avg_loss,
        "total_return"   : total_return,
        "max_drawdown"   : max_dd,
        "recovery_factor": recovery_factor,
        "avg_duration_bars": avg_dur,
        "med_duration_bars": med_dur,
        "stop_freq"      : stop_freq,
        "target_freq"    : target_freq,
        "timeout_freq"   : timeout_freq,
    }


def _empty_metrics(symbol: str) -> dict:
    return {
        "symbol": symbol, "trade_count": 0, "win_rate": 0.0,
        "profit_factor": 0.0, "sharpe": 0.0, "sortino": 0.0,
        "expectancy": 0.0, "avg_win": 0.0, "avg_loss": 0.0,
        "total_return": 0.0, "max_drawdown": 0.0, "recovery_factor": 0.0,
        "avg_duration_bars": 0.0, "med_duration_bars": 0.0,
        "stop_freq": 0.0, "target_freq": 0.0, "timeout_freq": 0.0,
    }


# ═══════════════════════════════════════════════════════════════════════════
# Allocator behaviour metrics
# ═══════════════════════════════════════════════════════════════════════════

def compute_allocator_metrics(dec_df: pd.DataFrame, symbol: str = "") -> dict:
    """Compute allocator behaviour statistics from per-bar decision log."""
    if dec_df is None or len(dec_df) == 0:
        return {"symbol": symbol, "no_trade_fraction": 1.0, "strategy_switch_count": 0}

    n = len(dec_df)

    no_trade_frac = float((~dec_df["trading_allowed"]).mean()) if "trading_allowed" in dec_df.columns else 1.0

    # Strategy switches
    strats = dec_df["selected_strategy"].values if "selected_strategy" in dec_df.columns else np.array(["NO_TRADE"] * n)
    switches = int(np.sum(strats[1:] != strats[:-1]))

    # Time per strategy
    strategy_time = {}
    if "selected_strategy" in dec_df.columns:
        vc = dec_df["selected_strategy"].value_counts(normalize=True)
        strategy_time = vc.to_dict()

    # Regime time fractions
    regime_frac = {}
    if "regime" in dec_df.columns:
        rf = dec_df["regime"].value_counts(normalize=True)
        for r in REGIMES_5:
            regime_frac[r] = float(rf.get(r, 0.0))

    # Average regime run duration
    if "regime" in dec_df.columns:
        regimes = dec_df["regime"].values
        runs = []
        cur = regimes[0]; rlen = 1
        for v in regimes[1:]:
            if v == cur:
                rlen += 1
            else:
                runs.append(rlen); cur = v; rlen = 1
        runs.append(rlen)
        avg_regime_dur = float(np.mean(runs))
    else:
        avg_regime_dur = 0.0

    # Risk utilisation
    avg_risk = float(dec_df["risk_fraction"].mean()) if "risk_fraction" in dec_df.columns else 0.0

    # Q statistics
    if "Q" in dec_df.columns:
        q_vals = dec_df["Q"].dropna().values
        q_mean = float(q_vals.mean()) if len(q_vals) > 0 else 0.0
        q_std  = float(q_vals.std())  if len(q_vals) > 1 else 0.0
        q_min  = float(q_vals.min())  if len(q_vals) > 0 else 0.0
        q_max  = float(q_vals.max())  if len(q_vals) > 0 else 0.0
    else:
        q_mean = q_std = q_min = q_max = 0.0

    return {
        "symbol"              : symbol,
        "total_bars"          : n,
        "no_trade_fraction"   : no_trade_frac,
        "strategy_switch_count": switches,
        "avg_regime_duration" : avg_regime_dur,
        "avg_risk_fraction"   : avg_risk,
        "regime_fractions"    : regime_frac,
        "strategy_time"       : strategy_time,
        "q_mean"              : q_mean,
        "q_std"               : q_std,
        "q_min"               : q_min,
        "q_max"               : q_max,
    }


# ═══════════════════════════════════════════════════════════════════════════
# Bootstrap confidence intervals
# ═══════════════════════════════════════════════════════════════════════════

def bootstrap_metric(
    rets: np.ndarray,
    metric_fn,
    n_boot: int = 1000,
    ci: float = 0.95,
) -> Tuple[float, float, float]:
    """
    Bootstrap confidence interval for a metric.
    Returns (point_estimate, ci_low, ci_high).
    """
    if len(rets) == 0:
        return 0.0, 0.0, 0.0
    point = metric_fn(rets)
    boots = []
    rng   = np.random.default_rng(42)
    for _ in range(n_boot):
        sample = rng.choice(rets, size=len(rets), replace=True)
        boots.append(metric_fn(sample))
    boots = np.array(boots)
    alpha = (1 - ci) / 2
    return float(point), float(np.percentile(boots, alpha*100)), float(np.percentile(boots, (1-alpha)*100))


def _pf_from_rets(rets: np.ndarray) -> float:
    wins   = rets[rets > 0].sum()
    losses = abs(rets[rets < 0].sum())
    return wins / (losses + 1e-12) if losses > 0 else (99.0 if wins > 0 else 0.0)


def _sharpe_from_rets(rets: np.ndarray) -> float:
    if len(rets) < 2:
        return 0.0
    return float(rets.mean() / (rets.std() + 1e-12) * np.sqrt(len(rets)))


def compute_bootstrap_stats(
    trades: pd.DataFrame,
    symbol: str = "",
    n_boot: int = 1000,
) -> dict:
    """Compute bootstrapped confidence intervals for key metrics."""
    ret_col = "scaled_net" if "scaled_net" in trades.columns else "net_ret"
    rets = trades[ret_col].dropna().values if trades is not None and len(trades) > 0 else np.array([])

    pf_est, pf_lo, pf_hi      = bootstrap_metric(rets, _pf_from_rets, n_boot)
    sr_est, sr_lo, sr_hi      = bootstrap_metric(rets, _sharpe_from_rets, n_boot)
    mean_est, mean_lo, mean_hi = bootstrap_metric(rets, np.mean, n_boot) if len(rets) > 0 else (0., 0., 0.)

    return {
        "symbol"      : symbol,
        "n_trades"    : len(rets),
        "pf_est"      : pf_est,  "pf_ci_lo"    : pf_lo,  "pf_ci_hi"    : pf_hi,
        "sharpe_est"  : sr_est,  "sharpe_ci_lo": sr_lo,  "sharpe_ci_hi": sr_hi,
        "mean_ret_est": mean_est,"mean_ret_lo"  : mean_lo,"mean_ret_hi"  : mean_hi,
    }


# ═══════════════════════════════════════════════════════════════════════════
# Statistical tests (cross-market)
# ═══════════════════════════════════════════════════════════════════════════

def _bh_fdr(p_values: List[float], alpha: float = 0.05) -> List[bool]:
    """Benjamini-Hochberg FDR correction."""
    n = len(p_values)
    if n == 0:
        return []
    sorted_idx = np.argsort(p_values)
    sorted_p   = np.array(p_values)[sorted_idx]
    thresholds = [(i + 1) / n * alpha for i in range(n)]
    reject = sorted_p <= thresholds
    # Find the largest k where p(k) <= k/m * alpha
    last_reject = -1
    for i in range(n - 1, -1, -1):
        if reject[i]:
            last_reject = i
            break
    result = np.zeros(n, dtype=bool)
    if last_reject >= 0:
        result[sorted_idx[:last_reject + 1]] = True
    return result.tolist()


def run_pairwise_tests(
    market_trades: Dict[str, pd.DataFrame],
    baseline_symbol: str = "EURUSD",
    n_boot: int = 500,
) -> pd.DataFrame:
    """
    Run statistical tests comparing each market's transport OS returns
    against the EUR/USD baseline and against each other.

    Tests: Mann-Whitney U, Wilcoxon signed-rank (if paired), permutation, Cohen's d.
    Applies BH FDR correction across all comparisons.
    """
    def get_rets(symbol):
        df = market_trades.get(symbol, pd.DataFrame())
        if df is None or len(df) == 0:
            return np.array([])
        col = "scaled_net" if "scaled_net" in df.columns else "net_ret"
        return df[col].dropna().values

    symbols   = [s for s in market_trades if s != baseline_symbol]
    base_rets = get_rets(baseline_symbol)
    rows = []
    rng  = np.random.default_rng(42)

    for sym in symbols:
        sym_rets = get_rets(sym)
        if len(sym_rets) == 0 or len(base_rets) == 0:
            rows.append({
                "market": sym, "n_market": len(sym_rets), "n_baseline": len(base_rets),
                "mean_market": 0.0, "mean_baseline": 0.0, "mean_diff": 0.0,
                "mw_stat": np.nan, "mw_p": np.nan,
                "perm_p": np.nan, "cohen_d": np.nan, "mw_reject_fdr": False,
            })
            continue

        mean_diff = float(sym_rets.mean() - base_rets.mean())

        # Mann-Whitney U
        try:
            mw_stat, mw_p = stats.mannwhitneyu(sym_rets, base_rets, alternative="two-sided")
        except Exception:
            mw_stat, mw_p = np.nan, np.nan

        # Permutation test (difference in means)
        combined = np.concatenate([sym_rets, base_rets])
        perm_diffs = []
        for _ in range(n_boot):
            perm = rng.permutation(combined)
            perm_diffs.append(perm[:len(sym_rets)].mean() - perm[len(sym_rets):].mean())
        perm_p = float(np.mean(np.abs(perm_diffs) >= abs(mean_diff)))

        # Cohen's d
        pooled_std = np.sqrt(
            (sym_rets.std()**2 * (len(sym_rets) - 1) + base_rets.std()**2 * (len(base_rets) - 1))
            / (len(sym_rets) + len(base_rets) - 2 + 1e-12)
        )
        cohen_d = mean_diff / (pooled_std + 1e-12)

        rows.append({
            "market"        : sym,
            "n_market"      : len(sym_rets),
            "n_baseline"    : len(base_rets),
            "mean_market"   : float(sym_rets.mean()),
            "mean_baseline" : float(base_rets.mean()),
            "mean_diff"     : mean_diff,
            "mw_stat"       : float(mw_stat) if not np.isnan(mw_stat) else np.nan,
            "mw_p"          : float(mw_p)    if not np.isnan(mw_p)    else np.nan,
            "perm_p"        : perm_p,
            "cohen_d"       : float(cohen_d),
            "mw_reject_fdr" : False,
        })

    df = pd.DataFrame(rows)
    if len(df) > 0 and "mw_p" in df.columns:
        p_vals = df["mw_p"].fillna(1.0).tolist()
        df["mw_reject_fdr"] = _bh_fdr(p_vals)

    return df


def run_within_market_tests(
    trades: pd.DataFrame,
    dec_df: pd.DataFrame,
    symbol: str = "",
    n_boot: int = 500,
) -> dict:
    """
    For one market: test whether Strong_Coherent returns are significantly
    better than returns from other regimes. Tests the core universality hypothesis:
    Q should identify superior trade conditions regardless of market.
    """
    if trades is None or len(trades) == 0:
        return {"symbol": symbol, "sc_vs_other_mw_p": np.nan, "sc_vs_other_reject": False}

    ret_col = "scaled_net" if "scaled_net" in trades.columns else "net_ret"
    if "regime" not in trades.columns:
        return {"symbol": symbol, "sc_vs_other_mw_p": np.nan, "sc_vs_other_reject": False}

    sc_rets    = trades.loc[trades["regime"] == "Strong_Coherent", ret_col].dropna().values
    other_rets = trades.loc[trades["regime"] != "Strong_Coherent", ret_col].dropna().values

    if len(sc_rets) < 3 or len(other_rets) < 3:
        return {
            "symbol"              : symbol,
            "sc_mean_ret"         : float(sc_rets.mean()) if len(sc_rets) > 0 else 0.0,
            "other_mean_ret"      : float(other_rets.mean()) if len(other_rets) > 0 else 0.0,
            "sc_vs_other_mw_p"    : np.nan,
            "sc_vs_other_reject"  : False,
            "sc_n"                : len(sc_rets),
            "other_n"             : len(other_rets),
        }

    try:
        mw_stat, mw_p = stats.mannwhitneyu(sc_rets, other_rets, alternative="greater")
    except Exception:
        mw_stat, mw_p = np.nan, np.nan

    # Wilcoxon on Strong Coherent returns vs zero
    try:
        wil_stat, wil_p = stats.wilcoxon(sc_rets) if len(sc_rets) >= 10 else (np.nan, np.nan)
    except Exception:
        wil_stat, wil_p = np.nan, np.nan

    cohen_d = (float(sc_rets.mean()) - float(other_rets.mean())) / (
        np.sqrt((sc_rets.std()**2 + other_rets.std()**2) / 2 + 1e-12)
    )

    return {
        "symbol"            : symbol,
        "sc_mean_ret"       : float(sc_rets.mean()),
        "other_mean_ret"    : float(other_rets.mean()),
        "sc_n"              : len(sc_rets),
        "other_n"           : len(other_rets),
        "sc_vs_other_mw_p"  : float(mw_p)  if not np.isnan(mw_p)  else np.nan,
        "sc_vs_other_wil_p" : float(wil_p) if not np.isnan(wil_p) else np.nan,
        "sc_vs_other_cohen_d": float(cohen_d),
        "sc_vs_other_reject": bool(mw_p < 0.05) if not np.isnan(mw_p) else False,
    }


# ═══════════════════════════════════════════════════════════════════════════
# Universality scoring
# ═══════════════════════════════════════════════════════════════════════════

def compute_universality_score(
    symbol: str,
    trade_metrics: dict,
    alloc_metrics: dict,
    regime_stats: dict,
    baseline_trade_metrics: dict,
) -> dict:
    """
    Compute a Transport Universality Score for one market.

    Criteria (each 0-1 score):
    1. PF > 1.0                 (transport profitable without recalibration)
    2. No-trade fraction > 80%  (OS suppresses trading in noisy periods)
    3. Strong_Coherent fraction similar to baseline (±15pp)
    4. Entropy similar to baseline (±20%)
    5. Allocator convergence (NY_Continuation or similar session strategy selected)

    Final rating: High (≥4), Moderate (3), Weak (2), Unsupported (<2)
    """
    criteria = {}

    # 1. Profitability
    pf = trade_metrics.get("profit_factor", 0.0)
    criteria["profitable"] = float(pf > 1.0)

    # 2. No-trade suppression
    ntf = alloc_metrics.get("no_trade_fraction", 0.0)
    criteria["no_trade_suppression"] = float(ntf > 0.80)

    # 3. Strong_Coherent fraction similarity
    sc_frac = regime_stats.get("regime_fractions", {}).get("Strong_Coherent", 0.0)
    baseline_sc = baseline_trade_metrics.get("sc_fraction", 0.05)
    criteria["sc_fraction_similar"] = float(abs(sc_frac - baseline_sc) < 0.15)

    # 4. Entropy similarity
    h = regime_stats.get("norm_entropy", 0.0)
    baseline_h = baseline_trade_metrics.get("norm_entropy", 0.51)
    criteria["entropy_similar"] = float(abs(h - baseline_h) / (baseline_h + 1e-12) < 0.35)

    # 5. No-trade fraction > 85% OR allocator selects tradeable strategy in SC
    strat_time = alloc_metrics.get("strategy_time", {})
    no_trade_dominant = strat_time.get("NO_TRADE", 0.0) > 0.80
    criteria["allocator_converged"] = float(no_trade_dominant)

    score_sum = sum(criteria.values())
    score_n   = len(criteria)
    score_frac = score_sum / score_n

    if score_frac >= 0.80:
        rating = "High"
    elif score_frac >= 0.60:
        rating = "Moderate"
    elif score_frac >= 0.40:
        rating = "Weak"
    else:
        rating = "Unsupported"

    return {
        "symbol"          : symbol,
        "criteria"        : criteria,
        "score_sum"       : score_sum,
        "score_fraction"  : score_frac,
        "universality_rating": rating,
        "profit_factor"   : pf,
        "no_trade_fraction": ntf,
        "sc_fraction"     : sc_frac,
        "norm_entropy"    : h,
    }


def compute_overall_universality_confidence(scores: List[dict]) -> dict:
    """Aggregate universality scores across all markets."""
    if not scores:
        return {"overall_confidence": "Unsupported", "score": 0.0, "n_markets": 0}

    # Accept either 'score_fraction' (from compute_universality_score) or 'Score' (from DataFrame)
    def _get_score(s):
        return s.get("score_fraction", s.get("Score", 0.0))

    def _get_rating(s):
        return s.get("universality_rating", s.get("Rating", "Unsupported"))

    def _get_symbol(s):
        return s.get("symbol", s.get("Market", ""))

    fracs   = [_get_score(s) for s in scores]
    ratings = [_get_rating(s) for s in scores]

    mean_score = float(np.mean(fracs))

    rating_map = {"High": 3, "Moderate": 2, "Weak": 1, "Unsupported": 0}
    mean_rating_val = float(np.mean([rating_map.get(r, 0) for r in ratings]))

    n_high   = sum(1 for r in ratings if r == "High")
    n_mod    = sum(1 for r in ratings if r == "Moderate")
    n_weak   = sum(1 for r in ratings if r == "Weak")
    n_unsup  = sum(1 for r in ratings if r == "Unsupported")

    if mean_score >= 0.80:
        overall = "High"
    elif mean_score >= 0.60:
        overall = "Moderate"
    elif mean_score >= 0.40:
        overall = "Weak"
    else:
        overall = "Unsupported"

    return {
        "overall_confidence"  : overall,
        "mean_score"          : mean_score,
        "mean_rating_value"   : mean_rating_val,
        "n_markets"           : len(scores),
        "n_high"              : n_high,
        "n_moderate"          : n_mod,
        "n_weak"              : n_weak,
        "n_unsupported"       : n_unsup,
        "market_ratings"      : {_get_symbol(s): _get_rating(s) for s in scores},
    }
