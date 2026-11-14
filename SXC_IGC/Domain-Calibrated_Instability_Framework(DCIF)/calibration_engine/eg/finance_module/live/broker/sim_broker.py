"""
live/broker/sim_broker.py

SimBroker — the single broker abstraction the Transport OS talks to.
Composes Account + SpreadModel + CommissionModel + SlippageModel + ExecutionEngine.
The Transport OS sees only this interface — no broker internals are exposed.
"""

import sys
from pathlib import Path
from typing import Dict, List, Optional

_ROOT = Path(__file__).resolve().parents[2]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from live_config import (
    INITIAL_BALANCE, SPREAD_PIPS, COMMISSION_PCT,
    SLIPPAGE_ENABLED, SLIPPAGE_SIGMA,
)
from live.broker.account    import Account
from live.broker.spread     import SpreadModel
from live.broker.commission import CommissionModel
from live.broker.slippage   import SlippageModel
from live.broker.execution  import ExecutionEngine


class SimBroker:
    """
    Simulated retail broker. Provides a clean interface for the live engine:
      on_signal()   — process a scheduler signal → open position
      on_bar()      — process a new bar → check exits, update floating PnL
      snapshot()    — current account state for logging/dashboard
    """

    def __init__(self, trade_logger=None):
        self._account    = Account(INITIAL_BALANCE)
        self._spread     = SpreadModel(SPREAD_PIPS)
        self._commission = CommissionModel(COMMISSION_PCT)
        self._slippage   = SlippageModel(SLIPPAGE_ENABLED, SLIPPAGE_SIGMA)
        self._execution  = ExecutionEngine(
            self._account, self._spread, self._commission,
            self._slippage, trade_logger,
        )
        self._last_prices: Dict[str, float] = {}
        self._bar_idx:     Dict[str, int]    = {}

    # ── OS-facing interface ───────────────────────────────────────────────

    def on_signal(
        self,
        symbol:    str,
        signal:    int,
        mid_price: float,
        atr:       float,
        regime:    str,
        strategy:  str,
        risk_frac: float,
    ) -> Optional[dict]:
        """Called by live_engine when scheduler produces a non-zero signal."""
        self._last_prices[symbol] = mid_price
        bar = self._bar_idx.get(symbol, 0)
        return self._execution.execute_signal(
            symbol, signal, mid_price, atr, regime, strategy, risk_frac, bar
        )

    def on_bar(
        self,
        symbol:    str,
        high:      float,
        low:       float,
        close:     float,
        mid_price: float,
    ) -> List[dict]:
        """
        Called on every completed bar regardless of signal.
        Updates floating PnL and checks exit conditions.
        Returns list of trades closed this bar.
        """
        self._last_prices[symbol] = mid_price
        self._bar_idx[symbol]     = self._bar_idx.get(symbol, 0) + 1
        self._account.update_floating(self._last_prices)
        bar = self._bar_idx[symbol]
        return self._execution.check_exits(symbol, high, low, close, bar)

    # ── account queries ───────────────────────────────────────────────────

    def snapshot(self) -> dict:
        return self._account.snapshot()

    def get_open_positions(self) -> List[dict]:
        return self._account.get_open_positions()

    def get_trade_history(self) -> List[dict]:
        return self._account.get_trade_history()

    @property
    def balance(self) -> float:
        return self._account.balance

    @property
    def equity(self) -> float:
        return self._account.equity

    @property
    def floating_pnl(self) -> float:
        return self._account.floating_pnl

    @property
    def realized_pnl(self) -> float:
        return self._account.realized_pnl
