import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, Any

# Assuming 100 data points (trading days)

def _create_base_series(n_points: int, base_value: float, noise_std: float, trend_start: float = 0.0, trend_end: float = 0.0) -> np.ndarray:
    """Helper to create noisy series with optional linear trend."""
    series = np.full(n_points, base_value)
    series *= (1.0 + np.random.randn(n_points) * noise_std)
    if trend_start != trend_end:
        series *= (1.0 + np.linspace(trend_start, trend_end, n_points))
    return np.clip(series, 1e-6, None) # Ensure positive

def generate_finance_stable_period(n_points: int = 100) -> Dict[str, Any]:
    """
    Generates synthetic finance data for a STABLE regime (T ≈ 0.0).
    Characteristics: Low Volatility (E), High Liquidity (F).
    """
    
    start_date = datetime(2023, 1, 1)
    timestamps = np.array([start_date + timedelta(days=i) for i in range(n_points)])
    
    # 1. ACCUMULATION (ρ): Slow, steady order imbalance accumulation.
    # Proxy: Normalized Net Order Imbalance (NOI)
    rho_raw = _create_base_series(n_points, base_value=0.05, noise_std=0.1)
    rho_smooth = pd.Series(rho_raw).rolling(window=5).mean().fillna(0.05).values
    
    # 2. EXCITATION (E): Low Volatility Regime (Normalized Daily Range)
    E_raw = _create_base_series(n_points, base_value=0.05, noise_std=0.15)
    E_mean = np.mean(E_raw)  # Expect low mean (e.g., ~0.05)
    
    # 3. RESILIENCE (F): High Liquidity (Normalized Inverse Bid-Ask Spread)
    # F should be near 1.0, meaning high damping capacity.
    F_raw = _create_base_series(n_points, base_value=0.9, noise_std=0.05)
    F_mean = np.mean(F_raw) # Expect high mean (e.g., ~0.90)
    
    # --- Output ---
    return {
        'timestamps': timestamps,
        'rho_series': rho_smooth,
        'E_series': E_raw,
        'F_series': F_raw,
        'E_mean_expected': E_mean,
        'F_mean_expected': F_mean
    }

def generate_finance_crisis_period(n_points: int = 100) -> Dict[str, Any]:
    """
    Generates synthetic finance data for a PRE-CRISIS regime (T ≈ 0.7).
    Characteristics: High Volatility (E), Collapsing Liquidity (F).
    """
    
    start_date = datetime(2024, 6, 1)
    timestamps = np.array([start_date + timedelta(days=i) for i in range(n_points)])
    
    # 1. ACCUMULATION (ρ): Increasing stress/imbalance leading up to event.
    rho_raw = _create_base_series(n_points, base_value=0.2, noise_std=0.2, trend_end=0.5)
    rho_smooth = pd.Series(rho_raw).rolling(window=5).mean().fillna(0.2).values
    
    # 2. EXCITATION (E): High Volatility Regime
    # E should be significantly higher than stable (e.g., ~0.25) and increasing.
    E_raw = _create_base_series(n_points, base_value=0.2, noise_std=0.2, trend_end=0.2)
    E_mean = np.mean(E_raw) # Expect high mean (e.g., ~0.25)
    
    # 3. RESILIENCE (F): Collapsing Liquidity
    # F should be low (e.g., ~0.35) and trending downwards.
    F_raw = _create_base_series(n_points, base_value=0.4, noise_std=0.1, trend_end=-0.1)
    F_mean = np.mean(F_raw) # Expect low mean (e.g., ~0.35)
    
    # --- Output ---
    return {
        'timestamps': timestamps,
        'rho_series': rho_smooth,
        'E_series': E_raw,
        'F_series': F_raw,
        'E_mean_expected': E_mean,
        'F_mean_expected': F_mean
    }

if __name__ == "__main__":
    # Simple test case execution to see the generated means
    np.random.seed(42)
    stable = generate_finance_stable_period()
    crisis = generate_finance_crisis_period()
    
    print("="*40)
    print("Finance Data Generator Test (Seed 42)")
    print("="*40)
    print("STABLE PERIOD (T ≈ 0.0 Target)")
    print(f"  E Mean: {np.mean(stable['E_series']):.4f} (Expected: Low)")
    print(f"  F Mean: {np.mean(stable['F_series']):.4f} (Expected: High)")
    print("\nCRISIS PERIOD (T ≈ 0.7 Target)")
    print(f"  E Mean: {np.mean(crisis['E_series']):.4f} (Expected: High)")
    print(f"  F Mean: {np.mean(crisis['F_series']):.4f} (Expected: Low)")
    print("="*40)

# Note: The actual factors used for calibration will be the observed means 
# from running the Analyzer, not the expected means.
