import numpy as np

class SXCOmegaEngine:
    def __init__(self):
        self.alpha = 1.254
        self.T_sys = 0.0
        self.phase = "NOMINAL"
        self.gamma_max = 0.8
        self.gamma = self.gamma_max
        self.beta = 0.4  # Drastic reduction for high-alpha stability
        self.dt = 0.05
        self.decay_rate = 0.05 
        
    def excitation_flux(self, signal):
        # Sigmoid squash to prevent input-driven divergence
        return 1 / (1 + np.exp(-(signal - 45) / 10))

    def step(self, signal):
        self.gamma *= (1 - self.decay_rate)
        E = self.excitation_flux(signal)
        
        # Alpha scaling applied to outflow resistance
        gamma_eff = (5.5 * self.alpha) if self.phase == "FIREWALL" else self.alpha
        
        inflow = E * self.beta
        outflow = gamma_eff * self.gamma * self.T_sys
        
        # The Delta-T calculation
        self.T_sys += (inflow - outflow) * self.dt
        
        # Hard Physical Limit (The Substrate Bound)
        self.T_sys = np.clip(self.T_sys, 0, 1.5)
        
        if self.T_sys > 1.0:
            self.phase = "FIREWALL"
        elif self.phase == "FIREWALL" and self.T_sys < 0.4:
            self.phase = "NOMINAL"
            
        return self.T_sys, self.phase
