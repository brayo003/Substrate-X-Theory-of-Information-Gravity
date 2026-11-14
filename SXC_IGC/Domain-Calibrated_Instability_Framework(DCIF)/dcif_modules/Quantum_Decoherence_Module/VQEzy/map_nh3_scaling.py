import h5py
import numpy as np
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
H5_PATH = os.path.join(BASE_DIR, 'qchem/nh3_16_qubit.h5')

if not os.path.exists(H5_PATH):
    print(f"Error: {H5_PATH} not found.")
else:
    with h5py.File(H5_PATH, 'r') as f:
        group = f['opt_params']
        keys = list(group.keys())
        
        # Taking a smaller sample (50) for the 16-qubit tensor to manage memory
        all_params = [group[k][()] for k in keys[:50]]
        param_matrix = np.array(all_params)
        drag_tensor = np.var(param_matrix, axis=0)
        
        global_mean = np.mean(drag_tensor)
        
        print("=== DCIF SCALING AUDIT: 16-QUBIT NH3 ===")
        print(f"Global Mean Variance (Gravity): {global_mean:.4f}")
        
        # Check Layer-wise accumulation
        layer_means = np.mean(drag_tensor, axis=(1, 2))
        print("\nLayer-wise Gravity Accumulation:")
        for i, m in enumerate(layer_means):
            print(f"  Layer {i}: {m:.4f}")

        if global_mean > 5.0:
            print("\n[!] STATUS: INFORMATION BLACKOUT")
            print("    The substrate has fully de-cohered the 16-qubit cluster.")
