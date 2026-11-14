"""
live_main.py — Phase 6A Entry Point

Start with:
    python live_main.py

This single command:
  1. Connects to Binance public WebSocket
  2. Streams BTCUSDT and ETHUSDT aggTrade events
  3. Aggregates ticks → 5-min OHLCV candles
  4. Runs the FROZEN Transport OS (Q, regime, scheduler)
  5. Executes decisions through SimBroker
  6. Maintains virtual account
  7. Logs everything to live_logs/
  8. Displays the monitoring dashboard

Nothing in the research pipeline is modified.
"""

import asyncio
import sys
import signal
from pathlib import Path

_ROOT = Path(__file__).resolve().parent
for _p in [str(_ROOT), str(_ROOT / "v12_validate")]:
    if _p not in sys.path:
        sys.path.insert(0, _p)

from live_config import DASHBOARD_ENABLED, LOGS_DIR, LIVE_MARKETS, TEST_MODE


def _print_banner():
    print("""
══════════════════════════════════════════════════════════════════════
  TRANSPORT OPERATING SYSTEM — LIVE RUNTIME  (Phase 6A)
══════════════════════════════════════════════════════════════════════
  Markets  : {markets}
  Logs     : {logs}
  Test mode: {test}
  Press Ctrl+C to stop gracefully.
══════════════════════════════════════════════════════════════════════
""".format(
        markets=", ".join(LIVE_MARKETS),
        logs=LOGS_DIR,
        test="ENABLED" if TEST_MODE else "disabled",
    ), flush=True)


async def _main():
    from live.monitoring.dashboard import Dashboard
    from live.runtime.orchestrator import Orchestrator

    dashboard = None
    if DASHBOARD_ENABLED:
        dashboard = Dashboard()
        dashboard.start()

    orchestrator = Orchestrator(dashboard=dashboard)

    # Graceful shutdown on SIGINT / SIGTERM
    loop = asyncio.get_running_loop()

    def _handle_stop():
        print("\n  Shutdown signal received — stopping gracefully …", flush=True)
        asyncio.create_task(orchestrator.stop())

    for sig in (signal.SIGINT, signal.SIGTERM):
        try:
            loop.add_signal_handler(sig, _handle_stop)
        except NotImplementedError:
            pass   # Windows

    await orchestrator.run()

    if dashboard:
        dashboard.stop()

    print("\n  Transport OS live runtime stopped.", flush=True)


if __name__ == "__main__":
    _print_banner()
    try:
        asyncio.run(_main())
    except KeyboardInterrupt:
        print("\n  Interrupted.", flush=True)
