import numpy as np

class SXCOmegaEngine:
    def __init__(self):
        self.T_sys = 0.0
        self.phase = "NOMINAL"
        self.gamma = 0.8
        self.beta = 3.5
        self.dt = 0.05
        
    def step(self, signal):
        E = 1 - np.exp(-signal / 40.0) if signal < 45 else 0.675 + ((signal-45)/20)
        gamma_eff = 2.2 if self.phase == "FIREWALL" else 1.0
        self.T_sys += (E * self.beta - gamma_eff * self.gamma * self.T_sys) * self.dt
        if self.T_sys > 1.0: self.phase = "FIREWALL"
        elif self.phase == "FIREWALL" and self.T_sys < 0.4: self.phase = "NOMINAL"
        return self.T_sys

def run_stress():
    print("--- [VALIDATION] Omega-Saturation Signal Stress ---")
    engine = SXCOmegaEngine()
    signals = [10, 30, 60, 90] # Increasing vacuum flux
    for s in signals:
        for _ in range(200):
            t_val = engine.step(s)
        print(f"Signal {s} | Final Tension: {t_val:.4f} | Phase: {engine.phase}")

if __name__ == "__main__":
    run_stress()
