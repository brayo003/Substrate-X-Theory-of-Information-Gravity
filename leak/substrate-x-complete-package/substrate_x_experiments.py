#!/usr/bin/env python3
"""
Substrate X experimental sandbox (clean version)

This script compares Newtonian orbits to an experimental "Substrate X" model.
It numerically integrates simple two-body motion equations under modified
force laws to visualize how leak/puff corrections alter orbital stability.
"""

import numpy as np
from scipy.integrate import solve_ivp
import matplotlib.pyplot as plt

# ============================================================
# GLOBAL PARAMETERS
# ============================================================
G = 6.67430e-11  # gravitational constant
M = 5.972e24     # Earth mass (kg)
m = 1000         # test particle (kg)
r0 = 7.0e6       # initial radius (m)
v0 = np.sqrt(G*M/r0) * 0.9      # initial velocity (m/s)

t_max = 6000     # simulation time (s)
dt = 1           # time step

t_span = (0, t_max)
t_eval = np.arange(0, t_max, dt)

# ============================================================
# FORCE DEFINITIONS
# ============================================================

def newtonian_force(r):
    """Standard Newtonian gravitational force."""
    r_mag = np.linalg.norm(r)
    return -G * M / r_mag**3 * r


def substrate_raw_force(r):
    """
    Hypothetical 'raw substrate' force:
    Adds a non-linear distance-dependent correction (unphysical test form).
    """
    r_mag = np.linalg.norm(r)
    correction = np.exp(-r_mag / 1e7) * 1e-3
    return -G * M / r_mag**3 * r * (1 + correction)


def substrate_corrected_force(r, alpha):
    """
    Corrected Substrate X force model.
    alpha controls the 'leak/puff' feedback strength.
    """
    r_mag = np.linalg.norm(r)
    base = -G * M / r_mag**3 * r
    correction = alpha * np.exp(-r_mag / 1e7)
    return base * (1 + correction)


# ============================================================
# ORBIT INTEGRATOR
# ============================================================

def orbit_rhs(t, y, force_func):
    r = y[:2]
    v = y[2:]
    a = force_func(r) / m
    return np.concatenate((v, a))


def run_orbit(name, force_func):
    """Runs an orbit integration and returns solution."""
    print(f"Running {name}...")
    y0 = np.array([r0, 0, 0, v0])
    try:
        sol = solve_ivp(
            lambda t, y: orbit_rhs(t, y, force_func),
            t_span, y0, t_eval=t_eval, rtol=1e-8, atol=1e-10
        )
        if not sol.success:
            print(f"Warning: solver for {name} not successful: {sol.message}")
            return None
        return sol
    except Exception as e:
        print(f"Error in {name}: {e}")
        return None


# ============================================================
# RUN EXPERIMENTS
# ============================================================

sols = {}
sols['newton'] = run_orbit("Newton baseline", newtonian_force)
sols['substrate_raw'] = run_orbit("Substrate raw", substrate_raw_force)

alpha_values = np.arange(0, 1.3, 0.1)
sols_alpha = {}

for alpha in alpha_values:
    def f(r, a=alpha):
        return substrate_corrected_force(r, a)
    name = f"Substrate corrected alpha={alpha:.2f}"
    sols_alpha[alpha] = run_orbit(name, f)


# ============================================================
# DIAGNOSTICS
# ============================================================

print("\nEnergy variation diagnostics:")
for key, sol in sols.items():
    if sol is None:
        continue
    r = np.sqrt(sol.y[0]**2 + sol.y[1]**2)
    v2 = sol.y[2]**2 + sol.y[3]**2
    E = 0.5 * m * v2 - G * M * m / r
    dE = np.std(E) / np.abs(np.mean(E))
    print(f"{key:30s}: ΔE/E ≈ {dE:.3e}")

# ============================================================
# PLOTTING
# ============================================================

plt.figure(figsize=(7, 7))
plt.title("Substrate X Orbit Comparison")

# Plot alpha variants
for a in alpha_values:
    sol = sols_alpha.get(a)
    if sol is None:
        print(f"Skipping alpha={a:.1f} (integration failed)")
        continue
    plt.plot(sol.y[0], sol.y[1], label=f"α={a:.1f}")

# Plot Newton baseline
if sols['newton'] is not None:
    plt.plot(sols['newton'].y[0], sols['newton'].y[1], 'k--', label='Newton')

plt.xlabel("x [m]")
plt.ylabel("y [m]")
plt.legend()
plt.axis("equal")
plt.grid(True)
plt.tight_layout()
plt.savefig("orbit_comparison.png", dpi=200)
plt.show()
print("\n✅ Plot saved as orbit_comparison.png")

