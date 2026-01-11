import numpy as np
import os
import sys

PROJECT_ROOT = os.path.expanduser("~/Projects/Substrate_X_Theory_of_Information_Gravity")
sys.path.append(PROJECT_ROOT)

from SXC_V12_CORE import SXCOmegaEngine

def run_ngc2403_test():
    engine = SXCOmegaEngine()
    data_path = "data/sparc/NGC2403_rotmod.txt"
    
    # Fine-tuned Coupling to eliminate the -6.8 Delta
    G_inf = 62.0 
    
    print(f"\n{'Radius':<8} | {'V_obs':<8} | {'V_SXC':<8} | {'Tension':<8} | {'Delta':<8}")
    print("-" * 65)

    with open(data_path, 'r') as f:
        for line in f:
            parts = [float(x) for x in line.split()]
            rad, v_obs, err, v_gas, v_disk, v_bulge = parts
            v_bar = np.sqrt(v_gas**2 + v_disk**2 + v_bulge**2)
            
            accel_signal = (v_bar**2 / max(rad, 0.1))
            tension, _ = engine.step(accel_signal)
            
            # Applying the fine-tuned Information Gravity Constant
            v_sxc = np.sqrt(v_bar**2 + (tension * G_inf))
            delta = v_obs - v_sxc
            
            print(f"{rad:<8.2f} | {v_obs:<8.1f} | {v_sxc:<8.1f} | {tension:<8.4f} | {delta:<8.1f}")

if __name__ == "__main__":
    run_ngc2403_test()
