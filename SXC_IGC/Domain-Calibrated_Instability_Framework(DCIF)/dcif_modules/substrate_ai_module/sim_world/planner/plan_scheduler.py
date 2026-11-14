from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Mapping


from ..core.ids import EventId, RevisionId, TickId, WorldId
from .planner_context import PlanProposal, PlanningEvent

def deterministic_hash(seed: str) -> int:
    s = str(seed or "")
    val = hash(s) % (2**32)
    return abs(val)



def _plan_event_id(world_id: WorldId, event_type: str, plan_id: str, tick_number: int, index: int) -> EventId:
    revision = RevisionId.new(world_id, TickId.new(world_id, tick_number), index, {"event_type": event_type, "plan_id": plan_id})
    return EventId.new(revision, index, {"event_type": event_type, "plan_id": plan_id})


def _scheduled_plan_id(world_id: WorldId, plan: PlanProposal, tick_number: int, index: int) -> str:
    seed = f"{world_id.value}|{plan.plan_id}|{tick_number}|{index}"
    return f"id_{deterministic_hash(seed)}"


@dataclass(frozen=True, slots=True)
class ScheduledPlan:
    scheduled_plan_id: str
    plan: PlanProposal
    scheduled_tick: int
    execute_tick: int
    status: str = "future"
    interval_ticks: int | None = None
    remaining_runs: int | None = None
    cancelled_reason: str = ""
    window_start_tick: int | None = None
    window_end_tick: int | None = None
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        object.__setattr__(self, "scheduled_plan_id", str(self.scheduled_plan_id))
        object.__setattr__(self, "status", str(self.status))
        object.__setattr__(self, "cancelled_reason", str(self.cancelled_reason))
        if self.interval_ticks is not None:
            object.__setattr__(self, "interval_ticks", int(self.interval_ticks))
        if self.remaining_runs is not None:
            object.__setattr__(self, "remaining_runs", int(self.remaining_runs))
        if self.window_start_tick is not None:
            object.__setattr__(self, "window_start_tick", int(self.window_start_tick))
        if self.window_end_tick is not None:
            object.__setattr__(self, "window_end_tick", int(self.window_end_tick))
        object.__setattr__(self, "metadata", MappingProxyType({} if self.metadata is None else dict(self.metadata)))


from types import MappingProxyType


@dataclass
class PlanScheduler:
    world_id: WorldId
    records: dict[str, ScheduledPlan] = field(default_factory=dict)
    events: list[PlanningEvent] = field(default_factory=list)
    _sequence: int = field(default=0, init=False, repr=False)

    def schedule_immediate(self, plan: PlanProposal, *, tick_number: int) -> ScheduledPlan:
        return self._register(plan, scheduled_tick=tick_number, execute_tick=tick_number, status="immediate")

    def schedule_future(self, plan: PlanProposal, *, execute_tick: int, tick_number: int) -> ScheduledPlan:
        status = "future" if execute_tick > tick_number else "immediate"
        return self._register(plan, scheduled_tick=tick_number, execute_tick=execute_tick, status=status)

    def schedule_delayed(self, plan: PlanProposal, *, delay_ticks: int, tick_number: int) -> ScheduledPlan:
        execute_tick = tick_number + max(0, int(delay_ticks))
        status = "delayed" if execute_tick > tick_number else "immediate"
        return self._register(plan, scheduled_tick=tick_number, execute_tick=execute_tick, status=status)

    def schedule_recurring(
        self,
        plan: PlanProposal,
        *,
        interval_ticks: int,
        tick_number: int,
        occurrences: int | None = None,
    ) -> ScheduledPlan:
        execute_tick = tick_number + max(1, int(interval_ticks))
        return self._register(
            plan,
            scheduled_tick=tick_number,
            execute_tick=execute_tick,
            status="recurring",
            interval_ticks=max(1, int(interval_ticks)),
            remaining_runs=occurrences,
        )

    def cancel(self, scheduled_plan_id: str, *, reason: str = "") -> ScheduledPlan | None:
        record = self.records.get(str(scheduled_plan_id))
        if record is None:
            return None
        updated = ScheduledPlan(
            scheduled_plan_id=record.scheduled_plan_id,
            plan=record.plan,
            scheduled_tick=record.scheduled_tick,
            execute_tick=record.execute_tick,
            status="cancelled",
            interval_ticks=record.interval_ticks,
            remaining_runs=record.remaining_runs,
            cancelled_reason=reason,
            window_start_tick=record.window_start_tick,
            window_end_tick=record.window_end_tick,
            metadata=record.metadata,
        )
        self.records[updated.scheduled_plan_id] = updated
        self._emit("PlanCancelled", updated.plan, updated.scheduled_tick, {"reason": reason}, updated.scheduled_plan_id)
        return updated

    def mark_executed(self, scheduled_plan_id: str, *, tick_number: int) -> ScheduledPlan | None:
        record = self.records.get(str(scheduled_plan_id))
        if record is None:
            return None
        updated = ScheduledPlan(
            scheduled_plan_id=record.scheduled_plan_id,
            plan=record.plan,
            scheduled_tick=record.scheduled_tick,
            execute_tick=record.execute_tick,
            status="executed",
            interval_ticks=record.interval_ticks,
            remaining_runs=None if record.remaining_runs is None else max(0, record.remaining_runs - 1),
            cancelled_reason=record.cancelled_reason,
            window_start_tick=record.window_start_tick,
            window_end_tick=record.window_end_tick,
            metadata=record.metadata,
        )
        self.records[updated.scheduled_plan_id] = updated
        self._emit("PlanScheduled", updated.plan, tick_number, {"execute_tick": updated.execute_tick}, updated.scheduled_plan_id)
        if updated.interval_ticks is not None and (updated.remaining_runs is None or updated.remaining_runs > 0):
            next_tick = tick_number + updated.interval_ticks
            self._sequence += 1
            rescheduled = ScheduledPlan(
                scheduled_plan_id=_scheduled_plan_id(self.world_id, updated.plan, tick_number, self._sequence),
                plan=updated.plan,
                scheduled_tick=tick_number,
                execute_tick=next_tick,
                status="recurring",
                interval_ticks=updated.interval_ticks,
                remaining_runs=updated.remaining_runs,
                window_start_tick=updated.window_start_tick,
                window_end_tick=updated.window_end_tick,
                metadata=updated.metadata,
            )
            self.records[rescheduled.scheduled_plan_id] = rescheduled
        return updated

    def due_plans(self, tick_number: int) -> tuple[ScheduledPlan, ...]:
        return tuple(
            record
            for record in sorted(self.records.values(), key=lambda item: (item.execute_tick, -item.plan.priority, item.plan.plan_id))
            if record.status in {"immediate", "future", "delayed", "recurring"} and record.execute_tick <= tick_number
        )

    def expire_due(self, tick_number: int) -> tuple[ScheduledPlan, ...]:
        expired: list[ScheduledPlan] = []
        for record in list(self.records.values()):
            if record.status in {"cancelled", "executed", "expired"}:
                continue
            if record.window_end_tick is not None and tick_number > record.window_end_tick:
                updated = ScheduledPlan(
                    scheduled_plan_id=record.scheduled_plan_id,
                    plan=record.plan,
                    scheduled_tick=record.scheduled_tick,
                    execute_tick=record.execute_tick,
                    status="expired",
                    interval_ticks=record.interval_ticks,
                    remaining_runs=record.remaining_runs,
                    cancelled_reason="window expired",
                    window_start_tick=record.window_start_tick,
                    window_end_tick=record.window_end_tick,
                    metadata=record.metadata,
                )
                self.records[updated.scheduled_plan_id] = updated
                expired.append(updated)
                self._emit("PlanExpired", updated.plan, tick_number, {"window_end_tick": record.window_end_tick}, updated.scheduled_plan_id)
        return tuple(expired)

    def list(self) -> tuple[ScheduledPlan, ...]:
        # Return only active plans (not completed or cancelled)
        active = {k: v for k, v in self.records.items() if v.status in {"future", "immediate", "delayed", "recurring"}}
        return tuple(sorted(active.values(), key=lambda item: (item.execute_tick, item.scheduled_tick, -item.plan.priority, item.plan.plan_id)))
    
    def cleanup(self, *, current_tick: int) -> int:
        """Remove completed plans to prevent memory explosion."""
        removed = 0
        to_remove = []
        
        for plan_id, record in self.records.items():
            # Remove plans that are completed, cancelled, or expired
            if record.status in {"completed", "cancelled", "expired"}:
                to_remove.append(plan_id)
            # Remove plans that are far in the past (execute_tick < current_tick - 5)
            elif record.execute_tick < current_tick - 5:
                to_remove.append(plan_id)
        
        for plan_id in to_remove:
            del self.records[plan_id]
            removed += 1
        
        return removed

    def _register(
        self,
        plan: PlanProposal,
        *,
        scheduled_tick: int,
        execute_tick: int,
        status: str,
        interval_ticks: int | None = None,
        remaining_runs: int | None = None,
    ) -> ScheduledPlan:
        self._sequence += 1
        record = ScheduledPlan(
            scheduled_plan_id=_scheduled_plan_id(self.world_id, plan, scheduled_tick, self._sequence),
            plan=plan,
            scheduled_tick=scheduled_tick,
            execute_tick=execute_tick,
            status=status,
            interval_ticks=interval_ticks,
            remaining_runs=remaining_runs,
            window_start_tick=plan.creation_tick,
            window_end_tick=None,
            metadata=plan.metadata,
        )
        self.records[record.scheduled_plan_id] = record
        self._emit("PlanScheduled", plan, scheduled_tick, {"execute_tick": execute_tick}, record.scheduled_plan_id)
        return record

    def _emit(
        self,
        event_type: str,
        plan: PlanProposal,
        tick_number: int,
        payload: Mapping[str, Any] | None = None,
        scheduled_plan_id: str | None = None,
    ) -> PlanningEvent:
        event = PlanningEvent(
            event_id=_plan_event_id(self.world_id, event_type, plan.plan_id, tick_number, len(self.events) + 1),
            world_id=self.world_id,
            event_type=event_type,
            timestamp=datetime.now(timezone.utc),
            tick_id=TickId.new(self.world_id, tick_number),
            revision_id=plan.planning_revision,
            goal_id=plan.goal_id,
            plan_id=plan.plan_id,
            payload={} if payload is None else dict(payload),
            metadata={"plan_status": plan.status, "scheduled_plan_id": scheduled_plan_id},
        )
        self.events.append(event)
        return event
