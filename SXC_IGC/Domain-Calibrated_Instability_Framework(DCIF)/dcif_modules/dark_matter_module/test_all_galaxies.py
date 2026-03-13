import numpy as np
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from new_v12 import MasterBridgeV12

def read_rotmod_file(filename):
    data = np.loadtxt(filename)
    radii_kpc = data[:, 0]
    v_obs_km_s = data[:, 1]
    return radii_kpc, v_obs_km_s

def test_one_galaxy(filepath, galaxy_name):
    try:
        radii_kpc, v_obs_km_s = read_rotmod_file(filepath)
        r_max_kpc = radii_kpc[-1]
        v_obs_max = v_obs_km_s[-1]
        
        r_max_m = r_max_kpc * 3.086e19
        v_obs_m_s = v_obs_max * 1000
        g_obs = v_obs_m_s**2 / r_max_m
        
        M_est = g_obs * r_max_m**2 / 6.67430e-11
        
        bridge = MasterBridgeV12(M_est)
        g_v12 = bridge.calculate_gravity_acceleration(r_max_m)
        
        return M_est, g_obs, g_v12, bridge.b, bridge.K
    except:
        return None, None, None, None, None

print("=== V12 THEORY TEST ===")
print("Using b ∝ 1/M^1.5, K calibrated for Milky Way")

ratios = []
count = 0
for filename in os.listdir('sparc_data'):
    if filename.endswith('_rotmod.dat'):
        galaxy_name = filename.replace('_rotmod.dat', '')
        filepath = os.path.join('sparc_data', filename)
        M, g_obs, g_v12, b, K = test_one_galaxy(filepath, galaxy_name)
        
        if M and g_obs and g_v12:
            ratio = g_v12 / g_obs
            ratios.append(ratio)
            count += 1
            
            if count % 10 == 0:
                print(f"{galaxy_name:<20} {M:.2e} {g_obs:.2e} {g_v12:.2e} {ratio:.3f}")
            
            if count >= 50:
                break

if ratios:
    print(f"\n=== RESULTS (first {len(ratios)} galaxies) ===")
    print(f"Average ratio: {np.mean(ratios):.3f} ± {np.std(ratios):.3f}")
    print(f"Within 10% of 1.0: {sum(0.9 < r < 1.1 for r in ratios)} galaxies")
    print(f"Within 20% of 1.0: {sum(0.8 < r < 1.2 for r in ratios)} galaxies")
    
    mean_ratio = np.mean(ratios)
    if 0.8 < mean_ratio < 1.2:
        print(f"\n✅ Theory fits observations")
    else:
        print(f"\n⚠️ Theory predicts average {mean_ratio:.2f}x observed gravity")
else:
    print("No galaxies processed.")
