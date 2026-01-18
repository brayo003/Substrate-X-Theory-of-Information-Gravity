import os
import pandas as pd
import numpy as np
from v12_engine import SXCOmegaEngine

def analyze_raw_substrate():
    engine = SXCOmegaEngine(beta=3.5, gamma=0.8)
    data_dir = 'raw_data'
    
    files = [f for f in os.listdir(data_dir) if f.endswith(('.txt', '.quantification.txt'))]
    
    print(f"{'FILE SOURCE':<25} | {'MAX T_SYS':<10} | {'FINAL PHASE'}")
    print("-" * 55)

    for fname in files:
        # Load numeric data (skipping non-numeric headers)
        try:
            df = pd.read_csv(os.path.join(data_dir, fname), sep='\t', comment='#')
            # Extract any numeric column as the 'Signal Field'
            numeric_cols = df.select_dtypes(include=[np.number]).columns
            if len(numeric_cols) == 0: continue
            
            signals = df[numeric_cols[0]].values
            
            max_t = 0
            current_phase = "NOMINAL"
            
            for s in signals[:500]: # Sample the first 500 informational units
                # Normalize signal for the engine (Log-Flux)
                flux = np.log1p(abs(s)) * 5
                t_sys, phase = engine.step(flux)
                max_t = max(max_t, t_sys)
                current_phase = phase
                
            print(f"{fname[:25]:<25} | {max_t:<10.4f} | {current_phase}")
            
        except Exception:
            continue

if __name__ == "__main__":
    analyze_raw_substrate()
