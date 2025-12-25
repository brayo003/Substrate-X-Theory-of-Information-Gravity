import time
from datetime import datetime

class FluxEngine:
    def __init__(self):
        self.modules = {
            'social_module':  {'E': 0.00, 'F': 0.8, 'T': 0.0, 'beta': 3.448, 'gamma': 0.75}, 
            'urban_module':   {'E': 0.60, 'F': 0.8, 'T': 0.0, 'beta': 3.383, 'gamma': 0.60},
            'finance_module': {'E': 0.50, 'F': 0.8, 'T': 0.0, 'beta': 3.500, 'gamma': 0.80}
        }
        # Scaled for 0.1s integration steps (Divided by 10)
        self.coupling = {
            ('urban_module', 'social_module'): 0.005, 
            ('finance_module', 'social_module'): 0.003
        }
        self.dt = 0.1

    def run(self, cycles=50):
        print(f"{'TIME':<10} | {'URBAN-T':<8} | {'FIN-T':<8} | {'SOC-T (COUPLED)':<15}")
        print("-" * 60)
        for i in range(cycles):
            new_tensions = {}
            # 1. Internal integration
            for name, m in self.modules.items():
                inflow = m['E'] * m['beta']
                outflow = m['gamma'] * m['F'] * m['T']
                new_tensions[name] = max(0.0, m['T'] + (inflow - outflow) * self.dt)
            
            # 2. Flux coupling (Pressure based)
            for (src, tgt), w in self.coupling.items():
                # Target gains a percentage of Source's current tension
                new_tensions[tgt] += (self.modules[src]['T'] * w)

            for name in self.modules:
                self.modules[name]['T'] = min(5.0, new_tensions[name])

            if i % 5 == 0:
                print(f"{datetime.now().strftime('%H:%M:%S')} | "
                      f"{self.modules['urban_module']['T']:>7.4f} | "
                      f"{self.modules['finance_module']['T']:>7.4f} | "
                      f"{self.modules['social_module']['T']:>14.4f}")
            time.sleep(0.01)

if __name__ == "__main__":
    FluxEngine().run()
