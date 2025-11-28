"""
Pure mathematical functions for tension calculation
"""
import numpy as np
from typing import List, Union

def compute_tension(concentration_data: Union[List[float], np.ndarray]) -> float:
    """
    Calculate tension from concentration data.
    
    Tension measures the spatial variability/gradient in concentration.
    Uniform concentration → zero tension.
    
    Args:
        concentration_data: Array of concentration values
        
    Returns:
        float: Tension value (≥ 0)
    """
    data = np.array(concentration_data)
    
    # Calculate gradient (spatial derivative)
    gradient = np.gradient(data)
    
    # Tension is related to the magnitude of gradient
    # For uniform data, gradient = 0 → tension = 0
    tension = np.sqrt(np.mean(gradient**2))
    
    return float(tension)

def compute_tension_variance(tensions: List[float]) -> float:
    """
    Calculate variance of tension values across domains.
    
    Args:
        tensions: List of tension values from multiple domains
        
    Returns:
        float: Variance of tensions
    """
    return float(np.var(tensions))
