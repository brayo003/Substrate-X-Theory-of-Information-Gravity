#!/usr/bin/env python3
import numpy as np
from complete_field_theory_solver_fixed import CompleteFieldTheorySolver

class DiagnosticHybridSolver(CompleteFieldTheorySolver):
    def __init__(self, M_factor=10000.0, eta_power=20.0, rho_cutoff=0.8, delta1=0.5, delta2=1.0, **kwargs):
        super().__init__(**kwargs) 
        
        self.delta1 = delta1  
        self.delta2 = delta2
        self.M_factor = M_factor
        self.eta_power = eta_power
        self.rho_cutoff = rho_cutoff
        
        print(f"🔍 DIAGNOSTIC HYBRID SOLVER")
        print(f"   Testing δ₁={self.delta1}, δ₂={self.delta2}")
        
    def compute_effective_stiffness(self, rho):
        if self.M_factor == 0.0:
            return self.alpha
        tanh_term = np.tanh(self.eta_power * (rho - self.rho_cutoff))
        stiffness_factor = 1.0 + self.M_factor * np.maximum(0.0, tanh_term)
        return self.alpha * stiffness_factor
        
    def compute_field_evolution(self):
        """DIAGNOSTIC: Compare base vs our evolution"""
        rho, E, F = self.rho, self.E, self.F
        
        # Get BASE evolution (with wrong parameters but correct dynamics)
        dE_dt_base, dF_dt_base = super().compute_field_evolution()
        
        # DIAGNOSTIC: Print what the base class is actually doing
        if hasattr(self, 'step_count'):
            self.step_count += 1
        else:
            self.step_count = 0
            
        if self.step_count % 100 == 0:
            print(f"🔍 Step {self.step_count}:")
            print(f"   Base F evolution - Max: {np.max(dF_dt_base):.3f}, Min: {np.min(dF_dt_base):.3f}")
            print(f"   Current F field - Max: {np.max(F):.3f}, RMS: {np.sqrt(np.mean(F**2)):.3f}")
        
        # Apply our stiffness modification to whatever base gives us
        if self.M_factor != 0.0:
            alpha_eff = self.compute_effective_stiffness(rho)
            dF_dt_base = dF_dt_base + (alpha_eff - self.alpha) * F
            
        return dE_dt_base, dF_dt_base

def diagnostic_test():
    print("🚀 DIAGNOSTIC HYBRID TEST")
    print("Goal: See what parameters/dynamics base class ACTUALLY uses")
    print("=" * 70)
    
    solver = DiagnosticHybridSolver(
        alpha=1e-5,
        delta1=0.5,   # What we want
        delta2=1.0,   # What we want  
        M_factor=10000.0,
        eta_power=20.0,
        rho_cutoff=0.8
    )
    
    solver.initialize_system('gaussian')
    print("Running diagnostic evolution...")
    
    # Track field evolution
    F_history = []
    
    for step in range(500):
        solver.evolve_system(1)
        if step % 50 == 0:
            F_rms = np.sqrt(np.mean(solver.F**2))
            F_history.append(F_rms)
            print(f"Step {step}: F_RMS = {F_rms:.3f}")
    
    print(f"\n📈 FIELD EVOLUTION SUMMARY:")
    print(f"F_RMS progression: {[f'{x:.3f}' for x in F_history]}")
    
    # Final analysis
    rho_max = np.max(solver.rho)
    F_rms_final = np.sqrt(np.mean(solver.F**2))
    
    print(f"Final: ρ_max={rho_max:.3f}, F_RMS={F_rms_final:.3f}")
    
    # Quick spectral check
    fft2 = np.fft.fft2(solver.F)
    power_spectrum = np.abs(fft2)**2
    power_spectrum = np.fft.fftshift(power_spectrum)
    
    n = solver.F.shape[0]
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
        print(f"Spectral: Solar={solar_frac:.1%}, Galactic={galactic_frac:.1%}")

diagnostic_test()
