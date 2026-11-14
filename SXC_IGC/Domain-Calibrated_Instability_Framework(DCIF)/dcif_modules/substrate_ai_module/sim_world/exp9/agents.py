"""Agent policies for Task 9 — no GT k*; discover via local obs + medium."""
from __future__ import annotations

import math
from typing import Any

import numpy as np

from sim_world.exp9 import config as cfg
from sim_world.exp9.env import (
    World, AgentState, sense_evidence, update_visited, move_toward,
)
from sim_world.exp9.field_backend import MediumBackend


def _explore_target(agent: AgentState, world: World, rng: np.random.Generator) -> tuple[float, float]:
    unvis = [i for i in range(len(world.landmarks)) if i not in agent.visited_landmarks]
    if unvis:
        i = int(rng.choice(unvis))
        return world.landmarks[i]
    i = int(rng.integers(0, len(world.landmarks)))
    lx, ly = world.landmarks[i]
    return lx + float(rng.normal(0, 3)), ly + float(rng.normal(0, 3))


def _commit_threshold(arch: str) -> float:
    if arch in ("nonlinear_sub", "hybrid", "ablation", "linear_sub"):
        return cfg.ACTIVATION_THRESH
    if arch == "pheromone":
        return cfg.PHER_COMMIT_THRESH
    return cfg.MSG_COMMIT_CONF


def _ensure_agent_aux(agent: AgentState) -> None:
    if not hasattr(agent, "hold_counts"):
        agent.hold_counts = {}  # type: ignore[attr-defined]
    if not hasattr(agent, "strong_obs_patches"):
        agent.strong_obs_patches = {}  # type: ignore[attr-defined]
    if not hasattr(agent, "deposited_landmarks"):
        agent.deposited_landmarks = set()  # type: ignore[attr-defined]
    if not hasattr(agent, "pending_deposits"):
        # landmark_id -> best obs confidence (carry of own local sensing)
        agent.pending_deposits = {}  # type: ignore[attr-defined]


def _msg_support(medium: MediumBackend, tick: int, landmark_id: int) -> tuple[float, int]:
    msgs = medium.list_messages(tick)
    confs = [m["confidence"] for m in msgs if m["landmark_id"] == landmark_id]
    if not confs:
        return 0.0, 0
    return float(np.mean(confs)), len(confs)


def agent_step(
    world: World,
    agent: AgentState,
    medium: MediumBackend,
    tick: int,
    rng: np.random.Generator,
    *,
    arch: str,
    ablation: str | None = None,
    deposit_amp: float | None = None,
    force_random_commit: bool = False,
    no_hysteresis: bool = False,
) -> dict[str, Any]:
    """One agent tick.

    Order (critical): read/commit on *already evolved* medium first, then deposit,
    then move. Prevents same-tick instantaneous peak ≥ θ (Task 8 readout_only confound).
    """
    events: dict[str, Any] = {"agent_id": agent.agent_id, "tick": tick}
    if agent.committed is not None or agent.disconnected:
        return events

    _ensure_agent_aux(agent)
    amp = cfg.DEP_AMP if deposit_amp is None else float(deposit_amp)
    update_visited(agent, world.landmarks)

    # ----- 1) Read + commit on post-evolution state -----
    readouts: dict[int, float] = {}
    msg_counts: dict[int, int] = {}
    if ablation != "readout_disabled" and not force_random_commit:
        for i, (lx, ly) in enumerate(world.landmarks):
            near = i in agent.visited_landmarks or math.hypot(agent.x - lx, agent.y - ly) <= cfg.SENSOR_RADIUS
            if not near:
                continue
            if arch in ("direct_msg", "blackboard"):
                mean_c, n_sup = _msg_support(medium, tick, i)
                readouts[i] = mean_c
                msg_counts[i] = n_sup
            elif arch == "hybrid":
                field_r = medium.query_at(lx, ly, tick)
                mean_c, n_sup = _msg_support(medium, tick, i)
                msg_counts[i] = n_sup
                readouts[i] = max(field_r, mean_c if n_sup >= cfg.MSG_MIN_SUPPORT else 0.0)
            elif arch == "independent":
                readouts[i] = float(agent.private_evidence.get(i, 0.0))
            else:
                readouts[i] = medium.query_at(lx, ly, tick)

    thr = _commit_threshold(arch if arch != "ablation" else "nonlinear_sub")
    if no_hysteresis:
        hold_need = 1
    elif arch in ("direct_msg", "blackboard"):
        hold_need = cfg.MSG_HOLD_TICKS
    elif arch == "pheromone":
        hold_need = cfg.PHER_HOLD_TICKS
    else:
        hold_need = cfg.COMMIT_HOLD_TICKS

    if force_random_commit or ablation == "fixed_random_policy":
        if tick > 20 and rng.random() < 0.05:
            agent.committed = int(rng.integers(0, len(world.landmarks)))
            agent.commit_tick = tick
            events["commit"] = agent.committed
            events["commit_mode"] = "random"
    elif arch == "independent":
        for lid, patches in getattr(agent, "strong_obs_patches", {}).items():
            if len(patches) >= cfg.INDEP_MIN_STRONG_OBS and lid in agent.visited_landmarks:
                agent.committed = lid
                agent.commit_tick = tick
                events["commit"] = lid
                events["commit_mode"] = "independent_multi_obs"
                break
    elif readouts:
        for lid, val in readouts.items():
            ok_support = True
            if arch in ("direct_msg", "blackboard"):
                ok_support = msg_counts.get(lid, 0) >= cfg.MSG_MIN_SUPPORT
            elif arch == "hybrid" and val < cfg.ACTIVATION_THRESH:
                # hybrid may commit on messages only with support, or on field latch
                ok_support = msg_counts.get(lid, 0) >= cfg.MSG_MIN_SUPPORT or val >= thr
            if val >= thr and lid in agent.visited_landmarks and ok_support:
                agent.hold_counts[lid] = agent.hold_counts.get(lid, 0) + 1  # type: ignore[attr-defined]
            else:
                agent.hold_counts[lid] = 0  # type: ignore[attr-defined]
        best_lid = max(readouts, key=lambda k: readouts[k])
        support_ok = True
        if arch in ("direct_msg", "blackboard"):
            support_ok = msg_counts.get(best_lid, 0) >= cfg.MSG_MIN_SUPPORT
        if (
            best_lid in agent.visited_landmarks
            and readouts[best_lid] >= thr
            and support_ok
            and agent.hold_counts.get(best_lid, 0) >= hold_need  # type: ignore[attr-defined]
        ):
            agent.committed = best_lid
            agent.commit_tick = tick
            events["commit"] = best_lid
            events["commit_readout"] = readouts[best_lid]
            events["commit_hold"] = agent.hold_counts.get(best_lid, 0)  # type: ignore[attr-defined]

    if agent.committed is not None:
        return events

    # ----- 2) Sense + queue pending deposits + optional write -----
    obs_list = sense_evidence(world, agent, tick, rng)
    for o in obs_list:
        lid = int(o["landmark_id"])
        prev = agent.private_evidence.get(lid, 0.0)
        agent.private_evidence[lid] = max(prev, float(o["obs"]))
        if float(o["obs"]) >= cfg.EVIDENCE_DETECT_THRESH:
            agent.strong_obs_patches.setdefault(lid, set()).add(int(o["patch_id"]))  # type: ignore[attr-defined]
            if cfg.ALLOW_EVIDENCE_CARRY:
                prev_p = agent.pending_deposits.get(lid, 0.0)  # type: ignore[attr-defined]
                agent.pending_deposits[lid] = max(prev_p, float(o["obs"]))  # type: ignore[attr-defined]

    deposited = False
    if agent.deposits_left > 0 and ablation != "deposit_disabled":
        # Prefer executing a pending carry at a nearby post (temporal coincidence aid)
        pending_items = sorted(
            agent.pending_deposits.items(),  # type: ignore[attr-defined]
            key=lambda kv: -kv[1],
        )
        for lid, conf in pending_items:
            if conf < cfg.EVIDENCE_DETECT_THRESH:
                continue
            if cfg.ONE_DEPOSIT_PER_LANDMARK and lid in agent.deposited_landmarks:
                continue
            lx, ly = world.landmarks[lid]
            if math.hypot(agent.x - lx, agent.y - ly) > cfg.SENSOR_RADIUS:
                move_toward(agent, lx, ly)
                deposited = True
                events["seeking_deposit"] = lid
                break
            jx = lx + float(rng.normal(0, cfg.DEPOSIT_JITTER))
            jy = ly + float(rng.normal(0, cfg.DEPOSIT_JITTER))
            if arch in ("direct_msg", "blackboard"):
                medium.send_message(lid, float(conf), tick)
            elif arch == "hybrid":
                medium.deposit(jx, jy, amp, tick)
                medium.send_message(lid, float(conf), tick)
            else:
                medium.deposit(jx, jy, amp, tick)
            agent.deposits_left -= 1
            agent.total_deposits += 1
            agent.deposited_landmarks.add(lid)  # type: ignore[attr-defined]
            # useful if any true patch maps to this landmark
            if any(p.landmark_id == lid and p.is_true for p in world.evidence):
                agent.useful_deposits += 1
            agent.pending_deposits.pop(lid, None)  # type: ignore[attr-defined]
            deposited = True
            events["deposit_landmark"] = lid
            break

    # ----- 3) Move (chemotaxis on medium / private cues) -----
    if not deposited:
        if agent.pending_deposits:  # type: ignore[attr-defined]
            lid = max(agent.pending_deposits, key=lambda k: agent.pending_deposits[k])  # type: ignore[attr-defined]
            tx, ty = world.landmarks[lid]
        elif readouts and max(readouts.values()) > 0.2:
            best_lid = max(readouts, key=lambda k: readouts[k])
            tx, ty = world.landmarks[best_lid]
        elif agent.private_evidence:
            best_lid = max(agent.private_evidence, key=lambda k: agent.private_evidence[k])
            tx, ty = world.landmarks[best_lid]
        else:
            tx, ty = _explore_target(agent, world, rng)
        move_toward(agent, tx, ty)

    return events


def majority_commit(agents: list[AgentState]) -> int | None:
    votes = [a.committed for a in agents if a.committed is not None]
    if not votes:
        return None
    vals, counts = np.unique(votes, return_counts=True)
    return int(vals[int(np.argmax(counts))])
