import json
import time
import os
import math

def load_coeff(m):
    p = f"./dcif_modules/{m}/coefficients.json"
    if not os.path.exists(p): p = f"./dcif_modules/Viral_Evolution_Module/coefficients.json"
    with open(p, 'r') as f: return json.load(f)['coefficients']

class HybridEngineV2:
    def __init__(self):
        self.base_coupling = 0.05
        self.coupling = {('urban_module', 'social_module'): 0.05}
        self.state = {m: {'E': 0.1, 'F': 0.8, 'T': 0.0} for m in ['seismic_module', 'urban_module', 'viral_evolution', 'social_module', 'finance_module']}
        self.decay_lambda = 0.05 # 5% entropy dissipation per cycle

    def compute(self, live_E):
        # 1. Decay existing excitation before adding new entropy
        for m in self.state:
            self.state[m]['E'] *= math.exp(-self.decay_lambda)

        # 2. Ingest Live Signals
        for m, val in live_E.items():
            if m in self.state: 
                # Signals are additive to current decayed state
                self.state[m]['E'] = max(self.state[m]['E'], val)
        
        # 3. Dynamic Damping (Emergency Mobilization)
        v_c = load_coeff('viral_evolution')
        f_mod = 1.0
        phase = "NOMINAL"
        
        if self.state['urban_module']['T'] > 0.7:
            self.coupling[('urban_module', 'social_module')] = self.base_coupling * 0.5
            f_mod = 1.2 # Mobilize 20% extra damping
            phase = "FIREWALL"
        elif 0.4 < self.state['urban_module']['T'] <= 0.7:
            self.coupling[('urban_module', 'social_module')] = self.base_coupling * 0.9
            phase = "PREDICTIVE"

        # 4. Physics Step
        erosion = max(0.1, 1.0 - ((v_c['beta'] * self.state['viral_evolution']['E']) - (v_c['gamma'] * self.state['viral_evolution']['F'])))
        for m in self.state:
            if m == 'viral_evolution': continue
            c = load_coeff(m)
            # Apply f_mod to Social and Finance specifically
            current_f = self.state[m]['F'] * (f_mod if m in ['social_module', 'finance_module'] else 1.0)
            self.state[m]['T'] = (c['beta'] * self.state[m]['E']) - (c['gamma'] * (current_f * erosion))
        
        # 5. Propagation
        self.state['urban_module']['E'] += self.state['seismic_module']['T'] * 0.02
        self.state['social_module']['E'] += (self.state['urban_module']['T'] * self.coupling[('urban_module', 'social_module')])
        
        return self.state['social_module']['T'], phase

if __name__ == "__main__":
    engine = HybridEngineV2()
    print(f"{'TIME':<10} | {'SOC-T':<10} | {'PHASE':<12} | {'ENTROPY DISK'}")
    print("-" * 55)
    
    while True:
        if os.path.exists("current_live_state.json"):
            with open("current_live_state.json", 'r') as f:
                live_E = json.load(f)
            
            soc_T, phase = engine.compute(live_E)
            ts = time.strftime("%H:%M:%S")
            # Calculate total system excitation for "Disk" metric
            total_e = sum(v['E'] for v in engine.state.values())
            print(f"{ts:<10} | {soc_T:>10.4f} | {phase:<12} | {total_e:>10.4f}")
        
        time.sleep(5)
