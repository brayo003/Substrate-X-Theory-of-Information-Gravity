from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Mapping

from .contracts import freeze_value
from .ids import WorldId


@dataclass(frozen=True, slots=True)
class KernelConfig:
    world_name: str = "sim_world"
    seed: str = "default"
    world_id: WorldId | None = None
    initial_state: Mapping[str, Any] = field(default_factory=dict)
    allow_rollback: bool = True
    enable_llm_generation: bool = True
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if self.world_id is None:
            object.__setattr__(self, "world_id", WorldId.new(self.world_name, self.seed))
        object.__setattr__(self, "initial_state", freeze_value(dict(self.initial_state)))
        object.__setattr__(self, "metadata", freeze_value(dict(self.metadata)))
