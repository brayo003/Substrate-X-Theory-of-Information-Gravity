from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from json import dumps
from typing import Any, Mapping, Protocol, runtime_checkable


from ..core.contracts import RenderSnapshot, freeze_value
from .render_profiles import RenderProfile
from .render_request import RenderRequest
from .render_result import RenderDiagnostics, RenderResult, RendererMetadata

def deterministic_hash(seed: str) -> int:
    s = str(seed or "")
    val = hash(s) % (2**32)
    return abs(val)



def _timestamp_from_seed(seed: str) -> datetime:
    # deterministic_hash returns an int; wrap it in a UUID the way
    # core/ids.py::_deterministic_uuid does (seed_uuid.int stays stable).
    from uuid import UUID

    seed_uuid = UUID(int=deterministic_hash(seed) % (2**128))
    seconds = seed_uuid.int % 86400
    micros = (seed_uuid.int // 86400) % 1_000_000
    return datetime(2000, 1, 1, tzinfo=timezone.utc) + timedelta(seconds=seconds, microseconds=micros)


def _sorted_entities(snapshot: RenderSnapshot) -> list[tuple[str, Mapping[str, Any]]]:
    entities = dict(snapshot.state.get("entities", {}))
    return sorted(((str(entity_id), dict(entity_state)) for entity_id, entity_state in entities.items()), key=lambda item: item[0])


def _entity_summary(entity_id: str, entity_state: Mapping[str, Any]) -> Mapping[str, Any]:
    return {
        "entity_id": entity_id,
        "type": entity_state.get("type"),
        "display_name": entity_state.get("display_name"),
        "room": dict(entity_state.get("components", {}).get("TransformComponent", {})).get("room"),
        "alive": entity_state.get("alive"),
        "enabled": entity_state.get("enabled"),
        "components": sorted(dict(entity_state.get("components", {})).keys()),
        "relationships": len(tuple(entity_state.get("relationships", ()))),
        "actions": len(tuple(entity_state.get("actions", ()))),
    }


def _render_summary(snapshot: RenderSnapshot) -> Mapping[str, Any]:
    return {
        "world_id": str(snapshot.world_id.value),
        "snapshot_id": str(snapshot.snapshot_id.value),
        "tick_id": None if snapshot.tick_id is None else str(snapshot.tick_id.value),
        "state_revision": None if snapshot.state_revision is None else str(snapshot.state_revision.value),
        "timestamp": None if snapshot.tick_id is None else str(snapshot.tick_id.value),
        "entities": [_entity_summary(entity_id, entity_state) for entity_id, entity_state in _sorted_entities(snapshot)],
        "metadata": dict(snapshot.metadata),
    }


def _jsonable(value: Any) -> Any:
    if isinstance(value, Mapping):
        return {str(key): _jsonable(inner) for key, inner in value.items()}
    if isinstance(value, tuple):
        return [_jsonable(item) for item in value]
    if isinstance(value, list):
        return [_jsonable(item) for item in value]
    if isinstance(value, set):
        return sorted(_jsonable(item) for item in value)
    return value


def _render_text(snapshot: RenderSnapshot, profile: RenderProfile, requested_output: str) -> str:
    summary = _render_summary(snapshot)
    lines = [
        f"RenderProfile: {profile.name}",
        f"World: {summary['world_id']}",
        f"Snapshot: {summary['snapshot_id']}",
        f"Tick: {summary['tick_id']}",
        f"Revision: {summary['state_revision']}",
    ]
    if requested_output:
        lines.append(f"Requested: {requested_output}")
    for entity in summary["entities"]:
        lines.append(
            f"- {entity['display_name']} [{entity['entity_id']}] type={entity['type']} room={entity['room']} components={','.join(entity['components'])}"
        )
    return "\n".join(lines)


def _render_ascii(snapshot: RenderSnapshot, profile: RenderProfile, requested_output: str) -> str:
    summary = _render_summary(snapshot)
    rows = [
        "+----------------------+----------------------+",
        f"| profile              | {profile.name:<20} |",
        f"| world                | {summary['world_id']:<20} |",
        f"| snapshot             | {summary['snapshot_id']:<20} |",
        f"| tick                 | {str(summary['tick_id']):<20} |",
        f"| revision             | {str(summary['state_revision']):<20} |",
        "+----------------------+----------------------+",
    ]
    if requested_output:
        rows.append(f"requested={requested_output}")
    for entity in summary["entities"]:
        rows.append(f"{entity['display_name']}|{entity['type']}|{entity['room']}|{','.join(entity['components'])}")
    return "\n".join(rows)


def _render_json(snapshot: RenderSnapshot, profile: RenderProfile, requested_output: str) -> str:
    payload = _render_summary(snapshot)
    payload = {**payload, "profile": profile.name, "requested_output": requested_output}
    return dumps(_jsonable(payload), sort_keys=True, separators=(",", ":"))


def _render_debug(snapshot: RenderSnapshot, profile: RenderProfile, requested_output: str) -> Mapping[str, Any]:
    return freeze_value(
        {
            "profile": profile.name,
            "requested_output": requested_output,
            "snapshot": _render_summary(snapshot),
        }
    )


@runtime_checkable
class RenderAdapter(Protocol):
    renderer_type: str
    renderer_name: str
    renderer_version: str

    def render(self, request: RenderRequest) -> RenderResult:
        ...

    def capabilities(self) -> Mapping[str, Any]:
        ...


@dataclass
class BaseRenderAdapter:
    renderer_type: str
    renderer_name: str
    renderer_version: str = "1.0"
    output_format: str = "text"
    limitations: tuple[str, ...] = field(default_factory=tuple)

    def capabilities(self) -> Mapping[str, Any]:
        return freeze_value(
            {
                "renderer_type": self.renderer_type,
                "renderer_name": self.renderer_name,
                "renderer_version": self.renderer_version,
                "output_format": self.output_format,
                "limitations": self.limitations,
            }
        )

    def _metadata(self, request: RenderRequest, output_payload: Any) -> RendererMetadata:
        seed = f"sim_world.renderer|{self.renderer_name}|{self.renderer_version}|{self.renderer_type}"
        return RendererMetadata(
            renderer_id=f"id_{deterministic_hash(seed)}",
            renderer_name=self.renderer_name,
            renderer_type=self.renderer_type,
            renderer_version=self.renderer_version,
            adapter_capabilities=self.capabilities(),
            profile_id=request.render_profile.profile_id,
            profile_name=request.render_profile.name,
            generation_parameters=dict(request.configuration),
            limitations=self.limitations,
            provenance={"adapter": self.renderer_name, "profile": request.render_profile.name},
            trace_evidence={
                "request_id": request.request_id,
                "snapshot_id": str(request.snapshot_id.value),
                "output_hash": repr(output_payload),
            },
            metadata=dict(request.metadata),
        )

    def _diagnostics(self, request: RenderRequest, generation_timestamp: datetime) -> RenderDiagnostics:
        return RenderDiagnostics(
            request_id=request.request_id,
            snapshot_id=request.snapshot_id,
            renderer_type=self.renderer_type,
            render_profile=request.render_profile.name,
            render_format=self.output_format,
            started_at=generation_timestamp,
            completed_at=generation_timestamp,
            duration_ms=0.0,
            warnings=(),
            errors=(),
            metadata={"adapter": self.renderer_name},
        )

    def _result(self, request: RenderRequest, output_payload: Any, *, requested_output: str = "") -> RenderResult:
        seed = f"{request.request_id}|{self.renderer_name}|{request.render_profile.profile_id}|{repr(freeze_value(output_payload))}"
        generation_timestamp = _timestamp_from_seed(seed)
        diagnostics = self._diagnostics(request, generation_timestamp)
        renderer_metadata = self._metadata(request, output_payload)
        return RenderResult.create(
            request=request,
            output_payload=output_payload,
            output_format=self.output_format,
            renderer_metadata=renderer_metadata,
            generation_timestamp=generation_timestamp,
            diagnostics=diagnostics,
            metadata={"requested_output": requested_output, "adapter": self.renderer_name},
        )


class TextRenderer(BaseRenderAdapter):
    def __init__(self) -> None:
        super().__init__(renderer_type="text", renderer_name="TextRenderer", output_format="text")

    def render(self, request: RenderRequest) -> RenderResult:
        snapshot = request.snapshot
        if snapshot is None:
            raise ValueError("render request requires a snapshot")
        output = _render_text(snapshot, request.render_profile, request.requested_output)
        return self._result(request, output, requested_output=request.requested_output)


class ASCIIRenderer(BaseRenderAdapter):
    def __init__(self) -> None:
        super().__init__(renderer_type="ascii", renderer_name="ASCIIRenderer", output_format="ascii")

    def render(self, request: RenderRequest) -> RenderResult:
        snapshot = request.snapshot
        if snapshot is None:
            raise ValueError("render request requires a snapshot")
        output = _render_ascii(snapshot, request.render_profile, request.requested_output)
        return self._result(request, output, requested_output=request.requested_output)


class JsonRenderer(BaseRenderAdapter):
    def __init__(self) -> None:
        super().__init__(renderer_type="json", renderer_name="JsonRenderer", output_format="json")

    def render(self, request: RenderRequest) -> RenderResult:
        snapshot = request.snapshot
        if snapshot is None:
            raise ValueError("render request requires a snapshot")
        output = _render_json(snapshot, request.render_profile, request.requested_output)
        return self._result(request, output, requested_output=request.requested_output)


class DebugRenderer(BaseRenderAdapter):
    def __init__(self) -> None:
        super().__init__(renderer_type="debug", renderer_name="DebugRenderer", output_format="debug")

    def render(self, request: RenderRequest) -> RenderResult:
        snapshot = request.snapshot
        if snapshot is None:
            raise ValueError("render request requires a snapshot")
        output = _render_debug(snapshot, request.render_profile, request.requested_output)
        return self._result(request, output, requested_output=request.requested_output)
