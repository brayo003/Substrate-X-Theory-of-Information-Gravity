"""Metric extraction and statistical helpers (incl. NI / TOST)."""

from __future__ import annotations

import math
from typing import Any, Dict, List, Optional, Sequence, Tuple

from .evaluator import (
    evaluate_protocol,
    first_collective_correct_round,
    first_correct_agreement_round,
)
from .protocol import ProtocolResult


# Pre-registered before v2 analysis (see AUDIT_REPORT.md / specification).
NONINFERIORITY_MARGIN_FRAC_CORRECT = 0.05


def extract_seed_metrics(
    model: str,
    seed: int,
    condition_id: str,
    result: ProtocolResult,
    eval_out: Dict[str, Any],
    timeline,
    created_all: Optional[set] = None,
) -> Dict[str, Any]:
    y = eval_out["ground_truth"]
    n = len(result.nodes)
    n_correct = int(round(eval_out["frac_correct"] * n)) if n else 0

    t_agree = first_correct_agreement_round(eval_out["round_evals"], y)
    t_coll = first_collective_correct_round(eval_out["round_evals"])

    msgs_per_correct = (
        result.total_messages / n_correct if n_correct > 0 else float("nan"))

    created_all = created_all or set()
    help_set = eval_out.get("edges_helping_correct") or set()
    carry_set = eval_out.get("edges_carrying_evidence") or set()
    created_used = sum(1 for e in created_all if result.edge_delivery_count.get(e, 0) > 0)
    created_help = sum(1 for e in created_all if e in help_set)
    created_carry = sum(1 for e in created_all if e in carry_set)

    final_graph = timeline.graphs[-1] if timeline.graphs else None
    final_blocks = (timeline.partitions[-1].num_blocks()
                    if timeline.partitions and timeline.partitions[-1] is not None
                    else float("nan"))

    last_correct = eval_out.get("agreement_correct")
    agr_maintained = int(bool(last_correct is True))

    return dict(
        condition_id=condition_id,
        model=model,
        seed=seed,
        ground_truth=y,
        frac_correct=eval_out["frac_correct"],
        frac_incorrect=eval_out["frac_incorrect"],
        frac_undecided=eval_out["frac_undecided"],
        collective=eval_out.get("collective"),
        collective_correct=(
            1 if eval_out.get("collective_correct") is True else
            0 if eval_out.get("collective_correct") is False else None),
        agreement_frac=eval_out.get("agreement_frac") or 0.0,
        agreement_correct=(
            1 if eval_out.get("agreement_correct") is True else
            0 if eval_out.get("agreement_correct") is False else None),
        agreement_maintained=agr_maintained,
        time_to_correct_agreement=t_agree if t_agree is not None else -1,
        time_to_collective_correct=t_coll if t_coll is not None else -1,
        total_messages=result.total_messages,
        unique_delivered=result.total_unique_delivered,
        duplicates_prevented=result.total_duplicates_prevented,
        rounds_executed=result.rounds_executed,
        stopped_reason=result.stopped_reason,
        messages_per_correct_node=msgs_per_correct,
        evidence_coverage=eval_out.get("evidence_coverage") or 0.0,
        final_edges=len(final_graph) if final_graph is not None else 0,
        final_blocks=final_blocks,
        total_created=timeline.total_created,
        total_removed=timeline.total_removed,
        created_edges_used=created_used,
        created_edges_carrying=created_carry,
        created_edges_helping_correct=created_help,
        control_infeasible=int(getattr(timeline, "control_infeasible", False)),
        decision_rule=result.decision_rule,
    )


def mean_std(vals: Sequence[float]) -> Tuple[float, float]:
    xs = [float(v) for v in vals if v == v]
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
    by_seed_a, by_seed_b = {}, {}
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
    d = [x for x in diffs if x == x and x != 0]
    n = len(d)
    if n < 10:
        return float("nan"), float("nan")
    order = sorted(range(n), key=lambda i: abs(d[i]))
    ranks = [0.0] * n
    i = 0
    while i < n:
        j = i
        while j + 1 < n and abs(d[order[j + 1]]) == abs(d[order[i]]):
            j += 1
        avg = (i + j + 2) / 2.0
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
    p = 2.0 * (1.0 - _phi(abs(z)))
    return W, min(max(p, 0.0), 1.0)


def _phi(z: float) -> float:
    return 0.5 * (1.0 + math.erf(z / math.sqrt(2.0)))


def _phi_inv_approx(p: float) -> float:
    """Approximate normal quantile (Beasley-Springer-Moro-ish rational)."""
    # For NI we mainly need one-sided normal test on mean; use erf inverse via
    # binary search for simplicity and robustness.
    if p <= 0:
        return float("-inf")
    if p >= 1:
        return float("inf")
    lo, hi = -10.0, 10.0
    for _ in range(80):
        mid = 0.5 * (lo + hi)
        if _phi(mid) < p:
            lo = mid
        else:
            hi = mid
    return 0.5 * (lo + hi)


def one_sided_mean_test(diffs: Sequence[float], null_mean: float,
                        alternative: str = "greater") -> Dict[str, Any]:
    """Normal-approx one-sided test on paired mean.

    alternative='greater': H1: mean > null_mean (e.g. NI of D vs CR:
      diffs = D-CR, null_mean = -δ, reject H0: mean ≤ -δ).
    alternative='less': H1: mean < null_mean.
    """
    xs = [float(x) for x in diffs if x == x]
    n = len(xs)
    m, s = mean_std(xs)
    if n < 2 or not (s == s):
        return dict(n=n, mean=m, se=float("nan"), z=float("nan"), p=float("nan"),
                    null_mean=null_mean, alternative=alternative)
    se = s / math.sqrt(n)
    if se <= 0:
        z = float("inf") if m > null_mean else (float("-inf") if m < null_mean else 0.0)
    else:
        z = (m - null_mean) / se
    if alternative == "greater":
        p = 1.0 - _phi(z)
    else:
        p = _phi(z)
    return dict(n=n, mean=m, se=se, z=z, p=min(max(p, 0.0), 1.0),
                null_mean=null_mean, alternative=alternative)


def tost_equivalence(diffs: Sequence[float], delta: float,
                     alpha: float = 0.05) -> Dict[str, Any]:
    """Two one-sided tests for equivalence at margin ±delta.

    Equivalence if both: mean > -delta and mean < +delta at level alpha
    (each one-sided).
    """
    low = one_sided_mean_test(diffs, -delta, alternative="greater")
    high = one_sided_mean_test(diffs, delta, alternative="less")
    equiv = (low["p"] == low["p"] and high["p"] == high["p"]
             and low["p"] < alpha and high["p"] < alpha)
    return dict(
        delta=delta, alpha=alpha,
        p_lower=low["p"], p_upper=high["p"],
        mean=low["mean"], n=low["n"],
        equivalent=bool(equiv),
        lower_test=low, upper_test=high,
    )


def noninferiority_test(diffs: Sequence[float], delta: float,
                        alpha: float = 0.05) -> Dict[str, Any]:
    """NI test: diffs = D - CR on frac_correct; H0: mean ≤ -delta.

    Reject H0 (declare non-inferior) if one-sided p < alpha for mean > -delta.
    """
    t = one_sided_mean_test(diffs, -delta, alternative="greater")
    t["delta"] = delta
    t["alpha"] = alpha
    t["noninferior"] = bool(t["p"] == t["p"] and t["p"] < alpha)
    return t


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
