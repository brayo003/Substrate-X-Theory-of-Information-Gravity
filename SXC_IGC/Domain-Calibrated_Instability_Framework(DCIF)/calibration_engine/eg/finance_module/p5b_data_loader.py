"""
p5b_data_loader.py — Phase 5B Intraday Data Loader.

Loads 2026 M1 data for the 4 markets that needed correction in Phase 5:
  EURUSD  — was excluded due to parser incompatibility
  XAUUSD  — was only daily bars (statistically insignificant)
  USOIL   — was only daily bars
  UKOIL   — was only daily bars

All 4 CSV files share the same format:
  timestamp (unix ms), open, high, low, close   [no volume column]

Aggregation: M1 → 5-min bars (same as BTC/ETH in Phase 5).

ABSOLUTE RULE: Q thresholds, transport equations, and all parameters
are IMMUTABLE. This is pure out-of-sample replay on improved data.
"""

import sys
import warnings
from pathlib import Path
from typing import Dict, Optional

import numpy as np
import pandas as pd

warnings.filterwarnings("ignore")

_HERE = Path(__file__).resolve().parent
for p in [str(_HERE), str(_HERE / "v12_validate")]:
    if p not in sys.path:
        sys.path.insert(0, p)

# ── IMMUTABLE Phase 2 imports ─────────────────────────────────────────────
from p2_transport_os import classify_q_global_p2

# ── Transport layer (IMMUTABLE) ───────────────────────────────────────────
from v12_validate.transport_layer import (
    compute_transport_from_series,
    DEFAULT_C,
    DEFAULT_TAU,
)

# ── FROZEN Q thresholds (NEVER refit) ────────────────────────────────────
Q05_FROZEN = -1.0
Q95_FROZEN =  1.73

DATA_DIR    = _HERE / "data"
PHASE5B_DIR = _HERE / "results" / "phase5b"

# Map: symbol → (data_subdir, glob_pattern)
_M1_FILE_MAP = {
    "EURUSD": (DATA_DIR / "2026",   "eurusd-m1-bid-2026*.csv"),
    "XAUUSD": (DATA_DIR / "XAUUSD", "xauusd-m1-bid-2026*.csv"),
    "USOIL":  (DATA_DIR / "USOIL",  "lightcmdusd-m1-bid-2026*.csv"),
    "UKOIL":  (DATA_DIR / "UKOIL",  "brentcmdusd-m1-bid-2026*.csv"),
}


def ensure_dirs():
    PHASE5B_DIR.mkdir(parents=True, exist_ok=True)
    (PHASE5B_DIR / "cache").mkdir(exist_ok=True)
    (PHASE5B_DIR / "plots").mkdir(exist_ok=True)


# ═══════════════════════════════════════════════════════════════════════════
# Shared M1 CSV loader
# All 4 files have: timestamp(unix ms),open,high,low,close  WITH header row
# ═══════════════════════════════════════════════════════════════════════════

def _load_m1_csv(symbol: str, data_dir: Path, glob_pattern: str) -> pd.DataFrame:
    """
    Load M1 CSV file(s) with format: timestamp_ms, open, high, low, close.
    Aggregates to 5-min bars. Returns OHLCV DataFrame with UTC DatetimeIndex.
    """
    csv_files = sorted(data_dir.glob(glob_pattern))
    if not csv_files:
        raise FileNotFoundError(
            f"No M1 files found for {symbol} in {data_dir} matching {glob_pattern}"
        )

    frames = []
    for fp in csv_files:
        try:
            # These files have a header: timestamp,open,high,low,close
            df = pd.read_csv(fp)
            df.columns = [c.lower().strip() for c in df.columns]

            # Identify timestamp column
            ts_col = next(
                (c for c in ["timestamp", "date", "time", "datetime"] if c in df.columns),
                df.columns[0]
            )

            # Parse timestamp — values are unix milliseconds
            ts_raw = pd.to_numeric(df[ts_col], errors="coerce")
            ts = pd.to_datetime(ts_raw, unit="ms", utc=True, errors="coerce")

            # Fallback: try string parsing if numeric failed
            if ts.isna().mean() > 0.5:
                ts = pd.to_datetime(df[ts_col], utc=True, errors="coerce")

            df["timestamp"] = ts
            df = df.dropna(subset=["timestamp"])

            for col in ["open", "high", "low", "close"]:
                if col in df.columns:
                    df[col] = pd.to_numeric(df[col], errors="coerce")

            if "volume" not in df.columns:
                df["volume"] = 1.0

            df = df.set_index("timestamp").sort_index()
            df = df[df.index.year == 2026]
            df = df.dropna(subset=["open", "close"])

            keep = [c for c in ["open", "high", "low", "close", "volume"] if c in df.columns]
            if len(df) > 0:
                frames.append(df[keep])
                print(f"    {fp.name}: {len(df):,} M1 bars", flush=True)

        except Exception as e:
            print(f"  WARNING loading {fp.name}: {e}", flush=True)
            continue

    if not frames:
        raise ValueError(f"No valid 2026 M1 data loaded for {symbol}")

    raw = pd.concat(frames).sort_index()
    raw = raw[~raw.index.duplicated(keep="first")]

    # Aggregate M1 → 5-min
    ohlc = raw.resample("5min").agg({
        "open":   "first",
        "high":   "max",
        "low":    "min",
        "close":  "last",
        "volume": "sum",
    }).dropna(subset=["open", "close"])

    ohlc = ohlc[ohlc.index.year == 2026]
    print(f"  {symbol} 2026: {len(raw):,} M1 bars → {len(ohlc):,} 5-min bars", flush=True)
    return ohlc


# ═══════════════════════════════════════════════════════════════════════════
# Technical indicators (IDENTICAL to p5_data_loader._add_indicators)
# ═══════════════════════════════════════════════════════════════════════════

def _add_indicators(df: pd.DataFrame) -> pd.DataFrame:
    close = df["close"]
    high  = df["high"]
    low   = df["low"]

    prev_close = close.shift(1)
    tr = pd.concat([
        high - low,
        (high - prev_close).abs(),
        (low  - prev_close).abs(),
    ], axis=1).max(axis=1)
    df["atr_14"] = tr.ewm(span=14, adjust=False).mean()

    delta = close.diff()
    gain  = delta.clip(lower=0).ewm(span=14, adjust=False).mean()
    loss  = (-delta.clip(upper=0)).ewm(span=14, adjust=False).mean()
    rs    = gain / (loss + 1e-12)
    df["rsi_14"] = 100 - (100 / (1 + rs))

    ema12 = close.ewm(span=12, adjust=False).mean()
    ema26 = close.ewm(span=26, adjust=False).mean()
    df["macd"]        = ema12 - ema26
    df["macd_signal"] = df["macd"].ewm(span=9, adjust=False).mean()
    df["macd_hist"]   = df["macd"] - df["macd_signal"]

    plus_dm  = (high - high.shift(1)).clip(lower=0)
    minus_dm = (low.shift(1) - low).clip(lower=0)
    mask  = plus_dm < minus_dm;  plus_dm[mask]  = 0.0
    mask2 = minus_dm < plus_dm;  minus_dm[mask2] = 0.0
    atr_s    = tr.ewm(span=14, adjust=False).mean()
    plus_di  = 100 * plus_dm.ewm(span=14,  adjust=False).mean() / (atr_s + 1e-12)
    minus_di = 100 * minus_dm.ewm(span=14, adjust=False).mean() / (atr_s + 1e-12)
    dx = 100 * (plus_di - minus_di).abs() / (plus_di + minus_di + 1e-12)
    df["adx_14"] = dx.ewm(span=14, adjust=False).mean()

    df["realized_vol_20"] = close.pct_change().rolling(20).std()

    sma20 = close.rolling(20).mean()
    std20 = close.rolling(20).std()
    df["bb_upper"] = sma20 + 2 * std20
    df["bb_lower"] = sma20 - 2 * std20
    df["bb_mid"]   = sma20

    if "volume" not in df.columns:
        df["volume"] = 1.0
    typical = (high + low + close) / 3
    df["vwap"] = (
        (typical * df["volume"]).rolling(20).sum()
        / (df["volume"].rolling(20).sum() + 1e-12)
    )

    df["kc_upper"] = df["macd"].ewm(span=20, adjust=False).mean() + 1.5 * df["atr_14"]
    df["kc_lower"] = df["macd"].ewm(span=20, adjust=False).mean() - 1.5 * df["atr_14"]

    low14  = low.rolling(14).min()
    high14 = high.rolling(14).max()
    df["stoch_k"] = 100 * (close - low14) / (high14 - low14 + 1e-12)
    df["stoch_d"] = df["stoch_k"].rolling(3).mean()

    tp    = (high + low + close) / 3
    tp_ma = tp.rolling(20).mean()
    tp_sd = tp.rolling(20).apply(lambda x: np.mean(np.abs(x - np.mean(x))), raw=True)
    df["cci_20"] = (tp - tp_ma) / (0.015 * tp_sd + 1e-12)

    df["roc_10"]       = close.pct_change(10) * 100
    df["donchian_high"] = high.rolling(20).max()
    df["donchian_low"]  = low.rolling(20).min()
    df["supertrend_dir"] = np.where(close > close.shift(1), 1, -1)

    df["ema_9"]  = close.ewm(span=9,  adjust=False).mean()
    df["ema_21"] = close.ewm(span=21, adjust=False).mean()
    df["ema_50"] = close.ewm(span=50, adjust=False).mean()
    df["sma_20"] = close.rolling(20).mean()
    df["sma_50"] = close.rolling(50).mean()

    return df


# ═══════════════════════════════════════════════════════════════════════════
# Composite builder (IDENTICAL to p5_data_loader._build_composite)
# ═══════════════════════════════════════════════════════════════════════════

def _build_composite(df: pd.DataFrame) -> pd.Series:
    close   = df["close"]
    signals = pd.DataFrame(index=df.index)

    rsi = df.get("rsi_14", pd.Series(50.0, index=df.index))
    signals["s_rsi"] = (rsi - 50.0) / 50.0

    macd     = df.get("macd", pd.Series(0.0, index=df.index))
    macd_std = macd.std()
    signals["s_macd"] = macd / (macd_std + 1e-12) if macd_std > 0 else macd * 0

    atr      = df.get("atr_14", pd.Series(1.0, index=df.index))
    atr_mean = atr.rolling(50).mean().fillna(atr)
    signals["s_atr"] = (atr / (atr_mean + 1e-12) - 1.0).clip(-2, 2) / 2.0

    roc     = df.get("roc_10", close.pct_change(10) * 100)
    roc_std = roc.std()
    signals["s_mom"] = roc / (roc_std * 10 + 1e-12) if roc_std > 0 else roc * 0

    bb_upper = df.get("bb_upper", close.rolling(20).mean() + 2 * close.rolling(20).std())
    bb_lower = df.get("bb_lower", close.rolling(20).mean() - 2 * close.rolling(20).std())
    bb_range = (bb_upper - bb_lower).replace(0, np.nan)
    signals["s_bb"] = ((close - bb_lower) / bb_range - 0.5) * 2

    adx = df.get("adx_14", pd.Series(25.0, index=df.index))
    signals["s_adx"] = (adx / 50.0 - 0.5)

    comp      = signals.mean(axis=1).fillna(0.0)
    comp_std  = comp.rolling(100, min_periods=20).std().fillna(1.0)
    comp_norm = (comp / (comp_std + 1e-12)).clip(-3, 3) / 3.0
    return comp_norm.rename("composite")


# ═══════════════════════════════════════════════════════════════════════════
# FROZEN transport pipeline (IMMUTABLE — Q thresholds never refit)
# ═══════════════════════════════════════════════════════════════════════════

def _apply_frozen_transport(df: pd.DataFrame, symbol: str = "") -> pd.DataFrame:
    """
    Apply the IMMUTABLE transport layer to an OHLC DataFrame.
    Q thresholds are FROZEN at Phase 1 values (Q05=-1.0, Q95=1.73).
    """
    df = df.copy()
    df = _add_indicators(df)
    composite = _build_composite(df)

    transport_df = compute_transport_from_series(composite, c=DEFAULT_C, tau=DEFAULT_TAU)
    for col in transport_df.columns:
        df[f"tr_{col}"] = transport_df[col].reindex(df.index)

    df["composite_norm"] = composite.reindex(df.index)

    # FROZEN regime classification — Q thresholds NEVER refit
    df["regime"] = df["tr_Q"].apply(
        lambda q: classify_q_global_p2(q, Q05_FROZEN, Q95_FROZEN)
    )
    return df


# ═══════════════════════════════════════════════════════════════════════════
# Load + prepare individual markets
# ═══════════════════════════════════════════════════════════════════════════

def load_market_5b(symbol: str, verbose: bool = True) -> pd.DataFrame:
    """
    Load, aggregate and apply frozen transport pipeline to one market.
    Returns a prepared DataFrame ready for OS replay.
    """
    if symbol not in _M1_FILE_MAP:
        raise ValueError(f"Symbol {symbol} not in Phase 5B market set. "
                         f"Available: {list(_M1_FILE_MAP.keys())}")

    data_dir, glob_pattern = _M1_FILE_MAP[symbol]

    if verbose:
        print(f"\n  [{symbol}] Loading 2026 M1 data …", flush=True)

    raw_ohlc = _load_m1_csv(symbol, data_dir, glob_pattern)

    if verbose:
        print(f"  [{symbol}] Applying frozen transport pipeline …", flush=True)

    prepared = _apply_frozen_transport(raw_ohlc, symbol=symbol)

    # Report regime distribution
    regime_counts = prepared["regime"].value_counts()
    total = len(prepared)
    if verbose:
        for regime, cnt in regime_counts.items():
            print(f"    {regime}: {cnt:,} ({100*cnt/total:.1f}%)", flush=True)
        print(f"  [{symbol}] {total:,} bars prepared with Q.", flush=True)

    return prepared


def load_all_markets_5b(verbose: bool = True) -> Dict[str, pd.DataFrame]:
    """
    Load all 4 Phase 5B markets with M1 data.
    Returns {symbol: prepared_df} for EURUSD, XAUUSD, USOIL, UKOIL.
    """
    ensure_dirs()
    markets = list(_M1_FILE_MAP.keys())
    data: Dict[str, pd.DataFrame] = {}
    failed = []

    for sym in markets:
        try:
            data[sym] = load_market_5b(sym, verbose=verbose)
        except Exception as e:
            print(f"  WARNING: [{sym}] failed — {e}", flush=True)
            failed.append(sym)

    if failed:
        print(f"\n  WARNING: Failed markets: {failed}", flush=True)

    return data


def get_q_stats_5b(df: pd.DataFrame) -> dict:
    """Compute Q statistics for a prepared 5B DataFrame."""
    if df is None or len(df) == 0 or "tr_Q" not in df.columns:
        return {}
    q = df["tr_Q"].dropna()
    if len(q) == 0:
        return {}
    coherent_mask = df["regime"].isin(["Weak_Coherent", "Strong_Coherent"])
    return {
        "q_mean"          : float(q.mean()),
        "q_std"           : float(q.std()),
        "q_median"        : float(q.median()),
        "q_coherent_frac" : float(coherent_mask.mean()),
        "n_bars"          : len(df),
    }


# ═══════════════════════════════════════════════════════════════════════════
# CLI / test
# ═══════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    print("Phase 5B — Data Loader Test")
    data = load_all_markets_5b(verbose=True)
    print(f"\nLoaded {len(data)} markets:")
    for sym, df in data.items():
        stats = get_q_stats_5b(df)
        print(f"  {sym:8s}: {len(df):>8,} bars | "
              f"Q_mean={stats.get('q_mean', 0):+.3f} | "
              f"coherent={stats.get('q_coherent_frac', 0):.1%}")
