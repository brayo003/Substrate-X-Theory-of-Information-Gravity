import pandas as pd
import numpy as np
from v12_engine import SXCOmegaEngine
from sklearn.preprocessing import StandardScaler

def run_dynamic_test():
    # Load the high-tension miRNA file
    data_file = 'raw_data/277ef499-3b0f-429e-a5fd-b63b59ce731f.mirbase21.isoforms.quantification.txt'
    df = pd.read_csv(data_file, sep='\t')
    raw_array = df.select_dtypes(include=[np.number]).iloc[:, 0].values.reshape(-1, 1)
    signals = StandardScaler().fit_transform(raw_array).flatten()

    # Initial state: Standard Calibration
    beta, gamma = 3.5, 0.8
    engine = SXCOmegaEngine(beta=beta, gamma=gamma)
    
    print(f"DYNAMIC CALIBRATION RIG | Substrate: miRNA")
    print(f"{'INDEX':<6} | {'T_SYS':<8} | {'BETA':<6} | {'GAMMA':<6} | {'ACTION'}")
    print("-" * 55)

    for i, s in enumerate(signals[:100]):
        t_sys, phase = engine.step(abs(s) * 5)
        action = "NONE"

        # Dynamic Logic: If T_SYS exceeds 0.7, trigger regulatory response
        if t_sys > 0.7 and phase == "NOMINAL":
            gamma += 0.2
            beta -= 0.1
            engine.gamma = gamma
            engine.beta = beta
            action = "STABILIZE"
        
        if phase == "FIREWALL":
            action = "SATURATED"

        if i % 10 == 0 or action != "NONE":
            print(f"{i:<6} | {t_sys:<8.4f} | {beta:<6.1f} | {gamma:<6.1f} | {action}")
        
        if phase == "FIREWALL":
            break

if __name__ == "__main__":
    run_dynamic_test()
