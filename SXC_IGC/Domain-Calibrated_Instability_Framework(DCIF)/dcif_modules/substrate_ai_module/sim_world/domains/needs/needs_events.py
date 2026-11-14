from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Mapping


@dataclass(frozen=True, slots=True)
class NeedEvent:
    event_type: str  # NeedIncreased, NeedReduced, NeedCritical, NeedSatisfied, NeedRecovered
    entity_id: str
    need_name: str
    old_value: float
    new_value: float
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "event_type": self.event_type,
            "entity_id": self.entity_id,
            "need_name": self.need_name,
            "old_value": self.old_value,
            "new_value": self.new_value,
            "metadata": dict(self.metadata),
        }
