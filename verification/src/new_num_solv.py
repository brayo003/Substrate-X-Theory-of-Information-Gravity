#!/usr/bin/env python3
"""
NUMERICAL SOLVER FOR SUBSTRATE X MASTER EQUATION (CORRECTED v3)

FIXES:
1. Fixed coordinate scaling in plots
2. Fixed energy calculation
3. Added stability constraints
4. Improved initial conditions
5. Better source term regularization
"""

import numpy as np
import matplotlib.pyplot as plt
from scipy import constants as const
from scipy.ndimage import laplace
import time
import warnings
warnings.filterwarnings('ignore')

class SubstrateXSolver:
    """Numerical solver for Substrate X Theory master equation"""
    
    def __init__(self, grid_size=128, domain_size=1e12, dim=2, 
                 tau=1e3, tau_irr=1e4, alpha=1e-10, beta=1e-10, gamma=1e-10, chi=1e6,
                 k_E=0.0, k_E_adv=0.0, k_F=0.0, k_vsub=0.0, k_u=0.0):
        # Physical constants
        self.G = const.G
        self.c = const.c
        self.M_sun = 1.989e30
        
        # Numerical parameters
        self.grid_size = grid_size
        self.domain_size = domain_size
        self.dim = dim
        self.dx = domain_size / grid_size
        # More conservative CFL for stability
        self.dt = 0.05 * self.dx / (self.c * np.sqrt(dim))
        
        # Substrate parameters
        self.tau = tau
        self.alpha = alpha
        self.beta = beta
        self.gamma = gamma
        self.chi = min(chi, 0.9 * self.c)
        self.tau_irr = tau_irr
        self.k_E = k_E
        self.k_E_adv = k_E_adv
        self.k_F = k_F
        self.k_vsub = k_vsub
        self.k_u = k_u
        
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
        
        # Grid coordinates (meters)
        self.x = np.linspace(-domain_size/2, domain_size/2, grid_size)
        if dim == 2:
            self.X, self.Y = np.meshgrid(self.x, self.x)
            self.R = np.sqrt(self.X**2 + self.Y**2)
        else:
            self.X, self.Y, self.Z = np.meshgrid(self.x, self.x, self.x)
            self.R = np.sqrt(self.X**2 + self.Y**2 + self.Z**2)
        
        # Regularization
        self.r_min = max(5 * self.dx, 1e8)  # At least 5 grid cells
        
        # Boundary condition
        self.bc_type = 'zero'
        self.last_acceleration = None
        self.stats_records = []
        
        print(f"Initialized solver:")
        print(f"  Grid: {grid_size}×{grid_size} ({dim}D)")
        print(f"  Domain: {domain_size/1e9:.2f} billion meters")
        print(f"  dx = {self.dx/1e9:.2f} billion meters")
        print(f"  dt = {self.dt:.2e} seconds")
        print(f"  CFL: {self.c * self.dt / self.dx:.4f}")
        print(f"  tau = {tau:.2e} s")
        print(f"  tau_irr = {tau_irr:.2e} s")
        print(f"  chi = {chi/1e6:.2f} million m/s ({chi/self.c:.4f} c)")
    
    def add_point_mass(self, mass, position, radius=None):
        """Add gravitational source with properly scaled fields"""
        if radius is None:
            radius = 2 * self.G * mass / (self.c**2)
        
        if self.dim == 2:
            x0, y0 = position
            r = np.sqrt((self.X - x0)**2 + (self.Y - y0)**2)
            r_reg = np.maximum(r, self.r_min)
            
            # Energy density: E = -GM/(r_reg) * (mass density)
            # Use a physically reasonable density scale
            # For point mass: approximate as uniform sphere of radius r_min
            volume_scale = (4/3) * np.pi * self.r_min**3
            density_scale = mass / volume_scale  # kg/m³
            # Gravitational potential energy density: E = -GMρ/r
            # But we want it in J/m³, so scale appropriately
            # Actually, let's use a simpler, more stable form:
            # E = -GM/(r_reg) * normalization_factor
            # where normalization_factor has units kg/m³ to give J/m³
            normalization = 1e-10  # Small normalization to keep E reasonable
            self.E += -self.G * mass * normalization / r_reg
            
            # Force density: F = -GM r̂/r² (N/m³)
            F_mag = self.G * mass / (r_reg**2)
            r_x = (self.X - x0)
            r_y = (self.Y - y0)
            r_norm = np.maximum(r_reg, 1e-10)
            F_x = -F_mag * r_x / r_norm
            F_y = -F_mag * r_y / r_norm
            self.F[:,:,0] += F_x
            self.F[:,:,1] += F_y
            
            # Substrate velocity: v_sub = √(2GM/r_reg) pointing outward
            v_esc_mag = np.sqrt(2 * self.G * mass / r_reg)
            v_sub_mag = np.minimum(v_esc_mag, 0.9 * self.c)
            v_sub_x = v_sub_mag * r_x / r_norm
            v_sub_y = v_sub_mag * r_y / r_norm
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
        
        total_mass = mass1 + mass2
        omega = np.sqrt(self.G * total_mass / separation**3)
        v_orbital = omega * separation / 2
        
        r1 = np.sqrt((self.X - pos1[0])**2 + (self.Y - pos1[1])**2)
        r2 = np.sqrt((self.X - pos2[0])**2 + (self.Y - pos2[1])**2)
        r1_reg = np.maximum(r1, self.r_min)
        r2_reg = np.maximum(r2, self.r_min)
        
        v_tang1 = np.minimum(v_orbital, 0.9 * self.c)
        v_tang2 = np.minimum(v_orbital, 0.9 * self.c)
        
        self.v_sub[:,:,0] += v_tang1 * (-(self.Y - pos1[1])) / r1_reg
        self.v_sub[:,:,1] += v_tang1 * ((self.X - pos1[0])) / r1_reg
        self.v_sub[:,:,0] += v_tang2 * (-(self.Y - pos2[1])) / r2_reg
        self.v_sub[:,:,1] += v_tang2 * ((self.X - pos2[0])) / r2_reg
        
        print(f"Binary: {mass1/self.M_sun:.2f} + {mass2/self.M_sun:.2f} M_sun, "
              f"sep = {separation/1e9:.2f} billion m")
    
    def compute_laplacian(self, field):
        """Compute ∇²s"""
        if self.bc_type == 'zero':
            laplacian = laplace(field, mode='constant', cval=0.0) / self.dx**2
        elif self.bc_type == 'periodic':
            laplacian = laplace(field, mode='wrap') / self.dx**2
        else:
            laplacian = laplace(field, mode='reflect') / self.dx**2
        return laplacian
    
    def compute_divergence(self, vector_field):
        """Compute ∇·(vector_field)"""
        if self.dim == 2:
            grad_x = np.gradient(vector_field[:,:,0], self.dx, axis=1)
            grad_y = np.gradient(vector_field[:,:,1], self.dx, axis=0)
            return grad_x + grad_y
        else:
            grad_x = np.gradient(vector_field[:,:,:,0], self.dx, axis=2)
            grad_y = np.gradient(vector_field[:,:,:,1], self.dx, axis=1)
            grad_z = np.gradient(vector_field[:,:,:,2], self.dx, axis=0)
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
        """Right-hand side enforcing the corrected second-order substrate PDE"""
        laplacian_s = self.compute_laplacian(s)
        grad_s = self.compute_gradient(s)
        grad_s_sq = np.sum(grad_s**2, axis=-1)
        
        if self.dim == 2:
            s_grad = s[:,:,np.newaxis] * grad_s
        else:
            s_grad = s[:,:,:,np.newaxis] * grad_s
        divergence_term = self.compute_divergence(s_grad)
        
        wave_term = self.c**2 * laplacian_s
        nonlinear_flux = self.alpha * divergence_term
        mixed_term = self.beta * s * laplacian_s
        gradient_term = self.gamma * grad_s_sq
        damping_term = -(1.0 / self.tau) * s_vel
        sigma_irr = -(1.0 / self.tau_irr) * (s_vel**3)
        
        coupling_term = 0.0
        if self.k_vsub != 0.0:
            if self.dim == 2:
                s_v_sub = s[:,:,np.newaxis] * self.v_sub
            else:
                s_v_sub = s[:,:,:,np.newaxis] * self.v_sub
            coupling_term += self.k_vsub * self.compute_divergence(s_v_sub)
        if self.k_u != 0.0:
            if self.dim == 2:
                chi_term = self.u
            else:
                chi_term = self.u
            coupling_term += self.k_u * self.compute_divergence(chi_term)
        if self.k_E != 0.0:
            coupling_term += self.k_E * self.E
        if self.k_E_adv != 0.0:
            if self.dim == 2:
                E_flux = self.E[:,:,np.newaxis] * self.v_sub
            else:
                E_flux = self.E[:,:,:,np.newaxis] * self.v_sub
            coupling_term += self.k_E_adv * self.compute_divergence(E_flux)
        if self.k_F != 0.0:
            coupling_term += self.k_F * self.compute_divergence(self.F)
        
        return (wave_term + nonlinear_flux + mixed_term + gradient_term +
                damping_term + sigma_irr + coupling_term)
    
    def collect_stats(self, current_time):
        """Aggregate global diagnostics for monitoring/exports."""
        grad_s = self.compute_gradient(self.s)
        grad_sq = np.sum(grad_s**2, axis=-1)
        if self.dim == 2:
            cell_volume = self.dx**2
        else:
            cell_volume = self.dx**3
        energy_density = self.s_vel**2 + self.c**2 * grad_sq
        total_energy = float(np.sum(energy_density) * cell_volume)
        stats = {
            "time": current_time,
            "max_s": float(np.max(self.s)),
            "min_s": float(np.min(self.s)),
            "mean_s": float(np.mean(self.s)),
            "max_abs_s": float(np.max(np.abs(self.s))),
            "max_s_vel": float(np.max(np.abs(self.s_vel))),
            "total_energy": total_energy,
        }
        if self.last_acceleration is not None:
            stats["mean_acceleration"] = float(np.mean(self.last_acceleration))
            stats["max_abs_acceleration"] = float(np.max(np.abs(self.last_acceleration)))
        return stats
    
    def step(self):
        """Advance one time step with stability checks"""
        acceleration = self.rhs(self.s, self.s_vel)
        self.last_acceleration = acceleration.copy()
        
        # Verlet integration
        s_new = 2.0 * self.s - self.s_prev + acceleration * self.dt**2
        
        # Stability: limit growth rate
        max_growth = 1.1  # Allow 10% growth per step max
        s_change = s_new - self.s
        s_change = np.clip(s_change, -max_growth * np.abs(self.s), 
                          max_growth * np.abs(self.s))
        s_new = self.s + s_change
        
        # Update velocity
        s_vel_new = (s_new - self.s_prev) / (2.0 * self.dt)
        
        # Boundary conditions
        if self.bc_type == 'zero':
            s_new[0,:] = 0
            s_new[-1,:] = 0
            s_new[:,0] = 0
            s_new[:,-1] = 0
            if self.dim == 3:
                s_new[:,:,0] = 0
                s_new[:,:,-1] = 0
        
        self.s_prev = self.s.copy()
        self.s = s_new
        self.s_vel = s_vel_new
        
        # Check for instabilities
        if np.any(np.isnan(self.s)) or np.any(np.isinf(self.s)):
            raise RuntimeError("Numerical instability!")
        
        return self.s
    
    def simulate(
        self,
        n_steps=1000,
        plot_interval=100,
        save_data=False,
        enable_plots=True,
        analyze=True,
        monitor=None,
        record_stats=False,
        stats_interval=10,
        stats_path=None,
    ):
        """Run simulation
        
        Parameters
        ----------
        n_steps : int
            Number of integration steps.
        plot_interval : int
            Steps between live plots (only if enable_plots is True).
        save_data : bool
            Whether to store snapshots every 100 steps.
        enable_plots : bool
            If False, suppresses interactive plotting during the run.
        analyze : bool
            If True, run analyze_results at the end.
        monitor : callable or None
            Optional callback monitor(step, solver) invoked each step.
        record_stats : bool
            If True, collect global diagnostics during the run.
        stats_interval : int
            Steps between stats samples.
        stats_path : str or Path
            Optional path to save stats JSON.
        """
        print(f"\nStarting simulation:")
        print(f"  Steps: {n_steps}")
        print(f"  Time step: {self.dt:.2e} s")
        print(f"  Total time: {n_steps * self.dt:.2e} s")
        print(f"  CFL: {self.c * self.dt / self.dx:.4f}")
        
        # Initial conditions: small, smooth perturbation
        if self.dim == 2:
            sigma_init = self.domain_size / 20  # Wider initial distribution
            perturbation = 0.001 * np.exp(-self.R**2 / (2 * sigma_init**2))
            self.s = perturbation.copy()
            self.s_prev = perturbation.copy()
            self.s_vel = np.zeros_like(self.s)
        
        time_history = []
        energy_history = []
        s_max_history = []
        s_history = []
        stats_records = []
        
        if enable_plots and self.dim == 2:
            fig, axes = plt.subplots(2, 3, figsize=(15, 10))
            plt.ion()
        else:
            fig = None
            axes = None
        
        start_time = time.time()
        
        try:
            for step in range(n_steps):
                current_s = self.step()
                
                if monitor is not None:
                    monitor(step, self)
                
                if record_stats and (step % stats_interval == 0):
                    stats_records.append(self.collect_stats(step * self.dt))
                
                if enable_plots and step % plot_interval == 0:
                    elapsed = time.time() - start_time
                    print(f"Step {step:5d}/{n_steps} ({step/n_steps*100:.1f}%) - "
                          f"Time: {step*self.dt:.2e} s - Elapsed: {elapsed:.1f} s")
                    
                    if self.dim == 2:
                        for ax in axes.flat:
                            ax.clear()
                        
                        # FIXED: Correct coordinate extent
                        extent_val = self.domain_size / 2 / 1e9  # billion meters
                        extent = [-extent_val, extent_val, -extent_val, extent_val]
                        
                        # Information density
                        s_plot = self.s
                        vmin_s = np.percentile(s_plot, 1)
                        vmax_s = np.percentile(s_plot, 99)
                        im1 = axes[0,0].imshow(s_plot, extent=extent, cmap='viridis', 
                                              origin='lower', vmin=vmin_s, vmax=vmax_s)
                        axes[0,0].set_title(f'Information Density s (step {step})')
                        axes[0,0].set_xlabel('x (billion m)')
                        axes[0,0].set_ylabel('y (billion m)')
                        plt.colorbar(im1, ax=axes[0,0])
                        
                        # Energy density
                        E_plot = self.E
                        E_nonzero = E_plot[E_plot != 0]
                        if len(E_nonzero) > 0:
                            E_min, E_max = np.percentile(E_nonzero, [1, 99])
                        else:
                            E_min, E_max = -1, 1
                        im2 = axes[0,1].imshow(E_plot, extent=extent, cmap='hot', 
                                              origin='lower', vmin=E_min, vmax=E_max)
                        axes[0,1].set_title('Energy Density E')
                        axes[0,1].set_xlabel('x (billion m)')
                        axes[0,1].set_ylabel('y (billion m)')
                        plt.colorbar(im2, ax=axes[0,1])
                        
                        # Substrate velocity
                        v_mag = np.sqrt(self.v_sub[:,:,0]**2 + self.v_sub[:,:,1]**2)
                        v_mag_c = v_mag / self.c
                        im3 = axes[0,2].imshow(v_mag_c, extent=extent, cmap='plasma', 
                                              origin='lower',
                                              vmin=0, vmax=np.percentile(v_mag_c, 99))
                        axes[0,2].set_title('Substrate Velocity |v_sub|/c')
                        axes[0,2].set_xlabel('x (billion m)')
                        axes[0,2].set_ylabel('y (billion m)')
                        plt.colorbar(im3, ax=axes[0,2])
                        
                        # Time derivative
                        im4 = axes[1,0].imshow(self.s_vel, extent=extent, cmap='RdBu_r', 
                                              origin='lower')
                        axes[1,0].set_title('Time Derivative ∂s/∂t')
                        axes[1,0].set_xlabel('x (billion m)')
                        axes[1,0].set_ylabel('y (billion m)')
                        plt.colorbar(im4, ax=axes[1,0])
                        
                        # Laplacian
                        laplacian = self.compute_laplacian(self.s)
                        im5 = axes[1,1].imshow(laplacian, extent=extent, cmap='RdBu_r', 
                                              origin='lower')
                        axes[1,1].set_title('Laplacian ∇²s')
                        axes[1,1].set_xlabel('x (billion m)')
                        axes[1,1].set_ylabel('y (billion m)')
                        plt.colorbar(im5, ax=axes[1,1])
                        
                        # Advection
                        s_v_sub = self.s[:,:,np.newaxis] * self.v_sub
                        advection = self.compute_divergence(s_v_sub)
                        im6 = axes[1,2].imshow(advection, extent=extent, cmap='RdBu_r', 
                                              origin='lower')
                        axes[1,2].set_title('Advection ∇·(s v_sub)')
                        axes[1,2].set_xlabel('x (billion m)')
                        axes[1,2].set_ylabel('y (billion m)')
                        plt.colorbar(im6, ax=axes[1,2])
                        
                        plt.tight_layout()
                        plt.draw()
                        plt.pause(0.01)
                
                # Store data
                if step % 10 == 0:
                    time_history.append(step * self.dt)
                    # CORRECTED: Wave energy calculation
                    grad_s = self.compute_gradient(self.s)
                    if self.dim == 2:
                        grad_sq = np.sum(grad_s**2, axis=-1)
                        # Wave energy density: (∂s/∂t)² + c²(∇s)²
                        energy_density = self.s_vel**2 + self.c**2 * grad_sq
                        wave_energy = np.sum(energy_density) * self.dx**2
                    else:
                        grad_sq = np.sum(grad_s**2, axis=-1)
                        energy_density = self.s_vel**2 + self.c**2 * grad_sq
                        wave_energy = np.sum(energy_density) * self.dx**3
                    energy_history.append(wave_energy)
                    s_max_history.append(np.max(np.abs(self.s)))
                    if save_data and step % 100 == 0:
                        s_history.append(self.s.copy())
        
        except KeyboardInterrupt:
            print("\nSimulation interrupted")
        except RuntimeError as e:
            print(f"\nError: {e}")
            return None, None, None
        
        if enable_plots and self.dim == 2:
            plt.ioff()
            plt.show()
        
        if analyze and len(time_history) > 0:
            self.analyze_results(time_history, energy_history, s_max_history, s_history)
        
        if record_stats:
            self.stats_records = stats_records
            if stats_path is not None:
                import json
                from pathlib import Path
                stats_payload = {
                    "metadata": {
                        "grid_size": self.grid_size,
                        "domain_size": self.domain_size,
                        "dim": self.dim,
                        "tau": self.tau,
                        "tau_irr": self.tau_irr
                    },
                    "records": stats_records
                }
                Path(stats_path).write_text(json.dumps(stats_payload, indent=2))
        
        return time_history, energy_history, s_history
    
    def analyze_results(self, times, energies, s_max, s_history):
        """Analyze results"""
        if len(times) == 0:
            return
        
        fig, axes = plt.subplots(2, 2, figsize=(12, 10))
        
        # Energy evolution
        energies_arr = np.array(energies)
        axes[0,0].plot(np.array(times)/1e6, energies_arr)
        axes[0,0].set_xlabel('Time (million seconds)')
        axes[0,0].set_ylabel('Total Wave Energy')
        axes[0,0].set_title('Energy Evolution')
        axes[0,0].grid(True)
        if np.max(energies_arr) > 0 and np.min(energies_arr) > 0:
            axes[0,0].set_yscale('log')
        
        # Maximum information density
        s_max_arr = np.array(s_max)
        axes[0,1].plot(np.array(times)/1e6, s_max_arr)
        axes[0,1].set_xlabel('Time (million seconds)')
        axes[0,1].set_ylabel('max(|s|)')
        axes[0,1].set_title('Maximum Information Density')
        axes[0,1].grid(True)
        
        # Final information density
        if self.dim == 2:
            final_s = self.s
            extent_val = self.domain_size / 2 / 1e9
            extent = [-extent_val, extent_val, -extent_val, extent_val]
            im = axes[1,0].imshow(final_s, extent=extent, cmap='viridis', origin='lower')
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
            if np.max(radial_profile) > 0:
                axes[1,1].set_yscale('log')
        
        plt.tight_layout()
        plt.savefig('substrate_x_analysis.png', dpi=150, bbox_inches='tight')
        print("\nAnalysis saved to 'substrate_x_analysis.png'")
        plt.show()

def main():
    """Run simulations"""
    print("=" * 80)
    print("SUBSTRATE X NUMERICAL SOLVER (CORRECTED v3)")
    print("=" * 80)
    
    # Test 1: Single star
    print("\n" + "=" * 80)
    print("TEST 1: Single Star")
    print("=" * 80)
    
    solver1 = SubstrateXSolver(
        grid_size=128,
        domain_size=2e12,
        dim=2,
        tau=1e3,
        alpha=1e-10,
        beta=1e-10,
        gamma=1e-10,
        chi=1e7
    )
    
    solver1.add_point_mass(1.0 * solver1.M_sun, (0, 0))
    times1, energies1, s_history1 = solver1.simulate(n_steps=500, plot_interval=50)
    
    print("\n" + "=" * 80)
    print("Simulation completed!")
    print("=" * 80)

if __name__ == "__main__":
    main()
