import json
import time
import os
from datetime import datetime

class ActiveDefenseEngine:
    def __init__(self):
        # Calibrated Beta (3.5) and Gamma coefficients
        self.modules = {
            'social_module': {'E': 0.45, 'F': 0.8, 'T': 0.0, 'beta': 3.448, 'gamma': 0.7},
            'urban_module': {'E': 0.15, 'F': 0.8, 'T': 0.0, 'beta': 3.383, 'gamma': 0.6},
            'finance_module': {'E': 0.30, 'F': 0.8, 'T': 0.0, 'beta': 3.5, 'gamma': 0.8},
            'seismic_module': {'E': 0.15, 'F': 0.9, 'T': 0.0, 'beta': 1.0, 'gamma': 0.5}
        }
        
        self.coupling = {
            ('urban_module', 'social_module'): 0.05,
            ('finance_module', 'social_module'): 0.03,
            ('seismic_module', 'urban_module'): 0.02
        }
        
        self.phase = "NOMINAL"
        self.emergency_active = False

    def propagate_tensions(self):
        new_tensions = {}
        # Calculate Base Tensions: T = beta*E - gamma*F
        for name, m in self.modules.items():
            new_tensions[name] = max(0.0, m['beta'] * m['E'] - m['gamma'] * m['F'])
        
        # Apply Coupling
        for (source, target), strength in self.coupling.items():
            new_tensions[target] += self.modules[source]['T'] * strength
        
        for name in self.modules:
            self.modules[name]['T'] = min(3.0, new_tensions[name])
        
        return self.modules['social_module']['T']

    def implement_emergency_protocols(self):
        if self.phase == "FIREWALL":
            # ACTIVE DEFENSE: Decoupling + Damping Boost
            for (source, target) in self.coupling:
                if target == 'social_module':
                    self.coupling[(source, target)] *= 0.3 # 70% decoupling
            
            self.modules['social_module']['F'] = 1.5 # Strategic Damping
            return "🛡️ ACTIVE DEFENSE: SHEDDING LOAD"
        return "📡 MONITORING: NOMINAL"

    def run_cycle(self, live_data):
        for module, value in live_data.items():
            if module in self.modules: self.modules[module]['E'] = value
        
        social_T = self.propagate_tensions()
        
        # Phase Detection
        if social_T >= 1.0: self.phase = "FIREWALL"
        elif social_T >= 0.4: self.phase = "PREDICTIVE"
        else: self.phase = "NOMINAL"
        
        defense_action = self.implement_emergency_protocols()
        return social_T, self.phase, defense_action

if __name__ == "__main__":
    engine = ActiveDefenseEngine()
    live_data = {'seismic_module': 0.15, 'social_module': 0.45, 'finance_module': 0.30, 'urban_module': 0.15}
    
    print(f"{'TIME':<10} | {'SOC-T':<8} | {'PHASE':<12} | {'DEFENSE ACTION'}")
    print("-" * 75)
    
    for cycle in range(10):
        ts = datetime.now().strftime("%H:%M:%S")
        soc_T, phase, defense = engine.run_cycle(live_data)
        
        # Simulation: Decay shock after defenses activate
        if phase == "FIREWALL":
            live_data['social_module'] *= 0.92 
            
        print(f"{ts:<10} | {soc_T:>8.4f} | {phase:<12} | {defense}")
        time.sleep(1)
