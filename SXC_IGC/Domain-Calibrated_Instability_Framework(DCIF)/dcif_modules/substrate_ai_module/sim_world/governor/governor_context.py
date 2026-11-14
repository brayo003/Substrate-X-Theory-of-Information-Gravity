from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Mapping

from ..core.contracts import freeze_value
from ..core.ids import RevisionId, TickId, WorldId


@dataclass(frozen=True, slots=True)
class GovernorContext:
    world_id: WorldId
    tick_id: TickId | None
    revision: RevisionId | None
    policy_version: str
    simulation_diagnostics: Any = None
    planner_diagnostics: Any = None
    transport_observation: Any = None
    verification_report: Any = None
    renderer_report: Any = None
    kernel_status: Mapping[str, Any] = field(default_factory=dict)
    correlation_id: str = ""
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        object.__setattr__(self, "policy_version", str(self.policy_version))
        object.__setattr__(self, "correlation_id", str(self.correlation_id))
        object.__setattr__(self, "kernel_status", freeze_value(dict(self.kernel_status)))
        object.__setattr__(self, "metadata", freeze_value(dict(self.metadata)))
