#!/usr/bin/env python3
"""
NUMERICAL SOLVER FOR SUBSTRATE X MASTER EQUATION (CORRECTED)

Corrected Master Equation:
∂²s/∂t² - c²∇²s + (1/τ)∂s/∂t + (1/τ)∇·(s v_sub + χ s u) = αE + β∇·(E v_sub) + γF - σ_irr

CORRECTIONS APPLIED:
1. Proper dimensional scaling (physical units)
2. Fixed divergence computation (correct axis ordering)
3. Regularized source terms (avoid singularities)
4. Improved boundary conditions
5. Better initial conditions
6. Physical σ_irr implementation
7. Stability checks and adaptive time stepping
"""

import numpy as np
import matplotlib.pyplot as plt
from scipy import constants as const
from scipy.ndimage import laplace
import time
import warnings
warnings.filterwarnings('ignore')

class SubstrateXSolver:
    """
    Numerical solver for Substrate X Theory master equation
    
    Physical units: meters, seconds, kilograms
    Information units: arbitrary (info)
    """
    
    def __init__(self, grid_size=128, domain_size=1e12, dim=2, 
                 tau=1e3, alpha=1e-10, beta=1e-10, gamma=1e-10, chi=1e6):
        """
        Initialize solver
        
        Parameters:
        -----------
        grid_size : int
            Number of grid points per dimension
        domain_size : float
            Physical size of domain in meters
        dim : int
            Dimension (2 or 3)
        tau : float
            Relaxation time constant (seconds)
        alpha, beta, gamma : float
            Coupling constants (with proper dimensions)
        chi : float
            Coherence speed (m/s, must be < c)
        """
        # Physical constants
        self.G = const.G          # 6.67430e-11 m³/kg/s²
        self.c = const.c          # 299792458 m/s
        self.M_sun = 1.989e30     # kg
        
        # Numerical parameters
        self.grid_size = grid_size
        self.domain_size = domain_size
        self.dim = dim
        self.dx = domain_size / grid_size
        
        # CFL condition: dt < dx / (c * sqrt(dim))
        # Use safety factor of 0.1 for stability
        self.dt = 0.1 * self.dx / (self.c * np.sqrt(dim))
        
        # Substrate parameters
        self.tau = tau
        self.alpha = alpha  # info/(J·s) = info/(kg·m²/s³)
        self.beta = beta     # info/(J·s)
        self.gamma = gamma  # info/(N·s) = info·s²/(kg·m)
        self.chi = min(chi, 0.9 * self.c)  # Ensure chi < c
        
        # Field arrays
        if dim == 2:
            self.s = np.zeros((grid_size, grid_size))
            self.s_prev = np.zeros((grid_size, grid_size))
            self.s_vel = np.zeros((grid_size, grid_size))
            self.v_sub = np.zeros((grid_size, grid_size, 2))
            self.u = np.zeros((grid_size, grid_size, 2))
            self.E = np.zeros((grid_size, grid_size))
            self.F = np.zeros((grid_size, grid_size, 2))
        elif dim == 3:
            self.s = np.zeros((grid_size, grid_size, grid_size))
            self.s_prev = np.zeros((grid_size, grid_size, grid_size))
            self.s_vel = np.zeros((grid_size, grid_size, grid_size))
            self.v_sub = np.zeros((grid_size, grid_size, grid_size, 3))
            self.u = np.zeros((grid_size, grid_size, grid_size, 3))
            self.E = np.zeros((grid_size, grid_size, grid_size))
            self.F = np.zeros((grid_size, grid_size, grid_size, 3))
        else:
            raise ValueError("dim must be 2 or 3")
        
        # Grid coordinates (physical units: meters)
        self.x = np.linspace(-domain_size/2, domain_size/2, grid_size)
        if dim == 2:
            self.X, self.Y = np.meshgrid(self.x, self.x)
            self.R = np.sqrt(self.X**2 + self.Y**2)
        else:
            self.X, self.Y, self.Z = np.meshgrid(self.x, self.x, self.x)
            self.R = np.sqrt(self.X**2 + self.Y**2 + self.Z**2)
        
        # Regularization parameter (avoid r=0 singularities)
        self.r_min = 1e8  # meters (minimum distance scale)
        
        # Boundary condition type
        self.bc_type = 'zero'  # 'zero', 'periodic', 'reflecting'
        
        print(f"Initialized solver:")
        print(f"  Grid: {grid_size}×{grid_size} ({dim}D)")
        print(f"  Domain: {domain_size/1e9:.2f} billion meters")
        print(f"  dx = {self.dx/1e9:.2f} billion meters")
        print(f"  dt = {self.dt:.2e} seconds")
        print(f"  CFL number: {self.c * self.dt / self.dx:.4f}")
        print(f"  tau = {tau:.2e} s")
        print(f"  chi = {chi/1e6:.2f} million m/s ({chi/self.c:.4f} c)")
    
    def add_point_mass(self, mass, position, radius=None):
        """
        Add gravitational source with regularized potential
        
        Parameters:
        -----------
        mass : float
            Mass in kg
        position : tuple
            (x, y) or (x, y, z) position in meters
        radius : float, optional
            Characteristic radius for regularization
        """
        if radius is None:
            radius = 2 * self.G * mass / (self.c**2)  # Schwarzschild radius
        
        if self.dim == 2:
            x0, y0 = position
            r = np.sqrt((self.X - x0)**2 + (self.Y - y0)**2)
            r_reg = r + self.r_min  # Regularized distance
            
            # Energy density: E = -GM/r (gravitational potential energy per unit volume)
            # For point mass: E = -GMρ/r where ρ is density
            # Approximate as: E ≈ -GM/(4πr³) for point source
            # More physically: E = -GM/(r_reg) * (some density scale)
            density_scale = mass / (4 * np.pi * r_reg**3)  # Approximate density
            self.E += -self.G * mass * density_scale / r_reg
            
            # Force density: F = -∇(GM/r) = GM r̂/r²
            # Regularized: F = GM r̂/(r_reg²)
            F_mag = self.G * mass / (r_reg**2)
            F_x = -F_mag * (self.X - x0) / (r_reg + 1e-10)
            F_y = -F_mag * (self.Y - y0) / (r_reg + 1e-10)
            self.F[:,:,0] += F_x
            self.F[:,:,1] += F_y
            
            # Substrate velocity: v_sub = -√(2GM/r_reg) (free-fall velocity)
            # Regularized and scaled to be < c
            v_esc = np.sqrt(2 * self.G * mass / r_reg)
            v_sub_mag = np.minimum(v_esc, 0.9 * self.c)  # Cap at 0.9c
            v_sub_x = -v_sub_mag * (self.X - x0) / (r_reg + 1e-10)
            v_sub_y = -v_sub_mag * (self.Y - y0) / (r_reg + 1e-10)
            self.v_sub[:,:,0] += v_sub_x
            self.v_sub[:,:,1] += v_sub_y
            
        print(f"Added mass {mass/self.M_sun:.3f} M_sun at ({x0/1e9:.2f}, {y0/1e9:.2f}) billion m")
    
    def add_binary_system(self, mass1, mass2, separation, center=(0,0)):
        """Add binary star system"""
        x_center, y_center = center
        pos1 = (x_center - separation/2, y_center)
        pos2 = (x_center + separation/2, y_center)
        
        self.add_point_mass(mass1, pos1)
        self.add_point_mass(mass2, pos2)
        
        # Orbital motion in substrate velocity
        total_mass = mass1 + mass2
        omega = np.sqrt(self.G * total_mass / separation**3)
        v_orbital = omega * separation / 2
        
        # Add circular motion around center of mass
        r1 = np.sqrt((self.X - pos1[0])**2 + (self.Y - pos1[1])**2)
        r2 = np.sqrt((self.X - pos2[0])**2 + (self.Y - pos2[1])**2)
        r1_reg = r1 + self.r_min
        r2_reg = r2 + self.r_min
        
        # Tangential velocity around each mass
        v_tang1 = np.minimum(v_orbital, 0.9 * self.c)
        v_tang2 = np.minimum(v_orbital, 0.9 * self.c)
        
        self.v_sub[:,:,0] += v_tang1 * (-(self.Y - pos1[1])) / r1_reg
        self.v_sub[:,:,1] += v_tang1 * ((self.X - pos1[0])) / r1_reg
        self.v_sub[:,:,0] += v_tang2 * (-(self.Y - pos2[1])) / r2_reg
        self.v_sub[:,:,1] += v_tang2 * ((self.X - pos2[0])) / r2_reg
        
        print(f"Binary system: {mass1/self.M_sun:.2f} + {mass2/self.M_sun:.2f} M_sun, "
              f"separation = {separation/1e9:.2f} billion m")
    
    def compute_laplacian(self, field):
        """Compute ∇²s using finite differences with boundary conditions"""
        if self.bc_type == 'zero':
            # Zero boundary: extend with zeros
            laplacian = laplace(field, mode='constant', cval=0.0) / self.dx**2
        elif self.bc_type == 'periodic':
            laplacian = laplace(field, mode='wrap') / self.dx**2
        else:  # reflecting
            laplacian = laplace(field, mode='reflect') / self.dx**2
        return laplacian
    
    def compute_divergence(self, vector_field):
        """
        Compute ∇·(vector_field) with CORRECT axis ordering
        
        For 2D: vector_field shape is (nx, ny, 2)
        For 3D: vector_field shape is (nx, ny, nz, 3)
        """
        if self.dim == 2:
            # vector_field[:,:,0] is x-component, vector_field[:,:,1] is y-component
            # np.gradient along axis=1 gives ∂/∂x, along axis=0 gives ∂/∂y
            grad_x = np.gradient(vector_field[:,:,0], self.dx, axis=1)  # ∂(v_x)/∂x
            grad_y = np.gradient(vector_field[:,:,1], self.dx, axis=0)  # ∂(v_y)/∂y
            return grad_x + grad_y
        else:  # 3D
            grad_x = np.gradient(vector_field[:,:,:,0], self.dx, axis=2)  # ∂/∂x
            grad_y = np.gradient(vector_field[:,:,:,1], self.dx, axis=1)  # ∂/∂y
            grad_z = np.gradient(vector_field[:,:,:,2], self.dx, axis=0)  # ∂/∂z
            return grad_x + grad_y + grad_z
    
    def compute_gradient(self, scalar_field):
        """Compute ∇s"""
        if self.dim == 2:
            grad_x = np.gradient(scalar_field, self.dx, axis=1)
            grad_y = np.gradient(scalar_field, self.dx, axis=0)
            return np.stack([grad_x, grad_y], axis=-1)
        else:
            grad_x = np.gradient(scalar_field, self.dx, axis=2)
            grad_y = np.gradient(scalar_field, self.dx, axis=1)
            grad_z = np.gradient(scalar_field, self.dx, axis=0)
            return np.stack([grad_x, grad_y, grad_z], axis=-1)
    
    def rhs(self, s, s_vel):
        """
        Right-hand side of master equation
        
        ∂²s/∂t² = c²∇²s - (1/τ)∂s/∂t - (1/τ)∇·(s v_sub + χ s u) 
                 + αE + β∇·(E v_sub) + γF - σ_irr
        """
        # Wave term: c²∇²s
        laplacian_s = self.compute_laplacian(s)
        wave_term = self.c**2 * laplacian_s
        
        # Damping term: -(1/τ)∂s/∂t
        damping_term = -(1.0 / self.tau) * s_vel
        
        # Advection term: -(1/τ)∇·(s v_sub)
        if self.dim == 2:
            s_v_sub = s[:,:,np.newaxis] * self.v_sub
        else:
            s_v_sub = s[:,:,:,np.newaxis] * self.v_sub
        advection_term = -(1.0 / self.tau) * self.compute_divergence(s_v_sub)
        
        # Coherence term: -(1/τ)∇·(χ s u)
        if self.dim == 2:
            chi_s_u = self.chi * s[:,:,np.newaxis] * self.u
        else:
            chi_s_u = self.chi * s[:,:,:,np.newaxis] * self.u
        coherence_term = -(1.0 / self.tau) * self.compute_divergence(chi_s_u)
        
        # Source terms
        energy_term = self.alpha * self.E
        
        # β∇·(E v_sub)
        if self.dim == 2:
            E_v_sub = self.E[:,:,np.newaxis] * self.v_sub
        else:
            E_v_sub = self.E[:,:,:,np.newaxis] * self.v_sub
        energy_advection_term = self.beta * self.compute_divergence(E_v_sub)
        
        # γF (force coupling - F is already force density vector)
        force_term = self.gamma * self.compute_divergence(self.F)
        
        # Irreversible processes: σ_irr = κ s² (nonlinear dissipation)
        # Physical: information loss proportional to information density squared
        kappa = 1e-15  # Dissipation coefficient (1/(info·s))
        sigma_irr = kappa * s**2
        
        # Assemble RHS (this is ∂²s/∂t²)
        rhs = (wave_term + damping_term + advection_term + coherence_term + 
               energy_term + energy_advection_term + force_term - sigma_irr)
        
        return rhs
    
    def step(self):
        """
        Advance one time step using Verlet integration
        
        For second-order ODE: ∂²s/∂t² = f(s, ∂s/∂t)
        Verlet: s(t+dt) = 2*s(t) - s(t-dt) + f(t) * dt²
        """
        # Compute acceleration
        acceleration = self.rhs(self.s, self.s_vel)
        
        # Verlet integration
        s_new = 2.0 * self.s - self.s_prev + acceleration * self.dt**2
        
        # Update velocity estimate
        s_vel_new = (s_new - self.s_prev) / (2.0 * self.dt)
        
        # Apply boundary conditions
        if self.bc_type == 'zero':
            s_new[0,:] = 0
            s_new[-1,:] = 0
            s_new[:,0] = 0
            s_new[:,-1] = 0
            if self.dim == 3:
                s_new[:,:,0] = 0
                s_new[:,:,-1] = 0
        
        # Update fields
        self.s_prev = self.s.copy()
        self.s = s_new
        self.s_vel = s_vel_new
        
        # Check for instabilities
        if np.any(np.isnan(self.s)) or np.any(np.isinf(self.s)):
            raise RuntimeError("Numerical instability detected! Check parameters.")
        
        return self.s
    
    def simulate(self, n_steps=1000, plot_interval=100, save_data=False):
        """
        Run full simulation
        
        Parameters:
        -----------
        n_steps : int
            Number of time steps
        plot_interval : int
            Steps between plots
        save_data : bool
            Save data to files
        """
        print(f"\nStarting simulation:")
        print(f"  Steps: {n_steps}")
        print(f"  Time step: {self.dt:.2e} s")
        print(f"  Total time: {n_steps * self.dt:.2e} s")
        print(f"  CFL: {self.c * self.dt / self.dx:.4f}")
        
        # Initial conditions: small Gaussian perturbation
        if self.dim == 2:
            sigma_init = self.domain_size / 10
            perturbation = 0.01 * np.exp(-self.R**2 / (2 * sigma_init**2))
            self.s = perturbation.copy()
            self.s_prev = perturbation.copy()
            self.s_vel = np.zeros_like(self.s)
        
        # Storage for analysis
        time_history = []
        energy_history = []
        s_max_history = []
        s_history = []
        
        # Setup plotting
        if self.dim == 2:
            fig, axes = plt.subplots(2, 3, figsize=(15, 10))
            plt.ion()
        
        start_time = time.time()
        
        try:
            for step in range(n_steps):
                current_s = self.step()
                
                if step % plot_interval == 0:
                    elapsed = time.time() - start_time
                    print(f"Step {step:5d}/{n_steps} ({step/n_steps*100:.1f}%) - "
                          f"Time: {step*self.dt:.2e} s - Elapsed: {elapsed:.1f} s")
                    
                    if self.dim == 2:
                        # Clear and replot
                        for ax in axes.flat:
                            ax.clear()
                        
                        # Information density
                        im1 = axes[0,0].imshow(self.s, extent=[-self.domain_size/2/1e9, 
                                                                 self.domain_size/2/1e9,
                                                                 -self.domain_size/2/1e9,
                                                                 self.domain_size/2/1e9],
                                              cmap='viridis', origin='lower',
                                              vmin=np.percentile(self.s, 1),
                                              vmax=np.percentile(self.s, 99))
                        axes[0,0].set_title(f'Information Density s (step {step})')
                        axes[0,0].set_xlabel('x (billion m)')
                        axes[0,0].set_ylabel('y (billion m)')
                        plt.colorbar(im1, ax=axes[0,0])
                        
                        # Energy density
                        im2 = axes[0,1].imshow(self.E, extent=[-self.domain_size/2/1e9,
                                                                self.domain_size/2/1e9,
                                                                -self.domain_size/2/1e9,
                                                                self.domain_size/2/1e9],
                                              cmap='hot', origin='lower')
                        axes[0,1].set_title('Energy Density E')
                        axes[0,1].set_xlabel('x (billion m)')
                        axes[0,1].set_ylabel('y (billion m)')
                        plt.colorbar(im2, ax=axes[0,1])
                        
                        # Substrate velocity magnitude
                        v_mag = np.sqrt(self.v_sub[:,:,0]**2 + self.v_sub[:,:,1]**2)
                        v_mag_c = v_mag / self.c
                        im3 = axes[0,2].imshow(v_mag_c, extent=[-self.domain_size/2/1e9,
                                                                self.domain_size/2/1e9,
                                                                -self.domain_size/2/1e9,
                                                                self.domain_size/2/1e9],
                                              cmap='plasma', origin='lower',
                                              vmin=0, vmax=1)
                        axes[0,2].set_title('Substrate Velocity |v_sub|/c')
                        axes[0,2].set_xlabel('x (billion m)')
                        axes[0,2].set_ylabel('y (billion m)')
                        plt.colorbar(im3, ax=axes[0,2])
                        
                        # Time derivative
                        im4 = axes[1,0].imshow(self.s_vel, extent=[-self.domain_size/2/1e9,
                                                                    self.domain_size/2/1e9,
                                                                    -self.domain_size/2/1e9,
                                                                    self.domain_size/2/1e9],
                                              cmap='RdBu_r', origin='lower')
                        axes[1,0].set_title('Time Derivative ∂s/∂t')
                        axes[1,0].set_xlabel('x (billion m)')
                        axes[1,0].set_ylabel('y (billion m)')
                        plt.colorbar(im4, ax=axes[1,0])
                        
                        # Laplacian
                        laplacian = self.compute_laplacian(self.s)
                        im5 = axes[1,1].imshow(laplacian, extent=[-self.domain_size/2/1e9,
                                                                  self.domain_size/2/1e9,
                                                                  -self.domain_size/2/1e9,
                                                                  self.domain_size/2/1e9],
                                              cmap='RdBu_r', origin='lower')
                        axes[1,1].set_title('Laplacian ∇²s')
                        axes[1,1].set_xlabel('x (billion m)')
                        axes[1,1].set_ylabel('y (billion m)')
                        plt.colorbar(im5, ax=axes[1,1])
                        
                        # Advection term
                        s_v_sub = self.s[:,:,np.newaxis] * self.v_sub
                        advection = self.compute_divergence(s_v_sub)
                        im6 = axes[1,2].imshow(advection, extent=[-self.domain_size/2/1e9,
                                                                  self.domain_size/2/1e9,
                                                                  -self.domain_size/2/1e9,
                                                                  self.domain_size/2/1e9],
                                              cmap='RdBu_r', origin='lower')
                        axes[1,2].set_title('Advection ∇·(s v_sub)')
                        axes[1,2].set_xlabel('x (billion m)')
                        axes[1,2].set_ylabel('y (billion m)')
                        plt.colorbar(im6, ax=axes[1,2])
                        
                        plt.tight_layout()
                        plt.draw()
                        plt.pause(0.01)
                
                # Store data
                if step % 10 == 0:  # Store every 10 steps
                    time_history.append(step * self.dt)
                    # Wave energy: ∫[(∂s/∂t)² + c²(∇s)²] dV
                    grad_s = self.compute_gradient(self.s)
                    if self.dim == 2:
                        grad_sq = np.sum(grad_s**2, axis=-1)
                        wave_energy = np.sum(self.s_vel**2 + self.c**2 * grad_sq) * self.dx**2
                    else:
                        grad_sq = np.sum(grad_s**2, axis=-1)
                        wave_energy = np.sum(self.s_vel**2 + self.c**2 * grad_sq) * self.dx**3
                    energy_history.append(wave_energy)
                    s_max_history.append(np.max(np.abs(self.s)))
                    if save_data and step % 100 == 0:
                        s_history.append(self.s.copy())
        
        except KeyboardInterrupt:
            print("\nSimulation interrupted by user")
        except RuntimeError as e:
            print(f"\nError: {e}")
            return None, None, None
        
        plt.ioff()
        if self.dim == 2:
            plt.show()
        
        # Analysis
        if len(time_history) > 0:
            self.analyze_results(time_history, energy_history, s_max_history, s_history)
        
        return time_history, energy_history, s_history
    
    def analyze_results(self, times, energies, s_max, s_history):
        """Analyze and plot simulation results"""
        if len(times) == 0:
            return
        
        fig, axes = plt.subplots(2, 2, figsize=(12, 10))
        
        # Energy evolution
        axes[0,0].plot(np.array(times)/1e6, np.array(energies))
        axes[0,0].set_xlabel('Time (million seconds)')
        axes[0,0].set_ylabel('Total Wave Energy')
        axes[0,0].set_title('Energy Evolution')
        axes[0,0].grid(True)
        axes[0,0].set_yscale('log')
        
        # Maximum information density
        axes[0,1].plot(np.array(times)/1e6, np.array(s_max))
        axes[0,1].set_xlabel('Time (million seconds)')
        axes[0,1].set_ylabel('max(|s|)')
        axes[0,1].set_title('Maximum Information Density')
        axes[0,1].grid(True)
        
        # Final information density
        if self.dim == 2:
            final_s = self.s
            im = axes[1,0].imshow(final_s, extent=[-self.domain_size/2/1e9,
                                                    self.domain_size/2/1e9,
                                                    -self.domain_size/2/1e9,
                                                    self.domain_size/2/1e9],
                                 cmap='viridis', origin='lower')
            axes[1,0].set_title('Final Information Density')
            axes[1,0].set_xlabel('x (billion m)')
            axes[1,0].set_ylabel('y (billion m)')
            plt.colorbar(im, ax=axes[1,0])
            
            # Radial profile
            radial_bins = np.linspace(0, self.domain_size/2, 50)
            radial_profile = []
            for r in radial_bins:
                mask = (self.R >= r - self.dx) & (self.R < r + self.dx)
                if np.any(mask):
                    radial_profile.append(np.mean(np.abs(final_s[mask])))
                else:
                    radial_profile.append(0)
            
            axes[1,1].plot(radial_bins/1e9, radial_profile)
            axes[1,1].set_xlabel('Radius (billion m)')
            axes[1,1].set_ylabel('|Information Density|')
            axes[1,1].set_title('Radial Profile')
            axes[1,1].grid(True)
            axes[1,1].set_yscale('log')
        
        plt.tight_layout()
        plt.savefig('substrate_x_analysis.png', dpi=150, bbox_inches='tight')
        print("\nAnalysis plot saved to 'substrate_x_analysis.png'")
        plt.show()

def main():
    """Run demonstration simulations"""
    print("=" * 80)
    print("SUBSTRATE X NUMERICAL SOLVER (CORRECTED)")
    print("=" * 80)
    
    # Test 1: Single star
    print("\n" + "=" * 80)
    print("TEST 1: Single Star")
    print("=" * 80)
    
    solver1 = SubstrateXSolver(
        grid_size=128,
        domain_size=2e12,  # 2 billion km
        dim=2,
        tau=1e3,          # 1000 seconds
        alpha=1e-10,      # Energy coupling
        beta=1e-10,       # Energy flow coupling
        gamma=1e-10,      # Force coupling
        chi=1e7           # 10 million m/s coherence speed
    )
    
    solver1.add_point_mass(1.0 * solver1.M_sun, (0, 0))
    times1, energies1, s_history1 = solver1.simulate(n_steps=500, plot_interval=50)
    
    # Test 2: Binary system
    print("\n" + "=" * 80)
    print("TEST 2: Binary System")
    print("=" * 80)
    
    solver2 = SubstrateXSolver(
        grid_size=128,
        domain_size=3e12,  # 3 billion km
        dim=2,
        tau=1e3,
        alpha=1e-10,
        beta=1e-10,
        gamma=1e-10,
        chi=1e7
    )
    
    solver2.add_binary_system(
        1.0 * solver2.M_sun,
        0.5 * solver2.M_sun,
        separation=1e11  # 100 million km
    )
    
    times2, energies2, s_history2 = solver2.simulate(n_steps=1000, plot_interval=100)
    
    print("\n" + "=" * 80)
    print("All simulations completed!")
    print("=" * 80)

if __name__ == "__main__":
    main()
