import numpy as np
import json
import os

def calculate_curvature(filename):
    if not os.path.exists(filename):
        return None
    
    with open(filename, 'r') as f:
        data = json.load(f)['items']
    
    views = np.array([item['views'] for item in data])
    # Flux (F) = Daily Change
    flux = np.diff(views, prepend=views[0])
    
    # Find the Peak (The Singularity Point)
    peak_idx = np.argmax(views)
    e_peak = views[peak_idx]
    f_peak = abs(flux[peak_idx])
    
    # K = Curvature Constant (Logarithmic scaling)
    # At K = 1.0, the system is at the Event Horizon.
    k = np.log10(e_peak) / np.log10(f_peak) if f_peak > 1 else 0
    return e_peak, f_peak, k

# Paths
kirk_file = "kirk_singularity.json"
mamdani_file = "mamdani_singularity.json"

print(f"--- SUBSTRATE-X SINGULARITY ANALYSIS ---")

k_res = calculate_curvature(kirk_file)
if k_res:
    print(f"KIRK (Assassination):")
    print(f"  Peak Mass (E): {k_res[0]:,}")
    print(f"  Peak Flux (F): {k_res[1]:,}")
    print(f"  Curvature (K): {k_res[2]:.8f}")

m_res = calculate_curvature(mamdani_file)
if m_res:
    print(f"\nMAMDANI (Election):")
    print(f"  Peak Mass (E): {m_res[0]:,}")
    print(f"  Peak Flux (F): {m_res[1]:,}")
    print(f"  Curvature (K): {m_res[2]:.8f}")

if k_res and m_res:
    ratio = k_res[2] / m_res[2]
    print(f"\nGRAVITATIONAL CONSISTENCY RATIO: {ratio:.6f}")
