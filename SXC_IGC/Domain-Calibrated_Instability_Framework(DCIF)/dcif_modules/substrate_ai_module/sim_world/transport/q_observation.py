from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Mapping

from ..core.contracts import freeze_value
from ..core.ids import EventId, RevisionId, TickId, WorldId


@dataclass(frozen=True, slots=True)
class CalibrationMetadata:
    profile_id: str
    profile_name: str
    version: str
    representation_type: str
    metric_weights: Mapping[str, float] = field(default_factory=dict)
    metric_thresholds: Mapping[str, float] = field(default_factory=dict)
    regime_thresholds: Mapping[str, float] = field(default_factory=dict)
    provenance: Mapping[str, Any] = field(default_factory=dict)
    selected_at: datetime | None = None
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        object.__setattr__(self, "profile_id", str(self.profile_id))
        object.__setattr__(self, "profile_name", str(self.profile_name))
        object.__setattr__(self, "version", str(self.version))
        object.__setattr__(self, "representation_type", str(self.representation_type))
        object.__setattr__(self, "metric_weights", freeze_value({key: float(value) for key, value in dict(self.metric_weights).items()}))
        object.__setattr__(self, "metric_thresholds", freeze_value({key: float(value) for key, value in dict(self.metric_thresholds).items()}))
        object.__setattr__(self, "regime_thresholds", freeze_value({key: float(value) for key, value in dict(self.regime_thresholds).items()}))
        object.__setattr__(self, "provenance", freeze_value(dict(self.provenance)))
        object.__setattr__(self, "metadata", freeze_value(dict(self.metadata)))


@dataclass(frozen=True, slots=True)
class QDiagnostics:
    observation_id: str
    world_id: WorldId
    tick_id: TickId | None
    previous_revision: RevisionId | None
    current_revision: RevisionId | None
    representation_type: str
    metric_values: Mapping[str, float] = field(default_factory=dict)
    thresholds: Mapping[str, float] = field(default_factory=dict)
    calibration_profile: str = ""
    calibration_version: str = ""
    warnings: tuple[str, ...] = field(default_factory=tuple)
    out_of_range_metrics: tuple[str, ...] = field(default_factory=tuple)
    observation_completeness: float = 1.0
    missing_data: tuple[str, ...] = field(default_factory=tuple)
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        object.__setattr__(self, "representation_type", str(self.representation_type))
        object.__setattr__(self, "metric_values", freeze_value({key: float(value) for key, value in dict(self.metric_values).items()}))
        object.__setattr__(self, "thresholds", freeze_value({key: float(value) for key, value in dict(self.thresholds).items()}))
        object.__setattr__(self, "calibration_profile", str(self.calibration_profile))
        object.__setattr__(self, "calibration_version", str(self.calibration_version))
        object.__setattr__(self, "warnings", tuple(str(item) for item in self.warnings))
        object.__setattr__(self, "out_of_range_metrics", tuple(str(item) for item in self.out_of_range_metrics))
        object.__setattr__(self, "observation_completeness", float(self.observation_completeness))
        object.__setattr__(self, "missing_data", tuple(str(item) for item in self.missing_data))
        object.__setattr__(self, "metadata", freeze_value(dict(self.metadata)))


@dataclass(frozen=True, slots=True)
class QEvent:
    event_id: EventId
    world_id: WorldId
    event_type: str
    timestamp: datetime
    tick_id: TickId | None
    previous_revision: RevisionId | None
    current_revision: RevisionId | None
    observation_id: str
    payload: Mapping[str, Any] = field(default_factory=dict)
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        object.__setattr__(self, "event_type", str(self.event_type))
        object.__setattr__(self, "observation_id", str(self.observation_id))
        object.__setattr__(self, "payload", freeze_value(dict(self.payload)))
        object.__setattr__(self, "metadata", freeze_value(dict(self.metadata)))


@dataclass(frozen=True, slots=True)
class QObservation:
    world_id: WorldId
    tick_id: TickId | None
    previous_revision: RevisionId | None
    current_revision: RevisionId | None
    observation_time: datetime
    observation_id: str = ""
    metric_values: Mapping[str, float] = field(default_factory=dict)
    calibration_profile: str = ""
    calibration_version: str = ""
    representation_type: str = ""
    confidence: float = 1.0
    q_value: float = 0.0
    regime: str = "unknown"
    uncertainty: float = 0.0
    thresholds: Mapping[str, float] = field(default_factory=dict)
    observed_pair: Mapping[str, Any] = field(default_factory=dict)
    calibration_metadata: CalibrationMetadata | None = None
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if self.observation_id:
            observation_id = str(self.observation_id)
        else:
            observation_id = str(
                EventId.new(
                    RevisionId.new(
                        self.world_id,
                        self.tick_id or TickId.new(self.world_id, 0),
                        0,
                        {
                            "current_revision": None if self.current_revision is None else str(self.current_revision.value),
                            "previous_revision": None if self.previous_revision is None else str(self.previous_revision.value),
                            "representation_type": self.representation_type,
                        },
                    ),
                    0,
                    {
                        "observation_time": self.observation_time.isoformat(),
                        "representation_type": self.representation_type,
                    },
                ).value
            )
        object.__setattr__(self, "observation_id", observation_id)
        object.__setattr__(self, "metric_values", freeze_value({key: float(value) for key, value in dict(self.metric_values).items()}))
        object.__setattr__(self, "calibration_profile", str(self.calibration_profile))
        object.__setattr__(self, "calibration_version", str(self.calibration_version))
        object.__setattr__(self, "representation_type", str(self.representation_type))
        object.__setattr__(self, "confidence", float(self.confidence))
        object.__setattr__(self, "q_value", float(self.q_value))
        object.__setattr__(self, "regime", str(self.regime))
        object.__setattr__(self, "uncertainty", float(self.uncertainty))
        object.__setattr__(self, "thresholds", freeze_value({key: float(value) for key, value in dict(self.thresholds).items()}))
        object.__setattr__(self, "observed_pair", freeze_value(dict(self.observed_pair)))
        object.__setattr__(self, "metadata", freeze_value(dict(self.metadata)))
