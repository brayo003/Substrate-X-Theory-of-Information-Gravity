"""live/broker/commission.py — Fixed fractional commission model."""

DEFAULT_RATE = 0.00030   # matches research COMMISSION_RT


class CommissionModel:
    def __init__(self, commission_map: dict):
        self._map = {k.upper(): float(v) for k, v in commission_map.items()}

    def compute(self, symbol: str, notional: float) -> float:
        """Return commission = notional * rate (round-trip included in rate)."""
        rate = self._map.get(symbol.upper(), DEFAULT_RATE)
        return abs(notional) * rate
