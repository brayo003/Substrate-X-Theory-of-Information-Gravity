"""
transport_integration.py — Integrate transport layer into the DCII pipeline.

Pipeline position:
    Historical Market Data
            │
    Signal Construction       ← build_signals_from_ticks() [signals.py]
    (ρ, E, F)
            │
    Transport Evolution       ← THIS MODULE
    ∂s/∂t
            │
    Transport State s(x,t)
            │
    Compute Q                 ← transport_layer.compute_transport_from_series()
            │
    Trading Analysis
            │
    Statistical Validation

This module does NOT modify the existing DCII calibration.
It adds transport quantities as additional columns to the existing data.
"""

import sys
import numpy as np
import pandas as pd
from pathlib import Path
from typing import Tuple, Optional, Dict

# ── Resolve paths ──────────────────────────────────────────────────────────
_HERE = Path(__file__).resolve().parent          # v12_validate/
_FM   = _HERE.parent                             # finance_module/
_CE   = _FM.parents[1]                           # calibration_engine/

if str(_CE) not in sys.path:
    sys.path.insert(0, str(_CE))

# ── Local imports ─────────────────────────────────────────────────────────
from v12_validate.transport_layer import (
    compute_transport_from_series,
    TransportCalibration,
    DEFAULT_C,
    DEFAULT_TAU,
)
from v12_validate.signals import build_signals_from_ticks, build_ohlc
from v12_validate.engine_runner import (
    SXCOmegaEngineStable,
    scale_signals_to_100,
    build_v12_composite,
    run_v12,
)


# ─────────────────────────────────────────────────────────────────────────────
# Main integration entry point
# ─────────────────────────────────────────────────────────────────────────────

def build_full_pipeline(
    ticks: pd.DataFrame,
    c: float = DEFAULT_C,
    tau: float = DEFAULT_TAU,
    bar_freq: str = "5min",
    verbose: bool = True,
) -> Tuple[pd.DataFrame, dict]:
    """
    Run the complete pipeline from ticks to transport-augmented DataFrame.

    Steps
    -----
    1. Build OHLC bars (5-min default)
    2. Compute 6 market signals (signals.py, unchanged)
    3. Compute normalized composite stress field s (signals.py, unchanged)
    4. Run V12 engine to get T_sys and phase (engine_runner.py, unchanged)
    5. Apply SXC-IGC transport layer → s_transport, Q, regime (NEW)
    6. Merge all quantities into one aligned DataFrame
    7. Compute future returns for each bar (5, 10, 20, 50 bars ahead)
    8. Add ATR, ADX proxy, RSI, MACD for cross-correlation analysis

    Parameters
    ----------
    ticks    : raw tick DataFrame from loader.py
    c        : transport propagation speed
    tau      : transport relaxation time (bars)
    bar_freq : OHLC resampling frequency
    verbose  : print progress

    Returns
    -------
    df      : full merged DataFrame
    meta    : dict with calibration parameters and dataset statistics
    """
    if verbose:
        print(f"  Building OHLC bars ({bar_freq}) …", flush=True)

    # ── Step 1+2+3: Signals pipeline (unchanged) ───────────────────────────
    ohlc, raw_signals, normalized_signals, composite = build_signals_from_ticks(
        ticks, freq=bar_freq
    )
    if verbose:
        print(f"    OHLC bars: {len(ohlc):,}  |  composite bars: {len(composite):,}")

    # ── Step 4: V12 engine (unchanged) ────────────────────────────────────
    if verbose:
        print("  Running V12 engine …", flush=True)
    scaled_signals, scale_params = scale_signals_to_100(raw_signals)
    v12_composite, scale_factor = build_v12_composite(scaled_signals)
    v12_df = run_v12(v12_composite)
    if verbose:
        fw_frac = (v12_df['phase'] == 'FIREWALL').mean()
        print(f"    V12: {len(v12_df):,} bars  |  FIREWALL fraction: {fw_frac:.3f}")

    # ── Step 5: Transport layer (NEW) ──────────────────────────────────────
    if verbose:
        print(f"  Computing transport field (c={c}, τ={tau}) …", flush=True)
    transport_df = compute_transport_from_series(composite, c=c, tau=tau)
    if verbose:
        coh_frac = (transport_df['Q'] > 0).mean()
        print(f"    Transport: Q coherent fraction = {coh_frac:.3f}")

    # ── Step 6: Merge all quantities ───────────────────────────────────────
    # Align on the composite index (which is a subset of ohlc)
    df = ohlc.copy()

    # Add V12 columns (align on index)
    for col in ['T_sys', 'phase', 'excitation']:
        df[col] = v12_df[col].reindex(df.index)

    # Add transport columns (align on index)
    for col in transport_df.columns:
        df[f'tr_{col}'] = transport_df[col].reindex(df.index)

    # Add normalized composite (sigmoid output)
    df['composite_norm'] = composite.reindex(df.index)

    # Add per-signal columns
    for sig_name, sig_series in normalized_signals.items():
        df[f'sig_{sig_name}'] = sig_series.reindex(df.index)

    # ── Step 7: Future returns ─────────────────────────────────────────────
    if verbose:
        print("  Computing future returns …", flush=True)
    for h in [5, 10, 20, 50]:
        df[f'ret_{h}b'] = df['close'].shift(-h) / df['close'] - 1.0
        df[f'abs_ret_{h}b'] = df[f'ret_{h}b'].abs()

    # Current-bar return
    df['ret_1b'] = df['close'].pct_change()

    # ── Step 8: Technical indicators for cross-correlation ────────────────
    if verbose:
        print("  Computing technical indicators …", flush=True)

    # ATR (Average True Range, 14-bar)
    high = df['high']
    low  = df['low']
    prev_close = df['close'].shift(1)
    tr1  = high - low
    tr2  = (high - prev_close).abs()
    tr3  = (low  - prev_close).abs()
    tr   = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
    df['atr_14'] = tr.rolling(14).mean()

    # RSI (14-bar)
    delta  = df['close'].diff()
    gain   = delta.clip(lower=0).rolling(14).mean()
    loss   = (-delta.clip(upper=0)).rolling(14).mean()
    rs     = gain / (loss + 1e-10)
    df['rsi_14'] = 100.0 - 100.0 / (1.0 + rs)

    # MACD (12/26/9)
    ema12       = df['close'].ewm(span=12, adjust=False).mean()
    ema26       = df['close'].ewm(span=26, adjust=False).mean()
    df['macd']  = ema12 - ema26
    df['macd_signal'] = df['macd'].ewm(span=9, adjust=False).mean()
    df['macd_hist']   = df['macd'] - df['macd_signal']

    # ADX proxy (14-bar Wilder-smoothed directional index)
    plus_dm  = high.diff().clip(lower=0)
    minus_dm = (-low.diff()).clip(lower=0)
    # Set DM to 0 where opposite is larger
    plus_dm  = plus_dm.where(plus_dm > minus_dm, 0.0)
    minus_dm = minus_dm.where(minus_dm > plus_dm, 0.0)
    tr_smooth      = tr.rolling(14).sum()
    plus_di        = 100.0 * plus_dm.rolling(14).sum() / (tr_smooth + 1e-10)
    minus_di       = 100.0 * minus_dm.rolling(14).sum() / (tr_smooth + 1e-10)
    dx             = 100.0 * (plus_di - minus_di).abs() / (plus_di + minus_di + 1e-10)
    df['adx_14']   = dx.rolling(14).mean()

    # Realized volatility (20-bar rolling std of log returns)
    log_ret = np.log(df['close'] / df['close'].shift(1))
    df['realized_vol_20'] = log_ret.rolling(20).std()
    df['realized_vol_5']  = log_ret.rolling(5).std()

    # Volume normalized
    df['vol_norm'] = df['volume'] / (df['volume'].rolling(50).mean() + 1e-10)

    # Drawdown from rolling 20-bar high
    roll_high = df['close'].rolling(20).max()
    df['drawdown_20'] = (df['close'] - roll_high) / (roll_high + 1e-10)

    # Trend strength: slope of 20-bar linear regression normalized by ATR
    df['trend_strength'] = _rolling_lr_slope(df['close'].values, window=20) / (df['atr_14'] + 1e-10)

    # ── Rename transport columns for cleaner access ────────────────────────
    # Primary columns of interest:
    #   tr_Q         : Q values
    #   tr_regime    : +1/-1
    #   tr_regime_str: 'COHERENT'/'INCOHERENT'
    #   tr_s_transport: PDE-evolved field
    #   tr_Q_abs     : |Q|
    #   tr_xi_c      : coherence length (constant)
    #   tr_grad_ln_s : log-gradient

    # ── Metadata ──────────────────────────────────────────────────────────
    calib = TransportCalibration(c=c, tau=tau)
    meta = {
        'calibration'     : calib.describe(),
        'n_bars'          : len(df),
        'n_ticks'         : len(ticks),
        'date_range'      : (str(df.index.min()), str(df.index.max())),
        'v12_scale_factor': float(scale_factor),
        'coherent_fraction': float((df['tr_Q'] > 0).mean()),
        'bar_freq'        : bar_freq,
        'scale_params'    : {k: {kk: float(vv) for kk, vv in v.items()}
                             for k, v in scale_params.items()},
    }

    if verbose:
        print(f"  Pipeline complete: {len(df):,} bars, "
              f"{df.index.min().date()} → {df.index.max().date()}")

    return df, meta


def _rolling_lr_slope(arr: np.ndarray, window: int) -> pd.Series:
    """Compute rolling linear regression slope via vectorized operations."""
    result = np.full(len(arr), np.nan)
    x      = np.arange(window, dtype=np.float64)
    x_mean = x.mean()
    x_var  = ((x - x_mean) ** 2).sum()
    for i in range(window, len(arr) + 1):
        y      = arr[i - window: i]
        valid  = ~np.isnan(y)
        if valid.sum() < window // 2:
            continue
        y_mean  = y[valid].mean()
        cov     = ((x[valid] - x_mean) * (y[valid] - y_mean)).sum()
        result[i - 1] = cov / (x_var + 1e-12)
    return pd.Series(result)


# ─────────────────────────────────────────────────────────────────────────────
# Per-year pipeline convenience wrapper
# ─────────────────────────────────────────────────────────────────────────────

def build_yearly_datasets(
    ticks: pd.DataFrame,
    c: float = DEFAULT_C,
    tau: float = DEFAULT_TAU,
    verbose: bool = True,
) -> Dict[str, Tuple[pd.DataFrame, dict]]:
    """
    Run the full pipeline separately per year AND combined.

    Returns
    -------
    dict with keys '2023', '2024', '2025', 'all'
    Each value is (df, meta).
    """
    results = {}

    # Per-year splits
    years = sorted(ticks['timestamp'].dt.year.unique())
    for yr in years:
        yr_ticks = ticks[ticks['timestamp'].dt.year == yr].copy()
        if len(yr_ticks) < 1000:
            continue
        if verbose:
            print(f"\n── Year {yr}: {len(yr_ticks):,} ticks ──")
        try:
            df, meta = build_full_pipeline(yr_ticks, c=c, tau=tau, verbose=verbose)
            df['year'] = yr
            results[str(yr)] = (df, meta)
        except Exception as e:
            print(f"  WARNING: Year {yr} failed: {e}")

    # Full combined dataset
    if verbose:
        print(f"\n── Full dataset: {len(ticks):,} ticks ──")
    df_all, meta_all = build_full_pipeline(ticks, c=c, tau=tau, verbose=verbose)
    df_all['year'] = df_all.index.year
    results['all'] = (df_all, meta_all)

    return results


# ─────────────────────────────────────────────────────────────────────────────
# Quick summary of transport-augmented DataFrame
# ─────────────────────────────────────────────────────────────────────────────

def transport_summary(df: pd.DataFrame) -> dict:
    """Return a summary dict of the transport field statistics."""
    Q = df['tr_Q'].dropna().values
    return {
        'n_bars'             : len(df),
        'n_valid_Q'          : int(np.sum(~np.isnan(df['tr_Q'].values))),
        'coherent_fraction'  : float((Q > 0).mean()),
        'incoherent_fraction': float((Q < 0).mean()),
        'mean_Q'             : float(Q.mean()),
        'std_Q'              : float(Q.std()),
        'median_Q'           : float(np.median(Q)),
        'min_Q'              : float(Q.min()),
        'max_Q'              : float(Q.max()),
        'q05_Q'              : float(np.percentile(Q, 5)),
        'q25_Q'              : float(np.percentile(Q, 25)),
        'q75_Q'              : float(np.percentile(Q, 75)),
        'q95_Q'              : float(np.percentile(Q, 95)),
        'xi_c'               : float(df['tr_xi_c'].iloc[0]),
        'date_start'         : str(df.index.min()),
        'date_end'           : str(df.index.max()),
    }
