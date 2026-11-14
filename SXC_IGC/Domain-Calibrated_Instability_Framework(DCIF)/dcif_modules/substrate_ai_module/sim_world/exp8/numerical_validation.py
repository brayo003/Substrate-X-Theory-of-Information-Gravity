"""Numerical convergence / stability checks for Task 8."""
from __future__ import annotations

from typing import Any

import numpy as np

from sim_world.exp8 import config as cfg
from sim_world.exp8.field_core import FieldSim, activated


# Fixed geometry with clear overlap (sep=2.5) so tests are not thr-borderline.
_NUM_A = (23.75, 25.0)
_NUM_B = (26.25, 25.0)
_NUM_MID = (25.0, 25.0)
_NUM_EVOLVE_PHYS = cfg.A_EVOLVE * cfg.DT  # match A physical time


def dt_convergence_near_pair(seed: int = 0) -> dict[str, Any]:
    """Activation decision for near-pair should agree across dt refinements.

    Requires positive high-basin activation (not vacuous all-zero agreement).
    """
    dts = (0.05, 0.025, 0.0125)
    results = []
    for dt in dts:
        sim = FieldSim("nonlinear_full", dt=dt)
        sim.deposit(*_NUM_A, cfg.A_SUB_AMP, 0)
        sim.deposit(*_NUM_B, cfg.A_SUB_AMP, 0)
        n_steps = int(round(_NUM_EVOLVE_PHYS / dt))
        ok = sim.evolve(n_steps)
        results.append({
            "dt": dt, "failed": not ok or sim.failed,
            "activated": int(activated(sim, *_NUM_MID)) if ok else None,
            "local_max": sim.local_max(*_NUM_MID) if ok else None,
            "max_field": sim.stats()["max"] if ok else None,
            "n_steps": n_steps,
        })
    acts = [r["activated"] for r in results if r["activated"] is not None]
    agree = len(set(acts)) == 1 and len(acts) == len(dts) and acts and acts[0] == 1
    return {"test": "dt_convergence_near_pair", "pass": bool(agree), "rows": results}


def grid_convergence_near_pair() -> dict[str, Any]:
    """Default vs finer grid: activation agreement on positive latch."""
    grids = ((20, 20), (30, 30), (40, 40))
    rows = []
    for nx, ny in grids:
        sim = FieldSim("nonlinear_full", nx=nx, ny=ny)
        sim.deposit(*_NUM_A, cfg.A_SUB_AMP, 0)
        sim.deposit(*_NUM_B, cfg.A_SUB_AMP, 0)
        ok = sim.evolve(cfg.A_EVOLVE)
        rows.append({
            "nx": nx, "ny": ny, "failed": not ok,
            "activated": int(activated(sim, *_NUM_MID)) if ok else None,
            "local_max": sim.local_max(*_NUM_MID) if ok else None,
        })
    fine_agree = (
        rows[1]["activated"] == rows[2]["activated"]
        and rows[1]["activated"] == 1
    )
    return {"test": "grid_convergence", "pass": bool(fine_agree), "rows": rows,
            "note": "20×20 may differ; 30×30 vs 40×40 must agree on activation=1"}


def single_below_threshold_stable() -> dict[str, Any]:
    """Single subthreshold deposit must NOT high-basin activate."""
    sim = FieldSim("nonlinear_full")
    sim.deposit(25.0, 25.0, cfg.A_SUB_AMP, 0)
    ok = sim.evolve(cfg.A_EVOLVE)
    act = activated(sim, 25.0, 25.0) if ok else True
    return {
        "test": "single_no_spurious_activation",
        "pass": bool(ok and not act),
        "local_max": sim.local_max(25.0, 25.0) if ok else None,
        "max_field": sim.stats()["max"] if ok else None,
        "failed": not ok,
    }


def boundedness_strong_deposit() -> dict[str, Any]:
    sim = FieldSim("nonlinear_full")
    sim.deposit(25.0, 25.0, 2.0, 0)
    ok = sim.evolve(80)
    st = sim.stats() if ok else {}
    bounded = ok and st.get("max", 99) < 5.0
    return {"test": "boundedness", "pass": bool(bounded), "stats": st, "failed": not ok}


def linear_decays_nonlinear_latches() -> dict[str, Any]:
    """Same deposits: nonlinear high-basin latch; linear does not."""
    rows = []
    for abl in ("nonlinear_full", "linear_telegraph"):
        sim = FieldSim(abl)
        sim.deposit(*_NUM_A, cfg.A_SUB_AMP, 0)
        sim.deposit(*_NUM_B, cfg.A_SUB_AMP, 0)
        ok = sim.evolve(cfg.A_EVOLVE)
        rows.append({
            "ablation": abl, "failed": not ok,
            "activated": int(activated(sim, *_NUM_MID)) if ok else None,
            "local_max": sim.local_max(*_NUM_MID) if ok else None,
        })
    ok = (
        rows[0]["activated"] == 1
        and rows[1]["activated"] == 0
        and not rows[0]["failed"] and not rows[1]["failed"]
    )
    return {"test": "nl_latch_vs_linear_decay", "pass": bool(ok), "rows": rows}


def run_numerical_suite() -> dict[str, Any]:
    tests = [
        dt_convergence_near_pair(),
        grid_convergence_near_pair(),
        single_below_threshold_stable(),
        boundedness_strong_deposit(),
        linear_decays_nonlinear_latches(),
    ]
    return {
        "all_pass": all(t["pass"] for t in tests),
        "tests": tests,
    }
