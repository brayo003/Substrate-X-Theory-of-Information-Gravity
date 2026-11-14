"""
Substrate Closure Weave (SCW) — first executable toy model.

This is an exploratory deterministic graph-rewrite system, not a validated
physical theory. It deliberately does not use a stochastic process, matrix
state, Hamiltonian, or quantum channel as its state-update rule.

State:
  - four ports/nodes: 0, 1, 2, 3
  - oriented strands (u, v, s), with orientation mark s in {-1, +1}
  - closure count c

Interaction routing:
  A: 0 -> 1 if c is even; otherwise 0 -> 3
  B: 1 -> 2 if c is even; otherwise 1 -> 0

Reorganization:
  Add the routed strand. If there is already a directed path from its target
  back to its source, the new strand closes a directed cycle. Select a
  shortest return path (ties broken by insertion order), invert the
  orientation marks on that cycle, and increment c.

This is a deliberately minimal axiom system. The routing rule is a proposal,
not derived from physical principles. No quantum prediction is claimed.
"""

from collections import deque
from copy import deepcopy
from itertools import product
import json


def shortest_path_edge_ids(edges, start, goal):
    """Shortest directed path; ties resolved by edge insertion order."""
    adjacency = {}
    for i, (u, v, sign) in enumerate(edges):
        adjacency.setdefault(u, []).append((v, i))

    queue = deque([start])
    previous_node = {start: None}
    previous_edge = {}

    while queue:
        node = queue.popleft()
        if node == goal:
            break
        for nxt, edge_id in adjacency.get(node, []):
            if nxt not in previous_node:
                previous_node[nxt] = node
                previous_edge[nxt] = edge_id
                queue.append(nxt)

    if goal not in previous_node:
        return None

    ids = []
    node = goal
    while node != start:
        ids.append(previous_edge[node])
        node = previous_node[node]
    return list(reversed(ids))


def initial_weave():
    """Three-strand starting weave: 0->2->1->3."""
    return {
        "strands": [(0, 2, +1), (2, 1, +1), (1, 3, +1)],
        "closures": 0,
        "history": [],
    }


def reweave(state, interaction):
    """Apply one deterministic interaction and return a new state."""
    if interaction not in ("A", "B"):
        raise ValueError("interaction must be 'A' or 'B'")

    result = deepcopy(state)
    even_closure = result["closures"] % 2 == 0

    if interaction == "A":
        source, target = (0, 1) if even_closure else (0, 3)
    else:
        source, target = (1, 2) if even_closure else (1, 0)

    return_path = shortest_path_edge_ids(
        result["strands"], target, source
    )
    result["strands"].append((source, target, +1))
    closed = return_path is not None

    if closed:
        cycle_ids = set(return_path + [len(result["strands"]) - 1])
        result["strands"] = [
            (u, v, -sign) if i in cycle_ids else (u, v, sign)
            for i, (u, v, sign) in enumerate(result["strands"])
        ]
        result["closures"] += 1

    result["history"].append({
        "interaction": interaction,
        "strand_added": [source, target],
        "cycle_closed": closed,
        "closure_count_after": result["closures"],
    })
    return result


def run_sequence(state, sequence):
    result = deepcopy(state)
    for interaction in sequence:
        result = reweave(result, interaction)
    return result


def observe(state):
    """A simple structural readout, not a quantum measurement rule."""
    return {
        "boundary_0_reaches_3":
            shortest_path_edge_ids(state["strands"], 0, 3) is not None,
        "closure_count": state["closures"],
        "closure_parity": state["closures"] % 2,
        "orientation_balance": sum(sign for _, _, sign in state["strands"]),
        "strand_count": len(state["strands"]),
    }


def coarse_signature(state):
    """Intentionally coarse summary that forgets which nodes are connected."""
    degree = {node: 0 for node in range(4)}
    for u, v, _ in state["strands"]:
        degree[u] += 1
        degree[v] += 1
    return (
        len(state["strands"]),
        tuple(sorted(degree.values())),
        sum(sign for _, _, sign in state["strands"]),
        state["closures"],
    )


def assert_valid(state):
    assert state["closures"] >= 0
    assert all(0 <= u < 4 and 0 <= v < 4 and u != v
               and sign in (-1, +1)
               for u, v, sign in state["strands"])


def run_experiments():
    base = initial_weave()

    # Experiment 1: exhaustive deterministic replay for every A/B sequence
    # of length 0 through 8.
    sequence_count = 0
    for length in range(9):
        for sequence in product("AB", repeat=length):
            one = run_sequence(base, sequence)
            two = run_sequence(base, sequence)
            assert_valid(one)
            assert one == two
            sequence_count += 1

    # Experiment 2: order sensitivity. Compare A-B-B with B-B-A.
    seq_left = ("A", "B", "B")
    seq_right = ("B", "B", "A")
    left = run_sequence(base, seq_left)
    right = run_sequence(base, seq_right)
    order_result = {
        "sequence_1": "".join(seq_left),
        "sequence_2": "".join(seq_right),
        "observation_1": observe(left),
        "observation_2": observe(right),
        "same_observation": observe(left) == observe(right),
        "history_1": left["history"],
        "history_2": right["history"],
    }
    assert observe(left) != observe(right)

    # Experiment 3: two initial structures with the same coarse signature
    # and same listed observation, followed by the same interaction sequence.
    w1 = {
        "strands": [(0, 1, +1), (0, 2, +1), (0, 3, +1)],
        "closures": 0,
        "history": [],
    }
    w2 = {
        "strands": [(0, 1, +1), (0, 3, +1), (2, 0, +1)],
        "closures": 0,
        "history": [],
    }
    assert coarse_signature(w1) == coarse_signature(w2)
    assert observe(w1) == observe(w2)

    probe = ("A", "A", "A", "B")
    w1_final = run_sequence(w1, probe)
    w2_final = run_sequence(w2, probe)
    hidden_structure_result = {
        "initial_coarse_signatures_equal":
            coarse_signature(w1) == coarse_signature(w2),
        "initial_observations_equal": observe(w1) == observe(w2),
        "probe_sequence": "".join(probe),
        "final_observation_1": observe(w1_final),
        "final_observation_2": observe(w2_final),
        "same_final_observation":
            observe(w1_final) == observe(w2_final),
        "history_1": w1_final["history"],
        "history_2": w2_final["history"],
    }
    assert observe(w1_final) != observe(w2_final)

    # Experiment 4: find shortest sequence whose reverse gives a different
    # observation from the chosen baseline.
    shortest_order_witness = None
    for length in range(1, 9):
        for sequence in product("AB", repeat=length):
            forward = run_sequence(base, sequence)
            reverse = run_sequence(base, sequence[::-1])
            if observe(forward) != observe(reverse):
                shortest_order_witness = {
                    "length": length,
                    "forward": "".join(sequence),
                    "reverse": "".join(sequence[::-1]),
                    "forward_observation": observe(forward),
                    "reverse_observation": observe(reverse),
                }
                break
        if shortest_order_witness:
            break

    return {
        "model": "SCW deterministic graph-rewrite toy model",
        "status": "exploratory; not a validated physical theory",
        "exhaustive_replay_sequences_checked": sequence_count,
        "all_replays_deterministic_and_states_valid": True,
        "order_sensitivity_test": order_result,
        "same_coarse_state_different_future_test": hidden_structure_result,
        "shortest_order_witness": shortest_order_witness,
        "limitations": [
            "The routing rule is stipulated, not derived.",
            "The readout is a structural observable, not a quantum measurement rule.",
            "No quantum system has been coupled yet.",
            "No empirical or uniquely quantum prediction has been established.",
            "A graph-rewrite formalism is not automatically novel mathematics."
        ],
    }


if __name__ == "__main__":
    print(json.dumps(run_experiments(), indent=2))
