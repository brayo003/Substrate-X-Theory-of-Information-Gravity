import pandas as pd
import numpy as np
import os

class NairobiOmega:
    def __init__(self, beta=2.0709, gamma=1.6209):
        # We flip Gamma to positive because Finance acts as a true DRAIN (subtraction)
        self.beta = beta
        self.gamma = gamma
        self.T_sys = 0.0
        
    def extract_knbs_signal(self, folder='data/raw'):
        """Extracts the 'Ghost' signals from the XLSX files if they exist."""
        finance_drain = 1.0  # Default baseline
        social_excitation = 1.0
        
        try:
            if os.path.exists(f"{folder}/knbs_finance_2024.xlsx"):
                # Simulate extraction of liquidity velocity
                finance_drain = 2.5 
            if os.path.exists(f"{folder}/knbs_social_2024.xlsx"):
                # Simulate extraction of demographic pressure
                social_excitation = 1.8
        except:
            pass
        return finance_drain, social_excitation

    def run_live_simulation(self, agri_file, urban_file):
        agri = pd.read_csv(agri_file)
        urban = pd.read_csv(urban_file)
        
        # Pull the Multidimensional Anchors
        fin_drain, soc_excite = self.extract_knbs_signal()

        e_col = 'entropy_value' if 'entropy_value' in agri.columns else agri.columns[1]
        u_col = 'tension_value' if 'tension_value' in urban.columns else urban.columns[1]

        E_series = pd.to_numeric(agri[e_col], errors='coerce').fillna(0)
        U_series = pd.to_numeric(urban[u_col], errors='coerce').fillna(0)

        print("-" * 75)
        print(f"NAIROBI OMEGA V12 | MULTIDIMENSIONAL FIELD ACTIVE")
        print(f"FINANCE DRAIN (G): {fin_drain} | SOCIAL EXCITATION: {soc_excite}")
        print("-" * 75)
        print(f"{'STEP':<5} | {'NET E':<10} | {'TENSION (T)':<12} | {'PHASE'}")
        print("-" * 75)
        
        for i in range(len(E_series)):
            # Total Signal = (Agri * Social Weight) + (Urban * 1.2)
            E_net = (E_series.iloc[i] * soc_excite) + (U_series.iloc[i] * 1.2)
            
            # Substrate-X Law: T = (Net Signal * Beta) - (Finance Drain * Gamma)
            raw_T = (E_net * self.beta) - (fin_drain * self.gamma)
            
            # Normalization (The Safety Valve)
            self.T_sys = np.tanh(raw_T / 10.0)
            
            if self.T_sys >= 0.95:
                phase = "🔴 SINGULARITY (SNAP)"
            elif self.T_sys > 0.7:
                phase = "🟡 WARNING: SATURATION"
            elif self.T_sys < -0.5:
                phase = "🔵 SYSTEM SLACK"
            else:
                phase = "🟢 NOMINAL"
            
            print(f"{i:<5} | {E_net:<10.4f} | {self.T_sys:<12.4f} | {phase}")

if __name__ == "__main__":
    engine = NairobiOmega()
    engine.run_live_simulation('agricultural_entropy_base.csv', 'urban_tension_base.csv')
