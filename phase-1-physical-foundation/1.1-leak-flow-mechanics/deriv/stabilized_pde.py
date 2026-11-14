import numpy as np
import matplotlib.pyplot as plt

# ================================
# PARAMETERS (you can tune these)
# ================================
nx = 400
dx = 1.0
dt = 0.001        # small time step for stability
steps = 20000     # run longer to see steady state

# Physical parameters
tau = 5.0         # inertia
c = 1.0           # wave speed
v = 0.2           # advection velocity
alpha = 0.002     # energy coupling
E = 1.0           # constant energy source
sigma = 0.002     # linear damping
b = 0.001         # CUBIC SATURATION COEFFICIENT (THIS IS NEW)

# ================================
# INITIALIZATION
# ================================
s = np.zeros(nx)          # current density
s_prev = np.zeros(nx)     # previous time step (for leapfrog)
s_prev2 = np.zeros(nx)    # two steps ago

# Initial perturbation
center = nx//2
width = 10
s[center-width:center+width] = np.exp(-0.5 * (np.arange(-width, width)/5)**2)
s = s / np.sum(s) * 10    # normalize total information

s_prev = s.copy()
s_prev2 = s.copy()

# Storage for diagnostics
max_history = []
min_history = []
total_history = []
time_history = []

print("="*60)
print("STABILIZED SUBSTRATE-X PDE SOLVER")
print("="*60)
print(f"Grid: {nx} points, dx={dx}, dt={dt}")
print(f"tau={tau}, c={c}, v={v}")
print(f"alpha={alpha}, E={E}, sigma={sigma}")
print(f"CUBIC SATURATION b={b}")
print("="*60)

# ================================
# TIME STEPPING
# ================================
for step in range(steps):
    # Second derivatives (centered difference)
    laplacian = (np.roll(s, -1) + np.roll(s, 1) - 2*s) / dx**2
    
    # First derivative for advection (upwind)
    if v > 0:
        advection = v * (s - np.roll(s, 1)) / dx
    else:
        advection = v * (np.roll(s, -1) - s) / dx
    
    # SOURCE TERMS
    source = alpha * E
    
    # LINEAR DAMPING
    damping = sigma * s
    
    # CUBIC SATURATION (THIS PREVENTS BLOW-UP)
    saturation = b * s**3
    
    # Second time derivative (leapfrog approximation)
    if step == 0:
        # First step: forward Euler
        d2s_dt2 = 0
        ds_dt = (s - s_prev) / dt
    else:
        d2s_dt2 = (s - 2*s_prev + s_prev2) / dt**2
    
    # RHS of the PDE
    rhs = (c**2 * tau * laplacian 
           - advection
           + source 
           - damping 
           - saturation)
    
    # Time evolution (semi-implicit)
    if step == 0:
        s_next = s + dt * rhs
    else:
        # Leapfrog for second-order system
        s_next = 2*s - s_prev + dt**2 * (rhs - d2s_dt2)
    
    # Shift time levels
    s_prev2 = s_prev.copy()
    s_prev = s.copy()
    s = s_next
    
    # Diagnostics every 1000 steps
    if step % 1000 == 0:
        total = np.sum(s)
        max_val = np.max(s)
        min_val = np.min(s)
        
        max_history.append(max_val)
        min_history.append(min_val)
        total_history.append(total)
        time_history.append(step * dt)
        
        print(f"step {step:5d} | t={step*dt:.2f} | "
              f"max={max_val:.3e} | min={min_val:.3e} | total={total:.3e}")
        
        # Check for blow-up
        if max_val > 1e10 or np.isnan(max_val):
            print("\n❌ BLOW-UP DETECTED - parameters may need adjustment")
            break

print("\n" + "="*60)
print("SIMULATION COMPLETE")
print("="*60)
print(f"Final max density: {np.max(s):.3e}")
print(f"Final min density: {np.min(s):.3e}")
print(f"Final total info: {np.sum(s):.3e}")
print("="*60)

# ================================
# PLOT RESULTS
# ================================
plt.figure(figsize=(12,8))

plt.subplot(2,2,1)
plt.plot(s)
plt.title(f'Final Density Profile (t={steps*dt:.2f})')
plt.xlabel('Grid position')
plt.ylabel('s (info density)')
plt.grid(alpha=0.3)

plt.subplot(2,2,2)
plt.semilogy(time_history, max_history, label='max', color='red')
plt.semilogy(time_history, min_history, label='min', color='blue')
plt.xlabel('Time')
plt.ylabel('s (log scale)')
plt.title('Max/Min Density Evolution')
plt.legend()
plt.grid(alpha=0.3)

plt.subplot(2,2,3)
plt.plot(time_history, total_history)
plt.xlabel('Time')
plt.ylabel('Total information')
plt.title('Total Information (should stabilize)')
plt.grid(alpha=0.3)

plt.subplot(2,2,4)
plt.plot(s - np.roll(s,1), label='gradient')
plt.xlabel('Grid position')
plt.ylabel('∇s')
plt.title('Information Gradient')
plt.grid(alpha=0.3)

plt.tight_layout()
plt.savefig('stabilized_pde_results.png', dpi=150)
print("\n✅ Plot saved to stabilized_pde_results.png")
