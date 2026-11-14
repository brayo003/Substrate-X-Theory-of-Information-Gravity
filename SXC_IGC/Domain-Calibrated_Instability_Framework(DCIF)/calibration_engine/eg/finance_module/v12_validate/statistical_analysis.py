"""
statistical_analysis.py — All 7 statistical questions + diagnostics.
"""
import numpy as np
import pandas as pd
from scipy.stats import spearmanr, pearsonr, mannwhitneyu
from typing import Dict, List, Tuple


# ── helpers ───────────────────────────────────────────────────────────────────

def _rank_biserial(u, n1, n2):
    return 2.0 * u / (n1 * n2) - 1.0

def _cohens_d(a, b):
    na, nb = len(a), len(b)
    if na < 2 or nb < 2:
        return np.nan
    pooled = np.sqrt(((na-1)*a.std(ddof=1)**2 + (nb-1)*b.std(ddof=1)**2)/(na+nb-2))
    return (a.mean() - b.mean()) / (pooled + 1e-12)

def _bootstrap_mean_diff(a, b, n_boot=1000, seed=42):
    rng = np.random.default_rng(seed)
    obs = a.mean() - b.mean()
    combined = np.concatenate([a, b])
    na = len(a)
    diffs = np.array([rng.permutation(combined)[:na].mean() -
                      rng.permutation(combined)[na:].mean()
                      for _ in range(n_boot)])
    return float(obs), float((diffs >= obs).mean())

def _mi_binned(x, y, bins=20):
    mask = np.isfinite(x) & np.isfinite(y)
    x, y = x[mask], y[mask]
    if len(x) < 30:
        return np.nan
    h, _, _ = np.histogram2d(x, y, bins=bins)
    pxy = h / h.sum()
    px = pxy.sum(axis=1, keepdims=True)
    py = pxy.sum(axis=0, keepdims=True)
    with np.errstate(divide='ignore', invalid='ignore'):
        mi = np.where(pxy > 0, pxy * np.log(pxy / (px * py + 1e-12)), 0.0).sum()
    return float(mi)

def _entropy_binned(x, bins=20):
    counts, _ = np.histogram(x[np.isfinite(x)], bins=bins)
    p = counts / (counts.sum() + 1e-12)
    p = p[p > 0]
    return float(-np.sum(p * np.log(p)))


# ── Q1: profitability by Q bin ─────────────────────────────────────────────

def q1_profitability_by_Q(trade_log: pd.DataFrame, n_bins: int = 3) -> pd.DataFrame:
    if len(trade_log) == 0:
        return pd.DataFrame()
    df = trade_log[['entry_Q', 'net_return']].dropna()
    if len(df) < n_bins * 5:
        return pd.DataFrame()
    try:
        labels = [f'Q_bin_{i+1}' for i in range(n_bins)]
        df = df.copy()
        df['qbin'] = pd.qcut(df['entry_Q'], q=n_bins, labels=labels, duplicates='drop')
    except Exception:
        return pd.DataFrame()
    rows = []
    for lbl in labels:
        sub = df[df['qbin'] == lbl]
        r = sub['net_return'].values
        if len(r) < 5:
            continue
        wins = r[r > 0]; losses = r[r < 0]
        pf = wins.sum() / (abs(losses.sum()) + 1e-12)
        sh = r.mean() / (r.std() + 1e-12) * np.sqrt(len(r))
        rows.append({'Q_bin': lbl,
                     'Q_min': sub['entry_Q'].min(), 'Q_max': sub['entry_Q'].max(),
                     'Q_median': sub['entry_Q'].median(), 'n_trades': len(r),
                     'avg_return': float(r.mean()), 'median_return': float(np.median(r)),
                     'profit_factor': float(pf), 'sharpe': float(sh),
                     'win_rate': float((r > 0).mean())})
    return pd.DataFrame(rows)


# ── Q2: noise analysis ─────────────────────────────────────────────────────

def q2_noise_analysis(df: pd.DataFrame, trade_log: pd.DataFrame) -> dict:
    out = {}
    for reg in ['COHERENT', 'INCOHERENT']:
        mask = df['tr_regime_str'] == reg
        sub  = df.loc[mask, 'ret_1b'].dropna().values
        if len(sub) > 10:
            out[f'{reg}_return_variance'] = float(np.var(sub))
            out[f'{reg}_return_mean']     = float(np.mean(sub))
            out[f'{reg}_n_bars']          = int(len(sub))
    if len(trade_log) > 0 and 'entry_regime' in trade_log.columns:
        tl = trade_log.copy()
        tl['false_break'] = (tl['net_return'] < 0) & (tl['duration_bars'] <= 5)
        for reg in ['COHERENT', 'INCOHERENT']:
            sub = tl[tl['entry_regime'] == reg]
            if len(sub) > 5:
                out[f'{reg}_false_breakout_rate'] = float(sub['false_break'].mean())
    Q = df['tr_Q'].values
    ret5 = df['ret_5b'].values if 'ret_5b' in df.columns else np.full(len(df), np.nan)
    ret1 = df['ret_1b'].values
    same = (np.sign(ret1) == np.sign(ret5)).astype(float)
    valid = np.isfinite(Q) & np.isfinite(same)
    if valid.sum() > 50:
        rho, p = spearmanr(Q[valid], same[valid])
        out['trend_persist_Q_spearman_rho'] = float(rho)
        out['trend_persist_Q_spearman_p']   = float(p)
    return out


# ── Q3: duration vs Q ──────────────────────────────────────────────────────

def q3_duration_vs_Q(trade_log: pd.DataFrame) -> dict:
    if len(trade_log) < 20:
        return {}
    df = trade_log[['entry_Q', 'duration_bars', 'entry_regime']].dropna()
    if len(df) < 20:
        return {}
    rho_s, p_s = spearmanr(df['entry_Q'], df['duration_bars'])
    rho_p, p_p = pearsonr(df['entry_Q'], df['duration_bars'])
    n  = len(df)
    se = 1.0 / np.sqrt(n - 3 + 1e-12)
    z  = np.arctanh(rho_s)
    ci = (float(np.tanh(z - 1.96 * se)), float(np.tanh(z + 1.96 * se)))
    coh   = df.loc[df['entry_regime'] == 'COHERENT', 'duration_bars'].mean()
    incoh = df.loc[df['entry_regime'] == 'INCOHERENT', 'duration_bars'].mean()
    return {'spearman_rho': float(rho_s), 'spearman_p': float(p_s),
            'pearson_r': float(rho_p), 'pearson_p': float(p_p),
            'n_trades': n, 'ci_95_low': ci[0], 'ci_95_high': ci[1],
            'mean_dur_coherent': float(coh) if not np.isnan(coh) else np.nan,
            'mean_dur_incoherent': float(incoh) if not np.isnan(incoh) else np.nan}


# ── Q4: stop-loss probability vs Q ────────────────────────────────────────

def q4_stoploss_vs_Q(trade_log: pd.DataFrame, n_bins: int = 5) -> pd.DataFrame:
    if len(trade_log) == 0:
        return pd.DataFrame()
    df = trade_log[['entry_Q', 'stop_hit']].dropna().copy()
    if len(df) < n_bins * 5:
        return pd.DataFrame()
    try:
        df['qbin'] = pd.qcut(df['entry_Q'], q=n_bins, duplicates='drop')
    except Exception:
        return pd.DataFrame()
    rows = []
    for qbin, sub in df.groupby('qbin', observed=True):
        rows.append({'Q_bin': str(qbin), 'Q_midpoint': float(qbin.mid),
                     'n_trades': len(sub), 'P_stop': float(sub['stop_hit'].mean()),
                     'stop_count': int(sub['stop_hit'].sum())})
    return pd.DataFrame(rows)


# ── Q5: volatility expansion vs Q ─────────────────────────────────────────

def q5_volatility_vs_Q(df: pd.DataFrame, horizons=(5, 10, 20, 50)) -> pd.DataFrame:
    Q = df['tr_Q'].values
    log_ret = np.log(df['close'] / df['close'].shift(1))
    rows = []
    for h in horizons:
        fwd_vol = log_ret.rolling(h).std().shift(-h).values
        valid = np.isfinite(Q) & np.isfinite(fwd_vol)
        if valid.sum() < 50:
            continue
        rho_s, p_s = spearmanr(Q[valid], fwd_vol[valid])
        rho_p, p_p = pearsonr(Q[valid], fwd_vol[valid])
        mi = _mi_binned(Q[valid], fwd_vol[valid])
        rows.append({'horizon_bars': h, 'horizon_min': h*5,
                     'spearman_rho': float(rho_s), 'spearman_p': float(p_s),
                     'pearson_r': float(rho_p), 'pearson_p': float(p_p),
                     'mutual_info': float(mi), 'n_obs': int(valid.sum())})
    return pd.DataFrame(rows)


# ── Q6: trend continuation vs Q ───────────────────────────────────────────

def q6_trend_vs_Q(df: pd.DataFrame, horizons=(10, 20, 50)) -> pd.DataFrame:
    ret1 = df['ret_1b'].values
    direction = np.sign(ret1)
    rows = []
    for h in horizons:
        col = f'ret_{h}b'
        if col not in df.columns:
            continue
        fwd  = df[col].values
        same = (np.sign(fwd) == direction).astype(float)
        same[direction == 0] = np.nan
        df_t = pd.DataFrame({'Q': df['tr_Q'].values,
                             'same_dir': same,
                             'regime': df['tr_regime_str'].values}).dropna()
        if len(df_t) < 50:
            continue
        for reg in ['COHERENT', 'INCOHERENT', 'ALL']:
            sub = df_t if reg == 'ALL' else df_t[df_t['regime'] == reg]
            if len(sub) < 30:
                continue
            rho, p = spearmanr(sub['Q'], sub['same_dir'])
            rows.append({'horizon_bars': h, 'horizon_min': h*5, 'regime': reg,
                         'trend_persist_prob': float(sub['same_dir'].mean()),
                         'Q_spearman_rho': float(rho), 'Q_spearman_p': float(p),
                         'n_obs': len(sub)})
    return pd.DataFrame(rows)


# ── Q7: signal improvement ────────────────────────────────────────────────

def q7_signal_improvement(df: pd.DataFrame, n_boot=500, horizon=10) -> pd.DataFrame:
    sig_cols = [c for c in df.columns if c.startswith('sig_')]
    ret_col  = f'ret_{horizon}b'
    if ret_col not in df.columns or len(sig_cols) == 0:
        return pd.DataFrame()
    Q   = df['tr_Q'].values
    ret = df[ret_col].values
    rows = []
    for sc in sig_cols:
        sig   = df[sc].values
        valid = np.isfinite(sig) & np.isfinite(ret) & np.isfinite(Q)
        if valid.sum() < 100:
            continue
        s_v, r_v, Q_v = sig[valid], ret[valid], Q[valid]
        pred  = np.where(s_v > np.median(s_v), 1, -1)
        succ  = (np.sign(r_v) == pred).astype(float)
        qmask = Q_v > 0
        if qmask.sum() < 30:
            continue
        base_rate = float(succ.mean())
        q_rate    = float(succ[qmask].mean())
        obs_diff  = q_rate - base_rate
        rng = np.random.default_rng(42)
        p_val = float(np.mean([
            succ[rng.choice([True, False], size=len(succ), p=[qmask.mean(), 1-qmask.mean()])].mean() - base_rate >= obs_diff
            for _ in range(n_boot)
        ]))
        rows.append({'signal': sc.replace('sig_', ''),
                     'base_success_rate': base_rate,
                     'Q_filtered_rate': q_rate,
                     'improvement': obs_diff,
                     'p_value': p_val,
                     'significant_5pct': bool(p_val < 0.05),
                     'n_base': int(valid.sum()),
                     'n_q_filtered': int(qmask.sum())})
    return pd.DataFrame(rows)


# ── Lag analysis ──────────────────────────────────────────────────────────

def lag_analysis(df: pd.DataFrame, max_lag=100) -> pd.DataFrame:
    targets = ['realized_vol_20', 'ret_1b', 'atr_14', 'vol_norm']
    Q = df['tr_Q'].values
    rows = []
    for tgt in targets:
        if tgt not in df.columns:
            continue
        y = df[tgt].values
        for lag in range(-max_lag, max_lag + 1):
            if lag < 0:
                q_s, y_s = Q[:len(Q)+lag], y[-lag:]
            elif lag > 0:
                q_s, y_s = Q[lag:], y[:len(y)-lag]
            else:
                q_s, y_s = Q, y
            valid = np.isfinite(q_s) & np.isfinite(y_s)
            if valid.sum() < 50:
                rows.append({'target': tgt, 'lag': lag, 'pearson_r': np.nan, 'n': 0})
                continue
            r, p = pearsonr(q_s[valid], y_s[valid])
            rows.append({'target': tgt, 'lag': lag,
                         'pearson_r': float(r), 'p_value': float(p),
                         'n': int(valid.sum())})
    return pd.DataFrame(rows)


# ── Cross-correlations ────────────────────────────────────────────────────

def cross_correlations(df: pd.DataFrame) -> pd.DataFrame:
    targets = ['atr_14', 'adx_14', 'rsi_14', 'macd', 'vol_norm',
               'ret_1b', 'realized_vol_20', 'drawdown_20',
               'trend_strength', 'T_sys', 'composite_norm']
    Q_idx = df['tr_Q'].dropna().index
    Q     = df['tr_Q'].loc[Q_idx].values
    rows  = []
    for col in targets:
        if col not in df.columns:
            continue
        y = df[col].reindex(Q_idx).values
        valid = np.isfinite(Q) & np.isfinite(y)
        if valid.sum() < 50:
            continue
        rp, pp = pearsonr(Q[valid], y[valid])
        rs, ps = spearmanr(Q[valid], y[valid])
        mi     = _mi_binned(Q[valid], y[valid])
        rows.append({'indicator': col,
                     'pearson_r': float(rp), 'pearson_p': float(pp),
                     'spearman_rho': float(rs), 'spearman_p': float(ps),
                     'mutual_info': float(mi), 'n_obs': int(valid.sum())})
    return pd.DataFrame(rows)


# ── Information content ───────────────────────────────────────────────────

def information_content(df: pd.DataFrame, horizon=10) -> dict:
    ret_col = f'ret_{horizon}b'
    if ret_col not in df.columns:
        return {}
    Q   = df['tr_Q'].values
    ret = df[ret_col].values
    valid = np.isfinite(Q) & np.isfinite(ret)
    if valid.sum() < 100:
        return {}
    Q_v   = Q[valid]
    ret_v = ret[valid]
    sign_ret = (ret_v > 0).astype(float)
    H_Y  = _entropy_binned(sign_ret, bins=2)
    MI   = _mi_binned(Q_v, sign_ret)
    out  = {'H_Y': float(H_Y), 'MI_Q_Y': float(MI),
            'conditional_entropy': float(max(0.0, H_Y - MI)),
            'info_gain_fraction': float(MI / (H_Y + 1e-12)),
            'horizon_bars': horizon, 'n_obs': int(valid.sum())}
    for indic in ['rsi_14', 'atr_14', 'T_sys']:
        if indic not in df.columns:
            continue
        x = df[indic].values[valid]
        out[f'MI_{indic}_Y'] = float(_mi_binned(x, sign_ret))
    return out


# ── Master runner ─────────────────────────────────────────────────────────

def run_all_analyses(df, trade_log_A, trade_log_B, verbose=True) -> dict:
    out = {}
    if verbose: print("  [Stats] Q1 …")
    out['q1_A'] = q1_profitability_by_Q(trade_log_A)
    out['q1_B'] = q1_profitability_by_Q(trade_log_B)
    if verbose: print("  [Stats] Q2 …")
    out['q2']   = q2_noise_analysis(df, trade_log_A)
    if verbose: print("  [Stats] Q3 …")
    out['q3_A'] = q3_duration_vs_Q(trade_log_A)
    out['q3_B'] = q3_duration_vs_Q(trade_log_B)
    if verbose: print("  [Stats] Q4 …")
    out['q4']   = q4_stoploss_vs_Q(trade_log_A)
    if verbose: print("  [Stats] Q5 …")
    out['q5']   = q5_volatility_vs_Q(df)
    if verbose: print("  [Stats] Q6 …")
    out['q6']   = q6_trend_vs_Q(df)
    if verbose: print("  [Stats] Q7 …")
    out['q7']   = q7_signal_improvement(df)
    if verbose: print("  [Stats] Lag analysis …")
    out['lag']  = lag_analysis(df)
    if verbose: print("  [Stats] Cross-correlations …")
    out['xcorr']= cross_correlations(df)
    if verbose: print("  [Stats] Information content …")
    out['info'] = information_content(df)
    return out
