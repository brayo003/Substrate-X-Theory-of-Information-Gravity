from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Mapping

from ..core.contracts import freeze_value


@dataclass(frozen=True, slots=True)
class ActionDefinition:
    identifier: str
    preconditions: tuple[str, ...] = ()
    required_components: tuple[str, ...] = ()
    resource_requirements: Mapping[str, float] = field(default_factory=dict)
    cooldown: float = 0.0
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        object.__setattr__(self, "identifier", str(self.identifier))
        object.__setattr__(self, "preconditions", tuple(str(value) for value in self.preconditions))
        object.__setattr__(self, "required_components", tuple(str(value) for value in self.required_components))
        object.__setattr__(self, "resource_requirements", freeze_value({key: float(value) for key, value in dict(self.resource_requirements).items()}))
        object.__setattr__(self, "cooldown", float(self.cooldown))
        object.__setattr__(self, "metadata", freeze_value(dict(self.metadata)))


@dataclass
class ActionRegistry:
    definitions: dict[str, ActionDefinition] = field(default_factory=dict)

    def register(self, action: ActionDefinition) -> ActionDefinition:
        self.definitions[action.identifier] = action
        return action

    def unregister(self, identifier: str) -> ActionDefinition | None:
        return self.definitions.pop(str(identifier), None)

    def get(self, identifier: str) -> ActionDefinition | None:
        return self.definitions.get(str(identifier))

    def has(self, identifier: str) -> bool:
        return str(identifier) in self.definitions

    def list(self) -> tuple[ActionDefinition, ...]:
        return tuple(self.definitions[key] for key in sorted(self.definitions))

    def serialize(self) -> tuple[Mapping[str, Any], ...]:
        return tuple(
            freeze_value(
                {
                    "identifier": action.identifier,
                    "preconditions": action.preconditions,
                    "required_components": action.required_components,
                    "resource_requirements": action.resource_requirements,
                    "cooldown": action.cooldown,
                    "metadata": action.metadata,
                }
            )
            for action in self.list()
        )
