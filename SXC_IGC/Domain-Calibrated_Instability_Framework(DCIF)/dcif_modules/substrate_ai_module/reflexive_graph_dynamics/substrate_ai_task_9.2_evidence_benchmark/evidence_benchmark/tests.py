"""Correctness tests for the evidence integration benchmark."""

from __future__ import annotations

import json
import os
import sys
import traceback
from typing import Any, Dict

from .conditions import SMOKE_CONDITION, BASELINE
from .evidence import generate_evidence, relabel_evidence
from .failures import schedule_edge_failures
from .graph_bridge import (
    make_mv_timeline,
    relabel_graph,
    relabel_partition,
    run_all_models,
    verify_d_cr_creation_match,
)
from .protocol import decide_from_known, run_protocol
from .streams import (
    EVIDENCE_OFFSET,
    FAILURE_OFFSET,
    RELABEL_OFFSET,
    evidence_rng,
    evidence_stream_seed,
    failure_stream_seed,
    relabel_rng,
    relabel_stream_seed,
)
from .evidence import EvidenceItem

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
    """Evidence is never counted twice."""
    nodes = list(range(4))
    # Build a cycle graph manually via substrate
    R = substrate.TransitionGraph(nodes)
    for i in nodes:
        R.add_edge(i, (i + 1) % 4)
        R.add_edge(i, (i + 2) % 4)
    bundle = generate_evidence(7, nodes, 0.9, "independent", "balanced")
    # Run many rounds; known map is keyed by token
    res = run_protocol(nodes, bundle, [R], max_rounds=20, send_cap=4,
                       max_messages=10000)
    for n, st in res.nodes.items():
        toks = list(st.known.keys())
        _check(len(toks) == len(set(toks)), f"duplicate tokens in known at {n}")
        # score uses each token once
        score_items = list(st.known.values())
        _check(len(score_items) == len(st.known), "known values length mismatch")
    _check(res.total_duplicates_prevented >= 0, "dup counter")
    # Force a known duplicate path: after full diffusion, more rounds should
    # only increase duplicates, not known sizes
    sizes = {n: len(st.known) for n, st in res.nodes.items()}
    res2 = run_protocol(nodes, bundle, [R], max_rounds=40, send_cap=4,
                        max_messages=10000)
    for n, st in res2.nodes.items():
        _check(len(st.known) == sizes[n] or len(st.known) >= sizes[n],
               "known shrank")
        _check(len(st.known) <= sum(1 for x in bundle.local_items.values() if x),
               "more tokens than generated")


def test_hidden_ground_truth_inaccessible():
    """Hidden ground truth is inaccessible to the network."""
    nodes = list(range(6))
    R = substrate.TransitionGraph(nodes)
    for i in nodes:
        R.add_edge(i, (i + 1) % 6)
    bundle = generate_evidence(3, nodes, 0.7)
    # Protocol API: only node_view and message fields
    for n in nodes:
        item = bundle.node_view(n)
        if item is not None:
            _check(not hasattr(item, "ground_truth"), "item leaks GT attr")
            _check("ground_truth" not in item.__dict__, "item dict leaks GT")
    res = run_protocol(nodes, bundle, [R], max_rounds=5, send_cap=2)
    # Inspect node states: only EvidenceItem fields
    for st in res.nodes.values():
        for item in st.known.values():
            _check(set(item.__dataclass_fields__) <= {"token", "bit", "weight"},
                   f"unexpected fields {item}")
    # Ensure decide_from_known has no y parameter
    import inspect
    sig = inspect.signature(decide_from_known)
    _check("y" not in sig.parameters and "ground" not in str(sig),
           "decision rule takes ground truth")


def test_no_central_coordinator():
    """No central coordinator determines the answer."""
    nodes = list(range(5))
    R = substrate.TransitionGraph(nodes)
    for i in nodes:
        R.add_edge(i, (i + 1) % 5)
    bundle = generate_evidence(11, nodes, 0.8)
    res = run_protocol(nodes, bundle, [R], max_rounds=8, send_cap=2)
    # Every node has its own decision; collective is a post-hoc majority of
    # those decisions, not an injected oracle.
    _check(all(hasattr(st, "decision") for st in res.nodes.values()),
           "missing local decisions")
    local = [st.decision for st in res.nodes.values()]
    # Collective in last round equals majority of locals (when defined)
    last = res.rounds[-1]
    decided = [d for d in local if d is not None]
    if not decided or decided.count(0) == decided.count(1):
        _check(last.collective is None, "collective should be undecided")
    else:
        maj = 0 if decided.count(0) > decided.count(1) else 1
        _check(last.collective == maj, "collective is not majority of locals")
    _check(last.collective != bundle.ground_truth or any(
        st.decision == bundle.ground_truth for st in res.nodes.values()),
           "collective correct without any correct local — oracle suspected")


def test_relabelling_statistical_equivalence():
    """Node relabelling does not change statistical behaviour."""
    seed = 42
    n = 8
    steps = 8
    models = run_all_models(seed, n, 0.25, 3, steps)
    R0, P0 = models["_R0"], models["_P0"]
    nodes = sorted(R0.states())
    bundle = generate_evidence(seed, nodes, 0.7)
    res1 = run_protocol(nodes, bundle, models["D"].graphs,
                        max_rounds=5, send_cap=2)

    rng = relabel_rng(seed)
    perm_list = nodes[:]
    rng.shuffle(perm_list)
    perm = {nodes[i]: perm_list[i] for i in range(n)}
    inv = {v: k for k, v in perm.items()}

    R0r = relabel_graph(R0, perm)
    # Relabel graph sequence for D
    graphs_r = [relabel_graph(g, perm) for g in models["D"].graphs]
    bundle_r = relabel_evidence(bundle, perm)
    nodes_r = sorted(R0r.states())
    res2 = run_protocol(nodes_r, bundle_r, graphs_r, max_rounds=5, send_cap=2)

    # Map decisions back
    dec1 = {n: res1.nodes[n].decision for n in nodes}
    dec2_mapped = {inv[n]: res2.nodes[n].decision for n in nodes_r}
    _check(dec1 == dec2_mapped, f"relabel changed decisions {dec1} vs {dec2_mapped}")
    _check(res1.total_messages == res2.total_messages, "message count changed")
    _check(res1.total_unique_delivered == res2.total_unique_delivered,
           "deliveries changed")
    _check(abs(res1.rounds[-1].frac_correct - res2.rounds[-1].frac_correct) < 1e-12,
           "frac_correct changed")


def test_identical_evidence_inputs():
    """Every model receives identical evidence inputs for a paired seed."""
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
        i1, i2 = b1.local_items[n], b2.local_items[n]
        if i1 is None:
            _check(i2 is None, "holder mismatch")
        else:
            _check(i1 == i2, f"evidence differs at {n}")
    # Same bundle object semantics for all models: regenerate once, reuse
    results = {}
    for name in ("A", "B", "C", "D"):
        results[name] = run_protocol(
            nodes, b1, models[name].graphs, max_rounds=3, send_cap=2)
    # Initial known sets must match (before communication topology matters)
    init_tokens = {
        name: {n: set(results[name].nodes[n].known) for n in nodes}
        # After protocol, known may differ — check starting items via bundle
    }
    for n in nodes:
        item = b1.node_view(n)
        for name in results:
            st = results[name].nodes[n]
            if item is None:
                # may have received messages; but token from empty start
                pass
            else:
                _check(item.token in st.known,
                       f"{name} lost local evidence at {n}")


def test_d_cr_matched_creation_counts():
    """D and CR have exactly matched creation counts."""
    seed = 2
    models = run_all_models(seed, 12, 0.25, 3, 20)
    if models["CR"].control_infeasible:
        raise TestFailure("unexpected CR infeasible on seed 2")
    _check(verify_d_cr_creation_match(models["D"], models["CR"]),
           "creation counts not matched")
    for t, (a, b) in enumerate(zip(models["D"].created_edges,
                                   models["CR"].created_edges)):
        _check(len(a) == len(b), f"step {t}: |created| D={len(a)} CR={len(b)}")
    _check(models["D"].total_created == models["CR"].total_created,
           "total created mismatch")


def test_message_budgets_enforced():
    """Message budgets are enforced identically."""
    nodes = list(range(6))
    R = substrate.TransitionGraph(nodes)
    for i in nodes:
        for j in nodes:
            if i != j:
                R.add_edge(i, j)
    bundle = generate_evidence(9, nodes, 0.7)
    cap = 30
    res = run_protocol(nodes, bundle, [R], max_rounds=50, send_cap=3,
                       max_messages=cap)
    _check(res.total_messages <= cap, f"budget exceeded: {res.total_messages}>{cap}")
    _check(res.stopped_reason in ("message_budget", "quiescence", "max_rounds"),
           res.stopped_reason)


def test_propagation_follows_graph():
    """Evidence propagation follows the intended graph."""
    # Disconnected: 0->1, 2->3 only. Evidence at 0 must not reach 2 or 3.
    nodes = [0, 1, 2, 3]
    R = substrate.TransitionGraph(nodes)
    R.add_edge(0, 1)
    R.add_edge(2, 3)
    bundle = generate_evidence(1, nodes, 0.99, distribution="balanced")
    # Force only node 0 has evidence by rebuilding uneven manually
    from .evidence import EvidenceBundle, EvidenceItem
    item0 = bundle.local_items[0]
    local = {0: item0, 1: None, 2: None, 3: None}
    b = EvidenceBundle(ground_truth=bundle.ground_truth, local_items=local)
    res = run_protocol(nodes, b, [R], max_rounds=10, send_cap=2)
    tok = item0.token
    _check(tok in res.nodes[0].known and tok in res.nodes[1].known,
           "should reach 1")
    _check(tok not in res.nodes[2].known and tok not in res.nodes[3].known,
           "leaked across components")


def test_disconnected_nodes_handled():
    """Disconnected nodes are handled correctly."""
    nodes = [0, 1, 2]
    R = substrate.TransitionGraph(nodes)  # no edges
    bundle = generate_evidence(4, nodes, 0.8)
    res = run_protocol(nodes, bundle, [R], max_rounds=5, send_cap=2)
    _check(res.total_messages == 0, "messages on empty graph")
    for n in nodes:
        item = bundle.local_items[n]
        if item is None:
            _check(len(res.nodes[n].known) == 0, "spurious knowledge")
        else:
            _check(set(res.nodes[n].known) == {item.token},
                   "should keep only local")


def test_incorrect_vs_correct_consensus():
    """Incorrect consensus is distinguished from correct consensus."""
    nodes = list(range(4))
    R = substrate.TransitionGraph(nodes)
    for i in nodes:
        for j in nodes:
            if i != j:
                R.add_edge(i, j)
    # Craft bundle: all evidence wrong
    y = 1
    items = {}
    for i, n in enumerate(nodes):
        items[n] = EvidenceItem(token=f"t{i}", bit=0, weight=2.0)
    b = __import__("evidence_benchmark.evidence", fromlist=["EvidenceBundle"]).EvidenceBundle(
        ground_truth=y, local_items=items)
    res = run_protocol(nodes, b, [R], max_rounds=3, send_cap=2)
    last = res.rounds[-1]
    _check(last.agreement_label == 0, "expected agreement on 0")
    _check(last.agreement_correct is False, "should be incorrect consensus")
    _check(last.collective_correct is False, "collective should be incorrect")
    # Correct case
    items2 = {n: EvidenceItem(token=f"u{i}", bit=1, weight=2.0)
              for i, n in enumerate(nodes)}
    b2 = type(b)(ground_truth=y, local_items=items2)
    res2 = run_protocol(nodes, b2, [R], max_rounds=3, send_cap=2)
    _check(res2.rounds[-1].agreement_correct is True, "expected correct consensus")


def test_random_streams_isolated():
    """Random streams cannot interfere with one another."""
    _check(EVIDENCE_OFFSET == 4 and FAILURE_OFFSET == 5 and RELABEL_OFFSET == 6,
           "offset collision with one.py")
    _check(len({1, 2, 3, EVIDENCE_OFFSET, FAILURE_OFFSET, RELABEL_OFFSET}) == 6,
           "offsets not distinct")
    s = 17
    # Drawing from evidence must not change failure stream reproducibility
    r1 = failure_stream_seed(s)
    _ = [evidence_rng(s).random() for _ in range(50)]
    r2 = failure_stream_seed(s)
    _check(r1 == r2, "evidence draws affected failure seed")
    # Failure draws don't change evidence reproduction
    b1 = generate_evidence(s, list(range(6)), 0.7)
    _ = [__import__("evidence_benchmark.streams", fromlist=["failure_rng"]).failure_rng(s).random()
         for _ in range(50)]
    b2 = generate_evidence(s, list(range(6)), 0.7)
    _check(b1.ground_truth == b2.ground_truth, "failure affected evidence")
    for n in range(6):
        _check(b1.local_items[n] == b2.local_items[n], "evidence changed")
    # one.py streams unchanged offsets
    _check(substrate.STREAM_DOMAIN_OFFSETS == {"init": 1, "move": 2, "ctrl": 3},
           "one.py streams altered")


def test_reproducibility():
    """Results can be reproduced from recorded seeds and configuration."""
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
    r1 = run_protocol(nodes, e1, a["D"].graphs, cond.max_rounds, cond.send_cap,
                      cond.max_messages)
    r2 = run_protocol(nodes, e2, b["D"].graphs, cond.max_rounds, cond.send_cap,
                      cond.max_messages)
    _check(r1.total_messages == r2.total_messages, "messages not reproducible")
    _check(r1.rounds[-1].frac_correct == r2.rounds[-1].frac_correct,
           "accuracy not reproducible")


def test_one_py_hash_preserved():
    """Preserved substrate hash matches the locked experiment."""
    path = os.path.join(_ROOT, "one.py")
    data = open(path, "rb").read()
    import hashlib
    sha = hashlib.sha256(data).hexdigest()
    _check(sha == "3671c48e08c26dbe0c6bab20b2ec2091c63f721fb2d8adaa4dd2a6543c11a88a",
           f"one.py changed: {sha}")


def run_all_tests() -> Dict[str, str]:
    tests = [
        ("E01_no_double_count", test_no_double_count),
        ("E02_hidden_ground_truth", test_hidden_ground_truth_inaccessible),
        ("E03_no_central_coordinator", test_no_central_coordinator),
        ("E04_relabelling", test_relabelling_statistical_equivalence),
        ("E05_identical_evidence", test_identical_evidence_inputs),
        ("E06_d_cr_creation_match", test_d_cr_matched_creation_counts),
        ("E07_message_budgets", test_message_budgets_enforced),
        ("E08_propagation_graph", test_propagation_follows_graph),
        ("E09_disconnected", test_disconnected_nodes_handled),
        ("E10_consensus_distinction", test_incorrect_vs_correct_consensus),
        ("E11_stream_isolation", test_random_streams_isolated),
        ("E12_reproducibility", test_reproducibility),
        ("E13_one_py_preserved", test_one_py_hash_preserved),
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
    print("Evidence benchmark correctness tests")
    res = run_all_tests()
    n_pass = sum(1 for v in res.values() if v == "PASS")
    print(f"\n  {n_pass}/{len(res)} tests passed")
    sys.exit(0 if n_pass == len(res) else 1)
