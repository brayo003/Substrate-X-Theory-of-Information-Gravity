import time
from datetime import datetime

class StressEngine:
    def __init__(self):
        self.modules = {
            'social_module': {'E': 0.45, 'F': 0.8, 'T': 0.0, 'beta': 3.448, 'gamma': 0.7, 'crisis': False},
            'urban_module':  {'E': 0.15, 'F': 0.8, 'T': 0.0, 'beta': 3.383, 'gamma': 0.6, 'crisis': False},
            'finance_module':{'E': 0.30, 'F': 0.8, 'T': 0.0, 'beta': 3.500, 'gamma': 0.8, 'crisis': False}
        }
        self.coupling = {
            ('urban_module', 'social_module'): 0.05, 
            ('finance_module', 'social_module'): 0.03
        }
        self.last_phase = None

    def run(self):
        while True:
            new_tensions = {}
            # 1. Base Tension Calculation
            for name, m in self.modules.items():
                damping = 1.5 if m['crisis'] else 1.0
                new_tensions[name] = max(0.0, (m['beta'] * m['E']) - (m['gamma'] * m['F'] * damping))
            
            # 2. Add Coupling
            for (src, tgt), w in self.coupling.items():
                new_tensions[tgt] += self.modules[src]['T'] * (w * (0.3 if self.modules[src]['crisis'] else 1.0))
            
            # 3. Update State
            for name in self.modules:
                self.modules[name]['T'] = new_tensions[name]
                self.modules[name]['crisis'] = True if self.modules[name]['T'] >= 1.0 else False

            # 4. Global Monitoring
            max_T = max(m['T'] for m in self.modules.values())
            phase = "FIREWALL" if max_T >= 1.0 else "PREDICTIVE" if max_T >= 0.4 else "NOMINAL"
            
            if phase != self.last_phase:
                print(f"{datetime.now().strftime('%H:%M:%S')} | {max_T:.4f} | {phase}", flush=True)
                self.last_phase = phase
            time.sleep(0.1)

if __name__ == "__main__":
    engine = StressEngine()
    engine.run()
