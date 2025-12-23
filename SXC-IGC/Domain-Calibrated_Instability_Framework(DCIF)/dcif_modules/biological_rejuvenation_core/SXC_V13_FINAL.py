import numpy as np

class SXCUnifiedEngine:
    """
    SXC_V13: The Unified Reality Protocol.
    Merges physics, entropy tax, and phase-state longevity.
    """
    def __init__(self):
        self.T_sys = 0.0
        self.phase = "NOMINAL"
        self.gamma_max = 0.8
        self.gamma = self.gamma_max
        self.integrity = 1.0       # 1.0 = Perfect Substrate (Birth/Inception)
        self.beta = 3.5
        self.dt = 0.05
        self.cost_per_pulse = 0.02 # 2% Physical Tax per Rejuvenation
        
    def step(self, signal):
        # Substrate Decay: As integrity drops, natural aging accelerates
        decay = 0.0001 * (1 + (1 - self.integrity)) 
        self.gamma *= (1 - decay)
        
        # Physics Engine (Inflow vs Outflow)
        E = 1 - np.exp(-signal / 40.0) if signal < 45 else 0.675 + ((signal - 45.0) / 20.0)
        gamma_eff = 2.2 if self.phase == "FIREWALL" else 1.0
        
        inflow = E * self.beta
        outflow = gamma_eff * self.gamma * self.T_sys
        self.T_sys += (inflow - outflow) * self.dt
        
        # Hysteresis Phase Logic
        if self.T_sys > 1.0:
            self.phase = "FIREWALL"
        elif self.phase == "FIREWALL" and self.T_sys < 0.4:
            self.phase = "NOMINAL"
        
        return self.T_sys, self.integrity

    def apply_intervention(self):
        """The 'Deep Clean' Reset: Lowers Tension, Burns Integrity."""
        self.integrity -= self.cost_per_pulse
        self.T_sys *= 0.60 
        # Repair capacity is capped by the current integrity of the substrate
        self.gamma = min(self.gamma_max * self.integrity, self.gamma * 1.15)

if __name__ == "__main__":
    engine = SXCUnifiedEngine()
    lifetimes = 0

    print(f"\n{'LIFE #':<8} | {'INTEGRITY':<12} | {'TENSION':<10} | {'PHASE'}")
    print("-" * 55)

    # Simulation: Run cycles until the substrate hits 10% (Structural Collapse)
    while engine.integrity > 0.1:
        lifetimes += 1
        
        # 1. Active Period: Standard noise (Market trading / Living)
        for _ in range(500):
            engine.step(25.0) 
        
        # 2. Crisis Event: High stress (Market Crash / Severe Illness)
        for _ in range(20):
            engine.step(85.0) 
            
        # 3. The Omega Recovery: 3 consecutive pulses to break the Firewall
        for _ in range(3):
            engine.apply_intervention()
            
        # Log state at the end of each rejuvenation cycle
        print(f"{lifetimes:<8} | {engine.integrity:>12.4f} | {engine.T_sys:>10.4f} | {engine.phase}")

    print("-" * 55)
    print(f"[TERMINATION] Total Sustainable Lifetimes: {lifetimes}")
    print("Deduction: Substrate exhausted. Critical Identity Dissolution reached.")
