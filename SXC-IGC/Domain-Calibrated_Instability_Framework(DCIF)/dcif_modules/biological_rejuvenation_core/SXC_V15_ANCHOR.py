import numpy as np

class SXCAnchorEngine:
    def __init__(self, tax_rate=0.001):
        self.T_sys = 0.0
        self.phase = "NOMINAL"
        self.gamma_max = 0.8
        self.gamma = self.gamma_max
        self.integrity = 1.0
        self.beta = 3.5
        self.dt = 0.05
        self.cost_per_pulse = tax_rate
        self.anchor_limit = 0.15 # Cannot drop below 15% without identity loss

    def step(self, signal):
        decay = 0.0001 * (1 + (1 - self.integrity)) 
        self.gamma *= (1 - decay)
        E = 1 - np.exp(-signal / 40.0) if signal < 45 else 0.675 + ((signal - 45.0) / 20.0)
        gamma_eff = 2.2 if self.phase == "FIREWALL" else 1.0
        self.T_sys += (E * self.beta - gamma_eff * self.gamma * self.T_sys) * self.dt
        if self.T_sys > 1.0: self.phase = "FIREWALL"
        elif self.phase == "FIREWALL" and self.T_sys < 0.4: self.phase = "NOMINAL"
        return self.T_sys, self.integrity

    def apply_intervention(self):
        # The Identity Anchor check
        if self.integrity - self.cost_per_pulse < self.anchor_limit:
            return False # Intervention Blocked: Preservation Priority
        self.integrity -= self.cost_per_pulse
        self.T_sys *= 0.60 
        self.gamma = min(self.gamma_max * self.integrity, self.gamma * 1.15)
        return True

if __name__ == "__main__":
    # Test at the 0.001 Sustainable Rate
    engine = SXCAnchorEngine(tax_rate=0.001)
    for life in range(1, 301):
        # Stress Phase
        for _ in range(500): engine.step(25.0)
        for _ in range(20): engine.step(85.0)
        
        # Recovery Phase
        success = True
        for _ in range(3):
            if not engine.apply_intervention():
                success = False
                break
        
        if not success or engine.phase == "FIREWALL" and engine.T_sys > 2.0:
            print(f"TERMINATED AT LIFE {life}: Identity Anchor Tripped or Systemic Lock.")
            break
        
        if life % 50 == 0:
            print(f"LIFE {life:<4} | Integrity: {engine.integrity:.4f} | Tension: {engine.T_sys:.4f}")
