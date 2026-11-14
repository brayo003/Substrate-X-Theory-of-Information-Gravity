from __future__ import annotations

from typing import Any

from ...core.contracts import TransitionProposal
from ...simulation.simulation_engine import SimulationEngine


def register(engine: SimulationEngine) -> None:
    engine.register_domain("time", lambda engine, context: (apply(context),))


def day_phase(tick_number: int) -> str:
    hour = (tick_number % 24)
    if hour < 6:
        return "night"
    if hour < 12:
        return "morning"
    if hour < 18:
        return "afternoon"
    return "evening"


def weekday_name(tick_number: int) -> str:
    days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    return days[(tick_number // 24) % 7]


def apply(context: Any) -> TransitionProposal:
    tick_number = int(context.tick_number)
    tick_context = getattr(context, "tick_context", None)
    tick_id = getattr(tick_context, "tick_id", None) if tick_context else None
    correlation_id = getattr(tick_context, "correlation_id", None) if tick_context else None
    
    # Fix: Ensure state_revision is None when there's no current revision
    state_revision = context.committed_revision
    if state_revision == 0 and context.committed_revision is None:
        state_revision = None
    
    return TransitionProposal(
        world_id=context.world_id,
        tick_id=tick_id,
        state_revision=state_revision,
        correlation_id=correlation_id,
        subject="domain.time",
        patch={
            "time": {
                "tick_number": tick_number,
                "hour": tick_number % 24,
                "phase": day_phase(tick_number),
                "weekday": weekday_name(tick_number),
            }
        },
        description="time domain update",
        metadata={"domain": "time", "phase": day_phase(tick_number)},
    )
