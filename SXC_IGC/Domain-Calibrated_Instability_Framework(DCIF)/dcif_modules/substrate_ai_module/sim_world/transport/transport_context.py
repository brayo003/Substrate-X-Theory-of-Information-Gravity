from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Mapping, Sequence

from ..core.contracts import RenderProposal, RenderSnapshot, TransitionProposal, VerificationReport, freeze_value
from ..core.ids import RevisionId, WorldId


@dataclass(frozen=True, slots=True)
class TransportContext:
    world_id: WorldId
    previous_snapshot: RenderSnapshot | None
    current_snapshot: RenderSnapshot | None
    previous_revision: RevisionId | None
    current_revision: RevisionId | None
    transition_proposals: tuple[TransitionProposal, ...] = field(default_factory=tuple)
    render_proposal: RenderProposal | None = None
    verification_report: VerificationReport | None = None
    configuration: Mapping[str, Any] = field(default_factory=dict)
    calibration_profile: Any = None
    representation_type: str = "snapshot_transition"
    domain_adapter_id: str = "default"
    correlation_id: str = ""
    tick_number: int = 0
    sampling_window: Mapping[str, Any] = field(default_factory=dict)
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        object.__setattr__(self, "transition_proposals", tuple(self.transition_proposals))
        object.__setattr__(self, "representation_type", str(self.representation_type))
        object.__setattr__(self, "domain_adapter_id", str(self.domain_adapter_id))
        object.__setattr__(self, "correlation_id", str(self.correlation_id))
        object.__setattr__(self, "tick_number", int(self.tick_number))
        object.__setattr__(self, "configuration", freeze_value(dict(self.configuration)))
        object.__setattr__(self, "sampling_window", freeze_value(dict(self.sampling_window)))
        object.__setattr__(self, "metadata", freeze_value(dict(self.metadata)))
