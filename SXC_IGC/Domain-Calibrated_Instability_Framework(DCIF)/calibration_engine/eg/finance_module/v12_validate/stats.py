"""
stats.py — Statistical validation of V12 against independent market labels.

All functions accept a merged DataFrame that has both V12 columns
(T_sys, phase) and independent label columns.

Tests performed
---------------
1. Contemporaneous: Mann-Whitney U, effect size (rank-biserial r),
   and conditional distributions of each label by phase.
2. Predictive: Spearman ρ between T_sys(t) and label(t+k) for
   k in {1,3,6,12} bars (5,15,30,60 min).
3. Lead/lag cross-correlation of T_sys vs realized_vol.
4. Permutation test: shuffle phase labels, recompute effect size,
   derive empirical p-value.
5. Stability: repeat Mann-Whitney per year and per session.
"""

import numpy as np
import pandas as pd
from scipy import stats as sp_stats
from scipy.stats import mannwhitneyu, spearmanr
from typing import Dict, List, Tuple


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _rank_biserial_r(u_stat: float, n1: int, n2: int) -> float:
    """Effect size for Mann-Whitney U."""
    return (2 * u_stat) / (n1 * n2) - 1.0


def _cohens_d(a: np.ndarray, b: np.ndarray) -> float:
    na, nb = len(a), len(b)
    if na < 2 or nb < 2:
        return np.nan
    pooled_std = np.sqrt(((na - 1) * a.std(ddof=1)**2 + (nb - 1) * b.std(ddof=1)**2) / (na + nb - 2))
    return (a.mean() - b.mean()) / (pooled_std + 1e-12)


# ---------------------------------------------------------------------------
# 1. Contemporaneous comparison: FIREWALL vs NOMINAL
# ---------------------------------------------------------------------------

def compare_phases(merged: pd.DataFrame, label_cols: List[str]) -> pd.DataFrame:
    """
    For each label column compute descriptive statistics and Mann-Whitney U
    comparing FIREWALL vs NOMINAL periods.

    Returns a DataFrame with one row per label.
    """
    fw = merged[merged['phase'] == 'FIREWALL']
    nm = merged[merged['phase'] == 'NOMINAL']

    rows = []
    for col in label_cols:
        a = fw[col].dropna().values
        b = nm[col].dropna().values
        if len(a) < 10 or len(b) < 10:
            continue
        try:
            u, p = mannwhitneyu(a, b, alternative='two-sided')
        except Exception:
            u, p = np.nan, np.nan
        r    = _rank_biserial_r(u, len(a), len(b)) if not np.isnan(u) else np.nan
        d    = _cohens_d(a, b)
        rows.append({
            'label'           : col,
            'FIREWALL_mean'   : a.mean(),
            'FIREWALL_median' : np.median(a),
            'NOMINAL_mean'    : b.mean(),
            'NOMINAL_median'  : np.median(b),
            'MW_U'            : u,
            'p_value'         : p,
            'rank_biserial_r' : r,
            'cohens_d'        : d,
            'n_firewall'      : len(a),
            'n_nominal'       : len(b),
            'significant'     : p < 0.05 if not np.isnan(p) else False,
        })
    return pd.DataFrame(rows)


# ---------------------------------------------------------------------------
# 2. Predictive: Spearman ρ at forward horizons
# ---------------------------------------------------------------------------

def predictive_correlation(merged: pd.DataFrame,
                            label_cols: List[str],
                            horizons: List[int] = (1, 3, 6, 12)) -> pd.DataFrame:
    """
    Compute Spearman ρ between T_sys(t) and label(t + k) for each horizon k.

    Returns wide DataFrame: rows = labels, columns = horizon k values.
    """
    T = merged['T_sys']
    rows = []
    for col in label_cols:
        row = {'label': col}
        for k in horizons:
            future = merged[col].shift(-k)
            mask   = T.notna() & future.notna()
            if mask.sum() < 30:
                row[f'rho_k{k}'] = np.nan
                row[f'p_k{k}']   = np.nan
                continue
            rho, p = spearmanr(T[mask], future[mask])
            row[f'rho_k{k}'] = rho
            row[f'p_k{k}']   = p
        rows.append(row)
    return pd.DataFrame(rows)


# ---------------------------------------------------------------------------
# 3. Lead/lag cross-correlation
# ---------------------------------------------------------------------------

def lead_lag_correlation(merged: pd.DataFrame,
                         target_col: str = 'realized_vol',
                         max_lag: int = 24) -> pd.Series:
    """
    Cross-correlation between T_sys and target_col at lags -max_lag … +max_lag.
    Positive lag means T_sys leads target.
    """
    T   = merged['T_sys'].dropna()
    lab = merged[target_col].dropna()
    common = T.index.intersection(lab.index)
    T_arr   = T.loc[common].values.astype(float)
    lab_arr = lab.loc[common].values.astype(float)

    # standardise
    T_std   = (T_arr   - T_arr.mean())   / (T_arr.std()   + 1e-12)
    lab_std = (lab_arr - lab_arr.mean()) / (lab_arr.std() + 1e-12)

    n    = len(T_std)
    lags = range(-max_lag, max_lag + 1)
    xcorr = []
    for lag in lags:
        if lag >= 0:
            a, b = T_std[:n - lag], lab_std[lag:]
        else:
            a, b = T_std[-lag:], lab_std[:n + lag]
        xcorr.append(np.dot(a, b) / (len(a) + 1e-12))

    return pd.Series(xcorr, index=list(lags), name=f'xcorr_T_vs_{target_col}')


# ---------------------------------------------------------------------------
# 4. Permutation test
# ---------------------------------------------------------------------------

def permutation_test(merged: pd.DataFrame,
                     label_col: str,
                     n_permutations: int = 1000,
                     seed: int = 42) -> dict:
    """
    Permutation test: shuffle phase labels and recompute rank-biserial r.
    Returns empirical p-value.
    """
    rng = np.random.default_rng(seed)
    phases = merged['phase'].values.copy()
    vals   = merged[label_col].values

    fw_mask = phases == 'FIREWALL'
    nm_mask = phases == 'NOMINAL'
    a_obs   = vals[fw_mask & ~np.isnan(vals)]
    b_obs   = vals[nm_mask & ~np.isnan(vals)]
    if len(a_obs) < 10 or len(b_obs) < 10:
        return {'observed_r': np.nan, 'p_permutation': np.nan}

    u_obs, _ = mannwhitneyu(a_obs, b_obs, alternative='two-sided')
    r_obs    = _rank_biserial_r(u_obs, len(a_obs), len(b_obs))

    null_r = []
    for _ in range(n_permutations):
        perm  = rng.permutation(phases)
        a_p   = vals[(perm == 'FIREWALL') & ~np.isnan(vals)]
        b_p   = vals[(perm == 'NOMINAL')  & ~np.isnan(vals)]
        if len(a_p) < 5 or len(b_p) < 5:
            continue
        try:
            u_p, _ = mannwhitneyu(a_p, b_p, alternative='two-sided')
            null_r.append(abs(_rank_biserial_r(u_p, len(a_p), len(b_p))))
        except Exception:
            pass

    null_r  = np.array(null_r)
    p_perm  = (null_r >= abs(r_obs)).mean() if len(null_r) > 0 else np.nan
    return {
        'label'        : label_col,
        'observed_r'   : r_obs,
        'null_r_mean'  : null_r.mean() if len(null_r) else np.nan,
        'null_r_p95'   : np.percentile(null_r, 95) if len(null_r) else np.nan,
        'p_permutation': p_perm,
        'n_permutations': len(null_r),
    }


# ---------------------------------------------------------------------------
# 5. Stability across years and sessions
# ---------------------------------------------------------------------------

def stability_by_year(merged: pd.DataFrame, label_cols: List[str]) -> pd.DataFrame:
    merged = merged.copy()
    merged['year'] = merged.index.year
    rows = []
    for yr in sorted(merged['year'].unique()):
        sub = merged[merged['year'] == yr]
        for col in label_cols:
            fw = sub[sub['phase'] == 'FIREWALL'][col].dropna().values
            nm = sub[sub['phase'] == 'NOMINAL'][col].dropna().values
            if len(fw) < 5 or len(nm) < 5:
                continue
            try:
                u, p = mannwhitneyu(fw, nm, alternative='two-sided')
                r    = _rank_biserial_r(u, len(fw), len(nm))
            except Exception:
                r, p = np.nan, np.nan
            rows.append({'year': yr, 'label': col,
                         'rank_biserial_r': r, 'p_value': p,
                         'n_fw': len(fw), 'n_nm': len(nm)})
    return pd.DataFrame(rows)


def stability_by_session(merged: pd.DataFrame, label_cols: List[str]) -> pd.DataFrame:
    if 'session' not in merged.columns:
        return pd.DataFrame()
    rows = []
    for sess in merged['session'].dropna().unique():
        sub = merged[merged['session'] == sess]
        for col in label_cols:
            fw = sub[sub['phase'] == 'FIREWALL'][col].dropna().values
            nm = sub[sub['phase'] == 'NOMINAL'][col].dropna().values
            if len(fw) < 5 or len(nm) < 5:
                continue
            try:
                u, p = mannwhitneyu(fw, nm, alternative='two-sided')
                r    = _rank_biserial_r(u, len(fw), len(nm))
            except Exception:
                r, p = np.nan, np.nan
            rows.append({'session': sess, 'label': col,
                         'rank_biserial_r': r, 'p_value': p,
                         'n_fw': len(fw), 'n_nm': len(nm)})
    return pd.DataFrame(rows)


# ---------------------------------------------------------------------------
# 6. Forward regime window analysis (predictive validation)
# ---------------------------------------------------------------------------

def forward_window_analysis(v12: pd.DataFrame,
                             labels_df: pd.DataFrame,
                             transitions: pd.DataFrame,
                             horizons_bars: List[int] = (1, 3, 6, 12),
                             entry_phase: str = 'FIREWALL') -> pd.DataFrame:
    """
    For every transition into entry_phase, measure mean label values
    in the window [0, k] bars after the transition.
    Compare against baseline (same labels in NOMINAL periods).
    """
    merged = v12.join(labels_df, how='inner')
    nm_means = merged[merged['phase'] == 'NOMINAL'][
        ['realized_vol', 'atr', 'spread_abs', 'adx', 'abs_return']
    ].mean()

    entries = transitions[transitions['phase'] == entry_phase]['timestamp_in']
    idx     = v12.index
    idx_set = set(idx)

    rows = []
    for ts in entries:
        if ts not in idx_set:
            continue
        pos = idx.get_loc(ts)
        for k in horizons_bars:
            end = min(pos + k, len(idx) - 1)
            window = merged.iloc[pos:end + 1]
            if len(window) == 0:
                continue
            row = {
                'entry_ts'        : ts,
                'horizon_bars'    : k,
                'horizon_min'     : k * 5,
                'mean_rv'         : window['realized_vol'].mean(),
                'mean_atr'        : window['atr'].mean(),
                'mean_spread'     : window['spread_abs'].mean(),
                'mean_adx'        : window['adx'].mean(),
                'mean_abs_return' : window['abs_return'].mean(),
            }
            rows.append(row)

    if not rows:
        return pd.DataFrame()

    df = pd.DataFrame(rows)
    # add baseline ratios
    for col, nm_col in [('mean_rv', 'realized_vol'), ('mean_atr', 'atr'),
                        ('mean_spread', 'spread_abs'), ('mean_adx', 'adx'),
                        ('mean_abs_return', 'abs_return')]:
        base = nm_means.get(nm_col, np.nan)
        df[f'{col}_vs_nominal'] = df[col] / (base + 1e-12)
    return df
