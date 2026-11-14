"""
v2_phase4.py  —  Phase IV: Strategy Suitability Matrix
Four strategies × two regimes, measuring MFE/MAE and full performance split.
"""
import numpy as np
import pandas as pd
from typing import Dict, List


HOLD_BARS = 20
ATR_STOP  = 1.0
PIP_COST  = 0.00020   # EUR/USD 2-pip spread


# ─────────────────────────────────────────────────────────────────────────────
# Strategy signal generators
# ─────────────────────────────────────────────────────────────────────────────

def _ema_trend_signals(df: pd.DataFrame) -> pd.Series:
    """EMA(9) × EMA(21) crossover."""
    fast = df['close'].ewm(span=9,  adjust=False).mean()
    slow = df['close'].ewm(span=21, adjust=False).mean()
    diff = fast - slow
    sig  = pd.Series(0, index=df.index, dtype=np.int8)
    sig[(diff > 0) & (diff.shift(1) <= 0)] =  1
    sig[(diff < 0) & (diff.shift(1) >= 0)] = -1
    return sig


def _mean_reversion_signals(df: pd.DataFrame) -> pd.Series:
    """Price > 2σ above 20-bar MA → short; < 2σ below → long."""
    ma   = df['close'].rolling(20).mean()
    std  = df['close'].rolling(20).std()
    upper = ma + 2 * std
    lower = ma - 2 * std
    sig  = pd.Series(0, index=df.index, dtype=np.int8)
    sig[df['close'] > upper] = -1   # short (mean revert down)
    sig[df['close'] < lower] =  1   # long  (mean revert up)
    # Only fire on first entry (edge detection)
    sig = sig.diff().fillna(0).clip(-1, 1).astype(np.int8)
    return sig


def _breakout_signals(df: pd.DataFrame) -> pd.Series:
    """20-bar Donchian channel breakout."""
    high20 = df['high'].rolling(20).max().shift(1)
    low20  = df['low'].rolling(20).min().shift(1)
    sig    = pd.Series(0, index=df.index, dtype=np.int8)
    sig[df['close'] > high20] =  1
    sig[df['close'] < low20]  = -1
    sig = sig.diff().fillna(0).clip(-1, 1).astype(np.int8)
    return sig


def _vol_compression_signals(df: pd.DataFrame) -> pd.Series:
    """
    Volatility compression breakout:
    Enter when Bollinger Width is in bottom 20th pct AND price makes a 5-bar high/low.
    """
    ma     = df['close'].rolling(20).mean()
    bw     = 2 * df['close'].rolling(20).std() / (ma + 1e-10)
    low_bw = bw < bw.rolling(100).quantile(0.20)
    h5     = df['high'].rolling(5).max().shift(1)
    l5     = df['low'].rolling(5).min().shift(1)
    sig    = pd.Series(0, index=df.index, dtype=np.int8)
    sig[(df['close'] > h5) & low_bw] =  1
    sig[(df['close'] < l5) & low_bw] = -1
    sig = sig.diff().fillna(0).clip(-1, 1).astype(np.int8)
    return sig


STRATEGIES = {
    'EMA_Trend'    : _ema_trend_signals,
    'MeanReversion': _mean_reversion_signals,
    'Breakout'     : _breakout_signals,
    'VolCompBreak' : _vol_compression_signals,
}


# ─────────────────────────────────────────────────────────────────────────────
# Trade runner
# ─────────────────────────────────────────────────────────────────────────────

def _run_trades(df: pd.DataFrame, signals: pd.Series,
                strategy_name: str) -> pd.DataFrame:
    """Execute trades and record MFE, MAE, Q at entry/exit."""
    close  = df['close'].values
    high   = df['high'].values
    low    = df['low'].values
    atr    = df['atr_14'].values
    Q      = df['tr_Q'].values
    regime = df['tr_regime_str'].values
    n      = len(df)

    trades = []
    for i, (ts, sig) in enumerate(signals.items()):
        if sig == 0:
            continue
        direction   = int(sig)
        entry_price = close[i]
        entry_atr   = float(atr[i]) if not np.isnan(atr[i]) else 0.0
        entry_Q     = float(Q[i])
        stop_dist   = ATR_STOP * entry_atr
        stop_price  = entry_price - direction * stop_dist

        exit_idx = min(i + HOLD_BARS, n - 1)
        stop_hit = False
        mfe = 0.0; mae = 0.0

        for j in range(i + 1, exit_idx + 1):
            p     = close[j]
            fav   = direction * (p - entry_price)
            adv   = direction * (entry_price - p)
            mfe   = max(mfe, fav)
            mae   = max(mae, adv)
            if direction == 1 and p <= stop_price:
                exit_idx = j; stop_hit = True; break
            elif direction == -1 and p >= stop_price:
                exit_idx = j; stop_hit = True; break

        exit_price = close[exit_idx]
        gross_ret  = direction * (exit_price - entry_price) / (entry_price + 1e-12)
        net_ret    = gross_ret - PIP_COST / entry_price

        trades.append({
            'strategy'    : strategy_name,
            'entry_time'  : ts,
            'exit_time'   : df.index[exit_idx],
            'direction'   : direction,
            'entry_price' : entry_price,
            'exit_price'  : exit_price,
            'gross_ret'   : gross_ret,
            'net_ret'     : net_ret,
            'duration'    : exit_idx - i,
            'stop_hit'    : stop_hit,
            'mfe'         : mfe / (entry_price + 1e-12),
            'mae'         : mae / (entry_price + 1e-12),
            'entry_Q'     : entry_Q,
            'exit_Q'      : float(Q[exit_idx]),
            'entry_regime': str(regime[i]) if not isinstance(regime[i], float) else 'UNKNOWN',
        })
    return pd.DataFrame(trades)


def _metrics(trades: pd.DataFrame) -> dict:
    if len(trades) == 0:
        return {'n': 0}
    r     = trades['net_ret'].values
    wins  = r[r > 0]; losses = r[r < 0]
    pf    = wins.sum() / (abs(losses.sum()) + 1e-12)
    sh    = r.mean() / (r.std() + 1e-12) * np.sqrt(len(r))
    exp   = r.mean()
    mfe   = trades['mfe'].mean()
    mae   = trades['mae'].mean()
    return {
        'n'            : len(r),
        'win_rate'     : float((r > 0).mean()),
        'avg_ret'      : float(r.mean()),
        'median_ret'   : float(np.median(r)),
        'profit_factor': float(pf),
        'sharpe'       : float(sh),
        'expectancy'   : float(exp),
        'avg_mfe'      : float(mfe),
        'avg_mae'      : float(mae),
        'mfe_mae_ratio': float(mfe / (mae + 1e-12)),
        'stop_rate'    : float(trades['stop_hit'].mean()),
    }


# ─────────────────────────────────────────────────────────────────────────────
# Phase IV master
# ─────────────────────────────────────────────────────────────────────────────

def phase4_strategy_regime_matrix(df: pd.DataFrame) -> dict:
    """
    Run all 4 strategies; split each trade log by Q regime; compute metrics.
    Returns:
      all_trades      pd.DataFrame  — combined trade log
      matrix          pd.DataFrame  — strategy × regime performance
      summary         dict
    """
    all_trades_list = []

    for name, gen_fn in STRATEGIES.items():
        signals = gen_fn(df)
        trades  = _run_trades(df, signals, name)
        if len(trades) > 0:
            all_trades_list.append(trades)

    if not all_trades_list:
        return {'all_trades': pd.DataFrame(), 'matrix': pd.DataFrame(), 'summary': {}}

    all_trades = pd.concat(all_trades_list, ignore_index=True)

    # ── Build matrix: strategy × {COHERENT, INCOHERENT, ALL} ──────────────
    matrix_rows = []
    for strat in STRATEGIES:
        strat_trades = all_trades[all_trades['strategy'] == strat]
        for regime in ['COHERENT', 'INCOHERENT', 'ALL']:
            if regime == 'ALL':
                sub = strat_trades
            else:
                sub = strat_trades[strat_trades['entry_regime'] == regime]
            m = _metrics(sub)
            m['strategy'] = strat
            m['regime']   = regime
            matrix_rows.append(m)

    matrix = pd.DataFrame(matrix_rows)

    # ── Summary: best/worst regime per strategy ────────────────────────────
    summary_rows = []
    for strat in STRATEGIES:
        sub = matrix[(matrix['strategy'] == strat) &
                     (matrix['regime'].isin(['COHERENT', 'INCOHERENT']))]
        if len(sub) < 2:
            continue
        coh_pf   = sub.loc[sub['regime'] == 'COHERENT',   'profit_factor'].values
        inc_pf   = sub.loc[sub['regime'] == 'INCOHERENT', 'profit_factor'].values
        coh_sh   = sub.loc[sub['regime'] == 'COHERENT',   'sharpe'].values
        inc_sh   = sub.loc[sub['regime'] == 'INCOHERENT', 'sharpe'].values
        coh_pf   = float(coh_pf[0]) if len(coh_pf) > 0 else np.nan
        inc_pf   = float(inc_pf[0]) if len(inc_pf) > 0 else np.nan
        coh_sh   = float(coh_sh[0]) if len(coh_sh) > 0 else np.nan
        inc_sh   = float(inc_sh[0]) if len(inc_sh) > 0 else np.nan
        best_reg = 'COHERENT' if coh_pf >= inc_pf else 'INCOHERENT'
        improve  = abs(coh_pf - inc_pf)
        summary_rows.append({
            'strategy'          : strat,
            'best_regime'       : best_reg,
            'coherent_pf'       : coh_pf,
            'incoherent_pf'     : inc_pf,
            'pf_difference'     : float(coh_pf - inc_pf),
            'coherent_sharpe'   : coh_sh,
            'incoherent_sharpe' : inc_sh,
            'sharpe_difference' : float(coh_sh - inc_sh),
        })

    summary = pd.DataFrame(summary_rows)
    return {'all_trades': all_trades, 'matrix': matrix, 'summary': summary}
