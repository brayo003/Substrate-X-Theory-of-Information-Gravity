import numpy as np
import os
import sys
from typing import Dict, Any, Tuple

# --- Dynamic Path Insertion for Core Infrastructure (Calibration Engine) ---
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
    from social_data_generator import generate_social_stable_period, generate_social_crisis_period
except ImportError:
    print("FATAL ERROR: Could not import social_data_generator.py.")
    sys.exit(1)

class SocialInstabilityAnalyzer:
    """
    Analyzer for computing Tension (T) in the SOCIAL MEDIA DOMAIN.
    Contains signal extraction logic for calibration.
    """
    
    def __init__(self):
        """Initializes constants, which will be set after calibration."""
        self.ALPHA = np.nan
        self.BETA = np.nan
        self.GAMMA = np.nan
        self.THRESHOLD = 0.9

    def compute_E_social(self, E_series: np.ndarray) -> float:
        """Excitation: Mean Posting Velocity / Amplification Rate."""
        return np.mean(E_series)

    def compute_F_social(self, F_series: np.ndarray) -> float:
        """Resilience: Mean Moderation / Algorithmic Decay / Fatigue."""
        return np.mean(F_series)
    
    def run_calibration(self) -> Tuple[float, float, float]:
        """
        Runs the full calibration sequence for the Social Media Module.
        """
        np.random.seed(88) # Use the fixed seed from the data generator test

        # --- 1. Generate and Extract Stable Anchor Data (T ≈ 0.0) ---
        stable_data = generate_social_stable_period(n_points=100)
        E_stable = self.compute_E_social(stable_data['E_series'])
        F_stable = self.compute_F_social(stable_data['F_series'])
        T_stable = 0.0 # Human-defined anchor
        
        # --- 2. Generate and Extract Crisis Anchor Data (T ≈ 0.9) ---
        crisis_data = generate_social_crisis_period(n_points=100)
        E_crisis = self.compute_E_social(crisis_data['E_series'])
        F_crisis = self.compute_F_social(crisis_data['F_series'])
        T_crisis = 0.9 # Human-defined anchor
        
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

# -----------------------------------------------------------
# EXECUTION BLOCK
# -----------------------------------------------------------

if __name__ == "__main__":
    
    print("="*60)
    print("DCII SOCIAL MEDIA MODULE v1.0: COEFFICIENT CALIBRATION")
    print("="*60)
    
    analyzer = SocialInstabilityAnalyzer()
    
    # Run the calibration process
    alpha, beta, gamma = analyzer.run_calibration()

    print("\n--- DCII v1.0 Social Media Calibration Outcome ---")
    
    if not np.isnan(beta):
        print(f"EQUATION: T = {beta:.4f}E - {gamma:.4f}F")
        print(f"Alpha (Accumulation α): {alpha:.4f} (Negligible)")
        print(f"Beta (Excitation β):    {beta:.4f}")
        print(f"Gamma (Resilience γ):   {gamma:.4f}")
        
        # Post-Calibration Taxonomy Interpretation
        print("\nTAXONOMY INTERPRETATION (Dominance Ordering):")
        # The social media factor E (0.2443) is much larger than F (0.0984) in crisis.
        # This domain is expected to be overwhelmingly excitation-driven.
        if beta / gamma > 5: # Use a higher ratio to signify "overwhelmingly dominant"
             print("  🔥 Highly Excitation-Driven: Posting Velocity (E) is the overwhelming causal factor.")
        elif beta > gamma:
            print("  ✅ Excitation-Driven Instability: Velocity (E) is the dominant causal factor.")
        else:
            print("  ⚠️ Resilience-Driven Stability: Damping (F) is dominant, indicating low systemic risk.")
            
        print("\nSTATUS: ✅ DCII v1.0 Social Media Calibration Coefficients Derived.")
    else:
        print("STATUS: ❌ CALIBRATION FAILED: Singular Matrix (Check Factor Dependency).")

    print("="*60)
