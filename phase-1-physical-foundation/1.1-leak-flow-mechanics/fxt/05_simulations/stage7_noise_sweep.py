import numpy as np
import emcee
import sys

# ------------------------------------------------------------
# 1. True parameters & data setup
# ------------------------------------------------------------
Gamma0_true = 1.0e3
k_true = 4.5e-7
om_max_true = 1.0e6
omega = np.logspace(3, 8, 20)

def substrate_model(omega, Gamma0, k, om_max):
    return Gamma0 + k * omega**2 / (1 + (omega/om_max)**2)

# ------------------------------------------------------------
# 2. Log‑probability (same as before)
# ------------------------------------------------------------
def log_prior(theta):
    Gamma0, k, om_max = theta
    if 0 < Gamma0 < 1e4 and 1e-10 < k < 1e-3 and 1e3 < om_max < 1e9:
        return 0.0
    return -np.inf

def log_likelihood(theta, omega, Gamma_meas, noise_frac):
    Gamma0, k, om_max = theta
    model = substrate_model(omega, Gamma0, k, om_max)
    # uncertainties proportional to measured value * noise_frac
    sigma = noise_frac * np.abs(Gamma_meas) + 1e-12  # avoid zero
    return -0.5 * np.sum(((Gamma_meas - model) / sigma)**2)

def log_probability(theta, omega, Gamma_meas, noise_frac):
    lp = log_prior(theta)
    if not np.isfinite(lp):
        return -np.inf
    return lp + log_likelihood(theta, omega, Gamma_meas, noise_frac)

# ------------------------------------------------------------
# 3. Noise fractions to test
# ------------------------------------------------------------
noise_fracs = [0.005, 0.01, 0.02, 0.05, 0.10, 0.20]
ndim = 3
nwalkers = 20
nsteps = 2000   # can be increased later for final plot
burnin = 500

# store results
results = {}

np.random.seed(42)

for noise_frac in noise_fracs:
    # Generate data
    Gamma_true = substrate_model(omega, Gamma0_true, k_true, om_max_true)
    noise = noise_frac * Gamma_true * np.random.randn(len(omega))
    Gamma_meas = Gamma_true + noise

    # initial positions
    initial = np.array([Gamma0_true, k_true, om_max_true])
    init_pos = initial + 0.01 * initial * np.random.randn(nwalkers, ndim)
    args = (omega, Gamma_meas, noise_frac)

    sampler = emcee.EnsembleSampler(nwalkers, ndim, log_probability, args=args)
    sampler.run_mcmc(init_pos, nsteps, progress=False)  # silent

    samples = sampler.get_chain(discard=burnin, flat=True)
    results[noise_frac] = samples

    # compute relative uncertainties
    k_samples = samples[:, 1]
    om_samples = samples[:, 2]
    k_rel = np.std(k_samples) / np.mean(k_samples)
    om_rel = np.std(om_samples) / np.mean(om_samples)

    print(f"Noise {noise_frac*100:4.1f}%  σ(k)/k = {k_rel*100:.2f}%  σ(ω_max)/ω_max = {om_rel*100:.2f}%")

print("\nTable complete.")
