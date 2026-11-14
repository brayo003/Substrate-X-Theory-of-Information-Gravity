"""
live_config.py — Phase 6A Runtime Configuration.

Single source of truth for all live system parameters.
Edit this file to change runtime behavior — nothing else needs touching.

Frozen research parameters are imported from the existing modules.
This file only contains live-system–specific configuration.
"""

from pathlib import Path

# ── Paths ─────────────────────────────────────────────────────────────────
ROOT_DIR   = Path(__file__).resolve().parent          # finance_module/
LIVE_DIR   = ROOT_DIR / "live"
LOGS_DIR   = ROOT_DIR / "live_logs"
LOGS_DIR.mkdir(exist_ok=True)

# ── Markets ───────────────────────────────────────────────────────────────
LIVE_MARKETS = ["BTCUSDT", "ETHUSDT"]

# ── Candle resolution ─────────────────────────────────────────────────────
CANDLE_MINUTES  = 5          # must match the frozen OS (5-min bars)
WARMUP_BARS     = 6          # bars before indicators gate opens (6 × 5 min = 30 min cold-start max)
                             # NOTE: backfill always fetches BACKFILL_BARS (100) regardless,
                             # so indicators are properly converged on normal startup.
                             # This value only applies to cold WebSocket fallback.

# ── Binance REST (historical backfill) ───────────────────────────────────
BINANCE_REST_BASE       = "https://api.binance.com"   # public, no auth required
BACKFILL_BARS           = 100   # historical bars fetched for indicator convergence (EMA-50, ATR, etc.)
BACKFILL_SAFETY_MARGIN  = 20    # extra bars fetched to absorb indicator burn-in
# Total candles requested = BACKFILL_BARS + BACKFILL_SAFETY_MARGIN = 120
# WARMUP_BARS is intentionally lower than BACKFILL_BARS so backfill always
# satisfies the warmup gate immediately — no cold-start delay on normal startup.

# ── Binance WebSocket ─────────────────────────────────────────────────────
BINANCE_WS_BASE = "wss://stream.binance.com:9443/ws"
WS_RECONNECT_DELAY_S  = 5    # seconds before reconnect attempt
WS_MAX_RECONNECTS     = 999  # effectively unlimited
WS_PING_INTERVAL_S    = 20   # keepalive ping

# ── SimBroker ─────────────────────────────────────────────────────────────
INITIAL_BALANCE     = 10_000.0   # USD

# Market frictions — per-market overrides possible in sim_broker
SPREAD_PIPS = {
    "BTCUSDT": 1.0,   # 1 USD spread
    "ETHUSDT": 0.10,  # $0.10 spread
}
COMMISSION_PCT = {
    "BTCUSDT": 0.00030,  # 0.03% round-trip (matches research COMMISSION_RT)
    "ETHUSDT": 0.00030,
}
SLIPPAGE_ENABLED = False     # disabled in Phase 6A
SLIPPAGE_SIGMA   = 0.0001    # stochastic slippage std (unused while disabled)

# ── Test mode ─────────────────────────────────────────────────────────────
# When True every position auto-closes after TEST_CLOSE_BARS bars
# regardless of scheduler exit conditions.  Set False for production.
TEST_MODE           = False
TEST_CLOSE_BARS     = 2      # bars (= 10 min at 5-min candles)

# ── Frozen OS parameters (re-exported for convenience) ───────────────────
# These are imported from the research modules — never change them here.
Q05_FROZEN  = -1.0
Q95_FROZEN  =  1.73
ATR_STOP    =  1.5
ATR_TARGET  =  2.5
HOLD_BARS   = 24   # matches p2_execution_engine.HOLD_BARS

# ── Logging ───────────────────────────────────────────────────────────────
LOG_MARKET_DATA   = True
LOG_CANDLES       = True
LOG_Q_VALUES      = True
LOG_DECISIONS     = True
LOG_TRADES        = True
LOG_ACCOUNT       = True
LOG_RUNTIME       = True
LOG_FLUSH_EVERY   = 10       # write buffer to disk every N events

# ── Dashboard ─────────────────────────────────────────────────────────────
DASHBOARD_REFRESH_S = 1.0    # seconds between screen redraws
DASHBOARD_ENABLED   = True
