import time
import random
import numpy as np
from datetime import datetime

class InsightEngine:
    def __init__(self):
        self.modules = {
            'finance_module': {'E': 0.1, 'F': 0.8, 'T': 0.0, 'beta': 3.5, 'gamma': 0.8},
            'social_module':  {'E': 0.1, 'F': 0.8, 'T': 0.0, 'beta': 3.448, 'gamma': 0.75}
        }
        self.phase = "NOMINAL"
        self.dt = 0.05
        self.vix = 18.2

    def run(self, cycles=1000):
        print(f"TIMESTAMP | MAX-T | PHASE | VIX (MARKET LAG) | STATE")
        print("-" * 70)
        
        for i in range(cycles):
            # Simulate the "Momentum Panic" - VIX climbs regardless of T
            self.vix += random.uniform(-0.1, 4.0) 
            
            # Map VIX to Excitation (High sensitivity)
            E_in = 1 - np.exp(-self.vix / 60.0)
            
            is_firewall = (self.phase == "FIREWALL")
            # The "Detection-Control Gap" Multiplier
            # We increase damping only as much as needed to stabilize, not crash T to zero
            gamma_eff = 2.2 if is_firewall else 1.0
            
            # Update Tension
            m = self.modules['finance_module']
            inflow = E_in * m['beta']
            outflow = gamma_eff * m['gamma'] * m['F'] * m['T']
            m['T'] = max(0.0, m['T'] + (inflow - outflow) * self.dt)

            # Phase Check
            if m['T'] >= 1.0: self.phase = "FIREWALL"
            elif self.phase == "FIREWALL" and m['T'] < 0.4: self.phase = "NOMINAL"

            if i % 10 == 0:
                # Extraordinary Detection logic:
                status = "STABILIZING" if (is_firewall and m['T'] < 2.2) else "DETECTING"
                print(f"{datetime.now().strftime('%H:%M:%S')} | {m['T']:>8.4f} | {self.phase:<12} | {self.vix:>15.2f} | {status}")
            
            time.sleep(0.02)

if __name__ == "__main__":
    InsightEngine().run()
