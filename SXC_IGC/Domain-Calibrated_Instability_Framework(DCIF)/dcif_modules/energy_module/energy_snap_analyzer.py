import pandas as pd
import numpy as np

def run_energy_scan():
    print("--- Substrate-X: Energy Snap-Scan [PJM 2024] ---")
    
    # 1. Load the localized substrate
    df = pd.read_csv("energy_load_2024.csv")
    load_col = [c for c in df.columns if 'Load' in c or 'MW' in c][0]
    
    # 2. Calibration Constants (from your previous run)
    beta = 0.9880
    gamma = 0.1862
    
    # 3. Calculate Tension (T) and Curvature (K) for every hour
    # T = (E * beta) - (E_mean * gamma)
    # K = T / capacity_threshold
    e_mean = df[load_col].mean()
    e_max = df[load_col].max()
    
    # We define the 'Fracture Threshold' as the 95th percentile of observed load
    threshold = df[load_col].quantile(0.95)
    
    df['Tension'] = (df[load_col] * beta) - (e_mean * gamma)
    df['K_Factor'] = df['Tension'] / (threshold * (beta - gamma))

    # 4. Find the 'Critical Hours'
    critical_events = df[df['K_Factor'] >= 1.0]
    
    print(f"Total Hours Scanned: {len(df)}")
    print(f"Critical Fracture Hours (K >= 1.0): {len(critical_events)}")
    
    if len(critical_events) > 0:
        peak_event = df.iloc[df['K_Factor'].idxmax()]
        print(f"\n[!] MAX CURVATURE DETECTED")
        print(f"Peak K: {peak_event['K_Factor']:.4f}")
        print(f"Peak Load: {peak_event[load_col]:,.2f} MW")
    else:
        print("\n[STATUS] Substrate remained Elastic throughout 2024.")

if __name__ == "__main__":
    run_energy_scan()
