import numpy as np
import sys
sys.path.insert(0, '/home/lenovo/Git/Substrate_X_Theory_of_Information_Gravity/assets/qftgrbrigbe/b')
from new_v12 import MasterBridgeV12

def galactic_v12_check():
    # Milky Way parameters
    G = 6.67430e-11
    gal_mass = 1.5e42  # kg (visible mass)
    edge_dist = 4.7e20  # meters (~50k light years)
    
    # 1. YOUR THEORY'S PREDICTION
    bridge = MasterBridgeV12(gal_mass)
    g_v12 = bridge.calculate_gravity_acceleration(edge_dist)
    
    # 2. NEWTONIAN PREDICTION (Visible Mass Only)
    g_newton = G * gal_mass / (edge_dist**2)
    
    # 3. TYPICAL OBSERVED VALUE (For Milky Way at 50k ly)
    g_observed_typical = 8.5 * g_newton  # Observed is ~8.5x Newton
    
    # 4. CALCULATE RATIOS
    v12_to_newton = g_v12 / g_newton
    v12_to_observed = g_v12 / g_observed_typical
    
    print(f"=== GALACTIC ROTATION CURVE TEST ===")
    print(f"Distance from center: {edge_dist:.2e} m (~50,000 light-years)")
    print(f"Visible mass used: {gal_mass:.2e} kg")
    print(f"")
    print(f"[1] Newtonian prediction: {g_newton:.2e} m/s²")
    print(f"[2] Your V12 prediction: {g_v12:.2e} m/s²")
    print(f"[3] Typical observed value: {g_observed_typical:.2e} m/s²")
    print(f"")
    print(f"CRITICAL RATIOS:")
    print(f"V12 / Newton = {v12_to_newton:.2e}x")
    print(f"V12 / Observed = {v12_to_observed:.2e}x")
    
    if 0.1 < v12_to_observed < 10:
        print(f"\n✅ Theory is in the ballpark! Needs calibration.")
    elif v12_to_observed < 0.1:
        print(f"\n⚠️ Theory underpredicts by factor {1/v12_to_observed:.1e}")
    else:
        print(f"\n⚠️ Theory overpredicts by factor {v12_to_observed:.1e}")

if __name__ == "__main__":
    galactic_v12_check()
