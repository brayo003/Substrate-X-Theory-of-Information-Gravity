import numpy as np
import matplotlib.pyplot as plt
import emcee

# True substrate and data (2% noise)
Gamma0_true, k_true, om_max_true = 1e3, 4.5e-7, 1e6
omega = np.logspace(3, 8, 20)
true_gamma = substrate_model(omega, Gamma0_true, k_true, om_max_true)
np.random.seed(42)
noise = 0.02 * true_gamma * np.random.randn(len(omega))
data = true_gamma + noise

def substrate_model(omega, Gamma0, k, om_max):
    return Gamma0 + k * omega**2 / (1 + (omega/om_max)**2)

# MCMC run (already done in previous test, but repeat here)
def log_prob(theta, omega, data):
    G0, k, om = theta
    if not (0<G0<1e4 and 1e-10<k<1e-3 and 1e3<om<1e9):
        return -np.inf
    model = substrate_model(omega, G0, k, om)
    sigma = 0.02 * np.abs(data) + 1e-12
    return -0.5 * np.sum(((data - model)/sigma)**2)

ndim, nwalkers, nsteps, burnin = 3, 20, 2000, 500
init = np.array([Gamma0_true, k_true, om_max_true])
pos = init + 0.01*init * np.random.randn(nwalkers, ndim)
sampler = emcee.EnsembleSampler(nwalkers, ndim, log_prob, args=(omega, data))
sampler.run_mcmc(pos, nsteps, progress=False)
samples = sampler.get_chain(discard=burnin, flat=True)

# posterior predictive: randomly select 200 samples from posterior
n_pred = 200
idx = np.random.choice(len(samples), n_pred, replace=False)
pred_curves = np.array([substrate_model(omega, *samples[i]) for i in idx])

# plot
plt.figure(figsize=(8,5))
# plot a few predictive realizations (light blue)
for i in range(20):
    plt.loglog(omega, pred_curves[i], color='lightblue', alpha=0.5)
# plot the predictive envelope (percentiles)
low = np.percentile(pred_curves, 2.5, axis=0)
high = np.percentile(pred_curves, 97.5, axis=0)
plt.fill_between(omega, low, high, color='blue', alpha=0.15, label='95% predictive interval')
plt.loglog(omega, data, 'k.', label='Observed data')
plt.xlabel('ω (rad/s)')
plt.ylabel('Γ (s⁻¹)')
plt.title('Posterior predictive check')
plt.legend()
plt.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig('posterior_predictive.png', dpi=150)
print("Posterior predictive plot saved. Data should lie within the envelope.")
