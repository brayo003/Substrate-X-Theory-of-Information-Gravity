from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Mapping


from ..core.contracts import freeze_value
from ..core.ids import SnapshotId
from .render_request import RenderRequest
from .render_profiles import RenderProfile

def deterministic_hash(seed: str) -> int:
    s = str(seed or "")
    val = hash(s) % (2**32)
    return abs(val)



def _result_id(request_id: str, renderer_type: str, output_format: str, output_payload: Any) -> str:
    seed = "|".join([str(request_id), str(renderer_type), str(output_format), repr(freeze_value(output_payload))])
    return f"id_{deterministic_hash('sim_world.render_result|' + seed)}"


@dataclass(frozen=True, slots=True)
class RendererMetadata:
    renderer_id: str
    renderer_name: str
    renderer_type: str
    renderer_version: str
    adapter_capabilities: Mapping[str, Any] = field(default_factory=dict)
    profile_id: str = ""
    profile_name: str = ""
    generation_parameters: Mapping[str, Any] = field(default_factory=dict)
    limitations: tuple[str, ...] = field(default_factory=tuple)
    provenance: Mapping[str, Any] = field(default_factory=dict)
    trace_evidence: Mapping[str, Any] = field(default_factory=dict)
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        object.__setattr__(self, "renderer_id", str(self.renderer_id))
        object.__setattr__(self, "renderer_name", str(self.renderer_name))
        object.__setattr__(self, "renderer_type", str(self.renderer_type))
        object.__setattr__(self, "renderer_version", str(self.renderer_version))
        object.__setattr__(self, "adapter_capabilities", freeze_value(dict(self.adapter_capabilities)))
        object.__setattr__(self, "profile_id", str(self.profile_id))
        object.__setattr__(self, "profile_name", str(self.profile_name))
        object.__setattr__(self, "generation_parameters", freeze_value(dict(self.generation_parameters)))
        object.__setattr__(self, "limitations", tuple(str(item) for item in self.limitations))
        object.__setattr__(self, "provenance", freeze_value(dict(self.provenance)))
        object.__setattr__(self, "trace_evidence", freeze_value(dict(self.trace_evidence)))
        object.__setattr__(self, "metadata", freeze_value(dict(self.metadata)))


@dataclass(frozen=True, slots=True)
class RenderDiagnostics:
    request_id: str
    snapshot_id: SnapshotId
    renderer_type: str
    render_profile: str
    render_format: str
    started_at: datetime
    completed_at: datetime
    duration_ms: float
    warnings: tuple[str, ...] = field(default_factory=tuple)
    errors: tuple[str, ...] = field(default_factory=tuple)
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        object.__setattr__(self, "request_id", str(self.request_id))
        object.__setattr__(self, "renderer_type", str(self.renderer_type))
        object.__setattr__(self, "render_profile", str(self.render_profile))
        object.__setattr__(self, "render_format", str(self.render_format))
        object.__setattr__(self, "warnings", tuple(str(item) for item in self.warnings))
        object.__setattr__(self, "errors", tuple(str(item) for item in self.errors))
        object.__setattr__(self, "duration_ms", float(self.duration_ms))
        object.__setattr__(self, "metadata", freeze_value(dict(self.metadata)))


@dataclass(frozen=True, slots=True)
class RenderResult:
    result_id: str
    request_id: str
    snapshot_id: SnapshotId
    renderer_type: str
    output_payload: Any
    output_format: str
    renderer_metadata: RendererMetadata
    generation_timestamp: datetime
    diagnostics: RenderDiagnostics
    profile: RenderProfile
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        object.__setattr__(self, "result_id", str(self.result_id))
        object.__setattr__(self, "request_id", str(self.request_id))
        object.__setattr__(self, "renderer_type", str(self.renderer_type))
        object.__setattr__(self, "output_format", str(self.output_format))
        object.__setattr__(self, "metadata", freeze_value(dict(self.metadata)))

    @classmethod
    def create(
        cls,
        *,
        request: RenderRequest,
        output_payload: Any,
        output_format: str,
        renderer_metadata: RendererMetadata,
        generation_timestamp: datetime,
        diagnostics: RenderDiagnostics,
        metadata: Mapping[str, Any] | None = None,
    ) -> "RenderResult":
        return cls(
            result_id=_result_id(request.request_id, request.renderer_type, output_format, output_payload),
            request_id=request.request_id,
            snapshot_id=request.snapshot_id,
            renderer_type=request.renderer_type,
            output_payload=output_payload,
            output_format=output_format,
            renderer_metadata=renderer_metadata,
            generation_timestamp=generation_timestamp,
            diagnostics=diagnostics,
            profile=request.render_profile,
            metadata={} if metadata is None else dict(metadata),
        )
