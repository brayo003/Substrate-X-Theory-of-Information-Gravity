import numpy as np
import matplotlib.pyplot as plt

# Parameters
a = 1.0
beta = 1.0
gamma = 1.0
kappa = 1.0
eps = 0.5

# Vector field
def system(T, z):
    dT = a*T**2 - gamma*T + beta*kappa/z
    dz = eps*T
    return dT, dz

# Grid
T_vals = np.linspace(-1, 2, 25)
z_vals = np.linspace(0.5, 3, 25)

T_grid, z_grid = np.meshgrid(T_vals, z_vals)

dT_grid = np.zeros_like(T_grid)
dz_grid = np.zeros_like(z_grid)

for i in range(len(T_vals)):
    for j in range(len(z_vals)):
        dT, dz = system(T_grid[j,i], z_grid[j,i])
        dT_grid[j,i] = dT
        dz_grid[j,i] = dz

plt.figure()
plt.quiver(T_grid, z_grid, dT_grid, dz_grid)
plt.xlabel("T")
plt.ylabel("z")
plt.title("Horn-Coupled Phase Portrait")
plt.show()
