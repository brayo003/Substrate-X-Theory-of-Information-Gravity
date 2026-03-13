import pandas as pd
import numpy as np

class V12DifferentialAudit:
    def __init__(self, filename="lhc_real_data.csv"):
        self.filename = filename
        self.limit = 10**10 

    def run_comparison(self):
        df = pd.read_csv(self.filename, on_bad_lines='skip', low_memory=False)
        df.columns = df.columns.str.strip()
        
        cols = ['px1', 'py1', 'px2', 'py2', 'pt1', 'pt2']
        for col in cols:
            df[col] = pd.to_numeric(df[col], errors='coerce')
        df = df.dropna(subset=cols)

        # Calculate Tension and MET for the whole set
        df['flux'] = df['pt1'] + df['pt2']
        df['tension'] = (df['flux'] / 0.0001**2)
        df['met'] = np.sqrt((-(df['px1'] + df['px2']))**2 + (-(df['py1'] + df['py2']))**2)
        
        # Split into Ghost (High Tension) and Baseline (Normal)
        ghosts = df[df['tension'] > self.limit]
        baseline = df[df['tension'] <= self.limit]

        avg_ghost_leak = ghosts['met'].mean()
        avg_base_leak = baseline['met'].mean()
        
        # Ratio of Leakage to Flux (Efficiency of the Shatter)
        ghost_efficiency = (ghosts['met'] / ghosts['flux']).mean()
        base_efficiency = (baseline['met'] / baseline['flux']).mean()

        print("⚛️ V12 DIFFERENTIAL SUBSTRATE AUDIT")
        print("-" * 50)
        print(f"Baseline Events: {len(baseline):,}")
        print(f"Ghost Events:    {len(ghosts):,}")
        print("-" * 50)
        print(f"Avg Baseline Leak: {avg_base_leak:.2f} GeV")
        print(f"Avg Ghost Leak:    {avg_ghost_leak:.2f} GeV")
        print(f"Leakage Multiplier: {avg_ghost_leak / avg_base_leak:.2f}x")
        
        print("\n[SHATTER EFFICIENCY]")
        print(f"Baseline Leak-to-Flux Ratio: {base_efficiency:.4f}")
        print(f"Ghost Leak-to-Flux Ratio:    {ghost_efficiency:.4f}")
        
        diff = (ghost_efficiency / base_efficiency)
        print(f"\nRESULT: High-Tension events are {diff:.2f}x more likely to bleed information.")

if __name__ == "__main__":
    V12DifferentialAudit().run_comparison()
