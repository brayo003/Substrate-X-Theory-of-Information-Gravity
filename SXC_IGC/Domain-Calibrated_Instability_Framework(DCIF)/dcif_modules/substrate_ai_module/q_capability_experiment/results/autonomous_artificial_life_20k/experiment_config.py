"""
Experiment configuration constants for the 20,000-tick autonomous artificial-life experiment.

World A: c_nominal=1.0, tau_nominal=1.0
World B: c_nominal=2.0, tau_nominal=1.0

Everything else identical. The physical-field condition is the sole independent variable.
"""
from __future__ import annotations

# ── Run identity ─────────────────────────────────────────────────────────────
RUN_ID = "aal20k_run_001"
GIT_REVISION = "8f101e7a303a909296511721ff202372c99cecfe"

# ── LLM settings ─────────────────────────────────────────────────────────────
OLLAMA_BASE_URL = "http://localhost:11434"
EXPERIMENT_MODEL = "qwen2.5-coder:1.5b"
LLM_TEMPERATURE = 0.7
LLM_MAX_TOKENS = 64
LLM_TIMEOUT = 360        # seconds per call

# ── Tick settings ─────────────────────────────────────────────────────────────
TARGET_TICKS = 20_000    # structural target; hardware constraint forces early stop
MAX_FEASIBLE_TICKS = 10  # hard cap for this hardware session (measured ~461s/tick)

# ── Checkpointing ─────────────────────────────────────────────────────────────
CHECKPOINT_INTERVAL = 100    # ticks between checkpoints
CHECKPOINT_INTERVAL_EARLY = 1  # also checkpoint every tick while ticks < 10 (full detail)

# ── Snapshot milestones ───────────────────────────────────────────────────────
SNAPSHOT_TICKS = {0, 1, 10, 100, 500, 1_000, 2_500, 5_000, 10_000, 15_000, 20_000}

# ── Field parameters ──────────────────────────────────────────────────────────
WORLD_A_NAME = "world_a_c1"
WORLD_B_NAME = "world_b_c2"
C_NOMINAL_A  = 1.0
C_NOMINAL_B  = 2.0
TAU_NOMINAL  = 1.0

# ── Reasoning gates (per-experiment instance overrides, not global) ───────────
COOLDOWN_TICKS      = 1
COOLDOWN_SECONDS    = 0.0
IMPORTANCE_THRESHOLD = 0.0

# ── Entities ──────────────────────────────────────────────────────────────────
SEED = "aal_20k_controlled_seed_v1"

ENTITY_DEFINITIONS = [
    {
        "name": "Agent_1",
        "type": "human",
        "location": "village_center",
        "needs": {"hunger": 0.85, "thirst": 0.75, "energy": 0.15},
        "inventory": {"food": 2.0, "water": 3.0},
    },
    {
        "name": "Agent_2",
        "type": "human",
        "location": "village_center",
        "needs": {"hunger": 0.60, "thirst": 0.55, "energy": 0.40},
        "inventory": {"food": 1.5, "water": 2.0},
    },
    {
        "name": "Agent_3",
        "type": "human",
        "location": "village_center",
        "needs": {"hunger": 0.40, "thirst": 0.35, "energy": 0.65},
        "inventory": {"food": 3.0, "water": 1.5},
    },
]

# ── 13 causal layers tracked for divergence ───────────────────────────────────
CAUSAL_LAYERS = [
    "field_parameters",
    "physical_field_state",
    "spectral_observable",
    "agent_perception",
    "llm_input",
    "llm_output",
    "intent",
    "goal",
    "plan",
    "action",
    "entity_state",
    "world_state",
    "memory",
]

# ── Measured LLM latency from benchmark ──────────────────────────────────────
BENCHMARK_LLM_LATENCY_MIN = 9.1    # seconds
BENCHMARK_LLM_LATENCY_MAX = 174.1  # seconds
BENCHMARK_LLM_LATENCY_AVG = 76.8   # seconds

# Derived estimates
LLM_CALLS_PER_TICK = len(ENTITY_DEFINITIONS) * 2  # 3 entities × 2 worlds = 6
ESTIMATED_SECONDS_PER_TICK = BENCHMARK_LLM_LATENCY_AVG * len(ENTITY_DEFINITIONS) * 2
ESTIMATED_HOURS_FOR_20K_TICKS = (ESTIMATED_SECONDS_PER_TICK * TARGET_TICKS) / 3600
