import pandas as pd
import numpy as np
from domain_adjacency_map import DomainGuard

class LogisticsBridge:
    def __init__(self, domain_file='domain_scales.csv'):
        self.df = pd.read_csv(domain_file)
        self.guard = DomainGuard()
        self.active_tensions = {"logistics": 0.0}

    def run_stress_test(self, inverse_stability=False):
        f_src = self.df[self.df['domain'] == 'finance_module'].iloc[0]
        l_tgt = self.df[self.df['domain'] == 'logistics'].iloc[0]
        
        # Determine the target's behavior
        gamma_tgt = l_tgt['gamma'] * -1 if inverse_stability else l_tgt['gamma']
        
        # Interference = (Gamma_Src / Gamma_Tgt)^2
        # Note: We use absolute value for the ratio, but the sign dictates tension behavior
        interference = (f_src['gamma'] / abs(gamma_tgt)) ** 2
        
        print(f"STRESS TEST: Finance -> Logistics | Inverse Stability: {inverse_stability}")
        print(f"Interference Load: {interference:.2f}x")
        print("-" * 65)
        
        for pulse in range(1, 6):
            # Tension Calculation:
            # If inverse_stability is True, tension compounds (positive feedback)
            if inverse_stability:
                delta_t = (1.0 * interference) * 0.01
                self.active_tensions["logistics"] = (self.active_tensions["logistics"] + delta_t) * 1.1 
            else:
                delta_t = (1.0 * interference) * 0.01
                self.active_tensions["logistics"] += delta_t
            
            t_current = self.active_tensions["logistics"]
            status = "STABLE" if t_current < 0.7 else "!!! TANGLE WARNING !!!"
            if t_current >= 1.0: status = "!!! SUBSTRATE SHATTER !!!"
            
            print(f"PULSE {pulse:02} | TENSION: {t_current:.4f} | {status}")
            if t_current >= 1.0: break

if __name__ == "__main__":
    bridge = LogisticsBridge()
    bridge.run_stress_test(inverse_stability=False)
    print("\n--- SWITCHING TO INVERSE STABILITY ---")
    bridge_inv = LogisticsBridge()
    bridge_inv.run_stress_test(inverse_stability=True)
