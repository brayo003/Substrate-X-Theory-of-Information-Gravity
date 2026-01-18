import numpy as np

G = 6.67430e-11
C = 299792458.0
HBAR = 1.054571817e-34
LP = np.sqrt(HBAR * G / C**3)

class MasterBridgeV12:
    def __init__(self, mass):
        self.M = mass
        self.Rs = (2 * G * mass) / (C**2)
        area = 4 * np.pi * self.Rs**2
        self.S_bh = area / (4 * LP**2)
        self.b = 1.0 / self.S_bh
        self.K = 3.7e-92  # Calibration constant

    def get_equilibrium_tension(self, distance):
        # CORRECT: Linear mass scaling (was cubic)
        r_phys = (G * self.M) / (C**2 * distance)  # distance NOT distance**3
        a = 1.0
        discriminant = a**2 + 4 * r_phys * self.b
        x = (-a - np.sqrt(discriminant)) / (-2 * self.b)
        return x

    def calculate_gravity_acceleration(self, distance):
        x = self.get_equilibrium_tension(distance)
        g_info = self.K * x * C**2 * LP
        g_newton = (G * self.M) / (distance**2)
        return g_newton + g_info

# Test code
if __name__ == "__main__":
    # Quick verification
    test_mass = 2.63e42  # UGC09133 that failed
    bridge = MasterBridgeV12(test_mass)
    d = 4.7e20
    x = bridge.get_equilibrium_tension(d)
    print(f"Mass: {test_mass:.2e} kg")
    print(f"b = {bridge.b:.2e}")
    print(f"x at {d:.1e} m = {x:.2e}")
    print(f"Expected: x ~ 1e-10 to 1e-5 (not 1e+101)")
