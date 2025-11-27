import numpy as np
from scipy.integrate import solve_ivp

def binary_pulsar_ode(t, y, G, M1, M2, k_diss):
    """ODE system for binary pulsar with energy dissipation"""
    x1, y1, x2, y2, vx1, vy1, vx2, vy2 = y
    dx = x1 - x2
    dy = y1 - y2
    r = np.sqrt(dx**2 + dy**2)
    
    # Gravitational force + dissipation
    F = G * M1 * M2 / r**2
    Fx = F * dx/r
    Fy = F * dy/r
    
    # Dissipation term (proportional to velocity difference)
    vx_rel = vx1 - vx2
    vy_rel = vy1 - vy2
    F_diss = k_diss * (vx_rel*dx + vy_rel*dy) / r
    
    return [
        vx1, vy1, vx2, vy2,
        -Fx/M1 - F_diss*dx/(M1*r),
        -Fy/M1 - F_diss*dy/(M1*r),
        Fx/M2 + F_diss*dx/(M2*r),
        Fy/M2 + F_diss*dy/(M2*r)
    ]

def test_binary_pulsar_decay():
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
        binary_pulsar_ode, t_span, y0,
        args=(6.67430e-11, M1, M2, k_diss),
        dense_output=True,
        rtol=1e-10
    )
    
    # Calculate period change
    t = sol.t
    x1 = sol.y[0]
    crossings = np.where(np.diff(np.sign(x1)))[0]
    periods = np.diff(t[crossings][:3])  # First few periods
    dP_dt = (periods[-1] - periods[0]) / (periods[0] * (len(periods)-1))
    
    # Verify against observed value
    expected_dP_dt = -2.4e-12  # s/s
    assert np.sign(dP_dt) == np.sign(expected_dP_dt), "Wrong sign of period change"
    assert 0.5 * abs(expected_dP_dt) < abs(dP_dt) < 2 * abs(expected_dP_dt), \
        f"dP/dt = {dP_dt:.1e} outside expected range"

if __name__ == "__main__":
    test_binary_pulsar_decay()
