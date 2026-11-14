# 🎯 SOLVER PATCH INSTRUCTIONS

## File: `src/numerical_solver.py`

### Change 1: Update method signature (around line 153)
```python
# OLD:
def add_point_mass(self, mass, position, radius=None):

# NEW:  
def add_point_mass(self, mass, position, k_eff=0.0, radius=None):
# OLD (WRONG):
density_scale = mass / (4 * np.pi * r_reg**3)  # Approximate density
self.E += -self.G * mass * density_scale / r_reg

# NEW (CORRECT):
self.E += -self.G * mass / r_reg  # Gravitational potential
# OLD (Newtonian only):
F_mag = self.G * mass / (r_reg**2)

# NEW (With enhancement):
g_newton = self.G * mass / (r_reg**2)
g_substrate = g_newton * (1 + k_eff)  # Apply enhancement
F_mag = g_substrate
# OLD:
print(f"Added mass {mass/self.M_sun:.3f} M_sun at ({x0/1e9:.2f}, {y0/1e9:.2f}) billion m")

# NEW:
print(f"Added mass {mass/self.M_sun:.3f} M_sun at ({x0/1e9:.2f}, {y0/1e9:.2f}) billion m with k_eff={k_eff}")

## 🎯 THE CORRECT APPROACH:

The key is to **call the original method first** to get the Newtonian baseline, then **add our enhancement** on top. This ensures we don't break the existing physics.

Run the corrected patch test and we should finally see proper k_eff values! 🚀



clear
