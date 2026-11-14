"""Experiments A–D for Task 9."""
from __future__ import annotations

from typing import Any

import numpy as np

from sim_world.exp9 import config as cfg
from sim_world.exp9.env import build_world, world_summary
from sim_world.exp9.agents import agent_step, majority_commit
from sim_world.exp9.field_backend import make_medium, SubstrateMedium


def _run_trial(
    seed: int,
    arch: str,
    *,
    ablation: str | None = None,
    noise_sigma: float | None = None,
    async_delay: int = 0,
    disconnect_ids: tuple[int, ...] = (),
    dispersed_evidence: bool = False,
    t_max: int | None = None,
    n_agents: int | None = None,
    force_random_commit: bool = False,
) -> dict[str, Any]:
    world = build_world(
        seed,
        noise_sigma=noise_sigma,
        async_delay=async_delay,
        disconnect_ids=disconnect_ids,
        dispersed_evidence=dispersed_evidence,
        t_max=t_max,
        n_agents=n_agents,
    )
    medium_arch = "ablation" if ablation else arch
    medium = make_medium(medium_arch, ablation=ablation)
    rng = np.random.default_rng(seed + 99)

    no_hyst = ablation == "no_hysteresis"
    force_rand = force_random_commit or ablation == "fixed_random_policy"
    events = []
    for tick in range(world.t_max):
        for agent in world.agents:
            ev = agent_step(
                world, agent, medium, tick, rng,
                arch=arch if not ablation else "ablation",
                ablation=ablation,
                force_random_commit=force_rand,
                no_hysteresis=no_hyst,
            )
            if ev.get("commit") is not None or ev.get("deposit_landmark") is not None:
                events.append(ev)
        medium.tick_update(tick)
        if medium.failed():
            break
        # Early stop if majority committed
        maj = majority_commit(world.agents)
        if maj is not None and sum(a.committed is not None for a in world.agents) >= max(2, len(world.agents) // 2 + 1):
            # wait one tick for tie-break stability
            if tick > 5:
                break

    commits = [a.committed for a in world.agents if a.committed is not None]
    maj = majority_commit(world.agents)
    correct = int(maj is not None and maj == world.true_landmark)
    wrong = int(maj is not None and maj != world.true_landmark)
    none = int(maj is None)
    latencies = [a.commit_tick for a in world.agents if a.commit_tick is not None]
    usage = medium.usage()
    usage.travel_distance = float(sum(a.travel for a in world.agents))

    return {
        "seed": seed,
        "arch": arch,
        "ablation": ablation,
        "failed": bool(medium.failed()),
        "true_landmark": world.true_landmark,
        "majority": maj,
        "correct": correct,
        "false_positive": wrong,
        "false_negative": none,
        "n_committed": len(commits),
        "decision_latency": float(np.mean(latencies)) if latencies else None,
        "useful_depositors": int(sum(1 for a in world.agents if a.useful_deposits > 0)),
        "n_field_deposits": int(sum(a.total_deposits for a in world.agents)),
        "usage": usage.to_dict(),
        "async_delay": async_delay,
        "noise_sigma": world.noise_sigma,
        "disconnect_ids": list(disconnect_ids),
        "dispersed_evidence": dispersed_evidence,
        "world": world_summary(world),
        "events_n": len(events),
    }


# ---------------------------------------------------------------------------
# Experiment A
# ---------------------------------------------------------------------------

def run_experiment_a(
    seeds: list[int],
    *,
    architectures: tuple[str, ...] | None = None,
    noise_sigma: float | None = None,
    async_delay: int = 0,
    disconnect_ids: tuple[int, ...] = (),
) -> dict[str, Any]:
    arches = architectures or cfg.ARCHITECTURES
    trials = []
    for seed in seeds:
        for arch in arches:
            trials.append(_run_trial(
                seed, arch,
                noise_sigma=noise_sigma,
                async_delay=async_delay,
                disconnect_ids=disconnect_ids,
            ))
    summary = {}
    for arch in arches:
        sub = [t for t in trials if t["arch"] == arch and not t["failed"]]
        if not sub:
            summary[arch] = {"n": 0}
            continue
        summary[arch] = {
            "n": len(sub),
            "correct_rate": float(np.mean([t["correct"] for t in sub])),
            "false_positive_rate": float(np.mean([t["false_positive"] for t in sub])),
            "false_negative_rate": float(np.mean([t["false_negative"] for t in sub])),
            "mean_latency": float(np.nanmean([t["decision_latency"] for t in sub if t["decision_latency"] is not None]))
                if any(t["decision_latency"] is not None for t in sub) else None,
            "mean_useful_depositors": float(np.mean([t["useful_depositors"] for t in sub])),
            "mean_deposits": float(np.mean([t["n_field_deposits"] for t in sub])),
            "mean_comm_volume": float(np.mean([t["usage"]["messages_sent"] for t in sub])),
            "mean_reads": float(np.mean([t["usage"]["reads"] for t in sub])),
            "mean_travel": float(np.mean([t["usage"]["travel_distance"] for t in sub])),
            "mean_resource": float(np.mean([t["usage"]["resource_expenditure"] for t in sub])),
            "task_completion_rate": float(np.mean([1 - t["false_negative"] for t in sub])),
        }
    return {"experiment": "A", "trials": trials, "summary": summary}


# ---------------------------------------------------------------------------
# Experiment B — causal chain ablations
# ---------------------------------------------------------------------------

def run_experiment_b(seeds: list[int]) -> dict[str, Any]:
    trials = []
    for seed in seeds:
        for abl in cfg.ABLATIONS_B:
            trials.append(_run_trial(
                seed, "nonlinear_sub", ablation=abl,
            ))
    summary = {}
    for abl in cfg.ABLATIONS_B:
        sub = [t for t in trials if t["ablation"] == abl and not t["failed"]]
        summary[abl] = {
            "n": len(sub),
            "correct_rate": float(np.mean([t["correct"] for t in sub])) if sub else None,
            "false_negative_rate": float(np.mean([t["false_negative"] for t in sub])) if sub else None,
        }
    # Causal checks
    full = summary.get("nonlinear_full", {}).get("correct_rate") or 0.0
    reaction = summary.get("reaction_off", {}).get("correct_rate") or 0.0
    readout = summary.get("readout_disabled", {}).get("correct_rate") or 0.0
    deposit = summary.get("deposit_disabled", {}).get("correct_rate") or 0.0
    random_p = summary.get("fixed_random_policy", {}).get("correct_rate") or 0.0
    causal = {
        "full_above_chance": full > 0.35,
        "reaction_drop": full - reaction,
        "readout_necessary": full > readout,
        "deposit_necessary": full > deposit,
        "beats_random": full > random_p,
        "chain_supported": bool(
            full > 0.35 and (full - reaction) > 0.15 and full > readout and full > deposit
        ),
    }
    return {"experiment": "B", "trials": trials, "summary": summary, "causal": causal}


# ---------------------------------------------------------------------------
# Experiment C — temporal async
# ---------------------------------------------------------------------------

def run_experiment_c(seeds: list[int], delays: tuple[int, ...] | None = None) -> dict[str, Any]:
    delays = delays or cfg.C_DELAYS
    arches = ("nonlinear_sub", "linear_sub", "direct_msg", "blackboard", "independent")
    trials = []
    for seed in seeds:
        for delay in delays:
            for arch in arches:
                trials.append(_run_trial(seed, arch, async_delay=int(delay)))
    by_delay = {}
    for delay in delays:
        by_delay[str(delay)] = {}
        for arch in arches:
            sub = [t for t in trials if t["async_delay"] == delay and t["arch"] == arch and not t["failed"]]
            by_delay[str(delay)][arch] = {
                "n": len(sub),
                "correct_rate": float(np.mean([t["correct"] for t in sub])) if sub else None,
                "mean_latency": float(np.nanmean([
                    t["decision_latency"] for t in sub if t["decision_latency"] is not None
                ])) if any(t["decision_latency"] is not None for t in sub) else None,
            }
    # Order discrimination probe: contradictory late evidence (distractors first already)
    order_note = (
        "Scalar field has no explicit order operator; performance vs delay measures "
        "integration window / retention, not temporal-order logic."
    )
    return {
        "experiment": "C",
        "trials": trials,
        "by_delay": by_delay,
        "order_discrimination": {"supported": False, "note": order_note},
    }


# ---------------------------------------------------------------------------
# Experiment D — spatial variants
# ---------------------------------------------------------------------------

def run_experiment_d(seeds: list[int]) -> dict[str, Any]:
    variants = {
        "clustered": dict(dispersed_evidence=False),
        "dispersed": dict(dispersed_evidence=True),
        "noise_high": dict(noise_sigma=0.5, dispersed_evidence=False),
        "disconnect_one": dict(disconnect_ids=(0,), dispersed_evidence=False),
    }
    arches = ("nonlinear_sub", "linear_sub", "pheromone", "direct_msg", "independent")
    trials = []
    for seed in seeds:
        for vname, kwargs in variants.items():
            for arch in arches:
                t = _run_trial(seed, arch, **kwargs)
                t["variant"] = vname
                trials.append(t)
    summary = {}
    for vname in variants:
        summary[vname] = {}
        for arch in arches:
            sub = [t for t in trials if t.get("variant") == vname and t["arch"] == arch and not t["failed"]]
            summary[vname][arch] = {
                "n": len(sub),
                "correct_rate": float(np.mean([t["correct"] for t in sub])) if sub else None,
                "mean_travel": float(np.mean([t["usage"]["travel_distance"] for t in sub])) if sub else None,
            }
    return {"experiment": "D", "trials": trials, "summary": summary}


# ---------------------------------------------------------------------------
# Controlled coincidence smoke (interface / mechanism sanity)
# ---------------------------------------------------------------------------

def controlled_coincidence_smoke(seed: int = 0) -> dict[str, Any]:
    """Non-autonomous sanity: two deposits at landmark 0 → nl latch, linear not."""
    lx, ly = cfg.LANDMARKS[0]
    out = {}
    for abl in ("nonlinear_full", "linear_telegraph"):
        m = SubstrateMedium(abl)
        m.deposit(lx, ly, cfg.DEP_AMP, 0)
        m.deposit(lx + 1.0, ly, cfg.DEP_AMP, 0)
        for t in range(60):
            m.tick_update(t)
        out[abl] = {
            "local_max": m.local_max(lx, ly),
            "activated": bool(m.local_max(lx, ly) >= cfg.ACTIVATION_THRESH),
            "failed": m.failed(),
        }
    return {
        "test": "controlled_coincidence_smoke",
        "pass": bool(out["nonlinear_full"]["activated"] and not out["linear_telegraph"]["activated"]),
        "rows": out,
    }
