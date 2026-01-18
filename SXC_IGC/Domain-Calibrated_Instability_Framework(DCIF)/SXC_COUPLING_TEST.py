import time
from datetime import datetime

class CouplingTestEngine:
    def __init__(self):
        self.modules = {
            'social_module':  {'E': 0.00, 'F': 0.8, 'T': 0.0, 'beta': 3.448, 'gamma': 0.7},
            'urban_module':   {'E': 0.60, 'F': 0.8, 'T': 0.0, 'beta': 3.383, 'gamma': 0.6},
            'finance_module': {'E': 0.50, 'F': 0.8, 'T': 0.0, 'beta': 3.500, 'gamma': 0.8}
        }
        self.coupling = {
            ('urban_module', 'social_module'): 0.05,
            ('finance_module', 'social_module'): 0.03
        }
        self.dt = 0.1

    def run(self, cycles=60):
        print(f"{'TIME':<10} | {'URBAN-T':<8} | {'FIN-T':<8} | {'SOC-T (COUPLED)':<15}")
        print('-'*50)
        for _ in range(cycles):
            # Update uncoupled tensions
            for name, mod in self.modules.items():
                mod['T'] += (mod['E'] * mod['beta'] - mod['T'] * mod['gamma']) * self.dt

            # Apply coupling to social_module
            coupled_T = self.modules['social_module']['T']
            for src, target in self.coupling:
                coupled_T += self.modules[src]['T'] * self.coupling[(src, target)]
            self.modules['social_module']['T'] = coupled_T

            t_str = datetime.now().strftime("%H:%M:%S")
            print(f"{t_str} | {self.modules['urban_module']['T']:<8.4f} | {self.modules['finance_module']['T']:<8.4f} | {self.modules['social_module']['T']:<15.4f}")
            time.sleep(self.dt)

if __name__ == "__main__":
    engine = CouplingTestEngine()
    engine.run(20)
