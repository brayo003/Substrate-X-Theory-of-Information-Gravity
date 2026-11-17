"""Bounded rule space, matching, and evaluation.

A rule is a pair (template, parameters).  The complete space is finite and
enumerated by `enumerate_space()`, so Model B can possess every rule Model D
can ever create.  This is the central fairness control of the study.

Templates (all edits are local; guards may consult global constraint state,
which is visible to every model):

  REACH      add u->v, u reachable from root, v not, dist(u,v) <= radius
  REACH_CAP  same, but only if outdeg(u) < K
  CAP        remove (u,w) from a node u with outdeg(u) > K
  CAP_SAFE   same, but only if removal preserves C1 and C4
  CYCLE      remove one edge of a mutual pair
  REQ        add a missing required edge
  REWIRE     remove (u,w) from an overfull u and add u->v nearby

Parameters are drawn from finite domains, so the whole space has 38 rules.
"""
from __future__ import annotations

from collections import deque
from dataclasses import dataclass
from functools import lru_cache
from typing import Dict, FrozenSet, List, Optional, Sequence, Set, Tuple

from .graph import (
    Graph, apply_edit, bfs_distances, in_adj, mutual_pairs,
    out_adj, out_degrees, reachable, total_violations, undirected_adj,
    violations as _violations,
)

ParamMap = Tuple[Tuple[str, object], ...]
Spec = Tuple[str, ParamMap]
MatchEdit = Tuple  # ("add",u,v) | ("remove",u,v) | ("rewire",u,w,v)

RADII = (1, 2, 3)
POLICIES = ("min_out", "max_out", "min_id")
CYCLE_POLICIES = ("min_id", "max_id", "non_req")
REQ_ORDERS = ("min_id", "max_id")
AVOID_CYCLE = (False, True)

TARGETS = {
    "REACH": (0,),
    "REACH_CAP": (0,),
    "CAP": (1,),
    "CAP_SAFE": (1,),
    "CYCLE": (2,),
    "REQ": (3,),
    "REWIRE": (1,),
}


def spec(template: str, **params) -> Spec:
    return (template, tuple(sorted(params.items())))


def spec_id(s: Spec) -> str:
    template, params = s
    if not params:
        return template
    return template + "|" + ",".join(f"{k}={v}" for k, v in params)


def spec_params(s: Spec) -> Dict[str, object]:
    return dict(s[1])


def enumerate_space() -> List[Spec]:
    """The complete rule space Model B receives, in a fixed order."""
    space: List[Spec] = []
    for r in RADII:
        for p in POLICIES:
            for ac in AVOID_CYCLE:
                space.append(spec("REACH", radius=r, policy=p, avoid_cycle=ac))
                space.append(spec("REACH_CAP", radius=r, policy=p, avoid_cycle=ac))
    for p in POLICIES:
        space.append(spec("CAP", policy=p))
        space.append(spec("CAP_SAFE", policy=p))
    for p in CYCLE_POLICIES:
        for sf in AVOID_CYCLE:
            space.append(spec("CYCLE", policy=p, safe=sf))
    for o in REQ_ORDERS:
        space.append(spec("REQ", order=o))
    for r in RADII:
        for p in POLICIES:
            for ac in AVOID_CYCLE:
                space.append(spec("REWIRE", radius=r, policy=p, avoid_cycle=ac))
    return space


SPACE = enumerate_space()
SPACE_BY_ID = {spec_id(s): s for s in SPACE}


# Seed library for Models A and D (deliberately incomplete: radius-1, unsafe adds).
SEED_IDS = [
    spec_id(spec("REQ", order="min_id")),
    spec_id(spec("CYCLE", policy="min_id", safe=False)),
    spec_id(spec("CAP", policy="min_out")),
    spec_id(spec("CAP_SAFE", policy="min_out")),
    spec_id(spec("REACH", radius=1, policy="min_out", avoid_cycle=False)),
    spec_id(spec("REACH_CAP", radius=1, policy="min_out", avoid_cycle=False)),
    spec_id(spec("REWIRE", radius=1, policy="min_out", avoid_cycle=False)),
]
SEED_SPECS = [SPACE_BY_ID[i] for i in SEED_IDS]


class Context:
    """Precomputed per-graph data, cached for repeated rule evaluation."""

    __slots__ = ("g", "out", "inn", "und", "deg", "reach", "unreached",
                 "missing_req", "mutuals", "dist", "safe_remove_cache")

    def __init__(self, g: Graph):
        self.g = g
        self.out = out_adj(g)
        self.inn = in_adj(g)
        self.und = undirected_adj(g)
        self.deg = out_degrees(g)
        self.reach = reachable(g)
        self.unreached = [v for v in range(g.n) if v not in self.reach]
        self.missing_req = sorted(g.required - g.edges)
        self.mutuals = mutual_pairs(g)
        self.dist = {v: bfs_distances(g, v, max(RADII)) for v in range(g.n)}
        self.safe_remove_cache: Dict[Tuple[int, int], bool] = {}

    def safe_remove(self, u: int, w: int) -> bool:
        key = (u, w)
        if key in self.safe_remove_cache:
            return self.safe_remove_cache[key]
        if (u, w) in self.g.required:
            self.safe_remove_cache[key] = False
            return False
        new_edges = self.g.edges - {(u, w)}
        tmp = self.g.copy_with(new_edges)
        ok = len(reachable(tmp)) == self.g.n and self.g.required <= new_edges
        self.safe_remove_cache[key] = ok
        return ok


@lru_cache(maxsize=32)
def context(g: Graph) -> Context:
    return Context(g)


def _rank(node: int, policy: str, ctx: Context) -> Tuple[int, int]:
    if policy == "min_out":
        return (ctx.deg[node], node)
    if policy == "max_out":
        return (-ctx.deg[node], node)
    if policy == "min_id":
        return (node, node)
    if policy == "max_id":
        return (-node, node)
    raise ValueError(policy)


def _choose_node(nodes: Sequence[int], policy: str, ctx: Context) -> Optional[int]:
    if not nodes:
        return None
    return min(nodes, key=lambda x: _rank(x, policy, ctx))


def _choose_edge(edges: Sequence[Tuple[int, int]], policy: str,
                 ctx: Context) -> Optional[Tuple[int, int]]:
    """Pick an edge by policy on the target node, then by source."""
    if not edges:
        return None
    return min(edges, key=lambda e: (_rank(e[1], policy, ctx), e[0]))


def match(s: Spec, g: Graph) -> Optional[Edit]:
    """Return the deterministic edit this rule would perform, or None."""
    template, params_t = s
    params = dict(params_t)
    ctx = context(g)

    if template in ("REACH", "REACH_CAP"):
        radius = int(params["radius"])
        policy = str(params["policy"])
        avoid = bool(params.get("avoid_cycle", False))
        cands = []
        for v in ctx.unreached:
            for u in ctx.reach:
                if u == v or u not in ctx.dist[v]:
                    continue
                d = ctx.dist[v][u]
                if d > radius:
                    continue
                if (u, v) in g.edges:
                    continue
                if avoid and (v, u) in g.edges:
                    continue
                if template == "REACH_CAP" and ctx.deg[u] >= g.K:
                    continue
                cands.append((d, u, v))
        if not cands:
            return None
        d, u, v = min(cands, key=lambda c: (c[0], _rank(c[1], policy, ctx), c[1], c[2]))
        return ("add", u, v)

    if template in ("CAP", "CAP_SAFE"):
        policy = str(params["policy"])
        over = [u for u in range(g.n) if ctx.deg[u] > g.K]
        if not over:
            return None
        u = max(over, key=lambda x: (ctx.deg[x], -x))
        edges = [(u, w) for w in ctx.out[u]]
        if template == "CAP_SAFE":
            edges = [(a, b) for a, b in edges if ctx.safe_remove(a, b)]
        # prefer required-preserving/non-required edges when available
        nonreq = [(a, b) for a, b in edges if (a, b) not in g.required]
        if nonreq:
            edges = nonreq
        e = _choose_edge(edges, policy, ctx)
        return None if e is None else ("remove", e[0], e[1])

    if template == "CYCLE":
        policy = str(params["policy"])
        safe_only = bool(params.get("safe", False))
        if not ctx.mutuals:
            return None
        pairs = ctx.mutuals
        if policy == "min_id":
            pairs = sorted(pairs)
        elif policy == "max_id":
            pairs = sorted(pairs, reverse=True)
        else:  # non_req
            nonreq = [(u, v) for u, v in pairs
                      if (u, v) not in g.required and (v, u) not in g.required]
            pairs = sorted(nonreq if nonreq else pairs)
        # choose which direction to remove: prefer a non-required edge
        cands = []
        for u, v in pairs:
            if (u, v) in g.required and (v, u) not in g.required:
                cands.append((v, u))
            else:
                cands.append((u, v))
        if safe_only:
            cands = [e for e in cands if ctx.safe_remove(*e)]
        if not cands:
            return None
        u, v = cands[0]
        return ("remove", u, v)

    if template == "REQ":
        if not ctx.missing_req:
            return None
        order = str(params["order"])
        e = min(ctx.missing_req) if order == "min_id" else max(ctx.missing_req)
        return ("add", e[0], e[1])

    if template == "REWIRE":
        radius = int(params["radius"])
        policy = str(params["policy"])
        avoid = bool(params.get("avoid_cycle", False))
        over = [u for u in range(g.n) if ctx.deg[u] > g.K]
        if not over:
            return None
        u = max(over, key=lambda x: (ctx.deg[x], -x))
        w_edges = [(u, w) for w in ctx.out[u]]
        # do not remove a required edge if another choice exists
        nonreq = [(a, b) for a, b in w_edges if (a, b) not in g.required]
        if nonreq:
            w_edges = nonreq
        we = _choose_edge(w_edges, policy, ctx)
        if we is None:
            return None
        w = we[1]
        cands = [v for v in ctx.und[u]
                 if v != w and (u, v) not in g.edges
                 and not (avoid and (v, u) in g.edges)
                 and ctx.dist[u].get(v, 99) <= radius]
        v = _choose_node(cands, policy, ctx)
        if v is None:
            return None
        return ("rewire", u, w, v)  # expanded by apply_rule_edit

    raise ValueError(template)


@dataclass
class EvalResult:
    edit: MatchEdit
    new_graph: Graph
    delta: int           # violations before - after (positive is improvement)
    violations_new: Tuple[int, int, int, int]


def evaluate(s: Spec, g: Graph) -> Optional[EvalResult]:
    """One rule evaluation: choose a match, simulate it, score it.

    This is the atomic cost unit in the experiment (1 op).
    """
    edit = match(s, g)
    if edit is None:
        return None
    if edit[0] == "rewire":
        _, u, w, v = edit
        tmp = g.copy_with((g.edges - {(u, w)}) | {(u, v)})
    else:
        tmp = apply_edit(g, edit)  # type: ignore[arg-type]
    if tmp is None:
        return None
    return EvalResult(
        edit=edit,
        new_graph=tmp,
        delta=total_violations(g) - total_violations(tmp),
        violations_new=_violations(tmp),
    )


def apply_spec(s: Spec, g: Graph) -> Optional[Edit]:
    """Apply a rule's chosen match and return the concrete applied edit.

    Rewire edits are returned as ("rewire", u, w) plus the new graph is
    obtained through `evaluate`.
    """
    ev = evaluate(s, g)
    return None if ev is None else ev.edit
