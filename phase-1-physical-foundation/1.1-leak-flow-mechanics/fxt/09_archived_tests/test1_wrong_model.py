import numpy as np
from scipy.optimize import curve_fit

omega = np.logspace(3, 8, 20)
Gamma0 = 1e3

# --- define alternative true models ---
def linear(omega, a):
    return Gamma0 + a * omega
def quadratic_no_sat(omega, a):
    return Gamma0 + a * omega**2
def logarithmic(omega, a):
    return Gamma0 + a * np.log(1 + omega)

# --- substrate model to fit ---
def substrate_model(omega, Gamma0, k, om_max):
    return Gamma0 + k * omega**2 / (1 + (omega/om_max)**2)

# choose coefficients so that the effect is comparable to the substrate one at 1e6 rad/s
ref = 1e6
sub_ref = 4.5e-7 * ref**2 / (1 + (ref/1e6)**2)   # = 2.25e5
a_lin = sub_ref / ref          # ~0.225
a_quad = sub_ref / ref**2      # 2.25e-7
a_log = sub_ref / np.log(1+ref)  # ~2.21e4

models = {
    'linear': (linear, a_lin),
    'quadratic (no sat)': (quadratic_no_sat, a_quad),
    'logarithmic': (logarithmic, a_log)
}

np.random.seed(123)
for name, (func, a_val) in models.items():
    true_gamma = func(omega, a_val)
    noise = 0.02 * true_gamma * np.random.randn(len(omega))
    measured = true_gamma + noise

    # fit substrate model
    try:
        popt, _ = curve_fit(substrate_model, omega, measured,
                            p0=[1e3, 1e-7, 1e6], maxfev=10000)
        Gamma0_fit, k_fit, om_fit = popt
        residuals = measured - substrate_model(omega, *popt)
        rss = np.sum(residuals**2)
        print(f"True model: {name}")
        print(f"  Fitted k_rot = {k_fit:.2e}, ω_max = {om_fit:.2e}")
        print(f"  RSS = {rss:.2e}  (vs expected from noise ~ {np.sum((noise)**2):.2e})")
        # check if k is spuriously "significant"
        if k_fit > 1e-8:
            print("  WARNING: spurious k_rot detected.")
        else:
            print("  k_rot effectively zero, model not fooled.")
    except Exception as e:
        print(f"True model: {name}  fit failed: {e}")
    print()
