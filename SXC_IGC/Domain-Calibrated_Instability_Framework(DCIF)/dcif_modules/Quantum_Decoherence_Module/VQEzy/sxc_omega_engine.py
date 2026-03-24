import numpy as np
import pandas as pd

class SXCOmegaEngine:
    def __init__(self):
        self.T_sys = 0.0
        self.phase = 'NOMINAL'
        self.gamma = 0.8
        self.beta = 3.5
        self.dt = 0.05
        self.decay_rate = 0.0005
    
    def excitation_flux(self, signal):
        if signal < 45:
            return 1 - np.exp(-signal / 40.0)
        return 0.675 + ((signal - 45.0) / 20.0)
    
    def step(self, signal):
        self.gamma *= (1 - self.decay_rate)
        E = self.excitation_flux(signal)
        
        # Phase-aware dampening: Firewall kicks in to dump heat
        gamma_eff = 5.0 if self.phase == 'FIREWALL' else 1.0
        
        inflow = E * self.beta
        outflow = gamma_eff * self.gamma * self.T_sys
        self.T_sys += (inflow - outflow) * self.dt
        
        # State Transition Logic (The Censor)
        if self.T_sys > 1.0:
            self.phase = 'FIREWALL'
        elif self.T_sys < 0.2:
            self.phase = 'NOMINAL'
            
        return self.T_sys, self.phase

# Test against the H2-level signal
engine = SXCOmegaEngine()
results = []
signals = np.linspace(30, 60, 100) # Simulating a VQE optimization run

for s in signals:
    t, p = engine.step(s)
    results.append({'signal': s, 'T_sys': t, 'phase': p})

df = pd.DataFrame(results)
print(f"=== SXC OMEGA ENGINE DIAGNOSTICS ===")
print(f"Final T_sys: {df['T_sys'].iloc[-1]:.4f}")
print(f"FIREWALL proportion: {(df['phase'] == 'FIREWALL').mean():.2%}")
print(f"Max System Stress: {df['T_sys'].max():.4f}")
