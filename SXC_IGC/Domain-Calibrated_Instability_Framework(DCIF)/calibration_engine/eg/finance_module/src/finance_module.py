"""
Finance DCII Module
Main class implementing the 9-step pipeline
"""

import pandas as pd
import numpy as np
from pathlib import Path
from typing import Dict, Any
from datetime import datetime
import json
import warnings

from dcii_core import DCIIEquation, CalibrationResult, StressScenario

warnings.filterwarnings('ignore')

class FinanceDCIIModule:
    """DCII Finance Module for US Equity Markets."""
    
    def __init__(self, name: str = "US_Equity_Markets_DCII"):
        self.name = name
        self.metadata = {
            'creation_date': datetime.now().strftime('%Y-%m-%d'),
            'calibration_date': None,
            'version': '1.0'
        }
        self.signals = {}
        self.normalized_signals = {}
        self.normalization_params = {}
        self.scenarios = {}
        self.coefficients = {'alpha': 0.0, 'beta': 1.0, 'gamma': 1.0}
        self.calibration_result = None
        self.stress_taxonomy = {}
        self.dcii_equation = DCIIEquation()
    
    # Step 1: Domain Definition
    def define_domain(self):
        """Step 1: Define the domain scope."""
        print("STEP 1: DOMAIN DEFINITION")
        print("-"*70)
        print("Domain: US Equity Markets")
        print("Scope: S&P 500 constituents and related derivatives")
        print("Time Horizon: Daily monitoring")
        print("Signals: Volatility, liquidity, momentum, sentiment")
        print()
        return {"market": "US Equity", "scope": "S&P 500"}
    
    # Step 2: Signal Definition
    def define_signals(self):
        """Step 2: Define market signals with SIMULATED data."""
        dates = pd.date_range(start='2020-01-01', end='2023-12-31', freq='B')
        np.random.seed(42)
        n = len(dates)
        t = np.arange(n) / 252
        
        self.signals = {
            'vix': pd.Series(20 + 10*np.sin(2*np.pi*t) + 5*np.random.randn(n), index=dates),
            'returns': pd.Series(0.0002 + 0.01*np.random.randn(n), index=dates),
            'volume': pd.Series(np.random.lognormal(0, 0.3, n), index=dates),
            'spread': pd.Series(np.random.exponential(0.02, n), index=dates),
            'pc_ratio': pd.Series(np.random.beta(2, 3, n)*1.5, index=dates),
        }
        
        print("STEP 2: SIGNAL DEFINITION")
        print("-"*70)
        for name, series in self.signals.items():
            print(f"  {name:15} | mean: {series.mean():7.4f} | std: {series.std():7.4f}")
        print()
        return self.signals
    
    # Step 3: Signal Normalization
    def normalize_signals(self, method='zscore'):
        """Step 3: Normalize signals to [0,1] range."""
        self.normalized_signals = {}
        self.normalization_params = {}
        
        for name, series in self.signals.items():
            if method == 'zscore':
                z = (series - series.mean()) / (series.std() + 1e-8)
                norm = 1 / (1 + np.exp(-z))
                self.normalization_params[name] = {'method': 'zscore', 'mean': float(series.mean()), 'std': float(series.std())}
            else:  # minmax
                mn, mx = series.min(), series.max()
                norm = (series - mn) / (mx - mn + 1e-8)
                self.normalization_params[name] = {'method': 'minmax', 'min': float(mn), 'max': float(mx)}
            
            self.normalized_signals[name] = pd.Series(norm, index=series.index)
        
        print("STEP 3: SIGNAL NORMALIZATION")
        print("-"*70)
        print(f"Method: {method}")
        for name, series in self.normalized_signals.items():
            print(f"  {name:15} | range: [{series.min():.3f}, {series.max():.3f}]")
        print()
        return self.normalized_signals
    
    # Step 4: Target States
    def define_target_states(self):
        """Step 4: Define target DCII states."""
        signal_names = list(self.normalized_signals.keys())
        
        self.scenarios = {
            'stable': StressScenario('stable', {n: 0.2 for n in signal_names}, 0.2, 1.0),
            'elevated': StressScenario('elevated', {n: 0.5 for n in signal_names}, 0.5, 1.0),
            'crisis': StressScenario('crisis', {n: 0.8 for n in signal_names}, 0.8, 2.0),
            'recovery': StressScenario('recovery', {n: 0.4 for n in signal_names}, 0.4, 1.0),
        }
        
        print("STEP 4: TARGET STATES")
        print("-"*70)
        for name, scen in self.scenarios.items():
            print(f"  {name:10} | Target: {scen.target_dcii:.2f} | Weight: {scen.weight:.1f}")
        print()
        return self.scenarios
    
    # Step 5: Stress Taxonomy
    def classify_stress_taxonomy(self):
        """Step 5: Classify stress levels."""
        self.stress_taxonomy = {
            'stable': {'range': (0.0, 0.3), 'color': 'green', 'actions': ['Normal ops']},
            'elevated': {'range': (0.3, 0.5), 'color': 'yellow', 'actions': ['Monitor']},
            'high': {'range': (0.5, 0.7), 'color': 'orange', 'actions': ['Reduce risk']},
            'critical': {'range': (0.7, 1.0), 'color': 'red', 'actions': ['Crisis mode']},
        }
        
        print("STEP 5: STRESS TAXONOMY")
        print("-"*70)
        for level, info in self.stress_taxonomy.items():
            low, high = info['range']
            print(f"  {level:10} | DCII: {low:.1f}-{high:.1f} | Action: {info['actions'][0]}")
        print()
        return self.stress_taxonomy
