"""
strategy_library.py — Independent Strategy Library for Phase 1 Transport Validation.

28 strategies across 7 families. Each strategy is COMPLETELY INDEPENDENT of Q.
Q is NEVER consulted inside any strategy. Strategies only use price/indicator data.

Strategy families:
  1. Trend        (6 strategies)
  2. Momentum     (5 strategies)
  3. MeanReversion(5 strategies)
  4. Breakout     (4 strategies)
  5. Scalping     (3 strategies)
  6. Volatility   (3 strategies)
  7. Session      (3 strategies)  [London, NY, Asian]

Each strategy exposes a single function:
    generate_signals(df) -> pd.Series of {-1, 0, +1}

The df must have at minimum: open, high, low, close, volume, atr_14, rsi_14,
macd, macd_signal, adx_14, realized_vol_20, and a DatetimeIndex (UTC).
All those columns are produced by transport_integration.build_full_pipeline().

Execution constants (identical for ALL strategies, enforced by execution_simulator):
    COMMISSION = 0.00020   # 2 pip one-way cost (spread + commission)
    SLIPPAGE   = 0.00005   # 0.5 pip slippage per side
    HOLD_BARS  = 24        # max bars in trade (2 hours at 5-min bars)
    ATR_STOP   = 1.5       # stop distance in ATR multiples
    ATR_TARGET = 2.5       # target distance in ATR multiples
"""

import numpy as np
import pandas as pd
from typing import Dict, Callable

# ── Execution constants (shared; execution_simulator enforces them) ────────
COMMISSION  = 0.00020   # EUR/USD 2-pip spread
SLIPPAGE    = 0.00005   # 0.5-pip slippage per side
HOLD_BARS   = 24        # max 2 hours at 5-min bars
ATR_STOP    = 1.5       # stop in ATR
ATR_TARGET  = 2.5       # target in ATR

_REGISTRY: Dict[str, Callable] = {}

def _register(family: str):
    """Decorator that registers a strategy function."""
    def decorator(fn):
        _REGISTRY[fn.__name__] = {'fn': fn, 'family': family}
        return fn
    return decorator

def get_all_strategies() -> Dict[str, dict]:
    """Return registry of all strategies."""
    return dict(_REGISTRY)

def get_families() -> Dict[str, list]:
    """Return {family: [strategy_name, ...]}."""
    out = {}
    for name, meta in _REGISTRY.items():
        fam = meta['family']
        out.setdefault(fam, []).append(name)
    return out

# ═══════════════════════════════════════════════════════════════════════════
# FAMILY 1 — TREND
# ═══════════════════════════════════════════════════════════════════════════

@_register('Trend')
def EMA_Crossover(df: pd.DataFrame) -> pd.Series:
    """EMA(9) / EMA(21) crossover."""
    fast = df['close'].ewm(span=9,  adjust=False).mean()
    slow = df['close'].ewm(span=21, adjust=False).mean()
    diff = fast - slow
    sig  = pd.Series(0, index=df.index, dtype=np.int8)
    sig[(diff > 0) & (diff.shift(1) <= 0)] =  1
    sig[(diff < 0) & (diff.shift(1) >= 0)] = -1
    return sig


@_register('Trend')
def SMA_Crossover(df: pd.DataFrame) -> pd.Series:
    """SMA(20) / SMA(50) crossover."""
    fast = df['close'].rolling(20).mean()
    slow = df['close'].rolling(50).mean()
    diff = fast - slow
    sig  = pd.Series(0, index=df.index, dtype=np.int8)
    sig[(diff > 0) & (diff.shift(1) <= 0)] =  1
    sig[(diff < 0) & (diff.shift(1) >= 0)] = -1
    return sig


@_register('Trend')
def MACD_Trend(df: pd.DataFrame) -> pd.Series:
    """MACD histogram sign change (already computed in pipeline)."""
    hist = df['macd_hist']
    sig  = pd.Series(0, index=df.index, dtype=np.int8)
    sig[(hist > 0) & (hist.shift(1) <= 0)] =  1
    sig[(hist < 0) & (hist.shift(1) >= 0)] = -1
    return sig


@_register('Trend')
def Supertrend(df: pd.DataFrame) -> pd.Series:
    """Supertrend with ATR multiplier 2.5, period 10."""
    period = 10
    mult   = 2.5
    hl2    = (df['high'] + df['low']) / 2.0
    atr    = df['atr_14']

    upper_band = hl2 + mult * atr
    lower_band = hl2 - mult * atr

    # rolling final bands
    final_upper = upper_band.copy()
    final_lower = lower_band.copy()
    close       = df['close'].values
    fu = final_upper.values.copy()
    fl = final_lower.values.copy()
    ub = upper_band.values
    lb = lower_band.values

    for i in range(1, len(close)):
        fu[i] = ub[i] if (ub[i] < fu[i-1] or close[i-1] > fu[i-1]) else fu[i-1]
        fl[i] = lb[i] if (lb[i] > fl[i-1] or close[i-1] < fl[i-1]) else fl[i-1]

    trend = np.zeros(len(close), dtype=np.int8)
    for i in range(1, len(close)):
        if close[i] > fu[i-1]:
            trend[i] =  1
        elif close[i] < fl[i-1]:
            trend[i] = -1
        else:
            trend[i] = trend[i-1]

    sig = pd.Series(0, index=df.index, dtype=np.int8)
    trend_s = pd.Series(trend, index=df.index)
    sig[(trend_s == 1) & (trend_s.shift(1) != 1)]   =  1
    sig[(trend_s == -1) & (trend_s.shift(1) != -1)] = -1
    return sig


@_register('Trend')
def Donchian_Trend(df: pd.DataFrame) -> pd.Series:
    """Donchian 20-bar channel: enter on close above/below channel."""
    upper = df['high'].rolling(20).max().shift(1)
    lower = df['low'].rolling(20).min().shift(1)
    mid   = (upper + lower) / 2
    sig   = pd.Series(0, index=df.index, dtype=np.int8)
    sig[(df['close'] > upper) & (df['close'].shift(1) <= upper.shift(1))] =  1
    sig[(df['close'] < lower) & (df['close'].shift(1) >= lower.shift(1))] = -1
    return sig


@_register('Trend')
def Turtle_Breakout(df: pd.DataFrame) -> pd.Series:
    """Original Turtle 20-bar breakout (System 1)."""
    high20 = df['high'].rolling(20).max().shift(1)
    low20  = df['low'].rolling(20).min().shift(1)
    sig    = pd.Series(0, index=df.index, dtype=np.int8)
    sig[(df['close'] > high20) & (df['close'].shift(1) <= high20.shift(1))] =  1
    sig[(df['close'] < low20)  & (df['close'].shift(1) >= low20.shift(1))]  = -1
    return sig

# ═══════════════════════════════════════════════════════════════════════════
# FAMILY 2 — MOMENTUM
# ═══════════════════════════════════════════════════════════════════════════

@_register('Momentum')
def RSI_Momentum(df: pd.DataFrame) -> pd.Series:
    """RSI(14) momentum: go long when RSI crosses above 50 from below."""
    rsi = df['rsi_14']
    sig = pd.Series(0, index=df.index, dtype=np.int8)
    sig[(rsi > 55) & (rsi.shift(1) <= 55)] =  1
    sig[(rsi < 45) & (rsi.shift(1) >= 45)] = -1
    return sig


@_register('Momentum')
def Stochastic_Momentum(df: pd.DataFrame) -> pd.Series:
    """Stochastic %K(14,3) crossover of %D(3)."""
    low14  = df['low'].rolling(14).min()
    high14 = df['high'].rolling(14).max()
    k      = 100 * (df['close'] - low14) / (high14 - low14 + 1e-10)
    d      = k.rolling(3).mean()
    sig    = pd.Series(0, index=df.index, dtype=np.int8)
    sig[(k > d) & (k.shift(1) <= d.shift(1)) & (k < 80)] =  1
    sig[(k < d) & (k.shift(1) >= d.shift(1)) & (k > 20)] = -1
    return sig


@_register('Momentum')
def ROC_Momentum(df: pd.DataFrame) -> pd.Series:
    """Rate of Change (12-bar) sign cross."""
    roc = df['close'].pct_change(12) * 100
    sig = pd.Series(0, index=df.index, dtype=np.int8)
    sig[(roc > 0) & (roc.shift(1) <= 0)] =  1
    sig[(roc < 0) & (roc.shift(1) >= 0)] = -1
    return sig


@_register('Momentum')
def CCI_Momentum(df: pd.DataFrame) -> pd.Series:
    """CCI(20) threshold cross: |CCI| > 100."""
    tp   = (df['high'] + df['low'] + df['close']) / 3.0
    ma   = tp.rolling(20).mean()
    mad  = tp.rolling(20).apply(lambda x: np.mean(np.abs(x - x.mean())), raw=True)
    cci  = (tp - ma) / (0.015 * mad + 1e-10)
    sig  = pd.Series(0, index=df.index, dtype=np.int8)
    sig[(cci > 100) & (cci.shift(1) <= 100)]   =  1
    sig[(cci < -100) & (cci.shift(1) >= -100)] = -1
    return sig


@_register('Momentum')
def ADX_Trend(df: pd.DataFrame) -> pd.Series:
    """ADX > 25 confirms trend; enter in direction of MACD histogram sign."""
    adx  = df['adx_14']
    hist = df['macd_hist']
    sig  = pd.Series(0, index=df.index, dtype=np.int8)
    strong = adx > 25
    sig[(hist > 0) & (hist.shift(1) <= 0) & strong] =  1
    sig[(hist < 0) & (hist.shift(1) >= 0) & strong] = -1
    return sig


# ═══════════════════════════════════════════════════════════════════════════
# FAMILY 3 — MEAN REVERSION
# ═══════════════════════════════════════════════════════════════════════════

@_register('MeanReversion')
def Bollinger_Reversion(df: pd.DataFrame) -> pd.Series:
    """Bollinger Band(20,2): fade 2σ extremes."""
    ma    = df['close'].rolling(20).mean()
    std   = df['close'].rolling(20).std()
    upper = ma + 2 * std
    lower = ma - 2 * std
    sig   = pd.Series(0, index=df.index, dtype=np.int8)
    sig[(df['close'] > upper) & (df['close'].shift(1) <= upper.shift(1))] = -1
    sig[(df['close'] < lower) & (df['close'].shift(1) >= lower.shift(1))] =  1
    return sig


@_register('MeanReversion')
def RSI_Reversal(df: pd.DataFrame) -> pd.Series:
    """RSI(14) reversal from oversold/overbought (<30/>70)."""
    rsi = df['rsi_14']
    sig = pd.Series(0, index=df.index, dtype=np.int8)
    sig[(rsi > 30) & (rsi.shift(1) <= 30)] =  1   # exit oversold = buy
    sig[(rsi < 70) & (rsi.shift(1) >= 70)] = -1   # exit overbought = sell
    return sig


@_register('MeanReversion')
def VWAP_Reversion(df: pd.DataFrame) -> pd.Series:
    """Intraday VWAP reversion: fade when price is >1 ATR from VWAP."""
    close  = df['close']
    vol    = df['volume'].replace(0, np.nan)
    # Rolling VWAP using 48-bar window (~4 hours)
    vwap   = (close * vol).rolling(48).sum() / (vol.rolling(48).sum() + 1e-10)
    diff   = close - vwap
    atr    = df['atr_14']
    sig    = pd.Series(0, index=df.index, dtype=np.int8)
    sig[(diff < -atr) & (diff.shift(1) >= -atr.shift(1))] =  1
    sig[(diff >  atr) & (diff.shift(1) <=  atr.shift(1))] = -1
    return sig


@_register('MeanReversion')
def ZScore_Reversion(df: pd.DataFrame) -> pd.Series:
    """Z-score of close vs 30-bar mean: fade |z|>2."""
    ma   = df['close'].rolling(30).mean()
    std  = df['close'].rolling(30).std()
    z    = (df['close'] - ma) / (std + 1e-10)
    sig  = pd.Series(0, index=df.index, dtype=np.int8)
    sig[(z < -2) & (z.shift(1) >= -2)] =  1
    sig[(z >  2) & (z.shift(1) <=  2)] = -1
    return sig


@_register('MeanReversion')
def Keltner_Reversion(df: pd.DataFrame) -> pd.Series:
    """Keltner Channel(20, ATR×1.5): fade price outside channel."""
    ema   = df['close'].ewm(span=20, adjust=False).mean()
    atr   = df['atr_14']
    upper = ema + 1.5 * atr
    lower = ema - 1.5 * atr
    sig   = pd.Series(0, index=df.index, dtype=np.int8)
    sig[(df['close'] > upper) & (df['close'].shift(1) <= upper.shift(1))] = -1
    sig[(df['close'] < lower) & (df['close'].shift(1) >= lower.shift(1))] =  1
    return sig

# ═══════════════════════════════════════════════════════════════════════════
# FAMILY 4 — BREAKOUT
# ═══════════════════════════════════════════════════════════════════════════

@_register('Breakout')
def Bollinger_Squeeze_Breakout(df: pd.DataFrame) -> pd.Series:
    """Bollinger Width bottom-20th pct squeeze, then breakout."""
    ma  = df['close'].rolling(20).mean()
    bw  = 2 * df['close'].rolling(20).std() / (ma + 1e-10)
    low = bw < bw.rolling(100).quantile(0.20)
    h5  = df['high'].rolling(5).max().shift(1)
    l5  = df['low'].rolling(5).min().shift(1)
    sig = pd.Series(0, index=df.index, dtype=np.int8)
    sig[(df['close'] > h5) & low & (df['close'].shift(1) <= h5.shift(1))] =  1
    sig[(df['close'] < l5) & low & (df['close'].shift(1) >= l5.shift(1))] = -1
    return sig


@_register('Breakout')
def Donchian_Breakout(df: pd.DataFrame) -> pd.Series:
    """Donchian 10-bar channel breakout."""
    high10 = df['high'].rolling(10).max().shift(1)
    low10  = df['low'].rolling(10).min().shift(1)
    sig    = pd.Series(0, index=df.index, dtype=np.int8)
    sig[(df['close'] > high10) & (df['close'].shift(1) <= high10.shift(1))] =  1
    sig[(df['close'] < low10)  & (df['close'].shift(1) >= low10.shift(1))]  = -1
    return sig


@_register('Breakout')
def ATR_Breakout(df: pd.DataFrame) -> pd.Series:
    """ATR breakout: price moves >1 ATR from 10-bar EMA."""
    ema = df['close'].ewm(span=10, adjust=False).mean()
    atr = df['atr_14']
    sig = pd.Series(0, index=df.index, dtype=np.int8)
    diff     = df['close'] - ema
    prev_diff = diff.shift(1)
    sig[(diff >  atr) & (prev_diff <=  atr.shift(1))] =  1
    sig[(diff < -atr) & (prev_diff >= -atr.shift(1))] = -1
    return sig


@_register('Breakout')
def Range_Breakout(df: pd.DataFrame) -> pd.Series:
    """4-bar consolidation range breakout (high-low < 0.5 ATR)."""
    atr      = df['atr_14']
    r4_high  = df['high'].rolling(4).max().shift(1)
    r4_low   = df['low'].rolling(4).min().shift(1)
    r4_range = r4_high - r4_low
    tight    = r4_range < 0.5 * atr
    sig      = pd.Series(0, index=df.index, dtype=np.int8)
    sig[(df['close'] > r4_high) & tight & (df['close'].shift(1) <= r4_high.shift(1))] =  1
    sig[(df['close'] < r4_low)  & tight & (df['close'].shift(1) >= r4_low.shift(1))]  = -1
    return sig


# ═══════════════════════════════════════════════════════════════════════════
# FAMILY 5 — SCALPING
# ═══════════════════════════════════════════════════════════════════════════

@_register('Scalping')
def EMA_Micro_Trend(df: pd.DataFrame) -> pd.Series:
    """Fast EMA(3)/EMA(8) micro-crossover for scalp entries."""
    fast = df['close'].ewm(span=3,  adjust=False).mean()
    slow = df['close'].ewm(span=8,  adjust=False).mean()
    diff = fast - slow
    sig  = pd.Series(0, index=df.index, dtype=np.int8)
    sig[(diff > 0) & (diff.shift(1) <= 0)] =  1
    sig[(diff < 0) & (diff.shift(1) >= 0)] = -1
    return sig


@_register('Scalping')
def VWAP_Scalp(df: pd.DataFrame) -> pd.Series:
    """Scalp off VWAP: enter when price tags VWAP and shows reversal candle."""
    close = df['close']
    vol   = df['volume'].replace(0, np.nan)
    vwap  = (close * vol).rolling(24).sum() / (vol.rolling(24).sum() + 1e-10)
    diff  = close - vwap
    atr   = df['atr_14']
    # Enter when price crosses back through VWAP (momentum toward VWAP)
    sig   = pd.Series(0, index=df.index, dtype=np.int8)
    sig[(diff > 0) & (diff.shift(1) <= 0) & (diff.abs() < 0.5 * atr)] =  1
    sig[(diff < 0) & (diff.shift(1) >= 0) & (diff.abs() < 0.5 * atr)] = -1
    return sig


@_register('Scalping')
def Volatility_Scalp(df: pd.DataFrame) -> pd.Series:
    """Scalp during low-volatility periods: RSI cross near 50."""
    rsi = df['rsi_14']
    rv  = df['realized_vol_20']
    low_vol = rv < rv.rolling(50).quantile(0.30)
    sig = pd.Series(0, index=df.index, dtype=np.int8)
    sig[(rsi > 50) & (rsi.shift(1) <= 50) & low_vol] =  1
    sig[(rsi < 50) & (rsi.shift(1) >= 50) & low_vol] = -1
    return sig


# ═══════════════════════════════════════════════════════════════════════════
# FAMILY 6 — VOLATILITY
# ═══════════════════════════════════════════════════════════════════════════

@_register('Volatility')
def ATR_Expansion(df: pd.DataFrame) -> pd.Series:
    """Enter when ATR expands >1.5× its 20-bar average (breakout direction)."""
    atr     = df['atr_14']
    atr_ma  = atr.rolling(20).mean()
    expand  = atr > 1.5 * atr_ma
    hist    = df['macd_hist']
    sig     = pd.Series(0, index=df.index, dtype=np.int8)
    sig[(expand) & (hist > 0) & (~expand.shift(1).fillna(False))] =  1
    sig[(expand) & (hist < 0) & (~expand.shift(1).fillna(False))] = -1
    return sig


@_register('Volatility')
def Volatility_Contraction(df: pd.DataFrame) -> pd.Series:
    """Enter on volatility contraction (RV bottom quartile) breakout."""
    rv      = df['realized_vol_20']
    low_vol = rv < rv.rolling(100).quantile(0.25)
    h10     = df['high'].rolling(10).max().shift(1)
    l10     = df['low'].rolling(10).min().shift(1)
    sig     = pd.Series(0, index=df.index, dtype=np.int8)
    sig[(df['close'] > h10) & low_vol & (df['close'].shift(1) <= h10.shift(1))] =  1
    sig[(df['close'] < l10) & low_vol & (df['close'].shift(1) >= l10.shift(1))] = -1
    return sig


@_register('Volatility')
def Squeeze_Expansion(df: pd.DataFrame) -> pd.Series:
    """Bollinger inside Keltner (squeeze), then Bollinger expands."""
    close  = df['close']
    ma20   = close.rolling(20).mean()
    std20  = close.rolling(20).std()
    atr    = df['atr_14']
    ema20  = close.ewm(span=20, adjust=False).mean()
    bb_up  = ma20 + 2 * std20
    bb_lo  = ma20 - 2 * std20
    kc_up  = ema20 + 1.5 * atr
    kc_lo  = ema20 - 1.5 * atr
    squeeze      = (bb_up < kc_up) & (bb_lo > kc_lo)
    squeeze_prev = squeeze.shift(1).fillna(False)
    expanded     = ~squeeze
    hist = df['macd_hist']
    sig  = pd.Series(0, index=df.index, dtype=np.int8)
    sig[(expanded) & (squeeze_prev) & (hist > 0)] =  1
    sig[(expanded) & (squeeze_prev) & (hist < 0)] = -1
    return sig


# ═══════════════════════════════════════════════════════════════════════════
# FAMILY 7 — SESSION / CARRY
# ═══════════════════════════════════════════════════════════════════════════

def _hour_utc(df: pd.DataFrame) -> pd.Series:
    """Return hour-of-day (UTC) as a Series."""
    return pd.Series(df.index.hour, index=df.index)


@_register('Session')
def London_Breakout(df: pd.DataFrame) -> pd.Series:
    """
    London Open breakout: enter long/short when price breaks the
    07:00–08:00 UTC range at the 08:00 bar.
    """
    hour   = _hour_utc(df)
    close  = df['close']
    sig    = pd.Series(0, index=df.index, dtype=np.int8)
    # Mark pre-London range high/low from 07:00 bar
    is_london_range = (hour >= 7) & (hour < 8)
    range_high = close.where(is_london_range).rolling(12, min_periods=1).max().shift(1)
    range_low  = close.where(is_london_range).rolling(12, min_periods=1).min().shift(1)
    is_london_open = (hour == 8)
    sig[(is_london_open) & (close > range_high) & (close.shift(1) <= range_high.shift(1))] =  1
    sig[(is_london_open) & (close < range_low)  & (close.shift(1) >= range_low.shift(1))]  = -1
    return sig


@_register('Session')
def NY_Continuation(df: pd.DataFrame) -> pd.Series:
    """
    NY open continuation: at 13:30 UTC (NY open), enter in direction of
    London trend (EMA9 vs EMA21 slope at that bar).
    """
    hour   = _hour_utc(df)
    fast   = df['close'].ewm(span=9,  adjust=False).mean()
    slow   = df['close'].ewm(span=21, adjust=False).mean()
    is_ny  = (hour == 13)
    sig    = pd.Series(0, index=df.index, dtype=np.int8)
    trend  = (fast > slow).astype(int) - (fast < slow).astype(int)
    sig[is_ny & (trend == 1) & (trend.shift(1) != 1)]   =  1
    sig[is_ny & (trend == -1) & (trend.shift(1) != -1)] = -1
    return sig


@_register('Session')
def Asian_Range(df: pd.DataFrame) -> pd.Series:
    """
    Asian range fade: fade breakouts of the 00:00–07:00 UTC Asian range
    during European session (08:00–12:00 UTC).
    """
    hour   = _hour_utc(df)
    close  = df['close']
    is_asian    = (hour >= 0) & (hour < 7)
    is_european = (hour >= 8) & (hour < 12)
    asian_high  = close.where(is_asian).rolling(84, min_periods=1).max().shift(1)
    asian_low   = close.where(is_asian).rolling(84, min_periods=1).min().shift(1)
    sig = pd.Series(0, index=df.index, dtype=np.int8)
    # Fade: if European session price re-enters Asian range, fade the move
    sig[(is_european) & (close > asian_high) & (close.shift(1) <= asian_high.shift(1))] = -1
    sig[(is_european) & (close < asian_low)  & (close.shift(1) >= asian_low.shift(1))]  =  1
    return sig
