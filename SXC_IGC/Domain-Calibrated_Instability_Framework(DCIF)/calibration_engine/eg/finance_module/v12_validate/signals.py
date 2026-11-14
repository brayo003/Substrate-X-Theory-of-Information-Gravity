"""
signals.py — Signal extraction for V12 validation.

Reuses the signal definitions from src/forex_pipeline.py (ForexSignalProcessor)
without modification.  Adds only the OHLC resampling step required to compute
them from raw ticks.

Signals produced (matching ForexSignalProcessor.generate_basic_signals):
    volatility        rolling std of returns (window=20)
    volume_ratio      volume / MA(volume, 50)
    spread_ratio      spread / MA(spread, 50)
    tick_frequency    rolling mean tick count (window=20)
    momentum_20min    pct_change(4) on 5-min closes
    momentum_1hr      pct_change(12) on 5-min closes

Normalisation: z-score with 99th-pct clipping, then sigmoid → (0, 1).
Matches ForexSignalProcessor.normalize_signals exactly.

V12 excitation input: composite signal = mean of all normalised signals.
The SXCOmegaEngine.excitation_flux() maps this composite through its own
nonlinear function.
"""

import numpy as np
import pandas as pd
from typing import Dict, Tuple


BAR_FREQ = "5min"
VOL_WINDOW    = 20
VOL_MA_WINDOW = 50
TICK_WINDOW   = 20


# ---------------------------------------------------------------------------
# OHLC resampling  (mirrors ForexSignalProcessor.create_ohlc)
# ---------------------------------------------------------------------------

def build_ohlc(ticks: pd.DataFrame, freq: str = BAR_FREQ) -> pd.DataFrame:
    """
    Resample ticks to OHLC bars.

    Parameters
    ----------
    ticks : DataFrame with columns timestamp, mid, total_vol, spread_pips
    freq  : pandas resample rule (default '5min')

    Returns
    -------
    OHLC DataFrame indexed by UTC timestamp.
    """
    df = ticks.set_index('timestamp').sort_index()
    mid = df['mid']

    ohlc = mid.resample(freq).ohlc()
    ohlc['volume']     = df['total_vol'].resample(freq).sum()
    ohlc['spread']     = df['spread_pips'].resample(freq).mean()
    ohlc['tick_count'] = mid.resample(freq).count()

    ohlc['returns']     = ohlc['close'].pct_change()
    ohlc['log_returns'] = np.log(ohlc['close'] / ohlc['close'].shift(1))

    # drop bars with no ticks (weekend gaps etc.)
    ohlc = ohlc[ohlc['tick_count'] > 0].copy()
    ohlc.dropna(subset=['close'], inplace=True)
    return ohlc


# ---------------------------------------------------------------------------
# Raw signals  (mirrors ForexSignalProcessor.generate_basic_signals)
# ---------------------------------------------------------------------------

def compute_raw_signals(ohlc: pd.DataFrame) -> Dict[str, pd.Series]:
    """
    Compute the six canonical signals defined by ForexSignalProcessor.

    Returns a dict of pd.Series aligned to the OHLC index.
    """
    df = ohlc.copy()

    volatility = df['returns'].rolling(window=VOL_WINDOW, min_periods=10).std()

    vol_ma       = df['volume'].rolling(window=VOL_MA_WINDOW, min_periods=25).mean()
    volume_ratio = df['volume'] / (vol_ma + 1e-8)

    spread_ma    = df['spread'].rolling(window=VOL_MA_WINDOW, min_periods=25).mean()
    spread_ratio = df['spread'] / (spread_ma + 1e-8)

    tick_freq = df['tick_count'].rolling(window=TICK_WINDOW, min_periods=10).mean()

    momentum_20min = df['close'].pct_change(periods=4)
    momentum_1hr   = df['close'].pct_change(periods=12)

    raw = {
        'volatility'    : volatility,
        'volume_ratio'  : volume_ratio,
        'spread_ratio'  : spread_ratio,
        'tick_frequency': tick_freq,
        'momentum_20min': momentum_20min,
        'momentum_1hr'  : momentum_1hr,
    }
    # drop leading NaN uniformly
    for k in raw:
        raw[k] = raw[k].dropna()

    return raw


# ---------------------------------------------------------------------------
# Normalisation  (mirrors ForexSignalProcessor.normalize_signals)
# ---------------------------------------------------------------------------

def normalize_signals(raw: Dict[str, pd.Series]) -> Tuple[Dict[str, pd.Series], Dict[str, dict]]:
    """
    Z-score with 99th-percentile clipping, then sigmoid → (0, 1).

    Returns
    -------
    normalized : dict of pd.Series
    params     : dict of {mean, std, q99} per signal (for real-time use)
    """
    normalized = {}
    params     = {}

    for name, series in raw.items():
        if len(series) < 10:
            continue
        q99         = series.quantile(0.99)
        clipped     = series.clip(upper=q99)
        mu, sigma   = clipped.mean(), clipped.std()
        sigma       = sigma if sigma > 0 else 1.0
        z           = (clipped - mu) / sigma
        norm        = 1.0 / (1.0 + np.exp(-z))
        normalized[name] = norm
        params[name]     = {'mean': mu, 'std': sigma, 'q99': q99}

    return normalized, params


# ---------------------------------------------------------------------------
# V12 composite signal
# ---------------------------------------------------------------------------

def build_composite(normalized: Dict[str, pd.Series]) -> pd.Series:
    """
    Align all normalised signals to a common index and compute the
    row-wise mean.  This single value is fed into SXCOmegaEngine.step()
    as the `signal` argument.

    The composite represents the average normalised stress across all
    six market dimensions.  Its range is (0, 1).  The SXCOmegaEngine's
    excitation_flux scales it to the 0–100 range expected by its
    internal piecewise function by multiplying by 100.
    """
    df = pd.DataFrame(normalized).dropna()
    composite = df.mean(axis=1)
    composite.name = 'composite'
    return composite


def build_signals_from_ticks(ticks: pd.DataFrame,
                              freq: str = BAR_FREQ
                              ) -> Tuple[pd.DataFrame,
                                         Dict[str, pd.Series],
                                         Dict[str, pd.Series],
                                         pd.Series]:
    """
    Convenience wrapper.

    Returns
    -------
    ohlc        : OHLC DataFrame
    raw         : dict of raw signal Series
    normalized  : dict of normalized signal Series
    composite   : single Series (V12 input)
    """
    ohlc               = build_ohlc(ticks, freq=freq)
    raw                = compute_raw_signals(ohlc)
    normalized, params = normalize_signals(raw)
    composite          = build_composite(normalized)
    return ohlc, raw, normalized, composite
