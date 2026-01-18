import os
import pandas as pd
import numpy as np
from v12_engine import SXCOmegaEngine
from sklearn.preprocessing import StandardScaler

def run_normalized_analysis():
    # Baseline calibration
    engine = SXCOmegaEngine(beta=3.5, gamma=0.8)
    data_dir = 'raw_data'
    scaler = StandardScaler()
    
    # We target the actual files we pulled earlier
    files = [f for f in os.listdir(data_dir) if f.endswith(('.txt', '.quantification.txt', '.seg.txt'))]
    
    if not files:
        print("ERROR: No data found in raw_data/. Run gdc_smart_pull.py first.")
        return

    print(f"DCIF NORMALIZED RESEARCH | Method: Z-Score (Mean=0, Std=1)")
    print(f"{'SOURCE FILE':<25} | {'MAX T_SYS':<10} | {'ENGINE STATE'}")
    print("-" * 65)

    for fname in files:
        try:
            # Load the raw informational field
            df = pd.read_csv(os.path.join(data_dir, fname), sep='\t', comment='#')
            numeric_data = df.select_dtypes(include=[np.number])
            if numeric_data.empty: continue
            
            # NORMALIZATION STEP: Remove raw magnitude
            # We treat the first numeric column as the signal array
            raw_array = numeric_data.iloc[:, 0].values.reshape(-1, 1)
            scaled_array = scaler.fit_transform(raw_array).flatten()
            
            max_t = 0
            saturated = False
            
            for s in scaled_array[:500]: # Sample 500 informational units
                # Signal is now the absolute deviation from the mean
                flux = abs(s) * 5 
                t_sys, phase = engine.step(flux)
                max_t = max(max_t, t_sys)
                
                if phase == "FIREWALL":
                    saturated = True
                    break
                    
            state = "SATURATED" if saturated else "NOMINAL"
            print(f"{fname[:25]:<25} | {max_t:<10.4f} | {state}")
            
        except Exception:
            continue

if __name__ == "__main__":
    run_normalized_analysis()
