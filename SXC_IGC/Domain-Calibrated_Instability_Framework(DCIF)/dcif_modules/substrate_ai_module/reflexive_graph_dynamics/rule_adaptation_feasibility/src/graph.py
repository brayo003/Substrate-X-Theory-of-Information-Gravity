"""Directed graph state, constraints, disruptions, and case generation.

The benchmark state is G_t = (V, E_t, r, K, R_req):

  V      fixed node set {0, ..., n-1}
  E_t    directed edge set
  r      designated root (0)
  K      per-case out-degree cap
  R_req  required dependency edges

Four constraints are evaluated:
  C1  root reaches every node
  C2  out-degree(v) <= K for all v
  C3  no mutual pair (u,v) and (v,u)
  C4  every required edge is present

All functions are deterministic given their inputs.  No global state.
"""
from __future__ import annotations

import random
from collections import deque
from dataclasses import dataclass
from typing import Dict, FrozenSet, Iterable, List, Optional, Sequence, Set, Tuple

Edge = Tuple[int, int]
Edit = Tuple[str, int, int]  # ("add"|"remove", u, v)


@dataclass(frozen=True)
class Graph:
    n: int
    edges: FrozenSet[Edge]
    root: int
    K: int
    required: FrozenSet[Edge]

    def copy_with(self, edges: Iterable[Edge]) -> "Graph":
        return Graph(self.n, frozenset(edges), self.root, self.K, self.required)


def out_adj(g: Graph) -> List[Set[int]]:
    adj: List[Set[int]] = [set() for _ in range(g.n)]
    for u, v in g.edges:
        adj[u].add(v)
    return adj


def in_adj(g: Graph) -> List[Set[int]]:
    adj: List[Set[int]] = [set() for _ in range(g.n)]
    for u, v in g.edges:
        adj[v].add(u)
    return adj


def undirected_adj(g: Graph) -> List[Set[int]]:
    adj: List[Set[int]] = [set() for _ in range(g.n)]
    for u, v in g.edges:
        adj[u].add(v)
        adj[v].add(u)
    return adj


def out_degree(g: Graph, u: int) -> int:
    return sum(1 for a, _ in g.edges if a == u)


def in_degree(g: Graph, u: int) -> int:
    return sum(1 for _, b in g.edges if b == u)


def out_degrees(g: Graph) -> List[int]:
    d = [0] * g.n
    for u, _ in g.edges:
        d[u] += 1
    return d


def reachable(g: Graph) -> Set[int]:
    adj = out_adj(g)
    seen = {g.root}
    stack = [g.root]
    while stack:
        u = stack.pop()
        for v in adj[u]:
            if v not in seen:
                seen.add(v)
                stack.append(v)
    return seen


def bfs_distances(g: Graph, src: int, max_depth: int) -> Dict[int, int]:
    """Undirected BFS distances from src up to max_depth."""
    adj = undirected_adj(g)
    dist = {src: 0}
    q = deque([src])
    while q:
        u = q.popleft()
        if dist[u] >= max_depth:
            continue
        for v in adj[u]:
            if v not in dist:
                dist[v] = dist[u] + 1
                q.append(v)
    return dist


def mutual_pairs(g: Graph) -> List[Tuple[int, int]]:
    pairs = []
    for u, v in g.edges:
        if u < v and (v, u) in g.edges:
            pairs.append((u, v))
    return pairs


def violations(g: Graph) -> Tuple[int, int, int, int]:
    """(unreachable nodes, out-degree excess, mutual pairs, missing required)."""
    v1 = g.n - len(reachable(g))
    deg = out_degrees(g)
    v2 = sum(max(0, d - g.K) for d in deg)
    v3 = len(mutual_pairs(g))
    v4 = len(g.required - g.edges)
    return (v1, v2, v3, v4)


def total_violations(g: Graph) -> int:
    return sum(violations(g))


def is_satisfied(g: Graph) -> bool:
    return total_violations(g) == 0


def apply_edit(g: Graph, edit: Edit) -> Optional[Graph]:
    kind, u, v = edit
    if u == v or not (0 <= u < g.n and 0 <= v < g.n):
        return None
    if kind == "add":
        if (u, v) in g.edges:
            return None
        return g.copy_with(g.edges | {(u, v)})
    if kind == "remove":
        if (u, v) not in g.edges:
            return None
        return g.copy_with(g.edges - {(u, v)})
    raise ValueError(f"unknown edit kind: {kind}")


def edit_delta(g: Graph, edit: Edit) -> Optional[Tuple[Graph, int]]:
    new = apply_edit(g, edit)
    if new is None:
        return None
    return new, total_violations(g) - total_violations(new)


# ---------------------------------------------------------------- disruptions
def _deletable_edges(g: Graph, allow_required: bool) -> List[Edge]:
    """Edges whose removal leaves every node with degree >= 1.

    This prevents an unrecoverable state in which a node has no incident
    edge at all, which no local rule could ever repair.
    """
    adj = undirected_adj(g)
    res = []
    for e in sorted(g.edges):
        u, v = e
        if not allow_required and e in g.required:
            continue
        if len(adj[u]) - 1 < 1 or len(adj[v]) - 1 < 1:
            continue
        res.append(e)
    return res


def disrupt_delete(g: Graph, k: int, rng: random.Random, allow_required: bool) -> Graph:
    pool = _deletable_edges(g, allow_required)
    rng.shuffle(pool)
    chosen = set(pool[:k])
    return g.copy_with(g.edges - chosen)


def disrupt_hub_and_cycles(g: Graph, k_hub: int, k_pairs: int,
                            rng: random.Random) -> Graph:
    edges = set(g.edges)
    deg = out_degrees(g)
    hub = max(range(g.n), key=lambda u: (deg[u], -u))
    candidates = [v for v in range(g.n) if v != hub and (hub, v) not in edges]
    rng.shuffle(candidates)
    for v in candidates[:k_hub]:
        edges.add((hub, v))
    # inject mutual pairs
    pairs = [(u, v) for u in range(g.n) for v in range(u + 1, g.n)
             if (u, v) not in edges and (v, u) not in edges]
    rng.shuffle(pairs)
    for u, v in pairs[:k_pairs]:
        edges.add((u, v))
        edges.add((v, u))
    return g.copy_with(edges)


# ---------------------------------------------------------------- case making
def _safe_add(edges: Set[Edge], u: int, v: int) -> bool:
    if u == v or (u, v) in edges or (v, u) in edges:
        return False
    edges.add((u, v))
    return True


def make_base_graph(n: int, K: int, seed: int) -> Graph:
    """A constraint-satisfying starting graph.

    A directed Hamiltonian cycle guarantees C1.  Extra forward edges add
    density.  Required edges are added without breaking C2 or C3.
    """
    rng = random.Random(seed)
    edges: Set[Edge] = {(i, (i + 1) % n) for i in range(n)}
    target = 2 * n
    attempts = 0
    while len(edges) < target and attempts < 50 * n:
        attempts += 1
        u = rng.randrange(n)
        v = rng.randrange(n)
        if u == v or (u, v) in edges or (v, u) in edges:
            continue
        if out_degree(Graph(n, frozenset(edges), 0, K, frozenset()), u) >= K:
            continue
        edges.add((u, v))
    # required edges
    req: Set[Edge] = set()
    tries = 0
    while len(req) < 6 and tries < 200:
        tries += 1
        u = rng.randrange(n)
        v = rng.randrange(n)
        if u == v or (u, v) in req or (v, u) in edges or (u, v) in edges:
            continue
        if out_degree(Graph(n, frozenset(edges), 0, K, frozenset()), u) >= K:
            continue
        edges.add((u, v))
        req.add((u, v))
    g = Graph(n, frozenset(edges), 0, K, frozenset(req))
    assert total_violations(g) == 0, f"base graph violates constraints: {violations(g)}"
    return g


@dataclass(frozen=True)
class Case:
    case_id: int
    seed: int
    n: int
    K: int
    initial: Graph
    disruptions: Tuple[Tuple[int, str, Tuple], ...]  # (op_threshold, kind, params)

    def to_json(self) -> dict:
        return dict(
            case_id=self.case_id, seed=self.seed, n=self.n, K=self.K,
            initial_edges=sorted([list(e) for e in self.initial.edges]),
            required=sorted([list(e) for e in self.initial.required]),
            disruptions=[dict(op=t, kind=k, params=list(p))
                         for t, k, p in self.disruptions],
        )


def make_case(case_id: int, n: int = 24, K: Optional[int] = None,
              disruption_ops: Sequence[int] = (250, 500, 750)) -> Case:
    seed = 1_000_003 + case_id * 7919
    if K is None:
        K = 3 if case_id % 2 == 0 else 4
    g = make_base_graph(n, K, seed)
    d1_seed = seed ^ 0xD1
    d2_seed = seed ^ 0xD2
    d3_seed = seed ^ 0xD3
    disruptions = (
        (disruption_ops[0], "delete", ("d1", 6, d1_seed)),
        (disruption_ops[1], "hub_cycles", ("d2", 5, 3, d2_seed)),
        (disruption_ops[2], "delete", ("d3", 8, d3_seed)),
    )
    return Case(case_id, seed, n, K, g, disruptions)


def apply_disruption(g: Graph, kind: str, params: Tuple) -> Graph:
    if kind == "delete":
        tag, k, seed = params
        allow = (tag == "d3")
        return disrupt_delete(g, k, random.Random(seed), allow_required=allow)
    if kind == "hub_cycles":
        _, k_hub, k_pairs, seed = params
        return disrupt_hub_and_cycles(g, k_hub, k_pairs, random.Random(seed))
    raise ValueError(kind)


def initial_violations(case: Case) -> Tuple[int, int, int, int]:
    return violations(case.initial)
