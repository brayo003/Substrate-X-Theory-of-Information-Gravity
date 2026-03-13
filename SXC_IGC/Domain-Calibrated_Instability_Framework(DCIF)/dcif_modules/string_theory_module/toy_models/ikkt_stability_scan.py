import numpy as np
import pandas as pd

def run_v12_stability_scan():
    # Generating a 'Moduli Scan' (Standard Theoretical Practice)
    # We simulate the scaling of coupling constant g_s
    gs_range = np.linspace(0.01, 2.5, 500)
    
    # V12 Parameters (Saturating the Theory)
    # b_sat represents the Hagedorn/UV Limit
    b_sat = 1.2 
    gamma = 0.8
    
    results = []
    for gs in gs_range:
        # T_sys represents the 'Theoretical Tension' of the construction
        # As coupling (gs) increases, tension builds
        tension = (gs**2) / (1 + b_sat * gs**3)
        
        # Classification based on your DCIF Regimes
        if tension < 0.3:
            regime = "WEAK_COUPLING"
        elif tension < 0.7:
            regime = "TRANSITION_ZONE"
        else:
            regime = "EFT_BREAKDOWN (SHATTER)"
            
        results.append({"gs": gs, "T_sys": tension, "regime": regime})

    df = pd.DataFrame(results)
    print("⚛️ V12 STRING STABILITY DIAGNOSTIC")
    print("-" * 40)
    print(df['regime'].value_counts())
    
    # Exporting the stability map
    df.to_csv("string_stability_map.csv", index=False)
    print("\n✅ Stability Map generated: string_stability_map.csv")

if __name__ == "__main__":
    run_v12_stability_scan()
