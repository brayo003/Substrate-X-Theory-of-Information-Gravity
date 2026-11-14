"""
live/runtime/orchestrator.py

Async event loop coordinator. Wires together:
  StartupBackfill → BinanceStream → LiveEngine (per symbol) → SimBroker → Loggers → Dashboard

Single asyncio event loop. All async tasks run here.

── Backfill addition ────────────────────────────────────────────────────────

Before starting the WebSocket, ``run()`` now calls ``StartupBackfill.run()``.
This replays historical REST candles through the existing pipeline, warming
all symbols to WARMUP_BARS before any live tick arrives.

The WebSocket task is only created AFTER backfill is complete.
The backfill replayer instances are injected into BinanceStream via
``stream.set_replayers()``, enabling duplicate suppression and reconnect
gap-fill for the rest of the session.

No other component is modified.  All Transport OS equations, engine,
broker, and scheduler are identical.
"""

import asyncio
import sys
import time
from pathlib import Path
from typing import Dict

_ROOT = Path(__file__).resolve().parents[2]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from live_config import LIVE_MARKETS, DASHBOARD_ENABLED, DASHBOARD_REFRESH_S

from live.market.binance_stream       import BinanceStream
from live.broker.sim_broker           import SimBroker
from live.runtime.live_engine         import LiveEngine
from live.runtime.startup_backfill    import StartupBackfill
from live.logging.runtime_logger      import RuntimeLogger
from live.logging.decision_logger     import DecisionLogger
from live.logging.trade_logger        import TradeLogger


class Orchestrator:
    """
    Starts and coordinates all live system components.
    Call await orchestrator.run() to begin streaming.

    Startup sequence
    ----------------
    1. Instantiate LiveEngines (loads frozen allocator — fast, local).
    2. Instantiate BinanceStream (creates builders + pipelines — no network).
    3. Run StartupBackfill:
       a. Fetch historical REST klines for all symbols.
       b. Replay through builders + pipelines (same path as live ticks).
       c. Validate all pipelines are ready.
    4. Inject replayers into BinanceStream for duplicate suppression and
       reconnect gap-fill.
    5. Start BinanceStream WebSocket (live operation begins here).
    """

    def __init__(self, dashboard=None):
        self._start_time = time.time()

        # Loggers
        self._rlog = RuntimeLogger()
        self._dlog = DecisionLogger()
        self._tlog = TradeLogger()

        # Broker (shared across all symbols)
        self._broker = SimBroker(trade_logger=self._tlog)

        # One LiveEngine per symbol
        self._engines: Dict[str, LiveEngine] = {
            sym: LiveEngine(sym, self._broker, self._dlog, self._rlog)
            for sym in LIVE_MARKETS
        }

        # Dashboard (optional)
        self._dashboard = dashboard

        # Stream (created during run)
        self._stream: BinanceStream | None = None

        # Latest per-symbol decision for dashboard
        self._last_decision: Dict[str, dict] = {}

    # ── main entry point ──────────────────────────────────────────────────

    async def run(self):
        """
        Start the full runtime.

        Phase 1 — Backfill (blocking, must complete before WS starts):
            Connect to Binance REST → fetch completed candles →
            replay through pipeline → validate readiness.

        Phase 2 — Live operation (indefinite):
            Connect WebSocket → stream aggTrades → run engine →
            execute decisions.
        """
        self._rlog.log("INFO", f"Orchestrator starting. Markets: {LIVE_MARKETS}")

        # ── Phase 1: Historical backfill ──────────────────────────────────
        # Create the stream object first so that StartupBackfill can share
        # the same builder/pipeline instances that BinanceStream will use.
        self._stream = BinanceStream(
            symbols=LIVE_MARKETS,
            on_candle_complete=self._on_candle,
            runtime_logger=self._rlog,
        )

        backfill = StartupBackfill(
            symbols   = LIVE_MARKETS,
            builders  = {sym: self._stream.get_builder(sym)  for sym in LIVE_MARKETS},
            pipelines = {sym: self._stream.get_pipeline(sym) for sym in LIVE_MARKETS},
            engines   = self._engines,
            logger    = self._rlog,
        )

        try:
            self._rlog.log(
                "INFO",
                "Backfill phase starting — WebSocket will connect after completion.",
            )
            replayers = await backfill.run()
        except Exception as exc:
            self._rlog.log(
                "ERROR",
                f"Backfill failed: {exc}. "
                "Starting WebSocket WITHOUT pre-warmed pipeline. "
                "The runtime will warm up naturally (WARMUP_BARS bars needed).",
            )
            replayers = {}

        # ── Inject replayers into stream for duplicate suppression / gap-fill
        if replayers:
            self._stream.set_replayers(replayers)
            self._rlog.log(
                "INFO",
                f"Backfill complete. Pipelines warmed. "
                f"Starting live WebSocket stream.",
            )
        else:
            self._rlog.log(
                "WARN",
                "No replayers available — stream will warm from cold start.",
            )

        # ── Phase 2: Live streaming ───────────────────────────────────────
        tasks = [asyncio.create_task(self._stream.start(), name="stream")]

        if DASHBOARD_ENABLED and self._dashboard:
            tasks.append(asyncio.create_task(
                self._dashboard_loop(), name="dashboard"
            ))

        tasks.append(asyncio.create_task(self._account_log_loop(), name="acct_log"))

        try:
            await asyncio.gather(*tasks)
        except asyncio.CancelledError:
            pass
        finally:
            await self._shutdown()

    async def stop(self):
        if self._stream:
            await self._stream.stop()

    # ── candle handler — called by BinanceStream ──────────────────────────

    async def _on_candle(self, symbol: str, df):
        """
        Receives a completed candle's indicator DataFrame from BinanceStream.
        Passes it to the per-symbol LiveEngine.
        """
        engine = self._engines.get(symbol)
        if engine is None:
            return

        try:
            decision = engine.on_candle(df)
            self._last_decision[symbol] = decision

            # Log account snapshot after every bar
            snap = self._broker.snapshot()
            self._tlog.log_account(snap)

            if self._dashboard:
                self._dashboard.update(
                    decisions=self._last_decision,
                    broker_snap=snap,
                    stream=self._stream,
                    uptime=time.time() - self._start_time,
                )

        except Exception as exc:
            self._rlog.log("ERROR", f"[{symbol}] on_candle error: {exc}")

    # ── periodic account logger ───────────────────────────────────────────

    async def _account_log_loop(self):
        """Log account snapshot every 60 seconds regardless of bars."""
        while True:
            await asyncio.sleep(60)
            try:
                snap = self._broker.snapshot()
                self._tlog.log_account(snap)
                self._rlog.log("INFO",
                    f"Account: balance={snap['balance']:.2f} "
                    f"equity={snap['equity']:.2f} "
                    f"float={snap['floating_pnl']:.2f} "
                    f"realized={snap['realized_pnl']:.2f} "
                    f"positions={snap['open_positions']}")
            except Exception as exc:
                self._rlog.log("WARN", f"Account log error: {exc}")

    # ── dashboard refresh loop ────────────────────────────────────────────

    async def _dashboard_loop(self):
        while True:
            await asyncio.sleep(DASHBOARD_REFRESH_S)
            try:
                if self._dashboard:
                    snap = self._broker.snapshot()
                    self._dashboard.update(
                        decisions=self._last_decision,
                        broker_snap=snap,
                        stream=self._stream,
                        uptime=time.time() - self._start_time,
                    )
            except Exception:
                pass

    # ── shutdown ──────────────────────────────────────────────────────────

    async def _shutdown(self):
        self._rlog.log("INFO", "Orchestrator shutting down — flushing logs")
        self._rlog.flush()
        self._dlog.flush()
        self._tlog.flush()
