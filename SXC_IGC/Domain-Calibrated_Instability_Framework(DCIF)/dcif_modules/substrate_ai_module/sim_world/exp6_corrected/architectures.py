"""Architecture-specific information pathways for corrected Task 6.

Critical constraints enforced here:
  C1–C4: no ground-truth coordinate access in agent decision APIs
  C3/C12: no shared task-claim oracle
  C6/C8: matched low-basin IC for linear and nonlinear substrates
  C10: solver failures recorded; no silent reset into success
  C11: each condition exposes a distinct deposit/query interface
"""
from __future__ import annotations

import math
import os
import sys
from dataclasses import dataclass, field
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
from sim_world.exp6_corrected import config as cfg


# ---------------------------------------------------------------------------
# Cost / usage accounting (fairness documentation)
# ---------------------------------------------------------------------------

@dataclass
class UsageStats:
    writes: int = 0
    reads: int = 0
    messages_sent: int = 0
    message_payload_bytes: int = 0
    solver_steps: int = 0
    solver_failures: int = 0
    solver_error_log: list = field(default_factory=list)
    channel_cells: int = 0

    def to_dict(self) -> dict[str, Any]:
        return {
            "writes": self.writes,
            "reads": self.reads,
            "messages_sent": self.messages_sent,
            "message_payload_bytes": self.message_payload_bytes,
            "solver_steps": self.solver_steps,
            "solver_failures": self.solver_failures,
            "solver_error_log": list(self.solver_error_log),
            "channel_cells": self.channel_cells,
        }


# ---------------------------------------------------------------------------
# Base interface — agents only ever call these methods
# ---------------------------------------------------------------------------

class MemoryBackend:
    """Common interface. No method may accept or return ground-truth env lists."""

    name: str = "base"

    def deposit(self, kind: str, x: float, y: float, value: float, tick: int,
                meta: Optional[dict] = None) -> None:
        raise NotImplementedError

    def query_at(self, kind: str, x: float, y: float, tick: int) -> float:
        """Read signal of `kind` at agent-chosen coordinates (typically own pose)."""
        raise NotImplementedError

    def list_known(self, kind: str, tick: int) -> list[dict]:
        """
        Structured records visible to this architecture.
        Independent/pheromone/substrate return [] (spatial-only); messaging/
        blackboard return explicit records. Never includes undiscovered GT.
        """
        return []

    def sample_gradient(self, kind: str, x: float, y: float, tick: int,
                        eps: float = 1.5) -> tuple[float, float]:
        """Local spatial gradient estimate from queries at nearby offsets."""
        c = self.query_at(kind, x, y, tick)
        cx = self.query_at(kind, x + eps, y, tick)
        cy = self.query_at(kind, x, y + eps, tick)
        return (cx - c) / eps, (cy - c) / eps

    def tick_update(self, tick: int) -> None:
        pass

    def usage(self) -> UsageStats:
        return UsageStats()

    def failed(self) -> bool:
        return False


# ---------------------------------------------------------------------------
# 1. Independent
# ---------------------------------------------------------------------------

class IndependentMemory(MemoryBackend):
    name = "independent"

    def __init__(self):
        self._stats = UsageStats()
        # Private per-agent caches are held by agents themselves; backend is empty.

    def deposit(self, kind, x, y, value, tick, meta=None):
        self._stats.writes += 1  # counted as local write only; not shared

    def query_at(self, kind, x, y, tick) -> float:
        self._stats.reads += 1
        return 0.0

    def usage(self):
        return self._stats


# ---------------------------------------------------------------------------
# 2. Direct messaging
# ---------------------------------------------------------------------------

class DirectMsgMemory(MemoryBackend):
    name = "direct_msg"

    def __init__(self):
        self._msgs: list[dict] = []
        self._stats = UsageStats()

    def deposit(self, kind, x, y, value, tick, meta=None):
        payload = {"kind": kind, "x": x, "y": y, "value": value,
                   "tick": tick, "meta": meta or {}}
        self._msgs.append(payload)
        self._stats.writes += 1
        self._stats.messages_sent += 1
        self._stats.message_payload_bytes += 32

    def query_at(self, kind, x, y, tick) -> float:
        self._stats.reads += 1
        best = 0.0
        for m in self._msgs:
            if m["kind"] != kind:
                continue
            if tick - m["tick"] > cfg.MSG_TTL:
                continue
            d = math.hypot(x - m["x"], y - m["y"])
            if d <= cfg.SENSOR_RADIUS * 2:
                best = max(best, float(m["value"]) * math.exp(-d / max(cfg.SENSOR_RADIUS, 1e-6)))
        return best

    def list_known(self, kind, tick) -> list[dict]:
        self._stats.reads += 1
        out = []
        for m in self._msgs:
            if m["kind"] == kind and tick - m["tick"] <= cfg.MSG_TTL:
                out.append(dict(m))
        return out

    def tick_update(self, tick):
        self._msgs = [m for m in self._msgs if tick - m["tick"] <= cfg.MSG_TTL]

    def usage(self):
        return self._stats


# ---------------------------------------------------------------------------
# 3. Blackboard
# ---------------------------------------------------------------------------

class BlackboardMemory(MemoryBackend):
    name = "blackboard"

    def __init__(self):
        self._entries: list[dict] = []
        self._stats = UsageStats()

    def deposit(self, kind, x, y, value, tick, meta=None):
        self._entries.append({
            "kind": kind, "x": x, "y": y, "value": value,
            "tick": tick, "meta": meta or {},
        })
        self._stats.writes += 1

    def query_at(self, kind, x, y, tick) -> float:
        self._stats.reads += 1
        best = 0.0
        for e in self._entries:
            if e["kind"] != kind:
                continue
            if tick - e["tick"] > cfg.BB_STALE:
                continue
            d = math.hypot(x - e["x"], y - e["y"])
            if d <= cfg.SENSOR_RADIUS * 3:
                best = max(best, float(e["value"]) * math.exp(-d / max(cfg.SENSOR_RADIUS, 1e-6)))
        return best

    def list_known(self, kind, tick) -> list[dict]:
        self._stats.reads += 1
        return [dict(e) for e in self._entries
                if e["kind"] == kind and tick - e["tick"] <= cfg.BB_STALE]

    def tick_update(self, tick):
        self._entries = [e for e in self._entries if tick - e["tick"] <= cfg.BB_STALE]

    def usage(self):
        return self._stats


# ---------------------------------------------------------------------------
# 4. Digital pheromone
# ---------------------------------------------------------------------------

class PheromoneMemory(MemoryBackend):
    name = "pheromone"

    def __init__(self):
        shape = (cfg.GRID_NX, cfg.GRID_NY)  # g[ix, iy] — matches substrate grid order
        self._grids: dict[str, np.ndarray] = {
            "resource": np.zeros(shape),
            "hazard": np.zeros(shape),
            "task": np.zeros(shape),
            "event": np.zeros(shape),
            "X": np.zeros(shape),
            "Y": np.zeros(shape),
            "claim": np.zeros(shape),
        }
        self._stats = UsageStats(channel_cells=len(self._grids) * shape[0] * shape[1])

    def _xy_to_ixiy(self, x, y):
        """Index into grids shaped (nx, ny) as g[ix, iy]."""
        ix = int(np.clip(round(x / cfg.GRID_X * (cfg.GRID_NX - 1)), 0, cfg.GRID_NX - 1))
        iy = int(np.clip(round(y / cfg.GRID_Y * (cfg.GRID_NY - 1)), 0, cfg.GRID_NY - 1))
        return ix, iy

    def _deposit_grid(self, grid, x, y, amp, width_cells=2.0):
        cix, ciy = self._xy_to_ixiy(x, y)
        r = int(math.ceil(width_cells * 3))
        for dx_ in range(-r, r + 1):
            for dy_ in range(-r, r + 1):
                nix, niy = cix + dx_, ciy + dy_
                if 0 <= nix < cfg.GRID_NX and 0 <= niy < cfg.GRID_NY:
                    d2 = dx_ * dx_ + dy_ * dy_
                    grid[nix, niy] += amp * math.exp(-d2 / (2 * width_cells ** 2))

    def deposit(self, kind, x, y, value, tick, meta=None):
        if kind not in self._grids:
            self._grids[kind] = np.zeros((cfg.GRID_NX, cfg.GRID_NY))
            self._stats.channel_cells = sum(g.size for g in self._grids.values())
        self._deposit_grid(self._grids[kind], x, y, float(value) * cfg.PHER_DEPOSIT)
        self._stats.writes += 1

    def query_at(self, kind, x, y, tick) -> float:
        self._stats.reads += 1
        grid = self._grids.get(kind)
        if grid is None:
            return 0.0
        ix, iy = self._xy_to_ixiy(x, y)
        return float(grid[ix, iy])

    def tick_update(self, tick):
        for g in self._grids.values():
            g *= (1.0 - cfg.PHER_EVAP)

    def usage(self):
        return self._stats


# ---------------------------------------------------------------------------
# 5/6. Linear and nonlinear substrate
# ---------------------------------------------------------------------------

def _build_field() -> tuple[InformationDensityField, PropagationParameters, RelaxationParameters]:
    """Matched IC for linear and nonlinear: low-basin, no random perturbations."""
    state = initialize_field_state(
        x_range=(0.0, cfg.GRID_X), y_range=(0.0, cfg.GRID_Y),
        nx=cfg.GRID_NX, ny=cfg.GRID_NY,
        initial_value=cfg.FIELD_IC,
        dt=cfg.DT,
    )
    f = InformationDensityField(
        state=state, information_quantity=1.0,
        physical_volume=cfg.GRID_X * cfg.GRID_Y,
        information_units="bits", spatial_units="m", density_units="bits/m³",
    )
    return f, PropagationParameters(c_nominal=cfg.NL_C), RelaxationParameters(tau_nominal=cfg.NL_TAU)


class SubstrateMemory(MemoryBackend):
    """Single scalar field. Encoding is kind-tagged only via deposit polarity/amp
    and spatial location; semantic multi-channel is NOT claimed for one scalar.

    Deposit convention (documented):
      resource / event / X / task / claim : positive Gaussian
      hazard / Y (when distinct polarity needed in Exp B): see experiment code
    """

    def __init__(self, nonlinear: bool):
        self.nonlinear = nonlinear
        self.name = "nonlinear_sub" if nonlinear else "linear_sub"
        self.field, self.prop, self.relax = _build_field()
        if nonlinear:
            self.react = NonlinearReactionParameters(r=cfg.NL_R, a=cfg.NL_A, b=cfg.NL_B)
        else:
            self.react = NonlinearReactionParameters(r=0.0, a=0.0, b=0.0)
        self._stats = UsageStats(channel_cells=cfg.GRID_NX * cfg.GRID_NY)
        self._failed = False
        # Kind is NOT separately channelized in the scalar field; deposits share
        # the same medium. Experiments that need X vs Y use spatial separation
        # and/or signed amplitudes, documented at call sites.

    def deposit(self, kind, x, y, value, tick, meta=None):
        if self._failed:
            return
        amp = float(value)
        # Signed kinds
        if kind == "hazard":
            amp = -abs(amp)
        self.field = apply_perturbation(
            self.field, PhysicalCoordinate(float(x), float(y), 0.0),
            amp, cfg.SUB_DEPOSIT_WIDTH,
        )
        self._stats.writes += 1

    def query_at(self, kind, x, y, tick) -> float:
        self._stats.reads += 1
        if self._failed:
            return 0.0
        nx, ny = self.field.state.grid_shape[0], self.field.state.grid_shape[1]
        s = self.field.state.field_values.reshape(nx, ny)  # s[ix, iy]
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
        if kind == "hazard":
            # Hazard encoded as negative deviation from IC≈0 → positive signal if mean<0
            return max(0.0, -mean)
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
            # NO silent reset — trial marked failed

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


def make_memory(condition: str) -> MemoryBackend:
    if condition == "independent":
        return IndependentMemory()
    if condition == "direct_msg":
        return DirectMsgMemory()
    if condition == "blackboard":
        return BlackboardMemory()
    if condition == "pheromone":
        return PheromoneMemory()
    if condition == "linear_sub":
        return SubstrateMemory(nonlinear=False)
    if condition == "nonlinear_sub":
        return SubstrateMemory(nonlinear=True)
    raise ValueError(f"Unknown condition: {condition!r}")


def architecture_fairness_notes() -> dict[str, Any]:
    """Document irreducible differences (C13) rather than pretending identity."""
    return {
        "matched": [
            "agent population", "environment generation rules", "sensor radius",
            "movement speed", "trial duration", "paired seeds",
            "observation opportunities (same sensor model)",
            "substrate IC and perturbations (linear vs nonlinear)",
        ],
        "inherent_differences": {
            "independent": "no shared writes; zero communication cost",
            "direct_msg": f"TTL={cfg.MSG_TTL}; explicit payloads; list_known available",
            "blackboard": f"stale={cfg.BB_STALE}; structured global records; list_known",
            "pheromone": f"multi-grid channels; cells={cfg.GRID_NX*cfg.GRID_NY} per channel; evap={cfg.PHER_EVAP}",
            "linear_sub": "single scalar field; linear telegraph; no bistable persistence",
            "nonlinear_sub": "single scalar field; bistable reaction; same grid/dt as linear",
        },
        "encoding_limitation": (
            "A single scalar substrate cannot provide independent semantic channels "
            "without spatial/amplitude encoding. Multi-channel claims require "
            "demonstrated separable readout; Exp B tests interaction via spatial "
            "relationship, not claimed multi-semantic multiplexing."
        ),
    }
