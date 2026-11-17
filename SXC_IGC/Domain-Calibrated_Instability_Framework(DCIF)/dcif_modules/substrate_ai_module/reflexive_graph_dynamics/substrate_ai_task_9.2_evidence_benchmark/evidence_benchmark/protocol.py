"""Distributed evidence propagation protocol (separate layer)."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Set, Tuple

from .evidence import EvidenceBundle, EvidenceItem


@dataclass
class NodeState:
    known: Dict[str, EvidenceItem] = field(default_factory=dict)
    pending: List[str] = field(default_factory=list)  # tokens to forward
    decision: Optional[int] = None  # 0, 1, or None (undecided)
    decision_history: List[Optional[int]] = field(default_factory=list)


@dataclass
class RoundMetrics:
    round_idx: int
    messages_sent: int
    new_deliveries: int
    duplicates_prevented: int
    frac_correct: float
    frac_incorrect: float
    frac_undecided: float
    agreement_frac: float
    agreement_label: Optional[int]
    agreement_correct: Optional[bool]
    collective: Optional[int]
    collective_correct: Optional[bool]


@dataclass
class ProtocolResult:
    nodes: Dict[Any, NodeState]
    rounds: List[RoundMetrics]
    total_messages: int
    total_unique_delivered: int  # network-wide unique (token,node) first deliveries beyond local
    total_duplicates_prevented: int
    rounds_executed: int
    stopped_reason: str
    # edge (a,b) -> number of first-time deliveries carried
    edge_delivery_count: Dict[Tuple[Any, Any], int] = field(default_factory=dict)
    # edges that carried evidence later used in a correct final local decision
    edges_helping_correct: Set[Tuple[Any, Any]] = field(default_factory=set)
    # per-token first delivery edges
    token_delivery_edges: Dict[str, Set[Tuple[Any, Any]]] = field(default_factory=dict)
    time_series: List[Dict[str, Any]] = field(default_factory=list)


def decide_from_known(known: Dict[str, EvidenceItem]) -> Optional[int]:
    if not known:
        return None
    score = 0.0
    for item in known.values():
        score += (2 * item.bit - 1) * item.weight
    if score > 0:
        return 1
    if score < 0:
        return 0
    return None


def _update_decisions(states: Dict[Any, NodeState]) -> None:
    for st in states.values():
        st.decision = decide_from_known(st.known)
        st.decision_history.append(st.decision)


def _agreement_stats(states: Dict[Any, NodeState], y: int):
    n = len(states)
    decisions = [st.decision for st in states.values()]
    n_correct = sum(1 for d in decisions if d == y)
    n_incorrect = sum(1 for d in decisions if d is not None and d != y)
    n_und = sum(1 for d in decisions if d is None)
    # agreement among all nodes (including undecided as non-agreement on a label)
    counts = {0: 0, 1: 0}
    for d in decisions:
        if d is not None:
            counts[d] += 1
    if counts[0] == 0 and counts[1] == 0:
        agr_label = None
        agr_frac = 0.0
    elif counts[0] >= counts[1]:
        agr_label = 0
        agr_frac = counts[0] / n
    else:
        agr_label = 1
        agr_frac = counts[1] / n
    if counts[0] == counts[1] and counts[0] > 0:
        # exact tie among decided — no unique agreement label
        if counts[0] + counts[1] == n:
            agr_label = None
            agr_frac = counts[0] / n
    agr_correct = (agr_label == y) if agr_label is not None else None
    # collective = majority of decided
    decided = counts[0] + counts[1]
    if decided == 0 or counts[0] == counts[1]:
        collective = None
    else:
        collective = 0 if counts[0] > counts[1] else 1
    coll_correct = (collective == y) if collective is not None else None
    return dict(
        frac_correct=n_correct / n,
        frac_incorrect=n_incorrect / n,
        frac_undecided=n_und / n,
        agreement_frac=agr_frac,
        agreement_label=agr_label,
        agreement_correct=agr_correct,
        collective=collective,
        collective_correct=coll_correct,
    )


def run_protocol(
    nodes: List[Any],
    bundle: EvidenceBundle,
    graph_sequence: List[Any],
    max_rounds: int,
    send_cap: int,
    max_messages: Optional[int] = None,
    failure_edges_by_round: Optional[Dict[int, Set[Tuple[Any, Any]]]] = None,
) -> ProtocolResult:
    """Run message passing on a sequence of directed graphs.

    graph_sequence[t] must support .successors(u) and .has_edge(a,b) and .edges().
    Length may be 1 (static) or many (dynamic). Round r uses
    graph_sequence[min(r, len-1)] minus any failed edges scheduled for that round
    (failures persist once applied).
    """
    if max_rounds < 1:
        raise ValueError("max_rounds >= 1")
    if send_cap < 1:
        raise ValueError("send_cap >= 1")
    if not graph_sequence:
        raise ValueError("empty graph sequence")

    y = bundle.ground_truth
    states: Dict[Any, NodeState] = {n: NodeState() for n in nodes}
    for n in nodes:
        item = bundle.node_view(n)
        if item is not None:
            states[n].known[item.token] = item
            states[n].pending.append(item.token)
    for n in nodes:
        states[n].pending = sorted(set(states[n].pending))

    _update_decisions(states)

    total_messages = 0
    total_unique_delivered = 0
    total_dup = 0
    edge_delivery: Dict[Tuple[Any, Any], int] = {}
    token_edges: Dict[str, Set[Tuple[Any, Any]]] = {}
    # track which tokens arrived via which created path for attribution
    failed: Set[Tuple[Any, Any]] = set()
    rounds_out: List[RoundMetrics] = []
    time_series: List[Dict[str, Any]] = []
    stopped = "max_rounds"
    quiescence_streak = 0

    # record t=0 pre-communication snapshot
    snap0 = _agreement_stats(states, y)
    time_series.append(dict(round=-1, messages_cum=0, **snap0))

    for r in range(max_rounds):
        if failure_edges_by_round and r in failure_edges_by_round:
            failed |= set(failure_edges_by_round[r])
        G = graph_sequence[min(r, len(graph_sequence) - 1)]
        msgs = 0
        new_del = 0
        dups = 0
        # Synchronous round: snapshot sends before any delivery so iteration
        # order over node labels cannot change the message multiset.
        send_plan: Dict[Any, List[str]] = {}
        for u in nodes:
            st = states[u]
            if not st.pending:
                continue
            send_plan[u] = st.pending[:send_cap]
            st.pending = st.pending[send_cap:]

        # Planned messages as a sorted list for deterministic budget truncation
        planned: List[Tuple[Any, Any, str]] = []
        for u in sorted(send_plan.keys(), key=lambda x: (str(type(x)), x)):
            for tok in send_plan[u]:
                for v in sorted(G.successors(u), key=lambda x: (str(type(x)), x)):
                    if (u, v) in failed:
                        continue
                    planned.append((u, v, tok))

        newly: Dict[Any, List[str]] = {n: [] for n in nodes}
        seen_new: Dict[Any, Set[str]] = {n: set() for n in nodes}
        for u, v, tok in planned:
            if max_messages is not None and total_messages + msgs >= max_messages:
                stopped = "message_budget"
                break
            msgs += 1
            item = states[u].known[tok]
            recv = states[v]
            if tok in recv.known or tok in seen_new[v]:
                dups += 1
            else:
                recv.known[tok] = item
                newly[v].append(tok)
                seen_new[v].add(tok)
                new_del += 1
                edge_delivery[(u, v)] = edge_delivery.get((u, v), 0) + 1
                token_edges.setdefault(tok, set()).add((u, v))

        for n, toks in newly.items():
            states[n].pending.extend(toks)
            # Keep pending in token-sorted order so send_cap selection is
            # label-anonymous (not arrival-order / iteration-order dependent).
            states[n].pending = sorted(set(states[n].pending))

        total_messages += msgs
        total_unique_delivered += new_del
        total_dup += dups
        _update_decisions(states)
        snap = _agreement_stats(states, y)
        rounds_out.append(RoundMetrics(
            round_idx=r, messages_sent=msgs, new_deliveries=new_del,
            duplicates_prevented=dups, **snap))
        time_series.append(dict(round=r, messages_cum=total_messages, **snap))

        if stopped == "message_budget":
            break
        if new_del == 0 and msgs == 0:
            quiescence_streak += 1
        else:
            quiescence_streak = 0
        if quiescence_streak >= 1 and r > 0:
            stopped = "quiescence"
            break
    else:
        stopped = "max_rounds"

    # Attribution: edges that delivered tokens present in correctly deciding nodes
    help_edges: Set[Tuple[Any, Any]] = set()
    for n, st in states.items():
        if st.decision == y:
            for tok in st.known:
                for e in token_edges.get(tok, ()):
                    help_edges.add(e)

    return ProtocolResult(
        nodes=states,
        rounds=rounds_out,
        total_messages=total_messages,
        total_unique_delivered=total_unique_delivered,
        total_duplicates_prevented=total_dup,
        rounds_executed=len(rounds_out),
        stopped_reason=stopped,
        edge_delivery_count=edge_delivery,
        edges_helping_correct=help_edges,
        token_delivery_edges=token_edges,
        time_series=time_series,
    )
