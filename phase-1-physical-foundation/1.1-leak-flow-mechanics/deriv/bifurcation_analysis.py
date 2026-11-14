import numpy as np
import matplotlib.pyplot as plt

# ---------------------------------
# Model parameters
# ---------------------------------
a = 1.0
gamma = 1.0
beta = 1.0

Ecrit = gamma**2/(4*a*beta)

print("\n==============================")
print("Analytical critical E =",Ecrit)
print("==============================\n")

# ---------------------------------
# Dynamics
# ---------------------------------
def step(T,E,dt=0.01):
    return T + dt*(a*T*T - gamma*T + beta*E)

# ---------------------------------
# Test multiple E values
# ---------------------------------
E_values = np.linspace(0,0.6,20)

final_T = []

for E in E_values:

    T = 0.05

    for _ in range(5000):
        T = step(T,E)

        if T>50:
            break

    final_T.append(T)

# ---------------------------------
# Plot result
# ---------------------------------
plt.scatter(E_values,final_T)
plt.axvline(Ecrit)
plt.xlabel("E")
plt.ylabel("Final Tension")
plt.title("Bifurcation threshold test")
plt.show()
