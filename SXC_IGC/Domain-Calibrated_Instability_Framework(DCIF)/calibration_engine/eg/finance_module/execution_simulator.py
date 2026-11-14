"""
execution_simulator.py — Uniform execution simulator for Phase 1 validation.

All 28 strategies execute under IDENTICAL conditions:
  - Commission: 2.0 pips one-way (spread + broker commission)
  - Slippage:   0.5 pip per side
  - Stop:       ATR_STOP × ATR(14)
  - Target:     ATR_TARGET × ATR(14)
  - Max hold:   HOLD_BARS bars (24 bars = 2 hours at 5-min bars)
  - Position:   1 unit (normalised; sizing handled separately)
  - No pyramiding, no partial exits

Each trade records:
  entry_time, exit_time, strategy, family, direction,
  entry_price, exit_price, gross_ret, net_ret,
  duration_bars, stop_hit, target_hit, timeout,
  mfe, mae, mfe_mae_ratio,
  entry_Q, exit_Q, entry_regime (5-level)

The 5-level Q regime classification used here (data-driven at runtime):
  Deep Incoherent  : Q <= Q5%
  Mod Incoherent   : Q5% < Q <= 0
  Transition       : Q == 0  (within ±ε)
  Weak Coherent    : 0 < Q < Q95%
  Strong Coherent  : Q >= Q95%
"""

import numpy as np
import pandas as pd
from typing import Dict, List

# ── Execution constants — DO NOT CHANGE PER STRATEGY ──────────────────────
COMMISSION_PER_SIDE = 0.00010   # 1 pip per side (2 pip total round-trip)
SLIPPAGE_PER_SIDE   = 0.00005   # 0.5 pip per side
TOTAL_COST_RT       = 2 * (COMMISSION_PER_SIDE + SLIPPAGE_PER_SIDE)  # per unit

HOLD_BARS  = 24     # 2 hours at 5-min bars
ATR_STOP   = 1.5    # stop loss multiplier
ATR_TARGET = 2.5    # take profit multiplier

# ── Q regime thresholds (computed from data in classify_q_regimes) ─────────
REGIMES_5 = [
    'Deep_Incoherent',
    'Mod_Incoherent',
    'Transition',
    'Weak_Coherent',
    'Strong_Coherent',
]


def classify_q_regimes(Q: np.ndarray) -> np.ndarray:
    """
    Classify Q values into 5 regimes using data-driven quantile thresholds.

    Boundaries (computed fresh from the full Q series):
      Q <= q05              → Deep_Incoherent
      q05 < Q <= 0          → Mod_Incoherent
      |Q| < 0.01            → Transition   (override; thin band around zero)
      0 < Q < q95           → Weak_Coherent
      Q >= q95              → Strong_Coherent
    """
    q05 = np.nanpercentile(Q, 5)
    q95 = np.nanpercentile(Q, 95)

    labels = np.empty(len(Q), dtype=object)
    for i, q in enumerate(Q):
        if np.isnan(q):
            labels[i] = 'Mod_Incoherent'
        elif abs(q) < 0.01:
            labels[i] = 'Transition'
        elif q <= q05:
            labels[i] = 'Deep_Incoherent'
        elif q < 0:
            labels[i] = 'Mod_Incoherent'
        elif q >= q95:
            labels[i] = 'Strong_Coherent'
        else:
            labels[i] = 'Weak_Coherent'
    return labels


def simulate_strategy(
    df: pd.DataFrame,
    signals: pd.Series,
    strategy_name: str,
    family: str,
    q_regimes: np.ndarray,
) -> pd.DataFrame:
    """
    Simulate one strategy under uniform execution assumptions.

    Parameters
    ----------
    df            : pipeline DataFrame (must have close, high, low, atr_14, tr_Q)
    signals       : Series of {-1, 0, +1} from strategy_library
    strategy_name : string identifier
    family        : strategy family name
    q_regimes     : pre-computed 5-level regime labels (same index as df)

    Returns
    -------
    DataFrame of individual trades with all fields.
    """
    close  = df['close'].values
    high   = df['high'].values
    low    = df['low'].values
    atr    = df['atr_14'].values
    Q_vals = df['tr_Q'].values
    n      = len(df)

    trades = []
    for i, (ts, sig) in enumerate(signals.items()):
        if sig == 0:
            continue
        direction   = int(sig)
        entry_price = close[i]
        atr_i       = float(atr[i]) if (i < n and not np.isnan(atr[i])) else 0.0
        if atr_i <= 0:
            continue

        stop_dist   = ATR_STOP   * atr_i
        target_dist = ATR_TARGET * atr_i
        stop_price   = entry_price - direction * stop_dist
        target_price = entry_price + direction * target_dist

        exit_idx   = min(i + HOLD_BARS, n - 1)
        stop_hit   = False
        target_hit = False
        mfe = 0.0
        mae = 0.0

        for j in range(i + 1, exit_idx + 1):
            h = high[j]
            l = low[j]
            p = close[j]
            fav = direction * (p - entry_price)
            adv = direction * (entry_price - p)
            mfe = max(mfe, fav)
            mae = max(mae, adv)

            # Check stop (worst case: low for long, high for short)
            if direction == 1:
                if l <= stop_price:
                    exit_idx  = j
                    stop_hit  = True
                    break
                if h >= target_price:
                    exit_idx   = j
                    target_hit = True
                    break
            else:
                if h >= stop_price:
                    exit_idx  = j
                    stop_hit  = True
                    break
                if l <= target_price:
                    exit_idx   = j
                    target_hit = True
                    break

        exit_price = close[exit_idx]
        gross_ret  = direction * (exit_price - entry_price) / (entry_price + 1e-12)
        # FIXED: TOTAL_COST_RT is already a fraction of notional, subtract directly.
        net_ret    = gross_ret - TOTAL_COST_RT

        trades.append({
            'strategy'     : strategy_name,
            'family'       : family,
            'entry_time'   : ts,
            'exit_time'    : df.index[exit_idx],
            'direction'    : direction,
            'entry_price'  : entry_price,
            'exit_price'   : exit_price,
            'gross_ret'    : gross_ret,
            'net_ret'      : net_ret,
            'duration_bars': exit_idx - i,
            'stop_hit'     : stop_hit,
            'target_hit'   : target_hit,
            'timeout'      : not stop_hit and not target_hit,
            'mfe'          : mfe / (entry_price + 1e-12),
            'mae'          : mae / (entry_price + 1e-12),
            'mfe_mae_ratio': mfe / (mae + 1e-12),
            'entry_Q'      : float(Q_vals[i]),
            'exit_Q'       : float(Q_vals[exit_idx]),
            'entry_regime' : str(q_regimes[i]),
        })

    return pd.DataFrame(trades) if trades else pd.DataFrame(columns=[
        'strategy','family','entry_time','exit_time','direction',
        'entry_price','exit_price','gross_ret','net_ret','duration_bars',
        'stop_hit','target_hit','timeout','mfe','mae','mfe_mae_ratio',
        'entry_Q','exit_Q','entry_regime'
    ])


def run_all_strategies(
    df: pd.DataFrame,
    strategy_registry: Dict,
) -> pd.DataFrame:
    """
    Run all strategies in the registry and collect trade logs.

    Parameters
    ----------
    df                : pipeline DataFrame
    strategy_registry : from strategy_library.get_all_strategies()

    Returns
    -------
    Combined DataFrame of all trades.
    """
    Q_arr     = df['tr_Q'].values
    q_regimes = classify_q_regimes(Q_arr)

    all_trades = []
    for name, meta in strategy_registry.items():
        fn     = meta['fn']
        family = meta['family']
        try:
            signals = fn(df)
            trades  = simulate_strategy(df, signals, name, family, q_regimes)
            if len(trades) > 0:
                all_trades.append(trades)
        except Exception as e:
            print(f"  WARNING: {name} failed: {e}")

    if not all_trades:
        return pd.DataFrame()
    combined = pd.concat(all_trades, ignore_index=True)
    return combined
