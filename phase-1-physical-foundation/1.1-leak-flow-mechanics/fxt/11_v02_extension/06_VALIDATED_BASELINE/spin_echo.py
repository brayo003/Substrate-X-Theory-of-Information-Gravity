"""Ideal-pulse conventional spin-echo phase accumulation.

The toggling-frame integral implements the time-dependent Zeeman detuning
described by Eq. (1) of the supplied paper.  It does not add any mechanism.
"""
from __future__ import annotations

import numpy as np


def echo_phase(tau_s, field_amplitude_gauss, rotation_frequency_hz,
               gamma_hz_per_gauss, rotation_phase_rad=0.0):
    """Return the spin-echo relative phase in radians for total echo time tau.

    The electron transition angular gyromagnetic ratio is `2*pi*gamma`.
    The pi pulse reverses the sign of the accumulated detuning in the second
    half, so the result is the signed integral under the two halves.
    """
    tau_s = np.asarray(tau_s, dtype=float)
    omega = 2 * np.pi * rotation_frequency_hz
    gamma = 2 * np.pi * gamma_hz_per_gauss
    phi = rotation_phase_rad

    # Integral cos(omega*t + phi) over [0,tau/2] minus [tau/2,tau].
    safe_omega = omega if omega != 0 else np.finfo(float).eps
    integral = (
        2 * np.sin(omega * tau_s / 2 + phi)
        - np.sin(phi)
        - np.sin(omega * tau_s + phi)
    ) / safe_omega
    return gamma * field_amplitude_gauss * integral


def gaussian_envelope(tau_s, coherence_time_s):
    tau_s = np.asarray(tau_s, dtype=float)
    return np.exp(-np.square(tau_s / coherence_time_s))

