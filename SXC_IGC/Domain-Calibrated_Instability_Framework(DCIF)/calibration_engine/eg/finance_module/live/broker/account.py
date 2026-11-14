"""
live/broker/account.py

Virtual trading account. Tracks balance, equity, positions, PnL.
Thread-safe. No external dependencies.
"""

import threading
import time
from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class Position:
    id:           int
    symbol:       str
    direction:    int        # +1 long, -1 short
    size:         float      # units
    entry_price:  float
    stop_price:   float
    target_price: float
    strategy:     str
    regime:       str
    open_time:    float      # unix timestamp
    commission:   float
    floating_pnl: float = 0.0


class Account:
    """
    Simulated broker account. Maintains balance, equity, positions, history.
    All monetary values in account currency (USD).
    """

    def __init__(self, initial_balance: float = 10_000.0):
        self._lock           = threading.RLock()
        self._balance        = float(initial_balance)
        self._realized_pnl   = 0.0
        self._floating_pnl   = 0.0
        self._positions: Dict[int, Position] = {}
        self._history:   List[dict]           = []
        self._next_id    = 1

    # ── read-only properties ──────────────────────────────────────────────

    @property
    def balance(self) -> float:
        with self._lock:
            return self._balance

    @property
    def equity(self) -> float:
        with self._lock:
            return self._balance + self._floating_pnl

    @property
    def floating_pnl(self) -> float:
        with self._lock:
            return self._floating_pnl

    @property
    def realized_pnl(self) -> float:
        with self._lock:
            return self._realized_pnl

    @property
    def margin_used(self) -> float:
        with self._lock:
            return sum(p.size * p.entry_price for p in self._positions.values())

    @property
    def free_margin(self) -> float:
        return self.equity - self.margin_used

    # ── position management ───────────────────────────────────────────────

    def open_position(
        self,
        symbol:       str,
        direction:    int,
        size:         float,
        entry_price:  float,
        stop_price:   float,
        target_price: float,
        strategy:     str,
        regime:       str,
        commission:   float = 0.0,
    ) -> int:
        with self._lock:
            pos_id = self._next_id
            self._next_id += 1
            pos = Position(
                id=pos_id, symbol=symbol, direction=direction,
                size=size, entry_price=entry_price,
                stop_price=stop_price, target_price=target_price,
                strategy=strategy, regime=regime,
                open_time=time.time(), commission=commission,
            )
            self._positions[pos_id] = pos
            self._balance -= commission
            self._realized_pnl -= commission
            return pos_id

    def close_position(
        self,
        position_id: int,
        exit_price:  float,
        reason:      str,
    ) -> Optional[dict]:
        with self._lock:
            pos = self._positions.pop(position_id, None)
            if pos is None:
                return None

            gross_pnl   = pos.direction * (exit_price - pos.entry_price) * pos.size
            net_pnl     = gross_pnl - pos.commission
            self._balance      += net_pnl
            self._realized_pnl += net_pnl

            trade = dict(
                position_id=position_id,
                symbol=pos.symbol,
                direction=pos.direction,
                size=pos.size,
                entry_price=pos.entry_price,
                exit_price=exit_price,
                stop_price=pos.stop_price,
                target_price=pos.target_price,
                strategy=pos.strategy,
                regime=pos.regime,
                open_time=pos.open_time,
                close_time=time.time(),
                commission=pos.commission,
                gross_pnl=gross_pnl,
                net_pnl=net_pnl,
                reason=reason,
                balance_after=self._balance,
            )
            self._history.append(trade)
            self._recalc_floating()
            return trade

    def update_floating(self, prices: Dict[str, float]):
        """Recalculate floating PnL from current mid prices."""
        with self._lock:
            for pos in self._positions.values():
                price = prices.get(pos.symbol, pos.entry_price)
                pos.floating_pnl = (
                    pos.direction * (price - pos.entry_price) * pos.size
                    - pos.commission
                )
            self._recalc_floating()

    def get_open_positions(self) -> List[dict]:
        with self._lock:
            return [self._pos_to_dict(p) for p in self._positions.values()]

    def get_positions_for_symbol(self, symbol: str) -> List[Position]:
        with self._lock:
            return [p for p in self._positions.values() if p.symbol == symbol]

    def get_trade_history(self) -> List[dict]:
        with self._lock:
            return list(self._history)

    def snapshot(self) -> dict:
        with self._lock:
            return dict(
                balance=self._balance,
                equity=self._balance + self._floating_pnl,
                floating_pnl=self._floating_pnl,
                realized_pnl=self._realized_pnl,
                margin_used=sum(
                    p.size * p.entry_price for p in self._positions.values()
                ),
                open_positions=len(self._positions),
                total_trades=len(self._history),
                timestamp=time.time(),
            )

    # ── helpers ───────────────────────────────────────────────────────────

    def _recalc_floating(self):
        self._floating_pnl = sum(p.floating_pnl for p in self._positions.values())

    def _pos_to_dict(self, p: Position) -> dict:
        return dict(
            id=p.id, symbol=p.symbol, direction=p.direction,
            size=p.size, entry_price=p.entry_price,
            stop_price=p.stop_price, target_price=p.target_price,
            strategy=p.strategy, regime=p.regime,
            open_time=p.open_time, commission=p.commission,
            floating_pnl=p.floating_pnl,
        )
