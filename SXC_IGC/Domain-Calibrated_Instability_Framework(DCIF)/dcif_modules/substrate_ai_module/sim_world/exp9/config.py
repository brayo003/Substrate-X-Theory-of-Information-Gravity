"""Task 9 configuration. Pilot may explore; confirmatory freeze in exp9_configuration.json."""
from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Any

# Matched to Tasks 7–8 bistable operating point (do not retune for advantage)
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

DEPOSIT_WIDTH = 2.0
READ_RADIUS = 5.0
ACTIVATION_THRESH = 0.85  # high-basin (Task 8)
# Slightly below Task 8's 0.50 so sustained-hold readout separates bistable latch
# from linear multi-deposit transients; controlled coincidence smoke still passes.
DEP_AMP = 0.45

# Environment
N_LANDMARKS = 4
LANDMARKS = (
    (12.0, 12.0),
    (38.0, 12.0),
    (12.0, 38.0),
    (38.0, 38.0),
)
N_AGENTS = 4
AGENT_SPEED = 3.0
SENSOR_RADIUS = 4.0
T_MAX = 200
MAX_DEPOSITS_PER_AGENT = 1  # scarce writes → coincidence needs multiple agents
OBS_NOISE_SIGMA = 0.30
EVIDENCE_TRUE_MEAN = 1.0
EVIDENCE_DISTRACTOR_MEAN = 0.40  # below detect on average; noise can still trigger
EVIDENCE_DETECT_THRESH = 0.65
N_TRUE_EVIDENCE = 4
N_DISTRACTOR_EVIDENCE = 4
EVIDENCE_JITTER = 5.5  # near posts but not trivial full coverage from one pose
# Small footprint jitter: coincidence is temporal+spatial overlap, not cell stacking
DEPOSIT_JITTER = 0.6
# Sustained readout for field media (tests persistence/hysteresis, not same-tick peak)
COMMIT_HOLD_TICKS = 20
# Conventional channels: shorter hold (no bistable latch); multi-source still required
MSG_HOLD_TICKS = 3
PHER_HOLD_TICKS = 3
# Independent: need many distinct strong patch observations (hard without sharing)
INDEP_MIN_STRONG_OBS = 3
# Agents initialize at public landmark posts (fair; does not reveal k*)
SPAWN_AT_LANDMARKS = True
# One deposit per landmark per agent (prevents solo amplitude stacking)
ONE_DEPOSIT_PER_LANDMARK = True
# Carry local observation to the public post (agent memory of own sensing — not GT)
ALLOW_EVIDENCE_CARRY = True

# Conventional baseline params — multi-source parity with 2-deposit coincidence
PHER_EVAP = 0.05
PHER_DEPOSIT = 1.0
PHER_COMMIT_THRESH = 0.75  # ~2 colocated deposits (single peak ~0.5)
MSG_TTL = 40
BB_STALE = 80
MSG_COMMIT_CONF = 0.65
MSG_MIN_SUPPORT = 2  # ≥2 corroborating reports (parity with coincidence)
HYBRID_MSG_BUDGET = 4

# Cost weights (reporting)
W_WRITE = 1.0
W_READ = 0.2
W_MSG = 1.0
W_TRAVEL = 0.05
W_SOLVER = 0.01

# Experiment C delays
C_DELAYS = (0, 2, 5, 10, 15, 20, 40)

# Seeds
PILOT_SEEDS = tuple(range(0, 8))
CONFIRM_SEED_START = 400
CONFIRM_N = 24
ALPHA = 0.05
N_PRIMARY_COMPS = 5

ARCHITECTURES = (
    "nonlinear_sub",
    "linear_sub",
    "independent",
    "direct_msg",
    "blackboard",
    "pheromone",
    "hybrid",
)

ABLATIONS_B = (
    "nonlinear_full",
    "linear_telegraph",
    "reaction_off",
    "no_propagation",
    "no_hysteresis",
    "readout_disabled",
    "deposit_disabled",
    "fixed_random_policy",
)


@dataclass(frozen=True)
class Exp9ProtocolFreeze:
    nl_r: float = NL_R
    nl_a: float = NL_A
    nl_b: float = NL_B
    nl_tau: float = NL_TAU
    nl_c: float = NL_C
    dt: float = DT
    dep_amp: float = DEP_AMP
    activation_thresh: float = ACTIVATION_THRESH
    commit_hold_ticks: int = COMMIT_HOLD_TICKS
    msg_min_support: int = MSG_MIN_SUPPORT
    n_agents: int = N_AGENTS
    t_max: int = T_MAX
    obs_noise_sigma: float = OBS_NOISE_SIGMA
    confirm_n: int = CONFIRM_N
    confirm_seed_start: int = CONFIRM_SEED_START
    encoding: str = "single_gaussian_near_task8_scale"
    note: str = (
        "Landmarks are public environmental posts; correct index k* withheld from agents. "
        "tau=1 so docstring/code Laplacian factor agree. "
        "DEP_AMP=0.45 + COMMIT_HOLD_TICKS=20 separate bistable latch from linear transients; "
        "field equation coefficients unchanged from Tasks 7–8."
    )

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
