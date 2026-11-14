import numpy as np, emcee, arviz as az

Gamma0_true, k_true, om_max_true = 1e3, 4.5e-7, 1e6
omega = np.logspace(3, 8, 20)

def substrate_model(omega, Gamma0, k, om_max):
    return Gamma0 + k * omega**2 / (1 + (omega/om_max)**2)

true_gamma = substrate_model(omega, Gamma0_true, k_true, om_max_true)
np.random.seed(42)
noise = 0.02 * true_gamma * np.random.randn(len(omega))
data = true_gamma + noise

# pointwise log-likelihood
def log_like_sub(theta, omega, y):
    G0, k, om = theta
    model = substrate_model(omega, G0, k, om)
    sigma = 0.02 * np.abs(y) + 1e-12
    return -0.5 * ((y - model)/sigma)**2 - np.log(sigma) - 0.5*np.log(2*np.pi)

def log_like_const(theta, omega, y):
    G0 = theta[0]
    model = np.full_like(omega, G0)
    sigma = 0.02 * np.abs(y) + 1e-12
    return -0.5 * ((y - model)/sigma)**2 - np.log(sigma) - 0.5*np.log(2*np.pi)

# MCMC substrate
def log_prob_sub(theta, omega, y):
    G0, k, om = theta
    if not (0<G0<1e4 and 1e-10<k<1e-3 and 1e3<om<1e9):
        return -np.inf
    return np.sum(log_like_sub(theta, omega, y))

ndim, nwalkers, nsteps, burnin = 3, 20, 2000, 500
init = np.array([Gamma0_true, k_true, om_max_true])
pos = init + 0.01*init * np.random.randn(nwalkers, ndim)
sampler_sub = emcee.EnsembleSampler(nwalkers, ndim, log_prob_sub, args=(omega, data))
sampler_sub.run_mcmc(pos, nsteps, progress=False)
samples_sub = sampler_sub.get_chain(discard=burnin, flat=True)

# MCMC constant
def log_prob_const(theta, omega, y):
    G0 = theta[0]
    if not 0<G0<1e4: return -np.inf
    return np.sum(log_like_const(theta, omega, y))

sampler_const = emcee.EnsembleSampler(20, 1, log_prob_const, args=(omega, data))
pos_const = np.array([Gamma0_true]) + 100 * np.random.randn(20,1)
sampler_const.run_mcmc(pos_const, nsteps, progress=False)
samples_const = sampler_const.get_chain(discard=burnin, flat=True)

# thin and compute pointwise log-likelihood
thin = 200
idx_sub = np.random.choice(len(samples_sub), thin, replace=False)
idx_const = np.random.choice(len(samples_const), thin, replace=False)
sub_ll = np.array([log_like_sub(samples_sub[i], omega, data) for i in idx_sub])
const_ll = np.array([log_like_const([samples_const[i]], omega, data) for i in idx_const])

idata_sub = az.from_dict(posterior={"Gamma0": samples_sub[:,0], "k": samples_sub[:,1], "om_max": samples_sub[:,2]},
                         log_likelihood={"Gamma": sub_ll})
idata_const = az.from_dict(posterior={"Gamma0": samples_const[:,0]},
                           log_likelihood={"Gamma": const_ll})

# Compute WAIC and LOO
waic_sub = az.waic(idata_sub, scale="deviance")
waic_const = az.waic(idata_const, scale="deviance")
loo_sub = az.loo(idata_sub, scale="deviance")
loo_const = az.loo(idata_const, scale="deviance")

# Inspect the returned objects to find the correct keys
print("WAIC object keys:", waic_sub.keys())
print("LOO object keys:", loo_sub.keys())

# Try to print using the first key that looks plausible
# Usually 'elpd_waic' or 'waic' depending on version
try:
    print(f"Constant WAIC: {waic_const['waic']:.1f}")
except KeyError:
    print(f"Constant WAIC (via elpd_waic): {waic_const['elpd_waic']:.1f}")
try:
    print(f"Substrate WAIC: {waic_sub['waic']:.1f}")
except KeyError:
    print(f"Substrate WAIC (via elpd_waic): {waic_sub['elpd_waic']:.1f}")
try:
    print(f"Constant LOO: {loo_const['loo']:.1f}")
except KeyError:
    print(f"Constant LOO (via elpd_loo): {loo_const['elpd_loo']:.1f}")
try:
    print(f"Substrate LOO: {loo_sub['loo']:.1f}")
except KeyError:
    print(f"Substrate LOO (via elpd_loo): {loo_sub['elpd_loo']:.1f}")
