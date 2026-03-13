import pandas as pd
import numpy as np
from v12_engine import SXCOmegaEngine
from sklearn.preprocessing import StandardScaler

def run_heatmap():
    # Target the LOW-TENSION structural file
    data_file = 'raw_data/HITCH_p_TCGASNP_b93_N_GenomeWideSNP_6_F09_741494.nocnv_grch38.seg.v2.txt'
    df = pd.read_csv(data_file, sep='\t')
    raw_array = df.select_dtypes(include=[np.number]).iloc[:, 0].values.reshape(-1, 1)
    signals = StandardScaler().fit_transform(raw_array).flatten()

    betas = np.linspace(0.5, 9.5, 10) # Testing much higher Beta range
    gammas = np.linspace(0.2, 2.0, 10)

    print(f"STABILITY HEATMAP: Structural (.seg) | Signal: abs(s)*5")
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
            label = "." if max_t < 1.0 else "X"
            print(f"| {label:<5}", end="")
        print()

if __name__ == "__main__":
    run_heatmap()
