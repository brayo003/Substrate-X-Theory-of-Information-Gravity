#!/usr/bin/env python3
"""
Fixed Calibration - Complete with keff values and best parameters
"""

import numpy as np
import matplotlib.pyplot as plt
from complete_field_theory_solver_fixed import CompleteFieldTheorySolver

class FixedCalibration:
    def __init__(self):
        self.keff_solar_target = 1e-3
        self.keff_galactic_target = 0.1
        self.r_solar = 0.05
        self.r_galactic = 0.3
        self.field_to_keff_scale = 1e-2
    
    def compute_keff_from_simulation(self, solver, results):
        """Compute keff from field gradients with proper scaling"""
        final = results[-1]
        F_field = final['F']
        
        # Compute field gradients (this gives forces)
        grad_F_x, grad_F_y = np.gradient(F_field, solver.dx, solver.dx)
        grad_F_magnitude = np.sqrt(grad_F_x**2 + grad_F_y**2)
        
        # Apply proper physical scaling
        scaled_grad_F = grad_F_magnitude * self.field_to_keff_scale
        
        # Compute at characteristic distances
        center_x, center_y = F_field.shape[1] // 2, F_field.shape[0] // 2
        y, x = np.ogrid[-center_y:F_field.shape[0]-center_y, -center_x:F_field.shape[1]-center_x]
        r = np.sqrt(x*x + y*y) * solver.dx
        
        # Solar scale
        solar_mask = (r >= self.r_solar * 0.8) & (r <= self.r_solar * 1.2)
        if np.any(solar_mask):
            keff_solar = np.mean(scaled_grad_F[solar_mask])
        else:
            idx = int(self.r_solar / solver.dx)
            keff_solar = scaled_grad_F[center_y, center_x + idx] if center_x + idx < F_field.shape[1] else scaled_grad_F[center_y, -1]
        
        # Galactic scale  
        galactic_mask = (r >= self.r_galactic * 0.8) & (r <= self.r_galactic * 1.2)
        if np.any(galactic_mask):
            keff_galactic = np.mean(scaled_grad_F[galactic_mask])
        else:
            idx = int(self.r_galactic / solver.dx)
            keff_galactic = scaled_grad_F[center_y, center_x + idx] if center_x + idx < F_field.shape[1] else scaled_grad_F[center_y, -1]
        
        return keff_solar, keff_galactic
    
    def run_complete_calibration(self):
        """Run complete calibration and return keff values"""
        print("🎯 COMPLETE CALIBRATION WITH keff VALUES")
        print("=" * 60)
        
        test_combinations = [
            (0.1, 0.1), (0.1, 0.2), (0.1, 0.3),
            (0.2, 0.1), (0.2, 0.2), (0.2, 0.3), 
            (0.3, 0.1), (0.3, 0.2), (0.3, 0.3),
            (0.5, 0.1), (0.5, 0.2), (0.5, 0.3)
        ]
        
        calibration_results = []
        
        print("δ₁  | δ₂  | keff_solar  | keff_galactic | Solar Err% | Galactic Err% | Total Err%")
        print("-" * 85)
        
        for delta1, delta2 in test_combinations:
            try:
                params = {
                    'grid_size': 64, 'domain_size': 1.0,
                    'alpha': 0.01, 'beta': 0.8, 'gamma': 0.3,
                    'delta1': delta1, 'delta2': delta2, 'kappa': 0.5,
                    'tau_rho': 0.2, 'tau_E': 0.15, 'tau_F': 0.25
                }
                
                solver = CompleteFieldTheorySolver(**params)
                results, diagnostics = solver.evolve_system(steps=50, pattern='gaussian')
                
                keff_solar, keff_galactic = self.compute_keff_from_simulation(solver, results)
                
                solar_error = abs(keff_solar - self.keff_solar_target) / self.keff_solar_target * 100
                galactic_error = abs(keff_galactic - self.keff_galactic_target) / self.keff_galactic_target * 100
                total_error = solar_error + galactic_error
                
                calibration_results.append({
                    'delta1': delta1, 'delta2': delta2,
                    'keff_solar': keff_solar, 'keff_galactic': keff_galactic,
                    'solar_error': solar_error, 'galactic_error': galactic_error,
                    'total_error': total_error,
                    'solver': solver, 'results': results, 'diagnostics': diagnostics
                })
                
                print(f"{delta1:3.1f} | {delta2:3.1f} | {keff_solar:11.2e} | {keff_galactic:13.3f} | {solar_error:9.1f} | {galactic_error:13.1f} | {total_error:10.1f}")
                
            except Exception as e:
                print(f"{delta1:3.1f} | {delta2:3.1f} | {'ERROR':11} | {'ERROR':13} | {'-':9} | {'-':13} | {'-':10}")
                continue
        
        return calibration_results
    
    def find_best_parameters(self, calibration_results):
        """Find the best parameter set based on keff matching"""
        if not calibration_results:
            return None
        
        best_result = min(calibration_results, key=lambda x: x['total_error'])
        
        print(f"\n🏆 BEST PARAMETER SET FOUND:")
        print(f"   δ₁ = {best_result['delta1']:.3f}, δ₂ = {best_result['delta2']:.3f}")
        print(f"   keff_solar: {best_result['keff_solar']:.2e} (target: {self.keff_solar_target:.2e})")
        print(f"   keff_galactic: {best_result['keff_galactic']:.3f} (target: {self.keff_galactic_target:.3f})")
        print(f"   Solar error: {best_result['solar_error']:.1f}%")
        print(f"   Galactic error: {best_result['galactic_error']:.1f}%")
        print(f"   Total error: {best_result['total_error']:.1f}%")
        
        return best_result
    
    def plot_calibration_results(self, calibration_results, best_result):
        """Plot complete calibration results"""
        fig, axes = plt.subplots(2, 3, figsize=(18, 12))
        
        # Extract data
        delta1_vals = [r['delta1'] for r in calibration_results]
        delta2_vals = [r['delta2'] for r in calibration_results]
        keff_solar_vals = [r['keff_solar'] for r in calibration_results]
        keff_galactic_vals = [r['keff_galactic'] for r in calibration_results]
        total_errors = [r['total_error'] for r in calibration_results]
        
        # keff_solar landscape
        sc1 = axes[0,0].scatter(delta1_vals, delta2_vals, c=keff_solar_vals, 
                               cmap='viridis', s=100, alpha=0.7)
        axes[0,0].set_xlabel('δ₁')
        axes[0,0].set_ylabel('δ₂')
        axes[0,0].set_title('keff_solar Distribution')
        plt.colorbar(sc1, ax=axes[0,0], label='keff_solar')
        
        # keff_galactic landscape
        sc2 = axes[0,1].scatter(delta1_vals, delta2_vals, c=keff_galactic_vals, 
                               cmap='plasma', s=100, alpha=0.7)
        axes[0,1].set_xlabel('δ₁')
        axes[0,1].set_ylabel('δ₂')
        axes[0,1].set_title('keff_galactic Distribution')
        plt.colorbar(sc2, ax=axes[0,1], label='keff_galactic')
        
        # Error landscape
        sc3 = axes[0,2].scatter(delta1_vals, delta2_vals, c=total_errors, 
                               cmap='hot_r', s=100, alpha=0.7)
        if best_result:
            axes[0,2].plot(best_result['delta1'], best_result['delta2'], 'r*', 
                          markersize=15, label='Best')
        axes[0,2].set_xlabel('δ₁')
        axes[0,2].set_ylabel('δ₂')
        axes[0,2].set_title('Total Error Landscape')
        axes[0,2].legend()
        plt.colorbar(sc3, ax=axes[0,2], label='Total Error (%)')
        
        # keff vs targets
        x_pos = range(len(calibration_results))
        solar_vals = [r['keff_solar'] for r in calibration_results]
        galactic_vals = [r['keff_galactic'] for r in calibration_results]
        
        axes[1,0].semilogy(x_pos, solar_vals, 'bo-', label='Computed', alpha=0.7)
        axes[1,0].axhline(y=self.keff_solar_target, color='red', linestyle='--', 
                         label=f'Target: {self.keff_solar_target:.1e}')
        axes[1,0].set_xlabel('Parameter Set')
        axes[1,0].set_ylabel('keff_solar')
        axes[1,0].set_title('Solar Scale keff')
        axes[1,0].legend()
        axes[1,0].grid(True, alpha=0.3)
        
        axes[1,1].plot(x_pos, galactic_vals, 'ro-', label='Computed', alpha=0.7)
        axes[1,1].axhline(y=self.keff_galactic_target, color='red', linestyle='--', 
                         label=f'Target: {self.keff_galactic_target:.3f}')
        axes[1,1].set_xlabel('Parameter Set')
        axes[1,1].set_ylabel('keff_galactic')
        axes[1,1].set_title('Galactic Scale keff')
        axes[1,1].legend()
        axes[1,1].grid(True, alpha=0.3)
        
        # Best result details
        if best_result:
            final = best_result['results'][-1]
            final_diag = best_result['diagnostics'][-1]
            
            # FIXED: Use correct key names
            axes[1,2].text(0.1, 0.9, 'BEST PARAMETERS:', fontweight='bold')
            axes[1,2].text(0.1, 0.8, f'δ₁ = {best_result["delta1"]:.3f}')
            axes[1,2].text(0.1, 0.7, f'δ₂ = {best_result["delta2"]:.3f}')
            axes[1,2].text(0.1, 0.6, f'keff_solar: {best_result["keff_solar"]:.2e}')
            axes[1,2].text(0.1, 0.5, f'keff_galactic: {best_result["keff_galactic"]:.3f}')
            axes[1,2].text(0.1, 0.4, f'Max ρ: {final_diag["max_rho"]:.3f}')  # ✅ FIXED
            axes[1,2].text(0.1, 0.3, f'E RMS: {final_diag["E_rms"]:.3f}')
            axes[1,2].text(0.1, 0.2, f'Total error: {best_result["total_error"]:.1f}%')
            axes[1,2].set_xlim(0, 1)
            axes[1,2].set_ylim(0, 1)
            axes[1,2].set_title('Best Parameter Summary')
            axes[1,2].axis('off')
        
        plt.tight_layout()
        plt.savefig('COMPLETE_CALIBRATION_RESULTS.png', dpi=150, bbox_inches='tight')
        plt.show()

def main():
    calibrator = FixedCalibration()
    calibration_results = calibrator.run_complete_calibration()
    
    if calibration_results:
        best_result = calibrator.find_best_parameters(calibration_results)
        calibrator.plot_calibration_results(calibration_results, best_result)
        
        print(f"\n🎉 CALIBRATION COMPLETE!")
        print(f"Found best parameters that minimize keff errors")
        print(f"Theory is now calibrated to realistic targets")
    else:
        print("❌ No successful calibration runs")

if __name__ == "__main__":
    main()
