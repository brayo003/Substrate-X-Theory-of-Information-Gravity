"""
labels.py — Independent market measurements (no V12 dependency).

All measurements are derived from OHLC bars produced by signals.build_ohlc().
None of them reference V12, DCII, T_sys, or any SXCOmega variable.

Computed labels
---------------
realized_vol      Rolling std of log-returns (window 20 bars = 100 min)
atr               Average True Range (14 bars)
adx               Average Directional Index (14 bars)
hurst             Rolling Hurst exponent (window 100 bars)
spread_norm       Spread normalised by its rolling median (window 100 bars)
tick_dens         Tick count per bar (proxy for liquidity)
range_pct         (high - low) / close — intrabar range
breakout          1 if close breaks 20-bar high/low, else 0
trend_persist     Rolling autocorrelation of log-returns (lag 1, window 20)
drawdown          Rolling drawdown from 20-bar peak
"""

import numpy as np
import pandas as pd


# ---------------------------------------------------------------------------
# Realized volatility
# ---------------------------------------------------------------------------

def realized_vol(ohlc: pd.DataFrame, window: int = 20) -> pd.Series:
    return ohlc['log_returns'].rolling(window, min_periods=10).std().rename('realized_vol')


# ---------------------------------------------------------------------------
# ATR
# ---------------------------------------------------------------------------

def atr(ohlc: pd.DataFrame, window: int = 14) -> pd.Series:
    high  = ohlc['high']
    low   = ohlc['low']
    close = ohlc['close']
    prev  = close.shift(1)
    tr    = pd.concat([high - low,
                       (high - prev).abs(),
                       (low  - prev).abs()], axis=1).max(axis=1)
    return tr.rolling(window, min_periods=5).mean().rename('atr')


# ---------------------------------------------------------------------------
# ADX  (Wilder smoothing)
# ---------------------------------------------------------------------------

def adx(ohlc: pd.DataFrame, window: int = 14) -> pd.Series:
    high  = ohlc['high']
    low   = ohlc['low']
    close = ohlc['close']

    up_move   = high.diff()
    down_move = -low.diff()

    plus_dm  = np.where((up_move > down_move) & (up_move > 0), up_move,  0.0)
    minus_dm = np.where((down_move > up_move) & (down_move > 0), down_move, 0.0)

    prev_close = close.shift(1)
    tr = pd.concat([high - low,
                    (high - prev_close).abs(),
                    (low  - prev_close).abs()], axis=1).max(axis=1)

    atr_w     = tr.ewm(alpha=1/window, adjust=False).mean()
    plus_di   = 100 * pd.Series(plus_dm,  index=ohlc.index).ewm(alpha=1/window, adjust=False).mean() / (atr_w + 1e-10)
    minus_di  = 100 * pd.Series(minus_dm, index=ohlc.index).ewm(alpha=1/window, adjust=False).mean() / (atr_w + 1e-10)

    dx  = (100 * (plus_di - minus_di).abs() / (plus_di + minus_di + 1e-10))
    adx_val = dx.ewm(alpha=1/window, adjust=False).mean()
    return adx_val.rename('adx')


# ---------------------------------------------------------------------------
# Hurst exponent  (R/S method, rolling)
# ---------------------------------------------------------------------------

def _hurst_rs(series: np.ndarray) -> float:
    """Estimate Hurst via R/S on a 1-D array of log-returns."""
    n = len(series)
    if n < 20:
        return np.nan
    lags = [max(4, n // k) for k in (8, 4, 2)]
    rs_vals = []
    for lag in lags:
        if lag >= n:
            continue
        sub = series[:lag]
        mean_sub = sub.mean()
        deviation = np.cumsum(sub - mean_sub)
        R = deviation.max() - deviation.min()
        S = sub.std()
        if S > 0:
            rs_vals.append(np.log(R / S))
    if len(rs_vals) < 2:
        return np.nan
    lags_log = [np.log(max(4, n // k)) for k in (8, 4, 2)][:len(rs_vals)]
    try:
        h = np.polyfit(lags_log, rs_vals, 1)[0]
    except Exception:
        h = np.nan
    return float(np.clip(h, 0.0, 1.0))


def hurst(ohlc: pd.DataFrame, window: int = 100) -> pd.Series:
    lr = ohlc['log_returns'].dropna().values
    idx = ohlc['log_returns'].dropna().index
    result = np.full(len(lr), np.nan)
    for i in range(window, len(lr)):
        result[i] = _hurst_rs(lr[i - window:i])
    return pd.Series(result, index=idx, name='hurst').reindex(ohlc.index)


# ---------------------------------------------------------------------------
# Normalised spread  (spread relative to its own rolling median)
# ---------------------------------------------------------------------------

def spread_norm(ohlc: pd.DataFrame, window: int = 100) -> pd.Series:
    med = ohlc['spread'].rolling(window, min_periods=20).median()
    return (ohlc['spread'] / (med + 1e-8)).rename('spread_norm')


# ---------------------------------------------------------------------------
# Range percent
# ---------------------------------------------------------------------------

def range_pct(ohlc: pd.DataFrame) -> pd.Series:
    return ((ohlc['high'] - ohlc['low']) / (ohlc['close'] + 1e-8)).rename('range_pct')


# ---------------------------------------------------------------------------
# Breakout flag
# ---------------------------------------------------------------------------

def breakout(ohlc: pd.DataFrame, window: int = 20) -> pd.Series:
    rolling_high = ohlc['high'].rolling(window, min_periods=window).max().shift(1)
    rolling_low  = ohlc['low'].rolling(window,  min_periods=window).min().shift(1)
    flag = ((ohlc['close'] > rolling_high) | (ohlc['close'] < rolling_low)).astype(int)
    return flag.rename('breakout')


# ---------------------------------------------------------------------------
# Trend persistence (lag-1 autocorrelation of log-returns)
# ---------------------------------------------------------------------------

def trend_persist(ohlc: pd.DataFrame, window: int = 20) -> pd.Series:
    lr = ohlc['log_returns']
    ac = lr.rolling(window, min_periods=10).apply(
        lambda x: pd.Series(x).autocorr(lag=1) if len(x) > 2 else np.nan,
        raw=False
    )
    return ac.rename('trend_persist')


# ---------------------------------------------------------------------------
# Rolling drawdown from 20-bar peak
# ---------------------------------------------------------------------------

def drawdown(ohlc: pd.DataFrame, window: int = 20) -> pd.Series:
    peak = ohlc['close'].rolling(window, min_periods=5).max()
    dd   = (ohlc['close'] - peak) / (peak + 1e-8)
    return dd.rename('drawdown')


# ---------------------------------------------------------------------------
# Convenience: compute all labels at once
# ---------------------------------------------------------------------------

def build_all_labels(ohlc: pd.DataFrame) -> pd.DataFrame:
    """
    Returns a DataFrame of all independent market measurements,
    aligned to the OHLC index.
    """
    parts = [
        realized_vol(ohlc),
        atr(ohlc),
        adx(ohlc),
        hurst(ohlc),
        spread_norm(ohlc),
        ohlc['tick_count'].rename('tick_density'),
        range_pct(ohlc),
        breakout(ohlc),
        trend_persist(ohlc),
        drawdown(ohlc),
        ohlc['spread'].rename('spread_abs'),
        ohlc['log_returns'].abs().rename('abs_return'),
    ]
    df = pd.concat(parts, axis=1)
    # tag trading session by UTC hour
    df['session'] = pd.cut(
        df.index.hour,
        bins=[-1, 6, 12, 18, 24],
        labels=['asia', 'london', 'ny', 'late'],
        right=True
    )
    return df
