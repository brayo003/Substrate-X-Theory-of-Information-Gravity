import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit

# 1. DATA INPUT (Local Density vs Measured η)
# Density is approximated as mass within the relevant volume (kg/m^3)
densities = np.array([
    1.4e-16,   # Solar System (Pioneer zone density)
    1.0e-21,   # Galactic Disk (Pulsar neighborhood)
    1.0e-27    # Cosmic Void (LIGO propagation path)
])

measured_eta = np.array([
    0.0531,    # Pioneer Result
    0.0185,    # Pulsar Result
    3.82e-16   # LIGO Result (effectively zero)
])

# 2. DEFINE THE PIVOT MODEL: η(ρ) = A * ρ^b
# If b is positive, η depends on how much "stuff" is in the way.
def density_model(rho, A, b):
    return A * np.power(rho, b)

# 3. PERFORM THE FIT
params, _ = curve_fit(density_model, densities, measured_eta)
A_fit, b_fit = params

print(f"=== PIVOT VALIDATION: DENSITY CORRELATION ===")
print(f"Scaling Exponent (b): {b_fit:.4f}")

# 4. LOGIC CHECK
if b_fit > 0.5:
    status = "VALIDATED: Substrate is an 'Information Clog' proportional to matter."
elif b_fit < 0.1:
    status = "FAILED: η is random. No correlation with density."
else:
    status = "INCONCLUSIVE: Weak coupling."

print(f"STATUS: {status}")

# 5. VISUALIZATION
plt.figure(figsize=(8, 5))
rho_range = np.logspace(-28, -15, 100)
plt.loglog(densities, measured_eta, 'ro', label='Measured Data')
plt.loglog(rho_range, density_model(rho_range, *params), 'b--', label='Pivot Prediction')
plt.xlabel("Local Matter Density (kg/m^3)")
plt.ylabel("Viscosity η")
plt.title("Is Substrate X a Local Density Effect?")
plt.grid(True, which="both", ls="-", alpha=0.2)
plt.legend()
plt.savefig('pivot_test.png')
print("Plot saved as 'pivot_test.png'")
