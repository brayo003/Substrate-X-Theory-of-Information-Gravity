import numpy as np

def run_fracture_scan():
    print("--- Substrate-X: Fracture Threshold Scan [Regime Transition] ---")
    
    # Calibrated Anchors from previous Real-Data run
    # base_excitation (E0) normalized to 1.0
    E0 = 1.0 
    beta = 0.102454   # COVID-19 coupling efficiency
    gamma = 0.08      # Estimated substrate damping/resistance
    k0 = 0.8586       # Current baseline curvature
    
    # Lambda (λ) is the scalar for Excitation Density
    # Scanning from current load (1.0) to 5.0x overload
    lambdas = np.linspace(1.0, 5.0, 41)
    
    print(f"{'Scalar (λ)':<12} | {'Tension (T)':<12} | {'Curvature (K)':<12} | {'Regime'}")
    print("-" * 65)
    
    fracture_found = False
    for lam in lambdas:
        # T = (λ * E0 * beta) - (gamma * E0)
        # K = k0 * (Normalized Tension / Normalized Excitation)
        # Note: In the brittle regime, K scales non-linearly with T
        T = (lam * E0 * beta) - gamma
        K = k0 * (T / (beta - gamma)) # Ratio of current stress to baseline capacity
        
        regime = "ELASTIC" if K < 1.0 else "FRACTURE"
        
        print(f"{lam:<12.2f} | {max(0, T):<12.4f} | {K:<12.4f} | {regime}")
        
        if K >= 1.0 and not fracture_found:
            print("\n[!] CRITICAL POINT REACHED: Systemic Elasticity Exhausted.")
            print(f"Critical Scalar λ* ≈ {lam:.2f}")
            fracture_found = True
            # We continue the scan to see the post-fracture gradient
            
    if not fracture_found:
        print("\n[STATUS] System is load-robust. No fracture detected within 5x scan.")

if __name__ == "__main__":
    run_fracture_scan()
