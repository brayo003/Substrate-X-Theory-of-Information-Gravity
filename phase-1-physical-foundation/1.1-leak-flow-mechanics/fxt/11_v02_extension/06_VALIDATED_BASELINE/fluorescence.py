"""Documented phenomenological fluorescence/contrast readout mapping."""
from __future__ import annotations

import numpy as np


def normalized_contrast(phase_rad, envelope, contrast, offset=0.0, readout_phase_rad=0.0):
    """Map ideal echo phase to normalized fluorescence contrast.

    `contrast`, `offset`, and `readout_phase_rad` are calibration parameters,
    not predictions of the paper's magnetic model.
    """
    return offset + contrast * np.asarray(envelope) * np.cos(np.asarray(phase_rad) + readout_phase_rad)

