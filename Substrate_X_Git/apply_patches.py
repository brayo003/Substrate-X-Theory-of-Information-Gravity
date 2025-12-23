#!/usr/bin/env python3
"""Apply the necessary patches to the Substrate X solver"""

import re

# Read the current solver file
with open('src/numerical_solver.py', 'r') as f:
    content = f.read()

# Patch 1: Update method signature
old_signature = "def add_point_mass(self, mass, position, radius=None):"
new_signature = "def add_point_mass(self, mass, position, k_eff=0.0, radius=None):"
content = content.replace(old_signature, new_signature)

# Patch 2: Fix E field calculation
old_e_calc = """            density_scale = mass / (4 * np.pi * r_reg**3)  # Approximate density
            self.E += -self.G * mass * density_scale / r_reg"""
new_e_calc = """            self.E += -self.G * mass / r_reg  # Gravitational potential"""
content = content.replace(old_e_calc, new_e_calc)

# Patch 3: Apply k_eff enhancement to F field
old_f_calc = "            F_mag = self.G * mass / (r_reg**2)"
new_f_calc = """            g_newton = self.G * mass / (r_reg**2)
            g_substrate = g_newton * (1 + k_eff)  # Apply enhancement
            F_mag = g_substrate"""
content = content.replace(old_f_calc, new_f_calc)

# Patch 4: Update print statement
old_print = 'print(f"Added mass {mass/self.M_sun:.3f} M_sun at ({x0/1e9:.2f}, {y0/1e9:.2f}) billion m")'
new_print = 'print(f"Added mass {mass/self.M_sun:.3f} M_sun at ({x0/1e9:.2f}, {y0/1e9:.2f}) billion m with k_eff={k_eff}")'
content = content.replace(old_print, new_print)

# Write the patched file
with open('src/numerical_solver_patched.py', 'w') as f:
    f.write(content)

print("✅ Patches applied successfully!")
print("New file: src/numerical_solver_patched.py")
print("Replace the original file or update your imports to use the patched version.")
