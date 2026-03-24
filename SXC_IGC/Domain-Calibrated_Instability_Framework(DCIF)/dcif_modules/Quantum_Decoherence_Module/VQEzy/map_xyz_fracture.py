import h5py
import numpy as np
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
H5_PATH = os.path.join(BASE_DIR, 'qmanybody/xyz_4_qubit.h5')

if not os.path.exists(H5_PATH):
    print(f"Error: {H5_PATH} not found.")
else:
    with h5py.File(H5_PATH, 'r') as f:
        group = f['opt_params']
        keys = list(group.keys())
        # Sample 200 for deep variance analysis
        all_params = [group[k][()] for k in keys[:200]]
        drag_tensor = np.var(np.array(all_params), axis=0)

        print("=== DCIF ANATOMY: XYZ MODEL INSTABILITY ===")
        print(f"Global Mean Variance: {np.mean(drag_tensor):.4f}")
        
        # Focus on the most unstable layer
        max_layer = np.argmax(np.mean(drag_tensor, axis=(1,2)))
        print(f"Most Fractured Layer: {max_layer}")
        
        for q in range(drag_tensor.shape[1]):
            row = drag_tensor[max_layer, q]
            print(f"  Qubit {q} Stability: [{' '.join([f'{v:6.3f}' for v in row])}]")

