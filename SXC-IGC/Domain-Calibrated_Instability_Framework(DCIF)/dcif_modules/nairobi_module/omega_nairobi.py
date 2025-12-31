import pandas as pd
import numpy as np
import os

class NairobiOmega:
    def __init__(self, beta=2.0709, gamma=-1.6209):
        self.beta = beta
        self.gamma = gamma
        self.T_sys = 0.0
        self.phase = "NOMINAL"
        
    def run_live_simulation(self, agri_file, urban_file):
        # 1. Load data
        agri = pd.read_csv(agri_file)
        urban = pd.read_csv(urban_file)
        
        # 2. Fix the "Sequence" Error (Casting to Float)
        # We take the column named 'entropy_value' or the second column if name differs
        e_col = 'entropy_value' if 'entropy_value' in agri.columns else agri.columns[1]
        t_col = 'tension_value' if 'tension_value' in urban.columns else urban.columns[1]

        # Convert to float and drop any rows that aren't numbers
        E_series = pd.to_numeric(agri[e_col], errors='coerce').fillna(0)
        F_series = pd.to_numeric(urban[t_col], errors='coerce').fillna(0)

        print("-" * 65)
        print(f"NAIROBI OMEGA ENGINE | SYSTEM STATUS: ACTIVE")
        print(f"BETA: {self.beta} | GAMMA: {self.gamma}")
        print("-" * 65)
        print(f"{'STEP':<5} | {'VOLT (E)':<10} | {'TENSION (T)':<12} | {'PHASE'}")
        print("-" * 65)
        
        for i in range(len(E_series)):
            E = E_series.iloc[i] 
            F = F_series.iloc[i]
            
            # Substrate-X Law: T = beta*E - gamma*F
            # Result: If gamma is -1.62, this adds urban stress to agri stress.
            self.T_sys = (self.beta * E) - (self.gamma * F)
            
            if self.T_sys > 1.0:
                self.phase = "🔴 SINGULARITY (SNAP)"
            elif self.T_sys > 0.8:
                self.phase = "🟡 WARNING: CRITICAL"
            else:
                self.phase = "🟢 NOMINAL"
            
            print(f"{i:<5} | {E:<10.4f} | {self.T_sys:<12.4f} | {self.phase}")

if __name__ == "__main__":
    engine = NairobiOmega()
    engine.run_live_simulation('agricultural_entropy_base.csv', 'urban_tension_base.csv')
