"""
phase3_runner.py — Universal market data loader and transport pipeline for Phase 3.

Supports:
  - BTCUSDT / ETHUSDT  : 1-min Binance CSVs → resample to 5-min → full pipeline
  - XAUUSD             : JSON daily OHLC → daily bars → transport pipeline
  - NAS100 / USOIL / UKOIL : CSV daily OHLC → daily bars → transport pipeline

The transport mathematics are IDENTICAL for every market.
Only data ingestion changes. Q thresholds are IMMUTABLE (q05=-1.0, q95=1.73).

All transport constants are imported directly from Phase 2 (NEVER re-calibrated).
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
from p2_transport_os import (
    classify_q_global_p2,
    BASE_RISK_PCT,
    COMMISSION_RT,
    REGIMES_5,
)
from p2_execution_engine import (
    run_transport_os_on_chunk,
    BarState,
    HOLD_BARS,
)

# ── Transport layer (IMMUTABLE) ───────────────────────────────────────────
from v12_validate.transport_layer import (
    compute_transport_from_series,
    DEFAULT_C,
    DEFAULT_TAU,
)

PHASE3_DIR = _HERE / "results" / "phase3"
DATA_DIR   = _HERE / "data"

# IMMUTABLE Q thresholds from Phase 2
Q05_GLOBAL = -1.0
Q95_GLOBAL =  1.73

# ═══════════════════════════════════════════════════════════════════════════
# Technical indicator builder (market-agnostic)
# ═══════════════════════════════════════════════════════════════════════════

def _add_indicators(df: pd.DataFrame) -> pd.DataFrame:
    """Add ATR, RSI, MACD, ADX, vol columns required by strategy library."""
    close = df["close"]
    high  = df["high"]
    low   = df["low"]

    # ATR-14
    prev_close = close.shift(1)
    tr = pd.concat([
        high - low,
        (high - prev_close).abs(),
        (low  - prev_close).abs(),
    ], axis=1).max(axis=1)
    df["atr_14"] = tr.ewm(span=14, adjust=False).mean()

    # RSI-14
    delta = close.diff()
    gain  = delta.clip(lower=0).ewm(span=14, adjust=False).mean()
    loss  = (-delta.clip(upper=0)).ewm(span=14, adjust=False).mean()
    rs    = gain / (loss + 1e-12)
    df["rsi_14"] = 100 - (100 / (1 + rs))

    # MACD
    ema12 = close.ewm(span=12, adjust=False).mean()
    ema26 = close.ewm(span=26, adjust=False).mean()
    df["macd"]        = ema12 - ema26
    df["macd_signal"] = df["macd"].ewm(span=9, adjust=False).mean()
    df["macd_hist"]   = df["macd"] - df["macd_signal"]

    # ADX-14
    plus_dm  = (high - high.shift(1)).clip(lower=0)
    minus_dm = (low.shift(1) - low).clip(lower=0)
    mask = plus_dm < minus_dm
    plus_dm[mask] = 0.0
    mask2 = minus_dm < plus_dm
    minus_dm[mask2] = 0.0
    atr_s  = tr.ewm(span=14, adjust=False).mean()
    plus_di  = 100 * plus_dm.ewm(span=14, adjust=False).mean()  / (atr_s + 1e-12)
    minus_di = 100 * minus_dm.ewm(span=14, adjust=False).mean() / (atr_s + 1e-12)
    dx = 100 * (plus_di - minus_di).abs() / (plus_di + minus_di + 1e-12)
    df["adx_14"] = dx.ewm(span=14, adjust=False).mean()

    # Realized volatility
    df["realized_vol_20"] = close.pct_change().rolling(20).std()

    # Bollinger Bands
    sma20 = close.rolling(20).mean()
    std20 = close.rolling(20).std()
    df["bb_upper"] = sma20 + 2 * std20
    df["bb_lower"] = sma20 - 2 * std20
    df["bb_mid"]   = sma20

    # VWAP proxy (rolling)
    if "volume" not in df.columns:
        df["volume"] = 1.0
    typical = (high + low + close) / 3
    df["vwap"] = (typical * df["volume"]).rolling(20).sum() / (df["volume"].rolling(20).sum() + 1e-12)

    # Keltner channels
    df["kc_upper"] = df["macd"].ewm(span=20, adjust=False).mean() + 1.5 * df["atr_14"]
    df["kc_lower"] = df["macd"].ewm(span=20, adjust=False).mean() - 1.5 * df["atr_14"]

    # Stochastic
    low14  = low.rolling(14).min()
    high14 = high.rolling(14).max()
    df["stoch_k"] = 100 * (close - low14) / (high14 - low14 + 1e-12)
    df["stoch_d"] = df["stoch_k"].rolling(3).mean()

    # CCI
    tp    = (high + low + close) / 3
    tp_ma = tp.rolling(20).mean()
    tp_sd = tp.rolling(20).apply(lambda x: np.mean(np.abs(x - np.mean(x))), raw=True)
    df["cci_20"] = (tp - tp_ma) / (0.015 * tp_sd + 1e-12)

    # ROC
    df["roc_10"] = close.pct_change(10) * 100

    # Donchian
    df["donchian_high"] = high.rolling(20).max()
    df["donchian_low"]  = low.rolling(20).min()

    # Supertrend proxy
    df["supertrend_dir"] = np.where(close > close.shift(1), 1, -1)

    # EMA series
    df["ema_9"]  = close.ewm(span=9,  adjust=False).mean()
    df["ema_21"] = close.ewm(span=21, adjust=False).mean()
    df["ema_50"] = close.ewm(span=50, adjust=False).mean()
    df["sma_20"] = close.rolling(20).mean()
    df["sma_50"] = close.rolling(50).mean()

    return df


def _build_composite_from_ohlc(df: pd.DataFrame) -> pd.Series:
    """
    Build a normalised composite signal from OHLC indicators.
    This is a simplified version of the full tick-based pipeline
    that works directly on OHLC bars. The composite is used only
    as input to the IMMUTABLE transport layer (compute_transport_from_series).
    The mathematics are identical — only the composite construction
    is adapted for OHLC-only data (no tick spreads available).
    """
    close = df["close"]
    n = len(df)
    signals = pd.DataFrame(index=df.index)

    # Signal 1: RSI normalised to [-1, 1]
    rsi = df.get("rsi_14", pd.Series(50.0, index=df.index))
    signals["s_rsi"] = (rsi - 50.0) / 50.0

    # Signal 2: MACD normalised
    macd = df.get("macd", pd.Series(0.0, index=df.index))
    macd_std = macd.std()
    signals["s_macd"] = macd / (macd_std + 1e-12) if macd_std > 0 else macd * 0

    # Signal 3: ATR ratio (current vs rolling mean)
    atr = df.get("atr_14", pd.Series(1.0, index=df.index))
    atr_mean = atr.rolling(50).mean().fillna(atr)
    signals["s_atr"] = (atr / (atr_mean + 1e-12) - 1.0).clip(-2, 2) / 2.0

    # Signal 4: Close momentum
    roc = df.get("roc_10", close.pct_change(10) * 100)
    roc_std = roc.std()
    signals["s_mom"] = roc / (roc_std * 10 + 1e-12) if roc_std > 0 else roc * 0

    # Signal 5: Bollinger band position
    bb_upper = df.get("bb_upper", close.rolling(20).mean() + 2*close.rolling(20).std())
    bb_lower = df.get("bb_lower", close.rolling(20).mean() - 2*close.rolling(20).std())
    bb_range = (bb_upper - bb_lower).replace(0, np.nan)
    signals["s_bb"] = ((close - bb_lower) / bb_range - 0.5) * 2

    # Signal 6: ADX (trend strength, scaled)
    adx = df.get("adx_14", pd.Series(25.0, index=df.index))
    signals["s_adx"] = (adx / 50.0 - 0.5)

    # Composite: equal-weight mean, then normalise to [-1, 1]
    comp = signals.mean(axis=1).fillna(0.0)
    comp_std = comp.rolling(100, min_periods=20).std().fillna(1.0)
    comp_norm = (comp / (comp_std + 1e-12)).clip(-3, 3) / 3.0

    return comp_norm.rename("composite")


def _apply_transport_to_ohlc(df: pd.DataFrame) -> pd.DataFrame:
    """
    Apply the IMMUTABLE transport layer to an OHLC DataFrame.
    Returns df augmented with tr_Q, tr_T, tr_phase, regime columns.
    """
    df = df.copy()
    df = _add_indicators(df)

    composite = _build_composite_from_ohlc(df)

    # IMMUTABLE transport layer
    transport_df = compute_transport_from_series(composite, c=DEFAULT_C, tau=DEFAULT_TAU)

    for col in transport_df.columns:
        df[f"tr_{col}"] = transport_df[col].reindex(df.index)

    df["composite_norm"] = composite.reindex(df.index)

    # Regime classification (IMMUTABLE thresholds)
    df["regime"] = df["tr_Q"].apply(
        lambda q: classify_q_global_p2(q, Q05_GLOBAL, Q95_GLOBAL)
    )

    return df


# ═══════════════════════════════════════════════════════════════════════════
# Market-specific data loaders
# ═══════════════════════════════════════════════════════════════════════════

def load_btc_or_eth(symbol: str) -> pd.DataFrame:
    """Load BTC or ETH 1-min Binance data and resample to 5-min OHLC."""
    market_dir = DATA_DIR / symbol
    if not market_dir.exists():
        raise FileNotFoundError(f"No data directory: {market_dir}")

    csv_files = sorted(market_dir.glob(f"{symbol}-1m-*.csv"))
    if not csv_files:
        raise FileNotFoundError(f"No 1-min CSVs found in {market_dir}")

    frames = []
    for fp in csv_files:
        try:
            chunk = pd.read_csv(fp, header=None, dtype=str)
            # Binance 1-min: col0=open_time_us (microseconds!), col1=open, col2=high,
            # col3=low, col4=close, col5=volume. col6=close_time_us — IGNORE col6+
            chunk = chunk.iloc[:, :6]
            chunk.columns = ["ts_us", "open", "high", "low", "close", "volume"]
            for col in ["ts_us", "open", "high", "low", "close", "volume"]:
                chunk[col] = pd.to_numeric(chunk[col], errors="coerce")
            chunk = chunk.dropna(subset=["ts_us", "open", "close"])
            # Convert microseconds → milliseconds, then to datetime
            ts_ms = (chunk["ts_us"] / 1000).astype("int64")
            chunk["timestamp"] = pd.to_datetime(ts_ms, unit="ms", utc=True)
            chunk = chunk.drop(columns=["ts_us"])
            chunk = chunk.set_index("timestamp")
            frames.append(chunk)
        except Exception as e:
            print(f"  WARNING loading {fp.name}: {e}")
            continue

    if not frames:
        raise ValueError(f"No valid data loaded for {symbol}")

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

    print(f"  {symbol}: {len(raw)} 1-min bars → {len(ohlc)} 5-min bars", flush=True)
    return ohlc


def load_xauusd() -> pd.DataFrame:
    """Load XAUUSD daily JSON data.

    Daily bars are re-timestamped to 13:30 UTC (NYSE open) so that session-gated
    strategies (NY_Continuation checks hour==13) fire correctly.
    This is data-ingestion adaptation only — transport mathematics are IMMUTABLE.
    """
    json_files = sorted((DATA_DIR / "XAUUSD").glob("*.json"))
    if not json_files:
        raise FileNotFoundError("No XAUUSD JSON files found")

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
            frames.append(df[["open", "high", "low", "close", "volume"]])
        except Exception as e:
            print(f"  WARNING loading {fp.name}: {e}")
            continue

    if not frames:
        raise ValueError("No valid XAUUSD data loaded")

    df = pd.concat(frames).sort_index()
    df = df[~df.index.duplicated(keep="first")]
    df = df.dropna(subset=["open", "close"])
    # Shift to 13:30 UTC so NY_Continuation (hour==13) gate fires
    df.index = df.index.normalize() + pd.Timedelta(hours=13, minutes=30)
    print(f"  XAUUSD: {len(df)} daily bars (shifted to 13:30 UTC)", flush=True)
    return df


def load_csv_market(symbol: str, data_subdir: str) -> pd.DataFrame:
    """Load daily CSV market (NAS100, USOIL, UKOIL).

    Daily bars are re-timestamped to 13:30 UTC so NY_Continuation fires.
    """
    market_dir = DATA_DIR / data_subdir
    if not market_dir.exists():
        raise FileNotFoundError(f"No data directory: {market_dir}")

    csv_files = sorted(market_dir.glob("*.csv"))
    if not csv_files:
        raise FileNotFoundError(f"No CSV files found in {market_dir}")

    frames = []
    for fp in csv_files:
        try:
            df = pd.read_csv(fp)
            df.columns = [c.lower().strip() for c in df.columns]
            if "timestamp" in df.columns:
                df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms", utc=True)
            elif "date" in df.columns:
                df["timestamp"] = pd.to_datetime(df["date"], utc=True)
            else:
                df["timestamp"] = pd.to_datetime(df.iloc[:, 0], unit="ms", utc=True)
            df = df.set_index("timestamp")
            for col in ["open", "high", "low", "close"]:
                if col in df.columns:
                    df[col] = pd.to_numeric(df[col], errors="coerce")
            if "volume" not in df.columns:
                df["volume"] = 1.0
            keep = [c for c in ["open", "high", "low", "close", "volume"] if c in df.columns]
            frames.append(df[keep].dropna(subset=["open", "close"]))
        except Exception as e:
            print(f"  WARNING loading {fp.name}: {e}")
            continue

    if not frames:
        raise ValueError(f"No valid {symbol} data loaded")

    df = pd.concat(frames).sort_index()
    df = df[~df.index.duplicated(keep="first")]
    # Shift to 13:30 UTC so NY_Continuation (hour==13) gate fires
    df.index = df.index.normalize() + pd.Timedelta(hours=13, minutes=30)
    print(f"  {symbol}: {len(df)} daily bars (shifted to 13:30 UTC)", flush=True)
    return df


# ═══════════════════════════════════════════════════════════════════════════
# Market registry
# ═══════════════════════════════════════════════════════════════════════════

MARKET_CONFIG = {
    "EURUSD": {
        "loader"    : None,   # uses cached Phase 2 parquets
        "timeframe" : "5min",
        "asset_class": "FX",
        "description": "EUR/USD Spot FX (baseline)",
    },
    "BTCUSDT": {
        "loader"    : lambda: load_btc_or_eth("BTCUSDT"),
        "timeframe" : "5min",
        "asset_class": "Crypto",
        "description": "Bitcoin / USDT Perpetual",
    },
    "ETHUSDT": {
        "loader"    : lambda: load_btc_or_eth("ETHUSDT"),
        "timeframe" : "5min",
        "asset_class": "Crypto",
        "description": "Ethereum / USDT Perpetual",
    },
    "XAUUSD": {
        "loader"    : load_xauusd,
        "timeframe" : "D1",
        "asset_class": "Commodity",
        "description": "Gold Spot (XAU/USD)",
    },
    "NAS100": {
        "loader"    : lambda: load_csv_market("NAS100", "NAS100"),
        "timeframe" : "D1",
        "asset_class": "Index",
        "description": "NASDAQ-100 Index",
    },
    "USOIL": {
        "loader"    : lambda: load_csv_market("USOIL", "USOIL"),
        "timeframe" : "D1",
        "asset_class": "Commodity",
        "description": "WTI Crude Oil",
    },
    "UKOIL": {
        "loader"    : lambda: load_csv_market("UKOIL", "UKOIL"),
        "timeframe" : "D1",
        "asset_class": "Commodity",
        "description": "Brent Crude Oil",
    },
}


def load_and_prepare_market(symbol: str) -> pd.DataFrame:
    """
    Load raw data for a market, apply transport pipeline,
    return enriched DataFrame with tr_Q, regime, indicators.
    """
    if symbol not in MARKET_CONFIG:
        raise ValueError(f"Unknown market: {symbol}. Available: {list(MARKET_CONFIG)}")

    cfg = MARKET_CONFIG[symbol]
    loader = cfg["loader"]
    if loader is None:
        raise ValueError(f"Use replay_eurusd_from_cache() for EURUSD")

    print(f"\n  Loading {symbol} ({cfg['description']}) …", flush=True)
    raw = loader()

    print(f"  Applying transport pipeline …", flush=True)
    df = _apply_transport_to_ohlc(raw)

    # Drop warmup rows (need enough bars for indicators)
    df = df.dropna(subset=["tr_Q", "atr_14", "rsi_14"])
    df = df.iloc[50:]  # discard first 50 bars for indicator warmup

    print(f"  {symbol}: {len(df)} usable bars after warmup", flush=True)
    return df


# ═══════════════════════════════════════════════════════════════════════════
# Transport OS execution on prepared DataFrame
# ═══════════════════════════════════════════════════════════════════════════

def run_transport_os_on_market(
    df: pd.DataFrame,
    os,
    strategy_registry: Dict,
    symbol: str,
    verbose: bool = True,
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Run the Transport OS on a prepared market DataFrame.
    Uses the IDENTICAL execution engine from Phase 2.

    Returns:
      trades_df   : completed trade records
      decisions_df: per-bar OS decisions
    """
    state = BarState()
    trade_df, dec_df, _ = run_transport_os_on_chunk(
        df, os, strategy_registry, state, bar_offset=0
    )

    if verbose:
        n_trades = len(trade_df) if trade_df is not None and len(trade_df) > 0 else 0
        print(f"  {symbol}: {n_trades} trades executed", flush=True)

    return trade_df, dec_df


# ═══════════════════════════════════════════════════════════════════════════
# Regime statistics (pure computation, no OS needed)
# ═══════════════════════════════════════════════════════════════════════════

def compute_regime_statistics(df: pd.DataFrame) -> dict:
    """Compute regime distribution, Markov matrix, and run statistics."""
    regimes = df["regime"].values
    n = len(regimes)
    if n == 0:
        return {}

    # Frequency distribution
    counts = {}
    for r in REGIMES_5:
        counts[r] = int(np.sum(regimes == r))

    fracs = {r: counts[r] / n for r in REGIMES_5}

    coherent_frac   = fracs.get("Strong_Coherent", 0) + fracs.get("Weak_Coherent", 0)
    incoherent_frac = fracs.get("Deep_Incoherent", 0) + fracs.get("Mod_Incoherent", 0)
    transition_frac = fracs.get("Transition", 0)

    # Shannon entropy
    p_vals = np.array([fracs[r] for r in REGIMES_5])
    p_vals = p_vals[p_vals > 0]
    entropy = float(-np.sum(p_vals * np.log(p_vals)))
    max_entropy = np.log(5)
    norm_entropy = entropy / max_entropy

    # Markov transition matrix
    markov = {r: {r2: 0 for r2 in REGIMES_5} for r in REGIMES_5}
    for i in range(n - 1):
        src, dst = regimes[i], regimes[i + 1]
        if src in markov and dst in markov[src]:
            markov[src][dst] += 1

    # Normalise rows
    for r in REGIMES_5:
        row_sum = sum(markov[r].values())
        if row_sum > 0:
            for r2 in REGIMES_5:
                markov[r][r2] /= row_sum

    # Mean regime duration (run-length encoding)
    runs: Dict[str, List[int]] = {r: [] for r in REGIMES_5}
    cur_regime = regimes[0]
    run_len = 1
    for i in range(1, n):
        if regimes[i] == cur_regime:
            run_len += 1
        else:
            runs[cur_regime].append(run_len)
            cur_regime = regimes[i]
            run_len = 1
    runs[cur_regime].append(run_len)

    mean_dur = {r: float(np.mean(runs[r])) if runs[r] else 0.0 for r in REGIMES_5}
    median_dur = {r: float(np.median(runs[r])) if runs[r] else 0.0 for r in REGIMES_5}

    # Persistence (self-transition probability)
    persistence = {r: float(markov[r].get(r, 0.0)) for r in REGIMES_5}

    return {
        "n_bars"          : n,
        "regime_counts"   : counts,
        "regime_fractions": fracs,
        "coherent_frac"   : coherent_frac,
        "incoherent_frac" : incoherent_frac,
        "transition_frac" : transition_frac,
        "entropy"         : entropy,
        "norm_entropy"    : norm_entropy,
        "markov"          : markov,
        "persistence"     : persistence,
        "mean_duration"   : mean_dur,
        "median_duration" : median_dur,
    }
