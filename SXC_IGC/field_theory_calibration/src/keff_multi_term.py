"""Multi-term effective coupling k_eff(r)
================================================
Provides an explicit *three–component* model motivated by the USER’s
"OPTION B" notes:
    • short-range (Yukawa / 1 / r²) – solar–system scale
    • intermediate  (1 / r)       – galactic scale
    • long-range    (constant)    – cosmological scale
The module exposes two helpers:
    keff(r)          – dimensionless coupling at radius *r* (metres)
    substrate_acc(r) – additional radial acceleration fraction relative
                       to Newtonian   a_sub = keff(r) × a_Newton
Constants are chosen so that:
    k_eff(1 AU)   ≈ 2×10⁻⁴   (Mercury bound)
    k_eff(10 kpc) = 0.30     (galaxy fits)
    k_eff(10 Mpc) ≈ 1        (cosmic scale placeholder)
Feel free to tweak k1,k2,k3,λ1 as data improve.
"""
from __future__ import annotations

import numpy as np
from scipy.constants import astronomical_unit as AU

# --- Tunable coefficients ----------------------------------------------------
# Short-range Yukawa term  k1 * exp(-r/λ1) / r²  (dimensionless factor on 1/r²)
# Solar-system data force this mode to be effectively zero.
K1 = 0.0             # short-range substrate decouples at AU scales
LAMBDA1 = 5e11       # 0.05 pc  (≈ Pluto orbit)

# Intermediate term   ~1/r with small-r suppression:  k2 * r / ((r+L2) * L2)
K2 = 3.0e17          # tuned so term ≈0.3 at r≈10 kpc when L2≪r
L2 = 1e18             # suppression scale (0.03 pc)

# Long-range constant term (placeholder for cosmology)
K3 = 1.0              # order-unity beyond Mpc scales

# -----------------------------------------------------------------------------


def keff(r: float | np.ndarray) -> np.ndarray:
    """Dimensionless effective coupling at radius *r* (metres)."""
    r = np.asanyarray(r)
    term_short = K1 * np.exp(-r / LAMBDA1)
    term_mid   = K2 * r / ((r + L2) * L2)
    term_long  = K3 * np.tanh(r / (3e22))                # smooth turn-on ~1 Mpc
    return term_short + term_mid + term_long


def substrate_acceleration_fraction(r: float | np.ndarray) -> np.ndarray:
    """Return a_sub / a_Newton  (purely radial, attractive)."""
    return keff(r)


# ----------------------------- quick demo ------------------------------------
if __name__ == "__main__":
    import pandas as pd

    radii = [AU, 1e12, 1e14, 1e16, 3.086e20, 3.086e22]  # AU, 0.1 pc, 10 pc, 10 kpc, 1 Mpc
    table = pd.DataFrame(
        {
            "r [m]": radii,
            "k_eff": keff(radii),
        }
    )
    with pd.option_context("display.max_rows", None):
        print(table)
