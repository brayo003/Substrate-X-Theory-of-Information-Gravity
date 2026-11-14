import numpy as np
import matplotlib.pyplot as plt

# True parameters
Gamma0 = 1e3
k = 4.5e-7
om = 1e6
sigma_rel = 0.02   # 2% noise

omega = np.logspace(3, 8, 20)

def substrate(omega, Gamma0, k, om):
    return Gamma0 + k * omega**2 / (1 + (omega/om)**2)

# Compute derivatives numerically
eps = 1e-3 * np.array([Gamma0, k, om])
def derivative(func, theta, i, omega):
    theta1 = theta.copy()
    theta2 = theta.copy()
    theta1[i] += eps[i]
    theta2[i] -= eps[i]
    return (func(omega, *theta1) - func(omega, *theta2)) / (2*eps[i])

theta = np.array([Gamma0, k, om])

# Fisher information matrix I_ij = sum_n (1/sigma_n^2) * (dΓ/dθ_i)(dΓ/dθ_j)
sigma = sigma_rel * substrate(omega, *theta)
I = np.zeros((3,3))
for i in range(3):
    dG_i = derivative(substrate, theta, i, omega)
    for j in range(3):
        dG_j = derivative(substrate, theta, j, omega)
        I[i,j] = np.sum( (dG_i * dG_j) / sigma**2 )

# Cramér-Rao lower bound (covariance matrix)
C = np.linalg.inv(I)
errors = np.sqrt(np.diag(C))

print("Cramér-Rao lower bounds (1σ):")
print(f"  σ_Γ0  = {errors[0]:.2e}")
print(f"  σ_k   = {errors[1]:.2e}   (relative: {errors[1]/k*100:.2f}%)")
print(f"  σ_ω   = {errors[2]:.2e}   (relative: {errors[2]/om*100:.2f}%)")
print()
print("Compare with MCMC from Stage 7 (2% noise):")
print("  σ_k/k ~ 1.12%, σ_ω/ω ~ 0.73%")
