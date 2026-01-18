#!/usr/bin/env python3
"""
Analysis script for dwarf galaxy rotation curves.
"""

import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path

# Set up paths
RESULTS_DIR = Path(__file__).resolve().parent / "results" / "dwarf_galaxies"
RESULTS_DIR.mkdir(parents=True, exist_ok=True)

PLOT_DIR = RESULTS_DIR / "dwarf_galaxies"
PLOT_DIR.mkdir(exist_ok=True)

def load_data():
    """Load the simulation data."""
    data = np.load(RESULTS_DIR / "dwarf_galaxy_rotation.npz")
    return {k: data[k] for k in data.files}

def plot_rotation_curve(data, save_path=None):
    """Plot the rotation curve with proper formatting."""
    plt.figure(figsize=(10, 6))
    
    # Plot curves
    plt.plot(data['r_kpc'], data['v_sub']/1000, 'b-', lw=2, label='Substrate Prediction')
    plt.plot(data['r_kpc'], data['v_newt']/1000, 'r--', lw=2, label='Newtonian (Stars Only)')
    
    # Add ratio in the top right
    ax2 = plt.gca().twinx()
    ax2.plot(data['r_kpc'], data['ratio'], 'g-', alpha=0.5, lw=1, label='v_sub/v_newt')
    ax2.set_ylabel('v_sub / v_newt', color='g')
    ax2.tick_params(axis='y', labelcolor='g')
    
    # Format plot
    plt.xlabel('Radius (kpc)')
    plt.ylabel('Circular Velocity (km/s)')
    plt.title(f'Dwarf Galaxy Rotation Curve\n(M* = {data["m_star"]:.1e} M☉, R_eff = {data["r_eff"]:.1f} kpc)')
    plt.grid(True, alpha=0.3)
    plt.legend()
    
    if save_path:
        plt.savefig(save_path, dpi=150, bbox_inches='tight')
        print(f"Plot saved to {save_path}")
    else:
        plt.show()
    plt.close()

def plot_velocity_ratio(data, save_path=None):
    """Plot the velocity ratio with a log scale."""
    plt.figure(figsize=(10, 5))
    
    # Calculate running median for smoother curve
    window_size = 10
    ratio_smooth = np.convolve(
        data['ratio'], 
        np.ones(window_size)/window_size, 
        mode='same'
    )
    
    plt.semilogy(data['r_kpc'], ratio_smooth, 'g-', lw=2)
    
    # Format plot
    plt.xlabel('Radius (kpc)')
    plt.ylabel('v_sub / v_newt')
    plt.title('Velocity Ratio (Substrate/Newtonian)')
    plt.grid(True, which='both', alpha=0.3)
    
    if save_path:
        plt.savefig(save_path, dpi=150, bbox_inches='tight')
        print(f"Plot saved to {save_path}")
    else:
        plt.show()
    plt.close()

def main():
    # Load the data
    data = load_data()
    
    # Create plots
    plot_rotation_curve(
        data, 
        save_path=PLOT_DIR / "detailed_rotation_curve.png"
    )
    
    plot_velocity_ratio(
        data,
        save_path=PLOT_DIR / "velocity_ratio.png"
    )
    
    # Print summary statistics
    print("\n=== Dwarf Galaxy Analysis Summary ===")
    print(f"Stellar Mass: {data['m_star']:.2e} M☉")
    print(f"Effective Radius: {data['r_eff']:.2f} kpc")
    print(f"Maximum v_sub: {np.max(data['v_sub']/1000):.2f} km/s")
    print(f"Maximum v_newt: {np.max(data['v_newt']/1000):.2f} km/s")
    print(f"Median v_sub/v_newt ratio: {np.median(data['ratio']):.2f}")
    print(f"Outer v_sub/v_newt ratio (last 10%): {np.mean(data['ratio'][-len(data['ratio'])//10:]):.2f}")

if __name__ == "__main__":
    main()
