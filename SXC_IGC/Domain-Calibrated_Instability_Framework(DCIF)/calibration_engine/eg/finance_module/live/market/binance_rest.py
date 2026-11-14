"""
live/market/binance_rest.py

Binance REST klines fetcher for historical backfill.

Responsibilities
----------------
- Fetch completed 5-min klines from the Binance REST API.
- Never return the currently-forming (incomplete) candle.
- Guarantee strict chronological order, no duplicates.
- Support pagination for fetches larger than the 1 000-candle REST limit.
- Support gap-fill: given a ``start_ts_ms`` return only candles *after* it.

Design constraints
------------------
- No authentication required (public endpoint).
- No modification to any research or live pipeline logic.
- This file is pure data-acquisition infrastructure.
"""

import sys
import time
import logging
from pathlib import Path
from typing import List, Optional

import urllib.request
import urllib.parse
import json

_ROOT = Path(__file__).resolve().parents[2]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from live_config import (
    BINANCE_REST_BASE,
    CANDLE_MINUTES,
    BACKFILL_BARS,
    BACKFILL_SAFETY_MARGIN,
)

log = logging.getLogger(__name__)

# ── Constants ──────────────────────────────────────────────────────────────
_KLINES_ENDPOINT  = "/api/v3/klines"
_REST_MAX_LIMIT   = 1_000           # Binance hard limit per request
_INTERVAL_STR     = f"{CANDLE_MINUTES}m"
_CANDLE_MS        = CANDLE_MINUTES * 60 * 1_000
_HTTP_TIMEOUT_S   = 10
_RETRY_COUNT      = 3
_RETRY_BACKOFF_S  = 2.0


# ── Public interface ───────────────────────────────────────────────────────

def fetch_completed_klines(
    symbol: str,
    n_candles: int = BACKFILL_BARS + BACKFILL_SAFETY_MARGIN,
    end_ts_ms: Optional[int] = None,
    start_ts_ms: Optional[int] = None,
) -> List[dict]:
    """
    Fetch up to ``n_candles`` most-recent *completed* 5-min klines for
    ``symbol`` from the Binance REST API.

    Parameters
    ----------
    symbol      : Binance symbol, e.g. "BTCUSDT".
    n_candles   : Total completed candles to return (default = BACKFILL_BARS
                  + BACKFILL_SAFETY_MARGIN = 120).
    end_ts_ms   : Exclusive upper bound (ms). Defaults to the open timestamp
                  of the currently-forming candle, which ensures only
                  *completed* candles are returned.
    start_ts_ms : If supplied, only candles whose open_ts > start_ts_ms are
                  returned.  Used for gap-fill after reconnect.

    Returns
    -------
    List of candle dicts, strictly ascending by ``open_ts_ms``, no
    duplicates.  Each dict has the shape expected by
    ``CandleBuilder.on_trade()`` calls:

        {
            "open_ts_ms" : int,           # Unix ms of candle open
            "close_ts_ms": int,           # Unix ms of candle close
            "timestamp"  : pd.Timestamp,  # UTC, open time
            "open"       : float,
            "high"       : float,
            "low"        : float,
            "close"      : float,
            "volume"     : float,
            "complete"   : True,
        }
    """
    import pandas as pd   # deferred; only needed here

    symbol = symbol.upper()

    # Default end_ts: open of the current (incomplete) candle
    now_ms = int(time.time() * 1_000)
    if end_ts_ms is None:
        # Open of the *currently forming* candle — we exclude it
        end_ts_ms = (now_ms // _CANDLE_MS) * _CANDLE_MS

    all_rows: List[list] = []
    fetch_end = end_ts_ms          # exclusive end timestamp for next batch
    remaining = n_candles

    while remaining > 0:
        batch_size = min(remaining, _REST_MAX_LIMIT)

        # Calculate start to reach exactly batch_size candles ending at fetch_end
        batch_start = fetch_end - batch_size * _CANDLE_MS

        # If a start_ts_ms filter is set, don't go earlier than it
        if start_ts_ms is not None:
            batch_start = max(batch_start, start_ts_ms + 1)
            if batch_start >= fetch_end:
                break

        rows = _fetch_klines_raw(symbol, batch_start, fetch_end, batch_size)

        if not rows:
            break

        # Prepend (we're walking backwards in time to fill the buffer)
        all_rows = rows + all_rows

        # Advance end pointer to just before the earliest candle fetched
        earliest_open_ms = int(rows[0][0])
        if earliest_open_ms <= batch_start:
            break   # no more data before this point

        fetch_end = earliest_open_ms
        remaining -= len(rows)

        if len(rows) < batch_size:
            break   # exchange returned fewer than requested — no more history

    # ── Post-processing ────────────────────────────────────────────────────
    # Deduplicate by open timestamp (keep last occurrence is fine since they
    # are identical for completed candles).
    seen: set = set()
    unique_rows: List[list] = []
    for row in all_rows:
        ots = int(row[0])
        if ots not in seen:
            seen.add(ots)
            unique_rows.append(row)

    # Sort ascending
    unique_rows.sort(key=lambda r: int(r[0]))

    # Apply start_ts_ms filter (strict greater-than)
    if start_ts_ms is not None:
        unique_rows = [r for r in unique_rows if int(r[0]) > start_ts_ms]

    # Exclude any candle whose close_ts >= end_ts_ms  (partial candle guard)
    # A completed candle's close_ts = open_ts + _CANDLE_MS - 1 ms
    unique_rows = [r for r in unique_rows if int(r[0]) + _CANDLE_MS <= end_ts_ms + 1]

    # Trim to requested count (most-recent n_candles)
    if len(unique_rows) > n_candles:
        unique_rows = unique_rows[-n_candles:]

    # Validate contiguity — warn on any gap
    _warn_gaps(symbol, unique_rows)

    # Convert to candle dicts
    candles: List[dict] = []
    for row in unique_rows:
        ots_ms = int(row[0])
        cts_ms = int(row[6])
        candles.append(dict(
            open_ts_ms  = ots_ms,
            close_ts_ms = cts_ms,
            timestamp   = pd.Timestamp(ots_ms, unit="ms", tz="UTC"),
            open        = float(row[1]),
            high        = float(row[2]),
            low         = float(row[3]),
            close       = float(row[4]),
            volume      = float(row[5]),
            complete    = True,
        ))

    log.info(
        "[BinanceREST] %s fetched %d completed candles "
        "(end_ts=%d, start_filter=%s)",
        symbol, len(candles), end_ts_ms,
        start_ts_ms if start_ts_ms is not None else "none",
    )
    return candles


# ── Gap-fill helper ────────────────────────────────────────────────────────

def fetch_gap_candles(
    symbol: str,
    after_ts_ms: int,
) -> List[dict]:
    """
    Return all completed candles for ``symbol`` with open_ts > ``after_ts_ms``
    and open_ts < current forming candle open.

    This is the reconnect gap-fill entry point.
    """
    now_ms    = int(time.time() * 1_000)
    end_ts_ms = (now_ms // _CANDLE_MS) * _CANDLE_MS

    if after_ts_ms >= end_ts_ms - _CANDLE_MS:
        # Nothing to fill — last processed candle is the most recent completed
        return []

    # Calculate how many candles are in the gap
    gap_candles = (end_ts_ms - after_ts_ms) // _CANDLE_MS
    # Safety cap: never request more than REST_MAX_LIMIT in a gap fill
    gap_candles = min(gap_candles, _REST_MAX_LIMIT)

    return fetch_completed_klines(
        symbol      = symbol,
        n_candles   = gap_candles,
        end_ts_ms   = end_ts_ms,
        start_ts_ms = after_ts_ms,
    )


# ── Internal REST call ────────────────────────────────────────────────────

def _fetch_klines_raw(
    symbol: str,
    start_ts_ms: int,
    end_ts_ms: int,
    limit: int,
) -> List[list]:
    """
    Call GET /api/v3/klines with retry.

    Returns raw list of kline arrays from Binance (ascending order).
    Excludes the currently-forming candle by using ``endTime = end_ts_ms - 1``.
    """
    params = {
        "symbol"    : symbol,
        "interval"  : _INTERVAL_STR,
        "startTime" : str(start_ts_ms),
        "endTime"   : str(end_ts_ms - 1),   # exclusive — exclude forming candle
        "limit"     : str(limit),
    }
    url = BINANCE_REST_BASE + _KLINES_ENDPOINT + "?" + urllib.parse.urlencode(params)

    for attempt in range(1, _RETRY_COUNT + 1):
        try:
            req = urllib.request.Request(
                url,
                headers={
                    "User-Agent": "TransportOS/1.0",
                    "Accept": "application/json",
                },
            )
            with urllib.request.urlopen(req, timeout=_HTTP_TIMEOUT_S) as resp:
                body = resp.read().decode("utf-8")
                data = json.loads(body)

            # Binance error responses are dicts: {"code": -1100, "msg": "..."}
            if isinstance(data, dict):
                raise RuntimeError(
                    f"Binance REST error: code={data.get('code')} "
                    f"msg={data.get('msg')}"
                )

            log.debug(
                "[BinanceREST] %s raw rows=%d start=%d end=%d",
                symbol, len(data), start_ts_ms, end_ts_ms,
            )
            return data   # list of kline arrays

        except urllib.error.HTTPError as exc:
            log.warning(
                "[BinanceREST] %s HTTP %d on attempt %d/%d: %s",
                symbol, exc.code, attempt, _RETRY_COUNT, exc.reason,
            )
            if attempt < _RETRY_COUNT:
                time.sleep(_RETRY_BACKOFF_S * attempt)
        except Exception as exc:
            log.warning(
                "[BinanceREST] %s fetch error attempt %d/%d: %s",
                symbol, attempt, _RETRY_COUNT, exc,
            )
            if attempt < _RETRY_COUNT:
                time.sleep(_RETRY_BACKOFF_S * attempt)

    raise RuntimeError(
        f"[BinanceREST] {symbol}: failed after {_RETRY_COUNT} attempts"
    )


# ── Gap validator ─────────────────────────────────────────────────────────

def _warn_gaps(symbol: str, rows: List[list]) -> None:
    """Emit a warning for any missing candles in the sequence."""
    for i in range(1, len(rows)):
        prev_open = int(rows[i - 1][0])
        curr_open = int(rows[i][0])
        expected  = prev_open + _CANDLE_MS
        if curr_open != expected:
            missing = (curr_open - expected) // _CANDLE_MS
            log.warning(
                "[BinanceREST] %s: gap detected — %d missing candle(s) "
                "between open_ts %d and %d",
                symbol, missing, prev_open, curr_open,
            )
