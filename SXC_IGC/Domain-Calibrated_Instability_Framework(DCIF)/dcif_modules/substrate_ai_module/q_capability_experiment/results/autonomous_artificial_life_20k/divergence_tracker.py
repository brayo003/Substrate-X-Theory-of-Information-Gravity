"""
Divergence tracker for 13-layer causal chain comparison between World A and World B.

Records the first tick at which each causal layer differs, for each entity
and at the world level.
"""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import Any, Optional

try:
    from experiment_config import CAUSAL_LAYERS
except ImportError:
    from .experiment_config import CAUSAL_LAYERS


@dataclass
class DivergenceEvent:
    layer: str
    tick: int
    entity: Optional[str]   # None = world-level
    description: str
    a_value: Any
    b_value: Any


class DivergenceTracker:
    """
    Records the first divergence tick for each of the 13 causal layers,
    at both world level and per-entity level.
    """

    def __init__(self, entity_names: list[str]) -> None:
        self.entity_names = list(entity_names)
        # world-level: layer → first tick (or None)
        self._world: dict[str, Optional[int]] = {L: None for L in CAUSAL_LAYERS}
        # per-entity: entity_name → layer → first tick (or None)
        self._entity: dict[str, dict[str, Optional[int]]] = {
            name: {L: None for L in CAUSAL_LAYERS}
            for name in entity_names
        }
        self._events: list[DivergenceEvent] = []

    def _record(self, layer: str, tick: int, entity: Optional[str],
                a_val: Any, b_val: Any) -> None:
        desc = f"{layer} differs at tick {tick}"
        if entity:
            desc += f" for {entity}"
        self._events.append(DivergenceEvent(
            layer=layer, tick=tick, entity=entity,
            description=desc, a_value=a_val, b_value=b_val,
        ))

    # ── World-level comparison ─────────────────────────────────────────────

    def check_field_parameters(self, tick: int, a_c: float, b_c: float,
                                a_tau: float, b_tau: float) -> None:
        if self._world["field_parameters"] is None and (a_c != b_c or a_tau != b_tau):
            self._world["field_parameters"] = tick
            self._record("field_parameters", tick, None,
                         {"c": a_c, "tau": a_tau}, {"c": b_c, "tau": b_tau})

    def check_field_state(self, tick: int, a_hash: str, b_hash: str) -> None:
        if self._world["physical_field_state"] is None and a_hash != b_hash:
            self._world["physical_field_state"] = tick
            self._record("physical_field_state", tick, None, a_hash, b_hash)

    def check_spectral(self, tick: int, a_spec: dict, b_spec: dict) -> None:
        if self._world["spectral_observable"] is None:
            # Compare key spectral fields
            keys = ["dominant_D", "dominant_regime", "weighted_D",
                    "spectral_entropy", "dominant_k"]
            differs = any(a_spec.get(k) != b_spec.get(k) for k in keys)
            if differs:
                self._world["spectral_observable"] = tick
                self._record("spectral_observable", tick, None, a_spec, b_spec)

    def check_world_state(self, tick: int, a_hash: str, b_hash: str) -> None:
        if self._world["world_state"] is None and a_hash != b_hash:
            self._world["world_state"] = tick
            self._record("world_state", tick, None, a_hash, b_hash)

    # ── Per-entity comparison ──────────────────────────────────────────────

    def _str_safe(self, v: Any) -> str:
        try:
            return json.dumps(v, sort_keys=True, default=str)
        except Exception:
            return str(v)

    def check_perception(self, tick: int, entity: str,
                         a_perc: dict, b_perc: dict) -> None:
        if self._entity[entity]["agent_perception"] is None:
            if self._str_safe(a_perc) != self._str_safe(b_perc):
                self._entity[entity]["agent_perception"] = tick
                if self._world["agent_perception"] is None:
                    self._world["agent_perception"] = tick
                self._record("agent_perception", tick, entity, a_perc, b_perc)

    def check_llm_input(self, tick: int, entity: str,
                        a_hash: str, b_hash: str) -> None:
        if self._entity[entity]["llm_input"] is None and a_hash != b_hash:
            self._entity[entity]["llm_input"] = tick
            if self._world["llm_input"] is None:
                self._world["llm_input"] = tick
            self._record("llm_input", tick, entity, a_hash, b_hash)

    def check_llm_output(self, tick: int, entity: str,
                         a_hash: str, b_hash: str) -> None:
        if self._entity[entity]["llm_output"] is None and a_hash != b_hash:
            self._entity[entity]["llm_output"] = tick
            if self._world["llm_output"] is None:
                self._world["llm_output"] = tick
            self._record("llm_output", tick, entity, a_hash, b_hash)

    def check_intent(self, tick: int, entity: str,
                     a_intent: str, b_intent: str) -> None:
        if self._entity[entity]["intent"] is None and a_intent != b_intent:
            self._entity[entity]["intent"] = tick
            if self._world["intent"] is None:
                self._world["intent"] = tick
            self._record("intent", tick, entity, a_intent, b_intent)

    def check_goal(self, tick: int, entity: str,
                   a_goal: str, b_goal: str) -> None:
        if self._entity[entity]["goal"] is None and a_goal != b_goal:
            self._entity[entity]["goal"] = tick
            if self._world["goal"] is None:
                self._world["goal"] = tick
            self._record("goal", tick, entity, a_goal, b_goal)

    def check_plan(self, tick: int, entity: str,
                   a_plan: str, b_plan: str) -> None:
        if self._entity[entity]["plan"] is None and a_plan != b_plan:
            self._entity[entity]["plan"] = tick
            if self._world["plan"] is None:
                self._world["plan"] = tick
            self._record("plan", tick, entity, a_plan, b_plan)

    def check_action(self, tick: int, entity: str,
                     a_action: str, b_action: str) -> None:
        if self._entity[entity]["action"] is None and a_action != b_action:
            self._entity[entity]["action"] = tick
            if self._world["action"] is None:
                self._world["action"] = tick
            self._record("action", tick, entity, a_action, b_action)

    def check_entity_state(self, tick: int, entity: str,
                           a_hash: str, b_hash: str) -> None:
        if self._entity[entity]["entity_state"] is None and a_hash != b_hash:
            self._entity[entity]["entity_state"] = tick
            if self._world["entity_state"] is None:
                self._world["entity_state"] = tick
            self._record("entity_state", tick, entity, a_hash, b_hash)

    def check_memory(self, tick: int, entity: str,
                     a_count: int, b_count: int) -> None:
        if self._entity[entity]["memory"] is None and a_count != b_count:
            self._entity[entity]["memory"] = tick
            if self._world["memory"] is None:
                self._world["memory"] = tick
            self._record("memory", tick, entity,
                         {"memory_count": a_count}, {"memory_count": b_count})

    # ── Output ────────────────────────────────────────────────────────────

    def to_dict(self) -> dict:
        return {
            "world_level_first_divergence": {
                k: v for k, v in self._world.items()
            },
            "entity_level_first_divergence": {
                ename: {k: v for k, v in layers.items()}
                for ename, layers in self._entity.items()
            },
            "divergence_events": [
                {
                    "layer": e.layer,
                    "tick": e.tick,
                    "entity": e.entity,
                    "description": e.description,
                    "a_value": str(e.a_value)[:200],
                    "b_value": str(e.b_value)[:200],
                }
                for e in self._events
            ],
            "total_divergence_events": len(self._events),
            "first_divergence_tick_overall": self._first_overall(),
        }

    def _first_overall(self) -> Optional[int]:
        ticks = [v for v in self._world.values() if v is not None]
        return min(ticks) if ticks else None
