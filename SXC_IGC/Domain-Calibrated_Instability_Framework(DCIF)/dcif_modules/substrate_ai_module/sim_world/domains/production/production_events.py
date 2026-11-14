from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Mapping, Sequence


@dataclass(frozen=True, slots=True)
class ProductionStarted:
    job_id: str
    recipe_id: str
    facility_id: str
    worker_id: str
    tick: int = 0
    event_type: str = field(default="ProductionStarted", init=False)

    def to_dict(self) -> dict[str, Any]:
        return {
            "event_type": self.event_type,
            "job_id": self.job_id,
            "recipe_id": self.recipe_id,
            "facility_id": self.facility_id,
            "worker_id": self.worker_id,
            "tick": self.tick,
        }


@dataclass(frozen=True, slots=True)
class InputsReserved:
    job_id: str
    inputs: tuple[tuple[str, float], ...]
    source_id: str
    tick: int = 0
    event_type: str = field(default="InputsReserved", init=False)

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "inputs",
            tuple(sorted((str(k), max(0.0, float(v))) for k, v in self.inputs)),
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "event_type": self.event_type,
            "job_id": self.job_id,
            "inputs": [{"identifier": k, "quantity": v} for k, v in self.inputs],
            "source_id": self.source_id,
            "tick": self.tick,
        }


@dataclass(frozen=True, slots=True)
class ProductionProgressed:
    job_id: str
    progress_before: float
    progress_after: float
    duration_ticks: int
    tick: int = 0
    event_type: str = field(default="ProductionProgressed", init=False)

    def __post_init__(self) -> None:
        object.__setattr__(self, "progress_before", max(0.0, min(1.0, float(self.progress_before))))
        object.__setattr__(self, "progress_after", max(0.0, min(1.0, float(self.progress_after))))
        object.__setattr__(self, "duration_ticks", max(1, int(self.duration_ticks)))

    def to_dict(self) -> dict[str, Any]:
        return {
            "event_type": self.event_type,
            "job_id": self.job_id,
            "progress_before": self.progress_before,
            "progress_after": self.progress_after,
            "duration_ticks": self.duration_ticks,
            "tick": self.tick,
        }


@dataclass(frozen=True, slots=True)
class ProductionCompleted:
    job_id: str
    recipe_id: str
    outputs: tuple[tuple[str, float], ...]
    tick: int = 0
    event_type: str = field(default="ProductionCompleted", init=False)

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "outputs",
            tuple(sorted((str(k), max(0.0, float(v))) for k, v in self.outputs)),
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "event_type": self.event_type,
            "job_id": self.job_id,
            "recipe_id": self.recipe_id,
            "outputs": [{"identifier": k, "quantity": v} for k, v in self.outputs],
            "tick": self.tick,
        }


@dataclass(frozen=True, slots=True)
class ProductionCancelled:
    job_id: str
    reason: str
    inputs_returned: tuple[tuple[str, float], ...]
    tick: int = 0
    event_type: str = field(default="ProductionCancelled", init=False)

    def __post_init__(self) -> None:
        object.__setattr__(self, "reason", str(self.reason))
        object.__setattr__(
            self,
            "inputs_returned",
            tuple(sorted((str(k), max(0.0, float(v))) for k, v in self.inputs_returned)),
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "event_type": self.event_type,
            "job_id": self.job_id,
            "reason": self.reason,
            "inputs_returned": [{"identifier": k, "quantity": v} for k, v in self.inputs_returned],
            "tick": self.tick,
        }


@dataclass(frozen=True, slots=True)
class ToolUsed:
    tool_type: str
    user_id: str
    job_id: str
    uses_incremented: int = 1
    durability_delta: float = 0.0
    tick: int = 0
    event_type: str = field(default="ToolUsed", init=False)

    def __post_init__(self) -> None:
        object.__setattr__(self, "tool_type", str(self.tool_type))
        object.__setattr__(self, "user_id", str(self.user_id))
        object.__setattr__(self, "job_id", str(self.job_id))
        object.__setattr__(self, "uses_incremented", max(0, int(self.uses_incremented)))
        object.__setattr__(self, "durability_delta", float(self.durability_delta))

    def to_dict(self) -> dict[str, Any]:
        return {
            "event_type": self.event_type,
            "tool_type": self.tool_type,
            "user_id": self.user_id,
            "job_id": self.job_id,
            "uses_incremented": self.uses_incremented,
            "durability_delta": self.durability_delta,
            "tick": self.tick,
        }


@dataclass(frozen=True, slots=True)
class ToolBroken:
    tool_type: str
    owner_id: str
    job_id: str
    tick: int = 0
    event_type: str = field(default="ToolBroken", init=False)

    def to_dict(self) -> dict[str, Any]:
        return {
            "event_type": self.event_type,
            "tool_type": self.tool_type,
            "owner_id": self.owner_id,
            "job_id": self.job_id,
            "tick": self.tick,
        }


@dataclass(frozen=True, slots=True)
class GoodsDeposited:
    job_id: str
    destination_id: str
    goods: tuple[tuple[str, float], ...]
    tick: int = 0
    event_type: str = field(default="GoodsDeposited", init=False)

    def __post_init__(self) -> None:
        object.__setattr__(self, "destination_id", str(self.destination_id))
        object.__setattr__(
            self,
            "goods",
            tuple(sorted((str(k), max(0.0, float(v))) for k, v in self.goods)),
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "event_type": self.event_type,
            "job_id": self.job_id,
            "destination_id": self.destination_id,
            "goods": [{"identifier": k, "quantity": v} for k, v in self.goods],
            "tick": self.tick,
        }


@dataclass(frozen=True, slots=True)
class RecipeExecuted:
    recipe_id: str
    facility_id: str
    worker_id: str
    inputs: tuple[tuple[str, float], ...]
    outputs: tuple[tuple[str, float], ...]
    duration_ticks: int
    tick: int = 0
    event_type: str = field(default="RecipeExecuted", init=False)

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "inputs",
            tuple(sorted((str(k), max(0.0, float(v))) for k, v in self.inputs)),
        )
        object.__setattr__(
            self,
            "outputs",
            tuple(sorted((str(k), max(0.0, float(v))) for k, v in self.outputs)),
        )
        object.__setattr__(self, "duration_ticks", max(1, int(self.duration_ticks)))

    def to_dict(self) -> dict[str, Any]:
        return {
            "event_type": self.event_type,
            "recipe_id": self.recipe_id,
            "facility_id": self.facility_id,
            "worker_id": self.worker_id,
            "inputs": [{"identifier": k, "quantity": v} for k, v in self.inputs],
            "outputs": [{"identifier": k, "quantity": v} for k, v in self.outputs],
            "duration_ticks": self.duration_ticks,
            "tick": self.tick,
        }


PRODUCTION_EVENT_TYPES: tuple[str, ...] = (
    "ProductionStarted",
    "InputsReserved",
    "ProductionProgressed",
    "ProductionCompleted",
    "ProductionCancelled",
    "ToolUsed",
    "ToolBroken",
    "GoodsDeposited",
    "RecipeExecuted",
)
