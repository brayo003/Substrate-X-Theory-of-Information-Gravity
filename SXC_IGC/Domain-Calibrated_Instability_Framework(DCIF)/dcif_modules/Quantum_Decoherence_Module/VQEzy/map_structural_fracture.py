import h5py
import numpy as np
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
H5_PATH = os.path.join(BASE_DIR, 'qchem/h2_4_qubit.h5')

with h5py.File(H5_PATH, 'r') as f:
    group = f['opt_params']
    keys = list(group.keys())
    all_params = [group[k][()] for k in keys[:200]]
    drag_tensor = np.var(np.array(all_params), axis=0)

    print("=== DCIF ANATOMY: PARAMETER INSTABILITY HEATMAP ===")
    for layer in range(drag_tensor.shape[0]):
        print(f"\nLayer {layer} (Instability per Qubit/Param):")
        # Visualizing the (2, 4) slice for each layer
        for qubit in range(drag_tensor.shape[1]):
            row = drag_tensor[layer, qubit]
            formatted_row = " ".join([f"{v:7.4f}" for v in row])
            print(f"  Qubit {qubit}: [{formatted_row}]")

    max_idx = np.unravel_index(np.argmax(drag_tensor), drag_tensor.shape)
    print(f"\n[CRITICAL POINT]: Highest Tension at Layer {max_idx[0]}, Qubit {max_idx[1]}, Param {max_idx[2]}")
    print(f"Value: {np.max(drag_tensor):.4f}")
