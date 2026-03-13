import pandas as pd

class SXCOmegaEngineFixed:
    def __init__(self, gamma=0.08):
        self.t_sys = 0.0
        self.gamma = gamma

    def step(self, flux):
        # Information Gravity: Injection + Current Tension - Decay
        self.t_sys = flux + (self.t_sys * (1 - self.gamma))
        
        # Logic Fix: State Transition must be absolute
        if self.t_sys > 1.0:
            return self.t_sys, "FIREWALL"
        return self.t_sys, "NOMINAL"

SIGMA = 5e-3 
engine = SXCOmegaEngineFixed(gamma=0.08) 
data = pd.read_csv('entropy_flux.csv', names=['flux'], header=0)

print(f"{'Step':<10} | {'Int Flux':<12} | {'T_sys':<12} | {'State'}")
print("-" * 55)

last_val = None
for i, row in data.iterrows():
    try:
        val = float(row['flux'])
    except: continue
    if last_val is None:
        last_val = val
        continue
    
    diff = val - last_val
    t_sys, phase = engine.step(diff * SIGMA)
    last_val = val
    
    if i % 10 == 0 or phase == "FIREWALL" and i < 20: # Show the transition clearly
        state_label = f"*** {phase} ***" if phase == "FIREWALL" else phase
        print(f"{i:<10} | {diff:<12.0f} | {t_sys:<12.4f} | {state_label}")
