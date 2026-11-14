import numpy as np
import pandas as pd

def find_shatter_boundary():
    # Sweep Energy Coupling (Beta) vs Governor Strength (b_sat)
    betas = np.linspace(0.5, 5.0, 100)
    governors = np.linspace(0.1, 1.5, 100)
    
    shatter_points = []

    for b in governors:
        for beta in betas:
            # We test the peak of the tension curve for this configuration
            # Tension = (beta * gs^2) / (1 + b * gs^3)
            # Analytically, peak occurs near gs ~ (2/(b))^(1/3)
            gs_peak = (2/b)**(1/3)
            max_tension = (beta * gs_peak**2) / (1 + b * gs_peak**3)
            
            status = "STABLE" if max_tension < 1.0 else "SHATTERED"
            shatter_points.append({
                "governor_strength": b,
                "energy_coupling": beta,
                "max_tension": max_tension,
                "status": status
            })

    df = pd.DataFrame(shatter_points)
    df.to_csv("stability_reports/shatter_boundary_map.csv", index=False)
    
    critical = df[df['status'] == "SHATTERED"].iloc[0] if "SHATTERED" in df.status.values else None
    
    print("⚛️ V12 SHATTER-POINT DIAGNOSTIC")
    print("-" * 40)
    if critical is not None:
        print(f"FIRST BREACH DETECTED:")
        print(f" > Governor Strength: {critical['governor_strength']:.4f}")
        print(f" > Energy Coupling:   {critical['energy_coupling']:.4f}")
        print(f" > Tension at Breach:  {critical['max_tension']:.4f}")
    else:
        print("RESULT: No Shatter-Point found in this parameter space.")

if __name__ == "__main__":
    find_shatter_boundary()
