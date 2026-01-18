"""Mercury perihelion precession with multi-term k_eff(r)."""
from __future__ import annotations

import numpy as np
from scipy.integrate import solve_ivp
from scipy.constants import G, astronomical_unit as AU, c
from pathlib import Path
import sys

# -----------------------------------------------------------------------------
# Ensure keff_multi_term is importable regardless of current working directory
THIS_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = THIS_DIR.parents[2]  # /.../Substrate X Theory of Information Gravity
sys.path.insert(0, str(PROJECT_ROOT / "github" / "validation"))

from keff_multi_term import keff as keff_r  # noqa: E402

M_SUN = 1.9885e30  # kg

# -----------------------------------------------------------------------------

def pn_accel(r_vec: np.ndarray, v_vec: np.ndarray) -> np.ndarray:
    """1-PN acceleration for a test mass around the Sun."""
    r = np.linalg.norm(r_vec)
    mu = G * M_SUN
    v2 = np.dot(v_vec, v_vec)
    rv = np.dot(r_vec, v_vec)
    c2 = c ** 2

    newt = -mu * r_vec / r**3
    scalar = newt * (4 * mu / r - v2 + 4 * rv**2 / r**2) / c2
    vector = -4 * mu * rv * v_vec / (r**3 * c2)
    return newt + scalar + vector


def mercury_precession(n_orbits: int = 30) -> float:
    """Return perihelion advance in arcsec/century using multi-term k_eff."""
    a = 0.387 * AU
    e = 0.205630
    P = 87.9691 * 24 * 3600  # orbital period (s)

    r_peri = a * (1 - e)
    v_peri = np.sqrt(G * M_SUN * (1 + e) / (a * (1 - e)))
    y0 = [r_peri, 0.0, 0.0, v_peri]

    def eom(t, y):
        x, y_, vx, vy = y
        r_vec = np.array([x, y_])
        v_vec = np.array([vx, vy])
        a_vec = pn_accel(r_vec, v_vec)
        r = np.linalg.norm(r_vec)
        a_vec += keff_r(r) * (-G * M_SUN * r_vec / r**3)
        return [vx, vy, a_vec[0], a_vec[1]]

    sol = solve_ivp(eom, (0, n_orbits * P), y0, rtol=1e-10, atol=1e-13, max_step=P/200)
    x, y_arr = sol.y[0], sol.y[1]
    r = np.hypot(x, y_arr)
    theta = np.unwrap(np.arctan2(y_arr, x))

    idx = np.where((r[1:-1] < r[:-2]) & (r[1:-1] < r[2:]))[0] + 1
    if len(idx) < 2:
        raise RuntimeError("Not enough perihelion passages detected; increase n_orbits")

    delta = (theta[idx[-1]] - theta[idx[0]]) / (len(idx) - 1) - 2 * np.pi
    arcsec_per_century = delta * 180 / np.pi * 3600 * (365.25 / 87.9691)
    return arcsec_per_century

# -----------------------------------------------------------------------------

if __name__ == "__main__":
    try:
        prec = mercury_precession()
        print(f"Predicted Mercury precession = {prec:.2f} arcsec/century")
        print("Target (GR)                 = 43.00 arcsec/century")
    except Exception:
        import traceback, sys as _s
        traceback.print_exc()
        _s.exit(1)

