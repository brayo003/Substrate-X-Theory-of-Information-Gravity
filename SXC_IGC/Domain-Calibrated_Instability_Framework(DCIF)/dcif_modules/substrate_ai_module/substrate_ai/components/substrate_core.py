# V12_SYNC_VERIFIED: 2026-03-13
#!/usr/bin/env python3
"""
V12 SUBSTRATE CORE - The physics engine
"""
import numpy as np

class SubstrateDynamics:
    def __init__(self):
        # V12 PARAMETERS from your bridge
        self.r = 0.153
        self.a = 1.0
        self.b = 1.0
        
        # Regime thresholds
        self.thresholds = {
            'vanilla': 0.3,
            'transitional': 0.6,
            'high_tension': 0.9,
            'saturated': 1.0
        }
    
    def calculate_tension(self, complexity: float, ambiguity: float, novelty: float) -> float:
        """V12 tension calculation"""
        input_rate = 0.4*complexity + 0.3*ambiguity + 0.3*novelty
        r_effective = self.r * input_rate
        
        discriminant = self.a**2 + 4 * self.b * r_effective
        
        if discriminant >= 0:
            x1 = (self.a + np.sqrt(discriminant)) / (2 * self.b)
            x2 = (self.a - np.sqrt(discriminant)) / (2 * self.b)
            solutions = [x for x in (x1, x2) if 0 < x <= 1.0]
            if solutions:
                return max(solutions)
        
        return min(input_rate, 1.0)
    
    def determine_regime(self, tension: float) -> str:
        """Map tension to regime"""
        if tension < self.thresholds['vanilla']:
            return 'vanilla'
        elif tension < self.thresholds['transitional']:
            return 'transitional'
        elif tension < self.thresholds['high_tension']:
            return 'high_tension'
        else:
            return 'saturated'
