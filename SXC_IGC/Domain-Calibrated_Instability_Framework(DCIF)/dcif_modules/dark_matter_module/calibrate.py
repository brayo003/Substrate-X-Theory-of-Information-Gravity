import numpy as np
from new_v12 import MasterBridgeV12

target_ratio = 8.5  # Want V12 to be 8.5x Newton at galactic edge
gal_mass = 1.5e42
edge_dist = 4.7e20

# Test different K values
for K in [1e-80, 1e-85, 1e-90, 1e-95, 1e-100]:
    bridge = MasterBridgeV12(gal_mass)
    bridge.K = K  # Override K
    g_v12 = bridge.calculate_gravity_acceleration(edge_dist)
    g_newton = (6.67430e-11 * gal_mass) / (edge_dist**2)
    ratio = (g_v12 - g_newton) / g_newton  # Extra gravity from V12
    print(f"K={K:.1e}: V12 adds {ratio:.1f}x Newton | Total = {g_v12/g_newton:.1f}x")
