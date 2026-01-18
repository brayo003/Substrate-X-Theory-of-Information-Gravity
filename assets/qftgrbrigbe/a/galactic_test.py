# Save as: galactic_test.py
import numpy as np
from new_v12 import MasterBridgeV12

def galactic_v12_check():
    # Milky Way parameters
    gal_mass = 1.5e42 # kg
    edge_dist = 4.7e20 # ~50k light years
    
    bridge = MasterBridgeV12(gal_mass)
    g_v12 = bridge.calculate_gravity_acceleration(edge_dist)
    
    # If x has a minimum floor (x_min), g plateaus instead of vanishing
    print(f"=== GALACTIC EDGE TEST ===")
    print(f"Distance: {edge_dist:.2e} m")
    print(f"V12 Predicted Acceleration: {g_v12:.2e} m/s^2")

if __name__ == "__main__":
    galactic_v12_check()
