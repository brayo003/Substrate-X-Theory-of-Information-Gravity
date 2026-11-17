"""Analysis pipeline for the rule-adaptation feasibility study.

Produces the four result tables required by the directive:

  MODEL_COMPARISON.csv   per-model aggregates with bootstrap CIs
  PAIRED_STATISTICS.csv  paired D-vs-baseline comparisons, Holm corrected
  RULE_EVOLUTION_LOG.csv all create/modify/disable/delete events (held-out)
  COMPLEXITY_METRICS.csv computational and rule-library costs

Reads only results/raw/eval_*.csv.  Deterministic: bootstrap seed is fixed.
"""
from __future__ import annotations

import csv
import json
import os
from collections import defaultdict
from typing import Dict, List, Sequence, Tuple

import numpy as np
from scipy import stats

HERE = os.path.dirname(os.path.abspath(__file__))
RAW = os.path.join(HERE, "results", "raw")
OUT = os.path.join(HERE, "results", "analysis")
BOOT = 10_000
RNG_SEED = 20261115

PRIMARY = ["final_violations", "recovery_ops", "auc_violations", "success"]
MODELS = ["A", "B", "C", "D", "Dc", "E1", "E2"]
PAIRS = [("D", "A"), ("D", "B"), ("D", "C"), ("D", "E1"), ("D", "E2"),
         ("Dc", "C"), ("Dc", "B"), ("D", "Dc")]


def load_runs(split: str = "eval") -> List[dict]:
    with open(os.path.join(RAW, f"{split}_runs.csv"), encoding="utf-8") as f:
        return list(csv.DictReader(f))


def load_csv(name: str) -> List[dict]:
    path = os.path.join(RAW, name)
    if not os.path.exists(path) or os.path.getsize(path) == 0:
        return []
    with open(path, encoding="utf-8") as f:
        return list(csv.DictReader(f))


def as_float(x: str) -> float:
    try:
        v = float(x)
    except (TypeError, ValueError):
        return float("nan")
    return v


def pivot(rows: List[dict], metric: str) -> Dict[str, Dict[str, float]]:
    out: Dict[str, Dict[str, float]] = defaultdict(dict)
    for r in rows:
        out[r["model"]][r["case_id"]] = as_float(r[metric])
    return out


def paired_vectors(rows, m1: str, m2: str, metric: str
                   ) -> Tuple[np.ndarray, np.ndarray, List[str]]:
    p = pivot(rows, metric)
    ids = sorted(set(p[m1]) & set(p[m2]), key=int)
    a = np.array([p[m1][c] for c in ids], dtype=float)
    b = np.array([p[m2][c] for c in ids], dtype=float)
    return a, b, ids


def boot_ci(x: np.ndarray, rng: np.random.Generator,
            stat=np.mean) -> Tuple[float, float]:
    if len(x) == 0:
        return float("nan"), float("nan")
    idx = rng.integers(0, len(x), size=(BOOT, len(x)))
    vals = stat(x[idx], axis=1)
    return float(np.percentile(vals, 2.5)), float(np.percentile(vals, 97.5))


def cliffs_delta(a: np.ndarray, b: np.ndarray) -> float:
    """P(a > b) - P(a < b), computed exactly over all pairs."""
    if len(a) == 0 or len(b) == 0:
        return float("nan")
    gt = sum((a[:, None] > b[None, :]).ravel())
    lt = sum((a[:, None] < b[None, :]).ravel())
    return float((gt - lt) / (len(a) * len(b)))


def mcnemar_exact(a: np.ndarray, b: np.ndarray) -> Tuple[int, int, float]:
    """Exact McNemar for paired binary outcomes (a = reference, b = other)."""
    a = np.asarray(a, dtype=int)
    b = np.asarray(b, dtype=int)
    n01 = int(np.sum((a == 0) & (b == 1)))
    n10 = int(np.sum((a == 1) & (b == 0)))
    n = n01 + n10
    if n == 0:
        return n01, n10, 1.0
    p = stats.binomtest(min(n01, n10), n, 0.5).pvalue
    return n01, n10, float(min(1.0, p))


def holm(pvals: Sequence[float]) -> List[float]:
    m = len(pvals)
    order = sorted(range(m), key=lambda i: pvals[i])
    adj = [1.0] * m
    prev = 0.0
    for rank, i in enumerate(order):
        val = min(1.0, (m - rank) * pvals[i])
        val = max(val, prev)
        adj[i] = val
        prev = val
    return adj


def model_comparison(rows: List[dict]) -> List[dict]:
    rng = np.random.default_rng(RNG_SEED)
    metrics = ["final_violations", "recovery_ops", "auc_violations",
               "success", "ops", "evals", "edits", "mods", "applications",
               "library_total", "library_enabled", "distinct_rules_used",
               "rule_reuse", "rule_stability", "n_censored", "n_recovered",
               "runtime_s", "peak_mem_kb"]
    out = []
    for m in MODELS:
        sub = [r for r in rows if r["model"] == m]
        if not sub:
            continue
        rec = {"model": m, "n_cases": len(sub)}
        for metric in metrics:
            vals = np.array([as_float(r[metric]) for r in sub], dtype=float)
            vals = vals[~np.isnan(vals)]
            if len(vals) == 0:
                continue
            lo, hi = boot_ci(vals, rng)
            rec[f"{metric}_mean"] = round(float(vals.mean()), 4)
            rec[f"{metric}_sd"] = round(float(vals.std(ddof=1)), 4) if len(vals) > 1 else 0.0
            rec[f"{metric}_median"] = round(float(np.median(vals)), 4)
            rec[f"{metric}_ci_lo"] = round(lo, 4)
            rec[f"{metric}_ci_hi"] = round(hi, 4)
        succ = np.array([as_float(r["success"]) for r in sub])
        total_ops = float(np.sum([as_float(r["ops"]) for r in sub]))
        rec["ops_per_success"] = round(total_ops / max(1.0, succ.sum()), 2)
        out.append(rec)
    return out


def paired_statistics(rows: List[dict]) -> List[dict]:
    rng = np.random.default_rng(RNG_SEED)
    raw: List[dict] = []
    for m1, m2 in PAIRS:
        for metric in PRIMARY:
            a, b, ids = paired_vectors(rows, m1, m2, metric)
            if len(a) == 0:
                continue
            if metric == "success":
                n01, n10, p = mcnemar_exact(a, b)
                rec = dict(
                    comparison=f"{m1}_vs_{m2}", metric=metric, n_pairs=len(ids),
                    mean_a=round(float(a.mean()), 4),
                    mean_b=round(float(b.mean()), 4),
                    mean_diff=round(float(a.mean() - b.mean()), 4),
                    median_diff=round(float(np.median(a - b)), 4),
                    ci_lo="", ci_hi="", test="mcnemar_exact", statistic=f"{n10}/{n01}",
                    p_value=round(p, 6), effect_size=round(float(a.mean() - b.mean()), 4),
                    effect_type="risk_difference", note="n10 = a wins, n01 = b wins",
                )
                raw.append(rec)
                continue
            diff = a - b
            lo, hi = boot_ci(diff, rng)
            try:
                res = stats.wilcoxon(a, b, zero_method="wilcox", alternative="two-sided")
                stat, p = float(res.statistic), float(res.pvalue)
            except ValueError:
                stat, p = float("nan"), 1.0
            # rank-biserial correlation from the signed ranks
            r = stats.rankdata(np.abs(diff))
            pos = float(np.sum(r[diff > 0]))
            neg = float(np.sum(r[diff < 0]))
            denom = pos + neg
            rbc = (pos - neg) / denom if denom else 0.0
            rec = dict(
                comparison=f"{m1}_vs_{m2}", metric=metric, n_pairs=len(ids),
                mean_a=round(float(a.mean()), 4),
                mean_b=round(float(b.mean()), 4),
                mean_diff=round(float(diff.mean()), 4),
                median_diff=round(float(np.median(diff)), 4),
                ci_lo=round(lo, 4), ci_hi=round(hi, 4),
                test="wilcoxon_signed_rank", statistic=round(stat, 4),
                p_value=round(p, 6), effect_size=round(float(rbc), 4),
                effect_type="rank_biserial",
                note="negative diff favours a (the first model named)",
            )
            raw.append(rec)
    # Holm correction within each metric family
    for metric in PRIMARY:
        fam = [r for r in raw if r["metric"] == metric]
        adj = holm([r["p_value"] for r in fam])
        for r, q in zip(fam, adj):
            r["p_holm"] = round(q, 6)
            r["significant_holm_0.05"] = int(q < 0.05)
    return raw


def evolution_log() -> List[dict]:
    events = load_csv("eval_events.csv")
    keep = ["case_id", "model", "op", "event", "uid", "old_spec", "new_spec",
            "reason", "target", "effect_observed", "effect_improved",
            "unnecessary", "prior_uses_50"]
    out = []
    for e in events:
        out.append({k: e.get(k, "") for k in keep})
    return out


def complexity_metrics(rows: List[dict]) -> List[dict]:
    out = []
    by_model = defaultdict(list)
    for r in rows:
        by_model[r["model"]].append(r)
    for m in MODELS:
        sub = by_model.get(m, [])
        if not sub:
            continue
        n = len(sub)
        rec = dict(
            model=m, n_cases=n,
            mean_ops=round(np.mean([as_float(r["ops"]) for r in sub]), 2),
            total_evals=int(np.sum([as_float(r["evals"]) for r in sub])),
            total_edits=int(np.sum([as_float(r["edits"]) for r in sub])),
            total_mods=int(np.sum([as_float(r["mods"]) for r in sub])),
            mean_mods_per_case=round(np.mean([as_float(r["mods"]) for r in sub]), 2),
            mean_library_total=round(np.mean([as_float(r["library_total"]) for r in sub]), 2),
            max_library_total=int(np.max([as_float(r["library_total"]) for r in sub])),
            mean_library_enabled=round(np.mean([as_float(r["library_enabled"]) for r in sub]), 2),
            mean_peak_mem_kb=round(np.mean([as_float(r["peak_mem_kb"]) for r in sub]), 2),
            mean_runtime_s=round(np.mean([as_float(r["runtime_s"]) for r in sub]), 4),
            total_runtime_s=round(np.sum([as_float(r["runtime_s"]) for r in sub]), 2),
            total_instances=int(np.sum([as_float(r["applications"]) for r in sub])),
            mean_rule_reuse=round(np.mean([as_float(r["rule_reuse"]) for r in sub]), 3),
            mean_rule_stability=round(np.mean([as_float(r["rule_stability"]) for r in sub]), 3),
            censored_phases=int(np.sum([as_float(r["n_censored"]) for r in sub])),
            successful_cases=int(np.sum([as_float(r["success"]) for r in sub])),
        )
        rec["ops_per_success"] = round(
            rec["mean_ops"] * n / max(1, rec["successful_cases"]), 2)
        rec["instances_per_edit"] = round(
            rec["total_instances"] / max(1, rec["total_edits"]), 3)
        out.append(rec)
    return out


def stability_metrics(rows: List[dict]) -> List[dict]:
    """Rule-level churn, taken from D's evolution events and decision traces."""
    events = load_csv("eval_events.csv")
    decisions = load_csv("eval_decisions.csv")
    out = []
    for m in ["C", "D", "Dc"]:
        ev = [e for e in events if e["model"] == m]
        ds = [d for d in decisions if d["model"] == m]
        cases = {e["case_id"] for e in ev}
        counts = defaultdict(int)
        for e in ev:
            counts[e["event"]] += 1
        # oscillation proxy: consecutive decisions that alternate between the
        # same two total-violation counts without reaching zero
        rev = 0
        for cid in {d["case_id"] for d in ds}:
            seq = [int(float(d["total"])) for d in ds if d["case_id"] == cid]
            for i in range(2, len(seq)):
                if seq[i] == seq[i - 2] and seq[i] != 0 and seq[i] != seq[i - 1]:
                    rev += 1
        out.append(dict(
            model=m,
            cases_with_events=len(cases),
            creates=counts.get("create", 0),
            modifies=counts.get("modify", 0),
            disables=counts.get("disable", 0),
            deletes=counts.get("delete", 0),
            events_total=len(ev),
            oscillation_steps=rev,
            mean_events_per_case=round(len(ev) / max(1, len({d["case_id"] for d in ds})), 2),
        ))
    return out


def write_csv(path: str, rows: List[dict]) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    if not rows:
        return
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        for r in rows:
            w.writerow(r)


def main() -> int:
    rows = load_runs("eval")
    os.makedirs(OUT, exist_ok=True)
    mc = model_comparison(rows)
    ps = paired_statistics(rows)
    rl = evolution_log()
    cx = complexity_metrics(rows)
    st = stability_metrics(rows)

    write_csv(os.path.join(HERE, "MODEL_COMPARISON.csv"), mc)
    write_csv(os.path.join(HERE, "PAIRED_STATISTICS.csv"), ps)
    write_csv(os.path.join(HERE, "RULE_EVOLUTION_LOG.csv"), rl)
    write_csv(os.path.join(HERE, "COMPLEXITY_METRICS.csv"), cx)
    write_csv(os.path.join(OUT, "STABILITY_METRICS.csv"), st)

    summary = dict(
        cases=len({r["case_id"] for r in rows}),
        models=MODELS,
        verdict_inputs={m: dict(
            successes=sum(int(as_float(r["success"])) for r in rows if r["model"] == m),
            total_violations=sum(int(as_float(r["final_violations"])) for r in rows if r["model"] == m),
        ) for m in MODELS},
        n_paired_tests=len(ps),
    )
    with open(os.path.join(OUT, "analysis_summary.json"), "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)
    print(json.dumps(summary["verdict_inputs"], indent=1))
    print(f"wrote {len(mc)} model rows, {len(ps)} paired tests, {len(rl)} events, {len(cx)} complexity rows")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
