import numpy as np
from typing import List, Dict

def calculate_tension(history: List[np.ndarray], external_pressure: float) -> float:
    """
    Calculates Tension based on recent field variance and external pressure.
    Tension measures the stress/volatility of the information field.
    """
    if len(history) < 2:
        return 0.0

    # Calculate recent volatility (variance of the last two states)
    current_state = history[-1]
    prev_state = history[-2]
    
    # Simple L2 distance/change rate
    field_change_rate = np.linalg.norm(current_state - prev_state) / current_state.size
    
    # Tension model: high change rate + high external pressure = high tension
    tension_raw = field_change_rate * external_pressure * 5.0 # Scaled factor
    
    # Normalize Tension (0.0 to 1.0)
    tension = np.clip(tension_raw, 0.0, 1.0)
    
    return tension

def calculate_momentum(history: List[np.ndarray]) -> float:
    """
    Calculates Momentum based on the average displacement vector of the field.
    Momentum measures the overall directional velocity or trend strength.
    """
    if len(history) < 3:
        return 0.0

    # Look at the mean concentration change over the last few steps
    mean_displacement = np.mean([np.linalg.norm(history[i] - history[i-1]) for i in range(1, len(history))])
    
    # Normalize Momentum (0.0 to 1.0, adjusted for grid size)
    # Scale factor based on grid size (e.g., 16x16 grid = 256 cells)
    grid_size_norm = np.sqrt(history[0].size) # Use sqrt for better scaling
    momentum_raw = mean_displacement * 10.0 / grid_size_norm 
    
    momentum = np.clip(momentum_raw, 0.0, 1.0)
    return momentum

def calculate_variance(history: List[np.ndarray]) -> float:
    """
    Calculates Variance based on the overall dispersion of the current field state.
    Variance measures the structural heterogeneity or disorder.
    """
    if not history:
        return 0.0
    
    current_state = history[-1]
    # Variance of the field distribution itself
    variance = np.clip(current_state.var() * 5.0, 0.0, 1.0) # Scale variance for normalization
    
    return variance

def generate_domain_tmv_metrics(history: List[np.ndarray], external_pressure: float) -> Dict[str, float]:
    """
    Composite function to generate all T-M-V metrics for a domain state.
    """
    metrics = {
        "Tension": calculate_tension(history, external_pressure),
        "Momentum": calculate_momentum(history),
        "Variance": calculate_variance(history)
    }
    return metrics

if __name__ == '__main__':
    # Simple test case for the metrics
    print("--- Dynamic Metrics Core Test ---")
    
    # Setup history: low change, low variance
    h1 = np.ones((4, 4)) * 0.5
    h2 = h1 + np.random.normal(0, 0.01, (4, 4))
    h3 = h2 + np.random.normal(0, 0.01, (4, 4))
    
    history_low = [h1, h2, h3]
    metrics_low = generate_domain_tmv_metrics(history_low, external_pressure=0.1)
    print(f"Low Volatility Test (Pressure=0.1): {metrics_low}")
    
    # Setup history: high change, high variance
    h4 = np.random.rand(4, 4) # High variance start
    h5 = h4 + np.random.normal(0, 0.5, (4, 4)) # High change
    h6 = h5 + np.random.normal(0, 0.5, (4, 4))
    
    history_high = [h4, h5, h6]
    metrics_high = generate_domain_tmv_metrics(history_high, external_pressure=0.9)
    print(f"High Volatility Test (Pressure=0.9): {metrics_high}")
