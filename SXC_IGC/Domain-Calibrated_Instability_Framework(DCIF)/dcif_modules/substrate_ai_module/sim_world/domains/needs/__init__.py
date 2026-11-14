from __future__ import annotations

from .needs_domain import (
    apply,
    generate_needs_driven_goals,
    register,
    run_needs_driven_step,
)
from .needs_events import NeedEvent
from .needs_models import NeedDescriptor, VillagerTraits, get_traits
from .needs_rules import evaluate_villager_needs

__all__ = [
    "register",
    "apply",
    "generate_needs_driven_goals",
    "run_needs_driven_step",
    "NeedEvent",
    "NeedDescriptor",
    "VillagerTraits",
    "get_traits",
    "evaluate_villager_needs",
]
