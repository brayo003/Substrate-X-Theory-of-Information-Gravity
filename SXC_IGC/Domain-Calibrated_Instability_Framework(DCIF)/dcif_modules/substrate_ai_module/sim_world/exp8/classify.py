"""Classify operations A–F into Categories 0–5 from experimental evidence."""
from __future__ import annotations

from typing import Any


def _acc(summary: dict, abl: str, case: str) -> float | None:
    cell = (summary or {}).get(abl, {}).get(case)
    if not cell:
        return None
    return cell.get("accuracy")


def _pact(summary: dict, abl: str, case: str) -> float | None:
    cell = (summary or {}).get(abl, {}).get(case)
    if not cell:
        return None
    return cell.get("p_activate")


def classify_operations(results: dict[str, Any]) -> dict[str, Any]:
    """
    Category rubric (Task 8 brief):
      0 not demonstrated
      1 passive retention
      2 linear transformation
      3 nonlinear transformation (linear ablation fails)
      4 robust primitive (response surface / noise / seeds)
      5 behaviourally useful (bridge causal isolation)
    """
    out: dict[str, Any] = {}
    A = results.get("A", {})
    B = results.get("B", {})
    C = results.get("C", {})
    D = results.get("D", {})
    E = results.get("E", {})
    F = results.get("F", {})
    bridge = results.get("behavioural_bridge")
    num = results.get("numerical", {})

    # --- A coincidence ---
    pm = A.get("primary_metrics") or {}
    near_f1 = (pm.get("near_pair") or {}).get("f1")
    far_fpr = None
    if pm.get("far_pair"):
        fp = pm["far_pair"].get("fp", 0)
        tn = pm["far_pair"].get("tn", 0)
        far_fpr = fp / (fp + tn) if (fp + tn) else None
    sumA = A.get("summary_by_ablation") or {}
    lin_near = _pact(sumA, "linear_telegraph", "near_pair")
    nl_near = _pact(sumA, "nonlinear_full", "near_pair")
    ro_near = _pact(sumA, "readout_only", "near_pair")
    a_cat = 0
    a_notes = []
    if near_f1 is not None and near_f1 >= 0.7 and (far_fpr is None or far_fpr <= 0.3):
        a_cat = 1
        a_notes.append("schedule-correct coincidence behaviour")
        if lin_near is not None and nl_near is not None and nl_near > lin_near + 0.4:
            a_cat = 3
            a_notes.append("linear ablation fails near-pair latch")
        surf = A.get("response_surface_nl") or {}
        cells = surf.get("cells") or []
        # Robust if activation region has both successes and failures across amp×sep
        acts = [c["p_activate"] for c in cells if c.get("p_activate") is not None]
        if a_cat >= 3 and acts and min(acts) < 0.3 and max(acts) > 0.7:
            a_cat = 4
            a_notes.append("response surface shows finite operating window")
        if ro_near is not None and ro_near >= 0.9 and a_cat >= 3:
            a_notes.append("WARNING: readout_only also high — check decoder/amp")
            a_cat = min(a_cat, 2)
    out["A_coincidence"] = {
        "category": a_cat,
        "near_f1": near_f1,
        "far_fpr": far_fpr,
        "nl_p_near": nl_near,
        "lin_p_near": lin_near,
        "notes": a_notes,
    }

    # --- B temporal ---
    window = B.get("integration_window") or {}
    p0 = (window.get("0") or {}).get("p_activate")
    p40 = (window.get("40") or {}).get("p_activate")
    p20 = (window.get("20") or {}).get("p_activate")
    b_cat = 0
    b_notes = []
    if p0 is not None and p40 is not None and p0 > 0.7 and p40 < 0.3:
        b_cat = 3
        b_notes.append("finite temporal integration window")
        # Check linear does not show same latch window
        trials = B.get("trials") or []
        lin0 = [t for t in trials if t.get("ablation") == "linear_telegraph"
                and t.get("delay") == 0 and not t.get("failed") and not t.get("reverse")]
        if lin0 and float(sum(t["y_pred"] for t in lin0) / len(lin0)) < 0.3:
            b_notes.append("linear lacks simultaneous latch")
        else:
            b_notes.append("check linear simultaneous activation")
        # Order sensitivity
        rev = [t for t in trials if t.get("ablation") == "nonlinear_full"
               and t.get("reverse") and not t.get("failed")]
        fwd = [t for t in trials if t.get("ablation") == "nonlinear_full"
               and not t.get("reverse") and t.get("delay") in (2, 5, 10)
               and not t.get("failed")]
        if rev and fwd:
            # delays in reverse may be 2,10 only
            b_notes.append("order discrimination not claimed (scalar bistability)")
        # Robust if short-delay end of window still activates and long delay fails
        p5 = (window.get("5") or {}).get("p_activate")
        if p5 is not None and p5 >= 0.7 and p40 is not None and p40 < 0.3:
            b_cat = 4
            b_notes.append("window robust through delay≈B_MEM_WINDOW with long-delay failure")
    elif p0 is not None and p0 > 0.5:
        b_cat = 1
        b_notes.append("activation without clear long-delay failure")
    out["B_temporal"] = {
        "category": b_cat,
        "p_delay0": p0,
        "p_delay20": p20,
        "p_delay40": p40,
        "notes": b_notes,
    }

    # --- C spatial ---
    sumC = C.get("summary") or {}
    c_acc_nl = _acc(sumC, "nonlinear_full", "cluster")
    c_disp = _pact(sumC, "nonlinear_full", "dispersed")
    c_clu = _pact(sumC, "nonlinear_full", "cluster")
    lin_clu = _pact(sumC, "linear_telegraph", "cluster")
    c_cat = 0
    c_notes = []
    if c_clu is not None and c_disp is not None and c_clu > 0.7 and c_disp < 0.3:
        c_cat = 3 if (lin_clu is None or lin_clu < 0.3) else 2
        c_notes.append("equal-mass cluster vs dispersed discrimination")
        if c_acc_nl is not None and c_acc_nl >= 0.75:
            c_cat = max(c_cat, 3)
            # modest robustness if triangle also works
            tri = _pact(sumC, "nonlinear_full", "triangle")
            if tri is not None and tri > 0.7:
                c_cat = 4
                c_notes.append("cluster+triangle activate under equal mass")
    out["C_spatial"] = {
        "category": c_cat,
        "p_cluster": c_clu,
        "p_dispersed": c_disp,
        "lin_p_cluster": lin_clu,
        "notes": c_notes,
    }

    # --- D threshold / hysteresis ---
    d_fwd = D.get("nl_mean_forward_amp")
    hyst = D.get("hysteresis") or []
    nl_h = [h for h in hyst if h.get("ablation") == "nonlinear_full"]
    lin_h = [h for h in hyst if h.get("ablation") == "linear_telegraph"]
    d_cat = 0
    d_notes = []
    if d_fwd is not None:
        d_cat = 1
        d_notes.append(f"forward activation amp≈{d_fwd:.3f}")
        nl_drop = [h.get("reverse_drop_neg_amp") for h in nl_h
                   if h.get("reverse_drop_neg_amp") is not None]
        lin_fwd = [h.get("forward_activation_amp") for h in lin_h
                   if h.get("forward_activation_amp") is not None]
        if nl_drop and (not lin_fwd or min(x for x in lin_fwd if x) > d_fwd + 0.15
                        or len(lin_fwd) < len(nl_h) * 0.5):
            d_cat = 3
            d_notes.append("nonlinear threshold / retention vs linear")
        if nl_drop and d_fwd is not None:
            d_cat = max(d_cat, 3)
            d_notes.append(f"reverse drop requires neg amp≈{float(sum(nl_drop)/len(nl_drop)):.2f}")
            if all(h.get("still_high_after_strong") for h in nl_h):
                d_cat = 4
                d_notes.append("state retention after strong deposit")
    out["D_threshold"] = {
        "category": d_cat,
        "nl_mean_forward_amp": d_fwd,
        "notes": d_notes,
    }

    # --- E conflict ---
    sumE = E.get("summary") or {}
    e_opp = _acc(sumE, "nonlinear_full", "oppose")
    e_agree = _acc(sumE, "nonlinear_full", "agree")
    e_cat = 0
    e_notes = [E.get("limitation") or "scalar polarity limitation"]
    if e_agree is not None and e_agree > 0.7 and e_opp is not None and e_opp > 0.7:
        e_cat = 2
        e_notes.append("amplitude cancel / agree predictable; not semantic")
        # If linear also does oppose cancel equally → Category 2
        lin_opp = _acc(sumE, "linear_telegraph", "oppose")
        if lin_opp is not None and lin_opp > 0.7:
            e_cat = 2
            e_notes.append("oppose cancel also in linear (superposition)")
    out["E_conflict"] = {
        "category": e_cat,
        "acc_agree": e_agree,
        "acc_oppose": e_opp,
        "notes": e_notes,
    }

    # --- F pattern ---
    lift = F.get("completion_lift_nl")
    sumF = F.get("summary") or {}
    f_po = _pact(sumF, "nonlinear_full", "partial_only")
    f_pa = _pact(sumF, "nonlinear_full", "partial_after_template")
    f_cat = 0
    f_notes = []
    if lift is not None and lift > 0.4 and (f_po or 0) < 0.3 and (f_pa or 0) > 0.7:
        f_cat = 3
        f_notes.append("prior high-state enables recovery after damage+partial")
        # Distinguish attractor retention vs true pattern completion
        f_notes.append(
            "Likely bistable attractor retention / local re-excitation, "
            "not multi-feature pattern completion in scalar field"
        )
        f_cat = min(f_cat, 3)  # do not award 4 for mere retention recovery
    elif (f_pa or 0) > 0.5:
        f_cat = 1
        f_notes.append("recovery without clear lift over partial_only")
    else:
        f_notes.append("genuine pattern completion not demonstrated")
    out["F_pattern"] = {
        "category": f_cat,
        "completion_lift": lift,
        "p_partial_only": f_po,
        "p_partial_after": f_pa,
        "notes": f_notes,
    }

    # Behavioural upgrade to 5 if bridge succeeds with causal isolation
    if bridge and bridge.get("justified") and bridge.get("causal_pass"):
        for key in ("A_coincidence", "D_threshold"):
            if out[key]["category"] >= 4:
                out[key]["category"] = 5
                out[key]["notes"].append("behavioural bridge causal pass")

    cats = [v["category"] for v in out.values()]
    max_cat = max(cats) if cats else 0
    n_ge3 = sum(1 for c in cats if c >= 3)
    n_ge4 = sum(1 for c in cats if c >= 4)

    # Acceptance level
    level = 0
    if max_cat >= 1:
        level = 1
    if max_cat >= 3 and num.get("all_pass"):
        level = 2
    if n_ge4 >= 1 or n_ge3 >= 2:
        level = max(level, 3)
    if any(v["category"] >= 5 for v in out.values()):
        level = 4
    # Level 5 reserved for distinctive architectural contribution — not auto-awarded
    out["_meta"] = {
        "max_category": max_cat,
        "n_nonlinear_ops": n_ge3,
        "n_robust_ops": n_ge4,
        "acceptance_level_suggested": level,
        "numerical_all_pass": bool(num.get("all_pass")),
    }
    return out
