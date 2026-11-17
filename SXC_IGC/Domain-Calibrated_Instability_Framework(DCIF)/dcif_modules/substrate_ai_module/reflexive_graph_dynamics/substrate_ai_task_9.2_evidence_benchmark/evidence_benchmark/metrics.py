"""Metric extraction and statistical helpers."""

from __future__ import annotations

import math
from typing import Any, Dict, List, Optional, Sequence, Tuple

from .protocol import ProtocolResult


def first_correct_agreement_round(result: ProtocolResult, y: int) -> Optional[int]:
    for rm in result.rounds:
        if rm.agreement_correct is True and rm.agreement_label == y and rm.agreement_frac >= 0.5:
            # require at least half the nodes on the correct label
            return rm.round_idx
    return None


def first_collective_correct_round(result: ProtocolResult) -> Optional[int]:
    for rm in result.rounds:
        if rm.collective_correct is True:
            return rm.round_idx
    return None


def agreement_maintained(result: ProtocolResult, y: int) -> bool:
    if not result.rounds:
        return False
    last = result.rounds[-1]
    return bool(last.agreement_correct is True and last.agreement_label == y)


def extract_seed_metrics(
    model: str,
    seed: int,
    condition_id: str,
    result: ProtocolResult,
    y: int,
    timeline,
    created_all: Optional[set] = None,
) -> Dict[str, Any]:
    last = result.rounds[-1] if result.rounds else None
    n = len(result.nodes)
    n_correct = sum(1 for st in result.nodes.values() if st.decision == y)
    n_incorrect = sum(
        1 for st in result.nodes.values()
        if st.decision is not None and st.decision != y)
    n_und = sum(1 for st in result.nodes.values() if st.decision is None)

    t_agree = first_correct_agreement_round(result, y)
    t_coll = first_collective_correct_round(result)

    msgs_per_correct = (
        result.total_messages / n_correct if n_correct > 0 else float("nan"))

    created_all = created_all or set()
    created_used = sum(1 for e in created_all if result.edge_delivery_count.get(e, 0) > 0)
    created_help = sum(1 for e in created_all if e in result.edges_helping_correct)

    # reachability from evidence sources on final graph
    sources = [n for n, st in result.nodes.items()
               if any(True for _ in [0])]  # placeholder replaced below
    # evidence holders: nodes that started with local evidence — approximate
    # by tokens that exist; use final graph BFS from all nodes that have local
    # — caller can pass; here compute coverage as mean known tokens / total tokens
    all_tokens = set()
    for st in result.nodes.values():
        all_tokens |= set(st.known)
    # better: coverage = mean fraction of global unique tokens known
    # Global unique = union; each node's coverage
    global_tokens = set()
    for st in result.nodes.values():
        global_tokens |= set(st.known.keys())
    # Actually global should be all tokens that exist in the bundle; use union of known at end
    # which under full connectivity equals all generated tokens present in network
    coverage = 0.0
    if global_tokens:
        coverage = sum(len(st.known) / len(global_tokens) for st in result.nodes.values()) / n

    final_graph = timeline.graphs[-1] if timeline.graphs else None
    final_blocks = (timeline.partitions[-1].num_blocks()
                    if timeline.partitions and timeline.partitions[-1] is not None
                    else float("nan"))

    return dict(
        condition_id=condition_id,
        model=model,
        seed=seed,
        ground_truth=y,
        frac_correct=n_correct / n,
        frac_incorrect=n_incorrect / n,
        frac_undecided=n_und / n,
        collective=last.collective if last else None,
        collective_correct=(1 if last and last.collective_correct else
                            0 if last and last.collective_correct is False else None),
        agreement_frac=last.agreement_frac if last else 0.0,
        agreement_correct=(1 if last and last.agreement_correct else
                           0 if last and last.agreement_correct is False else None),
        agreement_maintained=int(agreement_maintained(result, y)),
        time_to_correct_agreement=t_agree if t_agree is not None else -1,
        time_to_collective_correct=t_coll if t_coll is not None else -1,
        total_messages=result.total_messages,
        unique_delivered=result.total_unique_delivered,
        duplicates_prevented=result.total_duplicates_prevented,
        rounds_executed=result.rounds_executed,
        stopped_reason=result.stopped_reason,
        messages_per_correct_node=msgs_per_correct,
        evidence_coverage=coverage,
        final_edges=len(final_graph) if final_graph is not None else 0,
        final_blocks=final_blocks,
        total_created=timeline.total_created,
        total_removed=timeline.total_removed,
        created_edges_used=created_used,
        created_edges_helping_correct=created_help,
        control_infeasible=int(getattr(timeline, "control_infeasible", False)),
    )


def mean_std(vals: Sequence[float]) -> Tuple[float, float]:
    xs = [float(v) for v in vals if v == v]  # drop NaN
    if not xs:
        return float("nan"), float("nan")
    m = sum(xs) / len(xs)
    if len(xs) == 1:
        return m, 0.0
    var = sum((x - m) ** 2 for x in xs) / (len(xs) - 1)
    return m, math.sqrt(var)


def paired_diffs(rows: List[Dict[str, Any]], model_a: str, model_b: str,
                 metrics: Sequence[str], condition_id: Optional[str] = None
                 ) -> List[Dict[str, Any]]:
    by_seed_a = {}
    by_seed_b = {}
    for r in rows:
        if condition_id is not None and r.get("condition_id") != condition_id:
            continue
        if r.get("control_infeasible"):
            continue
        key = (r["condition_id"], r["seed"])
        if r["model"] == model_a:
            by_seed_a[key] = r
        elif r["model"] == model_b:
            by_seed_b[key] = r
    out = []
    keys = sorted(set(by_seed_a) & set(by_seed_b))
    for metric in metrics:
        diffs = []
        for k in keys:
            va, vb = by_seed_a[k].get(metric), by_seed_b[k].get(metric)
            if va is None or vb is None:
                continue
            try:
                diffs.append(float(va) - float(vb))
            except (TypeError, ValueError):
                continue
        m, s = mean_std(diffs)
        # normal approx 95% CI
        n = len(diffs)
        if n >= 2 and s == s:
            se = s / math.sqrt(n)
            ci_lo, ci_hi = m - 1.96 * se, m + 1.96 * se
        else:
            ci_lo = ci_hi = float("nan")
        out.append(dict(
            condition_id=condition_id or "ALL",
            pair=f"{model_a}-{model_b}",
            metric=metric,
            n=n,
            mean_diff=m,
            std_diff=s,
            ci95_lo=ci_lo,
            ci95_hi=ci_hi,
        ))
    return out


def wilcoxon_signed_rank(diffs: Sequence[float]) -> Tuple[float, float]:
    """Two-sided Wilcoxon signed-rank statistic and normal-approx p-value.

    Returns (W, p). If too few nonzero pairs, returns (nan, nan).
    """
    d = [x for x in diffs if x == x and x != 0]
    n = len(d)
    if n < 10:
        return float("nan"), float("nan")
    # rank absolute values
    order = sorted(range(n), key=lambda i: abs(d[i]))
    ranks = [0.0] * n
    i = 0
    while i < n:
        j = i
        while j + 1 < n and abs(d[order[j + 1]]) == abs(d[order[i]]):
            j += 1
        avg = (i + j + 2) / 2.0  # 1-based ranks averaged
        for k in range(i, j + 1):
            ranks[order[k]] = avg
        i = j + 1
    w_pos = sum(ranks[i] for i in range(n) if d[i] > 0)
    w_neg = sum(ranks[i] for i in range(n) if d[i] < 0)
    W = min(w_pos, w_neg)
    mean_w = n * (n + 1) / 4.0
    var_w = n * (n + 1) * (2 * n + 1) / 24.0
    if var_w <= 0:
        return W, float("nan")
    z = (W - mean_w) / math.sqrt(var_w)
    # two-sided from normal
    p = 2.0 * (1.0 - _phi(abs(z)))
    return W, min(max(p, 0.0), 1.0)


def _phi(z: float) -> float:
    # standard normal CDF via erf
    return 0.5 * (1.0 + math.erf(z / math.sqrt(2.0)))


def holm_bonferroni(pvals: List[Tuple[str, float]], alpha: float = 0.05
                    ) -> List[Dict[str, Any]]:
    indexed = [(i, name, p) for i, (name, p) in enumerate(pvals)]
    indexed.sort(key=lambda t: float("inf") if t[2] != t[2] else t[2])
    m = len(indexed)
    out = []
    reject_rest = False
    for rank, (i, name, p) in enumerate(indexed):
        thresh = alpha / (m - rank)
        sig = (not reject_rest) and (p == p) and (p < thresh)
        if not sig:
            reject_rest = True
        out.append(dict(hypothesis=name, p=p, holm_threshold=thresh,
                        significant=bool(sig), rank=rank + 1))
    out.sort(key=lambda d: d["rank"])
    return out
