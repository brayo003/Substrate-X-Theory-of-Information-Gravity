"""
live/market/binance_stream.py

Async Binance public WebSocket client.
Streams aggTrade events for multiple symbols → feeds CandleBuilder → emits
completed candles to the rest of the live pipeline.

No authentication required. Public streams only.

── Backfill/Replay additions (infrastructure only) ─────────────────────────

Two guards are added to this file.  Neither touches pipeline logic.

1. Duplicate-suppression guard
   When replay has run, completed WS candles whose open_ts_ms <= the
   replayer's ``last_replayed_ts_ms`` are silently discarded.  This
   prevents double-processing of candles that were already fed during
   startup backfill.

2. Reconnect gap-fill guard
   When the WS reconnects after a dropout, any completed candles missed
   during the outage are fetched from the Binance REST API and replayed
   through the identical pipeline before live streaming resumes.
   This prevents the engine from seeing a state gap after reconnection.

Both guards are injected only if the Orchestrator supplies a replayer
dict via ``set_replayers()``.  If no replayers are set the stream behaves
exactly as before — full backward compatibility.
"""

import asyncio
import json
import sys
import time
from pathlib import Path
from typing import Callable, Dict, Optional

import websockets
import websockets.exceptions

_ROOT = Path(__file__).resolve().parents[2]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from live_config import (
    WS_RECONNECT_DELAY_S,
    WS_MAX_RECONNECTS,
    WS_PING_INTERVAL_S,
    LIVE_MARKETS,
)
from live.market.candle_builder import CandleBuilder, IndicatorPipeline


class BinanceStream:
    """
    Connects to Binance combined aggTrade streams for all configured symbols.
    On each completed 5-min candle, calls on_candle_complete(symbol, df).
    Reconnects automatically on any WebSocket error.
    """

    def __init__(
        self,
        symbols: list,
        on_candle_complete: Callable,          # async fn(symbol, df)
        runtime_logger=None,
    ):
        self.symbols   = [s.upper() for s in symbols]
        self._on_candle = on_candle_complete
        self._logger    = runtime_logger

        # One builder + pipeline per symbol
        self._builders:  Dict[str, CandleBuilder]     = {}
        self._pipelines: Dict[str, IndicatorPipeline] = {}
        for sym in self.symbols:
            self._builders[sym]  = CandleBuilder(sym)
            self._pipelines[sym] = IndicatorPipeline(sym)

        self._last_price: Dict[str, float] = {}
        self._connected  = False
        self._stop_event = asyncio.Event()
        self._reconnect_count = 0
        self._start_time: Optional[float] = None

        # ── Backfill/replay references ────────────────────────────────────
        # Injected by Orchestrator after StartupBackfill completes.
        # Keyed by UPPER symbol.
        # Value: HistoricalReplayer instance (from live.market.historical_replay).
        self._replayers: Dict[str, object] = {}   # symbol → HistoricalReplayer | None

    # ── Backfill interface — called by Orchestrator after backfill done ───

    def set_replayers(self, replayers: Dict[str, object]) -> None:
        """
        Provide the per-symbol HistoricalReplayer instances produced by
        StartupBackfill.  Call this before ``start()`` to enable both
        duplicate suppression and reconnect gap-fill.

        Parameters
        ----------
        replayers : dict[symbol(upper) → HistoricalReplayer]
        """
        self._replayers = {k.upper(): v for k, v in replayers.items()}
        self._log(
            "INFO",
            f"Replayers registered for: {list(self._replayers.keys())}",
        )

    # ── public interface ──────────────────────────────────────────────────

    @property
    def is_connected(self) -> bool:
        return self._connected

    def last_price(self, symbol: str) -> Optional[float]:
        return self._last_price.get(symbol.upper())

    def get_pipeline(self, symbol: str) -> Optional[IndicatorPipeline]:
        return self._pipelines.get(symbol.upper())

    def get_builder(self, symbol: str) -> Optional[CandleBuilder]:
        return self._builders.get(symbol.upper())

    async def start(self):
        """Stream indefinitely, reconnecting on errors."""
        self._start_time = time.time()
        self._stop_event.clear()

        while not self._stop_event.is_set():
            if self._reconnect_count >= WS_MAX_RECONNECTS:
                self._log("ERROR", "Max reconnects reached — stopping stream")
                break
            try:
                await self._connect_and_stream()
            except asyncio.CancelledError:
                break
            except Exception as exc:
                self._connected = False
                self._reconnect_count += 1
                self._log("WARN", f"Stream error ({type(exc).__name__}: {exc}) — "
                                  f"reconnect #{self._reconnect_count} "
                                  f"in {WS_RECONNECT_DELAY_S}s")
                await asyncio.sleep(WS_RECONNECT_DELAY_S)

    async def stop(self):
        """Signal graceful shutdown."""
        self._stop_event.set()
        self._connected = False

    # ── connection ────────────────────────────────────────────────────────

    def _build_url(self) -> str:
        streams = "/".join(f"{s.lower()}@aggTrade" for s in self.symbols)
        return f"wss://stream.binance.com:9443/stream?streams={streams}"

    async def _connect_and_stream(self):
        url = self._build_url()
        self._log("INFO", f"Connecting → {url}")

        # ── Reconnect gap-fill guard ──────────────────────────────────────
        # Before opening the WebSocket we fill any gap that accumulated
        # during the outage. This must complete before the WS starts
        # delivering live ticks to prevent state divergence.
        if self._reconnect_count > 0 and self._replayers:
            await self._fill_reconnect_gaps()

        async with websockets.connect(
            url,
            ping_interval=WS_PING_INTERVAL_S,
            ping_timeout=30,
            close_timeout=10,
        ) as ws:
            self._connected = True
            self._log("INFO", f"Connected. Streaming {self.symbols}")

            async for raw in ws:
                if self._stop_event.is_set():
                    break
                try:
                    await self._handle_message(raw)
                except Exception as exc:
                    self._log("WARN", f"Message handling error: {exc}")

        self._connected = False

    # ── reconnect gap-fill ────────────────────────────────────────────────

    async def _fill_reconnect_gaps(self) -> None:
        """
        For each symbol, fetch all completed candles since the last
        successfully processed candle (``replayer.last_replayed_ts_ms``)
        and replay them through the pipeline before live ticks arrive.

        Runs in thread-pool executor to avoid blocking the event loop.
        Awaits completion of ALL symbols before returning.
        """
        from live.market.binance_rest import fetch_gap_candles

        self._log("INFO", "Reconnect detected — starting gap-fill …")

        loop = asyncio.get_event_loop()

        async def _gap_fill_one(symbol: str, replayer) -> None:
            after_ts = replayer.last_replayed_ts_ms
            if after_ts is None:
                return   # replay never ran; nothing to gap-fill

            self._log(
                "INFO",
                f"[{symbol}] Fetching gap candles after ts={after_ts}",
            )
            # Fetch is blocking I/O — offload to thread pool
            gap_candles = await loop.run_in_executor(
                None, fetch_gap_candles, symbol, after_ts
            )
            if gap_candles:
                # replay_gap is CPU-bound — also offload
                n_fed = await loop.run_in_executor(
                    None, replayer.replay_gap, gap_candles
                )
                self._log(
                    "INFO",
                    f"[{symbol}] Gap-fill: {n_fed} candle(s) replayed.",
                )
            else:
                self._log("INFO", f"[{symbol}] No gap candles to fill.")

        tasks = [
            _gap_fill_one(sym, self._replayers[sym])
            for sym in self.symbols
            if sym in self._replayers
        ]
        if tasks:
            await asyncio.gather(*tasks)

        self._log("INFO", "Gap-fill complete. Resuming live stream.")

    # ── message handling ──────────────────────────────────────────────────

    async def _handle_message(self, raw: str):
        msg = json.loads(raw)

        # Combined stream format: {"stream": "btcusdt@aggTrade", "data": {...}}
        stream = msg.get("stream", "")
        data   = msg.get("data", msg)   # fallback for single-stream

        # Extract symbol from stream name or from data field 's'
        sym_raw = data.get("s", stream.split("@")[0].upper())
        symbol  = sym_raw.upper()

        if symbol not in self._builders:
            return

        price = float(data["p"])
        self._last_price[symbol] = price

        builder  = self._builders[symbol]
        pipeline = self._pipelines[symbol]

        candle_completed = builder.on_aggTrade(data)

        if candle_completed:
            completed = builder.get_completed_candles()
            for candle in completed:

                # ── Duplicate-suppression guard ───────────────────────────
                # If this candle was already processed during startup replay,
                # skip it entirely. open_ts_ms is stored in each candle dict
                # when it came from the builder's _close_bar().
                # For WS candles the builder stores the open_ms in
                # candle["timestamp"] (a pd.Timestamp). Convert to ms.
                candle_open_ms = _ts_to_ms(candle.get("timestamp"))
                replayer = self._replayers.get(symbol)

                if replayer is not None and candle_open_ms is not None:
                    last_replayed = replayer.last_replayed_ts_ms
                    if (
                        last_replayed is not None
                        and candle_open_ms <= last_replayed
                    ):
                        self._log(
                            "DEBUG",
                            f"{symbol} duplicate candle @ {candle_open_ms} "
                            f"<= last_replayed {last_replayed} — skipped",
                        )
                        continue
                # ── End duplicate guard ───────────────────────────────────

                readiness = pipeline.add_candle(candle)
                self._log("CANDLE", f"{symbol} candle closed @ "
                                    f"{candle['timestamp']} close={candle['close']:.4f} "
                                    f"vol={candle['volume']:.2f} "
                                    f"{readiness}")

                # Update replayer cursor so gap-fill has a correct anchor
                if replayer is not None and candle_open_ms is not None:
                    _update_replayer_cursor(replayer, candle_open_ms)

            df = pipeline.get_df()
            if df is None:
                return
            await self._on_candle(symbol, df)

    # ── logging helper ────────────────────────────────────────────────────

    def _log(self, level: str, msg: str):
        if self._logger:
            self._logger.log(level, f"[BinanceStream] {msg}")
        else:
            ts = time.strftime("%H:%M:%S")
            print(f"  {ts} [{level}] {msg}", flush=True)


# ── Module-level helpers ───────────────────────────────────────────────────

def _ts_to_ms(ts) -> Optional[int]:
    """Convert a pd.Timestamp (or anything with .value) to Unix milliseconds."""
    try:
        import pandas as pd
        if ts is None:
            return None
        if isinstance(ts, pd.Timestamp):
            # .value is nanoseconds
            return ts.value // 1_000_000
        # Fallback: try int
        return int(ts)
    except Exception:
        return None


def _update_replayer_cursor(replayer, open_ts_ms: int) -> None:
    """
    Advance the replayer's last_replayed_ts_ms to track live WS candles.
    This keeps the gap-fill anchor current even after live candles arrive.

    We write directly to the replayer's protected field via the lock.
    The lock is already part of HistoricalReplayer's public contract.
    """
    with replayer._lock:
        if (
            replayer._last_replayed_ts_ms is None
            or open_ts_ms > replayer._last_replayed_ts_ms
        ):
            replayer._last_replayed_ts_ms = open_ts_ms
