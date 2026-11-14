import numpy as np
import emcee

# True parameters
Gamma0_true = 1.0e3
k_true = 4.5e-7
om_max_true = 1.0e6

def substrate_model(omega, Gamma0, k, om_max):
    return Gamma0 + k * omega**2 / (1 + (omega/om_max)**2)

# Log-probability (same as before, noise=2%)
def log_prob(theta, omega, data):
    Gamma0, k, om_max = theta
    if not (0<Gamma0<1e4 and 1e-10<k<1e-3 and 1e3<om_max<1e9):
        return -np.inf
    model = substrate_model(omega, Gamma0, k, om_max)
    sigma = 0.02 * np.abs(data) + 1e-12
    return -0.5 * np.sum(((data - model)/sigma)**2)

# MCMC settings
ndim, nwalkers, nsteps, burnin = 3, 20, 1500, 500

# define scenarios: (label, number of points, omega array)
scenarios = [
    ("full, N=10", 10, np.logspace(3, 8, 10)),
    ("full, N=50", 50, np.logspace(3, 8, 50)),
    ("low range 1e3-1e5", 20, np.logspace(3, 5, 20)),
    ("high range 1e6-1e8", 20, np.logspace(6, 8, 20)),
]

np.random.seed(42)

for label, N, omega in scenarios:
    true_gamma = substrate_model(omega, Gamma0_true, k_true, om_max_true)
    noise = 0.02 * true_gamma * np.random.randn(N)
    data = true_gamma + noise

    init = np.array([Gamma0_true, k_true, om_max_true])
    pos = init + 0.01*init * np.random.randn(nwalkers, ndim)
    sampler = emcee.EnsembleSampler(nwalkers, ndim, log_prob, args=(omega, data))
    sampler.run_mcmc(pos, nsteps, progress=False)
    samples = sampler.get_chain(discard=burnin, flat=True)
    k_samples = samples[:,1]
    k_rel = np.std(k_samples) / np.mean(k_samples)
    print(f"{label:<25} σ(k)/k = {k_rel*100:.2f}%")
