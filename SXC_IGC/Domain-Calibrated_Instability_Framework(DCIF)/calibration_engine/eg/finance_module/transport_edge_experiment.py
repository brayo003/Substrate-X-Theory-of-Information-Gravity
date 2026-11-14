"""
transport_edge_experiment.py
============================
Purposeful search for a transport-derived trading edge.

DIAGNOSIS (from prior evaluation + audit):
  - All 28 existing strategies lose because ATR(5-min EURUSD) ~= 6pip while
    RT cost = 5pip => breakeven WR = 58.8% (never achieved; actual ~38%)
  - Q = 100*|grad_ln_s|^2 - 1 is a monotone transform of |grad_ln_s|: redundant
  - tr_s_transport (PDE-smoothed composite) DOES have distinct information from Q
  - The composite s contains momentum_20min + momentum_1hr (price-directional)

STRATEGIES TESTED (4 candidates, distinct economic rationales):
  A. Transport Regime Trend: s_transport rising >= N bars + price momentum direction
     Wider stops: 2.5xATR stop, 4.0xATR target, 48-bar hold
  B. Wide-Stop EMA Cross: EMA9/21 crossover, no session filter, 3.0xATR/5.0xATR
     Tests whether the entry signal has value given correct sizing
  C. s_transport Divergence: composite_norm > s_transport + threshold (shock not absorbed)
     2.0xATR stop, 3.5xATR target
  D. Vol Breakout Baseline: rv5 spike + directional return, NO transport
     Baseline to determine whether transport adds value

WALK-FORWARD DESIGN (different from prior eval to avoid data-mining):
  IS  : 2023-01 to 2024-06  (parameter confirmation only)
  WF1 : 2024-07 to 2024-12
  WF2 : 2025-01 to 2025-10

SUCCESS CRITERIA (pre-defined):
  WF combined PF > 1.10, expectancy > +2pip, CI_lo > -3pip,
  PF_2x > 1.0, N >= 50, min fold PF >= 0.60
"""

import warnings, json
from pathlib import Path
from typing import Dict, List

import numpy as np
import pandas as pd

warnings.filterwarnings("ignore")

HERE      = Path(__file__).resolve().parent
CACHE_DIR = HERE / "cache"
OUT_DIR   = HERE / "results" / "transport_edge_experiment"
OUT_DIR.mkdir(parents=True, exist_ok=True)

COMMISSION = 0.00020
SLIPPAGE   = 0.00005
TOTAL_RT   = (COMMISSION + SLIPPAGE) * 2   # 0.00050 = 5pip RT

IS_START  = "2023-01"; IS_END  = "2024-06"
WF1_START = "2024-07"; WF1_END = "2024-12"
WF2_START = "2025-01"; WF2_END = "2025-10"

# Strategy A
A_RISING_BARS = 8;   A_STOP = 2.5; A_TGT = 4.0; A_HOLD = 48
# Strategy B
B_STOP = 3.0;        B_TGT  = 5.0; B_HOLD = 36
# Strategy C
C_DIV_THRESH = 0.04; C_STOP = 2.0; C_TGT  = 3.5; C_HOLD = 36
# Strategy D
D_VOL_MULT = 1.5;    D_VOL_WIN = 100; D_DIR_FRAC = 0.3
D_STOP = 2.0;        D_TGT  = 3.5; D_HOLD = 36


# ── Data loading ───────────────────────────────────────────────────────────

def load_cache() -> pd.DataFrame:
    files = sorted(CACHE_DIR.glob("ohlc_transport_*.parquet"))
    if not files:
        raise FileNotFoundError(f"No cache files in {CACHE_DIR}")
    frames = [pd.read_parquet(f) for f in files]
    full = pd.concat(frames).sort_index()
    return full[~full.index.duplicated(keep='first')]


# ── Feature engineering (all causal) ─────────────────────────────────────

def add_features(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()

    # Consecutive bars s_transport has been rising (reset on any down bar)
    st   = out['tr_s_transport']
    diff = st.diff()
    rc_arr = np.zeros(len(out), dtype=np.int32)
    for i in range(1, len(out)):
        rc_arr[i] = rc_arr[i-1] + 1 if diff.iloc[i] > 0 else 0
    out['st_rising_count'] = rc_arr

    # s_transport slope direction
    out['st_slope'] = diff.apply(lambda x: 1 if x > 0 else (-1 if x < 0 else 0))

    # Price momentum direction (1hr = 12 bars)
    mom = out['close'].pct_change(12)
    out['price_dir_1h'] = mom.apply(lambda x: 1 if x > 0 else (-1 if x < 0 else 0))

    # s_transport divergence from composite_norm
    out['st_diverge'] = out['composite_norm'] - out['tr_s_transport']
    out['comp_slope'] = out['composite_norm'].diff().apply(
        lambda x: 1 if x > 0 else (-1 if x < 0 else 0))

    # Volatility spike
    out['rv5_median'] = out['realized_vol_5'].rolling(D_VOL_WIN, min_periods=20).median()
    out['rv5_spike']  = out['realized_vol_5'] > (D_VOL_MULT * out['rv5_median'])

    # EMA crossover for Strategy B
    fast = out['close'].ewm(span=9,  adjust=False).mean()
    slow = out['close'].ewm(span=21, adjust=False).mean()
    trend = (fast > slow).astype(int) - (fast < slow).astype(int)
    out['ema_cross_up']   = (trend == 1)  & (trend.shift(1) != 1)
    out['ema_cross_down'] = (trend == -1) & (trend.shift(1) != -1)

    return out


# ── Signal generators ──────────────────────────────────────────────────────

def signal_A(df: pd.DataFrame) -> pd.Series:
    """Transport Regime Trend: s_transport rising >= A_RISING_BARS + price direction."""
    sig  = pd.Series(0, index=df.index, dtype=np.int8)
    just_entered = (df['st_rising_count'] >= A_RISING_BARS) & \
                   (df['st_rising_count'].shift(1) < A_RISING_BARS)
    sig[just_entered & (df['price_dir_1h'] == 1)]  =  1
    sig[just_entered & (df['price_dir_1h'] == -1)] = -1
    return sig


def signal_B(df: pd.DataFrame) -> pd.Series:
    """Wide-Stop EMA9/21 crossover, all hours."""
    sig = pd.Series(0, index=df.index, dtype=np.int8)
    sig[df['ema_cross_up'].fillna(False)]   =  1
    sig[df['ema_cross_down'].fillna(False)] = -1
    return sig


def signal_C(df: pd.DataFrame) -> pd.Series:
    """s_transport Divergence: composite_norm diverges above/below s_transport."""
    sig  = pd.Series(0, index=df.index, dtype=np.int8)
    div  = df['st_diverge']
    cslp = df['comp_slope']
    cross_up   = (div >  C_DIV_THRESH) & (div.shift(1) <=  C_DIV_THRESH)
    cross_down = (div < -C_DIV_THRESH) & (div.shift(1) >= -C_DIV_THRESH)
    sig[cross_up   & (cslp == 1)]  =  1
    sig[cross_down & (cslp == -1)] = -1
    return sig


def signal_D(df: pd.DataFrame) -> pd.Series:
    """Vol Breakout Baseline: rv5 spikes above median threshold + directional bar."""
    sig   = pd.Series(0, index=df.index, dtype=np.int8)
    spike = df['rv5_spike'].fillna(False)
    new_spike = spike & ~spike.shift(1).fillna(False)
    atr   = df['atr_14']
    ret   = df['returns']
    direc = ret.abs() > D_DIR_FRAC * atr
    sig[new_spike & direc & (ret > 0)] =  1
    sig[new_spike & direc & (ret < 0)] = -1
    return sig


# ── Bar-by-bar trade simulator ─────────────────────────────────────────────

def simulate(df, signal, stop_atr, target_atr, hold_bars,
             label, period, exit_signal=None):
    records = []
    in_trade = False
    direction = entry_price = stop = tgt = entry_atr = 0.0
    entry_bar = -1

    sig_arr   = signal.values.astype(np.int8)
    open_arr  = df['open'].values
    close_arr = df['close'].values
    high_arr  = df['high'].values
    low_arr   = df['low'].values
    atr_arr   = df['atr_14'].values
    ts_arr    = df.index
    n         = len(df)
    exit_arr  = exit_signal.values.astype(bool) if exit_signal is not None \
                else np.zeros(n, dtype=bool)

    for i in range(1, n):
        if in_trade:
            hi, lo, cl = high_arr[i], low_arr[i], close_arr[i]
            held = i - entry_bar
            if exit_arr[i]:
                ep, er = cl, "signal_exit"
            elif direction == 1 and lo <= stop:
                ep, er = stop, "stop"
            elif direction == -1 and hi >= stop:
                ep, er = stop, "stop"
            elif direction == 1 and hi >= tgt:
                ep, er = tgt, "target"
            elif direction == -1 and lo <= tgt:
                ep, er = tgt, "target"
            elif held >= hold_bars:
                ep, er = cl, "time"
            else:
                continue
            raw = direction * (ep - entry_price)
            net = raw - TOTAL_RT
            records.append(dict(strategy=label, period=period,
                                entry_time=ts_arr[entry_bar], exit_time=ts_arr[i],
                                direction=direction, entry_price=entry_price,
                                exit_price=ep, exit_reason=er, bars_held=held,
                                entry_atr_pip=entry_atr*10000,
                                raw_pnl=raw, net_pnl=net, cost=TOTAL_RT))
            in_trade = False

        if not in_trade and sig_arr[i-1] != 0:
            direction   = int(sig_arr[i-1])
            entry_price = float(open_arr[i])
            entry_bar   = i
            entry_atr   = max(float(atr_arr[i]), 1e-5)
            stop = entry_price - direction * stop_atr   * entry_atr
            tgt  = entry_price + direction * target_atr * entry_atr
            in_trade = True

    if in_trade:
        cl  = close_arr[-1]; raw = direction*(cl - entry_price); net = raw - TOTAL_RT
        records.append(dict(strategy=label, period=period,
                            entry_time=ts_arr[entry_bar], exit_time=ts_arr[-1],
                            direction=direction, entry_price=entry_price,
                            exit_price=cl, exit_reason='end_of_data',
                            bars_held=n-entry_bar, entry_atr_pip=entry_atr*10000,
                            raw_pnl=raw, net_pnl=net, cost=TOTAL_RT))
    return pd.DataFrame(records)


# ── Metrics ────────────────────────────────────────────────────────────────

def calc_metrics(t: pd.DataFrame, label: str, period: str) -> Dict:
    if t is None or len(t) == 0:
        return dict(strategy=label, period=period, n_trades=0,
                    win_rate=float('nan'), profit_factor=float('nan'),
                    expectancy_pips=float('nan'), total_net_pips=float('nan'),
                    max_drawdown_pips=float('nan'), pf_2x_cost=float('nan'),
                    avg_win_pip=float('nan'), avg_loss_pip=float('nan'),
                    ci_lo=float('nan'), ci_hi=float('nan'))
    wins = t[t.net_pnl > 0];   losses = t[t.net_pnl <= 0]
    gw   = wins.net_pnl.sum(); gl = losses.net_pnl.sum()
    pf   = (gw/-gl) if gl < 0 else float('inf')
    exp  = t.net_pnl.mean()
    eq   = t.net_pnl.cumsum()
    maxdd = (eq.cummax() - eq).max()
    t2   = t.net_pnl - TOTAL_RT
    pf2  = (t2[t2>0].sum() / -t2[t2<=0].sum()) if t2[t2<=0].sum() < 0 else float('inf')
    rng  = np.random.default_rng(42)
    if len(t) >= 5:
        boots = [rng.choice(t.net_pnl.values, size=len(t), replace=True).mean()
                 for _ in range(2000)]
        ci_lo = float(np.percentile(boots, 2.5)) * 10000
        ci_hi = float(np.percentile(boots, 97.5)) * 10000
    else:
        ci_lo = ci_hi = float('nan')
    return dict(strategy=label, period=period, n_trades=len(t),
                win_rate=round(len(wins)/len(t),3),
                profit_factor=round(pf,3),
                expectancy_pips=round(exp*10000,2),
                total_net_pips=round(t.net_pnl.sum()*10000,1),
                max_drawdown_pips=round(maxdd*10000,1),
                pf_2x_cost=round(pf2,3),
                avg_win_pip=round(wins.net_pnl.mean()*10000,1) if len(wins) else float('nan'),
                avg_loss_pip=round(losses.net_pnl.mean()*10000,1) if len(losses) else float('nan'),
                ci_lo=round(ci_lo,2), ci_hi=round(ci_hi,2))


# ── WF combined check ──────────────────────────────────────────────────────

def check_criteria(label: str, tlog: pd.DataFrame) -> Dict:
    if tlog is None or len(tlog) == 0:
        return dict(label=label, n=0, pf=0, pf2=0, exp=0,
                    ci_lo=float('nan'), ci_hi=float('nan'),
                    min_fold_pf=0, passed=False)
    n   = len(tlog)
    pnl = tlog['net_pnl']
    wins = pnl[pnl>0]; losses = pnl[pnl<=0]
    pf   = (wins.sum()/-losses.sum()) if losses.sum()<0 else float('inf')
    exp  = pnl.mean()*10000
    pnl2 = pnl - TOTAL_RT
    pf2  = (pnl2[pnl2>0].sum()/-pnl2[pnl2<=0].sum()) if pnl2[pnl2<=0].sum()<0 else float('inf')
    rng  = np.random.default_rng(42)
    if n >= 5:
        boots = [rng.choice(pnl.values, size=n, replace=True).mean() for _ in range(2000)]
        ci_lo = float(np.percentile(boots,2.5))*10000
        ci_hi = float(np.percentile(boots,97.5))*10000
    else:
        ci_lo = ci_hi = float('nan')
    fold_pfs = []
    for fold in ['WF1','WF2']:
        ft = tlog[tlog['period']==fold]
        if len(ft):
            fw = ft[ft.net_pnl>0].net_pnl.sum(); fl = ft[ft.net_pnl<=0].net_pnl.sum()
            fold_pfs.append((fw/-fl) if fl<0 else float('inf'))
    min_fold = min(fold_pfs) if fold_pfs else 0.0
    c1=pf>1.10; c2=exp>2.0; c3=(not(ci_lo!=ci_lo) and ci_lo>-3.0)
    c4=pf2>1.0; c5=n>=50;   c6=min_fold>=0.60
    return dict(label=label, n=n, pf=round(pf,3), pf2=round(pf2,3),
                exp=round(exp,2), ci_lo=round(ci_lo,2) if ci_lo==ci_lo else float('nan'),
                ci_hi=round(ci_hi,2) if ci_hi==ci_hi else float('nan'),
                min_fold_pf=round(min_fold,3), passed=all([c1,c2,c3,c4,c5,c6]),
                c1=c1,c2=c2,c3=c3,c4=c4,c5=c5,c6=c6)


# ── Main ───────────────────────────────────────────────────────────────────

def main():
    print("=" * 70)
    print("TRANSPORT EDGE EXPERIMENT")
    print("=" * 70)

    print("\nLoading cache...")
    full = load_cache()
    print(f"  {len(full):,} bars  ({full.index[0].date()} – {full.index[-1].date()})")

    print("Engineering features...")
    full = add_features(full)

    splits = {"IS":  full[IS_START:IS_END],
              "WF1": full[WF1_START:WF1_END],
              "WF2": full[WF2_START:WF2_END]}
    for nm, sl in splits.items():
        print(f"  {nm}: {len(sl):,} bars  ({sl.index[0].date()} – {sl.index[-1].date()})")

    # IS parameter confirmation
    is_df = splits["IS"]
    rc_pos = is_df['st_rising_count'][is_df['st_rising_count'] > 0]
    div_pos = is_df['st_diverge'][is_df['st_diverge'] > 0]
    is_params = {
        "IS_rising_bars_p50": float(rc_pos.median()),
        "IS_rising_bars_p70": float(rc_pos.quantile(0.70)),
        "A_RISING_BARS_used": A_RISING_BARS,
        "IS_diverge_p70":     float(div_pos.quantile(0.70)) if len(div_pos)>10 else C_DIV_THRESH,
        "C_DIV_THRESH_used":  C_DIV_THRESH,
        "IS_vol_spike_rate":  float(is_df['rv5_spike'].mean()),
        "TOTAL_RT_pip":       TOTAL_RT*10000,
    }
    print("\nIS parameters:")
    for k, v in is_params.items():
        print(f"  {k}: {v:.4f}" if isinstance(v, float) else f"  {k}: {v}")
    with open(OUT_DIR / "thresholds_is.json", "w") as f:
        json.dump(is_params, f, indent=2)

    # Signals (computed once over full history, then sliced — causal safe)
    print("\nGenerating signals...")
    sA = signal_A(full)
    sB = signal_B(full)
    sC = signal_C(full)
    sD = signal_D(full)
    # Dynamic exit signals
    exit_A = (full['st_slope'] == -1)  # s_transport turns down
    exit_C = full['st_diverge'].abs() < C_DIV_THRESH / 2  # divergence closes
    for s, nm in [(sA,'A'),(sB,'B'),(sC,'C'),(sD,'D')]:
        print(f"  Strategy {nm}: {(s!=0).sum():,} signals")

    # Simulation
    cfg = [
        ("A_Transport_Trend",   sA, A_STOP, A_TGT, A_HOLD, exit_A),
        ("B_Wide_EMA_Cross",    sB, B_STOP, B_TGT, B_HOLD, None),
        ("C_ST_Divergence",     sC, C_STOP, C_TGT, C_HOLD, exit_C),
        ("D_Vol_Breakout_Base", sD, D_STOP, D_TGT, D_HOLD, None),
    ]
    all_trades: List[pd.DataFrame] = []
    all_metrics: List[Dict]        = []

    print("\nRunning simulations...")
    for pname, sl in splits.items():
        for label, sig, sa, ta, hb, exs in cfg:
            sig_sl = sig[sl.index]
            ex_sl  = exs[sl.index] if exs is not None else None
            t = simulate(sl, sig_sl, sa, ta, hb, label, pname, ex_sl)
            m = calc_metrics(t, label, pname)
            all_trades.append(t)
            all_metrics.append(m)
            pf_s = f"{m['profit_factor']:.3f}" if m['profit_factor']==m['profit_factor'] else "n/a"
            exp_s = f"{m['expectancy_pips']:+.2f}" if m['expectancy_pips']==m['expectancy_pips'] else "n/a"
            print(f"  {pname:4s} | {label:25s} | N={m['n_trades']:5d}  PF={pf_s:>6}  exp={exp_s}pip")

    stats_df = pd.DataFrame(all_metrics)
    stats_df.to_csv(OUT_DIR / "signal_stats.csv", index=False)

    nonempty = [t for t in all_trades if not t.empty]
    if nonempty:
        trades_df = pd.concat(nonempty, ignore_index=True)
        trades_df.to_csv(OUT_DIR / "trade_log_all.csv", index=False)
        print(f"\n  Saved {len(trades_df):,} trades")
    else:
        trades_df = pd.DataFrame()

    # WF combined
    print("\n" + "=" * 70)
    print("WALK-FORWARD COMBINED (WF1 + WF2)")
    print("=" * 70)
    print(f"{'Strategy':<28} {'N':>5} {'PF':>6} {'PF2x':>6} {'exp':>7} "
          f"{'CI_lo':>7} {'CI_hi':>7} {'mFPF':>6}  CRITERIA")

    results_wf = {}
    if not trades_df.empty:
        wf = trades_df[trades_df['period'].isin(['WF1','WF2'])]
        for label, *_ in cfg:
            r = check_criteria(label, wf[wf['strategy']==label])
            results_wf[label] = r
            crit = f"[{'Y' if r['c1'] else 'N'}{'Y' if r['c2'] else 'N'}"  \
                   f"{'Y' if r['c3'] else 'N'}{'Y' if r['c4'] else 'N'}"   \
                   f"{'Y' if r['c5'] else 'N'}{'Y' if r['c6'] else 'N'}]"
            flag = "PASS" if r['passed'] else "FAIL"
            ci_lo_s = f"{r['ci_lo']:+.1f}" if r['ci_lo']==r['ci_lo'] else "  nan"
            ci_hi_s = f"{r['ci_hi']:+.1f}" if r['ci_hi']==r['ci_hi'] else "  nan"
            print(f"  {label:<28} {r['n']:>5}  {r['pf']:>5.3f}  {r['pf2']:>5.3f}  "
                  f"{r['exp']:>+6.2f}  {ci_lo_s:>6}  {ci_hi_s:>6}  {r['min_fold_pf']:>5.3f}"
                  f"  {crit} {flag}")

    return stats_df, trades_df, results_wf


if __name__ == "__main__":
    stats_df, trades_df, results_wf = main()

    # Build a concise report
    lines = [
        "# Transport Edge Experiment — Evidence Report",
        f"Generated: {pd.Timestamp.now(tz='UTC').strftime('%Y-%m-%d %H:%M UTC')}",
        f"IS: {IS_START}–{IS_END}  |  WF1: {WF1_START}–{WF1_END}  |  WF2: {WF2_START}–{WF2_END}",
        f"Cost: {TOTAL_RT*10000:.1f}pip RT",
        "",
        "## Success criteria (pre-defined)",
        "WF combined: PF>1.10, exp>+2pip, CI_lo>-3pip, PF_2x>1.0, N>=50, min_fold_PF>=0.60",
        "",
        "## IS Performance",
        stats_df[stats_df.period=='IS'].to_string(index=False),
        "",
        "## WF1 Performance",
        stats_df[stats_df.period=='WF1'].to_string(index=False),
        "",
        "## WF2 Performance",
        stats_df[stats_df.period=='WF2'].to_string(index=False),
        "",
        "## WF Combined Decision",
    ]
    for label, r in results_wf.items():
        fail_reasons = []
        if not r['c1']: fail_reasons.append(f"PF={r['pf']:.3f}<1.10")
        if not r['c2']: fail_reasons.append(f"exp={r['exp']:+.2f}<+2pip")
        if not r['c3']: fail_reasons.append(f"CI_lo={r['ci_lo']:.1f}<-3pip")
        if not r['c4']: fail_reasons.append(f"PF_2x={r['pf2']:.3f}<1.0")
        if not r['c5']: fail_reasons.append(f"N={r['n']}<50")
        if not r['c6']: fail_reasons.append(f"min_fold_PF={r['min_fold_pf']:.3f}<0.60")
        verdict = "PASS" if r['passed'] else "FAIL: " + "; ".join(fail_reasons)
        lines.append(f"  {label}: {verdict}")

    lines += [
        "",
        "## What remains to investigate",
        "- Higher ATR/cost ratio instrument (Gold, GBP/USD, NAS100 at 5-min)",
        "- Whether transport regime signal improves entry on daily bars (larger ATR)",
        "- C_ST_Divergence: conceptually sound but threshold may need IS recalibration",
    ]

    rp = OUT_DIR / "EDGE_REPORT.md"
    rp.write_text("\n".join(lines))
    print(f"\nReport written: {rp}")
    print(f"Stats: {OUT_DIR}/signal_stats.csv")
    print(f"Trades: {OUT_DIR}/trade_log_all.csv")
