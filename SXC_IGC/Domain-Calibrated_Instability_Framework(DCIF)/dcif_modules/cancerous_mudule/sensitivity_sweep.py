import pandas as pd
import numpy as np
from v12_engine import SXCOmegaEngine
from sklearn.preprocessing import StandardScaler

def run_sweep():
    data_file = 'raw_data/277ef499-3b0f-429e-a5fd-b63b59ce731f.mirbase21.isoforms.quantification.txt'
    df = pd.read_csv(data_file, sep='\t')
    raw_array = df.select_dtypes(include=[np.number]).iloc[:, 0].values.reshape(-1, 1)
    signals = StandardScaler().fit_transform(raw_array).flatten()

    print(f"BETA SENSITIVITY SWEEP | Substrate: miRNA Quantification")
    print(f"{'BETA':<10} | {'MAX T_SYS':<10} | {'ENGINE STATE'}")
    print("-" * 40)

    # Sweep Beta from 0.5 to 5.0
    for b in np.arange(0.5, 5.5, 0.5):
        engine = SXCOmegaEngine(beta=b, gamma=0.8)
        max_t = 0
        saturated = False
        
        for s in signals[:500]:
            t_sys, phase = engine.step(abs(s) * 5)
            max_t = max(max_t, t_sys)
            if phase == "FIREWALL":
                saturated = True
                break
        
        state = "SATURATED" if saturated else "NOMINAL"
        print(f"{b:<10.2f} | {max_t:<10.4f} | {state}")

if __name__ == "__main__":
    run_sweep()
