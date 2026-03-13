import pandas as pd
import numpy as np

def generate():
    t = np.linspace(0, 100, 1000) # 1000 steps for high resolution
    
    # CASE A: Steady State (1.2e14 n/cm2/s)
    steady = np.full(1000, 1.2e14)
    
    # CASE B: Pulsed (5.0e14 spikes, then 0. Total dose calibrated to match)
    # We pulse 24% of the time to keep total fluence roughly equal
    pulsed = np.array([5.0e14 if (i // 25) % 4 == 0 else 0.0 for i in range(1000)])
    
    df = pd.DataFrame({'time': t, 'flux_steady': steady, 'flux_pulsed': pulsed})
    df.to_csv('true_nuclear_data.csv', index=False)
    print("PHYSICS-READY DATASET GENERATED: true_nuclear_data.csv")

if __name__ == "__main__":
    generate()
