import pandas as pd
import numpy as np

def run_test():
    df = pd.read_csv("lhc_real_data.csv", on_bad_lines='skip')
    df.columns = df.columns.str.strip()
    
    # Calculate Energy (Flux) and Leak (MET)
    df['pt1'] = pd.to_numeric(df['pt1'], errors='coerce')
    df['pt2'] = pd.to_numeric(df['pt2'], errors='coerce')
    df['px1'] = pd.to_numeric(df['px1'], errors='coerce')
    df['px2'] = pd.to_numeric(df['px2'], errors='coerce')
    df['py1'] = pd.to_numeric(df['py1'], errors='coerce')
    df['py2'] = pd.to_numeric(df['py2'], errors='coerce')
    df = df.dropna(subset=['pt1', 'pt2', 'px1', 'px2', 'py1', 'py2'])

    df['total_energy'] = df['pt1'] + df['pt2']
    df['met'] = np.sqrt((-(df['px1'] + df['px2']))**2 + (-(df['py1'] + df['py2']))**2)
    df['leak_ratio'] = df['met'] / df['total_energy']

    # Sort by energy to see the trend
    df = df.sort_values('total_energy')
    
    # Group into bins to see if the ratio drops at high energy (Stabilization)
    bins = np.linspace(df['total_energy'].min(), df['total_energy'].max(), 10)
    df['energy_bin'] = pd.cut(df['total_energy'], bins)
    trend = df.groupby('energy_bin')['leak_ratio'].mean()

    print("⚛️ STABILIZATION ANALYSIS")
    print("-" * 40)
    print(trend)
    
    if trend.iloc[-1] < trend.iloc[0]:
        print("\nVERDICT: STABILIZATION DETECTED.")
        print("Leakage ratio decreases at high energy. The substrate is 'crystallizing'.")
    else:
        print("\nVERDICT: LINEAR LEAKAGE. No stabilization found.")

if __name__ == "__main__":
    run_test()
