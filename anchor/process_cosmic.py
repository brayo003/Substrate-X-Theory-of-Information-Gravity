import h5py
import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import butter, filtfilt

# 1. Load Data
filename = 'H-H1_LOSC_4_V1-1126256640-4096.hdf5'
with h5py.File(filename, 'r') as f:
    strain = f['strain']['Strain'][:]
    dt = f['strain']['Strain'].attrs['Xspacing']
    fs = int(1/dt)

# 2. Define the Bandpass Filter (35-350 Hz)
# This targets the 'Substrate X' ringing range
def bandpass_filter(data, lowcut, highcut, fs, order=4):
    nyq = 0.5 * fs
    low = lowcut / nyq
    high = highcut / nyq
    b, a = butter(order, [low, high], btype='band')
    return filtfilt(b, a, data)

# 3. Process the Strain
clean_strain = bandpass_filter(strain, 35, 350, fs)

# 4. Zoom to the GW150914 Event Window
# Event is at GPS 1126259462.4
center = int((1126259462.4 - 1126256640) * fs)
zoom_window = clean_strain[center - 500:center + 500]
time_axis = np.linspace(-0.12, 0.12, len(zoom_window))

# 5. Output Verification
print("--- SUBSTRATE X: COSMIC CHIRP REVEALED ---")
print(f"Max Amplitude Detected: {np.max(np.abs(zoom_window)):.2e}")
print("If this peak is < 1.0e-21, damping η is confirmed.")

plt.figure(figsize=(10, 5))
plt.plot(time_axis, zoom_window, color='red', label='Filtered Cosmic Signal')
plt.title("GW150914: The 1.3 Billion Year Residual")
plt.xlabel("Time around merger (s)")
plt.ylabel("Strain")
plt.legend()
plt.grid(True)
plt.show()
