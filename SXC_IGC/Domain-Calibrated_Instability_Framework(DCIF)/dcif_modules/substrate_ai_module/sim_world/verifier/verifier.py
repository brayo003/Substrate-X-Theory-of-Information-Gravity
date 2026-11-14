from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from json import JSONDecodeError, loads
from re import compile as re_compile
from typing import Any, Mapping


from ..core.contracts import RenderProposal, RenderSnapshot, freeze_value
from ..core.ids import SnapshotId, WorldId
from ..renderer.render_result import RenderResult

def deterministic_hash(seed: str) -> int:
    s = str(seed or "")
    val = hash(s) % (2**32)
    return abs(val)



_TEXT_ENTITY_RE = re_compile(
    r"^- (?P<display_name>.*?) \[(?P<entity_id>[^\]]+)\] type=(?P<type>[^ ]+) room=(?P<room>[^ ]+) components=(?P<components>.*)$"
)
_ASCII_ENTITY_RE = re_compile(r"^(?P<display_name>[^|]+)\|(?P<type>[^|]+)\|(?P<room>[^|]+)\|(?P<components>.*)$")


def _clamp(value: float) -> float:
    return max(0.0, min(1.0, float(value)))


def _canonical_text(value: Any) -> str:
    if isinstance(value, Mapping):
        return "{" + ",".join(f"{_canonical_text(key)}:{_canonical_text(inner)}" for key, inner in sorted(value.items(), key=lambda item: str(item[0]))) + "}"
    if isinstance(value, (list, tuple, set)):
        return "[" + ",".join(_canonical_text(item) for item in value) + "]"
    if hasattr(value, "value"):
        inner = getattr(value, "value")
        if hasattr(inner, "hex") or hasattr(inner, "int"):
            return str(inner)
    if hasattr(value, "value") and not isinstance(value, (str, bytes)):
        return _canonical_text(getattr(value, "value"))
    return repr(value)


def _summary_entity(entity_id: str, entity_state: Mapping[str, Any]) -> Mapping[str, Any]:
    components = dict(entity_state.get("components", {}))
    transform = dict(components.get("TransformComponent", {}))
    relationships = tuple(entity_state.get("relationships", ()))
    metadata = dict(entity_state.get("metadata", {}))
    return freeze_value(
        {
            "entity_id": entity_id,
            "type": entity_state.get("type"),
            "display_name": entity_state.get("display_name"),
            "room": transform.get("room"),
            "alive": entity_state.get("alive"),
            "enabled": entity_state.get("enabled"),
            "components": tuple(sorted(components.keys())),
            "relationships": len(relationships),
            "actions": len(tuple(entity_state.get("actions", ()))),
            "metadata": metadata,
        }
    )


def _snapshot_entities(snapshot: RenderSnapshot) -> dict[str, Mapping[str, Any]]:
    entities = dict(snapshot.state.get("entities", {}))
    return {str(entity_id): dict(entity_state) for entity_id, entity_state in sorted(entities.items(), key=lambda item: str(item[0]))}


def _snapshot_summary(snapshot: RenderSnapshot) -> Mapping[str, Any]:
    entities = _snapshot_entities(snapshot)
    return freeze_value(
        {
            "world_id": str(snapshot.world_id.value),
            "snapshot_id": str(snapshot.snapshot_id.value),
            "tick_id": None if snapshot.tick_id is None else str(snapshot.tick_id.value),
            "state_revision": None if snapshot.state_revision is None else str(snapshot.state_revision.value),
            "timestamp": str(snapshot.timestamp.isoformat()),
            "entity_count": len(entities),
            "relationship_count": sum(len(tuple(entity_state.get("relationships", ()))) for entity_state in entities.values()),
            "component_count": sum(len(dict(entity_state.get("components", {}))) for entity_state in entities.values()),
            "entities": [
                _summary_entity(entity_id, entity_state)
                for entity_id, entity_state in entities.items()
            ],
            "metadata": dict(snapshot.metadata),
        }
    )


def _parse_entity_line(line: str) -> Mapping[str, Any] | None:
    text_match = _TEXT_ENTITY_RE.match(line.strip())
    if text_match is not None:
        components = [item for item in text_match.group("components").split(",") if item]
        return freeze_value(
            {
                "entity_id": text_match.group("entity_id"),
                "type": text_match.group("type"),
                "display_name": text_match.group("display_name"),
                "room": text_match.group("room"),
                "components": tuple(sorted(component.strip() for component in components)),
                "alive": None,
                "enabled": None,
                "relationships": None,
                "actions": None,
                "metadata": {},
            }
        )
    ascii_match = _ASCII_ENTITY_RE.match(line.strip())
    if ascii_match is not None:
        components = [item for item in ascii_match.group("components").split(",") if item]
        return freeze_value(
            {
                "entity_id": "",
                "type": ascii_match.group("type").strip(),
                "display_name": ascii_match.group("display_name").strip(),
                "room": ascii_match.group("room").strip(),
                "components": tuple(sorted(component.strip() for component in components)),
                "alive": None,
                "enabled": None,
                "relationships": None,
                "actions": None,
                "metadata": {},
            }
        )
    return None


def _parse_text_output(text: str) -> Mapping[str, Any]:
    header: dict[str, Any] = {}
    entities: list[Mapping[str, Any]] = []
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line:
            continue
        if line.startswith("RenderProfile:"):
            header["profile"] = line.split(":", 1)[1].strip()
            continue
        if line.startswith("World:"):
            header["world_id"] = line.split(":", 1)[1].strip()
            continue
        if line.startswith("Snapshot:"):
            header["snapshot_id"] = line.split(":", 1)[1].strip()
            continue
        if line.startswith("Tick:"):
            header["tick_id"] = line.split(":", 1)[1].strip()
            continue
        if line.startswith("Revision:"):
            header["state_revision"] = line.split(":", 1)[1].strip()
            continue
        if line.startswith("Requested:"):
            header["requested_output"] = line.split(":", 1)[1].strip()
            continue
        parsed = _parse_entity_line(line)
        if parsed is not None:
            entities.append(parsed)
    header["entities"] = tuple(entities)
    header["entity_count"] = len(entities)
    header["relationship_count"] = sum(int(entity.get("relationships", 0) or 0) for entity in entities if entity.get("relationships") is not None)
    header["relationship_count_known"] = False
    header["component_count"] = sum(len(tuple(entity.get("components", ()))) for entity in entities)
    header["component_count_known"] = True
    return freeze_value(header)


def _parse_mapping_output(value: Mapping[str, Any]) -> Mapping[str, Any]:
    if "snapshot" in value and isinstance(value["snapshot"], Mapping):
        snapshot = dict(value["snapshot"])
        snapshot.setdefault("profile", value.get("profile"))
        snapshot.setdefault("requested_output", value.get("requested_output"))
        return _parse_mapping_output(snapshot)
    entities: list[Mapping[str, Any]] = []
    raw_entities = value.get("entities", ())
    if isinstance(raw_entities, Mapping):
        iterable = raw_entities.values()
    else:
        iterable = raw_entities
    for item in iterable:
        if not isinstance(item, Mapping):
            continue
        components = item.get("components", ())
        if isinstance(components, str):
            components = tuple(component.strip() for component in components.split(",") if component.strip())
        elif isinstance(components, Mapping):
            components = tuple(sorted(str(key) for key in components.keys()))
        else:
            components = tuple(sorted(str(component) for component in components))
        entities.append(
            freeze_value(
                {
                    "entity_id": str(item.get("entity_id", "")),
                    "type": item.get("type"),
                    "display_name": item.get("display_name"),
                    "room": item.get("room"),
                    "alive": item.get("alive"),
                    "enabled": item.get("enabled"),
                    "components": components,
                    "relationships": int(item.get("relationships", 0) or 0),
                    "actions": int(item.get("actions", 0) or 0),
                    "metadata": dict(item.get("metadata", {})) if isinstance(item.get("metadata", {}), Mapping) else {},
                }
            )
        )
    result = dict(value)
    result["entities"] = tuple(entities)
    result["entity_count"] = int(result.get("entity_count", len(entities)) or len(entities))
    if "relationship_count" not in result:
        result["relationship_count"] = sum(int(entity.get("relationships", 0) or 0) for entity in entities)
    result["relationship_count_known"] = True
    if "component_count" not in result:
        result["component_count"] = sum(len(tuple(entity.get("components", ()))) for entity in entities)
    result["component_count_known"] = True
    return freeze_value(result)


def _normalize_output_payload(payload: Any) -> Mapping[str, Any]:
    if isinstance(payload, Mapping):
        return _parse_mapping_output(payload)
    if isinstance(payload, str):
        stripped = payload.strip()
        if stripped.startswith("{") or stripped.startswith("["):
            try:
                loaded = loads(stripped)
            except JSONDecodeError:
                return _parse_text_output(payload)
            if isinstance(loaded, Mapping):
                return _parse_mapping_output(loaded)
            return freeze_value({"entities": tuple(), "entity_count": 0, "relationship_count": 0, "component_count": 0, "payload": loaded})
        return _parse_text_output(payload)
    if isinstance(payload, (list, tuple)):
        entities = []
        for item in payload:
            if isinstance(item, Mapping):
                entities.append(_parse_mapping_output(item))
        return freeze_value({"entities": tuple(entities), "entity_count": len(entities), "relationship_count": 0, "component_count": 0})
    return freeze_value({"entities": tuple(), "entity_count": 0, "relationship_count": 0, "component_count": 0, "value": payload})


def _extract_payload_identity(render_output: Any) -> tuple[Any, str, str, str]:
    renderer_type = ""
    output_format = "unknown"
    output_id = ""
    payload = render_output
    if isinstance(render_output, RenderResult):
        renderer_type = render_output.renderer_type
        output_format = render_output.output_format
        output_id = render_output.result_id
        payload = render_output.output_payload
    elif isinstance(render_output, RenderProposal):
        renderer_type = str(render_output.renderer_type)
        output_format = "proposal"
        seed = f"sim_world.verifier.proposal|{render_output.snapshot_id.value}|{renderer_type}|{_canonical_text(render_output.output)}"
        output_id = str(deterministic_hash(seed))
        payload = render_output.output
    else:
        renderer_type = getattr(render_output, "renderer_type", "") or ""
        output_format = getattr(render_output, "output_format", "unknown") or "unknown"
        seed = f"sim_world.verifier.output|{renderer_type}|{output_format}|{_canonical_text(render_output)}"
        output_id = str(deterministic_hash(seed))
        if hasattr(render_output, "output_payload"):
            payload = getattr(render_output, "output_payload")
        elif hasattr(render_output, "output"):
            payload = getattr(render_output, "output")
    return payload, renderer_type, output_format, output_id


def _event_timestamp(seed: str) -> datetime:
    seed_uuid = deterministic_hash(seed)
    seconds = seed_uuid % 86400
    micros = (seed_uuid // 86400) % 1_000_000
    return datetime(2000, 1, 1, tzinfo=timezone.utc) + timedelta(seconds=seconds, microseconds=micros)


@dataclass(frozen=True, slots=True)
class VerificationClaim:
    claim_id: str
    claim_type: str
    subject: str
    status: str
    expected: Any
    observed: Any
    confidence: float
    evidence: Mapping[str, Any] = field(default_factory=dict)
    localization: str = ""
    severity: str = "unknown"
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        object.__setattr__(self, "claim_id", str(self.claim_id))
        object.__setattr__(self, "claim_type", str(self.claim_type))
        object.__setattr__(self, "subject", str(self.subject))
        object.__setattr__(self, "status", str(self.status))
        object.__setattr__(self, "confidence", _clamp(self.confidence))
        object.__setattr__(self, "evidence", freeze_value(dict(self.evidence)))
        object.__setattr__(self, "localization", str(self.localization))
        object.__setattr__(self, "severity", str(self.severity))
        object.__setattr__(self, "metadata", freeze_value(dict(self.metadata)))


@dataclass(frozen=True, slots=True)
class VerificationDiscrepancy:
    discrepancy_id: str
    claim_id: str
    claim_type: str
    subject: str
    expected_fact: Any
    observed_fact: Any
    localization: str
    severity: str
    correction_constraint: Mapping[str, Any] = field(default_factory=dict)
    evidence: Mapping[str, Any] = field(default_factory=dict)
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        object.__setattr__(self, "discrepancy_id", str(self.discrepancy_id))
        object.__setattr__(self, "claim_id", str(self.claim_id))
        object.__setattr__(self, "claim_type", str(self.claim_type))
        object.__setattr__(self, "subject", str(self.subject))
        object.__setattr__(self, "localization", str(self.localization))
        object.__setattr__(self, "severity", str(self.severity))
        object.__setattr__(self, "correction_constraint", freeze_value(dict(self.correction_constraint)))
        object.__setattr__(self, "evidence", freeze_value(dict(self.evidence)))
        object.__setattr__(self, "metadata", freeze_value(dict(self.metadata)))


@dataclass(frozen=True, slots=True)
class CorrectionRequest:
    request_id: str
    claim_id: str
    claim_type: str
    subject: str
    preserve: tuple[str, ...] = field(default_factory=tuple)
    change: tuple[str, ...] = field(default_factory=tuple)
    constraints: Mapping[str, Any] = field(default_factory=dict)
    priority: int = 0
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        object.__setattr__(self, "request_id", str(self.request_id))
        object.__setattr__(self, "claim_id", str(self.claim_id))
        object.__setattr__(self, "claim_type", str(self.claim_type))
        object.__setattr__(self, "subject", str(self.subject))
        object.__setattr__(self, "preserve", tuple(str(item) for item in self.preserve))
        object.__setattr__(self, "change", tuple(str(item) for item in self.change))
        object.__setattr__(self, "constraints", freeze_value(dict(self.constraints)))
        object.__setattr__(self, "priority", int(self.priority))
        object.__setattr__(self, "metadata", freeze_value(dict(self.metadata)))


@dataclass(frozen=True, slots=True)
class VerificationEvidence:
    output_id: str
    renderer_type: str
    output_format: str
    raw_payload: Any
    parsed: Mapping[str, Any]
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        object.__setattr__(self, "output_id", str(self.output_id))
        object.__setattr__(self, "renderer_type", str(self.renderer_type))
        object.__setattr__(self, "output_format", str(self.output_format))
        object.__setattr__(self, "parsed", freeze_value(dict(self.parsed)))
        object.__setattr__(self, "metadata", freeze_value(dict(self.metadata)))


@dataclass(frozen=True, slots=True)
class NormalizedVerificationOutput:
    output_id: str
    renderer_type: str
    output_format: str
    payload: Any
    parsed: Mapping[str, Any]
    entities: Mapping[str, Mapping[str, Any]]
    metadata: Mapping[str, Any]

    def __post_init__(self) -> None:
        object.__setattr__(self, "output_id", str(self.output_id))
        object.__setattr__(self, "renderer_type", str(self.renderer_type))
        object.__setattr__(self, "output_format", str(self.output_format))
        object.__setattr__(self, "parsed", freeze_value(dict(self.parsed)))
        object.__setattr__(self, "entities", freeze_value({str(key): dict(value) for key, value in self.entities.items()}))
        object.__setattr__(self, "metadata", freeze_value(dict(self.metadata)))


def normalize_verification_output(render_output: Any) -> NormalizedVerificationOutput:
    payload, renderer_type, output_format, output_id = _extract_payload_identity(render_output)
    parsed = _normalize_output_payload(payload)
    entities = {}
    for entity in parsed.get("entities", ()):
        entity_id = str(entity.get("entity_id", ""))
        if not entity_id:
            seed = f"sim_world.verifier.entity|{output_id}|{entity.get('display_name', '')}|{entity.get('type', '')}"
            entity_id = str(deterministic_hash(seed))
        entities[entity_id] = dict(entity)
    metadata = {}
    if isinstance(render_output, RenderResult):
        metadata = {
            "result_id": render_output.result_id,
            "request_id": render_output.request_id,
            "profile_id": render_output.profile.profile_id,
            "profile_name": render_output.profile.name,
            "generation_timestamp": render_output.generation_timestamp.isoformat(),
            "renderer_metadata": dict(render_output.renderer_metadata.metadata),
            "diagnostics": dict(render_output.diagnostics.metadata),
        }
    elif isinstance(render_output, RenderProposal):
        metadata = {"renderer_type": render_output.renderer_type, "snapshot_id": str(render_output.snapshot_id.value)}
    return NormalizedVerificationOutput(
        output_id=output_id,
        renderer_type=renderer_type,
        output_format=output_format,
        payload=payload,
        parsed=parsed,
        entities=entities,
        metadata=metadata,
    )


def summary_from_snapshot(snapshot: RenderSnapshot) -> Mapping[str, Any]:
    return _snapshot_summary(snapshot)


def entity_signature(entity_id: str, entity_state: Mapping[str, Any]) -> str:
    return _canonical_text(_summary_entity(entity_id, entity_state))
