from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Mapping, Sequence

from ..core.contracts import freeze_value
from .resources import ResourceDescriptor


def component_key(component: Any) -> str:
    if isinstance(component, type):
        return component.__name__
    return getattr(component, "component_type", component.__class__.__name__)


def component_state(component: Any) -> Mapping[str, Any]:
    if hasattr(component, "to_state"):
        return freeze_value(dict(component.to_state()))
    if dataclass_is_instance(component):
        return freeze_value(asdict(component))
    if isinstance(component, Mapping):
        return freeze_value(dict(component))
    return freeze_value({"value": component})


def dataclass_is_instance(value: Any) -> bool:
    return hasattr(value, "__dataclass_fields__")


def deserialize_component(component_type: str, state: Mapping[str, Any]) -> Any:
    payload = dict(state)
    if component_type == "TransformComponent":
        return TransformComponent(
            position=tuple(payload.get("position", (0.0, 0.0, 0.0))),
            rotation=tuple(payload.get("rotation", (0.0, 0.0, 0.0, 1.0))),
            room=payload.get("room"),
        )
    if component_type == "InventoryComponent":
        items = tuple(
            ResourceDescriptor(
                identifier=str(item.get("identifier")),
                quantity=float(item.get("quantity", 0.0)),
                properties=dict(item.get("properties", {})),
            )
            for item in payload.get("items", ())
        )
        return InventoryComponent(items=items, capacity=payload.get("capacity"))
    if component_type == "HealthComponent":
        return HealthComponent(
            current=float(payload.get("current", 0.0)),
            maximum=float(payload.get("maximum", 0.0)),
            status=str(payload.get("status", "healthy")),
        )
    if component_type == "NeedsComponent":
        return NeedsComponent(needs=dict(payload.get("needs", {})))
    if component_type == "MemoryReferenceComponent":
        return MemoryReferenceComponent(references=tuple(payload.get("references", ())))
    if component_type == "RelationshipComponent":
        return RelationshipComponent(relationships=tuple(payload.get("relationships", ())))
    return payload


@dataclass(frozen=True, slots=True)
class TransformComponent:
    position: tuple[float, float, float] = (0.0, 0.0, 0.0)
    rotation: tuple[float, float, float, float] = (0.0, 0.0, 0.0, 1.0)
    room: str | None = None

    component_type: str = field(default="TransformComponent", init=False)

    def to_state(self) -> Mapping[str, Any]:
        return {
            "position": self.position,
            "rotation": self.rotation,
            "room": self.room,
            "component_type": self.component_type,
        }


@dataclass(frozen=True, slots=True)
class InventoryComponent:
    items: tuple[ResourceDescriptor, ...] = ()
    capacity: float | None = None

    component_type: str = field(default="InventoryComponent", init=False)

    def __post_init__(self) -> None:
        object.__setattr__(self, "items", tuple(self.items))
        if self.capacity is not None:
            object.__setattr__(self, "capacity", float(self.capacity))

    def to_state(self) -> Mapping[str, Any]:
        return {
            "items": tuple(component_state(item) for item in self.items),
            "capacity": self.capacity,
            "component_type": self.component_type,
        }


@dataclass(frozen=True, slots=True)
class HealthComponent:
    current: float
    maximum: float
    status: str = "healthy"

    component_type: str = field(default="HealthComponent", init=False)

    def __post_init__(self) -> None:
        object.__setattr__(self, "current", float(self.current))
        object.__setattr__(self, "maximum", float(self.maximum))

    def to_state(self) -> Mapping[str, Any]:
        return {
            "current": self.current,
            "maximum": self.maximum,
            "status": self.status,
            "component_type": self.component_type,
        }


@dataclass(frozen=True, slots=True)
class NeedsComponent:
    needs: Mapping[str, float] = field(default_factory=dict)

    component_type: str = field(default="NeedsComponent", init=False)

    def __post_init__(self) -> None:
        object.__setattr__(self, "needs", freeze_value({key: float(value) for key, value in dict(self.needs).items()}))

    def to_state(self) -> Mapping[str, Any]:
        return {
            "needs": self.needs,
            "component_type": self.component_type,
        }


@dataclass(frozen=True, slots=True)
class MemoryReferenceComponent:
    references: tuple[str, ...] = ()

    component_type: str = field(default="MemoryReferenceComponent", init=False)

    def __post_init__(self) -> None:
        object.__setattr__(self, "references", tuple(str(reference) for reference in self.references))

    def to_state(self) -> Mapping[str, Any]:
        return {
            "references": self.references,
            "component_type": self.component_type,
        }


@dataclass(frozen=True, slots=True)
class RelationshipComponent:
    relationships: tuple[str, ...] = ()

    component_type: str = field(default="RelationshipComponent", init=False)

    def __post_init__(self) -> None:
        object.__setattr__(self, "relationships", tuple(str(relationship) for relationship in self.relationships))

    def to_state(self) -> Mapping[str, Any]:
        return {
            "relationships": self.relationships,
            "component_type": self.component_type,
        }
