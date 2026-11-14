import numpy as np

# operating point (from your runs)
T0 = 6.5
M0 = 30.0
z0 = 3.0

beta_base = 3.5
gamma_base = 0.8
kappa = 0.05
alpha = 0.6
lam = 0.3

radius = 1.0 / z0
beta = beta_base * (1.0 / radius**0.5)
gamma = gamma_base * radius
E = 0.8  # high-load regime

# partial derivatives (Jacobian)
dT_dT = -gamma
dT_dz = E * (beta / (2*z0))

dM_dT = alpha
dM_dM = -lam

dz_dM = kappa / ((1+M0)**2)

J = np.array([
    [dT_dT,     0.0,     dT_dz],
    [dM_dT, dM_dM,     0.0  ],
    [0.0,    dz_dM,    0.0  ]
])

eigvals = np.linalg.eigvals(J)

print("Jacobian:")
print(J)
print("\nEigenvalues:")
print(eigvals)
