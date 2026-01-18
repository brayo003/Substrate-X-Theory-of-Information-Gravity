"""
DCII Core Classes
Core mathematical framework for Domain-Calibrated Instability Index
"""

import numpy as np
from typing import Dict, Optional, Any
from dataclasses import dataclass

class DCIIEquation:
    """Core DCII differential equation solver."""
    
    def __init__(self, alpha=0.0, beta=1.0, gamma=1.0):
        self.alpha = alpha
        self.beta = beta
        self.gamma = gamma
    
    def compute(self, signals: Dict[str, float], gradient_terms: Optional[Dict[str, float]] = None) -> float:
        """Compute DCII index from normalized signals [0,1]."""
        if not signals:
            return 0.0
        
        # Pressure term (β-weighted average of signals)
        pressure = sum(self.beta * s for s in signals.values()) / len(signals)
        
        # Resilience term (γ-weighted dispersion)
        signal_values = list(signals.values())
        if len(signal_values) > 1:
            dispersion = np.std(signal_values)
            resilience = self.gamma * dispersion
        else:
            resilience = 0.0
        
        # Gradient term (if provided)
        gradient = 0.0
        if gradient_terms:
            gradient = self.alpha * sum(gradient_terms.values())
        
        # DCII equation: ρ = pressure - resilience + gradient
        dcii = pressure - resilience + gradient
        
        # Bound between 0 and 1
        return max(0.0, min(1.0, dcii))

@dataclass
class CalibrationResult:
    """Results from DCII calibration."""
    beta: float
    gamma: float
    alpha: float = 0.0
    r_squared: float = 0.0
    mse: float = 0.0
    is_valid: bool = False
    validation_metrics: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.validation_metrics is None:
            self.validation_metrics = {}

@dataclass 
class StressScenario:
    """Definition of a stress scenario for calibration."""
    name: str
    signals: Dict[str, float]
    target_dcii: float
    weight: float = 1.0
