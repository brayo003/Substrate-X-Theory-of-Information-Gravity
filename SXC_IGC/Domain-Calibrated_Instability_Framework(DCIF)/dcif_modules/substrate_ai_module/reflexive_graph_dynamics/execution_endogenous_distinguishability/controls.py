#!/usr/bin/env python3
"""Additional controls for the endogenous-distinguishability experiment.

Uses one.py unmodified.  See CONTROL_DEFINITIONS.md for the pre-registered
definitions of models G, CS and CT.

Writes:
  results/controls/control_per_seed.csv
  results/controls/control_step_traces.csv
  results/controls/control_divergence.json
"""
import argparse
import csv
import json
import os
import random
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import one  # noqa: E402

OUT = os.path.join(HERE, "results", "controls")
REMOVAL_AGE = 5


class ControlMatchingFailure(RuntimeError):
    pass


def run_model_h(R_full, P0, z0, steps, uniforms, seed):
    """Gating on, refinement on, but refinement decoupled from the gate."""
    P = P0.copy()
    z = z0
    rec = one.RunResult("H", seed, initial_partition=P0.copy(),
                        initial_graph=R_full.copy(),
                        initial_blocks=P0.num_blocks(),
                        initial_edges=len(R_full), initial_z=z0)
    rec.partition_signatures = [P.signature()]
    rec.graph_signatures = [R_full.signature()]
    for t in range(steps):
        z_before = z
        z_after, traversed = one.apply_movement(
            uniforms[t], one.gate_successors(z_before, R_full, P), z_before)
        gate = one.gate_partition(R_full, P)
        new_P, n_splits = one.refine_once(R_full, P)
        new_gate = one.gate_partition(R_full, new_P)
        viol = len(one.consistency_violations(new_gate, new_P))
        rec.records.append(one.StepRecord(
            t=t, z_before=z_before, z_after=z_after,
            block_count=new_P.num_blocks(),
            partition_blocks=one._serialize_partition(new_P),
            graph_signature=R_full.signature(),
            gate_edge_count=len(new_gate),
            admissible_edge_count=len(R_full),
            created_edges_raw=0, removed_edges_raw=0, net_change=0,
            consistency_violations=viol, splits_this_step=n_splits,
            traversed=traversed, stalled=not traversed))
        P = new_P
        rec.partition_signatures.append(P.signature())
        rec.graph_signatures.append(R_full.signature())
        z = z_after
    return one._finalize_run(rec, z0, P, R_full.copy(),
                             one.gate_partition(R_full, P),
                             set(), set(), set())


def run_model_g(R_full, P0, z0, steps, uniforms, seed):
    """Gating on, refinement off, graph fixed."""
    P = P0.copy()
    z = z0
    rec = one.RunResult("G", seed, initial_partition=P0.copy(),
                        initial_graph=R_full.copy(),
                        initial_blocks=P0.num_blocks(),
                        initial_edges=len(R_full), initial_z=z0)
    rec.partition_signatures = [P.signature()]
    rec.graph_signatures = [R_full.signature()]
    for t in range(steps):
        z_before = z
        z_after, traversed = one.apply_movement(
            uniforms[t], one.gate_successors(z_before, R_full, P), z_before)
        gate = one.gate_partition(R_full, P)
        viol = len(one.consistency_violations(gate, P))
        rec.records.append(one.StepRecord(
            t=t, z_before=z_before, z_after=z_after,
            block_count=P.num_blocks(),
            partition_blocks=one._serialize_partition(P),
            graph_signature=R_full.signature(),
            gate_edge_count=len(gate),
            admissible_edge_count=len(R_full),
            created_edges_raw=0, removed_edges_raw=0, net_change=0,
            consistency_violations=viol, splits_this_step=0,
            traversed=traversed, stalled=not traversed))
        rec.partition_signatures.append(P.signature())
        rec.graph_signatures.append(R_full.signature())
        z = z_after
    return one._finalize_run(rec, z0, P, R_full.copy(),
                             one.gate_partition(R_full, P),
                             set(), set(), set())


def run_matched(R_full, P0, z0, steps, uniforms, seed, d_records, mode,
                removal_age=REMOVAL_AGE):
    """D's loop with a matched random placement rule (mode 'CS' or 'CT')."""
    if mode not in ("CS", "CT"):
        raise ValueError(mode)
    rng = random.Random(seed * 1_000_000 + (11 if mode == "CS" else 12))
    P = P0.copy()
    R = R_full.copy()
    R0_edges = R_full.edge_set()
    z = z0
    rec = one.RunResult(mode, seed, initial_partition=P0.copy(),
                        initial_graph=R_full.copy(),
                        initial_blocks=P0.num_blocks(),
                        initial_edges=len(R_full), initial_z=z0)
    rec.partition_signatures = [P.signature()]
    rec.graph_signatures = [R.signature()]
    active_ages = {}
    created_all, ever_traversed, affecting = set(), set(), set()
    augmented_keys = [one._augmented_key(z, P, R, active_ages, 0, removal_age)]

    for t in range(steps):
        s_g = one.gate_successors(z, R, P)
        z_after, traversed = one.apply_movement(uniforms[t], s_g, z)
        if traversed:
            e_trav = (z, z_after)
            ever_traversed.add(e_trav)
            if e_trav not in R0_edges:
                active_ages[e_trav] = t
        gate = one.gate_partition(R, P)
        new_P, n_splits = one.refine_once(gate, P)
        n_create = int(d_records[t].created_edges_raw)

        if mode == "CS":
            pool_z = [(z, b) for b in new_P.states()
                      if b != z and not new_P.equivalent(z, b)
                      and not R.has_edge(z, b)]
            if len(pool_z) < n_create:
                raise ControlMatchingFailure(
                    f"seed={seed} t={t}: source pool too small "
                    f"({n_create} > {len(pool_z)})")
            created = set(rng.sample(sorted(pool_z), n_create)) if n_create else set()
            pool_size = len(pool_z)
        else:  # CT
            counts = {}
            for e in d_records[t].created_set:
                key = (new_P.block_of(e[0]), new_P.block_of(e[1]))
                counts[key] = counts.get(key, 0) + 1
            pool = one.creation_pool(R, new_P)
            groups = {}
            for e in pool:
                key = (new_P.block_of(e[0]), new_P.block_of(e[1]))
                groups.setdefault(key, []).append(e)
            created = set()
            for key, k in sorted(counts.items()):
                elig = groups.get(key, [])
                if len(elig) < k:
                    raise ControlMatchingFailure(
                        f"seed={seed} t={t}: block-pair {key} too small "
                        f"({k} > {len(elig)})")
                created |= set(rng.sample(sorted(elig), k))
            pool_size = len(pool)

        removed = set()
        for e in R.edge_set():
            if e in R0_edges:
                continue
            if e == (z, z_after):
                continue
            if e not in active_ages:
                raise RuntimeError(f"active dynamic edge {e} missing metadata")
            if t - active_ages[e] >= removal_age:
                removed.add(e)
        new_R = R.copy()
        for e in created:
            new_R.add_edge(*e)
        for e in removed:
            new_R.remove_edge(*e)
        assert new_R.edge_set() == (R.edge_set() | created) - removed
        for e in removed:
            active_ages.pop(e, None)
        for e in created:
            active_ages[e] = t
        if traversed and (z, z_after) not in R0_edges:
            active_ages[(z, z_after)] = t
        created_all |= created
        for e in created:
            if e not in affecting and e in new_R.edge_set() and \
                    one.edge_affects_refinement(
                        e, one.gate_partition(new_R, new_P), new_P):
                affecting.add(e)
        new_gate = one.gate_partition(new_R, new_P)
        viol = len(one.consistency_violations(new_gate, new_P))
        ages_sig = tuple(sorted((e, min((t + 1) - ts, removal_age))
                                for e, ts in active_ages.items()))
        akey = one._augmented_key(z_after, new_P, new_R, active_ages,
                                  t + 1, removal_age)
        rec.records.append(one.StepRecord(
            t=t, z_before=z, z_after=z_after,
            block_count=new_P.num_blocks(),
            partition_blocks=one._serialize_partition(new_P),
            graph_signature=new_R.signature(),
            gate_edge_count=len(new_gate),
            admissible_edge_count=len(new_R),
            created_edges_raw=len(created), removed_edges_raw=len(removed),
            net_change=len(new_R) - len(R),
            consistency_violations=viol, splits_this_step=n_splits,
            traversed=traversed, stalled=not traversed,
            created_set=tuple(sorted(created)),
            removed_set=tuple(sorted(removed)),
            requested_create=n_create, creation_pool_size=pool_size,
            ages_signature=ages_sig, augmented_key=akey,
            candidates_pre_cap=n_create, candidates_post_cap=n_create,
            cap_saturated=False,
            unique_target_blocks=len({new_P.block_of(b) for (_, b) in created})))
        P = new_P
        R = new_R
        z = z_after
        rec.partition_signatures.append(P.signature())
        rec.graph_signatures.append(R.signature())
        augmented_keys.append(akey)

    rec.full_augmented_recurrence = one._full_recurrence(augmented_keys)
    return one._finalize_run(rec, z0, P, R,
                             one.gate_partition(R, P),
                             created_all, ever_traversed, affecting)


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--seeds", type=int, default=100)
    ap.add_argument("--steps", type=int, default=100)
    ap.add_argument("--n", type=int, default=12)
    ap.add_argument("--edge-prob", type=float, default=0.25)
    ap.add_argument("--initial-blocks", type=int, default=3)
    args = ap.parse_args(argv)

    os.makedirs(OUT, exist_ok=True)
    per_seed, step_rows = [], []
    divergence = {"n_seeds": args.seeds, "n_excluded": 0,
                  "G_trajectory_differs_from_A": 0,
                  "C_trajectory_differs_from_B": 0,
                  "C_trajectory_differs_from_G": 0,
                  "CS_created_mismatch": 0, "CT_created_mismatch": 0,
                  "CS_final_graph_differs_from_D": 0,
                  "CT_final_graph_differs_from_D": 0,
                  "CS_trajectory_differs_from_D": 0,
                  "CT_trajectory_differs_from_D": 0,
                  "H_trajectory_differs_from_C": 0,
                  "H_final_partition_differs_from_C": 0,
                  "H_final_gate_reach_differs_from_C": 0}

    for seed in range(args.seeds):
        R, P0 = one.generate_instance(seed, args.n, args.edge_prob,
                                      args.initial_blocks)
        z0 = seed % args.n
        uniforms = one.pre_draw_uniforms(seed, args.steps)
        rA = one.run_model_a(R, P0, z0, args.steps, uniforms, seed)
        rB = one.run_model_b(R, P0, z0, args.steps, uniforms, seed)
        rG = run_model_g(R, P0, z0, args.steps, uniforms, seed)
        rC = one.run_model_c(R, P0, z0, args.steps, uniforms, seed)
        rH = run_model_h(R, P0, z0, args.steps, uniforms, seed)
        rD = one.run_model_d(R, P0, z0, args.steps, uniforms, seed,
                             cap_per_source=None, removal_age=REMOVAL_AGE)
        runs = [rA, rB, rG, rH, rC, rD]
        try:
            rCS = run_matched(R, P0, z0, args.steps, uniforms, seed,
                              rD.records, "CS")
            runs.append(rCS)
        except ControlMatchingFailure as exc:
            divergence["n_excluded"] += 1
            print(" ", exc)
            rCS = None
        try:
            rCT = run_matched(R, P0, z0, args.steps, uniforms, seed,
                              rD.records, "CT")
            runs.append(rCT)
        except ControlMatchingFailure as exc:
            divergence["n_excluded"] += 1
            print(" ", exc)
            rCT = None

        for r in runs:
            per_seed.append(one._result_row(r))
            for s in r.records:
                step_rows.append(dict(
                    model=r.model, seed=r.seed, t=s.t,
                    z_before=s.z_before, z_after=s.z_after,
                    block_count=s.block_count,
                    gate_edge_count=s.gate_edge_count,
                    admissible_edge_count=s.admissible_edge_count,
                    created_raw=s.created_edges_raw,
                    removed_raw=s.removed_edges_raw,
                    net_change=s.net_change,
                    consistency_violations=s.consistency_violations,
                    splits=s.splits_this_step,
                    traversed=int(s.traversed), stalled=int(s.stalled),
                    created_set=json.dumps([list(e) for e in s.created_set])))

        if [x.z_after for x in rG.records] != [x.z_after for x in rA.records]:
            divergence["G_trajectory_differs_from_A"] += 1
        if [x.z_after for x in rC.records] != [x.z_after for x in rB.records]:
            divergence["C_trajectory_differs_from_B"] += 1
        if [x.z_after for x in rC.records] != [x.z_after for x in rG.records]:
            divergence["C_trajectory_differs_from_G"] += 1
        if [x.z_after for x in rH.records] != [x.z_after for x in rC.records]:
            divergence["H_trajectory_differs_from_C"] += 1
        if rH.final_partition.signature() != rC.final_partition.signature():
            divergence["H_final_partition_differs_from_C"] += 1
        if one.reachable_from(rH.final_gate, z0) != one.reachable_from(rC.final_gate, z0):
            divergence["H_final_gate_reach_differs_from_C"] += 1
        if rCS is not None:
            if sum(x.created_edges_raw for x in rCS.records) != \
                    sum(x.created_edges_raw for x in rD.records):
                divergence["CS_created_mismatch"] += 1
            if rCS.final_graph.edge_set() != rD.final_graph.edge_set():
                divergence["CS_final_graph_differs_from_D"] += 1
            if [x.z_after for x in rCS.records] != [x.z_after for x in rD.records]:
                divergence["CS_trajectory_differs_from_D"] += 1
        if rCT is not None:
            if sum(x.created_edges_raw for x in rCT.records) != \
                    sum(x.created_edges_raw for x in rD.records):
                divergence["CT_created_mismatch"] += 1
            if rCT.final_graph.edge_set() != rD.final_graph.edge_set():
                divergence["CT_final_graph_differs_from_D"] += 1
            if [x.z_after for x in rCT.records] != [x.z_after for x in rD.records]:
                divergence["CT_trajectory_differs_from_D"] += 1

    with open(os.path.join(OUT, "control_per_seed.csv"), "w", newline="",
              encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(per_seed[0].keys()))
        w.writeheader()
        for r in per_seed:
            w.writerow({k: r.get(k, "") for k in w.fieldnames})
    with open(os.path.join(OUT, "control_step_traces.csv"), "w", newline="",
              encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(step_rows[0].keys()))
        w.writeheader()
        for r in step_rows:
            w.writerow({k: r.get(k, "") for k in w.fieldnames})
    with open(os.path.join(OUT, "control_divergence.json"), "w",
              encoding="utf-8") as f:
        json.dump(divergence, f, indent=2, default=str)
    print(json.dumps(divergence, indent=2, default=str))
    return 0


if __name__ == "__main__":
    sys.exit(main())
