"""
v2_phase5_8.py  —  Phase V: Position Sizing | VI: Risk Mgmt | VII: Execution | VIII: Microstructure
"""
import numpy as np
import pandas as pd
from scipy.stats import mannwhitneyu

PIP_COST = 0.00020


# ── Phase V helpers ───────────────────────────────────────────────────────

def _q_to_size(q):
    if q <= -0.5:   return 0.25
    elif q <= 0.0:  return 0.50
    elif q <= 1.0:  return 1.00
    else:           return 1.50


def _perf(r_arr, label):
    r = r_arr[np.isfinite(r_arr)]
    if len(r) == 0:
        return {'sizing': label, 'n': 0}
    wins = r[r > 0]; losses = r[r < 0]
    pf   = wins.sum() / (abs(losses.sum()) + 1e-12)
    sh   = r.mean() / (r.std() + 1e-12) * np.sqrt(len(r))
    eq   = np.cumprod(1 + r)
    dd   = (eq - np.maximum.accumulate(eq)) / (np.maximum.accumulate(eq) + 1e-12)
    return {'sizing': label, 'n': len(r),
            'total_ret': float(eq[-1] - 1), 'avg_ret': float(r.mean()),
            'profit_factor': float(pf), 'sharpe': float(sh),
            'max_drawdown': float(dd.min()), 'win_rate': float((r > 0).mean())}


def phase5_position_sizing(all_trades: pd.DataFrame) -> dict:
    if len(all_trades) == 0:
        return {}
    t = all_trades.copy()
    t['q_size']    = t['entry_Q'].apply(_q_to_size)
    t['sized_ret'] = t['net_ret'] * t['q_size']

    cmp = pd.DataFrame([_perf(t['net_ret'].values,    'FLAT_100pct'),
                         _perf(t['sized_ret'].values,  'Q_SIZED')])

    t['bucket'] = pd.cut(t['q_size'], bins=[0,.3,.6,1.1,2.],
                          labels=['25%','50%','100%','150%'])
    brows = []
    for bkt, sub in t.groupby('bucket', observed=True):
        r = sub['net_ret'].values; r = r[np.isfinite(r)]
        if len(r) < 3: continue
        wins = r[r>0]; losses = r[r<0]
        brows.append({'bucket': str(bkt), 'n': len(r),
                      'avg_Q': float(sub['entry_Q'].mean()),
                      'avg_ret': float(r.mean()),
                      'pf': float(wins.sum()/(abs(losses.sum())+1e-12)),
                      'win_rate': float((r>0).mean())})
    return {'comparison': cmp, 'bucket_stats': pd.DataFrame(brows)}


# ── Phase VI helpers ──────────────────────────────────────────────────────

def _q_stop_target(q, atr):
    if   q >  1.0: return 2.0*atr, 4.0*atr
    elif q >  0.0: return 1.5*atr, 3.0*atr
    elif q > -0.5: return 1.0*atr, 1.5*atr
    else:          return 0.5*atr, 0.75*atr


def phase6_risk_management(df: pd.DataFrame, all_trades: pd.DataFrame) -> dict:
    if len(all_trades) == 0:
        return {}
    close   = df['close'].values
    Q_arr   = df['tr_Q'].values
    atr_arr = df['atr_14'].values if 'atr_14' in df.columns else np.ones(len(df)) * 0.0001
    n       = len(df)
    idx_map = {ts: i for i, ts in enumerate(df.index)}

    rows = []
    for _, tr in all_trades.iterrows():
        if tr['entry_time'] not in idx_map:
            continue
        i   = idx_map[tr['entry_time']]
        d   = int(tr['direction'])
        ep  = close[i]
        q   = float(Q_arr[i])
        atr = float(atr_arr[i]) if not np.isnan(atr_arr[i]) else 0.0001
        sd, td = _q_stop_target(q, atr)
        sp  = ep - d * sd
        tp  = ep + d * td
        rr  = td / (sd + 1e-12)
        outcome = 'timeout'
        ei = min(i + 20, n - 1)
        for j in range(i+1, ei+1):
            p = close[j]
            if d == 1:
                if p <= sp: outcome='stop';   ei=j; break
                if p >= tp: outcome='target'; ei=j; break
            else:
                if p >= sp: outcome='stop';   ei=j; break
                if p <= tp: outcome='target'; ei=j; break
        gross = d*(close[ei]-ep)/(ep+1e-12)
        net   = gross - PIP_COST/ep
        bkt   = ('high' if q>1 else 'med' if q>0 else 'low' if q>-0.5 else 'deep')
        rows.append({'strategy': tr['strategy'], 'entry_Q': q, 'Q_bucket': bkt,
                     'stop_atr': sd/(atr+1e-12), 'tgt_atr': td/(atr+1e-12),
                     'rr': rr, 'outcome': outcome, 'net_ret': net,
                     'stop_hit': outcome=='stop', 'target_hit': outcome=='target'})

    rm = pd.DataFrame(rows)
    if len(rm) == 0:
        return {}
    srows = []
    for bkt, sub in rm.groupby('Q_bucket'):
        r = sub['net_ret'].values; r = r[np.isfinite(r)]
        if len(r) < 3: continue
        wins=r[r>0]; losses=r[r<0]
        srows.append({'Q_bucket': bkt, 'n': len(r),
                      'stop_rate': float(sub['stop_hit'].mean()),
                      'target_rate': float(sub['target_hit'].mean()),
                      'avg_reward': float(wins.mean()) if len(wins)>0 else 0.,
                      'avg_loss': float(losses.mean()) if len(losses)>0 else 0.,
                      'pf': float(wins.sum()/(abs(losses.sum())+1e-12)),
                      'avg_rr': float(sub['rr'].mean())})
    return {'rm_trades': rm, 'rm_summary': pd.DataFrame(srows)}


# ── Phase VII ─────────────────────────────────────────────────────────────

def phase7_execution_quality(df: pd.DataFrame) -> dict:
    n      = len(df)
    Q      = df['tr_Q'].values
    regime = (Q > 0).astype(int)
    spread = df['spread_pips'].values if 'spread_pips' in df.columns else np.full(n, np.nan)
    vol    = df['vol_norm'].values    if 'vol_norm'    in df.columns else np.full(n, np.nan)
    iae    = np.abs(np.diff(df['close'].values, prepend=np.nan))

    rows = []
    for lbl, rv in [('COHERENT', 1), ('INCOHERENT', 0)]:
        m  = regime == rv
        sp = spread[m]; sp = sp[np.isfinite(sp)]
        vl = vol[m];    vl = vl[np.isfinite(vl)]
        ia = iae[m];    ia = ia[np.isfinite(ia)]
        rows.append({'regime': lbl, 'n_bars': int(m.sum()),
                     'mean_spread': float(np.nanmean(sp)),
                     'median_spread': float(np.nanmedian(sp)),
                     'p95_spread': float(np.nanpercentile(sp,95)) if len(sp)>0 else np.nan,
                     'mean_vol_norm': float(np.nanmean(vl)),
                     'mean_iae': float(np.nanmean(ia)),
                     'median_iae': float(np.nanmedian(ia))})

    exec_df = pd.DataFrame(rows)
    coh = spread[regime==1]; inc = spread[regime==0]
    coh = coh[np.isfinite(coh)]; inc = inc[np.isfinite(inc)]
    try:
        u, p = mannwhitneyu(coh, inc, alternative='two-sided')
    except Exception:
        u, p = np.nan, np.nan
    exec_df.attrs['mw_p'] = float(p)
    return {'exec_df': exec_df, 'mw_spread_p': float(p)}


# ── Phase VIII ────────────────────────────────────────────────────────────

def phase8_microstructure(df: pd.DataFrame) -> dict:
    n      = len(df)
    Q      = df['tr_Q'].values
    spread = df['spread_pips'].values if 'spread_pips' in df.columns else np.full(n, np.nan)
    vol    = df['volume'].values      if 'volume'      in df.columns else np.full(n, np.nan)
    tc     = df['tick_count'].values  if 'tick_count'  in df.columns else np.full(n, np.nan)
    vol_ma = pd.Series(vol).rolling(5).mean().values
    vol_acc= (vol - vol_ma) / (vol_ma + 1e-10)

    transitions = []
    for i in range(1, n):
        if Q[i]>0 and Q[i-1]<=0: transitions.append(('INCOH_COH', i))
        elif Q[i]<0 and Q[i-1]>=0: transitions.append(('COH_INCOH', i))

    W = 15
    acc = {k: {lag: {'sp':[],'va':[],'tc':[]} for lag in range(-W,W+1)}
           for k in ['INCOH_COH','COH_INCOH']}
    for kind, t in transitions:
        if t-W<0 or t+W>=n: continue
        for lag in range(-W, W+1):
            idx = t+lag
            acc[kind][lag]['sp'].append(spread[idx])
            acc[kind][lag]['va'].append(vol_acc[idx])
            acc[kind][lag]['tc'].append(tc[idx])

    rows = []
    for kind in acc:
        for lag, v in acc[kind].items():
            rows.append({'type': kind, 'lag': lag,
                         'mean_spread': float(np.nanmean(v['sp'])),
                         'mean_vol_acc': float(np.nanmean(v['va'])),
                         'mean_ticks': float(np.nanmean(v['tc'])),
                         'n': int(np.sum(np.isfinite(v['sp'])))})
    micro_df = pd.DataFrame(rows)

    summary = {}
    for kind in ['INCOH_COH','COH_INCOH']:
        sub = micro_df[micro_df['type']==kind]
        pre  = sub[sub['lag']<0]['mean_spread'].mean()
        post = sub[sub['lag']>=0]['mean_spread'].mean()
        summary[f'{kind}_pre_spread']   = float(pre)
        summary[f'{kind}_post_spread']  = float(post)
        summary[f'{kind}_spread_ratio'] = float(post/(pre+1e-12))
    return {'micro_df': micro_df, 'micro_summary': summary,
            'n_transitions': len(transitions)}
