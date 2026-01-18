import numpy as np

class SXCOmegaEngine:
    def __init__(self, beta=3.5, gamma=0.8):
        self.T_sys = 0.0
        self.phase = "NOMINAL"
        self.gamma_max = gamma
        self.gamma = self.gamma_max
        self.beta = beta
        self.dt = 0.05
        self.decay_rate = 0.0005 

    def excitation_flux(self, signal):
        # Maps biological variability to Information-Gravity flux
        if signal < 45:
            return 1 - np.exp(-signal / 40.0)
        return 0.675 + ((signal - 45.0) / 20.0)

    def step(self, signal):
        # 1. Decay the regulatory coefficient (gamma)
        self.gamma *= (1 - self.decay_rate)
        
        # 2. Compute inflow/outflow
        E = self.excitation_flux(signal)
        gamma_eff = 2.2 if self.phase == "FIREWALL" else 1.0
        inflow = E * self.beta
        outflow = gamma_eff * self.gamma * self.T_sys
        
        # 3. Update System Tension (T_sys)
        self.T_sys += (inflow - outflow) * self.dt
        
        # 4. Phase Transition Logic
        if self.T_sys > 1.0:
            self.phase = "FIREWALL"
        elif self.phase == "FIREWALL" and self.T_sys < 0.4:
            self.phase = "NOMINAL"
            
        return self.T_sys, self.phase
