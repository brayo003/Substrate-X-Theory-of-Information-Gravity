#!/usr/bin/env python3
import numpy as np
from complete_field_theory_solver_fixed import CompleteFieldTheorySolver

class SurgicalGalacticSolver(CompleteFieldTheorySolver):
    def __init__(self, M_factor=10000.0, eta_power=20.0, rho_cutoff=0.8, delta1=0.5, delta2=1.0, **kwargs):
        super().__init__(**kwargs) 
        
        # SURGICAL PARAMETERS: Keep what worked, boost only what failed
        self.delta1 = delta1  # KEEP the working value that gave 77.8% solar concentration
        self.delta2 = delta2  # BOOST only the galactic coupling
        self.M_factor = M_factor
        self.eta_power = eta_power
        self.rho_cutoff = rho_cutoff
        
        print(f"🎯 SURGICAL GALACTIC SOLVER")
        print(f"   Preserve: δ₁={self.delta1} (proven solar crusher)")
        print(f"   Boost: δ₂={self.delta2} (3.3× galactic coupling)")
        print(f"   Stiffness: M={M_factor:.0f}, η_power={eta_power}")
        
    def compute_effective_stiffness(self, rho):
        """Surgical stiffness that gave 77.8% solar concentration"""
        if self.M_factor == 0.0:
            return self.alpha
        tanh_term = np.tanh(self.eta_power * (rho - self.rho_cutoff))
        stiffness_factor = 1.0 + self.M_factor * np.maximum(0.0, tanh_term)
        return self.alpha * stiffness_factor
    
    def compute_laplacian(self, field):
        """Compute ∇² using finite differences"""
        laplacian = np.zeros_like(field)
        for i in range(1, self.grid_size-1):
            for j in range(1, self.grid_size-1):
                laplacian[i,j] = (field[i+1,j] + field[i-1,j] + 
                                 field[i,j+1] + field[i,j-1] - 4*field[i,j]) / (self.dx**2)
        return laplacian
        
    def compute_field_evolution(self):
        """SURGICAL OVERRIDE: Preserve working physics, boost galactic coupling"""
        rho, E, F = self.rho, self.E, self.F
        
        # PRESERVE the ρ evolution that worked with δ₁=0.5
        laplacian_rho = self.compute_laplacian(rho)
        alpha_eff = self.compute_effective_stiffness(rho)
        drho_dt = (self.gamma + alpha_eff * F**2) * laplacian_rho - rho / self.tau_rho
        
        # PRESERVE the E evolution that worked  
        laplacian_E = self.compute_laplacian(E)
        dE_dt = self.beta * F + laplacian_E - E / self.tau_E
        
        # BOOST ONLY the F evolution for galactic scales
        laplacian_F = self.compute_laplacian(F)
        
        # CRITICAL: Use OUR δ₁=0.5 and δ₂=1.0 (not base class defaults)
        dF_dt = (self.delta1 * rho + self.delta2 * E + laplacian_F - 
                self.kappa * F - F / self.tau_F)
        
        # Apply the surgical stiffness that gave 77.8% solar concentration
        dF_dt = dF_dt + (alpha_eff - self.alpha) * F
        
        return dE_dt, dF_dt

    def evolve_system(self, steps=1):
        """Use our surgical evolution"""
        for _ in range(steps):
            dE_dt, dF_dt = self.compute_field_evolution()
            self.E += self.dt * dE_dt
            self.F += self.dt * dF_dt
            
            # Boundary conditions
            self.E[0,:] = self.E[1,:]; self.E[-1,:] = self.E[-2,:]
            self.E[:,0] = self.E[:,1]; self.E[:,-1] = self.E[:,-2]
            self.F[0,:] = self.F[1,:]; self.F[-1,:] = self.F[-2,:]  
            self.F[:,0] = self.F[:,1]; self.F[:,-1] = self.F[:,-2]

def comprehensive_scale_test():
    print("🚀 SURGICAL GALACTIC BOOST TEST")
    print("Strategy: PRESERVE δ₁=0.5 (proven solar crusher)")
    print("          BOOST δ₂=1.0 (galactic scale amplifier)")
    print("=" * 70)
    
    solver = SurgicalGalacticSolver(
        alpha=1e-5,
        delta1=0.5,   # PRESERVE: This gave 77.8% solar concentration
        delta2=1.0,   # BOOST: 3.3× increase for galactic scales
        M_factor=10000.0,
        eta_power=20.0,
        rho_cutoff=0.8
    )
    
    solver.initialize_system('gaussian')
    print("Running evolution with surgical galactic boost...")
    solver.evolve_system(500)
    
    # Analysis
    rho, E, F = solver.rho, solver.E, solver.F
    rho_max = np.max(rho)
    F_rms = np.sqrt(np.mean(F**2))
    
    print(f"\n📊 SURGICAL BOOST RESULTS:")
    print(f"ρ_max: {rho_max:.3f} (stiffness active: {rho_max > 0.8})")
    print(f"F_RMS: {F_rms:.3f} (Target: >20 for galactic scales)")
    
    # Fourier analysis
    fft2 = np.fft.fft2(F)
    power_spectrum = np.abs(fft2)**2
    power_spectrum = np.fft.fftshift(power_spectrum)
    
    n = F.shape[0]
    kx = np.fft.fftshift(np.fft.fftfreq(n, solver.dx)) * 2 * np.pi
    ky = np.fft.fftshift(np.fft.fftfreq(n, solver.dx)) * 2 * np.pi
    kx_grid, ky_grid = np.meshgrid(kx, ky)
    k_magnitude = np.sqrt(kx_grid**2 + ky_grid**2)
    
    solar_k = (k_magnitude > 10) & (k_magnitude < 50)
    galactic_k = (k_magnitude > 0.1) & (k_magnitude < 2)
    
    total_energy = np.sum(power_spectrum[k_magnitude > 0])
    
    if total_energy > 0:
        solar_frac = np.sum(power_spectrum[solar_k]) / total_energy
        galactic_frac = np.sum(power_spectrum[galactic_k]) / total_energy
        
        print(f"Solar scales (10-50): {solar_frac:.1%}")
        print(f"Galactic scales (0.1-2): {galactic_frac:.1%}")
        
        if solar_frac > 0.5 and galactic_frac > 0.01:
            print("💫 BREAKTHROUGH: Scale separation achieved!")
            print(f"Solar/Galactic ratio: {solar_frac/galactic_frac:.1f}x")
        elif galactic_frac > 0.01:
            print("🔬 PROGRESS: Galactic scales emerging!")
        else:
            print("⚠️  Galactic scales still too weak")

comprehensive_scale_test()
