#!/usr/bin/env python3
"""
Field Theory Calibration Solver
Calibrates δ₁ and δ₂ parameters to match target keff values using evolved field states
"""

import numpy as np
import matplotlib.pyplot as plt
from complete_field_theory_solver_fixed import CompleteFieldTheorySolver

class FieldCalibrationSolver:
    def __init__(self):
        # Target keff values (dimensionless equivalents)
        self.keff_solar_target = 2e-4    # Solar system scale
        self.keff_galactic_target = 0.3  # Galactic scale
        
        # Reference distances (dimensionless)
        self.r_solar = 0.05    # ~50 AU in dimensionless units
        self.r_galactic = 0.3  # ~kpc scale
        
        print("🎯 FIELD THEORY CALIBRATION SOLVER")
        print("=" * 50)
        print(f"Target keff values:")
        print(f"  Solar scale (r={self.r_solar:.3f}): {self.keff_solar_target:.2e}")
        print(f"  Galactic scale (r={self.r_galactic:.3f}): {self.keff_galactic_target:.3f}")
    
    def compute_keff_from_fields(self, F_field, r_distance, pattern_scale=1.0):
        """Compute effective keff from F field at given distance"""
        # F field represents gravitational information potential
        # keff ∝ |∇F| at characteristic distance
        
        center_x, center_y = F_field.shape[1] // 2, F_field.shape[0] // 2
        
        # Find radial profile
        y, x = np.ogrid[-center_y:F_field.shape[0]-center_y, -center_x:F_field.shape[1]-center_x]
        r = np.sqrt(x*x + y*y) * pattern_scale
        
        # Compute radial gradient of F field
        F_r = F_field.copy()
        F_r[r > 0] = F_r[r > 0] / r[r > 0]  # Rough radial dependence
        
        grad_F_x, grad_F_y = np.gradient(F_r)
        grad_F_magnitude = np.sqrt(grad_F_x**2 + grad_F_y**2)
        
        # Find keff at target distance
        distance_mask = (r >= r_distance * 0.9) & (r <= r_distance * 1.1)
        if np.any(distance_mask):
            keff = np.mean(grad_F_magnitude[distance_mask])
        else:
            keff = grad_F_magnitude[center_y, center_x + int(r_distance/pattern_scale)]
        
        return keff
    
    def calibrate_parameters(self, initial_delta1=0.6, initial_delta2=0.4, 
                           calibration_steps=50, pattern='gaussian'):
        """Calibrate δ₁ and δ₂ to match target keff values"""
        print(f"\n🔧 CALIBRATING PARAMETERS for {pattern.upper()} pattern")
        print("Iter | δ₁     | δ₂     | keff_solar  | keff_galactic | Solar Err | Galactic Err")
        print("-" * 85)
        
        best_params = None
        best_error = float('inf')
        error_history = []
        
        # Parameter search ranges
        delta1_range = np.linspace(0.1, 2.0, calibration_steps)
        delta2_range = np.linspace(0.1, 1.5, calibration_steps)
        
        for i, delta1 in enumerate(delta1_range):
            for j, delta2 in enumerate(delta2_range):
                # Run simulation with current parameters
                params = {
                    'grid_size': 64,
                    'domain_size': 1.0,
                    'alpha': 0.01,
                    'beta': 0.8,
                    'gamma': 0.3,
                    'delta1': delta1,
                    'delta2': delta2,
                    'kappa': 0.5,
                    'tau_rho': 0.2,
                    'tau_E': 0.15,
                    'tau_F': 0.25
                }
                
                solver = CompleteFieldTheorySolver(**params)
                results, diagnostics = solver.evolve_system(steps=90, pattern=pattern)
                
                # Get equilibrium field state (step 90)
                F_field_eq = results[-1]['F']
                
                # Compute keff values
                keff_solar = self.compute_keff_from_fields(F_field_eq, self.r_solar)
                keff_galactic = self.compute_keff_from_fields(F_field_eq, self.r_galactic)
                
                # Compute errors
                solar_error = abs(keff_solar - self.keff_solar_target) / self.keff_solar_target
                galactic_error = abs(keff_galactic - self.keff_galactic_target) / self.keff_galactic_target
                total_error = solar_error + galactic_error
                
                error_history.append({
                    'delta1': delta1,
                    'delta2': delta2,
                    'keff_solar': keff_solar,
                    'keff_galactic': keff_galactic,
                    'total_error': total_error
                })
                
                # Update best parameters
                if total_error < best_error:
                    best_error = total_error
                    best_params = {
                        'delta1': delta1,
                        'delta2': delta2,
                        'keff_solar': keff_solar,
                        'keff_galactic': keff_galactic,
                        'solar_error': solar_error,
                        'galactic_error': galactic_error
                    }
                
                if (i * len(delta2_range) + j) % 50 == 0:  # Print progress
                    print(f"{i*len(delta2_range)+j:4d} | {delta1:6.3f} | {delta2:6.3f} | "
                          f"{keff_solar:11.2e} | {keff_galactic:13.3f} | {solar_error:9.3f} | {galactic_error:11.3f}")
        
        return best_params, error_history
    
    def run_calibration_study(self):
        """Run calibration for different patterns and find optimal parameters"""
        patterns = ['gaussian', 'double', 'asymmetric', 'quadrupole']
        calibration_results = {}
        
        for pattern in patterns:
            print(f"\n{'='*60}")
            print(f"CALIBRATING: {pattern.upper()} PATTERN")
            print('='*60)
            
            best_params, error_history = self.calibrate_parameters(pattern=pattern)
            calibration_results[pattern] = {
                'best_params': best_params,
                'error_history': error_history
            }
            
            print(f"\n✅ BEST PARAMETERS for {pattern}:")
            print(f"   δ₁ = {best_params['delta1']:.4f}, δ₂ = {best_params['delta2']:.4f}")
            print(f"   Achieved keff_solar: {best_params['keff_solar']:.2e} (target: {self.keff_solar_target:.2e})")
            print(f"   Achieved keff_galactic: {best_params['keff_galactic']:.3f} (target: {self.keff_galactic_target:.3f})")
            print(f"   Relative errors: Solar {best_params['solar_error']*100:.1f}%, Galactic {best_params['galactic_error']*100:.1f}%")
        
        # Visualization of calibration results
        self.plot_calibration_results(calibration_results)
        
        return calibration_results
    
    def plot_calibration_results(self, calibration_results):
        """Plot calibration results across different patterns"""
        fig, axes = plt.subplots(2, 2, figsize=(15, 12))
        
        patterns = list(calibration_results.keys())
        colors = ['blue', 'red', 'green', 'orange']
        
        # Parameter space exploration
        for idx, pattern in enumerate(patterns):
            error_data = calibration_results[pattern]['error_history']
            delta1_vals = [d['delta1'] for d in error_data]
            delta2_vals = [d['delta2'] for d in error_data]
            total_errors = [d['total_error'] for d in error_data]
            
            # Error landscape
            sc = axes[0,0].scatter(delta1_vals, delta2_vals, c=total_errors, 
                                 cmap='viridis', alpha=0.6, label=pattern)
            axes[0,0].set_xlabel('δ₁ (Substrate → E coupling)')
            axes[0,0].set_ylabel('δ₂ (E → F coupling)')
            axes[0,0].set_title('Parameter Space Error Landscape')
            axes[0,0].legend()
        
        plt.colorbar(sc, ax=axes[0,0], label='Total Error')
        
        # Achieved keff values vs targets
        solar_achieved = [calibration_results[p]['best_params']['keff_solar'] for p in patterns]
        galactic_achieved = [calibration_results[p]['best_params']['keff_galactic'] for p in patterns]
        
        x_pos = np.arange(len(patterns))
        width = 0.35
        
        axes[0,1].bar(x_pos - width/2, solar_achieved, width, label='Achieved', alpha=0.7)
        axes[0,1].axhline(y=self.keff_solar_target, color='red', linestyle='--', 
                         label=f'Target: {self.keff_solar_target:.1e}')
        axes[0,1].set_ylabel('keff_solar')
        axes[0,1].set_title('Solar Scale Calibration')
        axes[0,1].set_xticks(x_pos)
        axes[0,1].set_xticklabels(patterns)
        axes[0,1].legend()
        axes[0,1].set_yscale('log')
        
        axes[1,0].bar(x_pos - width/2, galactic_achieved, width, label='Achieved', alpha=0.7)
        axes[1,0].axhline(y=self.keff_galactic_target, color='red', linestyle='--', 
                         label=f'Target: {self.keff_galactic_target:.3f}')
        axes[1,0].set_ylabel('keff_galactic')
        axes[1,0].set_title('Galactic Scale Calibration')
        axes[1,0].set_xticks(x_pos)
        axes[1,0].set_xticklabels(patterns)
        axes[1,0].legend()
        
        # Optimal parameters by pattern
        delta1_optimal = [calibration_results[p]['best_params']['delta1'] for p in patterns]
        delta2_optimal = [calibration_results[p]['best_params']['delta2'] for p in patterns]
        
        axes[1,1].plot(x_pos, delta1_optimal, 'o-', linewidth=2, label='Optimal δ₁')
        axes[1,1].plot(x_pos, delta2_optimal, 's-', linewidth=2, label='Optimal δ₂')
        axes[1,1].set_xlabel('Pattern Type')
        axes[1,1].set_ylabel('Optimal Parameter Value')
        axes[1,1].set_title('Optimal Coupling Parameters by Pattern')
        axes[1,1].set_xticks(x_pos)
        axes[1,1].set_xticklabels(patterns)
        axes[1,1].legend()
        axes[1,1].grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.savefig('field_calibration_results.png', dpi=150, bbox_inches='tight')
        plt.show()
        
        # Show best overall parameters
        best_overall = None
        best_total_error = float('inf')
        
        for pattern in patterns:
            params = calibration_results[pattern]['best_params']
            total_error = params['solar_error'] + params['galactic_error']
            if total_error < best_total_error:
                best_total_error = total_error
                best_overall = (pattern, params)
        
        if best_overall:
            pattern, params = best_overall
            print(f"\n🏆 BEST OVERALL CALIBRATION:")
            print(f"   Pattern: {pattern}")
            print(f"   Parameters: δ₁ = {params['delta1']:.4f}, δ₂ = {params['delta2']:.4f}")
            print(f"   keff_solar: {params['keff_solar']:.2e} (error: {params['solar_error']*100:.1f}%)")
            print(f"   keff_galactic: {params['keff_galactic']:.3f} (error: {params['galactic_error']*100:.1f}%)")
            print(f"   Total error: {best_total_error*100:.1f}%")

def run_verification_simulation(optimal_params, pattern='gaussian'):
    """Run a verification simulation with calibrated parameters"""
    print(f"\n🔍 VERIFICATION SIMULATION with calibrated parameters")
    print(f"Pattern: {pattern}, δ₁ = {optimal_params['delta1']:.4f}, δ₂ = {optimal_params['delta2']:.4f}")
    
    params = {
        'grid_size': 64,
        'domain_size': 1.0,
        'alpha': 0.01,
        'beta': 0.8,
        'gamma': 0.3,
        'delta1': optimal_params['delta1'],
        'delta2': optimal_params['delta2'],
        'kappa': 0.5,
        'tau_rho': 0.2,
        'tau_E': 0.15,
        'tau_F': 0.25
    }
    
    solver = CompleteFieldTheorySolver(**params)
    results, diagnostics = solver.evolve_system(steps=100, pattern=pattern)
    
    # Plot final state with calibrated parameters
    fig, axes = plt.subplots(1, 3, figsize=(15, 4))
    
    final = results[-1]
    
    im1 = axes[0].imshow(final['rho'], extent=[-0.5,0.5,-0.5,0.5], origin='lower', cmap='viridis')
    axes[0].set_title(f'Final Density (Calibrated)\nMax ρ = {np.max(final["rho"]):.3f}')
    plt.colorbar(im1, ax=axes[0])
    
    im2 = axes[1].imshow(final['E'], extent=[-0.5,0.5,-0.5,0.5], origin='lower', cmap='RdBu_r')
    axes[1].set_title(f'E Field\nRMS = {np.sqrt(np.mean(final["E"]**2)):.3f}')
    plt.colorbar(im2, ax=axes[1])
    
    im3 = axes[2].imshow(final['F'], extent=[-0.5,0.5,-0.5,0.5], origin='lower', cmap='RdBu_r')
    axes[2].set_title(f'F Field\nRMS = {np.sqrt(np.mean(final["F"]**2)):.3f}')
    plt.colorbar(im3, ax=axes[2])
    
    plt.tight_layout()
    plt.savefig('calibrated_verification.png', dpi=150, bbox_inches='tight')
    plt.show()
    
    return solver, results, diagnostics

if __name__ == "__main__":
    # Run calibration study
    calibrator = FieldCalibrationSolver()
    calibration_results = calibrator.run_calibration_study()
    
    # Run verification with best parameters
    best_pattern = 'gaussian'  # You can choose the best pattern from results
    if best_pattern in calibration_results:
        optimal_params = calibration_results[best_pattern]['best_params']
        solver, results, diagnostics = run_verification_simulation(optimal_params, best_pattern)
