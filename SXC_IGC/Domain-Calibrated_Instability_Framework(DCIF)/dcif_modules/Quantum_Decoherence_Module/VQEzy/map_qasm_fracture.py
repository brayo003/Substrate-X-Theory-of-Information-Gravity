import h5py
import numpy as np
import os

# We are targeting a 'Dense' computational kernel from QASMBench
# These typically lack the 'balancing' symmetries of molecular models
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
H5_PATH = os.path.join(BASE_DIR, 'qasmbench/dense_kernel_5_qubit.h5')

if not os.path.exists(H5_PATH):
    print(f"Error: {H5_PATH} not found.")
else:
    with h5py.File(H5_PATH, 'r') as f:
        group = f['opt_params']
        keys = list(group.keys())
        all_params = [group[k][()] for k in keys[:100]]
        drag_tensor = np.var(np.array(all_params), axis=0)

        print("=== DCIF ANATOMY: QASMBENCH DENSE KERNEL ===")
        print(f"Global Mean Variance: {np.mean(drag_tensor):.4f}")
        
        # Checking for "Jitter" - high variance in specific gates rather than layers
        max_jitter = np.max(drag_tensor)
        print(f"Peak Single-Gate Gravity (Jitter): {max_jitter:.4f}")

        if max_jitter > 3.0:
            print("\n[!] DETECTED: SUBSTRATE REJECTION")
            print("    The hardware is physically incapable of holding this logic.")
