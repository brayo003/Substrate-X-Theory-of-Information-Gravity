"""v2_phase5_6.py — Phase V: Position Sizing | Phase VI: Risk Management"""
import numpy as np
import pandas as pd

PIP_COST = 0.00020


def _q_size(q):
    if q <= -0.5:  return 0.25
    elif q <= 0.0: return 0.50
    elif q <= 1.0: return 1.00
    else:          return 1.50


def _q_bucket(q):
    if q > 1.0:    return 'high'
    elif q > 0.0:  return 'med'
    elif q > -0.5: return 'low'
    else:          return 'deep'


def _q_stop_target(q, atr):
    if q > 1.0:    return 2.0*atr, 4.0*atr
    elif q > 0.0:  return 1.5*atr, 3.0*atr
    elif q > -0.5: return 1.0*atr, 1.5*atr
    else:          return 0.5*atr, 0.75*atr


def _perf_row(rets, label):
    r = np.asarray(rets, dtype=float)
    r = r[np.isfinite(r)]
    if len(r) == 0:
        return {'label': label, 'n': 0}
    wins = r[r > 0]; losses = r[r < 0]
    pf = wins.sum() / (abs(losses.sum()) + 1e-12)
    sh = r.mean() / (r.std() + 1e-12) * np.sqrt(len(r))
    eq = np.cumprod(1 + r)
    dd = (eq - np.maximum.accumulate(eq)) / (np.maximum.accumulate(eq) + 1e-12)
    return {'label': label, 'n': len(r),
            'total_ret': float(eq[-1]-1), 'avg_ret': float(r.mean()),
            'pf': float(pf), 'sharpe': float(sh),
            'max_dd': float(dd.min()), 'win_rate': float((r > 0).mean())}


# ── Phase V ───────────────────────────────────────────────────────────────

def phase5_position_sizing(all_trades: pd.DataFrame) -> dict:
    if len(all_trades) == 0:
        return {}
    t = all_trades.copy()
    t['q_size']    = t['entry_Q'].apply(_q_size)
    t['sized_ret'] = t['net_ret'] * t['q_size']

    comparison = pd.DataFrame([
        _perf_row(t['net_ret'].values,   'FLAT_100pct'),
        _perf_row(t['sized_ret'].values, 'Q_SIZED'),
    ])

    t['bucket'] = pd.cut(t['q_size'], bins=[0, .3, .6, 1.1, 2.],
                          labels=['25%', '50%', '100%', '150%'])
    rows = []
    for bkt, sub in t.groupby('bucket', observed=True):
        r = sub['net_ret'].values; r = r[np.isfinite(r)]
        if len(r) < 3: continue
        wins = r[r > 0]; losses = r[r < 0]
        rows.append({'bucket': str(bkt), 'n': len(r),
                     'avg_Q': float(sub['entry_Q'].mean()),
                     'avg_ret': float(r.mean()),
                     'pf': float(wins.sum()/(abs(losses.sum())+1e-12)),
                     'win_rate': float((r > 0).mean())})
    return {'comparison': comparison, 'bucket_stats': pd.DataFrame(rows)}


# ── Phase VI ──────────────────────────────────────────────────────────────

def phase6_risk_management(df: pd.DataFrame, all_trades: pd.DataFrame) -> dict:
    if len(all_trades) == 0:
        return {}
    close   = df['close'].values
    Q_arr   = df['tr_Q'].values
    atr_arr = df['atr_14'].values if 'atr_14' in df.columns else np.ones(len(df)) * 1e-4
    n       = len(df)
    idx_map = {ts: i for i, ts in enumerate(df.index)}

    rows = []
    for _, tr in all_trades.iterrows():
        if tr['entry_time'] not in idx_map:
            continue
        i   = idx_map[tr['entry_time']]
        d   = int(tr['direction'])
        ep  = float(close[i])
        q   = float(Q_arr[i])
        atr = float(atr_arr[i]) if np.isfinite(atr_arr[i]) else 1e-4
        sd, td = _q_stop_target(q, atr)
        sp = ep - d * sd
        tp = ep + d * td
        outcome = 'timeout'
        ei = min(i + 20, n - 1)
        for j in range(i+1, ei+1):
            p = float(close[j])
            if d == 1:
                if p <= sp: outcome = 'stop';   ei = j; break
                if p >= tp: outcome = 'target'; ei = j; break
            else:
                if p >= sp: outcome = 'stop';   ei = j; break
                if p <= tp: outcome = 'target'; ei = j; break
        net = d*(float(close[ei])-ep)/(ep+1e-12) - PIP_COST/ep
        rows.append({'strategy': tr['strategy'], 'entry_Q': q,
                     'Q_bucket': _q_bucket(q),
                     'stop_atr': sd/(atr+1e-12), 'tgt_atr': td/(atr+1e-12),
                     'rr': td/(sd+1e-12), 'outcome': outcome,
                     'net_ret': net, 'stop_hit': outcome=='stop',
                     'target_hit': outcome=='target'})

    rm = pd.DataFrame(rows)
    if len(rm) == 0:
        return {}
    srows = []
    for bkt, sub in rm.groupby('Q_bucket'):
        r = sub['net_ret'].values; r = r[np.isfinite(r)]
        if len(r) < 3: continue
        wins = r[r > 0]; losses = r[r < 0]
        srows.append({'Q_bucket': bkt, 'n': len(r),
                      'stop_rate':   float(sub['stop_hit'].mean()),
                      'target_rate': float(sub['target_hit'].mean()),
                      'avg_reward':  float(wins.mean())   if len(wins)   > 0 else 0.,
                      'avg_loss':    float(losses.mean()) if len(losses) > 0 else 0.,
                      'pf': float(wins.sum()/(abs(losses.sum())+1e-12)),
                      'avg_rr': float(sub['rr'].mean())})
    return {'rm_trades': rm, 'rm_summary': pd.DataFrame(srows)}
