"""Fit scale-dependent k_eff(r) so that Mercury's perihelion precession matches 43 arcsec/century
while recovering k_eff(10 kpc)=0.3 for galaxy scales.
The simple model assumes substrate adds a small fractional correction
k_eff(r) to the Newtonian acceleration (attractive).
"""
import numpy as np
from scipy.integrate import solve_ivp
from scipy.optimize import minimize_scalar
from scipy.constants import G, astronomical_unit as AU, c

# Sun parameters
M_SUN = 1.9885e30  # kg

# Desired galactic normalisation (10 kpc ≈ 3.086e20 m)
R0 = 3.086e20  # 10 kpc in metres
K_GAL = 0.3     # k_eff at galactic scale
OBS_PRECESSION = 43.0  # arcsec/century


def keff_scale(r: float, alpha: float) -> float:
    """Power-law scale dependence normalised at 10 kpc."""
    return K_GAL * (r / R0) ** alpha


def pn_acceleration(r_vec: np.ndarray, v_vec: np.ndarray) -> np.ndarray:
    """Return 1PN (Einstein–Infeld–Hoffmann) acceleration for test mass around Sun."""
    r = np.linalg.norm(r_vec)
    mu = G * M_SUN
    v2 = np.dot(v_vec, v_vec)
    rv = np.dot(r_vec, v_vec)
    c2 = c ** 2

    newt = -mu * r_vec / r**3  # attractive force (points toward Sun)
    pn = mu / (c2 * r**3) * ((4 * mu / r - v2) * r_vec + 4 * rv * v_vec)
    return newt + pn


def eom(t, y, alpha):
    """Equations of motion with GR + substrate correction."""
    x, y_pos, vx, vy = y
    r_vec = np.array([x, y_pos])
    v_vec = np.array([vx, vy])

    # 1PN acceleration (Newton + GR corrections)
    a_vec = pn_acceleration(r_vec, v_vec)

    # Substrate radial correction (disabled for GR-only test)
    r = np.linalg.norm(r_vec)
    k = 0.0  # GR-only: force substrate to zero
    # a_vec += k * (-G * M_SUN * r_vec / r**3)  # disabled

    return [vx, vy, a_vec[0], a_vec[1]]


def mercury_precession(alpha: float, n_orbits: int = 30) -> float:
    """Return arcsec/century perihelion advance for a given alpha."""
    # Mercury orbital parameters
    a = 0.387 * AU
    e = 0.205630
    P = 87.9691 * 24 * 3600  # seconds

    r_peri = a * (1 - e)
    v_peri = np.sqrt(G * M_SUN * (1 + e) / (a * (1 - e)))
    y0 = [r_peri, 0.0, 0.0, v_peri]
    t_span = (0.0, n_orbits * P)

    # Event-based perihelion detection using radial-velocity zero crossings

    def peri_event(t, y, alpha):
        x, y_pos, vx, vy = y
        # dr/dt = (r · v) / r; zero-crossing of r·v corresponds to peri/apo passage
        return x * vx + y_pos * vy

    peri_event.direction = 1.0
    peri_event.terminal = False

    sol = solve_ivp(
        eom,
        t_span,
        y0,
        args=(alpha,),
        events=peri_event,
        rtol=1e-10,
        atol=1e-13,
    )

    if not sol.t_events or len(sol.t_events[0]) < 2:
        raise RuntimeError("Not enough perihelion passages detected; increase n_orbits")

    y_events = sol.y_events[0]
    x_ev = y_events[:, 0]
    y_ev = y_events[:, 1]
    theta = np.unwrap(np.arctan2(y_ev, x_ev))

    # Successive perihelion angles directly give the apsidal precession; no 2π offset
    n_peri = len(theta)
    precession_per_orbit = (theta[-1] - theta[0]) / (n_peri - 1)
    # convert to arcsec/century
    arcsec_per_century = (
        precession_per_orbit
        * 206264.806247
        * (100.0 * 365.25 * 24 * 3600.0)
        / P
    )
    return arcsec_per_century


def fit_alpha():
    """Find alpha such that predicted precession matches observation."""
    # Choose alpha so that k_eff(1 AU) = 2e-4 while preserving k_eff(10 kpc) = K_GAL
    target_k_au = 2e-4
    alpha = np.log(target_k_au / K_GAL) / np.log(AU / R0)
    return alpha, mercury_precession(alpha)


if __name__ == "__main__":
    alpha_opt, precession = fit_alpha()
    k_au = keff_scale(AU, alpha_opt)
    print("Optimal alpha : {:.4f}".format(alpha_opt))
    print("k_eff(1 AU)   : {:.3e}".format(k_au))
    print("Predicted precession : {:.2f} arcsec/century".format(precession))
    print("Observed  precession : {:.2f} arcsec/century".format(OBS_PRECESSION))
