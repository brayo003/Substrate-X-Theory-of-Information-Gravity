#!/usr/bin/env python3
import numpy as np
from complete_field_theory_solver_fixed import CompleteFieldTheorySolver

class SurgicalStiffnessSolver(CompleteFieldTheorySolver):
    def __init__(self, M_factor=0.0, eta_power=20.0, rho_cutoff=0.8, **kwargs):
        super().__init__(**kwargs)
        self.M_factor = M_factor
        self.eta_power = eta_power
        self.rho_cutoff = rho_cutoff
        
        if M_factor > 0:
            self.alpha_eff_max = self.alpha * (1.0 + M_factor)
        else:
            self.alpha_eff_max = self.alpha
        
        print(f"🔪 SURGICAL STIFFNESS: M={M_factor:.0f}, η_power={eta_power}, ρ_cut={rho_cutoff}")
        print(f"   Max stiffness: α_eff_max = {self.alpha_eff_max:.2e}")
    
    def compute_effective_stiffness(self, rho):
        """Super-sharp surgical stiffness targeting only ρ > 0.8"""
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

def measure_field_contrast(solver):
    """Measure actual field behavior differences"""
    rho, E, F = solver.rho, solver.E, solver.F
    
    # Calculate field statistics
    F_rms = np.sqrt(np.mean(F**2))
    F_max = np.max(F)
    F_min = np.min(F)
    
    # Measure center vs edge contrast
    center_idx = solver.grid_size // 2
    F_center = F[center_idx, center_idx]
    F_edge = F[0, 0]
    center_edge_ratio = abs(F_center / F_edge) if F_edge != 0 else 0
    
    # Measure field gradient at different radii
    def radial_profile(field):
        center = (solver.grid_size // 2, solver.grid_size // 2)
        y, x = np.ogrid[:solver.grid_size, :solver.grid_size]
        r = np.sqrt((x - center[0])**2 + (y - center[1])**2)
        r = r.astype(int)
        
        radial_mean = np.bincount(r.ravel(), field.ravel()) / np.bincount(r.ravel())
        return radial_mean
    
    F_radial = radial_profile(F)
    
    # Estimate scales from radial decay
    if len(F_radial) > 10:
        # Short scale: decay from center to r=5
        short_scale = F_radial[0] / F_radial[5] if F_radial[5] != 0 else 0
        
        # Long scale: decay from r=10 to r=20  
        if len(F_radial) > 20:
            long_scale = F_radial[10] / F_radial[20] if F_radial[20] != 0 else 0
        else:
            long_scale = 0
    else:
        short_scale = long_scale = 0
    
    return {
        'F_rms': F_rms,
        'F_max': F_max,
        'F_min': F_min,
        'center_edge_ratio': center_edge_ratio,
        'short_scale_decay': short_scale,
        'long_scale_decay': long_scale,
        'F_center': F_center,
        'F_edge': F_edge
    }

print("🔪 SURGICAL STIFFNESS TEST - Enhanced Parameters")
print("η_power=20.0, ρ_cutoff=0.8, M=2000")
print("Target: Isolate stiffness to ρ≈1 only")
print("=" * 60)

# Test surgical parameters
solver = SurgicalStiffnessSolver(
    alpha=1e-5, 
    delta1=25.0,
    M_factor=2000.0, 
    eta_power=20.0, 
    rho_cutoff=0.8
)

solver.initialize_system('gaussian')
solver.evolve_system(50)

analysis = measure_field_contrast(solver)

print(f"\n📊 SURGICAL RESULTS:")
print(f"Field RMS: {analysis['F_rms']:.6f}")
print(f"Field Max: {analysis['F_max']:.6f}")
print(f"Field Min: {analysis['F_min']:.6f}")
print(f"Center/Edge Ratio: {analysis['center_edge_ratio']:.1f}x")
print(f"Short-scale decay (r=0→5): {analysis['short_scale_decay']:.2f}x")
print(f"Long-scale decay (r=10→20): {analysis['long_scale_decay']:.2f}x")
print(f"Center value: {analysis['F_center']:.6f}")
print(f"Edge value: {analysis['F_edge']:.6f}")

# Compare with baseline
print(f"\n🔍 COMPARISON TO BASELINE (M=0):")
print("Expected: Higher center/edge ratio, stronger short-scale decay")
print("This indicates solar scale compression while preserving galactic scale")
