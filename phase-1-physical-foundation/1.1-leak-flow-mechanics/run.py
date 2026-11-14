import numpy as np
import sys
import time

class StrictConvergenceAudit:
    def __init__(self):
        self.G = 6.67430e-11
        self.M_sun = 1.989e30
        self.mu = self.G * self.M_sun
        self.c = 299792458
        
        self.a = 57.91e9
        self.e_val = 0.2056
        self.r_peri = self.a * (1 - self.e_val)
        self.v_peri = np.sqrt(self.mu * (1 + self.e_val) / (self.a * (1 - self.e_val)))

        # Analytical GR Target
        self.gr_rad_per_orbit = (6 * np.pi * self.mu) / (self.a * (1 - self.e_val**2) * self.c**2)
        self.gr_arcsec_century = (self.gr_rad_per_orbit * (180/np.pi) * 3600) * 415.2

    def get_acc(self, pos, vel):
        r_mag = np.linalg.norm(pos)
        h = np.cross(pos, vel)
        h_mag2 = np.dot(h, h)
        
        a_n = -self.mu / r_mag**3 * pos
        # The exact 1/r^4 correction to be derived from Substrate X theory
        a_corr = a_n * (3 * h_mag2 / (self.c**2 * r_mag**2))
        return a_n + a_corr

    def get_lrl_angle(self, pos, vel):
        h = np.cross(pos, vel)
        e_vec = np.cross(vel, h) / self.mu - (pos / np.linalg.norm(pos))
        return np.arctan2(e_vec[1], e_vec[0])

    def run_sim(self, dt):
        pos = np.array([self.r_peri, 0.0, 0.0])
        vel = np.array([0.0, self.v_peri, 0.0])
        angles = []
        
        # Calculate steps needed for ~2 orbits (Mercury orbital period is ~88 days)
        max_steps = int((2 * 88 * 24 * 3600) / dt) + 50000 
        
        acc = self.get_acc(pos, vel)
        for step in range(max_steps):
            dot_prev = np.dot(pos, vel)
            
            # Standard Velocity Verlet (Leapfrog)
            vel += acc * (dt / 2.0)
            pos += vel * dt
            acc = self.get_acc(pos, vel)
            vel += acc * (dt / 2.0)
            
            dot_curr = np.dot(pos, vel)
            
            # LRL Angle measured strictly at Aphelion (Velocity is lowest, r*v crosses positive to negative)
            if dot_prev > 0 and dot_curr <= 0 and step > 1000:
                angles.append(self.get_lrl_angle(pos, vel))
                if len(angles) == 2:
                    break
                    
        if len(angles) == 2:
            shift_rad = angles[1] - angles[0]
            arcsec_cent = (shift_rad * (180/np.pi) * 3600) * 415.2
            return arcsec_cent
        return None

    def test_convergence(self):
        print(f"🔬 ANALYTICAL GR TARGET: {self.gr_arcsec_century:.4f} arcsec/century\n")
        print("—"*60)
        
        # Testing timestep reduction. Note: dt=1 will take roughly 15.2 million steps.
        dts = [10, 5, 2, 1] 
        
        for dt in dts:
            print(f"Testing dt = {dt}s ... ", end="")
            sys.stdout.flush()
            
            start_time = time.time()
            res = self.run_sim(dt)
            elapsed = time.time() - start_time
            
            if res is not None:
                error = abs(res - self.gr_arcsec_century)
                print(f"Result: {res:.4f} arcsec/century | Error: {error:.4f} | Time: {elapsed:.1f}s")
            else:
                print("Failed to complete orbits.")
        print("—"*60)

if __name__ == "__main__":
    StrictConvergenceAudit().test_convergence()
