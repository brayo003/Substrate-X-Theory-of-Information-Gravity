"""
Multi-Scale Test Suite for Substrate X Theory
"""

import sys
from pathlib import Path
import numpy as np

# Add project root to Python path
PROJECT_ROOT = Path(__file__).parent.parent.parent  # Go up to project root
sys.path.insert(0, str(PROJECT_ROOT))

# Import available test functions
try:
    from verification.second_base_tests.galaxy_scale_sim import run_galaxy_sim
    GALAXY_TEST_AVAILABLE = True
except ImportError:
    GALAXY_TEST_AVAILABLE = False
    print("Warning: Galaxy scale test not available")

def test_mercury_precession():
    """Test Mercury's perihelion precession"""
    import numpy as np
    from scipy.integrate import solve_ivp
    
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
        lambda t, y: [
            y[2],  # vx
            y[3],  # vy
            -G * M_sun / np.sqrt(y[0]**2 + y[1]**2)**3 * y[0],  # ax
            -G * M_sun / np.sqrt(y[0]**2 + y[1]**2)**3 * y[3]   # ay
        ],
        t_span, y0, 
        dense_output=True,
        rtol=1e-10,
        atol=1e-13
    )
    
    # Calculate precession
    theta = np.arctan2(sol.y[1], sol.y[0])
    precession = (theta[-1] - theta[0]) * 180/np.pi * 3600  # arcseconds/orbit
    precession_per_century = precession * (100/88)  # Mercury years per century
    
    print(f"  Calculated precession: {precession_per_century:.2f} arcsec/century")
    print(f"  Expected (GR): 43.0 arcsec/century")
    
    return {'precession': precession_per_century}

def test_binary_pulsar():
    """Test binary pulsar orbital decay"""
    import numpy as np
    from scipy.integrate import solve_ivp
    
    # Hulse-Taylor binary parameters
    M1 = 1.44 * 1.989e30  # kg
    M2 = 1.39 * 1.989e30
    P_orb = 27906.980895  # s
    e = 0.6171334
    
    # Initial conditions (simplified circular orbit)
    a = (P_orb**2 * 6.67430e-11 * (M1 + M2) / (4 * np.pi**2)) ** (1/3)
    v = np.sqrt(6.67430e-11 * (M1 + M2) / a)
    
    y0 = [a*M2/(M1+M2), 0, -a*M1/(M1+M2), 0, 0, v*M2/(M1+M2), 0, -v*M1/(M1+M2)]
    
    # Integrate for multiple orbits
    t_span = (0, 10 * P_orb)
    k_diss = 1e-15  # Tune to match observed decay
    
    sol = solve_ivp(
        lambda t, y: [
            y[4], y[5], y[6], y[7],  # x1', y1', x2', y2'
            -6.67430e-11 * M2 / ((y[0]-y[2])**2 + (y[1]-y[3])**2)**1.5 * (y[0]-y[2]),  # ax1
            -6.67430e-11 * M2 / ((y[0]-y[2])**2 + (y[1]-y[3])**2)**1.5 * (y[1]-y[3]),  # ay1
            6.67430e-11 * M1 / ((y[0]-y[2])**2 + (y[1]-y[3])**2)**1.5 * (y[0]-y[2]),   # ax2
            6.67430e-11 * M1 / ((y[0]-y[2])**2 + (y[1]-y[3])**2)**1.5 * (y[1]-y[3])    # ay2
        ],
        t_span, y0,
        dense_output=True,
        rtol=1e-10
    )
    
    # Calculate period change
    t = sol.t
    x1 = sol.y[0]
    crossings = np.where(np.diff(np.sign(x1)))[0]
    periods = np.diff(t[crossings][:3])  # First few periods
    dP_dt = (periods[-1] - periods[0]) / (periods[0] * (len(periods)-1))
    
    print(f"  Calculated dP/dt: {dP_dt:.1e} s/s")
    print(f"  Expected (Hulse-Taylor): -2.4e-12 s/s")
    
    return {'period_decay': dP_dt}

def run_tests():
    print("="*80)
    print("RUNNING MULTI-SCALE VALIDATION SUITE")
    print("="*80 + "\n")
    
    # Mercury Precession Test
    print("1. Mercury Precession Test")
    print("-"*40)
    test_mercury_precession()
    
    # Binary Pulsar Test
    print("\n2. Binary Pulsar Test")
    print("-"*40)
    test_binary_pulsar()
    
    # Galaxy Simulation Test
    if GALAXY_TEST_AVAILABLE:
        print("\n3. Galaxy Simulation Test")
        print("-"*40)
        run_galaxy_sim(m_star_msun=1e11, r_eff_kpc=4.0, k_eff=0.1)
    else:
        print("\nGalaxy simulation test not available")
    
    print("\n" + "="*80)
    print("TEST SUMMARY:")
    print("="*80)
    print("1. Mercury Precession: IMPLEMENTED")
    print("2. Binary Pulsar: IMPLEMENTED")
    print("3. Galaxy Simulation: ", "AVAILABLE" if GALAXY_TEST_AVAILABLE else "NOT AVAILABLE")

if __name__ == "__main__":
    run_tests()
