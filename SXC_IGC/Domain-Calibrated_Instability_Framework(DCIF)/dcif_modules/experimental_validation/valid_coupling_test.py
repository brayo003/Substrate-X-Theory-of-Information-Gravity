import pandas as pd
import numpy as np
from domain_adjacency_map import DomainGuard

class ValidatedBridge:
    def __init__(self, domain_file='domain_scales.csv'):
        self.df = pd.read_csv(domain_file)
        self.guard = DomainGuard()
        self.active_tensions = {row['domain']: 0.0 for _, row in self.df.iterrows()}

    def run_safe_flux(self, source_name, target_name, flux_magnitude=1.0):
        if not self.guard.is_coupling_allowed(source_name, target_name):
            return f"BLOCKED: No causal link between {source_name} and {target_name}"

        src = self.df[self.df['domain'] == source_name].iloc[0]
        tgt = self.df[self.df['domain'] == target_name].iloc[0]
        
        # Calculate Quadratic Interference
        interference = (src['gamma'] / tgt['gamma']) ** 2
        
        print(f"VALIDATED COUPLING: {source_name} -> {target_name}")
        print(f"Interference Load: {interference:.4f}x (Matched Substrates)")
        print("-" * 65)
        
        for pulse in range(1, 6):
            # Tension increment (0.1% normalized step)
            delta_t = (flux_magnitude * interference) * 0.01
            self.active_tensions[target_name] += delta_t
            
            t_current = self.active_tensions[target_name]
            status = "STABLE" if t_current < 0.7 else "TANGLE WARNING"
            print(f"PULSE {pulse:02} | TENSION: {t_current:.4f} | {status}")

if __name__ == "__main__":
    bridge = ValidatedBridge()
    bridge.run_safe_flux('finance_module', 'macroeconomics')
