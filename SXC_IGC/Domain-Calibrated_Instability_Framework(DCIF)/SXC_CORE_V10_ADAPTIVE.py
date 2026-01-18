import time
import random
from datetime import datetime

class AdaptiveDefenseEngine:
    def __init__(self):
        self.modules = {
            'social_module':  {'E': 0.1, 'F': 0.8, 'T': 0.0, 'beta': 3.448, 'gamma': 0.75},
            'urban_module':   {'E': 0.1, 'F': 0.8, 'T': 0.0, 'beta': 3.383, 'gamma': 0.60},
            'finance_module': {'E': 0.1, 'F': 0.8, 'T': 0.0, 'beta': 3.500, 'gamma': 0.80}
        }
        self.coupling = {
            ('urban_module', 'social_module'): 0.008,
            ('finance_module', 'social_module'): 0.005,
            ('social_module', 'finance_module'): 0.002
        }
        self.phase = "NOMINAL"
        self.dt = 0.05
        self.vix_mock = 18.0

    def fetch_live_signals(self):
        self.vix_mock += random.uniform(-0.5, 1.2) # Faster drift for stress test
        return {
            'finance_E': min(1.0, self.vix_mock / 40.0),
            'urban_E': random.uniform(0.1, 0.4),
            'social_E': 0.05
        }

    def run(self, cycles=500):
        print(f"TIMESTAMP | MAX-T | PHASE | VIX-SIG")
        print("-" * 50)
        for i in range(cycles):
            sig = self.fetch_live_signals()
            is_defending = (self.phase == "FIREWALL")
            
            # Adaptive Gamma calculation
            vix_pressure = max(0, (self.vix_mock - 30) / 50.0)
            defense_mult = 2.2 + vix_pressure if is_defending else 1.0
            
            new_tensions = {}
            for name, m in self.modules.items():
                if name == 'finance_module': m['E'] = sig['finance_E']
                if name == 'urban_module':   m['E'] = sig['urban_E']
                if name == 'social_module':  m['E'] = sig['social_E']

                inflow = m['E'] * m['beta']
                outflow = (m['gamma'] * defense_mult) * m['F'] * m['T']
                new_tensions[name] = max(0.0, m['T'] + (inflow - outflow) * self.dt)
            
            for (src, tgt), w in self.coupling.items():
                accel = 1.5 if self.modules[src]['T'] > 1.0 else 1.0
                new_tensions[tgt] += (self.modules[src]['T'] * w * accel)

            for name in self.modules:
                self.modules[name]['T'] = min(5.0, new_tensions[name])

            max_T = max(m['T'] for m in self.modules.values())
            
            # Hysteresis
            if max_T >= 1.0: self.phase = "FIREWALL"
            elif self.phase == "FIREWALL" and max_T < 0.4: self.phase = "NOMINAL"
            elif self.phase != "FIREWALL" and max_T >= 0.4: self.phase = "PREDICTIVE"

            if i % 10 == 0:
                print(f"{datetime.now().strftime('%H:%M:%S')} | {max_T:>8.4f} | {self.phase:<12} | {self.vix_mock:>7.2f}", flush=True)
            time.sleep(0.02)

if __name__ == "__main__":
    AdaptiveDefenseEngine().run()
