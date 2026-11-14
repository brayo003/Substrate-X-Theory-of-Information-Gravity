import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from matplotlib.animation import FuncAnimation

# --- 1. Setup the 3D Universe ---
fig = plt.figure(figsize=(10, 8))
ax = fig.add_subplot(111, projection='3d')
ax.set_title("V12 Engine: Gabriel's Horn Geometry Shatter", fontsize=14, fontweight='bold')

# --- 2. The V12 Engine Parameters ---
a = 1.0
gamma = 1.0
beta = 1.0
critical_E = (gamma**2) / (4 * a * beta) # The threshold is 0.25

# --- 3. The 3D Rendering Function ---
def draw_horn(length, is_shattered=False):
    ax.clear()
    ax.set_xlim(1, 10)
    ax.set_ylim(-1, 1)
    ax.set_zlim(-1, 1)
    ax.axis('off') # Turn off the boring grid lines to look more cinematic

    # Create the 3D mesh grid
    u = np.linspace(1, length, 100) # Length of the horn (x-axis)
    v = np.linspace(0, 2 * np.pi, 60) # Rotation around the horn
    U, V = np.meshgrid(u, v)

    # Parametric equations for Gabriel's Horn (y = 1/x)
    X = U
    Y = (1 / U) * np.cos(V)
    Z = (1 / U) * np.sin(V)

    # If the V12 Engine breaks, we destroy the geometry matrix
    if is_shattered:
        noise_level = 0.5 * (length - 5.0) # Noise increases as it breaks further
        X += np.random.normal(0, noise_level, X.shape)
        Y += np.random.normal(0, noise_level, Y.shape)
        Z += np.random.normal(0, noise_level, Z.shape)
        color_map = 'inferno' # Turn it into an explosive fire color
    else:
        color_map = 'viridis' # Normal cool geometry color

    # Render the surface
    ax.plot_surface(X, Y, Z, cmap=color_map, edgecolor='none', alpha=0.9)
    
    status_text = f"Energy Flux (E): {length/20:.3f}\nCritical Limit: {critical_E:.3f}"
    if is_shattered:
        status_text += "\nSYSTEM SHATTERED: GEOMETRY COLLAPSE"
        ax.text2D(0.05, 0.95, status_text, transform=ax.transAxes, color='red', fontsize=12, fontweight='bold')
    else:
        status_text += "\nStatus: Stable Rendering"
        ax.text2D(0.05, 0.95, status_text, transform=ax.transAxes, color='green', fontsize=12)

# --- 4. The Animation Loop ---
def update(frame):
    # Frame scales from 0 to 100. We map this to Horn Length (L) and Energy (E)
    current_length = 1.0 + (frame * 0.1)
    current_E = current_length / 20.0 # Mapping length to energy for the simulation
    
    if current_E >= critical_E:
        draw_horn(current_length, is_shattered=True)
    else:
        draw_horn(current_length, is_shattered=False)

# Run the animation at 20 frames per second
print("⚛️ Booting 3D Geometry Renderer...")
ani = FuncAnimation(fig, update, frames=100, interval=50, repeat=False)

plt.show()
