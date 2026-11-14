import numpy as np
import matplotlib.pyplot as plt

# Fixed parameters
a = 1.0
beta = 1.0
gamma = 1.0

E_values = np.linspace(0, 1.0, 400)

T_stable = []
T_unstable = []

for E in E_values:
    D = gamma**2 - 4*a*beta*E
    if D >= 0:
        T1 = (gamma - np.sqrt(D)) / (2*a)
        T2 = (gamma + np.sqrt(D)) / (2*a)
        T_stable.append(T1)
        T_unstable.append(T2)
    else:
        T_stable.append(np.nan)
        T_unstable.append(np.nan)

plt.figure()
plt.plot(E_values, T_stable, label="Stable Branch")
plt.plot(E_values, T_unstable, linestyle='--', label="Unstable Branch")
plt.xlabel("E")
plt.ylabel("Equilibrium T")
plt.title("Saddle-Node Bifurcation Diagram")
plt.legend()
plt.show()
