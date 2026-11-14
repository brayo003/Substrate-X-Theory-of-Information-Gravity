"""Gates G1 (mathematical) and G2 (dynamical) for corrected Task 6."""
from __future__ import annotations

import math
import os
import sys
from typing import Any

import numpy as np

_HERE = os.path.dirname(os.path.abspath(__file__))
_SIM = os.path.dirname(_HERE)
_PARENT = os.path.dirname(_SIM)
for _p in (_PARENT, _SIM):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from sim_world.domains.physical_field.physical_field_dynamics import (
    initialize_field_state,
    evolve_field,
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


def _make_field(
    initial_value: float,
    nx: int = cfg.GRID_NX,
    ny: int = cfg.GRID_NY,
    dt: float = cfg.DT,
    x_range=(0.0, cfg.GRID_X),
    y_range=(0.0, cfg.GRID_Y),
) -> InformationDensityField:
    state = initialize_field_state(
        x_range=x_range, y_range=y_range, nx=nx, ny=ny,
        initial_value=initial_value, dt=dt,
    )
    return InformationDensityField(
        state=state,
        information_quantity=1.0,
        physical_volume=float(x_range[1] * y_range[1]),
        information_units="bits",
        spatial_units="m",
        density_units="bits/m³",
    )


def _react(nonlinear: bool = True) -> NonlinearReactionParameters:
    if nonlinear:
        return NonlinearReactionParameters(r=cfg.NL_R, a=cfg.NL_A, b=cfg.NL_B)
    return NonlinearReactionParameters(r=0.0, a=0.0, b=0.0)


def _prop() -> PropagationParameters:
    return PropagationParameters(c_nominal=cfg.NL_C)


def _relax() -> RelaxationParameters:
    return RelaxationParameters(tau_nominal=cfg.NL_TAU)


def _evolve(field, n_steps: int, nonlinear: bool = True, record_errors: list | None = None):
    prop, relax, react = _prop(), _relax(), _react(nonlinear)
    for i in range(n_steps):
        try:
            field = evolve_field_nonlinear(field, prop, relax, react)
        except ValueError as exc:
            if record_errors is not None:
                record_errors.append({"step": i, "error": str(exc)})
            raise
    return field


def _stats(field: InformationDensityField) -> dict[str, float]:
    v = field.state.field_values
    return {
        "mean": float(np.mean(v)),
        "max": float(np.max(v)),
        "min": float(np.min(v)),
        "std": float(np.std(v)),
        "frac_above_separatrix": float(np.mean(v > cfg.S_MINUS)),
        "frac_high": float(np.mean(v > cfg.HIGH_STATE_THRESH)),
        "finite": bool(np.all(np.isfinite(v))),
    }


def _xy_to_ixiy(x: float, y: float, nx: int = cfg.GRID_NX, ny: int = cfg.GRID_NY):
    """Map physical (x,y) → (ix, iy) for field reshaped as (nx, ny) [ij meshgrid]."""
    ix = int(np.clip(round(x / cfg.GRID_X * (nx - 1)), 0, nx - 1))
    iy = int(np.clip(round(y / cfg.GRID_Y * (ny - 1)), 0, ny - 1))
    return ix, iy


def _field_2d(field: InformationDensityField) -> np.ndarray:
    """Return s[ix, iy] consistent with create_physical_grid(indexing='ij')."""
    nx, ny = field.state.grid_shape[0], field.state.grid_shape[1]
    return field.state.field_values.reshape(nx, ny)


def _high_extent(field: InformationDensityField) -> dict[str, float]:
    """Spatial extent of high-state region (cells above HIGH_STATE_THRESH)."""
    s = _field_2d(field)
    mask = s > cfg.HIGH_STATE_THRESH
    n = int(np.sum(mask))
    if n == 0:
        return {"n_high_cells": 0, "centroid_ix": float("nan"), "centroid_iy": float("nan"),
                "bbox_dix": 0, "bbox_diy": 0}
    iix, iiy = np.where(mask)
    return {
        "n_high_cells": n,
        "centroid_ix": float(np.mean(iix)),
        "centroid_iy": float(np.mean(iiy)),
        "bbox_dix": int(iix.max() - iix.min() + 1),
        "bbox_diy": int(iiy.max() - iiy.min() + 1),
    }


# ---------------------------------------------------------------------------
# Gate G1
# ---------------------------------------------------------------------------

def run_gate_g1() -> dict[str, Any]:
    """Mathematical verification gate."""
    results: dict[str, Any] = {"gate": "G1", "checks": {}}
    react = _react(True)

    # 1. Analytical equilibria
    eqs = react.homogeneous_equilibria()
    tol = 1e-6
    expected = sorted([cfg.S0, cfg.S_MINUS, cfg.S_PLUS])
    eq_ok = (
        len(eqs) == 3
        and abs(eqs[0] - expected[0]) < tol
        and abs(eqs[1] - expected[1]) < tol
        and abs(eqs[2] - expected[2]) < tol
    )
    results["checks"]["equilibria"] = {
        "pass": eq_ok,
        "computed": eqs,
        "expected": expected,
        "tolerance": tol,
    }

    # 2. Stability classification via linearized growth rate
    rates = {s: react.linearized_growth_rate(s) for s in eqs}
    stab_ok = (
        rates[eqs[0]] < 0          # s0 stable
        and rates[eqs[1]] > 0      # s- unstable
        and rates[eqs[2]] < 0      # s+ stable
    )
    results["checks"]["stability"] = {
        "pass": stab_ok,
        "growth_rates": {str(k): float(v) for k, v in rates.items()},
        "classification": {
            str(eqs[0]): "stable" if rates[eqs[0]] < 0 else "unstable",
            str(eqs[1]): "unstable" if rates[eqs[1]] > 0 else "stable",
            str(eqs[2]): "stable" if rates[eqs[2]] < 0 else "unstable",
        },
    }

    # 3. Solver evolves specified equation: homogeneous ODE check
    # For uniform field, Laplacian=0 → reaction-telegraph reduces to
    # τ v_t + v = r s + a s² - b s³; s_t = v
    # Compare one-step numerical update against analytic acceleration.
    field = _make_field(0.5)
    s0 = float(field.state.field_values[0])
    v0 = float(field.state.field_velocity[0])
    r, a, b = cfg.NL_R, cfg.NL_A, cfg.NL_B
    reaction = r * s0 + a * s0**2 - b * s0**3
    acc_analytic = (reaction - v0) / cfg.NL_TAU
    v_new = v0 + cfg.DT * acc_analytic
    s_new = s0 + cfg.DT * v_new
    field2 = evolve_field_nonlinear(field, _prop(), _relax(), react)
    s_num = float(field2.state.field_values[0])
    eq_match = abs(s_num - s_new) < 1e-10
    results["checks"]["equation_identity_homogeneous"] = {
        "pass": eq_match,
        "analytic_s": s_new,
        "numeric_s": s_num,
        "abs_err": abs(s_num - s_new),
    }

    # 4. Linear limit recovery
    field = _make_field(0.0)
    field = apply_perturbation(field, PhysicalCoordinate(25.0, 25.0, 0.0), 1.0, 2.0)
    lin = evolve_field(field, _prop(), _relax())
    nlin0 = evolve_field_nonlinear(field, _prop(), _relax(), _react(False))
    max_diff = float(np.max(np.abs(lin.state.field_values - nlin0.state.field_values)))
    results["checks"]["linear_limit"] = {
        "pass": max_diff < 1e-12,
        "max_abs_diff": max_diff,
    }

    # 5. Timestep convergence (homogeneous toward s+)
    means = {}
    for dt in (0.05, 0.025, 0.0125):
        f = _make_field(1.0, dt=dt)  # above separatrix → s+
        n_steps = int(round(20.0 / dt))
        errors: list = []
        try:
            f = _evolve(f, n_steps, True, errors)
            means[str(dt)] = _stats(f)["mean"]
        except ValueError as exc:
            means[str(dt)] = f"FAILED: {exc}"
    # Convergence: successive refinements approach s+
    if all(isinstance(means[k], float) for k in means):
        err_coarse = abs(means["0.05"] - cfg.S_PLUS)
        err_fine = abs(means["0.0125"] - cfg.S_PLUS)
        dt_ok = err_fine <= err_coarse + 0.05  # fine not worse than coarse
    else:
        dt_ok = False
    results["checks"]["timestep_convergence"] = {
        "pass": dt_ok,
        "means_after_t20": means,
        "target_s_plus": cfg.S_PLUS,
    }

    # 6. Spatial-resolution convergence (localized deposit persistence)
    extent_by_n = {}
    for n in (20, 30, 40):
        f = _make_field(cfg.FIELD_IC, nx=n, ny=n)
        # temporarily override reshape awareness via apply_perturbation
        f = apply_perturbation(f, PhysicalCoordinate(25.0, 25.0, 0.0),
                               cfg.SUB_DEPOSIT_AMP, cfg.SUB_DEPOSIT_WIDTH)
        errors = []
        try:
            # evolve with matching grid — use local evolve loop
            prop, relax, react_p = _prop(), _relax(), _react(True)
            for _ in range(100):
                f = evolve_field_nonlinear(f, prop, relax, react_p)
            s = f.state.field_values
            extent_by_n[n] = {
                "max": float(np.max(s)),
                "frac_high": float(np.mean(s > cfg.HIGH_STATE_THRESH)),
                "finite": bool(np.all(np.isfinite(s))),
            }
        except ValueError as exc:
            extent_by_n[n] = {"error": str(exc)}
    spat_ok = all(
        isinstance(extent_by_n[n], dict) and extent_by_n[n].get("finite", False)
        and extent_by_n[n].get("max", 0) > cfg.S_MINUS
        for n in (20, 30, 40)
    )
    results["checks"]["spatial_resolution"] = {
        "pass": spat_ok,
        "by_n": extent_by_n,
        "note": "Superthreshold deposit produces high-state across resolutions; "
                "zero-Laplacian BCs documented as pre-existing limitation.",
    }

    # 7. Boundary conditions documentation + finite check
    f = _make_field(cfg.FIELD_IC)
    f = apply_perturbation(f, PhysicalCoordinate(2.0, 2.0, 0.0), 1.0, 2.0)  # near corner
    f = _evolve(f, 50, True)
    st = _stats(f)
    results["checks"]["boundary_conditions"] = {
        "pass": st["finite"],
        "scheme": "zero-Laplacian at boundary nodes (pre-existing; see "
                  "BOUNDARY_CONDITION_INVESTIGATION.md)",
        "near_corner_deposit_stats": st,
    }

    # 8. Field remains numerically valid over parameter range used in experiment
    f = _make_field(cfg.FIELD_IC)
    f = apply_perturbation(f, PhysicalCoordinate(25.0, 25.0, 0.0),
                           cfg.SUB_DEPOSIT_AMP, cfg.SUB_DEPOSIT_WIDTH)
    errors = []
    try:
        f = _evolve(f, cfg.EXP_C_TICKS, True, errors)
        st = _stats(f)
        valid_ok = st["finite"] and len(errors) == 0
    except ValueError:
        valid_ok = False
        st = {}
    results["checks"]["numerical_validity"] = {
        "pass": valid_ok,
        "stats_after_exp_c_duration": st,
        "solver_errors": errors,
    }

    results["pass"] = all(c.get("pass", False) for c in results["checks"].values())
    return results


# ---------------------------------------------------------------------------
# Gate G2
# ---------------------------------------------------------------------------

def _deposit_record(field, amp: float, x: float, y: float) -> InformationDensityField:
    return apply_perturbation(
        field, PhysicalCoordinate(x, y, 0.0), amp, cfg.SUB_DEPOSIT_WIDTH
    )


def run_gate_g2() -> dict[str, Any]:
    """Dynamical verification: undisturbed, sub/superthreshold, localization, ablation."""
    out: dict[str, Any] = {"gate": "G2", "tests": {}}
    n_full = cfg.EXP_C_TICKS  # full ordinary experiment duration

    # Test 1 — Undisturbed field in low basin
    f = _make_field(cfg.FIELD_IC)
    init_stats = _stats(f)
    errors: list = []
    try:
        f = _evolve(f, n_full, True, errors)
        st = _stats(f)
        # Remain below separatrix globally
        t1_pass = (
            st["finite"]
            and st["max"] < cfg.S_MINUS
            and st["frac_above_separatrix"] < 1e-9
            and len(errors) == 0
        )
    except ValueError as exc:
        st = {"error": str(exc)}
        t1_pass = False
    out["tests"]["T1_undisturbed"] = {
        "pass": t1_pass,
        "initial": init_stats,
        "final": st,
        "solver_errors": errors,
        "deposit_amp": 0.0,
    }

    # Test 2 — Subthreshold deposit
    f = _make_field(cfg.FIELD_IC)
    f = _deposit_record(f, cfg.SUB_DEPOSIT_AMP_SUB, 25.0, 25.0)
    after_dep = _stats(f)
    errors = []
    try:
        f = _evolve(f, n_full, True, errors)
        st = _stats(f)
        # Should NOT produce persistent high-state transition
        t2_pass = (
            st["finite"]
            and st["frac_high"] < 0.01
            and st["max"] < cfg.HIGH_STATE_THRESH
            and len(errors) == 0
        )
    except ValueError as exc:
        st = {"error": str(exc)}
        t2_pass = False
    out["tests"]["T2_subthreshold"] = {
        "pass": t2_pass,
        "deposit_amp": cfg.SUB_DEPOSIT_AMP_SUB,
        "after_deposit": after_dep,
        "final": st,
        "extent": _high_extent(f) if t2_pass or isinstance(st, dict) else {},
        "solver_errors": errors,
    }

    # Test 3 — Superthreshold deposit
    f = _make_field(cfg.FIELD_IC)
    f = _deposit_record(f, cfg.SUB_DEPOSIT_AMP, 25.0, 25.0)
    after_dep = _stats(f)
    local_max_series = [after_dep["max"]]
    cross_time = None
    errors = []
    prop, relax, react = _prop(), _relax(), _react(True)
    try:
        for t in range(n_full):
            f = evolve_field_nonlinear(f, prop, relax, react)
            mx = float(np.max(f.state.field_values))
            local_max_series.append(mx)
            if cross_time is None and mx > cfg.HIGH_STATE_THRESH:
                cross_time = t
        st = _stats(f)
        extent = _high_extent(f)
        t3_pass = (
            st["finite"]
            and st["max"] > cfg.S_MINUS
            and st["frac_high"] > 0.0
            and cross_time is not None
        )
    except ValueError as exc:
        st = {"error": str(exc)}
        extent = {}
        t3_pass = False
    out["tests"]["T3_superthreshold"] = {
        "pass": t3_pass,
        "deposit_amp": cfg.SUB_DEPOSIT_AMP,
        "after_deposit": after_dep,
        "final": st,
        "time_of_threshold_crossing": cross_time,
        "extent": extent,
        "local_max_final": local_max_series[-1] if local_max_series else None,
        "solver_errors": errors,
    }

    # Test 4 — Deposit removal: transition persists after external deposit ends
    # (deposits are impulsive; evolve further after deposit without new deposits)
    f = _make_field(cfg.FIELD_IC)
    f = _deposit_record(f, cfg.SUB_DEPOSIT_AMP, 25.0, 25.0)
    f = _evolve(f, 40, True)  # allow transition
    mid = _stats(f)
    mid_extent = _high_extent(f)
    f = _evolve(f, 40, True)  # no further deposits
    fin = _stats(f)
    fin_extent = _high_extent(f)
    t4_pass = (
        mid["frac_high"] > 0
        and fin["frac_high"] > 0
        and fin["max"] > cfg.HIGH_STATE_THRESH
        and fin["finite"]
    )
    out["tests"]["T4_deposit_removal_persistence"] = {
        "pass": t4_pass,
        "after_transition": mid,
        "after_further_evolution_no_deposit": fin,
        "extent_mid": mid_extent,
        "extent_final": fin_extent,
        "persistence_duration_ticks": 40,
    }

    # Test 5 — Spatial localization
    f = _make_field(cfg.FIELD_IC)
    f = _deposit_record(f, cfg.SUB_DEPOSIT_AMP, 25.0, 25.0)
    f = _evolve(f, 60, True)
    st = _stats(f)
    extent = _high_extent(f)
    # Localized: high cells should not cover entire grid under these params
    t5_pass = (
        st["finite"]
        and extent["n_high_cells"] > 0
        and extent["n_high_cells"] < cfg.GRID_NX * cfg.GRID_NY * 0.5
    )
    out["tests"]["T5_spatial_localization"] = {
        "pass": t5_pass,
        "final_stats": st,
        "extent": extent,
        "note": "Spreading quantified; partial spread consistent with reaction-diffusion "
                "fronts is allowed if not whole-domain.",
    }

    # Test 6 — Two spatially separated deposits
    f = _make_field(cfg.FIELD_IC)
    f = _deposit_record(f, cfg.SUB_DEPOSIT_AMP, 12.0, 25.0)
    f = _deposit_record(f, cfg.SUB_DEPOSIT_AMP, 38.0, 25.0)
    f = _evolve(f, 60, True)
    s = _field_2d(f)
    nx, ny = s.shape

    def local_stats(x, y, r=3):
        ix, iy = _xy_to_ixiy(x, y, nx, ny)
        vals = []
        for dx_ in range(-r, r + 1):
            for dy_ in range(-r, r + 1):
                nix, niy = ix + dx_, iy + dy_
                if 0 <= nix < nx and 0 <= niy < ny:
                    vals.append(float(s[nix, niy]))
        if not vals:
            return {"mean": 0.0, "max": 0.0}
        return {"mean": float(np.mean(vals)), "max": float(np.max(vals))}

    left = local_stats(12.0, 25.0)
    right = local_stats(38.0, 25.0)
    midpt = local_stats(25.0, 25.0)
    extent = _high_extent(f)
    # Distinguishable: each deposit neighbourhood retains a local max above separatrix
    # and midpoint max is strictly below both peak maxima (two blobs, not one merged).
    distinguishable = (
        left["max"] > cfg.S_MINUS
        and right["max"] > cfg.S_MINUS
        and midpt["max"] < min(left["max"], right["max"])
    )
    t6_pass = distinguishable and _stats(f)["finite"]
    out["tests"]["T6_multiple_deposits"] = {
        "pass": t6_pass,
        "deposit_locations": [(12.0, 25.0), (38.0, 25.0)],
        "local_left": left,
        "local_right": right,
        "local_midpoint": midpt,
        "extent": extent,
        "regions_distinguishable": distinguishable,
        "note": "Field indexed as s[ix,iy] matching meshgrid(indexing='ij'). "
                "Distinguishability uses local maxima vs midpoint.",
    }

    # Test 7 — Linear ablation: bistable transition disappears
    f = _make_field(cfg.FIELD_IC)
    f = _deposit_record(f, cfg.SUB_DEPOSIT_AMP, 25.0, 25.0)
    after = _stats(f)
    f = _evolve(f, n_full, nonlinear=False)
    st = _stats(f)
    # Linear telegraph: deposit should decay / disperse; no sustained high basin
    t7_pass = st["finite"] and st["frac_high"] < 0.05
    out["tests"]["T7_linear_ablation"] = {
        "pass": t7_pass,
        "after_deposit": after,
        "final_linear": st,
        "note": "With r=a=b=0, persistent bistable high-state must not appear.",
    }

    out["pass"] = all(t.get("pass", False) for t in out["tests"].values())
    return out


def run_math_gates() -> dict[str, Any]:
    g1 = run_gate_g1()
    g2 = run_gate_g2()
    return {
        "G1": g1,
        "G2": g2,
        "proceed_to_agentic": bool(g1["pass"] and g2["pass"]),
    }


if __name__ == "__main__":
    import json
    res = run_math_gates()
    print(json.dumps({
        "G1_pass": res["G1"]["pass"],
        "G2_pass": res["G2"]["pass"],
        "G1_checks": {k: v.get("pass") for k, v in res["G1"]["checks"].items()},
        "G2_tests": {k: v.get("pass") for k, v in res["G2"]["tests"].items()},
    }, indent=2))
