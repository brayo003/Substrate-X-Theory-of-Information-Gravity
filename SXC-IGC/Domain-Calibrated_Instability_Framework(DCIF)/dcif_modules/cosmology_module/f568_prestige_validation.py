import numpy as np
from SXC_V12_CORE import SXCV12Universal

radii = [1.8, 3.7, 5.5, 7.3, 9.2, 12.8, 16.5, 20.2, 23.8, 27.5]
v_obs = [35.0, 58.0, 75.0, 88.0, 95.0, 103.0, 107.0, 109.0, 110.0, 110.0]
v_bar = [7.5, 14.2, 21.0, 27.8, 32.5, 38.4, 42.1, 44.2, 45.1, 45.5]

engine = SXCV12Universal()
print(f"{'Radius':<8} | {'V_bar':<8} | {'V_SXC':<8} | {'V_obs':<8} | {'Error'}")
print("-" * 50)

chi2 = 0
for i in range(len(radii)):
    signal = v_bar[i]
    tension = engine.compute_tension(signal, radii[i])
    v_sxc = engine.get_velocity(v_bar[i], tension)
    
    error = v_sxc - v_obs[i]
    chi2 += (error**2) / v_obs[i]
    print(f"{radii[i]:<8.1f} | {v_bar[i]:<8.1f} | {v_sxc:<8.1f} | {v_obs[i]:<8.1f} | {error:<8.1f}")

print("-" * 50)
print(f"FINAL F568-3 SXC χ²: {chi2:.2f}")
