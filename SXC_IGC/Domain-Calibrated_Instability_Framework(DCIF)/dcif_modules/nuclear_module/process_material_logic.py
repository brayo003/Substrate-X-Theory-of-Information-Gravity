import pandas as pd
import numpy as np
import warnings
warnings.filterwarnings('ignore')

df = pd.read_csv('irradiation_benchmarks.csv')

def sxc_predict(temp, t0):
    return 1.0 * np.exp(-0.012 * (temp - t0))

print(f"{'Material':<12} | {'Temp':<5} | {'Actual':<8} | {'SXC Pred':<8} | {'Accuracy'}")
print("-" * 55)

for mat in df['material'].unique():
    mat_df = df[df['material'] == mat]
    t0 = mat_df[mat_df['regime'] == 'crossover']['temp_c'].values[0]
    
    for _, row in mat_df.iterrows():
        pred = sxc_predict(row['temp_c'], t0)
        acc = 100 - abs((row['pulse_steady_ratio'] - pred) / row['pulse_steady_ratio'] * 100)
        print(f"{row['material']:<12} | {row['temp_c']:<5} | {row['pulse_steady_ratio']:<8.2f} | {pred:<8.2f} | {acc:.1f}%")
