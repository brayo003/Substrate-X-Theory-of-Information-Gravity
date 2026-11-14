"""
historical_validation.py — Historical Strategy Validation with Q Filter.

Implements two strategies:
    Strategy A: EMA crossover (baseline, no transport filter)
    Strategy B: EMA crossover with Q > 0 filter (transport-augmented)

Both strategies use identical parameters. Strategy B adds only:
    - Trade only when Q > 0 (COHERENT regime)

This is an observational validation. The purpose is to measure whether
Q adds statistically useful information, NOT to maximize profitability.

Trade mechanism:
    Entry: EMA(9) crosses above EMA(21) → LONG
           EMA(9) crosses below EMA(21) → SHORT
    Exit:  Fixed 20-bar holding period OR stop-loss at 1×ATR
    Stop:  1×ATR from entry price
"""

import numpy as np
import pandas as pd
from typing import Tuple, List, Dict, Optional


# ─────────────────────────────────────────────────────────────────────────────
# EMA crossover signal generator
# ─────────────────────────────────────────────────────────────────────────────

EMA_FAST  = 9    # fast EMA period (bars)
EMA_SLOW  = 21   # slow EMA period (bars)
HOLD_BARS = 20   # fixed holding period
STOP_ATR  = 1.0  # stop-loss multiplier × ATR


def generate_ema_signals(df: pd.DataFrame) -> pd.Series:
    """
    Generate +1 (long entry) / -1 (short entry) / 0 (no signal) from
    EMA crossover on the close price.

    Entry on bar where fast EMA crosses slow EMA.
    """
    close      = df['close']
    ema_fast   = close.ewm(span=EMA_FAST, adjust=False).mean()
    ema_slow   = close.ewm(span=EMA_SLOW, adjust=False).mean()

    diff       = ema_fast - ema_slow
    prev_diff  = diff.shift(1)

    # Crossover: sign changes
    signal = pd.Series(0, index=df.index, dtype=np.int8)
    signal[(diff > 0) & (prev_diff <= 0)] = 1   # bullish cross → long
    signal[(diff < 0) & (prev_diff >= 0)] = -1  # bearish cross → short

    return signal


# ─────────────────────────────────────────────────────────────────────────────
# Trade log generator
# ─────────────────────────────────────────────────────────────────────────────

def run_strategy(
    df: pd.DataFrame,
    strategy_name: str,
    q_filter: bool = False,
    q_threshold: float = 0.0,
    hold_bars: int = HOLD_BARS,
    stop_atr_mult: float = STOP_ATR,
) -> pd.DataFrame:
    """
    Run a strategy and generate a trade log.

    Parameters
    ----------
    df             : transport-augmented DataFrame (from build_full_pipeline)
    strategy_name  : 'A' or 'B' (for labeling)
    q_filter       : if True, skip trades when Q <= q_threshold
    q_threshold    : Q filter threshold (default 0.0)
    hold_bars      : fixed exit after this many bars
    stop_atr_mult  : stop-loss as ATR multiple

    Returns
    -------
    trade_log : DataFrame with one row per trade
    """
    raw_signals = generate_ema_signals(df)

    close  = df['close'].values
    atr    = df['atr_14'].values
    Q_vals = df['tr_Q'].values
    regime = df['tr_regime_str'].values
    T_sys  = df['T_sys'].values if 'T_sys' in df.columns else np.zeros(len(df))
    dcii   = df['composite_norm'].values if 'composite_norm' in df.columns else np.zeros(len(df))
    index  = df.index
    n      = len(df)

    trades = []

    for i, (ts, sig) in enumerate(raw_signals.items()):
        if sig == 0:
            continue

        # Q filter (Strategy B only)
        if q_filter and Q_vals[i] <= q_threshold:
            continue

        direction  = int(sig)       # +1 = long, -1 = short
        entry_price = close[i]
        entry_atr   = float(atr[i]) if not np.isnan(atr[i]) else 0.0
        entry_Q     = float(Q_vals[i])
        entry_regime = str(regime[i]) if not isinstance(regime[i], float) else 'UNKNOWN'
        stop_distance = stop_atr_mult * entry_atr

        # Determine stop-loss price
        if direction == 1:
            stop_price = entry_price - stop_distance
        else:
            stop_price = entry_price + stop_distance

        # Forward scan for exit
        exit_idx     = min(i + hold_bars, n - 1)
        stop_hit     = False
        actual_exit  = exit_idx

        for j in range(i + 1, exit_idx + 1):
            p = close[j]
            if direction == 1 and p <= stop_price:
                actual_exit = j
                stop_hit    = True
                break
            elif direction == -1 and p >= stop_price:
                actual_exit = j
                stop_hit    = True
                break

        exit_price = close[actual_exit]
        duration   = actual_exit - i

        # Return calculation (in price units, then as fraction)
        gross_return = direction * (exit_price - entry_price) / (entry_price + 1e-12)

        # Cost: 2 pip spread approximation for EUR/USD
        pip_cost = 0.00020 / entry_price
        net_return = gross_return - pip_cost

        # Future realized volatility at entry
        rvol_5  = float(df['realized_vol_5'].iloc[i])  if not df['realized_vol_5'].isna().iloc[i]  else np.nan
        rvol_20 = float(df['realized_vol_20'].iloc[i]) if not df['realized_vol_20'].isna().iloc[i] else np.nan

        # Future returns at fixed horizons (irrespective of actual exit)
        ret_5b  = float(df['ret_5b'].iloc[i])  if 'ret_5b'  in df.columns and not df['ret_5b'].isna().iloc[i]  else np.nan
        ret_10b = float(df['ret_10b'].iloc[i]) if 'ret_10b' in df.columns and not df['ret_10b'].isna().iloc[i] else np.nan
        ret_20b = float(df['ret_20b'].iloc[i]) if 'ret_20b' in df.columns and not df['ret_20b'].isna().iloc[i] else np.nan
        ret_50b = float(df['ret_50b'].iloc[i]) if 'ret_50b' in df.columns and not df['ret_50b'].isna().iloc[i] else np.nan

        # Directional future returns (aligned with trade direction)
        dir_ret_5b  = direction * ret_5b  if not np.isnan(ret_5b)  else np.nan
        dir_ret_10b = direction * ret_10b if not np.isnan(ret_10b) else np.nan
        dir_ret_20b = direction * ret_20b if not np.isnan(ret_20b) else np.nan

        trades.append({
            'strategy'       : strategy_name,
            'entry_time'     : ts,
            'exit_time'      : index[actual_exit],
            'direction'      : direction,
            'entry_price'    : entry_price,
            'exit_price'     : exit_price,
            'gross_return'   : gross_return,
            'net_return'     : net_return,
            'duration_bars'  : duration,
            'stop_hit'       : stop_hit,
            'entry_Q'        : entry_Q,
            'entry_regime'   : entry_regime,
            'entry_T_sys'    : float(T_sys[i]),
            'entry_dcii'     : float(dcii[i]),
            'entry_atr'      : entry_atr,
            'rvol_5_at_entry': rvol_5,
            'rvol_20_at_entry': rvol_20,
            'ret_5b'         : ret_5b,
            'ret_10b'        : ret_10b,
            'ret_20b'        : ret_20b,
            'ret_50b'        : ret_50b,
            'dir_ret_5b'     : dir_ret_5b,
            'dir_ret_10b'    : dir_ret_10b,
            'dir_ret_20b'    : dir_ret_20b,
            'q_filter_active': q_filter,
        })

    if not trades:
        return pd.DataFrame()

    trade_df = pd.DataFrame(trades)
    trade_df['Q_bin'] = pd.qcut(trade_df['entry_Q'], q=3, labels=['low_Q', 'mid_Q', 'high_Q'],
                                 duplicates='drop')
    return trade_df


# ─────────────────────────────────────────────────────────────────────────────
# Equity curve computation
# ─────────────────────────────────────────────────────────────────────────────

def compute_equity_curve(trade_log: pd.DataFrame, initial_capital: float = 1.0) -> pd.Series:
    """
    Compute cumulative equity curve from trade log (compound returns).
    Assumes equal position sizing per trade.
    """
    if len(trade_log) == 0:
        return pd.Series([initial_capital])

    returns = trade_log.sort_values('entry_time')['net_return'].values
    equity  = initial_capital * np.cumprod(1.0 + returns)
    return pd.Series(equity, index=range(len(equity)))


# ─────────────────────────────────────────────────────────────────────────────
# Strategy performance metrics
# ─────────────────────────────────────────────────────────────────────────────

def compute_strategy_metrics(trade_log: pd.DataFrame, name: str = '') -> dict:
    """
    Compute comprehensive performance metrics for a trade log.
    """
    if len(trade_log) == 0:
        return {'strategy': name, 'n_trades': 0, 'error': 'no trades'}

    r = trade_log['net_return'].values
    wins   = r[r > 0]
    losses = r[r < 0]
    equity = compute_equity_curve(trade_log)

    # Sharpe ratio (annualized, assuming 5-min bars, 252 trading days)
    if r.std() > 0:
        bars_per_year = 252 * 24 * 12    # 5-min bars per year
        trades_per_year = len(r) / max(1, len(trade_log['entry_time'].dt.year.unique()))
        sharpe = (r.mean() / r.std()) * np.sqrt(trades_per_year)
    else:
        sharpe = 0.0

    # Profit factor
    gross_profit = wins.sum() if len(wins) > 0 else 0.0
    gross_loss   = abs(losses.sum()) if len(losses) > 0 else 1e-10
    profit_factor = gross_profit / (gross_loss + 1e-12)

    # Max drawdown
    cum_max = np.maximum.accumulate(equity.values)
    drawdown = (equity.values - cum_max) / (cum_max + 1e-12)
    max_dd = float(drawdown.min())

    # Stop-loss hit rate
    stop_rate = float(trade_log['stop_hit'].mean())

    metrics = {
        'strategy'          : name,
        'n_trades'          : len(r),
        'win_rate'          : float((r > 0).mean()),
        'avg_return'        : float(r.mean()),
        'median_return'     : float(np.median(r)),
        'std_return'        : float(r.std()),
        'total_return'      : float((equity.iloc[-1] - 1.0) if len(equity) > 0 else 0.0),
        'sharpe_ratio'      : float(sharpe),
        'profit_factor'     : float(profit_factor),
        'max_drawdown'      : max_dd,
        'gross_profit'      : float(gross_profit),
        'gross_loss'        : float(gross_loss),
        'expectancy'        : float(r.mean()),
        'stop_hit_rate'     : stop_rate,
        'avg_duration_bars' : float(trade_log['duration_bars'].mean()),
        'q_filter_active'   : bool(trade_log['q_filter_active'].any()),
        'coherent_trade_pct': float((trade_log['entry_regime'] == 'COHERENT').mean()) if 'entry_regime' in trade_log.columns else np.nan,
    }
    return metrics


# ─────────────────────────────────────────────────────────────────────────────
# Strategy comparison table
# ─────────────────────────────────────────────────────────────────────────────

def compare_strategies(
    df: pd.DataFrame,
    q_threshold: float = 0.0,
) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """
    Run both strategies and return:
    (trade_log_combined, strategy_comparison_df, equity_curves_df)

    Parameters
    ----------
    df           : transport-augmented DataFrame
    q_threshold  : Q threshold for Strategy B (default 0.0)
    """
    log_A = run_strategy(df, strategy_name='A', q_filter=False)
    log_B = run_strategy(df, strategy_name='B', q_filter=True, q_threshold=q_threshold)

    metrics_A = compute_strategy_metrics(log_A, name='A (No Q filter)')
    metrics_B = compute_strategy_metrics(log_B, name='B (Q>0 filter)')

    comparison = pd.DataFrame([metrics_A, metrics_B])

    combined_log = pd.concat([log_A, log_B], ignore_index=True) if (len(log_A) > 0 and len(log_B) > 0) else pd.DataFrame()

    # Equity curves
    eq_A = compute_equity_curve(log_A)
    eq_B = compute_equity_curve(log_B)
    n_max = max(len(eq_A), len(eq_B))
    equity_df = pd.DataFrame({
        'strategy_A': pd.concat([eq_A, pd.Series([np.nan] * (n_max - len(eq_A)))]).values,
        'strategy_B': pd.concat([eq_B, pd.Series([np.nan] * (n_max - len(eq_B)))]).values,
        'trade_idx' : range(n_max),
    })

    return combined_log, comparison, equity_df


# ─────────────────────────────────────────────────────────────────────────────
# Return profile by Q bin
# ─────────────────────────────────────────────────────────────────────────────

def returns_by_q_bin(
    df: pd.DataFrame,
    n_bins: int = 5,
    horizons: List[int] = [5, 10, 20, 50],
) -> pd.DataFrame:
    """
    Compute average future returns conditioned on Q bin.
    This is the primary observational test: does Q predict future returns?

    Returns DataFrame with rows = Q bins, cols = return horizons + metrics.
    """
    Q_col = 'tr_Q'
    if Q_col not in df.columns:
        return pd.DataFrame()

    # Drop rows with NaN Q
    valid = df[Q_col].notna()
    df_v  = df[valid].copy()

    # Create Q bins
    try:
        df_v['Q_bin'] = pd.qcut(df_v[Q_col], q=n_bins, labels=False, duplicates='drop')
    except Exception:
        return pd.DataFrame()

    rows = []
    for bin_id in sorted(df_v['Q_bin'].dropna().unique()):
        subset = df_v[df_v['Q_bin'] == bin_id]
        Q_range = (float(subset[Q_col].min()), float(subset[Q_col].max()))

        row = {
            'Q_bin'        : int(bin_id),
            'Q_min'        : Q_range[0],
            'Q_max'        : Q_range[1],
            'Q_median'     : float(subset[Q_col].median()),
            'n_bars'       : len(subset),
            'coherent_frac': float((subset[Q_col] > 0).mean()),
        }
        for h in horizons:
            col = f'ret_{h}b'
            if col in df_v.columns:
                rets = subset[col].dropna()
                row[f'avg_ret_{h}b']    = float(rets.mean())
                row[f'abs_ret_{h}b']    = float(rets.abs().mean())
                row[f'median_ret_{h}b'] = float(rets.median())
                row[f'std_ret_{h}b']    = float(rets.std())
        rows.append(row)

    return pd.DataFrame(rows)


# ─────────────────────────────────────────────────────────────────────────────
# Trend continuation analysis
# ─────────────────────────────────────────────────────────────────────────────

def compute_trend_persistence(
    df: pd.DataFrame,
    horizons: List[int] = [10, 20, 50],
) -> pd.DataFrame:
    """
    For each bar, compute directional persistence probability
    conditioned on Q regime.

    Directional persistence: if the return at horizon h has the same
    sign as the 1-bar return at entry, the trend persists.
    """
    ret_1b = df['ret_1b']
    direction = np.sign(ret_1b)

    rows = []
    for h in horizons:
        col = f'ret_{h}b'
        if col not in df.columns:
            continue

        future_ret = df[col]
        same_dir   = (np.sign(future_ret) == direction).astype(float)
        same_dir[direction == 0] = np.nan

        df_temp = pd.DataFrame({
            'Q'         : df['tr_Q'],
            'same_dir'  : same_dir,
            'regime_str': df['tr_regime_str'],
        }).dropna()

        if len(df_temp) < 100:
            continue

        # By regime
        for reg in ['COHERENT', 'INCOHERENT']:
            sub = df_temp[df_temp['regime_str'] == reg]
            if len(sub) < 50:
                continue
            rows.append({
                'horizon_bars'       : h,
                'horizon_min'        : h * 5,
                'regime'             : reg,
                'trend_persist_prob' : float(sub['same_dir'].mean()),
                'n_bars'             : len(sub),
                'mean_Q'             : float(sub['Q'].mean()),
            })

        # Overall Spearman correlation Q vs same_dir
        from scipy.stats import spearmanr
        rho, p = spearmanr(df_temp['Q'], df_temp['same_dir'])
        rows.append({
            'horizon_bars'       : h,
            'horizon_min'        : h * 5,
            'regime'             : 'ALL',
            'trend_persist_prob' : float(df_temp['same_dir'].mean()),
            'n_bars'             : len(df_temp),
            'mean_Q'             : float(df_temp['Q'].mean()),
            'spearman_rho_Q'     : float(rho),
            'spearman_p'         : float(p),
        })

    return pd.DataFrame(rows)
