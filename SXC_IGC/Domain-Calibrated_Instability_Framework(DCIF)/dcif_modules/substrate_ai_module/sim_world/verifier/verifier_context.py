from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Mapping

from ..core.contracts import RenderProposal, RenderSnapshot, freeze_value
from ..core.ids import RevisionId, WorldId
from ..renderer.render_result import RenderResult


@dataclass(frozen=True, slots=True)
class VerifierContext:
    world_id: WorldId
    target_snapshot: RenderSnapshot
    render_output: Any
    renderer_type: str = ""
    render_profile: Any = None
    asset_versions: Mapping[str, Any] = field(default_factory=dict)
    sensor_scope: Mapping[str, Any] = field(default_factory=dict)
    extraction_hints: Mapping[str, Any] = field(default_factory=dict)
    configuration: Mapping[str, Any] = field(default_factory=dict)
    correlation_id: str = ""
    metadata: Mapping[str, Any] = field(default_factory=dict)
    render_result: RenderResult | None = None
    render_proposal: RenderProposal | None = None
    target_revision: RevisionId | None = None

    def __post_init__(self) -> None:
        object.__setattr__(self, "renderer_type", str(self.renderer_type))
        object.__setattr__(self, "correlation_id", str(self.correlation_id))
        object.__setattr__(self, "asset_versions", freeze_value(dict(self.asset_versions)))
        object.__setattr__(self, "sensor_scope", freeze_value(dict(self.sensor_scope)))
        object.__setattr__(self, "extraction_hints", freeze_value(dict(self.extraction_hints)))
        object.__setattr__(self, "configuration", freeze_value(dict(self.configuration)))
        object.__setattr__(self, "metadata", freeze_value(dict(self.metadata)))
        if self.target_revision is None:
            object.__setattr__(self, "target_revision", self.target_snapshot.state_revision)
