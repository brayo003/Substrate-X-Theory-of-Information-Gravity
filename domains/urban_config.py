# domains/urban_config.py - FIX: F-field shape

import numpy as np

# --- Core Constants ---
R_STIFFNESS = 1.5e-3
D_DIFFUSION = 0.8e-4
GRID_SIZE = 100
GRID_RESOLUTION = (GRID_SIZE, GRID_SIZE, 1) 

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
        'DT': 0.1
    }

    # 2. Initialize the fields
    rho_initial = np.zeros(GRID_RESOLUTION)
    center_x, center_y = GRID_SIZE // 2, GRID_SIZE // 2
    x, y = np.mgrid[0:GRID_SIZE, 0:GRID_SIZE]
    
    sigma = 15
    rho_2D = 10 * np.exp(-((x - center_x)**2 + (y - center_y)**2) / (2 * sigma**2))
    rho_initial[:, :, 0] = rho_2D 
    
    E_initial = np.ones(GRID_RESOLUTION) * 0.1
    
    # *** FIX IS HERE: F is now a SCALAR field like rho and E ***
    F_initial = np.zeros(GRID_RESOLUTION) 

    # Combine initial fields into a dictionary
    initial_fields = {
        'rho': rho_initial,
        'E': E_initial,
        'F': F_initial
    }
    
    return params, initial_fields

if __name__ == '__main__':
    params, fields = get_urban_parameters()
    print("Urban Config Loaded.")
    print(f"Initial Rho Shape: {fields['rho'].shape}")
    print(f"Initial F Shape: {fields['F'].shape}")
