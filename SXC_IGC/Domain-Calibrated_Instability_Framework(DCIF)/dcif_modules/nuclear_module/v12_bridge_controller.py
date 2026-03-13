class SXCOmegaEngine:
    def __init__(self, gamma=0.5):
        self.T_sys = 0.0
        self.gamma = gamma
        self.history = []

    def step(self, inflow, dt=1.0):
        # Memory Logic: Tension accumulates based on inflow minus a decay (outflow)
        # If inflow stops, T_sys doesn't hit 0 immediately (The Memory Effect)
        decay = self.T_sys * 0.1 
        self.T_sys += (inflow - decay) * dt
        
        # Ensure Tension doesn't go negative
        self.T_sys = max(0, self.T_sys)
        
        # Determine Regime
        phase = "NOMINAL" if self.T_sys < 70 else "FIREWALL"
        return self.T_sys, phase

def v12_adaptive_controller(current_tension, gamma, domain_name):
    K_DISASTER, SHATTER_POINT, WARNING_THRESHOLD = 0.780, 1.0, 0.7
    time_to_death = (SHATTER_POINT - (current_tension/100)) * (K_DISASTER / gamma)
    print(f"--- V12 BRIDGE STATUS: {domain_name} ---")
    print(f"Tension: {current_tension:.2f} | Time to Shatter: {time_to_death:.4f}")
