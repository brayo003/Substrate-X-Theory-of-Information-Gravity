#!/usr/bin/env python3
import numpy as np
import matplotlib.pyplot as plt
from complete_field_theory_solver_fixed import CompleteFieldTheorySolver

class VariableStiffnessSolver(CompleteFieldTheorySolver):
    """Solver with PHYSICAL variable stiffness field ξ"""
    
    def __init__(self, eta_scale=0.0, **kwargs):
        super().__init__(**kwargs)
        self.eta_scale = eta_scale  # Coupling strength to density
        print(f"🔧 VARIABLE STIFFNESS: α={self.alpha:.1e}, η_scale={eta_scale}")
    
    def compute_effective_stiffness(self, rho):
        """Compute density-dependent stiffness α_eff(ρ) = α * (1 + η_scale * ρ^2)"""
        # This is the physical mechanism for scale separation
        return self.alpha * (1.0 + self.eta_scale * rho**2)
    
    # --- FIX: Remove arguments from method signature ---
    def compute_field_evolution(self):
        # Retrieve fields from self (as expected by parent class)
        rho, E, F = self.rho, self.E, self.F 
        
        # 1. Compute time derivative of rho (same as parent)
        lap_rho = self.laplacian(rho)
        drho_dt = self.beta * E - rho / self.tau_rho + lap_rho

        # 2. Compute time derivative of E (same as parent)
        lap_E = self.laplacian(E)
        dE_dt = self.kappa * F - E / self.tau_E + lap_E
        
        # 3. Compute time derivative of F with VARIABLE STIFFNESS
        lap_F = self.laplacian(F)
        biharm_F = self.laplacian(lap_F)
        
        # CRITICAL: Calculate the spatially varying stiffness field
        alpha_eff = self.compute_effective_stiffness(rho) 
        
        # F field evolution using alpha_eff(ρ)
        dF_dt = (
            self.delta2 * E -                       # Source term
            lap_F -                                 # Diffusion
            alpha_eff * F -                         # VARIABLE STIFFNESS (mass) term
            self.gamma * biharm_F -                 # Dissipation (always constant)
            F / self.tau_F                          # Relaxation
        )
        
        # Time-step the fields (Euler step)
        new_rho = rho + self.dt * drho_dt
        new_E = E + self.dt * dE_dt
        new_F = F + self.dt * dF_dt
        
        # Apply boundary conditions / cleanup
        new_rho = np.clip(new_rho, 0.0, 1.0)
        
        return new_rho, new_E, new_F
    # --- END FIX ---


def analyze_scales(solver, final_F):
    center_x, center_y = final_F.shape[1] // 2, final_F.shape[0] // 2
    y, x = np.ogrid[-center_y:final_F.shape[0]-center_y, 
                    -center_x:final_F.shape[1]-center_x]
    r = np.sqrt(x*x + y*y) * solver.dx
    
    # Define analysis masks
    solar_mask = (r >= 0.04) & (r <= 0.06)
    galactic_mask = (r >= 0.28) & (r <= 0.32)
    
    grad_F_x, grad_F_y = np.gradient(final_F, solver.dx, solver.dx)
    grad_F = np.sqrt(grad_F_x**2 + grad_F_y**2)
    
    # Calculate keff values (normalized)
    keff_solar = np.mean(grad_F[solar_mask]) * 1e-2
    keff_galactic = np.mean(grad_F[galactic_mask]) * 1e-2
    
    # Calculate Propagation ratio
    F_solar = np.mean(np.abs(final_F[solar_mask]))
    F_galactic = np.mean(np.abs(final_F[galactic_mask]))
    propagation_ratio = F_galactic / F_solar if F_solar > 0 else 0

    return keff_solar, keff_galactic, final_F.mean(), propagation_ratio

def test_variable_stiffness():
    
    base_params = {
        'grid_size': 64, 'domain_size': 1.0, 'alpha': 1e-5, # Low alpha for propagation
        'beta': 0.5, 'gamma': 0.2, 'delta1': 25.0, 'delta2': 0.3, # High source
        'kappa': 0.4, 'tau_rho': 0.1, 'tau_E': 0.1, 'tau_F': 0.1
    }
    
    # Test sweeps for eta_scale (coupling strength)
    eta_test_cases = [0.0, 10.0, 50.0, 100.0, 500.0, 1000.0, 5000.0, 10000.0]
    results = []
    
    # Baseline for comparison
    baseline_solar_keff = 4.55e-03
    target_solar_keff = 1.0e-03
    target_solar_reduction = baseline_solar_keff / target_solar_keff # ~4.55
    
    print("🚀 VARIABLE STIFFNESS PHYSICS TEST")
    print("============================================================")
    print(f"Target: Solar k_eff={target_solar_keff:.1e} (Reduction: {target_solar_reduction:.1f}x)")
    print(f"Baseline (η=0): Solar k_eff={baseline_solar_keff:.2e}, Galactic k_eff=0.0046")
    print("============================================================")

    for eta_scale in eta_test_cases:
        print(f"\n🔬 Testing η_scale = {eta_scale:.1f}")
        print("-" * 35)
        
        try:
            params = {**base_params, 'eta_scale': eta_scale}
            solver = VariableStiffnessSolver(**params)
            
            # Run the simulation (FIX: verbose removed)
            results_data, diagnostics = solver.evolve_system(steps=40)
            
            final_F = results_data[-1]['F']
            keff_solar, keff_galactic, mean_F, prop_ratio = analyze_scales(solver, final_F)
            
            # Check for stability (Total Energy should be bounded)
            if not np.isnan(diagnostics[-1]['total_energy']) and diagnostics[-1]['total_energy'] < 1e5:
                stable = True
            else:
                stable = False
            
            if stable:
                reduction_factor = baseline_solar_keff / keff_solar if keff_solar > 0 else float('inf')
                print(f"✅ STABLE! F_RMS: {diagnostics[-1]['F_rms']:.4f}")
                print(f"  k_eff_solar: {keff_solar:.2e} ({reduction_factor:.1f}x reduction)")
                print(f"  k_eff_galactic: {keff_galactic:.4f}")
                print(f"  Propagation Ratio: {prop_ratio:.3f}")

                results.append({
                    'eta_scale': eta_scale,
                    'solar': keff_solar,
                    'galactic': keff_galactic,
                    'reduction': reduction_factor,
                    'prop_ratio': prop_ratio
                })

                if reduction_factor >= target_solar_reduction:
                    print(f"🎉 SUCCESS! Target reduction of {target_solar_reduction:.1f}x achieved!")
                
            else:
                print("❌ UNSTABLE - Simulation diverged.")

        except Exception as e:
            print(f"❌ FAILED due to exception: {e}")

    # Final Analysis (Omitted for brevity, but should be included for plotting)
    print("\n📊 SUMMARY OF η SWEEP")
    for r in results:
        print(f"η={r['eta_scale']:.1f}: Solar={r['solar']:.2e} ({r['reduction']:.1f}x), Galactic={r['galactic']:.4f}")

if __name__ == "__main__":
    test_variable_stiffness()
