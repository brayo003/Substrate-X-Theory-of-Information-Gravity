"""Run the distributed evidence integration experiment matrix (v2)."""

from __future__ import annotations

import csv
import hashlib
import json
import os
import sys
import time
from typing import Any, Dict, List, Optional, Sequence

from .conditions import (
    BASELINE,
    D_CR_PRIMARY,
    MODELS,
    NONINFERIORITY_MARGIN_FRAC_CORRECT,
    Condition,
    SMOKE_CONDITION,
    build_matrix,
    condition_to_dict,
)
from .evidence import empirical_pairwise_bit_correlation, generate_evidence
from .evaluator import evaluate_protocol
from .failures import schedule_edge_failures
from .graph_bridge import (
    make_mv_u_timeline,
    make_mv_w_timeline,
    make_static_directed_timeline,
    run_all_models,
    verify_d_cr_creation_match,
)
from .metrics import (
    extract_seed_metrics,
    holm_bonferroni,
    mean_std,
    noninferiority_test,
    paired_diffs,
    tost_equivalence,
    wilcoxon_signed_rank,
)
from .protocol import run_protocol
from .streams import evidence_stream_seed, failure_stream_seed, relabel_stream_seed

_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)
import one as substrate  # noqa: E402

DEFAULT_OUT = os.path.join(_ROOT, "evidence_benchmark_results_v2")
BENCHMARK_ID = "evidence_integration_v2"


def _source_hashes() -> Dict[str, Any]:
    path = os.path.join(_ROOT, "one.py")
    data = open(path, "rb").read()
    return dict(
        path=path,
        bytes=len(data),
        md5=hashlib.md5(data).hexdigest(),
        sha256=hashlib.sha256(data).hexdigest(),
    )


def _write_csv(path: str, rows: List[Dict[str, Any]]) -> None:
    if not rows:
        open(path, "w").write("")
        return
    keys = list(rows[0].keys())
    with open(path, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=keys)
        w.writeheader()
        for r in rows:
            w.writerow(r)


def _run_one_seed(cond: Condition, seed: int) -> Dict[str, Any]:
    """Run substrate models + conventional baselines for one paired seed."""
    models = run_all_models(
        seed=seed,
        n_states=cond.n_states,
        edge_prob=cond.edge_prob,
        n_initial_blocks=cond.initial_blocks,
        steps=cond.graph_steps,
        cap_per_source=None,
        removal_age=cond.removal_age,
    )
    R0 = models["_R0"]
    nodes = sorted(R0.states())
    bundle = generate_evidence(
        seed=seed,
        nodes=nodes,
        reliability=cond.reliability,
        correlation=cond.correlation,
        distribution=cond.distribution,
        adversarial_fraction=cond.adversarial_fraction,
    )
    net_view = bundle.network_view()

    fail_map = {}
    if cond.failure_fraction > 0:
        fail_round = max(0, cond.max_rounds // 2)
        fail_map = schedule_edge_failures(
            seed=seed,
            graph_edges=list(R0.edges()),
            r0_edges=set(R0.edges()),
            fail_round=fail_round,
            fraction=cond.failure_fraction,
        )

    models["STATIC"] = make_static_directed_timeline(R0, cond.graph_steps, seed)
    models["MV_W"] = make_mv_w_timeline(R0, cond.graph_steps, seed)
    models["MV_U"] = make_mv_u_timeline(R0, cond.graph_steps, seed)

    per_model_rows = []
    time_rows = []
    infeasible = False
    d_cr_match = None

    for name in MODELS:
        tl = models[name]
        if name == "CR" and tl.control_infeasible:
            infeasible = True
            per_model_rows.append(dict(
                condition_id=cond.condition_id, model="CR", seed=seed,
                control_infeasible=1, infeasible_reason=tl.infeasible_reason,
                frac_correct=float("nan"),
            ))
            continue

        created_all = set()
        for s in tl.created_edges:
            created_all |= s

        rule = "unweighted" if name == "MV_U" else "weighted"
        result = run_protocol(
            nodes=nodes,
            network_view=net_view,
            graph_sequence=tl.graphs,
            max_rounds=cond.max_rounds,
            send_cap=cond.send_cap,
            max_messages=cond.max_messages,
            failure_edges_by_round=fail_map if fail_map else None,
            decision_rule=rule,
        )
        ev = evaluate_protocol(result, bundle.ground_truth, bundle)
        row = extract_seed_metrics(
            model=name, seed=seed, condition_id=cond.condition_id,
            result=result, eval_out=ev, timeline=tl, created_all=created_all,
        )
        if fail_map:
            fr = min(fail_map.keys())
            post = [re for re in ev["round_evals"] if re["round_idx"] >= fr]
            if post:
                row["frac_correct_after_failure"] = post[-1]["frac_correct"]
                row["recovery_rounds"] = next(
                    (re["round_idx"] - fr for re in post
                     if re.get("collective_correct") is True), -1)
            else:
                row["frac_correct_after_failure"] = row["frac_correct"]
                row["recovery_rounds"] = -1
        else:
            row["frac_correct_after_failure"] = row["frac_correct"]
            row["recovery_rounds"] = -1
        per_model_rows.append(row)

        for re in ev["round_evals"]:
            if re["round_idx"] < 0:
                continue
            time_rows.append(dict(
                condition_id=cond.condition_id, model=name, seed=seed,
                round=re["round_idx"],
                frac_correct=re["frac_correct"],
                frac_incorrect=re["frac_incorrect"],
                frac_undecided=re["frac_undecided"],
                agreement_frac=re["agreement_frac"],
                agreement_correct=re["agreement_correct"],
                collective_correct=re["collective_correct"],
            ))

    if not infeasible and "D" in models and "CR" in models:
        d_cr_match = verify_d_cr_creation_match(models["D"], models["CR"])

    return dict(
        rows=per_model_rows,
        time_rows=time_rows,
        infeasible=infeasible,
        d_cr_match=d_cr_match,
        bundle=bundle,
        ground_truth=bundle.ground_truth,
    )


def run_condition(cond: Condition, seeds: Sequence[int],
                  out_dir: str, quiet: bool = False) -> Dict[str, Any]:
    rows, time_rows = [], []
    bundles_for_corr = []
    n_infeasible = 0
    match_failures = 0
    t0 = time.time()
    for i, seed in enumerate(seeds):
        res = _run_one_seed(cond, seed)
        rows.extend(res["rows"])
        time_rows.extend(res["time_rows"])
        bundles_for_corr.append(res["bundle"])
        if res["infeasible"]:
            n_infeasible += 1
        if res["d_cr_match"] is False:
            match_failures += 1
        if not quiet and (i + 1) % 10 == 0:
            print(f"  [{cond.condition_id}] seed {i+1}/{len(seeds)} "
                  f"({time.time()-t0:.1f}s)", flush=True)
    return dict(
        rows=rows, time_rows=time_rows,
        n_infeasible=n_infeasible, match_failures=match_failures,
        bundles=bundles_for_corr,
    )


def analyze(rows: List[Dict[str, Any]], conditions: List[Condition]
            ) -> Dict[str, Any]:
    metrics = [
        "frac_correct", "frac_incorrect", "frac_undecided",
        "collective_correct", "agreement_frac", "agreement_correct",
        "agreement_maintained", "time_to_correct_agreement",
        "time_to_collective_correct", "total_messages", "unique_delivered",
        "duplicates_prevented", "rounds_executed", "messages_per_correct_node",
        "evidence_coverage", "final_edges", "final_blocks", "total_created",
        "total_removed", "created_edges_used", "created_edges_carrying",
        "created_edges_helping_correct",
        "frac_correct_after_failure", "recovery_rounds",
    ]
    summary = []
    for cond in conditions:
        cid = cond.condition_id
        for model in MODELS:
            sub = [r for r in rows
                   if r.get("condition_id") == cid and r.get("model") == model
                   and not r.get("control_infeasible")]
            for m in metrics:
                vals = []
                for r in sub:
                    v = r.get(m)
                    if v is None:
                        continue
                    try:
                        fv = float(v)
                    except (TypeError, ValueError):
                        continue
                    if fv != fv:
                        continue
                    vals.append(fv)
                mean, std = mean_std(vals)
                summary.append(dict(
                    condition_id=cid, model=model, metric=m,
                    n=len(vals), mean=mean, std=std))

    paired = []
    for cond in conditions:
        for other in ("CR", "A", "B", "C", "STATIC", "MV_W", "MV_U"):
            paired.extend(paired_diffs(
                rows, "D", other, metrics, condition_id=cond.condition_id))

    # --- Primary pre-registered inference (baseline D−CR only) ---
    stat_rows = []
    holm_input = []
    base_rows = [r for r in rows if r.get("condition_id") == "baseline"
                 and not r.get("control_infeasible")]
    by_d = {r["seed"]: r for r in base_rows if r["model"] == "D"}
    by_cr = {r["seed"]: r for r in base_rows if r["model"] == "CR"}
    primary_diffs: Dict[str, List[float]] = {}
    for metric in D_CR_PRIMARY:
        diffs = []
        for s in sorted(set(by_d) & set(by_cr)):
            try:
                diffs.append(float(by_d[s][metric]) - float(by_cr[s][metric]))
            except (KeyError, TypeError, ValueError):
                continue
        primary_diffs[metric] = diffs
        W, p = wilcoxon_signed_rank(diffs)
        m, sd = mean_std(diffs)
        stat_rows.append(dict(
            scope="primary",
            condition_id="baseline", pair="D-CR", metric=metric,
            n=len(diffs), mean_diff=m, std_diff=sd, wilcoxon_W=W, p_value=p))
        holm_input.append((metric, p))
    holm = holm_bonferroni(holm_input, alpha=0.05)

    # Non-inferiority + TOST on frac_correct (pre-registered δ)
    delta = NONINFERIORITY_MARGIN_FRAC_CORRECT
    acc_diffs = primary_diffs.get("frac_correct", [])
    ni = noninferiority_test(acc_diffs, delta=delta, alpha=0.05)
    tost = tost_equivalence(acc_diffs, delta=delta, alpha=0.05)

    return dict(
        summary=summary, paired=paired, stats=stat_rows, holm=holm,
        noninferiority=ni, tost=tost,
        ni_margin=delta,
        primary_metrics=list(D_CR_PRIMARY),
    )


def run_full_experiment(
    seeds: Sequence[int],
    out_dir: str = DEFAULT_OUT,
    conditions: Optional[List[Condition]] = None,
    smoke: bool = False,
) -> Dict[str, Any]:
    os.makedirs(out_dir, exist_ok=True)
    os.makedirs(os.path.join(out_dir, "raw"), exist_ok=True)
    os.makedirs(os.path.join(out_dir, "figures"), exist_ok=True)

    if smoke:
        conditions = [SMOKE_CONDITION]
    elif conditions is None:
        conditions = build_matrix()

    all_rows, all_time = [], []
    infeasible_log = []
    match_fail_log = []
    corr_diagnostics = {}

    for cond in conditions:
        print(f"=== condition {cond.condition_id} "
              f"(n={cond.n_states}, seeds={len(seeds)}) ===", flush=True)
        res = run_condition(cond, seeds, out_dir)
        all_rows.extend(res["rows"])
        all_time.extend(res["time_rows"])
        if res["n_infeasible"]:
            infeasible_log.append(dict(
                condition_id=cond.condition_id, n=res["n_infeasible"]))
        if res["match_failures"]:
            match_fail_log.append(dict(
                condition_id=cond.condition_id, n=res["match_failures"]))
        # Empirical pairwise bit correlation diagnostic
        corr_diagnostics[cond.condition_id] = dict(
            correlation_setting=cond.correlation,
            empirical_mean_pairwise_bit_corr=empirical_pairwise_bit_correlation(
                res["bundles"]),
            n_bundles=len(res["bundles"]),
        )

    analysis = analyze(all_rows, conditions)

    hashes = _source_hashes()
    config = dict(
        benchmark_id=BENCHMARK_ID,
        architecture=(
            "Stage-1: evidence propagation over precomputed graph sequences. "
            "Substrate dynamics run first; evidence cannot alter edge creation. "
            "This is not evidence-driven graph adaptation."
        ),
        preserved_one_py=hashes,
        expected_one_py_sha256=
        "3671c48e08c26dbe0c6bab20b2ec2091c63f721fb2d8adaa4dd2a6543c11a88a",
        one_py_unchanged=(
            hashes["sha256"] ==
            "3671c48e08c26dbe0c6bab20b2ec2091c63f721fb2d8adaa4dd2a6543c11a88a"),
        prior_results_dir="evidence_benchmark_results",
        seeds=list(seeds),
        n_seeds=len(seeds),
        conditions=[condition_to_dict(c) for c in conditions],
        models=list(MODELS),
        baselines=dict(
            STATIC="static directed R0 + weighted decision",
            MV_W="static bidirected R0 + weighted decision (formerly mislabelled MV)",
            MV_U="static bidirected R0 + unweighted majority of bits",
            CR="creation-count-matched random edge placement (preserved)",
        ),
        noninferiority_margin_frac_correct=NONINFERIORITY_MARGIN_FRAC_CORRECT,
        primary_inference=dict(
            condition="baseline",
            pair="D-CR",
            metrics=list(D_CR_PRIMARY),
            note="Condition-level contrasts outside baseline primary list are exploratory.",
        ),
        correlation_diagnostics=corr_diagnostics,
        random_streams=dict(
            init="s*1000000+1 (one.py)",
            move="s*1000000+2 (one.py)",
            ctrl="s*1000000+3 (one.py)",
            evidence="s*1000000+4",
            failure="s*1000000+5",
            relabel="s*1000000+6",
            note="Distinctness claimed; independence NOT claimed.",
        ),
        stream_seeds={
            str(s): dict(
                init=substrate.init_stream_seed(s),
                move=substrate.move_stream_seed(s),
                ctrl=substrate.cr_stream_seed(s),
                evidence=evidence_stream_seed(s),
                failure=failure_stream_seed(s),
                relabel=relabel_stream_seed(s),
            ) for s in seeds
        },
        infeasible_controls=infeasible_log,
        d_cr_match_failures=match_fail_log,
        cap_per_source=None,
        removal_age=5,
    )

    _write_csv(os.path.join(out_dir, "raw", "per_seed_results.csv"), all_rows)
    _write_csv(os.path.join(out_dir, "per_seed_results.csv"), all_rows)
    _write_csv(os.path.join(out_dir, "raw", "time_series.csv"), all_time)
    _write_csv(os.path.join(out_dir, "time_series.csv"), all_time)
    _write_csv(os.path.join(out_dir, "summary.csv"), analysis["summary"])
    _write_csv(os.path.join(out_dir, "paired_differences.csv"), analysis["paired"])
    _write_csv(os.path.join(out_dir, "statistical_tests.csv"), analysis["stats"])
    with open(os.path.join(out_dir, "holm_bonferroni.json"), "w") as f:
        json.dump(analysis["holm"], f, indent=2)
    with open(os.path.join(out_dir, "noninferiority_tost.json"), "w") as f:
        json.dump(dict(
            noninferiority=analysis["noninferiority"],
            tost=analysis["tost"],
            margin=analysis["ni_margin"],
        ), f, indent=2, default=str)
    with open(os.path.join(out_dir, "configuration.json"), "w") as f:
        json.dump(config, f, indent=2, default=str)

    acc_rows = [r for r in analysis["summary"]
                if r["metric"] in (
                    "frac_correct", "messages_per_correct_node",
                    "total_messages", "evidence_coverage",
                    "agreement_correct", "time_to_correct_agreement")]
    _write_csv(os.path.join(out_dir, "accuracy_communication_summary.csv"), acc_rows)

    return dict(
        rows=all_rows, time_rows=all_time, analysis=analysis, config=config,
        out_dir=out_dir, conditions=conditions,
    )
