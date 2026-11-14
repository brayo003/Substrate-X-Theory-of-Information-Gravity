from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Mapping


@dataclass(frozen=True, slots=True)
class ResourceEvent:
    event_type: str  # ResourceCreated, ResourceTransferred, ResourceConsumed, ResourceStored, ResourceExhausted, ResourceDeposited, ResourceWithdrawn
    resource_type: str
    quantity: float
    source_id: str | None = None
    destination_id: str | None = None
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "event_type": self.event_type,
            "resource_type": self.resource_type,
            "quantity": self.quantity,
            "source_id": self.source_id,
            "destination_id": self.destination_id,
            "metadata": dict(self.metadata),
        }

    @staticmethod
    def created(resource_type: str, quantity: float, destination_id: str | None = None, metadata: Mapping[str, Any] | None = None) -> ResourceEvent:
        return ResourceEvent("ResourceCreated", resource_type, quantity, None, destination_id, metadata or {})

    @staticmethod
    def transferred(resource_type: str, quantity: float, source_id: str | None, destination_id: str | None, metadata: Mapping[str, Any] | None = None) -> ResourceEvent:
        return ResourceEvent("ResourceTransferred", resource_type, quantity, source_id, destination_id, metadata or {})

    @staticmethod
    def consumed(resource_type: str, quantity: float, source_id: str | None, metadata: Mapping[str, Any] | None = None) -> ResourceEvent:
        return ResourceEvent("ResourceConsumed", resource_type, quantity, source_id, None, metadata or {})

    @staticmethod
    def stored(resource_type: str, quantity: float, source_id: str | None, destination_id: str | None, metadata: Mapping[str, Any] | None = None) -> ResourceEvent:
        return ResourceEvent("ResourceStored", resource_type, quantity, source_id, destination_id, metadata or {})

    @staticmethod
    def exhausted(resource_type: str, quantity: float, source_id: str | None, metadata: Mapping[str, Any] | None = None) -> ResourceEvent:
        return ResourceEvent("ResourceExhausted", resource_type, quantity, source_id, None, metadata or {})

    @staticmethod
    def deposited(resource_type: str, quantity: float, source_id: str | None, destination_id: str | None, metadata: Mapping[str, Any] | None = None) -> ResourceEvent:
        return ResourceEvent("ResourceDeposited", resource_type, quantity, source_id, destination_id, metadata or {})

    @staticmethod
    def withdrawn(resource_type: str, quantity: float, source_id: str | None, destination_id: str | None, metadata: Mapping[str, Any] | None = None) -> ResourceEvent:
        return ResourceEvent("ResourceWithdrawn", resource_type, quantity, source_id, destination_id, metadata or {})
