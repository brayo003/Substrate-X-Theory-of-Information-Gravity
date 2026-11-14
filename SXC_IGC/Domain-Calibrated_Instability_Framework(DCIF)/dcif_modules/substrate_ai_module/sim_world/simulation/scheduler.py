from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Mapping


from ..core.contracts import freeze_value
from .simulation_context import ActionRequest, ScheduledAction

def deterministic_hash(seed: str) -> int:
    s = str(seed or "")
    val = hash(s) % (2**32)
    return abs(val)



def _action_id(request: ActionRequest, scheduled_tick: int, execute_tick: int, index: int) -> str:
    seed = f"{request.actor_id.value}|{request.action}|{request.correlation_id}|{scheduled_tick}|{execute_tick}|{index}"
    return f"id_{deterministic_hash(seed)}"


@dataclass
class ActionScheduler:
    records: dict[str, ScheduledAction] = field(default_factory=dict)
    _sequence: int = field(default=0, init=False, repr=False)

    def schedule_immediate(
        self,
        request: ActionRequest,
        *,
        tick_number: int,
        metadata: Mapping[str, Any] | None = None,
    ) -> ScheduledAction:
        return self._register(request, scheduled_tick=tick_number, execute_tick=tick_number, status="immediate", metadata=metadata)

    def schedule_future_tick(
        self,
        request: ActionRequest,
        *,
        execute_tick: int,
        tick_number: int,
        metadata: Mapping[str, Any] | None = None,
    ) -> ScheduledAction:
        status = "future" if execute_tick > tick_number else "immediate"
        return self._register(request, scheduled_tick=tick_number, execute_tick=execute_tick, status=status, metadata=metadata)

    def schedule_delayed(
        self,
        request: ActionRequest,
        *,
        delay_ticks: int,
        tick_number: int,
        metadata: Mapping[str, Any] | None = None,
    ) -> ScheduledAction:
        execute_tick = tick_number + max(0, int(delay_ticks))
        status = "delayed" if execute_tick > tick_number else "immediate"
        return self._register(request, scheduled_tick=tick_number, execute_tick=execute_tick, status=status, metadata=metadata)

    def schedule_recurring(
        self,
        request: ActionRequest,
        *,
        interval_ticks: int,
        tick_number: int,
        occurrences: int | None = None,
        metadata: Mapping[str, Any] | None = None,
    ) -> ScheduledAction:
        execute_tick = tick_number + max(1, int(interval_ticks))
        return self._register(
            request,
            scheduled_tick=tick_number,
            execute_tick=execute_tick,
            status="recurring",
            interval_ticks=max(1, int(interval_ticks)),
            remaining_runs=occurrences,
            metadata=metadata,
        )

    def cancel(self, action_id: str, *, reason: str = "") -> ScheduledAction | None:
        record = self.records.get(str(action_id))
        if record is None:
            return None
        self.records[str(action_id)] = ScheduledAction(
            action_id=record.action_id,
            request=record.request,
            scheduled_tick=record.scheduled_tick,
            execute_tick=record.execute_tick,
            status="cancelled",
            interval_ticks=record.interval_ticks,
            remaining_runs=record.remaining_runs,
            created_tick=record.created_tick,
            cancelled_reason=reason,
            metadata=record.metadata,
        )
        return self.records[str(action_id)]

    def due_actions(self, tick_number: int) -> tuple[ScheduledAction, ...]:
        return tuple(
            record
            for record in sorted(
                self.records.values(),
                key=lambda item: (item.execute_tick, -item.request.priority, item.request.correlation_id, item.action_id),
            )
            if record.status in {"immediate", "future", "delayed", "recurring"} and record.execute_tick <= tick_number
        )

    def mark_executed(self, action_id: str, *, tick_number: int) -> ScheduledAction | None:
        record = self.records.get(str(action_id))
        if record is None:
            return None
        updated = ScheduledAction(
            action_id=record.action_id,
            request=record.request,
            scheduled_tick=record.scheduled_tick,
            execute_tick=record.execute_tick,
            status="executed",
            interval_ticks=record.interval_ticks,
            remaining_runs=None if record.remaining_runs is None else max(0, record.remaining_runs - 1),
            created_tick=record.created_tick,
            cancelled_reason=record.cancelled_reason,
            metadata=record.metadata,
        )
        self.records[str(action_id)] = updated
        if updated.interval_ticks is not None and (updated.remaining_runs is None or updated.remaining_runs > 0):
            next_tick = tick_number + updated.interval_ticks
            rescheduled = ScheduledAction(
                action_id=_action_id(updated.request, updated.scheduled_tick, next_tick, self._sequence + 1),
                request=updated.request,
                scheduled_tick=tick_number,
                execute_tick=next_tick,
                status="recurring",
                interval_ticks=updated.interval_ticks,
                remaining_runs=updated.remaining_runs,
                created_tick=tick_number,
                metadata=updated.metadata,
            )
            self._sequence += 1
            self.records[rescheduled.action_id] = rescheduled
        return updated

    def list(self) -> tuple[ScheduledAction, ...]:
        return tuple(
            sorted(
                self.records.values(),
                key=lambda item: (item.execute_tick, item.scheduled_tick, item.request.priority, item.action_id),
            )
        )

    def _register(
        self,
        request: ActionRequest,
        *,
        scheduled_tick: int,
        execute_tick: int,
        status: str,
        interval_ticks: int | None = None,
        remaining_runs: int | None = None,
        metadata: Mapping[str, Any] | None = None,
    ) -> ScheduledAction:
        self._sequence += 1
        action_id = _action_id(request, scheduled_tick, execute_tick, self._sequence)
        record = ScheduledAction(
            action_id=action_id,
            request=request,
            scheduled_tick=scheduled_tick,
            execute_tick=execute_tick,
            status=status,
            interval_ticks=interval_ticks,
            remaining_runs=remaining_runs,
            created_tick=scheduled_tick,
            metadata={} if metadata is None else dict(metadata),
        )
        self.records[action_id] = record
        return record
