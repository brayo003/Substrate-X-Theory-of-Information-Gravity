"""Figures and report generation for the evidence benchmark (v2)."""

from __future__ import annotations

import csv
import json
import math
import os
from collections import defaultdict
from typing import Any, Dict, List, Optional, Sequence

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from .conditions import Condition, SMOKE_CONDITION, build_matrix


def plot_accuracy_over_time(time_rows: List[Dict[str, Any]], out_dir: str,
                            condition_id: str = "baseline") -> str:
    sub = [r for r in time_rows if r.get("condition_id") == condition_id
           and int(r.get("round", -2)) >= 0]
    by_model_round = defaultdict(lambda: defaultdict(list))
    for r in sub:
        by_model_round[r["model"]][int(r["round"])].append(float(r["frac_correct"]))

    fig, ax = plt.subplots(figsize=(9, 5))
    for model in ("A", "B", "C", "D", "CR", "STATIC", "MV_W", "MV_U"):
        if model not in by_model_round:
            continue
        rounds = sorted(by_model_round[model])
        means = [sum(by_model_round[model][t]) / len(by_model_round[model][t])
                 for t in rounds]
        ax.plot(rounds, means, label=model, linewidth=1.8)
    ax.set_xlabel("Communication round")
    ax.set_ylabel("Mean fraction correct")
    ax.set_title(f"Accuracy over time ({condition_id})")
    ax.legend(fontsize=8)
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
           and int(r.get("round", -2)) >= 0]
    by_model_round = defaultdict(lambda: defaultdict(list))
    for r in sub:
        by_model_round[r["model"]][int(r["round"])].append(
            float(r.get("agreement_frac") or 0.0))

    fig, ax = plt.subplots(figsize=(9, 5))
    for model in ("A", "B", "C", "D", "CR", "STATIC", "MV_W", "MV_U"):
        if model not in by_model_round:
            continue
        rounds = sorted(by_model_round[model])
        means = [sum(by_model_round[model][t]) / len(by_model_round[model][t])
                 for t in rounds]
        ax.plot(rounds, means, label=model, linewidth=1.8)
    ax.set_xlabel("Communication round")
    ax.set_ylabel("Mean agreement fraction")
    ax.set_title(f"Agreement over time ({condition_id})")
    ax.legend(fontsize=8)
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
    ni = analysis.get("noninferiority") or {}
    tost = analysis.get("tost") or {}
    delta = analysis.get("ni_margin", config.get("noninferiority_margin_frac_correct", 0.05))

    def mean_of(cid, model, metric):
        for r in summary:
            if (r["condition_id"] == cid and r["model"] == model
                    and r["metric"] == metric):
                return r["mean"], r["std"], r["n"]
        return float("nan"), float("nan"), 0

    lines = []
    lines.append("# Distributed Evidence Integration Benchmark — Experiment Report (v2)")
    lines.append("")
    lines.append("## Research question")
    lines.append("")
    lines.append(
        "Does Model D’s partition-conditioned edge-placement mechanism provide "
        "a measurable advantage (or disadvantage) for distributed evidence "
        "integration relative to creation-matched random placement (CR), "
        "models A/B/C, and conventional baselines STATIC / MV_W / MV_U?"
    )
    lines.append("")
    lines.append("## Exact methods")
    lines.append("")
    lines.append(
        "- **Stage-1 architecture:** substrate dynamics are run first; evidence "
        "propagation uses the **precomputed** graph sequence. Evidence does "
        "**not** drive edge creation. This is not evidence-driven adaptation.")
    lines.append("- Substrate: unchanged `one.py` "
                 f"(SHA-256 `{config['preserved_one_py']['sha256']}`).")
    lines.append(f"- `one.py` unchanged: **{config['one_py_unchanged']}**.")
    lines.append("- Protocol/evaluator split: network sees `NetworkEvidenceView` only; "
                 "ground truth is evaluator-only.")
    lines.append("- Models: A, B, C, D, CR; baselines STATIC (directed R0), "
                 "MV_W (bidirected R0 + weighted vote), MV_U (bidirected R0 + "
                 "unweighted majority).")
    lines.append("- Primary comparison: paired D − CR on baseline.")
    lines.append(
        f"- Pre-registered NI margin on `frac_correct`: δ = {delta} "
        "(absolute fraction of nodes).")
    lines.append(f"- Seeds: {config['n_seeds']}.")
    lines.append("- Prior v1 outputs preserved in `evidence_benchmark_results/`.")
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

    lines.append("## Main findings (baseline, primary)")
    lines.append("")
    lines.append("### Mean final fraction correct")
    lines.append("")
    lines.append("| model | mean | std | n |")
    lines.append("|---|---|---|---|")
    for m in ("A", "B", "C", "D", "CR", "STATIC", "MV_W", "MV_U"):
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
    lines.append("### Primary superiority tests (Wilcoxon + Holm)")
    lines.append("")
    lines.append("| metric | mean diff | p | Holm sig |")
    lines.append("|---|---|---|---|")
    holm_map = {h["hypothesis"]: h for h in holm}
    for r in stats:
        if r.get("scope") != "primary":
            continue
        h = holm_map.get(r["metric"], {})
        lines.append(
            f"| {r['metric']} | {_fmt(r['mean_diff'])} | {_fmt(r['p_value'], 4)} | "
            f"{h.get('significant', '')} |")
    lines.append("")
    lines.append("### Non-inferiority / equivalence on accuracy (pre-registered)")
    lines.append("")
    lines.append(
        f"- Margin δ = {delta} on mean paired `frac_correct` (D − CR).")
    lines.append(
        f"- NI test (H₀: mean ≤ −δ): p = {_fmt(ni.get('p'), 4)}; "
        f"noninferior = **{ni.get('noninferior')}**.")
    lines.append(
        f"- TOST equivalence (±δ): p_lower = {_fmt(tost.get('p_lower'), 4)}, "
        f"p_upper = {_fmt(tost.get('p_upper'), 4)}; "
        f"equivalent = **{tost.get('equivalent')}**.")
    lines.append(
        "- A CI that contains zero is **not** treated as proof of equivalence.")
    lines.append("")

    # Exploratory cross-condition
    lines.append("## Exploratory: D − CR frac_correct across conditions")
    lines.append("")
    lines.append("*Not primary confirmatory tests.*")
    lines.append("")
    lines.append("| condition | mean diff | 95% CI |")
    lines.append("|---|---|---|")
    for c in conditions:
        row = next((r for r in paired
                    if r["condition_id"] == c.condition_id
                    and r["pair"] == "D-CR" and r["metric"] == "frac_correct"), None)
        if row is None:
            continue
        lines.append(
            f"| {c.condition_id} | {_fmt(row['mean_diff'])} | "
            f"[{_fmt(row['ci95_lo'])}, {_fmt(row['ci95_hi'])}] |")
    lines.append("")

    lines.append("## Exploratory: communication cost (D − CR messages/correct)")
    lines.append("")
    lines.append("| condition | mean diff | 95% CI |")
    lines.append("|---|---|---|")
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
    lines.append("")

    # Correlation diagnostics
    corr_diag = config.get("correlation_diagnostics") or {}
    if corr_diag:
        lines.append("## Evidence correlation diagnostics")
        lines.append("")
        lines.append("| condition | setting | empirical mean pairwise bit corr |")
        lines.append("|---|---|---|")
        for cid, d in corr_diag.items():
            lines.append(
                f"| {cid} | {d.get('correlation_setting')} | "
                f"{_fmt(d.get('empirical_mean_pairwise_bit_corr'))} |")
        lines.append("")
        lines.append(
            "The decision rule remains a naive weighted/unweighted vote that "
            "treats items as independent; correlated conditions probe "
            "robustness to that misspecification.")
        lines.append("")

    # Primary question table
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
    holm_sig = {h["hypothesis"]: bool(h.get("significant")) for h in holm}

    acc_sup = bool(holm_sig.get("frac_correct"))
    cost_sup = bool(holm_sig.get("messages_per_correct_node")
                    and base_msg and base_msg.get("ci95_hi", 1) < 0)
    speed_sup = bool(holm_sig.get("time_to_correct_agreement")
                     and base_agr and base_agr.get("mean_diff", 0) < 0)
    cov_sup = bool(holm_sig.get("evidence_coverage"))
    ni_ok = bool(ni.get("noninferior"))
    eq_ok = bool(tost.get("equivalent"))

    lines.append("## Hypothesis assessment (demonstrated vs not demonstrated)")
    lines.append("")
    lines.append("| Question | Assessment |")
    lines.append("|---|---|")
    lines.append(
        "| Better decision accuracy (D vs CR)? | "
        + ("**Demonstrated superiority** (Holm)." if acc_sup else
           ("**Non-inferior at δ** (not superior)." if ni_ok else
            "**Not demonstrated** (neither superiority nor NI at δ)."))
        + " |")
    lines.append(
        "| Equivalence of accuracy at ±δ? | "
        + ("**Yes (TOST).**" if eq_ok else "**Not established.**")
        + " |")
    lines.append(
        "| Faster correct agreement? | "
        + ("**Supported (primary Holm).**" if speed_sup else
           "**Not demonstrated** on primary test.")
        + " |")
    lines.append(
        "| Lower communication cost? | "
        + ("**Supported (primary Holm; lower messages/correct).**" if cost_sup else
           "**Not demonstrated** on primary Holm test "
           "(exploratory condition tables are separate).")
        + " |")
    lines.append(
        "| Better evidence coverage? | "
        + ("**Supported (primary Holm).**" if cov_sup else
           "**Not demonstrated** on primary test.")
        + " |")
    fail_txt = "**Not demonstrated** (exploratory failures contrast)."
    if base_fail and base_fail.get("ci95_lo", -1) > 0:
        fail_txt = "Exploratory CI above 0; not a primary confirmatory claim."
    lines.append(f"| Greater resilience to failures? | {fail_txt} |")
    lines.append("")

    if acc_sup:
        verdict_key = "supports_accuracy"
        verdict_label = "supports accuracy advantage"
    elif ni_ok and cost_sup:
        verdict_key = "ni_accuracy_supports_cost"
        verdict_label = "non-inferior on accuracy; supports lower communication cost"
    elif ni_ok:
        verdict_key = "noninferior_accuracy_no_superiority"
        verdict_label = "non-inferior on accuracy; no demonstrated superiority"
    elif cost_sup:
        verdict_key = "mixed_cost_only"
        verdict_label = "no accuracy superiority/NI; communication-cost signal on primary test"
    else:
        verdict_key = "inconclusive"
        verdict_label = "inconclusive / not demonstrated on primary endpoints"

    lines.append(f"**Verdict: {verdict_label}.**")
    lines.append("")
    lines.append("### Separated claims")
    lines.append("")
    lines.append("**Demonstrated (primary analysis):** see table above.")
    lines.append("")
    lines.append(
        "**Hypotheses / exploratory only:** mechanism stories about localized "
        "vs diffuse edge placement; condition-level patterns outside baseline "
        "primary tests; any reading of CI∋0 as “equal performance.”")
    lines.append("")
    lines.append("## Limitations")
    lines.append("")
    lines.append("- Stage-1 only: precomputed graphs, not online evidence-driven rewiring.")
    lines.append("- Communication uses stored-graph edges, not gate-only routing.")
    lines.append("- Naive vote ignores dependence under correlated evidence.")
    lines.append("- Stream distinctness ≠ independence.")
    lines.append("- No claim of intelligence, novelty, or practical AI usefulness.")
    lines.append("")
    lines.append("## Reproducibility")
    lines.append("")
    lines.append("```bash")
    lines.append("python3 -m evidence_benchmark --test")
    lines.append("python3 -m evidence_benchmark --full --seeds 100")
    lines.append("```")
    lines.append("")
    lines.append(f"- Output: `{out_dir}`")
    lines.append(f"- Audit: `evidence_benchmark/AUDIT_REPORT.md`")
    lines.append(f"- Infeasible CR: {config.get('infeasible_controls')}")
    lines.append(f"- D/CR match failures: {config.get('d_cr_match_failures')}")
    lines.append("")

    path = os.path.join(out_dir, "experiment_report.md")
    with open(path, "w") as f:
        f.write("\n".join(lines) + "\n")
    with open(os.path.join(out_dir, "verdict.json"), "w") as f:
        json.dump(dict(
            verdict=verdict_key,
            label=verdict_label,
            accuracy_superiority=acc_sup,
            accuracy_noninferior=ni_ok,
            accuracy_equivalent_tost=eq_ok,
            communication_cost_primary=cost_sup,
            agreement_speed_primary=speed_sup,
            coverage_primary=cov_sup,
            ni_margin=delta,
            ni=ni,
            tost=tost,
        ), f, indent=2, default=str)
    return path


def regenerate_report_from_csvs(out_dir: str) -> str:
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
                if v in ("", "None"):
                    r[k] = None
                    continue
                if v == "nan":
                    r[k] = float("nan")
                    continue
                try:
                    if "." in v or "e" in v.lower():
                        r[k] = float(v)
                    else:
                        r[k] = int(v)
                except (TypeError, ValueError):
                    if isinstance(v, str) and v.lower() == "true":
                        r[k] = True
                    elif isinstance(v, str) and v.lower() == "false":
                        r[k] = False
        return rows

    summary = load_csv("summary.csv")
    paired = load_csv("paired_differences.csv")
    stats = load_csv("statistical_tests.csv")
    with open(os.path.join(out_dir, "holm_bonferroni.json")) as f:
        holm = json.load(f)
    ni_path = os.path.join(out_dir, "noninferiority_tost.json")
    if os.path.isfile(ni_path):
        with open(ni_path) as f:
            ni_blob = json.load(f)
        ni, tost = ni_blob.get("noninferiority"), ni_blob.get("tost")
        margin = ni_blob.get("margin", 0.05)
    else:
        ni, tost, margin = {}, {}, 0.05

    cond_ids = {c["condition_id"] for c in config.get("conditions", [])}
    if cond_ids == {SMOKE_CONDITION.condition_id}:
        conditions: Sequence[Condition] = [SMOKE_CONDITION]
    else:
        conditions = [c for c in build_matrix() if c.condition_id in cond_ids] or build_matrix()

    analysis = dict(summary=summary, paired=paired, stats=stats, holm=holm,
                    noninferiority=ni, tost=tost, ni_margin=margin)
    return write_experiment_report(out_dir, config, analysis, test_results, conditions)
