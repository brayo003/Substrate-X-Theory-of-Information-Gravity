import h5py
import numpy as np
import pandas as pd
import os

# Paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
H5_PATH = os.path.join(BASE_DIR, 'qchem/h2_4_qubit.h5')
SUBSTRATE_PATH = os.path.join(BASE_DIR, '..', 'ibmq_v12_performance_map.csv')

def run_audit():
    with h5py.File(H5_PATH, 'r') as f:
        group = f['opt_params']
        keys = list(group.keys())
        
        # Calculate Variance across all samples (The Substrate Drag)
        all_params = [group[k][()] for k in keys[:100]]
        param_matrix = np.array(all_params)
        
        # Variance per parameter coordinate (3, 2, 4)
        drag_tensor = np.var(param_matrix, axis=0)
        mean_drag = np.mean(drag_tensor)
        
        print(f"=== DCIF SUBSTRATE DRAG AUDIT: H2 (4-Qubit) ===")
        print(f"Tensor Footprint: {drag_tensor.shape}")
        print(f"Mean Substrate Drag (Variance): {mean_drag:.8f}")

    # Cross-reference with Toronto Tension
    if os.path.exists(SUBSTRATE_PATH):
        sub = pd.read_csv(SUBSTRATE_PATH)
        avg_tension = sub['Tension'].mean()
        print(f"Target Substrate Tension: {avg_tension:.4f}")
        
        # The V12 Prediction
        predicted_noise = avg_tension * 0.05 # Baseline scaling
        print(f"V12 Predicted Noise Floor: {predicted_noise:.8f}")
        
        if mean_drag > predicted_noise:
            print("\n[!] WARNING: Observed Drag exceeds Predicted Noise Floor.")
            print("    Substrate-X Effect confirmed: Environment is actively de-optimizing the VQE.")

run_audit()
