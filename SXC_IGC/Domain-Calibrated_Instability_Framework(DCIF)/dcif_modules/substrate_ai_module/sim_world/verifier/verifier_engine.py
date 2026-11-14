from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from typing import Any, Mapping


def deterministic_hash(seed: str) -> int:
    s = str(seed or "")
    val = hash(s) % (2**32)
    return abs(val)


from ..core.contracts import VerificationReport, freeze_value
from ..core.errors import VerificationError
from ..core.ids import EventId, SnapshotId, TickId, WorldId
from ..renderer.render_result import RenderResult
from .verifier import (
    CorrectionRequest,
    NormalizedVerificationOutput,
    VerificationClaim,
    VerificationDiscrepancy,
    VerificationEvidence,
    entity_signature,
    normalize_verification_output,
    summary_from_snapshot,
)
from .verifier_context import VerifierContext


def _clamp(value: float) -> float:
    return max(0.0, min(1.0, float(value)))


def _event_timestamp(seed: str) -> datetime:
    seed_uuid = deterministic_hash(seed)
    seconds = seed_uuid % 86400
    micros = (seed_uuid // 86400) % 1_000_000
    return datetime(2000, 1, 1, tzinfo=timezone.utc) + timedelta(seconds=seconds, microseconds=micros)


def _event_id(world_id: WorldId, event_type: str, output_id: str, index: int) -> EventId:
    seed = f"{world_id.value}|{event_type}|{output_id}|{index}"
    # deterministic_hash() returns an int; EventId.from_uuid() needs a real UUID
    # string, so build a deterministic EventId the way core/ids.py does.
    return EventId.deterministic("verifier.event", seed)


def _claim_id(world_id: WorldId, snapshot_id: SnapshotId, output_id: str, claim_type: str, subject: str) -> str:
    seed = f"sim_world.verifier.claim|{world_id.value}|{snapshot_id.value}|{output_id}|{claim_type}|{subject}"
    return f"id_{deterministic_hash(seed)}"


def _discrepancy_id(claim_id: str, expected_fact: Any, observed_fact: Any) -> str:
    seed = f"sim_world.verifier.discrepancy|{claim_id}|{repr(freeze_value(expected_fact))}|{repr(freeze_value(observed_fact))}"
    return f"id_{deterministic_hash(seed)}"


def _correction_id(discrepancy_id: str) -> str:
    seed = f"sim_world.verifier.correction|{discrepancy_id}"
    return f"id_{deterministic_hash(seed)}"


def _profile_name(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, str):
        return value
    return str(getattr(value, "name", getattr(value, "profile_id", value)))


def _profile_id(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, str):
        return value
    return str(getattr(value, "profile_id", value))


def _entity_lookup(observation: NormalizedVerificationOutput) -> dict[str, Mapping[str, Any]]:
    return {str(entity_id): dict(entity_state) for entity_id, entity_state in observation.entities.items()}


def _expected_entity_lookup(snapshot_summary: Mapping[str, Any]) -> dict[str, Mapping[str, Any]]:
    entities = snapshot_summary.get("entities", ())
    if isinstance(entities, tuple):
        return {str(entity["entity_id"]): dict(entity) for entity in entities}
    return {str(entity["entity_id"]): dict(entity) for entity in tuple(entities)}


def _canonical(value: Any) -> str:
    if isinstance(value, Mapping):
        return "{" + ",".join(f"{_canonical(key)}:{_canonical(inner)}" for key, inner in sorted(value.items(), key=lambda item: str(item[0]))) + "}"
    if isinstance(value, (list, tuple, set)):
        return "[" + ",".join(_canonical(item) for item in value) + "]"
    if hasattr(value, "value"):
        return str(getattr(value, "value"))
    return repr(value)


_IDENTITY_MARKER_KEYS = {
    "asset_id",
    "asset_key",
    "serial_number",
    "manufacturer",
    "visual_embedding",
    "creation_metadata",
    "stable_marker",
    "canonical_marker",
}


@dataclass(frozen=True, slots=True)
class VerificationEvent:
    event_id: EventId
    world_id: WorldId
    event_type: str
    timestamp: datetime
    tick_id: TickId | None
    snapshot_id: SnapshotId
    output_id: str
    renderer_type: str
    payload: Mapping[str, Any] = field(default_factory=dict)
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        object.__setattr__(self, "event_type", str(self.event_type))
        object.__setattr__(self, "output_id", str(self.output_id))
        object.__setattr__(self, "renderer_type", str(self.renderer_type))
        object.__setattr__(self, "payload", freeze_value(dict(self.payload)))
        object.__setattr__(self, "metadata", freeze_value(dict(self.metadata)))


@dataclass
class VerifierEngine:
    extractor_versions: Mapping[str, str] = field(
        default_factory=lambda: {
            "object": "1.0",
            "identity": "1.0",
            "relationship": "1.0",
            "scene": "1.0",
            "normalizer": "1.0",
        }
    )
    events: list[VerificationEvent] = field(default_factory=list)
    reports: list[VerificationReport] = field(default_factory=list)
    last_report: VerificationReport | None = field(default=None, init=False, repr=False)

    def normalize_output(self, render_output: Any) -> NormalizedVerificationOutput:
        return normalize_verification_output(render_output)

    def verify_objects(
        self,
        context: VerifierContext,
        observation: NormalizedVerificationOutput | None = None,
    ) -> tuple[VerificationClaim, ...]:
        observation = self.normalize_output(self._resolve_output(context)) if observation is None else observation
        snapshot_summary = summary_from_snapshot(context.target_snapshot)
        expected_entities = _expected_entity_lookup(snapshot_summary)
        observed_entities = _entity_lookup(observation)
        claims: list[VerificationClaim] = []
        for entity_id in sorted(expected_entities.keys() | observed_entities.keys()):
            expected = expected_entities.get(entity_id)
            observed = observed_entities.get(entity_id)
            if expected is None:
                claim = self._build_object_claim(context, observation, entity_id, expected={}, observed=observed, extra_entity=True)
            else:
                claim = self._build_object_claim(context, observation, entity_id, expected=expected, observed=observed, extra_entity=False)
            claims.append(claim)
        return tuple(claims)

    def verify_identity(
        self,
        context: VerifierContext,
        observation: NormalizedVerificationOutput | None = None,
    ) -> tuple[VerificationClaim, ...]:
        observation = self.normalize_output(self._resolve_output(context)) if observation is None else observation
        snapshot_summary = summary_from_snapshot(context.target_snapshot)
        expected_entities = _expected_entity_lookup(snapshot_summary)
        observed_entities = _entity_lookup(observation)
        claims: list[VerificationClaim] = []
        for entity_id in sorted(expected_entities.keys() | observed_entities.keys()):
            expected = expected_entities.get(entity_id)
            observed = observed_entities.get(entity_id)
            if expected is None:
                claim = self._build_identity_claim(context, observation, entity_id, expected={}, observed=observed, extra_entity=True)
            else:
                claim = self._build_identity_claim(context, observation, entity_id, expected=expected, observed=observed, extra_entity=False)
            claims.append(claim)
        return tuple(claims)

    def verify_relationships(
        self,
        context: VerifierContext,
        observation: NormalizedVerificationOutput | None = None,
    ) -> tuple[VerificationClaim, ...]:
        observation = self.normalize_output(self._resolve_output(context)) if observation is None else observation
        snapshot_summary = summary_from_snapshot(context.target_snapshot)
        expected_total = int(snapshot_summary.get("relationship_count", 0) or 0)
        observed_known = bool(observation.parsed.get("relationship_count_known", False))
        observed_total = int(observation.parsed.get("relationship_count", 0) or 0)
        claim_id = _claim_id(context.world_id, context.target_snapshot.snapshot_id, observation.output_id, "relationship", "relationships")
        if not observed_known:
            claim = VerificationClaim(
                claim_id=claim_id,
                claim_type="relationship",
                subject="relationships",
                status="unverifiable",
                expected={"relationship_count": expected_total},
                observed={"relationship_count": None},
                confidence=0.45,
                evidence={
                    "expected_relationship_count": expected_total,
                    "observed_relationship_count": None,
                    "relationship_count_known": False,
                },
                localization="scene.relationships",
                severity="unknown",
                metadata={"reason": "renderer output did not expose relationship counts"},
            )
            return (claim,)
        status = "passed" if expected_total == observed_total else "failed"
        confidence = 1.0 if status == "passed" else 0.0
        evidence = {
            "expected_relationship_count": expected_total,
            "observed_relationship_count": observed_total,
            "relationship_count_known": True,
        }
        claim = VerificationClaim(
            claim_id=claim_id,
            claim_type="relationship",
            subject="relationships",
            status=status,
            expected={"relationship_count": expected_total},
            observed={"relationship_count": observed_total},
            confidence=confidence,
            evidence=evidence,
            localization="scene.relationships",
            severity="ok" if status == "passed" else "high",
            metadata={"relationship_count_known": True},
        )
        return (claim,)

    def verify_scene(
        self,
        context: VerifierContext,
        observation: NormalizedVerificationOutput | None = None,
    ) -> tuple[VerificationClaim, ...]:
        observation = self.normalize_output(self._resolve_output(context)) if observation is None else observation
        snapshot_summary = summary_from_snapshot(context.target_snapshot)
        observed_summary = dict(observation.parsed)
        required_fields = ("world_id", "snapshot_id", "tick_id", "state_revision")
        optional_fields = ("entity_count", "relationship_count", "component_count", "profile", "requested_output")
        claim_id = _claim_id(context.world_id, context.target_snapshot.snapshot_id, observation.output_id, "scene", "scene")
        missing_required = [field for field in required_fields if observed_summary.get(field) in (None, "")]
        mismatched = [field for field in required_fields if observed_summary.get(field) not in (None, "") and str(observed_summary.get(field)) != str(snapshot_summary.get(field))]
        optional_mismatched = []
        expected_entity_fingerprint = _canonical(
            tuple(
                {
                    key: entity.get(key)
                    for key in ("entity_id", "type", "display_name", "room", "alive", "enabled", "components", "relationships", "actions")
                    if key in entity
                }
                for entity in snapshot_summary.get("entities", ())
            )
        )
        observed_entity_fingerprint = _canonical(
            tuple(
                {
                    key: entity.get(key)
                    for key in ("entity_id", "type", "display_name", "room", "alive", "enabled", "components", "relationships", "actions")
                    if key in entity
                }
                for entity in observed_summary.get("entities", ())
            )
        )
        for field in optional_fields:
            if field not in observed_summary:
                continue
            if field in ("relationship_count", "component_count") and not bool(observed_summary.get(f"{field}_known", True)):
                continue
            if field == "profile" and not _profile_name(context.render_profile):
                continue
            if field == "requested_output":
                expected_requested_output = None
                if context.render_result is not None and hasattr(context.render_result, "diagnostics"):
                    expected_requested_output = context.configuration.get("requested_output")
                elif context.configuration.get("requested_output"):
                    expected_requested_output = context.configuration.get("requested_output")
                if not expected_requested_output:
                    continue
            expected = snapshot_summary.get(field)
            observed = observed_summary.get(field)
            if field == "profile":
                expected = _profile_name(context.render_profile)
            if field == "requested_output":
                expected = expected_requested_output
            if _canonical(expected) != _canonical(observed):
                optional_mismatched.append(field)
        if observed_entity_fingerprint != expected_entity_fingerprint:
            optional_mismatched.append("entity_fingerprint")
        if missing_required:
            claim = VerificationClaim(
                claim_id=claim_id,
                claim_type="scene",
                subject="scene",
                status="unverifiable",
                expected={field: snapshot_summary.get(field) for field in required_fields},
                observed={field: observed_summary.get(field) for field in required_fields},
                confidence=0.4,
                evidence={
                    "missing_required_fields": tuple(missing_required),
                    "observed_scene": observed_summary,
                    "expected_scene": {field: snapshot_summary.get(field) for field in required_fields},
                },
                localization="scene.top_level",
                severity="unknown",
                metadata={"reason": "required scene fields were not available"},
            )
            return (claim,)
        if mismatched or optional_mismatched:
            claim = VerificationClaim(
                claim_id=claim_id,
                claim_type="scene",
                subject="scene",
                status="failed",
                expected={field: snapshot_summary.get(field) for field in (*required_fields, *optional_fields)},
                observed={field: observed_summary.get(field) for field in (*required_fields, *optional_fields)},
                confidence=0.0,
                evidence={
                    "mismatched_required_fields": tuple(mismatched),
                    "mismatched_optional_fields": tuple(optional_mismatched),
                    "observed_scene": observed_summary,
                    "expected_scene": snapshot_summary,
                },
                localization="scene.top_level",
                severity="high",
                metadata={"required_fields": required_fields, "optional_fields": optional_fields},
            )
            return (claim,)
        claim = VerificationClaim(
            claim_id=claim_id,
            claim_type="scene",
            subject="scene",
            status="passed" if not optional_mismatched else "unverifiable",
            expected={field: snapshot_summary.get(field) for field in (*required_fields, *optional_fields)},
            observed={field: observed_summary.get(field) for field in (*required_fields, *optional_fields)},
            confidence=1.0 if not optional_mismatched else 0.8,
            evidence={
                "observed_scene": observed_summary,
                "expected_scene": snapshot_summary,
            },
            localization="scene.top_level",
            severity="ok" if not optional_mismatched else "unknown",
            metadata={"required_fields": required_fields, "optional_fields": optional_fields},
        )
        return (claim,)

    def verify(
        self,
        context: VerifierContext,
    ) -> VerificationReport:
        if context.target_snapshot is None:
            raise VerificationError("verification requires a target snapshot")
        observation = self.normalize_output(self._resolve_output(context))
        self._emit("VerificationRequested", context, observation=observation, payload={"renderer_type": observation.renderer_type})
        self._emit("VerificationStarted", context, observation=observation, payload={"output_id": observation.output_id})

        object_claims = self.verify_objects(context, observation)
        identity_claims = self.verify_identity(context, observation)
        relationship_claims = self.verify_relationships(context, observation)
        scene_claims = self.verify_scene(context, observation)
        claims = object_claims + identity_claims + relationship_claims + scene_claims

        discrepancies = tuple(self._claim_to_discrepancy(claim) for claim in claims if claim.status == "failed")
        correction_requests = tuple(self._discrepancy_to_correction(discrepancy) for discrepancy in discrepancies)
        passed = not any(claim.status == "failed" for claim in claims)
        coverage = self._coverage(claims)
        confidence = self._aggregate_confidence(claims, coverage)
        uncertainty = _clamp(1.0 - confidence)
        severity = self._severity(claims)
        false_positive_risk = _clamp((1.0 - confidence) * 0.5 + (1.0 - coverage) * 0.5)
        false_negative_risk = _clamp((1.0 - coverage) * 0.75 + (0.0 if passed else 0.25))
        report = VerificationReport(
            world_id=context.world_id,
            snapshot_id=context.target_snapshot.snapshot_id,
            output_id=observation.output_id,
            tick_id=context.target_snapshot.tick_id,
            state_revision=context.target_snapshot.state_revision,
            passed=passed,
            confidence=confidence,
            discrepancies=discrepancies,
            evidence=self._report_evidence(context, observation, claims),
            metadata=self._report_metadata(context, observation, claims),
            extractor_versions=self.extractor_versions,
            claim_statuses=claims,
            uncertainty=uncertainty,
            severity=severity,
            coverage=coverage,
            false_positive_risk=false_positive_risk,
            false_negative_risk=false_negative_risk,
            correction_requests=correction_requests,
        )
        self.reports.append(report)
        self.last_report = report
        self._emit("VerificationCompleted", context, observation=observation, report=report, payload={"passed": passed, "confidence": confidence})
        self._emit("VerificationPublished", context, observation=observation, report=report, payload={"history_size": len(self.reports)})
        return report

    def history(self) -> tuple[VerificationReport, ...]:
        return tuple(self.reports)

    def capability_report(self) -> Mapping[str, Any]:
        return freeze_value(
            {
                "extractor_versions": dict(self.extractor_versions),
                "events": tuple(event.event_type for event in self.events),
                "report_count": len(self.reports),
            }
        )

    def _resolve_output(self, context: VerifierContext) -> Any:
        if context.render_result is not None:
            return context.render_result
        if context.render_proposal is not None:
            return context.render_proposal
        return context.render_output

    def _build_object_claim(
        self,
        context: VerifierContext,
        observation: NormalizedVerificationOutput,
        entity_id: str,
        *,
        expected: Mapping[str, Any],
        observed: Mapping[str, Any] | None,
        extra_entity: bool,
    ) -> VerificationClaim:
        claim_id = _claim_id(context.world_id, context.target_snapshot.snapshot_id, observation.output_id, "object", entity_id)
        if extra_entity:
            return VerificationClaim(
                claim_id=claim_id,
                claim_type="object",
                subject=f"entity:{entity_id}",
                status="failed",
                expected=None,
                observed=observed,
                confidence=0.0,
                evidence={"reason": "unexpected entity in rendered output", "observed": observed},
                localization=f"entity:{entity_id}",
                severity="high",
                metadata={"unexpected": True},
            )
        if observed is None:
            return VerificationClaim(
                claim_id=claim_id,
                claim_type="object",
                subject=f"entity:{entity_id}",
                status="failed",
                expected=expected,
                observed=None,
                confidence=0.0,
                evidence={"reason": "expected entity missing from rendered output", "expected_entity": expected},
                localization=f"entity:{entity_id}",
                severity="high",
                metadata={"missing": True},
            )
        assert observed is not None
        required_fields = ("entity_id", "type", "display_name")
        optional_fields = ("room", "components", "alive", "enabled", "relationships", "actions")
        missing_required = [field for field in required_fields if observed.get(field) in (None, "")]
        mismatched = []
        for field in required_fields:
            if observed.get(field) in (None, ""):
                continue
            if _canonical(expected.get(field)) != _canonical(observed.get(field)):
                mismatched.append(field)
        for field in optional_fields:
            if field not in observed or observed.get(field) is None:
                continue
            if field == "components":
                if tuple(expected.get(field, ())) != tuple(observed.get(field, ())):
                    mismatched.append(field)
            elif field in ("relationships", "actions"):
                if int(expected.get(field, 0) or 0) != int(observed.get(field, 0) or 0):
                    mismatched.append(field)
            elif _canonical(expected.get(field)) != _canonical(observed.get(field)):
                mismatched.append(field)
        if missing_required:
            return VerificationClaim(
                claim_id=claim_id,
                claim_type="object",
                subject=f"entity:{entity_id}",
                status="unverifiable",
                expected=expected,
                observed=observed,
                confidence=0.45,
                evidence={
                    "missing_required_fields": tuple(missing_required),
                    "observed_entity": observed,
                    "expected_entity": expected,
                },
                localization=f"entity:{entity_id}",
                severity="unknown",
                metadata={"reason": "renderer did not expose all required object fields"},
            )
        if mismatched:
            return VerificationClaim(
                claim_id=claim_id,
                claim_type="object",
                subject=f"entity:{entity_id}",
                status="failed",
                expected=expected,
                observed=observed,
                confidence=0.0,
                evidence={
                    "mismatched_fields": tuple(mismatched),
                    "observed_entity": observed,
                    "expected_entity": expected,
                },
                localization=f"entity:{entity_id}",
                severity="high",
                metadata={"required_fields": required_fields, "optional_fields": optional_fields},
            )
        status = "passed"
        confidence = 1.0
        if any(field not in observed or observed.get(field) is None for field in optional_fields):
            status = "unverifiable"
            confidence = 0.75
        return VerificationClaim(
            claim_id=claim_id,
            claim_type="object",
            subject=f"entity:{entity_id}",
            status=status,
            expected=expected,
            observed=observed,
            confidence=confidence,
            evidence={
                "observed_entity": observed,
                "expected_entity": expected,
            },
            localization=f"entity:{entity_id}",
            severity="ok" if status == "passed" else "unknown",
            metadata={"required_fields": required_fields, "optional_fields": optional_fields},
        )

    def _build_identity_claim(
        self,
        context: VerifierContext,
        observation: NormalizedVerificationOutput,
        entity_id: str,
        *,
        expected: Mapping[str, Any],
        observed: Mapping[str, Any] | None,
        extra_entity: bool,
    ) -> VerificationClaim:
        claim_id = _claim_id(context.world_id, context.target_snapshot.snapshot_id, observation.output_id, "identity", entity_id)
        if extra_entity:
            return VerificationClaim(
                claim_id=claim_id,
                claim_type="identity",
                subject=f"entity:{entity_id}",
                status="failed",
                expected=None,
                observed=observed,
                confidence=0.0,
                evidence={"reason": "unexpected entity in rendered output", "observed": observed},
                localization=f"identity:{entity_id}",
                severity="high",
                metadata={"unexpected": True},
            )
        if observed is None:
            return VerificationClaim(
                claim_id=claim_id,
                claim_type="identity",
                subject=f"entity:{entity_id}",
                status="failed",
                expected=expected,
                observed=None,
                confidence=0.0,
                evidence={"reason": "expected entity missing from rendered output", "expected_identity": expected},
                localization=f"identity:{entity_id}",
                severity="high",
                metadata={"missing": True},
            )
        assert observed is not None
        required_fields = ("entity_id", "type", "display_name")
        missing_required = [field for field in required_fields if observed.get(field) in (None, "")]
        mismatched = [field for field in required_fields if observed.get(field) not in (None, "") and _canonical(expected.get(field)) != _canonical(observed.get(field))]
        expected_metadata = dict(expected.get("metadata", {}))
        observed_metadata = dict(observed.get("metadata", {}))
        marker_keys = sorted((set(expected_metadata) | set(observed_metadata)) & _IDENTITY_MARKER_KEYS)
        marker_mismatched = [key for key in marker_keys if key in expected_metadata and key in observed_metadata and _canonical(expected_metadata.get(key)) != _canonical(observed_metadata.get(key))]
        marker_missing = [key for key in marker_keys if key in expected_metadata and key not in observed_metadata]
        if missing_required:
            return VerificationClaim(
                claim_id=claim_id,
                claim_type="identity",
                subject=f"entity:{entity_id}",
                status="unverifiable",
                expected=expected,
                observed=observed,
                confidence=0.45,
                evidence={
                    "missing_required_fields": tuple(missing_required),
                    "observed_identity": observed,
                    "expected_identity": expected,
                },
                localization=f"identity:{entity_id}",
                severity="unknown",
                metadata={"reason": "renderer did not expose all required identity fields"},
            )
        if mismatched or marker_mismatched:
            return VerificationClaim(
                claim_id=claim_id,
                claim_type="identity",
                subject=f"entity:{entity_id}",
                status="failed",
                expected=expected,
                observed=observed,
                confidence=0.0,
                evidence={
                    "mismatched_fields": tuple(mismatched),
                    "mismatched_markers": tuple(marker_mismatched),
                    "observed_identity": observed,
                    "expected_identity": expected,
                },
                localization=f"identity:{entity_id}",
                severity="high",
                metadata={"marker_missing": tuple(marker_missing), "marker_keys": tuple(marker_keys)},
            )
        status = "passed"
        confidence = 1.0
        if marker_missing:
            status = "unverifiable"
            confidence = 0.8
        return VerificationClaim(
            claim_id=claim_id,
            claim_type="identity",
            subject=f"entity:{entity_id}",
            status=status,
            expected=expected,
            observed=observed,
            confidence=confidence,
            evidence={
                "observed_identity": observed,
                "expected_identity": expected,
                "expected_markers": expected_metadata,
                "observed_markers": observed_metadata,
            },
            localization=f"identity:{entity_id}",
            severity="ok" if status == "passed" else "unknown",
            metadata={"marker_missing": tuple(marker_missing), "marker_keys": tuple(marker_keys)},
        )

    def _claim_to_discrepancy(self, claim: VerificationClaim) -> VerificationDiscrepancy:
        expected_fact = claim.expected
        observed_fact = claim.observed
        discrepancy_id = _discrepancy_id(claim.claim_id, expected_fact, observed_fact)
        if claim.claim_type == "relationship":
            localization = "scene.relationships"
            must_change = ("relationship_count",)
        elif claim.claim_type == "scene":
            localization = "scene.top_level"
            mismatched_required = tuple(claim.evidence.get("mismatched_required_fields", ()))
            mismatched_optional = tuple(claim.evidence.get("mismatched_optional_fields", ()))
            must_change = tuple(sorted({*mismatched_required, *mismatched_optional})) or ("scene_state",)
        else:
            localization = claim.localization
            mismatched_fields = tuple(claim.evidence.get("mismatched_fields", ()))
            must_change = mismatched_fields or ("entity_state",)
        return VerificationDiscrepancy(
            discrepancy_id=discrepancy_id,
            claim_id=claim.claim_id,
            claim_type=claim.claim_type,
            subject=claim.subject,
            expected_fact=expected_fact,
            observed_fact=observed_fact,
            localization=localization,
            severity=claim.severity,
            correction_constraint={
                "claim_type": claim.claim_type,
                "subject": claim.subject,
                "must_preserve": tuple(sorted(claim.evidence.keys())),
                "must_change": must_change,
            },
            evidence=claim.evidence,
            metadata=claim.metadata,
        )

    def _discrepancy_to_correction(self, discrepancy: VerificationDiscrepancy) -> CorrectionRequest:
        request_id = _correction_id(discrepancy.discrepancy_id)
        return CorrectionRequest(
            request_id=request_id,
            claim_id=discrepancy.claim_id,
            claim_type=discrepancy.claim_type,
            subject=discrepancy.subject,
            preserve=("identity", "continuity"),
            change=("match_target_snapshot",),
            constraints=discrepancy.correction_constraint,
            priority=10 if discrepancy.severity == "high" else 5,
            metadata=discrepancy.metadata,
        )

    def _coverage(self, claims: tuple[VerificationClaim, ...]) -> float:
        if not claims:
            return 1.0
        assessed = sum(1.0 for claim in claims if claim.status != "unverifiable")
        return _clamp(assessed / len(claims))

    def _aggregate_confidence(self, claims: tuple[VerificationClaim, ...], coverage: float) -> float:
        if not claims:
            return 1.0
        weighted = sum(claim.confidence for claim in claims) / len(claims)
        return _clamp((weighted * 0.75) + (coverage * 0.25))

    def _severity(self, claims: tuple[VerificationClaim, ...]) -> str:
        if any(claim.status == "failed" for claim in claims):
            return "critical" if sum(1 for claim in claims if claim.status == "failed") > 3 else "high"
        if any(claim.status == "unverifiable" for claim in claims):
            return "unknown"
        return "ok"

    def _report_evidence(
        self,
        context: VerifierContext,
        observation: NormalizedVerificationOutput,
        claims: tuple[VerificationClaim, ...],
    ) -> Mapping[str, Any]:
        return freeze_value(
            {
                "target_snapshot": summary_from_snapshot(context.target_snapshot),
                "observed_output": observation.parsed,
                "output_id": observation.output_id,
                "renderer_type": observation.renderer_type,
                "output_format": observation.output_format,
                "claim_count": len(claims),
                "claim_types": tuple(sorted({claim.claim_type for claim in claims})),
                "renderer_context": {
                    "renderer_type": context.renderer_type,
                    "render_profile": _profile_name(context.render_profile),
                    "render_profile_id": _profile_id(context.render_profile),
                    "correlation_id": context.correlation_id,
                    "asset_versions": dict(context.asset_versions),
                    "sensor_scope": dict(context.sensor_scope),
                    "extraction_hints": dict(context.extraction_hints),
                },
            }
        )

    def _report_metadata(
        self,
        context: VerifierContext,
        observation: NormalizedVerificationOutput,
        claims: tuple[VerificationClaim, ...],
    ) -> Mapping[str, Any]:
        return freeze_value(
            {
                "world_id": str(context.world_id.value),
                "snapshot_id": str(context.target_snapshot.snapshot_id.value),
                "tick_id": None if context.target_snapshot.tick_id is None else str(context.target_snapshot.tick_id.value),
                "target_revision": None if context.target_revision is None else str(context.target_revision.value),
                "output_id": observation.output_id,
                "renderer_type": observation.renderer_type,
                "render_profile": _profile_name(context.render_profile),
                "render_profile_id": _profile_id(context.render_profile),
                "correlation_id": context.correlation_id,
                "claim_count": len(claims),
                "passed_claims": sum(1 for claim in claims if claim.status == "passed"),
                "unverifiable_claims": sum(1 for claim in claims if claim.status == "unverifiable"),
                "failed_claims": sum(1 for claim in claims if claim.status == "failed"),
                "snapshot_summary_hash": repr(summary_from_snapshot(context.target_snapshot)),
                "context_metadata": dict(context.metadata),
            }
        )

    def _emit(
        self,
        event_type: str,
        context: VerifierContext,
        *,
        observation: NormalizedVerificationOutput,
        payload: Mapping[str, Any] | None = None,
        report: VerificationReport | None = None,
    ) -> VerificationEvent:
        timestamp = report.discrepancies[0].metadata.get("timestamp") if report is not None and report.discrepancies else None
        if not isinstance(timestamp, datetime):
            timestamp = _event_timestamp(f"{context.world_id.value}|{event_type}|{observation.output_id}|{len(self.events)+1}")
        event = VerificationEvent(
            event_id=_event_id(context.world_id, event_type, observation.output_id, len(self.events) + 1),
            world_id=context.world_id,
            event_type=event_type,
            timestamp=timestamp,
            tick_id=context.target_snapshot.tick_id,
            snapshot_id=context.target_snapshot.snapshot_id,
            output_id=observation.output_id,
            renderer_type=observation.renderer_type,
            payload={} if payload is None else dict(payload),
            metadata={
                "render_profile": _profile_name(context.render_profile),
                "render_profile_id": _profile_id(context.render_profile),
                "correlation_id": context.correlation_id,
            },
        )
        self.events.append(event)
        return event
