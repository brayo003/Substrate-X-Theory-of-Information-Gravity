import pandas as pd
import numpy as np
import os
from v12_engine import SXCOmegaEngine
from sklearn.preprocessing import StandardScaler

def get_tension_score(filepath, b=1.5, g=0.8):
    try:
        df = pd.read_csv(filepath, sep='\t')
        signals = StandardScaler().fit_transform(df['read_count'].values.reshape(-1, 1)).flatten()
        engine = SXCOmegaEngine(beta=b, gamma=g)
        
        # Accumulate tension over a fixed 1000-unit substrate window
        total_tension = sum([engine.step(abs(s)*5)[0] for s in signals[:1000]])
        return total_tension
    except Exception as e:
        return None

# Mapping files
targets = {
    "CANCER_REF": "raw_data/277ef499-3b0f-429e-a5fd-b63b59ce731f.mirbase21.isoforms.quantification.txt",
    "NORMAL_REF": "raw_data/normal_lung_control.txt"
}

print(f"DCIF BULK CLASSIFIER | RE-CALIBRATED BETA: 1.5")
print(f"{'SAMPLE ID':<15} | {'SYSTEMIC TAX (ΣT)':<18} | {'PREDICTION'}")
print("-" * 55)

for label, path in targets.items():
    score = get_tension_score(path)
    if score:
        # Prediction logic based on the 20% Delta threshold
        prediction = "MALIGNANT" if score > 50 else "STABLE (HEALTHY)"
        print(f"{label:<15} | {score:<18.2f} | {prediction}")

