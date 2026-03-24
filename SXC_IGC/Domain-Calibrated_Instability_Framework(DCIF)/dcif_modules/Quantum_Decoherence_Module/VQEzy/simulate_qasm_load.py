import numpy as np
import pandas as pd

# Using your Toronto Tension values as the "Signal" baseline
toronto_tension = [0.5238, 0.7257, 0.5749, 0.6151, 0.4280]

class SXCOmegaEngine:
    def __init__(self):
        self.T_sys = 0.0
        self.phase = 'NOMINAL'
        self.gamma = 0.8
        self.beta = 8.5  # CRITICAL: We bump Beta to 8.5 to simulate QASM density
        self.dt = 0.05

    def step(self, tension):
        # In QASM, tension is amplified by gate density
        E = 1 - np.exp(-tension * 2.0) 
        gamma_eff = 5.0 if self.phase == 'FIREWALL' else 1.0
        inflow = E * self.beta
        outflow = gamma_eff * self.gamma * self.T_sys
        self.T_sys += (inflow - outflow) * self.dt
        
        if self.T_sys > 1.0: self.phase = 'FIREWALL'
        return self.T_sys, self.phase

engine = SXCOmegaEngine()
print("=== V12 VIRTUAL QASM STRESS TEST (TORONTO SUBSTRATE) ===")
for i, t in enumerate(toronto_tension):
    sys_t, phase = engine.step(t)
    print(f"Qubit {i} | Tension: {t:.4f} | Sys_Stress: {sys_t:.4f} | Status: {phase}")
