"""Conventional rotating-NV field geometry from Eq. (1) of rota.pdf."""
from __future__ import annotations

import numpy as np


def effective_field(time_s, amplitude_gauss, rotation_frequency_hz, phase_rad):
    """Return B_eff(t) in gauss using the paper's Eq. (1) amplitude."""
    time_s = np.asarray(time_s, dtype=float)
    return amplitude_gauss * np.cos(2 * np.pi * rotation_frequency_hz * time_s + phase_rad)

