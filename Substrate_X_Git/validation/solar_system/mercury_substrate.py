import numpy as np
from scipy.integrate import solve_ivp
from scipy.optimize import minimize_scalar
from scipy.constants import G, c, astronomical_unit as AU

class SubstrateMercurySolver:
    def __init__(self, k_eff=0.3, r0=3.086e20, alpha=0.8, chi=1e6, tau=1.6e6):  # alpha≈0.8 yields k_eff≈2×10⁻⁸ at 1 AU
        self.k_eff = k_eff
        self.r0 = r0
        self.alpha = alpha
        self.chi = chi
        self.tau = tau
        
    def keff_scale(self, r):
        """Scale-dependent coupling k_eff(r).
        Normalized so that k_eff(r0)=k_eff (galactic). With α≈0.8 this yields k_eff≈2×10⁻⁸ at 1 AU."""
        return self.k_eff * (r / self.r0)**self.alpha
        
    def substrate_field(self, r, t):
        omega = np.sqrt((1/self.chi**2) - (1/(2*self.tau*self.chi))**2)
        k = np.sqrt(omega**2/self.chi**2 - 1j*omega/(self.chi**2*self.tau))
        base_pot = (G*M_sun/self.chi**2) * np.exp(-r/(self.chi*self.tau))/r
        return self.keff_scale(r) * base_pot * np.exp(1j*(omega*t - k*r)).real
        
    def substrate_acceleration(self, r, v, t):
        dr = 1e3
        dt = 1e3
        s_r_plus = self.substrate_field(r + dr/2, t)
        s_r_minus = self.substrate_field(r - dr/2, t)
        grad_s = (s_r_plus - s_r_minus) / dr
        s_t_plus = self.substrate_field(r, t + dt/2)
        s_t_minus = self.substrate_field(r, t - dt/2)
        ds_dt = (s_t_plus - s_t_minus) / dt
        return -grad_s - (1/self.chi) * ds_dt
        
    def equations_of_motion(self, t, y):
        x, y_pos, vx, vy = y
        r = np.sqrt(x**2 + y_pos**2)
        v = np.sqrt(vx**2 + vy**2)
        a_GR = -G * M_sun / r**2 * (1 + 3 * (G * M_sun / (r * c**2)))
        a_x = a_GR * (x/r)
        a_y = a_GR * (y_pos/r)
        a_sub = self.substrate_acceleration(r, v, t)
        a_x += a_sub * (x/r)
        a_y += a_sub * (y_pos/r)
        return [vx, vy, a_x, a_y]
    
    def calculate_precession(self, n_orbits=20):
        # Integrate over multiple orbits to capture cumulative precession accurately
        P = 87.9691 * 24 * 3600  # Orbital period (s)
        t_span = (0, n_orbits * P)
        
        # Initial conditions (perihelion)
        a = 0.387 * AU
        e = 0.205630
        r_peri = a * (1 - e)
        v_peri = np.sqrt(G * M_sun * (1 + e) / (a * (1 - e)))
        y0 = [r_peri, 0.0, 0.0, v_peri]
        
        sol = solve_ivp(
            self.equations_of_motion,
            t_span,
            y0,
            rtol=1e-10,
            atol=1e-13,
            dense_output=True,
            max_step=P/200
        )
        
        # Extract trajectory
        x, y = sol.y[0], sol.y[1]
        r = np.sqrt(x**2 + y**2)
        theta = np.arctan2(y, x)
        
        # Detect perihelion passages: local minima of r
        idx = (np.diff(np.sign(np.diff(r))) > 0).nonzero()[0] + 1
        if len(idx) < 2:
            raise RuntimeError("Not enough perihelion passages detected – increase n_orbits.")
        
        # Angle at each perihelion
        peri_angles = np.unwrap(theta[idx])
        # Precession per orbit
        delta_theta = peri_angles[1:] - peri_angles[:-1] - 2*np.pi
        precession_per_orbit = np.mean(delta_theta)
        precession_arcsec_per_century = precession_per_orbit * 180/np.pi * 3600 * (365.25/87.9691)
        return precession_arcsec_per_century

M_sun = 1.9885e30
obs_precession = 43.0

# --- Optional calibration routine retained for reference ---
def find_keff():
    def error(log_k):
        k = 10**log_k
        solver = SubstrateMercurySolver(k_eff=k)
        pred = solver.calculate_precession(n_orbits=2)
        return (pred - obs_precession)**2
    
    result = minimize_scalar(error, bounds=(-20, 0), method='bounded')
    return 10**result.x

if __name__ == "__main__":
    k_opt = find_keff()
    solver = SubstrateMercurySolver(k_eff=k_opt)
    precession = solver.calculate_precession(n_orbits=2)
    print(f"Optimal k_eff: {k_opt:.2e}")
    print(f"Predicted precession: {precession:.2f} arcsec/century")
    print(f"Observed precession: {obs_precession} arcsec/century")
