import numpy as np
import os

def run_v12_audit(filename):
    if not os.path.exists(filename):
        print(f"File {filename} not found. Skipping...")
        return

    coords = []
    with open(filename, "r") as f:
        for line in f:
            # We only want the Alpha Carbon (CA) to map the 'Substrate Backbone'
            if line.startswith("ATOM") and " CA " in line:
                try:
                    coords.append([float(line[30:38]), float(line[38:46]), float(line[46:54])])
                except:
                    continue

    coords = np.array(coords)
    num_residues = len(coords)
    
    # V12 Omega Engine Core
    T_sys = 0.0
    decay = 0.1
    history = []

    for i in range(num_residues):
        # Calculate Information Gravity (m) based on local packing
        distances = np.linalg.norm(coords - coords[i], axis=1)
        # We look at interactions within a 10-angstrom radius
        local_mass = np.sum([1.0/d for d in distances if 2.0 < d < 10.0])
        
        # T_sys = (T_sys + mass) * resilience_factor
        T_sys = (T_sys + local_mass) * (1 - decay)
        history.append(T_sys)

    peak_t = max(history)
    avg_t = np.mean(history)
    instability_index = peak_t / avg_t

    print(f"\n--- AUDIT: {filename} ---")
    print(f"Substrate Grains (Residues): {num_residues}")
    print(f"Peak Tension: {peak_t:.2f} | Avg Tension: {avg_t:.2f}")
    print(f"Instability Index (Peak/Avg): {instability_index:.4f}")

    if instability_index < 1.3:
        print("STATUS: HYPER-STABLE [Optimization Mode]")
    elif instability_index < 1.5:
        print("STATUS: NOMINAL [Transition Zone]")
    elif instability_index < 1.9:
        print("STATUS: METASTABLE [Pre-Critical Warning]")
    else:
        print("STATUS: SYSTEMIC FRACTURE [Substrate Collapse]")

# Execute the three-stage comparison
targets = ["ubiquitin.pdb", "prion.pdb", "amyloid.pdb"]
for target in targets:
    run_v12_audit(target)
