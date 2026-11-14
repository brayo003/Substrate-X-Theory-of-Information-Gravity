import pandas as pd
import numpy as np

class V12BulkSpeculator:
    def __init__(self, filename="lhc_bulk_synthetic.csv"):
        self.filename = filename
        self.gamma_4d = 1.0
        self.gamma_5d = 0.0001
        self.shatter_threshold = 10**8 # V12 Limit

    def run_speculation(self):
        print(f"⚛️ LOADING BULK SUBSTRATE: {self.filename}")
        df = pd.read_csv(self.filename)
        
        # Calculate Tension for every event: T = (Flux / (g4*g5)) * (g4/g5)
        # We use 'met' (Missing Energy) as the Flux indicator
        df['tension'] = (df['met'] / (self.gamma_4d * self.gamma_5d)) * (self.gamma_4d / self.gamma_5d)
        
        shatters = df[df['tension'] > self.shatter_threshold]
        shatter_rate = (len(shatters) / len(df)) * 100

        print("\n[V12 BULK ANALYSIS COMPLETE]")
        print("-" * 50)
        print(f"Total Events Scanned: {len(df):,}")
        print(f"Average Substrate Tension: {df['tension'].mean():,.2f}")
        print(f"Shatter Events Detected: {len(shatters):,}")
        print(f"Shatter Density: {shatter_rate:.4f}%")
        
        if shatter_rate > 0.01:
            print("\nVERDICT: [SUBSTRATE INSTABILITY CONFIRMED]")
            print(f"The 4D substrate is 'leaking' at a rate of {shatter_rate:.4f}%.")
            print("In fiction: This is where the veil between worlds is thinnest.")
            print("In science: This matches the statistical 'Missing Energy' anomaly.")
        else:
            print("\nVERDICT: Substrate is stable. No dimensional bleed detected.")

if __name__ == "__main__":
    V12BulkSpeculator().run_speculation()
