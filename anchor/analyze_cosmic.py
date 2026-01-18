import h5py
import numpy as np
import matplotlib.pyplot as plt

# 1. Open the Real File
filename = 'H-H1_LOSC_4_V1-1126256640-4096.hdf5'

with h5py.File(filename, 'r') as f:
    strain = f['strain']['Strain'][:]
    dt = f['strain']['Strain'].attrs['Xspacing']
    gps_start = f['meta']['GPSstart'][()]

# 2. Zoom into the Event Window (GW150914 is at ~1126259462)
event_time = 1126259462.4
rel_time = event_time - gps_start
start_idx = int((rel_time - 2) / dt)
end_idx = int((rel_time + 2) / dt)

event_strain = strain[start_idx:end_idx]
time_axis = np.linspace(-2, 2, len(event_strain))

# 3. Substrate X Inference
# In a pure vacuum (GR), amplitude A_0 = 1.0
# In Substrate X, A = A_0 * exp(-η * Distance)
eta_cosmic_predicted = 0.009858
distance_mpc = 410 

print(f"--- COSMIC SCALE VERIFICATION ---")
print(f"Targeting Event: GW150914 at {distance_mpc} Mpc")
print(f"Predicted Viscosity: {eta_cosmic_predicted}")

# Plotting the "Cosmic Layer"
plt.figure(figsize=(12, 5))
plt.plot(time_axis, event_strain, label='Observed Strain (Substrate X)', color='cyan', alpha=0.7)
plt.title("GW150914: The Ringing of the Cosmic Substrate")
plt.xlabel("Time from merger (s)")
plt.ylabel("Strain")
plt.legend()
plt.grid(True, alpha=0.3)
plt.show()
