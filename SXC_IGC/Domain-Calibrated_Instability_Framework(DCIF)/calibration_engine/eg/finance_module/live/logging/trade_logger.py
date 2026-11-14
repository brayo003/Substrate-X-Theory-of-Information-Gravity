"""
live/logging/trade_logger.py — Trade lifecycle and account update logger.
Logs every open, close, and account snapshot.
"""

import csv
import threading
import time
from pathlib import Path
import sys

_ROOT = Path(__file__).resolve().parents[2]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from live_config import LOGS_DIR, LOG_TRADES, LOG_ACCOUNT, LOG_FLUSH_EVERY


class TradeLogger:
    TRADE_COLS = [
        "ts_unix", "event",
        "position_id", "symbol", "direction", "size",
        "entry_price", "exit_price", "stop_price", "target_price",
        "strategy", "regime", "commission",
        "gross_pnl", "net_pnl", "reason",
        "balance_after", "equity_after",
    ]
    ACCOUNT_COLS = [
        "ts_unix", "ts_human",
        "balance", "equity", "floating_pnl", "realized_pnl",
        "margin_used", "open_positions", "total_trades",
    ]

    def __init__(self,
                 trade_file:   str = "trades.csv",
                 account_file: str = "account.csv"):
        self._trade_path   = LOGS_DIR / trade_file
        self._account_path = LOGS_DIR / account_file
        self._lock  = threading.Lock()
        self._tbuf: list = []
        self._abuf: list = []
        self._count = 0
        self._enabled_t = LOG_TRADES
        self._enabled_a = LOG_ACCOUNT
        self._init_files()

    def _init_files(self):
        for path, cols in [
            (self._trade_path,   self.TRADE_COLS),
            (self._account_path, self.ACCOUNT_COLS),
        ]:
            if not path.exists():
                with open(path, "w", newline="") as f:
                    csv.writer(f).writerow(cols)

    # ── trade events ──────────────────────────────────────────────────────

    def log_trade_open(self, fill: dict):
        if not self._enabled_t:
            return
        row = [
            time.time(), "OPEN",
            fill.get("position_id"), fill.get("symbol"),
            fill.get("direction"), round(fill.get("size", 0), 6),
            round(fill.get("fill_price", 0), 6), "",
            round(fill.get("stop", 0), 6), round(fill.get("target", 0), 6),
            fill.get("strategy"), fill.get("regime"),
            round(fill.get("commission", 0), 6),
            "", "", "", "", "",
        ]
        with self._lock:
            self._tbuf.append(row)
            self._maybe_flush()

    def log_trade_close(self, trade: dict):
        if not self._enabled_t:
            return
        row = [
            time.time(), "CLOSE",
            trade.get("position_id"), trade.get("symbol"),
            trade.get("direction"), round(trade.get("size", 0), 6),
            round(trade.get("entry_price", 0), 6),
            round(trade.get("exit_price", 0), 6),
            round(trade.get("stop_price", 0), 6),
            round(trade.get("target_price", 0), 6),
            trade.get("strategy"), trade.get("regime"),
            round(trade.get("commission", 0), 6),
            round(trade.get("gross_pnl", 0), 6),
            round(trade.get("net_pnl", 0), 6),
            trade.get("reason", ""),
            round(trade.get("balance_after", 0), 4), "",
        ]
        with self._lock:
            self._tbuf.append(row)
            self._maybe_flush()

    # ── account snapshot ──────────────────────────────────────────────────

    def log_account(self, snap: dict):
        if not self._enabled_a:
            return
        now = time.time()
        row = [
            now,
            time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(now)),
            round(snap.get("balance", 0), 4),
            round(snap.get("equity", 0), 4),
            round(snap.get("floating_pnl", 0), 4),
            round(snap.get("realized_pnl", 0), 4),
            round(snap.get("margin_used", 0), 4),
            snap.get("open_positions", 0),
            snap.get("total_trades", 0),
        ]
        with self._lock:
            self._abuf.append(row)
            self._maybe_flush()

    # ── flush ─────────────────────────────────────────────────────────────

    def flush(self):
        with self._lock:
            self._flush_all()

    def _maybe_flush(self):
        self._count += 1
        if self._count % LOG_FLUSH_EVERY == 0:
            self._flush_all()

    def _flush_all(self):
        if self._tbuf:
            with open(self._trade_path, "a", newline="") as f:
                csv.writer(f).writerows(self._tbuf)
            self._tbuf.clear()
        if self._abuf:
            with open(self._account_path, "a", newline="") as f:
                csv.writer(f).writerows(self._abuf)
            self._abuf.clear()
