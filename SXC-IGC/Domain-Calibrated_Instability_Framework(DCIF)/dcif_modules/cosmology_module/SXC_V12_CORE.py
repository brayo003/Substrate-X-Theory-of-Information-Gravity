import numpy as np

class SXCV12Universal:
    def __init__(self):
        # UNIVERSAL CONSTANTS: DYNAMIC INTEGRATION CALIBRATION
        self.V_LIMIT = 108.0   # Global asymptotic limit
        self.K_SAT = 0.55      # Strong Coupling (High 'Grip' at low signal)
        self.BETA = 0.125      # Logarithmic Excitation Drive
        self.GAMMA = 0.045     # Dynamic Dissipation
        
        self.T_sys = 0.0       # START AT ZERO (Natural Accumulation)
        self.last_r = 0.0

    def compute_tension(self, signal, r):
        """
        Dynamic Information Integration:
        Tension builds as a function of radial distance (dr).
        """
        dr = max(r - self.last_r, 0.1)
        self.last_r = r
        
        # Logarithmic Sensitivity: Softens the 'Cusp' problem
        E = np.log1p(signal) 
        
        inflow = E * self.BETA
        outflow = self.GAMMA * self.T_sys
        
        # Integration step based on actual spatial delta
        self.T_sys += (inflow - outflow) * dr
        return self.T_sys

    def get_velocity(self, v_bar, tension):
        # Saturation Law: V_sub = V_lim * (1 - e^(-K*T))
        v_sub = self.V_LIMIT * (1 - np.exp(-self.K_SAT * tension))
        return np.sqrt(v_bar**2 + v_sub**2)
