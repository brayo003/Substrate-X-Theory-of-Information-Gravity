"""Task 9 environment: landmarks, noisy evidence, no privileged k* to agents."""
from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Any

import numpy as np

from sim_world.exp9 import config as cfg


@dataclass
class EvidencePatch:
    patch_id: int
    x: float
    y: float
    landmark_id: int
    is_true: bool
    mean: float
    available_from: int = 0  # async onset


@dataclass
class AgentState:
    agent_id: int
    x: float
    y: float
    deposits_left: int = cfg.MAX_DEPOSITS_PER_AGENT
    visited_landmarks: set[int] = field(default_factory=set)
    private_evidence: dict[int, float] = field(default_factory=dict)  # landmark -> best obs
    committed: int | None = None
    commit_tick: int | None = None
    disconnected: bool = False
    useful_deposits: int = 0
    total_deposits: int = 0
    travel: float = 0.0


@dataclass
class World:
    seed: int
    true_landmark: int
    landmarks: list[tuple[float, float]]
    evidence: list[EvidencePatch]
    agents: list[AgentState]
    noise_sigma: float
    t_max: int


def _nearest_landmark(x: float, y: float, landmarks: list[tuple[float, float]]) -> int:
    best_i, best_d = 0, float("inf")
    for i, (lx, ly) in enumerate(landmarks):
        d = math.hypot(x - lx, y - ly)
        if d < best_d:
            best_d, best_i = d, i
    return best_i


def build_world(
    seed: int,
    *,
    n_agents: int | None = None,
    noise_sigma: float | None = None,
    t_max: int | None = None,
    async_delay: int = 0,
    disconnect_ids: tuple[int, ...] = (),
    dispersed_evidence: bool = False,
    n_true: int | None = None,
    n_distractor: int | None = None,
) -> World:
    rng = np.random.default_rng(seed + 17)
    landmarks = list(cfg.LANDMARKS)
    k_star = int(rng.integers(0, len(landmarks)))
    n_true = cfg.N_TRUE_EVIDENCE if n_true is None else n_true
    n_distractor = cfg.N_DISTRACTOR_EVIDENCE if n_distractor is None else n_distractor
    sigma = cfg.OBS_NOISE_SIGMA if noise_sigma is None else float(noise_sigma)
    t_max = cfg.T_MAX if t_max is None else int(t_max)
    n_agents = cfg.N_AGENTS if n_agents is None else int(n_agents)

    evidence: list[EvidencePatch] = []
    pid = 0
    tx, ty = landmarks[k_star]
    for _ in range(n_true):
        if dispersed_evidence:
            # place true evidence far from landmark (harder spatial integration)
            ang = float(rng.uniform(0, 2 * math.pi))
            rad = float(rng.uniform(8.0, 14.0))
            ex = float(np.clip(tx + rad * math.cos(ang), 2, cfg.GRID_X - 2))
            ey = float(np.clip(ty + rad * math.sin(ang), 2, cfg.GRID_Y - 2))
        else:
            ex = float(np.clip(tx + rng.normal(0, cfg.EVIDENCE_JITTER), 2, cfg.GRID_X - 2))
            ey = float(np.clip(ty + rng.normal(0, cfg.EVIDENCE_JITTER), 2, cfg.GRID_Y - 2))
        evidence.append(EvidencePatch(
            pid, ex, ey, k_star, True, cfg.EVIDENCE_TRUE_MEAN, available_from=int(async_delay),
        ))
        pid += 1

    wrong = [i for i in range(len(landmarks)) if i != k_star]
    for j in range(n_distractor):
        kid = int(wrong[j % len(wrong)])
        lx, ly = landmarks[kid]
        ex = float(np.clip(lx + rng.normal(0, cfg.EVIDENCE_JITTER), 2, cfg.GRID_X - 2))
        ey = float(np.clip(ly + rng.normal(0, cfg.EVIDENCE_JITTER), 2, cfg.GRID_Y - 2))
        evidence.append(EvidencePatch(
            pid, ex, ey, kid, False, cfg.EVIDENCE_DISTRACTOR_MEAN, available_from=0,
        ))
        pid += 1

    agents = []
    for i in range(n_agents):
        if cfg.SPAWN_AT_LANDMARKS:
            lx, ly = landmarks[i % len(landmarks)]
            x = float(np.clip(lx + rng.normal(0, 1.0), 1, cfg.GRID_X - 1))
            y = float(np.clip(ly + rng.normal(0, 1.0), 1, cfg.GRID_Y - 1))
        else:
            x = float(rng.uniform(5, cfg.GRID_X - 5))
            y = float(rng.uniform(5, cfg.GRID_Y - 5))
        agents.append(AgentState(
            agent_id=i,
            x=x,
            y=y,
            disconnected=(i in disconnect_ids),
        ))

    return World(
        seed=seed,
        true_landmark=k_star,
        landmarks=landmarks,
        evidence=evidence,
        agents=agents,
        noise_sigma=sigma,
        t_max=t_max,
    )


def sense_evidence(world: World, agent: AgentState, tick: int, rng: np.random.Generator) -> list[dict]:
    """Local noisy observations only — no GT is_true flag to agent policy."""
    out = []
    if agent.disconnected:
        return out
    for p in world.evidence:
        if tick < p.available_from:
            continue
        if math.hypot(agent.x - p.x, agent.y - p.y) <= cfg.SENSOR_RADIUS:
            obs = float(p.mean + rng.normal(0, world.noise_sigma))
            out.append({
                "patch_id": p.patch_id,
                "x": p.x,
                "y": p.y,
                "landmark_id": p.landmark_id,  # agent can associate patch to nearest known post if close
                "obs": obs,
            })
    return out


def update_visited(agent: AgentState, landmarks: list[tuple[float, float]]) -> None:
    for i, (lx, ly) in enumerate(landmarks):
        if math.hypot(agent.x - lx, agent.y - ly) <= cfg.SENSOR_RADIUS:
            agent.visited_landmarks.add(i)


def move_toward(agent: AgentState, tx: float, ty: float, speed: float = cfg.AGENT_SPEED) -> float:
    dx, dy = tx - agent.x, ty - agent.y
    dist = math.hypot(dx, dy)
    if dist < 1e-9:
        return 0.0
    step = min(speed, dist)
    agent.x += step * dx / dist
    agent.y += step * dy / dist
    agent.x = float(np.clip(agent.x, 0, cfg.GRID_X))
    agent.y = float(np.clip(agent.y, 0, cfg.GRID_Y))
    agent.travel += step
    return step


def nearest_landmark_id(agent: AgentState, landmarks: list[tuple[float, float]]) -> int:
    return _nearest_landmark(agent.x, agent.y, landmarks)


def world_summary(world: World) -> dict[str, Any]:
    return {
        "seed": world.seed,
        "true_landmark": world.true_landmark,  # evaluator only
        "n_agents": len(world.agents),
        "n_evidence": len(world.evidence),
        "n_true_evidence": sum(1 for e in world.evidence if e.is_true),
        "noise_sigma": world.noise_sigma,
        "t_max": world.t_max,
    }
