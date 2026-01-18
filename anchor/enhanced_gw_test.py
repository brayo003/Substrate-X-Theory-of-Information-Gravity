#!/usr/bin/env python3
"""
Enhanced Substrate X Test with GW150914 Data
- Adds frequency-dependent viscosity model: η(f) = eta0 * (f/100)**alpha
- Includes error estimation via finite-difference SNR curvature
- Saves results and diagnostic plots
"""

import numpy as np
import h5py
import matplotlib.pyplot as plt
from scipy.optimize import minimize

# PyCBC imports
from pycbc.types import TimeSeries
from pycbc.waveform import get_fd_waveform
from pycbc.filter import highpass, matched_filter
from pycbc.psd import interpolate, inverse_spectrum_truncation

def load_and_preprocess_data():
    """Load LIGO data and preprocess"""
    file_path = 'H-H1_LOSC_4_V1-1126256640-4096.hdf5'
    
    print("Loading LIGO data...")
    with h5py.File(file_path, 'r') as f:
        data = f['strain/Strain'][:]
        # Get sampling info - handle different attribute names
        if 'Xspacing' in f['strain/Strain'].attrs:
            dt = f['strain/Strain'].attrs['Xspacing']
        elif 'dt' in f['strain/Strain'].attrs:
            dt = f['strain/Strain'].attrs['dt']
        else:
            # Default for O1 data
            dt = 1.0/4096
            print(f"  Using default dt = {dt}")
    
    strain = TimeSeries(data, delta_t=dt)
    print(f"  Loaded {len(strain)} samples at {1/dt:.0f} Hz")
    
    # Highpass filter
    strain = highpass(strain, 15.0)
    return strain

def setup_waveform_and_psd(strain):
    """Create template waveform and PSD"""
    # GW150914 parameters
    m1, m2 = 36.2, 29.1  # Solar masses
    
    print("Generating waveform template...")
    target_len = len(strain) // 2 + 1
    hp, _ = get_fd_waveform(
        approximant="IMRPhenomD",
        mass1=m1, mass2=m2,
        f_lower=20,
        delta_f=strain.delta_f
    )
    hp.resize(target_len)
    
    print("Calculating PSD...")
    psd = strain.psd(4)
    psd = interpolate(psd, strain.delta_f)
    psd = inverse_spectrum_truncation(
        psd, 
        int(4 * strain.sample_rate),
        low_frequency_cutoff=20
    )
    
    return hp, psd

def get_snr_for_eta(eta, strain, hp, psd, dist_mpc=410):
    """
    Calculate SNR for constant viscosity model
    Model: h(f) = h_GR(f) * exp(-eta * f^2 * D)
    """
    freqs = hp.sample_frequencies
    # Apply viscosity damping
    attenuation = np.exp(-np.abs(eta) * (freqs**2) * dist_mpc)
    h_sx = hp * attenuation
    
    # Matched filter
    snr_series = matched_filter(
        h_sx, strain, 
        psd=psd, 
        low_frequency_cutoff=20
    )
    
    return float(abs(snr_series).max())

def get_snr_for_freq_dependent_eta(params, strain, hp, psd, dist_mpc=410):
    """
    Calculate SNR for frequency-dependent viscosity model
    Model: η(f) = eta0 * (f/100)^alpha
           h(f) = h_GR(f) * exp(-η(f) * f^2 * D)
    """
    eta0, alpha = params
    freqs = hp.sample_frequencies
    
    # Frequency-dependent viscosity
    eta_f = eta0 * (freqs/100.0)**alpha
    # Ensure non-negative
    eta_f = np.abs(eta_f)
    
    # Apply damping
    attenuation = np.exp(-eta_f * (freqs**2) * dist_mpc)
    h_sx = hp * attenuation
    
    # Matched filter
    snr_series = matched_filter(
        h_sx, strain, 
        psd=psd, 
        low_frequency_cutoff=20
    )
    
    # Return negative for minimization
    return -float(abs(snr_series).max())

def estimate_error(optimal_eta, strain, hp, psd, dist_mpc=410, delta=1e-17):
    """Estimate error using finite differences around optimal eta"""
    snr_opt = get_snr_for_eta(optimal_eta, strain, hp, psd, dist_mpc)
    snr_plus = get_snr_for_eta(optimal_eta + delta, strain, hp, psd, dist_mpc)
    snr_minus = get_snr_for_eta(optimal_eta - delta, strain, hp, psd, dist_mpc)
    
    # Second derivative approximation
    curvature = (snr_plus - 2*snr_opt + snr_minus) / (delta**2)
    
    if curvature < 0:
        # Maximum, so curvature should be negative
        sigma_eta = np.sqrt(-1.0 / curvature)
    else:
        sigma_eta = np.nan
    
    return sigma_eta

def test_constant_viscosity(strain, hp, psd):
    """Test constant viscosity model"""
    print("\n" + "="*60)
    print("TEST 1: CONSTANT VISCOSITY MODEL")
    print("="*60)
    
    # Get GR baseline
    snr_gr = get_snr_for_eta(0.0, strain, hp, psd)
    print(f"GR Baseline SNR (η=0): {snr_gr:.6f}")
    
    # Optimize for eta
    print("Optimizing for viscosity parameter η...")
    from scipy.optimize import minimize_scalar
    
    res = minimize_scalar(
        lambda eta: -get_snr_for_eta(eta, strain, hp, psd),
        bounds=(0, 1e-14),
        method='bounded'
    )
    
    best_eta = res.x
    snr_best = -res.fun
    delta_snr = snr_best - snr_gr
    
    # Estimate error
    eta_err = estimate_error(best_eta, strain, hp, psd)
    
    print(f"\nResults:")
    print(f"  Optimal η:      ({best_eta:.2e} ± {eta_err:.2e})")
    print(f"  Best SNR:       {snr_best:.6f}")
    print(f"  ΔSNR:           {delta_snr:.6f}")
    
    # Statistical significance
    if abs(delta_snr) < 0.1:
        print(f"  Conclusion:     No evidence for viscosity (η consistent with 0)")
        print(f"                  Upper limit: η < {best_eta + 2*eta_err:.1e} (95% CL)")
    else:
        print(f"  Conclusion:     Potential viscosity detected!")
        print(f"                  Significance: {abs(delta_snr):.1f}σ")
    
    return best_eta, eta_err, snr_gr, snr_best

def test_frequency_dependent_viscosity(strain, hp, psd, constant_eta_result):
    """Test frequency-dependent viscosity model"""
    print("\n" + "="*60)
    print("TEST 2: FREQUENCY-DEPENDENT VISCOSITY MODEL")
    print("="*60)
    print("Model: η(f) = η₀ × (f/100 Hz)^α")
    
    # Initial guess: small eta0, negative alpha (viscosity decreases with freq)
    eta0_guess = constant_eta_result[0]  # From constant model
    initial_guess = [max(eta0_guess, 1e-18), -1.0]  # [eta0, alpha]
    
    print(f"Initial guess: η₀ = {initial_guess[0]:.1e}, α = {initial_guess[1]:.2f}")
    
    # Optimize
    bounds = [(0, 1e-12), (-3, 2)]  # eta0, alpha bounds
    
    res = minimize(
        get_snr_for_freq_dependent_eta,
        initial_guess,
        args=(strain, hp, psd),
        bounds=bounds,
        method='L-BFGS-B'
    )
    
    eta0_opt, alpha_opt = res.x
    snr_opt = -res.fun
    
    # Compare with GR
    snr_gr = get_snr_for_eta(0.0, strain, hp, psd)
    delta_snr = snr_opt - snr_gr
    
    print(f"\nResults:")
    print(f"  Optimal η₀:     {eta0_opt:.2e}")
    print(f"  Optimal α:      {alpha_opt:.2f}")
    print(f"  Best SNR:       {snr_opt:.6f}")
    print(f"  ΔSNR vs GR:     {delta_snr:.6f}")
    
    # Calculate implied viscosity at different frequencies
    print(f"\nImplied viscosities:")
    print(f"  At 100 Hz:      η = {eta0_opt * (100/100)**alpha_opt:.2e}")
    print(f"  At 1 Hz:        η = {eta0_opt * (1/100)**alpha_opt:.2e}")
    print(f"  At 0.001 Hz:    η = {eta0_opt * (0.001/100)**alpha_opt:.2e}")
    
    if alpha_opt < -0.5:
        print(f"\nConclusion: Strong frequency dependence (α = {alpha_opt:.2f})")
        print(f"            Could reconcile GW limits with Pioneer anomaly")
    else:
        print(f"\nConclusion: Weak frequency dependence")
    
    return eta0_opt, alpha_opt, snr_opt

def create_diagnostic_plots(strain, hp, psd, const_results, freq_results):
    """Create diagnostic plots"""
    print("\nGenerating diagnostic plots...")
    
    # Plot 1: SNR vs eta
    etas = np.logspace(-20, -12, 50)
    snrs = [get_snr_for_eta(eta, strain, hp, psd) for eta in etas]
    
    plt.figure(figsize=(12, 4))
    
    plt.subplot(1, 3, 1)
    plt.loglog(etas, snrs, 'b-', linewidth=2)
    plt.axvline(const_results[0], color='r', linestyle='--', 
                label=f'Optimal η = {const_results[0]:.1e}')
    plt.xlabel('Viscosity η')
    plt.ylabel('SNR')
    plt.title('SNR vs Constant Viscosity')
    plt.grid(True, alpha=0.3)
    plt.legend()
    
    # Plot 2: Frequency-dependent model visualization
    plt.subplot(1, 3, 2)
    freqs = np.logspace(0, 3, 100)  # 1 Hz to 1 kHz
    eta0, alpha = freq_results[0], freq_results[1]
    eta_f = eta0 * (freqs/100)**alpha
    
    plt.loglog(freqs, eta_f, 'r-', linewidth=2)
    plt.xlabel('Frequency (Hz)')
    plt.ylabel('η(f)')
    plt.title(f'Frequency-dependent viscosity\nη₀={eta0:.1e}, α={alpha:.2f}')
    plt.grid(True, alpha=0.3)
    
    # Plot 3: Strain data snippet
    plt.subplot(1, 3, 3)
    time = np.arange(1000) / strain.sample_rate
    plt.plot(time, strain.numpy()[:1000], 'b-', alpha=0.7)
    plt.xlabel('Time (s)')
    plt.ylabel('Strain')
    plt.title('First 1000 samples of filtered strain')
    plt.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('substrate_x_diagnostics.png', dpi=150, bbox_inches='tight')
    print("  Saved plot to 'substrate_x_diagnostics.png'")

def main():
    """Main analysis function"""
    print("="*60)
    print("ENHANCED SUBSTRATE X ANALYSIS WITH GW150914")
    print("="*60)
    
    # Load and preprocess
    strain = load_and_preprocess_data()
    hp, psd = setup_waveform_and_psd(strain)
    
    # Test 1: Constant viscosity
    const_results = test_constant_viscosity(strain, hp, psd)
    
    # Test 2: Frequency-dependent viscosity
    freq_results = test_frequency_dependent_viscosity(strain, hp, psd, const_results)
    
    # Create plots
    create_diagnostic_plots(strain, hp, psd, const_results, freq_results)
    
    # Save results
    with open('substrate_x_results.txt', 'w') as f:
        f.write("# Substrate X Analysis Results - GW150914\n")
        f.write(f"# Constant model: η = {const_results[0]:.6e} ± {const_results[1]:.6e}\n")
        f.write(f"# Frequency model: η₀ = {freq_results[0]:.6e}, α = {freq_results[1]:.6f}\n")
        f.write(f"# SNR_GR = {const_results[2]:.6f}, SNR_best = {const_results[3]:.6f}\n")
        f.write(f"# Implied η at 0.001 Hz = {freq_results[0] * (0.001/100)**freq_results[1]:.6e}\n")
    
    print("\n" + "="*60)
    print("ANALYSIS COMPLETE")
    print("="*60)
    print("\nNext steps:")
    print("1. Compare implied low-frequency η with Pioneer anomaly result")
    print("2. Test with additional GW events (GW151226, GW170104, etc.)")
    print("3. Analyze pulsar timing data for nHz-frequency constraints")
    print("\nResults saved to 'substrate_x_results.txt'")

if __name__ == "__main__":
    main()
