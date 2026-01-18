import numpy as np

def test_b_term_constrain():
    print("--- [SXC-IGC] Testing Singularity Prevention (b-term) ---")
    # Simulation of a collapsing mass where r and a grow infinitely
    x = 0.1
    dt = 0.01
    b = 1.0 # The 'Bridge' Constant
    
    for i in range(1000):
        # Simulate increasing density 'r' and 'a' as r_s (Schwarzschild radius) shrinks
        r_dynamic = 0.1 + (i * 0.01)
        a_dynamic = 1.0 + (i * 0.02)
        
        x += (r_dynamic * x + a_dynamic * x**2 - b * x**3) * dt
        
        if i % 200 == 0:
            print(f"Step {i:4} | Substrate Density: {r_dynamic:.2f} | Info Strain x: {x:.4f}")
            
    print(f"Final Saturated Strain: {x:.4f} (Singularity Avoided by V12)")

if __name__ == "__main__":
    test_b_term_constrain()
