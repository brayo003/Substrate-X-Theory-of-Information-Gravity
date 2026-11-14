import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.spatial.distance import cdist

# ================== LOAD PDB ==================
def parse_pdb(filename):
    coords = []
    with open(filename, 'r') as f:
        for line in f:
            if line.startswith('ATOM'):
                x = float(line[30:38])
                y = float(line[38:46])
                z = float(line[46:54])
                coords.append([x, y, z])
    return np.array(coords)

coords = parse_pdb('ubiquitin.pdb')
print(f"Loaded {len(coords)} atoms")

# ================== ELASTIC NETWORK MODEL ==================
# Create a simple spring network between nearby atoms
distances = cdist(coords, coords)
cutoff = 8.0  # Angstroms
springs = (distances < cutoff) & (distances > 0)

# ================== GENERATE TRAJECTORY ==================
# Simulate a simple pulling/relaxation
time_steps = 1000
dt = 0.01
positions = coords.copy()
energy_history = []

for t in range(time_steps):
    # Random perturbation (thermal noise)
    perturbation = np.random.randn(*positions.shape) * 0.01
    
    # Spring forces (simplified)
    forces = np.zeros_like(positions)
    for i in range(len(positions)):
        connected = np.where(springs[i])[0]
        for j in connected:
            vec = positions[j] - positions[i]
            dist = np.linalg.norm(vec)
            if dist > 0:
                forces[i] += vec / dist * 0.1  # simple spring constant
    
    positions += (forces * dt) + perturbation
    energy = np.sum(np.linalg.norm(forces, axis=1))
    energy_history.append(energy)

# ================== SAVE TRAJECTORY ==================
df = pd.DataFrame({
    'time': np.arange(time_steps) * dt,
    'energy': energy_history,
    'signal': (energy_history / np.max(energy_history)) * 100
})
df.to_csv('ubiquitin_trajectory.csv', index=False)
print("\n✅ Generated trajectory saved to ubiquitin_trajectory.csv")
print(f"Energy range: {min(energy_history):.2f} to {max(energy_history):.2f}")

# ================== QUICK PLOT ==================
plt.figure(figsize=(12, 4))
plt.subplot(1, 2, 1)
plt.plot(df['time'], df['energy'])
plt.xlabel('Time')
plt.ylabel('Energy')
plt.title('Protein Energy Trajectory')

plt.subplot(1, 2, 2)
plt.plot(df['time'], df['signal'])
plt.xlabel('Time')
plt.ylabel('Signal (scaled)')
plt.title('V12 Input Signal')
plt.tight_layout()
plt.savefig('protein_trajectory.png')
print("✅ Plot saved to protein_trajectory.png")
