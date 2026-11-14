import numpy as np
import matplotlib.pyplot as plt
from scipy import ndimage
from sklearn.neighbors import NearestNeighbors

# Load your phase data
phase = np.load('escape_time.npy')
phase_zoom = np.load('escape_time_zoom.npy')

# Find the boundary using Laplace filter
boundary = ndimage.laplace(phase.astype(float))
boundary_points = np.where(np.abs(boundary) > 0.1)  # threshold to find edge

boundary_zoom = ndimage.laplace(phase_zoom.astype(float))
boundary_points_zoom = np.where(np.abs(boundary_zoom) > 0.1)

def fractal_dimension(points, resolution=100):
    """Estimate fractal dimension using box counting"""
    if len(points[0]) < 10:
        return np.nan
    
    # Convert to 2D array of coordinates
    coords = np.array([points[0], points[1]]).T
    
    # Simple box counting
    sizes = []
    counts = []
    for scale in np.linspace(1, min(phase.shape)/10, 20):
        size = int(scale)
        if size < 1: continue
        sizes.append(size)
        
        # Count boxes that contain points
        boxes = set()
        for x, y in coords:
            box = (int(x//size), int(y//size))
            boxes.add(box)
        counts.append(len(boxes))
    
    if len(counts) < 3:
        return np.nan
    
    # Fit power law: log(count) ~ D * log(1/size)
    log_sizes = np.log(1.0/np.array(sizes))
    log_counts = np.log(counts)
    D = np.polyfit(log_sizes, log_counts, 1)[0]
    return D

# Get boundary points
y_full, x_full = boundary_points
y_zoom, x_zoom = boundary_points_zoom

print(f"Full boundary points: {len(x_full)}")
print(f"Zoom boundary points: {len(x_zoom)}")

dim_full = fractal_dimension(boundary_points)
dim_zoom = fractal_dimension(boundary_points_zoom)

print(f"\nFractal dimension (full): {dim_full:.3f}")
print(f"Fractal dimension (zoom): {dim_zoom:.3f}")

if abs(dim_full - dim_zoom) < 0.2:
    print("\n✅ Dimensions match! The boundary is fractal (scale-invariant).")
else:
    print("\n❌ Dimensions differ. The boundary is not clearly fractal.")
