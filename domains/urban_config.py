# domains/urban_config.py

import numpy as np

# --- Core Constants (These should reflect the 'Urban' domain parameters) ---

# R_i: Resource/Interaction Stiffness (e.g., speed of policy change, infrastructure decay rate)
R_STIFFNESS = 1.5e-3  # Units: [1/time]

# D_i: Diffusion Coefficient (e.g., rate of information spread across city blocks)
D_DIFFUSION = 0.8e-4  # Units: [Area/time]

# GRID PARAMETERS (Define the size and resolution of the urban area being simulated)
GRID_SIZE = 100
GRID_RESOLUTION = (GRID_SIZE, GRID_SIZE, 1) # A 2D simulation grid

# --- Initial Field Conditions ---

def get_urban_parameters():
    """
    Returns the simulation parameters and initial field states 
    tailored for the Urban Dynamics domain.
    """
    
    # 1. Define the parameters dictionary
    params = {
        'R': R_STIFFNESS,
        'D': D_DIFFUSION,
        'GRID_RES': GRID_RESOLUTION,
        'DT': 0.1 # Time step size
    }

    # 2. Initialize the fields (rho, E, F)
    # rho (Mass/Matter Field - e.g., Population Density or Physical Infrastructure)
    rho_initial = np.zeros(GRID_RESOLUTION)
    
    # Place a high-density, Gaussian 'city center' in the middle
    center_x, center_y = GRID_SIZE // 2, GRID_SIZE // 2
    x, y = np.mgrid[0:GRID_SIZE, 0:GRID_SIZE]
    
    # Create a simple 2D Gaussian profile
    sigma = 15
    rho_2D = 10 * np.exp(-((x - center_x)**2 + (y - center_y)**2) / (2 * sigma**2))
    rho_initial[:, :, 0] = rho_2D 
    
    # E (Information Field - e.g., Social Cohesion, Economic Value)
    E_initial = np.ones(GRID_RESOLUTION) * 0.1 # Start with a small, uniform information field
    
    # F (Gravitational/Flow Field - This should typically be determined by E and rho, 
    # but we can set a zero or simple initial condition for stability)
    F_initial = np.zeros(GRID_RESOLUTION + (3,)) # Add a dimension for vector components (Fx, Fy, Fz)

    # Combine initial fields into a dictionary
    initial_fields = {
        'rho': rho_initial,
        'E': E_initial,
        'F': F_initial
    }
    
    return params, initial_fields

if __name__ == '__main__':
    # Simple check to verify the shapes when running the script directly
    params, fields = get_urban_parameters()
    print("Urban Config Loaded.")
    print(f"R_STIFFNESS: {params['R']}")
    print(f"Initial Rho Shape: {fields['rho'].shape}")
    print(f"Initial E Shape: {fields['E'].shape}")
    print(f"Initial F Shape: {fields['F'].shape}")
