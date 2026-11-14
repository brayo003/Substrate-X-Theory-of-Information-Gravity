"""
live/monitoring/dashboard.py

Curses-based terminal dashboard. Displays live system state.
Updates at DASHBOARD_REFRESH_S intervals (driven by orchestrator).
Degrades gracefully if curses is unavailable (stdout fallback).
"""

import sys
import time
import threading
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[2]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from live_config import LIVE_MARKETS, DASHBOARD_REFRESH_S

try:
    import curses
    _CURSES_OK = True
except ImportError:
    _CURSES_OK = False


def _fmt_uptime(seconds: float) -> str:
    s = int(seconds)
    h, rem = divmod(s, 3600)
    m, sec = divmod(rem, 60)
    return f"{h:02d}:{m:02d}:{sec:02d}"


def _fmt_pnl(val: float) -> str:
    sign = "+" if val >= 0 else ""
    return f"{sign}{val:.2f}"


class Dashboard:
    """
    Thread-safe dashboard. Call update() from the async loop;
    the curses rendering runs in a background thread.
    """

    def __init__(self):
        self._lock   = threading.Lock()
        self._state  = {}
        self._active = False
        self._thread = None
        self._screen = None

    # ── lifecycle ─────────────────────────────────────────────────────────

    def start(self):
        """Launch the dashboard rendering thread."""
        self._active = True
        if _CURSES_OK:
            self._thread = threading.Thread(
                target=self._run_curses, daemon=True, name="dashboard"
            )
            self._thread.start()
        else:
            # Stdout fallback — print on every update()
            pass

    def stop(self):
        self._active = False

    # ── update (called from orchestrator) ────────────────────────────────

    def update(self, decisions: dict, broker_snap: dict,
               stream=None, uptime: float = 0.0):
        with self._lock:
            self._state = dict(
                decisions=dict(decisions),
                broker=dict(broker_snap),
                connected=stream.is_connected if stream else False,
                last_prices={
                    sym: (stream.last_price(sym) or 0.0)
                    for sym in LIVE_MARKETS
                } if stream else {},
                uptime=uptime,
                ts=time.time(),
            )
        if not _CURSES_OK:
            self._print_fallback()

    # ── curses renderer ───────────────────────────────────────────────────

    def _run_curses(self):
        try:
            curses.wrapper(self._curses_loop)
        except Exception:
            pass   # dashboard crash must never kill the trading process

    def _curses_loop(self, stdscr):
        self._screen = stdscr
        curses.curs_set(0)
        stdscr.nodelay(True)
        curses.start_color()
        curses.use_default_colors()
        curses.init_pair(1, curses.COLOR_GREEN,  -1)
        curses.init_pair(2, curses.COLOR_RED,    -1)
        curses.init_pair(3, curses.COLOR_YELLOW, -1)
        curses.init_pair(4, curses.COLOR_CYAN,   -1)

        while self._active:
            try:
                stdscr.erase()
                with self._lock:
                    state = dict(self._state)
                if state:
                    self._draw(stdscr, state)
                stdscr.refresh()
            except curses.error:
                pass
            time.sleep(DASHBOARD_REFRESH_S)

    def _draw(self, scr, state: dict):
        h, w = scr.getmaxyx()
        row  = 0
        G  = curses.color_pair(1)
        R  = curses.color_pair(2)
        Y  = curses.color_pair(3)
        C  = curses.color_pair(4)
        N  = curses.A_NORMAL

        def put(r, c, text, attr=N):
            if r < h - 1 and c < w - 1:
                try:
                    scr.addstr(r, c, text[:w - c - 1], attr)
                except curses.error:
                    pass

        # Header
        title = "  TRANSPORT OS — LIVE RUNTIME"
        put(row, 0, "═" * min(w - 1, 70), C); row += 1
        put(row, 0, title, C | curses.A_BOLD); row += 1
        put(row, 0, f"  {time.strftime('%Y-%m-%d %H:%M:%S UTC', time.gmtime())}   "
                    f"Uptime: {_fmt_uptime(state.get('uptime', 0))}", N); row += 1
        put(row, 0, "─" * min(w - 1, 70), C); row += 1

        # Connection
        connected = state.get("connected", False)
        conn_str  = "● CONNECTED" if connected else "○ DISCONNECTED"
        conn_attr = G if connected else R
        put(row, 2, "Feed:  ", N)
        put(row, 9, conn_str, conn_attr); row += 1
        row += 1

        # Per-symbol state
        for sym in LIVE_MARKETS:
            dec   = state.get("decisions", {}).get(sym, {})
            price = state.get("last_prices", {}).get(sym, 0.0)
            q     = dec.get("q_val", float("nan"))
            regime  = dec.get("regime",   "—")
            strat   = dec.get("strategy", "—")
            signal  = dec.get("signal",   0)
            no_trd  = dec.get("no_trade", True)
            bar_idx = dec.get("bar_idx",  0)

            put(row, 2, f"── {sym} ", C | curses.A_BOLD); row += 1
            put(row, 4, f"Price:    {price:>12.4f}", N); row += 1
            q_str = f"{q:>+10.3f}" if q == q else "       nan"
            put(row, 4, f"Q:        {q_str}", Y); row += 1
            put(row, 4, f"Regime:   {regime:<20}", N); row += 1
            sig_str = ("BUY" if signal == 1 else "SELL" if signal == -1 else "FLAT")
            sig_attr = G if signal == 1 else R if signal == -1 else N
            put(row, 4, f"Strategy: {strat:<20}", N)
            put(row, 35, sig_str, sig_attr); row += 1
            nt_str  = "YES" if no_trd else "NO "
            nt_attr = Y if no_trd else G
            put(row, 4, "NoTrade:  ", N)
            put(row, 14, nt_str, nt_attr)
            put(row, 20, f"  Bar #{bar_idx}", N); row += 1
            row += 1

        # Account
        put(row, 0, "─" * min(w - 1, 70), C); row += 1
        broker = state.get("broker", {})
        bal    = broker.get("balance",      0.0)
        eq     = broker.get("equity",       0.0)
        flt    = broker.get("floating_pnl", 0.0)
        rlz    = broker.get("realized_pnl", 0.0)
        n_pos  = broker.get("open_positions", 0)
        n_trd  = broker.get("total_trades",   0)

        put(row, 2, f"Balance:      {bal:>12.2f}", N); row += 1
        put(row, 2, f"Equity:       {eq:>12.2f}", N); row += 1
        flt_attr = G if flt >= 0 else R
        put(row, 2, f"Floating PnL: ", N)
        put(row, 16, f"{_fmt_pnl(flt):>10}", flt_attr); row += 1
        rlz_attr = G if rlz >= 0 else R
        put(row, 2, f"Realized PnL: ", N)
        put(row, 16, f"{_fmt_pnl(rlz):>10}", rlz_attr); row += 1
        put(row, 2, f"Open:  {n_pos}   Trades: {n_trd}", N); row += 1

        put(row, 0, "═" * min(w - 1, 70), C)

    # ── stdout fallback ───────────────────────────────────────────────────

    def _print_fallback(self):
        with self._lock:
            state = dict(self._state)
        broker = state.get("broker", {})
        ts = time.strftime("%H:%M:%S")
        print(
            f"\r[{ts}] "
            + "  ".join(
                f"{sym} Q={state.get('decisions',{}).get(sym,{}).get('q_val',0):.2f} "
                f"R={state.get('decisions',{}).get(sym,{}).get('regime','?')[:4]}"
                for sym in LIVE_MARKETS
            )
            + f"  bal={broker.get('balance',0):.2f}"
            + f"  eq={broker.get('equity',0):.2f}"
            + f"  rlz={_fmt_pnl(broker.get('realized_pnl',0))}",
            end="", flush=True,
        )
