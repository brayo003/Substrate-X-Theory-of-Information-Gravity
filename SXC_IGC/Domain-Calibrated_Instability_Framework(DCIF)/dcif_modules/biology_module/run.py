import numpy as np
import matplotlib.pyplot as plt
from scipy.integrate import solve_ivp

# ---------- SUBSTRATE-X BACTERIA PARAMETERS ----------
a = 0.05      # Birth acceleration
gamma = 0.1   # Natural death rate
beta = 0.1    # Sensitivity to space
kappa = 5.0   # Total resource pool
eps = 0.2     # Rate at which bacteria consume space

def bacteria_system(t, state):
    T, z = state  # T = Population Tension, z = Space Occupied
    # The same math you used for the Horn!
    dT = a*T**2 - gamma*T + (beta * kappa / z)
    dz = eps * T
    return [dT, dz]

# Stop if the population "Shatters" (Explodes or Collapses)
def shatter_event(t, state):
    return state[0] - 50.0  # Threshold for "Shatter"
shatter_event.terminal = True

# ---------- RUN MONITORING ----------
sol = solve_ivp(bacteria_system, [0, 50], [2.0, 1.0], 
                events=shatter_event, max_step=0.1)

# ---------- VISUALIZE THE "LIFE SHATTER" ----------
plt.figure(figsize=(12, 5))

# Plot 1: Population Tension (The Sneeze/Crash Curve)
plt.subplot(1, 2, 1)
plt.plot(sol.t, sol.y[0], color='forestgreen', lw=2, label='Bacteria Tension')
plt.axvline(x=sol.t[-1], color='red', linestyle='--', label='Shatter Point')
plt.title("Biological Tension Monitoring")
plt.xlabel("Time")
plt.ylabel("Population Intensity")
plt.legend()
plt.grid(alpha=0.3)

# Plot 2: The Space-Tension Phase Portrait
plt.subplot(1, 2, 2)
plt.plot(sol.y[0], sol.y[1], color='blue', lw=2)
plt.scatter(sol.y[0][-1], sol.y[1][-1], color='red', s=100, zorder=5)
plt.title("Substrate Consumption Path")
plt.xlabel("Tension (T)")
plt.ylabel("Space Occupied (z)")
plt.grid(alpha=0.3)

plt.tight_layout()
plt.show()

print(f"Bacterial Shatter detected at t = {sol.t[-1]:.4f}")
