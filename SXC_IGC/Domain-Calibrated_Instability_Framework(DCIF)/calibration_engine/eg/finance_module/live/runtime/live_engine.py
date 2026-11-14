"""
live/runtime/live_engine.py

Bar-by-bar adapter between live candle data and the FROZEN Transport OS.

Reuses verbatim from the research pipeline:
  - p5_engine.load_frozen_allocator()       → allocator table
  - p5_engine.build_scheduler_table()       → {symbol: {regime: strategy}}
  - p5_engine.get_frozen_strategy_registry()→ {name: {fn, family}}
  - p5_engine.FROZEN_RISK_MAP               → {regime: risk_fraction}
  - p2_transport_os.classify_q_global_p2()  → regime string
  - live_config frozen constants

Nothing in the research modules is modified.
This file only adds the live-data adapter layer around them.
"""

import sys
import numpy as np
import pandas as pd
from pathlib import Path
from typing import Dict, Optional

_ROOT = Path(__file__).resolve().parents[2]
for _p in [str(_ROOT), str(_ROOT / "v12_validate")]:
    if _p not in sys.path:
        sys.path.insert(0, _p)

from live_config import Q05_FROZEN, Q95_FROZEN

# ── Import FROZEN research components (no modifications) ──────────────────
from p2_transport_os import classify_q_global_p2
from p5_engine import (
    load_frozen_allocator,
    build_scheduler_table,
    get_frozen_strategy_registry,
    FROZEN_RISK_MAP,
)


class LiveEngine:
    """
    Processes one completed 5-min candle at a time for a single symbol.
    Calls the frozen scheduler to produce a signal, then hands it to SimBroker.
    BarState is carried continuously across all bars — no resets.
    """

    def __init__(self, symbol: str, sim_broker, decision_logger=None, runtime_logger=None):
        self.symbol = symbol
        self._broker    = sim_broker
        self._dlog      = decision_logger
        self._rlog      = runtime_logger

        # Load frozen components once at startup
        allocator_df     = load_frozen_allocator()
        scheduler_all    = build_scheduler_table(allocator_df)
        self._scheduler  = scheduler_all.get(symbol, {})
        self._registry   = get_frozen_strategy_registry()

        # Pre-cache family lookup
        self._family_map = {
            name: meta.get("family", "Unknown")
            for name, meta in self._registry.items()
        }

        self._bar_idx    = 0
        self._last_q     = float("nan")
        self._last_regime = "Mod_Incoherent"
        self._last_strategy = "NO_TRADE"

        self._log("INFO", f"[{symbol}] LiveEngine ready. Scheduler: "
                  + str({r: s for r, s in self._scheduler.items()}))

    # ── main entry point ──────────────────────────────────────────────────

    def on_candle(self, df: pd.DataFrame) -> dict:
        """
        Called by orchestrator with the full rolling indicator DataFrame
        (all bars up to and including the just-completed candle).

        Returns a decision dict for logging/dashboard.
        """
        # Readiness is enforced by IndicatorPipeline.get_df(); None is a contract violation.
        if df is None:
            return {}

        self._bar_idx += 1
        last = df.iloc[-1]

        # Extract values from latest bar
        close = float(last.get("close",  0.0))
        high  = float(last.get("high",   close))
        low   = float(last.get("low",    close))
        atr   = float(last.get("atr_14", 0.0))
        q_val = float(last.get("tr_Q",   float("nan")))
        ts    = df.index[-1]

        if np.isnan(q_val):
            # Gate C: only NaN is an invalid transport state.
            # Q == -1.0 is the valid Deep_Incoherent physical minimum (∇ln(s)=0).
            # Gate A (BACKFILL_BARS=100) covers PDE initialization.
            regime = "Mod_Incoherent"
        else:
            regime = classify_q_global_p2(q_val, Q05_FROZEN, Q95_FROZEN)

        self._last_q      = q_val
        self._last_regime = regime

        # Frozen scheduler lookup
        os_strategy = self._scheduler.get(regime, "NO_TRADE")
        risk_frac   = FROZEN_RISK_MAP.get(regime, 0.0)
        family      = self._family_map.get(os_strategy, "NoTrade")

        self._last_strategy = os_strategy
        is_no_trade = (os_strategy == "NO_TRADE" or risk_frac == 0.0)

        # ── Check exits first (every bar regardless of signal) ────────────
        closed_trades = self._broker.on_bar(
            symbol=self.symbol, high=high, low=low, close=close, mid_price=close
        )

        # ── Compute strategy signal if not NoTrade ────────────────────────
        signal = 0
        if not is_no_trade:
            signal = self._compute_signal(os_strategy, df)

        # ── Send signal to broker ─────────────────────────────────────────
        fill = None
        if signal != 0:
            fill = self._broker.on_signal(
                symbol=self.symbol, signal=signal, mid_price=close,
                atr=atr, regime=regime, strategy=os_strategy, risk_frac=risk_frac,
            )

        # ── Log decision ──────────────────────────────────────────────────
        if self._dlog:
            self._dlog.log_bar(
                ts_bar=ts, symbol=self.symbol, bar_idx=self._bar_idx,
                close=close, atr=atr, q_val=q_val if not np.isnan(q_val) else 0.0,
                regime=regime, os_strategy=os_strategy, family=family,
                signal=signal, risk_frac=risk_frac, no_trade=is_no_trade,
            )

        return dict(
            symbol=self.symbol, bar_idx=self._bar_idx, ts=ts,
            close=close, atr=atr, q_val=q_val,
            regime=regime, strategy=os_strategy, family=family,
            signal=signal, risk_frac=risk_frac, no_trade=is_no_trade,
            fill=fill, closed_trades=closed_trades,
        )

    # ── frozen signal computation ─────────────────────────────────────────

    def _compute_signal(self, strategy_name: str, df: pd.DataFrame) -> int:
        meta = self._registry.get(strategy_name)
        if meta is None:
            return 0
        try:
            sig_series = meta["fn"](df)
            val = sig_series.iloc[-1]
            return int(val) if not pd.isna(val) else 0
        except Exception as exc:
            self._log("WARN", f"[{self.symbol}] Signal error ({strategy_name}): {exc}")
            return 0

    # ── state queries (for dashboard) ────────────────────────────────────

    @property
    def last_q(self) -> float:
        return self._last_q

    @property
    def last_regime(self) -> str:
        return self._last_regime

    @property
    def last_strategy(self) -> str:
        return self._last_strategy

    @property
    def bar_count(self) -> int:
        return self._bar_idx

    # ── helper ────────────────────────────────────────────────────────────

    def _log(self, level: str, msg: str):
        if self._rlog:
            self._rlog.log(level, msg)
        else:
            print(f"  [{level}] {msg}", flush=True)
