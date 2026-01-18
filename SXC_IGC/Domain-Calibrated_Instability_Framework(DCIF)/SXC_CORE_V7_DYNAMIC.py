import time
from datetime import datetime

class DynamicResilienceEngine:
    def __init__(self):
        # Parameters with established Beta/Gamma calibration
        self.modules = {
            'social_module':  {'E': 0.45, 'F': 0.8, 'T': 0.0, 'beta': 3.448, 'gamma': 0.7},
            'urban_module':   {'E': 0.15, 'F': 0.8, 'T': 0.0, 'beta': 3.383, 'gamma': 0.6},
            'finance_module': {'E': 0.30, 'F': 0.8, 'T': 0.0, 'beta': 3.500, 'gamma': 0.8}
        }
        self.coupling = {
            ('urban_module', 'social_module'): 0.05,
            ('finance_module', 'social_module'): 0.03
        }
        self.phase = "NOMINAL"
        self.dt = 0.1  # Time step for integration

    def run(self, cycles=100):
        print(f"{'TIME':<10} | {'MAX-T':<8} | {'PHASE':<12} | {'STATE'}")
        print("-" * 50)
        
        for i in range(cycles):
            new_tensions = {}
            is_defending = (self.phase == "FIREWALL")
            
            # 1. Differential Tension Update: dT = (Inflow - Outflow)
            for name, m in self.modules.items():
                # Inflow: Excitation * Beta
                inflow = m['E'] * m['beta']
                
                # Outflow: Gamma * Friction * (Boosted if Defending)
                damping_multiplier = 2.5 if is_defending else 1.0
                outflow = m['gamma'] * m['F'] * m['T'] * damping_multiplier
                
                # Integration: T_new = T_old + (dT * dt)
                dT = inflow - outflow
                new_tensions[name] = max(0.0, m['T'] + (dT * self.dt))
            
            # 2. Dynamic Coupling Propagation
            for (src, tgt), w in self.coupling.items():
                c_mod = 0.1 if is_defending else 1.0
                new_tensions[tgt] += new_tensions[src] * w * c_mod

            # Update actual module states
            for name in self.modules:
                self.modules[name]['T'] = min(3.0, new_tensions[name])

            # 3. Global Hysteresis Phase Logic
            max_T = max(m['T'] for m in self.modules.values())
            
            if max_T >= 1.0:
                self.phase = "FIREWALL"
            elif self.phase == "FIREWALL" and max_T < 0.4:
                self.phase = "NOMINAL"
            elif self.phase != "FIREWALL" and max_T >= 0.4:
                self.phase = "PREDICTIVE"
            elif self.phase != "FIREWALL" and max_T < 0.4:
                self.phase = "NOMINAL"

            # 4. Simulate Environmental Decay (Shock passes after 40 cycles)
            if i > 40:
                for name in self.modules:
                    self.modules[name]['E'] *= 0.92

            if i % 5 == 0: # Log every 5th cycle to see progression
                print(f"{datetime.now().strftime('%H:%M:%S')} | {max_T:>8.4f} | {self.phase:<12} | E_avg: {sum(m['E'] for m in self.modules.values())/3:.3f}")
            
            time.sleep(self.dt)

if __name__ == "__main__":
    DynamicResilienceEngine().run()
