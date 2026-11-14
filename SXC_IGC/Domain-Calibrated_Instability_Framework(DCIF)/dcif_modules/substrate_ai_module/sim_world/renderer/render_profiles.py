from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Mapping


from ..core.contracts import freeze_value

def deterministic_hash(seed: str) -> int:
    s = str(seed or "")
    val = hash(s) % (2**32)
    return abs(val)



def _profile_id(name: str, renderer_type: str, output_format: str) -> str:
    seed = f"sim_world.render_profile|{name}|{renderer_type}|{output_format}"
    return f"id_{deterministic_hash(seed)}"


@dataclass(frozen=True, slots=True)
class RenderProfile:
    name: str
    renderer_type: str
    output_format: str
    modality: str = ""
    description: str = ""
    preferred_adapter: str = ""
    configuration: Mapping[str, Any] = field(default_factory=dict)
    metadata: Mapping[str, Any] = field(default_factory=dict)
    profile_id: str = ""

    def __post_init__(self) -> None:
        object.__setattr__(self, "name", str(self.name))
        object.__setattr__(self, "renderer_type", str(self.renderer_type))
        object.__setattr__(self, "output_format", str(self.output_format))
        object.__setattr__(self, "modality", str(self.modality))
        object.__setattr__(self, "description", str(self.description))
        object.__setattr__(self, "preferred_adapter", str(self.preferred_adapter))
        object.__setattr__(self, "configuration", freeze_value(dict(self.configuration)))
        object.__setattr__(self, "metadata", freeze_value(dict(self.metadata)))
        if not self.profile_id:
            object.__setattr__(self, "profile_id", _profile_id(self.name, self.renderer_type, self.output_format))


@dataclass
class RenderProfileRegistry:
    profiles: dict[str, RenderProfile] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.profiles:
            for profile in (
                RenderProfile(
                    name="text",
                    renderer_type="text",
                    output_format="text",
                    modality="text",
                    preferred_adapter="text",
                    description="Plain text rendering profile",
                ),
                RenderProfile(
                    name="structured_json",
                    renderer_type="json",
                    output_format="json",
                    modality="data",
                    preferred_adapter="json",
                    description="Structured JSON rendering profile",
                ),
                RenderProfile(
                    name="ascii",
                    renderer_type="ascii",
                    output_format="ascii",
                    modality="text",
                    preferred_adapter="ascii",
                    description="ASCII rendering profile",
                ),
                RenderProfile(
                    name="debug",
                    renderer_type="debug",
                    output_format="debug",
                    modality="debug",
                    preferred_adapter="debug",
                    description="Debug rendering profile",
                ),
                RenderProfile(
                    name="2d",
                    renderer_type="debug",
                    output_format="2d",
                    modality="2d",
                    preferred_adapter="debug",
                    description="2D rendering profile",
                ),
                RenderProfile(
                    name="2.5d",
                    renderer_type="debug",
                    output_format="2.5d",
                    modality="2.5d",
                    preferred_adapter="debug",
                    description="2.5D rendering profile",
                ),
                RenderProfile(
                    name="3d",
                    renderer_type="debug",
                    output_format="3d",
                    modality="3d",
                    preferred_adapter="debug",
                    description="3D rendering profile",
                ),
                RenderProfile(
                    name="image",
                    renderer_type="debug",
                    output_format="image",
                    modality="image",
                    preferred_adapter="debug",
                    description="Image rendering profile",
                ),
                RenderProfile(
                    name="video",
                    renderer_type="debug",
                    output_format="video",
                    modality="video",
                    preferred_adapter="debug",
                    description="Video rendering profile",
                ),
            ):
                self.register(profile)

    def register(self, profile: RenderProfile) -> RenderProfile:
        self.profiles[profile.profile_id] = profile
        self.profiles[profile.name] = profile
        self.profiles[profile.renderer_type] = profile
        self.profiles[profile.output_format] = profile
        return profile

    def lookup(self, identifier: str | None) -> RenderProfile | None:
        if identifier is None:
            return None
        return self.profiles.get(str(identifier))

    def select(self, profile: RenderProfile | str | None = None, *, renderer_type: str | None = None) -> RenderProfile:
        if isinstance(profile, RenderProfile):
            return profile
        if isinstance(profile, str):
            selected = self.lookup(profile)
            if selected is not None:
                return selected
        if renderer_type is not None:
            selected = self.lookup(renderer_type)
            if selected is not None:
                return selected
        return self.lookup("text") or next(iter(self.profiles.values()))

    def capabilities(self) -> Mapping[str, Any]:
        return freeze_value(
            {
                "profiles": sorted({profile.name for profile in self.profiles.values()}),
                "renderer_types": sorted({profile.renderer_type for profile in self.profiles.values()}),
                "output_formats": sorted({profile.output_format for profile in self.profiles.values()}),
            }
        )
