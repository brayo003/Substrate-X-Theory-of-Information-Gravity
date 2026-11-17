#!/usr/bin/env python3
"""Analysis for the endogenous-distinguishability execution.

Reads only outputs produced in this workspace; writes the three deliverable
CSVs plus supporting tables and stats.json.
"""
import csv
import json
import math
import os
import sys

import numpy as np
import networkx as nx
from scipy import stats as sps

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, ROOT)
import one  # noqa: E402

N = 12
STEPS = 100
PRIMARY = os.path.join(ROOT, "results", "primary", "experiment_results")
CONTROLS = os.path.join(ROOT, "results", "controls")
OUT = os.path.join(ROOT, "results", "analysis")
os.makedirs(OUT, exist_ok=True)

RNG = np.random.default_rng(20261115)
BOOT = 10000


# ---------------------------------------------------------------- utilities
def load_csv(path):
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def num(v, default=None):
    if v is None or v == "" or v == "None":
        return default
    try:
        return float(v)
    except (TypeError, ValueError):
        return default


def write_csv(name, rows):
    path = os.path.join(OUT, name) if not name.startswith("/") else name
    def clean(v):
        if isinstance(v, float) and not math.isfinite(v):
            return ""
        return v
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        for r in rows:
            w.writerow({k: clean(r.get(k, "")) for k in w.fieldnames})
    return path


def build_graph(edges):
    g = one.TransitionGraph(range(N))
    for a, b in edges:
        g.add_edge(a, b)
    return g


def graph_from_json(s):
    return build_graph([tuple(e) for e in json.loads(s)])


def fresh_gate(row):
    R = graph_from_json(row["final_edges_json"])
    P = one.Partition(range(N), json.loads(row["final_partition"]))
    return one.gate_partition(R, P), R, P


def reach_size(g, z0):
    return len(one.reachable_from(g, z0))


def topology(g, z0):
    n = N
    edges = g.edge_set()
    m = len(edges)
    outd = [sum(1 for a2, _ in edges if a2 == a) for a in range(n)]
    ind = [sum(1 for _, b2 in edges if b2 == a) for a in range(n)]
    H = nx.DiGraph()
    H.add_nodes_from(range(n))
    H.add_edges_from(edges)
    U = nx.Graph(H)
    U.remove_edges_from(list(nx.selfloop_edges(U)))
    wccs = list(nx.connected_components(U))
    largest = max((len(c) for c in wccs), default=0)
    if largest >= 2:
        sub = U.subgraph(max(wccs, key=len))
        avg_path = nx.average_shortest_path_length(sub)
    else:
        avg_path = float("nan")
    return dict(
        n_nodes=n, n_edges=m,
        density=(m / (n * (n - 1))) if n > 1 else float("nan"),
        mean_out_degree=float(np.mean(outd)),
        sd_out_degree=float(np.std(outd, ddof=1)) if n > 1 else 0.0,
        max_out_degree=max(outd),
        mean_in_degree=float(np.mean(ind)),
        sd_in_degree=float(np.std(ind, ddof=1)) if n > 1 else 0.0,
        max_in_degree=max(ind),
        clustering=float(nx.average_clustering(U)) if U.number_of_edges() else 0.0,
        n_weak_components=len(wccs),
        largest_wcc=largest,
        avg_path_length=avg_path,
        reach_from_z0=reach_size(g, z0),
    )


def quotient(g, P):
    pairs = set()
    cross = set()
    for a, b in g.edge_set():
        u, v = P.block_of(a), P.block_of(b)
        pairs.add((u, v))
        if u != v:
            cross.add((u, v))
    nb = P.num_blocks()
    return dict(
        quotient_blocks=nb,
        quotient_distinct_pairs=len(pairs),
        quotient_cross_pairs=len(cross),
        quotient_density=(len(cross) / (nb * (nb - 1))) if nb > 1 else float("nan"),
        consistency_violations=len(one.consistency_violations(g, P)),
    )


def paired_stats(d, rng=RNG, boot=BOOT):
    d = np.asarray([x for x in d if x is not None and np.isfinite(x)], dtype=float)
    n = len(d)
    if n == 0:
        return dict(n=0)
    mean = float(np.mean(d))
    sd = float(np.std(d, ddof=1)) if n > 1 else 0.0
    se = sd / math.sqrt(n) if n else float("nan")
    idx = rng.integers(0, n, size=(boot, n))
    means = d[idx].mean(axis=1)
    lo, hi = np.percentile(means, [2.5, 97.5])
    dz = mean / sd if sd > 0 else float("nan")
    nz = d[d != 0]
    if sd == 0 or len(nz) == 0:
        p = 1.0
    else:
        try:
            if n >= 10:
                p = float(sps.wilcoxon(d, zero_method="wilcox", alternative="two-sided",
                                       method="approx").pvalue)
            else:
                p = float(sps.wilcoxon(d, zero_method="wilcox", alternative="two-sided").pvalue)
        except Exception:
            p = 1.0
    return dict(n=n, mean=mean, sd=sd, se=se, ci_lo=float(lo), ci_hi=float(hi),
                dz=float(dz), median=float(np.median(d)),
                n_nonzero=int(len(nz)), n_pos=int((nz > 0).sum()),
                n_neg=int((nz < 0).sum()), p_raw=p)


def holm(rows, key="p_raw", out="p_holm"):
    order = sorted(range(len(rows)), key=lambda i: rows[i].get(key, 1.0))
    m = len(rows)
    prev = 0.0
    for rank, i in enumerate(order):
        p = rows[i].get(key, 1.0)
        adj = min(1.0, (m - rank) * p)
        prev = max(prev, adj)
        rows[i][out] = prev
    for r in rows:
        r.setdefault(out, 1.0)
    return rows


# ---------------------------------------------------------------- load data
primary = load_csv(os.path.join(PRIMARY, "per_seed_results.csv"))
controls = load_csv(os.path.join(CONTROLS, "control_per_seed.csv"))
primary_steps = load_csv(os.path.join(PRIMARY, "step_traces.csv"))
control_steps = load_csv(os.path.join(CONTROLS, "control_step_traces.csv"))
part_traces = load_csv(os.path.join(PRIMARY, "partition_traces.csv"))
graph_trace = load_csv(os.path.join(PRIMARY, "graph_trace.csv"))

P = {}
for r in primary + controls:
    P.setdefault(r["model"], {})[int(r["seed"])] = r
STEP = {}
for r in primary_steps + control_steps:
    STEP.setdefault((r["model"], int(r["seed"])), {})[int(r["t"])] = r

models = ["A", "B", "G", "H", "C", "D", "CR", "CS", "CT"]

# derived per-run facts
DER = {}
for m in models:
    for s, row in P.get(m, {}).items():
        R = graph_from_json(row["final_edges_json"])
        Pf = one.Partition(range(N), json.loads(row["final_partition"]))
        gate = one.gate_partition(R, Pf)
        z0 = int(row["initial_z"])
        d = dict(row=row)
        d["stored_top"] = topology(R, z0)
        d["gate_top"] = topology(gate, z0)
        d["quot_stored"] = quotient(R, Pf)
        d["quot_gate"] = quotient(gate, Pf)
        d["gate_edges_fresh"] = len(gate)
        d["stored_reach"] = reach_size(R, z0)
        d["gate_reach"] = reach_size(gate, z0)
        d["traj_match"] = tuple(json.loads(row["trajectory"]))
        d["partition_sig"] = tuple(sorted(tuple(sorted(b)) for b in json.loads(row["final_partition"])))
        d["stored_edges"] = frozenset(map(tuple, json.loads(row["final_edges_json"])))
        d["stalled"] = [int(STEP[(m, s)][t]["stalled"]) for t in range(STEPS)]
        first = next((i for i, x in enumerate(d["stalled"]) if x), None)
        d["first_stall"] = first
        d["absorbing_stall"] = bool(first is not None and all(d["stalled"][first:]))
        d["ends_stalled"] = bool(d["stalled"][-1])
        d["n_stalls_calc"] = sum(d["stalled"])
        # source concentration of created edges
        src_total = src_at_z = 0
        for t in range(STEPS):
            zbefore = int(STEP[(m, s)][t]["z_before"])
            for pair in json.loads(STEP[(m, s)][t]["created_set"]):
                src_total += 1
                if pair[0] == zbefore:
                    src_at_z += 1
        d["created_from_z"] = src_at_z
        d["created_total_step"] = src_total
        d["source_fraction"] = (src_at_z / src_total) if src_total else float("nan")
        DER[(m, s)] = d


# ---------------------------------------------------------------- MODEL_COMPARISON.csv
mc_rows = []
for s in range(100):
    row = dict(seed=s)
    for m in ("A", "B", "G", "H", "C"):
        d = DER[(m, s)]
        row[f"{m}_distinct_states"] = int(d["row"]["distinct_states"])
        row[f"{m}_n_traversed"] = int(d["row"]["n_traversed"])
        row[f"{m}_n_stalls"] = d["n_stalls_calc"]
        row[f"{m}_ends_stalled"] = int(d["ends_stalled"])
        row[f"{m}_absorbing_stall"] = int(d["absorbing_stall"])
        row[f"{m}_final_blocks"] = int(d["row"]["final_blocks"])
        row[f"{m}_final_edges"] = int(d["row"]["final_edges"])
        row[f"{m}_final_gate_edges"] = d["gate_edges_fresh"]
        row[f"{m}_stored_reach"] = d["stored_reach"]
        row[f"{m}_gate_reach"] = d["gate_reach"]
        row[f"{m}_partition_stable_at"] = int(d["row"]["partition_stable_at"])
        row[f"{m}_total_splits"] = int(d["row"]["total_splits"])
        row[f"{m}_clustering"] = d["stored_top"]["clustering"]
        row[f"{m}_avg_path_length"] = d["stored_top"]["avg_path_length"]
    for metric in ("distinct_states", "n_traversed", "n_stalls", "final_blocks",
                   "final_gate_edges", "stored_reach", "gate_reach", "total_splits"):
        def gv(m):
            d = DER[(m, s)]
            if metric == "final_gate_edges":
                return d["gate_edges_fresh"]
            if metric == "stored_reach":
                return d["stored_reach"]
            if metric == "gate_reach":
                return d["gate_reach"]
            if metric == "n_stalls":
                return d["n_stalls_calc"]
            return float(d["row"][metric])
        row[f"DiD_CB_GA_{metric}"] = (gv("C") - gv("B")) - (gv("G") - gv("A"))
        row[f"C_minus_B_{metric}"] = gv("C") - gv("B")
        row[f"C_minus_H_{metric}"] = gv("C") - gv("H")
    mc_rows.append(row)
write_csv(os.path.join(ROOT, "MODEL_COMPARISON.csv"), mc_rows)


# ---------------------------------------------------------------- D_CR_RESULTS.csv
dcr_rows = []
for s in range(100):
    d, c = DER[("D", s)], DER[("CR", s)]
    cs = DER.get(("CS", s))
    ct = DER.get(("CT", s))
    row = dict(
        seed=s,
        d_created=int(float(d["row"]["total_created_raw"])),
        cr_created=int(float(c["row"]["total_created_raw"])),
        created_match=int(d["row"]["total_created_raw"] == c["row"]["total_created_raw"]),
        d_removed=int(float(d["row"]["total_removed_raw"])),
        cr_removed=int(float(c["row"]["total_removed_raw"])),
        d_final_edges=int(d["row"]["final_edges"]),
        cr_final_edges=int(c["row"]["final_edges"]),
        d_traversed_created=int(d["row"]["created_ever_effective"]),
        cr_traversed_created=int(c["row"]["created_ever_effective"]),
        final_graph_same=int(d["stored_edges"] == c["stored_edges"]),
        trajectory_same=int(d["traj_match"] == c["traj_match"]),
        final_partition_same=int(d["partition_sig"] == c["partition_sig"]),
        stored_reach_same=int(d["stored_reach"] == c["stored_reach"]),
        gate_reach_same_fresh=int(d["gate_reach"] == c["gate_reach"]),
        gate_reach_same_as_reported=int(
            reach_size(graph_from_json(d["row"]["final_gate_edges_json"]), int(d["row"]["initial_z"]))
            == reach_size(graph_from_json(c["row"]["final_gate_edges_json"]), int(c["row"]["initial_z"]))),
        d_gate_edges_fresh=d["gate_edges_fresh"],
        cr_gate_edges=c["gate_edges_fresh"],
        d_partition_stable_at=int(d["row"]["partition_stable_at"]),
        cr_partition_stable_at=int(c["row"]["partition_stable_at"]),
        d_graph_stable_at=int(d["row"]["graph_stable_at"]),
        cr_graph_stable_at=int(c["row"]["graph_stable_at"]),
        d_density=d["stored_top"]["density"],
        cr_density=c["stored_top"]["density"],
        d_clustering=d["stored_top"]["clustering"],
        cr_clustering=c["stored_top"]["clustering"],
        d_components=d["stored_top"]["n_weak_components"],
        cr_components=c["stored_top"]["n_weak_components"],
        d_largest_wcc=d["stored_top"]["largest_wcc"],
        cr_largest_wcc=c["stored_top"]["largest_wcc"],
        d_avg_path=d["stored_top"]["avg_path_length"],
        cr_avg_path=c["stored_top"]["avg_path_length"],
        d_source_fraction=d["source_fraction"],
        cr_source_fraction=c["source_fraction"],
        cs_feasible=int(cs is not None),
        ct_feasible=int(ct is not None),
        cs_created=(int(float(cs["row"]["total_created_raw"])) if cs else ""),
        ct_created=(int(float(ct["row"]["total_created_raw"])) if ct else ""),
        cs_final_graph_same=(int(cs["stored_edges"] == d["stored_edges"]) if cs else ""),
        ct_final_graph_same=(int(ct["stored_edges"] == d["stored_edges"]) if ct else ""),
        cs_trajectory_same=(int(cs["traj_match"] == d["traj_match"]) if cs else ""),
        ct_trajectory_same=(int(ct["traj_match"] == d["traj_match"]) if ct else ""),
    )
    dcr_rows.append(row)
write_csv(os.path.join(ROOT, "D_CR_RESULTS.csv"), dcr_rows)


# ---------------------------------------------------------------- STRUCTURAL_METRICS.csv
sm_rows = []
for m in models:
    for s in sorted(P.get(m, {})):
        d = DER[(m, s)]
        for space in ("stored", "gate"):
            top = d[f"{space}_top"]
            q = d[f"quot_{space}"]
            row = dict(model=m, seed=s, space=space, initial_z=int(d["row"]["initial_z"]))
            row.update(top)
            row.update(q)
            row["final_blocks"] = int(d["row"]["final_blocks"])
            row["final_gate_edges_fresh"] = d["gate_edges_fresh"]
            row["partition_stable_at"] = int(d["row"]["partition_stable_at"])
            row["graph_stable_at"] = int(d["row"]["graph_stable_at"])
            row["combined_stable_at"] = int(d["row"]["combined_stable_at"])
            row["graph_stable_censored"] = int(int(d["row"]["graph_stable_at"]) >= STEPS)
            row["created_ever_effective"] = int(d["row"]["created_ever_effective"])
            row["source_fraction_created"] = d["source_fraction"]
            sm_rows.append(row)
write_csv(os.path.join(ROOT, "STRUCTURAL_METRICS.csv"), sm_rows)


# ---------------------------------------------------------------- claim reproduction
def mean_of(m, key, derive=None):
    vals = []
    for s in sorted(P.get(m, {})):
        d = DER[(m, s)]
        if derive:
            vals.append(derive(d))
        else:
            v = num(d["row"].get(key))
            if v is not None:
                vals.append(v)
    return float(np.mean(vals)) if vals else float("nan")


claims = [
    ("D mean created edges", 612.13, mean_of("D", "total_created_raw")),
    ("CR mean created edges", 612.13, mean_of("CR", "total_created_raw")),
    ("D mean created edges ever traversed", 16.67, mean_of("D", "created_ever_effective")),
    ("CR mean created edges ever traversed", 35.87, mean_of("CR", "created_ever_effective")),
    ("D mean final edges", None, mean_of("D", "final_edges")),
    ("CR mean final edges", None, mean_of("CR", "final_edges")),
    ("D mean partition stable at", None, mean_of("D", "partition_stable_at")),
    ("D mean graph stable at", None, mean_of("D", "graph_stable_at")),
    ("CR mean partition stable at", None, mean_of("CR", "partition_stable_at")),
    ("CR mean graph stable at", None, mean_of("CR", "graph_stable_at")),
]
claim_rows = []
for name, claimed, observed in claims:
    claim_rows.append(dict(claim=name, claimed=("" if claimed is None else claimed),
                           observed=round(observed, 4),
                           reproduced=("" if claimed is None else
                                       int(abs(round(observed, 2) - claimed) < 0.005))))
write_csv("claim_reproduction.csv", claim_rows)

exact_rows = []
def add_exact(name, count, denom, note=""):
    exact_rows.append(dict(check=name, count=count, denominator=denom, note=note))

add_exact("D.CR per-seed created counts equal", sum(r["created_match"] for r in dcr_rows), 100,
          "matched by construction: CR receives D's per-step counts")
add_exact("D/CR final graph identical", sum(r["final_graph_same"] for r in dcr_rows), 100,
          "different placement rules with equal counts cannot share a graph")
add_exact("D/CR trajectory identical", sum(r["trajectory_same"] for r in dcr_rows), 100,
          "different graphs change admissible moves")
add_exact("D/CR final partition identical", sum(r["final_partition_same"] for r in dcr_rows), 100,
          "no partition difference in 100/100")
add_exact("D/CR stored reach identical", sum(r["stored_reach_same"] for r in dcr_rows), 100, "")
add_exact("D/CR gate reach identical (fresh gate)", sum(r["gate_reach_same_fresh"] for r in dcr_rows), 100,
          "corrected: gate recomputed from final graph and partition")
add_exact("D/CR gate reach identical (as reported by one.py)", sum(r["gate_reach_same_as_reported"] for r in dcr_rows), 100,
          "one.py stores D's pre-final gate; stale for D")
add_exact("CS feasible seeds", sum(r["cs_feasible"] for r in dcr_rows), 100,
          "source+count matched control")
add_exact("CT feasible seeds", sum(r["ct_feasible"] for r in dcr_rows), 100,
          "count+quotient-topology matched control")
csn = sum(r["cs_feasible"] for r in dcr_rows)
ctn = sum(r["ct_feasible"] for r in dcr_rows)
add_exact("CS completed runs with same final graph as D", sum(r["cs_final_graph_same"] for r in dcr_rows if r["cs_feasible"]), csn, "")
add_exact("CT completed runs with same final graph as D", sum(r["ct_final_graph_same"] for r in dcr_rows if r["ct_feasible"]), ctn, "")
add_exact("CS completed runs with same trajectory as D", sum(r["cs_trajectory_same"] for r in dcr_rows if r["cs_feasible"]), csn, "")
add_exact("CT completed runs with same trajectory as D", sum(r["ct_trajectory_same"] for r in dcr_rows if r["ct_feasible"]), ctn, "")
add_exact("C runs ending stalled", sum(DER[("C", s)]["ends_stalled"] for s in range(100)), 100, "")
add_exact("C runs with absorbing stall", sum(DER[("C", s)]["absorbing_stall"] for s in range(100)), 100, "")
add_exact("G runs ending stalled", sum(DER[("G", s)]["ends_stalled"] for s in range(100)), 100, "")
add_exact("G runs with absorbing stall", sum(DER[("G", s)]["absorbing_stall"] for s in range(100)), 100, "")
add_exact("H final partition identical to C", sum(DER[("H", s)]["partition_sig"] == DER[("C", s)]["partition_sig"] for s in range(100)), 100, "")
add_exact("H trajectory identical to C", sum(DER[("H", s)]["traj_match"] == DER[("C", s)]["traj_match"] for s in range(100)), 100, "")
add_exact("H gate reach identical to C", sum(DER[("H", s)]["gate_reach"] == DER[("C", s)]["gate_reach"] for s in range(100)), 100, "")
write_csv("exact_counts.csv", exact_rows)


# ---------------------------------------------------------------- censoring / stabilization
cen_rows = []
for m in models:
    ss = sorted(P.get(m, {}))
    if not ss:
        continue
    ps = [int(DER[(m, s)]["row"]["partition_stable_at"]) for s in ss]
    gs = [int(DER[(m, s)]["row"]["graph_stable_at"]) for s in ss]
    cen_rows.append(dict(
        model=m, n=len(ss),
        partition_stable_mean=round(float(np.mean(ps)), 3),
        partition_stable_max=max(ps),
        partition_stable_within_4=sum(p <= 4 for p in ps),
        graph_stable_mean=round(float(np.mean(gs)), 3),
        graph_stable_censored=sum(g >= STEPS for g in gs),
        graph_stable_censored_fraction=round(sum(g >= STEPS for g in gs) / len(gs), 3),
        final_blocks_mean=round(float(np.mean([int(DER[(m, s)]["row"]["final_blocks"]) for s in ss])), 3),
        final_blocks_12=sum(int(DER[(m, s)]["row"]["final_blocks"]) == N for s in ss),
        final_gate_equals_stored_minus_selfloops=sum(
            DER[(m, s)]["gate_edges_fresh"] ==
            len([e for e in DER[(m, s)]["stored_edges"] if e[0] != e[1]]) for s in ss),
    ))
write_csv("stabilization.csv", cen_rows)


# ---------------------------------------------------------------- degeneracy of D placement
forced_steps = total_steps = 0
extra_pool_sizes = []
# reconstruct R_t from graph_trace (t=-1 initial, t>=0 post-step), per model
gt = {}
for r in graph_trace:
    gt.setdefault((r["model"], int(r["seed"])), {})[int(r["t"])] = frozenset(
        tuple(e) for e in json.loads(r["graph_signature"]))
pt = {}
for r in part_traces:
    if r["model"] == "D":
        pt.setdefault(int(r["seed"]), {})[int(r["t"])] = one.Partition(
            range(N), json.loads(r["partition"]))
for s in range(100):
    for t in range(STEPS):
        R = build_graph(sorted(gt[("D", s)][t - 1]))
        z = int(STEP[("D", s)][t]["z_before"])
        Pn = pt[s][t]
        C = one.generate_candidates(z, R, Pn)
        pool_z = {(z, b) for b in Pn.states()
                  if b != z and not Pn.equivalent(z, b) and not R.has_edge(z, b)}
        total_steps += 1
        if C == pool_z:
            forced_steps += 1
        extra_pool_sizes.append(len(pool_z) - len(C))
deg_rows = [dict(
    metric="D steps where candidate set equals source cross-block pool",
    value=forced_steps, denominator=total_steps,
    fraction=round(forced_steps / total_steps, 6),
    note="matching source+count leaves no placement freedom on these steps"),
    dict(metric="mean extra pool edges per D step", value=round(float(np.mean(extra_pool_sizes)), 4),
         denominator=total_steps, fraction="", note="|pool_z|-|C_t|"),
    dict(metric="D created edges sourced at z", value=round(float(np.mean([DER[("D", s)]["source_fraction"] for s in range(100)])), 6),
         denominator=100, fraction="", note="fraction of created edges with source = current state"),
    dict(metric="CR created edges sourced at z", value=round(float(np.mean([DER[("CR", s)]["source_fraction"] for s in range(100)])), 6),
         denominator=100, fraction="", note="same fraction for the count-matched random control"),
]
write_csv("degeneracy.csv", deg_rows)


# ---------------------------------------------------------------- statistics
def metric(m, s, key):
    d = DER[(m, s)]
    if key == "n_stalls":
        return float(d["n_stalls_calc"])
    if key == "final_gate_edges":
        return float(d["gate_edges_fresh"])
    if key == "stored_reach":
        return float(d["stored_reach"])
    if key == "gate_reach":
        return float(d["gate_reach"])
    return float(d["row"][key])


interaction_metrics = ["distinct_states", "n_traversed", "n_stalls", "final_blocks",
                       "final_gate_edges", "stored_reach", "gate_reach", "total_splits"]
irows = []
for k in interaction_metrics:
    d = [(metric("C", s, k) - metric("B", s, k)) - (metric("G", s, k) - metric("A", s, k))
         for s in range(100)]
    st = paired_stats(d)
    st.update(metric=k, contrast="DiD=(C-B)-(G-A)")
    irows.append(st)
holm(irows)
write_csv("table_interaction.csv", irows)

dec_rows = []
for k in interaction_metrics:
    for a, b in (("C", "B"), ("G", "A"), ("C", "G"), ("C", "A"), ("C", "H"), ("H", "B")):
        d = [metric(a, s, k) - metric(b, s, k) for s in range(100)]
        st = paired_stats(d)
        st.update(metric=k, contrast=f"{a}-{b}")
        dec_rows.append(st)
holm(dec_rows)
write_csv("table_decomposition.csv", dec_rows)

dcr_metrics = ["final_edges", "total_removed_raw", "created_ever_effective",
               "graph_stable_at", "partition_stable_at", "distinct_states",
               "stored_reach", "gate_reach", "final_gate_edges"]
drows = []
for k in dcr_metrics:
    d = [metric("D", s, k) - metric("CR", s, k) for s in range(100)]
    st = paired_stats(d)
    st.update(metric=k, contrast="D-CR")
    drows.append(st)
holm(drows)
write_csv("table_dcr.csv", drows)

# H-vs-C family (coupling of refinement input)
hrows = []
for k in ["distinct_states", "n_traversed", "n_stalls", "final_blocks",
          "final_gate_edges", "stored_reach", "gate_reach", "total_splits"]:
    d = [metric("C", s, k) - metric("H", s, k) for s in range(100)]
    st = paired_stats(d)
    st.update(metric=k, contrast="C-H")
    hrows.append(st)
holm(hrows)
write_csv("table_coupling_isolation.csv", hrows)

# ---------------------------------------------------------------- topology tables
TOPO_METRICS = ["density", "mean_out_degree", "sd_out_degree", "max_out_degree",
                "clustering", "n_weak_components", "largest_wcc",
                "avg_path_length", "quotient_cross_pairs", "quotient_density",
                "consistency_violations", "reach_from_z0"]
topo_rows = []
for m in models:
    ss = sorted(P.get(m, {}))
    if not ss:
        continue
    for space in ("stored", "gate"):
        for k in TOPO_METRICS:
            vals = [DER[(m, s)][f"{space}_top" if k in
                                ("density", "mean_out_degree", "sd_out_degree",
                                 "max_out_degree", "clustering", "n_weak_components",
                                 "largest_wcc", "avg_path_length", "reach_from_z0")
                                else f"quot_{space}"][k] for s in ss]
            vals = [v for v in vals if v is not None and np.isfinite(v)]
            topo_rows.append(dict(model=m, space=space, metric=k, n=len(vals),
                                  mean=round(float(np.mean(vals)), 6),
                                  sd=round(float(np.std(vals, ddof=1)), 6)))
write_csv("table_topology_means.csv", topo_rows)

td_rows = []
for space in ("stored", "gate"):
    for k in TOPO_METRICS:
        def tv(m, s):
            src = DER[(m, s)][f"{space}_top" if k in
                              ("density", "mean_out_degree", "sd_out_degree",
                               "max_out_degree", "clustering", "n_weak_components",
                               "largest_wcc", "avg_path_length", "reach_from_z0")
                              else f"quot_{space}"]
            return float(src[k])
        d = [tv("D", s) - tv("CR", s) for s in range(100)]
        st = paired_stats(d)
        st.update(space=space, metric=k, contrast="D-CR")
        td_rows.append(st)
holm(td_rows)
write_csv("table_topology_dcr.csv", td_rows)

# D vs feasible source/topology-matched controls (same topology metrics)
tc_rows = []
for ctrl in ("CS", "CT"):
    ss = [s for s in range(100) if s in P.get(ctrl, {})]
    for k in ["sd_out_degree", "max_out_degree", "clustering", "n_weak_components",
              "largest_wcc", "avg_path_length", "density", "created_ever_effective",
              "final_edges"]:
        def cv(m, s):
            if k == "created_ever_effective":
                return float(DER[(m, s)]["row"]["created_ever_effective"])
            if k == "final_edges":
                return float(DER[(m, s)]["row"]["final_edges"])
            return float(DER[(m, s)]["stored_top"][k])
        d = [cv("D", s) - cv(ctrl, s) for s in ss]
        st = paired_stats(d)
        st.update(space="stored", metric=k, contrast=f"D-{ctrl}",
                  n_seeds_feasible=len(ss))
        tc_rows.append(st)
holm(tc_rows)
write_csv("table_topology_d_controls.csv", tc_rows)

summary = dict(
    interaction=irows, decomposition=dec_rows, dcr=drows, coupling_isolation=hrows,
    topology_dcr=td_rows, topology_d_controls=tc_rows,
    exact_counts=exact_rows, claims=claim_rows, stabilization=cen_rows,
    degeneracy=deg_rows,
)
with open(os.path.join(OUT, "stats.json"), "w", encoding="utf-8") as f:
    json.dump(summary, f, indent=2, default=str)

print("wrote deliverables and supporting tables to", OUT)
print("interaction:")
for r in irows:
    print(f"  {r['metric']:<20} DiD={r['mean']:9.3f} CI=[{r['ci_lo']:8.3f},{r['ci_hi']:8.3f}] "
          f"dz={r['dz']:7.3f} p={r['p_raw']:.2e} holm={r['p_holm']:.2e}")
print("D-CR:")
for r in drows:
    print(f"  {r['metric']:<24} diff={r['mean']:9.3f} CI=[{r['ci_lo']:8.3f},{r['ci_hi']:8.3f}] "
          f"dz={r['dz']:7.3f} p={r['p_raw']:.2e} holm={r['p_holm']:.2e}")
print("C-H:")
for r in hrows:
    print(f"  {r['metric']:<24} diff={r['mean']:9.3f} CI=[{r['ci_lo']:8.3f},{r['ci_hi']:8.3f}] "
          f"dz={r['dz']:7.3f} p={r['p_raw']:.2e} holm={r['p_holm']:.2e}")
