import pandas as pd
import numpy as np
from v12_engine import SXCOmegaEngine
from sklearn.preprocessing import StandardScaler

def process_file(filepath):
    df = pd.read_csv(filepath, sep='\t')
    raw_array = df['read_count'].values.reshape(-1, 1)
    return StandardScaler().fit_transform(raw_array).flatten()

cancer_signals = process_file('raw_data/277ef499-3b0f-429e-a5fd-b63b59ce731f.mirbase21.isoforms.quantification.txt')
normal_signals = process_file('raw_data/normal_lung_control.txt')

print(f"{'BETA':<6} | {'NORMAL MAX T':<12} | {'CANCER MAX T':<12} | {'STATUS'}")
print("-" * 50)

# Sweep Beta downwards to find the "Stability Window"
for b in np.arange(3.0, 0.5, -0.5):
    results = []
    for signals in [normal_signals, cancer_signals]:
        engine = SXCOmegaEngine(beta=b, gamma=0.8)
        max_t = 0
        for s in signals[:500]:
            t_sys, phase = engine.step(abs(s) * 5)
            max_t = max(max_t, t_sys)
        results.append(max_t)
    
    status = "GAP FOUND" if results[0] < 1.0 and results[1] >= 1.0 else "OVERLAP"
    if results[0] < 1.0 and results[1] < 1.0: status = "BOTH STABLE"
    
    print(f"{b:<6.1f} | {results[0]:<12.4f} | {results[1]:<12.4f} | {status}")
