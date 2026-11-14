"""Numerical validation with continuous field metrics + decision agreement."""
from __future__ import annotations

from typing import Any

import numpy as np

from sim_world.exp9 import config as cfg
from sim_world.exp9.field_backend import SubstrateMedium
from sim_world.exp9.experiments import _run_trial


def _near_pair_sim(dt: float, nx: int, ny: int) -> dict[str, Any]:
    lx, ly = cfg.LANDMARKS[0]
    sim = SubstrateMedium("nonlinear_full", dt=dt, nx=nx, ny=ny)
    sim.deposit(lx, ly, cfg.DEP_AMP, 0)
    sim.deposit(lx + 1.5, ly, cfg.DEP_AMP, 0)
    phys = 60 * cfg.DT
    n_steps = int(round(phys / dt))
    for t in range(n_steps):
        sim.tick_update(t)
    g = sim.grid()
    return {
        "failed": sim.failed(),
        "local_max": sim.local_max(lx, ly),
        "activated": int(sim.local_max(lx, ly) >= cfg.ACTIVATION_THRESH),
        "max_field": float(np.max(g)) if not sim.failed() else None,
        "mean_field": float(np.mean(g)) if not sim.failed() else None,
        "grid": g if not sim.failed() else None,
        "dt": dt,
        "nx": nx,
        "ny": ny,
        "n_steps": n_steps,
    }


def dt_sensitivity() -> dict[str, Any]:
    dts = (0.05, 0.025, 0.0125)
    rows = []
    grids = []
    for dt in dts:
        r = _near_pair_sim(dt, cfg.GRID_NX, cfg.GRID_NY)
        rows.append({k: v for k, v in r.items() if k != "grid"})
        grids.append(r["grid"])
    # Compare continuous profiles on coarsest shared reshape — use local_max / max error
    ref = rows[0]
    amp_errs = []
    for r in rows[1:]:
        if ref["local_max"] is None or r["local_max"] is None:
            amp_errs.append(None)
        else:
            amp_errs.append(abs(r["local_max"] - ref["local_max"]))
    acts = [r["activated"] for r in rows if r["activated"] is not None]
    decision_agree = len(set(acts)) == 1 and len(acts) == len(dts)
    # Continuous pass: relative local_max error < 15% between finest and default
    cont_ok = amp_errs[-1] is not None and amp_errs[-1] / max(ref["local_max"], 1e-6) < 0.15
    return {
        "test": "dt_sensitivity",
        "pass_binary": bool(decision_agree and acts and acts[0] == 1),
        "pass_continuous": bool(cont_ok),
        "pass": bool(decision_agree and acts and acts[0] == 1 and cont_ok),
        "amp_abs_err_vs_dt005": amp_errs,
        "rows": rows,
        "note": "Binary agreement alone is insufficient; continuous local_max error also required.",
    }


def spatial_resolution_sensitivity() -> dict[str, Any]:
    grids = ((30, 30), (40, 40), (50, 50))
    rows = []
    for nx, ny in grids:
        r = _near_pair_sim(cfg.DT, nx, ny)
        rows.append({k: v for k, v in r.items() if k != "grid"})
    # Activation-boundary proxy: fraction of cells above thresh near landmark
    # Decision agreement across 30/40/50
    acts = [r["activated"] for r in rows]
    decision_agree = len(set(acts)) == 1 and acts[0] == 1
    # Continuous: |local_max_30 - local_max_50| / local_max_50
    lm = [r["local_max"] for r in rows]
    rel_err = abs(lm[0] - lm[2]) / max(lm[2], 1e-6) if all(v is not None for v in lm) else 1.0
    cont_ok = rel_err < 0.20
    # Agent decision: run one trial at default only vs note — field decision boundary
    return {
        "test": "spatial_resolution_sensitivity",
        "pass_binary": bool(decision_agree),
        "pass_continuous": bool(cont_ok),
        "pass": bool(decision_agree and cont_ok),
        "local_max_rel_err_30_vs_50": float(rel_err),
        "rows": rows,
        "note": "Task 8 binary-only grid check strengthened with continuous local_max error.",
    }


def high_deposit_density_stability() -> dict[str, Any]:
    sim = SubstrateMedium("nonlinear_full")
    rng = np.random.default_rng(0)
    for i in range(20):
        x = float(rng.uniform(10, 40))
        y = float(rng.uniform(10, 40))
        sim.deposit(x, y, cfg.DEP_AMP, i)
        sim.tick_update(i)
    for t in range(20, 80):
        sim.tick_update(t)
    return {
        "test": "high_deposit_density",
        "pass": bool(not sim.failed() and np.isfinite(sim.grid_max())),
        "max_field": sim.grid_max() if not sim.failed() else None,
        "failed": sim.failed(),
    }


def seed_reproducibility() -> dict[str, Any]:
    a = _run_trial(401, "nonlinear_sub")
    b = _run_trial(401, "nonlinear_sub")
    keys = ("correct", "majority", "true_landmark", "n_field_deposits")
    agree = all(a[k] == b[k] for k in keys)
    return {"test": "seed_reproducibility", "pass": bool(agree), "a": {k: a[k] for k in keys},
            "b": {k: b[k] for k in keys}}


def agent_decision_under_refinement() -> dict[str, Any]:
    """Whether default protocol agent decisions are stable across matched seeds.

    Full re-grid agent sims would require medium nx overrides end-to-end; here we
    document field-level decision stability from spatial_resolution_sensitivity and
    report one seed's commitment under default grid as the operational setting.
    """
    t = _run_trial(402, "nonlinear_sub")
    return {
        "test": "agent_decision_default_grid",
        "seed": 402,
        "correct": t["correct"],
        "majority": t["majority"],
        "note": "Operational claims use 30×30; continuous field refinement reported separately.",
    }


def run_numerical_suite() -> dict[str, Any]:
    blocks = [
        dt_sensitivity(),
        spatial_resolution_sensitivity(),
        high_deposit_density_stability(),
        seed_reproducibility(),
        agent_decision_under_refinement(),
        # BC note
        {
            "test": "boundary_condition_note",
            "pass": True,
            "note": (
                "compute_laplacian uses interior-only stencil (Dirichlet-like). "
                "Landmarks inset from boundary; BC sensitivity not claimed as varied."
            ),
        },
    ]
    # all_pass: require continuous+binary where applicable
    flags = []
    for b in blocks:
        if "pass" in b:
            flags.append(bool(b["pass"]))
    return {
        "blocks": blocks,
        "all_pass": all(flags) if flags else False,
        "n_blocks": len(blocks),
    }
