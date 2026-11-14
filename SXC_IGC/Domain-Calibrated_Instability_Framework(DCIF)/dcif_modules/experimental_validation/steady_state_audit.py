import pandas as pd
from SXC_V12_Master_Controller import SXCV12Master

class SteadyStateEngine(SXCV12Master):
    def run_equilibrium_test(self, cycles=20):
        links = [
            ("finance_module", "macroeconomics"),
            ("finance_module", "logistics"),
            ("cybersecurity", "telecom")
        ]
        
        print(f"{'LINK':<30} | {'IN-FLUX':<10} | {'LEAK (γ)':<10} | {'NET Δ'}")
        print("-" * 70)

        for src, tgt in links:
            src_data = self.df[self.df['domain'] == src].iloc[0]
            tgt_data = self.df[self.df['domain'] == tgt].iloc[0]
            
            # 1. Calculate Transformer Output
            interference = (src_data['gamma'] / tgt_data['gamma']) ** 2
            transformed_flux = 1.0 / interference
            
            # 2. Compare against Natural Dissipation (Gamma)
            # We normalize gamma to the same pulse scale (e.g., gamma/100)
            leakage = tgt_data['gamma'] / 10.0 
            net_change = transformed_flux - leakage
            
            state = "HEATING" if net_change > 0 else "COOL/STEADY"
            
            print(f"{src[:12]}->{tgt[:12]:<15} | {transformed_flux:.4f}   | {leakage:.4f}   | {net_change:+.4f} ({state})")

if __name__ == "__main__":
    engine = SteadyStateEngine()
    engine.run_equilibrium_test()
