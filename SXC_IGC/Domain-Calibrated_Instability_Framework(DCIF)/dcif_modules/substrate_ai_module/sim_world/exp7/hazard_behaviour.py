"""Track A — Hazard discoverer→recipient behavioural utility (Gates T3–T6)."""
from __future__ import annotations

import math
from typing import Any, Literal

import numpy as np

from sim_world.exp7 import config as cfg
from sim_world.exp7.memory import make_memory
from sim_world.exp7.integrity import recipient_decide


# Corridor geometry (fixed; paired across architectures via seed only for noise)
START = (5.0, 20.0)
GOAL = (45.0, 20.0)
HAZARD_CENTER = (25.0, 20.0)
DETOUR_WP = (25.0, 40.0)


def _in_hazard(x, y, hx=HAZARD_CENTER[0], hy=HAZARD_CENTER[1],
               hr=cfg.HAZARD_RADIUS) -> bool:
    return math.hypot(x - hx, y - hy) <= hr


def _move_toward(x, y, tx, ty, speed, rng) -> tuple[float, float]:
    dx, dy = tx - x, ty - y
    d = math.hypot(dx, dy)
    if d < 1e-6:
        return x, y
    step = min(speed, d)
    nx = float(np.clip(x + (dx / d) * step + rng.uniform(-0.05, 0.05), 0, cfg.GRID_X))
    ny = float(np.clip(y + (dy / d) * step + rng.uniform(-0.05, 0.05), 0, cfg.GRID_Y))
    return nx, ny


def _discoverer_run(mem, rng, deposit: bool) -> dict[str, Any]:
    """Agent A walks the straight corridor, senses hazard, optionally deposits, leaves."""
    x, y = START
    discovered = False
    deposit_tick = None
    for tick in range(40):
        mem.tick_update(tick)
        if mem.failed():
            return {"failed": True, "discovered": False}
        if (not discovered) and math.hypot(x - HAZARD_CENTER[0], y - HAZARD_CENTER[1]) <= cfg.SENSOR_RADIUS:
            discovered = True
            if deposit:
                mem.deposit("hazard", HAZARD_CENTER[0], HAZARD_CENTER[1],
                            cfg.HAZARD_DEPOSIT_AMP, tick)
                deposit_tick = tick
        x, y = _move_toward(x, y, GOAL[0], GOAL[1], cfg.AGENT_SPEED, rng)
        if math.hypot(x - GOAL[0], y - GOAL[1]) < 2.0:
            break
    return {
        "failed": False,
        "discovered": discovered,
        "deposit_tick": deposit_tick,
        "deposited": deposit and discovered,
        "end_xy": (x, y),
    }


def _evolve(mem, n_ticks: int, start_tick: int = 0) -> bool:
    for t in range(start_tick, start_tick + n_ticks):
        mem.tick_update(t)
        if mem.failed():
            return False
    return True


def _clear_kind(mem, kind: str = "hazard") -> None:
    """Remove architecture-held hazard info (control replacement / refresh)."""
    if hasattr(mem, "_msgs"):
        mem._msgs = [m for m in mem._msgs if m.get("kind") != kind]
    if hasattr(mem, "_entries"):
        mem._entries = [e for e in mem._entries if e.get("kind") != kind]
    if hasattr(mem, "_grids") and kind in getattr(mem, "_grids", {}):
        mem._grids[kind][:] = 0.0
    if hasattr(mem, "field") and hasattr(mem, "nonlinear"):
        # Re-init substrate field (controls replace, do not stack on truth)
        from sim_world.exp7.memory import Exp7SubstrateMemory
        fresh = Exp7SubstrateMemory(
            nonlinear=bool(mem.nonlinear),
            c=float(mem.prop.c_nominal),
            name=mem.name,
        )
        mem.field = fresh.field
        mem._failed = False


def _refresh_share(mem, condition: str, hx: float, hy: float, tick: int) -> None:
    """
    After discoverer finishes, stamp a fresh share at `tick` so TTL/stale clocks
    measure only the intentional post-share delay (not discoverer travel time).

    Spatial media keep the discoverer's field; structured media get a fresh write.
    """
    if condition in ("direct_msg", "blackboard"):
        _clear_kind(mem, "hazard")
        mem.deposit("hazard", hx, hy, cfg.HAZARD_DEPOSIT_AMP, tick)
    elif condition == "independent":
        return
    # pheromone / substrates: field already holds discoverer deposit; no re-stamp


InfoMode = Literal[
    "A_no_discovery",
    "B_withheld",
    "C_immediate",
    "D_delay5",
    "E_delay15",
    "F_disconnect",
    "CTRL_correct",
    "CTRL_incorrect",
    "CTRL_random",
    "CTRL_ablated",
]


def run_hazard_trial(
    seed: int,
    condition: str,
    info_mode: InfoMode,
) -> dict[str, Any]:
    """
    Full causal chain trial.
    Evaluation layer alone knows HAZARD_CENTER for scoring exposure.

    Timing model:
      discoverer deposits → optional share refresh → age=`delay` → recipient decides.
    TTL/stale therefore reflect persistence under delay, not travel-time artifacts.
    """
    rng = np.random.default_rng(seed + 77)
    mem = make_memory(condition)

    # --- Discoverer phase ---
    # Discovery deposit for all modes except pure no-discovery baseline.
    # Control modes that replace info still need discoverer to establish discovery
    # happened; their injectable content is applied after clear.
    do_deposit = info_mode not in ("A_no_discovery",)
    if info_mode in ("CTRL_incorrect", "CTRL_random"):
        # Discoverer still finds hazard, but shared content will be replaced
        do_deposit = True
    disc = _discoverer_run(mem, rng, deposit=do_deposit)
    if disc.get("failed"):
        return {"seed": seed, "condition": condition, "info_mode": info_mode,
                "failed": True, "solver_failed": True}

    readout_enabled = info_mode not in ("B_withheld", "CTRL_ablated", "A_no_discovery")

    delay = {
        "A_no_discovery": 0,
        "B_withheld": 0,
        "C_immediate": 0,
        "D_delay5": 5,
        "E_delay15": 15,
        "F_disconnect": 20,
        "CTRL_correct": 5,
        "CTRL_incorrect": 5,
        "CTRL_random": 5,
        "CTRL_ablated": 5,
    }[info_mode]

    # Share stamp at tick 0 relative clock; then age by `delay` only.
    share_tick = 0
    if info_mode == "A_no_discovery":
        pass
    elif info_mode == "B_withheld":
        # Deposit exists but recipient readout disabled — no refresh needed
        pass
    elif info_mode == "CTRL_incorrect":
        _clear_kind(mem, "hazard")
        mem.deposit("hazard", 25.0, 40.0, cfg.HAZARD_DEPOSIT_AMP, share_tick)
    elif info_mode == "CTRL_random":
        _clear_kind(mem, "hazard")
        rx = float(rng.uniform(5, 45))
        ry = float(rng.uniform(5, 45))
        # Keep random off the true corridor center so false info is distinct
        while math.hypot(rx - HAZARD_CENTER[0], ry - HAZARD_CENTER[1]) < 8.0:
            rx = float(rng.uniform(5, 45))
            ry = float(rng.uniform(5, 45))
        mem.deposit("hazard", rx, ry, cfg.HAZARD_DEPOSIT_AMP, share_tick)
    elif info_mode == "CTRL_correct":
        _clear_kind(mem, "hazard")
        mem.deposit("hazard", HAZARD_CENTER[0], HAZARD_CENTER[1],
                    cfg.HAZARD_DEPOSIT_AMP, share_tick)
    elif info_mode == "CTRL_ablated":
        # Keep true deposit in architecture; recipient cannot read it
        _refresh_share(mem, condition, HAZARD_CENTER[0], HAZARD_CENTER[1], share_tick)
    else:
        # C/D/E/F: refresh structured share; spatial keep discoverer field
        if disc.get("deposited"):
            _refresh_share(mem, condition, HAZARD_CENTER[0], HAZARD_CENTER[1], share_tick)

    if delay > 0:
        if not _evolve(mem, delay, start_tick=share_tick + 1):
            return {"seed": seed, "condition": condition, "info_mode": info_mode,
                    "failed": True, "solver_failed": True}

    decision_tick = share_tick + delay + 1
    decision = recipient_decide(
        mem, START[0], START[1], decision_tick, GOAL, local_obs=[],
        readout_enabled=readout_enabled,
    )

    # Recovery measured BEFORE any movement into hazard
    recovery_signal = decision["hazard_signal"] if readout_enabled else 0.0
    recovered = recovery_signal >= 0.25
    chose_detour = bool(decision["chose_detour"]) and readout_enabled

    # Execute path
    x, y = START
    exposure_ticks = 0
    entered = False
    unique_entries = 0
    path_len = 0.0
    completed = False
    waypoints = [DETOUR_WP, GOAL] if chose_detour else [GOAL]
    wp_i = 0
    avoided = 0
    would_enter_if_direct = True
    if chose_detour and would_enter_if_direct:
        avoided = 1  # pre-commitment diversion before exposure

    false_positive_avoid = 0
    if chose_detour and info_mode in ("CTRL_incorrect", "CTRL_random", "A_no_discovery"):
        false_positive_avoid = 1

    for step in range(80):
        mem.tick_update(decision_tick + 1 + step)
        if mem.failed():
            return {"seed": seed, "condition": condition, "info_mode": info_mode,
                    "failed": True, "solver_failed": True,
                    "usage": mem.usage().to_dict()}
        tx, ty = waypoints[wp_i]
        nx, ny = _move_toward(x, y, tx, ty, cfg.AGENT_SPEED, rng)
        path_len += math.hypot(nx - x, ny - y)
        x, y = nx, ny
        if _in_hazard(x, y):
            exposure_ticks += 1
            if not entered:
                entered = True
                unique_entries += 1
        if math.hypot(x - tx, y - ty) < 2.0:
            wp_i += 1
            if wp_i >= len(waypoints):
                completed = True
                break

    straight_len = math.hypot(GOAL[0] - START[0], GOAL[1] - START[1])
    detour_extra = max(0.0, path_len - straight_len)
    detour_cost = cfg.DETOUR_LENGTH_PENALTY_WEIGHT * detour_extra

    return {
        "seed": seed,
        "condition": condition,
        "info_mode": info_mode,
        "failed": False,
        "solver_failed": False,
        "discoverer_discovered": disc["discovered"],
        "discoverer_deposited": disc.get("deposited", False),
        "delay": delay,
        "decision_tick": decision_tick,
        "readout_enabled": readout_enabled,
        "recovery_signal": float(recovery_signal),
        "recovered_before_entry": bool(recovered),
        "chose_detour": bool(chose_detour),
        "route_modified": bool(chose_detour),
        "hazard_entry_events": int(unique_entries),
        "hazard_exposure_ticks": int(exposure_ticks),
        "avoided_crossings": int(avoided if exposure_ticks == 0 else 0),
        "false_positive_avoidance": int(false_positive_avoid if chose_detour else 0),
        "path_length": float(path_len),
        "detour_extra": float(detour_extra),
        "detour_cost": float(detour_cost),
        "completed": bool(completed),
        "usage": mem.usage().to_dict(),
    }


def run_track_a(seeds: list[int], verbose: bool = True) -> dict[str, Any]:
    modes = list(cfg.TRACK_A_DELAYS.keys()) + [
        "CTRL_correct", "CTRL_incorrect", "CTRL_random", "CTRL_ablated",
    ]
    trials = []
    total = len(seeds) * len(cfg.CONDITIONS) * len(modes)
    done = 0
    for seed in seeds:
        for cond in cfg.CONDITIONS:
            for mode in modes:
                trials.append(run_hazard_trial(seed, cond, mode))  # type: ignore
                done += 1
                if verbose and done % 40 == 0:
                    print(f"  TrackA {done}/{total}")

    summary: dict[str, Any] = {}
    for cond in cfg.CONDITIONS:
        summary[cond] = {}
        for mode in modes:
            sub = [t for t in trials
                   if t["condition"] == cond and t["info_mode"] == mode and not t.get("failed")]
            failed = sum(1 for t in trials
                         if t["condition"] == cond and t["info_mode"] == mode and t.get("failed"))
            if not sub:
                summary[cond][mode] = {"n": 0, "n_failed": failed}
                continue
            def m(key):
                return float(np.mean([t[key] for t in sub]))
            summary[cond][mode] = {
                "n": len(sub),
                "n_failed": failed,
                "recovery_rate": m("recovered_before_entry"),
                "detour_rate": m("chose_detour"),
                "exposure_mean": m("hazard_exposure_ticks"),
                "avoided_mean": m("avoided_crossings"),
                "entry_mean": m("hazard_entry_events"),
                "fp_avoid_mean": m("false_positive_avoidance"),
                "detour_extra_mean": m("detour_extra"),
                "completion_mean": m("completed"),
            }

    # Gate evaluation (evidence-based)
    # Focus on nonlinear_sub for capability; also require at least one architecture works
    def gate_for(cond: str) -> dict[str, Any]:
        s = summary.get(cond, {})
        noinfo = s.get("A_no_discovery", {})
        imm = s.get("C_immediate", {})
        d5 = s.get("D_delay5", {})
        d15 = s.get("E_delay15", {})
        disc = s.get("F_disconnect", {})
        correct = s.get("CTRL_correct", {})
        incorrect = s.get("CTRL_incorrect", {})
        random = s.get("CTRL_random", {})
        ablated = s.get("CTRL_ablated", {})

        t3 = (imm.get("recovery_rate", 0) > 0.5) if imm else False
        # T4: correct info increases detour vs noinfo; incorrect/random not same success pattern
        t4 = False
        if imm and noinfo and correct and incorrect and random:
            t4 = (
                correct.get("detour_rate", 0) > noinfo.get("detour_rate", 1) + 0.2
                and correct.get("exposure_mean", 99) < noinfo.get("exposure_mean", 0) - 0.5
                and incorrect.get("avoided_mean", 1) < correct.get("avoided_mean", 0) + 0.1
            )
            # incorrect/random should not match correct avoidance success
            t4 = t4 and (
                correct.get("avoided_mean", 0) > incorrect.get("avoided_mean", 1) + 0.2
                or correct.get("exposure_mean", 99) < incorrect.get("exposure_mean", 0) - 0.5
            )
        t5 = False
        if imm and noinfo:
            t5 = (
                imm.get("exposure_mean", 99) < noinfo.get("exposure_mean", 0) - 0.5
                and imm.get("completion_mean", 0) >= 0.8 * max(noinfo.get("completion_mean", 0), 0.5)
                and imm.get("avoided_mean", 0) > 0.3
            )
        # T6: delayed / disconnect still reduce exposure vs noinfo
        delayed_ok = False
        if noinfo:
            for blk in (d5, d15, disc):
                if blk and blk.get("exposure_mean", 99) < noinfo.get("exposure_mean", 0) - 0.5:
                    delayed_ok = True
                    break
        only_immediate = (
            imm.get("exposure_mean", 99) < noinfo.get("exposure_mean", 0) - 0.5
            and not delayed_ok
        ) if imm and noinfo else False
        return {
            "T3_recovery": bool(t3),
            "T4_behavioural_response": bool(t4),
            "T5_utility": bool(t5),
            "T6_persistent_memory": bool(delayed_ok),
            "only_immediate_communication": bool(only_immediate),
            "ablated_detour_rate": ablated.get("detour_rate", None),
        }

    gates_by_cond = {c: gate_for(c) for c in cfg.CONDITIONS}
    # Overall Track A gates: PASS if any architecture demonstrates the chain;
    # nonlinear-specific claims handled in Track B.
    t3 = any(g["T3_recovery"] for g in gates_by_cond.values())
    t4 = any(g["T4_behavioural_response"] for g in gates_by_cond.values())
    t5 = any(g["T5_utility"] for g in gates_by_cond.values())
    t6 = any(g["T6_persistent_memory"] for g in gates_by_cond.values())

    return {
        "track": "A_hazard_behaviour",
        "trials": trials,
        "summary": summary,
        "gates_by_condition": gates_by_cond,
        "T3": {"pass": t3, "note": "Recipient recovers hazard info before entry"},
        "T4": {"pass": t4, "note": "Correct info changes route; controls differ"},
        "T5": {"pass": t5, "note": "Exposure reduced with completion preserved"},
        "T6": {"pass": t6, "note": "Delayed/disconnected info still useful"},
        "n_seeds": len(seeds),
        "primary_endpoint": cfg.TRACK_A_PRIMARY,
    }
