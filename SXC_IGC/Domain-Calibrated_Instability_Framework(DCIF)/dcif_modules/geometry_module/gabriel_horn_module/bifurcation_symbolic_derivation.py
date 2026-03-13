import sympy as sp

# Symbols
T, a, beta, gamma, E = sp.symbols('T a beta gamma E', positive=True)

# Dynamical equation
f = a*T**2 - gamma*T + beta*E

# Fixed points
fixed_points = sp.solve(f, T)

# Jacobian
df_dT = sp.diff(f, T)

# Discriminant condition
discriminant = gamma**2 - 4*a*beta*E

print("=== Fixed Points ===")
print(fixed_points)

print("\n=== Jacobian ===")
print(df_dT)

print("\n=== Instability Condition ===")
print("Real equilibria exist if:", discriminant, ">= 0")

print("\n=== Bifurcation Threshold ===")
print("Critical surface:", sp.Eq(discriminant, 0))
