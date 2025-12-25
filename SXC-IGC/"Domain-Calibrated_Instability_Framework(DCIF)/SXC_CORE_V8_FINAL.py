import time
from datetime import datetime

class ActiveDefenseEngine:
    def __init__(self):
        # Established Beta/Gamma calibration
        self.modules = {
            'social_module':  {'E': 0.10, 'F': 0.8, 'T': 0.0, 'beta': 3.448, 'gamma': 0.75},
            'urban_module':   {'E': 0.55, 'F': 0.8, 'T': 0.0, 'beta': 3.383, 'gamma': 0.60},
            'finance_module': {'E': 0.45, 'F': 0.8, 'T': 0.0, 'beta': 3.500, 'gamma': 0.80}
        }
        # Coupling weights (Flux-calibrated)
        self.coupling = {
            ('urban_module', 'social_module'): 0.008,
            ('finance_module', 'social_module'): 0.005,
            ('social_module', 'finance_module'): 0.002 # Back-propagation
        }
        self.phase = "NOMINAL"
        self.dt = 0.05 # Increased fidelity

    def run(self, cycles=200):
        print(f"{'TIMESTAMP':<10} | {'MAX-T':<8} | {'PHASE':<12} | {'SOC-T':<8}")
        print("-" * 50)
        
        for i in range(cycles):
            new_tensions = {}
            is_defending = (self.phase == "FIREWALL")
            
            # 1. State Integration (dT/dt)
            for name, m in self.modules.items():
                # Dynamic Friction adjustment based on Phase
                eff_gamma = m['gamma'] * (2.2 if is_defending else 1.0)
                
                inflow = m['E'] * m['beta']
                outflow = eff_gamma * m['F'] * m['T']
                
                dT = inflow - outflow
                new_tensions[name] = max(0.0, m['T'] + (dT * self.dt))
            
            # 2. Flux Coupling
            for (src, tgt), w in self.coupling.items():
                # Non-linear acceleration when src T > 1.0
                accel = 1.5 if self.modules[src]['T'] > 1.0 else 1.0
                new_tensions[tgt] += (self.modules[src]['T'] * w * accel)

            # 3. Apply Updates
            for name in self.modules:
                self.modules[name]['T'] = min(5.0, new_tensions[name])

            # 4. Global Hysteresis Logic (Schmitt Trigger)
            max_T = max(m['T'] for m in self.modules.values())
            if max_T >= 1.0:
                self.phase = "FIREWALL"
            elif self.phase == "FIREWALL" and max_T < 0.4:
                self.phase = "NOMINAL"
            elif self.phase != "FIREWALL" and max_T >= 0.4:
                self.phase = "PREDICTIVE"

            if i % 10 == 0:
                print(f"{datetime.now().strftime('%H:%M:%S')} | {max_T:>8.4f} | {self.phase:<12} | {self.modules['social_module']['T']:>7.4f}")
            
            # Environmental Decay Simulation (After cycle 100)
            if i > 100:
                for name in self.modules:
                    self.modules[name]['E'] *= 0.95

            time.sleep(0.02)

if __name__ == "__main__":
    ActiveDefenseEngine().run()
