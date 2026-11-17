"""Correctness tests for the evidence integration benchmark (v2)."""

from __future__ import annotations

import inspect
import os
import sys
import traceback
from typing import Any, Dict

from .conditions import SMOKE_CONDITION, NONINFERIORITY_MARGIN_FRAC_CORRECT
from .evidence import (
    EvidenceBundle,
    EvidenceItem,
    NetworkEvidenceView,
    empirical_pairwise_bit_correlation,
    generate_evidence,
    relabel_evidence,
)
from .evaluator import attribute_edges, evaluate_protocol
from .graph_bridge import (
    make_mv_u_timeline,
    make_mv_w_timeline,
    make_static_directed_timeline,
    relabel_graph,
    run_all_models,
    verify_d_cr_creation_match,
)
from .metrics import noninferiority_test, tost_equivalence
from .protocol import (
    agreement_from_decisions,
    decide_from_known,
    decide_unweighted_majority,
    run_protocol,
)
from .streams import (
    EVIDENCE_OFFSET,
    FAILURE_OFFSET,
    RELABEL_OFFSET,
    evidence_rng,
    failure_stream_seed,
    relabel_rng,
)

_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)
import one as substrate


class TestFailure(AssertionError):
    pass


def _check(cond: bool, msg: str) -> None:
    if not cond:
        raise TestFailure(msg)


def test_no_double_count():
    nodes = list(range(4))
    R = substrate.TransitionGraph(nodes)
    for i in nodes:
        R.add_edge(i, (i + 1) % 4)
        R.add_edge(i, (i + 2) % 4)
    bundle = generate_evidence(7, nodes, 0.9, "independent", "balanced")
    res = run_protocol(nodes, bundle.network_view(), [R], max_rounds=20,
                       send_cap=4, max_messages=10000)
    for n, st in res.nodes.items():
        toks = list(st.known.keys())
        _check(len(toks) == len(set(toks)), f"duplicate tokens in known at {n}")
    sizes = {n: len(st.known) for n, st in res.nodes.items()}
    res2 = run_protocol(nodes, bundle.network_view(), [R], max_rounds=40,
                        send_cap=4, max_messages=10000)
    for n, st in res2.nodes.items():
        _check(len(st.known) >= sizes[n], "known shrank")
        _check(len(st.known) <= sum(1 for x in bundle.local_items.values() if x),
               "more tokens than generated")


def test_hidden_ground_truth_inaccessible():
    """Protocol cannot access ground truth."""
    nodes = list(range(6))
    R = substrate.TransitionGraph(nodes)
    for i in nodes:
        R.add_edge(i, (i + 1) % 6)
    bundle = generate_evidence(3, nodes, 0.7)
    view = bundle.network_view()
    _check(not hasattr(view, "ground_truth"), "NetworkEvidenceView has GT")
    _check("ground_truth" not in getattr(view, "__dataclass_fields__", {}),
           "GT field on view")
    # Must reject bundle-like objects that expose GT
    try:
        run_protocol(nodes, bundle, [R], max_rounds=2, send_cap=1)  # type: ignore
        raise TestFailure("protocol accepted EvidenceBundle with GT")
    except (ValueError, AttributeError, TypeError):
        pass
    res = run_protocol(nodes, view, [R], max_rounds=5, send_cap=2)
    for st in res.nodes.values():
        for item in st.known.values():
            _check(set(item.__dataclass_fields__) <= {"token", "bit", "weight"},
                   f"unexpected fields {item}")
    sig = inspect.signature(decide_from_known)
    _check("y" not in sig.parameters and "ground" not in str(sig),
           "decision rule takes ground truth")
    # Evaluator alone uses GT
    ev = evaluate_protocol(res, bundle.ground_truth, bundle)
    _check("frac_correct" in ev, "evaluator missing frac_correct")


def test_no_central_coordinator():
    nodes = list(range(5))
    R = substrate.TransitionGraph(nodes)
    for i in nodes:
        R.add_edge(i, (i + 1) % 5)
    bundle = generate_evidence(11, nodes, 0.8)
    res = run_protocol(nodes, bundle.network_view(), [R], max_rounds=8, send_cap=2)
    ev = evaluate_protocol(res, bundle.ground_truth, bundle)
    local = [st.decision for st in res.nodes.values()]
    snap = agreement_from_decisions({i: local[i] for i in range(5)})
    _check(snap["collective"] == ev["collective"] or (
        snap["collective"] is None and ev["collective"] is None),
           "evaluator collective mismatch")
    if snap["collective"] is not None:
        _check(any(d == snap["collective"] for d in local),
               "collective without supporting local")


def _relabel_once(seed, max_messages, send_cap, max_rounds, with_failures=False,
                  use_dynamic=False):
    n = 8
    steps = 8
    models = run_all_models(seed, n, 0.25, 3, steps)
    R0 = models["_R0"]
    nodes = sorted(R0.states())
    bundle = generate_evidence(seed, nodes, 0.7)
    graphs = models["D"].graphs if use_dynamic else [R0.copy()]
    fail_map = None
    if with_failures:
        from .failures import schedule_edge_failures
        fail_map = schedule_edge_failures(
            seed, list(R0.edges()), set(R0.edges()), fail_round=1, fraction=0.3)

    res1 = run_protocol(nodes, bundle.network_view(), graphs,
                        max_rounds=max_rounds, send_cap=send_cap,
                        max_messages=max_messages,
                        failure_edges_by_round=fail_map)

    rng = relabel_rng(seed)
    perm_list = nodes[:]
    rng.shuffle(perm_list)
    # Ensure non-identity when possible
    if perm_list == nodes and n > 1:
        perm_list = nodes[1:] + nodes[:1]
    perm = {nodes[i]: perm_list[i] for i in range(n)}
    inv = {v: k for k, v in perm.items()}

    graphs_r = [relabel_graph(g, perm) for g in graphs]
    bundle_r = relabel_evidence(bundle, perm)
    nodes_r = sorted(perm[n_] for n_ in nodes)
    fail_r = None
    if fail_map:
        fail_r = {
            r: {(perm[a], perm[b]) for (a, b) in edges}
            for r, edges in fail_map.items()
        }
    res2 = run_protocol(nodes_r, bundle_r.network_view(), graphs_r,
                        max_rounds=max_rounds, send_cap=send_cap,
                        max_messages=max_messages,
                        failure_edges_by_round=fail_r)

    dec1 = {n_: res1.nodes[n_].decision for n_ in nodes}
    dec2_mapped = {inv[n_]: res2.nodes[n_].decision for n_ in nodes_r}
    return res1, res2, dec1, dec2_mapped


def test_relabelling_statistical_equivalence():
    res1, res2, dec1, dec2 = _relabel_once(
        42, max_messages=5000, send_cap=2, max_rounds=5)
    _check(dec1 == dec2, f"relabel changed decisions {dec1} vs {dec2}")
    _check(res1.total_messages == res2.total_messages, "message count changed")
    _check(res1.total_unique_delivered == res2.total_unique_delivered,
           "deliveries changed")


def test_relabelling_restrictive_budget():
    """Relabel invariance under binding global message budget."""
    res1, res2, dec1, dec2 = _relabel_once(
        42, max_messages=25, send_cap=2, max_rounds=10)
    _check(res1.total_messages == res2.total_messages,
           f"budget msgs {res1.total_messages} vs {res2.total_messages}")
    _check(dec1 == dec2, f"budget relabel decisions {dec1} vs {dec2}")
    _check(res1.stopped_reason == res2.stopped_reason, "stop reason diverged")


def test_relabelling_caps_failures_dynamic():
    res1, res2, dec1, dec2 = _relabel_once(
        7, max_messages=80, send_cap=1, max_rounds=6,
        with_failures=True, use_dynamic=True)
    _check(dec1 == dec2, f"dynamic/fail relabel {dec1} vs {dec2}")
    _check(res1.total_messages == res2.total_messages, "msgs diverged")
    _check(res1.total_unique_delivered == res2.total_unique_delivered,
           "unique deliveries diverged")


def test_identical_evidence_inputs():
    seed = 5
    cond = SMOKE_CONDITION
    models = run_all_models(seed, cond.n_states, cond.edge_prob,
                            cond.initial_blocks, cond.graph_steps)
    R0 = models["_R0"]
    nodes = sorted(R0.states())
    b1 = generate_evidence(seed, nodes, cond.reliability)
    b2 = generate_evidence(seed, nodes, cond.reliability)
    _check(b1.ground_truth == b2.ground_truth, "GT differs")
    for n in nodes:
        _check(b1.local_items[n] == b2.local_items[n], f"evidence differs at {n}")
    for name in ("A", "B", "C", "D"):
        res = run_protocol(nodes, b1.network_view(), models[name].graphs,
                           max_rounds=3, send_cap=2)
        item = b1.node_view(n)
        # local token retained if present
        for n in nodes:
            item = b1.node_view(n)
            if item is not None:
                _check(item.token in res.nodes[n].known,
                       f"{name} lost local evidence at {n}")


def test_d_cr_matched_creation_counts():
    seed = 2
    models = run_all_models(seed, 12, 0.25, 3, 20)
    if models["CR"].control_infeasible:
        raise TestFailure("unexpected CR infeasible on seed 2")
    _check(verify_d_cr_creation_match(models["D"], models["CR"]),
           "creation counts not matched")
    for t, (a, b) in enumerate(zip(models["D"].created_edges,
                                   models["CR"].created_edges)):
        _check(len(a) == len(b), f"step {t}: |created| D={len(a)} CR={len(b)}")


def test_message_budgets_enforced():
    nodes = list(range(6))
    R = substrate.TransitionGraph(nodes)
    for i in nodes:
        for j in nodes:
            if i != j:
                R.add_edge(i, j)
    bundle = generate_evidence(9, nodes, 0.7)
    cap = 30
    res = run_protocol(nodes, bundle.network_view(), [R], max_rounds=50,
                       send_cap=3, max_messages=cap)
    _check(res.total_messages <= cap, f"budget exceeded: {res.total_messages}>{cap}")


def test_propagation_follows_graph():
    nodes = [0, 1, 2, 3]
    R = substrate.TransitionGraph(nodes)
    R.add_edge(0, 1)
    R.add_edge(2, 3)
    bundle = generate_evidence(1, nodes, 0.99, distribution="balanced")
    item0 = bundle.local_items[0]
    local = {0: item0, 1: None, 2: None, 3: None}
    b = EvidenceBundle(ground_truth=bundle.ground_truth, local_items=local)
    res = run_protocol(nodes, b.network_view(), [R], max_rounds=10, send_cap=2)
    tok = item0.token
    _check(tok in res.nodes[0].known and tok in res.nodes[1].known, "should reach 1")
    _check(tok not in res.nodes[2].known and tok not in res.nodes[3].known,
           "leaked across components")


def test_disconnected_nodes_handled():
    nodes = [0, 1, 2]
    R = substrate.TransitionGraph(nodes)
    bundle = generate_evidence(4, nodes, 0.8)
    res = run_protocol(nodes, bundle.network_view(), [R], max_rounds=5, send_cap=2)
    _check(res.total_messages == 0, "messages on empty graph")


def test_incorrect_vs_correct_consensus():
    nodes = list(range(4))
    R = substrate.TransitionGraph(nodes)
    for i in nodes:
        for j in nodes:
            if i != j:
                R.add_edge(i, j)
    y = 1
    items = {n: EvidenceItem(token=f"t{i}", bit=0, weight=2.0)
             for i, n in enumerate(nodes)}
    b = EvidenceBundle(ground_truth=y, local_items=items)
    res = run_protocol(nodes, b.network_view(), [R], max_rounds=3, send_cap=2)
    ev = evaluate_protocol(res, y, b)
    _check(ev["agreement_label"] == 0, "expected agreement on 0")
    _check(ev["agreement_correct"] is False, "should be incorrect consensus")
    items2 = {n: EvidenceItem(token=f"u{i}", bit=1, weight=2.0)
              for i, n in enumerate(nodes)}
    b2 = EvidenceBundle(ground_truth=y, local_items=items2)
    res2 = run_protocol(nodes, b2.network_view(), [R], max_rounds=3, send_cap=2)
    ev2 = evaluate_protocol(res2, y, b2)
    _check(ev2["agreement_correct"] is True, "expected correct consensus")


def test_agreement_ties_with_undecided():
    """Tie among decided nodes must not yield a unique collective label."""
    # 3 vote 0, 3 vote 1, 2 undecided
    decs = {0: 0, 1: 0, 2: 0, 3: 1, 4: 1, 5: 1, 6: None, 7: None}
    snap = agreement_from_decisions(decs)
    _check(snap["agreement_label"] is None, "tie assigned a label")
    _check(snap["collective"] is None, "tie assigned collective")
    # All-decided tie
    snap2 = agreement_from_decisions({0: 0, 1: 0, 2: 1, 3: 1})
    _check(snap2["agreement_label"] is None and snap2["collective"] is None,
           "all-decided tie")
    # Clear majority with undecided
    snap3 = agreement_from_decisions({0: 1, 1: 1, 2: 1, 3: 0, 4: None})
    _check(snap3["agreement_label"] == 1 and snap3["collective"] == 1,
           "majority with undecided")


def test_edge_attribution_first_delivery_into_correct():
    """Only inbound first-deliveries into correct nodes count as helping."""
    nodes = [0, 1, 2]
    R = substrate.TransitionGraph(nodes)
    R.add_edge(0, 1)
    R.add_edge(1, 2)
    y = 1
    # Only node 0 holds correct evidence; 1 and 2 start empty.
    items = {
        0: EvidenceItem(token="ta", bit=1, weight=2.0),
        1: None,
        2: None,
    }
    b = EvidenceBundle(ground_truth=y, local_items=items)
    res = run_protocol(nodes, b.network_view(), [R], max_rounds=5, send_cap=2)
    ev = evaluate_protocol(res, y, b)
    carry, help_e = attribute_edges(res, y)
    _check((0, 1) in carry, "0->1 should carry")
    _check((1, 2) in carry, "1->2 should carry")
    # Node 2 ends correct if it received the bit; helping edge into 2 is 1->2.
    # Edge 0->1 delivered into node 1 — counts for help only if node 1 is correct.
    if res.nodes[2].decision == y:
        _check((1, 2) in help_e, "inbound to correct node 2 missing")
    if res.nodes[1].decision != y:
        _check((0, 1) not in help_e or res.nodes[1].decision == y,
               "edge into incorrect node credited incorrectly")
    # Explicit: edges_helping_correct ⊆ edges that first-delivered into a
    # finally-correct node
    for e in help_e:
        _check(e in carry, "help edge not in carry set")


def test_random_streams_isolated():
    _check(EVIDENCE_OFFSET == 4 and FAILURE_OFFSET == 5 and RELABEL_OFFSET == 6,
           "offset collision with one.py")
    s = 17
    r1 = failure_stream_seed(s)
    _ = [evidence_rng(s).random() for _ in range(50)]
    r2 = failure_stream_seed(s)
    _check(r1 == r2, "evidence draws affected failure seed")
    b1 = generate_evidence(s, list(range(6)), 0.7)
    from .streams import failure_rng
    _ = [failure_rng(s).random() for _ in range(50)]
    b2 = generate_evidence(s, list(range(6)), 0.7)
    _check(b1.ground_truth == b2.ground_truth, "failure affected evidence")
    _check(substrate.STREAM_DOMAIN_OFFSETS == {"init": 1, "move": 2, "ctrl": 3},
           "one.py streams altered")


def test_reproducibility():
    seed = 0
    cond = SMOKE_CONDITION
    a = run_all_models(seed, cond.n_states, cond.edge_prob,
                       cond.initial_blocks, cond.graph_steps)
    b = run_all_models(seed, cond.n_states, cond.edge_prob,
                       cond.initial_blocks, cond.graph_steps)
    _check(a["D"].run.final_graph.signature() == b["D"].run.final_graph.signature(),
           "D graph not reproducible")
    nodes = sorted(a["_R0"].states())
    e1 = generate_evidence(seed, nodes, cond.reliability)
    e2 = generate_evidence(seed, nodes, cond.reliability)
    r1 = run_protocol(nodes, e1.network_view(), a["D"].graphs,
                      cond.max_rounds, cond.send_cap, cond.max_messages)
    r2 = run_protocol(nodes, e2.network_view(), b["D"].graphs,
                      cond.max_rounds, cond.send_cap, cond.max_messages)
    _check(r1.total_messages == r2.total_messages, "messages not reproducible")
    ev1 = evaluate_protocol(r1, e1.ground_truth)
    ev2 = evaluate_protocol(r2, e2.ground_truth)
    _check(ev1["frac_correct"] == ev2["frac_correct"], "accuracy not reproducible")


def test_one_py_hash_preserved():
    path = os.path.join(_ROOT, "one.py")
    data = open(path, "rb").read()
    import hashlib
    sha = hashlib.sha256(data).hexdigest()
    _check(sha == "3671c48e08c26dbe0c6bab20b2ec2091c63f721fb2d8adaa4dd2a6543c11a88a",
           f"one.py changed: {sha}")


def test_baselines_mv_u_and_static():
    seed = 3
    models = run_all_models(seed, 8, 0.25, 3, 5)
    R0 = models["_R0"]
    st = make_static_directed_timeline(R0, 5, seed)
    _check(all(g.signature() == R0.signature() for g in st.graphs),
           "STATIC not constant R0")
    # MV_U ignores weights: many light correct vs one heavy wrong → majority wins
    nodes = [0, 1, 2, 3]
    R = substrate.TransitionGraph(nodes)
    for i in nodes:
        for j in nodes:
            if i != j:
                R.add_edge(i, j)
                R.add_edge(j, i)
    items = {
        0: EvidenceItem(token="a", bit=1, weight=0.1),
        1: EvidenceItem(token="b", bit=1, weight=0.1),
        2: EvidenceItem(token="c", bit=1, weight=0.1),
        3: EvidenceItem(token="d", bit=0, weight=10.0),
    }
    b = EvidenceBundle(ground_truth=1, local_items=items)
    # Weighted would pick 0; unweighted majority picks 1
    _check(decide_from_known({t: items[t] for t in nodes if items[t]}) == 0,
           "weighted sanity")
    _check(decide_unweighted_majority({t: items[t] for t in nodes}) == 1,
           "unweighted sanity")
    res_u = run_protocol(nodes, b.network_view(), [R], max_rounds=4, send_cap=4,
                         decision_rule="unweighted")
    # After full mix, every node has all 4 bits → majority 1
    for st_ in res_u.nodes.values():
        _check(st_.decision == 1, f"MV_U decision {st_.decision}")


def test_correlation_structure_quantified():
    nodes = list(range(12))
    indep = [generate_evidence(s, nodes, 0.7, correlation="independent")
             for s in range(40)]
    corr = [generate_evidence(s, nodes, 0.7, correlation="correlated")
            for s in range(40)]
    c_i = empirical_pairwise_bit_correlation(indep)
    c_c = empirical_pairwise_bit_correlation(corr)
    _check(c_c == c_c and c_i == c_i, "nan correlation")
    _check(c_c > c_i + 0.05, f"correlated ({c_c}) not > independent ({c_i})")
    _check(corr[0].correlation_model == "group_equicorrelated_mixture",
           "model name")
    _check(NONINFERIORITY_MARGIN_FRAC_CORRECT == 0.05, "NI margin drifted")


def test_ni_tost_helpers():
    # Clearly non-inferior and equivalent near zero
    diffs = [0.01] * 50 + [-0.01] * 50
    ni = noninferiority_test(diffs, delta=0.05)
    _check(ni["noninferior"] is True, "NI should pass near zero")
    tost = tost_equivalence(diffs, delta=0.05)
    _check(tost["equivalent"] is True, "TOST should pass near zero")
    # Clearly inferior
    bad = [-0.2] * 80
    ni2 = noninferiority_test(bad, delta=0.05)
    _check(ni2["noninferior"] is False, "NI should fail when much worse")


def test_v1_results_preserved():
    v1 = os.path.join(_ROOT, "evidence_benchmark_results")
    _check(os.path.isdir(v1), "v1 results missing")
    _check(os.path.isfile(os.path.join(v1, "experiment_report.md")),
           "v1 report missing")


def run_all_tests() -> Dict[str, str]:
    tests = [
        ("E01_no_double_count", test_no_double_count),
        ("E02_hidden_ground_truth", test_hidden_ground_truth_inaccessible),
        ("E03_no_central_coordinator", test_no_central_coordinator),
        ("E04_relabelling", test_relabelling_statistical_equivalence),
        ("E04b_relabel_budget", test_relabelling_restrictive_budget),
        ("E04c_relabel_fail_dyn", test_relabelling_caps_failures_dynamic),
        ("E05_identical_evidence", test_identical_evidence_inputs),
        ("E06_d_cr_creation_match", test_d_cr_matched_creation_counts),
        ("E07_message_budgets", test_message_budgets_enforced),
        ("E08_propagation_graph", test_propagation_follows_graph),
        ("E09_disconnected", test_disconnected_nodes_handled),
        ("E10_consensus_distinction", test_incorrect_vs_correct_consensus),
        ("E10b_agreement_ties", test_agreement_ties_with_undecided),
        ("E11_stream_isolation", test_random_streams_isolated),
        ("E12_reproducibility", test_reproducibility),
        ("E13_one_py_preserved", test_one_py_hash_preserved),
        ("E14_edge_attribution", test_edge_attribution_first_delivery_into_correct),
        ("E15_baselines_mv_u_static", test_baselines_mv_u_and_static),
        ("E16_correlation_quantified", test_correlation_structure_quantified),
        ("E17_ni_tost_helpers", test_ni_tost_helpers),
        ("E18_v1_preserved", test_v1_results_preserved),
    ]
    results = {}
    for name, fn in tests:
        try:
            fn()
            results[name] = "PASS"
            print(f"  {name}: PASS")
        except Exception as exc:
            results[name] = f"FAIL: {exc}"
            print(f"  {name}: FAIL: {exc}")
            traceback.print_exc()
    return results


if __name__ == "__main__":
    print("Evidence benchmark correctness tests (v2)")
    res = run_all_tests()
    n_pass = sum(1 for v in res.values() if v == "PASS")
    print(f"\n  {n_pass}/{len(res)} tests passed")
    sys.exit(0 if n_pass == len(res) else 1)
