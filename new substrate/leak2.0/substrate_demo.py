import numpy as np
import matplotlib.pyplot as plt
from scipy.integrate import solve_ivp
from scipy.signal import argrelextrema

class SubstrateXSolver:
    def __init__(self, G=1.0, m_X=0.0, M=1.0):
        self.G = G
        self.m_X = m_X
        self.M = M
        
    def yukawa_potential(self, r):
        if np.any(r == 0):
            r = np.maximum(r, 1e-12)
        return -self.G * self.M / r * np.exp(-self.m_X * r)
    
    def yukawa_force(self, r):
        if np.any(r == 0):
            r = np.maximum(r, 1e-12)
        term1 = self.G * self.M / r**2
        term2 = self.G * self.M * self.m_X / r
        return -(term1 + term2) * np.exp(-self.m_X * r)
    
    def orbital_equations(self, t, state):
        r, r_dot, theta, theta_dot = state
        if r <= 0:
            return [0, 0, 0, 0]
        r_ddot = r * theta_dot**2 + self.yukawa_force(r)
        theta_ddot = -2 * r_dot * theta_dot / r
        return [r_dot, r_ddot, theta_dot, theta_ddot]
    
    def solve_orbit(self, r0, v0_theta, t_span, n_steps=10000):
        state0 = [r0, 0.0, 0.0, v0_theta / r0]
        t_eval = np.linspace(t_span[0], t_span[1], n_steps)
        sol = solve_ivp(self.orbital_equations, t_span, state0, 
                       t_eval=t_eval, rtol=1e-8, atol=1e-10, method='RK45')
        return sol

def plot_potential_comparison():
    solver = SubstrateXSolver(G=1.0, M=1.0)
    r = np.linspace(0.1, 5.0, 1000)
    
    plt.figure(figsize=(12, 4))
    
    plt.subplot(131)
    for m_X in [0.0, 0.1, 0.5]:
        solver.m_X = m_X
        phi = solver.yukawa_potential(r)
        plt.plot(r, phi, label=f'm_X = {m_X}')
    plt.xlabel('r'); plt.ylabel('Φ(r)'); plt.legend()
    plt.title('Potential')
    
    plt.subplot(132)
    for m_X in [0.0, 0.1, 0.5]:
        solver.m_X = m_X
        force = solver.yukawa_force(r)
        plt.plot(r, -force, label=f'm_X = {m_X}')
    plt.xlabel('r'); plt.ylabel('-F(r)'); plt.legend()
    plt.title('Force')
    
    plt.subplot(133)
    for m_X in [0.1, 0.5]:
        solver.m_X = m_X
        force_yukawa = solver.yukawa_force(r)
        force_newton = -solver.G * solver.M / r**2
        ratio = -force_yukawa / force_newton
        plt.plot(r, ratio, label=f'm_X = {m_X}')
    plt.axhline(1.0, color='k', linestyle='--', alpha=0.5)
    plt.xlabel('r'); plt.ylabel('F_Yukawa / F_Newton'); plt.legend()
    plt.title('Force Ratio')
    
    plt.tight_layout()
    plt.show()

def measure_perihelion_precession():
    a = 1.0
    e = 0.2056
    r_peri = a * (1 - e)
    v_peri = np.sqrt((1 + e) / (r_peri * (1 - e)))
    
    t_span = [0, 10 * 2*np.pi]
    m_X_values = [0.0, 0.01, 0.05, 0.1]
    
    plt.figure(figsize=(10, 8))
    
    for i, m_X in enumerate(m_X_values):
        solver = SubstrateXSolver(G=1.0, M=1.0, m_X=m_X)
        sol = solver.solve_orbit(r_peri, v_peri, t_span, n_steps=50000)
        
        r_vals = sol.y[0]
        theta_vals = sol.y[2]
        
        idx_min = argrelextrema(r_vals, np.less, order=100)[0]
        
        if len(idx_min) > 1:
            peri_theta = theta_vals[idx_min]
            delta_theta = np.diff(peri_theta)
            precession = np.mean(delta_theta) - 2*np.pi
            print(f"m_X = {m_X:.3f}: Precession = {precession:.6f} rad/orbit")
        
        x_vals = r_vals * np.cos(theta_vals)
        y_vals = r_vals * np.sin(theta_vals)
        
        plt.subplot(2, 2, i+1)
        plt.plot(x_vals, y_vals, 'b-', alpha=0.7)
        plt.plot(0, 0, 'ro', markersize=10)
        plt.xlabel('x'); plt.ylabel('y')
        plt.title(f'm_X = {m_X}\nPrecession: {precession:.6f} rad/orbit')
        plt.axis('equal')
    
    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    print("=== Substrate X Numerical Demo ===")
    plot_potential_comparison()
    measure_perihelion_precession()
