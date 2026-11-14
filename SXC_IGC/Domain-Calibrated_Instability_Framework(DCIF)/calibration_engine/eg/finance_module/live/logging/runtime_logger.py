"""
live/logging/runtime_logger.py — General runtime event logger.
Logs connection events, errors, reconnects to CSV + stdout.
"""

import csv
import threading
import time
from pathlib import Path
import sys

_ROOT = Path(__file__).resolve().parents[2]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from live_config import LOGS_DIR, LOG_RUNTIME, LOG_FLUSH_EVERY


class RuntimeLogger:
    COLUMNS = ["ts_unix", "ts_human", "level", "message"]

    def __init__(self, filename: str = "runtime.csv"):
        self._path    = LOGS_DIR / filename
        self._lock    = threading.Lock()
        self._buf: list = []
        self._count   = 0
        self._enabled = LOG_RUNTIME
        self._init_file()

    def _init_file(self):
        if not self._path.exists():
            with open(self._path, "w", newline="") as f:
                csv.writer(f).writerow(self.COLUMNS)

    def log(self, level: str, message: str):
        if not self._enabled:
            return
        now = time.time()
        row = [now, time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(now)), level, message]
        with self._lock:
            self._buf.append(row)
            self._count += 1
            if self._count % LOG_FLUSH_EVERY == 0:
                self._flush()
        if level in ("WARN", "ERROR", "INFO"):
            print(f"  [{level}] {message}", flush=True)

    def flush(self):
        with self._lock:
            self._flush()

    def _flush(self):
        if not self._buf:
            return
        with open(self._path, "a", newline="") as f:
            csv.writer(f).writerows(self._buf)
        self._buf.clear()
