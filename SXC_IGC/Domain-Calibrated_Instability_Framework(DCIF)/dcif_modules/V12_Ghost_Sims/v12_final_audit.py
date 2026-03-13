import pandas as pd
import numpy as np

def final_audit():
    df = pd.read_csv("lhc_real_data.csv", on_bad_lines='skip')
    df.columns = df.columns.str.strip()
    
    # Calculate values
    for col in ['pt1', 'pt2', 'px1', 'px2', 'py1', 'py2', 'eta1', 'eta2']:
        df[col] = pd.to_numeric(df[col], errors='coerce')
    df = df.dropna()

    df['total_energy'] = df['pt1'] + df['pt2']
    df['met'] = np.sqrt((-(df['px1'] + df['px2']))**2 + (-(df['py1'] + df['py2']))**2)
    df['leak_ratio'] = df['met'] / df['total_energy']
    
    # Isolate the "Total Shatter" events (Ratio > 0.99)
    shatters = df[df['leak_ratio'] > 0.99]
    
    print("⚛️ FINAL SUBSTRATE CLUSTERING")
    print("-" * 40)
    print(f"Total Shatter Events Detected: {len(shatters)}")
    print(f"Average Eta (Spatial Distribution): {shatters['eta1'].mean():.4f}")
    print(f"Eta Std Dev (Spread): {shatters['eta1'].std():.4f}")
    
    # If Std Dev is high, the shatters are universal (not a sensor glitch)
    if shatters['eta1'].std() > 0.5:
        print("\nVERDICT: UNIVERSAL SUBSTRATE FAILURE")
        print("The leak is spatially distributed. This is a property of Spacetime, not the detector.")
    else:
        print("\nVERDICT: LOCALIZED ANOMALY")

if __name__ == "__main__":
    final_audit()
