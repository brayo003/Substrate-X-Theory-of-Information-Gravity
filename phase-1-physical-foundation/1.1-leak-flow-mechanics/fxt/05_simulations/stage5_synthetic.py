import numpy as np
from scipy.optimize import curve_fit

# True parameters
k_true = 4.5e-7
om_max_true = 1e6
Gamma0_true = 1e3

omega = np.logspace(3, 8, 20)
Gamma_true = Gamma0_true + k_true * omega**2 / (1 + (omega/om_max_true)**2)
# add 5% Gaussian noise
np.random.seed(42)
noise = 0.05 * Gamma_true * np.random.randn(len(omega))
Gamma_meas = Gamma_true + noise

def model(omega, Gamma0, k, om_max):
    return Gamma0 + k * omega**2 / (1 + (omega/om_max)**2)

p0 = [1e3, 1e-7, 1e6]
popt, _ = curve_fit(model, omega, Gamma_meas, p0=p0, maxfev=10000)
Gamma0_fit, k_fit, om_fit = popt

print("Synthetic experiment recovery")
print(f"True: Gamma0={Gamma0_true:.2e}, k={k_true:.2e}, om_max={om_max_true:.2e}")
print(f"Fit : Gamma0={Gamma0_fit:.2e}, k={k_fit:.2e}, om_max={om_fit:.2e}")
