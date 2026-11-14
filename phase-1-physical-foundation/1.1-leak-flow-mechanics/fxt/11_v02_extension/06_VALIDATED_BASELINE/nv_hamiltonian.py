"""Minimal conventional two-level Hamiltonian used by the optional QuTiP check."""
from __future__ import annotations

import numpy as np


def zeeman_hamiltonian_qutip(field_gauss, gamma_hz_per_gauss):
    """Return H/hbar = (gamma_angular B/2) sigma_z in rad/s, using QuTiP."""
    import qutip as qt
    return 0.5 * (2 * np.pi * gamma_hz_per_gauss) * field_gauss * qt.sigmaz()

