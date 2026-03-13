import numpy as np
import pandas as pd
import sys

def classify_theory(beta, b):
    # Theoretical Peak Tension Logic
    gs_peak = (2/b)**(1/3)
    max_tension = (beta * gs_peak**2) / (1 + b * gs_peak**3)
    
    # Distance to Shatter: Ds = 1.0 - max_tension
    # Positive Ds = Stable; Negative Ds = Shattered
    ds = 1.0 - max_tension
    
    print(f"\n⚛️ V12 CLASSIFICATION REPORT")
    print("-" * 35)
    print(f"Input Beta (Coupling):  {beta:.4f}")
    print(f"Input b (Governor):     {b:.4f}")
    print(f"Peak Tension (T_sys):   {max_tension:.4f}")
    print(f"Distance to Shatter:    {ds:.4f}")
    print("-" * 35)

    if ds > 0.2:
        print("VERDICT: LANDSCAPE (Deeply Stable)")
    elif 0 <= ds <= 0.2:
        print("VERDICT: MARGINAL (Edge of Swampland)")
    else:
        print("VERDICT: SWAMPLAND (Physical Breach)")
    print("-" * 35)

if __name__ == "__main__":
    if len(sys.argv) == 3:
        classify_theory(float(sys.argv[1]), float(sys.argv[2]))
    else:
        # Default test case: A theory known to be on the edge
        classify_theory(0.8, 0.5)
