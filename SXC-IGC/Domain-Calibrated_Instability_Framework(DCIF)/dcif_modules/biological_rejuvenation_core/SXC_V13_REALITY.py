import numpy as np

class SXCRealityEngine:
    def __init__(self):
        self.T_sys = 0.0
        self.phase = "NOMINAL"
        self.gamma_max = 0.8
        self.gamma = self.gamma_max
        self.integrity = 1.0  # NEW: Substrate Health (1.0 = perfect)
        self.beta = 3.5
        self.dt = 0.05
        
    def step(self, signal):
        # The 'Aging' of the substrate itself
        decay = 0.0001 * (1 + (1 - self.integrity)) 
        self.gamma *= (1 - decay)
        
        # Physics
        E = 1 - np.exp(-signal / 40.0) if signal < 45 else 0.675 + ((signal - 45.0) / 20.0)
        gamma_eff = 2.2 if self.phase == "FIREWALL" else 1.0
        
        self.T_sys += (E * self.beta - gamma_eff * self.gamma * self.T_sys) * self.dt
        
        # Phase Logic
        if self.T_sys > 1.0: self.phase = "FIREWALL"
        elif self.phase == "FIREWALL" and self.T_sys < 0.4: self.phase = "NOMINAL"
        
        return self.T_sys, self.integrity

    def apply_intervention(self):
        """ The Cost of Rejuvenation """
        cost = 0.02 # Each 'Deep Clean' costs 2% of total substrate life
        self.integrity -= cost
        self.T_sys *= 0.60 
        self.gamma = min(0.8, self.gamma * 1.10) # Partial repair of the 'pipe'
