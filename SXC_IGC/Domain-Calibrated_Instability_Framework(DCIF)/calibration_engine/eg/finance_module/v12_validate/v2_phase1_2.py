"""
v2_phase1_2.py  —  Phase I: Regime Persistence  &  Phase II: Volatility Cluster Origin
"""
import numpy as np
import pandas as pd
from scipy.stats import mannwhitneyu, spearmanr


# ─────────────────────────────────────────────────────────────────────────────
# Phase I — Regime Persistence
# ─────────────────────────────────────────────────────────────────────────────

def _run_lengths(regime: np.ndarray):
    """Return arrays of run-lengths for value=1 and value=0 runs."""
    runs1, runs0 = [], []
    cur = regime[0]; length = 1
    for v in regime[1:]:
        if v == cur:
            length += 1
        else:
            (runs1 if cur == 1 else runs0).append(length)
            cur = v; length = 1
    (runs1 if cur == 1 else runs0).append(length)
    return np.array(runs1, dtype=float), np.array(runs0, dtype=float)


def phase1_regime_persistence(df: pd.DataFrame) -> dict:
    """
    Compute run-length statistics and first-order Markov transition matrix
    for the Q regime (COHERENT=1, INCOHERENT=0).

    Returns a dict with:
      run_stats       pd.DataFrame  — summary stats per regime
      markov          pd.DataFrame  — 2×2 transition probability matrix
      transition_df   pd.DataFrame  — every regime episode
    """
    regime = (df['tr_Q'] > 0).astype(int).values
    runs_coh, runs_inc = _run_lengths(regime)

    # ── run-length stats ───────────────────────────────────────────────────
    def _stats(arr, name):
        if len(arr) == 0:
            return {'regime': name, 'n_episodes': 0}
        return {
            'regime'        : name,
            'n_episodes'    : len(arr),
            'mean_bars'     : float(arr.mean()),
            'median_bars'   : float(np.median(arr)),
            'std_bars'      : float(arr.std()),
            'min_bars'      : int(arr.min()),
            'max_bars'      : int(arr.max()),
            'p25_bars'      : float(np.percentile(arr, 25)),
            'p75_bars'      : float(np.percentile(arr, 75)),
            'mean_min'      : float(arr.mean() * 5),
            'median_min'    : float(np.median(arr) * 5),
        }

    run_stats = pd.DataFrame([_stats(runs_coh, 'COHERENT'),
                               _stats(runs_inc, 'INCOHERENT')])

    # ── Markov transition matrix ───────────────────────────────────────────
    trans = np.zeros((2, 2), dtype=int)
    for i in range(len(regime) - 1):
        trans[regime[i], regime[i + 1]] += 1

    row_sums = trans.sum(axis=1, keepdims=True)
    row_sums = np.where(row_sums == 0, 1, row_sums)
    prob = trans / row_sums

    markov = pd.DataFrame(prob,
                          index  =['from_INCOHERENT', 'from_COHERENT'],
                          columns=['to_INCOHERENT',   'to_COHERENT'])

    # ── episode catalogue ──────────────────────────────────────────────────
    episodes = []
    start = 0; cur = regime[0]
    for i in range(1, len(regime)):
        if regime[i] != cur:
            episodes.append({
                'start_bar'  : start,
                'end_bar'    : i - 1,
                'duration'   : i - start,
                'regime'     : 'COHERENT' if cur == 1 else 'INCOHERENT',
                'start_time' : df.index[start],
                'end_time'   : df.index[i - 1],
                'mean_Q'     : float(df['tr_Q'].iloc[start:i].mean()),
            })
            cur = regime[i]; start = i
    episodes.append({
        'start_bar'  : start,
        'end_bar'    : len(regime) - 1,
        'duration'   : len(regime) - start,
        'regime'     : 'COHERENT' if cur == 1 else 'INCOHERENT',
        'start_time' : df.index[start],
        'end_time'   : df.index[-1],
        'mean_Q'     : float(df['tr_Q'].iloc[start:].mean()),
    })
    transition_df = pd.DataFrame(episodes)

    # ── Is it persistent or noisy? ─────────────────────────────────────────
    # A geometric distribution implies memoryless (noisy); test if mean > 1.5
    coherent_mean = float(runs_coh.mean()) if len(runs_coh) > 0 else 0
    incoherent_mean = float(runs_inc.mean()) if len(runs_inc) > 0 else 0
    # Geometric null: E[run] = 1/p_switch; p_switch from off-diagonal Markov
    p_switch_coh  = float(prob[1, 0])  # P(COH→INCOH)
    p_switch_inc  = float(prob[0, 1])  # P(INCOH→COH)
    geometric_mean_coh  = 1.0 / (p_switch_coh  + 1e-12)
    geometric_mean_inc  = 1.0 / (p_switch_inc  + 1e-12)

    persistence_verdict = {
        'coherent_mean_bars'      : coherent_mean,
        'incoherent_mean_bars'    : incoherent_mean,
        'geometric_null_coh_bars' : geometric_mean_coh,
        'geometric_null_inc_bars' : geometric_mean_inc,
        'P_stay_coherent'         : float(prob[1, 1]),
        'P_stay_incoherent'       : float(prob[0, 0]),
        'verdict'                 : (
            'PERSISTENT' if (float(prob[1, 1]) > 0.7 or float(prob[0, 0]) > 0.7)
            else 'NOISY'
        ),
    }

    return {
        'run_stats'       : run_stats,
        'markov'          : markov,
        'transition_df'   : transition_df,
        'persistence'     : persistence_verdict,
    }


# ─────────────────────────────────────────────────────────────────────────────
# Phase II — Volatility Cluster Origin
# ─────────────────────────────────────────────────────────────────────────────

def phase2_volatility_cluster_origin(
    df: pd.DataFrame,
    pre_bars: int = 20,
    post_bars: int = 40,
) -> dict:
    """
    Event study: measure ATR, realized vol, and rolling variance in a
    [-pre_bars, +post_bars] window around every INCOHERENT→COHERENT transition.

    Returns:
      event_profiles   pd.DataFrame  — mean profile indexed by lag (bar)
      event_catalogue  pd.DataFrame  — one row per event with timestamps
      summary          dict          — whether vol expansion follows transition
    """
    regime = (df['tr_Q'] > 0).astype(int).values
    n      = len(regime)

    # Locate INCOH→COH transitions (0→1)
    transitions = [i for i in range(1, n) if regime[i] == 1 and regime[i - 1] == 0]

    if len(transitions) == 0:
        return {'event_profiles': pd.DataFrame(), 'event_catalogue': pd.DataFrame(),
                'summary': {'n_events': 0}}

    # Build ATR and realized vol arrays
    atr_arr = df['atr_14'].values if 'atr_14' in df.columns else np.full(n, np.nan)
    rv5_arr = df['realized_vol_5'].values  if 'realized_vol_5'  in df.columns else np.full(n, np.nan)
    rv20_arr= df['realized_vol_20'].values if 'realized_vol_20' in df.columns else np.full(n, np.nan)
    scol    = 'spread' if 'spread' in df.columns else 'spread_pips'
    spread  = df[scol].values              if scol               in df.columns else np.full(n, np.nan)
    vol_arr = df['vol_norm'].values        if 'vol_norm'         in df.columns else np.full(n, np.nan)
    Q_arr   = df['tr_Q'].values

    lags    = np.arange(-pre_bars, post_bars + 1)
    records = {lag: {'atr': [], 'rv5': [], 'rv20': [], 'spread': [], 'vol': [], 'Q': []}
               for lag in lags}

    cat_rows = []
    for t in transitions:
        i0 = t - pre_bars
        i1 = t + post_bars
        if i0 < 0 or i1 >= n:
            continue
        # Normalize by pre-event mean ATR (avoid scale differences across events)
        pre_atr = np.nanmean(atr_arr[i0: t])
        scale   = pre_atr if (pre_atr > 0 and not np.isnan(pre_atr)) else 1.0
        for lag in lags:
            idx = t + lag
            records[lag]['atr'].append(atr_arr[idx] / scale)
            records[lag]['rv5'].append(rv5_arr[idx])
            records[lag]['rv20'].append(rv20_arr[idx])
            records[lag]['spread'].append(spread[idx])
            records[lag]['vol'].append(vol_arr[idx])
            records[lag]['Q'].append(Q_arr[idx])
        cat_rows.append({
            'transition_bar'  : t,
            'transition_time' : df.index[t],
            'pre_atr'         : float(pre_atr),
            'Q_at_transition' : float(Q_arr[t]),
            'post5_atr'       : float(np.nanmean(atr_arr[t: t + 5])),
            'atr_expansion'   : float(np.nanmean(atr_arr[t: t + 5]) / (scale + 1e-12)),
        })

    profile_rows = []
    for lag in lags:
        vals = records[lag]
        profile_rows.append({
            'lag'           : lag,
            'mean_atr_norm' : float(np.nanmean(vals['atr'])),
            'mean_rv5'      : float(np.nanmean(vals['rv5'])),
            'mean_rv20'     : float(np.nanmean(vals['rv20'])),
            'mean_spread'   : float(np.nanmean(vals['spread'])),
            'mean_vol'      : float(np.nanmean(vals['vol'])),
            'mean_Q'        : float(np.nanmean(vals['Q'])),
            'std_atr_norm'  : float(np.nanstd(vals['atr'])),
            'n_events'      : int(np.sum(~np.isnan(vals['atr']))),
        })

    event_profiles  = pd.DataFrame(profile_rows)
    event_catalogue = pd.DataFrame(cat_rows)

    # Summary: does ATR in post_bars > pre_bars?
    pre_mean  = event_profiles.loc[event_profiles['lag'] < 0,  'mean_atr_norm'].mean()
    post_mean = event_profiles.loc[event_profiles['lag'] >= 0, 'mean_atr_norm'].mean()
    post5_mean= event_profiles.loc[(event_profiles['lag'] >= 0) & (event_profiles['lag'] <= 5), 'mean_atr_norm'].mean()

    # Mann-Whitney test: pre-event ATR vs post-event ATR
    pre_vals  = event_profiles.loc[event_profiles['lag'] < 0,  'mean_atr_norm'].values
    post_vals = event_profiles.loc[event_profiles['lag'] >= 0, 'mean_atr_norm'].values
    try:
        u, p = mannwhitneyu(post_vals, pre_vals, alternative='greater')
    except Exception:
        u, p = np.nan, np.nan

    summary = {
        'n_events'           : len(cat_rows),
        'pre_mean_atr_norm'  : float(pre_mean),
        'post_mean_atr_norm' : float(post_mean),
        'post5_mean_atr_norm': float(post5_mean),
        'vol_expansion_ratio': float(post_mean / (pre_mean + 1e-12)),
        'mw_u'               : float(u),
        'mw_p'               : float(p),
        'vol_expansion_significant': bool(p < 0.05) if not np.isnan(p) else False,
    }

    return {
        'event_profiles'  : event_profiles,
        'event_catalogue' : event_catalogue,
        'summary'         : summary,
    }
