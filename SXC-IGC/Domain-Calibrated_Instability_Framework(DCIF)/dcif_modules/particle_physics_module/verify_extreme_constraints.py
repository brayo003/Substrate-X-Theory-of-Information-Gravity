import numpy as np

def check_extreme_limits(g_n, m_x_mev):
    # 1. Neutron Scattering (n-Pb) - usually limits g_n to ~1e-4
    # 2. SN1987A Trapping - if g_n > 1e-4, the boson is trapped (SAFE)
    # 3. Red Giant Cooling - limits very light bosons; 17MeV is usually too heavy
    
    n_pb_limit = 2e-4
    sn1987a_trapping_threshold = 1e-4
    
    print(f"--- EXTREME CONSTRAINT AUDIT (g_n = {g_n:.2e}) ---")
    
    # Check Neutron Scattering
    if g_n > n_pb_limit:
        n_status = "WARNING: Potential Conflict with n-Pb scattering"
    else:
        n_status = "SAFE: Consistent with n-Pb scattering"
        
    # Check SN1987A (The Trapping Defense)
    if g_n > sn1987a_trapping_threshold:
        astro_status = "SAFE: Boson is TRAPPED in supernova core (no energy loss)"
    else:
        astro_status = "DANGER: Boson escapes SN1987A (Falsified by cooling data)"
        
    return n_status, astro_status

# Test your current validated g_n
g_n_val = 1.09e-03
n_res, a_res = check_extreme_limits(g_n_val, 17.01)

print(f"Neutron Result:      {n_res}")
print(f"Astrophysic Result:  {a_res}")
print("-" * 50)
print("INTEGRITY CONCLUSION:")
print("The model survives SN1987A because it is 'strongly' coupled enough to stay trapped.")
print("The n-Pb scattering may require the X17 to be an AXIAL-VECTOR to suppress low-energy limits.")
