"""Frozen Task 8 configuration (do not retune after confirmatory inspection)."""
from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Any

GRID_NX = 30
GRID_NY = 30
GRID_X = 50.0
GRID_Y = 50.0
DT = 0.05

NL_R = -0.5
NL_A = 2.0
NL_B = 1.0
NL_TAU = 1.0
NL_C = 1.0
FIELD_IC = 0.0

S_MINUS = (2.0 - (2.0 ** 0.5)) / 2.0
S_PLUS = (2.0 + (2.0 ** 0.5)) / 2.0

DEPOSIT_WIDTH = 2.0
READ_RADIUS = 5.0
# High-basin latch: requires dynamical growth beyond instantaneous deposit peak.
# At A_SUB_AMP=0.50, near-pair peak0≈0.71; nonlinear evolves to ≈0.99; linear decays.
# thr=0.85 ⇒ readout_only and linear fail; nonlinear near succeeds (pilot-verified).
ACTIVATION_THRESH = 0.85

# ---------------------------------------------------------------------------
# Encoding note (Task 7 carry-forward ambiguity, not a Task-7 edit)
# Task 7 AND deposited each site twice (kind X/Y + kind event), so
# AND_SUB_AMP=0.18 was effectively ~0.36 per site and used thr=0.40 (separatrix
# evidence). Task 8 uses a clean single-Gaussian-per-input encoding with a
# stricter high-basin threshold so the decoder cannot fire on peak0 alone.
# ---------------------------------------------------------------------------
A_SUB_AMP = 0.50
A_NEAR_SEP = 3.0
A_FAR_SEP = 18.0
A_EVOLVE = 60
A_SEP_GRID = (2.0, 3.0, 4.0, 6.0, 8.0, 10.0, 12.0, 15.0, 18.0)
A_AMP_GRID = (0.30, 0.35, 0.40, 0.45, 0.50, 0.55, 0.60, 0.70, 0.85)
A_TRIPLE_FRAC = 0.65  # each of 3 deposits; individually subthreshold

# Experiment B — temporal integration (amp=0.50, thr=0.85: window ~5 ticks)
B_SUB_AMP = 0.50
B_SEP = 3.0
B_DELAYS = (0, 2, 5, 10, 15, 20, 40)
B_MEM_WINDOW = 5  # GT: activate if delay <= window
B_EVOLVE_AFTER = 60

# Experiment C — equal mass
C_TOTAL_MASS = 1.00  # two × 0.50
C_EVOLVE = 60

# Experiment D — hysteresis / threshold
D_AMP_SWEEP = (0.10, 0.20, 0.30, 0.40, 0.50, 0.60, 0.70, 0.85, 1.00, 1.20)
D_EVOLVE = 80
D_HOLD = 40

# Experiment E
E_AMP = 0.70  # agree should high-basin latch; compete uses A_SUB_AMP
E_EVOLVE = 40

# Experiment F
F_TEMPLATE_AMP = 1.2
F_PARTIAL_FRAC = 0.4
F_EVOLVE = 50

# Behavioural bridge (conditional)
BRIDGE_OBS_AMP = 0.50
BRIDGE_SEP_NEAR = 3.0
BRIDGE_SEP_FAR = 18.0
BRIDGE_EVOLVE = 60

PILOT_SEEDS = tuple(range(0, 8))
CONFIRM_SEED_START = 300
CONFIRM_N = 24
ALPHA = 0.05
N_PRIMARY_COMPS = 6  # A–F primary endpoint family

ABLATIONS = (
    "nonlinear_full",
    "linear_telegraph",
    "reaction_off",
    "no_propagation",
    "no_inertia",
    "readout_only",
)


@dataclass(frozen=True)
class Exp8ProtocolFreeze:
    nl_r: float = NL_R
    nl_a: float = NL_A
    nl_b: float = NL_B
    nl_tau: float = NL_TAU
    nl_c: float = NL_C
    dt: float = DT
    activation_thresh: float = ACTIVATION_THRESH
    a_sub_amp: float = A_SUB_AMP
    a_near_sep: float = A_NEAR_SEP
    a_far_sep: float = A_FAR_SEP
    a_triple_frac: float = A_TRIPLE_FRAC
    b_mem_window: int = B_MEM_WINDOW
    encoding: str = "single_gaussian_per_input"
    task7_encoding_note: str = (
        "Task7 AND used dual kind deposits (effective ~2x amp) and thr=0.40; "
        "Task8 uses single deposit per input, amp=0.50, high-basin thr=0.85 "
        "so readout_only cannot pass on instantaneous overlap"
    )
    confirm_n: int = CONFIRM_N
    note: str = "tau=1 so docstring/code Laplacian factor agree"

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
