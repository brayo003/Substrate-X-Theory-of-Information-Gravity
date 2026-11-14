"""
EXP3 Analysis — Predictive Information and Statistical Analysis
==============================================================

Runs:
  1. Main statistical analysis from exp3_main_results.json
  2. Predictive-information analysis from exp3_main_per_tick.jsonl
     - For horizons h in {1,2,3,5,8}
     - Threshold trained on seeds 7000-7019, evaluated on 7020-7039
     - AUROC, Brier score, precision, recall, F1
     - Cross-correlation (lead-lag)
  3. Event-type (A/B/C/D) breakdown
  4. Mechanism isolation analysis

Outputs:
  exp3_predictive_analysis.json   - Full predictive results
  exp3_full_analysis.json         - Combined statistical + predictive
"""

from __future__ import annotations
import json
import math
import os
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
_PARENT = os.path.dirname(_HERE)
if _PARENT not in sys.path:
    sys.path.insert(0, _PARENT)

import numpy as np

# ---------------------------------------------------------------------------
# Load data
# ---------------------------------------------------------------------------

def load_summaries(path: str) -> list[dict]:
    with open(path) as f:
        return json.load(f)


def load_per_tick(path: str, conditions: list[str] | None = None,
                  seed_range: tuple[int,int] | None = None) -> list[dict]:
    """Stream JSONL, optionally filtering by condition and seed range."""
    recs = []
    with open(path) as f:
        for line in f:
            rec = json.loads(line)
            if conditions and rec["condition"] not in conditions:
                continue
            if seed_range:
                lo, hi = seed_range
                if not (lo <= rec["seed"] < hi):
                    continue
            recs.append(rec)
    return recs


# ---------------------------------------------------------------------------
# Statistical helpers
# ---------------------------------------------------------------------------

def _paired_ttest(a: list[float], b: list[float]) -> tuple[float, float]:
    d = [ai - bi for ai, bi in zip(a, b)]
    n = len(d)
    if n < 2:
        return float("nan"), float("nan")
    mean_d = sum(d) / n
    var_d = sum((x - mean_d)**2 for x in d) / (n - 1)
    if var_d == 0:
        return float("nan"), float("nan")
    t = mean_d / math.sqrt(var_d / n)
    p = math.erfc(abs(t) / math.sqrt(2.0))
    return t, p


def _bootstrap_ci(d: list[float], n_boot: int = 2000) -> tuple[float, float]:
    rng = np.random.default_rng(42)
    arr = np.array(d)
    boot = np.array([float(np.mean(rng.choice(arr, size=len(arr), replace=True)))
                     for _ in range(n_boot)])
    return float(np.percentile(boot, 2.5)), float(np.percentile(boot, 97.5))


def _cohens_d(d: list[float]) -> float:
    n = len(d)
    if n < 2:
        return float("nan")
    mean_d = sum(d) / n
    std_d = math.sqrt(sum((x - mean_d)**2 for x in d) / (n - 1))
    return mean_d / std_d if std_d > 0 else float("nan")


def compare(summaries: list[dict], cond_a: str, cond_b: str,
            metric: str = "coord_completion_rate") -> dict:
    a_map = {r["seed"]: r[metric] for r in summaries
             if r["condition"] == cond_a and r.get(metric) is not None}
    b_map = {r["seed"]: r[metric] for r in summaries
             if r["condition"] == cond_b and r.get(metric) is not None}
    seeds = sorted(set(a_map) & set(b_map))
    if not seeds:
        return {"error": "no_paired_seeds"}
    a_v = [a_map[s] for s in seeds]
    b_v = [b_map[s] for s in seeds]
    d_v = [a - b for a, b in zip(a_v, b_v)]
    t, p = _paired_ttest(a_v, b_v)
    ci = _bootstrap_ci(d_v)
    cd = _cohens_d(d_v)
    return {
        "cond_a": cond_a, "cond_b": cond_b,
        "n": len(d_v),
        "mean_a": round(float(np.mean(a_v)), 6),
        "mean_b": round(float(np.mean(b_v)), 6),
        "mean_diff": round(float(np.mean(d_v)), 6),
        "std_diff": round(float(np.std(d_v, ddof=1)), 6) if len(d_v) > 1 else 0.,
        "ci_95": [round(ci[0], 6), round(ci[1], 6)],
        "t": round(t, 4) if not math.isnan(t) else None,
        "p_ttest": round(p, 6) if not math.isnan(p) else None,
        "p_bonferroni": round(min(p * 6, 1.0), 6) if not math.isnan(p) else None,
        "cohens_d": round(cd, 4) if not math.isnan(cd) else None,
        "significant": not math.isnan(p) and p < (0.05 / 6),
    }


# ---------------------------------------------------------------------------
# Predictive-information analysis
# ---------------------------------------------------------------------------

def auroc(scores: list[float], labels: list[int]) -> float:
    """Trapezoidal AUROC from scalar scores and binary labels."""
    n = len(scores)
    if n == 0:
        return float("nan")
    pos = sum(labels)
    neg = n - pos
    if pos == 0 or neg == 0:
        return float("nan")
    # Sort by descending score
    pairs = sorted(zip(scores, labels), key=lambda x: -x[0])
    tpr_points = [0.0]
    fpr_points = [0.0]
    tp = fp = 0
    for _, label in pairs:
        if label == 1:
            tp += 1
        else:
            fp += 1
        tpr_points.append(tp / pos)
        fpr_points.append(fp / neg)
    # Trapezoidal integration
    area = 0.0
    for i in range(1, len(tpr_points)):
        area += (fpr_points[i] - fpr_points[i-1]) * (tpr_points[i] + tpr_points[i-1]) / 2
    return float(area)


def brier_score(probs: list[float], labels: list[int]) -> float:
    if not probs:
        return float("nan")
    return float(np.mean([(p - l)**2 for p, l in zip(probs, labels)]))


def precision_recall_f1(scores: list[float], labels: list[int],
                         threshold: float) -> tuple[float, float, float]:
    preds = [1 if s >= threshold else 0 for s in scores]
    tp = sum(1 for p, l in zip(preds, labels) if p == 1 and l == 1)
    fp = sum(1 for p, l in zip(preds, labels) if p == 1 and l == 0)
    fn = sum(1 for p, l in zip(preds, labels) if p == 0 and l == 1)
    prec = tp / (tp + fp) if (tp + fp) > 0 else 0.0
    rec  = tp / (tp + fn) if (tp + fn) > 0 else 0.0
    f1   = 2 * prec * rec / (prec + rec) if (prec + rec) > 0 else 0.0
    return prec, rec, f1


def find_best_threshold(scores: list[float], labels: list[int]) -> float:
    """Find threshold maximising F1 on training data."""
    thresholds = sorted(set(scores))
    best_f1 = -1.
    best_t = 0.0
    for t in thresholds:
        _, _, f1 = precision_recall_f1(scores, labels, t)
        if f1 > best_f1:
            best_f1 = f1
            best_t = t
    return best_t


def predictive_analysis_at_horizon(
    train_recs: list[dict],
    eval_recs: list[dict],
    h: int,
    condition: str = "spectral",
) -> dict:
    """
    Predict coord_task_active at tick t+h from c_spectral_actual at tick t.
    Train threshold on train_recs; evaluate on eval_recs.
    
    Features: c_spectral_actual[t] (available to agents in spectral condition)
    Target:   coord_task_active[t+h] (hidden from agents; used only for evaluation)
    
    No future information enters features.
    """
    # Build per-seed tick arrays for the spectral condition
    def build_arrays(recs: list[dict]) -> tuple[list[float], list[int]]:
        """Group by seed, pair t with t+h."""
        by_seed: dict[int, list[dict]] = {}
        for rec in recs:
            if rec["condition"] != condition:
                continue
            by_seed.setdefault(rec["seed"], []).append(rec)
        
        scores: list[float] = []
        labels: list[int] = []
        for seed, seed_recs in by_seed.items():
            seed_recs_sorted = sorted(seed_recs, key=lambda r: r["tick"])
            n = len(seed_recs_sorted)
            for i in range(n - h):
                feat = seed_recs_sorted[i]["c_spectral_actual"]
                tgt  = int(seed_recs_sorted[i + h]["coord_task_active"])
                scores.append(feat)
                labels.append(tgt)
        return scores, labels
    
    train_scores, train_labels = build_arrays(train_recs)
    eval_scores, eval_labels   = build_arrays(eval_recs)
    
    if not train_scores or not eval_scores:
        return {"h": h, "error": "no_data"}
    
    # Baseline predictor: predict using base rate
    base_rate = sum(train_labels) / len(train_labels)
    base_probs = [base_rate] * len(eval_labels)
    
    # Find threshold on training set
    threshold = find_best_threshold(train_scores, train_labels)
    
    # Evaluate on held-out set
    eval_auroc  = auroc(eval_scores, eval_labels)
    eval_brier  = brier_score(eval_scores, eval_labels)
    base_brier  = brier_score(base_probs, eval_labels)
    prec, rec, f1 = precision_recall_f1(eval_scores, eval_labels, threshold)
    
    # False positive / negative rates
    preds = [1 if s >= threshold else 0 for s in eval_scores]
    n_pos = sum(eval_labels)
    n_neg = len(eval_labels) - n_pos
    fp = sum(1 for p, l in zip(preds, eval_labels) if p == 1 and l == 0)
    fn = sum(1 for p, l in zip(preds, eval_labels) if p == 0 and l == 1)
    fpr = fp / n_neg if n_neg > 0 else 0.
    fnr = fn / n_pos if n_pos > 0 else 0.
    
    return {
        "h": h,
        "condition": condition,
        "threshold_trained_on_train": round(threshold, 5),
        "n_train": len(train_scores),
        "n_eval": len(eval_scores),
        "n_pos_eval": n_pos,
        "base_rate": round(base_rate, 5),
        # Eval metrics
        "auroc": round(eval_auroc, 5) if not math.isnan(eval_auroc) else None,
        "brier": round(eval_brier, 5) if not math.isnan(eval_brier) else None,
        "brier_base": round(base_brier, 5) if not math.isnan(base_brier) else None,
        "brier_skill": round(1 - eval_brier / base_brier, 5) if not math.isnan(base_brier) and base_brier > 0 else None,
        "precision": round(prec, 5),
        "recall": round(rec, 5),
        "f1": round(f1, 5),
        "fpr": round(fpr, 5),
        "fnr": round(fnr, 5),
        "auroc_vs_chance": round(eval_auroc - 0.5, 5) if not math.isnan(eval_auroc) else None,
    }


# ---------------------------------------------------------------------------
# Lead-lag cross-correlation
# ---------------------------------------------------------------------------

def cross_correlation_analysis(recs: list[dict], condition: str = "spectral",
                                lags: list[int] | None = None) -> dict:
    """
    Compute mean cross-correlation between c_spectral_actual and coord_task_active
    across seeds. Positive lag k: c_spectral at t paired with demand at t+k
    (c_spectral leads demand).
    """
    if lags is None:
        lags = [-8, -5, -3, -2, -1, 0, 1, 2, 3, 5, 8]
    
    by_seed: dict[int, list[dict]] = {}
    for rec in recs:
        if rec["condition"] != condition:
            continue
        by_seed.setdefault(rec["seed"], []).append(rec)
    
    xcorr_by_lag: dict[int, list[float]] = {k: [] for k in lags}
    
    for seed, seed_recs in by_seed.items():
        seed_recs_sorted = sorted(seed_recs, key=lambda r: r["tick"])
        c = np.array([r["c_spectral_actual"] for r in seed_recs_sorted])
        d = np.array([float(r["coord_task_active"]) for r in seed_recs_sorted])
        n = len(c)
        
        for lag in lags:
            if lag >= 0:
                # c leads d: pair c[t] with d[t+lag]
                if lag >= n: continue
                c_seg = c[:n - lag]
                d_seg = d[lag:]
            else:
                # c lags d: pair c[t] with d[t+lag] (lag<0 → d[t-|lag|])
                k = -lag
                if k >= n: continue
                c_seg = c[k:]
                d_seg = d[:n - k]
            
            if len(c_seg) < 5:
                continue
            # Normalised cross-correlation at this lag
            c_z = c_seg - c_seg.mean()
            d_z = d_seg - d_seg.mean()
            denom = np.std(c_seg) * np.std(d_seg)
            if denom < 1e-10:
                continue
            xc = float(np.mean(c_z * d_z) / denom)
            xcorr_by_lag[lag].append(xc)
    
    result = {}
    for lag in lags:
        vals = xcorr_by_lag[lag]
        if vals:
            result[str(lag)] = {
                "lag": lag,
                "mean_xcorr": round(float(np.mean(vals)), 6),
                "std_xcorr": round(float(np.std(vals)), 6),
                "n_seeds": len(vals),
            }
    
    # Find peak lag
    peak_lag = max(result.keys(),
                   key=lambda k: result[k]["mean_xcorr"],
                   default=None)
    
    return {"xcorr_by_lag": result, "peak_lag": int(peak_lag) if peak_lag else None}


# ---------------------------------------------------------------------------
# Event-type breakdown
# ---------------------------------------------------------------------------

def event_type_analysis(recs: list[dict], conditions: list[str]) -> dict:
    """
    For each condition, compute CCR by event type A/B/C/D.
    Types:
      A: precursor + task (TP opportunity)
      B: task only        (FN opportunity)
      C: precursor only   (FP risk)
      D: neither
    """
    result = {}
    for cond in conditions:
        cond_recs = [r for r in recs if r["condition"] == cond]
        type_succ = {"A": 0, "B": 0}
        type_opp  = {"A": 0, "B": 0}
        type_fp   = {"C": 0}
        type_cnt  = {"C": 0, "D": 0}
        
        for rec in cond_recs:
            et = rec["event_type"]
            if et in ("A", "B") and rec["coord_task_active"]:
                type_opp[et] += 1
                if rec["coord_success"]:
                    type_succ[et] += 1
            elif et == "C":
                type_cnt["C"] += 1
                if rec["n_cooperating"] >= rec.get("min_coord", 3):
                    type_fp["C"] += 1
        
        result[cond] = {
            "type_a_opp": type_opp["A"],
            "type_b_opp": type_opp["B"],
            "type_a_ccr": round(type_succ["A"] / type_opp["A"], 5) if type_opp["A"] > 0 else None,
            "type_b_ccr": round(type_succ["B"] / type_opp["B"], 5) if type_opp["B"] > 0 else None,
            "type_c_count": type_cnt["C"],
            "type_c_fp_rate": round(type_fp["C"] / type_cnt["C"], 5) if type_cnt["C"] > 0 else None,
            "delta_ab": round(
                (type_succ["A"] / type_opp["A"] if type_opp["A"] > 0 else 0) -
                (type_succ["B"] / type_opp["B"] if type_opp["B"] > 0 else 0),
                5
            ) if type_opp["A"] > 0 and type_opp["B"] > 0 else None,
        }
    
    return result


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    print("\n" + "=" * 65)
    print("  EXP3 PREDICTIVE INFORMATION ANALYSIS")
    print("=" * 65)
    
    results_path  = os.path.join(_HERE, "exp3_main_results.json")
    per_tick_path = os.path.join(_HERE, "exp3_main_per_tick.jsonl")
    
    if not os.path.exists(results_path):
        print(f"  ERROR: {results_path} not found. Run main experiment first.")
        return
    if not os.path.exists(per_tick_path):
        print(f"  ERROR: {per_tick_path} not found. Run main experiment first.")
        return
    
    summaries = load_summaries(results_path)
    print(f"  Loaded {len(summaries)} trial summaries")
    
    # -----------------------------------------------------------------------
    # 1. Summary statistics
    # -----------------------------------------------------------------------
    print("\n--- 1. Summary statistics ---")
    from collections import defaultdict
    by_cond = defaultdict(list)
    for r in summaries:
        by_cond[r["condition"]].append(r["coord_completion_rate"])
    
    for cond, vals in sorted(by_cond.items()):
        vals = [v for v in vals if v is not None]
        print(f"  {cond:>18}: CCR={np.mean(vals):.4f}±{np.std(vals, ddof=1):.4f}  n={len(vals)}")
    
    # -----------------------------------------------------------------------
    # 2. Main comparisons
    # -----------------------------------------------------------------------
    print("\n--- 2. Statistical comparisons ---")
    comparisons_config = [
        ("spectral", "baseline"),
        ("spectral", "online_shuffled"),
        ("spectral", "online_delayed"),
        ("spectral", "running_mean"),
        ("precursor_only", "baseline"),
        ("feedback_only", "baseline"),
    ]
    comparisons = {}
    for ca, cb in comparisons_config:
        r = compare(summaries, ca, cb)
        key = f"{ca}_vs_{cb}"
        comparisons[key] = r
        ci = r.get("ci_95", [None, None])
        print(f"  {ca:>18} vs {cb:>18}: diff={r.get('mean_diff',0):+.4f} "
              f"[{ci[0]:+.4f},{ci[1]:+.4f}] p={r.get('p_ttest','n/a')} "
              f"d={r.get('cohens_d','n/a')} {'SIG' if r.get('significant') else '~'}")
    
    # -----------------------------------------------------------------------
    # 3. Load per-tick records (spectral condition only for predictive analysis)
    # -----------------------------------------------------------------------
    print("\n--- 3. Loading per-tick records ---")
    
    # Train: seeds 7000-7019; Eval: 7020-7039
    TRAIN_RANGE = (7000, 7020)
    EVAL_RANGE  = (7020, 7040)
    
    train_recs = load_per_tick(per_tick_path, conditions=["spectral"], seed_range=TRAIN_RANGE)
    eval_recs  = load_per_tick(per_tick_path, conditions=["spectral"], seed_range=EVAL_RANGE)
    all_spec_recs = train_recs + eval_recs
    print(f"  Spectral train records: {len(train_recs)}  eval records: {len(eval_recs)}")
    
    # -----------------------------------------------------------------------
    # 4. Predictive information analysis
    # -----------------------------------------------------------------------
    print("\n--- 4. Predictive information (c_spectral → future coord demand) ---")
    print(f"  {'h':>4}  {'AUROC':>7}  {'vs_chance':>10}  {'Brier':>7}  {'Skill':>7}  "
          f"{'Prec':>6}  {'Rec':>6}  {'F1':>6}  {'FPR':>6}")
    
    horizons = [1, 2, 3, 5, 8]
    pred_results = []
    for h in horizons:
        r = predictive_analysis_at_horizon(train_recs, eval_recs, h)
        pred_results.append(r)
        if "error" in r:
            print(f"  h={h}: {r['error']}")
            continue
        print(f"  h={h:1d}  {(r['auroc'] or 0):>7.4f}  {(r['auroc_vs_chance'] or 0):>+10.4f}  "
              f"{(r['brier'] or 0):>7.4f}  {(r['brier_skill'] or 0):>+7.4f}  "
              f"{r['precision']:>6.4f}  {r['recall']:>6.4f}  {r['f1']:>6.4f}  {r['fpr']:>6.4f}")
    
    # -----------------------------------------------------------------------
    # 5. Lead-lag cross-correlation
    # -----------------------------------------------------------------------
    print("\n--- 5. Lead-lag cross-correlation (spectral condition) ---")
    xcorr = cross_correlation_analysis(all_spec_recs)
    xcorr_data = xcorr["xcorr_by_lag"]
    print(f"  {'lag':>5}  {'xcorr':>8}  {'std':>8}  interpretation")
    for lag_str in sorted(xcorr_data.keys(), key=lambda x: int(x)):
        lag = int(lag_str)
        v = xcorr_data[lag_str]
        interp = ("c_spectral leads demand" if lag > 0 else
                  "contemporaneous" if lag == 0 else
                  f"c_spectral lags demand by {-lag}")
        print(f"  {lag:>5}  {v['mean_xcorr']:>+8.4f}  {v['std_xcorr']:>8.4f}  {interp}")
    print(f"  Peak lag: {xcorr['peak_lag']}")
    
    # -----------------------------------------------------------------------
    # 6. Event-type breakdown
    # -----------------------------------------------------------------------
    print("\n--- 6. Event-type breakdown (Type A vs B: precursor effect) ---")
    
    # Load all conditions for event analysis
    all_recs = load_per_tick(per_tick_path, conditions=["baseline", "spectral", "precursor_only"])
    conds_for_event = ["baseline", "spectral", "precursor_only"]
    et_analysis = event_type_analysis(all_recs, conds_for_event)
    
    print(f"  {'condition':>18}  {'A_ccr':>7}  {'B_ccr':>7}  {'A-B':>7}  "
          f"{'C_fp_rate':>10}  {'A_opp':>6}  {'B_opp':>6}")
    for cond in conds_for_event:
        v = et_analysis.get(cond, {})
        print(f"  {cond:>18}  {(v.get('type_a_ccr') or 0):>7.4f}  "
              f"{(v.get('type_b_ccr') or 0):>7.4f}  "
              f"{(v.get('delta_ab') or 0):>+7.4f}  "
              f"{(v.get('type_c_fp_rate') or 0):>10.4f}  "
              f"{v.get('type_a_opp',0):>6}  {v.get('type_b_opp',0):>6}")
    
    print("\n  Type A: precursor+task (best scenario for environmental sensing)")
    print("  Type B: task only (tests fallback: substrate from past feedback only)")
    print("  Type C: precursor without task (false positive risk)")
    print("  A-B gap measures: how much precursor signal helps vs no precursor")
    
    # -----------------------------------------------------------------------
    # 7. Mechanism isolation
    # -----------------------------------------------------------------------
    print("\n--- 7. Mechanism isolation ---")
    mech_comps = [
        ("precursor_only", "baseline", "Environmental sensing (precursor without feedback)"),
        ("feedback_only",  "baseline", "Feedback reinforcement (feedback without precursor)"),
        ("spectral",       "feedback_only",  "Additional value of precursor in full condition"),
        ("spectral",       "precursor_only", "Cost of feedback noise (spectral vs clean precursor)"),
    ]
    for ca, cb, label in mech_comps:
        r = compare(summaries, ca, cb)
        print(f"  {label}:")
        print(f"    {ca} vs {cb}: diff={r.get('mean_diff',0):+.4f} "
              f"p={r.get('p_ttest','n/a')} d={r.get('cohens_d','n/a')} "
              f"{'SIG' if r.get('significant') else '~'}")
    
    # -----------------------------------------------------------------------
    # Save
    # -----------------------------------------------------------------------
    output = {
        "summary_stats": {
            cond: {
                "mean": round(float(np.mean([v for v in vals if v is not None])), 6),
                "std":  round(float(np.std([v for v in vals if v is not None], ddof=1)), 6),
                "n":    len([v for v in vals if v is not None]),
            }
            for cond, vals in by_cond.items()
        },
        "comparisons": comparisons,
        "predictive_analysis": {
            "train_seeds": list(range(7000, 7020)),
            "eval_seeds":  list(range(7020, 7040)),
            "note": "threshold trained on train_seeds, evaluated on eval_seeds. No future information.",
            "horizons": pred_results,
        },
        "cross_correlation": xcorr,
        "event_type_analysis": et_analysis,
    }
    
    out_path = os.path.join(_HERE, "exp3_predictive_analysis.json")
    with open(out_path, "w") as f:
        json.dump(output, f, indent=2)
    size_kb = os.path.getsize(out_path) // 1024
    print(f"\n  Saved → {os.path.basename(out_path)}  ({size_kb}KB)")
    print("=" * 65)


if __name__ == "__main__":
    main()
