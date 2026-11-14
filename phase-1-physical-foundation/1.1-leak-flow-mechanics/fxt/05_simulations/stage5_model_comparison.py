import numpy as np
from scipy.optimize import curve_fit
import matplotlib.pyplot as plt

# True substrate parameters (if present)
k_true = 4.5e-7
om_max_true = 1e6
Gamma0_true = 1e3

omega = np.logspace(3, 8, 20)

def substrate_model(omega, Gamma0, k, om_max):
    return Gamma0 + k * omega**2 / (1 + (omega/om_max)**2)

def constant_model(omega, Gamma0):
    return np.full_like(omega, Gamma0)

np.random.seed(123)

# ----- 1. Generate data WITHOUT substrate (null model) -----
Gamma_std = np.full_like(omega, Gamma0_true)
noise_std = 0.02 * Gamma0_true * np.random.randn(len(omega))
Gamma_meas_std = Gamma_std + noise_std

# Fit constant model
popt_const_std, _ = curve_fit(constant_model, omega, Gamma_meas_std, p0=[Gamma0_true])
# Fit substrate model (expect k close to 0)
popt_sub_std, _ = curve_fit(substrate_model, omega, Gamma_meas_std,
                            p0=[Gamma0_true, 1e-7, 1e6], maxfev=10000)

print("=== NULL MODEL DATA (no substrate) ===")
print(f"Constant fit:  Γ0 = {popt_const_std[0]:.2e}")
print(f"Substrate fit: Γ0 = {popt_sub_std[0]:.2e}, k = {popt_sub_std[1]:.2e}, ω_max = {popt_sub_std[2]:.2e}")
print("  (k should be ~0; if k is spuriously large, model is over-parameterized)")

# ----- 2. Generate data WITH substrate -----
Gamma_sub = substrate_model(omega, Gamma0_true, k_true, om_max_true)
noise_sub = 0.02 * Gamma_sub * np.random.randn(len(omega))
Gamma_meas_sub = Gamma_sub + noise_sub

# Fit constant model
popt_const_sub, _ = curve_fit(constant_model, omega, Gamma_meas_sub, p0=[Gamma0_true])
# Fit substrate model
popt_sub_sub, _ = curve_fit(substrate_model, omega, Gamma_meas_sub,
                            p0=[Gamma0_true, 1e-7, 1e6], maxfev=10000)

print("\n=== SUBSTRATE DATA ===")
print(f"True:            Γ0={Gamma0_true:.2e}, k={k_true:.2e}, ω_max={om_max_true:.2e}")
print(f"Constant fit:    Γ0 = {popt_const_sub[0]:.2e}")
print(f"Substrate fit:   Γ0 = {popt_sub_sub[0]:.2e}, k = {popt_sub_sub[1]:.2e}, ω_max = {popt_sub_sub[2]:.2e}")

# Compute residuals and AIC for substrate data
res_const = Gamma_meas_sub - constant_model(omega, *popt_const_sub)
res_sub   = Gamma_meas_sub - substrate_model(omega, *popt_sub_sub)
n = len(omega)
aic_const = n * np.log(np.sum(res_const**2)/n) + 2*1
aic_sub   = n * np.log(np.sum(res_sub**2)/n)   + 2*3
print(f"AIC constant: {aic_const:.1f}, AIC substrate: {aic_sub:.1f}")
print(f"ΔAIC = {aic_sub - aic_const:.1f} (negative -> substrate favoured)")

# Optional: quick plot
plt.figure(figsize=(6,4))
plt.loglog(omega, Gamma_meas_sub, 'k.')
omega_fine = np.logspace(3,8,100)
plt.loglog(omega_fine, constant_model(omega_fine, *popt_const_sub), 'b--', label='Const')
plt.loglog(omega_fine, substrate_model(omega_fine, *popt_sub_sub), 'r-', label='Substrate')
plt.legend()
plt.grid(alpha=0.3)
plt.title('Synthetic data with substrate')
plt.tight_layout()
plt.savefig('stage5_model_comparison.png', dpi=150)
print("Plot saved.")
