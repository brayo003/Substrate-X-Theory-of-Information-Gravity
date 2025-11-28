"""
Pure mathematical functions for domain alignment calculation
"""
import numpy as np
from typing import List

def compute_alignment(tensions: List[float]) -> float:
    """
    Calculate domain alignment from tension values.
    
    Alignment measures how synchronized/coherent domains are.
    Identical tensions → perfect alignment (1.0)
    Divergent tensions → low alignment (approaching 0.0)
    
    Args:
        tensions: List of tension values from multiple domains
        
    Returns:
        float: Alignment value between 0.0 and 1.0
    """
    if len(tensions) < 2:
        return 1.0  # Single domain is perfectly aligned with itself
    
    # Convert to numpy array
    tensions_array = np.array(tensions)
    
    # Calculate coefficient of variation (normalized standard deviation)
    mean_tension = np.mean(tensions_array)
    if mean_tension == 0:
        return 1.0  # All tensions are zero → perfect alignment
    
    cv = np.std(tensions_array) / mean_tension  # Coefficient of variation
    
    # Convert to alignment score (0.0 to 1.0)
    # CV = 0 → perfect alignment (1.0)
    # CV → ∞ → zero alignment (0.0)  
    alignment = 1.0 / (1.0 + cv)
    
    return float(np.clip(alignment, 0.0, 1.0))

def compute_tension_variance(tensions: List[float]) -> float:
    """
    Calculate variance of tension values (intermediate calculation).
    
    Args:
        tensions: List of tension values
        
    Returns:
        float: Variance of tensions
    """
    return float(np.var(tensions))
