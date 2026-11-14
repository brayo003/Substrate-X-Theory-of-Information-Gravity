"""Experiment C — Agentic coordination (Gates G7–G9 / Claim D).

Three independent task classes in separate trial modes:
  C1 resource discovery, C2 hazard avoidance, C3 task allocation.

No ground-truth coordinate querying in decisions.
No shared task_claimed oracle in the decision pathway.
Hazard avoidance counted only for pre-entry diversions.
Duplicate work = unique redundant exploration events (not per-tick dwell).
"""
from __future__ import annotations

import math
import os
import sys
from dataclasses import dataclass, field
from typing import Any, Literal

import numpy as np

_HERE = os.path.dirname(os.path.abspath(__file__))
_SIM = os.path.dirname(_HERE)
_PARENT = os.path.dirname(_SIM)
for _p in (_PARENT, _SIM):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from sim_world.exp6_corrected import config as cfg
from sim_world.exp6_corrected.architectures import make_memory, MemoryBackend
from sim_world.exp6_corrected.oracle_tests import choose_movement_target


@dataclass
class ResourceSite:
    site_id: int
    x: float
    y: float
    tick_available: int
    tick_expires: int


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
    n_agents_needed: int


@dataclass
class Agent:
    agent_id: int
    x: float
    y: float
    energy: float = 1.0
    # Private local memory (independent condition + all conditions' sensor cache)
    known_resources: set[int] = field(default_factory=set)
    known_hazards: list[tuple[float, float, float]] = field(default_factory=list)
    claimed_tasks_local: set[int] = field(default_factory=set)
    last_resource_visit: dict[int, int] = field(default_factory=dict)


def generate_environment(seed: int, n_ticks: int = cfg.EXP_C_TICKS) -> dict[str, Any]:
    rng = np.random.default_rng(seed + 9000)
    resources = []
    for i in range(cfg.N_RESOURCES):
        t0 = int(rng.integers(0, n_ticks // 2))
        dur = int(rng.integers(10, 35))
        resources.append(ResourceSite(
            i, float(rng.uniform(3, cfg.GRID_X - 3)), float(rng.uniform(3, cfg.GRID_Y - 3)),
            t0, min(t0 + dur, n_ticks),
        ))
    hazards = []
    for i in range(cfg.N_HAZARDS):
        t0 = int(rng.integers(5, n_ticks // 2))
        dur = int(rng.integers(8, 30))
        hazards.append(HazardZone(
            i, float(rng.uniform(5, cfg.GRID_X - 5)), float(rng.uniform(5, cfg.GRID_Y - 5)),
            float(rng.uniform(3, 7)), t0, min(t0 + dur, n_ticks),
        ))
    tasks = []
    for i in range(cfg.N_TASK_SLOTS):
        t0 = int(rng.integers(5, n_ticks - 15))
        dur = int(rng.integers(10, 25))
        tasks.append(TaskSlot(
            i, float(rng.uniform(5, cfg.GRID_X - 5)), float(rng.uniform(5, cfg.GRID_Y - 5)),
            t0, min(t0 + dur, n_ticks), int(rng.choice([1, 2])),
        ))
    return {"resources": resources, "hazards": hazards, "task_slots": tasks}


def _make_agents(seed: int) -> list[Agent]:
    rng = np.random.default_rng(seed + 1000)
    return [
        Agent(i, float(rng.uniform(2, cfg.GRID_X - 2)), float(rng.uniform(2, cfg.GRID_Y - 2)),
              float(rng.uniform(0.7, 1.0)))
        for i in range(cfg.N_AGENTS)
    ]


def _in_hazard(ax, ay, hz: HazardZone) -> bool:
    return math.hypot(ax - hz.x, ay - hz.y) <= hz.radius


def _move_toward(agent: Agent, tx, ty, speed, rng):
    dx, dy = tx - agent.x, ty - agent.y
    d = math.hypot(dx, dy)
    if d < 0.01:
        return
    step = min(speed, d)
    agent.x = float(np.clip(agent.x + (dx / d) * step + rng.uniform(-0.2, 0.2), 0, cfg.GRID_X))
    agent.y = float(np.clip(agent.y + (dy / d) * step + rng.uniform(-0.2, 0.2), 0, cfg.GRID_Y))


def _move_random(agent: Agent, speed, rng):
    ang = float(rng.uniform(0, 2 * math.pi))
    step = float(rng.uniform(0, speed))
    agent.x = float(np.clip(agent.x + step * math.cos(ang), 0, cfg.GRID_X))
    agent.y = float(np.clip(agent.y + step * math.sin(ang), 0, cfg.GRID_Y))


def _hazard_avoid_target(agent: Agent, mem: MemoryBackend, tick: int,
                         proposed: tuple[float, float] | None) -> tuple[float, float] | None:
    """
    Pre-entry avoidance: if proposed step or current heading enters a known hazard
    signal region, divert perpendicular / away. Uses architecture hazard query and
    agent's private known_hazards — never the full GT hazard list.
    """
    # Gather known hazard centres from private memory + architecture
    hazards = list(agent.known_hazards)
    for rec in mem.list_known("hazard", tick):
        hazards.append((float(rec["x"]), float(rec["y"]), float(rec.get("value", 4.0))))

    # Spatial signal: if hazard query high at proposed point, divert
    if proposed is None:
        return None
    px, py = proposed
    hz_sig = mem.query_at("hazard", px, py, tick)
    danger = hz_sig > 0.25
    for hx, hy, hr in hazards:
        if math.hypot(px - hx, py - hy) <= hr + 1.0:
            danger = True
            break
    if not danger:
        return proposed
    # Divert: move away from nearest known hazard centre
    if hazards:
        hx, hy, _ = min(hazards, key=lambda h: math.hypot(agent.x - h[0], agent.y - h[1]))
        dx, dy = agent.x - hx, agent.y - hy
        d = math.hypot(dx, dy) or 1.0
        return agent.x + 3.0 * dx / d, agent.y + 3.0 * dy / d
    # Gradient descent on hazard field
    gx, gy = mem.sample_gradient("hazard", agent.x, agent.y, tick)
    return agent.x - 3.0 * gx, agent.y - 3.0 * gy


def run_trial_c(
    seed: int,
    condition: str,
    mode: Literal["resource", "hazard", "allocation", "all"] = "all",
    n_ticks: int = cfg.EXP_C_TICKS,
    env: dict | None = None,
) -> dict[str, Any]:
    if env is None:
        env = generate_environment(seed, n_ticks)
    resources: list[ResourceSite] = env["resources"]
    hazards: list[HazardZone] = env["hazards"]
    task_slots: list[TaskSlot] = env["task_slots"]

    rng_move = np.random.default_rng(seed + 2000)
    agents = _make_agents(seed)
    mem = make_memory(condition)

    # --- Evaluation-only ledgers (NOT readable by agents) ---
    eval_resources_found: set[int] = set()
    # Unique redundant visits: (agent_id, site_id) first revisit after another agent found it
    unique_dup_visits: set[tuple[int, int]] = set()
    agents_per_resource: dict[int, set[int]] = {r.site_id: set() for r in resources}

    hazard_exposure_ticks = 0
    unique_hazard_entries: set[tuple[int, int]] = set()  # (agent_id, hz_id)
    avoided_crossings = 0
    false_positive_avoidances = 0
    detour_steps = 0

    # Task evaluation ledger (ground truth conflicts) — agents cannot read this
    eval_assignees: dict[int, list[int]] = {}
    task_completions = 0
    duplicate_assignments = 0
    coordination_writes = 0

    solver_failed = False

    for tick in range(n_ticks):
        mem.tick_update(tick)
        if mem.failed():
            solver_failed = True
            break

        active_res = [r for r in resources if r.tick_available <= tick < r.tick_expires]
        active_hz = [h for h in hazards if h.tick_start <= tick < h.tick_end]
        open_tasks = [t for t in task_slots if t.tick_open <= tick < t.tick_close]

        for agent in agents:
            # ---- Sensing (local only) ----
            local_obs = []
            if mode in ("resource", "all"):
                for r in active_res:
                    if math.hypot(agent.x - r.x, agent.y - r.y) <= cfg.SENSOR_RADIUS:
                        local_obs.append({"x": r.x, "y": r.y, "value": 1.0, "site_id": r.site_id})
                        # First discovery
                        if r.site_id not in eval_resources_found:
                            eval_resources_found.add(r.site_id)
                            mem.deposit("resource", r.x, r.y, cfg.SUB_DEPOSIT_AMP, tick)
                            coordination_writes += 1
                        agents_per_resource[r.site_id].add(agent.agent_id)
                        # Unique duplicate: this agent visits a resource already found
                        # by someone, and this is a new (agent, site) pair — not dwell
                        prev = agent.last_resource_visit.get(r.site_id)
                        if r.site_id in eval_resources_found and agent.agent_id not in (
                            # if more than one agent has visited, count this agent's first visit as potential dup
                            set()
                        ):
                            if len(agents_per_resource[r.site_id]) > 1:
                                # Count at most once per (agent, site)
                                unique_dup_visits.add((agent.agent_id, r.site_id))
                        # Dwell tracking: update last visit; do NOT increment dup each tick
                        agent.last_resource_visit[r.site_id] = tick
                        agent.known_resources.add(r.site_id)

            if mode in ("hazard", "all"):
                for h in active_hz:
                    if math.hypot(agent.x - h.x, agent.y - h.y) <= cfg.SENSOR_RADIUS:
                        agent.known_hazards.append((h.x, h.y, h.radius))
                        mem.deposit("hazard", h.x, h.y, cfg.SUB_DEPOSIT_AMP, tick)
                        coordination_writes += 1

            if mode in ("allocation", "all"):
                for ts in open_tasks:
                    if math.hypot(agent.x - ts.x, agent.y - ts.y) <= cfg.SENSOR_RADIUS * 1.5:
                        # Architecture-specific claim check — NO global claim dict for decisions
                        already = False
                        if condition in ("direct_msg", "blackboard"):
                            known = mem.list_known("claim", tick)
                            claimants = [k for k in known
                                         if int((k.get("meta") or {}).get("slot_id", -1)) == ts.slot_id]
                            # Also match by value encoding
                            claimants += [k for k in known if int(k.get("value", -99)) == ts.slot_id]
                            n_claim = len({id(c) for c in claimants})  # rough
                            n_claim = len(claimants)
                            if n_claim >= ts.n_agents_needed:
                                already = True
                            # Self already claimed?
                            if ts.slot_id in agent.claimed_tasks_local:
                                already = True
                        elif condition == "independent":
                            if ts.slot_id in agent.claimed_tasks_local:
                                already = True
                        else:
                            # Spatial: if claim signal strong and agent already claimed locally
                            sig = mem.query_at("claim", ts.x, ts.y, tick)
                            if ts.slot_id in agent.claimed_tasks_local:
                                already = True
                            elif sig > 1.5 and ts.n_agents_needed == 1:
                                already = True  # likely taken

                        if not already and ts.slot_id not in agent.claimed_tasks_local:
                            agent.claimed_tasks_local.add(ts.slot_id)
                            mem.deposit("claim", ts.x, ts.y, float(ts.slot_id), tick,
                                        meta={"slot_id": ts.slot_id, "agent": agent.agent_id})
                            mem.deposit("task", ts.x, ts.y, 1.0, tick,
                                        meta={"slot_id": ts.slot_id})
                            coordination_writes += 1
                            # Evaluation ledger
                            eval_assignees.setdefault(ts.slot_id, []).append(agent.agent_id)
                            assigned = eval_assignees[ts.slot_id]
                            if len(assigned) == ts.n_agents_needed:
                                task_completions += 1
                            elif ts.n_agents_needed == 1 and len(assigned) > 1:
                                duplicate_assignments += 1

            # ---- Movement (no GT resource list) ----
            proposed = None
            if mode in ("resource", "all"):
                proposed = choose_movement_target(mem, agent.x, agent.y, tick, local_obs)
            if mode in ("allocation", "all") and proposed is None:
                # Move toward known tasks via architecture
                known_t = mem.list_known("task", tick)
                if known_t:
                    rec = known_t[0]
                    proposed = (float(rec["x"]), float(rec["y"]))
                else:
                    gx, gy = mem.sample_gradient("task", agent.x, agent.y, tick)
                    if math.hypot(gx, gy) > 1e-4:
                        proposed = (agent.x + 2 * gx, agent.y + 2 * gy)

            # Hazard avoidance (pre-entry)
            if mode in ("hazard", "all"):
                diverted = _hazard_avoid_target(agent, mem, tick, proposed)
                # Would proposed enter an actual active hazard? (eval only)
                would_enter = False
                if proposed is not None:
                    for h in active_hz:
                        if _in_hazard(proposed[0], proposed[1], h):
                            would_enter = True
                            break
                if diverted is not None and diverted != proposed and would_enter:
                    avoided_crossings += 1
                    detour_steps += 1
                    proposed = diverted
                elif diverted is not None and diverted != proposed and not would_enter:
                    # Diverted due to false-positive hazard signal
                    if mem.query_at("hazard", *(proposed or (agent.x, agent.y)), tick) > 0.25:
                        false_positive_avoidances += 1
                        detour_steps += 1
                    proposed = diverted

            # Execute move
            if proposed is not None:
                _move_toward(agent, proposed[0], proposed[1], cfg.AGENT_SPEED, rng_move)
            else:
                _move_random(agent, cfg.AGENT_SPEED, rng_move)

            # ---- Exposure measurement (independent of avoidance decision) ----
            if mode in ("hazard", "all"):
                for h in active_hz:
                    if _in_hazard(agent.x, agent.y, h):
                        hazard_exposure_ticks += 1
                        unique_hazard_entries.add((agent.agent_id, h.hz_id))

    # Metrics
    n_found = len(eval_resources_found)
    # Unique duplicate visits: agents visiting a resource that multiple agents visited
    # Exclude the "first" discoverer conceptually: count agents beyond the first per resource
    multi_agent_visits = sum(max(0, len(s) - 1) for s in agents_per_resource.values() if s)
    dup_fraction = multi_agent_visits / max(n_found, 1)

    unassigned = sum(1 for t in task_slots if t.slot_id not in eval_assignees)

    out = {
        "seed": seed,
        "condition": condition,
        "mode": mode,
        "failed": solver_failed,
        "solver_failed": solver_failed,
        "usage": mem.usage().to_dict(),
        # C1
        "res_discovery_rate": n_found / max(len(resources), 1),
        "resources_found": n_found,
        "unique_dup_visits": multi_agent_visits,
        "dup_work_fraction": dup_fraction,
        "agents_per_resource_mean": float(np.mean([len(s) for s in agents_per_resource.values()])),
        # C2
        "hazard_exposure_ticks": hazard_exposure_ticks,
        "unique_hazard_entries": len(unique_hazard_entries),
        "avoided_crossings": avoided_crossings,
        "false_positive_avoidances": false_positive_avoidances,
        "detour_steps": detour_steps,
        # C3
        "task_completion_rate": task_completions / max(len(task_slots), 1),
        "duplicate_assignments": duplicate_assignments,
        "unassigned_tasks": unassigned,
        "coordination_writes": coordination_writes,
    }
    return out


def run_experiment_c(seeds: list[int], conditions: list[str] | None = None,
                     verbose: bool = True) -> dict[str, Any]:
    conditions = list(conditions or cfg.CONDITIONS)
    # Run each task class separately (mandatory)
    modes = ("resource", "hazard", "allocation")
    trials = []
    total = len(seeds) * len(conditions) * len(modes)
    done = 0
    for seed in seeds:
        env = generate_environment(seed, cfg.EXP_C_TICKS)
        for cond in conditions:
            for mode in modes:
                trials.append(run_trial_c(seed, cond, mode=mode, env=env))
                done += 1
                if verbose and done % 20 == 0:
                    print(f"  ExpC {done}/{total}")

    summary: dict[str, Any] = {}
    for cond in conditions:
        summary[cond] = {}
        for mode in modes:
            subset = [t for t in trials
                      if t["condition"] == cond and t["mode"] == mode and not t.get("failed")]
            failed = [t for t in trials
                      if t["condition"] == cond and t["mode"] == mode and t.get("failed")]
            if not subset:
                summary[cond][mode] = {"n": 0, "n_failed": len(failed)}
                continue
            keys = {
                "resource": ["res_discovery_rate", "dup_work_fraction", "unique_dup_visits"],
                "hazard": ["hazard_exposure_ticks", "unique_hazard_entries",
                           "avoided_crossings", "false_positive_avoidances", "detour_steps"],
                "allocation": ["task_completion_rate", "duplicate_assignments",
                               "unassigned_tasks", "coordination_writes"],
            }[mode]
            s = {"n": len(subset), "n_failed": len(failed)}
            for k in keys:
                vals = [t[k] for t in subset]
                s[f"{k}_mean"] = float(np.mean(vals))
                s[f"{k}_std"] = float(np.std(vals, ddof=1)) if len(vals) > 1 else 0.0
            summary[cond][mode] = s

    # Evidence-based gates (code existence alone is insufficient)
    res_ok = any(
        summary.get(c, {}).get("resource", {}).get("res_discovery_rate_mean", 0) > 0
        for c in conditions
    )
    # G8 requires actual pre-entry diversions under hazard info, not merely
    # that exposure is measured separately. Zero avoided crossings → FAIL.
    avoid_means = [
        summary.get(c, {}).get("hazard", {}).get("avoided_crossings_mean", 0.0)
        for c in conditions
    ]
    exposure_means = [
        summary.get(c, {}).get("hazard", {}).get("hazard_exposure_ticks_mean", 0.0)
        for c in conditions
    ]
    any_avoid = any(a > 0 for a in avoid_means)
    # Architecture differentiation on exposure (optional signal of policy effect)
    exposure_varies = (max(exposure_means) - min(exposure_means)) > 1e-6 if exposure_means else False

    task_ok = any(
        summary.get(c, {}).get("allocation", {}).get("task_completion_rate_mean", 0) > 0
        for c in conditions
    )

    g7 = {
        "pass_candidate": bool(res_ok),
        "note": (
            "Metrics from eval ledger; decisions use sensor/architecture only "
            "(no GT resource list in choose_movement_target)."
        ),
        "any_discovery_observed": bool(res_ok),
    }
    g8 = {
        "pass_candidate": bool(any_avoid),
        "note": (
            "Avoidance counted only for pre-entry diversions; exposure measured "
            "independently. PASS requires observed avoided_crossings > 0."
        ),
        "avoided_crossings_by_condition": {
            c: summary.get(c, {}).get("hazard", {}).get("avoided_crossings_mean", 0.0)
            for c in conditions
        },
        "exposure_identical_across_conditions": not exposure_varies,
        "any_pre_entry_avoidance_observed": bool(any_avoid),
    }
    g9 = {
        "pass_candidate": bool(task_ok),
        "note": "No shared task_claimed in decision pathway; claims via architecture only",
        "any_task_completion_observed": bool(task_ok),
    }

    return {
        "experiment": "C_agentic_coordination",
        "modes": list(modes),
        "trials": trials,
        "summary": summary,
        "g7_notes": g7,
        "g8_notes": g8,
        "g9_notes": g9,
        "n_seeds": len(seeds),
    }
