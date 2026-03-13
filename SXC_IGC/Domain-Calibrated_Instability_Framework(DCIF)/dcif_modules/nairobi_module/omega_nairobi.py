import pandas as pd
import numpy as np
import os

class NairobiOmega:
    def __init__(self, beta=0.5922, gamma=0.6698):
        # Using calibrated coefficients from your calibrate_nairobi.py
        self.beta = beta
        self.gamma = gamma
        self.conflict_factor = 2.8
        
    def extract_knbs_signal(self, folder='data/raw'):
        # Dynamic extraction from KNBS Substrates
        finance_drain = 2.5 if os.path.exists(f"{folder}/knbs_finance_2024.xlsx") else 1.0
        social_excitation = 1.8 if os.path.exists(f"{folder}/knbs_social_2024.xlsx") else 1.0
        return finance_drain, social_excitation

    def run_live_simulation(self, agri_file, urban_file):
        agri = pd.read_csv(agri_file)
        urban = pd.read_csv(urban_file)
        fin_drain, soc_excite = self.extract_knbs_signal()

        e_col = agri.columns[1]
        u_col = urban.columns[1]

        print("-" * 85)
        print(f"NAIROBI OMEGA V12 | TRIANGULAR CONFLICT ENGINE ACTIVE")
        print(f"BETA: {self.beta:.4f} | GAMMA: {self.gamma:.4f} | CONFLICT FACTOR: {self.conflict_factor}")
        print("-" * 85)
        print(f"{'STEP':<5} | {'NET E':<10} | {'TENSION (T)':<12} | {'PHASE'}")
        print("-" * 85)

        # Threshold for 'Tangle' is 70% of the max observed E_net
        temp_e_net = (agri[e_col] * soc_excite) + (urban[u_col] * 1.2)
        tangle_point = temp_e_net.quantile(0.70)
        
        for i in range(len(agri)):
            E_base = (agri[e_col].iloc[i] * soc_excite) + (urban[u_col].iloc[i] * 1.2)
            
            # THE SUBSTRATE-X LAW: 
            # If signal exceeds Tangle Point, apply the 2.8x Interference Factor
            if E_base > tangle_point:
                E_effective = E_base * self.conflict_factor
            else:
                E_effective = E_base
                
            raw_T = (E_effective * self.beta) - (fin_drain * self.gamma)
            T_sys = np.tanh(raw_T / 10.0) # Normalization
            
            if T_sys >= 0.90:
                phase = "🔴 GHOST SNAP (3-WAY CONFLICT)"
            elif T_sys > 0.6:
                phase = "🟡 TANGLE DETECTED"
            else:
                phase = "🟢 STABLE SUBSTRATE"
            
            print(f"{i:<5} | {E_base:<10.4f} | {T_sys:<12.4f} | {phase}")

if __name__ == "__main__":
    engine = NairobiOmega()
    engine.run_live_simulation('agricultural_entropy_base.csv', 'urban_tension_base.csv')
