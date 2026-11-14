import numpy as np
import glob
import os
import sys
from SXC_Dynamic_Sink import SXCGovernor

# 1. Access the local SPARC data
files = glob.glob("data/sparc/*.dat")
if not files:
    print("Error: No data in data/sparc/")
    sys.exit(1)

# 2. Pick a known 'difficult' galaxy or just the first one for a raw test
# We'll use the one with the most data points to ensure maximum tension accumulation
files.sort(key=lambda x: os.path.getsize(x), reverse=True)
target_galaxy = files[0]

print(f"--- SXC-IGC INTERNAL STRESS TEST ---")
print(f"Target Substrate: {os.path.basename(target_galaxy)}")

try:
    data = np.genfromtxt(target_galaxy)
    r, v_obs = data[:, 0], data[:, 1]
    v_bar = np.sqrt(np.nan_to_num(data[:, 3:6]**2).sum(axis=1))
    
    gov = SXCGovernor()
    tensions = []
    
    for i in range(len(r)):
        if r[i] <= 0: continue
        # Calculation: Acceleration signal
        sig = v_bar[i]**2 / r[i]
        # Run step with zero calibration
        gov.step(sig, v_obs[i], v_bar[i])
        tensions.append(gov.T_sys)
    
    print(f"Points Processed: {len(tensions)}")
    print(f"Max Tension:      {max(tensions):.4f}")
    print(f"Final Tension:    {gov.T_sys:.4f}")
    
    if gov.T_sys < 2.0:
        print("\nRESULT: CERTAINTY. The 1.254 scaling is self-stabilizing.")
    else:
        print("\nRESULT: BS. The engine accumulates too much tension.")

except Exception as e:
    print(f"Execution Error: {e}")
