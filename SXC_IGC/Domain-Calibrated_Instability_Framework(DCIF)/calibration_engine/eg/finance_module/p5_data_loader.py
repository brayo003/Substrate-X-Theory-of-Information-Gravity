"""
p5_data_loader.py — Phase 5 Out-of-Sample Data Loader.

Loads and prepares 2026 data for all 7 markets.
Applies the FROZEN transport Q computation — no refit, no recalibration.

ABSOLUTE RULE: Q thresholds, transport equations, and all parameters are
IMMUTABLE. This is pure out-of-sample replay.

Markets: EURUSD, BTCUSDT, ETHUSDT, NAS100, XAUUSD, USOIL, UKOIL
Data range: 2026-01-01 to current (2026-07-22)
"""

import sys
import gc
import json
import warnings
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import numpy as np
import pandas as pd

warnings.filterwarnings("ignore")

_HERE = Path(__file__).resolve().parent
_CE   = _HERE.parents[1]
for p in [str(_CE), str(_HERE), str(_HERE / "v12_validate")]:
    if p not in sys.path:
        sys.path.insert(0, p)

# ── IMMUTABLE Phase 2 imports ─────────────────────────────────────────────
from p2_transport_os import classify_q_global_p2, COMMISSION_RT, BASE_RISK_PCT

# ── Transport layer (IMMUTABLE) ───────────────────────────────────────────
from v12_validate.transport_layer import (
    compute_transport_from_series,
    DEFAULT_C,
    DEFAULT_TAU,
)

# ── FROZEN Q thresholds (Phase 1 / Phase 2 derived, NEVER refit) ─────────
Q05_FROZEN = -1.0
Q95_FROZEN =  1.73

MARKET_ORDER = ["EURUSD", "BTCUSDT", "ETHUSDT", "NAS100", "XAUUSD", "USOIL", "UKOIL"]

DATA_DIR   = _HERE / "data"
PHASE5_DIR = _HERE / "results" / "phase5"
CACHE_DIR  = PHASE5_DIR / "cache"

YEAR_2026 = 2026


def ensure_dirs():
    PHASE5_DIR.mkdir(parents=True, exist_ok=True)
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    (PHASE5_DIR / "plots").mkdir(exist_ok=True)


# ═══════════════════════════════════════════════════════════════════════════
# Technical indicator builder (IDENTICAL to phase3_runner._add_indicators)
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
    mask = plus_dm < minus_dm;   plus_dm[mask] = 0.0
    mask2 = minus_dm < plus_dm;  minus_dm[mask2] = 0.0
    atr_s    = tr.ewm(span=14, adjust=False).mean()
    plus_di  = 100 * plus_dm.ewm(span=14, adjust=False).mean()  / (atr_s + 1e-12)
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
    df["vwap"] = (typical * df["volume"]).rolling(20).sum() / (df["volume"].rolling(20).sum() + 1e-12)

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

    df["roc_10"] = close.pct_change(10) * 100
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
# Composite builder (IDENTICAL to phase3_runner._build_composite_from_ohlc)
# ═══════════════════════════════════════════════════════════════════════════

def _build_composite(df: pd.DataFrame) -> pd.Series:
    close = df["close"]
    signals = pd.DataFrame(index=df.index)

    rsi = df.get("rsi_14", pd.Series(50.0, index=df.index))
    signals["s_rsi"] = (rsi - 50.0) / 50.0

    macd = df.get("macd", pd.Series(0.0, index=df.index))
    macd_std = macd.std()
    signals["s_macd"] = macd / (macd_std + 1e-12) if macd_std > 0 else macd * 0

    atr = df.get("atr_14", pd.Series(1.0, index=df.index))
    atr_mean = atr.rolling(50).mean().fillna(atr)
    signals["s_atr"] = (atr / (atr_mean + 1e-12) - 1.0).clip(-2, 2) / 2.0

    roc = df.get("roc_10", close.pct_change(10) * 100)
    roc_std = roc.std()
    signals["s_mom"] = roc / (roc_std * 10 + 1e-12) if roc_std > 0 else roc * 0

    bb_upper = df.get("bb_upper", close.rolling(20).mean() + 2*close.rolling(20).std())
    bb_lower = df.get("bb_lower", close.rolling(20).mean() - 2*close.rolling(20).std())
    bb_range = (bb_upper - bb_lower).replace(0, np.nan)
    signals["s_bb"] = ((close - bb_lower) / bb_range - 0.5) * 2

    adx = df.get("adx_14", pd.Series(25.0, index=df.index))
    signals["s_adx"] = (adx / 50.0 - 0.5)

    comp = signals.mean(axis=1).fillna(0.0)
    comp_std = comp.rolling(100, min_periods=20).std().fillna(1.0)
    comp_norm = (comp / (comp_std + 1e-12)).clip(-3, 3) / 3.0
    return comp_norm.rename("composite")


# ═══════════════════════════════════════════════════════════════════════════
# FROZEN transport pipeline (apply Q, do not refit thresholds)
# ═══════════════════════════════════════════════════════════════════════════

def _apply_frozen_transport(df: pd.DataFrame) -> pd.DataFrame:
    """
    Apply the IMMUTABLE transport layer to an OHLC DataFrame.
    Q thresholds are FROZEN at Phase 1 values (Q05=-1.0, Q95=1.73).
    """
    df = df.copy()
    df = _add_indicators(df)
    composite = _build_composite(df)

    # IMMUTABLE transport computation
    transport_df = compute_transport_from_series(composite, c=DEFAULT_C, tau=DEFAULT_TAU)
    for col in transport_df.columns:
        df[f"tr_{col}"] = transport_df[col].reindex(df.index)

    df["composite_norm"] = composite.reindex(df.index)

    # FROZEN regime classification — NO REFIT
    df["regime"] = df["tr_Q"].apply(
        lambda q: classify_q_global_p2(q, Q05_FROZEN, Q95_FROZEN)
    )

    return df


# ═══════════════════════════════════════════════════════════════════════════
# Market-specific 2026 loaders
# ═══════════════════════════════════════════════════════════════════════════

def _load_eurusd_2026() -> pd.DataFrame:
    """
    Load 2026 EURUSD M1 data from the 2026 folder and aggregate to 5-min bars.
    Uses the same CSV format as the existing 2026 download script.
    """
    data_2026 = DATA_DIR / "2026"
    csv_files = sorted(data_2026.glob("eurusd-m1-bid-2026*.csv"))
    if not csv_files:
        raise FileNotFoundError(f"No EURUSD 2026 CSV files found in {data_2026}")

    frames = []
    for fp in csv_files:
        try:
            df = pd.read_csv(fp, header=None)
            if df.shape[1] >= 6:
                df = df.iloc[:, :6]
                df.columns = ["timestamp", "open", "high", "low", "close", "volume"]
            elif df.shape[1] >= 5:
                df = df.iloc[:, :5]
                df.columns = ["timestamp", "open", "high", "low", "close"]
                df["volume"] = 1.0
            else:
                # Try with header
                df = pd.read_csv(fp)
                df.columns = [c.lower().strip() for c in df.columns]

            for col in ["open", "high", "low", "close"]:
                if col in df.columns:
                    df[col] = pd.to_numeric(df[col], errors="coerce")

            # Parse timestamp
            if "timestamp" in df.columns:
                ts_series = pd.to_datetime(df["timestamp"], errors="coerce", utc=True)
                if ts_series.isna().all():
                    # Try numeric ms
                    ts_series = pd.to_datetime(
                        pd.to_numeric(df["timestamp"], errors="coerce"),
                        unit="ms", utc=True, errors="coerce"
                    )
                df["timestamp"] = ts_series

            df = df.dropna(subset=["timestamp", "open", "close"])
            df = df.set_index("timestamp").sort_index()
            # Filter 2026 only
            df = df[df.index.year == 2026]
            if len(df) > 0:
                frames.append(df[["open", "high", "low", "close", "volume"]])
        except Exception as e:
            print(f"  WARNING loading {fp.name}: {e}")
            continue

    if not frames:
        raise ValueError("No valid EURUSD 2026 data loaded")

    raw = pd.concat(frames).sort_index()
    raw = raw[~raw.index.duplicated(keep="first")]

    # Resample to 5-min
    ohlc = raw.resample("5min").agg({
        "open":   "first",
        "high":   "max",
        "low":    "min",
        "close":  "last",
        "volume": "sum",
    }).dropna(subset=["open", "close"])

    ohlc = ohlc[ohlc.index.year == 2026]
    print(f"  EURUSD 2026: {len(raw)} M1 bars → {len(ohlc)} 5-min bars", flush=True)
    return ohlc


def _load_crypto_2026(symbol: str) -> pd.DataFrame:
    """Load 2026 Binance 1-min CSVs for BTC or ETH → 5-min bars."""
    market_dir = DATA_DIR / symbol
    # Only 2026 files
    csv_files = sorted(market_dir.glob(f"{symbol}-1m-2026-*.csv"))
    if not csv_files:
        raise FileNotFoundError(f"No 2026 {symbol} CSVs found in {market_dir}")

    frames = []
    for fp in csv_files:
        try:
            chunk = pd.read_csv(fp, header=None, dtype=str)
            chunk = chunk.iloc[:, :6]
            chunk.columns = ["ts_us", "open", "high", "low", "close", "volume"]
            for col in ["ts_us", "open", "high", "low", "close", "volume"]:
                chunk[col] = pd.to_numeric(chunk[col], errors="coerce")
            chunk = chunk.dropna(subset=["ts_us", "open", "close"])
            ts_ms = (chunk["ts_us"] / 1000).astype("int64")
            chunk["timestamp"] = pd.to_datetime(ts_ms, unit="ms", utc=True)
            chunk = chunk.drop(columns=["ts_us"]).set_index("timestamp")
            chunk = chunk[chunk.index.year == 2026]
            frames.append(chunk)
        except Exception as e:
            print(f"  WARNING loading {fp.name}: {e}")
            continue

    if not frames:
        raise ValueError(f"No valid 2026 {symbol} data loaded")

    raw = pd.concat(frames).sort_index()
    raw = raw[~raw.index.duplicated(keep="first")]

    ohlc = raw.resample("5min").agg({
        "open":   "first",
        "high":   "max",
        "low":    "min",
        "close":  "last",
        "volume": "sum",
    }).dropna(subset=["open", "close"])

    ohlc = ohlc[ohlc.index.year == 2026]
    print(f"  {symbol} 2026: {len(raw)} 1-min bars → {len(ohlc)} 5-min bars", flush=True)
    return ohlc


def _load_csv_daily_2026(symbol: str, data_subdir: str) -> pd.DataFrame:
    """Load 2026 daily CSV for NAS100, USOIL, UKOIL, XAUUSD."""
    market_dir = DATA_DIR / data_subdir
    # Look for 2026 files
    csv_files = sorted(market_dir.glob("*2026*.csv"))
    if not csv_files:
        # Fall back to any CSV with 2026 data
        csv_files = sorted(market_dir.glob("*.csv"))
    if not csv_files:
        raise FileNotFoundError(f"No 2026 CSV files found for {symbol} in {market_dir}")

    frames = []
    for fp in csv_files:
        try:
            df = pd.read_csv(fp)
            df.columns = [c.lower().strip() for c in df.columns]
            # Detect timestamp/date column
            ts_col = None
            for candidate in ["timestamp", "date", "time", "datetime"]:
                if candidate in df.columns:
                    ts_col = candidate
                    break
            if ts_col is None:
                ts_col = df.columns[0]

            try:
                ts = pd.to_datetime(df[ts_col], unit="ms", utc=True, errors="coerce")
                if ts.isna().mean() > 0.5:
                    ts = pd.to_datetime(df[ts_col], utc=True, errors="coerce")
            except Exception:
                ts = pd.to_datetime(df[ts_col], utc=True, errors="coerce")

            df["timestamp"] = ts
            df = df.dropna(subset=["timestamp"])
            df = df.set_index("timestamp").sort_index()

            for col in ["open", "high", "low", "close"]:
                if col in df.columns:
                    df[col] = pd.to_numeric(df[col], errors="coerce")

            if "volume" not in df.columns:
                df["volume"] = 1.0

            # Filter 2026 only
            df = df[df.index.year == 2026]
            if len(df) > 0:
                keep = [c for c in ["open", "high", "low", "close", "volume"] if c in df.columns]
                frames.append(df[keep].dropna(subset=["open", "close"]))
        except Exception as e:
            print(f"  WARNING loading {fp.name}: {e}")
            continue

    if not frames:
        raise ValueError(f"No valid 2026 {symbol} data loaded")

    df = pd.concat(frames).sort_index()
    df = df[~df.index.duplicated(keep="first")]
    df = df.dropna(subset=["open", "close"])
    # Shift to 13:30 UTC for session-gated strategies
    df.index = df.index.normalize() + pd.Timedelta(hours=13, minutes=30)
    print(f"  {symbol} 2026: {len(df)} daily bars (→ 13:30 UTC)", flush=True)
    return df


def _load_xauusd_2026() -> pd.DataFrame:
    """Load 2026 XAUUSD daily CSV data."""
    market_dir = DATA_DIR / "XAUUSD"
    csv_files = sorted(market_dir.glob("*2026*.csv"))
    if not csv_files:
        csv_files = sorted(market_dir.glob("*.csv"))
    if not csv_files:
        # Fallback: check JSON
        json_files = sorted(market_dir.glob("*2026*.json"))
        if json_files:
            return _load_xauusd_json_2026(json_files)
        raise FileNotFoundError(f"No 2026 XAUUSD data found in {market_dir}")

    return _load_csv_daily_2026("XAUUSD", "XAUUSD")


def _load_xauusd_json_2026(json_files) -> pd.DataFrame:
    frames = []
    for fp in json_files:
        try:
            with open(fp) as f:
                data = json.load(f)
            if isinstance(data, list):
                df = pd.DataFrame(data)
            elif isinstance(data, dict) and "data" in data:
                df = pd.DataFrame(data["data"])
            else:
                df = pd.DataFrame(data)
            df.columns = [c.lower() for c in df.columns]
            df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms", utc=True)
            df = df.set_index("timestamp")
            for col in ["open", "high", "low", "close"]:
                df[col] = pd.to_numeric(df[col], errors="coerce")
            df["volume"] = 1.0
            df = df[df.index.year == 2026]
            if len(df) > 0:
                frames.append(df[["open", "high", "low", "close", "volume"]])
        except Exception as e:
            print(f"  WARNING loading {fp.name}: {e}")
    if not frames:
        raise ValueError("No valid XAUUSD 2026 JSON data")
    df = pd.concat(frames).sort_index()
    df = df[~df.index.duplicated(keep="first")]
    df.index = df.index.normalize() + pd.Timedelta(hours=13, minutes=30)
    return df


# ═══════════════════════════════════════════════════════════════════════════
# Master loader
# ═══════════════════════════════════════════════════════════════════════════

MARKET_LOADERS_2026 = {
    "EURUSD":  _load_eurusd_2026,
    "BTCUSDT": lambda: _load_crypto_2026("BTCUSDT"),
    "ETHUSDT": lambda: _load_crypto_2026("ETHUSDT"),
    "XAUUSD":  _load_xauusd_2026,
    "NAS100":  lambda: _load_csv_daily_2026("NAS100", "NAS100"),
    "USOIL":   lambda: _load_csv_daily_2026("USOIL", "USOIL"),
    "UKOIL":   lambda: _load_csv_daily_2026("UKOIL", "UKOIL"),
}


def load_and_prepare_2026(symbol: str, use_cache: bool = True, verbose: bool = True) -> pd.DataFrame:
    """
    Load 2026 raw data, apply FROZEN transport pipeline, return prepared DataFrame.
    No refitting. No lookahead. Pure out-of-sample.
    """
    ensure_dirs()
    cache_path = CACHE_DIR / f"prepared_2026_{symbol}.parquet"

    if use_cache and cache_path.exists():
        df = pd.read_parquet(cache_path)
        if verbose:
            print(f"  [{symbol}] Loaded from cache: {len(df)} bars, "
                  f"regime dist: " + " | ".join(
                      f"{r[:4]}={v}" for r, v in df["regime"].value_counts().items()
                  ), flush=True)
        return df

    if verbose:
        print(f"\n  [{symbol}] Loading 2026 raw data …", flush=True)

    loader = MARKET_LOADERS_2026.get(symbol)
    if loader is None:
        raise ValueError(f"Unknown market: {symbol}")

    raw = loader()
    if len(raw) == 0:
        raise ValueError(f"Empty data for {symbol}")

    if verbose:
        print(f"  [{symbol}] Applying frozen transport pipeline …", flush=True)

    prepared = _apply_frozen_transport(raw)
    prepared = prepared.dropna(subset=["tr_Q"])

    if verbose:
        n_bars = len(prepared)
        regime_counts = prepared["regime"].value_counts()
        print(f"  [{symbol}] {n_bars} bars with Q computed.", flush=True)
        for r, v in regime_counts.items():
            print(f"    {r}: {v} ({100*v/n_bars:.1f}%)", flush=True)

    prepared.to_parquet(cache_path)
    return prepared


def load_all_markets_2026(
    markets: List[str] = None,
    use_cache: bool = True,
    verbose: bool = True,
) -> Dict[str, pd.DataFrame]:
    """Load and prepare 2026 data for all (or specified) markets."""
    if markets is None:
        markets = MARKET_ORDER

    ensure_dirs()
    result: Dict[str, pd.DataFrame] = {}
    failed: List[str] = []

    for sym in markets:
        try:
            df = load_and_prepare_2026(sym, use_cache=use_cache, verbose=verbose)
            result[sym] = df
        except Exception as e:
            print(f"  [{sym}] ERROR: {e}", flush=True)
            failed.append(sym)

    if failed:
        print(f"\n  WARNING: Failed markets: {failed}", flush=True)

    return result


def get_q_stats_2026(df: pd.DataFrame) -> Dict:
    """Compute Q distribution statistics for a 2026 prepared DataFrame."""
    q = df["tr_Q"].dropna()
    if len(q) == 0:
        return {}
    return {
        "q_mean":    float(q.mean()),
        "q_std":     float(q.std()),
        "q_median":  float(q.median()),
        "q_5pct":    float(q.quantile(0.05)),
        "q_95pct":   float(q.quantile(0.95)),
        "q_entropy": float(_shannon_entropy(q)),
        "q_coherent_frac": float((q > 0).mean()),
        "q_incoherent_frac": float((q < 0).mean()),
        "n_bars":    int(len(q)),
    }


def _shannon_entropy(series: pd.Series, n_bins: int = 50) -> float:
    """Shannon entropy of Q distribution."""
    counts, _ = np.histogram(series.values, bins=n_bins)
    probs = counts / (counts.sum() + 1e-12)
    probs = probs[probs > 0]
    return float(-np.sum(probs * np.log(probs + 1e-12)))


if __name__ == "__main__":
    print("Phase 5 — Data Loader Test")
    data = load_all_markets_2026(verbose=True)
    print(f"\nLoaded {len(data)} markets:")
    for sym, df in data.items():
        q_stats = get_q_stats_2026(df)
        print(f"  {sym}: {len(df)} bars | Q_mean={q_stats.get('q_mean', 0):.3f} | "
              f"coherent={q_stats.get('q_coherent_frac',0):.1%}")
