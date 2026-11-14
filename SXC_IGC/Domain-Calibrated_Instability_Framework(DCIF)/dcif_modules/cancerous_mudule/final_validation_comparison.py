import pandas as pd
import numpy as np
from v12_engine import SXCOmegaEngine
from sklearn.preprocessing import StandardScaler

def process_file(filepath):
    df = pd.read_csv(filepath, sep='\t')
    # Target 'read_count' column as the primary signal
    raw_array = df['read_count'].values.reshape(-1, 1)
    return StandardScaler().fit_transform(raw_array).flatten()

def run_comparison():
    # Standard tension calibration
    engine = SXCOmegaEngine(beta=3.5, gamma=0.8)
    
    # Files
    cancer_file = 'raw_data/277ef499-3b0f-429e-a5fd-b63b59ce731f.mirbase21.isoforms.quantification.txt'
    normal_file = 'raw_data/normal_lung_control.txt'
    
    print(f"DCIF VALIDATION TRACE | Engine: V12 | Beta: 3.5 | Gamma: 0.8")
    print(f"{'SUBSTRATE':<20} | {'MAX T_SYS':<10} | {'OUTCOME'}")
    print("-" * 55)

    for label, path in [("CANCER (miRNA)", cancer_file), ("NORMAL (miRNA)", normal_file)]:
        signals = process_file(path)
        max_t = 0
        state = "NOMINAL"
        
        # We process the first 1000 signals to see the accumulation effect
        for s in signals[:1000]:
            t_sys, phase = engine.step(abs(s) * 5)
            max_t = max(max_t, t_sys)
            if phase == "FIREWALL":
                state = "SATURATED"
                break
        
        print(f"{label:<20} | {max_t:<10.4f} | {state}")

if __name__ == "__main__":
    run_comparison()
