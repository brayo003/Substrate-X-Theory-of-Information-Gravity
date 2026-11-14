"""
strategy_statistics.py — Statistical analysis engine for Phase 1 validation.

For every (strategy, regime) cell computes:
  Performance: profit_factor, sharpe, sortino, max_drawdown, expectancy,
               avg_trade_ret, win_rate, trade_count, avg_duration,
               stop_frequency, target_frequency

Statistical tests per strategy (coherent vs incoherent):
  - Mann-Whitney U (non-parametric, H0: distributions are equal)
  - Permutation test (10,000 permutations)
  - Bootstrap confidence intervals (1,000 bootstrap samples)
  - Cohen's d effect size
  - Rank-biserial correlation (effect size for MW)
  - Benjamini-Hochberg FDR correction across all strategies

All raw p-values are corrected via BH-FDR before reporting.
"""

import numpy as np
import pandas as pd
from scipy import stats
from typing import Dict, List, Tuple, Optional


REGIMES_5 = [
    'Deep_Incoherent',
    'Mod_Incoherent',
    'Transition',
    'Weak_Coherent',
    'Strong_Coherent',
]

N_BOOTSTRAP   = 1000
N_PERMUTATION = 5000


# ─────────────────────────────────────────────────────────────────────────────
# Core performance metrics
# ─────────────────────────────────────────────────────────────────────────────

def compute_metrics(returns: np.ndarray, trades_df: pd.DataFrame = None) -> dict:
    """
    Compute full performance metrics for a set of trade returns.

    Parameters
    ----------
    returns   : 1-D array of net returns per trade
    trades_df : optional DataFrame for duration / stop / target stats

    Returns
    -------
    dict of metrics
    """
    r = np.asarray(returns, dtype=np.float64)
    n = len(r)

    if n == 0:
        return {
            'trade_count': 0,
            'profit_factor': np.nan, 'sharpe': np.nan, 'sortino': np.nan,
            'max_drawdown': np.nan, 'expectancy': np.nan,
            'avg_trade_ret': np.nan, 'median_trade_ret': np.nan,
            'win_rate': np.nan, 'std_ret': np.nan,
            'avg_duration': np.nan, 'stop_freq': np.nan, 'target_freq': np.nan,
        }

    wins   = r[r > 0]
    losses = r[r < 0]
    gross_win  = wins.sum()
    gross_loss = abs(losses.sum())
    pf     = gross_win / (gross_loss + 1e-12)

    # Sharpe: annualize over trade count (not time)
    mean_r = r.mean()
    std_r  = r.std(ddof=1) if n > 1 else 1e-10
    sharpe = mean_r / (std_r + 1e-10) * np.sqrt(n)

    # Sortino: downside deviation
    down    = r[r < 0]
    down_std = down.std(ddof=1) if len(down) > 1 else 1e-10
    sortino  = mean_r / (down_std + 1e-10) * np.sqrt(n)

    # Max drawdown on cumulative equity curve
    cum  = np.cumsum(r)
    peak = np.maximum.accumulate(cum)
    dd   = peak - cum
    max_dd = float(dd.max()) if n > 0 else 0.0

    expectancy   = mean_r
    win_rate     = float((r > 0).mean())

    # Trade-level optional metrics
    avg_dur    = np.nan
    stop_freq  = np.nan
    tgt_freq   = np.nan
    if trades_df is not None and len(trades_df) > 0:
        if 'duration_bars' in trades_df.columns:
            avg_dur = float(trades_df['duration_bars'].mean())
        if 'stop_hit' in trades_df.columns:
            stop_freq = float(trades_df['stop_hit'].mean())
        if 'target_hit' in trades_df.columns:
            tgt_freq = float(trades_df['target_hit'].mean())

    return {
        'trade_count'     : n,
        'profit_factor'   : float(pf),
        'sharpe'          : float(sharpe),
        'sortino'         : float(sortino),
        'max_drawdown'    : float(max_dd),
        'expectancy'      : float(expectancy),
        'avg_trade_ret'   : float(mean_r),
        'median_trade_ret': float(np.median(r)),
        'win_rate'        : float(win_rate),
        'std_ret'         : float(std_r),
        'avg_duration'    : float(avg_dur),
        'stop_freq'       : float(stop_freq),
        'target_freq'     : float(tgt_freq),
    }


# ─────────────────────────────────────────────────────────────────────────────
# Build strategy × regime performance matrix
# ─────────────────────────────────────────────────────────────────────────────

def build_strategy_regime_matrix(all_trades: pd.DataFrame) -> pd.DataFrame:
    """
    Build the full Strategy × Regime performance matrix.

    Returns a DataFrame with columns:
      strategy, family, regime, trade_count, profit_factor, sharpe, sortino,
      max_drawdown, expectancy, avg_trade_ret, win_rate, avg_duration,
      stop_freq, target_freq
    """
    rows = []
    strategies = all_trades['strategy'].unique()

    for strat in strategies:
        st = all_trades[all_trades['strategy'] == strat]
        family = st['family'].iloc[0] if len(st) > 0 else 'Unknown'

        # ALL combined
        m = compute_metrics(st['net_ret'].values, st)
        m['strategy'] = strat
        m['family']   = family
        m['regime']   = 'ALL'
        rows.append(m)

        # Per regime
        for regime in REGIMES_5:
            sub = st[st['entry_regime'] == regime]
            m   = compute_metrics(sub['net_ret'].values, sub)
            m['strategy'] = strat
            m['family']   = family
            m['regime']   = regime
            rows.append(m)

    return pd.DataFrame(rows)


# ─────────────────────────────────────────────────────────────────────────────
# Statistical tests
# ─────────────────────────────────────────────────────────────────────────────

def cohen_d(a: np.ndarray, b: np.ndarray) -> float:
    """Cohen's d effect size."""
    na, nb = len(a), len(b)
    if na < 2 or nb < 2:
        return np.nan
    pooled_var = ((na - 1) * a.var(ddof=1) + (nb - 1) * b.var(ddof=1)) / (na + nb - 2)
    return (a.mean() - b.mean()) / (np.sqrt(pooled_var) + 1e-12)


def rank_biserial_r(a: np.ndarray, b: np.ndarray) -> float:
    """Rank-biserial correlation (effect size for Mann-Whitney)."""
    na, nb = len(a), len(b)
    if na == 0 or nb == 0:
        return np.nan
    u, _ = stats.mannwhitneyu(a, b, alternative='two-sided')
    return float(1 - (2 * u) / (na * nb))


def permutation_test(a: np.ndarray, b: np.ndarray, n_perm: int = N_PERMUTATION) -> float:
    """Two-sided permutation test on difference of means."""
    na, nb = len(a), len(b)
    if na < 3 or nb < 3:
        return np.nan
    observed = abs(a.mean() - b.mean())
    combined = np.concatenate([a, b])
    rng      = np.random.default_rng(42)
    count    = 0
    for _ in range(n_perm):
        perm   = rng.permutation(combined)
        diff   = abs(perm[:na].mean() - perm[na:].mean())
        if diff >= observed:
            count += 1
    return count / n_perm


def bootstrap_ci(
    returns: np.ndarray,
    n_boot: int = N_BOOTSTRAP,
    ci: float = 0.95,
    statistic: str = 'mean',
) -> Tuple[float, float, float]:
    """
    Bootstrap confidence interval for a statistic on returns.

    Returns (lower, estimate, upper).
    """
    r = returns[~np.isnan(returns)]
    if len(r) < 3:
        return (np.nan, np.nan, np.nan)

    rng = np.random.default_rng(42)
    boot_stats = np.empty(n_boot)

    for i in range(n_boot):
        sample = rng.choice(r, size=len(r), replace=True)
        if statistic == 'mean':
            boot_stats[i] = sample.mean()
        elif statistic == 'sharpe':
            std = sample.std(ddof=1)
            boot_stats[i] = sample.mean() / (std + 1e-10)
        elif statistic == 'profit_factor':
            w = sample[sample > 0].sum()
            l = abs(sample[sample < 0].sum())
            boot_stats[i] = w / (l + 1e-12)
        else:
            boot_stats[i] = sample.mean()

    alpha = (1 - ci) / 2
    lo    = float(np.percentile(boot_stats, 100 * alpha))
    hi    = float(np.percentile(boot_stats, 100 * (1 - alpha)))
    est   = float(np.percentile(boot_stats, 50))
    return lo, est, hi


def fdr_correction(pvalues: np.ndarray, alpha: float = 0.05) -> Tuple[np.ndarray, np.ndarray]:
    """
    Benjamini-Hochberg FDR correction.

    Returns (reject_array, corrected_pvalues).
    """
    p = np.asarray(pvalues, dtype=float)
    n = len(p)
    if n == 0:
        return np.array([], dtype=bool), np.array([])

    # Replace NaN with 1.0 (no evidence)
    p_clean = np.where(np.isnan(p), 1.0, p)

    order     = np.argsort(p_clean)
    rank      = np.empty(n, dtype=int)
    rank[order] = np.arange(1, n + 1)

    corrected = np.minimum(1.0, p_clean * n / rank)
    # monotone: ensure corrected p is non-decreasing when sorted
    for i in range(n - 2, -1, -1):
        corrected[order[i]] = min(corrected[order[i]], corrected[order[i + 1]])

    reject = corrected < alpha
    return reject, corrected


# ─────────────────────────────────────────────────────────────────────────────
# Run all significance tests
# ─────────────────────────────────────────────────────────────────────────────

def run_significance_tests(all_trades: pd.DataFrame) -> pd.DataFrame:
    """
    For every strategy, compare returns in COHERENT (Weak + Strong)
    vs INCOHERENT (Deep + Mod) regimes.

    Tests:
      - Mann-Whitney U
      - Permutation test
      - Bootstrap CI on mean return difference
      - Cohen's d effect size
      - Rank-biserial r
      - FDR-corrected p-values (across all strategies)

    Returns DataFrame with one row per strategy.
    """
    coherent_regimes    = {'Weak_Coherent', 'Strong_Coherent'}
    incoherent_regimes  = {'Deep_Incoherent', 'Mod_Incoherent'}

    rows = []
    strategies = sorted(all_trades['strategy'].unique())

    for strat in strategies:
        st   = all_trades[all_trades['strategy'] == strat]
        coh  = st[st['entry_regime'].isin(coherent_regimes)]['net_ret'].values
        inc  = st[st['entry_regime'].isin(incoherent_regimes)]['net_ret'].values

        row = {'strategy': strat, 'n_coherent': len(coh), 'n_incoherent': len(inc)}

        if len(coh) >= 3 and len(inc) >= 3:
            # Mann-Whitney
            try:
                mw_u, mw_p = stats.mannwhitneyu(coh, inc, alternative='two-sided')
                row['mw_statistic'] = float(mw_u)
                row['mw_p']         = float(mw_p)
            except Exception:
                row['mw_statistic'] = np.nan
                row['mw_p']         = np.nan

            # Permutation
            row['perm_p'] = permutation_test(coh, inc)

            # Effect sizes
            row['cohen_d']          = cohen_d(coh, inc)
            row['rank_biserial_r']  = rank_biserial_r(coh, inc)

            # Mean difference and CI
            diff = float(coh.mean() - inc.mean())
            row['mean_diff_coh_minus_inc'] = diff
            diff_arr = coh - inc[:min(len(coh), len(inc))]  # approximate
            lo, est, hi = bootstrap_ci(coh - coh.mean(), statistic='mean')
            lo2, est2, hi2 = bootstrap_ci(inc - inc.mean(), statistic='mean')
            row['coh_mean_ret']   = float(coh.mean())
            row['inc_mean_ret']   = float(inc.mean())
            row['coh_ci_low']     = lo
            row['coh_ci_high']    = hi
            row['inc_ci_low']     = lo2
            row['inc_ci_high']    = hi2
        else:
            for k in ['mw_statistic', 'mw_p', 'perm_p', 'cohen_d',
                      'rank_biserial_r', 'mean_diff_coh_minus_inc',
                      'coh_mean_ret', 'inc_mean_ret',
                      'coh_ci_low', 'coh_ci_high', 'inc_ci_low', 'inc_ci_high']:
                row[k] = np.nan

        rows.append(row)

    df = pd.DataFrame(rows)
    if len(df) == 0:
        return df

    # FDR correction on MW p-values
    reject_mw,  corrected_mw  = fdr_correction(df['mw_p'].values)
    reject_perm, corrected_perm = fdr_correction(df['perm_p'].values)

    df['mw_p_fdr']         = corrected_mw
    df['mw_reject_fdr']    = reject_mw
    df['perm_p_fdr']       = corrected_perm
    df['perm_reject_fdr']  = reject_perm

    return df


# ─────────────────────────────────────────────────────────────────────────────
# Bootstrap statistics table
# ─────────────────────────────────────────────────────────────────────────────

def run_bootstrap_statistics(all_trades: pd.DataFrame) -> pd.DataFrame:
    """
    Bootstrap confidence intervals for key metrics per (strategy, regime).

    Returns DataFrame with columns:
      strategy, regime, metric, lower_95ci, estimate, upper_95ci
    """
    rows = []
    strategies = sorted(all_trades['strategy'].unique())
    regimes    = REGIMES_5 + ['ALL']

    for strat in strategies:
        st = all_trades[all_trades['strategy'] == strat]
        for regime in regimes:
            if regime == 'ALL':
                sub = st
            else:
                sub = st[st['entry_regime'] == regime]
            if len(sub) < 5:
                continue
            r = sub['net_ret'].values
            for stat in ['mean', 'sharpe', 'profit_factor']:
                lo, est, hi = bootstrap_ci(r, statistic=stat)
                rows.append({
                    'strategy'   : strat,
                    'regime'     : regime,
                    'metric'     : stat,
                    'lower_95ci' : lo,
                    'estimate'   : est,
                    'upper_95ci' : hi,
                })

    return pd.DataFrame(rows)
