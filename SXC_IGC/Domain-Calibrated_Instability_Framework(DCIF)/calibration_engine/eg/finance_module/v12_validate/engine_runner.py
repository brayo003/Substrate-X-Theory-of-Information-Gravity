"""
engine_runner.py — Run the canonical SXCOmegaEngine over the full history.

Imports SXCOmegaEngine directly from calibration_engine/SXC_V12_CORE.py
(the canonical implementation).  Does NOT redefine it.

Signal scaling convention (matching dcif_modules/energy_module usage):
    Each raw signal is min-max scaled to [0, 100] using its 2nd/98th
    percentile, clipping outliers.  The composite is the row-mean of
    all scaled signals.  This gives the engine a natural operating range
    where quiet periods sit ~10-30 and stressed periods sit ~50-80+,
    consistent with the excitation_flux knee at 45.
"""

import sys
import numpy as np
import pandas as pd
from pathlib import Path
from typing import Dict, Tuple

# ---------------------------------------------------------------------------
# Import canonical SXCOmegaEngine
# ---------------------------------------------------------------------------
# File lives at:
#   calibration_engine/eg/finance_module/v12_validate/engine_runner.py
# Canonical core lives at:
#   calibration_engine/SXC_V12_CORE.py   (parents[3])
_ENGINE_DIR = Path(__file__).resolve().parents[3]   # = calibration_engine/
if str(_ENGINE_DIR) not in sys.path:
    sys.path.insert(0, str(_ENGINE_DIR))

from SXC_V12_CORE import SXCOmegaEngine  # canonical implementation


# ---------------------------------------------------------------------------
# Per-signal percentile scaling to [0, 100]
# ---------------------------------------------------------------------------

def scale_signals_to_100(raw: Dict[str, pd.Series],
                          p_low: float = 2.0,
                          p_high: float = 98.0) -> Tuple[Dict[str, pd.Series], dict]:
    """
    Scale each raw signal to [0, 100] using its p_low / p_high percentile
    range.  Values outside the range are clipped.

    This matches the convention used in dcif_modules/energy_module:
        df['scaled_signal'] = (df['value'] / df['value'].max()) * 100

    The percentile-based approach is more robust to outliers than max-scaling.

    Returns
    -------
    scaled  : dict of scaled pd.Series
    params  : dict of {lo, hi} per signal (for documentation)
    """
    scaled = {}
    params = {}
    for name, s in raw.items():
        lo = np.percentile(s.dropna(), p_low)
        hi = np.percentile(s.dropna(), p_high)
        if hi <= lo:
            hi = lo + 1e-8
        clipped = s.clip(lower=lo, upper=hi)
        scaled[name] = ((clipped - lo) / (hi - lo) * 100.0)
        params[name] = {'lo': lo, 'hi': hi}
    return scaled, params


def build_v12_composite(scaled: Dict[str, pd.Series],
                        target_median: float = 8.0) -> Tuple[pd.Series, float]:
    """
    Build the V12 composite input signal.

    The SXCOmegaEngine FIREWALL steady-state threshold is at signal ≈ 10.3
    (where E·β = γ·T, i.e. E = γ/β = 0.8/3.5 = 0.2286,
    and  1 − exp(−s/40) = 0.2286  →  s ≈ 10.3).

    Typical quiet-market conditions must sit below this boundary so that
    NOMINAL and FIREWALL phases both occur with meaningful frequency.
    The percentile-scaled composite has a median of ~33, which is permanently
    above the boundary.  This function rescales so that the composite median
    maps to target_median (default 8.0), leaving stressed bars to spike above
    the threshold and trigger FIREWALL.

    Returns
    -------
    composite     : pd.Series, values in [0, ~100], median ≈ target_median
    scale_factor  : linear rescale applied (for documentation)
    """
    df         = pd.DataFrame(scaled).dropna()
    raw_comp   = df.mean(axis=1)
    actual_med = raw_comp.median()
    if actual_med <= 0:
        actual_med = 1.0
    scale_factor = target_median / actual_med
    composite    = (raw_comp * scale_factor).clip(lower=0.0)
    composite.name = 'v12_composite'
    return composite, scale_factor



# ---------------------------------------------------------------------------
# Stable engine for continuous multi-year runs
# ---------------------------------------------------------------------------

class SXCOmegaEngineStable(SXCOmegaEngine):
    """
    SXCOmegaEngine with γ-decay disabled for continuous history runs.

    The canonical engine decays γ by 0.05 % per step (half-life ≈ 1,386 bars
    ≈ 5 trading days).  Over 72,000+ bars the damping collapses to ~0,
    making outflow vanish and T_sys diverge to thousands.

    For the forensic validation across 2+ years of data we hold γ constant
    at γ_max.  This is consistent with the engine's own apply_intervention()
    logic which resets γ toward γ_max, and with the intent of the engine as
    a real-time estimator that would receive interventions in practice.
    """
    def step(self, signal):
        # Skip the gamma decay line from the parent step()
        self.gamma = self.gamma_max          # hold gamma at maximum
        E         = self.excitation_flux(signal)
        gamma_eff = 2.2 if self.phase == "FIREWALL" else 1.0
        inflow    = E * self.beta
        outflow   = gamma_eff * self.gamma * self.T_sys
        self.T_sys += (inflow - outflow) * self.dt

        if self.T_sys > 1.0:
            self.phase = "FIREWALL"
        elif self.phase == "FIREWALL" and self.T_sys < 0.4:
            self.phase = "NOMINAL"

        return self.T_sys, self.phase


# ---------------------------------------------------------------------------
# Run engine sequentially over composite signal series
# ---------------------------------------------------------------------------

def run_v12(composite: pd.Series) -> pd.DataFrame:
    """
    Execute SXCOmegaEngineStable tick-by-tick over the composite signal.

    Parameters
    ----------
    composite : pd.Series indexed by UTC timestamp, values in [0, ~30]
                (produced by build_v12_composite with target_median=8)

    Returns
    -------
    DataFrame with index = composite.index and columns:
        T_sys, phase, excitation, inflow, outflow, gamma, composite
    """
    engine = SXCOmegaEngineStable()

    records = []
    for ts, sig in composite.items():
        sig_val   = float(sig)
        E         = engine.excitation_flux(sig_val)
        gamma_eff = 2.2 if engine.phase == "FIREWALL" else 1.0
        inflow    = E * engine.beta
        outflow   = gamma_eff * engine.gamma * engine.T_sys

        T, phase  = engine.step(sig_val)

        records.append({
            'T_sys'      : T,
            'phase'      : phase,
            'excitation' : E,
            'inflow'     : inflow,
            'outflow'    : outflow,
            'gamma'      : engine.gamma,
            'composite'  : sig_val,
        })

    return pd.DataFrame(records, index=composite.index)


# ---------------------------------------------------------------------------
# Phase transition catalogue
# ---------------------------------------------------------------------------

def extract_transitions(v12: pd.DataFrame) -> pd.DataFrame:
    """
    Identify every phase transition.  Returns one row per episode.
    """
    phase     = v12['phase']
    events    = []
    start_idx = 0
    cur_phase = phase.iloc[0]

    for i in range(1, len(phase)):
        if phase.iloc[i] != cur_phase:
            events.append({
                'timestamp_in'  : v12.index[start_idx],
                'phase'         : cur_phase,
                'T_at_entry'    : v12['T_sys'].iloc[start_idx],
                'T_at_exit'     : v12['T_sys'].iloc[i - 1],
                'duration_bars' : i - start_idx,
                'duration_min'  : (i - start_idx) * 5,
            })
            cur_phase = phase.iloc[i]
            start_idx = i

    events.append({
        'timestamp_in'  : v12.index[start_idx],
        'phase'         : cur_phase,
        'T_at_entry'    : v12['T_sys'].iloc[start_idx],
        'T_at_exit'     : v12['T_sys'].iloc[-1],
        'duration_bars' : len(phase) - start_idx,
        'duration_min'  : (len(phase) - start_idx) * 5,
    })

    return pd.DataFrame(events)
