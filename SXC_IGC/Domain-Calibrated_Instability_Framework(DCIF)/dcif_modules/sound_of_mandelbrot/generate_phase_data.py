import numpy as np
import matplotlib.pyplot as plt

# V12 engine (simplified for speed)
def check_firewall(r, a, steps=500):
    x = 0.1
    for _ in range(steps):
        x += 0.05 * (r * x + a * x**2 - 1.0 * x**3)
        if x > 0.5:  # K > 0.5 threshold
            return 1  # FIREWALL
    return 0  # NOMINAL

print("Generating full phase diagram...")
r_vals = np.linspace(0, 1, 200)
a_vals = np.linspace(0, 2, 200)
phase = np.zeros((len(r_vals), len(a_vals)))

for i, r in enumerate(r_vals):
    for j, a in enumerate(a_vals):
        phase[i, j] = check_firewall(r, a)

np.save('phase_data.npy', phase)
print("Saved phase_data.npy")

# Plot
plt.imshow(phase.T, origin='lower', extent=[0, 1, 0, 2], cmap='coolwarm', aspect='auto')
plt.xlabel('r (growth rate)')
plt.ylabel('a (nonlinearity)')
plt.title('Phase Diagram: NOMINAL (blue) vs FIREWALL (red)')
plt.colorbar(label='Phase')
plt.savefig('phase_diagram.png')
print("Saved phase_diagram.png")

print("\nGenerating zoom...")
zoom_r = np.linspace(0.4, 0.6, 400)
zoom_a = np.linspace(0.8, 1.2, 400)
phase_zoom = np.zeros((len(zoom_r), len(zoom_a)))

for i, r in enumerate(zoom_r):
    for j, a in enumerate(zoom_a):
        phase_zoom[i, j] = check_firewall(r, a)

np.save('phase_zoom.npy', phase_zoom)
print("Saved phase_zoom.npy")

plt.figure()
plt.imshow(phase_zoom.T, origin='lower', extent=[0.4, 0.6, 0.8, 1.2], cmap='coolwarm', aspect='auto')
plt.xlabel('r (zoom)')
plt.ylabel('a (zoom)')
plt.title('Zoom on Boundary')
plt.savefig('phase_zoom.png')
print("Saved phase_zoom.png")
