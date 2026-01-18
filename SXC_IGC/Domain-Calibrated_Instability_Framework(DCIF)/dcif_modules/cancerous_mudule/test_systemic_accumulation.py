import pandas as pd
import numpy as np
from v12_engine import SXCOmegaEngine
from sklearn.preprocessing import StandardScaler

def process_file(filepath):
    df = pd.read_csv(filepath, sep='\t')
    raw_array = df['read_count'].values.reshape(-1, 1)
    return StandardScaler().fit_transform(raw_array).flatten()

cancer_signals = process_file('raw_data/277ef499-3b0f-429e-a5fd-b63b59ce731f.mirbase21.isoforms.quantification.txt')
normal_signals = process_file('raw_data/normal_lung_control.txt')

def get_accumulation(signals, b=1.5, g=0.8):
    engine = SXCOmegaEngine(beta=b, gamma=g)
    total_tension = 0
    for s in signals[:1000]:
        t_sys, _ = engine.step(abs(s) * 5)
        total_tension += t_sys
    return total_tension

c_acc = get_accumulation(cancer_signals)
n_acc = get_accumulation(normal_signals)

print(f"ACCUMULATED SYSTEMIC TENSION (1000 STEPS)")
print(f"CANCER: {c_acc:.2f}")
print(f"NORMAL: {n_acc:.2f}")
print(f"DELTA: {((c_acc/n_acc)-1)*100:.2f}%")
