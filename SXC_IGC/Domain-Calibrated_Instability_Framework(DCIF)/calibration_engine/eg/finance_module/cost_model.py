"""
cost_model.py — Unified Cost Model for Trading System

Single source of truth for all trading costs, exchange constraints, and execution parameters.
This replaces the fragmented cost constants across multiple files.

All phases (Phase 1-5, Live) must import from this file exclusively.
"""

from dataclasses import dataclass
from typing import Dict, Optional
from enum import Enum


class ExchangeType(Enum):
    """Supported exchange types."""
    BINANCE_SPOT = "binance_spot"
    BINANCE_FUTURES = "binance_futures"


class OrderType(Enum):
    """Order types for maker/taker distinction."""
    MARKET = "market"  # Taker
    LIMIT = "limit"    # Maker (if provides liquidity)


@dataclass
class MarketConstraints:
    """Exchange-specific trading constraints."""
    min_notional: float      # Minimum USD value per trade
    min_lot_size: float     # Minimum units per trade
    price_precision: int     # Decimal places for price
    quantity_precision: int  # Decimal places for quantity
    max_position: Optional[float] = None  # Maximum position size
    allow_shorting: bool = False


@dataclass
class CostParameters:
    """Cost parameters for a specific market."""
    commission_maker: float   # Maker fee rate (e.g., 0.001 = 0.1%)
    commission_taker: float   # Taker fee rate
    spread_pips: float       # Half-spread in quote currency
    slippage_sigma: float    # Standard deviation of slippage (optional)
    
    def get_commission(self, order_type: OrderType) -> float:
        """Get commission rate based on order type."""
        if order_type == OrderType.LIMIT:
            return self.commission_maker
        return self.commission_taker


# ── Market-Specific Configurations ───────────────────────────────────────────

# Binance Spot constraints (realistic values)
BINANCE_SPOT_CONSTRAINTS = MarketConstraints(
    min_notional=5.0,          # $5 minimum order value
    min_lot_size=0.001,        # 0.001 BTC minimum
    price_precision=2,          # 2 decimal places for USD pairs
    quantity_precision=3,      # 3 decimal places for crypto
    max_position=None,          # No hard limit on Spot
    allow_shorting=False,      # Spot does not allow shorting
)

# Binance Futures constraints (for future implementation)
BINANCE_FUTURES_CONSTRAINTS = MarketConstraints(
    min_notional=5.0,
    min_lot_size=0.001,
    price_precision=2,
    quantity_precision=3,
    max_position=1000.0,       # Example limit
    allow_shorting=True,       # Futures allow shorting
)


# ── Cost Parameters by Market ───────────────────────────────────────────────────

MARKET_COSTS: Dict[str, CostParameters] = {
    "BTCUSDT": CostParameters(
        commission_maker=0.0010,  # 0.10% maker
        commission_taker=0.0010,  # 0.10% taker
        spread_pips=0.50,         # $0.50 half-spread (realistic for BTC)
        slippage_sigma=0.0001,   # Optional: 1 bps slippage std
    ),
    "ETHUSDT": CostParameters(
        commission_maker=0.0010,  # 0.10% maker
        commission_taker=0.0010,  # 0.10% taker
        spread_pips=0.05,         # $0.05 half-spread (realistic for ETH)
        slippage_sigma=0.0001,
    ),
    "EURUSD": CostParameters(
        commission_maker=0.0002,  # 2 pips = 0.0002
        commission_taker=0.0002,  # 2 pips
        spread_pips=0.0001,       # 1 pip half-spread
        slippage_sigma=0.00005,  # 0.5 pip slippage
    ),
}

# Default for unknown markets
DEFAULT_COSTS = CostParameters(
    commission_maker=0.0010,
    commission_taker=0.0010,
    spread_pips=0.10,
    slippage_sigma=0.0001,
)


# ── Execution Parameters (formerly in multiple files) ─────────────────────────

# These replace the scattered constants from:
# - execution_simulator.py
# - strategy_library.py
# - p1_strategy_runner.py
# - p2_transport_os.py
# - live_config.py

HOLD_BARS = 24              # Maximum bars to hold position (2 hours at 5-min bars)
ATR_STOP_MULTIPLIER = 1.5   # Stop loss distance in ATR multiples
ATR_TARGET_MULTIPLIER = 2.5 # Take profit distance in ATR multiples

# Risk management (replaces BASE_RISK_PCT from p2_transport_os.py)
BASE_RISK_PCT = 0.01         # 1% max risk per trade
MAX_RISK_PCT = 0.02         # 2% absolute maximum risk per trade


# ── Utility Functions ───────────────────────────────────────────────────────────

def get_market_costs(market: str) -> CostParameters:
    """Get cost parameters for a specific market."""
    return MARKET_COSTS.get(market, DEFAULT_COSTS)


def get_market_constraints(market: str, exchange: ExchangeType = ExchangeType.BINANCE_SPOT) -> MarketConstraints:
    """Get trading constraints for a specific market and exchange."""
    if exchange == ExchangeType.BINANCE_SPOT:
        return BINANCE_SPOT_CONSTRAINTS
    elif exchange == ExchangeType.BINANCE_FUTURES:
        return BINANCE_FUTURES_CONSTRAINTS
    else:
        return BINANCE_SPOT_CONSTRAINTS  # Default


def calculate_commission(
    notional: float,
    commission_rate: float,
) -> float:
    """
    Calculate commission based on notional value.
    
    Args:
        notional: Trade value in USD (units * price)
        commission_rate: Commission rate (e.g., 0.001 = 0.1%)
    
    Returns:
        Commission amount in USD
    """
    return notional * commission_rate


def calculate_spread_cost(
    units: float,
    spread_pips: float,
) -> float:
    """
    Calculate spread cost (half-spread applied on entry and exit).
    
    Args:
        units: Number of units traded
        spread_pips: Half-spread in quote currency
    
    Returns:
        Total spread cost for round-trip (entry + exit)
    """
    return units * spread_pips * 2  # Round-trip cost


def calculate_total_cost(
    units: float,
    entry_price: float,
    exit_price: float,
    commission_rate: float,
    spread_pips: float,
) -> float:
    """
    Calculate total trading cost for a round-trip trade.
    
    Args:
        units: Number of units traded
        entry_price: Entry price per unit
        exit_price: Exit price per unit
        commission_rate: Commission rate per side
        spread_pips: Half-spread in quote currency
    
    Returns:
        Total cost in quote currency
    """
    entry_notional = units * entry_price
    exit_notional = units * exit_price
    
    # Commission (both sides)
    entry_commission = calculate_commission(entry_notional, commission_rate)
    exit_commission = calculate_commission(exit_notional, commission_rate)
    
    # Spread (both sides)
    spread_cost = calculate_spread_cost(units, spread_pips)
    
    return entry_commission + exit_commission + spread_cost


def validate_order_constraints(
    units: float,
    price: float,
    market: str,
    exchange: ExchangeType = ExchangeType.BINANCE_SPOT,
) -> tuple[bool, str]:
    """
    Validate order against exchange constraints.
    
    Args:
        units: Number of units
        price: Price per unit
        market: Market symbol
        exchange: Exchange type
    
    Returns:
        (is_valid, error_message)
    """
    constraints = get_market_constraints(market, exchange)
    
    notional = units * price
    
    # Check minimum notional
    if notional < constraints.min_notional:
        return False, f"Order notional ${notional:.2f} below minimum ${constraints.min_notional}"
    
    # Check minimum lot size
    if units < constraints.min_lot_size:
        return False, f"Order size {units} below minimum {constraints.min_lot_size}"
    
    # Check maximum position (if set)
    if constraints.max_position and units > constraints.max_position:
        return False, f"Order size {units} exceeds maximum {constraints.max_position}"
    
    # Check shorting constraint
    if not constraints.allow_shorting and units < 0:
        return False, "Shorting not allowed on this exchange"
    
    return True, ""


def apply_rounding(
    price: float,
    quantity: float,
    market: str,
    exchange: ExchangeType = ExchangeType.BINANCE_SPOT,
) -> tuple[float, float]:
    """
    Apply exchange-specific rounding to price and quantity.
    
    Args:
        price: Raw price
        quantity: Raw quantity
        market: Market symbol
        exchange: Exchange type
    
    Returns:
        (rounded_price, rounded_quantity)
    """
    constraints = get_market_constraints(market, exchange)
    
    rounded_price = round(price, constraints.price_precision)
    rounded_quantity = round(quantity, constraints.quantity_precision)
    
    return rounded_price, rounded_quantity


# ── Legacy Compatibility Layer ─────────────────────────────────────────────────

# These constants provide backward compatibility during migration
# TODO: Remove after all files are updated to use new structure

# Phase 1 legacy (from execution_simulator.py, strategy_library.py)
COMMISSION_PER_SIDE_LEGACY = 0.00010   # 1 pip per side
SLIPPAGE_PER_SIDE_LEGACY = 0.00005     # 0.5 pip per side
TOTAL_COST_RT_LEGACY = 2 * (COMMISSION_PER_SIDE_LEGACY + SLIPPAGE_PER_SIDE_LEGACY)

# Phase 2 legacy (from p2_transport_os.py)
COMMISSION_RT_LEGACY = 0.00030        # 3 pip round-trip

# Live config legacy (from live_config.py)
INITIAL_BALANCE_LEGACY = 10_000.0      # USD


# ── Migration Guide ─────────────────────────────────────────────────────────────

"""
MIGRATION GUIDE FOR EXISTING CODE:

OLD (execution_simulator.py):
    COMMISSION_PER_SIDE = 0.00010
    SLIPPAGE_PER_SIDE = 0.00005
    net_ret = gross_ret - TOTAL_COST_RT / entry_price

NEW:
    from cost_model import get_market_costs, calculate_total_cost
    costs = get_market_costs("EURUSD")
    total_cost = calculate_total_cost(units, entry_price, exit_price, 
                                       costs.commission_taker, costs.spread_pips)
    net_ret = gross_ret - total_cost / (units * entry_price)

OLD (p2_transport_os.py):
    COMMISSION_RT = 0.00030
    net = gross - COMMISSION_RT / state.entry_price

NEW:
    from cost_model import get_market_costs, calculate_commission
    costs = get_market_costs("EURUSD")
    notional = units * state.entry_price
    commission = calculate_commission(notional, costs.commission_taker)
    net = gross - commission / notional

OLD (live_config.py):
    SPREAD_PIPS = {"BTCUSDT": 1.0, "ETHUSDT": 0.10}
    COMMISSION_PCT = {"BTCUSDT": 0.00030, "ETHUSDT": 0.00030}

NEW:
    from cost_model import get_market_costs
    btc_costs = get_market_costs("BTCUSDT")
    eth_costs = get_market_costs("ETHUSDT")
    # Use btc_costs.commission_taker, btc_costs.spread_pips, etc.
"""