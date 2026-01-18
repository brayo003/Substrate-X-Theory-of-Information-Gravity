import json
import time
import os
from datetime import datetime

class EmergencyEngine:
    def __init__(self):
        # Initial State
        self.state = {m: {'E': 0.1, 'F': 0.8, 'T': 0.0} for m in 
                     ['seismic_module', 'urban_module', 'viral_evolution', 
                      'social_module', 'finance_module']}
        
        # DUAL THRESHOLD SYSTEM
        self.THRESHOLDS = {
            'IMMEDIATE_COLLAPSE': 1.0,   
            'FIREWALL': 0.63,            
            'PREDICTIVE': 0.4,           
            'ENTROPY_FIREWALL': 2.0      
        }
        
        self.total_entropy = 0.0
        self.phase_history = []
        self.beta_calibrated = 3.56  # Corrected sensitivity

    def compute(self, live_E):
        for m, val in live_E.items():
            if m in self.state:
                self.state[m]['E'] = val
        
        # INSTANT TENSION CALCULATION (Fast Timescale)
        # Using the calibrated Beta for high-sensitivity detection
        social_T = self.state['social_module']['E'] * self.beta_calibrated 
        
        # CUMULATIVE ENTROPY (Slow Timescale)
        self.total_entropy += social_T * 0.01
        
        # EMERGENCY HIERARCHY
        if social_T >= self.THRESHOLDS['IMMEDIATE_COLLAPSE']:
            phase = "FIREWALL"
            reason = "🚨 COLLAPSE DETECTED (T >= 1.0)"
        elif social_T >= self.THRESHOLDS['FIREWALL']:
            phase = "FIREWALL"
            reason = "🔴 High tension"
        elif social_T >= self.THRESHOLDS['PREDICTIVE']:
            phase = "PREDICTIVE"
            reason = "🟡 Elevated tension"
        else:
            phase = "NOMINAL"
            reason = "🟢 Nominal"
        
        # ENTROPY OVERRIDE
        if self.total_entropy >= self.THRESHOLDS['ENTROPY_FIREWALL'] and phase != "FIREWALL":
            phase = "FIREWALL"
            reason = f"🔴 Cumulative stress ({self.total_entropy:.1f})"
        
        return social_T, phase, reason, self.total_entropy

if __name__ == "__main__":
    engine = EmergencyEngine()
    live_data = {
        'seismic_module': 0.15,
        'social_module': 0.45,  # T = 0.45 * 3.56 = 1.602
        'finance_module': 0.30,
        'viral_evolution': 0.20
    }
    
    print(f"{'TIME':<10} | {'SOC-T':<10} | {'PHASE':<12} | {'REASON':<30} | {'ENTROPY':<10}")
    print("-" * 85)
    
    for cycle in range(5):
        current_time = datetime.now().strftime("%H:%M:%S")
        soc_T, phase, reason, entropy = engine.compute(live_data)
        
        # Terminal formatting for the "MANY" (Impact Visualization)
        color = "\033[91m" if "COLLAPSE" in reason else "\033[93m" if "FIREWALL" in phase else ""
        reset = "\033[0m"
        
        print(f"{current_time:<10} | {soc_T:>10.4f} | {phase:<12} | {color}{reason:<30}{reset} | {entropy:>10.4f}")
        if "COLLAPSE" in reason:
            print("   ⚠️  PROTOCOL: Shedding Urban-Social Coupling... Emergency Damping Active.")
        time.sleep(1)
