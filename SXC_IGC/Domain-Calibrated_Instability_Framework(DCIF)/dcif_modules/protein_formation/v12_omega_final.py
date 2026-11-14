import numpy as np
import os

def run_v12_omega_audit(filename):
    if not os.path.exists(filename): return
    coords = []
    with open(filename, "r") as f:
        for line in f:
            if line.startswith("ATOM") and " CA " in line:
                coords.append([float(line[30:38]), float(line[38:46]), float(line[46:54])])
    
    coords = np.array(coords)
    T_sys, history, decay = 0.0, [], 0.1

    for i in range(len(coords)):
        distances = np.linalg.norm(coords - coords[i], axis=1)
        local_mass = np.sum([1.0/d for d in distances if 2.0 < d < 10.0])
        T_sys = (T_sys + local_mass) * (1 - decay)
        history.append(T_sys)

    peak_t, avg_t = max(history), np.mean(history)
    idx = peak_t / avg_t

    print(f"\n--- V12 OMEGA AUDIT: {filename} ---")
    print(f"Peak T: {peak_t:.2f} | Index: {idx:.4f}")

    # PHASE LOGIC
    if peak_t > 100.0:
        print("STATUS: [SUBSTRATE COLLAPSE] - Absolute Gravity Saturation (Crystalline Trap/Implosion)")
    elif idx > 1.35:
        print("STATUS: [DYNAMIC FRACTURE] - Localized Instability (Metastable/Explosion)")
    elif idx < 1.25 and peak_t < 30.0:
        print("STATUS: [OPTIMAL SUBSTRATE] - Balanced Resilience (F)")
    else:
        print("STATUS: [TRANSITION] - Nominal tension levels.")

targets = ["ubiquitin.pdb", "prion.pdb", "amyloid.pdb"]
for t in targets: run_v12_omega_audit(t)
