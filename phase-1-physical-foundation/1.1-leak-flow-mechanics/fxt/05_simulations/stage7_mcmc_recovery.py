import numpy as np
import matplotlib.pyplot as plt
import emcee
import corner

# ------------------------------------------------------------
# 1. True substrate parameters
# ------------------------------------------------------------
Gamma0_true = 1.0e3
k_true = 4.5e-7
om_max_true = 1.0e6

# ------------------------------------------------------------
# 2. Generate synthetic data at different noise levels
# ------------------------------------------------------------
omega = np.logspace(3, 8, 20)   # same as earlier stages

def substrate_model(omega, Gamma0, k, om_max):
    return Gamma0 + k * omega**2 / (1 + (omega/om_max)**2)

# Choose a noise fraction to study (change this to 0.005,0.01,0.02,0.05,0.1,0.2)
noise_frac = 0.02   # 2% noise for demonstration
np.random.seed(42)
Gamma_true = substrate_model(omega, Gamma0_true, k_true, om_max_true)
noise = noise_frac * Gamma_true * np.random.randn(len(omega))
Gamma_meas = Gamma_true + noise

# ------------------------------------------------------------
# 3. Define log‑probability (likelihood + priors)
# ------------------------------------------------------------
def log_prior(theta):
    Gamma0, k, om_max = theta
    if not (0 < Gamma0 < 1e4 and 1e-10 < k < 1e-3 and 1e3 < om_max < 1e9):
        return -np.inf
    return 0.0   # flat prior within bounds

def log_likelihood(theta, omega, Gamma_meas):
    Gamma0, k, om_max = theta
    model = substrate_model(omega, Gamma0, k, om_max)
    return -0.5 * np.sum((Gamma_meas - model)**2 / (noise_frac * Gamma_meas)**2)

def log_probability(theta, omega, Gamma_meas):
    lp = log_prior(theta)
    if not np.isfinite(lp):
        return -np.inf
    return lp + log_likelihood(theta, omega, Gamma_meas)

# ------------------------------------------------------------
# 4. MCMC setup
# ------------------------------------------------------------
ndim = 3
nwalkers = 20
nsteps = 2000   # increase for smoother posteriors (e.g. 5000)

# initial positions spread around true values
initial = np.array([Gamma0_true, k_true, om_max_true])
init_pos = initial + 0.01 * initial * np.random.randn(nwalkers, ndim)

args = (omega, Gamma_meas)

sampler = emcee.EnsembleSampler(nwalkers, ndim, log_probability, args=args)
sampler.run_mcmc(init_pos, nsteps, progress=True)

# ------------------------------------------------------------
# 5. Discard burn‑in and flatten
# ------------------------------------------------------------
burnin = 500
samples = sampler.get_chain(discard=burnin, flat=True)

# ------------------------------------------------------------
# 6. Print parameter estimates
# ------------------------------------------------------------
print("\n=== MCMC Parameter Recovery (noise = {}%) ===".format(noise_frac*100))
for i, name in enumerate(["Gamma0", "k", "om_max"]):
    mcmc_vals = samples[:, i]
    med = np.median(mcmc_vals)
    low, high = np.percentile(mcmc_vals, [16, 84])
    print(f"{name} = {med:.2e}  (+{high-med:.2e} / -{med-low:.2e})  (true: {initial[i]:.2e})")

# ------------------------------------------------------------
# 7. Corner plot
# ------------------------------------------------------------
fig = corner.corner(samples, labels=["$\\Gamma_0$", "$k$", "$\\omega_{max}$"],
                    truths=initial, quantiles=[0.16, 0.5, 0.84],
                    show_titles=True, title_fmt='.2e')
plt.suptitle(f"MCMC recovery, {noise_frac*100:.0f}% noise", fontsize=14)
plt.tight_layout()
plt.savefig(f'mcmc_recovery_noise_{int(noise_frac*100)}pct.png', dpi=150)
print("Corner plot saved.")
