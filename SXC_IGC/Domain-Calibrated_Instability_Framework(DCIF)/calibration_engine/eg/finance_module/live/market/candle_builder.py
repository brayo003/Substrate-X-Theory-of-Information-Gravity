"""
live/market/candle_builder.py

Aggregates live Binance aggTrade ticks into completed 5-min OHLCV candles,
then runs the FROZEN indicator + transport pipeline identical to p5b_data_loader.
"""

import sys
import threading
from collections import deque
from dataclasses import dataclass
from pathlib import Path
from datetime import datetime, timezone

import numpy as np
import pandas as pd

# Ensure finance_module root is on path
_ROOT = Path(__file__).resolve().parents[2]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))
if str(_ROOT / "v12_validate") not in sys.path:
    sys.path.insert(0, str(_ROOT / "v12_validate"))

from live_config import CANDLE_MINUTES, WARMUP_BARS, Q05_FROZEN, Q95_FROZEN
from p2_transport_os import classify_q_global_p2
from v12_validate.transport_layer import compute_transport_from_series, DEFAULT_C, DEFAULT_TAU


# ─────────────────────────────────────────────────────────────────────────
# CandleBuilder — tick aggregator
# ─────────────────────────────────────────────────────────────────────────

class CandleBuilder:
    """Aggregates raw trade ticks into fixed-duration OHLCV candles."""

    def __init__(self, symbol: str, candle_minutes: int = CANDLE_MINUTES):
        self.symbol = symbol
        self.candle_ms = candle_minutes * 60 * 1000
        self._lock = threading.Lock()

        self._current_open_ms: int = -1
        self._o = self._h = self._l = self._c = 0.0
        self._vol = 0.0

        self._completed: list = []   # list of candle dicts

    # ── public interface ──────────────────────────────────────────────────

    def on_aggTrade(self, msg: dict) -> bool:
        """
        Ingest a Binance aggTrade message dict.
        Returns True if a candle completed.
        """
        price = float(msg["p"])
        qty   = float(msg["q"])
        ts_ms = int(msg["T"])
        return self.on_trade(price, qty, ts_ms)

    def on_trade(self, price: float, qty: float, ts_ms: int) -> bool:
        """
        Ingest one trade. Returns True if a new candle just completed.
        """
        bar_open_ms = (ts_ms // self.candle_ms) * self.candle_ms

        with self._lock:
            if self._current_open_ms < 0:
                # First tick ever
                self._start_bar(bar_open_ms, price)
                self._update_bar(price, qty)
                return False

            if bar_open_ms == self._current_open_ms:
                # Same candle
                self._update_bar(price, qty)
                return False

            # New candle: close the previous one
            completed = self._close_bar()
            self._completed.append(completed)
            self._start_bar(bar_open_ms, price)
            self._update_bar(price, qty)
            return True

    def get_completed_candles(self) -> list:
        """Drain and return all completed candle dicts."""
        with self._lock:
            out = self._completed[:]
            self._completed.clear()
            return out

    def get_current_partial(self) -> dict | None:
        """Return a snapshot of the in-progress (incomplete) candle, or None."""
        with self._lock:
            if self._current_open_ms < 0:
                return None
            ts = pd.Timestamp(self._current_open_ms, unit="ms", tz="UTC")
            return dict(timestamp=ts, open=self._o, high=self._h,
                        low=self._l, close=self._c, volume=self._vol,
                        complete=False)

    @property
    def bars_ready(self) -> int:
        with self._lock:
            return len(self._completed)

    # ── private helpers ───────────────────────────────────────────────────

    def _start_bar(self, open_ms: int, price: float):
        self._current_open_ms = open_ms
        self._o = self._h = self._l = self._c = price
        self._vol = 0.0

    def _update_bar(self, price: float, qty: float):
        if price > self._h: self._h = price
        if price < self._l: self._l = price
        self._c   = price
        self._vol += qty

    def _close_bar(self) -> dict:
        ts = pd.Timestamp(self._current_open_ms, unit="ms", tz="UTC")
        return dict(timestamp=ts, open=self._o, high=self._h,
                    low=self._l, close=self._c, volume=self._vol,
                    complete=True)


# ─────────────────────────────────────────────────────────────────────────
# IndicatorPipeline — rolling window + frozen transport
# ─────────────────────────────────────────────────────────────────────────

@dataclass(frozen=True)
class PipelineReadiness:
    """
    Self-reporting warmup state for IndicatorPipeline.

    A single log line from ``str(readiness)`` exposes bars, warmup,
    remaining, and ready — no inference required at runtime.
    """

    bars: int
    warmup: int
    remaining: int
    ready: bool
    bars_received: int
    deque_maxlen: int | None

    def __str__(self) -> str:
        parts = [
            f"bars={self.bars}",
            f"warmup={self.warmup}",
            f"remaining={self.remaining}",
            f"ready={self.ready}",
        ]
        if self.bars_received != self.bars:
            parts.append(f"bars_received={self.bars_received}")
            parts.append(f"deque_maxlen={self.deque_maxlen}")
        return " ".join(parts)


class IndicatorPipeline:
    """
    Maintains a rolling window of completed candles and recomputes the
    FROZEN indicator + transport pipeline on each new bar.
    """

    def __init__(self, symbol: str, warmup_bars: int = WARMUP_BARS, maxlen: int = 200):
        self.symbol = symbol
        self.warmup_bars = warmup_bars
        self._deque: deque = deque(maxlen=maxlen)
        self._bars_received: int = 0
        self._df_cache: pd.DataFrame | None = None
        self._lock = threading.Lock()

    def add_candle(self, candle: dict) -> PipelineReadiness:
        """
        Add a completed candle dict and invalidate the indicator cache.

        Returns the post-ingest readiness snapshot. ``bars_received`` is
        monotonic across the pipeline lifetime; ``bars`` is the rolling
        window size and plateaus once ``deque_maxlen`` is reached.
        """
        with self._lock:
            prev_bars = len(self._deque)
            self._deque.append(candle)
            self._bars_received += 1
            self._df_cache = None

            maxlen = self._deque.maxlen
            if maxlen is not None and prev_bars < maxlen and len(self._deque) <= prev_bars:
                raise RuntimeError(
                    f"[{self.symbol}] add_candle did not grow deque "
                    f"(prev={prev_bars}, now={len(self._deque)}, maxlen={maxlen})"
                )

            return self._readiness_unlocked()

    @property
    def readiness(self) -> PipelineReadiness:
        with self._lock:
            return self._readiness_unlocked()

    @property
    def n_bars(self) -> int:
        return self.readiness.bars

    def get_df(self) -> pd.DataFrame | None:
        """
        Return a fully-computed DataFrame with OHLCV + all indicators +
        tr_Q + regime columns.

        Returns None while warmup is incomplete. This method is the sole
        execution gate — callers advance downstream only when the return
        value is not None.
        """
        with self._lock:
            if not self._warmup_complete_unlocked():
                return None
            if self._df_cache is not None:
                return self._df_cache.copy()
            df = self._build_df()
            self._df_cache = df
            return df.copy()

    def _warmup_complete_unlocked(self) -> bool:
        """Single readiness predicate — gated only by ``get_df()``."""
        return len(self._deque) >= self.warmup_bars

    def _readiness_unlocked(self) -> PipelineReadiness:
        bars = len(self._deque)
        warmup = self.warmup_bars
        ready = self._warmup_complete_unlocked()
        return PipelineReadiness(
            bars=bars,
            warmup=warmup,
            remaining=max(0, warmup - bars),
            ready=ready,
            bars_received=self._bars_received,
            deque_maxlen=self._deque.maxlen,
        )

    # ── internal build ────────────────────────────────────────────────────

    def _build_df(self) -> pd.DataFrame:
        rows = list(self._deque)
        df = pd.DataFrame(rows)
        df = df.set_index("timestamp").sort_index()
        df = df[["open", "high", "low", "close", "volume"]].astype(float)

        df = _add_indicators(df)
        composite = _build_composite(df)

        transport_df = compute_transport_from_series(
            composite, c=DEFAULT_C, tau=DEFAULT_TAU
        )
        for col in transport_df.columns:
            df[f"tr_{col}"] = transport_df[col].reindex(df.index)

        df["composite_norm"] = composite.reindex(df.index)
        df["regime"] = df["tr_Q"].apply(
            lambda q: classify_q_global_p2(q, Q05_FROZEN, Q95_FROZEN)
            if pd.notna(q) else "Mod_Incoherent"
        )
        return df


# ─────────────────────────────────────────────────────────────────────────
# Indicator functions — IDENTICAL to p5b_data_loader
# ─────────────────────────────────────────────────────────────────────────

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
    df["rsi_14"] = 100 - (100 / (1 + gain / (loss + 1e-12)))

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
    plus_di  = 100 * plus_dm.ewm(span=14, adjust=False).mean() / (atr_s + 1e-12)
    minus_di = 100 * minus_dm.ewm(span=14, adjust=False).mean() / (atr_s + 1e-12)
    dx = 100 * (plus_di - minus_di).abs() / (plus_di + minus_di + 1e-12)
    df["adx_14"] = dx.ewm(span=14, adjust=False).mean()

    df["realized_vol_20"] = close.pct_change().rolling(20).std()

    sma20 = close.rolling(20).mean()
    std20 = close.rolling(20).std()
    df["bb_upper"] = sma20 + 2 * std20
    df["bb_lower"] = sma20 - 2 * std20
    df["bb_mid"]   = sma20

    typical = (high + low + close) / 3
    vol = df.get("volume", pd.Series(1.0, index=df.index))
    df["vwap"] = (
        (typical * vol).rolling(20).sum() / (vol.rolling(20).sum() + 1e-12)
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

    df["roc_10"]        = close.pct_change(10) * 100
    df["donchian_high"] = high.rolling(20).max()
    df["donchian_low"]  = low.rolling(20).min()
    df["supertrend_dir"] = np.where(close > close.shift(1), 1, -1)

    df["ema_9"]  = close.ewm(span=9,  adjust=False).mean()
    df["ema_21"] = close.ewm(span=21, adjust=False).mean()
    df["ema_50"] = close.ewm(span=50, adjust=False).mean()
    df["sma_20"] = sma20
    df["sma_50"] = close.rolling(50).mean()

    return df


def _build_composite(df: pd.DataFrame) -> pd.Series:
    close   = df["close"]
    signals = pd.DataFrame(index=df.index)

    rsi = df.get("rsi_14", pd.Series(50.0, index=df.index))
    signals["s_rsi"] = (rsi - 50.0) / 50.0

    macd = df.get("macd", pd.Series(0.0, index=df.index))
    mstd = macd.std()
    signals["s_macd"] = macd / (mstd + 1e-12) if mstd > 0 else macd * 0

    atr  = df.get("atr_14", pd.Series(1.0, index=df.index))
    amean = atr.rolling(50).mean().fillna(atr)
    signals["s_atr"] = (atr / (amean + 1e-12) - 1.0).clip(-2, 2) / 2.0

    roc = df.get("roc_10", close.pct_change(10) * 100)
    rstd = roc.std()
    signals["s_mom"] = roc / (rstd * 10 + 1e-12) if rstd > 0 else roc * 0

    bb_u = df.get("bb_upper", sma20 + 2 * close.rolling(20).std()
                  if (sma20 := close.rolling(20).mean()) is not None else close)
    bb_l = df.get("bb_lower", close.rolling(20).mean() - 2 * close.rolling(20).std())
    bb_r = (bb_u - bb_l).replace(0, np.nan)
    signals["s_bb"] = ((close - bb_l) / bb_r - 0.5) * 2

    adx = df.get("adx_14", pd.Series(25.0, index=df.index))
    signals["s_adx"] = adx / 50.0 - 0.5

    comp     = signals.mean(axis=1).fillna(0.0)
    comp_std = comp.rolling(100, min_periods=20).std().fillna(1.0)
    composite = ((comp / (comp_std + 1e-12)).clip(-3, 3) / 3.0).rename("composite")

    print("\n==============================")
    print("COMPOSITE")
    print(composite.tail(20))
    print("min =", composite.min())
    print("max =", composite.max())
    print("==============================")

    return composite
