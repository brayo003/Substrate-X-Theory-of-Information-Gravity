"""
live/broker/execution.py

Translates scheduler signals into SimBroker orders.
Checks exits on every bar (stop, target, HOLD_BARS timeout, TEST_MODE).
"""

import sys
import time
from pathlib import Path
from typing import List, Optional

_ROOT = Path(__file__).resolve().parents[2]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from live_config import (
    ATR_STOP, ATR_TARGET, HOLD_BARS,
    TEST_MODE, TEST_CLOSE_BARS,
)
from live.broker.account import Account
from live.broker.spread import SpreadModel
from live.broker.commission import CommissionModel
from live.broker.slippage import SlippageModel


class ExecutionEngine:
    """
    Receives scheduler decisions, applies market frictions, manages
    position lifecycle. Calls Account for all bookkeeping.
    """

    def __init__(
        self,
        account:    Account,
        spread:     SpreadModel,
        commission: CommissionModel,
        slippage:   SlippageModel,
        trade_logger=None,
    ):
        self._account    = account
        self._spread     = spread
        self._commission = commission
        self._slippage   = slippage
        self._logger     = trade_logger

        # bar_idx counter per symbol for HOLD_BARS tracking
        self._entry_bar: dict = {}   # {position_id: bar_idx_at_entry}
        self._bar_counter: dict = {} # {symbol: current bar index}

    # ── entry ─────────────────────────────────────────────────────────────

    def execute_signal(
        self,
        symbol:    str,
        signal:    int,       # +1 BUY, -1 SELL, 0 flat
        mid_price: float,
        atr:       float,
        regime:    str,
        strategy:  str,
        risk_frac: float,
        bar_idx:   int,
    ) -> Optional[dict]:
        """
        Open a position if signal != 0 and no position already open.
        Returns fill dict or None.
        """
        if signal == 0:
            return None

        # Gate F — direction-aware position lifecycle.
        #
        # Same direction  → duplicate signal: hold existing position, block new entry.
        # Opposite direction → reversal: close existing position first, then open new.
        # This preserves the one-position invariant while enabling field-state reversals.
        open_positions = self._account.get_positions_for_symbol(symbol)
        if open_positions:
            existing = open_positions[0]
            if existing.direction == signal:
                # Duplicate — block
                return None
            else:
                # Reversal — close existing at mid_price, then fall through to open new
                commission_close = self._commission.compute(
                    symbol, existing.size * mid_price
                )
                trade = self._account.close_position(
                    existing.id, mid_price, "reversal"
                )
                if trade:
                    trade["reason"]  = "reversal"
                    trade["bar_idx"] = bar_idx
                    trade["elapsed"] = bar_idx - self._entry_bar.get(existing.id, bar_idx)
                    self._entry_bar.pop(existing.id, None)
                    if self._logger:
                        self._logger.log_trade_close(trade)
                # open_positions is now empty — fall through to open reversed position

        if atr <= 0 or mid_price <= 0:
            return None

        # Apply frictions to fill price
        if signal == 1:
            fill_price = self._spread.apply_buy(symbol, mid_price)
        else:
            fill_price = self._spread.apply_sell(symbol, mid_price)
        fill_price = self._slippage.apply(symbol, fill_price, signal)

        stop   = fill_price - signal * ATR_STOP   * atr
        target = fill_price + signal * ATR_TARGET * atr

        # Size in units so that risk_frac of balance is at stake
        risk_distance = ATR_STOP * atr
        notional      = self._account.balance * max(risk_frac, 0.01)
        size          = notional / (risk_distance * fill_price + 1e-12)
        commission    = self._commission.compute(symbol, size * fill_price)

        pos_id = self._account.open_position(
            symbol=symbol, direction=signal, size=size,
            entry_price=fill_price, stop_price=stop, target_price=target,
            strategy=strategy, regime=regime, commission=commission,
        )

        self._entry_bar[pos_id] = bar_idx
        self._bar_counter[symbol] = bar_idx

        fill = dict(
            position_id=pos_id, symbol=symbol, direction=signal,
            size=size, fill_price=fill_price, stop=stop, target=target,
            commission=commission, strategy=strategy, regime=regime,
            bar_idx=bar_idx, ts=time.time(),
        )
        if self._logger:
            self._logger.log_trade_open(fill)
        return fill

    # ── exit ──────────────────────────────────────────────────────────────

    def check_exits(
        self,
        symbol:   str,
        high:     float,
        low:      float,
        close:    float,
        bar_idx:  int,
    ) -> List[dict]:
        """
        Check every open position for this symbol against stop/target/timeout.
        Returns list of closed trade dicts.
        """
        closed = []
        positions = self._account.get_positions_for_symbol(symbol)

        for pos in positions:
            entry_bar = self._entry_bar.get(pos.id, bar_idx)
            elapsed   = bar_idx - entry_bar

            stop_hit = target_hit = timeout = False
            exit_price = close

            if pos.direction == 1:
                if low <= pos.stop_price:
                    stop_hit   = True
                    exit_price = pos.stop_price
                elif high >= pos.target_price:
                    target_hit = True
                    exit_price = pos.target_price
            else:
                if high >= pos.stop_price:
                    stop_hit   = True
                    exit_price = pos.stop_price
                elif low <= pos.target_price:
                    target_hit = True
                    exit_price = pos.target_price

            # TEST_MODE: force close after TEST_CLOSE_BARS
            close_bars = TEST_CLOSE_BARS if TEST_MODE else HOLD_BARS
            if elapsed >= close_bars and not stop_hit and not target_hit:
                timeout    = True
                exit_price = close

            if stop_hit or target_hit or timeout:
                reason = ("stop" if stop_hit else
                          "target" if target_hit else
                          ("test_timeout" if TEST_MODE else "hold_timeout"))

                trade = self._account.close_position(pos.id, exit_price, reason)
                if trade:
                    trade["reason"]     = reason
                    trade["bar_idx"]    = bar_idx
                    trade["elapsed"]    = elapsed
                    closed.append(trade)
                    self._entry_bar.pop(pos.id, None)
                    if self._logger:
                        self._logger.log_trade_close(trade)

        return closed
