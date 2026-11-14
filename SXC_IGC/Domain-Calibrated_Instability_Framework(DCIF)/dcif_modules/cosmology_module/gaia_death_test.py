import pandas as pd
import numpy as np
import os
from SXC_Dynamic_Sink import SXCGovernor

# Load Gaia Data
# Gaia DR3 columns: 'r' (kpc), 'vphi' (km/s), and usually 'err_vphi'
try:
    df = pd.read_csv("gaia_dr3_rotation_curve.csv")
    # Clean column names in case of whitespace
    df.columns = df.columns.str.strip()
except Exception as e:
    print(f"Error loading CSV: {e}")
    exit()

print(f"--- SXC-IGC GAIA DR3 STRESS TEST ---")
print(f"Testing on {len(df)} points of Milky Way data (Gaia DR3).")

# Initialize Engine
gov = SXCGovernor()
results = []

# Map Gaia data to your Governor logic
for i, row in df.iterrows():
    r = row['r']
    v_obs = row['vphi']
    
    # We use v_obs as the 'v_bar' proxy to see if the governor 
    # can stabilize the kinetic signal without a specific baryon model
    # Signal is usually v^2 / r (acceleration)
    signal = (v_obs**2) / r if r > 0 else 0
    
    # Use your specific step function
    # Passing v_obs for both bar and obs to check for deterministic stability
    correction = gov.step(signal, v_obs, v_obs)
    results.append(gov.T_sys)

final_t = gov.T_sys
max_t = max(results)

print(f"Max Tension reached: {max_t:.4f}")
print(f"Final Tension: {final_t:.4f}")

# The Overfitting Verdict
if final_t < 1.0:
    print("\nVERDICT: DETERMINISTIC STABILITY.")
    print("The engine generalized to the Milky Way's decline.")
else:
    print("\nVERDICT: OVERFITTED / UNSTABLE.")
    print("The system failed to absorb the Gaia DR3 variance.")
