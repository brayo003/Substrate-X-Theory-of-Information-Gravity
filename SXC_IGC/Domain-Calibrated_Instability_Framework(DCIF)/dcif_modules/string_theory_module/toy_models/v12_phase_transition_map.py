import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Patch

def generate_boundary_map():
    print("⚛️ Initializing V12 Parameter Sweep (10,000 Universes)...")
    
    # Sweep Beta (Energy Injection) from 0.1 to 5.0
    betas = np.linspace(0.1, 5.0, 100)
    # Sweep b (Governor Infrastructure) from 0.1 to 5.0
    bs = np.linspace(0.1, 5.0, 100)

    # Create the coordinate grid
    B_grid, b_grid = np.meshgrid(betas, bs)
    Ds_grid = np.zeros_like(B_grid)

    # Calculate Distance to Shatter (Ds) for every coordinate
    for i in range(len(bs)):
        for j in range(len(betas)):
            beta = B_grid[i, j]
            b = b_grid[i, j]
            
            # The Analytical Solution
            gs_peak = (2.0 / b)**(1.0 / 3.0)
            max_tension = (beta * gs_peak**2) / (1.0 + b * gs_peak**3)
            Ds_grid[i, j] = 1.0 - max_tension

    # Rendering the Map
    plt.figure(figsize=(10, 8))
    
    # We define the strict phase boundaries
    # Red (Swampland: Ds < 0), Yellow (Marginal: 0 to 0.2), Green (Landscape: Ds > 0.2)
    levels = [-5.0, 0.0, 0.2, 2.0]
    colors = ['#ff4c4c', '#ffd700', '#4caf50'] 

    plt.contourf(B_grid, b_grid, Ds_grid, levels=levels, colors=colors, alpha=0.85)
    
    # Overlay the theoretical critical curve (b = 4/27 * beta^3)
    critical_beta = np.linspace(0.1, 5.0, 100)
    critical_b = (4.0 / 27.0) * (critical_beta**3)
    plt.plot(critical_beta, critical_b, 'k--', linewidth=2, label=r'Critical Boundary ($b = \frac{4}{27}\beta^3$)')

    # Formatting
    plt.title('SXC-V12: The Landscape vs. Swampland Phase Map', fontsize=16, fontweight='bold')
    plt.xlabel(r'Energy Coupling ($\beta$)', fontsize=14)
    plt.ylabel(r'Substrate Governor Capacity ($b$)', fontsize=14)
    
    # Custom Legend
    legend_elements = [
        Patch(facecolor='#4caf50', edgecolor='k', label='Landscape (Stable)'),
        Patch(facecolor='#ffd700', edgecolor='k', label='Marginal (Edge Case)'),
        Patch(facecolor='#ff4c4c', edgecolor='k', label='Swampland (Shattered Vacuum)'),
        plt.Line2D([0], [0], color='k', linestyle='--', linewidth=2, label='Critical Equation Curve')
    ]
    plt.legend(handles=legend_elements, loc='upper left', fontsize=11)
    
    # Save the physical proof
    filename = 'v12_landscape_boundary_map.png'
    plt.savefig(filename, dpi=300, bbox_inches='tight')
    print(f"✅ Substrate mapped. Graphic saved as: {filename}")

if __name__ == "__main__":
    generate_boundary_map()
