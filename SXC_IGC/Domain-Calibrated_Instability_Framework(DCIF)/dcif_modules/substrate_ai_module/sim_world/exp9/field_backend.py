"""Task 9 medium backends — local deposit/read; no GT; no Task 6–8 file edits."""
from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Any, Optional

import numpy as np

from sim_world.domains.physical_field.physical_field_dynamics import (
    initialize_field_state,
    evolve_field_nonlinear,
    compute_laplacian,
    apply_perturbation,
)
from sim_world.domains.physical_field.physical_field_models import (
    InformationDensityField,
    PhysicalCoordinate,
    PropagationParameters,
    RelaxationParameters,
    NonlinearReactionParameters,
    FieldState,
)
from sim_world.exp9 import config as cfg


@dataclass
class UsageStats:
    writes: int = 0
    reads: int = 0
    messages_sent: int = 0
    message_payload_bytes: int = 0
    solver_steps: int = 0
    solver_failures: int = 0
    travel_distance: float = 0.0
    solver_error_log: list = field(default_factory=list)

    def resource_expenditure(self) -> float:
        return (
            cfg.W_WRITE * self.writes
            + cfg.W_READ * self.reads
            + cfg.W_MSG * self.messages_sent
            + cfg.W_TRAVEL * self.travel_distance
            + cfg.W_SOLVER * self.solver_steps
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "writes": self.writes,
            "reads": self.reads,
            "messages_sent": self.messages_sent,
            "message_payload_bytes": self.message_payload_bytes,
            "solver_steps": self.solver_steps,
            "solver_failures": self.solver_failures,
            "travel_distance": float(self.travel_distance),
            "resource_expenditure": float(self.resource_expenditure()),
        }


class MediumBackend:
    name: str = "base"

    def deposit(self, x: float, y: float, amp: float, tick: int) -> None:
        raise NotImplementedError

    def query_at(self, x: float, y: float, tick: int) -> float:
        raise NotImplementedError

    def send_message(self, landmark_id: int, confidence: float, tick: int) -> None:
        pass

    def list_messages(self, tick: int) -> list[dict]:
        return []

    def tick_update(self, tick: int) -> None:
        pass

    def usage(self) -> UsageStats:
        return UsageStats()

    def failed(self) -> bool:
        return False

    def grid_max(self) -> float:
        return 0.0


class IndependentMedium(MediumBackend):
    """No shared channel; query always 0. Agents use private obs only."""

    name = "independent"

    def __init__(self):
        self._stats = UsageStats()

    def deposit(self, x, y, amp, tick):
        self._stats.writes += 1  # counted attempt; no shared effect

    def query_at(self, x, y, tick):
        self._stats.reads += 1
        return 0.0

    def usage(self):
        return self._stats


class DirectMsgMedium(MediumBackend):
    name = "direct_msg"

    def __init__(self, ttl: int | None = None):
        self.ttl = int(cfg.MSG_TTL if ttl is None else ttl)
        self._msgs: list[dict] = []
        self._stats = UsageStats()

    def deposit(self, x, y, amp, tick):
        # Spatial write unused; count as no-op write attempt for budget parity optional
        self._stats.writes += 1

    def query_at(self, x, y, tick):
        self._stats.reads += 1
        return 0.0

    def send_message(self, landmark_id, confidence, tick):
        self._msgs.append({
            "landmark_id": int(landmark_id),
            "confidence": float(confidence),
            "tick": int(tick),
        })
        self._stats.messages_sent += 1
        self._stats.message_payload_bytes += 8

    def list_messages(self, tick):
        self._stats.reads += 1
        return [m for m in self._msgs if tick - m["tick"] <= self.ttl]

    def tick_update(self, tick):
        self._msgs = [m for m in self._msgs if tick - m["tick"] <= self.ttl]

    def usage(self):
        return self._stats


class BlackboardMedium(MediumBackend):
    name = "blackboard"

    def __init__(self, stale: int | None = None):
        self.stale = int(cfg.BB_STALE if stale is None else stale)
        self._entries: list[dict] = []
        self._stats = UsageStats()

    def deposit(self, x, y, amp, tick):
        self._stats.writes += 1

    def query_at(self, x, y, tick):
        self._stats.reads += 1
        return 0.0

    def send_message(self, landmark_id, confidence, tick):
        self._entries.append({
            "landmark_id": int(landmark_id),
            "confidence": float(confidence),
            "tick": int(tick),
        })
        self._stats.messages_sent += 1
        self._stats.message_payload_bytes += 8
        self._stats.writes += 1

    def list_messages(self, tick):
        self._stats.reads += 1
        return [e for e in self._entries if tick - e["tick"] <= self.stale]

    def tick_update(self, tick):
        self._entries = [e for e in self._entries if tick - e["tick"] <= self.stale]

    def usage(self):
        return self._stats


class PheromoneMedium(MediumBackend):
    name = "pheromone"

    def __init__(self):
        self._grid = np.zeros((cfg.GRID_NX, cfg.GRID_NY))
        self._stats = UsageStats()

    def _ixiy(self, x, y):
        ix = int(np.clip(round(x / cfg.GRID_X * (cfg.GRID_NX - 1)), 0, cfg.GRID_NX - 1))
        iy = int(np.clip(round(y / cfg.GRID_Y * (cfg.GRID_NY - 1)), 0, cfg.GRID_NY - 1))
        return ix, iy

    def deposit(self, x, y, amp, tick):
        cix, ciy = self._ixiy(x, y)
        w = 2.0
        r = int(math.ceil(w * 3))
        for dx in range(-r, r + 1):
            for dy in range(-r, r + 1):
                nix, niy = cix + dx, ciy + dy
                if 0 <= nix < cfg.GRID_NX and 0 <= niy < cfg.GRID_NY:
                    self._grid[nix, niy] += float(amp) * cfg.PHER_DEPOSIT * math.exp(
                        -(dx * dx + dy * dy) / (2 * w * w)
                    )
        self._stats.writes += 1

    def query_at(self, x, y, tick):
        self._stats.reads += 1
        ix, iy = self._ixiy(x, y)
        # local max in read radius
        r = max(1, int(round(cfg.READ_RADIUS / cfg.GRID_X * cfg.GRID_NX)))
        vals = []
        for dx in range(-r, r + 1):
            for dy in range(-r, r + 1):
                nix, niy = ix + dx, iy + dy
                if 0 <= nix < cfg.GRID_NX and 0 <= niy < cfg.GRID_NY:
                    vals.append(self._grid[nix, niy])
        return float(np.max(vals)) if vals else 0.0

    def tick_update(self, tick):
        self._grid *= (1.0 - cfg.PHER_EVAP)

    def grid_max(self):
        return float(np.max(self._grid))

    def usage(self):
        return self._stats


class SubstrateMedium(MediumBackend):
    """Nonlinear / linear / ablated reaction-telegraph field."""

    def __init__(
        self,
        ablation: str = "nonlinear_full",
        *,
        name: str | None = None,
        allow_deposit: bool = True,
        allow_readout: bool = True,
        nx: int | None = None,
        ny: int | None = None,
        dt: float | None = None,
        c: float | None = None,
    ):
        self.ablation = ablation
        self.allow_deposit = allow_deposit
        self.allow_readout = allow_readout
        self.name = name or ablation
        self._stats = UsageStats()
        self._failed = False

        nx = cfg.GRID_NX if nx is None else nx
        ny = cfg.GRID_NY if ny is None else ny
        dt = cfg.DT if dt is None else dt
        state = initialize_field_state(
            x_range=(0.0, cfg.GRID_X), y_range=(0.0, cfg.GRID_Y),
            nx=nx, ny=ny, initial_value=cfg.FIELD_IC, dt=dt,
        )
        self.field = InformationDensityField(
            state=state, information_quantity=1.0,
            physical_volume=cfg.GRID_X * cfg.GRID_Y,
            information_units="bits", spatial_units="m", density_units="bits/m³",
        )

        c_val = cfg.NL_C if c is None else c
        if ablation in ("linear_telegraph", "reaction_off"):
            r_val = a_val = b_val = 0.0
        else:
            r_val, a_val, b_val = cfg.NL_R, cfg.NL_A, cfg.NL_B
        if ablation == "no_propagation":
            c_val = 0.0

        self.prop = PropagationParameters(c_nominal=float(c_val))
        self.relax = RelaxationParameters(tau_nominal=float(cfg.NL_TAU))
        self.react = NonlinearReactionParameters(r=r_val, a=a_val, b=b_val)
        self.no_inertia = ablation == "no_inertia"
        self.readout_only = ablation == "readout_only"
        self.deposit_log: list[dict] = []  # analysis only — agents never read

    def deposit(self, x, y, amp, tick):
        if self._failed or not self.allow_deposit:
            return
        self.field = apply_perturbation(
            self.field, PhysicalCoordinate(float(x), float(y), 0.0),
            float(amp), cfg.DEPOSIT_WIDTH,
        )
        self._stats.writes += 1
        self.deposit_log.append({"x": x, "y": y, "amp": amp, "tick": tick})

    def query_at(self, x, y, tick) -> float:
        self._stats.reads += 1
        if self._failed or not self.allow_readout:
            return 0.0
        return self.local_max(x, y)

    def local_max(self, x: float, y: float, radius: float = cfg.READ_RADIUS) -> float:
        s = self.grid()
        nx, ny = s.shape
        ix = int(np.clip(round(x / cfg.GRID_X * (nx - 1)), 0, nx - 1))
        iy = int(np.clip(round(y / cfg.GRID_Y * (ny - 1)), 0, ny - 1))
        r = max(1, int(round(radius / cfg.GRID_X * nx)))
        vals = []
        for dx in range(-r, r + 1):
            for dy in range(-r, r + 1):
                nix, niy = ix + dx, iy + dy
                if 0 <= nix < nx and 0 <= niy < ny:
                    vals.append(s[nix, niy])
        return float(np.max(vals)) if vals else 0.0

    def grid(self) -> np.ndarray:
        nx, ny = self.field.state.grid_shape[0], self.field.state.grid_shape[1]
        return self.field.state.field_values.reshape(nx, ny)

    def tick_update(self, tick):
        if self._failed or self.readout_only:
            return
        try:
            if self.no_inertia:
                self._step_no_inertia()
            else:
                self.field = evolve_field_nonlinear(
                    self.field, self.prop, self.relax, self.react)
            self._stats.solver_steps += 1
        except ValueError as exc:
            self._failed = True
            self._stats.solver_failures += 1
            self._stats.solver_error_log.append({"tick": tick, "error": str(exc)})

    def _step_no_inertia(self) -> None:
        state = self.field.state
        s = state.field_values.reshape(state.grid_shape)
        c = self.prop.c_nominal
        r, a, b = self.react.r, self.react.a, self.react.b
        lap = compute_laplacian(s, state.dx, state.dy, state.dz)
        reaction = r * s + a * (s ** 2) - b * (s ** 3)
        s_new = s + state.dt * ((c ** 2) * lap + reaction)
        if not np.all(np.isfinite(s_new)):
            raise ValueError("no_inertia: non-finite field")
        new_state = FieldState(
            field_values=s_new.ravel(),
            coordinates=state.coordinates,
            field_velocity=np.zeros_like(state.field_velocity),
            dx=state.dx, dy=state.dy, dz=state.dz, dt=state.dt,
            physical_time=state.physical_time + state.dt,
            grid_shape=state.grid_shape, metric=state.metric,
        )
        self.field = InformationDensityField(
            state=new_state,
            information_quantity=self.field.information_quantity,
            physical_volume=self.field.physical_volume,
            information_units=self.field.information_units,
            spatial_units=self.field.spatial_units,
            density_units=self.field.density_units,
        )

    def grid_max(self):
        return float(np.max(self.field.state.field_values))

    def failed(self):
        return self._failed

    def usage(self):
        return self._stats


class HybridMedium(MediumBackend):
    """Nonlinear substrate + capped direct messages."""

    name = "hybrid"

    def __init__(self, msg_budget: int | None = None):
        self.field = SubstrateMedium("nonlinear_full", name="hybrid_field")
        self.msg = DirectMsgMedium()
        self.msg_budget = int(cfg.HYBRID_MSG_BUDGET if msg_budget is None else msg_budget)
        self._msgs_used = 0
        self._stats = UsageStats()

    def deposit(self, x, y, amp, tick):
        self.field.deposit(x, y, amp, tick)

    def query_at(self, x, y, tick):
        return self.field.query_at(x, y, tick)

    def send_message(self, landmark_id, confidence, tick):
        if self._msgs_used >= self.msg_budget:
            return
        self.msg.send_message(landmark_id, confidence, tick)
        self._msgs_used += 1

    def list_messages(self, tick):
        return self.msg.list_messages(tick)

    def tick_update(self, tick):
        self.field.tick_update(tick)
        self.msg.tick_update(tick)

    def failed(self):
        return self.field.failed()

    def usage(self):
        u = UsageStats()
        for part in (self.field.usage(), self.msg.usage()):
            u.writes += part.writes
            u.reads += part.reads
            u.messages_sent += part.messages_sent
            u.message_payload_bytes += part.message_payload_bytes
            u.solver_steps += part.solver_steps
            u.solver_failures += part.solver_failures
            u.travel_distance += part.travel_distance
            u.solver_error_log.extend(part.solver_error_log)
        return u


def make_medium(arch: str, ablation: str | None = None) -> MediumBackend:
    if arch == "independent":
        return IndependentMedium()
    if arch == "direct_msg":
        return DirectMsgMedium()
    if arch == "blackboard":
        return BlackboardMedium()
    if arch == "pheromone":
        return PheromoneMedium()
    if arch == "linear_sub":
        return SubstrateMedium("linear_telegraph", name="linear_sub")
    if arch == "nonlinear_sub":
        return SubstrateMedium("nonlinear_full", name="nonlinear_sub")
    if arch == "hybrid":
        return HybridMedium()
    if arch == "ablation":
        abl = ablation or "nonlinear_full"
        allow_dep = abl != "deposit_disabled"
        allow_read = abl != "readout_disabled"
        mapped = {
            "nonlinear_full": "nonlinear_full",
            "linear_telegraph": "linear_telegraph",
            "reaction_off": "reaction_off",
            "no_propagation": "no_propagation",
            "no_hysteresis": "linear_telegraph",  # non-persistent linear response
            "readout_disabled": "nonlinear_full",
            "deposit_disabled": "nonlinear_full",
            "fixed_random_policy": "nonlinear_full",
            "no_inertia": "no_inertia",
            "readout_only": "readout_only",
        }.get(abl, abl)
        return SubstrateMedium(
            mapped, name=abl, allow_deposit=allow_dep, allow_readout=allow_read,
        )
    raise ValueError(f"unknown architecture: {arch}")
