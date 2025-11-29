from sympy import symbols, simplify, Eq, solve, sqrt

delta1, delta2, tauE, tauF, R, K = symbols('delta1 delta2 tauE tauF R K', positive=True)

# New R definition (square root of time ratio)
R_expr = sqrt(tauF/tauE)
K_expr = delta1/delta2

# Critical delta1
delta1_crit = delta2

# C_universal expression
C_universal = simplify(R_expr * K_expr * delta1_crit)   # = sqrt(tauF/tauE) * delta1
C_universal_at_bif = C_universal.subs(delta1, delta1_crit)  # delta1=delta2

# Solve for tauF/tauE that yields C=2 (symbolic)
time_ratio_condition = solve(Eq(C_universal_at_bif, 2), tauF/tauE)

print("C_universal (general):", C_universal)
print("C_universal at bifurcation (delta1=delta2):", C_universal_at_bif)
print("Critical time ratio tauF/tauE for C=2:", time_ratio_condition)
