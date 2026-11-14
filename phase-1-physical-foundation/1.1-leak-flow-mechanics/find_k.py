#!/usr/bin/env python3
import numpy as np

# Earth-Sun system
G = 6.67430e-11
M_sun = 1.989e30
M_earth = 5.972e24  
r_earth = 1.496e11

# Target force
F_target = G * M_sun * M_earth / r_earth**2
print(f"TARGET FORCE: {F_target:.2e} N")

# Your substrate parameters at Earth's orbit
R_sun = 7e8
s_star = 1e20  # at Sun surface
v_star = 1000  # at Sun surface

# At Earth's orbit
s_earth = s_star * (R_sun / r_earth)    # s ∝ 1/r
v_earth = v_star * (R_sun / r_earth)    # v ∝ 1/r

print(f"s_earth = {s_earth:.2e} info/m³")
print(f"v_earth = {v_earth:.2e} m/s")
print(f"s × v = {s_earth * v_earth:.2e}")

# Your force law: F = k × m × s × v
# So: k = F / (m × s × v)
k_correct = F_target / (M_earth * s_earth * v_earth)
print(f"CORRECT k = {k_correct:.2e}")

# Test it
F_test = k_correct * M_earth * s_earth * v_earth
print(f"TEST: {F_test:.2e} N (should match target)")
print(f"RATIO: {F_test/F_target:.6f}")
