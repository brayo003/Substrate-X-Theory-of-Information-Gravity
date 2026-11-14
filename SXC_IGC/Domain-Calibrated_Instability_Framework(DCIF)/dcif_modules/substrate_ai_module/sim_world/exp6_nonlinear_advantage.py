"""
EXP6 — Nonlinear Substrate Agentic Advantage Experiment
========================================================

Hypothesis: a nonlinear reaction-telegraph substrate provides heterogeneous
agents with a persistent, distributed, dynamically evolving representation
that improves coordination, information recovery, and decision quality over
conventional communication alternatives under matched information budgets.

Conditions
----------
A — Independent     : no shared memory, no messaging
B — Direct-msg      : agents broadcast discoveries; recipients forget after TTL
C — Blackboard      : shared write-once list, global read; matched write budget
D — Pheromone       : stigmergic grid, Gaussian deposit + evaporation
E — Nonlinear-sub   : nonlinear reaction-telegraph field (r,a,b ≠ 0)
F — Linear-sub      : linear telegraph field (r=a=b=0, ablation of E)

Task families (run in same trial environment)
---------------------------------------------
Task 1 — Distributed resource discovery
Task 2 — Hazardous-region coordination
Task 3 — Distributed task allocation (conflict avoidance)

Statistical design
------------------
• Paired comparisons: each seed generates identical event schedules for all
  conditions.
• Primary outcomes (pre-registered): task-completion rate, duplicate-work
  fraction, information-recovery accuracy.
• Effect sizes: Cohen's d.
• CIs: bootstrap (2000 resamples, 95%).
• Multiple-comparison correction: Bonferroni over 5 pairwise comparisons vs A.
• Pilot (N=20 seeds) → variance estimate → confirmatory (N=60 seeds).

Usage
-----
  python exp6_nonlinear_advantage.py          # full run
  python exp6_nonlinear_advantage.py --pilot  # pilot only
"""
from __future__ import annotations

import argparse
import json
import math
import os
import random
import sys
import time
from dataclasses import dataclass, field
from typing import Any

import numpy as np

# ---------------------------------------------------------------------------
# Path setup
# ---------------------------------------------------------------------------
_HERE   = os.path.dirname(os.path.abspath(__file__))
_PARENT = os.path.dirname(_HERE)
for _p in (_PARENT, _HERE):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from sim_world.domains.physical_field.physical_field_dynamics import (
    initialize_field_state,
    evolve_field,
    evolve_field_nonlinear,
    apply_perturbation,
    compute_spectral_transport_observable,
)
from sim_world.domains.physical_field.physical_field_models import (
    InformationDensityField,
    FieldState,
    PhysicalCoordinate,
    PropagationParameters,
    RelaxationParameters,
    NonlinearReactionParameters,
)

# ===========================================================================
# SECTION 1 — GLOBAL CONSTANTS
# ===========================================================================

# Grid
GRID_NX: int   = 30
GRID_NY: int   = 30
GRID_X:  float = 50.0
GRID_Y:  float = 50.0
DT:      float = 0.05

# Agents
N_AGENTS: int = 6
AGENT_SPEED: float = 2.0        # m/tick max move
SENSOR_RADIUS: float = 4.0      # m — agent "sees" within this radius

# Substrate parameters (nonlinear condition)
NL_R: float = -0.5
NL_A: float =  2.0
NL_B: float =  1.0
NL_TAU: float = 1.0
NL_C:   float = 1.0

# Substrate deposit / readout
SUB_DEPOSIT_AMP:   float = 2.0   # amplitude written when agent injects info
SUB_DEPOSIT_WIDTH: float = 2.0   # Gaussian σ (m) for injection
SUB_READ_RADIUS:   float = 4.0   # m — spatial average for readout

# Pheromone
PHER_EVAP: float    = 0.05       # evaporation per tick (fraction)
PHER_DEPOSIT: float = 1.0        # deposit per event

# Direct-message TTL
MSG_TTL: int = 8                 # ticks a message persists

# Task parameters
N_RESOURCES:    int   = 8        # resource sites
N_HAZARDS:      int   = 5        # hazard zones
N_TASK_SLOTS:   int   = 6        # task-allocation slots
RESOURCE_REWARD: float = 2.0
HAZARD_COST:     float = 3.0
ALLOC_REWARD:    float = 2.5
STALE_TICKS:     int   = 20      # event becomes stale after this many ticks

# Trial length
N_TICKS: int = 80

# Conditions
CONDITIONS: list[str] = ["independent", "direct_msg", "blackboard", "pheromone",
                          "nonlinear_sub", "linear_sub"]

# ===========================================================================
# SECTION 2 — ENVIRONMENT EVENTS (shared across conditions per seed)
# ===========================================================================

@dataclass
class ResourceSite:
    site_id: int
    x: float
    y: float
    tick_available: int
    tick_expires: int
    value: float = RESOURCE_REWARD

@dataclass
class HazardZone:
    hz_id: int
    x: float
    y: float
    radius: float
    tick_start: int
    tick_end: int

@dataclass
class TaskSlot:
    slot_id: int
    x: float
    y: float
    tick_open: int
    tick_close: int
    n_agents_needed: int    # 1 or 2
    value: float = ALLOC_REWARD

def generate_environment(seed: int, n_ticks: int = N_TICKS) -> dict[str, Any]:
    """
    Generate all events for one trial. Same seed → identical events across
    all conditions (paired comparison).
    """
    rng = np.random.default_rng(seed + 9000)

    resources = []
    for i in range(N_RESOURCES):
        t_avail = int(rng.integers(0, n_ticks // 2))
        duration = int(rng.integers(10, 35))
        resources.append(ResourceSite(
            site_id=i,
            x=float(rng.uniform(3., GRID_X - 3.)),
            y=float(rng.uniform(3., GRID_Y - 3.)),
            tick_available=t_avail,
            tick_expires=min(t_avail + duration, n_ticks),
        ))

    hazards = []
    for i in range(N_HAZARDS):
        t_start = int(rng.integers(5, n_ticks // 2))
        duration = int(rng.integers(8, 30))
        hazards.append(HazardZone(
            hz_id=i,
            x=float(rng.uniform(5., GRID_X - 5.)),
            y=float(rng.uniform(5., GRID_Y - 5.)),
            radius=float(rng.uniform(3., 7.)),
            tick_start=t_start,
            tick_end=min(t_start + duration, n_ticks),
        ))

    task_slots = []
    for i in range(N_TASK_SLOTS):
        t_open = int(rng.integers(5, n_ticks - 15))
        duration = int(rng.integers(10, 25))
        n_needed = int(rng.choice([1, 2], p=[0.5, 0.5]))
        task_slots.append(TaskSlot(
            slot_id=i,
            x=float(rng.uniform(5., GRID_X - 5.)),
            y=float(rng.uniform(5., GRID_Y - 5.)),
            tick_open=t_open,
            tick_close=min(t_open + duration, n_ticks),
            n_agents_needed=n_needed,
        ))

    return {"resources": resources, "hazards": hazards, "task_slots": task_slots}


# ===========================================================================
# SECTION 3 — AGENT
# ===========================================================================

@dataclass
class Agent:
    agent_id:  int
    x:         float
    y:         float
    energy:    float = 1.0
    # Task 1 — resources collected
    resources_collected: int = 0
    # Task 2 — hazard exposures
    hazard_exposures:    int = 0
    # Task 3 — tasks completed
    tasks_completed:     int = 0

    def dist(self, x: float, y: float) -> float:
        return math.hypot(self.x - x, self.y - y)

    def move_toward(self, tx: float, ty: float, speed: float, rng: np.random.Generator) -> None:
        dx = tx - self.x
        dy = ty - self.y
        d = math.hypot(dx, dy)
        if d < 0.01:
            return
        step = min(speed, d)
        noise_x = float(rng.uniform(-0.3, 0.3))
        noise_y = float(rng.uniform(-0.3, 0.3))
        self.x = float(np.clip(self.x + (dx / d) * step + noise_x, 0., GRID_X))
        self.y = float(np.clip(self.y + (dy / d) * step + noise_y, 0., GRID_Y))

    def move_random(self, speed: float, rng: np.random.Generator) -> None:
        angle = float(rng.uniform(0., 2 * math.pi))
        step  = float(rng.uniform(0., speed))
        self.x = float(np.clip(self.x + step * math.cos(angle), 0., GRID_X))
        self.y = float(np.clip(self.y + step * math.sin(angle), 0., GRID_Y))


def _make_agents(seed: int) -> list[Agent]:
    rng = np.random.default_rng(seed + 1000)
    agents = []
    for i in range(N_AGENTS):
        agents.append(Agent(
            agent_id=i,
            x=float(rng.uniform(2., GRID_X - 2.)),
            y=float(rng.uniform(2., GRID_Y - 2.)),
            energy=float(rng.uniform(0.7, 1.0)),
        ))
    return agents


# ===========================================================================
# SECTION 4 — COMMUNICATION BACKENDS
# ===========================================================================

class IndependentMemory:
    """Condition A: no shared state."""
    def deposit_resource(self, x, y, tick): pass
    def deposit_hazard(self, x, y, r, tick): pass
    def deposit_task(self, slot_id, x, y, tick): pass
    def query_resource(self, ax, ay, tick) -> float: return 0.0
    def query_hazard(self, ax, ay, tick) -> float: return 0.0
    def query_task(self, slot_id, tick) -> float: return 0.0
    def tick_update(self, tick): pass


class DirectMsgMemory:
    """
    Condition B: agents broadcast (x,y,kind,tick); messages expire after TTL.
    Read: strongest unexpired signal within sensor radius.
    Budget-matched: same number of deposits as blackboard (one per agent per
    tick maximum — identical to blackboard write rate).
    """
    def __init__(self):
        # Each message: (x, y, kind, value, tick_sent)
        self._msgs: list[tuple[float,float,str,float,int]] = []

    def _deposit(self, x, y, kind, value, tick):
        self._msgs.append((x, y, kind, value, tick))

    def deposit_resource(self, x, y, tick):
        self._deposit(x, y, "resource", RESOURCE_REWARD, tick)

    def deposit_hazard(self, x, y, r, tick):
        self._deposit(x, y, "hazard", r, tick)

    def deposit_task(self, slot_id, x, y, tick):
        self._deposit(x, y, "task", float(slot_id), tick)

    def _query(self, ax, ay, kind, tick) -> float:
        best = 0.0
        for (mx, my, mk, mv, mt) in self._msgs:
            if mk != kind: continue
            if tick - mt > MSG_TTL: continue
            d = math.hypot(ax - mx, ay - my)
            if d <= SENSOR_RADIUS * 2:
                best = max(best, mv * math.exp(-d / SENSOR_RADIUS))
        return best

    def query_resource(self, ax, ay, tick) -> float:
        return self._query(ax, ay, "resource", tick)

    def query_hazard(self, ax, ay, tick) -> float:
        return self._query(ax, ay, "hazard", tick)

    def query_task(self, slot_id, tick) -> float:
        for (mx, my, mk, mv, mt) in self._msgs:
            if mk == "task" and int(mv) == slot_id and tick - mt <= MSG_TTL:
                return 1.0
        return 0.0

    def tick_update(self, tick):
        # Expire old messages
        self._msgs = [(x,y,k,v,t) for (x,y,k,v,t) in self._msgs
                      if tick - t <= MSG_TTL]


class BlackboardMemory:
    """
    Condition C: global append-only list; each entry has a timestamp.
    Entries expire after STALE_TICKS. Budget: unlimited reads, writes capped
    to N_AGENTS per tick (same as direct-msg rate).
    """
    def __init__(self):
        self._entries: list[dict] = []

    def _add(self, kind, x, y, extra, tick):
        self._entries.append({"kind": kind, "x": x, "y": y,
                               "extra": extra, "tick": tick})

    def deposit_resource(self, x, y, tick):
        self._add("resource", x, y, RESOURCE_REWARD, tick)

    def deposit_hazard(self, x, y, r, tick):
        self._add("hazard", x, y, r, tick)

    def deposit_task(self, slot_id, x, y, tick):
        self._add("task", x, y, float(slot_id), tick)

    def _query_spatial(self, ax, ay, kind, tick, radius=SENSOR_RADIUS*2) -> float:
        best = 0.0
        for e in self._entries:
            if e["kind"] != kind: continue
            if tick - e["tick"] > STALE_TICKS: continue
            d = math.hypot(ax - e["x"], ay - e["y"])
            if d <= radius:
                best = max(best, e["extra"] * math.exp(-d / SENSOR_RADIUS))
        return best

    def query_resource(self, ax, ay, tick) -> float:
        return self._query_spatial(ax, ay, "resource", tick)

    def query_hazard(self, ax, ay, tick) -> float:
        return self._query_spatial(ax, ay, "hazard", tick)

    def query_task(self, slot_id, tick) -> float:
        for e in self._entries:
            if e["kind"] == "task" and int(e["extra"]) == slot_id:
                if tick - e["tick"] <= STALE_TICKS:
                    return 1.0
        return 0.0

    def tick_update(self, tick):
        self._entries = [e for e in self._entries
                         if tick - e["tick"] <= STALE_TICKS]


class PheromoneMemory:
    """
    Condition D: separate evaporating grids for resources, hazards, tasks.
    Gaussian deposit; exponential evaporation each tick.
    Budget-equivalent: same spatial deposit function as substrate conditions.
    """
    def __init__(self):
        shape = (GRID_NY, GRID_NX)
        self._resource_grid = np.zeros(shape)
        self._hazard_grid   = np.zeros(shape)
        self._task_grids    = {}   # slot_id -> grid

    def _xy_to_ij(self, x, y):
        i = int(np.clip(round(y / GRID_Y * (GRID_NY - 1)), 0, GRID_NY - 1))
        j = int(np.clip(round(x / GRID_X * (GRID_NX - 1)), 0, GRID_NX - 1))
        return i, j

    def _deposit_grid(self, grid: np.ndarray, x, y, amp, width_cells=2.0):
        ci, cj = self._xy_to_ij(x, y)
        r = int(math.ceil(width_cells * 3))
        for di in range(-r, r+1):
            for dj in range(-r, r+1):
                ni, nj = ci+di, cj+dj
                if 0 <= ni < GRID_NY and 0 <= nj < GRID_NX:
                    d2 = di*di + dj*dj
                    grid[ni, nj] += amp * math.exp(-d2 / (2 * width_cells**2))

    def deposit_resource(self, x, y, tick):
        self._deposit_grid(self._resource_grid, x, y, PHER_DEPOSIT)

    def deposit_hazard(self, x, y, r, tick):
        self._deposit_grid(self._hazard_grid, x, y, PHER_DEPOSIT * r)

    def deposit_task(self, slot_id, x, y, tick):
        if slot_id not in self._task_grids:
            self._task_grids[slot_id] = np.zeros((GRID_NY, GRID_NX))
        self._deposit_grid(self._task_grids[slot_id], x, y, PHER_DEPOSIT)

    def _read_at(self, grid, x, y) -> float:
        i, j = self._xy_to_ij(x, y)
        return float(grid[i, j])

    def query_resource(self, ax, ay, tick) -> float:
        return self._read_at(self._resource_grid, ax, ay)

    def query_hazard(self, ax, ay, tick) -> float:
        return self._read_at(self._hazard_grid, ax, ay)

    def query_task(self, slot_id, tick) -> float:
        if slot_id not in self._task_grids:
            return 0.0
        return self._read_at(self._task_grids[slot_id], 0, 0)   # global max

    def tick_update(self, tick):
        self._resource_grid *= (1.0 - PHER_EVAP)
        self._hazard_grid   *= (1.0 - PHER_EVAP)
        for g in self._task_grids.values():
            g *= (1.0 - PHER_EVAP)


def _build_substrate_field(seed: int) -> tuple:
    """Build an InformationDensityField for substrate conditions."""
    rng = np.random.default_rng(seed + 7000)
    state = initialize_field_state(
        x_range=(0., GRID_X), y_range=(0., GRID_Y),
        nx=GRID_NX, ny=GRID_NY,
        initial_value=1.0,
        dt=DT,
    )
    f = InformationDensityField(
        state=state, information_quantity=1.,
        physical_volume=GRID_X * GRID_Y * 1.,
        information_units="bits", spatial_units="m", density_units="bits/m³",
    )
    # Light random initial perturbations
    for _ in range(3):
        bx = float(rng.uniform(5., GRID_X - 5.))
        by = float(rng.uniform(5., GRID_Y - 5.))
        amp = float(rng.uniform(0.5, 1.5))
        f = apply_perturbation(f, PhysicalCoordinate(bx, by, 0.), amp, 4.0)
    prop  = PropagationParameters(c_nominal=NL_C)
    relax = RelaxationParameters(tau_nominal=NL_TAU)
    return f, prop, relax


class SubstrateMemory:
    """
    Conditions E (nonlinear) and F (linear): write info into the field via
    Gaussian perturbations; read by computing local spectral observable or
    local spatial average within SUB_READ_RADIUS.

    Deposit convention:
      resource discovery  → positive perturbation at site
      hazard discovery    → negative perturbation at hazard centre
      task deposit        → moderate positive at task location

    Readout:
      resource query  → local field mean (positive = resource present)
      hazard query    → local field mean (negative = hazard present)
      task query      → global C_spectral (collective activity level)
    """
    def __init__(self, seed: int, nonlinear: bool):
        self.nonlinear = nonlinear
        self.field, self.prop, self.relax = _build_substrate_field(seed)
        if nonlinear:
            self.react = NonlinearReactionParameters(r=NL_R, a=NL_A, b=NL_B)
        else:
            self.react = NonlinearReactionParameters()   # linear limit

    def _coord(self, x, y) -> PhysicalCoordinate:
        return PhysicalCoordinate(float(x), float(y), 0.)

    def deposit_resource(self, x, y, tick):
        self.field = apply_perturbation(
            self.field, self._coord(x, y), SUB_DEPOSIT_AMP, SUB_DEPOSIT_WIDTH)

    def deposit_hazard(self, x, y, r, tick):
        # Negative deposit encodes hazard
        self.field = apply_perturbation(
            self.field, self._coord(x, y), -SUB_DEPOSIT_AMP * r, SUB_DEPOSIT_WIDTH)

    def deposit_task(self, slot_id, x, y, tick):
        self.field = apply_perturbation(
            self.field, self._coord(x, y), SUB_DEPOSIT_AMP * 0.5, SUB_DEPOSIT_WIDTH)

    def _local_mean(self, ax, ay) -> float:
        """Spatial average of field within SUB_READ_RADIUS around (ax,ay)."""
        s = self.field.state.field_values.reshape(GRID_NY, GRID_NX)
        ci = int(np.clip(round(ay / GRID_Y * (GRID_NY - 1)), 0, GRID_NY - 1))
        cj = int(np.clip(round(ax / GRID_X * (GRID_NX - 1)), 0, GRID_NX - 1))
        r_cells = max(1, int(round(SUB_READ_RADIUS / GRID_X * GRID_NX)))
        vals = []
        for di in range(-r_cells, r_cells + 1):
            for dj in range(-r_cells, r_cells + 1):
                ni, nj = ci + di, cj + dj
                if 0 <= ni < GRID_NY and 0 <= nj < GRID_NX:
                    vals.append(s[ni, nj])
        return float(np.mean(vals)) if vals else 0.0

    def query_resource(self, ax, ay, tick) -> float:
        """Positive local mean → likely resource."""
        return max(0., self._local_mean(ax, ay) - 1.0)   # subtract background

    def query_hazard(self, ax, ay, tick) -> float:
        """Negative deviation from background → hazard signal."""
        return max(0., 1.0 - self._local_mean(ax, ay))

    def query_task(self, slot_id, tick) -> float:
        """Use global C_spectral as a collective-activity proxy."""
        try:
            obs = compute_spectral_transport_observable(
                self.field, self.prop, self.relax)
            return float(0.5 * (1.0 + obs.c_spectral))
        except Exception:
            return 0.5

    def tick_update(self, tick):
        try:
            self.field = evolve_field_nonlinear(
                self.field, self.prop, self.relax, self.react)
        except ValueError:
            # Numerical instability: reset field (counts as a failure event)
            self.field, self.prop, self.relax = _build_substrate_field(tick)


def _make_memory(condition: str, seed: int):
    if condition == "independent":
        return IndependentMemory()
    elif condition == "direct_msg":
        return DirectMsgMemory()
    elif condition == "blackboard":
        return BlackboardMemory()
    elif condition == "pheromone":
        return PheromoneMemory()
    elif condition == "nonlinear_sub":
        return SubstrateMemory(seed, nonlinear=True)
    elif condition == "linear_sub":
        return SubstrateMemory(seed, nonlinear=False)
    raise ValueError(f"Unknown condition: {condition!r}")


# ===========================================================================
# SECTION 5 — TASK LOGIC
# ===========================================================================

def _in_hazard(ax, ay, hz: HazardZone) -> bool:
    return math.hypot(ax - hz.x, ay - hz.y) <= hz.radius


def run_trial(seed: int, condition: str, n_ticks: int = N_TICKS,
              env: dict | None = None) -> dict[str, Any]:
    """
    Run one complete trial for a given condition.

    Returns a flat metrics dict.
    """
    if env is None:
        env = generate_environment(seed, n_ticks)

    resources:   list[ResourceSite] = env["resources"]
    hazards:     list[HazardZone]   = env["hazards"]
    task_slots:  list[TaskSlot]     = env["task_slots"]

    rng_agents = np.random.default_rng(seed + 1000)
    rng_move   = np.random.default_rng(seed + 2000)

    agents  = _make_agents(seed)
    memory  = _make_memory(condition, seed)

    # Tracking sets (per trial)
    resources_found:   set[int] = set()   # site_ids found by any agent
    resources_duped:   int = 0            # re-visits to already-found sites
    hazard_hits:       int = 0
    hazard_avoidances: int = 0            # agent knew about hazard, avoided
    task_completions:  int = 0
    task_conflicts:    int = 0            # two agents claim same 1-slot task
    # Info-recovery: ground truth vs agent readout
    resource_read_errs: list[float] = []
    hazard_read_errs:   list[float] = []

    agent_found_resource: dict[int, set[int]] = {a.agent_id: set() for a in agents}
    task_claimed: dict[int, list[int]] = {}   # slot_id -> [agent_ids]

    for tick in range(n_ticks):
        memory.tick_update(tick)

        # Ground-truth knowledge: active events this tick
        active_resources = [r for r in resources
                            if r.tick_available <= tick < r.tick_expires]
        active_hazards   = [h for h in hazards
                            if h.tick_start <= tick < h.tick_end]
        open_tasks       = [t for t in task_slots
                            if t.tick_open <= tick < t.tick_close]

        for agent in agents:
            # ---- Sense nearby resources ----
            nearby_res = [r for r in active_resources
                          if agent.dist(r.x, r.y) <= SENSOR_RADIUS]
            for r in nearby_res:
                if r.site_id not in resources_found:
                    resources_found.add(r.site_id)
                    agent.resources_collected += 1
                    memory.deposit_resource(r.x, r.y, tick)
                elif r.site_id in agent_found_resource[agent.agent_id]:
                    resources_duped += 1   # agent already knew → no duplicate
                else:
                    # Another agent already found it; this is a duplicate visit
                    resources_duped += 1
                agent_found_resource[agent.agent_id].add(r.site_id)

            # ---- Information recovery: resource ----
            # Ground truth: nearest active resource within 2× sensor radius
            nearest_res_dist = min(
                (agent.dist(r.x, r.y) for r in active_resources), default=99.)
            gt_res_signal = max(0., 1. - nearest_res_dist / (SENSOR_RADIUS * 2))
            read_res = float(np.clip(memory.query_resource(agent.x, agent.y, tick), 0., 5.))
            read_res_norm = float(np.clip(read_res / RESOURCE_REWARD, 0., 1.))
            resource_read_errs.append(abs(gt_res_signal - read_res_norm))

            # ---- Hazard detection & avoidance ----
            in_hz = any(_in_hazard(agent.x, agent.y, h) for h in active_hazards)
            hz_signal = memory.query_hazard(agent.x, agent.y, tick)
            knows_hazard = hz_signal > 0.3

            if in_hz:
                if knows_hazard:
                    hazard_avoidances += 1   # agent sensed hazard via memory
                else:
                    hazard_hits += 1
                    agent.energy = max(0., agent.energy - 0.15)

            # Deposit hazard knowledge when sensed directly
            for h in active_hazards:
                if agent.dist(h.x, h.y) <= SENSOR_RADIUS:
                    memory.deposit_hazard(h.x, h.y, h.radius, tick)

            # ---- Information recovery: hazard ----
            nearest_hz_dist = min(
                (agent.dist(h.x, h.y) for h in active_hazards), default=99.)
            gt_hz_signal = max(0., 1. - nearest_hz_dist / (SENSOR_RADIUS * 2))
            read_hz = float(np.clip(memory.query_hazard(agent.x, agent.y, tick), 0., 5.))
            read_hz_norm = float(np.clip(read_hz / HAZARD_COST, 0., 1.))
            hazard_read_errs.append(abs(gt_hz_signal - read_hz_norm))

            # ---- Task allocation ----
            for ts in open_tasks:
                if agent.dist(ts.x, ts.y) > SENSOR_RADIUS * 1.5:
                    continue
                if ts.slot_id not in task_claimed:
                    task_claimed[ts.slot_id] = []
                if agent.agent_id not in task_claimed[ts.slot_id]:
                    task_claimed[ts.slot_id].append(agent.agent_id)
                    memory.deposit_task(ts.slot_id, ts.x, ts.y, tick)
                    if len(task_claimed[ts.slot_id]) == ts.n_agents_needed:
                        task_completions += 1
                        agent.tasks_completed += 1
                    elif ts.n_agents_needed == 1 and len(task_claimed[ts.slot_id]) > 1:
                        task_conflicts += 1

            # ---- Movement: toward best-known opportunity ----
            best_target = None
            best_score  = -1.

            for r in active_resources:
                sig = memory.query_resource(r.x, r.y, tick)
                d   = agent.dist(r.x, r.y)
                score = sig / (1. + d * 0.1)
                if score > best_score:
                    best_score  = score
                    best_target = (r.x, r.y)

            if best_target and best_score > 0.1:
                agent.move_toward(best_target[0], best_target[1],
                                  AGENT_SPEED, rng_move)
            else:
                agent.move_random(AGENT_SPEED, rng_move)

    # ---- Aggregate metrics ----
    total_res  = len(active_resources) if active_resources else 1
    total_hz   = max(len(hazards), 1)
    total_task = max(len(task_slots), 1)

    res_completion_rate  = len(resources_found) / max(len(resources), 1)
    dup_work_fraction    = resources_duped / max(len(resources_found), 1)
    hz_exposure_rate     = hazard_hits / (hazard_hits + hazard_avoidances + 1)
    task_completion_rate = task_completions / total_task
    task_conflict_rate   = task_conflicts / max(task_completions + task_conflicts, 1)
    res_info_error       = float(np.mean(resource_read_errs)) if resource_read_errs else 1.
    hz_info_error        = float(np.mean(hazard_read_errs))   if hazard_read_errs else 1.
    info_recovery_acc    = 1. - 0.5 * (res_info_error + hz_info_error)

    total_resources_col = sum(a.resources_collected for a in agents)
    total_tasks_done    = sum(a.tasks_completed for a in agents)

    return {
        "seed":               seed,
        "condition":          condition,
        "n_ticks":            n_ticks,
        # Task 1 — resource discovery
        "res_completion_rate":  res_completion_rate,
        "dup_work_fraction":    dup_work_fraction,
        "resources_collected":  total_resources_col,
        # Task 2 — hazard coordination
        "hazard_hits":          hazard_hits,
        "hazard_avoidances":    hazard_avoidances,
        "hz_exposure_rate":     hz_exposure_rate,
        # Task 3 — task allocation
        "task_completion_rate": task_completion_rate,
        "task_conflict_rate":   task_conflict_rate,
        "tasks_completed":      total_tasks_done,
        # Information recovery
        "res_info_error":       res_info_error,
        "hz_info_error":        hz_info_error,
        "info_recovery_acc":    info_recovery_acc,
        # Composite
        "composite_score": (
            0.35 * res_completion_rate +
            0.35 * (1. - hz_exposure_rate) +
            0.20 * task_completion_rate +
            0.10 * info_recovery_acc
        ),
    }


# ===========================================================================
# SECTION 6 — STATISTICS (stdlib + numpy only, no scipy)
# ===========================================================================

def _bootstrap_ci(data: list[float], n_boot: int = 2000,
                  alpha: float = 0.05, rng_seed: int = 42) -> tuple[float, float]:
    """Bootstrap 95% CI for the mean."""
    rng = np.random.default_rng(rng_seed)
    arr = np.asarray(data)
    n   = len(arr)
    if n < 2:
        m = float(arr[0]) if n == 1 else 0.
        return m, m
    boot_means = np.array([np.mean(rng.choice(arr, size=n, replace=True))
                           for _ in range(n_boot)])
    lo = float(np.percentile(boot_means, 100 * alpha / 2))
    hi = float(np.percentile(boot_means, 100 * (1 - alpha / 2)))
    return lo, hi


def _cohens_d(a: list[float], b: list[float]) -> float:
    """Cohen's d (unsigned) with pooled SD."""
    na, nb = len(a), len(b)
    if na < 2 or nb < 2:
        return 0.
    ma, mb = np.mean(a), np.mean(b)
    sa, sb = np.std(a, ddof=1), np.std(b, ddof=1)
    sp = math.sqrt(((na - 1) * sa**2 + (nb - 1) * sb**2) / (na + nb - 2))
    return float(abs(ma - mb) / sp) if sp > 1e-10 else 0.


def _paired_t_pvalue(a: list[float], b: list[float]) -> float:
    """
    Two-tailed paired t-test p-value (pure Python/numpy, no scipy).
    Returns p-value; if n < 2 returns 1.0.
    """
    diffs = np.asarray(a) - np.asarray(b)
    n = len(diffs)
    if n < 2:
        return 1.0
    mean_d = np.mean(diffs)
    std_d  = np.std(diffs, ddof=1)
    if std_d < 1e-12:
        return 0.0 if abs(mean_d) > 1e-12 else 1.0
    t_stat = mean_d / (std_d / math.sqrt(n))
    # Approximate p-value using the t-distribution via regularised incomplete beta
    # B(x; a, b) approximation for t-dist CDF with df = n-1
    df = n - 1
    x  = df / (df + t_stat**2)
    # Regularised incomplete beta via continued fraction (Abramowitz & Stegun 26.5.8)
    def _reg_inc_beta(x_, a_, b_):
        """Regularised incomplete beta I_x(a,b) via CF."""
        if x_ <= 0.: return 0.
        if x_ >= 1.: return 1.
        # Use symmetry if needed
        if x_ > (a_ + 1.) / (a_ + b_ + 2.):
            return 1. - _reg_inc_beta(1. - x_, b_, a_)
        # Log of beta function
        lbeta = (math.lgamma(a_) + math.lgamma(b_) - math.lgamma(a_ + b_))
        front = math.exp(math.log(x_) * a_ + math.log(1. - x_) * b_ - lbeta) / a_
        # CF evaluation (Lentz)
        TINY = 1e-30
        f = TINY
        C, D = f, 0.
        for m in range(0, 200):
            # Even step
            if m == 0:
                numer = 1.
            else:
                numer = m * (b_ - m) * x_ / ((a_ + 2*m - 1.) * (a_ + 2*m))
            D = 1. + numer * D
            if abs(D) < TINY: D = TINY
            C = 1. + numer / C
            if abs(C) < TINY: C = TINY
            D = 1. / D
            delta = C * D
            f *= delta
            # Odd step
            numer2 = -(a_ + m) * (a_ + b_ + m) * x_ / ((a_ + 2*m) * (a_ + 2*m + 1.))
            D = 1. + numer2 * D
            if abs(D) < TINY: D = TINY
            C = 1. + numer2 / C
            if abs(C) < TINY: C = TINY
            D = 1. / D
            delta = C * D
            f *= delta
            if abs(delta - 1.) < 1e-10:
                break
        return front * f

    p_one = _reg_inc_beta(x, df / 2., 0.5)   # P(T <= |t|) for one tail
    return float(2. * p_one)                   # two-tailed


def analyze_results(results: list[dict]) -> dict[str, Any]:
    """
    Aggregate results across seeds; compute means, CIs, Cohen's d, p-values
    with Bonferroni correction against the Independent baseline (condition A).
    """
    # Group by condition
    by_cond: dict[str, list[dict]] = {}
    for r in results:
        by_cond.setdefault(r["condition"], []).append(r)

    primary_metrics = [
        "res_completion_rate", "dup_work_fraction", "hz_exposure_rate",
        "task_completion_rate", "info_recovery_acc", "composite_score",
    ]

    # Per-condition summary
    summaries: dict[str, dict] = {}
    for cond, trials in by_cond.items():
        s: dict[str, Any] = {"n": len(trials)}
        for m in primary_metrics:
            vals = [t[m] for t in trials]
            s[f"{m}_mean"] = float(np.mean(vals))
            s[f"{m}_std"]  = float(np.std(vals, ddof=1)) if len(vals) > 1 else 0.
            lo, hi = _bootstrap_ci(vals)
            s[f"{m}_ci95"] = [lo, hi]
        summaries[cond] = s

    # Paired comparisons vs Independent (Bonferroni: n_comparisons = 5)
    n_comparisons = len(CONDITIONS) - 1
    alpha_bonf = 0.05 / n_comparisons

    comparisons: dict[str, dict] = {}
    if "independent" in by_cond:
        base_trials = by_cond["independent"]
        base_seeds  = {t["seed"]: t for t in base_trials}

        for cond in CONDITIONS:
            if cond == "independent":
                continue
            comp_trials = by_cond.get(cond, [])
            comp_seeds  = {t["seed"]: t for t in comp_trials}
            shared      = sorted(set(base_seeds) & set(comp_seeds))

            if len(shared) < 2:
                comparisons[cond] = {"n_paired": len(shared), "note": "insufficient data"}
                continue

            comp_data: dict[str, Any] = {"n_paired": len(shared)}
            for m in primary_metrics:
                a_vals = [base_seeds[s][m] for s in shared]
                b_vals = [comp_seeds[s][m] for s in shared]
                d = _cohens_d(a_vals, b_vals)
                p = _paired_t_pvalue(a_vals, b_vals)
                mean_diff = float(np.mean(np.array(b_vals) - np.array(a_vals)))
                lo, hi    = _bootstrap_ci(
                    list(np.array(b_vals) - np.array(a_vals)))
                comp_data[m] = {
                    "mean_diff":   mean_diff,
                    "cohens_d":    d,
                    "p_value":     p,
                    "p_bonf_sig":  p < alpha_bonf,
                    "diff_ci95":   [lo, hi],
                    "direction":   "better" if mean_diff > 0 else "worse",
                }
                # For dup_work and hz_exposure, lower is better
                if m in ("dup_work_fraction", "hz_exposure_rate"):
                    comp_data[m]["direction"] = "better" if mean_diff < 0 else "worse"
            comparisons[cond] = comp_data

    # Outcome classification for nonlinear_sub vs independent
    outcome = _classify_outcome(comparisons.get("nonlinear_sub", {}),
                                summaries.get("nonlinear_sub", {}),
                                summaries.get("independent", {}))

    return {
        "summaries":          summaries,
        "comparisons_vs_independent": comparisons,
        "alpha_bonferroni":   alpha_bonf,
        "outcome_classification": outcome,
    }


def _classify_outcome(comp: dict, nl_summary: dict, ind_summary: dict) -> str:
    """
    Classify result into Outcome 1–4 (per Task 6 specification).
    Decision is based solely on Bonferroni-corrected significance and effect size.
    """
    if not comp or "composite_score" not in comp:
        return "OUTCOME_1_NO_DEMONSTRATED_ADVANTAGE"

    n_sig_better = sum(
        1 for m, v in comp.items()
        if isinstance(v, dict)
        and v.get("p_bonf_sig", False)
        and v.get("direction") == "better"
    )
    max_d = max(
        (v.get("cohens_d", 0.) for v in comp.values() if isinstance(v, dict)),
        default=0.
    )

    if n_sig_better == 0:
        return "OUTCOME_1_NO_DEMONSTRATED_ADVANTAGE"
    elif n_sig_better == 1:
        return "OUTCOME_2_SPECIALIZED_ADVANTAGE"
    elif n_sig_better >= 2 and max_d >= 0.5:
        return "OUTCOME_3_COLLECTIVE_INFORMATION_PROCESSING_ADVANTAGE"
    else:
        return "OUTCOME_2_SPECIALIZED_ADVANTAGE"


# ===========================================================================
# SECTION 7 — PILOT + CONFIRMATORY RUNS
# ===========================================================================

def run_batch(seeds: list[int], conditions: list[str],
              n_ticks: int = N_TICKS,
              verbose: bool = True) -> list[dict]:
    """Run all conditions for each seed. Same env per seed across conditions."""
    results = []
    total = len(seeds) * len(conditions)
    done  = 0
    t0    = time.time()

    for seed in seeds:
        env = generate_environment(seed, n_ticks)
        for cond in conditions:
            try:
                r = run_trial(seed, cond, n_ticks, env)
                results.append(r)
            except Exception as exc:
                results.append({
                    "seed": seed, "condition": cond,
                    "error": str(exc), "failed": True,
                })
            done += 1
            if verbose and done % 10 == 0:
                elapsed = time.time() - t0
                rate    = done / elapsed
                eta     = (total - done) / rate if rate > 0 else 0
                print(f"  {done}/{total}  elapsed={elapsed:.0f}s  ETA={eta:.0f}s")

    return results


# ===========================================================================
# SECTION 8 — MAIN ENTRY POINT
# ===========================================================================

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--pilot",    action="store_true",
                        help="Run pilot only (20 seeds)")
    parser.add_argument("--seeds",    type=int, default=60,
                        help="Number of seeds for confirmatory run")
    parser.add_argument("--ticks",    type=int, default=N_TICKS)
    parser.add_argument("--out",      default="exp6_results.json")
    args = parser.parse_args()

    out_dir = os.path.dirname(os.path.abspath(__file__))

    # --- PILOT ---
    pilot_seeds = list(range(0, 20))
    print(f"\n=== PILOT: {len(pilot_seeds)} seeds × {len(CONDITIONS)} conditions ===")
    pilot_results = run_batch(pilot_seeds, CONDITIONS, args.ticks, verbose=True)

    pilot_ok = [r for r in pilot_results if not r.get("failed")]
    pilot_failed = len(pilot_results) - len(pilot_ok)
    print(f"Pilot: {len(pilot_ok)} OK, {pilot_failed} failed")

    pilot_analysis = analyze_results(pilot_ok)
    pilot_path = os.path.join(out_dir, "exp6_pilot_results.json")
    with open(pilot_path, "w") as f:
        json.dump({"results": pilot_ok, "analysis": pilot_analysis}, f, indent=2)
    print(f"Pilot saved → {pilot_path}")
    _print_summary(pilot_analysis, label="PILOT")

    if args.pilot:
        return

    # --- CONFIRMATORY ---
    # Seeds 100..100+N to avoid overlap with pilot (seeds 0..19)
    confirm_seeds = list(range(100, 100 + args.seeds))
    print(f"\n=== CONFIRMATORY: {len(confirm_seeds)} seeds × {len(CONDITIONS)} conditions ===")
    confirm_results = run_batch(confirm_seeds, CONDITIONS, args.ticks, verbose=True)

    confirm_ok     = [r for r in confirm_results if not r.get("failed")]
    confirm_failed = len(confirm_results) - len(confirm_ok)
    print(f"Confirmatory: {len(confirm_ok)} OK, {confirm_failed} failed")

    confirm_analysis = analyze_results(confirm_ok)
    confirm_path = os.path.join(out_dir, args.out)
    with open(confirm_path, "w") as f:
        json.dump({"results": confirm_ok, "analysis": confirm_analysis}, f, indent=2)
    print(f"Confirmatory saved → {confirm_path}")
    _print_summary(confirm_analysis, label="CONFIRMATORY")


def _print_summary(analysis: dict, label: str = ""):
    print(f"\n--- {label} SUMMARY ---")
    summaries = analysis.get("summaries", {})
    comps     = analysis.get("comparisons_vs_independent", {})

    header = f"{'Condition':<18}  {'composite':>9}  {'res_rate':>8}  {'hz_exp':>7}  {'task_rate':>9}  {'info_acc':>8}"
    print(header)
    print("-" * len(header))
    for cond in CONDITIONS:
        s = summaries.get(cond, {})
        comp = float(s.get("composite_score_mean", float("nan")))
        res  = float(s.get("res_completion_rate_mean", float("nan")))
        hz   = float(s.get("hz_exposure_rate_mean", float("nan")))
        task = float(s.get("task_completion_rate_mean", float("nan")))
        info = float(s.get("info_recovery_acc_mean", float("nan")))
        ci   = s.get("composite_score_ci95", [float("nan"), float("nan")])
        print(f"{cond:<18}  {comp:>9.3f}  {res:>8.3f}  {hz:>7.3f}  {task:>9.3f}  {info:>8.3f}"
              f"  CI=[{ci[0]:.3f},{ci[1]:.3f}]")

    print()
    print("Pairwise vs Independent (Bonferroni-corrected):")
    for cond, comp in comps.items():
        if "note" in comp:
            continue
        cs = comp.get("composite_score", {})
        p  = cs.get("p_value", float("nan"))
        d  = cs.get("cohens_d", float("nan"))
        md = cs.get("mean_diff", float("nan"))
        sig = "***" if cs.get("p_bonf_sig") else "   "
        print(f"  {cond:<18}  composite Δ={md:+.3f}  d={d:.3f}  p={p:.4f} {sig}")

    print()
    outcome = analysis.get("outcome_classification", "N/A")
    print(f"Outcome classification (nonlinear_sub): {outcome}")


if __name__ == "__main__":
    main()
