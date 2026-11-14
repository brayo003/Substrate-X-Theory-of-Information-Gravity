from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from typing import Any, Mapping, Sequence


from ..core.contracts import RenderProposal, RenderSnapshot, TransitionProposal, VerificationReport, freeze_value
from ..core.ids import EventId, RevisionId, TickId, WorldId
from .q_calibrator import CalibrationApplication, QCalibrator
from .q_metrics import QMetrics, _snapshot_mapping
from .q_observation import CalibrationMetadata, QDiagnostics, QEvent, QObservation
from .transport_context import TransportContext

def deterministic_hash(seed: str) -> int:
    s = str(seed or "")
    val = hash(s) % (2**32)
    return abs(val)



def _tick_time(tick_number: int) -> datetime:
    return datetime(2000, 1, 1, tzinfo=timezone.utc) + timedelta(seconds=max(0, int(tick_number)))


def _event_id(world_id: WorldId, event_type: str, observation_id: str, tick_number: int, index: int) -> EventId:
    revision = RevisionId.new(world_id, TickId.new(world_id, tick_number), index, {"event_type": event_type, "observation_id": observation_id})
    return EventId.new(revision, index, {"event_type": event_type, "observation_id": observation_id})


@dataclass
class TransportEngine:
    metrics: QMetrics = field(default_factory=QMetrics)
    calibrator: QCalibrator = field(default_factory=QCalibrator)
    observations: list[QObservation] = field(default_factory=list)
    events: list[QEvent] = field(default_factory=list)
    last_observation: QObservation | None = field(default=None, init=False, repr=False)
    last_diagnostics: QDiagnostics | None = field(default=None, init=False, repr=False)
    last_calibration: CalibrationMetadata | None = field(default=None, init=False, repr=False)

    def observe(self, context: TransportContext) -> QObservation:
        previous_snapshot = context.previous_snapshot
        current_snapshot = context.current_snapshot
        representation_type = context.representation_type
        tick_number = context.tick_number
        previous_revision = context.previous_revision
        current_revision = context.current_revision

        metric_values = dict(self.metrics.compute_all(previous_snapshot, current_snapshot, context=context))
        calibration = self.calibrator.apply(metric_values, context=context, tick_number=tick_number, representation_type=representation_type)
        observation_time = _tick_time(tick_number)
        observation_id = self._observation_id(
            context.world_id,
            previous_revision=previous_revision,
            current_revision=current_revision,
            representation_type=representation_type,
            calibration_metadata=calibration.calibration_metadata,
            metric_values=metric_values,
            correlation_id=context.correlation_id,
            tick_number=tick_number,
        )

        diagnostics = QDiagnostics(
            observation_id=observation_id,
            world_id=context.world_id,
            tick_id=self._tick_id(context, current_snapshot, previous_snapshot),
            previous_revision=previous_revision,
            current_revision=current_revision,
            representation_type=representation_type,
            metric_values=metric_values,
            thresholds=calibration.thresholds,
            calibration_profile=calibration.calibration_metadata.profile_name,
            calibration_version=calibration.calibration_metadata.version,
            warnings=calibration.warnings,
            out_of_range_metrics=calibration.out_of_range_metrics,
            observation_completeness=calibration.observation_completeness,
            missing_data=calibration.missing_data,
            metadata={
                "correlation_id": context.correlation_id,
                "domain_adapter_id": context.domain_adapter_id,
                "transition_proposals": len(context.transition_proposals),
                "render_proposal": context.render_proposal is not None,
                "verification_report": context.verification_report is not None,
                **dict(context.metadata),
            },
        )
        self.last_diagnostics = diagnostics
        self.last_calibration = calibration.calibration_metadata

        observation = QObservation(
            observation_id=observation_id,
            world_id=context.world_id,
            tick_id=diagnostics.tick_id,
            previous_revision=previous_revision,
            current_revision=current_revision,
            observation_time=observation_time,
            metric_values=metric_values,
            calibration_profile=calibration.calibration_metadata.profile_name,
            calibration_version=calibration.calibration_metadata.version,
            representation_type=representation_type,
            confidence=calibration.confidence,
            q_value=calibration.q_value,
            regime=calibration.regime,
            uncertainty=calibration.uncertainty,
            thresholds=calibration.thresholds,
            observed_pair=self._observed_pair(context, previous_snapshot, current_snapshot, calibration, observation_id),
            calibration_metadata=calibration.calibration_metadata,
            metadata={
                "correlation_id": context.correlation_id,
                "domain_adapter_id": context.domain_adapter_id,
                "tick_number": tick_number,
                "calibration_profile_id": calibration.calibration_metadata.profile_id,
                **dict(context.metadata),
            },
        )

        self._emit(
            "MetricsComputed",
            context,
            observation_id=observation_id,
            payload={"metric_names": tuple(sorted(metric_values)), "count": len(metric_values)},
            timestamp=observation_time,
        )
        self._emit(
            "CalibrationApplied",
            context,
            observation_id=observation_id,
            payload={
                "profile": calibration.calibration_metadata.profile_name,
                "version": calibration.calibration_metadata.version,
                "q_value": calibration.q_value,
            },
            timestamp=observation_time,
        )
        self._emit(
            "ObservationCreated",
            context,
            observation_id=observation_id,
            payload={"regime": calibration.regime, "confidence": calibration.confidence},
            timestamp=observation_time,
        )

        self.observations.append(observation)
        self.last_observation = observation
        self._emit(
            "ObservationPublished",
            context,
            observation_id=observation_id,
            payload={"history_size": len(self.observations)},
            timestamp=observation_time,
        )
        return observation

    def history(self) -> tuple[QObservation, ...]:
        return tuple(self.observations)

    def _tick_id(self, context: TransportContext, current_snapshot: RenderSnapshot | None, previous_snapshot: RenderSnapshot | None) -> TickId | None:
        if current_snapshot is not None and current_snapshot.tick_id is not None:
            return current_snapshot.tick_id
        if previous_snapshot is not None and previous_snapshot.tick_id is not None:
            return previous_snapshot.tick_id
        if context.tick_number is None:
            return None
        return TickId.new(context.world_id, context.tick_number)

    def _observed_pair(
        self,
        context: TransportContext,
        previous_snapshot: RenderSnapshot | None,
        current_snapshot: RenderSnapshot | None,
        calibration: CalibrationApplication,
        observation_id: str,
    ) -> Mapping[str, Any]:
        previous_state = {} if previous_snapshot is None else dict(_snapshot_mapping(previous_snapshot))
        current_state = {} if current_snapshot is None else dict(_snapshot_mapping(current_snapshot))
        return freeze_value(
            {
                "observation_id": observation_id,
                "previous_snapshot_id": None if previous_snapshot is None else str(previous_snapshot.snapshot_id.value),
                "current_snapshot_id": None if current_snapshot is None else str(current_snapshot.snapshot_id.value),
                "previous_revision": None if context.previous_revision is None else str(context.previous_revision.value),
                "current_revision": None if context.current_revision is None else str(context.current_revision.value),
                "domain_adapter_id": context.domain_adapter_id,
                "representation_type": context.representation_type,
                "correlation_id": context.correlation_id,
                "previous_entity_count": len(dict(previous_state.get("entities", {}))),
                "current_entity_count": len(dict(current_state.get("entities", {}))),
                "transition_proposals": len(context.transition_proposals),
                "calibration_profile": calibration.calibration_metadata.profile_name,
                "calibration_version": calibration.calibration_metadata.version,
            }
        )

    def _observation_id(
        self,
        world_id: WorldId,
        *,
        previous_revision: RevisionId | None,
        current_revision: RevisionId | None,
        representation_type: str,
        calibration_metadata: CalibrationMetadata,
        metric_values: Mapping[str, float],
        correlation_id: str,
        tick_number: int,
    ) -> str:
        metric_seed = "|".join(f"{key}:{float(value):.6f}" for key, value in sorted(metric_values.items()))
        seed = "|".join(
            [
                str(world_id.value),
                str(previous_revision.value) if previous_revision is not None else "None",
                str(current_revision.value) if current_revision is not None else "None",
                representation_type,
                calibration_metadata.profile_id,
                calibration_metadata.version,
                correlation_id,
                str(tick_number),
                metric_seed,
            ]
        )
        return f"id_{deterministic_hash(seed)}"

    def _emit(
        self,
        event_type: str,
        context: TransportContext,
        *,
        observation_id: str,
        payload: Mapping[str, Any] | None = None,
        timestamp: datetime | None = None,
    ) -> QEvent:
        event = QEvent(
            event_id=_event_id(context.world_id, event_type, observation_id, context.tick_number, len(self.events) + 1),
            world_id=context.world_id,
            event_type=event_type,
            timestamp=_tick_time(context.tick_number) if timestamp is None else timestamp,
            tick_id=TickId.new(context.world_id, context.tick_number),
            previous_revision=context.previous_revision,
            current_revision=context.current_revision,
            observation_id=observation_id,
            payload={} if payload is None else dict(payload),
            metadata={
                "domain_adapter_id": context.domain_adapter_id,
                "representation_type": context.representation_type,
                "correlation_id": context.correlation_id,
            },
        )
        self.events.append(event)
        return event
