import numpy as np

# --- FUNDAMENTAL CONSTANTS ---
G = 6.67430e-11
c = 299792458.0
ħ = 1.054571817e-34
Lp = np.sqrt(ħ * G / c**3)
Mp = np.sqrt(ħ * c / G)
R_H = 1.37e26  # Hubble radius in meters

class UnifiedV12Bridge:
    def __init__(self, mass):
        self.M = mass
        self.R_s = 2 * G * mass / c**2
        
    def regime_diagnostic(self, r):
        """Return which physics dominates at radius r"""
        uv = self.R_s / r          # Black hole influence
        ir = r / R_H               # Cosmological influence
        
        # Total "bridge activity" - your x_total
        x_total = uv + ir
        
        if uv < 1e-6 and ir < 1e-6:
            return "NEWTONIAN_SILENCE", x_total, 0.0
        elif uv > 0.1:
            return "BLACK_HOLE_BRIDGE", x_total, uv
        elif ir > 0.1:
            return "COSMOLOGICAL_BRIDGE", x_total, ir
        elif ir > 1e-4:
            return "DARK_MATTER_REGIME", x_total, ir
        else:
            return "TRANSITION", x_total, max(uv, ir)
    
    def gravitational_acceleration(self, r):
        """Complete V12-modified gravity"""
        regime, x_total, signal = self.regime_diagnostic(r)
        
        # Base Newtonian
        g_newton = G * self.M / r**2
        
        if regime == "NEWTONIAN_SILENCE":
            return g_newton
            
        elif regime == "DARK_MATTER_REGIME":
            # Galactic scale - add substrate acceleration
            # This matches your ruun.py results
            g_substrate = c**2 / R_H  # ~6.56e-10 m/s²
            return g_newton + g_substrate
            
        elif regime == "COSMOLOGICAL_BRIDGE":
            # Hubble scale - cosmological constant effects
            g_cosmological = 0.5 * c**2 / R_H  # Reduced effect
            return g_newton + g_cosmological
            
        elif regime == "BLACK_HOLE_BRIDGE":
            # Near horizon - full V12 saturation
            # Information density x approaches 1
            x = min(0.99, signal)  # Cap near saturation
            saturation_factor = 1.0 / (1.0 - x)
            return g_newton * saturation_factor
            
        else:  # TRANSITION
            # Linear interpolation between regimes
            if signal > 0:
                transition_factor = 1.0 + 0.1 * np.log10(1 + signal*1000)
                return g_newton * transition_factor
            return g_newton
    
    def orbital_velocity(self, r):
        """Circular orbital velocity from V12 gravity"""
        g = self.gravitational_acceleration(r)
        return np.sqrt(g * r)

# --- TEST SUITE ---
def run_complete_test():
    print("=== UNIFIED V12 BRIDGE TEST ===\n")
    
    test_cases = [
        ("Solar @ Schwarzschild", 1.989e30, 2954),
        ("Solar @ 1 AU", 1.989e30, 1.496e11),
        ("Milky Way core", 1e6*1.989e30, 1e16),
        ("Milky Way edge", 1.5e42, 4.7e20),
        ("Cosmological", 1e53, 1e26)
    ]
    
    for name, M, r in test_cases:
        bridge = UnifiedV12Bridge(M)
        regime, x_total, signal = bridge.regime_diagnostic(r)
        g = bridge.gravitational_acceleration(r)
        v = bridge.orbital_velocity(r)
        
        g_newton = G * M / r**2
        v_newton = np.sqrt(g_newton * r)
        
        print(f"{name:20} | R={r:.1e}m")
        print(f"  Regime: {regime:20} | x_total: {x_total:.2e}")
        print(f"  g_v12/g_newton: {g/g_newton:.3f} | v_v12: {v/1000:.1f} km/s (Newton: {v_newton/1000:.1f})")
        print()

if __name__ == "__main__":
    run_complete_test()
