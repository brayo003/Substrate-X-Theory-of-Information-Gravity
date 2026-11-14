"""
v2_phase3.py  —  Phase III: Regime Comparison Against Existing Methods
"""
import numpy as np
import pandas as pd
from scipy.stats import spearmanr


def _bollinger_width(close: pd.Series, window: int = 20) -> pd.Series:
    ma  = close.rolling(window).mean()
    std = close.rolling(window).std()
    return (2 * std / (ma + 1e-10))


def _historical_vol(close: pd.Series, window: int = 20) -> pd.Series:
    return np.log(close / close.shift(1)).rolling(window).std() * np.sqrt(252 * 12 * 24)


def _add_comparison_indicators(df: pd.DataFrame) -> pd.DataFrame:
    """Add Bollinger Width and Historical Volatility to df (ADX/ATR already present)."""
    df = df.copy()
    if 'boll_width' not in df.columns:
        df['boll_width'] = _bollinger_width(df['close'])
    if 'hist_vol_20' not in df.columns:
        df['hist_vol_20'] = _historical_vol(df['close'])
    return df


def _first_threshold_cross(series: pd.Series, threshold: float,
                            direction: str = 'above') -> np.ndarray:
    """
    For a rolling indicator, find the first bar where it crosses a threshold.
    Returns an integer array: 1 at the first crossing bar, 0 elsewhere.
    """
    arr = series.values
    out = np.zeros(len(arr), dtype=int)
    above = arr > threshold
    for i in range(1, len(arr)):
        if direction == 'above' and above[i] and not above[i - 1]:
            out[i] = 1
        elif direction == 'below' and not above[i] and above[i - 1]:
            out[i] = 1
    return out


def phase3_lead_lag_comparison(df: pd.DataFrame) -> dict:
    """
    For each comparison indicator, measure:
    - Average lead/lag relative to Q crossing zero
    - Detection rate (did indicator confirm within N bars?)
    - False alarm rate (indicator crossed threshold but Q did not follow?)

    Returns lead_lag_df, detection_df, summary
    """
    df = _add_comparison_indicators(df)
    n  = len(df)

    # ── Binary Q signal: Q crosses from negative to positive ──────────────
    Q    = df['tr_Q'].values
    q_up = np.zeros(n, dtype=int)   # Q<0 → Q>0
    q_dn = np.zeros(n, dtype=int)   # Q>0 → Q<0
    for i in range(1, n):
        if Q[i] > 0 and Q[i - 1] <= 0:
            q_up[i] = 1
        elif Q[i] < 0 and Q[i - 1] >= 0:
            q_dn[i] = 1

    q_up_idx = np.where(q_up)[0]
    q_dn_idx = np.where(q_dn)[0]

    # ── For each indicator define a "signal" event ─────────────────────────
    # We use percentile-based thresholds (75th pct = high regime)
    indicators = {}
    if 'adx_14' in df.columns:
        thr = np.nanpercentile(df['adx_14'].dropna().values, 75)
        indicators['ADX_14'] = (_first_threshold_cross(df['adx_14'], thr, 'above'),
                                 thr, 'ADX>75pct')
    if 'atr_14' in df.columns:
        thr = np.nanpercentile(df['atr_14'].dropna().values, 75)
        indicators['ATR_14'] = (_first_threshold_cross(df['atr_14'], thr, 'above'),
                                 thr, 'ATR>75pct')
    if 'hist_vol_20' in df.columns:
        thr = np.nanpercentile(df['hist_vol_20'].dropna().values, 75)
        indicators['HistVol_20'] = (_first_threshold_cross(df['hist_vol_20'], thr, 'above'),
                                     thr, 'HV>75pct')
    if 'boll_width' in df.columns:
        thr = np.nanpercentile(df['boll_width'].dropna().values, 75)
        indicators['BollWidth_20'] = (_first_threshold_cross(df['boll_width'], thr, 'above'),
                                       thr, 'BW>75pct')
    if 'realized_vol_20' in df.columns:
        thr = np.nanpercentile(df['realized_vol_20'].dropna().values, 75)
        indicators['RealizedVol_20'] = (_first_threshold_cross(df['realized_vol_20'], thr, 'above'),
                                         thr, 'RV20>75pct')

    # ── Lead/lag calculation ───────────────────────────────────────────────
    # For every Q up-transition, find the nearest indicator event within ±50 bars
    max_window = 50
    rows = []
    for name, (sig_arr, thr, desc) in indicators.items():
        sig_idx = np.where(sig_arr)[0]
        leads   = []   # positive = Q leads indicator (Q fires first)
        for qt in q_up_idx:
            window = sig_idx[(sig_idx >= qt - max_window) & (sig_idx <= qt + max_window)]
            if len(window) == 0:
                continue
            nearest = window[np.argmin(np.abs(window - qt))]
            leads.append(int(qt - nearest))  # positive if Q before indicator

        if len(leads) == 0:
            rows.append({'indicator': name, 'description': desc,
                         'n_paired': 0, 'mean_lead_bars': np.nan,
                         'median_lead_bars': np.nan, 'std_lead_bars': np.nan})
            continue

        leads_arr = np.array(leads)
        rows.append({
            'indicator'         : name,
            'description'       : desc,
            'n_paired'          : len(leads_arr),
            'mean_lead_bars'    : float(leads_arr.mean()),    # +ve = Q leads
            'median_lead_bars'  : float(np.median(leads_arr)),
            'std_lead_bars'     : float(leads_arr.std()),
            'mean_lead_min'     : float(leads_arr.mean() * 5),
            'pct_Q_leads'       : float((leads_arr > 0).mean()),  # fraction where Q fires first
        })

    lead_lag_df = pd.DataFrame(rows)

    # ── Detection accuracy ─────────────────────────────────────────────────
    # True positive: Q up and indicator confirms within post_window bars
    post_window = 20
    det_rows = []
    for name, (sig_arr, thr, desc) in indicators.items():
        sig_idx = np.where(sig_arr)[0]
        n_q     = len(q_up_idx)
        n_true_pos = 0
        n_false_neg = 0
        for qt in q_up_idx:
            confirmed = np.any((sig_idx > qt) & (sig_idx <= qt + post_window))
            if confirmed:
                n_true_pos += 1
            else:
                n_false_neg += 1
        # False alarms: indicator fires but Q does not within post_window
        n_false_alarm = 0
        for si in sig_idx:
            q_follows = np.any((q_up_idx > si) & (q_up_idx <= si + post_window))
            if not q_follows:
                n_false_alarm += 1

        det_rows.append({
            'indicator'       : name,
            'n_q_transitions' : n_q,
            'true_positives'  : n_true_pos,
            'false_negatives' : n_false_neg,
            'n_ind_signals'   : len(sig_idx),
            'false_alarms'    : n_false_alarm,
            'detection_rate'  : float(n_true_pos / (n_q + 1e-12)),
            'false_alarm_rate': float(n_false_alarm / (len(sig_idx) + 1e-12)),
        })

    detection_df = pd.DataFrame(det_rows)

    # ── Spearman correlations at multiple lags ─────────────────────────────
    xcorr_rows = []
    for name in (['ADX_14', 'ATR_14', 'HistVol_20', 'BollWidth_20', 'RealizedVol_20']):
        col_map = {'ADX_14': 'adx_14', 'ATR_14': 'atr_14',
                   'HistVol_20': 'hist_vol_20', 'BollWidth_20': 'boll_width',
                   'RealizedVol_20': 'realized_vol_20'}
        col = col_map.get(name)
        if col not in df.columns:
            continue
        y = df[col].values
        for lag in range(-30, 31):
            if lag < 0:
                q_s, y_s = Q[:len(Q)+lag], y[-lag:]
            elif lag > 0:
                q_s, y_s = Q[lag:], y[:len(y)-lag]
            else:
                q_s, y_s = Q, y
            valid = np.isfinite(q_s) & np.isfinite(y_s)
            if valid.sum() < 30:
                continue
            rho, p = spearmanr(q_s[valid], y_s[valid])
            xcorr_rows.append({'indicator': name, 'lag': lag,
                                'spearman_rho': float(rho), 'p_value': float(p),
                                'n': int(valid.sum())})

    xcorr_df = pd.DataFrame(xcorr_rows)

    return {
        'lead_lag_df'  : lead_lag_df,
        'detection_df' : detection_df,
        'xcorr_df'     : xcorr_df,
    }
