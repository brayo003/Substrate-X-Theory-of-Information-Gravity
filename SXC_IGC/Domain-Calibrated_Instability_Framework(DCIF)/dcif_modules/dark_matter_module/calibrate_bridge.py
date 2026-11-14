import numpy as np

# FUNDAMENTAL CONSTANTS
G = 6.67430e-11
C = 299792458.0
RH = 1.37e26 
KPC_TO_M = 3.086e19

def final_validation():
    # Load SPARC NGC 5055
    data = np.loadtxt('sparc_data/NGC5055_rotmod.dat', skiprows=3)
    r_kpc, v_obs, v_gas, v_disk = data[:, 0], data[:, 1], data[:, 3], data[:, 4]
    
    # 1. FIXED Mass-to-Light (Industry standard)
    ups = 0.5 
    v_n_kms = np.sqrt(v_gas**2 + (ups * v_disk**2))
    r_m = r_kpc * KPC_TO_M
    g_n = (v_n_kms * 1000)**2 / r_m
    
    # 2. SPHERICAL BRIDGE COUPLING (1/4pi)
    # This aligns with the 0.08 ratio found in your Milky Way diagnostic
    a0 = (C**2) / (4 * np.pi * RH) 
    
    # 3. Geometric Mean Transition
    g_total = np.sqrt(g_n * (g_n + a0))
    v_final = np.sqrt(g_total * r_m) / 1000
    
    print(f"--- NGC 5055 FINAL SPHERICAL BRIDGE ---")
    print(f"{'Radius (kpc)':<15} | {'Observed':<10} | {'Bridge V':<10} | {'Error'}")
    print("-" * 60)
    for i in [0, len(r_kpc)//2, -1]:
        err = abs(v_obs[i] - v_final[i])
        print(f"{r_kpc[i]:<15.2f} | {v_obs[i]:<10.2f} | {v_final[i]:<10.2f} | {err:.2f} km/s")

if __name__ == "__main__":
    final_validation()
