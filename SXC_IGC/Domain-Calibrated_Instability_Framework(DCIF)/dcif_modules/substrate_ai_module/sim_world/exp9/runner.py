"""Task 9 runner: pilot → freeze → confirmatory → reports artifacts."""
from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from typing import Any

import numpy as np

from sim_world.exp9 import config as cfg
from sim_world.exp9.config import Exp9ProtocolFreeze
from sim_world.exp9.experiments import (
    run_experiment_a,
    run_experiment_b,
    run_experiment_c,
    run_experiment_d,
    controlled_coincidence_smoke,
)
from sim_world.exp9.numerical import run_numerical_suite
from sim_world.exp9.statistics import paired_correct_rates, bonferroni


_HERE = os.path.dirname(os.path.abspath(__file__))
_SIM = os.path.dirname(_HERE)


def _json_default(o):
    if isinstance(o, (np.integer,)):
        return int(o)
    if isinstance(o, (np.floating,)):
        return float(o)
    if isinstance(o, np.ndarray):
        return o.tolist()
    raise TypeError(type(o))


def _write(path: str, obj: Any) -> None:
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, indent=2, default=_json_default)


def classify_acceptance(results: dict[str, Any]) -> dict[str, Any]:
    """Evidence-gated acceptance level — do not inflate."""
    a = results.get("A", {}).get("summary", {})
    b = results.get("B", {}).get("causal", {})
    nl = (a.get("nonlinear_sub") or {}).get("correct_rate")
    lin = (a.get("linear_sub") or {}).get("correct_rate")
    indep = (a.get("independent") or {}).get("correct_rate")
    msg = (a.get("direct_msg") or {}).get("correct_rate")

    level = 0
    reasons = []

    smoke = results.get("smoke", {})
    if smoke.get("pass"):
        level = max(level, 1)
        reasons.append("Level1: deposit/read + controlled latch interface OK")

    if nl is not None and indep is not None and nl > indep + 0.05:
        level = max(level, 2)
        reasons.append("Level2: nl collective correct_rate exceeds independent")

    if b.get("chain_supported"):
        level = max(level, 3)
        reasons.append("Level3: Exp B causal chain supported by ablations")

    # Level 4: autonomous utility under noise/async vs fair baselines — require
    # nl useful vs independent AND not collapsed under delay0, with noise sweep present
    noise = results.get("A_noise", {}).get("summary", {})
    async0 = results.get("C", {}).get("by_delay", {}).get("0", {}).get("nonlinear_sub", {})
    if (
        nl is not None and indep is not None and nl >= 0.5 and nl > indep + 0.1
        and (async0.get("correct_rate") or 0) >= 0.4
        and b.get("chain_supported")
    ):
        level = max(level, 4)
        reasons.append("Level4: collective utility vs independent under protocol")

    # Level 5: distinctive vs messaging/BB/pheromone — only if nl beats msg with margin
    # and mechanism attributed. Default withhold.
    if (
        level >= 4 and msg is not None and nl is not None and nl > msg + 0.15
        and lin is not None and nl > lin + 0.15
    ):
        level = 5
        reasons.append("Level5: nl exceeds messaging and linear with margin")
    else:
        reasons.append(
            "Level5 withheld: requires distinctive advantage vs fair messaging/BB "
            "not explained by conventional channels"
        )

    unsupported = []
    if msg is not None and nl is not None and msg >= nl:
        unsupported.append("Substrate superiority over direct messaging not established")
    if not b.get("chain_supported"):
        unsupported.append("Composed coincidence→hysteresis agent chain not fully supported")
    if results.get("C", {}).get("order_discrimination", {}).get("supported") is False:
        unsupported.append("Temporal order discrimination (scalar field limitation)")

    return {
        "acceptance_level": level,
        "reasons": reasons,
        "unsupported_claims": unsupported,
        "rates": {"nonlinear": nl, "linear": lin, "independent": indep, "direct_msg": msg},
    }


def run_pilot() -> dict[str, Any]:
    seeds = list(cfg.PILOT_SEEDS)
    smoke = controlled_coincidence_smoke()
    numerical = run_numerical_suite()
    A = run_experiment_a(seeds)
    B = run_experiment_b(seeds)
    C = run_experiment_c(seeds, delays=(0, 5, 15, 40))
    D = run_experiment_d(seeds)
    A_noise = run_experiment_a(seeds, noise_sigma=0.45)
    paired = {
        "nl_vs_lin": paired_correct_rates(A["trials"], "nonlinear_sub", "linear_sub"),
        "nl_vs_indep": paired_correct_rates(A["trials"], "nonlinear_sub", "independent"),
        "nl_vs_msg": paired_correct_rates(A["trials"], "nonlinear_sub", "direct_msg"),
    }
    out = {
        "phase": "pilot",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "smoke": smoke,
        "numerical": numerical,
        "A": A,
        "A_noise": A_noise,
        "B": B,
        "C": C,
        "D": D,
        "paired": paired,
    }
    out["acceptance_preview"] = classify_acceptance(out)
    return out


def freeze_config(pilot: dict[str, Any]) -> dict[str, Any]:
    freeze = Exp9ProtocolFreeze()
    doc = {
        "frozen_at": datetime.now(timezone.utc).isoformat(),
        "protocol": freeze.to_dict(),
        "pilot_preview_level": pilot.get("acceptance_preview", {}).get("acceptance_level"),
        "confirm_seeds": list(range(cfg.CONFIRM_SEED_START, cfg.CONFIRM_SEED_START + cfg.CONFIRM_N)),
        "primary_outcomes": [
            "A: nl vs linear correct_rate",
            "A: nl vs independent correct_rate",
            "A: nl vs direct_msg correct_rate (report; superiority not required)",
            "B: chain_supported",
            "C: delay0 vs delay40 nl correct_rate",
        ],
        "note": "Do not retune parameters after inspecting confirmatory outcomes.",
    }
    _write(os.path.join(_SIM, "exp9_configuration.json"), doc)
    _write(os.path.join(_HERE, "exp9_configuration.json"), doc)
    return doc


def run_confirmatory() -> dict[str, Any]:
    seeds = list(range(cfg.CONFIRM_SEED_START, cfg.CONFIRM_SEED_START + cfg.CONFIRM_N))
    smoke = controlled_coincidence_smoke()
    numerical = run_numerical_suite()
    A = run_experiment_a(seeds)
    B = run_experiment_b(seeds)
    C = run_experiment_c(seeds)
    D = run_experiment_d(seeds)
    A_noise = run_experiment_a(seeds, noise_sigma=0.45)
    A_disc = run_experiment_a(seeds, disconnect_ids=(0,))

    paired = {
        "nl_vs_lin": paired_correct_rates(A["trials"], "nonlinear_sub", "linear_sub"),
        "nl_vs_indep": paired_correct_rates(A["trials"], "nonlinear_sub", "independent"),
        "nl_vs_msg": paired_correct_rates(A["trials"], "nonlinear_sub", "direct_msg"),
        "nl_vs_bb": paired_correct_rates(A["trials"], "nonlinear_sub", "blackboard"),
        "nl_vs_pher": paired_correct_rates(A["trials"], "nonlinear_sub", "pheromone"),
    }
    # C delay contrast
    c_trials_nl = [
        t for t in C["trials"]
        if t["arch"] == "nonlinear_sub" and t["async_delay"] in (0, 40) and not t["failed"]
    ]
    # Build pseudo paired delay0 vs delay40
    d0 = {t["seed"]: t["correct"] for t in c_trials_nl if t["async_delay"] == 0}
    d40 = {t["seed"]: t["correct"] for t in c_trials_nl if t["async_delay"] == 40}
    delay_pair_trials = []
    for s in sorted(set(d0) & set(d40)):
        delay_pair_trials.append({"seed": s, "arch": "delay0", "correct": d0[s], "failed": False})
        delay_pair_trials.append({"seed": s, "arch": "delay40", "correct": d40[s], "failed": False})
    paired["delay0_vs_delay40"] = paired_correct_rates(delay_pair_trials, "delay0", "delay40")

    pvals = [
        paired["nl_vs_lin"].get("p_perm", 1.0),
        paired["nl_vs_indep"].get("p_perm", 1.0),
        paired["nl_vs_msg"].get("p_perm", 1.0),
        0.0 if B.get("causal", {}).get("chain_supported") else 1.0,
        paired["delay0_vs_delay40"].get("p_perm", 1.0),
    ]
    multi = bonferroni(pvals, cfg.ALPHA, m=cfg.N_PRIMARY_COMPS)

    out = {
        "phase": "confirmatory",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "seeds": seeds,
        "smoke": smoke,
        "numerical": numerical,
        "A": A,
        "A_noise": A_noise,
        "A_disconnect": A_disc,
        "B": B,
        "C": C,
        "D": D,
        "paired": paired,
        "multiple_comparisons": multi,
    }
    out["acceptance"] = classify_acceptance(out)
    return out


def write_numerical_md(numerical: dict[str, Any], path: str) -> None:
    lines = [
        "# EXP9 Numerical Validation",
        "",
        f"**Date:** {datetime.now(timezone.utc).date().isoformat()}",
        f"**all_pass:** `{numerical.get('all_pass')}`",
        "",
        "Continuous metrics required in addition to binary activation agreement.",
        "",
    ]
    for b in numerical.get("blocks", []):
        lines.append(f"## {b.get('test')}")
        lines.append("")
        lines.append(f"- pass: `{b.get('pass')}`")
        if "pass_binary" in b:
            lines.append(f"- pass_binary: `{b.get('pass_binary')}`")
            lines.append(f"- pass_continuous: `{b.get('pass_continuous')}`")
        if "note" in b:
            lines.append(f"- note: {b['note']}")
        lines.append("")
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")


def write_report(conf: dict[str, Any], pilot: dict[str, Any], path: str) -> None:
    acc = conf.get("acceptance", {})
    a = conf.get("A", {}).get("summary", {})
    level = acc.get("acceptance_level")
    lines = [
        "# EXP9 Experimental Report — Autonomous Substrate-Mediated Collective Computation",
        "",
        f"**Date:** {datetime.now(timezone.utc).date().isoformat()}",
        f"**Acceptance level:** **{level}**",
        "",
        "## Central question",
        "",
        "Has the project progressed from demonstrating computational properties of a nonlinear "
        "substrate to demonstrating that autonomous agents can use those properties as part of "
        "a larger collective computational architecture?",
        "",
        f"**Answer (evidence-gated):** acceptance Level {level}. "
        + (
            "Partial/limited autonomous use demonstrated; see unsupported claims."
            if (level or 0) < 5
            else "Distinctive architectural contribution claimed."
        ),
        "",
        "## What was tested",
        "",
        "- Exp A: distributed noisy evidence → landmark commitment across 7 architectures",
        "- Exp B: coincidence→hysteresis causal chain ablations",
        "- Exp C: async evidence delays",
        "- Exp D: spatial clustered/dispersed/noise/disconnect variants",
        "- Numerical suite with continuous field errors",
        "",
        "## What was implemented",
        "",
        "- Isolated `exp9/` package; Task 6–8 untouched",
        "- Local deposit/read interface; public landmarks; withheld \(k^*\)",
        "- Fair baselines: independent, messaging, blackboard, pheromone, linear, hybrid",
        "",
        "## Agent observability",
        "",
        "Agents observe local evidence patches within sensor radius (noisy scalars) and local "
        "medium readouts at visited landmarks. They do **not** receive true landmark identity, "
        "global field argmax, or other agents' deposit logs.",
        "",
        "## Results summary (confirmatory)",
        "",
        "| Architecture | Correct rate | FP | FN | Mean resource |",
        "|---|---|---|---|---|",
    ]
    for arch, s in a.items():
        lines.append(
            f"| {arch} | {s.get('correct_rate')} | {s.get('false_positive_rate')} | "
            f"{s.get('false_negative_rate')} | {s.get('mean_resource')} |"
        )
    lines += [
        "",
        "### Paired comparisons",
        "",
        "```",
        json.dumps(conf.get("paired", {}), indent=2, default=_json_default)[:4000],
        "```",
        "",
        "### Exp B causal",
        "",
        "```",
        json.dumps(conf.get("B", {}).get("causal", {}), indent=2),
        "```",
        "",
        "## Substrate contribution / necessary mechanisms",
        "",
        "- Controlled smoke coincidence latch: nl vs linear (interface sanity).",
        "- Agent-level contribution judged by Exp A/B ablations and paired rates.",
        "- Propagation necessity re-evaluated in agent setting via `no_propagation` ablation.",
        "",
        "## Baselines that matched or outperformed",
        "",
        "See confirmatory table; messaging/blackboard expected competitive when bandwidth plentiful.",
        "",
        "## Hypotheses that failed / limitations",
        "",
    ]
    for u in acc.get("unsupported_claims", []):
        lines.append(f"- {u}")
    lines += [
        "",
        "## Numerical / statistical limitations",
        "",
        f"- numerical.all_pass = `{conf.get('numerical', {}).get('all_pass')}`",
        f"- confirmatory N = {cfg.CONFIRM_N}; Bonferroni m = {cfg.N_PRIMARY_COMPS}",
        "- Dirichlet-like BC not swept; \(\\tau\\neq1\) Laplacian ambiguity inherited (unused).",
        "- Pilot used for preview only; confirmatory seeds 400+.",
        "",
        f"## Acceptance reasons",
        "",
    ]
    for r in acc.get("reasons", []):
        lines.append(f"- {r}")
    lines += [
        "",
        "## Claims remaining unsupported",
        "",
    ]
    for u in acc.get("unsupported_claims", []):
        lines.append(f"- {u}")
    lines += [
        "",
        "## Artifact index",
        "",
        "- `exp9/EXP9_PRE_IMPLEMENTATION_AUDIT.md`",
        "- `exp9/EXP9_ARCHITECTURAL_SPECIFICATION.md`",
        "- `exp9/EXP9_EXPERIMENTAL_PROTOCOL.md`",
        "- `exp9/EXP9_BASELINE_FAIRNESS_AUDIT.md`",
        "- `exp9/EXP9_NUMERICAL_VALIDATION.md`",
        "- `exp9_configuration.json` / `exp9_results.json`",
        "- `exp9_pilot_results.json`",
        "- `tests/test_exp9_*.py`",
        "",
    ]
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")


def main(phase: str = "all") -> dict[str, Any]:
    if phase in ("pilot", "all"):
        pilot = run_pilot()
        _write(os.path.join(_SIM, "exp9_pilot_results.json"), pilot)
        _write(os.path.join(_HERE, "exp9_pilot_results.json"), pilot)
        freeze_config(pilot)
        write_numerical_md(
            pilot["numerical"],
            os.path.join(_HERE, "EXP9_NUMERICAL_VALIDATION.md"),
        )
    else:
        pilot = {}

    if phase in ("confirm", "all"):
        conf = run_confirmatory()
        # Strip heavy trial duplication for root summary? Keep full for reproducibility.
        _write(os.path.join(_SIM, "exp9_results.json"), conf)
        _write(os.path.join(_HERE, "exp9_results.json"), conf)
        # Per-seed raw extract
        raw = {
            "A": conf["A"]["trials"],
            "B": conf["B"]["trials"],
            "C": conf["C"]["trials"],
            "D": conf["D"]["trials"],
        }
        _write(os.path.join(_HERE, "exp9_raw_per_seed.json"), raw)
        write_numerical_md(
            conf["numerical"],
            os.path.join(_HERE, "EXP9_NUMERICAL_VALIDATION.md"),
        )
        write_report(
            conf, pilot,
            os.path.join(_HERE, "EXP9_EXPERIMENTAL_REPORT.md"),
        )
        # Also copy report to sim_world root for discoverability (new file, not overwriting T6–8)
        write_report(conf, pilot, os.path.join(_SIM, "EXP9_EXPERIMENTAL_REPORT.md"))
        return conf
    return pilot


if __name__ == "__main__":
    import sys
    ph = sys.argv[1] if len(sys.argv) > 1 else "all"
    main(ph)
