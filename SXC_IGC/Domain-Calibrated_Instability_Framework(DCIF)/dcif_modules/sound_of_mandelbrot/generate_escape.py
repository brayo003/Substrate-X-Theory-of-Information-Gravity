import numpy as np

def get_escape_time(c_min, c_max, size, max_iter):
    x = np.linspace(c_min.real, c_max.real, size)
    y = np.linspace(c_min.imag, c_max.imag, size)
    X, Y = np.meshgrid(x, y)
    C = X + 1j * Y
    Z = np.zeros_like(C)
    escape = np.zeros(C.shape, dtype=float)
    
    for i in range(max_iter):
        mask = np.abs(Z) <= 2
        Z[mask] = Z[mask]**2 + C[mask]
        escape[mask] = i
    return escape

print("Generating Full Map (200 iterations)...")
full_data = get_escape_time(-2.0 - 1.2j, 1.0 + 1.2j, 800, 200)
np.save('escape_time.npy', full_data)

print("Generating High-Res Zoom (2000 iterations, this may take 10-20 seconds)...")
zoom_data = get_escape_time(-0.755 - 0.105j, -0.745 - 0.095j, 800, 2000)
np.save('escape_time_zoom.npy', zoom_data)

print("✅ High-Resolution grids generated.")
