"""
xauusd_baseline.py
==================
Baseline strategy test on XAUUSD daily bars.

DATA
----
  Daily bid bars, 566 bars, 2025-01-01 to 2026-07-21.
  Bid prices only — no embedded spread.

COST MODEL
----------
  XAUUSD daily bars.  Enter at next bar's open.
  Conservative RT cost: 0.75 USD/oz (mid-range of 0.50–1.00 USD estimate).
  2x sensitivity: 1.50 USD/oz.
  No point-value adjustment needed — prices already in USD/oz.

STRATEGIES (3 simple baselines, distinct rationales)
------------------------------------------------------
  1. EMA_Trend:   EMA10 / EMA30 crossover. Enter at next open.
                  Stop = 1.5 × ATR14, Target = 2.5 × ATR14, Hold = 20 bars.
  2. Donchian20:  Close above/below 20-day channel high/low.
                  Stop = 1.5 × ATR14, Target = 3.0 × ATR14, Hold = 30 bars.
  3. MOM_Revert:  RSI(14) exit from extreme (<30 / >70): fade exhaustion.
                  Stop = 1.0 × ATR14, Target = 2.0 × ATR14, Hold = 15 bars.

WALK-FORWARD
------------
  IS  : 2025-01 to 2025-08  (8 months, ~173 bars) — parameter confirmation
  WF1 : 2025-09 to 2025-12  (4 months, ~87 bars)
  WF2 : 2026-01 to 2026-07  (7 months, ~140 bars — previously seen; noted as limitation)

  NOTE: With only 566 daily bars total, WF folds are small. WF2 overlaps the
  previously examined 2026 period, so it is a consistency check, not fresh OOS.
  Results should be interpreted with appropriate uncertainty given small N.

SUCCESS CRITERIA (pre-defined)
-------------------------------
  WF combined: PF > 1.20, expectancy > 0 USD, N >= 20, min-fold PF >= 0.60.
  Lower bar than the 5-min experiment because daily-bar trade counts are small.

OUTPUT
------
  results/xauusd_baseline/signal_stats.csv
  results/xauusd_baseline/trade_log.csv
  results/xauusd_baseline/BASELINE_REPORT.md
"""

import json, warnings
from pathlib import Path
import numpy as np
import pandas as pd

warnings.filterwarnings("ignore")

HERE    = Path(__file__).resolve().parent
OUT_DIR = HERE / "results" / "xauusd_baseline"
OUT_DIR.mkdir(parents=True, exist_ok=True)

RT_COST    = 0.75   # USD per oz, round-trip (conservative mid-range)
RT_COST_2X = 1.50

IS_END  = "2025-08-31"
WF1_START = "2025-09-01"; WF1_END = "2025-12-31"
WF2_START = "2026-01-01"; WF2_END = "2026-07-21"


# ── Load data ──────────────────────────────────────────────────────────────

def load_xauusd() -> pd.DataFrame:
    import json as _json
    frames = []
    p25 = HERE / "data/XAUUSD/xauusd-d1-bid-2025-01-01-2025-12-31.json"
    p26 = HERE / "data/XAUUSD/xauusd-d1-bid-2026-01-01-2026-07-22.csv"
    if p25.exists():
        raw = _json.loads(p25.read_text())
        df  = pd.DataFrame(raw)
        df['date'] = pd.to_datetime(df['timestamp'], unit='ms', utc=True)
        frames.append(df.set_index('date')[['open','high','low','close']])
    if p26.exists():
        df  = pd.read_csv(p26)
        df['date'] = pd.to_datetime(df['timestamp'], unit='ms', utc=True)
        frames.append(df.set_index('date')[['open','high','low','close']])
    full = pd.concat(frames).sort_index()
    full = full[~full.index.duplicated(keep='first')]
    return full


def add_indicators(df: pd.DataFrame) -> pd.DataFrame:
    c  = df['close']
    h  = df['high']
    l  = df['low']
    pc = c.shift(1)
    tr = pd.concat([h-l, (h-pc).abs(), (l-pc).abs()], axis=1).max(axis=1)
    df['atr14']  = tr.ewm(span=14, adjust=False).mean()
    df['ema10']  = c.ewm(span=10, adjust=False).mean()
    df['ema30']  = c.ewm(span=30, adjust=False).mean()
    df['don_hi'] = h.rolling(20).max().shift(1)  # prior 20-bar high
    df['don_lo'] = l.rolling(20).min().shift(1)
    # RSI(14)
    delta = c.diff()
    gain  = delta.clip(lower=0).ewm(span=14, adjust=False).mean()
    loss  = (-delta.clip(upper=0)).ewm(span=14, adjust=False).mean()
    df['rsi14']  = 100 - 100/(1 + gain/(loss + 1e-10))
    return df


# ── Signals ────────────────────────────────────────────────────────────────

def sig_ema(df):
    s    = pd.Series(0, index=df.index, dtype=np.int8)
    diff = df['ema10'] - df['ema30']
    s[(diff > 0) & (diff.shift(1) <= 0)] =  1
    s[(diff < 0) & (diff.shift(1) >= 0)] = -1
    return s

def sig_don(df):
    s = pd.Series(0, index=df.index, dtype=np.int8)
    c = df['close']
    s[(c > df['don_hi']) & (c.shift(1) <= df['don_hi'].shift(1))] =  1
    s[(c < df['don_lo']) & (c.shift(1) >= df['don_lo'].shift(1))] = -1
    return s

def sig_rsi(df):
    s   = pd.Series(0, index=df.index, dtype=np.int8)
    rsi = df['rsi14']
    s[(rsi > 30) & (rsi.shift(1) <= 30)] =  1   # exit oversold → long
    s[(rsi < 70) & (rsi.shift(1) >= 70)] = -1   # exit overbought → short
    return s


# ── Simulator ─────────────────────────────────────────────────────────────

def simulate(df, signal, stop_m, tgt_m, hold, label, period):
    rec = []
    in_t = False
    d = ep = st = tg = ea = 0.0
    eb = -1
    sig  = signal.values.astype(np.int8)
    opn  = df['open'].values
    cls  = df['close'].values
    hi   = df['high'].values
    lo   = df['low'].values
    atr  = df['atr14'].values
    ts   = df.index
    n    = len(df)
    for i in range(1, n):
        if in_t:
            held = i - eb
            if d == 1  and lo[i] <= st: xp, xr = st, 'stop'
            elif d==-1 and hi[i] >= st: xp, xr = st, 'stop'
            elif d == 1  and hi[i] >= tg: xp, xr = tg, 'target'
            elif d==-1  and lo[i] <= tg: xp, xr = tg, 'target'
            elif held >= hold:           xp, xr = cls[i], 'time'
            else: continue
            raw = d*(xp - ep); net = raw - RT_COST
            rec.append(dict(strategy=label, period=period,
                            entry_time=ts[eb], exit_time=ts[i],
                            direction=int(d), entry_price=ep, exit_price=xp,
                            exit_reason=xr, bars_held=held,
                            entry_atr=ea, raw_pnl=raw, net_pnl=net))
            in_t = False
        if not in_t and sig[i-1] != 0:
            d=int(sig[i-1]); ep=float(opn[i]); eb=i
            ea=max(float(atr[i]),0.01)
            st=ep - d*stop_m*ea; tg=ep + d*tgt_m*ea; in_t=True
    if in_t:
        raw=d*(cls[-1]-ep); net=raw-RT_COST
        rec.append(dict(strategy=label, period=period,
                        entry_time=ts[eb], exit_time=ts[-1],
                        direction=int(d), entry_price=ep, exit_price=cls[-1],
                        exit_reason='end', bars_held=n-eb,
                        entry_atr=ea, raw_pnl=raw, net_pnl=net))
    return pd.DataFrame(rec)


# ── Metrics ────────────────────────────────────────────────────────────────

def metrics(t, label, period):
    if t is None or len(t)==0:
        return dict(strategy=label, period=period, n=0,
                    wr=float('nan'), pf=float('nan'),
                    exp_usd=float('nan'), total_usd=float('nan'),
                    pf_2x=float('nan'), ci_lo=float('nan'), ci_hi=float('nan'))
    pnl = t['net_pnl']
    w = pnl[pnl>0]; l = pnl[pnl<=0]
    pf  = (w.sum()/-l.sum()) if l.sum()<0 else float('inf')
    exp = pnl.mean()
    p2  = pnl - RT_COST
    pf2 = (p2[p2>0].sum()/-p2[p2<=0].sum()) if p2[p2<=0].sum()<0 else float('inf')
    rng = np.random.default_rng(42)
    if len(t)>=5:
        boots=[rng.choice(pnl.values,size=len(t),replace=True).mean() for _ in range(2000)]
        ci_lo=float(np.percentile(boots,2.5)); ci_hi=float(np.percentile(boots,97.5))
    else:
        ci_lo=ci_hi=float('nan')
    return dict(strategy=label, period=period, n=len(t),
                wr=round(len(w)/len(t),3),
                pf=round(pf,3), exp_usd=round(exp,3),
                total_usd=round(pnl.sum(),2),
                pf_2x=round(pf2,3),
                ci_lo=round(ci_lo,3), ci_hi=round(ci_hi,3))


# ── Main ───────────────────────────────────────────────────────────────────

def main():
    print("=== XAUUSD DAILY BASELINE ===")
    df = load_xauusd()
    df = add_indicators(df)
    print(f"  {len(df)} bars  {df.index[0].date()} – {df.index[-1].date()}")

    splits = {"IS":  df[:IS_END],
              "WF1": df[WF1_START:WF1_END],
              "WF2": df[WF2_START:WF2_END]}
    for nm,sl in splits.items():
        print(f"  {nm}: {len(sl)} bars")

    cfg = [("EMA_Trend",    sig_ema, 1.5, 2.5, 20),
           ("Donchian20",   sig_don, 1.5, 3.0, 30),
           ("RSI_Reversion",sig_rsi, 1.0, 2.0, 15)]

    all_t=[]; all_m=[]
    print()
    for pname, sl in splits.items():
        for label, sigfn, sm, tm, hb in cfg:
            sig = sigfn(df)[sl.index]
            t   = simulate(sl, sig, sm, tm, hb, label, pname)
            m   = metrics(t, label, pname)
            all_t.append(t); all_m.append(m)
            print(f"  {pname:4s}|{label:16s}| N={m['n']:3d}  "
                  f"PF={m['pf']:.3f}  exp={m['exp_usd']:+.3f} USD")

    stats = pd.DataFrame(all_m)
    stats.to_csv(OUT_DIR/"signal_stats.csv", index=False)
    nonempty=[t for t in all_t if not t.empty]
    if nonempty:
        trades=pd.concat(nonempty,ignore_index=True)
        trades.to_csv(OUT_DIR/"trade_log.csv", index=False)
    else:
        trades=pd.DataFrame()

    # WF combined
    print("\n=== WF COMBINED (WF1+WF2) ===")
    print(f"  RT cost: {RT_COST} USD/oz  |  2x: {RT_COST_2X} USD/oz")
    print(f"  {'Strategy':<18} {'N':>4} {'PF':>6} {'PF2x':>6} "
          f"{'exp':>8} {'CI_lo':>8} {'CI_hi':>8}  PASS")
    if not trades.empty:
        wf = trades[trades['period'].isin(['WF1','WF2'])]
        for label,*_ in cfg:
            tl = wf[wf['strategy']==label]
            n=len(tl)
            if n==0: continue
            pnl=tl['net_pnl']
            w=pnl[pnl>0]; l=pnl[pnl<=0]
            pf=(w.sum()/-l.sum()) if l.sum()<0 else float('inf')
            exp=pnl.mean()
            p2=pnl-RT_COST
            pf2=(p2[p2>0].sum()/-p2[p2<=0].sum()) if p2[p2<=0].sum()<0 else float('inf')
            rng=np.random.default_rng(42)
            if n>=5:
                boots=[rng.choice(pnl.values,size=n,replace=True).mean() for _ in range(2000)]
                ci_lo=float(np.percentile(boots,2.5)); ci_hi=float(np.percentile(boots,97.5))
            else:
                ci_lo=ci_hi=float('nan')
            fold_pfs=[]
            for fold in ['WF1','WF2']:
                ft=tl[tl['period']==fold]
                if len(ft):
                    fw=ft[ft.net_pnl>0].net_pnl.sum(); fl=ft[ft.net_pnl<=0].net_pnl.sum()
                    fold_pfs.append((fw/-fl) if fl<0 else float('inf'))
            min_pf=min(fold_pfs) if fold_pfs else 0.0
            passed=(pf>1.20 and exp>0 and n>=20 and min_pf>=0.60)
            flag="PASS" if passed else "FAIL"
            print(f"  {label:<18} {n:>4}  {pf:>5.3f}  {pf2:>5.3f}  "
                  f"{exp:>+7.3f}  {ci_lo:>7.3f}  {ci_hi:>7.3f}  {flag}")

    return stats, trades

if __name__=="__main__":
    stats, trades = main()
    print(f"\nOutputs: {OUT_DIR}")
