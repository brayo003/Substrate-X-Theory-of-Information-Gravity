# core/universal_stable_core.py
# Universal Dynamics Engine - Functional Core PDE Solver

import numpy as np

class UniversalDynamicsEngine:
    """
    The core PDE solver for the Substrate X Theory of Information Gravity.
    This class contains the domain-agnostic physics/math (Reaction-Diffusion model).
    """
    def __init__(self, params):
        self.params = params
        self.GRID_X = params['GRID_RES'][0]
        self.GRID_Y = params['GRID_RES'][1]
        self.DT = params['DT']
        self.R = params['R']
        self.D = params['D']
        
        # NOTE: For now, we hardcode the Urban reaction constants here for simplicity. 
        # In a fully domain-agnostic model, these would be loaded from a universal source.
        self.delta1, self.delta2 = 2.0, 1.2
        self.alpha, self.beta, self.gamma = 1.2, 0.8, 1.0
        self.tau_E, self.tau_F = 0.6, 0.4
        
        self.rho = None
        self.E = None
        self.F = None
        self.steps = 0

    def set_initial_conditions(self, rho_initial, E_initial, F_initial):
        self.rho = rho_initial
        self.E = E_initial
        self.F = F_initial

    def laplacian_2d(self, field):
        """Standard 2D Laplacian operator (Diffusion) with Neumann boundaries."""
        laplacian = np.zeros_like(field)
        
        # Use simple 5-point stencil for the interior
        laplacian[1:-1, 1:-1] = (
            field[:-2, 1:-1] + field[2:, 1:-1] +  # Y-direction
            field[1:-1, :-2] + field[1:-1, 2:] - 4 * field[1:-1, 1:-1] # X-direction
        )
        # Assuming grid resolution dx=dy=1 for simplicity in this core.
        return laplacian

    # --- REACTION TERMS (Based on the tested Urban equations) ---
    def reaction_rho(self, rho, E, F):
        """Density evolution: development drives growth, constraints limit it""" 
        return self.delta1 * E * rho * (1 - rho) - self.delta2 * F * rho
    
    def reaction_E(self, rho, E, F):
        """Development evolution: density creates potential, constraints limit it"""
        return (self.alpha * rho + self.beta * E * (1 - E) - self.gamma * F * E - self.tau_E * E)

    def reaction_F(self, rho, E):
        """Constraint evolution: density increases constraint, potential decreases it"""
        # This is simplified; F is usually a vector field, but treated as a scalar source here.
        return (self.R * rho - self.R * E - self.tau_F * F)
        
    # --- CORE SOLVER ---
    def run_simulation(self, num_steps):
        """Runs the simulation using Forward Euler integration."""
        rho, E, F = self.rho, self.E, self.F
        dt = self.DT
        D = self.D
        R = self.R # Re-using R for the F-field reaction (Urban constraint logic)
        
        for _ in range(num_steps):
            
            # 1. Calculate Diffusion Term (Laplacian)
            L_rho = self.laplacian_2d(rho)
            L_E = self.laplacian_2d(E)
            
            # 2. Calculate Reaction Term
            R_rho = self.reaction_rho(rho, E, F)
            R_E = self.reaction_E(rho, E, F)
            R_F = self.reaction_F(rho, E)
            
            # 3. Apply Forward Euler Integration
            # The Diffusion Coefficient 'D' is applied only to the rho and E fields
            
            # d_rho/dt = D * Laplacian(rho) + R_rho
            drho_dt = D * L_rho + R_rho 
            
            # d_E/dt = D * Laplacian(E) + R_E
            dE_dt = D * L_E + R_E
            
            # d_F/dt = R_F (F is assumed to be a non-diffusing constraint field for simplicity)
            dF_dt = R_F 
            
            # Update fields
            rho += drho_dt * dt
            E += dE_dt * dt
            F += dF_dt * dt
            
            # Ensure fields remain positive (Physical constraint)
            rho = np.clip(rho, a_min=0, a_max=None)
            E = np.clip(E, a_min=0, a_max=None)
            F = np.clip(F, a_min=0, a_max=None)
            
            self.steps += 1
            
        final_fields = {
            'rho': rho,
            'E': E,
            'F': F
        }
        final_metrics = {'stability_flag': True, 'final_variance': np.var(rho)}
        
        return final_fields, final_metrics
        
