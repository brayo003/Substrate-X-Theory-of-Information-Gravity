import numpy as np

G = 6.67430e-11
c = 299792458.0
R_H = 1.37e26

# What threshold gives observed Milky Way velocity at 8 kpc?
M_mw = 1.5e41
r_8kpc = 8 * 3.086e19

R_s = 2 * G * M_mw / c**2
x_total = R_s/r_8kpc + r_8kpc/R_H

print(f"Milky Way at 8 kpc:")
print(f"  R_s = {R_s:.2e} m")
print(f"  r = {r_8kpc:.2e} m")
print(f"  x_total = {x_total:.2e}")
print(f"  Your threshold: 0.05")
print(f"  Needed threshold to activate: ≤ {x_total:.2e}")
print(f"  Factor off by: {0.05/x_total:.0f}×")

# What bridge strength gives observed 230 km/s?
v_observed = 230e3  # m/s
g_needed = v_observed**2 / r_8kpc
g_newton = G * M_mw / r_8kpc**2
g_bridge_needed = g_needed - g_newton

print(f"\nTo get 230 km/s at 8 kpc:")
print(f"  g_newton = {g_newton:.2e} m/s²")
print(f"  g_needed = {g_needed:.2e} m/s²")
print(f"  g_bridge_needed = {g_bridge_needed:.2e} m/s²")
print(f"  Your bridge strength (c²/R_H) = {c**2/R_H:.2e} m/s²")
print(f"  Ratio (needed/your) = {g_bridge_needed/(c**2/R_H):.2f}")
