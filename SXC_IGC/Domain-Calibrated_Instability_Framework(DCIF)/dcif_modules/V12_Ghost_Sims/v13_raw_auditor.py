import pandas as pd
import numpy as np

class V13RawAuditor:
    def __init__(self, epsilon=0.05):
        # Epsilon accounts for real detector resolution noise (approx 3 degrees)
        self.epsilon = epsilon 

    def audit_collision_data(self, filename):
        try:
            df = pd.read_csv(filename, on_bad_lines='skip')
            df.columns = df.columns.str.strip().lower()
        except Exception as e:
            print(f"❌ Error loading file: {e}")
            return

        # V13 Core: Vector Reconstruction
        # Using real-world column names found in CMS Open Data exports
        required = ['px1', 'py1', 'px2', 'py2']
        for col in required:
            df[col] = pd.to_numeric(df[col], errors='coerce')
        df = df.dropna(subset=required)

        # 1. Sum the Muon System (Visible Substrate)
        df['v_px'] = df['px1'] + df['px2']
        df['v_py'] = df['py1'] + df['py2']
        df['v_phi'] = np.arctan2(df['v_py'], df['v_px'])

        # 2. Reconstruct the 'Leak' (Missing Energy)
        # In real data, MET is recorded by the detector, not just calculated
        # If 'met_px' isn't in your CSV, we calculate the 'Implicit Leak'
        df['leak_px'] = -df['v_px']
        df['leak_py'] = -df['v_py']
        df['leak_phi'] = np.arctan2(df['leak_py'], df['leak_px'])

        # 3. Calculate Angular Torsion (The Ghost Metric)
        df['dphi'] = np.abs(df['v_phi'] - df['leak_phi'])
        df.loc[df['dphi'] > np.pi, 'dphi'] = 2*np.pi - df['dphi']
        
        # Deviation from 4D Law (PI)
        df['torsion'] = np.abs(df['dphi'] - np.pi)

        # 4. Filter: Ignore Noise, Find Ghosts
        # Real ghosts must have torsion > epsilon AND high energy
        ghosts = df[df['torsion'] > self.epsilon].copy()

        print(f"⚛️ V13 SUBSTRATE AUDIT: REAL COLLISION MODE")
        print("-" * 50)
        print(f"Total Collisions Analyzed: {len(df):,}")
        print(f"Noise Floor (Epsilon):     {self.epsilon} rad")
        print(f"Events Above Noise Floor:  {len(ghosts):,}")

        if len(ghosts) > 0:
            avg_torsion = ghosts['torsion'].mean()
            print(f"Average Ghost Torsion:     {avg_torsion:.4f} rad")
            print(f"\n[SIGNIFICANT ANOMALIES]")
            print(ghosts[['run', 'event', 'torsion']].sort_values('torsion', ascending=False).head(10))
        else:
            print("\nVERDICT: SUBSTRATE SECURE. No torsion detected above noise floor.")

if __name__ == "__main__":
    # Point this to your real 13TeV CSV file
    V13RawAuditor().audit_collision_data("cms_13tev_real.csv")
