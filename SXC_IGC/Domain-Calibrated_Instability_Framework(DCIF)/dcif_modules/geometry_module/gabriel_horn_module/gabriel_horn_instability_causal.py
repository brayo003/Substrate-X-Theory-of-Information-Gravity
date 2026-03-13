import numpy as np

class GabrielHornEngine:
    def __init__(self, z_start=1.0, z_end=10.0):
        self.z = z_start
        self.z_end = z_end
        self.T_sys = 0.5
        self.beta_base = 3.5
        self.gamma_base = 0.8
        self.dt = 0.05
        self.kappa = 0.02  # geometry response strength
        
    def get_geometry_factors(self, z: float):
        radius = 1.0 / z
        beta_eff = self.beta_base * (1.0 / radius**0.5)
        gamma_eff = self.gamma_base * radius
        return beta_eff, gamma_eff

    def z_drift(self, T):
        return self.kappa * (T / (1.0 + T))

    def simulate_drift(self, signals):
        history = []
        z_current = self.z
        
        for signal in signals:
            beta_eff, gamma_eff = self.get_geometry_factors(z_current)

            if signal < 45:
                E = 1 - np.exp(-signal / 40.0)
            else:
                E = 0.675 + ((signal - 45.0) / 20.0)

            inflow = E * beta_eff
            outflow = gamma_eff * self.T_sys

            self.T_sys += (inflow - outflow) * self.dt
            z_current += self.z_drift(self.T_sys) * self.dt

            history.append((z_current, self.T_sys))

            if self.T_sys > 10.0 or z_current > self.z_end:
                break

        return history


engine = GabrielHornEngine()
signals = [50] * 500
results = engine.simulate_drift(signals)

print("CAUSAL CLOSURE TEST")
print(f"Steps: {len(results)}")
print(f"End z: {results[-1][0]:.3f}")
print(f"Final Tension: {results[-1][1]:.3f}")
