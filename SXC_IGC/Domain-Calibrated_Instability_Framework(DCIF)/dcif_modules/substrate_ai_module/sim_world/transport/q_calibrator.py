from __future__ import annotations

from dataclasses import dataclass, field, replace
from datetime import datetime, timedelta, timezone
from typing import Any, Mapping


from ..core.contracts import freeze_value
from ..core.ids import WorldId
from .q_observation import CalibrationMetadata
from .transport_context import TransportContext

def deterministic_hash(seed: str) -> int:
    s = str(seed or "")
    val = hash(s) % (2**32)
    return abs(val)



def _clamp(value: float) -> float:
    return max(0.0, min(1.0, float(value)))


def _profile_id(name: str, version: str, representation_type: str) -> str:
    seed = f"sim_world.qcalibration|{name}|{version}|{representation_type}"
    return f"id_{deterministic_hash(seed)}"


def _default_metric_weights() -> Mapping[str, float]:
    return {
        "state_distance": 1.2,
        "representation_distance": 0.9,
        "identity_preservation": 1.3,
        "topology_preservation": 1.1,
        "component_preservation": 1.1,
        "relationship_preservation": 1.0,
        "transition_magnitude": 0.8,
        "structural_consistency": 1.0,
        "temporal_consistency": 1.0,
    }


def _default_metric_thresholds() -> Mapping[str, float]:
    return {
        "state_distance": 0.20,
        "representation_distance": 0.30,
        "identity_preservation": 0.95,
        "topology_preservation": 0.90,
        "component_preservation": 0.90,
        "relationship_preservation": 0.90,
        "transition_magnitude": 0.35,
        "structural_consistency": 0.85,
        "temporal_consistency": 0.80,
    }


def _default_metric_modes() -> Mapping[str, str]:
    return {
        "state_distance": "max",
        "representation_distance": "max",
        "identity_preservation": "min",
        "topology_preservation": "min",
        "component_preservation": "min",
        "relationship_preservation": "min",
        "transition_magnitude": "max",
        "structural_consistency": "min",
        "temporal_consistency": "min",
    }


def _default_regime_thresholds() -> Mapping[str, float]:
    return {
        "stable": 0.85,
        "warning": 0.70,
        "boundary": 0.50,
        "critical": 0.0,
    }


@dataclass(frozen=True, slots=True)
class CalibrationProfile:
    name: str
    version: str
    representation_type: str
    metric_weights: Mapping[str, float] = field(default_factory=_default_metric_weights)
    metric_thresholds: Mapping[str, float] = field(default_factory=_default_metric_thresholds)
    metric_modes: Mapping[str, str] = field(default_factory=_default_metric_modes)
    regime_thresholds: Mapping[str, float] = field(default_factory=_default_regime_thresholds)
    provenance: Mapping[str, Any] = field(default_factory=dict)
    metadata: Mapping[str, Any] = field(default_factory=dict)
    profile_id: str = ""

    def __post_init__(self) -> None:
        object.__setattr__(self, "name", str(self.name))
        object.__setattr__(self, "version", str(self.version))
        object.__setattr__(self, "representation_type", str(self.representation_type))
        object.__setattr__(self, "metric_weights", freeze_value({key: float(value) for key, value in dict(self.metric_weights).items()}))
        object.__setattr__(self, "metric_thresholds", freeze_value({key: float(value) for key, value in dict(self.metric_thresholds).items()}))
        object.__setattr__(self, "metric_modes", freeze_value({key: str(value) for key, value in dict(self.metric_modes).items()}))
        object.__setattr__(self, "regime_thresholds", freeze_value({key: float(value) for key, value in dict(self.regime_thresholds).items()}))
        object.__setattr__(self, "provenance", freeze_value(dict(self.provenance)))
        object.__setattr__(self, "metadata", freeze_value(dict(self.metadata)))
        if not self.profile_id:
            object.__setattr__(self, "profile_id", _profile_id(self.name, self.version, self.representation_type))


@dataclass(frozen=True, slots=True)
class CalibrationApplication:
    calibration_metadata: CalibrationMetadata
    metric_values: Mapping[str, float]
    q_value: float
    regime: str
    confidence: float
    uncertainty: float
    thresholds: Mapping[str, float]
    warnings: tuple[str, ...]
    out_of_range_metrics: tuple[str, ...]
    observation_completeness: float
    missing_data: tuple[str, ...]
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        object.__setattr__(self, "metric_values", freeze_value({key: float(value) for key, value in dict(self.metric_values).items()}))
        object.__setattr__(self, "q_value", float(self.q_value))
        object.__setattr__(self, "regime", str(self.regime))
        object.__setattr__(self, "confidence", float(self.confidence))
        object.__setattr__(self, "uncertainty", float(self.uncertainty))
        object.__setattr__(self, "thresholds", freeze_value({key: float(value) for key, value in dict(self.thresholds).items()}))
        object.__setattr__(self, "warnings", tuple(str(item) for item in self.warnings))
        object.__setattr__(self, "out_of_range_metrics", tuple(str(item) for item in self.out_of_range_metrics))
        object.__setattr__(self, "observation_completeness", float(self.observation_completeness))
        object.__setattr__(self, "missing_data", tuple(str(item) for item in self.missing_data))
        object.__setattr__(self, "metadata", freeze_value(dict(self.metadata)))


@dataclass
class QCalibrator:
    profiles: dict[str, CalibrationProfile] = field(default_factory=dict)
    default_profile_name: str = "default"
    default_version: str = "1.0"

    def __post_init__(self) -> None:
        if not self.profiles:
            self.register_profile(
                CalibrationProfile(
                    name="default",
                    version="1.0",
                    representation_type="snapshot_transition",
                    provenance={"source": "builtin", "policy": "balanced"},
                    metadata={"profile_class": "default"},
                )
            )
            self.register_profile(
                CalibrationProfile(
                    name="strict",
                    version="1.0",
                    representation_type="snapshot_transition",
                    metric_weights={
                        "state_distance": 1.5,
                        "representation_distance": 1.0,
                        "identity_preservation": 1.4,
                        "topology_preservation": 1.2,
                        "component_preservation": 1.2,
                        "relationship_preservation": 1.1,
                        "transition_magnitude": 1.0,
                        "structural_consistency": 1.2,
                        "temporal_consistency": 1.1,
                    },
                    regime_thresholds={"stable": 0.92, "warning": 0.78, "boundary": 0.55, "critical": 0.0},
                    provenance={"source": "builtin", "policy": "strict"},
                    metadata={"profile_class": "strict"},
                )
            )

    def register_profile(self, profile: CalibrationProfile) -> CalibrationProfile:
        self.profiles[profile.profile_id] = profile
        return profile

    def profile(self, profile_id: str) -> CalibrationProfile | None:
        return self.profiles.get(str(profile_id))

    def select_profile(
        self,
        profile: CalibrationProfile | str | None = None,
        *,
        representation_type: str | None = None,
    ) -> CalibrationProfile:
        if isinstance(profile, CalibrationProfile):
            return profile
        if isinstance(profile, str):
            match = self._match_profile(profile, representation_type=representation_type)
            if match is not None:
                return match
        if representation_type is not None:
            match = self._match_profile(self.default_profile_name, representation_type=representation_type)
            if match is not None:
                return match
        match = self._match_profile(self.default_profile_name)
        if match is not None:
            return match
        return next(iter(self.profiles.values()))

    def apply(
        self,
        metric_values: Mapping[str, float],
        *,
        context: TransportContext,
        tick_number: int,
        representation_type: str | None = None,
    ) -> CalibrationApplication:
        profile = self.select_profile(context.calibration_profile or context.configuration.get("calibration_profile"), representation_type=representation_type or context.representation_type)
        selected_at = datetime(2000, 1, 1, tzinfo=timezone.utc) + timedelta(seconds=max(0, int(tick_number)))
        completeness, missing_data = self._completeness(context)
        out_of_range, warnings = self._threshold_warnings(profile, metric_values, completeness=completeness, missing_data=missing_data)
        calibrated_score = self._score(profile, metric_values)
        q_value = _clamp(calibrated_score * completeness)
        regime = self._regime(profile, q_value)
        confidence = _clamp(q_value * completeness)
        uncertainty = _clamp(1.0 - confidence + (1.0 - completeness) * 0.25)
        metadata = CalibrationMetadata(
            profile_id=profile.profile_id,
            profile_name=profile.name,
            version=profile.version,
            representation_type=representation_type or context.representation_type,
            metric_weights=profile.metric_weights,
            metric_thresholds=profile.metric_thresholds,
            regime_thresholds=profile.regime_thresholds,
            provenance=profile.provenance,
            selected_at=selected_at,
            metadata={**dict(profile.metadata), "world_id": str(context.world_id.value), "domain_adapter_id": context.domain_adapter_id},
        )
        return CalibrationApplication(
            calibration_metadata=metadata,
            metric_values=metric_values,
            q_value=q_value,
            regime=regime,
            confidence=confidence,
            uncertainty=uncertainty,
            thresholds={**dict(profile.metric_thresholds), **dict(profile.regime_thresholds)},
            warnings=warnings,
            out_of_range_metrics=out_of_range,
            observation_completeness=completeness,
            missing_data=missing_data,
            metadata={"representation_type": representation_type or context.representation_type, "domain_adapter_id": context.domain_adapter_id},
        )

    def _match_profile(self, name: str, *, representation_type: str | None = None) -> CalibrationProfile | None:
        candidates = [profile for profile in self.profiles.values() if profile.name == name]
        if representation_type is not None:
            for profile in candidates:
                if profile.representation_type == representation_type:
                    return profile
        return candidates[0] if candidates else None

    def _score(self, profile: CalibrationProfile, metric_values: Mapping[str, float]) -> float:
        weighted_sum = 0.0
        total_weight = 0.0
        for metric_name, weight in dict(profile.metric_weights).items():
            raw_value = float(metric_values.get(metric_name, 0.0))
            if profile.metric_modes.get(metric_name, "max") == "max":
                score_value = 1.0 - raw_value
            else:
                score_value = raw_value
            weighted_sum += score_value * float(weight)
            total_weight += float(weight)
        if total_weight <= 0:
            return 0.0
        return _clamp(weighted_sum / total_weight)

    def _regime(self, profile: CalibrationProfile, q_value: float) -> str:
        thresholds = dict(profile.regime_thresholds)
        if q_value >= thresholds.get("stable", 0.85):
            return "stable"
        if q_value >= thresholds.get("warning", 0.70):
            return "warning"
        if q_value >= thresholds.get("boundary", 0.50):
            return "boundary"
        return "critical"

    def _completeness(self, context: TransportContext) -> tuple[float, tuple[str, ...]]:
        missing: list[str] = []
        present = 0
        if context.previous_snapshot is not None:
            present += 1
        else:
            missing.append("previous_snapshot")
        if context.current_snapshot is not None:
            present += 1
        else:
            missing.append("current_snapshot")
        completeness = present / 2.0
        return completeness, tuple(missing)

    def _threshold_warnings(
        self,
        profile: CalibrationProfile,
        metric_values: Mapping[str, float],
        *,
        completeness: float,
        missing_data: tuple[str, ...],
    ) -> tuple[tuple[str, ...], tuple[str, ...]]:
        out_of_range: list[str] = []
        warnings: list[str] = []
        for metric_name, threshold in dict(profile.metric_thresholds).items():
            mode = profile.metric_modes.get(metric_name, "max")
            value = float(metric_values.get(metric_name, 0.0))
            failed = value > threshold if mode == "max" else value < threshold
            if failed:
                out_of_range.append(metric_name)
                warnings.append(f"{metric_name}={value:.4f} outside {mode} threshold {threshold:.4f}")
        if completeness < 1.0:
            warnings.append(f"observation completeness={completeness:.2f}")
        if missing_data:
            warnings.extend(f"missing:{item}" for item in missing_data)
        return tuple(out_of_range), tuple(warnings)
