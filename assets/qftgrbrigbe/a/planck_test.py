# Save as: planck_test.py
import numpy as np
from new_v12 import MasterBridgeV12

# Physical Constants
G = 6.67430e-11
C = 299792458.0
HBAR = 1.054571817e-34
LP = np.sqrt(HBAR * G / C**3)
MP = np.sqrt(HBAR * C / G)

def planck_scale_test():
    print(f"=== V12 QUANTUM GRAVITY TEST: THE PLANCK SCALE ===")
    
    # Create a Planck Particle (Mass = Mp, Radius = Lp)
    bridge = MasterBridgeV12(MP)
    
    # Test distances approaching the center
    distances = [LP * 10, LP * 2, LP, LP * 0.5]
    
    print(f"{'Distance':<15} | {'Tension (x)':<15} | {'Status'}")
    print("-" * 50)
    
    for d in distances:
        x = bridge.get_equilibrium_tension(d)
        status = "SATURATED" if x >= 0.99 else "STABLE"
        print(f"{d/LP:5.1f} Lp | {x:15.6f} | {status}")

if __name__ == "__main__":
    planck_scale_test()

