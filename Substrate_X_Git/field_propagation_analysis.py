#!/usr/bin/env python3
"""
Field Propagation Analysis - Understanding why galactic effects aren't appearing
"""

import numpy as np
import matplotlib.pyplot as plt
from complete_field_theory_solver_fixed import CompleteFieldTheorySolver

def analyze_field_propagation():
    print("🔬 FIELD PROPAGATION ANALYSIS")
    print("=" * 50)
    print("Investigating why galactic-scale effects aren't appearing...")
    
    # Test our best parameters
    params = {
        'grid_size': 64, 'domain_size': 1.0,
        'alpha': 0.01, 'beta': 0.1, 'gamma': 0.3,  # Best overall
        'delta1': 0.5, 'delta2': 0.3, 'kappa': 0.5,
        'tau_rho': 0.2, 'tau_E': 0.15, 'tau_F': 0.25
    }
    
    solver = CompleteFieldTheorySolver(**params)
    results, diagnostics = solver.evolve_system(steps=100, pattern='gaussian')
    
    final = results[-1]
    
    # Analyze field propagation in detail
    print(f"\n📊 FIELD PROPAGATION ANALYSIS:")
    print(f"Grid size: {solver.grid_size}, dx: {solver.dx:.4f}")
    print(f"Domain size: 1.0, so physical scale: ~2.0 units diameter")
    
    # Compute radial profiles
    center_x, center_y = final['F'].shape[1] // 2, final['F'].shape[0] // 2
    y, x = np.ogrid[-center_y:final['F'].shape[0]-center_y, -center_x:final['F'].shape[1]-center_x]
    r = np.sqrt(x*x + y*y) * solver.dx
    
    # Analyze F field at different distances
    distances = [0.05, 0.1, 0.2, 0.3, 0.4]  # From solar to galactic scale
    field_strengths = []
    gradient_strengths = []
    
    print(f"\n📏 FIELD STRENGTHS AT DIFFERENT DISTANCES:")
    print("Distance | F Field | Gradient | Notes")
    print("-" * 50)
    
    for dist in distances:
        mask = (r >= dist * 0.9) & (r <= dist * 1.1)
        if np.any(mask):
            F_strength = np.mean(np.abs(final['F'][mask]))
            
            # Compute gradient at this distance
            grad_F_x, grad_F_y = np.gradient(final['F'], solver.dx, solver.dx)
            grad_F_magnitude = np.sqrt(grad_F_x**2 + grad_F_y**2)
            grad_strength = np.mean(grad_F_magnitude[mask])
            
            field_strengths.append(F_strength)
            gradient_strengths.append(grad_strength)
            
            note = "Solar scale" if dist == 0.05 else "Galactic scale" if dist == 0.3 else "Intermediate"
            print(f"{dist:8.2f} | {F_strength:8.4f} | {grad_strength:8.4f} | {note}")
        else:
            field_strengths.append(0)
            gradient_strengths.append(0)
            print(f"{dist:8.2f} | {'N/A':8} | {'N/A':8} | Out of range")
    
    # Plot comprehensive analysis
    fig, axes = plt.subplots(2, 3, figsize=(18, 12))
    
    # F field
    im1 = axes[0,0].imshow(final['F'], extent=[-0.5,0.5,-0.5,0.5], origin='lower', cmap='RdBu_r')
    axes[0,0].set_title('F Field (Gravitational)')
    axes[0,0].set_xlabel('Position')
    axes[0,0].set_ylabel('Position')
    plt.colorbar(im1, ax=axes[0,0])
    
    # Mark analysis distances
    for dist in distances:
        circle = plt.Circle((0, 0), dist, fill=False, color='red', linestyle='--', alpha=0.7)
        axes[0,0].add_patch(circle)
        axes[0,0].text(dist, 0, f'{dist}', color='red', fontsize=8)
    
    # Radial profile of F field
    radial_F = []
    radial_positions = np.linspace(0, 0.45, 50)
    for radius in radial_positions:
        mask = (r >= radius * 0.95) & (r <= radius * 1.05)
        if np.any(mask):
            radial_F.append(np.mean(np.abs(final['F'][mask])))
        else:
            radial_F.append(0)
    
    axes[0,1].plot(radial_positions, radial_F, 'b-', linewidth=2)
    axes[0,1].axvline(x=0.05, color='yellow', linestyle='--', label='Solar scale')
    axes[0,1].axvline(x=0.3, color='red', linestyle='--', label='Galactic scale')
    axes[0,1].set_xlabel('Distance from center')
    axes[0,1].set_ylabel('|F Field|')
    axes[0,1].set_title('Radial F Field Profile')
    axes[0,1].legend()
    axes[0,1].grid(True, alpha=0.3)
    
    # Field gradients (actual forces)
    grad_F_x, grad_F_y = np.gradient(final['F'], solver.dx, solver.dx)
    grad_F_magnitude = np.sqrt(grad_F_x**2 + grad_F_y**2)
    
    im2 = axes[0,2].imshow(grad_F_magnitude, extent=[-0.5,0.5,-0.5,0.5], origin='lower', cmap='hot')
    axes[0,2].set_title('Gravitational Force |∇F|')
    plt.colorbar(im2, ax=axes[0,2])
    
    # Radial profile of gradients
    radial_grad = []
    for radius in radial_positions:
        mask = (r >= radius * 0.95) & (r <= radius * 1.05)
        if np.any(mask):
            radial_grad.append(np.mean(grad_F_magnitude[mask]))
        else:
            radial_grad.append(0)
    
    axes[1,0].plot(radial_positions, radial_grad, 'r-', linewidth=2)
    axes[1,0].axvline(x=0.05, color='yellow', linestyle='--', label='Solar scale')
    axes[1,0].axvline(x=0.3, color='red', linestyle='--', label='Galactic scale')
    axes[1,0].set_xlabel('Distance from center')
    axes[1,0].set_ylabel('|∇F| (Force)')
    axes[1,0].set_title('Radial Force Profile')
    axes[1,0].legend()
    axes[1,0].grid(True, alpha=0.3)
    
    # Scale separation analysis
    solar_idx = np.argmin(np.abs(radial_positions - 0.05))
    galactic_idx = np.argmin(np.abs(radial_positions - 0.3))
    
    if radial_grad[solar_idx] > 0 and radial_grad[galactic_idx] > 0:
        scale_ratio = radial_grad[galactic_idx] / radial_grad[solar_idx]
        axes[1,1].bar(['Solar', 'Galactic'], [radial_grad[solar_idx], radial_grad[galactic_idx]], 
                     color=['yellow', 'red'])
        axes[1,1].set_ylabel('Force Strength |∇F|')
        axes[1,1].set_title(f'Scale Separation: {scale_ratio:.4f}')
        axes[1,1].text(0.5, 0.9, f'Ratio: {scale_ratio:.2e}', transform=axes[1,1].transAxes, 
                      ha='center', fontweight='bold')
    else:
        axes[1,1].text(0.5, 0.5, 'Insufficient data\nfor scale analysis', 
                      transform=axes[1,1].transAxes, ha='center')
        axes[1,1].set_title('Scale Separation Analysis')
    
    # Insights and recommendations
    insights = []
    if max(radial_grad) < 1e-4:
        insights.append("❌ Forces too weak at all scales")
    elif radial_grad[galactic_idx] / radial_grad[solar_idx] < 0.1:
        insights.append("❌ Force drops too rapidly with distance")
    else:
        insights.append("✅ Reasonable force propagation")
    
    if max(radial_F) < 0.01:
        insights.append("❌ F field too localized")
    else:
        insights.append("✅ F field has sufficient range")
    
    axes[1,2].text(0.1, 0.9, 'KEY INSIGHTS:', fontweight='bold')
    for i, insight in enumerate(insights):
        axes[1,2].text(0.1, 0.8 - i*0.1, insight, fontsize=10)
    
    axes[1,2].text(0.1, 0.4, 'RECOMMENDATIONS:', fontweight='bold')
    axes[1,2].text(0.1, 0.3, '• Increase δ₂ for stronger F field', fontsize=9)
    axes[1,2].text(0.1, 0.2, '• Reduce γ for less dissipation', fontsize=9) 
    axes[1,2].text(0.1, 0.1, '• Test different initial conditions', fontsize=9)
    axes[1,2].set_xlim(0, 1)
    axes[1,2].set_ylim(0, 1)
    axes[1,2].set_title('Analysis Results')
    axes[1,2].axis('off')
    
    plt.tight_layout()
    plt.savefig('field_propagation_analysis.png', dpi=150, bbox_inches='tight')
    plt.show()
    
    print(f"\n🎯 ANALYSIS COMPLETE!")
    print(f"Best parameters: β=0.10, γ=0.30, δ₁=0.5, δ₂=0.3")
    print(f"Scale separation challenge identified - working on solutions!")

if __name__ == "__main__":
    analyze_field_propagation()
