#!/usr/bin/env python3
"""
MINIMAL DCII IMPLEMENTATION
Simple, working version without complex features
"""

import json
import numpy as np
import pandas as pd
from datetime import datetime
from pathlib import Path
from typing import Dict, List
from scipy import optimize

class MinimalDCII:
    """Minimal DCII implementation."""
    
    def __init__(self, name="Market_DCII"):
        self.name = name
        self.signals = {}
        self.norm_params = {}
        self.beta = 1.0
        self.gamma = 1.0
    
    def create_data(self):
        """Create example data."""
        dates = pd.date_range(end=datetime.now(), periods=500, freq='B')
        np.random.seed(42)
        
        self.signals = {
            'volatility': pd.Series(20 + 10*np.random.randn(len(dates)), index=dates),
            'returns': pd.Series(0.0002 + 0.01*np.random.randn(len(dates)), index=dates),
            'liquidity': pd.Series(np.random.lognormal(0, 0.3, len(dates)), index=dates),
        }
        return self
    
    def normalize(self):
        """Normalize signals."""
        self.norm_params = {}
        for name, series in self.signals.items():
            mean, std = series.mean(), series.std()
            self.norm_params[name] = {'mean': float(mean), 'std': float(std)}
        return self
    
    def normalize_current(self, current: Dict[str, float]) -> Dict[str, float]:
        """Normalize current values."""
        norm = {}
        for name, value in current.items():
            if name in self.norm_params:
                params = self.norm_params[name]
                z = (value - params['mean']) / (params['std'] + 1e-8)
                norm[name] = 1 / (1 + np.exp(-z))
            else:
                norm[name] = value
        return norm
    
    def calibrate(self):
        """Simple calibration."""
        # Define scenarios
        scenarios = [
            {'signals': {'volatility': 0.2, 'returns': 0.2, 'liquidity': 0.2}, 'target': 0.2},
            {'signals': {'volatility': 0.5, 'returns': 0.5, 'liquidity': 0.5}, 'target': 0.5},
            {'signals': {'volatility': 0.8, 'returns': 0.8, 'liquidity': 0.8}, 'target': 0.8},
        ]
        
        def objective(params):
            beta, gamma = params
            error = 0
            for scen in scenarios:
                signals = list(scen['signals'].values())
                pressure = beta * np.mean(signals)
                resilience = gamma * np.std(signals) if len(signals) > 1 else 0
                dcii = pressure - resilience
                error += (dcii - scen['target'])**2
            return error
        
        result = optimize.minimize(objective, [1.0, 1.0], bounds=[(0.5, 2.0), (0.5, 2.0)])
        if result.success:
            self.beta, self.gamma = result.x
            print(f"Calibrated: β={self.beta:.3f}, γ={self.gamma:.3f}")
        return self
    
    def compute(self, signals: Dict[str, float]) -> float:
        """Compute DCII."""
        values = list(signals.values())
        pressure = self.beta * np.mean(values)
        resilience = self.gamma * np.std(values) if len(values) > 1 else 0
        dcii = pressure - resilience
        return max(0, min(1, dcii))
    
    def monitor(self, current: Dict[str, float]) -> Dict:
        """Monitor current conditions."""
        norm = self.normalize_current(current)
        dcii = self.compute(norm)
        
        if dcii < 0.3:
            level = "Stable"
        elif dcii < 0.5:
            level = "Elevated"
        elif dcii < 0.7:
            level = "High"
        else:
            level = "Critical"
        
        return {
            'dcii': float(dcii),
            'level': level,
            'time': datetime.now().isoformat(),
            'signals': norm
        }
    
    def run(self):
        """Run minimal pipeline."""
        print("Minimal DCII Pipeline")
        print("="*40)
        
        self.create_data()
        self.normalize()
        self.calibrate()
        
        # Test
        test = {'volatility': 30, 'returns': -0.02, 'liquidity': 0.8}
        result = self.monitor(test)
        
        print(f"\nTest Results:")
        print(f"  DCII: {result['dcii']:.3f}")
        print(f"  Level: {result['level']}")
        print(f"  Time: {result['time']}")
        
        return result

# Quick usage
if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "run":
        dcii = MinimalDCII()
        dcii.run()
    else:
        # Simple test
        dcii = MinimalDCII()
        dcii.create_data().normalize().calibrate()
        
        # Test monitoring
        test_signals = {'volatility': 25, 'returns': -0.01, 'liquidity': 1.2}
        result = dcii.monitor(test_signals)
        
        print(json.dumps(result, indent=2))
