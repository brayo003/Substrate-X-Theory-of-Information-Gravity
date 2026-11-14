"""Frozen experimental configuration for the corrected Task 6 protocol.

Parameters are registered before confirmatory analysis. Do not retune after
inspecting confirmatory results.
"""
from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Any

# ---------------------------------------------------------------------------
# Grid / solver
# ---------------------------------------------------------------------------
GRID_NX: int = 30
GRID_NY: int = 30
GRID_X: float = 50.0
GRID_Y: float = 50.0
DT: float = 0.05

# Nonlinear reaction-telegraph (bistable candidate set)
NL_R: float = -0.5
NL_A: float = 2.0
NL_B: float = 1.0
NL_TAU: float = 1.0
NL_C: float = 1.0

# Analytical equilibria for (r,a,b)=(-0.5,2,1)
S0: float = 0.0
S_MINUS: float = (2.0 - (2.0 ** 0.5)) / 2.0   # ≈ 0.292893 (unstable)
S_PLUS: float = (2.0 + (2.0 ** 0.5)) / 2.0    # ≈ 1.707107 (stable high)

# Corrected IC: low-state basin (strictly below separatrix)
FIELD_IC: float = 0.0
# No random IC perturbations for fairness (C8 / D12)

# Deposit / readout
SUB_DEPOSIT_AMP: float = 1.2          # superthreshold local push above s-
SUB_DEPOSIT_AMP_SUB: float = 0.15     # subthreshold (G2 Test 2)
SUB_DEPOSIT_WIDTH: float = 2.0
SUB_READ_RADIUS: float = 4.0
HIGH_STATE_THRESH: float = 0.9        # classification threshold for high basin

# Agents / sensors
N_AGENTS: int = 6
AGENT_SPEED: float = 2.0
SENSOR_RADIUS: float = 4.0

# Conventional baselines
PHER_EVAP: float = 0.05
PHER_DEPOSIT: float = 1.0
MSG_TTL: int = 8
BB_STALE: int = 20

# Experiment A
EXP_A_TICKS: int = 60
EXP_A_DELAYS: tuple[int, ...] = (5, 15, 30)
EXP_A_DISTANCES: tuple[float, ...] = (5.0, 15.0, 25.0)

# Experiment B
EXP_B_TICKS: int = 40
EXP_B_SEPARATIONS: tuple[float, ...] = (6.0, 18.0)  # near vs far spatial relation

# Experiment C
EXP_C_TICKS: int = 80
N_RESOURCES: int = 8
N_HAZARDS: int = 5
N_TASK_SLOTS: int = 6

CONDITIONS: tuple[str, ...] = (
    "independent",
    "direct_msg",
    "blackboard",
    "pheromone",
    "linear_sub",
    "nonlinear_sub",
)

# Statistical plan (pre-registered before confirmatory)
PILOT_SEEDS: tuple[int, ...] = tuple(range(0, 12))
CONFIRM_SEED_START: int = 100
# Primary hypothesis: Experiment B interaction-task F1 for BOTH_NEAR
# (not raw accuracy — 4/5 cases are negative; always-0 yields 0.8 accuracy).
# nonlinear_sub vs conventional baselines (pre-registered comparison family).
PRIMARY_ENDPOINT: str = "exp_b_interaction_f1"
PRIMARY_COMPARISON: str = "nonlinear_sub_vs_conventional_max"
ALPHA: float = 0.05
# Comparison family for multiplicity (confirmatory):
# 1) nonlinear vs linear (ablation)
# 2) nonlinear vs direct_msg
# 3) nonlinear vs blackboard
# 4) nonlinear vs pheromone
# 5) nonlinear vs independent
N_PRIMARY_COMPARISONS: int = 5
MIN_MEANINGFUL_EFFECT_DZ: float = 0.5


@dataclass(frozen=True)
class ProtocolFreeze:
    """Snapshot of frozen protocol for results provenance."""
    field_ic: float = FIELD_IC
    nl_r: float = NL_R
    nl_a: float = NL_A
    nl_b: float = NL_B
    dt: float = DT
    grid: tuple[int, int] = (GRID_NX, GRID_NY)
    primary_endpoint: str = PRIMARY_ENDPOINT
    primary_comparison: str = PRIMARY_COMPARISON
    alpha: float = ALPHA
    n_primary_comparisons: int = N_PRIMARY_COMPARISONS
    min_meaningful_effect_dz: float = MIN_MEANINGFUL_EFFECT_DZ

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
