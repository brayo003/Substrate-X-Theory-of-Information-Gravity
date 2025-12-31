import numpy as np
from typing import Dict, Any

def _create_base_series(n_points: int, base_value: float, noise_std: float) -> np.ndarray:
    """Helper to create noisy, positive series."""
    series = np.full(n_points, base_value)
    series *= (1.0 + np.random.randn(n_points) * noise_std)
    return np.clip(series, 1e-6, None) 

def generate_social_stable_period(n_points: int = 100) -> Dict[str, Any]:
    """
    Generates synthetic social media data for a STABLE regime (T ≈ 0.0 Target).
    Characteristics: Low Posting Velocity (E), High Moderation/Fatigue (F).
    """
    np.random.seed(88) # Fixed seed for consistent factor means
    
    # E (Excitation): Low Posting Velocity
    E_raw = _create_base_series(n_points, base_value=0.01, noise_std=0.1)
    E_mean = np.mean(E_raw) 
    
    # F (Resilience): High Moderation/Fatigue
    F_raw = _create_base_series(n_points, base_value=0.75, noise_std=0.05)
    F_mean = np.mean(F_raw)
    
    return {'E_series': E_raw, 'F_series': F_raw, 'E_mean': E_mean, 'F_mean': F_mean}

def generate_social_crisis_period(n_points: int = 100) -> Dict[str, Any]:
    """
    Generates synthetic social media data for a CASCADE regime (T ≈ 0.9 Target).
    Characteristics: Very High Posting Velocity (E), Low Moderation/Fatigue (F).
    """
    np.random.seed(88) # Fixed seed for consistent factor means
    
    # E (Excitation): Very High Posting Velocity
    E_raw = _create_base_series(n_points, base_value=0.25, noise_std=0.2)
    E_mean = np.mean(E_raw) 
    
    # F (Resilience): Low Moderation/Fatigue (Algorithmic Decay is weak)
    F_raw = _create_base_series(n_points, base_value=0.1, noise_std=0.1)
    F_mean = np.mean(F_raw) 
    
    return {'E_series': E_raw, 'F_series': F_raw, 'E_mean': E_mean, 'F_mean': F_mean}

if __name__ == "__main__":
    stable = generate_social_stable_period()
    crisis = generate_social_crisis_period()
    
    print("="*45)
    print("Social Data Generator Test (Seed 88)")
    print("="*45)
    print("STABLE PERIOD (T ≈ 0.0 Target)")
    print(f"  E Mean (Velocity): {stable['E_mean']:.4f}")
    print(f"  F Mean (Damping):  {stable['F_mean']:.4f}")
    print("\nCRISIS PERIOD (T ≈ 0.9 Target)")
    print(f"  E Mean (Velocity): {crisis['E_mean']:.4f}")
    print(f"  F Mean (Damping):  {crisis['F_mean']:.4f}")
    print("="*45)

