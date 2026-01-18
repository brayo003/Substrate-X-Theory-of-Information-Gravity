#!/usr/bin/env python3
"""
Galactic Scale Calibration - Targeting β and γ parameters
Based on the insight that substrate stiffness controls long-range behavior
"""

import numpy as np
import matplotlib.pyplot as plt
from complete_field_theory_solver_fixed import CompleteFieldTheorySolver

class GalacticCalibration:
    def __init__(self):
        # Fixed coupling parameters (our best from previous calibration)
        self.delta1 = 0.5
        self.delta2 = 0.3
        
        # Targets
        self.keff_solar_target = 1e-3
        self.keff_galactic_target = 0.1
        self.r_solar = 0.05
        self.r_galactic = 0.3
        self.field_to_keff_scale = 1e-2
        
        print("🌌 GALACTIC SCALE CALIBRATION")
        print("=" * 50)
        print("Strategy: Vary substrate parameters β and γ")
        print("to enable long-range force propagation")
        print(f"Fixed couplings: δ₁={self.delta1}, δ₂={self.delta2}")
    
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
    
    def run_beta_gamma_sweep(self):
        """Sweep β and γ parameters to find galactic-scale solution"""
        print("\n🔬 SWEEPING β AND γ PARAMETERS")
        print("β controls non-linear self-interaction (long-range effects)")
        print("γ controls higher-order curvature/dissipation")
        print("\nβ     | γ     | keff_solar  | keff_galactic | Solar Err% | Galactic Err% | Total Err%")
        print("-" * 90)
        
        # Test different β and γ values for long-range behavior
        test_combinations = [
            # Original values for reference
            (0.8, 0.3),
            # Reduce dissipation for longer range
            (0.8, 0.1), (0.8, 0.05), (0.8, 0.01),
            # Modify non-linearity for different range behavior
            (0.5, 0.3), (0.3, 0.3), (0.1, 0.3),
            (1.0, 0.3), (1.5, 0.3), (2.0, 0.3),
            # Combined adjustments
            (0.5, 0.1), (1.0, 0.1), (1.5, 0.05),
            # Extreme values to test limits
            (0.1, 0.01), (2.0, 0.01)
        ]
        
        results = []
        
        for beta, gamma in test_combinations:
            try:
                params = {
                    'grid_size': 64, 'domain_size': 1.0,
                    'alpha': 0.01, 'beta': beta, 'gamma': gamma,
                    'delta1': self.delta1, 'delta2': self.delta2, 'kappa': 0.5,
                    'tau_rho': 0.2, 'tau_E': 0.15, 'tau_F': 0.25
                }
                
                solver = CompleteFieldTheorySolver(**params)
                sim_results, diagnostics = solver.evolve_system(steps=50, pattern='gaussian')
                
                keff_solar, keff_galactic = self.compute_keff_from_simulation(solver, sim_results)
                
                solar_error = abs(keff_solar - self.keff_solar_target) / self.keff_solar_target * 100
                galactic_error = abs(keff_galactic - self.keff_galactic_target) / self.keff_galactic_target * 100
                total_error = solar_error + galactic_error
                
                results.append({
                    'beta': beta, 'gamma': gamma,
                    'keff_solar': keff_solar, 'keff_galactic': keff_galactic,
                    'solar_error': solar_error, 'galactic_error': galactic_error,
                    'total_error': total_error,
                    'solver': solver, 'results': sim_results, 'diagnostics': diagnostics
                })
                
                print(f"{beta:4.2f} | {gamma:5.2f} | {keff_solar:11.2e} | {keff_galactic:13.3f} | {solar_error:9.1f} | {galactic_error:13.1f} | {total_error:10.1f}")
                
            except Exception as e:
                print(f"{beta:4.2f} | {gamma:5.2f} | {'ERROR':11} | {'ERROR':13} | {'-':9} | {'-':13} | {'-':10}")
                continue
        
        return results
    
    def analyze_galactic_solutions(self, results):
        """Analyze which parameter combinations give the best galactic-scale performance"""
        if not results:
            return None
        
        # Find best overall
        best_overall = min(results, key=lambda x: x['total_error'])
        
        # Find best galactic performance (prioritize galactic scale)
        best_galactic = min(results, key=lambda x: x['galactic_error'])
        
        # Find best that maintains reasonable solar performance
        reasonable_solar = [r for r in results if r['solar_error'] < 100]  # Solar error < 100%
        if reasonable_solar:
            best_balanced = min(reasonable_solar, key=lambda x: x['galactic_error'])
        else:
            best_balanced = best_galactic
        
        print(f"\n🏆 BEST SOLUTIONS FOUND:")
        print(f"Overall best (total error): β={best_overall['beta']:.2f}, γ={best_overall['gamma']:.2f}")
        print(f"  keff_solar: {best_overall['keff_solar']:.2e}, keff_galactic: {best_overall['keff_galactic']:.3f}")
        print(f"  Total error: {best_overall['total_error']:.1f}%")
        
        print(f"\nBest galactic performance: β={best_galactic['beta']:.2f}, γ={best_galactic['gamma']:.2f}")
        print(f"  keff_solar: {best_galactic['keff_solar']:.2e}, keff_galactic: {best_galactic['keff_galactic']:.3f}")
        print(f"  Galactic error: {best_galactic['galactic_error']:.1f}%")
        
        if reasonable_solar:
            print(f"\nBest balanced: β={best_balanced['beta']:.2f}, γ={best_balanced['gamma']:.2f}")
            print(f"  keff_solar: {best_balanced['keff_solar']:.2e}, keff_galactic: {best_balanced['keff_galactic']:.3f}")
            print(f"  Solar error: {best_balanced['solar_error']:.1f}%, Galactic error: {best_balanced['galactic_error']:.1f}%")
        
        return {
            'best_overall': best_overall,
            'best_galactic': best_galactic,
            'best_balanced': best_balanced if reasonable_solar else best_galactic
        }
    
    def plot_parameter_landscape(self, results, best_solutions):
        """Plot how β and γ affect the scale separation"""
        fig, axes = plt.subplots(2, 3, figsize=(18, 12))
        
        # Extract data
        beta_vals = [r['beta'] for r in results]
        gamma_vals = [r['gamma'] for r in results]
        keff_solar_vals = [r['keff_solar'] for r in results]
        keff_galactic_vals = [r['keff_galactic'] for r in results]
        galactic_errors = [r['galactic_error'] for r in results]
        
        # keff_solar vs β,γ
        sc1 = axes[0,0].scatter(beta_vals, gamma_vals, c=keff_solar_vals, 
                               cmap='viridis', s=100, alpha=0.7, norm='log')
        axes[0,0].set_xlabel('β (Non-linear self-interaction)')
        axes[0,0].set_ylabel('γ (Curvature/Dissipation)')
        axes[0,0].set_title('Solar Scale keff vs β,γ')
        plt.colorbar(sc1, ax=axes[0,0], label='keff_solar')
        
        # keff_galactic vs β,γ
        sc2 = axes[0,1].scatter(beta_vals, gamma_vals, c=keff_galactic_vals, 
                               cmap='plasma', s=100, alpha=0.7)
        axes[0,1].set_xlabel('β (Non-linear self-interaction)')
        axes[0,1].set_ylabel('γ (Curvature/Dissipation)')
        axes[0,1].set_title('Galactic Scale keff vs β,γ')
        plt.colorbar(sc2, ax=axes[0,1], label='keff_galactic')
        
        # Galactic error landscape
        sc3 = axes[0,2].scatter(beta_vals, gamma_vals, c=galactic_errors, 
                               cmap='hot_r', s=100, alpha=0.7)
        if best_solutions:
            best = best_solutions['best_galactic']
            axes[0,2].plot(best['beta'], best['gamma'], 'r*', markersize=15, label='Best Galactic')
        axes[0,2].set_xlabel('β')
        axes[0,2].set_ylabel('γ')
        axes[0,2].set_title('Galactic Error Landscape')
        axes[0,2].legend()
        plt.colorbar(sc3, ax=axes[0,2], label='Galactic Error (%)')
        
        # Scale separation analysis
        scale_ratios = [g/s if s > 0 else 0 for g, s in zip(keff_galactic_vals, keff_solar_vals)]
        sc4 = axes[1,0].scatter(beta_vals, gamma_vals, c=scale_ratios, 
                               cmap='coolwarm', s=100, alpha=0.7)
        axes[1,0].set_xlabel('β')
        axes[1,0].set_ylabel('γ')
        axes[1,0].set_title('Scale Separation (keff_galactic / keff_solar)')
        plt.colorbar(sc4, ax=axes[1,0], label='Scale Ratio')
        
        # Parameter trends
        unique_betas = sorted(set(beta_vals))
        for beta in unique_betas[:4]:  # Plot first 4 for clarity
            beta_mask = [b == beta for b in beta_vals]
            if any(beta_mask):
                gamma_subset = [g for g, m in zip(gamma_vals, beta_mask) if m]
                keff_galactic_subset = [k for k, m in zip(keff_galactic_vals, beta_mask) if m]
                axes[1,1].plot(gamma_subset, keff_galactic_subset, 'o-', 
                             label=f'β={beta}', linewidth=2)
        
        axes[1,1].axhline(y=self.keff_galactic_target, color='red', linestyle='--', 
                         linewidth=2, label='Target')
        axes[1,1].set_xlabel('γ')
        axes[1,1].set_ylabel('keff_galactic')
        axes[1,1].set_title('Galactic keff vs γ for different β')
        axes[1,1].legend()
        axes[1,1].grid(True, alpha=0.3)
        
        # Best solution summary
        if best_solutions:
            best = best_solutions['best_balanced']
            axes[1,2].text(0.1, 0.9, 'BEST BALANCED SOLUTION:', fontweight='bold')
            axes[1,2].text(0.1, 0.8, f'β = {best["beta"]:.3f}')
            axes[1,2].text(0.1, 0.7, f'γ = {best["gamma"]:.3f}')
            axes[1,2].text(0.1, 0.6, f'δ₁ = {self.delta1:.3f}')
            axes[1,2].text(0.1, 0.5, f'δ₂ = {self.delta2:.3f}')
            axes[1,2].text(0.1, 0.4, f'keff_solar: {best["keff_solar"]:.2e}')
            axes[1,2].text(0.1, 0.3, f'keff_galactic: {best["keff_galactic"]:.3f}')
            axes[1,2].text(0.1, 0.2, f'Scale ratio: {best["keff_galactic"]/best["keff_solar"]:.1f}')
            axes[1,2].set_xlim(0, 1)
            axes[1,2].set_ylim(0, 1)
            axes[1,2].set_title('Optimal Parameters')
            axes[1,2].axis('off')
        
        plt.tight_layout()
        plt.savefig('galactic_scale_calibration.png', dpi=150, bbox_inches='tight')
        plt.show()

def main():
    calibrator = GalacticCalibration()
    results = calibrator.run_beta_gamma_sweep()
    
    if results:
        best_solutions = calibrator.analyze_galactic_solutions(results)
        calibrator.plot_parameter_landscape(results, best_solutions)
        
        print(f"\n🎉 GALACTIC SCALE CALIBRATION COMPLETE!")
        print(f"Found optimal substrate parameters for long-range behavior")
        
        if best_solutions:
            best = best_solutions['best_balanced']
            print(f"\n🚀 RECOMMENDED PARAMETERS:")
            print(f"α=0.01, β={best['beta']:.3f}, γ={best['gamma']:.3f}")
            print(f"δ₁={calibrator.delta1:.3f}, δ₂={calibrator.delta2:.3f}")
            print(f"Scale separation achieved: {best['keff_galactic']/best['keff_solar']:.1f}x")
    else:
        print("❌ No successful calibration runs")

if __name__ == "__main__":
    main()
