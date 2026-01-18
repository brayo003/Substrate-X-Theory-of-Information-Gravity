import pandas as pd
import numpy as np
from v12_engine import SXCOmegaEngine
from sklearn.preprocessing import StandardScaler

def get_score(filepath, b, g):
    df = pd.read_csv(filepath, sep='\t')
    signals = StandardScaler().fit_transform(df['read_count'].values.reshape(-1, 1)).flatten()
    engine = SXCOmegaEngine(beta=b, gamma=g)
    return sum([engine.step(abs(s)*5)[0] for s in signals[:1000]])

# Constants
BETA = 1.5
TARGET_TAX = 44.83  # The Normal Baseline
cancer_path = 'raw_data/277ef499-3b0f-429e-a5fd-b63b59ce731f.mirbase21.isoforms.quantification.txt'

print(f"SIMULATING REGULATORY RESCUE | Target ΣT: {TARGET_TAX}")
print(f"{'DRAIN (GAMMA)':<15} | {'CURRENT ΣT':<12} | {'RESCUE STATUS'}")
print("-" * 50)

for g in np.arange(0.8, 1.3, 0.05):
    current_tax = get_score(cancer_path, BETA, g)
    status = "RESCUED" if current_tax <= TARGET_TAX else "INSUFFICIENT"
    print(f"{g:<15.2f} | {current_tax:<12.2f} | {status}")
    if status == "RESCUED":
        break
