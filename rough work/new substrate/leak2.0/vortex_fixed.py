import numpy as np
import matplotlib.pyplot as plt
from scipy.integrate import solve_ivp

class SubstrateXVortex:
    def __init__(self, g=1.0, m_X=0.1, hbar=1.0, mass=1.0):
        self.g = g
        self.m_X = m_X
        self.hbar = hbar
        self.mass = mass
        
    def solve_vortex(self, R_max=20.0, n_points=1000):
        """Solve vortex using shooting method"""
        def vortex_eqns(r, y, mu):
            psi, psi_prime = y
            n = 1  # winding number
            
            if r < 1e-10:
                # Near origin expansion
                dpsi_dr = psi_prime
                d2psi_dr2 = (2.0 * self.mass / self.hbar**2) * (mu - self.m_X**2 * self.hbar**2/(2*self.mass)) * psi
            else:
                dpsi_dr = psi_prime
                d2psi_dr2 = - (1/r)*psi_prime + (n**2/r**2)*psi + \
                            (2*self.mass/self.hbar**2) * (mu - self.g*abs(psi)**2 - \
                            self.m_X**2 * self.hbar**2/(2*self.mass)) * psi
            return [dpsi_dr, d2psi_dr2]
        
        # Find correct chemical potential
        def objective(mu):
            r_span = [1e-8, R_max]
            sol = solve_ivp(
                lambda r, y: vortex_eqns(r, y, mu),
                r_span, [0.0, 1.0], 
                t_eval=np.linspace(1e-8, R_max, n_points),
                rtol=1e-6
            )
            return sol.y[0][-1] - 1.0  # Target psi(∞)=1
        
        from scipy.optimize import root_scalar
        mu_sol = root_scalar(objective, bracket=[-1.0, 0.0], method='bisect')
        mu = mu_sol.root
        
        # Final solution
        r_span = [1e-8, R_max]
        sol = solve_ivp(
            lambda r, y: vortex_eqns(r, y, mu),
            r_span, [0.0, 1.0], 
            t_eval=np.linspace(1e-8, R_max, n_points),
            rtol=1e-8
        )
        
        return sol.t, sol.y[0], sol.y[1], mu
    
    def compute_vortex_energy(self, r, psi, psi_prime):
        """Compute vortex mass/energy"""
        n = 1
        dr = r[1] - r[0]
        
        # Remove origin to avoid division by zero
        r_safe = r[1:]
        psi_safe = psi[1:]
        psi_prime_safe = psi_prime[1:]
        
        # Energy densities
        kinetic = 0.5 * self.hbar**2/self.mass * (psi_prime_safe**2 + (n**2/r_safe**2)*psi_safe**2)
        interaction = 0.5 * self.g * psi_safe**4
        substrate = 0.5 * self.m_X**2 * self.hbar**2 * psi_safe**2
        
        total_density = kinetic + interaction + substrate
        total_energy = 2 * np.pi * np.sum(total_density * r_safe) * dr
        
        return total_energy, total_density

def run_vortex_analysis():
    print("=== SUBSTRATE X VORTEX ANALYSIS ===")
    
    vortex = SubstrateXVortex()
    m_X_values = [0.01, 0.1, 0.5, 1.0]
    
    plt.figure(figsize=(15, 5))
    
    # Plot 1: Vortex profiles
    plt.subplot(131)
    for m_X in m_X_values:
        vortex.m_X = m_X
        r, psi, psi_prime, mu = vortex.solve_vortex()
        plt.plot(r, psi, label=f'm_X = {m_X}')
        print(f"m_X = {m_X:.2f}: μ = {mu:.4f}, ψ(∞) = {psi[-1]:.4f}")
    
    plt.xlabel('r'); plt.ylabel('ψ(r)'); plt.legend()
    plt.title('Vortex Profiles')
    
    # Plot 2: Energy density for one case
    plt.subplot(132)
    vortex.m_X = 0.1
    r, psi, psi_prime, mu = vortex.solve_vortex()
    energy, energy_density = vortex.compute_vortex_energy(r, psi, psi_prime)
    plt.plot(r[1:], energy_density, 'r-')
    plt.xlabel('r'); plt.ylabel('Energy Density')
    plt.title(f'Total Energy = {energy:.3f}')
    
    # Plot 3: Mass spectrum
    plt.subplot(133)
    masses = []
    for m_X in m_X_values:
        vortex.m_X = m_X
        r, psi, psi_prime, mu = vortex.solve_vortex()
        energy, _ = vortex.compute_vortex_energy(r, psi, psi_prime)
        masses.append(energy)
        print(f"m_X = {m_X:.2f} → Vortex Mass = {energy:.4f}")
    
    plt.plot(m_X_values, masses, 'bo-')
    plt.xlabel('m_X'); plt.ylabel('Vortex Mass')
    plt.title('Mass Spectrum')
    
    plt.tight_layout()
    plt.savefig('vortex_results.png')
    plt.show()
    
    print("\n=== RESULTS SUMMARY ===")
    print("Vortex solutions found successfully!")
    print("Check vortex_results.png for plots")
    return masses

if __name__ == "__main__":
    masses = run_vortex_analysis()
