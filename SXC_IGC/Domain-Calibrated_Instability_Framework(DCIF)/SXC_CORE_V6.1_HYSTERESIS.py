import time
from datetime import datetime

class HysteresisEngine:
    def __init__(self):
        # Initial Parameters (Sustained High Excitation)
        self.modules = {
            'social_module': {'E': 0.45, 'F': 0.8, 'T': 0.0, 'beta': 3.448, 'gamma': 0.7},
            'urban_module':  {'E': 0.15, 'F': 0.8, 'T': 0.0, 'beta': 3.383, 'gamma': 0.6},
            'finance_module':{'E': 0.30, 'F': 0.8, 'T': 0.0, 'beta': 3.500, 'gamma': 0.8}
        }
        self.coupling = {
            ('urban_module', 'social_module'): 0.05, 
            ('finance_module', 'social_module'): 0.03
        }
        self.phase = "NOMINAL"

    def run(self):
        while True:
            new_tensions = {}
            # Active Defense persistence check
            is_defending = (self.phase == "FIREWALL")
            
            # 1. Base Tension with Persistent Damping
            for name, m in self.modules.items():
                damping = 1.8 if is_defending else 1.0 # Increased Damping persistence
                new_tensions[name] = max(0.0, (m['beta'] * m['E']) - (m['gamma'] * m['F'] * damping))
            
            # 2. Coupled Loads
            for (src, tgt), w in self.coupling.items():
                c_mod = 0.2 if is_defending else 1.0 # Drastic load shedding
                new_tensions[tgt] += (new_tensions[src] * w * c_mod)
            
            for name in self.modules:
                self.modules[name]['T'] = new_tensions[name]

            max_T = max(m['T'] for m in self.modules.values())
            
            # 3. SCHMITT TRIGGER LOGIC
            # If we hit 1.0, enter FIREWALL
            if max_T >= 1.0:
                self.phase = "FIREWALL"
            # If in FIREWALL, stay there until we drop below 0.4
            elif is_defending and max_T > 0.4:
                self.phase = "FIREWALL"
            # Otherwise, follow standard progression
            elif max_T >= 0.4:
                self.phase = "PREDICTIVE"
            else:
                self.phase = "NOMINAL"
            
            # Log all cycles for stability verification
            print(f"{datetime.now().strftime('%H:%M:%S')} | {max_T:.4f} | {self.phase}", flush=True)
            time.sleep(0.1)

if __name__ == "__main__":
    HysteresisEngine().run()
