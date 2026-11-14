from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Mapping

from ..core.contracts import RenderSnapshot, freeze_value
from ..core.ids import WorldId
from .render_profiles import RenderProfile


@dataclass(frozen=True, slots=True)
class RendererContext:
    world_id: WorldId
    snapshot: RenderSnapshot
    render_profile: RenderProfile | str | None = None
    renderer_type: str | None = None
    requested_output: str = ""
    configuration: Mapping[str, Any] = field(default_factory=dict)
    user_parameters: Mapping[str, Any] = field(default_factory=dict)
    correlation_id: str = ""
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        object.__setattr__(self, "requested_output", str(self.requested_output))
        object.__setattr__(self, "renderer_type", None if self.renderer_type is None else str(self.renderer_type))
        object.__setattr__(self, "correlation_id", str(self.correlation_id))
        object.__setattr__(self, "configuration", freeze_value(dict(self.configuration)))
        object.__setattr__(self, "user_parameters", freeze_value(dict(self.user_parameters)))
        object.__setattr__(self, "metadata", freeze_value(dict(self.metadata)))
