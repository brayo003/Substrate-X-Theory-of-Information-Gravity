from __future__ import annotations

from typing import Any, Iterable, Mapping

from sim_world.core.contracts import TransitionProposal
from sim_world.simulation.simulation_engine import SimulationEngine

from .society_models import (
    VillageState,
    Household,
    CommunalProject,
    ActiveCelebration,
    ActiveEmergency,
    Leadership,
    LaborAllocation,
    clamp,
    make_household_id,
    make_project_id,
    make_emergency_id,
    make_village_id,
    _as_float,
    _as_int,
    _as_mapping,
    _as_tuple_of_str,
    FOOD_CRISIS_RESERVE_PER_PERSON,
    WOOD_RESERVE_MIN_PER_HOUSEHOLD,
    DEFAULT_PROSPERITY,
    DEFAULT_STABILITY,
    DEFAULT_MORALE,
)

from .society_rules import (
    evaluate_village_tick,
    evaluate_emergencies,
    evaluate_communal_projects,
    evaluate_celebrations,
    evaluate_leadership,
    compute_prosperity_components,
    compute_stability_components,
    compute_morale_components,
    derive_resource_shortage,
    derive_emergency_level,
    derive_population_from_entities,
    derive_workforce_from_entities,
    derive_society_goals,
    should_hold_meeting_for,
    labor_priority_for,
)


def register(engine: SimulationEngine) -> None:
    engine.register_domain("society", lambda engine, context: (apply(context),))


def apply(context: Any) -> TransitionProposal:
    # MINIMAL: Return empty patch
    return TransitionProposal(
        world_id=getattr(context, "world_id", None),
        tick_id=getattr(getattr(context, "tick_context", None), "tick_id", None) if hasattr(context, "tick_context") else None,
        state_revision=getattr(context, "committed_revision", None),
        correlation_id=getattr(getattr(context, "tick_context", None), "correlation_id", None) if hasattr(context, "tick_context") else None,
        subject="domain.society",
        patch={"society": {"village_state": {}}},
        description="society domain minimal",
        metadata={"events": []},
    )