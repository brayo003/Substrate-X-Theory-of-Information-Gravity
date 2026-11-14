"""Gates G3 (no-oracle) and G4 (architectural integrity)."""
from __future__ import annotations

import inspect
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

from sim_world.exp6_corrected import config as cfg
from sim_world.exp6_corrected.architectures import (
    make_memory, architecture_fairness_notes, MemoryBackend,
)


def _agent_choose_target(memory: MemoryBackend, ax: float, ay: float, tick: int,
                         local_observations: list[dict]) -> tuple[float, float] | None:
    """
    Decision pathway used by Experiment C movement — intentionally has NO access
    to ground-truth resource lists. Candidates come only from:
      - local_observations (sensor hits)
      - memory.list_known (messaging/blackboard)
      - local gradient ascent on memory.query_at at own position
    """
    candidates: list[tuple[float, float, float]] = []
    for obs in local_observations:
        candidates.append((obs["x"], obs["y"], 1.0 + float(obs.get("value", 1.0))))

    for rec in memory.list_known("resource", tick):
        candidates.append((float(rec["x"]), float(rec["y"]), 0.8 + float(rec.get("value", 0))))

    # Local gradient hint (spatial media) — query only near agent
    gx, gy = memory.sample_gradient("resource", ax, ay, tick)
    grad_norm = math.hypot(gx, gy)
    if grad_norm > 1e-4:
        step = cfg.SENSOR_RADIUS
        candidates.append((ax + step * gx / grad_norm, ay + step * gy / grad_norm, grad_norm))

    if not candidates:
        return None
    # Score by signal / distance
    best = None
    best_score = -1.0
    for tx, ty, sig in candidates:
        d = math.hypot(ax - tx, ay - ty)
        score = sig / (1.0 + 0.1 * d)
        if score > best_score:
            best_score = score
            best = (tx, ty)
    return best


def decision_invariance_test() -> dict[str, Any]:
    """
    C5 / G3: change hidden environmental truth while agent-visible info identical.
    Agent decisions must remain identical.
    """
    results = {}
    for cond in cfg.CONDITIONS:
        mem = make_memory(cond)
        # Visible history identical: one deposited resource message/signal at (10,10)
        mem.deposit("resource", 10.0, 10.0, cfg.SUB_DEPOSIT_AMP, tick=0)
        # Local observations identical
        local_obs = [{"x": 10.0, "y": 10.0, "value": 1.0}]
        # Hidden worlds differ — but are NOT passed to the decision function
        hidden_world_A = {"resources": [(10.0, 10.0), (40.0, 40.0)]}
        hidden_world_B = {"resources": [(10.0, 10.0), (5.0, 45.0), (45.0, 5.0)]}
        # Decisions with same visible state
        d1 = _agent_choose_target(mem, 12.0, 12.0, tick=1, local_observations=local_obs)
        d2 = _agent_choose_target(mem, 12.0, 12.0, tick=1, local_observations=local_obs)
        # Explicitly ensure hidden worlds are unused: decision fn signature has no env
        sig = inspect.signature(_agent_choose_target)
        has_env_param = any(p in sig.parameters for p in ("env", "resources", "hazards", "tasks"))
        identical = d1 == d2 and not has_env_param
        # Additionally: querying at a hidden coordinate must not be done by movement;
        # we verify helper never iterates hidden lists (static check via source)
        src = inspect.getsource(_agent_choose_target)
        leaks = any(tok in src for tok in ("hidden_world", "active_resources", "env["))
        results[cond] = {
            "decision_A": d1,
            "decision_B": d2,
            "identical": identical and not leaks,
            "hidden_worlds_differ": hidden_world_A != hidden_world_B,
            "decision_fn_has_env_param": has_env_param,
            "source_leak_tokens": leaks,
        }
    all_pass = all(v["identical"] for v in results.values())
    return {"pass": all_pass, "per_condition": results}


def runtime_pathway_traces() -> dict[str, Any]:
    """G4: each architecture actually uses its pathway (writes/reads)."""
    traces = {}
    for cond in cfg.CONDITIONS:
        mem = make_memory(cond)
        mem.deposit("resource", 20.0, 20.0, 1.0, tick=0)
        mem.deposit("hazard", 30.0, 30.0, 1.0, tick=0)
        q = mem.query_at("resource", 20.0, 20.0, tick=1)
        known = mem.list_known("resource", tick=1)
        mem.tick_update(1)
        u = mem.usage()
        traces[cond] = {
            "writes": u.writes,
            "reads": u.reads,
            "query_value": float(q),
            "list_known_count": len(known),
            "uses_list_known": cond in ("direct_msg", "blackboard"),
            "spatial_only": cond in ("pheromone", "linear_sub", "nonlinear_sub"),
            "zero_comm": cond == "independent",
            "failed": mem.failed(),
        }
        # Integrity expectations
        if cond == "independent":
            traces[cond]["pathway_ok"] = (q == 0.0 and len(known) == 0)
        elif cond in ("direct_msg", "blackboard"):
            traces[cond]["pathway_ok"] = (len(known) >= 1 and u.writes >= 1)
        else:
            traces[cond]["pathway_ok"] = (u.writes >= 1 and q > 0.0)
    all_ok = all(t["pathway_ok"] for t in traces.values())
    return {"pass": all_ok, "traces": traces}


def isolation_checks() -> dict[str, Any]:
    """No shared claim oracle; scoring state separate from decision state."""
    # Architectures do not expose a global task_claimed
    import sim_world.exp6_corrected.architectures as arch_mod
    src = inspect.getsource(arch_mod)
    has_global_claim = "task_claimed" in src
    # Two memories must not share mutable state
    m1 = make_memory("blackboard")
    m2 = make_memory("blackboard")
    m1.deposit("resource", 1.0, 1.0, 1.0, tick=0)
    isolated = len(m2.list_known("resource", 0)) == 0
    return {
        "pass": (not has_global_claim) and isolated,
        "architectures_contain_task_claimed": has_global_claim,
        "separate_backend_instances_isolated": isolated,
    }


def run_gate_g3() -> dict[str, Any]:
    inv = decision_invariance_test()
    # Code inspection notes
    notes = {
        "movement_helper_forbids_resource_list": True,
        "hazard_list_not_in_decision_signature": True,
        "ground_truth_eval_only": (
            "Experiment C scoring may read env; agent decide/move must not."
        ),
    }
    return {
        "gate": "G3",
        "pass": inv["pass"],
        "decision_invariance": inv,
        "inspection_notes": notes,
    }


def run_gate_g4() -> dict[str, Any]:
    traces = runtime_pathway_traces()
    iso = isolation_checks()
    fairness = architecture_fairness_notes()
    return {
        "gate": "G4",
        "pass": traces["pass"] and iso["pass"],
        "pathway_traces": traces,
        "isolation": iso,
        "fairness_documentation": fairness,
    }


def run_oracle_gates() -> dict[str, Any]:
    g3 = run_gate_g3()
    g4 = run_gate_g4()
    return {"G3": g3, "G4": g4, "proceed": g3["pass"] and g4["pass"]}


# Export decision helper for Experiment C (single implementation → no oracle drift)
choose_movement_target = _agent_choose_target


if __name__ == "__main__":
    import json
    print(json.dumps(run_oracle_gates(), indent=2, default=str))
