"""Task 7 memory backends.

Reuses Task 6 MemoryBackend implementations via import (no Task 6 file edits).
Hazard encoding for Track A: positive danger-marker (documented) so bistable
latching is testable — differs from Task 6's negative hazard convention.
"""
from __future__ import annotations

import math
import os
import sys
from typing import Any, Optional

import numpy as np

_HERE = os.path.dirname(os.path.abspath(__file__))
_SIM = os.path.dirname(_HERE)
_PARENT = os.path.dirname(_SIM)
for _p in (_PARENT, _SIM):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from sim_world.domains.physical_field.physical_field_dynamics import (
    initialize_field_state,
    evolve_field_nonlinear,
    apply_perturbation,
)
from sim_world.domains.physical_field.physical_field_models import (
    InformationDensityField,
    PhysicalCoordinate,
    PropagationParameters,
    RelaxationParameters,
    NonlinearReactionParameters,
)
from sim_world.exp6_corrected.architectures import (
    IndependentMemory,
    DirectMsgMemory,
    BlackboardMemory,
    PheromoneMemory,
    MemoryBackend,
    UsageStats,
)
from sim_world.exp7 import config as cfg


class PositiveHazardBlackboard(BlackboardMemory):
    """Blackboard with configurable stale window (Track A vs Track B budgets)."""

    def __init__(self, stale: int | None = None):
        super().__init__()
        self.name = "blackboard"
        self.stale = int(cfg.BB_STALE if stale is None else stale)

    def query_at(self, kind, x, y, tick) -> float:
        self._stats.reads += 1
        best = 0.0
        for e in self._entries:
            if e["kind"] != kind:
                continue
            if tick - e["tick"] > self.stale:
                continue
            d = math.hypot(x - e["x"], y - e["y"])
            if d <= cfg.SENSOR_RADIUS * 4:
                best = max(best, float(e["value"]) * math.exp(-d / max(cfg.SENSOR_RADIUS, 1e-6)))
        return best

    def list_known(self, kind, tick):
        self._stats.reads += 1
        return [dict(e) for e in self._entries
                if e["kind"] == kind and tick - e["tick"] <= self.stale]

    def tick_update(self, tick):
        self._entries = [e for e in self._entries if tick - e["tick"] <= self.stale]


class PositiveHazardDirectMsg(DirectMsgMemory):
    name = "direct_msg"

    def __init__(self, ttl: int | None = None):
        super().__init__()
        self.ttl = int(cfg.MSG_TTL if ttl is None else ttl)

    def tick_update(self, tick):
        self._msgs = [m for m in self._msgs if tick - m["tick"] <= self.ttl]

    def list_known(self, kind, tick):
        self._stats.reads += 1
        return [dict(m) for m in self._msgs
                if m["kind"] == kind and tick - m["tick"] <= self.ttl]

    def query_at(self, kind, x, y, tick) -> float:
        self._stats.reads += 1
        best = 0.0
        for m in self._msgs:
            if m["kind"] != kind:
                continue
            if tick - m["tick"] > self.ttl:
                continue
            d = math.hypot(x - m["x"], y - m["y"])
            if d <= cfg.SENSOR_RADIUS * 3:
                best = max(best, float(m["value"]) * math.exp(-d / max(cfg.SENSOR_RADIUS, 1e-6)))
        return best


class Exp7SubstrateMemory(MemoryBackend):
    """Scalar field with *positive* hazard danger-marker encoding (Exp7 Track A/B).

    Ablation knobs:
      nonlinear: reaction terms on/off
      c: propagation speed (0 disables spatial coupling)
    """

    def __init__(self, nonlinear: bool = True, c: float = cfg.NL_C,
                 r: float | None = None, a: float | None = None, b: float | None = None,
                 name: str | None = None):
        self.nonlinear = nonlinear
        self.name = name or ("nonlinear_sub" if nonlinear else "linear_sub")
        state = initialize_field_state(
            x_range=(0.0, cfg.GRID_X), y_range=(0.0, cfg.GRID_Y),
            nx=cfg.GRID_NX, ny=cfg.GRID_NY,
            initial_value=cfg.FIELD_IC, dt=cfg.DT,
        )
        self.field = InformationDensityField(
            state=state, information_quantity=1.0,
            physical_volume=cfg.GRID_X * cfg.GRID_Y,
            information_units="bits", spatial_units="m", density_units="bits/m³",
        )
        self.prop = PropagationParameters(c_nominal=float(c))
        self.relax = RelaxationParameters(tau_nominal=cfg.NL_TAU)
        if nonlinear:
            self.react = NonlinearReactionParameters(
                r=cfg.NL_R if r is None else r,
                a=cfg.NL_A if a is None else a,
                b=cfg.NL_B if b is None else b,
            )
        else:
            self.react = NonlinearReactionParameters(r=0.0, a=0.0, b=0.0)
        self._stats = UsageStats(channel_cells=cfg.GRID_NX * cfg.GRID_NY)
        self._failed = False

    def deposit(self, kind, x, y, value, tick, meta=None):
        if self._failed:
            return
        # Exp7: all kinds including hazard deposit as signed `value` as given.
        # Callers deposit hazard with positive amp (danger marker).
        self.field = apply_perturbation(
            self.field, PhysicalCoordinate(float(x), float(y), 0.0),
            float(value), cfg.SUB_DEPOSIT_WIDTH,
        )
        self._stats.writes += 1

    def query_at(self, kind, x, y, tick) -> float:
        self._stats.reads += 1
        if self._failed:
            return 0.0
        nx, ny = self.field.state.grid_shape[0], self.field.state.grid_shape[1]
        s = self.field.state.field_values.reshape(nx, ny)
        ix = int(np.clip(round(x / cfg.GRID_X * (nx - 1)), 0, nx - 1))
        iy = int(np.clip(round(y / cfg.GRID_Y * (ny - 1)), 0, ny - 1))
        r_cells = max(1, int(round(cfg.SUB_READ_RADIUS / cfg.GRID_X * nx)))
        vals = []
        for dx_ in range(-r_cells, r_cells + 1):
            for dy_ in range(-r_cells, r_cells + 1):
                nix, niy = ix + dx_, iy + dy_
                if 0 <= nix < nx and 0 <= niy < ny:
                    vals.append(s[nix, niy])
        mean = float(np.mean(vals)) if vals else 0.0
        # Positive danger-marker / event readout
        return max(0.0, mean)

    def tick_update(self, tick):
        if self._failed:
            return
        try:
            self.field = evolve_field_nonlinear(
                self.field, self.prop, self.relax, self.react)
            self._stats.solver_steps += 1
        except ValueError as exc:
            self._failed = True
            self._stats.solver_failures += 1
            self._stats.solver_error_log.append({"tick": tick, "error": str(exc)})

    def usage(self):
        return self._stats

    def failed(self):
        return self._failed

    def field_stats(self) -> dict[str, float]:
        v = self.field.state.field_values
        return {
            "mean": float(np.mean(v)),
            "max": float(np.max(v)),
            "min": float(np.min(v)),
            "frac_high": float(np.mean(v > cfg.HIGH_STATE_THRESH)),
        }

    def local_max(self, x, y, radius: float = 5.0) -> float:
        nx, ny = self.field.state.grid_shape[0], self.field.state.grid_shape[1]
        s = self.field.state.field_values.reshape(nx, ny)
        ix = int(np.clip(round(x / cfg.GRID_X * (nx - 1)), 0, nx - 1))
        iy = int(np.clip(round(y / cfg.GRID_Y * (ny - 1)), 0, ny - 1))
        r = max(1, int(round(radius / cfg.GRID_X * nx)))
        vals = []
        for dx_ in range(-r, r + 1):
            for dy_ in range(-r, r + 1):
                nix, niy = ix + dx_, iy + dy_
                if 0 <= nix < nx and 0 <= niy < ny:
                    vals.append(s[nix, niy])
        return float(np.max(vals)) if vals else 0.0


def make_memory(condition: str, *, track: str = "A") -> MemoryBackend:
    """
    track='A': native TTL/stale (tests persistence under delay).
    track='B': capacity-matched persistence covering AND_EVOLVE_TICKS so
               conventional structured memory is not crippled by TTL alone.
    """
    if track == "B":
        persist = cfg.AND_EVOLVE_TICKS + 10
        msg_ttl, bb_stale = persist, persist
    else:
        msg_ttl, bb_stale = cfg.MSG_TTL, cfg.BB_STALE

    if condition == "independent":
        return IndependentMemory()
    if condition == "direct_msg":
        return PositiveHazardDirectMsg(ttl=msg_ttl)
    if condition == "blackboard":
        return PositiveHazardBlackboard(stale=bb_stale)
    if condition == "pheromone":
        return PheromoneMemory()
    if condition == "linear_sub":
        return Exp7SubstrateMemory(nonlinear=False, name="linear_sub")
    if condition == "nonlinear_sub":
        return Exp7SubstrateMemory(nonlinear=True, name="nonlinear_sub")
    raise ValueError(condition)


def make_ablation(ablation: str) -> MemoryBackend:
    if ablation == "nonlinear_full":
        return Exp7SubstrateMemory(nonlinear=True, name="nonlinear_full")
    if ablation in ("linear_telegraph", "nonlinear_reaction_off"):
        return Exp7SubstrateMemory(nonlinear=False, name=ablation)
    if ablation == "no_propagation":
        return Exp7SubstrateMemory(nonlinear=True, c=0.0, name="no_propagation")
    raise ValueError(ablation)


def fairness_notes() -> dict[str, Any]:
    return {
        "matched": [
            "paired seeds", "corridor geometry", "sensor radius", "agent speed",
            "deposit amplitude schedule", "observation opportunities",
        ],
        "hazard_encoding_exp7": (
            "Positive danger-marker deposits for all architectures. "
            "Differs from Task 6 SubstrateMemory negative hazard convention "
            "so bistable latching of hazard marks is scientifically testable."
        ),
        "inherent_differences": {
            "direct_msg": f"TrackA TTL={cfg.MSG_TTL}; TrackB TTL={cfg.AND_EVOLVE_TICKS + 10}",
            "blackboard": f"TrackA stale={cfg.BB_STALE}; TrackB stale={cfg.AND_EVOLVE_TICKS + 10}",
            "pheromone": f"evap={cfg.PHER_EVAP}; multi-channel grids",
            "linear_sub": "single scalar; no bistable latch",
            "nonlinear_sub": "single scalar; bistable reaction",
        },
        "track_b_fairness": (
            "Structured baselines receive persist window ≥ AND_EVOLVE_TICKS so "
            "T9 is not an artifact of TTL expiry. Spatial media keep native dynamics."
        ),
    }
