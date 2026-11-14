import numpy as np
import matplotlib.pyplot as plt
import time

# --- 1. CORE PHYSICS (Layer 1: Immutable) ---
L, Nx = 10.0, 100
dx = L / (Nx - 1)
dt = 0.0005 
T_final = 1.0
Nt = int(T_final / dt)

# --- 2. DOMAIN ADAPTATION (Layer 2: Heterogeneity & Noise) ---
x = np.linspace(0, L, Nx)
rho = np.exp(-0.5 * ((x - 5) / 0.8)**2)
E, F = np.zeros(Nx), np.zeros(Nx)

# Heterogeneous Zone (The "Hunted" Cave effect)
delta1 = np.ones(Nx) * 1.5
delta1[(x > 4) & (x < 6)] = 6.0 

tau_rho, gamma1, delta2, gamma2, D_base = 0.5, 0.8, 0.5, 0.4, 0.05
noise_intensity = 0.02 # Stochastic forcing (η)

# --- 3. LAYER 3: TERMINAL LOGGING & ADAPTIVE CONTROL ---
energy_log = []
print(f"{'Step':<8} | {'Total Energy':<15} | {'Max Density':<12} | {'Status'}")
print("-" * 55)

for n in range(Nt):
    # Laplacian Calculation
    lap_rho = (np.roll(rho, -1) - 2*rho + np.roll(rho, 1)) / dx**2
    lap_E = (np.roll(E, -1) - 2*E + np.roll(E, 1)) / dx**2
    lap_F = (np.roll(F, -1) - 2*F + np.roll(F, 1)) / dx**2

    # Stochastic Noise (η) - Modeling Fluctuations
    eta = np.random.normal(0, noise_intensity, Nx)

    # Core Equations
    d_rho = D_base * lap_rho - (rho / tau_rho) + eta
    d_E = delta1 * rho - gamma1 * E + lap_E
    d_F = delta2 * E - gamma2 * F + lap_F

    rho += d_rho * dt
    E += d_E * dt
    F += d_F * dt

    # Boundary Conditions
    for field in [rho, E, F]: field[0], field[-1] = field[1], field[-2]

    # Terminal Output & Layer 3 Control logic
    if n % 200 == 0:
        total_energy = np.sum(rho + E + F) * dx
        max_rho = np.max(rho)
        
        # Adaptive Parameter Adjustment (Layer 3)
        status = "STABLE"
        if len(energy_log) > 1 and total_energy > energy_log[-1]:
            delta1 *= 0.99 # Dampen excitability if energy trends upward
            status = "ADAPTING"
        
        energy_log.append(total_energy)
        print(f"{n:<8} | {total_energy:<15.6f} | {max_rho:<12.6f} | {status}")

# --- 4. FINAL VISUALIZATION ---
plt.figure(figsize=(10, 5))
plt.plot(x, rho, label="Final Density (ρ)", color='cyan')
plt.plot(x, E, label="Final Excitation (E)", color='orange', ls='--')
plt.title("UMDE Final Validation: Stability under Noise & Control")
plt.legend()
plt.show()
