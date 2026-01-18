#!/usr/bin/env python3
import numpy as np
from complete_field_theory_solver_fixed import CompleteFieldTheorySolver

class MaximumSurgicalSolver(CompleteFieldTheorySolver):
    def __init__(self, M_factor=10000.0, eta_power=20.0, rho_cutoff=0.8, **kwargs):
        super().__init__(**kwargs)
        self.M_factor = M_factor
        self.eta_power = eta_power
        self.rho_cutoff = rho_cutoff
        
        self.alpha_eff_max = self.alpha * (1.0 + M_factor)
        
        print(f"💥 MAXIMUM SURGICAL STIFFNESS: M={M_factor:.0f}")
        print(f"   α_eff_max = {self.alpha_eff_max:.3f} (10,000× amplification)")
        print(f"   Surgical: η_power={eta_power}, ρ_cut={rho_cutoff}")
        print(f"   Target: Crush solar scales while preserving galactic")
    
    def compute_effective_stiffness(self, rho):
        if self.M_factor == 0.0:
            return self.alpha
            
        tanh_term = np.tanh(self.eta_power * (rho - self.rho_cutoff))
        stiffness_factor = 1.0 + self.M_factor * np.maximum(0.0, tanh_term)
        return self.alpha * stiffness_factor
        
    def compute_field_evolution(self):
        rho, E, F = self.rho, self.E, self.F
        dE_dt, dF_dt = super().compute_field_evolution()
        
        if self.M_factor != 0.0:
            alpha_eff = self.compute_effective_stiffness(rho)
            dF_dt = dF_dt + (alpha_eff - self.alpha) * F
            
        return dE_dt, dF_dt

def measure_scale_separation(solver):
    """Comprehensive scale measurement"""
    rho, E, F = solver.rho, solver.E, solver.F
    
    # Basic field stats
    F_rms = np.sqrt(np.mean(F**2))
    F_center = F[32, 32]
    F_edge = F[0, 0]
    
    # Radial profile analysis
    center = (32, 32)
    y, x = np.ogrid[:64, :64]
    r = np.sqrt((x - center[0])**2 + (y - center[1])**2).astype(int)
    
    radial_F = np.bincount(r.ravel(), F.ravel()) / np.bincount(r.ravel())
    
    # Calculate scale lengths
    if len(radial_F) > 15:
        # Solar scale: very short range (r=0 to r=3)
        solar_scale = radial_F[0] / radial_F[3] if radial_F[3] != 0 else 0
        
        # Intermediate scale (r=5 to r=10)  
        if len(radial_F) > 10:
            intermediate_scale = radial_F[5] / radial_F[10] if radial_F[10] != 0 else 0
        else:
            intermediate_scale = 0
            
        # Galactic scale (r=15 to r=25)
        if len(radial_F) > 25:
            galactic_scale = radial_F[15] / radial_F[25] if radial_F[25] != 0 else 0
        else:
            galactic_scale = 0
    else:
        solar_scale = intermediate_scale = galactic_scale = 0
    
    return {
        'F_rms': F_rms,
        'center_edge_ratio': abs(F_center / F_edge) if F_edge != 0 else 0,
        'solar_scale_compression': solar_scale,
        'intermediate_scale': intermediate_scale,
        'galactic_scale_preservation': galactic_scale,
        'F_center': F_center,
        'F_edge': F_edge,
        'radial_profile': radial_F[:30]  # First 30 radial bins
    }

print("💥 MAXIMUM SURGICAL STIFFNESS TEST")
print("M=10000, α_eff_max=0.10, η_power=20, ρ_cut=0.8")
print("Pushing stiffness to stability limits")
print("=" * 70)

solver = MaximumSurgicalSolver(
    alpha=1e-5, 
    delta1=25.0,
    M_factor=10000.0, 
    eta_power=20.0, 
    rho_cutoff=0.8
)

solver.initialize_system('gaussian')
solver.evolve_system(60)  # Extended evolution

analysis = measure_scale_separation(solver)

print(f"\n📊 MAXIMUM STIFFNESS RESULTS:")
print(f"Field RMS: {analysis['F_rms']:.6f}")
print(f"Center/Edge Ratio: {analysis['center_edge_ratio']:.1f}x")
print(f"Solar Scale Compression (r=0→3): {analysis['solar_scale_compression']:.1f}x")
print(f"Intermediate Scale (r=5→10): {analysis['intermediate_scale']:.1f}x")
print(f"Galactic Scale (r=15→25): {analysis['galactic_scale_preservation']:.1f}x")
print(f"Center Value: {analysis['F_center']:.6f}")
print(f"Edge Value: {analysis['F_edge']:.6f}")

print(f"\n🎯 TARGET ASSESSMENT:")
solar_target = 0.001
galactic_target = 0.100
current_galactic = analysis['F_rms']

solar_progress = analysis['solar_scale_compression']  # Higher = more compression
galactic_progress = current_galactic / galactic_target

print(f"Solar Compression: {solar_progress:.1f}x (need strong local decay)")
print(f"Galactic Strength: {galactic_progress:.1f}x of target")

if solar_progress > 10 and galactic_progress > 0.5:
    print("💫 SIGNIFICANT PROGRESS - Scale separation emerging!")
elif analysis['center_edge_ratio'] > 20:
    print("🔬 STRONG LOCALIZATION - Surgical approach working!")
else:
    print("⚠️  Needs more stiffness or different approach")

# Show radial profile
print(f"\n📈 RADIAL PROFILE (first 15 points):")
for i, val in enumerate(analysis['radial_profile'][:15]):
    print(f"  r={i}: {val:.6f}")
