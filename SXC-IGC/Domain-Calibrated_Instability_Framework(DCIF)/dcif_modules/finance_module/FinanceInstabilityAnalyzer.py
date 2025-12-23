import numpy as np
import pandas as pd
from typing import Dict, Any, Tuple
import os
import sys

# --- Dynamic Path Insertion for Core Infrastructure (Calibration Engine) ---
# This ensures modularity: the analyzer can access the solver.py file.
# We navigate up two directories (finance_module -> dcii_modules -> DCIF) 
# and down into 'calibration_engine'.

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FRAMEWORK_ROOT = os.path.abspath(os.path.join(BASE_DIR, '..', '..'))
CALIBRATION_ENGINE_PATH = os.path.join(FRAMEWORK_ROOT, 'calibration_engine')

if CALIBRATION_ENGINE_PATH not in sys.path:
    sys.path.append(CALIBRATION_ENGINE_PATH)

# Import the core solver function from the infrastructure layer
try:
    from solver import solve_dcii_coefficients_two_anchor
except ImportError:
    print(f"FATAL ERROR: Could not import solver.py from {CALIBRATION_ENGINE_PATH}")
    print("Please ensure solver.py is in the 'calibration_engine' directory.")
    sys.exit(1)

# Import the local data generator
try:
    from finance_data_generator import generate_finance_stable_period, generate_finance_crisis_period
except ImportError:
    print("FATAL ERROR: Could not import finance_data_generator.py.")
    sys.exit(1)

class FinanceInstabilityAnalyzer:
    """
    Analyzer for computing ρ, E, F in the FINANCE DOMAIN.
    Contains signal extraction logic for calibration.
    """
    
    def __init__(self):
        """Initializes constants, which will be set after calibration."""
        self.ALPHA = np.nan
        self.BETA = np.nan
        self.GAMMA = np.nan
        self.THRESHOLD = 0.7
    
    # -----------------------------------------------------------
    # SIGNAL EXTRACTION (Factor Computation) - Simple Mean for Calibration
    # -----------------------------------------------------------

    def compute_rho_finance(self, rho_series: np.ndarray) -> float:
        """Accumulation: Mean Net Order Imbalance (NOI)."""
        # For calibration, we just need the average magnitude of imbalance
        return np.mean(rho_series)

    def compute_E_finance(self, E_series: np.ndarray) -> float:
        """Excitation: Mean Volatility (Normalized Daily Range)."""
        # The primary driver of instability in finance
        return np.mean(E_series)

    def compute_F_finance(self, F_series: np.ndarray) -> float:
        """Resilience: Mean Liquidity (Normalized Inverse Bid-Ask Spread)."""
        # The primary dampener; low F means high friction/low liquidity
        return np.mean(F_series)
    
    # -----------------------------------------------------------
    # MAIN CALIBRATION DRIVER
    # -----------------------------------------------------------

    def run_calibration(self) -> Tuple[float, float, float]:
        """
        Runs the full calibration sequence for the Finance Module.
        1. Generate synthetic data for two anchors.
        2. Compute factor means (E and F) for each anchor.
        3. Call the external Solver Engine.
        """
        np.random.seed(42) # Ensure reproducibility from the data generator test

        # --- 1. Generate and Extract Stable Anchor Data (T ≈ 0.0) ---
        stable_data = generate_finance_stable_period(n_points=100)
        E_stable = self.compute_E_finance(stable_data['E_series'])
        F_stable = self.compute_F_finance(stable_data['F_series'])
        T_stable = 0.0 # Human-defined anchor
        
        # --- 2. Generate and Extract Crisis Anchor Data (T ≈ 0.7) ---
        crisis_data = generate_finance_crisis_period(n_points=100)
        E_crisis = self.compute_E_finance(crisis_data['E_series'])
        F_crisis = self.compute_F_finance(crisis_data['F_series'])
        T_crisis = 0.7 # Human-defined anchor
        
        # --- 3. Call Calibration Engine (Solver) ---
        print("--- Calling DCII Calibration Engine (solver.py) ---")
        print(f"  Stable Anchor Inputs: E={E_stable:.4f}, F={F_stable:.4f}, T={T_stable:.1f}")
        print(f"  Crisis Anchor Inputs: E={E_crisis:.4f}, F={F_crisis:.4f}, T={T_crisis:.1f}")
        
        alpha, beta, gamma = solve_dcii_coefficients_two_anchor(
            E_stable, F_stable, T_stable,
            E_crisis, F_crisis, T_crisis
        )
        
        self.ALPHA = alpha
        self.BETA = beta
        self.GAMMA = gamma
        
        return alpha, beta, gamma

    def compute_T_finance(self, E: np.ndarray, F: np.ndarray) -> np.ndarray:
        """Computes Tension Index T using the derived coefficients."""
        if np.isnan(self.BETA) or np.isnan(self.GAMMA):
            raise ValueError("Coefficients must be calibrated before computing Tension (T).")
        
        # T = α|∇ρ| + βE - γF (Ignoring ρ term for 2-point solve)
        T = (self.BETA * E) - (self.GAMMA * F)
        return T

# -----------------------------------------------------------
# EXECUTION BLOCK
# -----------------------------------------------------------

if __name__ == "__main__":
    
    print("="*60)
    print("DCII FINANCE MODULE v1.0: COEFFICIENT CALIBRATION")
    print("="*60)
    
    analyzer = FinanceInstabilityAnalyzer()
    
    # Run the calibration process
    alpha, beta, gamma = analyzer.run_calibration()

    print("\n--- DCII v1.0 Finance Calibration Outcome ---")
    
    if not np.isnan(beta):
        print(f"EQUATION: T = {beta:.4f}E - {gamma:.4f}F")
        print(f"Alpha (Accumulation α): {alpha:.4f} (Negligible)")
        print(f"Beta (Excitation β):    {beta:.4f}")
        print(f"Gamma (Resilience γ):   {gamma:.4f}")
        
        # Post-Calibration Taxonomy Interpretation (P7 requirement)
        print("\nTAXONOMY INTERPRETATION (Dominance Ordering):")
        if beta > gamma:
            print("  ✅ Excitation-Driven Instability: Volatility (E) is the dominant causal factor.")
        else:
            print("  ⚠️ Resilience-Driven Stability: Damping (F) is dominant, indicating low systemic risk.")
            
        print("\nSTATUS: ✅ DCII v1.0 Finance Calibration Coefficients Derived.")
    else:
        print("STATUS: ❌ CALIBRATION FAILED: Singular Matrix (Check Factor Dependency).")

    print("="*60)
