"""
EXP2 Environment
================

CoordinationTaskEnvironment for the controlled spectral substrate coordination
experiment.

DESIGN PRINCIPLES
-----------------
1. Coordination demand varies over simulation time, generated from a seeded
   RNG stream that is separate from field, agent, and ablation streams.

2. The coordination schedule is NEVER accessible to agent policies.
   Agents observe only: (a) which task slots are currently open,
   (b) how many resources they have, (c) the substrate signal (condition-
   dependent). They do NOT receive the schedule, task timers, or any quantity
   that encodes future demand.

3. Bidirectional field coupling:
   - When ≥ MIN_COORD_AGENTS agents commit to cooperate on the same zone
     in the same tick, a COHERENT concentrated perturbation is applied to the
     field at that zone.  This pushes high-k fluctuation power → C_spectral ↑.
   - Individual actions apply DISPERSED small perturbations from agent positions.
   - The field thus encodes the collective coordination history.

4. Two task types:
   COORDINATION task: requires MIN_COORD_AGENTS (≥3) simultaneous commitments
     at the announced zone.  Reward: COORD_REWARD per participating agent.
   INDEPENDENT task:  any single agent can complete alone.
     Reward: INDEP_REWARD per completion.  
     Opportunity cost of unnecessary coordination: if an agent cooperates
     when no coordination task is active, it wastes an independent task slot.

5. Agents are informed that a coordination task is *available* (zone announced)
   but not whether the task is part of a "wave" of upcoming tasks.

INFORMATION AVAILABLE TO AGENTS
--------------------------------
Per-tick observation (fed into agent context, NOT the hidden schedule):
  - coord_task_active (bool): a coordination task is open this tick
  - coord_task_zone (x, y) or None: announced zone if active
  - indep_slots_available (int): number of independent tasks available
  - agent_resources (float): own resource level
  - c_spectral (float, condition-dependent): substrate signal or 0.0

Hidden from agents:
  - task schedule (when future tasks arrive, how many, cluster structure)
  - task timer (ticks remaining for current task)
  - other agents' actions (agents are independent decision-makers)
"""

from __future__ import annotations

import math
import os
import sys
from dataclasses import dataclass, field
from typing import Any

_HERE = os.path.dirname(os.path.abspath(__file__))
_PARENT = os.path.dirname(_HERE)
if _PARENT not in sys.path:
    sys.path.insert(0, _PARENT)

import numpy as np

from sim_world.domains.physical_field.physical_field_dynamics import (
    initialize_field_state,
    evolve_field,
    apply_perturbation,
    compute_spectral_transport_observable,
)
from sim_world.domains.physical_field.physical_field_models import (
    InformationDensityField,
    PhysicalCoordinate,
    PropagationParameters,
    RelaxationParameters,
)
from sim_world.domains.physical_field.substrate_state import SubstrateState


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

N_AGENTS: int = 5
MIN_COORD_AGENTS: int = 3        # minimum agents needed to complete a coord task
COORD_REWARD: float = 2.0        # reward per agent for a successful coord task
INDEP_REWARD: float = 0.6        # reward per completion of an independent task
UNNECESSARY_COORD_COST: float = 0.3  # opportunity cost when cooperating with no task
TASK_WINDOW_TICKS: int = 3       # ticks a coordination task stays open
INDEP_SLOTS_PER_TICK: int = 3    # how many independent tasks available each tick
GRID_NX: int = 30
GRID_NY: int = 30
GRID_X_MAX: float = 50.0
GRID_Y_MAX: float = 50.0
DT: float = 0.05

# Perturbation parameters
COHERENT_PERT_AMP: float = 3.5   # amplitude per coordinating agent (additive)
INDEP_PERT_AMP: float = 0.4      # amplitude for individual action
PERT_WIDTH_COHERENT: float = 2.5  # narrow → high k modes → C_spectral ↑
PERT_WIDTH_INDEP: float = 5.0    # wider → lower k modes


# ---------------------------------------------------------------------------
# Task schedule generator
# ---------------------------------------------------------------------------

def generate_task_schedule(
    n_ticks: int,
    rng: np.random.Generator,
    cluster_prob: float = 0.35,
    cluster_size_range: tuple[int, int] = (3, 6),
    solo_rate: float = 0.08,
) -> list[dict]:
    """Generate coordination task schedule independently of field or agents.

    Returns a list of task descriptors, one entry per coordination task.
    Each descriptor:
      {
        "tick_start": int,          # tick the task becomes available
        "zone": (float, float),     # (x, y) of coordination zone
        "task_id": int,
      }

    Strategy: tasks arrive in clusters (high local demand) separated by quiet
    periods. This creates genuine temporal structure in coordination demand
    that the substrate might or might not track.

    Args:
        n_ticks: Total simulation ticks.
        rng: Seeded RNG for schedule generation (must be isolated from field/agent RNGs).
        cluster_prob: Probability that a tick starts a new cluster.
        cluster_size_range: (min, max) tasks per cluster.
        solo_rate: Probability of a solo coordination task per tick (non-cluster).
    """
    tasks = []
    task_id = 0
    tick = 0
    while tick < n_ticks:
        # Decide: cluster event?
        if float(rng.random()) < cluster_prob:
            cluster_size = int(rng.integers(cluster_size_range[0],
                                            cluster_size_range[1] + 1))
            # Spread cluster tasks across TASK_WINDOW_TICKS * 2 ticks
            spread = max(1, TASK_WINDOW_TICKS)
            for ci in range(cluster_size):
                t_offset = int(rng.integers(0, spread))
                t_task = min(tick + t_offset, n_ticks - 1)
                zone = (
                    float(rng.uniform(10.0, GRID_X_MAX - 10.0)),
                    float(rng.uniform(10.0, GRID_Y_MAX - 10.0)),
                )
                tasks.append({
                    "tick_start": t_task,
                    "zone": zone,
                    "task_id": task_id,
                })
                task_id += 1
            # Skip ahead past cluster + cooldown
            tick += spread + int(rng.integers(4, 10))
        else:
            # Solo task
            if float(rng.random()) < solo_rate:
                zone = (
                    float(rng.uniform(10.0, GRID_X_MAX - 10.0)),
                    float(rng.uniform(10.0, GRID_Y_MAX - 10.0)),
                )
                tasks.append({
                    "tick_start": tick,
                    "zone": zone,
                    "task_id": task_id,
                })
                task_id += 1
            tick += 1

    # Sort by start tick
    tasks.sort(key=lambda t: t["tick_start"])
    return tasks


# ---------------------------------------------------------------------------
# Agent state
# ---------------------------------------------------------------------------

@dataclass
class AgentState:
    agent_id: int
    x: float
    y: float
    resources: float          # accumulated task rewards
    hunger: float             # 0=satisfied, 1=hungry (from indep tasks maintaining food)
    energy: float             # 0=depleted, 1=full
    stress: float             # 0=calm, 1=stressed
    _initial_resources: float = field(init=False)

    def __post_init__(self) -> None:
        self._initial_resources = self.resources

    # --- Decision: given observation, return action ---

    def decide(
        self,
        obs: "TickObservation",
        signal: float,              # C_spectral or 0.0 depending on condition
    ) -> str:
        """
        Select action given observation and substrate signal.

        Actions:
          "cooperate"   — commit to the announced coordination zone
          "independent" — complete an independent task
          "forage"      — address hunger need
          "rest"        — address energy need

        Policy:
          The substrate signal (via coordination_capacity) modulates the
          agent's willingness to cooperate. Higher signal → lower threshold
          needed for cooperation decision.

          Critical needs still override.
        """
        # Critical needs always override
        if self.hunger > 0.80:
            return "forage"
        if self.energy < 0.15:
            return "rest"

        # Coordination-capacity from substrate
        coord_cap = 0.5 * (1.0 + max(-1.0, min(1.0, signal)))

        if obs.coord_task_active:
            # A coordination task is announced. Cooperate if capacity sufficient.
            need_pressure = (self.hunger + self.stress) / 2.0
            threshold = 0.30 + 0.40 * need_pressure  # rises with need
            if coord_cap > threshold and self.stress < 0.65:
                return "cooperate"

        # No coordination task (or not enough capacity): go independent
        if obs.indep_slots_available > 0 and self.hunger > 0.35:
            return "independent"
        if self.energy < 0.40:
            return "rest"
        if self.hunger > 0.40:
            return "forage"
        return "independent"

    def apply_outcome(
        self,
        action: str,
        signal: float,
        coord_success: bool,
        coord_participating: bool,
    ) -> None:
        """Update agent state based on action outcome."""
        coord_eff = 0.8 + 0.4 * max(0.0, signal)  # 0.8–1.2

        if action == "cooperate":
            if coord_success and coord_participating:
                # Successful coordination: get reward, reduce stress
                self.resources += COORD_REWARD
                self.stress = max(0.0, self.stress - 0.12 * coord_eff)
                self.energy = max(0.0, self.energy - 0.05 / coord_eff)
                self.hunger = min(1.0, self.hunger + 0.02)
            else:
                # Failed coordination or no task: opportunity cost
                self.resources -= UNNECESSARY_COORD_COST
                self.energy = max(0.0, self.energy - 0.07)
                self.hunger = min(1.0, self.hunger + 0.03)

        elif action == "independent":
            self.resources += INDEP_REWARD
            self.hunger = max(0.0, self.hunger - 0.10)
            self.energy = max(0.0, self.energy - 0.06)

        elif action == "forage":
            self.hunger = max(0.0, self.hunger - 0.18)
            self.energy = max(0.0, self.energy - 0.08)

        elif action == "rest":
            self.energy = min(1.0, self.energy + 0.12)
            self.stress = max(0.0, self.stress - 0.05)

        # Metabolic tick
        self.hunger = min(1.0, self.hunger + 0.015)


# ---------------------------------------------------------------------------
# Per-tick observation (what agents can see)
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class TickObservation:
    tick: int
    coord_task_active: bool           # a coord task is open this tick
    coord_task_zone: tuple | None     # (x, y) if active, else None
    indep_slots_available: int        # independent task slots
    # Note: NO schedule information, NO task timers, NO future demand


# ---------------------------------------------------------------------------
# Field builder (vectorised perturbation for speed)
# ---------------------------------------------------------------------------

def _build_field(
    rng: np.random.Generator,
    tau: float,
    c: float = 1.0,
) -> tuple:
    """Build initial field. Returns (field, prop, relax)."""
    state = initialize_field_state(
        x_range=(0.0, GRID_X_MAX),
        y_range=(0.0, GRID_Y_MAX),
        nx=GRID_NX,
        ny=GRID_NY,
        initial_value=1.0,
        dt=DT,
    )
    f = InformationDensityField(
        state=state,
        information_quantity=1.0,
        physical_volume=GRID_X_MAX * GRID_Y_MAX * 1.0,
        information_units="bits",
        spatial_units="m",
        density_units="bits/m³",
    )
    # Seed-derived initial bumps
    for _ in range(4):
        bx = float(rng.uniform(10.0, 40.0))
        by = float(rng.uniform(10.0, 40.0))
        amp = float(rng.uniform(2.0, 4.0))
        f = apply_perturbation(f, PhysicalCoordinate(bx, by, 0.0), amp, 3.0)
    prop = PropagationParameters(c_nominal=c)
    relax = RelaxationParameters(tau_nominal=tau)
    return f, prop, relax


def _make_agents(rng: np.random.Generator) -> list[AgentState]:
    """Create N_AGENTS with seed-derived initial states."""
    agents = []
    for i in range(N_AGENTS):
        agents.append(AgentState(
            agent_id=i,
            x=float(rng.uniform(5.0, GRID_X_MAX - 5.0)),
            y=float(rng.uniform(5.0, GRID_Y_MAX - 5.0)),
            resources=0.0,
            hunger=float(rng.uniform(0.20, 0.45)),
            energy=float(rng.uniform(0.65, 0.90)),
            stress=float(rng.uniform(0.10, 0.30)),
        ))
    return agents


# ---------------------------------------------------------------------------
# Field coupling (bidirectional)
# ---------------------------------------------------------------------------

def _apply_coordination_perturbation(
    field: InformationDensityField,
    zone_x: float,
    zone_y: float,
    n_participating: int,
) -> InformationDensityField:
    """Apply coherent concentrated perturbation at coordination zone.

    Coherent: concentrated at zone center → high-k modes → C_spectral ↑.
    """
    total_amp = COHERENT_PERT_AMP * n_participating
    return apply_perturbation(
        field,
        PhysicalCoordinate(zone_x, zone_y, 0.0),
        total_amp,
        PERT_WIDTH_COHERENT,
    )


def _apply_individual_perturbation(
    field: InformationDensityField,
    agent: AgentState,
) -> InformationDensityField:
    """Apply dispersed perturbation from individual agent action."""
    return apply_perturbation(
        field,
        PhysicalCoordinate(agent.x, agent.y, 0.0),
        INDEP_PERT_AMP,
        PERT_WIDTH_INDEP,
    )


# ---------------------------------------------------------------------------
# Single-tick logic
# ---------------------------------------------------------------------------

@dataclass
class TickResult:
    tick: int
    # Task outcomes
    coord_task_active: bool
    coord_task_zone: tuple | None
    coord_task_id: int | None
    n_cooperating: int              # agents who chose cooperate
    coord_success: bool             # n_cooperating >= MIN_COORD_AGENTS
    # Metrics
    indep_completions: int
    # Field observable (computed AFTER field evolves, AFTER perturbations)
    c_spectral: float
    f_prop: float
    f_over: float
    dominant_regime: str
    spectral_entropy: float
    weighted_D: float
    # Agent states snapshot
    agent_states: list[dict]
    # Raw observable (not passed to agents during decision)
    obs_raw: dict


# ---------------------------------------------------------------------------
# Main simulation loop
# ---------------------------------------------------------------------------

def run_trial(
    seed: int,
    condition: str,            # "baseline" | "spectral" | "time_reversed" | "shuffled" | "constant"
    n_ticks: int,
    tau: float,
    c: float = 1.0,
    exp_id: str = "",
) -> dict[str, Any]:
    """
    Run one complete trial.  Fully self-contained.

    RNG streams (isolated):
      rng_field   (seed)         — field initialisation, bump positions
      rng_agents  (seed + 1_000) — agent initial states
      rng_schedule(seed + 2_000) — task schedule generation
      rng_ablation(seed + 3_000) — shuffled ablation permutation

    Returns a dict containing:
      - experiment metadata
      - full per-tick records
      - aggregate metrics
    """
    if not exp_id:
        exp_id = f"exp2_{condition}_{seed}"

    # -------------------------------------------------------------------
    # 1. Isolated RNG streams
    # -------------------------------------------------------------------
    rng_field    = np.random.default_rng(seed)
    rng_agents   = np.random.default_rng(seed + 1_000)
    rng_schedule = np.random.default_rng(seed + 2_000)
    rng_ablation = np.random.default_rng(seed + 3_000)

    # -------------------------------------------------------------------
    # 2. Build field, agents, task schedule
    # -------------------------------------------------------------------
    field, prop, relax = _build_field(rng_field, tau, c)
    agents = _make_agents(rng_agents)
    task_schedule = generate_task_schedule(n_ticks, rng_schedule)

    # -------------------------------------------------------------------
    # 3. Pre-compute ablation signal series if needed.
    #    For time_reversed, shuffled, constant: we need the full spectral
    #    series from an identical reference run FIRST.
    # -------------------------------------------------------------------
    ablation_signals: list[float] | None = None
    if condition in ("time_reversed", "shuffled", "constant"):
        # Run an identical field-only pass to collect spectral series.
        # Uses the same RNG seed for field and schedule (identical environment).
        ref_rng_field = np.random.default_rng(seed)
        ref_rng_agents = np.random.default_rng(seed + 1_000)
        ref_rng_schedule = np.random.default_rng(seed + 2_000)

        ref_field, ref_prop, ref_relax = _build_field(ref_rng_field, tau, c)
        ref_agents = _make_agents(ref_rng_agents)
        ref_schedule = generate_task_schedule(n_ticks, ref_rng_schedule)

        spectral_series: list[float] = []
        for t in range(n_ticks):
            # Determine active task this tick (same schedule)
            active_task = None
            for task in ref_schedule:
                if (task["tick_start"] <= t <
                        task["tick_start"] + TASK_WINDOW_TICKS):
                    active_task = task
                    break
            obs_ref = TickObservation(
                tick=t,
                coord_task_active=active_task is not None,
                coord_task_zone=active_task["zone"] if active_task else None,
                indep_slots_available=INDEP_SLOTS_PER_TICK,
            )
            # Agents act with spectral signal (reference condition)
            ref_obs_spectral = compute_spectral_transport_observable(
                ref_field, ref_prop, ref_relax)
            ref_signal = ref_obs_spectral.c_spectral
            spectral_series.append(ref_signal)
            ref_actions = [a.decide(obs_ref, ref_signal) for a in ref_agents]
            cooperating = [
                a for a, act in zip(ref_agents, ref_actions)
                if act == "cooperate"
            ]
            coord_ok = (active_task is not None and
                        len(cooperating) >= MIN_COORD_AGENTS)
            if coord_ok:
                ref_field = _apply_coordination_perturbation(
                    ref_field, active_task["zone"][0],
                    active_task["zone"][1], len(cooperating))
            for a, act in zip(ref_agents, ref_actions):
                ref_field = _apply_individual_perturbation(ref_field, a)
                a.apply_outcome(act, ref_signal, coord_ok,
                                act == "cooperate" and coord_ok)
            ref_field = evolve_field(ref_field, ref_prop, ref_relax)

        # Apply ablation transformation
        if condition == "time_reversed":
            ablation_signals = list(reversed(spectral_series))
        elif condition == "shuffled":
            arr = spectral_series[:]
            rng_ablation.shuffle(arr)
            ablation_signals = arr
        elif condition == "constant":
            mean_val = float(np.mean(spectral_series))
            ablation_signals = [mean_val] * n_ticks

    # -------------------------------------------------------------------
    # 4. Main simulation loop
    # -------------------------------------------------------------------
    per_tick_records: list[dict] = []
    coord_task_opportunities = 0
    coord_task_successes = 0
    indep_completions_total = 0

    for tick in range(n_ticks):
        # --- 4a. Determine active coordination task ---
        active_task = None
        for task in task_schedule:
            if task["tick_start"] <= tick < task["tick_start"] + TASK_WINDOW_TICKS:
                active_task = task
                break
        if active_task is not None:
            coord_task_opportunities += 1

        # --- 4b. Build per-tick observation (no hidden info) ---
        tick_obs = TickObservation(
            tick=tick,
            coord_task_active=active_task is not None,
            coord_task_zone=active_task["zone"] if active_task else None,
            indep_slots_available=INDEP_SLOTS_PER_TICK,
        )

        # --- 4c. Compute substrate signal for this condition ---
        if condition == "baseline":
            signal = 0.0
            # Still compute observable for recording, but don't pass to agents
            spectral_obs = compute_spectral_transport_observable(
                field, prop, relax)
            c_sp = spectral_obs.c_spectral
        elif condition == "spectral":
            spectral_obs = compute_spectral_transport_observable(
                field, prop, relax)
            signal = spectral_obs.c_spectral
            c_sp = signal
        elif condition in ("time_reversed", "shuffled", "constant"):
            assert ablation_signals is not None
            signal = ablation_signals[tick]
            # Still compute actual field observable for records
            spectral_obs = compute_spectral_transport_observable(
                field, prop, relax)
            c_sp = spectral_obs.c_spectral
        else:
            raise ValueError(f"Unknown condition: {condition!r}")

        # --- 4d. Agent decisions ---
        actions: dict[int, str] = {}
        for agent in agents:
            actions[agent.agent_id] = agent.decide(tick_obs, signal)

        # --- 4e. Coordination outcome ---
        cooperating_agents = [
            a for a in agents if actions[a.agent_id] == "cooperate"
        ]
        n_cooperating = len(cooperating_agents)
        coord_success = (
            active_task is not None and n_cooperating >= MIN_COORD_AGENTS
        )
        if coord_success:
            coord_task_successes += 1

        indep_agents = [a for a in agents if actions[a.agent_id] == "independent"]
        indep_completions = min(len(indep_agents), INDEP_SLOTS_PER_TICK)
        indep_completions_total += indep_completions

        # --- 4f. Bidirectional field coupling ---
        # Coordination perturbation AFTER decisions but BEFORE next tick's observation
        if coord_success:
            field = _apply_coordination_perturbation(
                field,
                active_task["zone"][0],
                active_task["zone"][1],
                n_cooperating,
            )
        # Individual perturbations from all agents
        for agent in agents:
            field = _apply_individual_perturbation(field, agent)

        # --- 4g. Apply outcomes to agents ---
        for agent in agents:
            agent.apply_outcome(
                actions[agent.agent_id],
                signal,
                coord_success,
                actions[agent.agent_id] == "cooperate" and coord_success,
            )

        # --- 4h. Evolve field ---
        field = evolve_field(field, prop, relax)

        # --- 4i. Record per-tick state ---
        per_tick_records.append({
            "exp_id":               exp_id,
            "condition":            condition,
            "seed":                 seed,
            "tick":                 tick,
            "tau":                  tau,
            # Task
            "coord_task_active":    active_task is not None,
            "coord_task_id":        active_task["task_id"] if active_task else None,
            "coord_task_zone_x":    active_task["zone"][0] if active_task else None,
            "coord_task_zone_y":    active_task["zone"][1] if active_task else None,
            # Coordination outcome
            "n_cooperating":        n_cooperating,
            "coord_success":        coord_success,
            "indep_completions":    indep_completions,
            # Substrate signal (what agents received)
            "signal_to_agents":     round(signal, 6),
            # Actual field observable (ground truth, independent of condition)
            "c_spectral_actual":    round(c_sp, 6),
            "f_prop":               round(spectral_obs.propagating_power_fraction, 6),
            "f_over":               round(spectral_obs.overdamped_power_fraction, 6),
            "dominant_regime":      spectral_obs.dominant_regime,
            "spectral_entropy":     round(spectral_obs.spectral_entropy, 6),
            "weighted_D":           round(spectral_obs.weighted_D, 6),
            # Agent states
            "agent_states":         [
                {
                    "id":        a.agent_id,
                    "action":    actions[a.agent_id],
                    "resources": round(a.resources, 4),
                    "hunger":    round(a.hunger, 4),
                    "energy":    round(a.energy, 4),
                    "stress":    round(a.stress, 4),
                }
                for a in agents
            ],
        })

    # -------------------------------------------------------------------
    # 5. Aggregate metrics
    # -------------------------------------------------------------------
    coord_completion_rate = (
        coord_task_successes / coord_task_opportunities
        if coord_task_opportunities > 0 else float("nan")
    )
    total_resources = sum(a.resources for a in agents)
    mean_resources = total_resources / N_AGENTS
    mean_hunger = sum(a.hunger for a in agents) / N_AGENTS
    mean_energy = sum(a.energy for a in agents) / N_AGENTS
    mean_stress = sum(a.stress for a in agents) / N_AGENTS
    coord_rate = sum(
        1 for r in per_tick_records for a in r["agent_states"]
        if a["action"] == "cooperate"
    ) / (N_AGENTS * n_ticks)
    indep_rate = sum(
        1 for r in per_tick_records for a in r["agent_states"]
        if a["action"] == "independent"
    ) / (N_AGENTS * n_ticks)

    # C_spectral statistics (actual field values)
    c_actuals = [r["c_spectral_actual"] for r in per_tick_records]
    c_std = float(np.std(c_actuals))
    c_mean = float(np.mean(c_actuals))

    return {
        "exp_id":                   exp_id,
        "condition":                condition,
        "seed":                     seed,
        "tau":                      tau,
        "n_ticks":                  n_ticks,
        "n_agents":                 N_AGENTS,
        "valid":                    True,
        # PRIMARY
        "coord_completion_rate":    round(coord_completion_rate, 6)
                                    if not math.isnan(coord_completion_rate) else None,
        # SECONDARY
        "coord_task_opportunities": coord_task_opportunities,
        "coord_task_successes":     coord_task_successes,
        "indep_completions_total":  indep_completions_total,
        "mean_resources":           round(mean_resources, 6),
        "total_resources":          round(total_resources, 6),
        "mean_hunger":              round(mean_hunger, 6),
        "mean_energy":              round(mean_energy, 6),
        "mean_stress":              round(mean_stress, 6),
        "coordination_rate":        round(coord_rate, 6),
        "independent_rate":         round(indep_rate, 6),
        # Field observable stats
        "c_spectral_mean":          round(c_mean, 6),
        "c_spectral_std":           round(c_std, 6),
        # Raw records
        "per_tick": per_tick_records,
    }
