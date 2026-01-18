import json
import time
import os

def load_coeff(m):
    p = f"./dcif_modules/{m}/coefficients.json"
    if not os.path.exists(p): p = f"./dcif_modules/Viral_Evolution_Module/coefficients.json"
    with open(p, 'r') as f: return json.load(f)['coefficients']

class HybridEngine:
    def __init__(self):
        self.base_coupling = 0.05
        self.coupling = {('urban_module', 'social_module'): 0.05}
        self.state = {m: {'E': 0.1, 'F': 0.8, 'T': 0.0} for m in ['seismic_module', 'urban_module', 'viral_evolution', 'social_module', 'finance_module']}

    def compute(self, live_E):
        # Update Excitation from Live State
        for m, val in live_E.items():
            if m in self.state: self.state[m]['E'] = val
        
        # Physics & Erosion
        v_c = load_coeff('viral_evolution')
        erosion = max(0.1, 1.0 - ((v_c['beta'] * self.state['viral_evolution']['E']) - (v_c['gamma'] * self.state['viral_evolution']['F'])))
        
        # Hybrid Phase Logic
        phase = "NOMINAL"
        if 0.4 < self.state['urban_module']['T'] <= 0.7:
            self.coupling[('urban_module', 'social_module')] = self.base_coupling * 0.9
            phase = "PREDICTIVE"
        elif self.state['urban_module']['T'] > 0.7:
            self.coupling[('urban_module', 'social_module')] = self.base_coupling * 0.5
            phase = "FIREWALL"

        # Update Tension
        for m in self.state:
            if m == 'viral_evolution': continue
            c = load_coeff(m)
            self.state[m]['T'] = (c['beta'] * self.state[m]['E']) - (c['gamma'] * (self.state[m]['F'] * erosion))
        
        # Propagation
        self.state['urban_module']['E'] += self.state['seismic_module']['T'] * 0.02
        self.state['social_module']['E'] += (self.state['urban_module']['T'] * self.coupling[('urban_module', 'social_module')])
        
        return self.state['social_module']['T'], phase

if __name__ == "__main__":
    engine = HybridEngine()
    print(f"{'TIME':<10} | {'SOCIAL-T':<10} | {'PHASE':<12} | {'STATUS'}")
    print("-" * 50)
    
    while True:
        if os.path.exists("current_live_state.json"):
            with open("current_live_state.json", 'r') as f:
                live_E = json.load(f)
            
            soc_T, phase = engine.compute(live_E)
            status = "⚠️ WARNING" if soc_T > 0.6 else "✅ STABLE"
            if phase == "FIREWALL": status = "🚨 CRITICAL"
            
            ts = time.strftime("%H:%M:%S")
            print(f"{ts:<10} | {soc_T:>10.4f} | {phase:<12} | {status}")
        
        time.sleep(5)
