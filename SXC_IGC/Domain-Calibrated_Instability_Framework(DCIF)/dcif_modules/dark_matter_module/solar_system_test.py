import numpy as np
import sys
sys.path.insert(0, '/home/lenovo/Git/Substrate_X_Theory_of_Information_Gravity/assets/qftgrbrigbe/b')
from new_v12 import MasterBridgeV12

# Earth around Sun
sun_mass = 1.989e30
earth_dist = 1.496e11  # 1 AU

bridge = MasterBridgeV12(sun_mass)
g_v12 = bridge.calculate_gravity_acceleration(earth_dist)
g_newton = (6.67430e-11 * sun_mass) / (earth_dist**2)

print(f"=== SOLAR SYSTEM TEST ===")
print(f"Sun mass: {sun_mass:.2e} kg")
print(f"Earth distance: {earth_dist:.2e} m (1 AU)")
print(f"Newtonian gravity: {g_newton:.6f} m/s²")
print(f"Your V12 gravity: {g_v12:.6f} m/s²")
print(f"Ratio (V12/Newton): {g_v12/g_newton:.6f}")
print(f"\nExpected: Very close to 1.0 (Newton works perfectly in solar system)")
