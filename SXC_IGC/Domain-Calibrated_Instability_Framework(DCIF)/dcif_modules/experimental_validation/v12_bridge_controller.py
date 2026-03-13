import pandas as pd
import numpy as np

class V12BridgeController:
    def __init__(self, domain_file='domain_scales.csv'):
        self.df = pd.read_csv(domain_file)
        self.k_v12 = 1.20397  
        self.active_tensions = {row['domain']: 0.0 for _, row in self.df.iterrows()}

    def run_adaptive_test(self, source_name, target_name, flux_magnitude, steps=10):
        src = self.df[self.df['domain'] == source_name].iloc[0]
        tgt = self.df[self.df['domain'] == target_name].iloc[0]
        
        interference = (src['gamma'] / tgt['gamma']) ** 2
        
        print(f"ADAPTIVE V12 TEST: {source_name} -> {target_name}")
        print(f"Interference Load: {interference:.2f}x")
        print("-" * 65)
        
        for i in range(1, steps + 1):
            current_t = self.active_tensions[target_name]
            
            # ADAPTIVE BRAKE: Brake = Interference Ratio
            # This cancels the quadratic heat precisely.
            if current_t > 0.7:
                brake = interference 
                status = f"SHIELD ACTIVE (Brake: {brake:.2f}x)"
            else:
                brake = 1.0
                status = "NOMINAL"
            
            # Tension Increment: (Flux * Interference) / Brake
            delta_t = (flux_magnitude * interference / brake) * 0.001
            self.active_tensions[target_name] += delta_t
            
            print(f"Step {i:02} | Tension: {self.active_tensions[target_name]:.4f} | {status}")
            
            if self.active_tensions[target_name] >= 1.0:
                print("!!! GHOST SNAP: SHIELD OVERWHELMED !!!")
                break

if __name__ == "__main__":
    bridge = V12BridgeController()
    bridge.run_adaptive_test('macroeconomics', 'logistics', flux_magnitude=1.0, steps=20)
