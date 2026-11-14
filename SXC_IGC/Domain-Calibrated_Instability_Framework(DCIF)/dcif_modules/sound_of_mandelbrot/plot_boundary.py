import numpy as np
import matplotlib.pyplot as plt
from scipy import ndimage

phase = np.load('phase_data.npy')
phase_zoom = np.load('phase_zoom.npy')

# Find boundaries using Laplace filter
boundary = ndimage.laplace(phase.astype(float))
boundary_zoom = ndimage.laplace(phase_zoom.astype(float))

plt.figure(figsize=(12,5))
plt.subplot(1,2,1)
plt.imshow(np.abs(boundary).T, origin='lower', cmap='hot')
plt.title('Full Boundary')

plt.subplot(1,2,2)
plt.imshow(np.abs(boundary_zoom).T, origin='lower', cmap='hot')
plt.title('Zoomed Boundary')
plt.savefig('boundary_comparison.png')
print("✅ Saved boundary_comparison.png")
