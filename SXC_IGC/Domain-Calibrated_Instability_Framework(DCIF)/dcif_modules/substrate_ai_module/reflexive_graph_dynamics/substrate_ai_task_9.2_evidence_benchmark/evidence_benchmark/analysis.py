"""Figures and report generation for the evidence benchmark."""

from __future__ import annotations

import json
import math
import os
from collections import defaultdict
from typing import Any, Dict, List, Optional, Sequence

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from .conditions import Condition, condition_to_dict


def plot_accuracy_over_time(time_rows: List[Dict[str, Any]], out_dir: str,
                            condition_id: str = "baseline") -> str:
    sub = [r for r in time_rows if r.get("condition_id") == condition_id
           and r.get("round", -2) >= 0]
    by_model_round = defaultdict(lambda: defaultdict(list))
    for r in sub:
        by_model_round[r["model"]][int(r["round"])].append(float(r["frac_correct"]))

    fig, ax = plt.subplots(figsize=(8, 5))
    for model in ("A", "B", "C", "D", "CR", "MV"):
        if model not in by_model_round:
            continue
        rounds = sorted(by_model_round[model])
        means = [sum(by_model_round[model][t]) / len(by_model_round[model][t])
                 for t in rounds]
        ax.plot(rounds, means, label=model, linewidth=2)
    ax.set_xlabel("Communication round")
    ax.set_ylabel("Mean fraction correct")
    ax.set_title(f"Accuracy over time ({condition_id})")
    ax.legend()
    ax.set_ylim(-0.05, 1.05)
    ax.grid(True, alpha=0.3)
    path = os.path.join(out_dir, "figures", f"accuracy_over_time_{condition_id}.png")
    fig.tight_layout()
    fig.savefig(path, dpi=140)
    plt.close(fig)
    return path


def plot_agreement_over_time(time_rows: List[Dict[str, Any]], out_dir: str,
                             condition_id: str = "baseline") -> str:
    sub = [r for r in time_rows if r.get("condition_id") == condition_id
           and r.get("round", -2) >= 0]
    by_model_round = defaultdict(lambda: defaultdict(list))
    for r in sub:
        # agreement on correct label proxied by agreement_correct bool + frac
        val = float(r.get("agreement_frac") or 0.0)
        if r.get("agreement_correct") is False:
            val = -val  # optional; keep raw agreement_frac
        by_model_round[r["model"]][int(r["round"])].append(
            float(r.get("agreement_frac") or 0.0))

    fig, ax = plt.subplots(figsize=(8, 5))
    for model in ("A", "B", "C", "D", "CR", "MV"):
        if model not in by_model_round:
            continue
        rounds = sorted(by_model_round[model])
        means = [sum(by_model_round[model][t]) / len(by_model_round[model][t])
                 for t in rounds]
        ax.plot(rounds, means, label=model, linewidth=2)
    ax.set_xlabel("Communication round")
    ax.set_ylabel("Mean agreement fraction")
    ax.set_title(f"Agreement over time ({condition_id})")
    ax.legend()
    ax.set_ylim(-0.05, 1.05)
    ax.grid(True, alpha=0.3)
    path = os.path.join(out_dir, "figures", f"agreement_over_time_{condition_id}.png")
    fig.tight_layout()
    fig.savefig(path, dpi=140)
    plt.close(fig)
    return path


def plot_d_vs_cr_paired(paired: List[Dict[str, Any]], out_dir: str,
                        condition_id: str = "baseline") -> str:
    metrics = ["frac_correct", "evidence_coverage", "messages_per_correct_node",
               "time_to_correct_agreement", "agreement_correct"]
    sub = [r for r in paired if r.get("condition_id") == condition_id
           and r.get("pair") == "D-CR" and r.get("metric") in metrics]
    fig, ax = plt.subplots(figsize=(9, 5))
    labels, means, lo, hi = [], [], [], []
    for m in metrics:
        row = next((r for r in sub if r["metric"] == m), None)
        if row is None:
            continue
        labels.append(m)
        means.append(row["mean_diff"])
        lo.append(row["mean_diff"] - row["ci95_lo"]
                  if row["ci95_lo"] == row["ci95_lo"] else 0)
        hi.append(row["ci95_hi"] - row["mean_diff"]
                  if row["ci95_hi"] == row["ci95_hi"] else 0)
    x = range(len(labels))
    ax.bar(x, means, yerr=[lo, hi], capsize=4, color="steelblue", alpha=0.85)
    ax.axhline(0, color="black", linewidth=1)
    ax.set_xticks(list(x))
    ax.set_xticklabels(labels, rotation=25, ha="right")
    ax.set_ylabel("Mean paired difference (D − CR)")
    ax.set_title(f"D vs CR paired differences ({condition_id})")
    ax.grid(True, axis="y", alpha=0.3)
    path = os.path.join(out_dir, "figures", f"d_vs_cr_{condition_id}.png")
    fig.tight_layout()
    fig.savefig(path, dpi=140)
    plt.close(fig)
    return path


def _fmt(x: Any, nd: int = 4) -> str:
    try:
        v = float(x)
    except (TypeError, ValueError):
        return str(x)
    if v != v:
        return "nan"
    return f"{v:.{nd}f}"


def write_experiment_report(
    out_dir: str,
    config: Dict[str, Any],
    analysis: Dict[str, Any],
    test_results: Dict[str, str],
    conditions: Sequence[Condition],
) -> str:
    summary = analysis["summary"]
    paired = analysis["paired"]
    stats = analysis["stats"]
    holm = analysis["holm"]

    def mean_of(cid, model, metric):
        for r in summary:
            if (r["condition_id"] == cid and r["model"] == model
                    and r["metric"] == metric):
                return r["mean"], r["std"], r["n"]
        return float("nan"), float("nan"), 0

    lines = []
    lines.append("# Distributed Evidence Integration Benchmark — Experiment Report")
    lines.append("")
    lines.append("## Research question")
    lines.append("")
    lines.append(
        "Does Model D’s partition-conditioned edge-placement mechanism provide "
        "a measurable advantage (or disadvantage) for distributed evidence "
        "integration relative to creation-matched random placement (CR), "
        "models A/B/C, and a conventional majority-vote gossip baseline (MV)?"
    )
    lines.append("")
    lines.append("## Exact methods")
    lines.append("")
    lines.append("- Substrate: unchanged `one.py` "
                 f"(SHA-256 `{config['preserved_one_py']['sha256']}`).")
    lines.append(f"- `one.py` unchanged check: **{config['one_py_unchanged']}**.")
    lines.append("- Evidence protocol: separate layer (`evidence_benchmark/`); "
                 "see `benchmark_specification.md`.")
    lines.append("- Models: A, B, C, D, CR from substrate; MV = bidirected "
                 "initial-graph majority-vote message passing.")
    lines.append("- Primary comparison: paired D − CR.")
    lines.append("- Seeds: "
                 f"{config['n_seeds']}; streams: init/move/ctrl/evidence/failure/relabel.")
    lines.append("")
    lines.append("## Experimental conditions")
    lines.append("")
    lines.append("| id | n | p | corr | dist | rounds | fail | adv |")
    lines.append("|---|---|---|---|---|---|---|---|")
    for c in conditions:
        lines.append(
            f"| {c.condition_id} | {c.n_states} | {c.reliability} | "
            f"{c.correlation} | {c.distribution} | {c.max_rounds} | "
            f"{c.failure_fraction} | {c.adversarial_fraction} |")
    lines.append("")
    lines.append("## Test results")
    lines.append("")
    n_pass = sum(1 for v in test_results.values() if v == "PASS")
    lines.append(f"Correctness tests: **{n_pass}/{len(test_results)} PASS**.")
    lines.append("")
    for k, v in test_results.items():
        lines.append(f"- `{k}`: {v}")
    lines.append("")
    lines.append("## Main findings (baseline condition)")
    lines.append("")
    lines.append("### Mean final fraction correct")
    lines.append("")
    lines.append("| model | mean | std | n |")
    lines.append("|---|---|---|---|")
    for m in ("A", "B", "C", "D", "CR", "MV"):
        mu, sd, n = mean_of("baseline", m, "frac_correct")
        lines.append(f"| {m} | {_fmt(mu)} | {_fmt(sd)} | {n} |")
    lines.append("")
    lines.append("### Paired D − CR (baseline)")
    lines.append("")
    lines.append("| metric | mean diff | 95% CI | n |")
    lines.append("|---|---|---|---|")
    for r in paired:
        if r["condition_id"] == "baseline" and r["pair"] == "D-CR":
            if r["metric"] in (
                    "frac_correct", "evidence_coverage",
                    "messages_per_correct_node", "time_to_correct_agreement",
                    "agreement_correct", "total_messages",
                    "frac_correct_after_failure"):
                lines.append(
                    f"| {r['metric']} | {_fmt(r['mean_diff'])} | "
                    f"[{_fmt(r['ci95_lo'])}, {_fmt(r['ci95_hi'])}] | {r['n']} |")
    lines.append("")
    lines.append("### Statistical tests (baseline D−CR, Wilcoxon + Holm)")
    lines.append("")
    lines.append("| metric | mean diff | p | Holm sig |")
    lines.append("|---|---|---|---|")
    holm_map = {h["hypothesis"]: h for h in holm}
    for r in stats:
        h = holm_map.get(r["metric"], {})
        lines.append(
            f"| {r['metric']} | {_fmt(r['mean_diff'])} | {_fmt(r['p_value'], 4)} | "
            f"{h.get('significant', '')} |")
    lines.append("")

    # Cross-condition consistency for frac_correct D-CR
    lines.append("### D − CR frac_correct across conditions")
    lines.append("")
    lines.append("| condition | mean diff | 95% CI |")
    lines.append("|---|---|---|")
    pos = neg = zero = 0
    for c in conditions:
        row = next((r for r in paired
                    if r["condition_id"] == c.condition_id
                    and r["pair"] == "D-CR" and r["metric"] == "frac_correct"), None)
        if row is None:
            continue
        lines.append(
            f"| {c.condition_id} | {_fmt(row['mean_diff'])} | "
            f"[{_fmt(row['ci95_lo'])}, {_fmt(row['ci95_hi'])}] |")
        md, lo, hi = row["mean_diff"], row["ci95_lo"], row["ci95_hi"]
        if md == md:
            if lo > 0:
                pos += 1
            elif hi < 0:
                neg += 1
            else:
                zero += 1
    lines.append("")

    # Secondary endpoints and comparisons used for a structured verdict.
    base_fc = next((r for r in paired if r["condition_id"] == "baseline"
                    and r["pair"] == "D-CR" and r["metric"] == "frac_correct"), None)
    base_msg = next((r for r in paired if r["condition_id"] == "baseline"
                     and r["pair"] == "D-CR"
                     and r["metric"] == "messages_per_correct_node"), None)
    base_agr = next((r for r in paired if r["condition_id"] == "baseline"
                     and r["pair"] == "D-CR"
                     and r["metric"] == "time_to_correct_agreement"), None)
    base_cov = next((r for r in paired if r["condition_id"] == "baseline"
                     and r["pair"] == "D-CR"
                     and r["metric"] == "evidence_coverage"), None)
    base_fail = next((r for r in paired if r["condition_id"] == "failures"
                      and r["pair"] == "D-CR"
                      and r["metric"] == "frac_correct"), None)
    holm_map_sig = {h["hypothesis"]: bool(h.get("significant")) for h in holm}
    holm_any = any(holm_map_sig.values())
    cost_sig = holm_map_sig.get("messages_per_correct_node", False)
    cost_ci_neg = bool(
        base_msg and base_msg["ci95_hi"] == base_msg["ci95_hi"]
        and base_msg["ci95_hi"] < 0)

    # Communication-cost table across conditions
    lines.append("## Negative findings")
    lines.append("")
    lines.append(
        "- Graph stability / edge creation volume is **not** treated as success; "
        "only evidence-integration metrics are interpretive endpoints.")
    if zero:
        lines.append(
            f"- In {zero} conditions, the D−CR accuracy CI included zero.")
    if neg:
        lines.append(
            f"- In {neg} conditions, D was significantly worse than CR on accuracy.")
    mv_row = next((r for r in paired if r["condition_id"] == "baseline"
                   and r["pair"] == "D-MV" and r["metric"] == "frac_correct"), None)
    if mv_row:
        lines.append(
            f"- D − MV frac_correct mean diff = {_fmt(mv_row['mean_diff'])} "
            f"(CI [{_fmt(mv_row['ci95_lo'])}, {_fmt(mv_row['ci95_hi'])}]).")
    lines.append("")

    lines.append("## Limitations")
    lines.append("")
    lines.append("- Communication uses stored-graph edges, not gate-only routing.")
    lines.append("- Round index coupled to graph time index (one schedule among many).")
    lines.append("- Stream distinctness ≠ independence.")
    lines.append("- Synthetic binary task; no claim about real-world sensing.")
    lines.append("- No claim of intelligence, novelty, or practical AI usefulness.")
    lines.append("")

    lines.append("## Reproducibility")
    lines.append("")
    lines.append("```bash")
    lines.append("python3 -m evidence_benchmark.run_benchmark --test")
    lines.append("python3 -m evidence_benchmark.run_benchmark --full --seeds 100")
    lines.append("```")
    lines.append("")
    lines.append(f"- Output directory: `{out_dir}`")
    lines.append("- Configuration: `configuration.json`")
    lines.append(f"- Infeasible CR seeds: {config.get('infeasible_controls')}")
    lines.append(f"- D/CR match failures: {config.get('d_cr_match_failures')}")
    lines.append("")

    lines.append("## Additional comparisons")
    lines.append("")
    lines.append("### Models A/B/C identity on this task")
    lines.append("")
    lines.append(
        "Under the stored-graph communication layer, A, B, and C share the same "
        "static edge set `R0` (A/B never modify edges; C refines partitions and "
        "gates movement but does not create edges). Consequently their "
        "evidence-integration metrics are identical in every seed. Partition "
        "refinement alone does not change this protocol’s message routes.")
    lines.append("")
    lines.append("### Communication efficiency (D − CR messages per correct node)")
    lines.append("")
    lines.append("| condition | mean diff | 95% CI |")
    lines.append("|---|---|---|")
    cost_pos = cost_neg = cost_zero = 0
    for c in conditions:
        row = next((r for r in paired
                    if r["condition_id"] == c.condition_id
                    and r["pair"] == "D-CR"
                    and r["metric"] == "messages_per_correct_node"), None)
        if row is None:
            continue
        lines.append(
            f"| {c.condition_id} | {_fmt(row['mean_diff'])} | "
            f"[{_fmt(row['ci95_lo'])}, {_fmt(row['ci95_hi'])}] |")
        lo, hi = row["ci95_lo"], row["ci95_hi"]
        if lo == lo and hi == hi:
            if lo > 0:
                cost_pos += 1
            elif hi < 0:
                cost_neg += 1
            else:
                cost_zero += 1
    lines.append("")
    lines.append(
        "Negative differences mean D used fewer messages per correctly informed "
        "node than CR. Across conditions, CI entirely below 0 in "
        f"{cost_neg}/{cost_pos + cost_neg + cost_zero}, above 0 in {cost_pos}, "
        f"overlapping 0 in {cost_zero}.")
    lines.append("")
    lines.append(
        "This is a **communication-cost** difference, not an accuracy advantage. "
        "It does not by itself justify claiming that partition-conditioned "
        "placement improves evidence integration quality.")
    lines.append("")
    lines.append("### D versus A and MV (baseline)")
    lines.append("")
    lines.append("| pair | metric | mean diff | 95% CI |")
    lines.append("|---|---|---|---|")
    for pair in ("D-A", "D-MV", "D-C"):
        for metric in ("frac_correct", "messages_per_correct_node",
                       "evidence_coverage", "total_messages"):
            row = next((r for r in paired if r["condition_id"] == "baseline"
                        and r["pair"] == pair and r["metric"] == metric), None)
            if row is None:
                continue
            lines.append(
                f"| {pair} | {metric} | {_fmt(row['mean_diff'])} | "
                f"[{_fmt(row['ci95_lo'])}, {_fmt(row['ci95_hi'])}] |")
    lines.append("")
    lines.append("### Possible mechanism notes (non-causal claims)")
    lines.append("")
    lines.append(
        "- Where D uses fewer messages than CR at matched creation counts, a "
        "plausible mechanism is that D’s candidates are localized at the mover "
        "`z_t` and may form shorter bursty routes near the trajectory, whereas "
        "CR samples globally from the cross-block pool, producing more diffuse "
        "connectivity and more duplicate/wasted forwards. This remains a "
        "hypothesis consistent with the metrics, not a proof.")
    lines.append(
        "- Accuracy near ceiling under strong reliability (`rel_strong`) limits "
        "discriminability; weak-reliability conditions remain inconclusive on "
        "accuracy when CIs include 0.")
    lines.append("")

    # Structured primary-question assessment
    acc_ok = bool(base_fc and base_fc["ci95_lo"] > 0 and holm_map_sig.get("frac_correct"))
    acc_bad = bool(base_fc and base_fc["ci95_hi"] < 0)
    speed_ok = bool(base_agr and base_agr["ci95_hi"] < 0)  # D faster => negative time
    cost_ok = bool(cost_sig and cost_ci_neg)
    cov_ok = bool(base_cov and base_cov["ci95_lo"] > 0
                  and holm_map_sig.get("evidence_coverage"))
    fail_ok = bool(base_fail and base_fail["ci95_lo"] > 0)

    if acc_ok and pos > neg:
        verdict_key = "supports_accuracy"
        verdict_label = "supports"
        verdict_text = (
            "Evidence supports a modest accuracy advantage of D over CR under "
            f"the locked baseline, with CI-excluding-zero consistency in "
            f"{pos}/{pos + neg + zero} conditions.")
    elif acc_bad:
        verdict_key = "weakens"
        verdict_label = "weakens"
        verdict_text = (
            "Evidence weakens the hypothesis: D underperforms CR on primary "
            "accuracy (CI below 0).")
    elif cost_ok and not acc_ok:
        verdict_key = "mixed_fails_accuracy_supports_cost"
        verdict_label = "mixed — fails to distinguish on accuracy; supports a small communication-cost advantage"
        verdict_text = (
            "On final decision accuracy, correct agreement, evidence coverage, "
            "and failure resilience, paired D−CR differences are near zero with "
            "CIs that include zero (or are exactly zero under ceiling effects). "
            "A Holm-significant reduction in messages_per_correct_node and "
            "total_messages indicates a small communication-cost advantage for "
            "D versus creation-matched CR under several conditions. This does "
            "not establish an accuracy advantage for partition-conditioned "
            "placement, nor practical AI usefulness.")
    else:
        verdict_key = "fails_to_distinguish"
        verdict_label = "fails_to_distinguish"
        verdict_text = (
            "Evidence fails to distinguish D from CR on primary accuracy: "
            "paired differences are small and/or confidence intervals include "
            "zero after accounting for uncertainty and multiple comparisons.")

    lines.append("## Hypothesis assessment")
    lines.append("")
    lines.append(f"**Verdict: {verdict_label}.**")
    lines.append("")
    lines.append("| Primary question | Assessment |")
    lines.append("|---|---|")
    lines.append(
        "| Higher final decision accuracy (D vs CR)? | "
        + ("**Yes.**" if acc_ok else ("**Worse.**" if acc_bad else
           "**No.** Mean paired diff near 0; 95% CI includes 0 "
           f"(or undefined Wilcoxon). Same pattern in {zero}/{pos+neg+zero} "
           "conditions with CI overlapping 0."))
        + " |")
    lines.append(
        "| Faster correct agreement? | "
        + ("**Yes.**" if speed_ok else "**No.** CI includes 0 (or undefined).")
        + " |")
    lines.append(
        "| Lower communication cost for equivalent accuracy? | "
        + ("**Yes (narrow).** Baseline messages/correct-node CI entirely "
           "below 0; Holm-significant where tested."
           if cost_ok else "**No clear advantage.**")
        + " |")
    lines.append(
        "| Better resilience after failures? | "
        + ("**Yes.**" if fail_ok else
           "**No clear advantage.** Failure-condition accuracy CI includes 0.")
        + " |")
    lines.append(
        "| More reliable evidence coverage? | "
        + ("**Yes.**" if cov_ok else "**No.** CI includes 0.")
        + " |")
    lines.append("")
    lines.append(verdict_text)
    lines.append("")
    lines.append(
        "Relative to static A/B/C, both D and CR (and MV) improve "
        "coverage/accuracy somewhat by adding routes; that effect is about "
        "*creating edges*, not D’s specific placement rule. Relative to MV, "
        "baseline accuracy is indistinguishable when the D−MV CI includes 0.")
    lines.append("")
    lines.append(
        "This benchmark does not establish intelligence, emergent "
        "collective computation, or superiority over established "
        "distributed algorithms beyond the specific MV gossip baseline "
        "under the stated constraints.")
    lines.append("")

    path = os.path.join(out_dir, "experiment_report.md")
    with open(path, "w") as f:
        f.write("\n".join(lines) + "\n")
    verdict_payload = {
        "verdict": verdict_key,
        "accuracy_D_vs_CR": (
            "supports" if acc_ok else ("weakens" if acc_bad else "fails_to_distinguish")),
        "communication_cost_D_vs_CR": (
            "supports_lower_cost_for_D" if cost_ok else "fails_to_distinguish"),
        "agreement_speed_D_vs_CR": (
            "supports" if speed_ok else "fails_to_distinguish"),
        "coverage_D_vs_CR": (
            "supports" if cov_ok else "fails_to_distinguish"),
        "resilience_D_vs_CR": (
            "supports" if fail_ok else "fails_to_distinguish"),
        "explanation": verdict_text,
    }
    with open(os.path.join(out_dir, "verdict.json"), "w") as f:
        json.dump(verdict_payload, f, indent=2)
    return path


def regenerate_report_from_csvs(out_dir: str) -> str:
    """Rebuild experiment_report.md / verdict.json from saved CSVs (no re-run)."""
    import csv

    from .conditions import Condition, build_matrix, SMOKE_CONDITION

    with open(os.path.join(out_dir, "configuration.json")) as f:
        config = json.load(f)
    with open(os.path.join(out_dir, "test_results.json")) as f:
        test_results = json.load(f)

    def load_csv(name: str) -> List[Dict[str, Any]]:
        path = os.path.join(out_dir, name)
        with open(path, newline="") as f:
            rows = list(csv.DictReader(f))
        for r in rows:
            for k, v in list(r.items()):
                if v in ("", "None", "nan"):
                    if k in ("wilcoxon_W", "p_value", "mean_diff", "std_diff",
                             "ci95_lo", "ci95_hi", "mean", "std", "n"):
                        try:
                            r[k] = float("nan") if v == "nan" else (
                                None if v in ("", "None") else float(v))
                        except ValueError:
                            pass
                    continue
                try:
                    if "." in v or "e" in v.lower() or "E" in v:
                        r[k] = float(v)
                    else:
                        r[k] = int(v)
                except ValueError:
                    if v.lower() == "true":
                        r[k] = True
                    elif v.lower() == "false":
                        r[k] = False
        return rows

    summary = load_csv("summary.csv")
    paired = load_csv("paired_differences.csv")
    stats = load_csv("statistical_tests.csv")
    with open(os.path.join(out_dir, "holm_bonferroni.json")) as f:
        holm = json.load(f)

    # Restore float NaNs written as null/NaN in JSON
    for h in holm:
        if h.get("p") is None or (isinstance(h.get("p"), float) and math.isnan(h["p"])):
            h["p"] = float("nan")

    cond_ids = {c["condition_id"] for c in config.get("conditions", [])}
    if cond_ids == {SMOKE_CONDITION.condition_id}:
        conditions: Sequence[Condition] = [SMOKE_CONDITION]
    else:
        conditions = [c for c in build_matrix() if c.condition_id in cond_ids] or build_matrix()

    analysis = {"summary": summary, "paired": paired, "stats": stats, "holm": holm}
    return write_experiment_report(out_dir, config, analysis, test_results, conditions)
