from __future__ import annotations

from dataclasses import dataclass, field, replace
from datetime import datetime, timezone
from typing import Any, Mapping, Sequence


from ..core.ids import EventId, RevisionId, TickId, WorldId
from .planner_context import Goal, PlanningEvent

def deterministic_hash(seed: str) -> int:
    s = str(seed or "")
    val = hash(s) % (2**32)
    return abs(val)



def _goal_event_id(world_id: WorldId, event_type: str, goal_id: str, tick_number: int, index: int) -> EventId:
    revision = RevisionId.new(world_id, TickId.new(world_id, tick_number), index, {"event_type": event_type, "goal_id": goal_id})
    return EventId.new(revision, index, {"event_type": event_type, "goal_id": goal_id})


def _goal_id(world_id: WorldId, subject: str, kind: str, entity_id: str | None, tick_number: int, index: int) -> str:
    seed = f"{world_id.value}|{subject}|{kind}|{entity_id}|{tick_number}|{index}"
    return f"id_{deterministic_hash(seed)}"


@dataclass
class GoalManager:
    world_id: WorldId
    goals: dict[str, Goal] = field(default_factory=dict)
    events: list[PlanningEvent] = field(default_factory=list)
    _sequence: int = field(default=0, init=False, repr=False)

    def create_goal(
        self,
        *,
        subject: str,
        kind: str,
        entity_id=None,
        target_state: Mapping[str, Any] | None = None,
        priority: int = 0,
        utility: float = 0.0,
        rationale: str = "",
        deadline_tick: int | None = None,
        window_start_tick: int | None = None,
        window_end_tick: int | None = None,
        horizon_ticks: int = 1,
        provenance: Mapping[str, Any] | None = None,
        confidence: float = 1.0,
        constraints: Sequence[str] | None = None,
        interruption_policy: str = "suspend",
        created_tick: int = 0,
        created_revision: RevisionId | None = None,
        metadata: Mapping[str, Any] | None = None,
    ) -> Goal:
        self._sequence += 1
        goal = Goal(
            goal_id=_goal_id(self.world_id, subject, kind, None if entity_id is None else str(entity_id.value), created_tick, self._sequence),
            subject=subject,
            kind=kind,
            entity_id=entity_id,
            target_state={} if target_state is None else dict(target_state),
            priority=priority,
            utility=utility,
            rationale=rationale,
            deadline_tick=deadline_tick,
            window_start_tick=window_start_tick,
            window_end_tick=window_end_tick,
            horizon_ticks=horizon_ticks,
            provenance={} if provenance is None else dict(provenance),
            confidence=confidence,
            constraints=tuple(constraints or ()),
            interruption_policy=interruption_policy,
            status="pending",
            created_tick=created_tick,
            created_revision=created_revision,
            metadata={} if metadata is None else dict(metadata),
        )
        self.goals[goal.goal_id] = goal
        self._emit("GoalCreated", goal, created_tick, created_revision)
        return goal

    def submit_goal(self, goal: Goal) -> Goal:
        self.goals[goal.goal_id] = goal
        self._emit("GoalCreated", goal, goal.created_tick, goal.created_revision)
        return goal

    def get_goal(self, goal_id: str) -> Goal | None:
        return self.goals.get(str(goal_id))

    def list_goals(self, *, include_terminal: bool = False) -> tuple[Goal, ...]:
        goals = self.goals.values()
        if include_terminal:
            return tuple(sorted(goals, key=lambda goal: (-goal.priority, goal.goal_id)))
        return tuple(sorted((goal for goal in goals if goal.status not in {"completed", "cancelled", "expired"}), key=lambda goal: (-goal.priority, goal.goal_id)))
    
    def cleanup(self, *, current_tick: int) -> int:
        """Remove completed goals to prevent memory explosion."""
        removed = 0
        to_remove = []
        
        for goal_id, goal in self.goals.items():
            # Remove goals that are completed, cancelled, or expired
            if goal.status in {"completed", "cancelled", "expired"}:
                to_remove.append(goal_id)
            # Remove goals that are far in the past (created_tick < current_tick - 10)
            elif goal.created_tick < current_tick - 10:
                to_remove.append(goal_id)
        
        for goal_id in to_remove:
            del self.goals[goal_id]
            removed += 1
        
        return removed


    def has_outstanding_goal(self, entity_id, kind: str, subject_phrase: str = "") -> bool:
        """True if the entity already has a non-terminal goal of this kind.

        Used by goal generators to stay idempotent: without this, hunger/social/
        movement goals were re-created every tick and re-planned forever, which
        drove Eat/Drink/Walk spam and prevented goals from ever settling.

        Phrase is matched by containment because subjects are formatted as
        "{name} {verb} {noun}" (e.g. "Aria seek food"), so a bare prefix of
        "seek food" would never match.
        """
        for goal in self.list_goals(include_terminal=False):
            if goal.entity_id is not None and goal.entity_id == entity_id and goal.kind == kind:
                if not subject_phrase or (subject_phrase in goal.subject):
                    return True
        return False


    def goals_for_entity(self, entity_id) -> tuple[Goal, ...]:
        return tuple(goal for goal in self.list_goals(include_terminal=True) if goal.entity_id == entity_id)

    def activate(self, goal_id: str, *, tick: int) -> Goal | None:
        return self._set_status(goal_id, "active", tick=tick)

    def complete(self, goal_id: str, *, tick: int, reason: str = "") -> Goal | None:
        goal = self._set_status(goal_id, "completed", tick=tick, reason=reason)
        if goal is not None:
            self._emit("GoalCompleted", goal, tick, goal.created_revision, {"reason": reason})
        return goal

    def cancel(self, goal_id: str, *, tick: int, reason: str = "") -> Goal | None:
        goal = self._set_status(goal_id, "cancelled", tick=tick, reason=reason)
        if goal is not None:
            self._emit("GoalCancelled", goal, tick, goal.created_revision, {"reason": reason})
        return goal

    def block(self, goal_id: str, *, tick: int, reason: str = "") -> Goal | None:
        return self._set_status(goal_id, "blocked", tick=tick, reason=reason)

    def expire(self, goal_id: str, *, tick: int, reason: str = "") -> Goal | None:
        goal = self._set_status(goal_id, "expired", tick=tick, reason=reason)
        if goal is not None:
            self._emit("GoalExpired", goal, tick, goal.created_revision, {"reason": reason})
        return goal

    def mark_from_state(self, goal_id: str, status: str, *, tick: int, reason: str = "") -> Goal | None:
        goal = self.get_goal(goal_id)
        if goal is None:
            return None
        if goal.status == status:
            return goal
        updated = replace(goal, status=status)
        self.goals[goal.goal_id] = updated
        self._emit(f"Goal{status.title()}", updated, tick, updated.created_revision, {"reason": reason})
        return updated

    def outstanding(self) -> tuple[Goal, ...]:
        return self.list_goals(include_terminal=False)

    def history(self) -> tuple[PlanningEvent, ...]:
        return tuple(self.events)

    def _set_status(self, goal_id: str, status: str, *, tick: int, reason: str = "") -> Goal | None:
        goal = self.goals.get(str(goal_id))
        if goal is None:
            return None
        if goal.status == status:
            return goal
        updated = replace(goal, status=status)
        self.goals[goal.goal_id] = updated
        self._emit(f"Goal{status.title()}", updated, tick, updated.created_revision, {"reason": reason})
        return updated

    def _emit(
        self,
        event_type: str,
        goal: Goal,
        tick_number: int,
        revision_id: RevisionId | None,
        payload: Mapping[str, Any] | None = None,
    ) -> PlanningEvent:
        event = PlanningEvent(
            event_id=_goal_event_id(self.world_id, event_type, goal.goal_id, tick_number, len(self.events) + 1),
            world_id=self.world_id,
            event_type=event_type,
            timestamp=datetime.now(timezone.utc),
            tick_id=TickId.new(self.world_id, tick_number),
            revision_id=revision_id,
            goal_id=goal.goal_id,
            payload={} if payload is None else dict(payload),
            metadata={"goal_status": goal.status},
        )
        self.events.append(event)
        return event
