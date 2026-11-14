"""Frozen Task 7 configuration. Do not retune after confirmatory inspection."""
from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Any

# Reuse Task 6 grid / bistable parameters (matched, not retuned)
GRID_NX: int = 30
GRID_NY: int = 30
GRID_X: float = 50.0
GRID_Y: float = 50.0
DT: float = 0.05

NL_R: float = -0.5
NL_A: float = 2.0
NL_B: float = 1.0
NL_TAU: float = 1.0
NL_C: float = 1.0
FIELD_IC: float = 0.0
S_MINUS: float = (2.0 - (2.0 ** 0.5)) / 2.0
S_PLUS: float = (2.0 + (2.0 ** 0.5)) / 2.0
HIGH_STATE_THRESH: float = 0.9

SUB_DEPOSIT_WIDTH: float = 2.0
SUB_READ_RADIUS: float = 4.0

# Track A — hazard corridor
AGENT_SPEED: float = 2.0
SENSOR_RADIUS: float = 3.5
HAZARD_RADIUS: float = 5.0
# Positive danger-marker amplitude (substrate latching); NOT Task-6 negative encoding
HAZARD_DEPOSIT_AMP: float = 1.2
DETOUR_LENGTH_PENALTY_WEIGHT: float = 0.02  # cost reported, not free

# Track A info-sharing conditions
# A none | B discovered-withheld | C immediate | D delay5 | E delay15 | F disconnect
TRACK_A_DELAYS: dict[str, int] = {
    "A_no_discovery": -1,
    "B_withheld": -1,
    "C_immediate": 0,
    "D_delay5": 5,
    "E_delay15": 15,
    "F_disconnect": 20,  # discoverer gone; evolve then recipient acts
}

# Track B — bistable AND-gate (primary computational challenge)
# Individually subthreshold; pair near/overlap crosses separatrix
# Pilot-tuned (exploratory): single deposit max≈0.21 < s-≈0.29;
# near pair max≈0.51 > s- (high-basin entry). Readout uses crossed-separatrix
# evidence (thr=0.40), not full s+ saturation — documented in freeze file.
AND_SUB_AMP: float = 0.18
AND_SUPER_PAIR_FACTOR: float = 1.0
AND_NEAR_SEP: float = 3.0
AND_FAR_SEP: float = 18.0
AND_EVOLVE_TICKS: int = 60
AND_READ_THRESH: float = 0.40  # above separatrix ≈0.293; latched toward high

# Conventional baselines (matched to Task 6 fairness docs)
PHER_EVAP: float = 0.05
PHER_DEPOSIT: float = 1.0
MSG_TTL: int = 8
BB_STALE: int = 40  # longer than AND_EVOLVE for fair structured persistence in Track B

CONDITIONS: tuple[str, ...] = (
    "independent",
    "direct_msg",
    "blackboard",
    "pheromone",
    "linear_sub",
    "nonlinear_sub",
)

# Ablations for Track B (mechanism isolation)
ABLATIONS: tuple[str, ...] = (
    "nonlinear_full",
    "linear_telegraph",
    "nonlinear_reaction_off",  # r=a=b=0 identical to linear
    "no_propagation",         # c=0
)

# Statistics
PILOT_SEEDS: tuple[int, ...] = tuple(range(0, 10))
CONFIRM_SEED_START: int = 200
ALPHA: float = 0.05
# Track A primary family: informed (C/D/E/F as applicable) vs A_no_discovery, per architecture
# Track B primary family: nonlinear vs {linear, direct_msg, blackboard, pheromone, independent}
N_TRACK_A_PRIMARY_COMPS: int = 1  # primary: mean exposure informed vs no-info within nonlinear (and report all)
N_TRACK_B_PRIMARY_COMPS: int = 5
MIN_MEANINGFUL_EFFECT_DZ: float = 0.5

TRACK_A_PRIMARY: str = "paired_exposure_reduction_informed_vs_noinfo"
TRACK_B_PRIMARY: str = "bistable_and_gate_f1"


@dataclass(frozen=True)
class Exp7ProtocolFreeze:
    field_ic: float = FIELD_IC
    nl_r: float = NL_R
    nl_a: float = NL_A
    nl_b: float = NL_B
    hazard_deposit_amp: float = HAZARD_DEPOSIT_AMP
    hazard_encoding: str = "positive_danger_marker"
    and_sub_amp: float = AND_SUB_AMP
    and_near_sep: float = AND_NEAR_SEP
    and_far_sep: float = AND_FAR_SEP
    track_a_primary: str = TRACK_A_PRIMARY
    track_b_primary: str = TRACK_B_PRIMARY
    alpha: float = ALPHA
    min_dz: float = MIN_MEANINGFUL_EFFECT_DZ
    bb_stale: int = BB_STALE

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
