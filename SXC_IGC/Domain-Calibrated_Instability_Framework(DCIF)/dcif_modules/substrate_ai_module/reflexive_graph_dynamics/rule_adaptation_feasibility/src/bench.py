"""Episode runner: one case x one model, with a shared operation budget."""
from __future__ import annotations

import time
import tracemalloc
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

from .graph import Case, Graph, apply_disruption, total_violations, violations
from .models import Model

BUDGET_OPS = 900
MAX_STALLS = 4


@dataclass
class EpisodeResult:
    metrics: dict
    events: List[dict]
    decisions: List[dict]


def run_episode(case: Case, model: Model, budget_ops: int = BUDGET_OPS,
                max_stalls: int = MAX_STALLS) -> EpisodeResult:
    g = case.initial
    ops = edits = evals = mods = applied = 0
    stalls = 0
    next_d = 0
    active = -1
    disruption_ops = [0] * len(case.disruptions)
    phase_end_ops = [0] * len(case.disruptions)
    recovery: List[Optional[int]] = [None] * len(case.disruptions)
    censored = [False] * len(case.disruptions)
    phase_viol: List[int] = []
    auc_num = 0.0
    decisions: List[dict] = []
    events: List[dict] = []

    tracemalloc.start()
    t0 = time.perf_counter()

    while ops < budget_ops:
        # apply any due disruption before the next decision
        while next_d < len(case.disruptions) and ops >= case.disruptions[next_d][0]:
            if active >= 0:
                phase_end_ops[active] = ops
                if recovery[active] is None:
                    censored[active] = True
            t_d, kind, params = case.disruptions[next_d]
            g = apply_disruption(g, kind, params)
            active = next_d
            disruption_ops[active] = ops
            phase_viol.append(total_violations(g))
            next_d += 1

        before = total_violations(g)
        d = model.decide(g, ops)
        if d.ops == 0 and not d.applied:
            if total_violations(g) == 0 and next_d < len(case.disruptions):
                ops = max(ops, case.disruptions[next_d][0])
                continue
            if total_violations(g) == 0 and next_d >= len(case.disruptions):
                break
            break
        g = d.graph
        ops += d.ops
        evals += d.evals
        mods += d.mods
        if d.applied:
            edits += 1
            stalls = 0
        elif d.meta_events:
            # the rule library changed, so give the system a fresh chance
            stalls = 0
        else:
            stalls += 1
        if d.meta_events:
            for ev in d.meta_events:
                ev = dict(ev)
                ev["case_id"] = case.case_id
                ev["model"] = model.name
                events.append(ev)
        after = total_violations(g)
        auc_num += (d.ops if d.ops > 0 else 1) * after
        if active >= 0 and recovery[active] is None and after == 0:
            recovery[active] = ops - disruption_ops[active]
        vv = violations(g)
        decisions.append(dict(
            case_id=case.case_id, model=model.name, step=len(decisions),
            op_start=ops - d.ops, ops=d.ops, edits=edits, evals=evals,
            mods=mods, v1=vv[0], v2=vv[1], v3=vv[2], v4=vv[3], total=after,
            applied=int(d.applied), rid=d.rid or "", delta=d.delta,
            library_enabled=sum(1 for r in model.rules.values() if r.enabled),
            library_total=len(model.rules), stalled=int(d.stalled),
        ))
        if stalls >= max_stalls:
            break

    if active >= 0:
        phase_end_ops[active] = ops
    if active >= 0 and recovery[active] is None:
        censored[active] = True
    for i in range(len(case.disruptions)):
        if recovery[i] is None and phase_end_ops[i] > 0:
            censored[i] = True

    peak = tracemalloc.get_traced_memory()[1]
    tracemalloc.stop()
    runtime = time.perf_counter() - t0

    final_v = violations(g)
    final_total = sum(final_v)
    # recovery: censored phases charged the remaining budget from their start
    rec_vals = []
    for i in range(len(case.disruptions)):
        if recovery[i] is not None:
            rec_vals.append(float(recovery[i]))
        elif phase_end_ops[i] > 0:
            rec_vals.append(float(max(0, phase_end_ops[i] - disruption_ops[i])))
    enabled = [r for r in model.rules.values() if r.enabled]
    used_uids = {u for (_, u, _, _) in model.applied_log}
    metrics = dict(
        case_id=case.case_id, model=model.name, n=case.n, K=case.K,
        final_v1=final_v[0], final_v2=final_v[1], final_v3=final_v[2],
        final_v4=final_v[3], final_violations=final_total,
        success=int(final_total == 0),
        recovery_ops=(sum(rec_vals) / len(rec_vals)) if rec_vals else float("nan"),
        n_recovered=sum(1 for r in recovery if r is not None),
        n_censored=sum(1 for c in censored if c),
        auc_violations=auc_num / max(1, ops),
        ops=ops, edits=edits, evals=evals, mods=mods,
        applications=len(model.applied_log),
        library_enabled=len(enabled), library_total=len(model.rules),
        distinct_rules_used=len(used_uids),
        rule_reuse=(len(model.applied_log) / len(used_uids)) if used_uids else 0.0,
        rule_stability=(mods / edits) if edits else 0.0,
        stalled_decisions=stalls,
        budget_exhausted=int(ops >= budget_ops),
        runtime_s=runtime,
        peak_mem_kb=peak / 1024.0,
        phase_initial_viol=phase_viol[0] if phase_viol else 0,
        phase_final_viol=final_total,
    )
    return EpisodeResult(metrics, events, decisions)


def annotate_effects(events: List[dict], applied_log: List[Tuple]) -> None:
    """Fill effect_observed / effect_improved / unnecessary in place."""
    for ev in events:
        op = ev["op"]
        uid = ev["uid"]
        if ev["event"] == "delete":
            prior = ev.get("prior_uses_50", 0)
            ev["effect_observed"] = 0
            ev["effect_improved"] = 0
            ev["unnecessary"] = int(prior == 0)
            continue
        window = [(o, d) for (o, u, d, _) in applied_log
                  if u == uid and op <= o <= op + 50]
        ev["effect_observed"] = int(bool(window))
        ev["effect_improved"] = int(any(d > 0 for _, d in window))
        ev["unnecessary"] = int(not window)
