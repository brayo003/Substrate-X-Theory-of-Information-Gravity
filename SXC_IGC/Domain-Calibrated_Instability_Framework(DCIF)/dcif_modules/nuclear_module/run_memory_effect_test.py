import pandas as pd

class SXCMemoryEngine:
    def __init__(self, gamma=0.05): # Gamma is the 'Annealing' rate
        self.t_sys = 0.0
        self.gamma = gamma

    def step(self, flux):
        # Tension = Flux + (Remaining Tension * (1 - Annealing))
        self.t_sys = flux + (self.t_sys * (1 - self.gamma))
        return self.t_sys

# Total Dose (Fluence) = 1.0 DPA
# Steady: 0.01 DPA per step for 100 steps
# Pulsed: 0.1 DPA per step for 10 steps, with 9 steps of 'Zero' in between

engine_steady = SXCMemoryEngine(gamma=0.02)
engine_pulsed = SXCMemoryEngine(gamma=0.02)

results = []

# Simulate 100 T-intervals
for t in range(100):
    # Steady Dose
    t_steady = engine_steady.step(0.01)
    
    # Pulsed Dose (Every 10th step is a high-flux burst)
    flux_pulsed = 0.1 if t % 10 == 0 else 0.0
    t_pulsed = engine_pulsed.step(flux_pulsed)
    
    results.append((t, t_steady, t_pulsed))

print(f"{'Interval':<10} | {'Steady T_sys':<15} | {'Pulsed T_sys':<15} | {'Delta'}")
print("-" * 60)
for r in results[::10]:
    delta = r[2] - r[1]
    print(f"{r[0]:<10} | {r[1]:<15.4f} | {r[2]:<15.4f} | {delta:<.4f}")

