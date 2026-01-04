import numpy as np

# FUNDAMENTAL CONSTANTS
G = 6.67430e-11
C = 299792458.0
RH = 1.37e26 # Hubble Radius

class V12RegimeEngine:
    def __init__(self, mass):
        self.M = mass
        self.Rs = (2 * G * mass) / (C**2)

    def get_bridge_activity(self, r):
        # 1. UV Signal (Near Horizon)
        uv_signal = self.Rs / r
        
        # 2. IR Signal (Near Hubble Boundary)
        # This is the 'Substrate Noise' that explains Dark Matter
        ir_signal = r / RH
        
        # 3. The V12 Total Activity (x)
        x_total = uv_signal + ir_signal
        
        # Determine if we are in a 'Newtonian Dead Zone'
        is_newtonian = uv_signal < 1e-4 and ir_signal < 1e-4
        return x_total, is_newtonian

# TEST THE REGIMES
sun = V12RegimeEngine(1.989e30)
for r in [3000, 1.496e11, 1e21, 1e26]:
    x, dead_zone = sun.get_bridge_activity(r)
    status = "BRIDGE ACTIVE" if not dead_zone else "NEWTONIAN SILENCE"
    print(f"Radius: {r:.1e}m | x_total: {x:.2e} | Status: {status}")
