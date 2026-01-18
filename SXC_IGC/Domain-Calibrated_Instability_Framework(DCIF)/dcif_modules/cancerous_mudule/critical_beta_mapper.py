import os
import pandas as pd
import numpy as np
from v12_engine import SXCOmegaEngine
from sklearn.preprocessing import StandardScaler

def find_critical_beta(signals):
    # Search beta from 0.1 to 10.0 in increments of 0.1
    for b in np.arange(0.1, 10.1, 0.1):
        engine = SXCOmegaEngine(beta=b, gamma=0.8)
        for s in signals[:500]:
            _, phase = engine.step(abs(s) * 5)
            if phase == "FIREWALL":
                return b
    return 10.0 # Cap

def run_mapper():
    data_dir = 'raw_data'
    scaler = StandardScaler()
    files = [f for f in os.listdir(data_dir) if f.endswith(('.txt', '.quantification.txt', '.seg.txt'))]
    
    results = []
    print(f"MAPPING SUBSTRATE COMPLEXITY | Gamma=0.8")
    print(f"{'FILE SOURCE':<25} | {'CRITICAL BETA':<15} | {'RANK'}")
    print("-" * 55)

    for fname in files:
        try:
            df = pd.read_csv(os.path.join(data_dir, fname), sep='\t', comment='#')
            numeric_data = df.select_dtypes(include=[np.number])
            if numeric_data.empty: continue
            
            raw_array = numeric_data.iloc[:, 0].values.reshape(-1, 1)
            signals = scaler.fit_transform(raw_array).flatten()
            
            beta_c = find_critical_beta(signals)
            results.append((fname, beta_c))
        except:
            continue

    # Sort by complexity (Lowest Beta_c = Most Complex)
    results.sort(key=lambda x: x[1])
    
    for i, (fname, b_c) in enumerate(results):
        rank = "HIGH TENSION" if b_c < 2.5 else "LOW TENSION"
        print(f"{fname[:25]:<25} | {b_c:<15.2f} | {rank}")

if __name__ == "__main__":
    run_mapper()
