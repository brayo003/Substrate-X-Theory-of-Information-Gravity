import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import minimize
from scipy.integrate import solve_ivp

class SubstrateXDataFits:
    def __init__(self):
        # Physical constants
        self.G = 6.67430e-11
        self.c = 299792458.0
        self.M_sun = 1.98847e30
        self.AU = 1.496e11
        self.parsec = 3.08567758e16
        
        # Solar system data
        self.mercury_data = {
            'a': 0.3871 * self.AU, 'e': 0.2056, 'period': 87.969 * 24 * 3600,
            'observed_precession': 42.98  # arcsec/century
        }
        self.earth_data = {
            'a': 1.0 * self.AU, 'e': 0.0167, 'period': 365.256 * 24 * 3600,  
            'observed_precession': 3.84  # arcsec/century
        }
        
        # Galactic rotation data (approximate)
        self.galactic_data = {
            'r_kpc': np.array([1, 5, 10, 15, 20]),  # radius in kpc
            'v_km_s': np.array([200, 220, 240, 230, 220])  # rotation velocity
        }
        self.galactic_data['r_m'] = self.galactic_data['r_kpc'] * 1e3 * self.parsec
        
        # Pioneer anomaly (if any residual)
        self.pioneer_accel = 8.74e-10  # m/s² (original reported value)
    
    def substrate_x_acceleration(self, r, m_X, alpha=1.0):
        """Acceleration in Substrate X theory"""
        # Yukawa-like modification
        base_accel = self.G * self.M_sun / r**2
        yukawa_factor = (1 + m_X * r) * np.exp(-m_X * r)
        return base_accel * yukawa_factor * alpha
    
    def newtonian_acceleration(self, r):
        """Standard Newtonian acceleration"""
        return self.G * self.M_sun / r**2
    
    def compute_precession(self, a, e, m_X, alpha=1.0, n_orbits=10):
        """Compute orbital precession for given parameters"""
        def orbital_equations(t, state):
            r, r_dot, theta, theta_dot = state
            if r <= 0: return [0, 0, 0, 0]
            
            # Substrate X acceleration
            accel = -self.substrate_x_acceleration(r, m_X, alpha)
            
            r_ddot = r * theta_dot**2 + accel
            theta_ddot = -2 * r_dot * theta_dot / r
            return [r_dot, r_ddot, theta_dot, theta_ddot]
        
        # Initial conditions at perihelion
        r_peri = a * (1 - e)
        v_peri = np.sqrt(self.G * self.M_sun * (1 + e) / (r_peri * (1 - e)))
        
        t_span = [0, n_orbits * 2*np.pi * np.sqrt(a**3/(self.G * self.M_sun))]
        state0 = [r_peri, 0, 0, v_peri / r_peri]
        
        sol = solve_ivp(orbital_equations, t_span, state0, rtol=1e-10, atol=1e-12)
        
        # Detect perihelia and compute precession
        from scipy.signal import argrelextrema
        r_vals = sol.y[0]
        theta_vals = sol.y[2]
        idx_min = argrelextrema(r_vals, np.less, order=50)[0]
        
        if len(idx_min) > 1:
            peri_theta = theta_vals[idx_min]
            delta_theta = np.diff(peri_theta)
            avg_delta = np.mean(delta_theta)
            precession_per_orbit = avg_delta - 2*np.pi
            return precession_per_orbit * (180/np.pi) * 3600  # arcsec/orbit
        return 0
    
    def galactic_rotation_curve(self, r, m_X, alpha=1.0):
        """Compute galactic rotation velocity"""
        # For spherical mass distribution M(r) = M_total * (r/(r + r_c)) 
        M_total = 1e12 * self.M_sun  # Approximate Milky Way mass
        r_c = 2e3 * self.parsec      # Core radius
        
        M_enc = M_total * (r / (r + r_c))**1.5  # Approximate profile
        
        # Newtonian + Substrate X correction
        v_newton = np.sqrt(self.G * M_enc / r)
        yukawa_correction = np.sqrt((1 + m_X * r) * np.exp(-m_X * r) * alpha)
        
        return v_newton * yukawa_correction
    
    def objective_function(self, params):
        """Objective function to minimize"""
        m_X, alpha = params
        
        # Solar system constraints (high weight)
        mercury_precession = self.compute_precession(
            self.mercury_data['a'], self.mercury_data['e'], m_X, alpha)
        mercury_arcsec_century = mercury_precession * (100 * 365.25 / 87.969)
        mercury_error = (mercury_arcsec_century - self.mercury_data['observed_precession'])**2
        
        # Galactic rotation constraints
        v_pred = self.galactic_rotation_curve(self.galactic_data['r_m'], m_X, alpha)
        galactic_error = np.sum((v_pred/1000 - self.galactic_data['v_km_s'])**2)  # km/s
        
        # Pioneer anomaly constraint (small weight - mostly explained now)
        pioneer_r = 20 * self.AU  # Pioneer distance
        pioneer_accel_pred = self.substrate_x_acceleration(pioneer_r, m_X, alpha) - \
                           self.newtonian_acceleration(pioneer_r)
        pioneer_error = (pioneer_accel_pred / self.pioneer_accel - 1)**2 * 0.1  # Reduced weight
        
        total_error = mercury_error * 1000 + galactic_error + pioneer_error
        return total_error
    
    def fit_parameters(self):
        """Fit m_X and alpha to observational data"""
        print("FITTING SUBSTRATE X PARAMETERS TO OBSERVATIONAL DATA...")
        
        # Initial guess and bounds
        initial_guess = [1e-16, 1.0]  # m_X [1/m], alpha [dimensionless]
        bounds = [(1e-20, 1e-10), (0.8, 1.2)]  # Physical bounds
        
        result = minimize(self.objective_function, initial_guess, bounds=bounds, 
                         method='L-BFGS-B', options={'maxiter': 100})
        
        m_X_opt, alpha_opt = result.x
        
        print(f"\n=== FITTING RESULTS ===")
        print(f"Optimal m_X = {m_X_opt:.2e} m⁻¹")
        print(f"Optimal α = {alpha_opt:.6f}")
        print(f"Corresponding length scale = {1/m_X_opt/self.parsec:.2f} kpc")
        print(f"Fit quality: χ² = {result.fun:.6f}")
        
        return m_X_opt, alpha_opt
    
    def plot_fits(self, m_X_opt, alpha_opt):
        """Plot theory vs data for all constraints"""
        fig, axes = plt.subplots(2, 2, figsize=(12, 10))
        
        # Plot 1: Solar system precession
        m_X_test = np.logspace(-18, -14, 50)
        mercury_precessions = []
        
        for m_X in m_X_test:
            precession = self.compute_precession(
                self.mercury_data['a'], self.mercury_data['e'], m_X, alpha_opt)
            mercury_precessions.append(precession * (100 * 365.25 / 87.969))
        
        axes[0,0].semilogx(m_X_test, mercury_precessions, 'b-', linewidth=2)
        axes[0,0].axhline(self.mercury_data['observed_precession'], 
                         color='red', linestyle='--', label='Observed')
        axes[0,0].axvline(m_X_opt, color='green', linestyle=':', label='Best fit')
        axes[0,0].set_xlabel('m_X [m⁻¹]')
        axes[0,0].set_ylabel('Mercury Precession [″/century]')
        axes[0,0].set_title('Solar System: Mercury Precession')
        axes[0,0].legend()
        axes[0,0].grid(True, alpha=0.3)
        
        # Plot 2: Galactic rotation curve
        r_plot = np.logspace(18, 21, 100)  # 0.1 to 100 kpc
        v_newton = self.galactic_rotation_curve(r_plot, 0, 1.0)  # Newtonian
        v_substrate = self.galactic_rotation_curve(r_plot, m_X_opt, alpha_opt)
        
        axes[0,1].loglog(r_plot/self.parsec/1e3, v_newton/1000, 'r--', 
                        label='Newtonian', linewidth=2)
        axes[0,1].loglog(r_plot/self.parsec/1e3, v_substrate/1000, 'b-', 
                        label='Substrate X', linewidth=2)
        axes[0,1].scatter(self.galactic_data['r_kpc'], self.galactic_data['v_km_s'],
                         color='black', s=50, label='Observations')
        axes[0,1].set_xlabel('Galactic Radius [kpc]')
        axes[0,1].set_ylabel('Rotation Velocity [km/s]')
        axes[0,1].set_title('Galactic Rotation Curve')
        axes[0,1].legend()
        axes[0,1].grid(True, alpha=0.3)
        
        # Plot 3: Acceleration profile
        r_solar = np.logspace(10, 14, 100)  # Solar system scales
        a_newton = self.newtonian_acceleration(r_solar)
        a_substrate = self.substrate_x_acceleration(r_solar, m_X_opt, alpha_opt)
        
        axes[1,0].loglog(r_solar/self.AU, a_newton, 'r--', label='Newtonian', linewidth=2)
        axes[1,0].loglog(r_solar/self.AU, a_substrate, 'b-', label='Substrate X', linewidth=2)
        axes[1,0].set_xlabel('Orbital Radius [AU]')
        axes[1,0].set_ylabel('Acceleration [m/s²]')
        axes[1,0].set_title('Solar System Acceleration')
        axes[1,0].legend()
        axes[1,0].grid(True, alpha=0.3)
        
        # Plot 4: Parameter constraints
        m_X_range = np.logspace(-18, -14, 100)
        alpha_range = np.linspace(0.95, 1.05, 100)
        chi2_surface = np.zeros((len(m_X_range), len(alpha_range)))
        
        for i, m_X in enumerate(m_X_range):
            for j, alpha in enumerate(alpha_range):
                chi2_surface[i,j] = self.objective_function([m_X, alpha])
        
        im = axes[1,1].contourf(alpha_range, np.log10(m_X_range), np.log10(chi2_surface+1), 
                               levels=20, cmap='viridis')
        axes[1,1].scatter(alpha_opt, np.log10(m_X_opt), color='red', s=100, 
                         marker='*', label='Best fit')
        axes[1,1].set_xlabel('Coupling α')
        axes[1,1].set_ylabel('log₁₀(m_X [m⁻¹])')
        axes[1,1].set_title('Parameter Constraints')
        axes[1,1].legend()
        plt.colorbar(im, ax=axes[1,1], label='log₁₀(χ²)')
        
        plt.tight_layout()
        plt.savefig('substrate_x_fits.png', dpi=150, bbox_inches='tight')
        plt.show()
        
        return fig

def main():
    """Run complete data fitting analysis"""
    print("SUBSTRATE X THEORY - OBSERVATIONAL DATA FITS")
    print("="*60)
    
    fitter = SubstrateXDataFits()
    
    # Fit parameters to data
    m_X_opt, alpha_opt = fitter.fit_parameters()
    
    # Generate fit plots
    fig = fitter.plot_fits(m_X_opt, alpha_opt)
    
    print(f"\n=== PHYSICAL INTERPRETATION ===")
    print(f"Best-fit m_X = {m_X_opt:.2e} m⁻¹")
    print(f"Corresponding length scale: {1/m_X_opt/fitter.parsec:.1f} kpc")
    print(f"Coupling strength: α = {alpha_opt:.6f} (close to 1)")
    
    if 1/m_X_opt/fitter.parsec > 1:
        print("→ Length scale > 1 kpc suggests cosmological relevance")
        print("→ Could address dark matter phenomenology")
    else:
        print("→ Solar system scale modifications")
    
    print(f"\nCheck 'substrate_x_fits.png' for detailed comparison plots")

if __name__ == "__main__":
    main()
