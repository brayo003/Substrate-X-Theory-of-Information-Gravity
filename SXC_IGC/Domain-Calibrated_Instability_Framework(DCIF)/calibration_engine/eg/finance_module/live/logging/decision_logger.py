"""
live/logging/decision_logger.py — Per-bar OS decision logger.
Logs Q value, regime, scheduler decision, allocator selection on every bar.
"""

import csv
import threading
import time
from pathlib import Path
import sys

_ROOT = Path(__file__).resolve().parents[2]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from live_config import LOGS_DIR, LOG_DECISIONS, LOG_FLUSH_EVERY


class DecisionLogger:
    COLUMNS = [
        "ts_unix", "ts_bar", "symbol", "bar_idx",
        "close", "atr", "q_val", "regime",
        "os_strategy", "family", "signal", "risk_frac", "no_trade",
    ]

    def __init__(self, filename: str = "decisions.csv"):
        self._path    = LOGS_DIR / filename
        self._lock    = threading.Lock()
        self._buf: list = []
        self._count   = 0
        self._enabled = LOG_DECISIONS
        self._init_file()

    def _init_file(self):
        if not self._path.exists():
            with open(self._path, "w", newline="") as f:
                csv.writer(f).writerow(self.COLUMNS)

    def log_bar(
        self,
        ts_bar,
        symbol:      str,
        bar_idx:     int,
        close:       float,
        atr:         float,
        q_val:       float,
        regime:      str,
        os_strategy: str,
        family:      str,
        signal:      int,
        risk_frac:   float,
        no_trade:    bool,
    ):
        if not self._enabled:
            return
        row = [
            time.time(), str(ts_bar), symbol, bar_idx,
            round(close, 6), round(atr, 6), round(q_val, 6), regime,
            os_strategy, family, signal, round(risk_frac, 6), int(no_trade),
        ]
        with self._lock:
            self._buf.append(row)
            self._count += 1
            if self._count % LOG_FLUSH_EVERY == 0:
                self._flush()

    def flush(self):
        with self._lock:
            self._flush()

    def _flush(self):
        if not self._buf:
            return
        with open(self._path, "a", newline="") as f:
            csv.writer(f).writerows(self._buf)
        self._buf.clear()
