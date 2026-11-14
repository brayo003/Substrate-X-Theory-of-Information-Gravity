from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Mapping


def deterministic_hash(seed: str) -> int:
    s = str(seed or "")
    val = hash(s) % (2**32)
    return abs(val)


CORE_RESOURCES: tuple[str, ...] = (
    "food",
    "water",
    "wood",
    "stone",
    "iron",
    "fuel",
    "tools",
    "seeds",
)


@dataclass(frozen=True, slots=True)
class ResourceItem:
    resource_id: str
    resource_type: str
    quantity: float
    owner_id: str | None = None
    location_id: str | None = None
    container_id: str | None = None
    quality: float = 1.0
    maximum_capacity: float = 500.0

    def __post_init__(self) -> None:
        object.__setattr__(self, "resource_id", str(self.resource_id))
        object.__setattr__(self, "resource_type", str(self.resource_type))
        object.__setattr__(self, "quantity", max(0.0, float(self.quantity)))
        object.__setattr__(self, "quality", max(0.0, min(1.0, float(self.quality))))
        object.__setattr__(self, "maximum_capacity", float(self.maximum_capacity))

    @property
    def owner(self) -> str | None:
        return self.owner_id

    @property
    def location(self) -> str | None:
        return self.location_id

    @property
    def container(self) -> str | None:
        return self.container_id

    @staticmethod
    def create(
        resource_type: str,
        quantity: float,
        *,
        owner_id: str | None = None,
        location_id: str | None = None,
        container_id: str | None = None,
        quality: float = 1.0,
        maximum_capacity: float = 500.0,
        seed: str | None = None,
    ) -> ResourceItem:
        unique_seed = seed or f"{resource_type}:{quantity}:{owner_id}:{location_id}:{container_id}"
        resource_id = f"resource_{deterministic_hash(unique_seed)}"
        return ResourceItem(
            resource_id=resource_id,
            resource_type=resource_type,
            quantity=quantity,
            owner_id=owner_id,
            location_id=location_id,
            container_id=container_id,
            quality=quality,
            maximum_capacity=maximum_capacity,
        )

    def to_descriptor(self) -> dict[str, Any]:
        return {
            "identifier": self.resource_type,
            "quantity": self.quantity,
            "properties": {
                "resource_id": self.resource_id,
                "owner_id": self.owner_id,
                "location_id": self.location_id,
                "container_id": self.container_id,
                "quality": self.quality,
                "maximum_capacity": self.maximum_capacity,
            },
        }

    def to_dict(self) -> dict[str, Any]:
        return {
            "resource_id": self.resource_id,
            "resource_type": self.resource_type,
            "quantity": self.quantity,
            "owner": self.owner_id,
            "owner_id": self.owner_id,
            "location": self.location_id,
            "location_id": self.location_id,
            "container": self.container_id,
            "container_id": self.container_id,
            "quality": self.quality,
            "maximum_capacity": self.maximum_capacity,
        }

    @staticmethod
    def from_descriptor(data: Mapping[str, Any], default_owner: str | None = None) -> ResourceItem:
        identifier = str(data.get("identifier", "food"))
        quantity = float(data.get("quantity", 0.0))
        props = dict(data.get("properties", {}))
        seed = f"{identifier}:{quantity}:{default_owner}"
        resource_id = props.get("resource_id") or f"resource_{deterministic_hash(seed)}"
        return ResourceItem(
            resource_id=resource_id,
            resource_type=identifier,
            quantity=quantity,
            owner_id=props.get("owner_id") or default_owner,
            location_id=props.get("location_id"),
            container_id=props.get("container_id"),
            quality=float(props.get("quality", 1.0)),
            maximum_capacity=float(props.get("maximum_capacity", 500.0)),
        )
