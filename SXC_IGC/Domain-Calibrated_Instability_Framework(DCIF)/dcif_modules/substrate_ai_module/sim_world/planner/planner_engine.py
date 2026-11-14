from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Mapping, Sequence

from .goal_manager import GoalManager
from ..core.ids import EventId, RevisionId, TickId, WorldId
from .plan_generator import PlanGenerator
from .plan_scheduler import PlanScheduler
from .plan_validator import PlanValidationResult, PlanValidator
from .planner_context import Goal, PlanProposal, PlannerContext, PlanningDiagnostics, PlanningEvent, PlanningPhaseReport


def _flatten_requests(plans: Sequence[PlanProposal]) -> tuple[Any, ...]:
    requests: list[Any] = []
    for plan in plans:
        requests.extend(plan.action_requests)
    return tuple(requests)


@dataclass
class PlannerEngine:
    world_id: WorldId
    goal_manager: GoalManager = field(init=False)
    plan_generator: PlanGenerator = field(init=False)
    plan_validator: PlanValidator = field(default_factory=PlanValidator)
    plan_scheduler: PlanScheduler = field(init=False)
    events: list[PlanningEvent] = field(default_factory=list)
    last_diagnostics: PlanningDiagnostics | None = field(default=None, init=False, repr=False)
    last_future_action_requests: tuple[Any, ...] = field(default_factory=tuple, init=False, repr=False)

    def __post_init__(self) -> None:
        self.goal_manager = GoalManager(self.world_id)
        self.plan_generator = PlanGenerator(self.world_id)
        self.plan_scheduler = PlanScheduler(self.world_id)

    def plan(
        self,
        context: PlannerContext,
        *,
        goals: Sequence[Goal] | None = None,
    ) -> tuple[PlanProposal, ...]:
        planning_goals = tuple(goals or context.outstanding_goals or self.goal_manager.outstanding())
        phase_reports: list[PlanningPhaseReport] = []
        evaluated_goals: list[Goal] = []
        generated_plans: list[PlanProposal] = []
        validated_results: list[PlanValidationResult] = []
        rejected_count = 0
        events_before = len(self.events)
        self.last_future_action_requests = ()

        evaluated_goals.extend(self._evaluate_goals(context, planning_goals))
        phase_reports.append(PlanningPhaseReport("load_context", 0, metadata={"snapshot_tick": str(context.current_tick.value)}))
        phase_reports.append(PlanningPhaseReport("evaluate_goals", len(evaluated_goals), accepted_count=len(evaluated_goals)))

        candidates = self.plan_generator.generate(context, evaluated_goals)
        phase_reports.append(PlanningPhaseReport("generate_candidates", len(candidates), accepted_count=len(candidates)))

        validated = self.plan_validator.validate_many(context, candidates, evaluated_goals)
        for result in validated:
            validated_results.append(result)
            if result.valid:
                generated_plans.append(result.plan)
            else:
                rejected_count += 1
                self._emit(
                    "PlanRejected",
                    context,
                    goal_id=result.plan.goal_id,
                    plan_id=result.plan.plan_id,
                    payload={
                        "failures": [
                            {"code": failure.code, "message": failure.message, "details": dict(failure.details)}
                            for failure in result.failures
                        ]
                    },
                )
        phase_reports.append(PlanningPhaseReport("validate_candidates", len(validated), accepted_count=len(generated_plans), rejected_count=rejected_count))

        estimated = tuple(
            plan if "estimated_start_tick" in plan.metadata else self._with_estimated_schedule(context, plan)
            for plan in generated_plans
        )
        phase_reports.append(PlanningPhaseReport("estimate_schedule", len(estimated), accepted_count=len(estimated)))

        prioritized = tuple(self._prioritize(context, estimated))
        phase_reports.append(PlanningPhaseReport("prioritize_plans", len(prioritized), accepted_count=len(prioritized)))

        future_action_requests = _flatten_requests(prioritized)
        for plan in prioritized:
            scheduled = self.plan_scheduler.schedule_future(
                plan,
                execute_tick=plan.metadata.get("estimated_start_tick", context.current_tick_number + 1),
                tick_number=context.current_tick_number,
            )
            self._emit("PlanGenerated", context, goal_id=plan.goal_id, plan_id=plan.plan_id, payload={"scheduled_plan_id": scheduled.scheduled_plan_id})
        self.last_future_action_requests = future_action_requests

        diagnostics = PlanningDiagnostics(
            world_id=context.world_id,
            tick_id=context.current_tick,
            tick_number=context.current_tick_number,
            committed_revision=context.committed_revision,
            goals_evaluated=len(evaluated_goals),
            plans_generated=len(prioritized),
            plans_validated=len(validated),
            plans_rejected=rejected_count,
            phase_reports=tuple(phase_reports),
            future_action_requests=self.last_future_action_requests,
            events=tuple(self.events[events_before:]),
            metadata={"goal_ids": [goal.goal_id for goal in evaluated_goals]},
        )
        self.last_diagnostics = diagnostics
        return prioritized

    def schedule_accepted_plans(self, context: PlannerContext, plans: Sequence[PlanProposal]) -> tuple[Any, ...]:
        scheduled: list[Any] = []
        for plan in plans:
            scheduled.append(self.plan_scheduler.schedule_future(plan, execute_tick=plan.metadata.get("estimated_start_tick", context.current_tick_number + 1), tick_number=context.current_tick_number))
        return tuple(scheduled)

    def _evaluate_goals(self, context: PlannerContext, goals: Sequence[Goal]) -> list[Goal]:
        evaluated: list[Goal] = []
        for goal in goals:
            if goal.status in {"cancelled", "completed", "expired"}:
                continue
            if self._goal_satisfied(context, goal):
                completed = self.goal_manager.complete(goal.goal_id, tick=context.current_tick_number, reason="goal satisfied")
                if completed is not None:
                    evaluated.append(completed)
                continue
            if goal.deadline_tick is not None and context.current_tick_number > goal.deadline_tick:
                expired = self.goal_manager.expire(goal.goal_id, tick=context.current_tick_number, reason="deadline elapsed")
                if expired is not None:
                    evaluated.append(expired)
                continue
            active = self.goal_manager.activate(goal.goal_id, tick=context.current_tick_number)
            if active is not None:
                evaluated.append(active)
        return evaluated

    def _goal_satisfied(self, context: PlannerContext, goal: Goal) -> bool:
        if not goal.target_state:
            return False
        actor = dict(context.snapshot.state.get("entities", {})).get(str(goal.entity_id.value)) if goal.entity_id is not None else None
        if actor is None:
            return False
        components = dict(actor.get("components", {}))
        metadata = dict(actor.get("metadata", {}))
        desired = dict(goal.target_state)
        if "room" in desired:
            room = dict(components.get("TransformComponent", {})).get("room")
            if room == desired["room"]:
                return True
        if "held_item" in desired:
            if str(desired["held_item"]) in set(str(item) for item in metadata.get("holding", ())):
                return True
        if "status" in desired and metadata.get("status") == desired["status"]:
            return True
        # A sleep goal is satisfied when the villager's energy has recovered to
        # the wake threshold (0.5), not merely while status == "sleeping". The
        # needs-domain flips status to "awake" once energy >= 0.5, so trusting
        # only status=="sleeping" orphans the sleep goal forever -> it stays
        # active and the dedup guard blocks future sleep goals. Completing it on
        # energy recovery lets the sleep need re-fire normally later.
        if "status" in desired and desired["status"] == "sleeping":
            needs = dict(dict(components.get("NeedsComponent", {}) or {}).get("needs", {}))
            if float(needs.get("energy", 0.0)) >= 0.5:
                return True
        if goal.kind.lower() in {"hunger", "thirst", "survival"}:
            needs = dict(dict(components.get("NeedsComponent", {})).get("needs", {}))
            threshold = float(desired.get("threshold", 0.25))
            key = "hunger" if goal.kind.lower() != "thirst" else "thirst"
            if float(needs.get(key, 1.0)) <= threshold:
                return True
        # A social/conversation goal is satisfied when the villager actually
        # talks, not only when they reach the tavern. Without this, the (properly
        # deduped) single socialize goal replans Talk every tick forever because
        # the actor never leaves the farm -> runaway Talk spam that drowns work
        # goals (farmers 1592 Talks, fields never planted).
        kind = goal.kind.lower()
        if kind in {"conversation", "talk", "approach", "socialize", "social"}:
            if str(metadata.get("last_action", "")) == "Talk":
                return True
        return False

    def _prioritize(self, context: PlannerContext, plans: Sequence[PlanProposal]) -> list[PlanProposal]:
        return sorted(
            plans,
            key=lambda plan: (
                -plan.priority,
                plan.estimated_cost,
                plan.estimated_duration,
                plan.goal_id,
                plan.plan_id,
            ),
        )

    def _with_estimated_schedule(self, context: PlannerContext, plan: PlanProposal) -> PlanProposal:
        metadata = dict(plan.metadata)
        metadata.setdefault("estimated_start_tick", context.current_tick_number + 1)
        metadata.setdefault("estimated_end_tick", context.current_tick_number + plan.estimated_duration)
        return PlanProposal(
            plan_id=plan.plan_id,
            goal_id=plan.goal_id,
            entity_id=plan.entity_id,
            priority=plan.priority,
            estimated_cost=plan.estimated_cost,
            estimated_duration=plan.estimated_duration,
            action_requests=plan.action_requests,
            dependencies=plan.dependencies,
            required_resources=plan.required_resources,
            confidence=plan.confidence,
            creation_tick=plan.creation_tick,
            planning_revision=plan.planning_revision,
            status=plan.status,
            goal_subject=plan.goal_subject,
            metadata=metadata,
        )

    def _emit(
        self,
        event_type: str,
        context: PlannerContext,
        *,
        goal_id: str | None = None,
        plan_id: str | None = None,
        payload: Mapping[str, Any] | None = None,
    ) -> PlanningEvent:
        revision = RevisionId.new(context.world_id, context.current_tick, len(self.events) + 1, {"event_type": event_type, "goal_id": goal_id, "plan_id": plan_id})
        event = PlanningEvent(
            event_id=EventId.new(revision, len(self.events) + 1, {"event_type": event_type, "goal_id": goal_id, "plan_id": plan_id}),
            world_id=context.world_id,
            event_type=event_type,
            timestamp=datetime.now(timezone.utc),
            tick_id=context.current_tick,
            revision_id=context.committed_revision,
            goal_id=goal_id,
            plan_id=plan_id,
            payload={} if payload is None else dict(payload),
            metadata={"tick_number": context.current_tick_number},
        )
        self.events.append(event)
        return event
