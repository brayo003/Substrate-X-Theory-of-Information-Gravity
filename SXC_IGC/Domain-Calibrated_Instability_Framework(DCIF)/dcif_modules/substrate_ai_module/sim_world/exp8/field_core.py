"""Field construction, evolution, deposits, readout — Task 8 only."""
from __future__ import annotations

import math
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
from sim_world.exp8 import config as cfg


class FieldSim:
    """Minimal substrate simulator with ablation knobs."""

    def __init__(
        self,
        ablation: str = "nonlinear_full",
        *,
        r: float | None = None,
        a: float | None = None,
        b: float | None = None,
        c: float | None = None,
        tau: float | None = None,
        dt: float | None = None,
        nx: int | None = None,
        ny: int | None = None,
    ):
        self.ablation = ablation
        self.failed = False
        self.error_log: list[dict] = []
        self.n_steps = 0
        self.deposit_log: list[dict] = []  # for baselines/GT only — NOT used by decoder

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
        tau_val = cfg.NL_TAU if tau is None else tau
        if ablation in ("linear_telegraph", "reaction_off", "readout_only"):
            r_val = a_val = b_val = 0.0
        else:
            r_val = cfg.NL_R if r is None else r
            a_val = cfg.NL_A if a is None else a
            b_val = cfg.NL_B if b is None else b
        if ablation == "no_propagation":
            c_val = 0.0

        self.prop = PropagationParameters(c_nominal=float(c_val))
        self.relax = RelaxationParameters(tau_nominal=float(tau_val))
        self.react = NonlinearReactionParameters(r=r_val, a=a_val, b=b_val)
        self.no_inertia = ablation == "no_inertia"
        self.readout_only = ablation == "readout_only"

    def deposit(self, x: float, y: float, amp: float, tick: int = 0) -> None:
        if self.failed:
            return
        self.field = apply_perturbation(
            self.field, PhysicalCoordinate(float(x), float(y), 0.0),
            float(amp), cfg.DEPOSIT_WIDTH,
        )
        self.deposit_log.append({"x": x, "y": y, "amp": amp, "tick": tick})

    def step(self, tick: int = 0) -> bool:
        if self.failed or self.readout_only:
            return not self.failed
        try:
            if self.no_inertia:
                self._step_no_inertia()
            else:
                self.field = evolve_field_nonlinear(
                    self.field, self.prop, self.relax, self.react)
            self.n_steps += 1
        except ValueError as exc:
            self.failed = True
            self.error_log.append({"tick": tick, "error": str(exc)})
            return False
        return True

    def _step_no_inertia(self) -> None:
        """First-order reaction-diffusion-like step (documented approximation).

        s ← s + dt·(c²∇²s + reaction); v forced to 0.
        Uses same Laplacian/reaction as nonlinear path (code form).
        """
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

    def evolve(self, n: int, start_tick: int = 0) -> bool:
        for t in range(start_tick, start_tick + n):
            if not self.step(t):
                return False
        return True

    def grid(self) -> np.ndarray:
        nx, ny = self.field.state.grid_shape[0], self.field.state.grid_shape[1]
        return self.field.state.field_values.reshape(nx, ny)

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

    def stats(self) -> dict[str, float]:
        v = self.field.state.field_values
        return {
            "mean": float(np.mean(v)),
            "max": float(np.max(v)),
            "min": float(np.min(v)),
            "frac_high": float(np.mean(v > cfg.ACTIVATION_THRESH)),
            "frac_splus": float(np.mean(v > 0.9)),
        }


def activated(sim: FieldSim, x: float, y: float, thr: float = cfg.ACTIVATION_THRESH) -> bool:
    """Decoder: field-only local max ≥ threshold. Never reads deposit_log."""
    return sim.local_max(x, y) >= thr


def pair_sites(seed: int, sep: float, cx: float | None = None, cy: float | None = None):
    rng = np.random.default_rng(seed + 4242)
    if cx is None:
        cx = float(rng.uniform(16, cfg.GRID_X - 16))
    if cy is None:
        cy = float(rng.uniform(16, cfg.GRID_Y - 16))
    ang = float(rng.uniform(0, 2 * math.pi))
    hx, hy = 0.5 * sep * math.cos(ang), 0.5 * sep * math.sin(ang)
    a = (float(np.clip(cx - hx, 8, cfg.GRID_X - 8)),
         float(np.clip(cy - hy, 8, cfg.GRID_Y - 8)))
    b = (float(np.clip(cx + hx, 8, cfg.GRID_X - 8)),
         float(np.clip(cy + hy, 8, cfg.GRID_Y - 8)))
    return a, b, (0.5 * (a[0] + b[0]), 0.5 * (a[1] + b[1]))
