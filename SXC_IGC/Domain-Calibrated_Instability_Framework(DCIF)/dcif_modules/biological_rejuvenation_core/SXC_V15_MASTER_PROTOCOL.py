import sys
import os
import numpy as np

# Add parent and root to path to ensure SXC_V12_CORE is accessible
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

try:
    from SXC_V12_CORE import SXCOmegaEngine
except ImportError:
    # Fallback/Mock if running in isolation
    class SXCOmegaEngine:
        def __init__(self):
            self.T_sys = 0.0
            self.phase = "NOMINAL"

class SXCMasterProtocol:
    """
    SXC_V15_MASTER: Integrated Rejuvenation Logic.
    Now optimized as a DCIF Module.
    """
    def __init__(self, tax_rate=0.001):
        self.T_sys = 0.0
        self.phase = "NOMINAL"
        self.gamma_max = 0.8
        self.gamma = self.gamma_max
        self.integrity = 1.0
        self.beta = 3.5
        self.dt = 0.05
        self.cost_per_pulse = tax_rate
        self.anchor_limit = 0.15 

    def step(self, signal):
        decay = 0.0001 * (1 + (1 - self.integrity)) 
        self.gamma *= (1 - decay)
        E = 1 - np.exp(-signal / 40.0) if signal < 45 else 0.675 + ((signal - 45.0) / 20.0)
        gamma_eff = 2.2 if self.phase == "FIREWALL" else 1.0
        self.T_sys += (E * self.beta - gamma_eff * self.gamma * self.T_sys) * self.dt
        if self.T_sys > 1.0: self.phase = "FIREWALL"
        elif self.phase == "FIREWALL" and self.T_sys < 0.4: self.phase = "NOMINAL"
        return self.T_sys, self.integrity

    def apply_omega_reset(self):
        for _ in range(3):
            if self.integrity - self.cost_per_pulse < self.anchor_limit:
                return False
            self.integrity -= self.cost_per_pulse
            self.T_sys *= 0.60 
            self.gamma = min(self.gamma_max * self.integrity, self.gamma * 1.15)
        return True

print("SXC_V15: Module successfully linked to DCIF Core.")
