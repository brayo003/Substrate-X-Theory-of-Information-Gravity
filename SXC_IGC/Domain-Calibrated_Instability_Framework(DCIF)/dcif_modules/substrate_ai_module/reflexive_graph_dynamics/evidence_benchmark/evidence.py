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


@dataclass(frozen=True)
class NetworkEvidenceView:
    """Protocol-facing view: local items only. No ground_truth attribute."""

    local_items: Dict[Any, Optional[EvidenceItem]]

    def local_item(self, node: Any) -> Optional[EvidenceItem]:
        return self.local_items.get(node)


@dataclass
class EvidenceBundle:
    """Evaluator-side bundle. Nodes / protocol never receive this object."""

    ground_truth: int
    local_items: Dict[Any, Optional[EvidenceItem]]
    adversarial_nodes: Set[Any] = field(default_factory=set)
    reliability: float = 0.7
    correlation: str = "independent"
    distribution: str = "balanced"
    token_serials: Dict[str, int] = field(default_factory=dict)
    # Correlated-model metadata (evaluator diagnostics)
    corr_rho: float = 0.0
    corr_group: Set[Any] = field(default_factory=set)
    correlation_model: str = "independent_bernoulli"

    def node_view(self, node: Any) -> Optional[EvidenceItem]:
        return self.local_items.get(node)

    def network_view(self) -> NetworkEvidenceView:
        """Strip GT: protocol may only see this object."""
        return NetworkEvidenceView(local_items=dict(self.local_items))


def _opaque_token(seed: int, serial: int) -> str:
    payload = f"{seed}|ev|{serial}".encode("utf-8")
    return hashlib.sha256(payload).hexdigest()[:16]


def _weight_from_reliability(p: float) -> float:
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
    corr_rho: float = 0.6,
) -> EvidenceBundle:
    """Generate paired evidence for a seed.

    ## Generative models

    Let holders H ⊆ V, reliability p ∈ (0,1), ground truth y ∈ {0,1}.

    **independent** (`correlation_model = independent_bernoulli`):
      For each i ∈ H independently: P(b_i = y) = p.

    **correlated** (`correlation_model = group_equicorrelated_mixture`):
      Draw a random group G ⊂ H with |G| = max(1, ⌊|H|/2⌋).
      Draw U ~ Uniform(0,1).
      If U < ρ (default ρ=0.6):
        Draw shared bit S with P(S=y)=p; set b_i = S for all i ∈ G.
        For i ∈ H\\G: independent Bernoulli as above.
      Else:
        All i ∈ H independent Bernoulli as above.

      Induced pairwise correlation for i≠j both in G (approximately, for the
      mixture): Corr(b_i, b_j) = ρ · Var(S) / Var(b) under the shared branch,
      and 0 on the independent branch; empirical pairwise correlation is
      recorded in analysis. Exact Var(b_i)=p(1-p) when bits are coded in {0,1}
      with mean p toward y — here we code raw class bits; diagnostics use
      empirical Pearson on {0,1} codes across seeds/holders.

    **Adversarial** (separate): fraction of holders flip to 1-y with weight
    boost; applied after the correlation step.

    The local decision rule remains a **naive weighted (or unweighted) sum**
    that treats known items as independent. Under correlation this is
    statistically misspecified; the correlated condition tests robustness to
    that misspecification, not an optimal dependent-evidence aggregator.
    """
    if correlation not in ("independent", "correlated"):
        raise ValueError(correlation)
    if distribution not in ("balanced", "uneven"):
        raise ValueError(distribution)
    if not (0.0 < reliability < 1.0):
        raise ValueError("reliability must be in (0,1)")
    if not (0.0 <= adversarial_fraction <= 1.0):
        raise ValueError("adversarial_fraction must be in [0,1]")
    if not (0.0 <= corr_rho <= 1.0):
        raise ValueError("corr_rho must be in [0,1]")

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
    corr_group: Set[Any] = set()
    model_name = "independent_bernoulli"
    rho_used = 0.0

    raw_bits: Dict[Any, int] = {}

    if correlation == "independent" or not holders:
        for n in holders:
            raw_bits[n] = y if rng.random() < reliability else (1 - y)
        model_name = "independent_bernoulli"
    else:
        model_name = "group_equicorrelated_mixture"
        rho_used = corr_rho
        half = list(holders)
        rng.shuffle(half)
        g_size = max(1, len(half) // 2)
        corr_group = set(half[:g_size])
        rest = holders - corr_group
        if rng.random() < corr_rho:
            shared = y if rng.random() < reliability else (1 - y)
            for n in corr_group:
                raw_bits[n] = shared
        else:
            for n in corr_group:
                raw_bits[n] = y if rng.random() < reliability else (1 - y)
        for n in rest:
            raw_bits[n] = y if rng.random() < reliability else (1 - y)

    adv_n = int(round(adversarial_fraction * len(holders))) if holders else 0
    adv_candidates = list(holders)
    rng.shuffle(adv_candidates)
    adversarial_nodes = set(adv_candidates[:adv_n])

    for n in holders:
        bit = raw_bits[n]
        w = base_w
        if n in adversarial_nodes:
            bit = 1 - y
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
        corr_rho=rho_used,
        corr_group=corr_group,
        correlation_model=model_name,
    )


def relabel_evidence(bundle: EvidenceBundle, perm: Dict[Any, Any]) -> EvidenceBundle:
    """Apply a node relabelling to local item placement. Tokens unchanged."""
    new_local = {perm[n]: item for n, item in bundle.local_items.items()}
    new_adv = {perm[n] for n in bundle.adversarial_nodes}
    new_group = {perm[n] for n in bundle.corr_group}
    return EvidenceBundle(
        ground_truth=bundle.ground_truth,
        local_items=new_local,
        adversarial_nodes=new_adv,
        reliability=bundle.reliability,
        correlation=bundle.correlation,
        distribution=bundle.distribution,
        token_serials=dict(bundle.token_serials),
        corr_rho=bundle.corr_rho,
        corr_group=new_group,
        correlation_model=bundle.correlation_model,
    )


def empirical_pairwise_bit_correlation(bundles: Sequence[EvidenceBundle]) -> float:
    """Mean Pearson correlation across holder-pairs that co-appear, pooled."""
    # For each bundle, among holders, compute mean pairwise corr contribution
    xs: List[Tuple[float, float]] = []
    # Collect aligned pairs is hard across seeds; instead for each bundle
    # compute average pairwise product moment within holders.
    corrs = []
    for b in bundles:
        holders = [n for n, it in b.local_items.items() if it is not None]
        if len(holders) < 2:
            continue
        bits = [b.local_items[n].bit for n in holders]
        m = sum(bits) / len(bits)
        var = sum((x - m) ** 2 for x in bits) / len(bits)
        if var <= 1e-12:
            corrs.append(1.0)  # all equal
            continue
        s = 0.0
        c = 0
        for i in range(len(bits)):
            for j in range(i + 1, len(bits)):
                s += (bits[i] - m) * (bits[j] - m) / var
                c += 1
        if c:
            corrs.append(s / c)
    if not corrs:
        return float("nan")
    return sum(corrs) / len(corrs)
