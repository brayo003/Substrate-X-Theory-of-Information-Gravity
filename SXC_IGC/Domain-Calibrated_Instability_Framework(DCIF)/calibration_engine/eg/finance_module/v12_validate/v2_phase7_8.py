"""v2_phase7_8.py — Phase VII: Execution Quality | Phase VIII: Microstructure"""
import numpy as np
import pandas as pd
from scipy.stats import mannwhitneyu


def phase7_execution_quality(df: pd.DataFrame) -> dict:
    n      = len(df)
    Q      = df['tr_Q'].values
    regime = (Q > 0).astype(int)
    scol   = 'spread' if 'spread' in df.columns else 'spread_pips'
    spread = df[scol].values         if scol      in df.columns else np.full(n, np.nan)
    vol    = df['vol_norm'].values   if 'vol_norm' in df.columns else np.full(n, np.nan)
    iae    = np.abs(np.diff(df['close'].values, prepend=np.nan))

    rows = []
    for lbl, rv in [('COHERENT', 1), ('INCOHERENT', 0)]:
        m  = regime == rv
        sp = spread[m]; sp = sp[np.isfinite(sp)]
        vl = vol[m];    vl = vl[np.isfinite(vl)]
        ia = iae[m];    ia = ia[np.isfinite(ia)]
        rows.append({
            'regime':         lbl,
            'n_bars':         int(m.sum()),
            'mean_spread':    float(np.nanmean(sp))    if len(sp) > 0 else np.nan,
            'median_spread':  float(np.nanmedian(sp))  if len(sp) > 0 else np.nan,
            'p95_spread':     float(np.nanpercentile(sp, 95)) if len(sp) > 0 else np.nan,
            'mean_vol_norm':  float(np.nanmean(vl))    if len(vl) > 0 else np.nan,
            'mean_iae':       float(np.nanmean(ia))    if len(ia) > 0 else np.nan,
            'median_iae':     float(np.nanmedian(ia))  if len(ia) > 0 else np.nan,
        })

    exec_df = pd.DataFrame(rows)
    coh = spread[regime == 1]; coh = coh[np.isfinite(coh)]
    inc = spread[regime == 0]; inc = inc[np.isfinite(inc)]
    try:
        u, p = mannwhitneyu(coh, inc, alternative='two-sided')
    except Exception:
        u, p = np.nan, np.nan
    return {'exec_df': exec_df, 'mw_spread_u': float(u), 'mw_spread_p': float(p)}


def phase8_microstructure(df: pd.DataFrame) -> dict:
    n      = len(df)
    Q      = df['tr_Q'].values
    scol   = 'spread' if 'spread' in df.columns else 'spread_pips'
    spread = df[scol].values          if scol      in df.columns else np.full(n, np.nan)
    vol    = df['volume'].values      if 'volume'   in df.columns else np.full(n, np.nan)
    tc     = df['tick_count'].values  if 'tick_count' in df.columns else np.full(n, np.nan)
    vol_ma  = pd.Series(vol).rolling(5).mean().values
    vol_acc = (vol - vol_ma) / (np.abs(vol_ma) + 1e-10)

    transitions = []
    for i in range(1, n):
        if Q[i] > 0 and Q[i-1] <= 0:
            transitions.append(('INCOH_COH', i))
        elif Q[i] < 0 and Q[i-1] >= 0:
            transitions.append(('COH_INCOH', i))

    W   = 15
    acc = {k: {lag: {'sp': [], 'va': [], 'tc': []}
               for lag in range(-W, W+1)}
           for k in ['INCOH_COH', 'COH_INCOH']}

    for kind, t in transitions:
        if t - W < 0 or t + W >= n:
            continue
        for lag in range(-W, W+1):
            idx = t + lag
            acc[kind][lag]['sp'].append(float(spread[idx]))
            acc[kind][lag]['va'].append(float(vol_acc[idx]))
            acc[kind][lag]['tc'].append(float(tc[idx]))

    rows = []
    for kind in acc:
        for lag, v in acc[kind].items():
            rows.append({
                'type':        kind,
                'lag':         lag,
                'mean_spread': float(np.nanmean(v['sp'])),
                'mean_vol_acc':float(np.nanmean(v['va'])),
                'mean_ticks':  float(np.nanmean(v['tc'])),
                'n_events':    int(np.sum(np.isfinite(v['sp']))),
            })
    micro_df = pd.DataFrame(rows)

    summary = {'n_transitions': len(transitions)}
    for kind in ['INCOH_COH', 'COH_INCOH']:
        sub  = micro_df[micro_df['type'] == kind]
        pre  = float(sub[sub['lag'] <  0]['mean_spread'].mean())
        post = float(sub[sub['lag'] >= 0]['mean_spread'].mean())
        summary[f'{kind}_pre_spread']   = pre
        summary[f'{kind}_post_spread']  = post
        summary[f'{kind}_spread_ratio'] = post / (pre + 1e-12)

    return {'micro_df': micro_df, 'micro_summary': summary}
