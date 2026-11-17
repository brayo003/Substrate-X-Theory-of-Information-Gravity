"""Evaluator-only metrics. Ground truth never enters the protocol."""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Set, Tuple

from .evidence import EvidenceBundle, NetworkEvidenceView
from .protocol import (
    DeliveryEvent,
    ProtocolResult,
    agreement_from_decisions,
    decide_from_known,
)


def evaluate_protocol(
    result: ProtocolResult,
    ground_truth: int,
    bundle: Optional[EvidenceBundle] = None,
) -> Dict[str, Any]:
    """Compute correctness / agreement-vs-truth from protocol outputs + GT."""
    y = ground_truth
    n = len(result.nodes)
    decisions = {nid: st.decision for nid, st in result.nodes.items()}
    n_correct = sum(1 for d in decisions.values() if d == y)
    n_incorrect = sum(1 for d in decisions.values() if d is not None and d != y)
    n_und = sum(1 for d in decisions.values() if d is None)

    # decision_history[0] = pre-communication; [1..] align with rounds 0..
    round_evals: List[Dict[str, Any]] = []
    history_len = 0
    if result.nodes:
        history_len = len(next(iter(result.nodes.values())).decision_history)
    for r in range(history_len):
        decs = {nid: st.decision_history[r] for nid, st in result.nodes.items()}
        snap = agreement_from_decisions(decs)
        agr_correct = (snap["agreement_label"] == y) if snap["agreement_label"] is not None else None
        coll_correct = (snap["collective"] == y) if snap["collective"] is not None else None
        n_c = sum(1 for d in decs.values() if d == y)
        n_i = sum(1 for d in decs.values() if d is not None and d != y)
        n_u = sum(1 for d in decs.values() if d is None)
        round_evals.append(dict(
            round_idx=r - 1,
            frac_correct=n_c / n if n else float("nan"),
            frac_incorrect=n_i / n if n else float("nan"),
            frac_undecided=n_u / n if n else float("nan"),
            agreement_frac=snap["agreement_frac"],
            agreement_label=snap["agreement_label"],
            agreement_correct=agr_correct,
            collective=snap["collective"],
            collective_correct=coll_correct,
        ))

    last = round_evals[-1] if round_evals else None

    # Edge attribution (evaluator-side)
    carry, help_correct = attribute_edges(result, y)

    # Coverage vs all tokens in network view / bundle
    global_tokens: Set[str] = set()
    for st in result.nodes.values():
        global_tokens |= set(st.known.keys())
    if bundle is not None:
        for item in bundle.local_items.values():
            if item is not None:
                global_tokens.add(item.token)
    coverage = 0.0
    if global_tokens and n:
        coverage = sum(len(st.known) / len(global_tokens)
                       for st in result.nodes.values()) / n

    return dict(
        ground_truth=y,
        frac_correct=n_correct / n if n else float("nan"),
        frac_incorrect=n_incorrect / n if n else float("nan"),
        frac_undecided=n_und / n if n else float("nan"),
        collective=last["collective"] if last else None,
        collective_correct=(
            None if last is None or last["collective_correct"] is None
            else bool(last["collective_correct"])),
        agreement_frac=last["agreement_frac"] if last else 0.0,
        agreement_label=last["agreement_label"] if last else None,
        agreement_correct=(
            None if last is None or last["agreement_correct"] is None
            else bool(last["agreement_correct"])),
        round_evals=round_evals,
        edges_carrying_evidence=carry,
        edges_helping_correct=help_correct,
        evidence_coverage=coverage,
        decisions=decisions,
    )


def attribute_edges(
    result: ProtocolResult,
    ground_truth: int,
) -> Tuple[Set[Tuple[Any, Any]], Set[Tuple[Any, Any]]]:
    """Attribute edges from time-indexed first deliveries.

    - edges_carrying_evidence: any edge that performed ≥1 first delivery into
      its head.
    - edges_helping_correct: edges whose first delivery into node v contributed
      a token to v's known set, where v's *final* decision equals ground truth.

    This is contribution-to-evidence at the receiving correct node — not a
    test of causal necessity (alternate paths are not counterfactually removed).
    """
    y = ground_truth
    carry: Set[Tuple[Any, Any]] = set()
    help_e: Set[Tuple[Any, Any]] = set()
    # first delivery into v of token tok: record edge (u,v)
    first_into: Dict[Tuple[Any, str], Tuple[Any, Any]] = {}
    for ev in result.deliveries:
        carry.add((ev.src, ev.dst))
        key = (ev.dst, ev.token)
        if key not in first_into:
            first_into[key] = (ev.src, ev.dst)

    for nid, st in result.nodes.items():
        if st.decision != y:
            continue
        for tok in st.known:
            e = first_into.get((nid, tok))
            if e is not None:
                help_e.add(e)
    return carry, help_e


def first_correct_agreement_round(round_evals: List[Dict[str, Any]], y: int
                                  ) -> Optional[int]:
    for re in round_evals:
        if re["round_idx"] < 0:
            continue
        if (re.get("agreement_correct") is True
                and re.get("agreement_label") == y
                and (re.get("agreement_frac") or 0) >= 0.5):
            return int(re["round_idx"])
    return None


def first_collective_correct_round(round_evals: List[Dict[str, Any]]
                                   ) -> Optional[int]:
    for re in round_evals:
        if re["round_idx"] < 0:
            continue
        if re.get("collective_correct") is True:
            return int(re["round_idx"])
    return None


def network_view_from_bundle(bundle: EvidenceBundle) -> NetworkEvidenceView:
    return bundle.network_view()
