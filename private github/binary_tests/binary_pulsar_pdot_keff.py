"""Binary pulsar orbital decay with multi-term k_eff(r).

Uses Peters–Mathews GR formula for Pdot and a scale-dependent coupling
G_eff = G * (1 + k_eff(a)), where k_eff(r) is the same multi-term
function constrained by Mercury (AU) and galaxies (kpc).

This is a clean, parameter-free propagation of the existing k_eff(r)
into the Hulse–Taylor scale.
"""
from __future__ import annotations

import numpy as np
from pathlib import Path
import sys
from scipy.constants import G, c

# -----------------------------------------------------------------------------
# Ensure keff_multi_term is importable regardless of cwd
THIS_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = THIS_DIR.parents[2]  # /.../Substrate X Theory of Information Gravity
sys.path.insert(0, str(PROJECT_ROOT / "github" / "validation"))

from keff_multi_term import keff as keff_r  # noqa: E402

# Hulse–Taylor system parameters (PSR B1913+16)
M_SUN = 1.9885e30  # kg
M1 = 1.44 * M_SUN
M2 = 1.39 * M_SUN
P_ORB = 27906.980895  # s (orbital period)
ECC = 0.6171334

# Observed GR-like Pdot (s/s)
PDOT_OBS = -2.4e-12


def peters_pdot(P: float, e: float, m1: float, m2: float, G_eff: float) -> float:
    """Pdot from Peters–Mathews formula with effective coupling G_eff.

    dP/dt = -(192*pi/5) * (G_eff^(5/3)/c^5) * (Mc^(5/3) * n^(5/3)) * f(e)
    where Mc is the chirp mass and n = 2*pi/P is mean motion.
    """
    Mc = (m1 * m2) ** (3.0 / 5.0) / (m1 + m2) ** (1.0 / 5.0)
    n = 2.0 * np.pi / P
    f_e = (1 + 73.0 / 24.0 * e**2 + 37.0 / 96.0 * e**4) / (1 - e**2) ** (7.0 / 2.0)
    return -(192.0 * np.pi / 5.0) * (G_eff ** (5.0 / 3.0) / c**5) * (Mc ** (5.0 / 3.0) * n ** (5.0 / 3.0)) * f_e


def run_binary_pulsar_keff_test():
    """Compute GR and substrate-modified Pdot for Hulse–Taylor binary."""
    # Semi-major axis from Kepler's 3rd law
    a = (G * (M1 + M2) * P_ORB**2 / (4.0 * np.pi**2)) ** (1.0 / 3.0)

    # Local coupling from the same multi-term k_eff(r)
    k_local = float(keff_r(a))

    # GR baseline (k_eff = 0)
    pdot_gr = peters_pdot(P_ORB, ECC, M1, M2, G)

    # Substrate-modified (G_eff = G (1 + k_eff))
    G_eff = G * (1.0 + k_local)
    pdot_sub = peters_pdot(P_ORB, ECC, M1, M2, G_eff)

    return {
        "a_m": a,
        "k_eff_local": k_local,
        "pdot_gr": pdot_gr,
        "pdot_sub": pdot_sub,
    }


if __name__ == "__main__":
    out = run_binary_pulsar_keff_test()
    print(f"Semi-major axis a        = {out['a_m']:.3e} m")
    print(f"Local k_eff(a)           = {out['k_eff_local']:.3e}")
    print()
    print(f"GR Pdot (G)              = {out['pdot_gr']:.3e} s/s")
    print(f"Substrate Pdot (G_eff)   = {out['pdot_sub']:.3e} s/s")
    print(f"Observed Pdot (HT)       = {PDOT_OBS:.3e} s/s")
    if out['pdot_gr'] != 0:
        print(f"Substrate / GR           = {out['pdot_sub']/out['pdot_gr']:.6f}")
    if PDOT_OBS != 0:
        print(f"GR / Observed            = {out['pdot_gr']/PDOT_OBS:.6f}")
        print(f"Substrate / Observed     = {out['pdot_sub']/PDOT_OBS:.6f}")
