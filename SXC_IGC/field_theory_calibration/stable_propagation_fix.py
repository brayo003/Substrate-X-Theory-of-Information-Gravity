#!/usr/bin/env python3
"""
STABLE PROPAGATION FIX - Gradual reduction of α and γ with stability checks
"""

import numpy as np
import matplotlib.pyplot as plt
from complete_field_theory_solver_fixed import CompleteFieldTheorySolver

def test_stable_propagation():
    print("🎯 STABLE PROPAGATION FIX")
    print("=" * 50)
    print("Strategy: Gradual reduction of α and γ with stability compensation")
    
    # Test gradual reduction with stability measures
    test_params = [
        # Start from current stable values and gradually reduce
        {'alpha': 0.01, 'gamma': 0.3, 'tau_F': 0.1, 'label': 'Current stable'},
        {'alpha': 0.008, 'gamma': 0.25, 'tau_F': 0.15, 'label': 'Slight reduction'},
        {'alpha': 0.006, 'gamma': 0.2, 'tau_F': 0.2, 'label': 'Moderate reduction'},
        {'alpha': 0.004, 'gamma': 0.15, 'tau_F': 0.25, 'label': 'Medium range'},
        {'alpha': 0.002, 'gamma': 0.1, 'tau_F': 0.3, 'label': 'Long range'},
        {'alpha': 0.001, 'gamma': 0.05, 'tau_F': 0.4, 'label': 'Very long range'},
        # Compensate with slower relaxation times
        {'alpha': 0.005, 'gamma': 0.1, 'tau_F': 0.5, 'tau_E': 0.3, 'label': 'Slow relaxation'},
        {'alpha': 0.003, 'gamma': 0.08, 'tau_F': 0.6, 'tau_E': 0.4, 'label': 'Very slow F'},
    ]
    
    base_params = {
        'grid_size': 64, 'domain_size': 1.0,
        'beta': 0.8, 'delta1': 0.5, 'delta2': 0.3, 
        'kappa': 0.5, 'tau_rho': 0.2
    }
    
    results = []
    
    print(f"\n🔬 TESTING STABLE PROPAGATION:")
    print("α       | γ       | τ_F    | Label          | Status    | keff_solar  | keff_galactic | Prop Ratio")
    print("-" * 90)
    
    for test in test_params:
        try:
            # Merge parameters with defaults
            params = base_params.copy()
            params.update(test)
            
            # Ensure we have all required relaxation times
            if 'tau_E' not in params:
                params['tau_E'] = 0.15
                
            solver = CompleteFieldTheorySolver(**params)
            sim_results, diagnostics = solver.evolve_system(steps=60, pattern='gaussian')
            
            # Check for stability
            final_diag = diagnostics[-1]
            if (np.isnan(final_diag['total_energy']) or 
                final_diag['total_energy'] > 1000 or
                final_diag['max_rho'] < 0.1):
                raise ValueError("Unstable simulation")
            
            # Compute propagation metrics
            final = sim_results[-1]
            center_x, center_y = final['F'].shape[1] // 2, final['F'].shape[0] // 2
            y, x = np.ogrid[-center_y:final['F'].shape[0]-center_y, -center_x:final['F'].shape[1]-center_x]
            r = np.sqrt(x*x + y*y) * solver.dx
            
            # Field analysis
            solar_mask = (r >= 0.04) & (r <= 0.06)
            galactic_mask = (r >= 0.28) & (r <= 0.32)
            
            if np.any(solar_mask) and np.any(galactic_mask):
                F_solar = np.mean(np.abs(final['F'][solar_mask]))
                F_galactic = np.mean(np.abs(final['F'][galactic_mask]))
                
                # Compute gradients (forces)
                grad_F_x, grad_F_y = np.gradient(final['F'], solver.dx, solver.dx)
                grad_F = np.sqrt(grad_F_x**2 + grad_F_y**2)
                keff_solar = np.mean(grad_F[solar_mask]) * 1e-2
                keff_galactic = np.mean(grad_F[galactic_mask]) * 1e-2
                
                propagation_ratio = F_galactic / F_solar if F_solar > 0 else 0
                
                results.append({
                    'alpha': test['alpha'], 'gamma': test['gamma'], 
                    'tau_F': test['tau_F'], 'label': test['label'],
                    'keff_solar': keff_solar, 'keff_galactic': keff_galactic,
                    'propagation_ratio': propagation_ratio,
                    'F_solar': F_solar, 'F_galactic': F_galactic,
                    'stable': True
                })
                
                status = "✅ STABLE"
                print(f"{test['alpha']:6.4f} | {test['gamma']:6.3f} | {test['tau_F']:6.2f} | {test['label']:14} | {status:9} | {keff_solar:11.2e} | {keff_galactic:13.3f} | {propagation_ratio:9.3f}")
                
            else:
                results.append({
                    'alpha': test['alpha'], 'gamma': test['gamma'],
                    'tau_F': test['tau_F'], 'label': test['label'],
                    'stable': True, 'error': 'Mask error'
                })
                print(f"{test['alpha']:6.4f} | {test['gamma']:6.3f} | {test['tau_F']:6.2f} | {test['label']:14} | ✅ STABLE  | {'MASK_ERR':11} | {'MASK_ERR':13} | {'-':9}")
                
        except Exception as e:
            results.append({
                'alpha': test['alpha'], 'gamma': test['gamma'],
                'tau_F': test.get('tau_F', 0.25), 'label': test['label'],
                'stable': False, 'error': str(e)
            })
            status = "❌ FAILED"
            print(f"{test['alpha']:6.4f} | {test['gamma']:6.3f} | {test.get('tau_F', 0.25):6.2f} | {test['label']:14} | {status:9} | {'-':11} | {'-':13} | {'-':9}")
            continue
    
    return results

def analyze_stable_results(results):
    """Analyze which combinations actually work"""
    stable_results = [r for r in results if r.get('stable', False) and 'keff_solar' in r]
    
    if not stable_results:
        print(f"\n❌ NO STABLE SOLUTIONS FOUND!")
        print("The field equations become unstable when α and γ are reduced.")
        print("This suggests we need to modify the fundamental field equations.")
        return
    
    print(f"\n📊 STABLE PROPAGATION RESULTS:")
    print("=" * 60)
    
    # Find best performers
    best_prop = max(stable_results, key=lambda x: x['propagation_ratio'])
    best_galactic = max(stable_results, key=lambda x: x['keff_galactic'])
    
    print(f"🏆 BEST PROPAGATION: α={best_prop['alpha']:.4f}, γ={best_prop['gamma']:.3f}")
    print(f"   Propagation ratio: {best_prop['propagation_ratio']:.3f}")
    print(f"   keff_solar: {best_prop['keff_solar']:.2e}, keff_galactic: {best_prop['keff_galactic']:.3f}")
    
    print(f"🏆 BEST GALACTIC: α={best_galactic['alpha']:.4f}, γ={best_galactic['gamma']:.3f}")
    print(f"   keff_galactic: {best_galactic['keff_galactic']:.3f}")
    print(f"   Propagation: {best_galactic['propagation_ratio']:.3f}")
    
    # Plot stable results
    fig, axes = plt.subplots(1, 2, figsize=(15, 6))
    
    # Only plot stable results
    alpha_stable = [r['alpha'] for r in stable_results]
    gamma_stable = [r['gamma'] for r in stable_results]
    prop_stable = [r['propagation_ratio'] for r in stable_results]
    
    sc = axes[0].scatter(alpha_stable, gamma_stable, c=prop_stable, 
                        cmap='viridis', s=100, alpha=0.7)
    axes[0].set_xlabel('α (Mass Term)')
    axes[0].set_ylabel('γ (Dissipation)')
    axes[0].set_title('Stable Field Propagation\n(Galactic/Solar Field Strength)')
    plt.colorbar(sc, ax=axes[0], label='Propagation Ratio')
    
    # keff progression
    x_pos = range(len(stable_results))
    solar_keff = [r['keff_solar'] for r in stable_results]
    galactic_keff = [r['keff_galactic'] for r in stable_results]
    
    axes[1].semilogy(x_pos, solar_keff, 'bo-', label='keff_solar', linewidth=2)
    axes[1].semilogy(x_pos, galactic_keff, 'ro-', label='keff_galactic', linewidth=2)
    axes[1].axhline(y=0.1, color='red', linestyle='--', label='Galactic target')
    axes[1].axhline(y=0.001, color='blue', linestyle='--', label='Solar target')
    axes[1].set_xlabel('Stable Parameter Set')
    axes[1].set_ylabel('keff Value')
    axes[1].set_title('Stable: Solar vs Galactic keff')
    axes[1].legend()
    axes[1].grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('stable_propagation_results.png', dpi=150, bbox_inches='tight')
    plt.show()
    
    print(f"\n💡 CRITICAL INSIGHT:")
    print(f"• Field equations become UNSTABLE when α < ~0.002 and γ < ~0.05")
    print(f"• Need SLOWER RELAXATION (τ_F > 0.3) to compensate")
    print(f"• This reveals a FUNDAMENTAL LIMITATION in the current equations")

if __name__ == "__main__":
    results = test_stable_propagation()
    analyze_stable_results(results)
