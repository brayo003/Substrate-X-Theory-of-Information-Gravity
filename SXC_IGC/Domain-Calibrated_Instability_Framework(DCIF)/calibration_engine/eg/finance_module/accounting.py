"""
accounting.py — Unified Account Balance and Position Tracking System

Provides complete monetary flow traceability with full audit trail.
Implements the accounting equation: Opening Cash + Realized PnL - Fees ± Transfers = Ending Cash

This system replaces the fragmented cum_pnl tracking across execution engines.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple
from datetime import datetime
from enum import Enum
import json
from pathlib import Path


class TransactionType(Enum):
    """Types of monetary transactions."""
    DEPOSIT = "deposit"
    WITHDRAWAL = "withdrawal"
    TRADE_OPEN = "trade_open"
    TRADE_CLOSE = "trade_close"
    FEE = "fee"
    FUNDING = "funding"  # For futures
    DIVIDEND = "dividend"
    ADJUSTMENT = "adjustment"


class PositionSide(Enum):
    """Position direction."""
    LONG = "long"
    SHORT = "short"


@dataclass
class Transaction:
    """Single monetary transaction with full audit trail."""
    timestamp: datetime
    transaction_type: TransactionType
    amount: float  # Positive for inflows, negative for outflows
    description: str
    reference_id: Optional[str] = None  # Trade ID, order ID, etc.
    metadata: dict = field(default_factory=dict)
    
    def to_dict(self) -> dict:
        """Convert to dictionary for serialization."""
        return {
            "timestamp": self.timestamp.isoformat(),
            "transaction_type": self.transaction_type.value,
            "amount": self.amount,
            "description": self.description,
            "reference_id": self.reference_id,
            "metadata": self.metadata,
        }


@dataclass
class Position:
    """Open position tracking."""
    symbol: str
    side: PositionSide
    entry_price: float
    units: float
    entry_time: datetime
    stop_loss: Optional[float] = None
    take_profit: Optional[float] = None
    strategy: Optional[str] = None
    regime: Optional[str] = None
    entry_q: Optional[float] = None
    
    @property
    def notional(self) -> float:
        """Current notional value."""
        return self.units * self.entry_price
    
    @property
    def unrealized_pnl(self, current_price: float) -> float:
        """Calculate unrealized PnL at current price."""
        if self.side == PositionSide.LONG:
            return (current_price - self.entry_price) * self.units
        else:
            return (self.entry_price - current_price) * self.units
    
    def to_dict(self) -> dict:
        """Convert to dictionary for serialization."""
        return {
            "symbol": self.symbol,
            "side": self.side.value,
            "entry_price": self.entry_price,
            "units": self.units,
            "entry_time": self.entry_time.isoformat(),
            "stop_loss": self.stop_loss,
            "take_profit": self.take_profit,
            "strategy": self.strategy,
            "regime": self.regime,
            "entry_q": self.entry_q,
        }


@dataclass
class Trade:
    """Completed trade record."""
    trade_id: str
    symbol: str
    side: PositionSide
    entry_price: float
    exit_price: float
    units: float
    entry_time: datetime
    exit_time: datetime
    gross_pnl: float
    fees: float
    net_pnl: float
    strategy: Optional[str] = None
    regime: Optional[str] = None
    entry_q: Optional[float] = None
    exit_q: Optional[float] = None
    stop_hit: bool = False
    target_hit: bool = False
    timeout: bool = False
    
    @property
    def duration_seconds(self) -> float:
        """Trade duration in seconds."""
        return (self.exit_time - self.entry_time).total_seconds()
    
    def to_dict(self) -> dict:
        """Convert to dictionary for serialization."""
        return {
            "trade_id": self.trade_id,
            "symbol": self.symbol,
            "side": self.side.value,
            "entry_price": self.entry_price,
            "exit_price": self.exit_price,
            "units": self.units,
            "entry_time": self.entry_time.isoformat(),
            "exit_time": self.exit_time.isoformat(),
            "duration_seconds": self.duration_seconds,
            "gross_pnl": self.gross_pnl,
            "fees": self.fees,
            "net_pnl": self.net_pnl,
            "strategy": self.strategy,
            "regime": self.regime,
            "entry_q": self.entry_q,
            "exit_q": self.exit_q,
            "stop_hit": self.stop_hit,
            "target_hit": self.target_hit,
            "timeout": self.timeout,
        }


class Account:
    """
    Unified account management with full accounting integrity.
    
    Implements the accounting equation:
    Opening Cash + Realized PnL - Fees - Funding ± Transfers = Ending Cash
    """
    
    def __init__(self, initial_balance: float, account_id: str = "default"):
        self.account_id = account_id
        self.initial_balance = initial_balance
        self.current_balance = initial_balance
        
        # PnL tracking
        self.realized_pnl = 0.0
        self.unrealized_pnl = 0.0
        self.total_fees = 0.0
        self.total_funding = 0.0
        
        # Position tracking
        self.positions: Dict[str, Position] = {}  # symbol -> Position
        
        # Transaction history
        self.transactions: List[Transaction] = []
        self.trades: List[Trade] = []
        
        # Performance tracking
        self.equity_curve: List[Tuple[datetime, float]] = []
        self.peak_equity = initial_balance
        self.max_drawdown = 0.0
        
        # Statistics
        self.total_trades = 0
        self.winning_trades = 0
        self.losing_trades = 0
        
        # Add initial deposit transaction
        self._add_transaction(
            TransactionType.DEPOSIT,
            initial_balance,
            "Initial deposit",
            reference_id="initial_deposit"
        )
    
    def _add_transaction(
        self,
        transaction_type: TransactionType,
        amount: float,
        description: str,
        reference_id: Optional[str] = None,
        metadata: dict = None
    ) -> None:
        """Add a transaction to the account history."""
        transaction = Transaction(
            timestamp=datetime.utcnow(),
            transaction_type=transaction_type,
            amount=amount,
            description=description,
            reference_id=reference_id,
            metadata=metadata or {}
        )
        self.transactions.append(transaction)
        
        # Update balance
        self.current_balance += amount
    
    def open_position(
        self,
        symbol: str,
        side: PositionSide,
        entry_price: float,
        units: float,
        strategy: Optional[str] = None,
        regime: Optional[str] = None,
        entry_q: Optional[float] = None,
        stop_loss: Optional[float] = None,
        take_profit: Optional[float] = None,
        commission: float = 0.0,
    ) -> Tuple[bool, str]:
        """
        Open a new position.
        
        Args:
            symbol: Market symbol
            side: LONG or SHORT
            entry_price: Entry price per unit
            units: Number of units
            strategy: Strategy name
            regime: Regime at entry
            entry_q: Q value at entry
            stop_loss: Stop loss price
            take_profit: Take profit price
            commission: Commission cost
        
        Returns:
            (success, error_message)
        """
        # Check if position already exists
        if symbol in self.positions:
            return False, f"Position already exists for {symbol}"
        
        # Check sufficient balance
        required_margin = units * entry_price
        if required_margin > self.current_balance:
            return False, f"Insufficient balance: ${required_margin:.2f} required, ${self.current_balance:.2f} available"
        
        # Create position
        position = Position(
            symbol=symbol,
            side=side,
            entry_price=entry_price,
            units=units,
            entry_time=datetime.utcnow(),
            stop_loss=stop_loss,
            take_profit=take_profit,
            strategy=strategy,
            regime=regime,
            entry_q=entry_q,
        )
        
        self.positions[symbol] = position
        
        # Deduct commission
        if commission > 0:
            self._add_transaction(
                TransactionType.FEE,
                -commission,
                f"Commission for opening {symbol} position",
                reference_id=f"{symbol}_open_fee"
            )
            self.total_fees += commission
        
        # Record trade open
        self._add_transaction(
            TransactionType.TRADE_OPEN,
            -required_margin,  # Deduct from available balance
            f"Open {side.value} position in {symbol}",
            reference_id=f"{symbol}_open"
        )
        
        return True, ""
    
    def close_position(
        self,
        symbol: str,
        exit_price: float,
        commission: float = 0.0,
        stop_hit: bool = False,
        target_hit: bool = False,
        timeout: bool = False,
        exit_q: Optional[float] = None,
    ) -> Tuple[bool, str, Optional[Trade]]:
        """
        Close an existing position.
        
        Args:
            symbol: Market symbol
            exit_price: Exit price per unit
            commission: Commission cost
            stop_hit: Whether stop loss was hit
            target_hit: Whether take profit was hit
            timeout: Whether trade timed out
            exit_q: Q value at exit
        
        Returns:
            (success, error_message, trade_record)
        """
        if symbol not in self.positions:
            return False, f"No position exists for {symbol}", None
        
        position = self.positions[symbol]
        
        # Calculate PnL
        if position.side == PositionSide.LONG:
            gross_pnl = (exit_price - position.entry_price) * position.units
        else:
            gross_pnl = (position.entry_price - exit_price) * position.units
        
        # Calculate net PnL
        net_pnl = gross_pnl - commission
        
        # Update statistics
        self.realized_pnl += gross_pnl
        self.total_fees += commission
        self.total_trades += 1
        
        if net_pnl > 0:
            self.winning_trades += 1
        else:
            self.losing_trades += 1
        
        # Add transactions
        exit_notional = position.units * exit_price
        self._add_transaction(
            TransactionType.TRADE_CLOSE,
            exit_notional,  # Add back to balance
            f"Close {position.side.value} position in {symbol}",
            reference_id=f"{symbol}_close"
        )
        
        if commission > 0:
            self._add_transaction(
                TransactionType.FEE,
                -commission,
                f"Commission for closing {symbol} position",
                reference_id=f"{symbol}_close_fee"
            )
        
        # Create trade record
        trade = Trade(
            trade_id=f"{symbol}_{position.entry_time.strftime('%Y%m%d_%H%M%S')}",
            symbol=symbol,
            side=position.side,
            entry_price=position.entry_price,
            exit_price=exit_price,
            units=position.units,
            entry_time=position.entry_time,
            exit_time=datetime.utcnow(),
            gross_pnl=gross_pnl,
            fees=commission,
            net_pnl=net_pnl,
            strategy=position.strategy,
            regime=position.regime,
            entry_q=position.entry_q,
            exit_q=exit_q,
            stop_hit=stop_hit,
            target_hit=target_hit,
            timeout=timeout,
        )
        
        self.trades.append(trade)
        
        # Remove position
        del self.positions[symbol]
        
        # Update equity curve
        self._update_equity_curve()
        
        return True, "", trade
    
    def update_unrealized_pnl(self, current_prices: Dict[str, float]) -> None:
        """
        Update unrealized PnL based on current market prices.
        
        Args:
            current_prices: {symbol: current_price}
        """
        total_unrealized = 0.0
        
        for symbol, position in self.positions.items():
            if symbol in current_prices:
                unrealized = position.unrealized_pnl(current_prices[symbol])
                total_unrealized += unrealized
        
        self.unrealized_pnl = total_unrealized
    
    def _update_equity_curve(self) -> None:
        """Update equity curve and drawdown tracking."""
        current_equity = self.current_balance + self.unrealized_pnl
        self.equity_curve.append((datetime.utcnow(), current_equity))
        
        # Update peak and drawdown
        if current_equity > self.peak_equity:
            self.peak_equity = current_equity
        
        drawdown = self.peak_equity - current_equity
        if drawdown > self.max_drawdown:
            self.max_drawdown = drawdown
    
    def get_account_summary(self) -> dict:
        """Get complete account summary."""
        self.update_unrealized_pnl({})  # Will just use current unrealized
        
        current_equity = self.current_balance + self.unrealized_pnl
        
        return {
            "account_id": self.account_id,
            "initial_balance": self.initial_balance,
            "current_balance": self.current_balance,
            "unrealized_pnl": self.unrealized_pnl,
            "realized_pnl": self.realized_pnl,
            "total_fees": self.total_fees,
            "total_funding": self.total_funding,
            "current_equity": current_equity,
            "total_return": (current_equity - self.initial_balance) / self.initial_balance,
            "peak_equity": self.peak_equity,
            "max_drawdown": self.max_drawdown,
            "max_drawdown_pct": self.max_drawdown / self.peak_equity if self.peak_equity > 0 else 0,
            "open_positions": len(self.positions),
            "total_trades": self.total_trades,
            "winning_trades": self.winning_trades,
            "losing_trades": self.losing_trades,
            "win_rate": self.winning_trades / self.total_trades if self.total_trades > 0 else 0,
        }
    
    def verify_accounting_equation(self) -> Tuple[bool, float, str]:
        """
        Verify the accounting equation:
        Opening Cash + Realized PnL - Fees - Funding ± Transfers = Ending Cash
        
        Returns:
            (is_valid, discrepancy, explanation)
        """
        # Calculate transfers (deposits - withdrawals)
        transfers = sum(
            t.amount for t in self.transactions 
            if t.transaction_type in [TransactionType.DEPOSIT, TransactionType.WITHDRAWAL]
        )
        
        # Calculate expected ending balance
        expected_balance = (
            self.initial_balance 
            + self.realized_pnl 
            - self.total_fees 
            - self.total_funding 
            + transfers
        )
        
        # Calculate discrepancy
        discrepancy = abs(self.current_balance - expected_balance)
        
        # Check validity (allow small floating-point tolerance)
        is_valid = discrepancy < 0.01  # 1 cent tolerance
        
        explanation = (
            f"Opening: ${self.initial_balance:.2f} + "
            f"Realized PnL: ${self.realized_pnl:.2f} - "
            f"Fees: ${self.total_fees:.2f} - "
            f"Funding: ${self.total_funding:.2f} + "
            f"Transfers: ${transfers:.2f} = "
            f"Expected: ${expected_balance:.2f} | "
            f"Actual: ${self.current_balance:.2f}"
        )
        
        return is_valid, discrepancy, explanation
    
    def get_position_value(self, symbol: str, current_price: float) -> float:
        """Get current value of a position."""
        if symbol not in self.positions:
            return 0.0
        
        position = self.positions[symbol]
        return position.units * current_price
    
    def get_leverage(self, symbol: str, current_price: float) -> float:
        """Calculate current leverage for a position."""
        if symbol not in self.positions:
            return 0.0
        
        position_value = self.get_position_value(symbol, current_price)
        if position_value == 0:
            return 0.0
        
        return position_value / self.current_balance
    
    def save_to_file(self, filepath: Path) -> None:
        """Save account state to file for persistence."""
        state = {
            "account_id": self.account_id,
            "initial_balance": self.initial_balance,
            "current_balance": self.current_balance,
            "realized_pnl": self.realized_pnl,
            "unrealized_pnl": self.unrealized_pnl,
            "total_fees": self.total_fees,
            "total_funding": self.total_funding,
            "positions": {k: v.to_dict() for k, v in self.positions.items()},
            "transactions": [t.to_dict() for t in self.transactions],
            "trades": [t.to_dict() for t in self.trades],
            "equity_curve": [(t.isoformat(), v) for t, v in self.equity_curve],
            "peak_equity": self.peak_equity,
            "max_drawdown": self.max_drawdown,
            "total_trades": self.total_trades,
            "winning_trades": self.winning_trades,
            "losing_trades": self.losing_trades,
        }
        
        with open(filepath, 'w') as f:
            json.dump(state, f, indent=2)
    
    @classmethod
    def load_from_file(cls, filepath: Path) -> 'Account':
        """Load account state from file."""
        with open(filepath, 'r') as f:
            state = json.load(f)
        
        account = cls(state["initial_balance"], state["account_id"])
        account.current_balance = state["current_balance"]
        account.realized_pnl = state["realized_pnl"]
        account.unrealized_pnl = state["unrealized_pnl"]
        account.total_fees = state["total_fees"]
        account.total_funding = state["total_funding"]
        account.peak_equity = state["peak_equity"]
        account.max_drawdown = state["max_drawdown"]
        account.total_trades = state["total_trades"]
        account.winning_trades = state["winning_trades"]
        account.losing_trades = state["losing_trades"]
        
        # Reconstruct positions
        for symbol, pos_dict in state["positions"].items():
            account.positions[symbol] = Position(
                symbol=pos_dict["symbol"],
                side=PositionSide(pos_dict["side"]),
                entry_price=pos_dict["entry_price"],
                units=pos_dict["units"],
                entry_time=datetime.fromisoformat(pos_dict["entry_time"]),
                stop_loss=pos_dict.get("stop_loss"),
                take_profit=pos_dict.get("take_profit"),
                strategy=pos_dict.get("strategy"),
                regime=pos_dict.get("regime"),
                entry_q=pos_dict.get("entry_q"),
            )
        
        # Reconstruct transactions
        for trans_dict in state["transactions"]:
            account.transactions.append(Transaction(
                timestamp=datetime.fromisoformat(trans_dict["timestamp"]),
                transaction_type=TransactionType(trans_dict["transaction_type"]),
                amount=trans_dict["amount"],
                description=trans_dict["description"],
                reference_id=trans_dict.get("reference_id"),
                metadata=trans_dict.get("metadata", {}),
            ))
        
        # Reconstruct trades
        for trade_dict in state["trades"]:
            account.trades.append(Trade(
                trade_id=trade_dict["trade_id"],
                symbol=trade_dict["symbol"],
                side=PositionSide(trade_dict["side"]),
                entry_price=trade_dict["entry_price"],
                exit_price=trade_dict["exit_price"],
                units=trade_dict["units"],
                entry_time=datetime.fromisoformat(trade_dict["entry_time"]),
                exit_time=datetime.fromisoformat(trade_dict["exit_time"]),
                gross_pnl=trade_dict["gross_pnl"],
                fees=trade_dict["fees"],
                net_pnl=trade_dict["net_pnl"],
                strategy=trade_dict.get("strategy"),
                regime=trade_dict.get("regime"),
                entry_q=trade_dict.get("entry_q"),
                exit_q=trade_dict.get("exit_q"),
                stop_hit=trade_dict.get("stop_hit", False),
                target_hit=trade_dict.get("target_hit", False),
                timeout=trade_dict.get("timeout", False),
            ))
        
        # Reconstruct equity curve
        account.equity_curve = [
            (datetime.fromisoformat(t), v) 
            for t, v in state["equity_curve"]
        ]
        
        return account


# ── Utility Functions ───────────────────────────────────────────────────────────

def calculate_position_size(
    account_balance: float,
    risk_per_trade: float,
    entry_price: float,
    stop_loss_price: float,
) -> float:
    """
    Calculate position size based on risk management rules.
    
    Args:
        account_balance: Current account balance
        risk_per_trade: Risk percentage (e.g., 0.01 for 1%)
        entry_price: Entry price per unit
        stop_loss_price: Stop loss price per unit
    
    Returns:
        Number of units to trade
    """
    risk_amount = account_balance * risk_per_trade
    stop_distance = abs(entry_price - stop_loss_price)
    
    if stop_distance == 0:
        return 0.0
    
    position_size = risk_amount / stop_distance
    return position_size


def calculate_risk_reward_ratio(
    entry_price: float,
    stop_loss_price: float,
    take_profit_price: float,
) -> float:
    """
    Calculate risk/reward ratio.
    
    Args:
        entry_price: Entry price
        stop_loss_price: Stop loss price
        take_profit_price: Take profit price
    
    Returns:
        Risk/reward ratio (reward:risk)
    """
    risk = abs(entry_price - stop_loss_price)
    reward = abs(take_profit_price - entry_price)
    
    if risk == 0:
        return 0.0
    
    return reward / risk