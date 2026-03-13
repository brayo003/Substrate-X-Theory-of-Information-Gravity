import pandas as pd
import numpy as np

def run_energy_scan():
    print("--- Substrate-X: Energy Snap-Scan [Calibrated Trigger] ---")
    
    df = pd.read_csv("energy_load_2024.csv")
    load_col = [c for c in df.columns if 'Load' in c or 'MW' in c][0]
    
    beta, gamma = 0.9855, 0.1857
    e_mean = df[load_col].mean()
    threshold = df[load_col].quantile(0.95)
    # The 'Tangle Point': Conflict starts at 70% of the threshold
    tangle_point = threshold * 0.70 
    conflict_factor = 2.8

    df['Classical_Tension'] = (df[load_col] * beta) - (e_mean * gamma)
    df['Classical_K'] = df['Classical_Tension'] / (threshold * (beta - gamma))

    def calculate_sxc_tension(val):
        # Interference begins as the field approaches the threshold
        signal = val * conflict_factor if val > tangle_point else val
        return (signal * beta) - (e_mean * gamma)

    df['SXC_Tension'] = df[load_col].apply(calculate_sxc_tension)
    df['SXC_K'] = df['SXC_Tension'] / (threshold * (beta - gamma))

    classical_snaps = len(df[df['Classical_K'] >= 1.0])
    sxc_snaps = len(df[df['SXC_K'] >= 1.0])
    
    print(f"Classical Fracture Hours: {classical_snaps}")
    print(f"Substrate-X Ghost Snaps: {sxc_snaps}")
    print(f"Hidden Instability Ratio: {sxc_snaps / (classical_snaps if classical_snaps > 0 else 1):.2f}x")

if __name__ == "__main__":
    run_energy_scan()
