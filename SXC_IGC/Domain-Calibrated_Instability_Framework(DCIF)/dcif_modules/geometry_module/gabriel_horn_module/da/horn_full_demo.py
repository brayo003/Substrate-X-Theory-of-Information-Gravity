import numpy as np
from scipy.integrate import quad
import csv

# =====================================================
# 1. Surface Area of Gabriel's Horn
# =====================================================

def surface_area(L):
    integrand = lambda x: (1/x) * np.sqrt(1 + 1/x**4)
    result, _ = quad(integrand, 1, L)
    return 2*np.pi*result

L_vals = np.linspace(1.1, 100, 200)
S_vals = np.array([surface_area(L) for L in L_vals])
log_approx = 2*np.pi*np.log(L_vals)

print("\n=== SURFACE AREA SAMPLE VALUES ===")
for i in range(0, len(L_vals), 40):
    print(f"L={L_vals[i]:.2f} | Exact S={S_vals[i]:.6f} | 2πlogL={log_approx[i]:.6f}")

# Residual analysis
residual = S_vals - log_approx
print("\n=== LOG SCALING ERROR ===")
print("Mean absolute error:", np.mean(np.abs(residual)))
print("Max absolute error:", np.max(np.abs(residual)))

# Save surface data
with open("horn_surface_data.csv", "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["L", "Exact_Surface", "Log_Approx", "Residual"])
    for L, S, A, R in zip(L_vals, S_vals, log_approx, residual):
        writer.writerow([L, S, A, R])

print("\nSurface data saved to horn_surface_data.csv")

# =====================================================
# 2. Dynamical Reduction
# =====================================================

def horn_dynamics(T, a, gamma, beta, E):
    return a*T**2 - gamma*T + beta*E

def simulate(T0, a, gamma, beta, E, dt=0.01, steps=5000):
    T = T0
    traj = []
    for _ in range(steps):
        T += dt * horn_dynamics(T, a, gamma, beta, E)
        traj.append(T)
    return np.array(traj)

a = 1.0
gamma = 1.0
beta = 1.0
E = 0.2

# Critical threshold
E_crit = gamma**2 / (4*a*beta)
print("\n=== BIFURCATION THRESHOLD ===")
print("Critical E =", E_crit)
print("Current E =", E)

# Fixed points
D = gamma**2 - 4*a*beta*E
if D >= 0:
    T1 = (gamma - np.sqrt(D)) / (2*a)
    T2 = (gamma + np.sqrt(D)) / (2*a)
    print("\n=== FIXED POINTS ===")
    print("T_stable =", T1)
    print("T_unstable =", T2)
else:
    print("\nNo real fixed points (post-bifurcation regime)")

# Stability classification
def stability(T):
    derivative = 2*a*T - gamma
    if derivative < 0:
        return "Stable"
    else:
        return "Unstable"

if D >= 0:
    print("\nStability of T_stable:", stability(T1))
    print("Stability of T_unstable:", stability(T2))

# Simulate dynamics
traj = simulate(0.1, a, gamma, beta, E)

print("\n=== TRAJECTORY STATISTICS ===")
print("Initial T =", traj[0])
print("Final T =", traj[-1])
print("Max T =", np.max(traj))
print("Min T =", np.min(traj))

# Save trajectory
with open("horn_dynamics_data.csv", "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["Step", "T"])
    for i, T in enumerate(traj):
        writer.writerow([i, T])

print("\nTrajectory data saved to horn_dynamics_data.csv")

print("\n=== COMPLETE ===")
