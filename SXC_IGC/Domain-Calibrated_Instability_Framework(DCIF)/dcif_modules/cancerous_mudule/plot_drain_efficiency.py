import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from v12_engine import SXCOmegaEngine
from sklearn.preprocessing import StandardScaler

def process_file(filepath):
    df = pd.read_csv(filepath, sep='\t')
    return StandardScaler().fit_transform(df['read_count'].values.reshape(-1, 1)).flatten()

c_signals = process_file('raw_data/277ef499-3b0f-429e-a5fd-b63b59ce731f.mirbase21.isoforms.quantification.txt')
n_signals = process_file('raw_data/normal_lung_control.txt')

def get_trace(signals):
    engine = SXCOmegaEngine(beta=1.5, gamma=0.8)
    return [engine.step(abs(s)*5)[0] for s in signals[:200]]

plt.figure(figsize=(10, 5))
plt.plot(get_trace(c_signals), label='CANCER (High Persistence)', color='red', alpha=0.7)
plt.plot(get_trace(n_signals), label='NORMAL (Rapid Drain)', color='blue', alpha=0.7)
plt.title('Substrate-X: Drain Efficiency Comparison (20% Delta)')
plt.ylabel('Systemic Tension (T_SYS)')
plt.xlabel('Informational Steps')
plt.legend()
plt.grid(True, which='both', linestyle='--', alpha=0.5)
plt.savefig('drain_efficiency.png')
print("SUCCESS: 'drain_efficiency.png' generated. View this to see the Delta.")
