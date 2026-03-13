import pandas as pd
import numpy as np
from v12_engine import SXCOmegaEngine
from sklearn.preprocessing import StandardScaler

def run_rescue():
    # Target the high-tension miRNA file
    data_file = 'raw_data/277ef499-3b0f-429e-a5fd-b63b59ce731f.mirbase21.isoforms.quantification.txt'
    df = pd.read_csv(data_file, sep='\t')
    raw_array = df.select_dtypes(include=[np.number]).iloc[:, 0].values.reshape(-1, 1)
    signals = StandardScaler().fit_transform(raw_array).flatten()

    # Hold Beta at 3.5 (The point where it previously saturated)
    fixed_beta = 3.5
    
    print(f"REGULATORY RESCUE | Substrate: miRNA | Fixed Beta: {fixed_beta}")
    print(f"{'GAMMA (Drain)':<15} | {'MAX T_SYS':<10} | {'ENGINE STATE'}")
    print("-" * 45)

    # Sweep Gamma from 0.1 to 2.0
    for g in np.arange(0.1, 2.1, 0.2):
        engine = SXCOmegaEngine(beta=fixed_beta, gamma=g)
        max_t = 0
        saturated = False
        
        for s in signals[:500]:
            t_sys, phase = engine.step(abs(s) * 5)
            max_t = max(max_t, t_sys)
            if phase == "FIREWALL":
                saturated = True
                # We don't break here so we can see how far past 1.0 T_SYS goes
        
        state = "SATURATED" if max_t >= 1.0 else "NOMINAL"
        print(f"{g:<15.2f} | {max_t:<10.4f} | {state}")

if __name__ == "__main__":
    run_rescue()
