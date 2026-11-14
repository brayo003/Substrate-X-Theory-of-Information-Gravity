import sys
import numpy as np
import matplotlib.pyplot as plt

a = 1.0
beta = 1.0
gamma = 1.0
E = 0.4   # above threshold

dt = float(sys.argv[1]) if len(sys.argv) > 1 else 0.01
T = 0.1
history = []

for i in range(200000):
    dT = (a*T**2 - gamma*T + beta*E) * dt
    T += dT
    
    if T > 1e6:
        print("dt =", dt)
        print("Blow-up detected at step:", i)
        print("Approx blow-up time:", i*dt)
        break
        
    history.append(T)



plt.figure()
plt.plot(history)
plt.title("Finite-Time Blow-Up Regime")
plt.xlabel("Time Step")
plt.ylabel("T")
plt.show()
