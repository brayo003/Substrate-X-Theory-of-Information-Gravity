"""Distributed evidence propagation protocol (separate layer).

Ground truth is never an input. Correctness metrics are computed by evaluator.py.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Set, Tuple

from .evidence import EvidenceItem, NetworkEvidenceView


@dataclass
class NodeState:
    known: Dict[str, EvidenceItem] = field(default_factory=dict)
    pending: List[str] = field(default_factory=list)
    decision: Optional[int] = None
    decision_history: List[Optional[int]] = field(default_factory=list)


@dataclass
class DeliveryEvent:
    """First-time delivery of token into dst via edge (src, dst) at round."""

    round_idx: int
    src: Any
    dst: Any
    token: str


@dataclass
class RoundCommMetrics:
    """Protocol-local communication counters (no ground-truth fields)."""

    round_idx: int
    messages_sent: int
    new_deliveries: int
    duplicates_prevented: int


@dataclass
class ProtocolResult:
    nodes: Dict[Any, NodeState]
    rounds: List[RoundCommMetrics]
    total_messages: int
    total_unique_delivered: int
    total_duplicates_prevented: int
    rounds_executed: int
    stopped_reason: str
    deliveries: List[DeliveryEvent] = field(default_factory=list)
    edge_delivery_count: Dict[Tuple[Any, Any], int] = field(default_factory=dict)
    decision_rule: str = "weighted"


def decide_from_known(known: Dict[str, EvidenceItem]) -> Optional[int]:
    """Weighted signed vote (primary rule for substrate models)."""
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


def decide_unweighted_majority(known: Dict[str, EvidenceItem]) -> Optional[int]:
    """Genuine unweighted majority of known bits; tie → undecided."""
    if not known:
        return None
    c0 = c1 = 0
    for item in known.values():
        if item.bit == 0:
            c0 += 1
        else:
            c1 += 1
    if c0 == c1:
        return None
    return 0 if c0 > c1 else 1


def _update_decisions(states: Dict[Any, NodeState], rule: str) -> None:
    fn = decide_unweighted_majority if rule == "unweighted" else decide_from_known
    for st in states.values():
        st.decision = fn(st.known)
        st.decision_history.append(st.decision)


def agreement_from_decisions(decisions: Dict[Any, Optional[int]]) -> Dict[str, Any]:
    """Agreement / collective from local decisions only (no ground truth).

    Tie among decided nodes ⇒ no unique agreement_label and no collective,
    whether or not undecided nodes remain.
    """
    n = len(decisions)
    counts = {0: 0, 1: 0}
    for d in decisions.values():
        if d is not None:
            counts[d] += 1
    decided = counts[0] + counts[1]
    if decided == 0:
        return dict(
            agreement_frac=0.0,
            agreement_label=None,
            collective=None,
        )
    if counts[0] == counts[1]:
        # Tie: no unique label (includes ties with undecided present).
        return dict(
            agreement_frac=counts[0] / n if n else 0.0,
            agreement_label=None,
            collective=None,
        )
    if counts[0] > counts[1]:
        return dict(
            agreement_frac=counts[0] / n if n else 0.0,
            agreement_label=0,
            collective=0,
        )
    return dict(
        agreement_frac=counts[1] / n if n else 0.0,
        agreement_label=1,
        collective=1,
    )


def run_protocol(
    nodes: List[Any],
    network_view: NetworkEvidenceView,
    graph_sequence: List[Any],
    max_rounds: int,
    send_cap: int,
    max_messages: Optional[int] = None,
    failure_edges_by_round: Optional[Dict[int, Set[Tuple[Any, Any]]]] = None,
    decision_rule: str = "weighted",
) -> ProtocolResult:
    """Run message passing on a sequence of directed graphs.

    `network_view` must not contain ground truth.
    graph_sequence[t] supports .successors(u). Round r uses
    graph_sequence[min(r, len-1)] minus cumulative failed edges.
    """
    if max_rounds < 1:
        raise ValueError("max_rounds >= 1")
    if send_cap < 1:
        raise ValueError("send_cap >= 1")
    if not graph_sequence:
        raise ValueError("empty graph sequence")
    if decision_rule not in ("weighted", "unweighted"):
        raise ValueError(decision_rule)
    if hasattr(network_view, "ground_truth"):
        raise ValueError("ground truth must not be passed into the protocol")

    states: Dict[Any, NodeState] = {n: NodeState() for n in nodes}
    for n in nodes:
        item = network_view.local_item(n)
        if item is not None:
            states[n].known[item.token] = item
            states[n].pending.append(item.token)
    for n in nodes:
        states[n].pending = sorted(set(states[n].pending))

    _update_decisions(states, decision_rule)

    total_messages = 0
    total_unique_delivered = 0
    total_dup = 0
    edge_delivery: Dict[Tuple[Any, Any], int] = {}
    deliveries: List[DeliveryEvent] = []
    failed: Set[Tuple[Any, Any]] = set()
    rounds_out: List[RoundCommMetrics] = []
    stopped = "max_rounds"

    for r in range(max_rounds):
        if failure_edges_by_round and r in failure_edges_by_round:
            failed |= set(failure_edges_by_round[r])
        G = graph_sequence[min(r, len(graph_sequence) - 1)]
        msgs = 0
        new_del = 0
        dups = 0

        # Snapshot pending sends (label-independent selection within node:
        # pending already token-sorted).
        send_plan: Dict[Any, List[str]] = {}
        for u in nodes:
            st = states[u]
            if not st.pending:
                continue
            send_plan[u] = st.pending[:send_cap]
            st.pending = st.pending[send_cap:]

        # Token-atomic planning: group by opaque token (label-free order).
        # For each token, collect the multiset of planned edge sends; either
        # execute the entire token batch or skip it if it would exceed budget.
        by_token: Dict[str, List[Tuple[Any, Any]]] = {}
        for u, toks in send_plan.items():
            for tok in toks:
                for v in G.successors(u):
                    if (u, v) in failed:
                        continue
                    by_token.setdefault(tok, []).append((u, v))

        newly: Dict[Any, List[str]] = {n: [] for n in nodes}
        seen_new: Dict[Any, Set[str]] = {n: set() for n in nodes}
        budget_hit = False

        for tok in sorted(by_token.keys()):
            edges = by_token[tok]
            # Deterministic but label-anonymous edge order within token:
            # sort by (hash of endpoints with token) — wait, hash(u) uses labels.
            # Use set semantics for *which* edges fire (all-or-nothing), and
            # iterate in an order derived only from token + a commutative key.
            # For identical behaviour under relabel: the SET of (perm(u),perm(v))
            # must match. Message count = len(edges). Iteration order among
            # edges only matters for duplicate bookkeeping within the same
            # destination; use sorted by (str(type), id) would break labels.
            # Fix: sort edges by frozenset encoding via token-keyed digest of
            # *pair of endpoint tokens already known?* Endpoints are labels.
            #
            # Under token-atomic execution, every edge in `edges` fires if the
            # batch fits. Relabel maps the set of edges. Duplicate detection is
            # per (dst, tok) so order among edges into different dsts is moot;
            # order into same dst: first wins for delivery record, rest are dups
            # — still label-invariant as SET of first-delivery edges.
            # Use arbitrary but fixed order: sort by (repr(type), repr(u), repr(v))
            # ONLY for determinism within a labelling; relabel equivalence is
            # on aggregates (messages, known sets mapped), not on DeliveryEvent
            # ordering. For known-set equivalence, first-delivery into v of tok
            # is unique regardless of which parallel edge wins if multiple
            # u->v exist... multiple u can send same tok to v; first in
            # iteration records delivery edge. That CAN be label-dependent for
            # *which* edge is attributed, but known sets stay equal.
            #
            # For message counts and decisions: all edges fire → invariant.
            n_batch = len(edges)
            if max_messages is not None and total_messages + msgs + n_batch > max_messages:
                # Cannot fit this token batch; stop without partial send.
                stopped = "message_budget"
                budget_hit = True
                break

            # Sort only for deterministic attribution within a fixed labelling.
            for u, v in sorted(edges, key=lambda e: (str(type(e[0])), str(e[0]),
                                                     str(type(e[1])), str(e[1]))):
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
                    deliveries.append(DeliveryEvent(
                        round_idx=r, src=u, dst=v, token=tok))

        for n, toks in newly.items():
            states[n].pending.extend(toks)
            states[n].pending = sorted(set(states[n].pending))

        total_messages += msgs
        total_unique_delivered += new_del
        total_dup += dups
        _update_decisions(states, decision_rule)
        rounds_out.append(RoundCommMetrics(
            round_idx=r, messages_sent=msgs, new_deliveries=new_del,
            duplicates_prevented=dups))

        if budget_hit:
            break
        if new_del == 0 and msgs == 0 and r > 0:
            stopped = "quiescence"
            break
    else:
        stopped = "max_rounds"

    return ProtocolResult(
        nodes=states,
        rounds=rounds_out,
        total_messages=total_messages,
        total_unique_delivered=total_unique_delivered,
        total_duplicates_prevented=total_dup,
        rounds_executed=len(rounds_out),
        stopped_reason=stopped,
        deliveries=deliveries,
        edge_delivery_count=edge_delivery,
        decision_rule=decision_rule,
    )
