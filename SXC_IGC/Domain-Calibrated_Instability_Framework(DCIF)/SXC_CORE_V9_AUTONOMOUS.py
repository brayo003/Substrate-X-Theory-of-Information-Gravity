import time
import random
from datetime import datetime

class AutonomousDefenseEngine:
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
        self.vix_mock = 18.0 # Base market volatility

    def fetch_live_signals(self):
        """Mock Ingestor: Simulates external market and urban entropy."""
        self.vix_mock += random.uniform(-0.5, 0.8) # Volatility drift
        network_stress = random.uniform(0.1, 0.4)
        
        return {
            'finance_E': min(1.0, self.vix_mock / 40.0),
            'urban_E': network_stress,
            'social_E': 0.05 # Baseline social excitation
        }

    def run(self, cycles=300):
        print(f"{'TIMESTAMP':<10} | {'MAX-T':<8} | {'PHASE':<12} | {'VIX-SIG':<8}")
        print("-" * 50)
        
        for i in range(cycles):
            signals = self.fetch_live_signals()
            is_defending = (self.phase == "FIREWALL")
            new_tensions = {}

            # 1. Update Inflow via Live Signals & Internal Dynamics
            for name, m in self.modules.items():
                # Map signals to specific module excitation
                if name == 'finance_module': m['E'] = signals['finance_E']
                if name == 'urban_module':   m['E'] = signals['urban_E']
                if name == 'social_module':  m['E'] = signals['social_E']

                eff_gamma = m['gamma'] * (2.2 if is_defending else 1.0)
                inflow = m['E'] * m['beta']
                outflow = eff_gamma * m['F'] * m['T']
                
                new_tensions[name] = max(0.0, m['T'] + (inflow - outflow) * self.dt)
            
            # 2. Flux Coupling with Back-Propagation
            for (src, tgt), w in self.coupling.items():
                accel = 1.5 if self.modules[src]['T'] > 1.0 else 1.0
                new_tensions[tgt] += (self.modules[src]['T'] * w * accel)

            # 3. Apply and Phase-Check (Hysteresis)
            for name in self.modules:
                self.modules[name]['T'] = min(5.0, new_tensions[name])

            max_T = max(m['T'] for m in self.modules.values())
            if max_T >= 1.0:
                self.phase = "FIREWALL"
            elif self.phase == "FIREWALL" and max_T < 0.4:
                self.phase = "NOMINAL"
            elif self.phase != "FIREWALL" and max_T >= 0.4:
                self.phase = "PREDICTIVE"

            if i % 20 == 0:
                print(f"{datetime.now().strftime('%H:%M:%S')} | {max_T:>8.4f} | {self.phase:<12} | {self.vix_mock:>7.2f}")
            
            time.sleep(0.02)

if __name__ == "__main__":
    AutonomousDefenseEngine().run()
