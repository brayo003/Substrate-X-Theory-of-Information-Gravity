"""Locked experimental condition matrix (chosen before seeing results)."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Dict, List


@dataclass(frozen=True)
class Condition:
    condition_id: str
    n_states: int
    edge_prob: float
    initial_blocks: int
    graph_steps: int
    removal_age: int
    reliability: float
    correlation: str
    distribution: str
    max_rounds: int
    send_cap: int
    max_messages: int
    failure_fraction: float  # 0 = none
    adversarial_fraction: float
    notes: str


# Graph dynamics length matches communication horizon for high budget.
# Medium size / reliability / budget is the primary locked baseline.
BASELINE = Condition(
    condition_id="baseline",
    n_states=12,
    edge_prob=0.25,
    initial_blocks=3,
    graph_steps=40,
    removal_age=5,
    reliability=0.70,
    correlation="independent",
    distribution="balanced",
    max_rounds=15,
    send_cap=2,
    max_messages=5000,
    failure_fraction=0.0,
    adversarial_fraction=0.0,
    notes="Primary locked baseline; n matches preserved graph experiment.",
)


def build_matrix() -> List[Condition]:
    """One-factor-at-a-time + targeted combinations. Values locked a priori."""
    b = BASELINE
    conds = [b]

    def derive(cid, notes, **kwargs):
        d = asdict(b)
        d.update(kwargs)
        d["condition_id"] = cid
        d["notes"] = notes
        return Condition(**d)

    # Reliability
    conds.append(derive("rel_weak", "Weak evidence reliability.", reliability=0.55))
    conds.append(derive("rel_strong", "Strong evidence reliability.", reliability=0.90))
    # Correlation
    conds.append(derive("corr", "Correlated evidence sources.", correlation="correlated"))
    # Distribution
    conds.append(derive("uneven", "Uneven evidence placement (25% holders).",
                        distribution="uneven"))
    # Budget
    conds.append(derive("budget_low", "Low communication budget.",
                        max_rounds=5, send_cap=1, max_messages=400))
    conds.append(derive("budget_high", "High communication budget.",
                        max_rounds=40, send_cap=4, max_messages=20000))
    # Failures
    conds.append(derive("failures", "Controlled exogenous edge failures (20% of R0).",
                        failure_fraction=0.20))
    # Adversarial (separate)
    conds.append(derive("adversarial", "20% adversarial misleading sources.",
                        adversarial_fraction=0.20))
    # Network size
    conds.append(derive("size_small", "Small network.", n_states=8, max_messages=3000))
    conds.append(derive("size_large", "Larger network.", n_states=20, max_messages=12000))
    # Stress combo (pre-registered, not tuned post hoc)
    conds.append(derive(
        "stress_weak_fail",
        "Weak reliability under failures.",
        reliability=0.55, failure_fraction=0.20))
    return conds


SMOKE_CONDITION = Condition(
    condition_id="smoke",
    n_states=8,
    edge_prob=0.25,
    initial_blocks=3,
    graph_steps=10,
    removal_age=5,
    reliability=0.70,
    correlation="independent",
    distribution="balanced",
    max_rounds=5,
    send_cap=2,
    max_messages=500,
    failure_fraction=0.0,
    adversarial_fraction=0.0,
    notes="Smoke test only.",
)


PRIMARY_METRICS = [
    "frac_correct",
    "time_to_correct_agreement",
    "messages_per_correct_node",
    "frac_correct",  # post-failure uses same field under failures condition
    "evidence_coverage",
]

# Distinct primary endpoints for D-CR (for Holm adjustment)
D_CR_PRIMARY = [
    "frac_correct",
    "time_to_correct_agreement",
    "messages_per_correct_node",
    "evidence_coverage",
    "agreement_correct",
]


def condition_to_dict(c: Condition) -> Dict[str, Any]:
    return asdict(c)
