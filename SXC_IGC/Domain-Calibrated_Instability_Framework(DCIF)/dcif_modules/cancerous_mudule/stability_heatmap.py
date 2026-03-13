import pandas as pd
import numpy as np
from v12_engine import SXCOmegaEngine
from sklearn.preprocessing import StandardScaler

def run_heatmap():
    data_file = 'raw_data/277ef499-3b0f-429e-a5fd-b63b59ce731f.mirbase21.isoforms.quantification.txt'
    df = pd.read_csv(data_file, sep='\t')
    raw_array = df.select_dtypes(include=[np.number]).iloc[:, 0].values.reshape(-1, 1)
    signals = StandardScaler().fit_transform(raw_array).flatten()

    # Define ranges for Beta and Gamma
    betas = np.linspace(0.5, 4.5, 9)
    gammas = np.linspace(0.2, 2.0, 10)

    print(f"STABILITY HEATMAP: miRNA | Signal: abs(s)*5")
    print(f"{'B/G':<6}", end="")
    for g in gammas: print(f"| {g:<5.1f}", end="")
    print("\n" + "-" * 75)

    for b in betas:
        print(f"{b:<5.1f}", end="")
        for g in gammas:
            engine = SXCOmegaEngine(beta=b, gamma=g)
            max_t = 0
            for s in signals[:500]:
                t_sys, phase = engine.step(abs(s) * 5)
                max_t = max(max_t, t_sys)
            
            # Label: . = Nominal, X = Saturated
            label = "." if max_t < 1.0 else "X"
            print(f"| {label:<5}", end="")
        print()

if __name__ == "__main__":
    run_heatmap()
