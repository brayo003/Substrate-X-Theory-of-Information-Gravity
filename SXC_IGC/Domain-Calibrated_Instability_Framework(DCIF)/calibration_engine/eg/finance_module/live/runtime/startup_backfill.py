"""
live/runtime/startup_backfill.py

StartupBackfill: orchestrates historical backfill for all configured symbols.

Responsibilities
----------------
1. For each symbol:
   a. Calculate required candle count (BACKFILL_BARS + BACKFILL_SAFETY_MARGIN).
   b. Fetch completed klines from Binance REST API.
   c. Run HistoricalReplayer.replay() through the existing pipeline.
2. Block until ALL symbols have their pipelines warmed and replay_complete=True.
3. Return the per-symbol replayer instances to the Orchestrator so that
   BinanceStream can use them for reconnect gap-fill and duplicate suppression.

Design guarantees
-----------------
- Runs to completion before the WebSocket connects — this is enforced by
  the Orchestrator calling ``await backfill.run()`` before creating the
  BinanceStream task.
- No state is reset; the pipelines are the same objects BinanceStream will
  use during live operation.
- No modifications to existing transport equations, engine, or broker.
- asyncio-compatible: ``run()`` is a coroutine that offloads CPU-bound work
  to a thread pool so the event loop stays responsive.

Usage (called by Orchestrator)
-------------------------------
    backfill = StartupBackfill(
        symbols   = LIVE_MARKETS,
        builders  = stream_builders,    # dict[symbol → CandleBuilder]
        pipelines = stream_pipelines,   # dict[symbol → IndicatorPipeline]
        engines   = engines,            # dict[symbol → LiveEngine]
        logger    = runtime_logger,
    )
    replayers = await backfill.run()   # blocks until all symbols ready
    # replayers: dict[symbol → HistoricalReplayer]
"""

import asyncio
import sys
import time
import logging
from pathlib import Path
from typing import Dict, List, Optional

_ROOT = Path(__file__).resolve().parents[2]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from live_config import (
    BACKFILL_BARS,
    BACKFILL_SAFETY_MARGIN,
    LIVE_MARKETS,
)
from live.market.binance_rest     import fetch_completed_klines
from live.market.historical_replay import HistoricalReplayer

log = logging.getLogger(__name__)

_TOTAL_CANDLES = BACKFILL_BARS + BACKFILL_SAFETY_MARGIN


class StartupBackfill:
    """
    Coordinates historical backfill for all symbols.

    All work is deterministic: same candle history → same pipeline state.
    """

    def __init__(
        self,
        symbols   : List[str],
        builders  : Dict[str, object],   # symbol → CandleBuilder
        pipelines : Dict[str, object],   # symbol → IndicatorPipeline
        engines   : Optional[Dict[str, object]] = None,   # symbol → LiveEngine
        logger    = None,
    ):
        self._symbols   = [s.upper() for s in symbols]
        self._builders  = builders
        self._pipelines = pipelines
        self._engines   = engines or {}
        self._logger    = logger

        # Built during run(); one replayer per symbol
        self._replayers: Dict[str, HistoricalReplayer] = {}

    # ── Public interface ──────────────────────────────────────────────────

    @property
    def replayers(self) -> Dict[str, HistoricalReplayer]:
        """
        The per-symbol HistoricalReplayer instances.
        Available after ``run()`` completes.
        """
        return self._replayers

    async def run(self) -> Dict[str, HistoricalReplayer]:
        """
        Fetch and replay historical candles for all symbols.

        Runs each symbol's backfill concurrently in the event-loop thread pool
        to avoid blocking the event loop.

        Returns dict[symbol → HistoricalReplayer] when ALL symbols are ready.

        Raises RuntimeError if any symbol fails to reach WARMUP_BARS after
        replay (which would indicate a REST API problem or insufficient
        history available).
        """
        self._log("INFO", (
            f"StartupBackfill: beginning historical backfill for "
            f"{self._symbols}. "
            f"Requesting {_TOTAL_CANDLES} candles per symbol "
            f"({BACKFILL_BARS} warmup + {BACKFILL_SAFETY_MARGIN} safety)."
        ))

        t0 = time.monotonic()
        loop = asyncio.get_event_loop()

        # Run all symbols concurrently in executor threads
        tasks = [
            loop.run_in_executor(None, self._backfill_symbol, symbol)
            for symbol in self._symbols
        ]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Check for errors
        for symbol, result in zip(self._symbols, results):
            if isinstance(result, Exception):
                raise RuntimeError(
                    f"Backfill failed for {symbol}: {result}"
                ) from result

        elapsed = time.monotonic() - t0
        self._log(
            "INFO",
            f"StartupBackfill complete in {elapsed:.1f}s. "
            f"Symbols: {self._symbols}. "
            f"All pipelines ready: "
            f"{', '.join(f'{s}={r.replay_complete}' for s, r in self._replayers.items())}",
        )

        # Validate all pipelines are actually ready
        for symbol, replayer in self._replayers.items():
            pipeline = self._pipelines[symbol]
            r = pipeline.readiness
            if not r.ready:
                raise RuntimeError(
                    f"[{symbol}] Pipeline NOT ready after backfill: "
                    f"bars={r.bars} warmup={r.warmup} remaining={r.remaining}. "
                    f"Consider increasing BACKFILL_BARS or BACKFILL_SAFETY_MARGIN."
                )

        return self._replayers

    # ── Per-symbol backfill (blocking — runs in thread pool) ─────────────

    def _backfill_symbol(self, symbol: str) -> None:
        """
        Fetch and replay historical candles for a single symbol.
        Called from a thread-pool executor — must not call asyncio APIs.
        """
        self._log("INFO", f"[{symbol}] Fetching {_TOTAL_CANDLES} historical candles …")

        t0 = time.monotonic()

        # ── 1. Fetch completed klines ─────────────────────────────────────
        candles = fetch_completed_klines(
            symbol    = symbol,
            n_candles = _TOTAL_CANDLES,
        )

        if not candles:
            raise RuntimeError(
                f"[{symbol}] Binance REST returned 0 candles. "
                "Cannot complete backfill."
            )

        self._log(
            "INFO",
            f"[{symbol}] Received {len(candles)} candles. "
            f"Range: {candles[0]['timestamp']} → {candles[-1]['timestamp']}",
        )

        # ── 2. Build replayer using the SAME builder/pipeline as BinanceStream ──
        replayer = HistoricalReplayer(
            symbol   = symbol,
            builder  = self._builders[symbol],
            pipeline = self._pipelines[symbol],
            engine   = self._engines.get(symbol),
            logger   = self._logger,
        )

        # ── 3. Replay candles through the live pipeline ───────────────────
        n_fed = replayer.replay(candles)

        elapsed = time.monotonic() - t0
        pipeline = self._pipelines[symbol]
        r = pipeline.readiness

        self._log(
            "INFO",
            f"[{symbol}] Backfill done in {elapsed:.2f}s. "
            f"Fed {n_fed} candles. "
            f"Pipeline: bars={r.bars} warmup={r.warmup} ready={r.ready} "
            f"last_ts_ms={replayer.last_replayed_ts_ms}",
        )

        # Store replayer for export to BinanceStream
        self._replayers[symbol] = replayer

    # ── Logging helper ────────────────────────────────────────────────────

    def _log(self, level: str, msg: str):
        if self._logger:
            self._logger.log(level, f"[StartupBackfill] {msg}")
        else:
            ts = time.strftime("%H:%M:%S")
            print(f"  {ts} [StartupBackfill/{level}] {msg}", flush=True)
