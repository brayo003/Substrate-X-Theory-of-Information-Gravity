import json
import time
from datetime import datetime

class ProductionResilienceEngine:
    def __init__(self):
        # Module-specific coefficients (Calibrated Beta/Gamma)
        self.modules = {
            'social_module': {'E': 0.45, 'F': 0.8, 'T': 0.0, 'beta': 3.448, 'gamma': 0.7, 'crisis': False},
            'urban_module':  {'E': 0.15, 'F': 0.8, 'T': 0.0, 'beta': 3.383, 'gamma': 0.6, 'crisis': False},
            'finance_module':{'E': 0.30, 'F': 0.8, 'T': 0.0, 'beta': 3.500, 'gamma': 0.8, 'crisis': False},
            'seismic_module':{'E': 0.15, 'F': 0.9, 'T': 0.0, 'beta': 1.000, 'gamma': 0.5, 'crisis': False}
        }
        
        # Completed Coupling Matrix: Source -> Target : Strength
        self.coupling = {
            ('urban_module', 'social_module'): 0.05,
            ('finance_module', 'social_module'): 0.03,
            ('seismic_module', 'urban_module'): 0.02,
            ('social_module', 'finance_module'): 0.01 
        }
        
        self.last_phase = None
        self.recovery_window = 10
        self.recovery_counters = {m: 0 for m in self.modules}

    def compute_vector_tensions(self):
        new_tensions = {}
        # 1. Internal Substrate Calculation
        for name, m in self.modules.items():
            # Apply Adaptive Damping if module is in recovery
            damping_mod = 1.5 if m['crisis'] else 1.0
            new_tensions[name] = max(0.0, (m['beta'] * m['E']) - (m['gamma'] * m['F'] * damping_mod))
        
        # 2. Coupled Entropy Distribution
        for (src, tgt), weight in self.coupling.items():
            # Apply Load Shedding if source is unstable
            coupling_mod = 0.3 if self.modules[src]['crisis'] else 1.0
            new_tensions[tgt] += self.modules[src]['T'] * (weight * coupling_mod)
            
        # 3. State Update & Hysteresis Logic
        for name in self.modules:
            self.modules[name]['T'] = min(3.0, new_tensions[name])
            if self.modules[name]['T'] >= 1.0:
                self.modules[name]['crisis'] = True
                self.recovery_counters[name] = self.recovery_window
            elif self.recovery_counters[name] > 0:
                self.recovery_counters[name] -= 1
            else:
                self.modules[name]['crisis'] = False
        
        # 4. Critical Path Detection (Max-T)
        return max(m['T'] for m in self.modules.values())

    def run_cycle(self, live_data):
        for m, val in live_data.items():
            if m in self.modules: self.modules[m]['E'] = val
            
        max_T = self.compute_vector_tensions()
        
        # Threshold Logic
        if max_T >= 1.0: current_phase = "FIREWALL"
        elif max_T >= 0.4: current_phase = "PREDICTIVE"
        else: current_phase = "NOMINAL"
        
        action = "DEFENSE_ACTIVE: SHEDDING_LOAD" if current_phase == "FIREWALL" else "MONITORING: NOMINAL"
        
        # State-Change Logging Optimization
        log_entry = None
        if current_phase != self.last_phase:
            log_entry = (max_T, current_phase, action)
            self.last_phase = current_phase
            
        return log_entry

if __name__ == "__main__":
    engine = ProductionResilienceEngine()
    live_data = {'social_module': 0.45, 'urban_module': 0.15, 'finance_module': 0.3, 'seismic_module': 0.15}
    
    print(f"{'TIME':<10} | {'MAX-T':<8} | {'PHASE':<12} | {'ACTION'}")
    print("-" * 65)
    
    for cycle in range(25):
        ts = datetime.now().strftime("%H:%M:%S")
        result = engine.run_cycle(live_data)
        
        if result:
            max_t, phase, action = result
            print(f"{ts:<10} | {max_t:>8.4f} | {phase:<12} | {action}")
        
        # Simulate Shock Decay during Firewall
        if engine.last_phase == "FIREWALL":
            live_data['social_module'] *= 0.85
        time.sleep(0.1)
