import numpy as np
from scipy.integrate import solve_ivp
import matplotlib.pyplot as plt

# Constants (in natural units where M_pl = 1)
H0 = 2.2e-18  # Hubble constant in 1/s (∼70 km/s/Mpc)
rho_crit = 3 * H0**2  # Critical density

# Model parameters from your framework
r = 0.153267
a = -0.333  # -1/3
b = 0.25    # 1/4

# Coupling parameter (to be constrained)
beta = 1e-3  # Initial guess
X0 = 1.0     # Background Substrate X field value

# Time span (in units of 1/H0)
t_span = (0.01, 100.0)  # From early universe to present
t_eval = np.logspace(-2, 2, 1000)  # Logarithmic time sampling

def s_field_derivatives(t, y, beta_val, X0_val):
    """Differential equations for the s-field and Hubble parameter."""
    x, xdot, H = y
    
    # s-field equation: ẍ + 3Hẋ + V'(x) = βX₀²
    xdotdot = -3 * H * xdot + r * x + a * x**2 + b * x**3 + beta_val * X0_val**2
    
    # Friedmann equation: 3H² = ρ_total
    rho_m = 0.3 * (1 + t**2) / t**2  # Matter density evolution (Ω_m = 0.3)
    rho_s = 0.5 * xdot**2 + 0.5 * r * x**2 + (a/3) * x**3 + (b/4) * x**4 - beta_val * X0_val**2 * x
    
    Hdot = -0.5 * (rho_m + rho_s + 3*0)  # Assuming pressureless matter
    
    return [xdot, xdotdot, Hdot]

# Initial conditions
x0 = 1e-5      # Small initial value
xdot0 = 0.0    # Initially static
H0_initial = 100 * H0  # Early universe H is much larger

y0 = [x0, xdot0, H0_initial]

# Solve the ODE
solution = solve_ivp(
    s_field_derivatives, 
    t_span, 
    y0, 
    t_eval=t_eval,
    args=(beta, X0),
    method='RK45',
    rtol=1e-6,
    atol=1e-8
)

# Plot results
plt.figure(figsize=(12, 8))

# Plot s-field evolution
plt.subplot(2, 1, 1)
plt.semilogx(solution.t, solution.y[0], 'b-', linewidth=2)
plt.xlabel('Time (1/H₀)')
plt.ylabel('s-field value')
plt.title('Cosmological Evolution of s-field')
plt.grid(True, which="both", ls="--")

# Plot Hubble parameter
plt.subplot(2, 1, 2)
plt.loglog(solution.t, solution.y[2]/H0, 'r-', linewidth=2)
plt.xlabel('Time (1/H₀)')
plt.ylabel('H(z)/H₀')
plt.title('Hubble Parameter Evolution')
plt.grid(True, which="both", ls="--")

plt.tight_layout()
plt.savefig('cosmological_evolution.png')
plt.show()
