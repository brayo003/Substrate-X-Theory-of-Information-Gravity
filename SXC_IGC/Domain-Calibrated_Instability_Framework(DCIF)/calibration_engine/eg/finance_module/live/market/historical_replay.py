"""
live/market/historical_replay.py

HistoricalReplayer: feeds historical REST candles through the same
CandleBuilder + IndicatorPipeline path used for live WebSocket candles.

Design principles
-----------------
- ZERO bypass of existing pipeline logic.
- Every historical candle is injected via CandleBuilder.on_trade()
  (same code path as a live aggTrade tick), which in turn populates
  IndicatorPipeline.add_candle().
- After replay the IndicatorPipeline holds exactly the same state it
  would have if those candles had arrived live.
- Tracks ``last_replayed_ts_ms`` so BinanceStream can suppress duplicate
  candles and request gap-fills on reconnect.
- Thread-safe: replay runs synchronously but state is protected for
  the async reader.

Execution path per candle
--------------------------
    Historical candle (REST dict)
        ↓
    HistoricalReplayer.replay_candle(candle)
        ↓
    _inject_as_synthetic_trades(candle, builder)
        – on_trade(open,  qty=0, ts=open_ts_ms)
        – on_trade(high,  qty=0, ts=open_ts_ms + 1)
        – on_trade(low,   qty=0, ts=open_ts_ms + 2)
        – on_trade(close, qty=candle_volume, ts=close_ts_ms - 1)
          [the close trade IS the last tick; it carries the volume so the
           candle is closed by the next bar's open tick in live mode, but
           here we force-close using the next synthetic tick approach below]
        ↓
    Force-close by calling on_trade with next bar's open timestamp
        ↓
    builder.get_completed_candles() → [candle]
        ↓
    pipeline.add_candle(candle)
        ↓
    LiveEngine.on_candle(pipeline.get_df())  ← if engine attached

Note on injection strategy
---------------------------
CandleBuilder closes the current bar when a trade arrives in the *next*
candle period. To force-close each historical candle without knowing the
next live tick we send a synthetic 1-ms-later "closing tick" whose
timestamp is exactly ``candle_close_ts_ms + 1`` (which falls inside the
next candle period). This mirrors exactly how the candle builder works
with live ticks — it closes a candle upon receiving the first tick of a
new period.
"""

import logging
import threading
from typing import Dict, List, Optional

log = logging.getLogger(__name__)


class HistoricalReplayer:
    """
    Replays historical candles through the live CandleBuilder/IndicatorPipeline.

    One instance per symbol, shared between StartupBackfill and BinanceStream.

    Parameters
    ----------
    symbol   : Symbol string (e.g. "BTCUSDT").
    builder  : The symbol's CandleBuilder instance (same object used by
               BinanceStream — NOT a copy).
    pipeline : The symbol's IndicatorPipeline instance (same object used by
               BinanceStream — NOT a copy).
    engine   : Optional LiveEngine to call on_candle() after each bar.
               If None, only the pipeline state is warmed (no signals).
    logger   : Optional runtime logger.
    """

    def __init__(
        self,
        symbol: str,
        builder,            # CandleBuilder
        pipeline,           # IndicatorPipeline
        engine=None,        # LiveEngine | None
        logger=None,
    ):
        self.symbol   = symbol
        self._builder  = builder
        self._pipeline = pipeline
        self._engine   = engine
        self._logger   = logger

        # The highest open_ts_ms successfully replayed (inclusive).
        # BinanceStream will ignore live WS candles with open_ts <= this.
        self._last_replayed_ts_ms: Optional[int] = None

        # Set to True once replay() completes, False until then.
        # BinanceStream blocks until this is True for each symbol.
        self._replay_complete = False

        # Protects _last_replayed_ts_ms and _replay_complete
        self._lock = threading.Lock()

    # ── Public properties ─────────────────────────────────────────────────

    @property
    def last_replayed_ts_ms(self) -> Optional[int]:
        """Timestamp (ms) of the last candle open successfully replayed."""
        with self._lock:
            return self._last_replayed_ts_ms

    @property
    def replay_complete(self) -> bool:
        """True after replay() has finished without error."""
        with self._lock:
            return self._replay_complete

    # ── Main entry points ─────────────────────────────────────────────────

    def replay(self, candles: List[dict]) -> int:
        """
        Replay a list of historical candle dicts (from BinanceREST) through
        the pipeline in strict chronological order.

        Parameters
        ----------
        candles : Sorted list of candle dicts as returned by
                  ``fetch_completed_klines()``.

        Returns
        -------
        Number of candles successfully fed into the pipeline.
        """
        if not candles:
            with self._lock:
                self._replay_complete = True
            return 0

        # Ensure strict ascending order (defence-in-depth)
        candles = sorted(candles, key=lambda c: c["open_ts_ms"])

        # Deduplicate against already-replayed candles
        with self._lock:
            already = self._last_replayed_ts_ms

        if already is not None:
            candles = [c for c in candles if c["open_ts_ms"] > already]

        n_fed = 0
        for candle in candles:
            self._replay_one(candle)
            n_fed += 1

        with self._lock:
            self._replay_complete = True

        self._log(
            "INFO",
            f"[{self.symbol}] Replay complete. {n_fed} candles fed. "
            f"Pipeline bars={self._pipeline.n_bars} "
            f"ready={self._pipeline.readiness.ready}",
        )
        return n_fed

    def replay_gap(self, candles: List[dict]) -> int:
        """
        Feed gap candles after a WebSocket reconnect.

        Semantically identical to ``replay()`` but does NOT set
        ``replay_complete`` (it is already True by this point) and does
        NOT require candles to be the initial batch.

        Returns number of candles fed.
        """
        if not candles:
            return 0

        candles = sorted(candles, key=lambda c: c["open_ts_ms"])

        with self._lock:
            already = self._last_replayed_ts_ms

        if already is not None:
            candles = [c for c in candles if c["open_ts_ms"] > already]

        n_fed = 0
        for candle in candles:
            self._replay_one(candle)
            n_fed += 1

        self._log(
            "INFO",
            f"[{self.symbol}] Gap-fill complete. {n_fed} candle(s) replayed.",
        )
        return n_fed

    # ── Single-candle injection ───────────────────────────────────────────

    def _replay_one(self, candle: dict):
        """
        Inject one historical candle through the CandleBuilder then hand
        the completed candle to IndicatorPipeline (and optionally LiveEngine).

        Execution path
        --------------
        1. Inject four synthetic trades that encode the candle's OHLCV
           geometry within its time window.
        2. Send one "close-trigger" trade at ``close_ts_ms + 1`` ms so
           CandleBuilder closes the bar the same way it would on a live tick.
        3. Drain ``builder.get_completed_candles()``.
        4. Feed each completed candle into ``pipeline.add_candle()``.
        5. If an engine is attached and the pipeline is ready, call
           ``engine.on_candle(pipeline.get_df())``.
        """
        ots_ms  = candle["open_ts_ms"]
        cts_ms  = candle["close_ts_ms"]
        o, h, l, c = (
            candle["open"], candle["high"], candle["low"], candle["close"]
        )
        vol = candle["volume"]

        # ── 1. Inject OHLCV trades within this candle period ──────────────
        # Timestamps must all be within [ots_ms, cts_ms]
        self._builder.on_trade(o,   0.0,  ots_ms)       # open tick
        self._builder.on_trade(h,   0.0,  ots_ms + 1)   # high
        self._builder.on_trade(l,   0.0,  ots_ms + 2)   # low
        self._builder.on_trade(c,   vol,  cts_ms - 1)   # close (carries volume)

        # ── 2. Close-trigger: a synthetic tick in the NEXT candle period ──
        # This is the mechanism CandleBuilder uses to detect a bar boundary.
        trigger_ts = cts_ms + 1   # first ms of the next 5-min period
        self._builder.on_trade(c, 0.0, trigger_ts)

        # ── 3. Drain completed candles ────────────────────────────────────
        completed = self._builder.get_completed_candles()

        if not completed:
            self._log(
                "WARN",
                f"[{self.symbol}] No completed candle produced for "
                f"open_ts={ots_ms}. Builder state may be ahead.",
            )
            return

        # ── 4. Feed into IndicatorPipeline ────────────────────────────────
        for bar in completed:
            readiness = self._pipeline.add_candle(bar)
            self._log(
                "DEBUG",
                f"[{self.symbol}] Replayed bar open={ots_ms} close={c:.4f} "
                f"{readiness}",
            )

        # ── 5. Drive engine if pipeline is ready ──────────────────────────
        if self._engine is not None:
            df = self._pipeline.get_df()
            if df is not None:
                try:
                    self._engine.on_candle(df)
                except Exception as exc:
                    self._log(
                        "WARN",
                        f"[{self.symbol}] Engine error during replay: {exc}",
                    )

        # ── 6. Update last-replayed cursor ────────────────────────────────
        with self._lock:
            if (
                self._last_replayed_ts_ms is None
                or ots_ms > self._last_replayed_ts_ms
            ):
                self._last_replayed_ts_ms = ots_ms

    # ── Logging helper ────────────────────────────────────────────────────

    def _log(self, level: str, msg: str):
        if self._logger:
            self._logger.log(level, msg)
        else:
            import time as _time
            ts = _time.strftime("%H:%M:%S")
            print(f"  {ts} [{level}] {msg}", flush=True)
