"""live/broker/spread.py — Fixed spread model."""


class SpreadModel:
    DEFAULT_SPREAD = 1.0

    def __init__(self, spread_map: dict):
        self._map = {k.upper(): float(v) for k, v in spread_map.items()}

    def apply_buy(self, symbol: str, mid_price: float) -> float:
        """Return ask price (buyer pays mid + half spread)."""
        return mid_price + self._map.get(symbol.upper(), self.DEFAULT_SPREAD) / 2

    def apply_sell(self, symbol: str, mid_price: float) -> float:
        """Return bid price (seller receives mid - half spread)."""
        return mid_price - self._map.get(symbol.upper(), self.DEFAULT_SPREAD) / 2
