import h5py
import numpy as np
import pandas as pd
import os

# Get the absolute path of the directory this script is in
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
H5_PATH = os.path.join(BASE_DIR, 'opt_params.h5')
SUBSTRATE_PATH = os.path.join(BASE_DIR, '..', 'ibmq_v12_performance_map.csv')

try:
    if not os.path.exists(H5_PATH):
        raise FileNotFoundError(f"H5 file not found at {H5_PATH}")
    
    substrate = pd.read_csv(SUBSTRATE_PATH)
    
    with h5py.File(H5_PATH, 'r') as f:
        group = f['opt_params']
        samples = sorted(list(group.keys()), key=lambda x: int(x.split('_')[-1]))
        
        volatility = []
        centroids = []
        
        for s in samples[:200]:
            data = group[s][()]
            volatility.append(np.var(data))
            centroids.append(np.mean(data))

    avg_vol = np.mean(volatility)
    drift = np.std(centroids)
    
    print(f"=== DCIF VQE SUBSTRATE ANALYSIS ===")
    print(f"Mean Parameter Volatility: {avg_vol:.6f}")
    print(f"Geometric Centroid Drift:  {drift:.6f}")
    
    high_gravity_risk = substrate[substrate['Tension'] > 0.5]['Tension'].mean()
    print(f"Current Chip Tension Stress: {high_gravity_risk:.4f}")
    
    if drift > (avg_vol * 0.5):
        print("\n[!] WARNING: Substrate Drift detected.")
        print("    Information Gravity is warping the optimization landscape.")

except Exception as e:
    print(f"STATUS: {e}")
