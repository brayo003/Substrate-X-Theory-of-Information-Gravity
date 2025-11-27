#!/usr/bin/env python3
import numpy as np
from complete_field_theory_solver_fixed import CompleteFieldTheorySolver

class WorkingStiffnessSolver(CompleteFieldTheorySolver):
    def __init__(self, eta_scale=0.0, **kwargs):
        super().__init__(**kwargs)
        self.eta_scale = eta_scale
    
    def compute_field_evolution(self):
        rho, E, F = self.rho, self.E, self.F
        dE_dt, dF_dt = super().compute_field_evolution()
        
        if self.eta_scale != 0:
            alpha_eff = self.alpha * (1.0 + self.eta_scale * rho**2)
            original_stiffness = self.alpha * F
            variable_stiffness = alpha_eff * F
            dF_dt = dF_dt - original_stiffness + variable_stiffness
        
        return dE_dt, dF_dt

def analyze_proper_scales(solver):
    """Proper scale analysis using field patterns"""
    rho, E, F = solver.rho, solver.E, solver.F
    
    # Calculate field properties
    F_rms = np.sqrt(np.mean(F**2))
    
    # Calculate correlation lengths using autocorrelation
    def correlation_length(field):
        autocorr = np.correlate(field.flatten(), field.flatten(), mode='full')
        autocorr = autocorr[len(autocorr)//2:]
        autocorr = autocorr / autocorr[0]
        
        # Find where autocorrelation drops to 1/e
        threshold = 1/np.e
        for i in range(1, len(autocorr)):
            if autocorr[i] < threshold:
                return i * solver.dx
        return len(autocorr) * solver.dx
    
    # Calculate lengths for different fields
    solar_length = correlation_length(F)  # Short scale
    galactic_length = correlation_length(rho)  # Long scale
    
    # Convert to effective couplings (inverse length)
    keff_solar = 1.0 / (solar_length + 1e-10)
    keff_galactic = 1.0 / (galactic_length + 1e-10)
    
    return {
        'keff_solar': keff_solar,
        'keff_galactic': keff_galactic,
        'solar_length': solar_length,
        'galactic_length': galactic_length,
        'F_rms': F_rms
    }

def test_stiffness_effects():
    print("🔧 PROPER STIFFNESS EFFECTS TEST")
    print("=" * 60)
    print("Looking for: Galactic boost & Solar reduction via scale lengths")
    print("=" * 60)
    
    eta_values = [0.0, 100.0, 500.0, 1000.0, 5000.0]
    results = []
    
    for eta in eta_values:
        print(f"\nη = {eta}:")
        solver = WorkingStiffnessSolver(alpha=1e-5, delta1=25.0, eta_scale=eta)
        solver.initialize_system('gaussian')
        solver.evolve_system(30)
        
        analysis = analyze_proper_scales(solver)
        
        print(f"  Solar scale: {analysis['solar_length']:.4f} (k={analysis['keff_solar']:.3f})")
        print(f"  Galactic scale: {analysis['galactic_length']:.4f} (k={analysis['keff_galactic']:.3f})")
        print(f"  F_RMS: {analysis['F_rms']:.6f}")
        
        results.append({
            'eta': eta,
            'solar_length': analysis['solar_length'],
            'galactic_length': analysis['galactic_length'],
            'solar_k': analysis['keff_solar'],
            'galactic_k': analysis['keff_galactic']
        })
    
    # Analyze improvements
    baseline = results[0]
    print(f"\n📊 IMPROVEMENTS vs BASELINE (η=0):")
    print(f"Baseline - Solar: {baseline['solar_k']:.3f}, Galactic: {baseline['galactic_k']:.3f}")
    
    for res in results[1:]:
        solar_change = res['solar_k'] / baseline['solar_k']
        galactic_change = res['galactic_k'] / baseline['galactic_k']
        ratio_change = (res['galactic_k']/res['solar_k']) / (baseline['galactic_k']/baseline['solar_k'])
        
        print(f"η={res['eta']}: Solar {solar_change:.2f}x, Galactic {galactic_change:.2f}x, Ratio {ratio_change:.2f}x")

test_stiffness_effects()
