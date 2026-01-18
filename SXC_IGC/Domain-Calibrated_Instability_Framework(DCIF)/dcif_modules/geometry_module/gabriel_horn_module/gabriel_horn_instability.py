import numpy as np

class GabrielHornEngine:
    def __init__(self, z_start=1.0, z_end=10.0):
        self.z = z_start
        self.z_end = z_end
        self.T_sys = 0.5
        self.beta_base = 3.5
        self.gamma_base = 0.8
        self.dt = 0.05
        
    def get_geometry_factors(self, z: float):
        radius = 1.0 / z
        beta_eff = self.beta_base * (1.0 / radius**0.5)
        gamma_eff = self.gamma_base * radius
        return beta_eff, gamma_eff

    def simulate_drift(self, signals):
        history = []
        z_current = self.z
        
        for signal in signals:
            beta_eff, gamma_eff = self.get_geometry_factors(z_current)

            E = 1 - np.exp(-signal / 40.0) if signal < 45 else 0.675 + ((signal - 45.0) / 20.0)
            inflow = E * beta_eff
            outflow = gamma_eff * self.T_sys

            self.T_sys += (inflow - outflow) * self.dt

            z_current += 0.01  # BREAK: drift independent of tension

            history.append((z_current, self.T_sys))

            if self.T_sys > 10.0:
                break

        return history

engine = GabrielHornEngine()
signals = [50] * 200
results = engine.simulate_drift(signals)

print("BREAK TEST 3")
print(f"End z: {results[-1][0]:.2f}")
print(f"Final Tension: {results[-1][1]:.2f}")
