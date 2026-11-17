"""Domain-separated PRNG streams for the evidence benchmark.

Offsets 1, 2, 3 are reserved by one.py (init, move, ctrl) and must not be reused.
"""

from __future__ import annotations

import random

# Must not collide with one.py STREAM_DOMAIN_OFFSETS = {init:1, move:2, ctrl:3}
EVIDENCE_OFFSET = 4
FAILURE_OFFSET = 5
RELABEL_OFFSET = 6


def _seed(experimental_seed: int, offset: int) -> int:
    return experimental_seed * 1_000_000 + offset


def evidence_stream_seed(seed: int) -> int:
    return _seed(seed, EVIDENCE_OFFSET)


def failure_stream_seed(seed: int) -> int:
    return _seed(seed, FAILURE_OFFSET)


def relabel_stream_seed(seed: int) -> int:
    return _seed(seed, RELABEL_OFFSET)


def evidence_rng(seed: int) -> random.Random:
    return random.Random(evidence_stream_seed(seed))


def failure_rng(seed: int) -> random.Random:
    return random.Random(failure_stream_seed(seed))


def relabel_rng(seed: int) -> random.Random:
    return random.Random(relabel_stream_seed(seed))
