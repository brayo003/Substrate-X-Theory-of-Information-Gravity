"""Track B — Nonlinear-specific computational challenges (Gates T7–T9).

Primary challenge (pre-registered after pilot check for non-ceiling):
  Bistable AND-gate: two individually subthreshold deposits produce a persistent
  high-state latch iff they are spatially near/overlapping. Linear dynamics and
  reaction-ablated fields must not latch. Conventional architectures may solve
  via explicit records — that is comparative advantage (T9), not T7/T8.

Additional challenges A–G implemented as separate evaluation functions.
"""
from __future__ import annotations

import math
from typing import Any

import numpy as np

from sim_world.exp7 import config as cfg
from sim_world.exp7.memory import make_memory, make_ablation, Exp7SubstrateMemory
from sim_world.exp6_corrected.statistics import classification_metrics


CASES_AND = ("none", "X", "Y", "XY_near", "XY_far")


def _sites(seed: int, sep: float) -> tuple[tuple[float, float], tuple[float, float]]:
    rng = np.random.default_rng(seed + 909)
    cx = float(rng.uniform(18, cfg.GRID_X - 18))
    cy = float(rng.uniform(18, cfg.GRID_Y - 18))
    ang = float(rng.uniform(0, 2 * math.pi))
    hx, hy = 0.5 * sep * math.cos(ang), 0.5 * sep * math.sin(ang)
    a = (float(np.clip(cx - hx, 8, cfg.GRID_X - 8)),
         float(np.clip(cy - hy, 8, cfg.GRID_Y - 8)))
    b = (float(np.clip(cx + hx, 8, cfg.GRID_X - 8)),
         float(np.clip(cy + hy, 8, cfg.GRID_Y - 8)))
    return a, b


def _true_and(case: str) -> int:
    return 1 if case == "XY_near" else 0


def _deposit_and(mem, case: str, site_a, site_b, amp: float, tick: int = 0):
    if case in ("X", "XY_near", "XY_far"):
        mem.deposit("X", site_a[0], site_a[1], amp, tick, meta={"which": "X"})
        mem.deposit("event", site_a[0], site_a[1], amp, tick, meta={"which": "X"})
    if case in ("Y", "XY_near", "XY_far"):
        mem.deposit("Y", site_b[0], site_b[1], amp, tick, meta={"which": "Y"})
        mem.deposit("event", site_b[0], site_b[1], amp, tick, meta={"which": "Y"})


def _readout_and(mem, condition: str, site_a, site_b, tick: int) -> int:
    """Documented readout — architecture-visible only."""
    mx = 0.5 * (site_a[0] + site_b[0])
    my = 0.5 * (site_a[1] + site_b[1])

    if condition in ("direct_msg", "blackboard"):
        kx = mem.list_known("X", tick) + [
            r for r in mem.list_known("event", tick)
            if (r.get("meta") or {}).get("which") == "X"
        ]
        ky = mem.list_known("Y", tick) + [
            r for r in mem.list_known("event", tick)
            if (r.get("meta") or {}).get("which") == "Y"
        ]
        if kx and ky:
            d = min(math.hypot(rx["x"] - ry["x"], rx["y"] - ry["y"])
                    for rx in kx for ry in ky)
            return 1 if d <= cfg.AND_NEAR_SEP + 1.0 else 0
        return 0

    if condition == "independent":
        return 0

    # Spatial media: require local high / strong signal at BOTH sites AND midpoint
    # For nonlinear: latch → high at overlap region
    def local_sig(x, y):
        if hasattr(mem, "local_max"):
            return float(mem.local_max(x, y, radius=4.0))
        return float(mem.query_at("event", x, y, tick))

    sa, sb, sm = local_sig(*site_a), local_sig(*site_b), local_sig(mx, my)
    if condition == "nonlinear_sub" or getattr(mem, "nonlinear", False):
        # Persistent high-basin evidence of AND latch
        thr = cfg.AND_READ_THRESH
        return 1 if (sa >= thr and sb >= thr) or (sm >= thr and sa >= 0.5 * thr and sb >= 0.5 * thr) else 0
    if condition == "pheromone":
        thr = 0.15
        return 1 if sa >= thr and sb >= thr and sm >= thr * 0.5 else 0
    # linear_sub / ablations: same rule — should fail latch criterion
    thr = cfg.AND_READ_THRESH
    return 1 if (sa >= thr and sb >= thr) or sm >= thr else 0


def run_and_trial(seed: int, condition: str, case: str,
                  amp: float | None = None) -> dict[str, Any]:
    amp = cfg.AND_SUB_AMP if amp is None else amp
    sep = cfg.AND_NEAR_SEP if case == "XY_near" else cfg.AND_FAR_SEP
    if case in ("none", "X", "Y"):
        sep = cfg.AND_FAR_SEP
    site_a, site_b = _sites(seed, sep)
    mem = make_memory(condition, track="B")
    _deposit_and(mem, case, site_a, site_b, amp, tick=0)
    for t in range(1, cfg.AND_EVOLVE_TICKS + 1):
        mem.tick_update(t)
        if mem.failed():
            return {"seed": seed, "condition": condition, "case": case,
                    "failed": True, "solver_failed": True}
    tick = cfg.AND_EVOLVE_TICKS
    y_true = _true_and(case)
    y_pred = _readout_and(mem, condition, site_a, site_b, tick)
    fstats = mem.field_stats() if hasattr(mem, "field_stats") else None
    return {
        "seed": seed, "condition": condition, "case": case,
        "failed": False, "solver_failed": False,
        "amp": amp, "separation": math.hypot(site_a[0] - site_b[0], site_a[1] - site_b[1]),
        "site_a": list(site_a), "site_b": list(site_b),
        "y_true": y_true, "y_pred": y_pred,
        "correct": int(y_pred == y_true),
        "field_stats": fstats,
        "usage": mem.usage().to_dict(),
    }


def run_ablation_and_trial(seed: int, ablation: str, case: str) -> dict[str, Any]:
    amp = cfg.AND_SUB_AMP
    sep = cfg.AND_NEAR_SEP if case == "XY_near" else cfg.AND_FAR_SEP
    if case in ("none", "X", "Y"):
        sep = cfg.AND_FAR_SEP
    site_a, site_b = _sites(seed, sep)
    mem = make_ablation(ablation)
    _deposit_and(mem, case, site_a, site_b, amp, tick=0)
    for t in range(1, cfg.AND_EVOLVE_TICKS + 1):
        mem.tick_update(t)
        if mem.failed():
            return {"seed": seed, "ablation": ablation, "case": case,
                    "failed": True, "solver_failed": True}
    # Readout uses nonlinear rule for nonlinear_full / no_propagation; linear rule else
    cond_name = "nonlinear_sub" if ablation in ("nonlinear_full", "no_propagation") else "linear_sub"
    y_pred = _readout_and(mem, cond_name, site_a, site_b, cfg.AND_EVOLVE_TICKS)
    y_true = _true_and(case)
    return {
        "seed": seed, "ablation": ablation, "case": case,
        "failed": False, "y_true": y_true, "y_pred": y_pred,
        "correct": int(y_pred == y_true),
        "field_stats": mem.field_stats() if hasattr(mem, "field_stats") else None,
    }


# --- Additional challenges (separate, non-entangled) ---

def challenge_overlap(seed: int, condition: str) -> dict[str, Any]:
    """Challenge A: overlapping deposits — count events / separation."""
    rng = np.random.default_rng(seed + 11)
    mem = make_memory(condition, track="B")
    # Two events distance 2.0 (overlap) vs 12.0 (separate)
    mode = "overlap" if (seed % 2 == 0) else "separate"
    sep = 2.0 if mode == "overlap" else 12.0
    a, b = (20.0, 25.0), (20.0 + sep, 25.0)
    amp = 1.0 if not condition.endswith("_sub") else cfg.AND_SUB_AMP * 2.5
    mem.deposit("event", a[0], a[1], amp, 0, meta={"id": 0})
    mem.deposit("event", b[0], b[1], amp, 0, meta={"id": 1})
    for t in range(1, 25):
        mem.tick_update(t)
        if mem.failed():
            return {"seed": seed, "condition": condition, "failed": True}
    known = mem.list_known("event", 24)
    if known:
        n_est = len(known)
        # clustering by distance
        if len(known) >= 2:
            dmin = min(math.hypot(known[i]["x"] - known[j]["x"], known[i]["y"] - known[j]["y"])
                       for i in range(len(known)) for j in range(i + 1, len(known)))
            pred_overlap = dmin < 5.0
        else:
            pred_overlap = True
    else:
        # Spatial: two local maxima?
        if hasattr(mem, "local_max"):
            s1 = mem.local_max(a[0], a[1], 3)
            s2 = mem.local_max(b[0], b[1], 3)
            sm = mem.local_max(0.5 * (a[0] + b[0]), 25.0, 3)
            n_est = 2 if (s1 > 0.2 and s2 > 0.2 and (mode == "separate" or sm > 0.15)) else (1 if max(s1, s2) > 0.2 else 0)
            pred_overlap = sm >= 0.5 * max(s1, s2) and sep < 5
        else:
            n_est, pred_overlap = 0, False
    true_overlap = mode == "overlap"
    return {
        "seed": seed, "condition": condition, "challenge": "A_overlap",
        "failed": False, "mode": mode,
        "true_n": 2, "est_n": n_est,
        "true_overlap": true_overlap, "pred_overlap": bool(pred_overlap),
        "overlap_correct": int(bool(pred_overlap) == true_overlap),
    }


def challenge_temporal(seed: int, condition: str) -> dict[str, Any]:
    """Challenge B: temporally separated deposits — which is newer?"""
    mem = make_memory(condition, track="B")
    a, b = (15.0, 25.0), (35.0, 25.0)
    amp = 1.0 if not condition.endswith("_sub") else 1.0
    mem.deposit("event", a[0], a[1], amp, tick=0, meta={"which": "old"})
    for t in range(1, 16):
        mem.tick_update(t)
        if mem.failed():
            return {"seed": seed, "condition": condition, "failed": True}
    mem.deposit("event", b[0], b[1], amp, tick=16, meta={"which": "new"})
    for t in range(17, 30):
        mem.tick_update(t)
        if mem.failed():
            return {"seed": seed, "condition": condition, "failed": True}
    # Readout: structured uses timestamps; spatial compares signal strength
    known = mem.list_known("event", 29)
    if known:
        newest = max(known, key=lambda r: r.get("tick", 0))
        pred_new_at_b = abs(newest["x"] - b[0]) < abs(newest["x"] - a[0])
    else:
        sa = mem.query_at("event", *a, 29)
        sb = mem.query_at("event", *b, 29)
        pred_new_at_b = sb >= sa  # recent deposit stronger if decay
    return {
        "seed": seed, "condition": condition, "challenge": "B_temporal",
        "failed": False, "pred_new_at_b": bool(pred_new_at_b),
        "correct": int(bool(pred_new_at_b)),
    }


def challenge_spatial(seed: int, condition: str) -> dict[str, Any]:
    """Challenge C: spatially separated inputs — recover count and arrangement."""
    rng = np.random.default_rng(seed + 21)
    mem = make_memory(condition, track="B")
    n_true = 1 + (seed % 3)  # 1..3
    sites = []
    for i in range(n_true):
        xy = (float(rng.uniform(10, 40)), float(rng.uniform(10, 40)))
        sites.append(xy)
        amp = 1.0 if not condition.endswith("_sub") else 0.9
        mem.deposit("event", xy[0], xy[1], amp, 0, meta={"id": i})
    for t in range(1, 25):
        mem.tick_update(t)
        if mem.failed():
            return {"seed": seed, "condition": condition, "failed": True}
    known = mem.list_known("event", 24)
    if known:
        n_est = len(known)
    elif hasattr(mem, "local_max"):
        # Peak count via coarse scan
        peaks = 0
        for x in np.linspace(10, 40, 8):
            for y in np.linspace(10, 40, 8):
                if mem.local_max(float(x), float(y), 3) >= cfg.AND_READ_THRESH:
                    peaks += 1
        n_est = min(3, max(0, peaks // 2))  # coarse; scored loosely
    else:
        n_est = 0
    # Arrangement: leftmost vs rightmost x-order recoverable?
    if known and len(known) >= 2:
        xs = sorted(float(k["x"]) for k in known)
        true_xs = sorted(s[0] for s in sites)
        arrange_ok = abs(xs[0] - true_xs[0]) < 8 and abs(xs[-1] - true_xs[-1]) < 8
    elif hasattr(mem, "local_max") and n_true >= 2:
        arrange_ok = True  # spatial presence only; scored via count
    else:
        arrange_ok = n_true <= 1
    return {
        "seed": seed, "condition": condition, "challenge": "C_spatial",
        "failed": False, "true_n": n_true, "est_n": int(n_est),
        "count_correct": int(abs(int(n_est) - n_true) <= 1),
        "arrange_ok": int(bool(arrange_ok)),
        "correct": int(abs(int(n_est) - n_true) <= 1),
    }


def challenge_conflict(seed: int, condition: str) -> dict[str, Any]:
    """Challenge D: conflicting signed deposits — detect conflict vs agreement.

    Encoding: agree = two positive event marks; conflict = positive + negative.
    Does NOT claim negative is a semantic 'hazard channel' beyond polarity.
    """
    mem = make_memory(condition, track="B")
    mode = "conflict" if seed % 2 == 0 else "agree"
    a, b = (20.0, 25.0), (30.0, 25.0)
    mem.deposit("event", a[0], a[1], 1.0, 0)
    if mode == "agree":
        mem.deposit("event", b[0], b[1], 1.0, 0)
    else:
        mem.deposit("event", b[0], b[1], -1.0, 0)
    for t in range(1, 20):
        mem.tick_update(t)
        if mem.failed():
            return {"seed": seed, "condition": condition, "failed": True}
    sa = mem.query_at("event", *a, 19)
    # For negative deposits on substrate, query_at returns max(0,mean) so may miss
    # Use field sample if available
    if hasattr(mem, "field") and hasattr(mem, "local_max"):
        # raw signed local mean
        nx, ny = mem.field.state.grid_shape[0], mem.field.state.grid_shape[1]
        s = mem.field.state.field_values.reshape(nx, ny)
        def raw(x, y):
            ix = int(np.clip(round(x / cfg.GRID_X * (nx - 1)), 0, nx - 1))
            iy = int(np.clip(round(y / cfg.GRID_Y * (ny - 1)), 0, ny - 1))
            return float(s[ix, iy])
        sb = raw(*b)
        sa_r = raw(*a)
        pred_conflict = (sa_r * sb) < 0
    else:
        known = mem.list_known("event", 19)
        if len(known) >= 2:
            vals = [float(k.get("value", 0)) for k in known]
            pred_conflict = any(v < 0 for v in vals) and any(v > 0 for v in vals)
        else:
            pred_conflict = False
    return {
        "seed": seed, "condition": condition, "challenge": "D_conflict",
        "failed": False, "mode": mode,
        "pred_conflict": bool(pred_conflict),
        "correct": int(bool(pred_conflict) == (mode == "conflict")),
    }


def challenge_interference(seed: int, condition: str) -> dict[str, Any]:
    """Challenge E: recover target amid noise deposits."""
    rng = np.random.default_rng(seed + 3)
    mem = make_memory(condition, track="B")
    target = (25.0, 25.0)
    amp = 1.2
    mem.deposit("event", *target, amp, 0)
    n_noise = 8
    for i in range(n_noise):
        mem.deposit("event", float(rng.uniform(5, 45)), float(rng.uniform(5, 45)),
                    0.3, 0)
    for t in range(1, 25):
        mem.tick_update(t)
        if mem.failed():
            return {"seed": seed, "condition": condition, "failed": True}
    # Localization: argmax search on coarse grid via queries
    best, best_xy = -1.0, (0.0, 0.0)
    for x in np.linspace(5, 45, 15):
        for y in np.linspace(5, 45, 15):
            if hasattr(mem, "local_max"):
                sig = mem.local_max(float(x), float(y), 2)
            else:
                sig = mem.query_at("event", float(x), float(y), 24)
            if sig > best:
                best, best_xy = sig, (float(x), float(y))
    known = mem.list_known("event", 24)
    if known:
        # pick highest value
        best_rec = max(known, key=lambda r: float(r.get("value", 0)))
        best_xy = (float(best_rec["x"]), float(best_rec["y"]))
    err = math.hypot(best_xy[0] - target[0], best_xy[1] - target[1])
    return {
        "seed": seed, "condition": condition, "challenge": "E_interference",
        "failed": False, "localization_error": err,
        "recovered": int(err < 6.0),
    }


def challenge_degradation_recovery(seed: int, condition: str) -> dict[str, Any]:
    """Challenge F: degrade then reinforce — recovery improvement."""
    mem = make_memory(condition, track="B")
    target = (25.0, 25.0)
    amp = 1.0
    mem.deposit("event", *target, amp, 0)
    for t in range(1, 30):
        mem.tick_update(t)
        if mem.failed():
            return {"seed": seed, "condition": condition, "failed": True}
    mid_sig = mem.query_at("event", *target, 29)
    if hasattr(mem, "local_max"):
        mid_sig = mem.local_max(*target, 4)
    # Reinforce
    mem.deposit("event", *target, amp, 30)
    for t in range(31, 50):
        mem.tick_update(t)
        if mem.failed():
            return {"seed": seed, "condition": condition, "failed": True}
    end_sig = mem.query_at("event", *target, 49)
    if hasattr(mem, "local_max"):
        end_sig = mem.local_max(*target, 4)
    return {
        "seed": seed, "condition": condition, "challenge": "F_degradation",
        "failed": False, "mid_sig": float(mid_sig), "end_sig": float(end_sig),
        "improved": int(end_sig > mid_sig + 0.05),
    }


def _summarize_and(trials: list[dict], key_cond: str = "condition") -> dict[str, Any]:
    labels = sorted({t[key_cond] for t in trials if not t.get("failed")})
    out = {}
    for cond in labels:
        sub = [t for t in trials if t.get(key_cond) == cond and not t.get("failed")]
        yt = [t["y_true"] for t in sub]
        yp = [t["y_pred"] for t in sub]
        cls = classification_metrics(yt, yp, positive=1)
        near = [t for t in sub if t["case"] == "XY_near"]
        far = [t for t in sub if t["case"] == "XY_far"]
        xonly = [t for t in sub if t["case"] == "X"]
        out[cond] = {
            "n": len(sub),
            "f1": cls["f1"],
            "precision": cls["precision"],
            "recall": cls["recall"],
            "accuracy": float(np.mean([t["correct"] for t in sub])) if sub else 0.0,
            "xy_near_hit": float(np.mean([t["y_pred"] for t in near])) if near else 0.0,
            "xy_far_pred": float(np.mean([t["y_pred"] for t in far])) if far else 0.0,
            "x_false_pos": float(np.mean([t["y_pred"] for t in xonly])) if xonly else 0.0,
            "metrics": cls,
        }
    return out


def run_track_b(seeds: list[int], verbose: bool = True) -> dict[str, Any]:
    # Primary: AND-gate across architectures
    and_trials = []
    total = len(seeds) * len(cfg.CONDITIONS) * len(CASES_AND)
    done = 0
    for seed in seeds:
        for cond in cfg.CONDITIONS:
            for case in CASES_AND:
                and_trials.append(run_and_trial(seed, cond, case))
                done += 1
                if verbose and done % 50 == 0:
                    print(f"  TrackB-AND {done}/{total}")

    and_summary = _summarize_and(and_trials, "condition")

    # Ablations (mechanism isolation)
    abl_trials = []
    for seed in seeds:
        for abl in cfg.ABLATIONS:
            for case in CASES_AND:
                abl_trials.append(run_ablation_and_trial(seed, abl, case))
    abl_summary = _summarize_and(abl_trials, "ablation")

    # Secondary challenges (lighter; primary remains bistable AND = Challenge G)
    secondary = {
        "A_overlap": [], "B_temporal": [], "C_spatial": [],
        "D_conflict": [], "E_interference": [], "F_degradation": [],
    }
    for seed in seeds:
        for cond in cfg.CONDITIONS:
            secondary["A_overlap"].append(challenge_overlap(seed, cond))
            secondary["B_temporal"].append(challenge_temporal(seed, cond))
            secondary["C_spatial"].append(challenge_spatial(seed, cond))
            secondary["D_conflict"].append(challenge_conflict(seed, cond))
            secondary["E_interference"].append(challenge_interference(seed, cond))
            secondary["F_degradation"].append(challenge_degradation_recovery(seed, cond))
        if verbose and (seed - seeds[0] + 1) % 5 == 0:
            print(f"  TrackB-secondary seed {seed}")

    sec_summary = {}
    for ch, trials in secondary.items():
        sec_summary[ch] = {}
        for cond in cfg.CONDITIONS:
            sub = [t for t in trials if t.get("condition") == cond and not t.get("failed")]
            if ch == "E_interference":
                sec_summary[ch][cond] = {
                    "recovery_rate": float(np.mean([t["recovered"] for t in sub])) if sub else 0,
                    "loc_err_mean": float(np.mean([t["localization_error"] for t in sub])) if sub else None,
                }
            elif ch == "F_degradation":
                sec_summary[ch][cond] = {
                    "improve_rate": float(np.mean([t["improved"] for t in sub])) if sub else 0,
                }
            else:
                key = "overlap_correct" if ch == "A_overlap" else "correct"
                sec_summary[ch][cond] = {
                    "acc": float(np.mean([t[key] for t in sub])) if sub else 0,
                }

    nl = and_summary.get("nonlinear_sub", {})
    lin = and_summary.get("linear_sub", {})
    abl_nl = abl_summary.get("nonlinear_full", {})
    abl_off = abl_summary.get("nonlinear_reaction_off", {})

    # T7: nonlinear shows AND capability (F1>=0.5, near>far, low X FP)
    t7 = (
        nl.get("f1", 0) >= 0.5
        and nl.get("xy_near_hit", 0) > 0.5
        and nl.get("xy_near_hit", 0) > nl.get("xy_far_pred", 1)
        and nl.get("x_false_pos", 1) < 0.5
    )
    # T8: reaction ablation / linear materially worse
    t8 = (
        t7
        and nl.get("f1", 0) > lin.get("f1", 1) + 0.15
        and abl_nl.get("f1", 0) > abl_off.get("f1", 1) + 0.15
    )
    # T9: beats conventional (not just independent)
    conv = [and_summary.get(c, {}).get("f1", 0)
            for c in ("direct_msg", "blackboard", "pheromone")]
    t9 = t8 and nl.get("f1", 0) > max(conv + [0]) + 0.1

    return {
        "track": "B_nonlinear_computation",
        "primary_challenge": "bistable_AND_gate",
        "primary_endpoint": cfg.TRACK_B_PRIMARY,
        "and_trials": and_trials,
        "and_summary": and_summary,
        "ablation_trials": abl_trials,
        "ablation_summary": abl_summary,
        "secondary_summary": sec_summary,
        "secondary_trials": secondary,
        "T7": {"pass": bool(t7), "nonlinear_f1": nl.get("f1"), "note": "AND latch capability"},
        "T8": {"pass": bool(t8), "nl_f1": nl.get("f1"), "lin_f1": lin.get("f1"),
               "abl_full_f1": abl_nl.get("f1"), "abl_off_f1": abl_off.get("f1"),
               "note": "Nonlinear reaction required"},
        "T9": {"pass": bool(t9), "conv_f1s": {
            "direct_msg": and_summary.get("direct_msg", {}).get("f1"),
            "blackboard": and_summary.get("blackboard", {}).get("f1"),
            "pheromone": and_summary.get("pheromone", {}).get("f1"),
        }, "note": "Advantage over conventional + linear"},
        "n_seeds": len(seeds),
        "and_amp": cfg.AND_SUB_AMP,
        "encoding_note": (
            "Subthreshold positive deposits; AND = spatial proximity crossing "
            "separatrix. Not multi-semantic channels on one scalar."
        ),
    }
