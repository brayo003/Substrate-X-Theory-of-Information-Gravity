import numpy as np

v_obs = [45.2, 68.4, 85.1, 92.5, 98.7, 103.2, 107.5, 110.8, 114.1, 117.2, 125.4, 128.9, 131.2, 133.5, 134.1, 134.5]
v_bar = [12.4, 25.6, 38.5, 48.5, 55.9, 61.9, 66.7, 70.7, 73.8, 76.6, 83.2, 87.8, 94.8, 102.7, 109.5, 113.8]
radii = [0.30, 0.61, 0.91, 1.22, 1.52, 1.83, 2.13, 2.44, 2.74, 3.05, 4.00, 5.00, 7.00, 10.00, 15.00, 20.00]

# Calibrated Saturation Constants from our chi2 success
V_LIMIT = 83.17
K_SAT = 0.1494

print(f"{'Radius':>6} | {'V_bar':>6} | {'V_SXC':>6} | {'V_obs':>6} | {'Delta':>6}")
print("-" * 45)

# Use the Tension values your V12 engine actually produces
tensions = [4.179, 12.90, 25.71, 40.04, 54.27, 67.56, 79.65, 90.30, 99.53, 107.35, 112.82, 116.17, 116.98, 115.70, 112.31, 107.89]

for i in range(len(radii)):
    # SATURATION LOGIC: Substrate cannot provide infinite energy
    v_sub = V_LIMIT * (1 - np.exp(-K_SAT * tensions[i]))
    v_sxc = np.sqrt(v_bar[i]**2 + v_sub**2)
    delta = v_obs[i] - v_sxc
    
    print(f"{radii[i]:6.2f} | {v_bar[i]:6.1f} | {v_sxc:6.1f} | {v_obs[i]:6.1f} | {delta:6.1f}")
