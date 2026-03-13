import numpy as np
import matplotlib.pyplot as plt

a = 1.0
beta = 1.0
gamma = 1.0

# Choose E above threshold
E = 0.4   # critical is gamma^2/(4aβ) = 0.25

dt = 0.01
T = 0.1
history = []

for i in range(2000):
    dT = (a*T**2 - gamma*T + beta*E) * dt
    T += dT
    
    if T > 1e6:
        print("Blow-up detected at step:", i)
        break
        
    history.append(T)


plt.figure()
plt.plot(history)
plt.title("Finite-Time Blow-Up Regime")
plt.xlabel("Time Step")
plt.ylabel("T")
plt.show()
