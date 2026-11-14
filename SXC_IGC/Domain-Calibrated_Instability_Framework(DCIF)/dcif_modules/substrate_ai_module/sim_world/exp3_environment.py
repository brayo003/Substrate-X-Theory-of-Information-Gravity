"""
EXP3 Environment — Substrate-Mediated Coordination Discovery
=============================================================

Key design changes from EXP2:

1. NO coordination gate. Agents never receive coord_task_active.
   They must independently discover coordination opportunities through
   the substrate signal alone.

2. Probabilistic policy: P(cooperate) = coord_cap = 0.5*(1+c_spectral).
   This creates a smooth, testable relationship between signal and behavior.

3. Environmental precursor: an independent external event injects a narrow
   Gaussian (high-k) perturbation into the field 3-8 ticks before some
   coordination tasks. This is the ONLY direct environmental signal path.

4. Four event types (hidden from agents, recorded for analysis):
   A = precursor + task  (TP opportunity)
   B = task only         (FN opportunity)
   C = precursor only    (FP risk)
   D = neither           (TN)

5. Seven experimental conditions:
   baseline        — signal=0.0
   spectral        — actual C_spectral
   online_shuffled — past C_spectral values, random draw from history
   online_delayed  — C_spectral[t-k], k=5
   running_mean    — mean(C_spectral[0..t])
   precursor_only  — C_spectral, agent perturbations disabled
   feedback_only   — C_spectral, environmental precursor disabled

6. ALL ablations are strictly online: at tick t, only signals from ticks
   0..t are used. No future information anywhere.

INFORMATION AVAILABLE TO AGENTS (exhaustive):
  - Own hunger, energy, stress
  - Own accumulated resources
  - Substrate signal (condition-dependent; see above)
  - NOTHING ELSE

Hidden from agents (recorded for evaluation only):
  - coord_task_active, task schedule, task zone
  - precursor_active, precursor zone, event_type
  - Other agents' actions
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
    evolve_field_nonlinear,
    apply_perturbation,
    compute_spectral_transport_observable,
)
from sim_world.domains.physical_field.physical_field_models import (
    InformationDensityField,
    PhysicalCoordinate,
    PropagationParameters,
    RelaxationParameters,
    NonlinearReactionParameters,
)


# ---------------------------------------------------------------------------
# Constants (frozen after pilot calibration)
# ---------------------------------------------------------------------------

N_AGENTS: int = 5
MIN_COORD_AGENTS: int = 3         # requires 3 of 5 to cooperate (pilot-calibrated)
TASK_WINDOW_TICKS: int = 8        # ticks a task stays open (pilot-calibrated: tw=8 maximises spectral gap)
TASK_INTERVAL_MIN: int = 8        # min ticks between tasks
TASK_INTERVAL_MAX: int = 15       # max ticks between tasks
INDEP_REWARD: float = 0.5         # reward per independent task completion
COORD_REWARD: float = 2.5         # reward per agent for successful coordination
UNNECESSARY_COORD_COST: float = 0.4   # cost per tick of unnecessary cooperation

PRECURSOR_PROB: float = 0.60      # P(task has precursor) → Type A vs B
PRECURSOR_SPURIOUS_PROB: float = 0.30  # P(spurious precursor → Type C) per quiet period
PRECURSOR_LEAD_MIN: int = 3       # ticks before task that precursor fires
PRECURSOR_LEAD_MAX: int = 8
PRECURSOR_AMP: float = 5.0        # amplitude of precursor perturbation
PRECURSOR_WIDTH: float = 1.5      # width (m) — narrow → high-k → C_spectral ↑

AGENT_PERT_AMP: float = 0.4       # individual agent perturbation amplitude
AGENT_PERT_WIDTH: float = 5.0     # wide → lower-k → less C_spectral change
COORD_PERT_AMP: float = 3.0       # per-agent amplitude on coordination success
COORD_PERT_WIDTH: float = 2.5     # narrow → high-k

GRID_NX: int = 30
GRID_NY: int = 30
GRID_X_MAX: float = 50.0
GRID_Y_MAX: float = 50.0
DT: float = 0.05

ONLINE_SHUFFLE_DELAY: int = 5     # delay k for online_delayed condition

CONDITIONS = [
    "baseline",
    "spectral",
    "online_shuffled",
    "online_delayed",
    "running_mean",
    "precursor_only",
    "feedback_only",
]


# ---------------------------------------------------------------------------
# Schedule generation
# ---------------------------------------------------------------------------

@dataclass
class TaskEvent:
    task_id: int
    tick_start: int
    zone: tuple[float, float]
    has_precursor: bool           # Type A (True) or Type B (False)
    precursor_tick: int | None    # tick the precursor fires (if has_precursor)
    precursor_zone: tuple[float, float] | None


@dataclass
class PrecursorEvent:
    precursor_id: int
    tick: int
    zone: tuple[float, float]
    task_id: int | None           # None → Type C (spurious)


def generate_schedule(
    n_ticks: int,
    rng: np.random.Generator,
) -> tuple[list[TaskEvent], list[PrecursorEvent]]:
    """
    Generate task and precursor schedules independently.

    Returns (tasks, precursors). Both are sorted by tick.
    The schedule determines event types:
      A = task with precursor (precursor_tick < task tick_start)
      B = task without precursor
      C = spurious precursor (no subsequent task)
      D = quiet period (neither)

    Nothing in this function uses field state or agent state.
    It is driven entirely by rng (seed+2000).
    """
    tasks: list[TaskEvent] = []
    precursors: list[PrecursorEvent] = []
    task_id = 0
    precursor_id = 0

    tick = int(rng.integers(TASK_INTERVAL_MIN // 2, TASK_INTERVAL_MIN))
    while tick < n_ticks:
        # Task zone (randomised, not correlated with precursor zone)
        tz = (float(rng.uniform(10., GRID_X_MAX - 10.)),
              float(rng.uniform(10., GRID_Y_MAX - 10.)))

        has_precursor = float(rng.random()) < PRECURSOR_PROB
        precursor_tick = None
        precursor_zone = None

        if has_precursor:
            lead = int(rng.integers(PRECURSOR_LEAD_MIN, PRECURSOR_LEAD_MAX + 1))
            precursor_tick = tick - lead
            if precursor_tick >= 0:
                # Precursor zone differs from task zone
                pz = (float(rng.uniform(5., GRID_X_MAX - 5.)),
                      float(rng.uniform(5., GRID_Y_MAX - 5.)))
                precursors.append(PrecursorEvent(
                    precursor_id=precursor_id,
                    tick=precursor_tick,
                    zone=pz,
                    task_id=task_id,
                ))
                precursor_zone = pz
                precursor_id += 1
            else:
                has_precursor = False  # lead would go before tick 0

        tasks.append(TaskEvent(
            task_id=task_id,
            tick_start=tick,
            zone=tz,
            has_precursor=has_precursor,
            precursor_tick=precursor_tick,
            precursor_zone=precursor_zone,
        ))
        task_id += 1

        # Possibly insert a spurious precursor in the gap before next task
        gap = int(rng.integers(TASK_INTERVAL_MIN, TASK_INTERVAL_MAX + 1))
        gap_tick = tick + TASK_WINDOW_TICKS + 1
        if (float(rng.random()) < PRECURSOR_SPURIOUS_PROB
                and gap_tick + 2 < tick + gap):
            sp_tick = gap_tick + int(rng.integers(0, max(1, gap - TASK_WINDOW_TICKS - 3)))
            if sp_tick < n_ticks:
                pz = (float(rng.uniform(5., GRID_X_MAX - 5.)),
                      float(rng.uniform(5., GRID_Y_MAX - 5.)))
                precursors.append(PrecursorEvent(
                    precursor_id=precursor_id,
                    tick=sp_tick,
                    zone=pz,
                    task_id=None,  # spurious
                ))
                precursor_id += 1

        tick += gap

    tasks.sort(key=lambda t: t.tick_start)
    precursors.sort(key=lambda p: p.tick)
    return tasks, precursors


# ---------------------------------------------------------------------------
# Field helpers
# ---------------------------------------------------------------------------

def _build_field(rng: np.random.Generator, tau: float, c: float = 1.0) -> tuple:
    state = initialize_field_state(
        x_range=(0., GRID_X_MAX), y_range=(0., GRID_Y_MAX),
        nx=GRID_NX, ny=GRID_NY, initial_value=1.0, dt=DT,
    )
    f = InformationDensityField(
        state=state, information_quantity=1.,
        physical_volume=GRID_X_MAX * GRID_Y_MAX * 1.,
        information_units="bits", spatial_units="m", density_units="bits/m³",
    )
    for _ in range(4):
        bx = float(rng.uniform(10., 40.))
        by = float(rng.uniform(10., 40.))
        amp = float(rng.uniform(1.5, 3.0))
        f = apply_perturbation(f, PhysicalCoordinate(bx, by, 0.), amp, 3.0)
    return f, PropagationParameters(c_nominal=c), RelaxationParameters(tau_nominal=tau)


# ---------------------------------------------------------------------------
# Agent state
# ---------------------------------------------------------------------------

@dataclass
class AgentState:
    agent_id: int
    x: float
    y: float
    resources: float
    hunger: float
    energy: float
    stress: float
    _initial_stress: float = field(init=False)

    def __post_init__(self) -> None:
        self._initial_stress = self.stress

    def p_cooperate(self, signal: float) -> float:
        """P(cooperate) = coordination_capacity = 0.5*(1+c_spectral)."""
        return 0.5 * (1.0 + max(-1.0, min(1.0, signal)))

    def decide(self, signal: float, rng_dec: np.random.Generator) -> str:
        """
        Probabilistic decision. No task announcement.

        Actions: cooperate | independent | forage | rest

        Physical overrides (not task information):
          hunger > 0.85 → forage
          energy < 0.10 → rest
        These override cooperation to prevent agent starvation.
        """
        if self.hunger > 0.85:
            return "forage"
        if self.energy < 0.10:
            return "rest"

        p_coop = self.p_cooperate(signal)
        if float(rng_dec.random()) < p_coop:
            return "cooperate"

        # Fall through to need-based local actions
        if self.hunger > 0.50:
            return "forage"
        if self.energy < 0.35:
            return "rest"
        return "independent"

    def apply_outcome(
        self,
        action: str,
        signal: float,
        coord_success: bool,
        coord_participating: bool,
    ) -> None:
        coord_eff = 0.8 + 0.4 * max(0., signal)   # 0.8–1.2

        if action == "cooperate":
            if coord_success and coord_participating:
                self.resources += COORD_REWARD
                self.stress = max(0., self.stress - 0.10 * coord_eff)
                self.energy = max(0., self.energy - 0.05 / coord_eff)
                self.hunger = min(1., self.hunger + 0.02)
            else:
                # Unnecessary cooperation: opportunity cost
                self.resources -= UNNECESSARY_COORD_COST
                self.energy = max(0., self.energy - 0.07)
                self.hunger = min(1., self.hunger + 0.03)

        elif action == "independent":
            self.resources += INDEP_REWARD
            self.hunger = max(0., self.hunger - 0.10)
            self.energy = max(0., self.energy - 0.06)

        elif action == "forage":
            self.hunger = max(0., self.hunger - 0.18)
            self.energy = max(0., self.energy - 0.07)

        elif action == "rest":
            self.energy = min(1., self.energy + 0.12)
            self.stress = max(0., self.stress - 0.05)

        # Metabolic tick
        self.hunger = min(1., self.hunger + 0.015)


def _make_agents(rng: np.random.Generator) -> list[AgentState]:
    agents = []
    for i in range(N_AGENTS):
        agents.append(AgentState(
            agent_id=i,
            x=float(rng.uniform(5., GRID_X_MAX - 5.)),
            y=float(rng.uniform(5., GRID_Y_MAX - 5.)),
            resources=0.,
            hunger=float(rng.uniform(0.20, 0.45)),
            energy=float(rng.uniform(0.65, 0.90)),
            stress=float(rng.uniform(0.10, 0.30)),
        ))
    return agents


# ---------------------------------------------------------------------------
# Signal computation (all online)
# ---------------------------------------------------------------------------

def compute_signal(
    condition: str,
    field,
    prop,
    relax,
    c_history: list[float],   # C_spectral history[0..t-1] (past only)
    rng_ablation: np.random.Generator,
    delay: int = ONLINE_SHUFFLE_DELAY,
) -> float:
    """
    Compute signal for this tick. ALL ablations are strictly online:
    at tick t, only c_history[0..t-1] (already elapsed ticks) are available.

    Returns signal ∈ [-1, +1] (or 0.0 for baseline).
    """
    if condition == "baseline":
        return 0.0

    # Spectral conditions: compute actual C_spectral first
    obs = compute_spectral_transport_observable(field, prop, relax)
    c_actual = float(obs.c_spectral)

    if condition in ("spectral", "precursor_only", "feedback_only"):
        return c_actual

    if condition == "online_shuffled":
        if not c_history:
            return c_actual   # no history yet → use current
        # Draw uniformly from past observations
        idx = int(rng_ablation.integers(0, len(c_history)))
        return float(c_history[idx])

    if condition == "online_delayed":
        if len(c_history) < delay:
            return c_history[0] if c_history else 0.0
        return float(c_history[-delay])   # c_history[-delay] = tick t-delay

    if condition == "running_mean":
        if not c_history:
            return c_actual
        return float(np.mean(c_history))

    raise ValueError(f"Unknown condition: {condition!r}")


# ---------------------------------------------------------------------------
# Main trial runner
# ---------------------------------------------------------------------------

def run_trial(
    seed: int,
    condition: str,
    n_ticks: int,
    tau: float,
    c: float = 1.0,
    exp_id: str = "",
    task_window: int = TASK_WINDOW_TICKS,
    min_coord: int = MIN_COORD_AGENTS,
    reaction_params: NonlinearReactionParameters | None = None,
) -> dict[str, Any]:
    """
    Run one complete EXP3 trial.

    RNG streams (fully isolated):
      seed          → rng_field    (field initialisation)
      seed + 1000   → rng_agents   (agent initial states)
      seed + 2000   → rng_schedule (task + precursor schedule)
      seed + 3000   → rng_ablation (online ablation draws)
      seed + 4000   → rng_decision (agent cooperation decisions)
      seed + 5000   → rng_precursor (precursor zone / timing variation — currently
                                     folded into rng_schedule, kept for future)

    Returns dict with metadata, aggregate metrics, and per_tick records.
    Per-tick records include:
      - Hidden evaluation fields (event_type, precursor_active, task_active)
        → NEVER passed to agents
      - Signal delivered to agents (condition-dependent)
      - Actual C_spectral from field (always recorded for analysis)
      - Agent decisions and outcomes
    """
    if not exp_id:
        exp_id = f"exp3_{condition}_{seed}_tau{tau:.1f}".replace(".", "p")

    assert condition in CONDITIONS, f"Unknown condition: {condition!r}"

    # 1. Build isolated RNG streams
    rng_field    = np.random.default_rng(seed)
    rng_agents   = np.random.default_rng(seed + 1_000)
    rng_schedule = np.random.default_rng(seed + 2_000)
    rng_ablation = np.random.default_rng(seed + 3_000)
    rng_decision = np.random.default_rng(seed + 4_000)

    # 2. Build field, agents, schedule
    field, prop, relax = _build_field(rng_field, tau, c)
    agents = _make_agents(rng_agents)
    tasks, precursors = generate_schedule(n_ticks, rng_schedule)

    # 3. Build lookup maps for O(1) access
    # active_at[tick] = task (may overlap if window >1)
    active_at: dict[int, TaskEvent] = {}
    for task in tasks:
        for t in range(task.tick_start, min(task.tick_start + task_window, n_ticks)):
            if t not in active_at:
                active_at[t] = task

    precursor_at: dict[int, PrecursorEvent] = {}
    for prec in precursors:
        precursor_at[prec.tick] = prec

    # Determine event type for each tick (for evaluation records only)
    def event_type(tick: int) -> str:
        has_task = tick in active_at
        has_prec = tick in precursor_at
        if has_task and has_prec:   return "A"
        if has_task:                return "B"
        if has_prec:                return "C"
        return "D"

    # 4. Main loop
    per_tick_records: list[dict] = []
    c_history: list[float] = []  # C_spectral history (actual values, all past ticks)

    coord_opp = 0
    coord_succ = 0
    unneeded_coord = 0
    inactive_ticks = 0
    indep_completions_total = 0
    # Event-type counters
    type_counts: dict[str, int] = {"A": 0, "B": 0, "C": 0, "D": 0}
    type_succ:   dict[str, int] = {"A": 0, "B": 0}

    for tick in range(n_ticks):
        active_task = active_at.get(tick)
        active_prec = precursor_at.get(tick)
        etype = event_type(tick)
        type_counts[etype] += 1

        if active_task is not None:
            coord_opp += 1

        # --- Apply environmental precursor to field ---
        # For precursor_only and spectral conditions: apply precursor.
        # For feedback_only: NO precursor (testing feedback-only mechanism).
        # For all other conditions: apply precursor (it enters field, not agent context).
        apply_precursor = (
            active_prec is not None and condition != "feedback_only"
        )
        if apply_precursor:
            field = apply_perturbation(
                field,
                PhysicalCoordinate(active_prec.zone[0], active_prec.zone[1], 0.),
                PRECURSOR_AMP, PRECURSOR_WIDTH,
            )

        # --- Compute actual C_spectral (always, for recording) ---
        obs_actual = compute_spectral_transport_observable(field, prop, relax)
        c_actual = float(obs_actual.c_spectral)

        # --- Compute signal for agents (condition-dependent, strictly online) ---
        signal = compute_signal(
            condition, field, prop, relax,
            c_history, rng_ablation,
        )

        # --- Agent decisions (probabilistic, no task announcement) ---
        actions: dict[int, str] = {}
        for agent in agents:
            actions[agent.agent_id] = agent.decide(signal, rng_decision)

        # --- Coordination outcome ---
        n_cooperating = sum(1 for a in actions.values() if a == "cooperate")
        coord_success = (active_task is not None and n_cooperating >= min_coord)
        if coord_success:
            coord_succ += 1
            if etype in ("A", "B"):
                type_succ[etype] = type_succ.get(etype, 0) + 1

        # Unnecessary cooperation: n_coop >= min_coord when no task
        if active_task is None:
            inactive_ticks += 1
            if n_cooperating >= min_coord:
                unneeded_coord += 1

        # Independent completions
        n_indep = sum(1 for a in actions.values() if a == "independent")
        indep_completions_total += n_indep

        # --- Field coupling (bidirectional) ---
        # Coordination perturbation: only if condition allows agent perturbations
        # precursor_only disables agent-to-field perturbations.
        apply_agent_perts = (condition != "precursor_only")

        if apply_agent_perts:
            if coord_success:
                field = apply_perturbation(
                    field,
                    PhysicalCoordinate(active_task.zone[0], active_task.zone[1], 0.),
                    COORD_PERT_AMP * n_cooperating, COORD_PERT_WIDTH,
                )
            for agent in agents:
                field = apply_perturbation(
                    field,
                    PhysicalCoordinate(agent.x, agent.y, 0.),
                    AGENT_PERT_AMP, AGENT_PERT_WIDTH,
                )

        # --- Apply outcomes ---
        for agent in agents:
            agent.apply_outcome(
                actions[agent.agent_id], signal,
                coord_success,
                actions[agent.agent_id] == "cooperate" and coord_success,
            )

        # --- Evolve field ---
        # evolve_field_nonlinear falls through to the linear solver when
        # reaction_params is None or all-zero (preserves existing behavior)
        field = evolve_field_nonlinear(field, prop, relax, reaction_params)

        # --- Update history (AFTER decision, so current tick is now past) ---
        c_history.append(c_actual)

        # --- Record ---
        per_tick_records.append({
            "exp_id":           exp_id,
            "condition":        condition,
            "seed":             seed,
            "tick":             tick,
            "tau":              tau,
            "task_window":      task_window,
            "min_coord":        min_coord,
            # Hidden evaluation fields (NOT available to agents)
            "coord_task_active": active_task is not None,
            "coord_task_id":    active_task.task_id if active_task else None,
            "precursor_active": active_prec is not None,
            "precursor_id":     active_prec.precursor_id if active_prec else None,
            "precursor_is_spurious": (active_prec.task_id is None) if active_prec else None,
            "event_type":       etype,
            # Signal delivered to agents
            "signal_to_agents": round(signal, 6),
            # Actual field observable (always recorded)
            "c_spectral_actual": round(c_actual, 6),
            "f_prop":           round(obs_actual.propagating_power_fraction, 6),
            "f_over":           round(obs_actual.overdamped_power_fraction, 6),
            "dominant_regime":  obs_actual.dominant_regime,
            "spectral_entropy": round(obs_actual.spectral_entropy, 6),
            "weighted_D":       round(obs_actual.weighted_D, 6),
            # Outcomes
            "n_cooperating":    n_cooperating,
            "coord_success":    coord_success,
            "indep_completions": n_indep,
            # Agent states
            "agent_states": [
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

    # --- Aggregate metrics ---
    ccr = coord_succ / coord_opp if coord_opp > 0 else None
    unneeded_rate = unneeded_coord / inactive_ticks if inactive_ticks > 0 else 0.

    # Event-type completion rates
    type_a_ccr = (type_succ.get("A", 0) / max(1, sum(1 for r in per_tick_records
                   if r["event_type"]=="A" and r["coord_task_active"])))
    type_b_ccr = (type_succ.get("B", 0) / max(1, sum(1 for r in per_tick_records
                   if r["event_type"]=="B" and r["coord_task_active"])))
    type_c_fp  = sum(1 for r in per_tick_records
                     if r["event_type"]=="C" and r["n_cooperating"] >= min_coord
                     ) / max(1, type_counts["C"])

    c_actuals = [r["c_spectral_actual"] for r in per_tick_records]

    return {
        "exp_id":               exp_id,
        "condition":            condition,
        "seed":                 seed,
        "tau":                  tau,
        "n_ticks":              n_ticks,
        "n_agents":             N_AGENTS,
        "task_window":          task_window,
        "min_coord":            min_coord,
        "valid":                True,
        # PRIMARY
        "coord_completion_rate": round(ccr, 6) if ccr is not None else None,
        # SECONDARY
        "coord_task_opportunities": coord_opp,
        "coord_task_successes":     coord_succ,
        "unnecessary_coop_rate":    round(unneeded_rate, 6),
        "indep_completions_total":  indep_completions_total,
        "mean_resources":           round(sum(a.resources for a in agents)/N_AGENTS, 6),
        "mean_hunger":              round(sum(a.hunger for a in agents)/N_AGENTS, 6),
        "mean_energy":              round(sum(a.energy for a in agents)/N_AGENTS, 6),
        "mean_stress":              round(sum(a.stress for a in agents)/N_AGENTS, 6),
        "coordination_rate":        round(sum(1 for r in per_tick_records
                                              for a in r["agent_states"]
                                              if a["action"]=="cooperate")/(N_AGENTS*n_ticks), 6),
        # Event-type metrics (for mechanism analysis)
        "type_a_opportunities":     type_counts["A"],
        "type_b_opportunities":     type_counts["B"],
        "type_c_count":             type_counts["C"],
        "type_a_ccr":               round(type_a_ccr, 6),
        "type_b_ccr":               round(type_b_ccr, 6),
        "type_c_fp_rate":           round(type_c_fp, 6),
        # Field signal stats
        "c_spectral_mean":          round(float(np.mean(c_actuals)), 6),
        "c_spectral_std":           round(float(np.std(c_actuals)), 6),
        # Raw records
        "per_tick": per_tick_records,
    }
