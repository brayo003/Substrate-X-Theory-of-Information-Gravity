from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Mapping


from ..core.contracts import RenderSnapshot, freeze_value
from ..core.ids import SnapshotId, WorldId
from .render_profiles import RenderProfile

def deterministic_hash(seed: str) -> int:
    s = str(seed or "")
    val = hash(s) % (2**32)
    return abs(val)



def _request_id(world_id: WorldId, snapshot_id: SnapshotId, renderer_type: str, profile_id: str, requested_output: str, configuration: Mapping[str, Any], metadata: Mapping[str, Any]) -> str:
    seed = "|".join(
        [
            str(world_id.value),
            str(snapshot_id.value),
            str(renderer_type),
            str(profile_id),
            str(requested_output),
            repr(freeze_value(dict(configuration))),
            repr(freeze_value(dict(metadata))),
        ]
    )
    return f"id_{deterministic_hash('sim_world.render_request|' + seed)}"


@dataclass(frozen=True, slots=True)
class RenderRequest:
    request_id: str
    snapshot_id: SnapshotId
    render_profile: RenderProfile
    renderer_type: str
    requested_output: str
    configuration: Mapping[str, Any] = field(default_factory=dict)
    metadata: Mapping[str, Any] = field(default_factory=dict)
    snapshot: RenderSnapshot | None = None

    def __post_init__(self) -> None:
        object.__setattr__(self, "request_id", str(self.request_id))
        object.__setattr__(self, "renderer_type", str(self.renderer_type))
        object.__setattr__(self, "requested_output", str(self.requested_output))
        object.__setattr__(self, "configuration", freeze_value(dict(self.configuration)))
        object.__setattr__(self, "metadata", freeze_value(dict(self.metadata)))

    @classmethod
    def create(
        cls,
        *,
        world_id: WorldId,
        snapshot: RenderSnapshot,
        render_profile: RenderProfile,
        renderer_type: str,
        requested_output: str = "",
        configuration: Mapping[str, Any] | None = None,
        metadata: Mapping[str, Any] | None = None,
    ) -> "RenderRequest":
        configuration = {} if configuration is None else dict(configuration)
        metadata = {} if metadata is None else dict(metadata)
        return cls(
            request_id=_request_id(
                world_id,
                snapshot.snapshot_id,
                renderer_type,
                render_profile.profile_id,
                requested_output,
                configuration,
                metadata,
            ),
            snapshot_id=snapshot.snapshot_id,
            render_profile=render_profile,
            renderer_type=renderer_type,
            requested_output=requested_output,
            configuration=configuration,
            metadata=metadata,
            snapshot=snapshot,
        )
