import pandas as pd
import numpy as np

def scan_asymmetry():
    # Load and clean headers
    df = pd.read_csv("lhc_real_data.csv", on_bad_lines='skip')
    df.columns = df.columns.str.strip()
    
    # Required columns for vector math
    cols = ['px1', 'py1', 'px2', 'py2']
    for col in cols:
        df[col] = pd.to_numeric(df[col], errors='coerce')
    df = df.dropna(subset=cols)

    # 1. Calculate the Muon System Vector
    muon_px = df['px1'] + df['px2']
    muon_py = df['py1'] + df['py2']
    muon_phi = np.arctan2(muon_py, muon_px)

    # 2. Calculate the "Leak" Vector (MET)
    met_px = -muon_px
    met_py = -muon_py
    met_phi = np.arctan2(met_py, met_px)

    # 3. Calculate Angular Delta (dPhi) and Deviation from PI
    dphi = np.abs(muon_phi - met_phi)
    # Wrap angles
    dphi = np.where(dphi > np.pi, 2*np.pi - dphi, dphi)
    
    # Deviation is how far we are from the perfect 180-degree (PI) balance
    df['deviation'] = np.abs(dphi - np.pi)

    # 4. Search for Asymmetry (Deviation > 0.001 radians)
    # We use a small epsilon to ignore floating point rounding errors
    anomalies = df[df['deviation'] > 1e-4].copy()

    print("⚛️ V12 ASYMMETRIC FLUX SCANNER")
    print("-" * 40)
    print(f"Total Events Scanned: {len(df):,}")
    print(f"Asymmetric Anomalies Found: {len(anomalies)}")

    if len(anomalies) > 0:
        print("\n[TOP ANOMALY SAMPLES]")
        # Sorting by highest deviation to find the "Ugliest" events
        samples = anomalies.sort_values('deviation', ascending=False).head(5)
        for _, row in samples.iterrows():
            print(f"Event {int(row['Event'])}: Deviation={row['deviation']:.6f} rad")
        
        print("\nVERDICT: SUBSTRATE TORSION DETECTED")
        print("These events do not conserve 4D angular momentum locally.")
    else:
        print("\nVERDICT: 4D RIGIDITY")
        print("Every single event in this file is perfectly balanced in 4D.")

if __name__ == "__main__":
    scan_asymmetry()
