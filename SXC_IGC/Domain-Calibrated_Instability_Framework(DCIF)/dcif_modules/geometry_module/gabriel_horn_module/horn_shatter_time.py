import numpy as np
import matplotlib.pyplot as plt
from scipy.integrate import solve_ivp

# ---------- CALIBRATED PARAMETERS ----------
a = 1.0
beta = 1.0
gamma = 1.0
kappa = 7.15 * gamma**2 / (4 * a * beta)   # = 1.7875
eps = 0.5

print(f"=== CALIBRATED PARAMETERS ===")
print(f"a = {a}, beta = {beta}, gamma = {gamma}")
print(f"kappa = {kappa:.4f} (from z_c = 7.15)")
print(f"eps = {eps}")
print(f"Critical length z_c = {4*a*beta*kappa/gamma**2:.2f}\n")

# ---------- SYSTEM DEFINITION WITH EVENT DETECTION ----------
def system(t, state):
    T, z = state
    dT = a*T**2 - gamma*T + beta*kappa/z
    dz = eps * T
    return [dT, dz]

def shatter_event(t, state):
    T, z = state
    return z - 7.15
shatter_event.terminal = True
shatter_event.direction = 1

# ---------- INTEGRATE EXACTLY TO SHATTER POINT ----------
sol = solve_ivp(system, [0, 100], [0.1, 1.0], 
                events=shatter_event, 
                max_step=0.001,
                rtol=1e-8, 
                atol=1e-11)

# ---------- RESULTS ----------
if sol.t_events[0].size > 0:
    t_shatter = sol.t_events[0][0]
    z_shatter = sol.y_events[0][0][1]
    T_shatter = sol.y_events[0][0][0]
    
    print(f"\n=== EXACT SHATTER TIME ===")
    print(f"Initial: T0 = 0.1, z0 = 1.0")
    print(f"Shatter at t = {t_shatter:.6f}")
    print(f"           z = {z_shatter:.4f} (target: 7.15)")
    print(f"           T = {T_shatter:.4f}")
else:
    print("\nNo shatter event detected within t=100")
    exit()

# ---------- TRAJECTORY PLOTS ----------
t_dense = np.linspace(0, t_shatter * 1.1, 10000)
sol_dense = solve_ivp(system, [0, t_shatter * 1.1], [0.1, 1.0], 
                      t_eval=t_dense, max_step=0.001)

plt.figure(figsize=(12, 4))

plt.subplot(1,3,1)
plt.plot(sol_dense.t, sol_dense.y[1], 'b-', linewidth=2)
plt.axhline(y=7.15, color='r', linestyle='--', label='z = 7.15 (shatter)')
plt.axvline(x=t_shatter, color='r', linestyle=':', alpha=0.5)
plt.xlabel('Time')
plt.ylabel('Horn length z')
plt.title('Horn growth to shatter')
plt.legend()
plt.grid(alpha=0.3)

plt.subplot(1,3,2)
plt.plot(sol_dense.t, sol_dense.y[0], 'g-', linewidth=2)
plt.axvline(x=t_shatter, color='r', linestyle=':', alpha=0.5)
plt.xlabel('Time')
plt.ylabel('Tension T')
plt.title('Tension evolution')
plt.grid(alpha=0.3)
plt.yscale('log')

plt.subplot(1,3,3)
plt.plot(sol_dense.y[0], sol_dense.y[1], 'b-', linewidth=2)
plt.plot(T_shatter, z_shatter, 'ro', markersize=8, label='Shatter point')
plt.xlabel('Tension T')
plt.ylabel('Horn length z')
plt.title('Phase trajectory')
plt.legend()
plt.grid(alpha=0.3)
plt.xlim(0, T_shatter * 1.1)
plt.ylim(1, z_shatter * 1.1)

plt.tight_layout()
plt.savefig('horn_shatter_time.png', dpi=150)
plt.show()

# ---------- CALIBRATED PHASE PORTRAIT ----------
T_vals = np.linspace(0, 2.0, 20)
z_vals = np.linspace(1, 8.0, 20)
T_grid, z_grid = np.meshgrid(T_vals, z_vals)

dT_grid = np.zeros_like(T_grid)
dz_grid = np.zeros_like(z_grid)

for i in range(len(T_vals)):
    for j in range(len(z_vals)):
        dT, dz = system(0, [T_grid[j,i], z_grid[j,i]])
        dT_grid[j,i] = dT
        dz_grid[j,i] = dz

plt.figure(figsize=(8, 6))
plt.quiver(T_grid, z_grid, dT_grid, dz_grid, alpha=0.6)
plt.axhline(y=7.15, color='r', linestyle='--', linewidth=2, label='Shatter line (z=7.15)')
plt.plot(T_shatter, z_shatter, 'ro', markersize=8, label='Shatter point')
plt.xlabel('Tension T')
plt.ylabel('Horn length z')
plt.title(f'Calibrated Phase Portrait (κ = {kappa:.2f})')
plt.xlim(0, 2.0)
plt.ylim(1, 8.0)
plt.legend()
plt.grid(alpha=0.3)
plt.savefig('horn_calibrated_phase_portrait.png', dpi=150)
plt.show()

print(f"\n✓ Module complete. Shatter time = {t_shatter:.6f}")
print(f"✓ Plots saved: horn_shatter_time.png, horn_calibrated_phase_portrait.png")
