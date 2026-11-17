"""Evidence generation. Ground truth is evaluator-only."""

from __future__ import annotations

import hashlib
import math
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Sequence, Set, Tuple

from .streams import evidence_rng


@dataclass(frozen=True)
class EvidenceItem:
    """A single local evidence item. token is opaque (no source id)."""

    token: str
    bit: int
    weight: float


@dataclass
class EvidenceBundle:
    """Evaluator-side bundle. Nodes never receive this object."""

    ground_truth: int
    # node -> item or None if no local evidence
    local_items: Dict[Any, Optional[EvidenceItem]]
    adversarial_nodes: Set[Any] = field(default_factory=set)
    reliability: float = 0.7
    correlation: str = "independent"
    distribution: str = "balanced"
    # serial order used to build opaque tokens
    token_serials: Dict[str, int] = field(default_factory=dict)

    def node_view(self, node: Any) -> Optional[EvidenceItem]:
        """What a node is allowed to know at start: its own item only."""
        return self.local_items.get(node)


def _opaque_token(seed: int, serial: int) -> str:
    payload = f"{seed}|ev|{serial}".encode("utf-8")
    return hashlib.sha256(payload).hexdigest()[:16]


def _weight_from_reliability(p: float) -> float:
    # logit magnitude; clamp away from 0/1
    p = min(max(p, 1e-6), 1.0 - 1e-6)
    return abs(math.log(p / (1.0 - p)))


def generate_evidence(
    seed: int,
    nodes: Sequence[Any],
    reliability: float,
    correlation: str = "independent",
    distribution: str = "balanced",
    adversarial_fraction: float = 0.0,
    adversarial_weight_boost: float = 2.0,
) -> EvidenceBundle:
    """Generate paired evidence for a seed.

    correlation:
      - independent: each holder flips independently with rate 1-p
      - correlated: a shared error bit is applied to a random half of holders
    distribution:
      - balanced: every node holds one item
      - uneven: only the first ceil(0.25*|V|) nodes (after RNG shuffle) hold items
    adversarial_fraction: fraction of holders whose bit is flipped and weight boosted
    """
    if correlation not in ("independent", "correlated"):
        raise ValueError(correlation)
    if distribution not in ("balanced", "uneven"):
        raise ValueError(distribution)
    if not (0.0 < reliability < 1.0):
        raise ValueError("reliability must be in (0,1)")
    if not (0.0 <= adversarial_fraction <= 1.0):
        raise ValueError("adversarial_fraction must be in [0,1]")

    rng = evidence_rng(seed)
    y = rng.randint(0, 1)
    nodes_list = list(nodes)
    order = nodes_list[:]
    rng.shuffle(order)

    if distribution == "balanced":
        holders = set(order)
    else:
        k = max(1, int(math.ceil(0.25 * len(order))))
        holders = set(order[:k])

    base_w = _weight_from_reliability(reliability)
    local: Dict[Any, Optional[EvidenceItem]] = {n: None for n in nodes_list}
    token_serials: Dict[str, int] = {}
    serial = 0

    # Pre-draw independent noisy bits for all holders
    raw_bits: Dict[Any, int] = {}
    for n in holders:
        if rng.random() < reliability:
            raw_bits[n] = y
        else:
            raw_bits[n] = 1 - y

    if correlation == "correlated" and holders:
        # Shared error: with probability (1-p), flip a random half of holders together
        shared_error = rng.random() >= reliability
        half = list(holders)
        rng.shuffle(half)
        group = set(half[: max(1, len(half) // 2)])
        if shared_error:
            for n in group:
                raw_bits[n] = 1 - y
            # remaining holders keep independent draws already stored
        else:
            for n in group:
                raw_bits[n] = y

    adv_n = int(round(adversarial_fraction * len(holders)))
    adv_candidates = list(holders)
    rng.shuffle(adv_candidates)
    adversarial_nodes = set(adv_candidates[:adv_n])

    for n in holders:
        bit = raw_bits[n]
        w = base_w
        if n in adversarial_nodes:
            bit = 1 - y  # misleading toward wrong class
            w = base_w * adversarial_weight_boost
        tok = _opaque_token(seed, serial)
        token_serials[tok] = serial
        serial += 1
        local[n] = EvidenceItem(token=tok, bit=bit, weight=w)

    return EvidenceBundle(
        ground_truth=y,
        local_items=local,
        adversarial_nodes=adversarial_nodes,
        reliability=reliability,
        correlation=correlation,
        distribution=distribution,
        token_serials=token_serials,
    )


def relabel_evidence(bundle: EvidenceBundle, perm: Dict[Any, Any]) -> EvidenceBundle:
    """Apply a node relabelling to local item placement. Tokens unchanged."""
    new_local = {perm[n]: item for n, item in bundle.local_items.items()}
    new_adv = {perm[n] for n in bundle.adversarial_nodes}
    return EvidenceBundle(
        ground_truth=bundle.ground_truth,
        local_items=new_local,
        adversarial_nodes=new_adv,
        reliability=bundle.reliability,
        correlation=bundle.correlation,
        distribution=bundle.distribution,
        token_serials=dict(bundle.token_serials),
    )
