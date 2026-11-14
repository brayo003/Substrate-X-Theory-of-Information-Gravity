import pandas as pd
import numpy as np

def run_alignment_check():
    df = pd.read_csv("lhc_real_data.csv", on_bad_lines='skip')
    df.columns = df.columns.str.strip()
    
    # Calculate Vectors
    for col in ['px1', 'py1', 'px2', 'py2', 'phi1', 'phi2']:
        df[col] = pd.to_numeric(df[col], errors='coerce')
    df = df.dropna()

    # 1. Calculate the Muon System Vector (The visible push)
    df['muon_system_px'] = df['px1'] + df['px2']
    df['muon_system_py'] = df['py1'] + df['py2']
    df['muon_phi'] = np.arctan2(df['muon_system_py'], df['muon_system_px'])

    # 2. Calculate the "Leak" Vector (The MET)
    df['met_px'] = -df['muon_system_px']
    df['met_py'] = -df['muon_system_py']
    df['met_phi'] = np.arctan2(df['met_py'], df['met_px'])

    # 3. Calculate Angular Delta (dPhi)
    # Standard 4D physics requires dPhi to be exactly PI (180 degrees)
    df['dphi'] = np.abs(df['muon_phi'] - df['met_phi'])
    df.loc[df['dphi'] > np.pi, 'dphi'] = 2*np.pi - df['dphi']

    # Isolate our 15,093 "Total Shatter" events
    df['total_energy'] = np.sqrt(df['px1']**2 + df['py1']**2) + np.sqrt(df['px2']**2 + df['py2']**2)
    df['met_total'] = np.sqrt(df['met_px']**2 + df['met_py']**2)
    shatters = df[df['met_total'] / df['total_energy'] > 0.99]

    print("⚛️ V12 ANGULAR INTEGRITY CHECK")
    print("-" * 40)
    print(f"Analyzing Shatter Events: {len(shatters)}")
    
    avg_dphi = shatters['dphi'].mean()
    print(f"Average Angular Delta: {avg_dphi:.4f} rad (Expected: {np.pi:.4f})")
    
    # Deviation from 180 degrees
    deviation = np.abs(avg_dphi - np.pi)
    
    print(f"Alignment Deviation: {deviation:.6f}")
    
    if deviation < 1e-5:
        print("\nVERDICT: [4D SHADOW]")
        print("The leak is perfectly opposite the muons. It is the 'rest of the car'.")
    else:
        print("\nVERDICT: [SUBSTRATE TORSION]")
        print(f"The leak is off-axis by {np.degrees(deviation):.4f} degrees.")
        print("Information is exiting the 4D plane at a non-standard angle.")

if __name__ == "__main__":
    run_alignment_check()
