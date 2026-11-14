"""
transport_strategy_integrator.py — Maps Q transport regimes to strategy execution.

CRITICAL CONSTRAINTS (enforced by design):
  - Q NEVER generates buy/sell signals.
  - Q ONLY determines:
      (a) whether to trade (gate)
      (b) which strategy family is active
      (c) risk parameters (position size multiplier, stop multiplier)
      (d) position sizing policy
      (e) stop policy

The actual trade signal always comes from strategy_library strategies.
Q is a meta-layer above the signal layer.

Regime → policy mapping (inferred from data, defaults set conservatively):
  Deep_Incoherent  → Mean Reversion preferred; reduced size (0.5); wider stop
  Mod_Incoherent   → Mean Reversion / Scalp; normal size (1.0); normal stop
  Transition       → NO TRADE (regime unstable)
  Weak_Coherent    → Momentum / Breakout; normal size (1.0); normal stop
  Strong_Coherent  → Trend; increased size (1.5); trailing stop
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Optional

from execution_simulator import (
    REGIMES_5, classify_q_regimes,
    simulate_strategy, HOLD_BARS, ATR_STOP, ATR_TARGET
)
from strategy_library import get_all_strategies, get_families


# ── Default regime gate: which regimes allow trading ──────────────────────
# Transition regime is blocked by default (can be overridden).
DEFAULT_TRADE_GATE = {
    'Deep_Incoherent' : True,
    'Mod_Incoherent'  : True,
    'Transition'      : False,   # NO TRADE in transition zone
    'Weak_Coherent'   : True,
    'Strong_Coherent' : True,
}

# ── Default position size multipliers per regime ───────────────────────────
DEFAULT_SIZE_POLICY = {
    'Deep_Incoherent' : 0.5,    # reduced; high incoherence = high risk
    'Mod_Incoherent'  : 1.0,
    'Transition'      : 0.0,    # blocked
    'Weak_Coherent'   : 1.0,
    'Strong_Coherent' : 1.5,    # increased; strong coherence = clear trend
}

# ── Default stop multiplier per regime (relative to ATR_STOP) ─────────────
DEFAULT_STOP_POLICY = {
    'Deep_Incoherent' : 1.25,   # wider stop in choppy regime
    'Mod_Incoherent'  : 1.0,
    'Transition'      : 1.0,
    'Weak_Coherent'   : 1.0,
    'Strong_Coherent' : 0.85,   # tighter stop in trending regime
}

# ── Preferred families per regime (inferred from theory; validated empirically)
REGIME_PREFERRED_FAMILIES = {
    'Deep_Incoherent' : ['MeanReversion', 'Scalping'],
    'Mod_Incoherent'  : ['MeanReversion', 'Scalping'],
    'Transition'      : [],          # no preferred family; no trade
    'Weak_Coherent'   : ['Momentum', 'Breakout'],
    'Strong_Coherent' : ['Trend', 'Breakout'],
}


def get_regime_at_index(q_regimes: np.ndarray, idx: int) -> str:
    """Safe regime lookup."""
    if idx < 0 or idx >= len(q_regimes):
        return 'Mod_Incoherent'
    return str(q_regimes[idx])


def apply_regime_gate(
    df: pd.DataFrame,
    signals: pd.Series,
    q_regimes: np.ndarray,
    trade_gate: Dict[str, bool] = None,
) -> pd.Series:
    """
    Filter signal series by regime gate.
    Signals in blocked regimes are zeroed out.
    Q does NOT change the signal direction — only zeros out disallowed entries.
    """
    if trade_gate is None:
        trade_gate = DEFAULT_TRADE_GATE

    gated = signals.copy()
    for i, (ts, sig) in enumerate(signals.items()):
        if sig == 0:
            continue
        regime = get_regime_at_index(q_regimes, i)
        if not trade_gate.get(regime, True):
            gated.iloc[i] = 0

    return gated


def simulate_with_regime_gate(
    df: pd.DataFrame,
    strategy_name: str,
    family: str,
    q_regimes: np.ndarray,
    trade_gate: Dict[str, bool] = None,
    size_policy: Dict[str, float] = None,
) -> pd.DataFrame:
    """
    Simulate a strategy with Q-based regime gating applied.
    Strategy signals are generated first (Q-blind), then gated by regime.
    Position size multiplier from size_policy is recorded but not
    applied to returns (sizing impact reported separately).
    """
    from strategy_library import get_all_strategies
    registry = get_all_strategies()
    if strategy_name not in registry:
        return pd.DataFrame()

    fn      = registry[strategy_name]['fn']
    signals = fn(df)

    if trade_gate is None:
        trade_gate = DEFAULT_TRADE_GATE
    gated = apply_regime_gate(df, signals, q_regimes, trade_gate)

    trades = simulate_strategy(df, gated, strategy_name, family, q_regimes)

    # Annotate with size multiplier (for later sizing analysis)
    if size_policy and len(trades) > 0:
        trades['size_multiplier'] = trades['entry_regime'].map(
            lambda r: size_policy.get(r, 1.0)
        )
        trades['sized_net_ret'] = trades['net_ret'] * trades['size_multiplier']
    else:
        if len(trades) > 0:
            trades['size_multiplier'] = 1.0
            trades['sized_net_ret']   = trades['net_ret']

    return trades


def build_gated_trade_log(
    df: pd.DataFrame,
    trade_gate: Dict[str, bool] = None,
    size_policy: Dict[str, float] = None,
) -> pd.DataFrame:
    """
    Run all strategies with regime gating applied.
    Returns combined trade log with size_multiplier column.
    """
    registry  = get_all_strategies()
    Q_arr     = df['tr_Q'].values
    q_regimes = classify_q_regimes(Q_arr)

    if trade_gate is None:
        trade_gate = DEFAULT_TRADE_GATE
    if size_policy is None:
        size_policy = DEFAULT_SIZE_POLICY

    all_trades = []
    for name, meta in registry.items():
        family = meta['family']
        trades = simulate_with_regime_gate(
            df, name, family, q_regimes, trade_gate, size_policy
        )
        if len(trades) > 0:
            all_trades.append(trades)

    return pd.concat(all_trades, ignore_index=True) if all_trades else pd.DataFrame()


def compute_sizing_comparison(
    ungated_trades: pd.DataFrame,
    gated_trades: pd.DataFrame,
) -> pd.DataFrame:
    """
    Compare baseline (ungated, equal-weight) vs Q-gated returns.

    Returns DataFrame with one row per strategy showing:
      strategy, baseline_pf, gated_pf, baseline_sharpe, gated_sharpe,
      baseline_dd, gated_dd, trade_count_diff
    """
    from strategy_statistics import compute_metrics

    rows = []
    strategies = sorted(ungated_trades['strategy'].unique())

    for strat in strategies:
        ug = ungated_trades[ungated_trades['strategy'] == strat]['net_ret'].values
        gt_df = gated_trades[gated_trades['strategy'] == strat] if len(gated_trades) > 0 else pd.DataFrame()
        gt = gt_df['net_ret'].values if len(gt_df) > 0 else np.array([])

        m_ug = compute_metrics(ug)
        m_gt = compute_metrics(gt)

        rows.append({
            'strategy'       : strat,
            'baseline_n'     : m_ug['trade_count'],
            'gated_n'        : m_gt['trade_count'],
            'baseline_pf'    : m_ug['profit_factor'],
            'gated_pf'       : m_gt['profit_factor'],
            'baseline_sharpe': m_ug['sharpe'],
            'gated_sharpe'   : m_gt['sharpe'],
            'baseline_dd'    : m_ug['max_drawdown'],
            'gated_dd'       : m_gt['max_drawdown'],
            'pf_improvement' : m_gt['profit_factor'] - m_ug['profit_factor'],
            'dd_reduction'   : m_ug['max_drawdown'] - m_gt['max_drawdown'],
        })

    return pd.DataFrame(rows)
