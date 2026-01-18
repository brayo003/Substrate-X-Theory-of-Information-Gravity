import numpy as np
import matplotlib.pyplot as plt
from cobaya.run import run
from cobaya.theory import Theory
import os
from getdist import plots, MCSamples

# Ensure output directory exists
os.makedirs("mcmc_results", exist_ok=True)

class TensionDarkEnergy(Theory):
    params = {
        'r': 0.153267,    # Critical parameter from your work
        'w0': -0.97,      # Dark energy EOS
        'wa': 0.0,        # EOS time evolution
        'sigma8': 0.81,   # Structure growth
        'h': 0.674,       # Hubble parameter
        'omega_b': 0.0224,# Baryon density
        'omega_cdm': 0.12 # CDM density
    }

    def calculate(self, state, **params_values):
        # Simple power spectrum model (replace with your actual calculation)
        k = np.logspace(-4, 1, 100)  # k in h/Mpc
        Pk = 2e4 * k**0.8 * np.exp(-(k/0.1)**2)  # Example power spectrum
        
        # Store results
        state['Pk_interpolator'] = (k, Pk)
        state['Pk_grid'] = (k, Pk)  # For consistency with Cobaya

# MCMC configuration
info = {
    'output': 'mcmc_results/tension_mcmc',
    'force': True,
    
    'likelihood': {
        'planck_2018_highl_plik.TT': None,  # Planck CMB temperature
        'planck_2018_lowl_ee': None,         # Low-EE
        'planck_2018_lowl_tt': None,         # Low-TT
        'bao.boss_dr12_consensus': None,     # BAO data
        'sn.pantheon': None                  # Supernovae
    },
    
    'theory': {
        'tension_de': TensionDarkEnergy,
        'camb': None  # Will use CAMB for background evolution
    },
    
    'params': {
        # Your model parameters
        'r': {'prior': {'min': 0.14, 'max': 0.17}, 'latex': r'r'},
        'w0': {'prior': {'min': -1.1, 'max': -0.9}, 'latex': r'w_0'},
        'wa': {'prior': {'min': -0.5, 'max': 0.5}, 'latex': r'w_a'},
        'sigma8': {'prior': {'min': 0.7, 'max': 0.9}, 'latex': r'\sigma_8'},
        
        # Standard ΛCDM parameters
        'h': {'prior': {'min': 0.6, 'max': 0.8}, 'latex': r'h'},
        'omega_b': {'prior': {'min': 0.02, 'max': 0.025}, 'latex': r'\Omega_b h^2'},
        'omega_cdm': {'prior': {'min': 0.1, 'max': 0.14}, 'latex': r'\Omega_c h^2'},
        'tau_reio': {'prior': {'min': 0.01, 'max': 0.1}, 'latex': r'\tau'},
    },
    
    'sampler': {
        'mcmc': {
            'max_tries': 10000,
            'burn_in': 0.3,  # Discard first 30% of chains
            'Rminus1_stop': 0.01,  # Convergence criterion
            'max_samples': 1000  # Maximum number of samples
        }
    }
}

# Run MCMC
print("Starting MCMC analysis...")
updated_info, sampler = run(info)

# Load and plot results
print("Analysis complete. Generating plots...")
samples = MCSamples("mcmc_results/tension_mcmc")
g = plots.get_single_plotter()
g.triangle_plot(samples, ['r', 'w0', 'sigma8', 'h'], filled=True)
plt.savefig('mcmc_results/parameter_constraints.png', dpi=150, bbox_inches='tight')
print("Results saved to mcmc_results/")
