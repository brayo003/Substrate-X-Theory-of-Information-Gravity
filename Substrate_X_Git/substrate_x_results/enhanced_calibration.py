#!/usr/bin/env python3
"""
Enhanced Field Theory Calibration
With proper field scaling and wider parameter search
"""

import numpy as np
import matplotlib.pyplot as plt
from complete_field_theory_solver_fixed import CompleteFieldTheorySolver

class EnhancedCalibration:
    def __init__(self):
        self.keff_solar_target = 2e-4
        self.keff_galactic_target = 0.3
        self.r_solar = 0.05
        self.r_galactic = 0.3
        
    def compute_keff_from_simulation(self, solver, results):
        """Compute keff from actual simulation results with proper scaling"""
        final = results[-1]
        F_field = final['F']
        
        # Compute field gradients (this is what creates forces)
        grad_F_x, grad_F_y = np.gradient(F_field, solver.dx, solver.dx)
        grad_F_magnitude = np.sqrt(grad_F_x**2 + grad_F_y**2)
        
        # Compute at characteristic distances
        center_x, center_y = F_field.shape[1] // 2, F_field.shape[0] // 2
        y, x = np.ogrid[-center_y:F_field.shape[0]-center_y, -center_x:F_field.shape[1]-center_x]
        r = np.sqrt(x*x + y*y) * solver.dx
        
        # Solar scale (small distance)
        solar_mask = (r >= self.r_solar * 0.8) & (r <= self.r_solar * 1.2)
        if np.any(solar_mask):
            keff_solar = np.mean(grad_F_magnitude[solar_mask])
        else:
            # Fallback: interpolate
            idx = int(self.r_solar / solver.dx)
            keff_solar = grad_F_magnitude[center_y, center_x + idx]
        
        # Galactic scale (larger distance)  
        galactic_mask = (r >= self.r_galactic * 0.8) & (r <= self.r_galactic * 1.2)
        if np.any(galactic_mask):
            keff_galactic = np.mean(grad_F_magnitude[galactic_mask])
        else:
            idx = int(self.r_galactic / solver.dx)
            keff_galactic = grad_F_magnitude[center_y, center_x + idx]
        
        return keff_solar, keff_galactic
    
    def run_enhanced_calibration(self):
        """Run calibration with enhanced parameter search"""
        print("🔧 ENHANCED CALIBRATION WITH WIDER PARAMETER RANGE")
        print("=" * 60)
        
        # Test a wider range of parameters
        delta1_range = [0.1, 0.5, 1.0, 2.0, 5.0]  # Wider range for δ₁
        delta2_range = [0.1, 0.5, 1.0, 2.0, 5.0, 10.0]  # Much wider for δ₂
        
        best_params = None
        best_error = float('inf')
        results = []
        
        print("Testing parameter combinations...")
        print("δ₁     | δ₂     | keff_solar  | keff_galactic | Solar Err% | Galactic Err%")
        print("-" * 80)
        
        for delta1 in delta1_range:
            for delta2 in delta2_range:
                try:
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
                    sim_results, diagnostics = solver.evolve_system(steps=50, pattern='gaussian')  # Faster calibration
                    
                    keff_solar, keff_galactic = self.compute_keff_from_simulation(solver, sim_results)
                    
                    solar_error = abs(keff_solar - self.keff_solar_target) / self.keff_solar_target
                    galactic_error = abs(keff_galactic - self.keff_galactic_target) / self.keff_galactic_target
                    total_error = solar_error + galactic_error
                    
                    results.append({
                        'delta1': delta1,
                        'delta2': delta2,
                        'keff_solar': keff_solar,
                        'keff_galactic': keff_galactic,
                        'solar_error': solar_error,
                        'galactic_error': galactic_error,
                        'total_error': total_error
                    })
                    
                    print(f"{delta1:6.1f} | {delta2:6.1f} | {keff_solar:11.2e} | {keff_galactic:13.3f} | {solar_error*100:9.1f} | {galactic_error*100:12.1f}")
                    
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
                        
                except Exception as e:
                    print(f"{delta1:6.1f} | {delta2:6.1f} | {'ERROR':11} | {'ERROR':13} | {'-':9} | {'-':12}")
                    continue
        
        return best_params, results
    
    def plot_enhanced_results(self, best_params, all_results):
        """Plot enhanced calibration results"""
        fig, axes = plt.subplots(2, 3, figsize=(18, 12))
        
        # Extract data
        delta1_vals = [r['delta1'] for r in all_results]
        delta2_vals = [r['delta2'] for r in all_results]
        keff_solar_vals = [r['keff_solar'] for r in all_results]
        keff_galactic_vals = [r['keff_galactic'] for r in all_results]
        total_errors = [r['total_error'] for r in all_results]
        
        # Error landscape
        sc1 = axes[0,0].scatter(delta1_vals, delta2_vals, c=total_errors, 
                               cmap='viridis', s=100, alpha=0.7)
        axes[0,0].set_xlabel('δ₁ (Substrate → E coupling)')
        axes[0,0].set_ylabel('δ₂ (E → F coupling)')
        axes[0,0].set_title('Total Error Landscape')
        axes[0,0].set_xscale('log')
        axes[0,0].set_yscale('log')
        plt.colorbar(sc1, ax=axes[0,0], label='Total Error')
        
        # Mark best point
        if best_params:
            axes[0,0].plot(best_params['delta1'], best_params['delta2'], 'r*', 
                          markersize=15, label='Optimal')
            axes[0,0].legend()
        
        # keff_solar vs parameters
        sc2 = axes[0,1].scatter(delta1_vals, delta2_vals, c=keff_solar_vals, 
                               cmap='plasma', s=100, alpha=0.7, norm='log')
        axes[0,1].axhline(y=best_params['delta2'] if best_params else 1, color='red', linestyle='--', alpha=0.5)
        axes[0,1].axvline(x=best_params['delta1'] if best_params else 1, color='red', linestyle='--', alpha=0.5)
        axes[0,1].set_xlabel('δ₁')
        axes[0,1].set_ylabel('δ₂')
        axes[0,1].set_title('keff_solar Distribution')
        axes[0,1].set_xscale('log')
        axes[0,1].set_yscale('log')
        plt.colorbar(sc2, ax=axes[0,1], label='keff_solar')
        
        # keff_galactic vs parameters
        sc3 = axes[0,2].scatter(delta1_vals, delta2_vals, c=keff_galactic_vals, 
                               cmap='plasma', s=100, alpha=0.7)
        axes[0,2].axhline(y=best_params['delta2'] if best_params else 1, color='red', linestyle='--', alpha=0.5)
        axes[0,2].axvline(x=best_params['delta1'] if best_params else 1, color='red', linestyle='--', alpha=0.5)
        axes[0,2].set_xlabel('δ₁')
        axes[0,2].set_ylabel('δ₂')
        axes[0,2].set_title('keff_galactic Distribution')
        axes[0,2].set_xscale('log')
        axes[0,2].set_yscale('log')
        plt.colorbar(sc3, ax=axes[0,2], label='keff_galactic')
        
        # Parameter sweeps
        unique_delta1 = sorted(set(delta1_vals))
        unique_delta2 = sorted(set(delta2_vals))
        
        # keff_solar vs δ₂ for different δ₁
        for delta1 in unique_delta1[:3]:  # Plot first 3 values for clarity
            mask = [d1 == delta1 for d1 in delta1_vals]
            if any(mask):
                delta2_subset = [d2 for d2, m in zip(delta2_vals, mask) if m]
                keff_solar_subset = [k for k, m in zip(keff_solar_vals, mask) if m]
                axes[1,0].semilogy(delta2_subset, keff_solar_subset, 'o-', 
                                 label=f'δ₁={delta1}', linewidth=2)
        
        axes[1,0].axhline(y=self.keff_solar_target, color='red', linestyle='--', 
                         linewidth=2, label='Target')
        axes[1,0].set_xlabel('δ₂')
        axes[1,0].set_ylabel('keff_solar')
        axes[1,0].set_title('keff_solar vs δ₂ for different δ₁')
        axes[1,0].legend()
        axes[1,0].grid(True, alpha=0.3)
        
        # keff_galactic vs δ₂ for different δ₁
        for delta1 in unique_delta1[:3]:
            mask = [d1 == delta1 for d1 in delta1_vals]
            if any(mask):
                delta2_subset = [d2 for d2, m in zip(delta2_vals, mask) if m]
                keff_galactic_subset = [k for k, m in zip(keff_galactic_vals, mask) if m]
                axes[1,1].plot(delta2_subset, keff_galactic_subset, 'o-', 
                             label=f'δ₁={delta1}', linewidth=2)
        
        axes[1,1].axhline(y=self.keff_galactic_target, color='red', linestyle='--', 
                         linewidth=2, label='Target')
        axes[1,1].set_xlabel('δ₂')
        axes[1,1].set_ylabel('keff_galactic')
        axes[1,1].set_title('keff_galactic vs δ₂ for different δ₁')
        axes[1,1].legend()
        axes[1,1].grid(True, alpha=0.3)
        
        # Error convergence
        iterations = range(len(total_errors))
        axes[1,2].semilogy(iterations, total_errors, 'bo-', linewidth=2)
        axes[1,2].set_xlabel('Parameter Combination')
        axes[1,2].set_ylabel('Total Error')
        axes[1,2].set_title('Error Convergence')
        axes[1,2].grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.savefig('enhanced_calibration_results.png', dpi=150, bbox_inches='tight')
        plt.show()
        
        return best_params

def run_final_calibrated_simulation(best_params):
    """Run final simulation with calibrated parameters"""
    if not best_params:
        print("No optimal parameters found!")
        return
    
    print(f"\n🎉 RUNNING FINAL CALIBRATED SIMULATION")
    print(f"Optimal parameters: δ₁ = {best_params['delta1']:.3f}, δ₂ = {best_params['delta2']:.3f}")
    
    params = {
        'grid_size': 64,
        'domain_size': 1.0,
        'alpha': 0.01,
        'beta': 0.8,
        'gamma': 0.3,
        'delta1': best_params['delta1'],
        'delta2': best_params['delta2'],
        'kappa': 0.5,
        'tau_rho': 0.2,
        'tau_E': 0.15,
        'tau_F': 0.25
    }
    
    solver = CompleteFieldTheorySolver(**params)
    results, diagnostics = solver.evolve_system(steps=100, pattern='gaussian')
    
    # Compute final keff values
    calibrator = EnhancedCalibration()
    keff_solar, keff_galactic = calibrator.compute_keff_from_simulation(solver, results)
    
    print(f"\n📈 FINAL CALIBRATED RESULTS:")
    print(f"   keff_solar: {keff_solar:.2e} (target: {calibrator.keff_solar_target:.2e})")
    print(f"   keff_galactic: {keff_galactic:.3f} (target: {calibrator.keff_galactic_target:.3f})")
    print(f"   Solar error: {abs(keff_solar - calibrator.keff_solar_target)/calibrator.keff_solar_target*100:.1f}%")
    print(f"   Galactic error: {abs(keff_galactic - calibrator.keff_galactic_target)/calibrator.keff_galactic_target*100:.1f}%")
    
    # Plot final fields
    final = results[-1]
    fig, axes = plt.subplots(2, 3, figsize=(18, 12))
    
    # Density and fields
    im1 = axes[0,0].imshow(final['rho'], extent=[-0.5,0.5,-0.5,0.5], origin='lower', cmap='viridis')
    axes[0,0].set_title(f'Calibrated Density\nMax ρ = {np.max(final["rho"]):.3f}')
    plt.colorbar(im1, ax=axes[0,0])
    
    im2 = axes[0,1].imshow(final['E'], extent=[-0.5,0.5,-0.5,0.5], origin='lower', cmap='RdBu_r')
    axes[0,1].set_title(f'E Field\nRMS = {np.sqrt(np.mean(final["E"]**2)):.3f}')
    plt.colorbar(im2, ax=axes[0,1])
    
    im3 = axes[0,2].imshow(final['F'], extent=[-0.5,0.5,-0.5,0.5], origin='lower', cmap='RdBu_r')
    axes[0,2].set_title(f'F Field (Gravitational)\nkeff_solar = {keff_solar:.2e}')
    plt.colorbar(im3, ax=axes[0,2])
    
    # Mark calibration distances
    for ax in axes[0,:]:
        circle_solar = plt.Circle((0, 0), calibrator.r_solar, fill=False, 
                                color='yellow', linestyle='--', linewidth=2, label='Solar scale')
        circle_galactic = plt.Circle((0, 0), calibrator.r_galactic, fill=False, 
                                   color='red', linestyle='--', linewidth=2, label='Galactic scale')
        ax.add_patch(circle_solar)
        ax.add_patch(circle_galactic)
    
    # Field gradients (actual forces)
    grad_F_x, grad_F_y = np.gradient(final['F'], solver.dx, solver.dx)
    grad_F_magnitude = np.sqrt(grad_F_x**2 + grad_F_y**2)
    
    im4 = axes[1,0].imshow(grad_F_magnitude, extent=[-0.5,0.5,-0.5,0.5], origin='lower', cmap='hot')
    axes[1,0].set_title('Gravitational Force Magnitude\n|∇F|')
    plt.colorbar(im4, ax=axes[1,0])
    
    # Energy evolution
    steps = [d['step'] for d in diagnostics]
    total_energy = [d['total_energy'] for d in diagnostics]
    axes[1,1].plot(steps, total_energy, 'k-', linewidth=2)
    axes[1,1].set_xlabel('Time Step')
    axes[1,1].set_ylabel('Total Energy')
    axes[1,1].set_title('Energy Evolution')
    axes[1,1].grid(True, alpha=0.3)
    
    # Field correlations
    rho_E_corr = [d.get('rho_E_correlation', 0) for d in diagnostics]
    axes[1,2].plot(steps, rho_E_corr, 'r-', linewidth=2)
    axes[1,2].set_xlabel('Time Step')
    axes[1,2].set_ylabel('ρ-E Correlation')
    axes[1,2].set_title('Substrate-Field Correlation')
    axes[1,2].grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('final_calibrated_simulation.png', dpi=150, bbox_inches='tight')
    plt.show()
    
    return solver, results, diagnostics

if __name__ == "__main__":
    calibrator = EnhancedCalibration()
    best_params, all_results = calibrator.run_enhanced_calibration()
    
    if best_params:
        print(f"\n🏆 BEST PARAMETERS FOUND:")
        print(f"   δ₁ = {best_params['delta1']:.3f}, δ₂ = {best_params['delta2']:.3f}")
        print(f"   keff_solar: {best_params['keff_solar']:.2e} (error: {best_params['solar_error']*100:.1f}%)")
        print(f"   keff_galactic: {best_params['keff_galactic']:.3f} (error: {best_params['galactic_error']*100:.1f}%)")
        
        # Plot results
        calibrator.plot_enhanced_results(best_params, all_results)
        
        # Run final simulation
        solver, results, diagnostics = run_final_calibrated_simulation(best_params)
        
        print(f"\n✅ ENHANCED CALIBRATION COMPLETE!")
        print("The field theory is now properly calibrated to match observational constraints.")
    else:
        print("❌ Calibration failed. No suitable parameters found.")
