# domains/energy_config.py
# Configuration for the Energy Dynamics Domain (Oil/Gas, Grid, Renewables)

import numpy as np

# --- Universal Energy Constants ---
GRID_SIZE = 100
GRID_RESOLUTION = (GRID_SIZE, GRID_SIZE, 1) 

# Base R_i (Resource/Interaction Stiffness) and D_i (Diffusion Coefficient)
# Energy systems typically have high diffusion and low inherent stiffness (except for resistance/losses)
D_BASE = 5.0e-3 # High diffusion for fast energy/heat spread
R_BASE = 0.5e-3 # Low interaction stiffness

# --- Sub-Domain Specific Parameters ---
# These are tuned constants that allow the universal engine to model different physics.
ENERGY_SUB_DOMAIN_CONSTANTS = {
    # Simulates slow, viscous flow (high R, low D) and high pressure (high initial rho)
    "OIL_GAS": {
        'R': 8.0e-3, # High resistance to flow/extraction
        'D': 1.0e-3, # Low diffusion/permeability
        'rho_scale': 50.0,
    },
    # Simulates highly localized generation and high flow (low R, high D)
    "RENEWABLES": {
        'R': 0.1e-3, # Very low stiffness/resistance
        'D': 9.0e-3, # High flow/diffusion rate
        'rho_scale': 20.0,
    },
    # Simulates systems with high storage capacity (high initial E) and medium flow
    "STORAGE": {
        'R': 5.0e-3, # Medium stiffness/pressure tolerance
        'D': 3.0e-3, # Medium flow rate
        'rho_scale': 30.0,
    },
    # Uses balanced constants for general distribution networks
    "GRID_MANAGEMENT": {
        'R': R_BASE, 
        'D': D_BASE,
        'rho_scale': 10.0,
    },
}

def get_energy_parameters(domain_type="GRID_MANAGEMENT"):
    """
    Returns the simulation parameters and initial field states 
    tailored for a specific Energy Dynamics sub-domain.
    """
    domain_type = domain_type.upper()
    
    if domain_type not in ENERGY_SUB_DOMAIN_CONSTANTS:
        raise ValueError(f"Unknown energy domain type: {domain_type}")

    constants = ENERGY_SUB_DOMAIN_CONSTANTS[domain_type]
    
    # 1. Define the parameters dictionary
    params = {
        'R': constants['R'],
        'D': constants['D'],
        'GRID_RES': GRID_RESOLUTION,
        'DT': 0.05 # Smaller time step for high-diffusion energy systems
    }

    # 2. Initialize the fields (rho, E, F)
    
    # rho (Energy Mass/Pressure Field) - Initialized with a localized high-pressure source
    rho_initial = np.zeros(GRID_RESOLUTION)
    center_x, center_y = GRID_SIZE // 2, GRID_SIZE // 2
    x, y = np.mgrid[0:GRID_SIZE, 0:GRID_SIZE]
    
    # Gaussian pulse source (representing a reservoir, power plant, or battery)
    sigma = 10
    rho_2D = constants['rho_scale'] * np.exp(-((x - center_x)**2 + (y - center_y)**2) / (2 * sigma**2))
    rho_initial[:, :, 0] = rho_2D 
    
    # E (Generation/Potential Field) - Initialized with a uniform baseline potential
    E_initial = np.ones(GRID_RESOLUTION) * 0.05
    
    # F (Resistance/Losses Field) - Initialized with a simple uniform baseline resistance
    F_initial = np.ones(GRID_RESOLUTION) * 0.01 

    # Combine initial fields into a dictionary
    initial_fields = {
        'rho': rho_initial,
        'E': E_initial,
        'F': F_initial
    }
    
    return params, initial_fields

if __name__ == '__main__':
    # Simple check for parameter loading
    params, fields = get_energy_parameters("OIL_GAS")
    print("Energy Config Loaded (OIL_GAS).")
    print(f"R: {params['R']}, D: {params['D']}")
    print(f"Initial Rho Sum: {np.sum(fields['rho'])}")
