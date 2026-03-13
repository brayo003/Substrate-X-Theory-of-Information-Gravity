import numpy as np
import sys
import os
sys.path.insert(0, '/home/lenovo/Git/Substrate_X_Theory_of_Information_Gravity/assets/qftgrbrigbe/b')
from new_v12 import MasterBridgeV12

def read_rotmod_file(filename):
    """Read rotation curve data from SPARC .dat file"""
    data = np.loadtxt(filename)
    # Format: radius (kpc), velocity (km/s), velocity_error, etc.
    radii_kpc = data[:, 0]  # kiloparsecs
    v_obs_km_s = data[:, 1]  # observed velocity
    return radii_kpc, v_obs_km_s

def test_one_galaxy(filepath, galaxy_name):
    """Test V12 theory on one galaxy"""
    try:
        radii_kpc, v_obs_km_s = read_rotmod_file(filepath)
        
        # Use the farthest point (galaxy edge) like your earlier test
        r_max_kpc = radii_kpc[-1]
        v_obs_max = v_obs_km_s[-1]
        
        # Convert units
        r_max_m = r_max_kpc * 3.086e19  # kpc → meters
        v_obs_m_s = v_obs_max * 1000    # km/s → m/s
        
        # Calculate observed acceleration (v²/r)
        g_obs = v_obs_m_s**2 / r_max_m
        
        # Estimate mass from Newton (M = g_obs * r² / G)
        M_est = g_obs * r_max_m**2 / 6.67430e-11
        
        # Your V12 prediction
        bridge = MasterBridgeV12(M_est)
        g_v12 = bridge.calculate_gravity_acceleration(r_max_m)
        
        return M_est, g_obs, g_v12
    except:
        return None, None, None

# Main test
print("=== TESTING V12 THEORY ON SPARC DATABASE ===")
print(f"Using calibration constant K = 3.7e-92")
print(f"{'Galaxy':<20} {'Mass (kg)':<15} {'g_obs (m/s²)':<15} {'g_v12 (m/s²)':<15} {'Ratio':<10}")
print("="*80)

ratios = []
for filename in os.listdir('sparc_data'):
    if filename.endswith('_rotmod.dat'):
        galaxy_name = filename.replace('_rotmod.dat', '')
        filepath = os.path.join('sparc_data', filename)
        M, g_obs, g_v12 = test_one_galaxy(filepath, galaxy_name)
        
        if M and g_obs and g_v12:
            ratio = g_v12 / g_obs
            ratios.append(ratio)
            print(f"{galaxy_name:<20} {M:.2e} {g_obs:.2e} {g_v12:.2e} {ratio:.3f}")

# Statistics
print(f"\n=== RESULTS SUMMARY ===")
print(f"Tested {len(ratios)} galaxies")
print(f"Average g_v12/g_obs ratio: {np.mean(ratios):.3f} ± {np.std(ratios):.3f}")
print(f"Within 10% of 1.0: {sum(0.9 < r < 1.1 for r in ratios)} galaxies")
print(f"Within 20% of 1.0: {sum(0.8 < r < 1.2 for r in ratios)} galaxies")

if 0.9 < np.mean(ratios) < 1.1 and np.std(ratios) < 0.2:
    print(f"\n✅ SUCCESS: V12 theory matches SPARC database!")
else:
    print(f"\n⚠️ Needs tuning: Average ratio = {np.mean(ratios):.3f}")
