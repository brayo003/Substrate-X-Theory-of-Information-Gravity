import numpy as np
from scipy.integrate import solve_ivp

def mercury_ode(t, y, G, M_sun, k_eff):
    """ODE system for Mercury's orbit with substrate effects"""
    x, y, vx, vy = y
    r = np.sqrt(x**2 + y**2)
    factor = (G * M_sun / r**3) * (1 + k_eff * np.exp(-r/1e10))
    
    return [
        vx,
        vy,
        -factor * x,
        -factor * y
    ]

def test_mercury_precession():
    # Constants
    G = 6.67430e-11
    M_sun = 1.9885e30
    k_eff = 0.0  # Should be calibrated to match GR prediction
    
    # Initial conditions (Mercury at perihelion)
    a = 5.79e10  # Semi-major axis (m)
    e = 0.2056   # Eccentricity
    r_peri = a * (1 - e)
    v_peri = np.sqrt(G * M_sun * (1 + e) / (a * (1 - e)))
    
    y0 = [r_peri, 0, 0, v_peri]
    t_span = (0, 88 * 24 * 3600)  # One Mercury year
    
    # Integrate orbit
    sol = solve_ivp(
        mercury_ode, t_span, y0, 
        args=(G, M_sun, k_eff),
        dense_output=True,
        rtol=1e-10,
        atol=1e-13
    )
    
    # Calculate precession
    theta = np.arctan2(sol.y[1], sol.y[0])
    precession = (theta[-1] - theta[0]) * 180/np.pi * 3600  # arcseconds/orbit
    precession_per_century = precession * (100/88)  # Mercury years per century
    
    # Verify against GR prediction
    expected_precession = 43.0  # arcsec/century
    tolerance = 0.1  # 0.1 arcsec/century
    assert abs(precession_per_century - expected_precession) < tolerance, \
        f"Precession {precession_per_century:.2f} outside tolerance"

if __name__ == "__main__":
    test_mercury_precession()
