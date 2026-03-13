import pandas as pd
from SXC_V12_Master_Controller import SXCV12Master

class ParallelShield(SXCV12Master):
    def __init__(self):
        super().__init__()
        self.intervention_count = 0

    def step_simulation(self, raw_flux_a=1.0, raw_flux_b=1.0):
        # Parallel Links
        links = [
            ("cybersecurity", "telecom"), 
            ("finance_module", "logistics")
        ]
        
        print(f"{'ACTIVE LINK':<30} | {'TENSION':<10} | {'ACTION'}")
        print("-" * 65)

        for i, (src, tgt) in enumerate(links):
            flux = raw_flux_a if i == 0 else raw_flux_b
            
            # Execute through V12 Master (Transformer Logic)
            result = self.execute_bridge(src, tgt, raw_flux=flux)
            
            t_curr = result['current_tension']
            action = "FLOWING"
            
            # Intervention Layer (Dashboard Logic)
            if t_curr > 0.7:
                self.tension_registry[tgt] *= 0.8  # The Shield
                action = "SHIELD ACTIVE"
                self.intervention_count += 1
            
            print(f"{result['link']:<30} | {t_curr:.4f} | {action}")

if __name__ == "__main__":
    shield = ParallelShield()
    
    for pulse in range(1, 11):
        print(f"\n[PULSE {pulse:02}] GLOBAL FLUX UPDATE")
        # Simulating a "Bursty" event: High Cyber pressure, Standard Finance pressure
        shield.step_simulation(raw_flux_a=1.5, raw_flux_b=1.0)
