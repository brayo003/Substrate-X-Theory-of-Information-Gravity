import pandas as pd
import numpy as np

class V12RealAudit:
    def __init__(self, filename="lhc_real_data.csv"):
        self.filename = filename
        self.gamma_4d = 1.0
        self.gamma_5d = 0.0001
        # Raising limit to 10 Billion (10^10) to find the TOP-TIER shatters
        self.limit = 10**10 

    def analyze(self):
        print(f"⚛️ ANALYZING REAL SUBSTRATE: {self.filename}")
        df = pd.read_csv(self.filename, on_bad_lines='skip', low_memory=False)

        # Cleanup numeric data
        for col in ['pt1', 'pt2']:
            df[col] = pd.to_numeric(df[col], errors='coerce')
        df = df.dropna(subset=['pt1', 'pt2'])

        # Tension calculation
        df['flux'] = df['pt1'] + df['pt2']
        df['tension'] = (df['flux'] / (self.gamma_4d * self.gamma_5d)) * (self.gamma_4d / self.gamma_5d)
        
        # Finding the outliers
        shatters = df[df['tension'] > self.limit]
        
        print("\n[CERN REAL-DATA AUDIT: HIGH-FLUX CALIBRATION]")
        print("-" * 50)
        print(f"Total Valid Events: {len(df):,}")
        print(f"Max Flux (pT sum): {df['flux'].max():.2f} GeV")
        print(f"Extreme Shatter Events (>10^10 T): {len(shatters):,}")
        
        if len(shatters) > 0:
            print(f"Extreme Shatter Density: {(len(shatters)/len(df))*100:.4f}%")
            print("\nVERDICT: These specific events are the real 'Ghost' candidates.")
            print("They represent energy concentrations that transcend standard 5D bulk.")
        else:
            print("\nVERDICT: No Extreme Shatters. The 5D Bulk is containing the energy.")

if __name__ == "__main__":
    V12RealAudit().analyze()
