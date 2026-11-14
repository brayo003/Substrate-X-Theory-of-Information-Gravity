from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable, Mapping, Sequence

from ..core.contracts import TransitionProposal, freeze_value
from ..core.ids import EntityId
from .simulation_context import SimulationContext


@dataclass(frozen=True, slots=True)
class RuleViolation:
    code: str
    message: str
    proposal_index: int
    subject: str
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        object.__setattr__(self, "code", str(self.code))
        object.__setattr__(self, "message", str(self.message))
        object.__setattr__(self, "subject", str(self.subject))
        object.__setattr__(self, "metadata", freeze_value(dict(self.metadata)))


RuleCallable = Callable[[SimulationContext, tuple[TransitionProposal, ...]], tuple[RuleViolation, ...]]


@dataclass
class WorldRules:
    rules: dict[str, RuleCallable] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.rules:
            self.rules = {
                "single_writer": self._rule_single_writer,
                "living_entities_only": self._rule_living_entities_only,
                "resource_non_negative": self._rule_resource_non_negative,
                "door_state": self._rule_door_state,
            }

    def register(self, name: str, rule: RuleCallable) -> None:
        self.rules[str(name)] = rule

    def evaluate(self, context: SimulationContext, proposals: tuple[TransitionProposal, ...]) -> tuple[RuleViolation, ...]:
        violations: list[RuleViolation] = []
        for rule in self.rules.values():
            violations.extend(rule(context, proposals))
        return tuple(violations)

    def resolve_conflicts(
        self,
        context: SimulationContext,
        proposals: tuple[TransitionProposal, ...],
    ) -> tuple[TransitionProposal, ...]:
        accepted: list[TransitionProposal] = []
        seen_entities: set[str] = set()
        conflicts: list[RuleViolation] = []
        for index, proposal in enumerate(proposals):
            entity_ids = self._proposal_entities(proposal)
            if entity_ids and seen_entities.intersection(entity_ids):
                conflicts.append(
                    RuleViolation(
                        code="conflict",
                        message="proposal conflicts with an earlier write",
                        proposal_index=index,
                        subject=proposal.subject,
                        metadata={"entities": sorted(entity_ids)},
                    )
                )
                continue
            accepted.append(proposal)
            seen_entities.update(entity_ids)
        return tuple(accepted)

    def _proposal_entities(self, proposal: TransitionProposal) -> set[str]:
        entities: set[str] = set()
        metadata = dict(proposal.metadata)
        for key in ("entity_id", "actor_id", "target_id", "item_id"):
            value = metadata.get(key)
            if isinstance(value, str) and value:
                entities.add(value)
        patch = dict(proposal.patch)
        for entity_id in dict(patch.get("entities", {})).keys():
            entities.add(str(entity_id))
        return entities

    def _rule_single_writer(self, context: SimulationContext, proposals: tuple[TransitionProposal, ...]) -> tuple[RuleViolation, ...]:
        return ()

    def _rule_living_entities_only(self, context: SimulationContext, proposals: tuple[TransitionProposal, ...]) -> tuple[RuleViolation, ...]:
        violations: list[RuleViolation] = []
        for index, proposal in enumerate(proposals):
            actor_id = dict(proposal.metadata).get("entity_id")
            if not isinstance(actor_id, str):
                continue
            entity = dict(context.world_state.get("entities", {})).get(actor_id)
            if entity is None:
                continue
            if not bool(entity.get("alive", True)):
                violations.append(RuleViolation("dead_entity", "dead entities cannot act", index, proposal.subject, {"entity_id": actor_id}))
        return tuple(violations)

    def _rule_resource_non_negative(self, context: SimulationContext, proposals: tuple[TransitionProposal, ...]) -> tuple[RuleViolation, ...]:
        return ()

    def _rule_door_state(self, context: SimulationContext, proposals: tuple[TransitionProposal, ...]) -> tuple[RuleViolation, ...]:
        return ()

