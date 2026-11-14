"""live/broker/slippage.py — Optional stochastic slippage model."""

import random


class SlippageModel:
    """
    Applies market impact slippage to fill prices.
    Disabled in Phase 6A. Architecture supports future stochastic modes.
    """

    def __init__(self, enabled: bool = False, sigma: float = 0.0001):
        self.enabled = enabled
        self.sigma   = sigma

    def apply(self, symbol: str, price: float, direction: int) -> float:
        """
        direction: +1 for buys (slippage worsens fill upward),
                   -1 for sells (slippage worsens fill downward).
        Returns price unchanged when disabled.
        """
        if not self.enabled or self.sigma <= 0:
            return price
        impact = abs(random.gauss(0, self.sigma * price))
        return price + direction * impact
