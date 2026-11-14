import sympy as sp

# Symbols
T, z = sp.symbols('T z')
a, beta, gamma, kappa, eps = sp.symbols('a beta gamma kappa eps', positive=True)

# Geometric excitation
E = kappa / z

# Coupled system
f1 = a*T**2 - gamma*T + beta*E
f2 = eps*T

# Jacobian matrix
J = sp.Matrix([
    [sp.diff(f1, T), sp.diff(f1, z)],
    [sp.diff(f2, T), sp.diff(f2, z)]
])

print("=== System ===")
print("dT/dt =", f1)
print("dz/dt =", f2)

print("\n=== Jacobian ===")
sp.pprint(J)

# Fixed points
fixed = sp.solve([f1, f2], (T, z), dict=True)
print("\n=== Fixed Points ===")
print(fixed)

