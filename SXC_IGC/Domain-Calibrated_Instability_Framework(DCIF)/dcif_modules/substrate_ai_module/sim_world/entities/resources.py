from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Mapping

from ..core.contracts import freeze_value


@dataclass(frozen=True, slots=True)
class ResourceDescriptor:
    identifier: str
    quantity: float
    properties: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        object.__setattr__(self, "identifier", str(self.identifier))
        object.__setattr__(self, "quantity", float(self.quantity))
        object.__setattr__(self, "properties", freeze_value(dict(self.properties)))

    def with_quantity(self, quantity: float) -> "ResourceDescriptor":
        return ResourceDescriptor(self.identifier, quantity, self.properties)

    def to_state(self) -> Mapping[str, Any]:
        return {
            "identifier": self.identifier,
            "quantity": self.quantity,
            "properties": self.properties,
        }


@dataclass
class ResourceStore:
    resources: dict[str, ResourceDescriptor] = field(default_factory=dict)

    def add(self, resource: ResourceDescriptor) -> ResourceDescriptor:
        existing = self.resources.get(resource.identifier)
        if existing is None:
            self.resources[resource.identifier] = resource
        else:
            merged_quantity = existing.quantity + resource.quantity
            merged_properties = dict(existing.properties)
            merged_properties.update(resource.properties)
            self.resources[resource.identifier] = ResourceDescriptor(
                resource.identifier,
                merged_quantity,
                merged_properties,
            )
        return self.resources[resource.identifier]

    def remove(self, identifier: str, quantity: float | None = None) -> ResourceDescriptor | None:
        existing = self.resources.get(identifier)
        if existing is None:
            return None
        if quantity is None or quantity >= existing.quantity:
            return self.resources.pop(identifier)
        remaining = existing.quantity - quantity
        self.resources[identifier] = existing.with_quantity(remaining)
        return self.resources[identifier]

    def get(self, identifier: str) -> ResourceDescriptor | None:
        return self.resources.get(identifier)

    def list(self) -> tuple[ResourceDescriptor, ...]:
        return tuple(self.resources[key] for key in sorted(self.resources))

    def total_quantity(self, identifier: str) -> float:
        descriptor = self.resources.get(identifier)
        return 0.0 if descriptor is None else descriptor.quantity
