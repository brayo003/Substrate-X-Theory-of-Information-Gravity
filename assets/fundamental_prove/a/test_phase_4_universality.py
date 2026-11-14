import numpy as np
import matplotlib.pyplot as plt
from engine_core import sxc_drift

def run_test():
    dt = 0.05
    steps = 5000
    x0 = 0.1
    
    # Solvers
    euler = np.zeros(steps)
    rk4 = np.zeros(steps)
    
    euler[0] = rk4[0] = x0
    
    for t in range(1, steps):
        # Euler
        euler[t] = euler[t-1] + dt * sxc_drift(euler[t-1])
        
        # RK4
        k1 = sxc_drift(rk4[t-1])
        k2 = sxc_drift(rk4[t-1] + dt*k1/2)
        k3 = sxc_drift(rk4[t-1] + dt*k2/2)
        k4 = sxc_drift(rk4[t-1] + dt*k3)
        rk4[t] = rk4[t-1] + (dt/6)*(k1 + 2*k2 + 2*k3 + k4)

    plt.figure(figsize=(10, 5))
    plt.plot(euler, label='Euler (1st Order)')
    plt.plot(rk4, '--', label='RK4 (4th Order)')
    plt.axhline(y=1.5, color='r', linestyle=':', label='Theoretical Limit (1.5)')
    plt.title("Phase IV: Solver Invariance & Attractor Stability")
    plt.ylabel("Information Density (I)")
    plt.legend()
    plt.savefig('phase_4_universality.png')
    print("Universality test complete. Results saved to phase_4_universality.png")

if __name__ == "__main__":
    run_test()
