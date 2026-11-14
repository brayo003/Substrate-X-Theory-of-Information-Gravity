import sys
import numpy as np
import matplotlib.pyplot as plt

resolution = int(sys.argv[1]) if len(sys.argv) > 1 else 200

a = 1.0
beta = 1.0
gamma = 1.0

E_vals = np.linspace(0, 0.4, resolution)

stable_branch = []
unstable_branch = []

for E in E_vals:
    D = gamma**2 - 4*a*beta*E
    if D >= 0:
        T1 = (gamma - np.sqrt(D)) / (2*a)
        T2 = (gamma + np.sqrt(D)) / (2*a)
        stable_branch.append(T1)
        unstable_branch.append(T2)
    else:
        stable_branch.append(np.nan)
        unstable_branch.append(np.nan)

plt.plot(E_vals, stable_branch)
plt.plot(E_vals, unstable_branch)
plt.show()
