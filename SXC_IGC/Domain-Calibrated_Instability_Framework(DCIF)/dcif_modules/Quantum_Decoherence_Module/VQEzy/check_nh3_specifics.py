import h5py
import numpy as np
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
H5_PATH = os.path.join(BASE_DIR, 'qchem/nh3_16_qubit.h5')

with h5py.File(H5_PATH, 'r') as f:
    data = f['opt_params/sample_0'][()]
    # Shape is (3, 8, 4) or similar? Let's check the shape first
    print(f"Tensor Shape: {data.shape}")
    
    all_params = [f[f'opt_params/{k}'][()] for k in list(f['opt_params'].keys())[:50]]
    drag_tensor = np.var(np.array(all_params), axis=0)
    
    # Check the variance of the first 2 qubits (The High Tension ones)
    print(f"\nQubit 0 Variance (Avg across layers): {np.mean(drag_tensor[:, 0, :]):.4f}")
    print(f"Qubit 1 Variance (Avg across layers): {np.mean(drag_tensor[:, 1, :]):.4f}")
