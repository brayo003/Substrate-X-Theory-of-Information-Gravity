#!/usr/bin/env python3
import numpy as np
import matplotlib.pyplot as plt
from complete_field_theory_solver_fixed import CompleteFieldTheorySolver

class CalibratedSolver(CompleteFieldTheorySolver):
    def __init__(self, M_factor=10000.0, eta_power=20.0, rho_cutoff=0.8, **kwargs):
        super().__init__(**kwargs)
        self.M_factor = M_factor
        self.eta_power = eta_power
        self.rho_cutoff = rho_cutoff
        
    def compute_effective_stiffness(self, rho):
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

def compute_power_spectrum(field, dx):
    """Compute 2D power spectrum and radial average"""
    # 2D Fourier transform
    fft2 = np.fft.fft2(field)
    power_spectrum = np.abs(fft2)**2
    
    # Shift zero frequency to center
    power_spectrum = np.fft.fftshift(power_spectrum)
    
    # Create k-space coordinates
    n = field.shape[0]
    kx = np.fft.fftshift(np.fft.fftfreq(n, dx)) * 2 * np.pi
    ky = np.fft.fftshift(np.fft.fftfreq(n, dx)) * 2 * np.pi
    kx_grid, ky_grid = np.meshgrid(kx, ky)
    k_magnitude = np.sqrt(kx_grid**2 + ky_grid**2)
    
    # Radial average
    k_max = np.max(k_magnitude)
    k_bins = np.linspace(0, k_max, min(100, n//2))
    radial_power = np.zeros_like(k_bins)
    
    for i in range(len(k_bins)-1):
        mask = (k_magnitude >= k_bins[i]) & (k_magnitude < k_bins[i+1])
        if np.any(mask):
            radial_power[i] = np.mean(power_spectrum[mask])
    
    return k_bins, radial_power, power_spectrum

def analyze_scale_separation(solver):
    """Comprehensive Fourier analysis of scale separation"""
    rho, E, F = solver.rho, solver.E, solver.F
    
    print("\n📊 FOURIER SCALE ANALYSIS")
    print("=" * 60)
    
    # Compute power spectra
    k_rho, P_rho, _ = compute_power_spectrum(rho, solver.dx)
    k_F, P_F, P_F_2d = compute_power_spectrum(F, solver.dx)
    
    # Find spectral peaks
    def find_peaks(k, P, min_prominence=0.1):
        from scipy.signal import find_peaks
        
        # Normalize power
        P_norm = P / np.max(P) if np.max(P) > 0 else P
        
        # Find peaks
        peaks, properties = find_peaks(P_norm, prominence=min_prominence)
        
        peak_info = []
        for i, peak_idx in enumerate(peaks):
            if k[peak_idx] > 0:  # Exclude k=0 (DC component)
                peak_info.append({
                    'k': k[peak_idx],
                    'power': P[peak_idx],
                    'prominence': properties['prominences'][i]
                })
        
        return sorted(peak_info, key=lambda x: x['power'], reverse=True)
    
    # Find peaks in F spectrum
    F_peaks = find_peaks(k_F, P_F, min_prominence=0.05)
    
    print("🎯 SPECTRAL PEAKS ANALYSIS:")
    if len(F_peaks) >= 2:
        # Highest peak is solar scale, next is galactic scale
        solar_peak = F_peaks[0]
        galactic_peak = F_peaks[1] if len(F_peaks) > 1 else F_peaks[0]
        
        scale_ratio = solar_peak['k'] / galactic_peak['k'] if galactic_peak['k'] > 0 else 0
        energy_ratio = solar_peak['power'] / galactic_peak['power'] if galactic_peak['power'] > 0 else 0
        
        print(f"SOLAR SCALE: k={solar_peak['k']:.3f} (high wavenumber)")
        print(f"GALACTIC SCALE: k={galactic_peak['k']:.3f} (low wavenumber)")
        print(f"SCALE SEPARATION RATIO: {scale_ratio:.1f}x")
        print(f"ENERGY RATIO: {energy_ratio:.1f}x")
        
        if scale_ratio >= 50:
            print("💫 SUCCESS: Strong scale separation confirmed!")
        elif scale_ratio >= 20:
            print("🔬 MODERATE: Clear scale separation observed")
        else:
            print("⚠️  WEAK: Limited scale separation")
    
    elif len(F_peaks) == 1:
        print(f"Single peak at k={F_peaks[0]['k']:.3f}")
        print("Insufficient peaks for scale separation analysis")
    else:
        print("No clear spectral peaks detected")
    
    # Analyze spectral energy distribution
    k_cutoff_solar = 10.0  # Approximate solar scale cutoff
    k_cutoff_galactic = 0.1  # Approximate galactic scale cutoff
    
    solar_energy = np.sum(P_F[k_F > k_cutoff_solar])
    galactic_energy = np.sum(P_F[k_F < k_cutoff_galactic])
    total_energy = np.sum(P_F[k_F > 0])  # Exclude k=0
    
    if total_energy > 0:
        solar_fraction = solar_energy / total_energy
        galactic_fraction = galactic_energy / total_energy
        
        print(f"\n📈 ENERGY DISTRIBUTION:")
        print(f"Solar scales (k > {k_cutoff_solar}): {solar_fraction:.1%}")
        print(f"Galactic scales (k < {k_cutoff_galactic}): {galactic_fraction:.1%}")
        print(f"Scale separation energy ratio: {solar_fraction/galactic_fraction:.1f}x")
    
    return {
        'k_F': k_F,
        'P_F': P_F,
        'peaks': F_peaks,
        'scale_ratio': scale_ratio if 'scale_ratio' in locals() else 0,
        'energy_ratio': energy_ratio if 'energy_ratio' in locals() else 0
    }

def plot_spectra(solver, results):
    """Plot the power spectra for visualization"""
    rho, E, F = solver.rho, solver.E, solver.F
    
    k_rho, P_rho, _ = compute_power_spectrum(rho, solver.dx)
    k_F, P_F, P_F_2d = compute_power_spectrum(F, solver.dx)
    
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(12, 10))
    
    # Plot F field
    im1 = ax1.imshow(F, cmap='RdBu_r', extent=[0, solver.domain_size, 0, solver.domain_size])
    ax1.set_title('F Field (Spatial Domain)')
    ax1.set_xlabel('x')
    ax1.set_ylabel('y')
    plt.colorbar(im1, ax=ax1)
    
    # Plot radial power spectrum
    ax2.loglog(k_F[k_F>0], P_F[k_F>0], 'b-', linewidth=2, label='F field')
    ax2.loglog(k_rho[k_rho>0], P_rho[k_rho>0], 'r--', alpha=0.7, label='ρ field')
    
    # Mark peaks
    if results['peaks']:
        for i, peak in enumerate(results['peaks'][:3]):  # Top 3 peaks
            ax2.axvline(peak['k'], color='orange', linestyle=':', alpha=0.8)
            ax2.text(peak['k'], peak['power'], f'Peak {i+1}', rotation=90, fontsize=8)
    
    ax2.set_xlabel('Wavenumber k')
    ax2.set_ylabel('Power Spectrum')
    ax2.set_title('Radial Power Spectrum')
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    
    # Plot 2D power spectrum
    im3 = ax3.imshow(np.log10(P_F_2d + 1e-10), cmap='viridis', 
                    extent=[-np.pi/solver.dx, np.pi/solver.dx, -np.pi/solver.dx, np.pi/solver.dx])
    ax3.set_title('2D F Power Spectrum (log scale)')
    ax3.set_xlabel('k_x')
    ax3.set_ylabel('k_y')
    plt.colorbar(im3, ax=ax3)
    
    # Plot scale separation summary
    ax4.axis('off')
    summary_text = f"""
    FOURIER ANALYSIS RESULTS
    
    Scale Separation Ratio: {results.get('scale_ratio', 0):.1f}x
    Energy Ratio: {results.get('energy_ratio', 0):.1f}x
    
    Spectral Peaks:
    """
    if results['peaks']:
        for i, peak in enumerate(results['peaks'][:3]):
            summary_text += f"\nPeak {i+1}: k={peak['k']:.3f}"
    
    ax4.text(0.1, 0.9, summary_text, transform=ax4.transAxes, fontfamily='monospace',
             verticalalignment='top', fontsize=10)
    
    plt.tight_layout()
    plt.savefig('fourier_scale_analysis.png', dpi=150, bbox_inches='tight')
    plt.show()

print("🚀 FOURIER SCALE SEPARATION ANALYSIS")
print("M=10000, η_power=20, ρ_cut=0.8")
print("Target: Quantify 100× scale separation in wavenumber domain")
print("=" * 70)

# Create and evolve solver
solver = CalibratedSolver(
    alpha=1e-5,
    delta1=25.0,
    M_factor=10000.0,
    eta_power=20.0,
    rho_cutoff=0.8
)

print("Initializing and evolving to stable state...")
solver.initialize_system('gaussian')
solver.evolve_system(500)  # Evolve to stable state

print("Performing Fourier analysis...")
results = analyze_scale_separation(solver)

print("\nGenerating spectral plots...")
plot_spectra(solver, results)

print(f"\n💫 FOURIER ANALYSIS COMPLETE")
print("Check 'fourier_scale_analysis.png' for spectral visualization")
print("Scale separation quantified in wavenumber domain!")
