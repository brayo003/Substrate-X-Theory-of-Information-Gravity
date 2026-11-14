import numpy as np
import h5py
from pycbc.types import TimeSeries
from pycbc.waveform import get_fd_waveform
from pycbc.filter import highpass, matched_filter
from pycbc.psd import interpolate, inverse_spectrum_truncation
from scipy.optimize import minimize_scalar

# 1. LOAD DATA
file_path = 'H-H1_LOSC_4_V1-1126256640-4096.hdf5'
with h5py.File(file_path, 'r') as f:
    data = f['strain/Strain'][:]
    dt = f['strain/Strain'].attrs['Xspacing']

strain = TimeSeries(data, delta_t=dt)
strain = highpass(strain, 15.0)

# 2. MATCH TEMPLATE LENGTH
target_len = len(strain) // 2 + 1
hp, hc = get_fd_waveform(approximant="IMRPhenomD",
                         mass1=36.2, mass2=29.1,
                         f_lower=20, delta_f=strain.delta_f)
hp.resize(target_len)

# 3. CALCULATE PSD
psd = strain.psd(4)
psd = interpolate(psd, strain.delta_f)
psd = inverse_spectrum_truncation(psd, int(4 * strain.sample_rate),
                                  low_frequency_cutoff=20)

# 4. OPTIMIZATION ENGINE
def get_snr_for_eta(eta):
    dist_mpc = 410
    freqs = hp.sample_frequencies
    # Viscous Damping: h(f) = h_GR(f) * exp(-eta * f^2 * D)
    attenuation = np.exp(-abs(eta) * (freqs**2) * dist_mpc)
    h_sx = hp * attenuation
    
    snr_series = matched_filter(h_sx, strain, psd=psd, low_frequency_cutoff=20)
    
    # FIX: Use the native PyCBC .max() method instead of np.max() 
    # to avoid the NumPy 'axis' keyword error.
    return -float(abs(snr_series).max())

# 5. EXECUTE INFERENCE
print("Starting rigorous inference...")
snr_gr = -get_snr_for_eta(0.0)

# Search for best eta in the cosmic range
res = minimize_scalar(get_snr_for_eta, bounds=(0, 1e-15), method='bounded')
best_eta = abs(res.x)
snr_sx = -res.fun

print(f"\n--- RIGOROUS SUBSTRATE X INFERENCE ---")
print(f"GR Baseline SNR (η=0): {snr_gr:.6f}")
print(f"Substrate X Best SNR:  {snr_sx:.6f} at η = {best_eta:.2e}")

delta_snr = snr_sx - snr_gr
if delta_snr > 0.01:
    print(f"RESULT: η={best_eta:.2e} improves SNR by {delta_snr:.4f}")
else:
    print(f"RESULT: No significant damping. Space is a vacuum (η=0).")
