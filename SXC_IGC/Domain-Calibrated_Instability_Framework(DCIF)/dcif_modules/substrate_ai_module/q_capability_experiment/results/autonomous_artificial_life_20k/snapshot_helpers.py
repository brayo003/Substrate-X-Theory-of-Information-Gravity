"""
Snapshot and checkpoint helpers for the 20k-tick experiment.

Snapshots are full JSON dumps of world state at milestone ticks.
Checkpoints contain enough data to resume or audit the run.
"""
from __future__ import annotations

import json
import os
import time
from datetime import datetime, timezone
from typing import Any, TYPE_CHECKING

if TYPE_CHECKING:
    pass


def _safe(v: Any, default: Any = None) -> Any:
    """Return v if JSON-serialisable, else str(v)."""
    try:
        json.dumps(v)
        return v
    except Exception:
        return str(v) if v is not None else default


def extract_spectral(kernel: Any) -> dict:
    obs = kernel._last_spectral_transport_observable
    if obs is None:
        return {}
    return {
        "dominant_k":                  float(getattr(obs, "dominant_k", 0.0) or 0.0),
        "dominant_D":                  float(getattr(obs, "dominant_D", 0.0) or 0.0),
        "dominant_regime":             str(getattr(obs, "dominant_regime", "") or ""),
        "weighted_D":                  float(getattr(obs, "weighted_D", 0.0) or 0.0),
        "spectral_entropy":            float(getattr(obs, "spectral_entropy", 0.0) or 0.0),
        "c_nominal":                   float(getattr(obs, "c_nominal", 0.0) or 0.0),
        "tau_nominal":                 float(getattr(obs, "tau_nominal", 0.0) or 0.0),
        "k_critical":                  float(getattr(obs, "k_critical", 0.0) or 0.0),
        "propagating_power_fraction":  float(getattr(obs, "propagating_power_fraction", 0.0) or 0.0),
        "overdamped_power_fraction":   float(getattr(obs, "overdamped_power_fraction", 0.0) or 0.0),
        "critical_power_fraction":     float(getattr(obs, "critical_power_fraction", 0.0) or 0.0),
        "spectral_resolution":         float(getattr(obs, "spectral_resolution", 0.0) or 0.0),
        "num_modes":                   int(getattr(obs, "num_modes", 0) or 0),
    }


def extract_entity_snapshot(kernel: Any, entity_id: Any) -> dict:
    """Serialize an entity's current state into a plain dict."""
    entity = kernel.entity_registry.entities.get(entity_id)
    if entity is None:
        return {}
    try:
        if hasattr(entity, "serialize"):
            data = entity.serialize()
        else:
            data = {
                "entity_id": str(entity.entity_id),
                "entity_type": str(getattr(entity, "entity_type", "")),
                "display_name": str(getattr(entity, "display_name", "")),
                "components": {},
            }
        return _safe(data, {})
    except Exception as e:
        return {"error": str(e)}


def extract_entity_needs(entity_data: dict) -> dict:
    try:
        comps = entity_data.get("components", {})
        needs_comp = comps.get("NeedsComponent", {})
        return dict(needs_comp.get("needs", {}))
    except Exception:
        return {}


def extract_entity_location(entity_data: dict) -> str:
    try:
        comps = entity_data.get("components", {})
        tf = comps.get("TransformComponent", {})
        return str(tf.get("room", "unknown"))
    except Exception:
        return "unknown"


def extract_entity_inventory(entity_data: dict) -> dict:
    try:
        comps = entity_data.get("components", {})
        inv = comps.get("InventoryComponent", {})
        items = inv.get("items", [])
        result = {}
        for item in items:
            if isinstance(item, dict):
                result[item.get("identifier", "?")] = float(item.get("quantity", 0))
        return result
    except Exception:
        return {}


def build_world_snapshot(
    world_label: str,
    kernel: Any,
    entity_ids: list,
    entity_names: list,
    tick: int,
    run_id: str,
    llm_accounting: Any,
) -> dict:
    """Build a full world snapshot dict for a milestone tick."""
    entities = {}
    for eid, ename in zip(entity_ids, entity_names):
        edata = extract_entity_snapshot(kernel, eid)
        entities[ename] = {
            "entity_id": str(eid),
            "entity_name": ename,
            "snapshot": edata,
            "needs": extract_entity_needs(edata),
            "location": extract_entity_location(edata),
            "inventory": extract_entity_inventory(edata),
        }
        # Memory statistics
        mem = kernel.entity_registry.agent_memories.get(eid)
        if mem:
            try:
                entities[ename]["memory_stats"] = {
                    "total_memories": len(getattr(mem, "_memories", [])),
                }
            except Exception:
                entities[ename]["memory_stats"] = {}

    # Goals per entity
    goals_per_entity = {}
    try:
        for eid, ename in zip(entity_ids, entity_names):
            outstanding = kernel.planner_engine.goal_manager.outstanding()
            entity_goals = [g for g in outstanding if str(getattr(g, "entity_id", "")) == str(eid)]
            goals_per_entity[ename] = [
                {
                    "goal_id": str(getattr(g, "goal_id", "")),
                    "description": str(getattr(g, "description", "")),
                    "priority": float(getattr(g, "priority", 0.0)),
                    "status": str(getattr(g, "status", "")),
                }
                for g in entity_goals
            ]
    except Exception as e:
        goals_per_entity["error"] = str(e)

    # Field state
    field_info = {
        "c_nominal": float(getattr(kernel._propagation_params, "c_nominal", 0.0)
                          if kernel._propagation_params else 0.0),
        "tau_nominal": float(getattr(kernel._relaxation_params, "tau_nominal", 0.0)
                            if kernel._relaxation_params else 0.0),
    }

    return {
        "run_id": run_id,
        "world": world_label,
        "tick": tick,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "field_parameters": field_info,
        "spectral_observable": extract_spectral(kernel),
        "entities": entities,
        "goals_per_entity": goals_per_entity,
        "world_state_keys": list(kernel.current_state.keys()),
        "llm_accounting": llm_accounting.to_dict() if llm_accounting else {},
    }


def save_snapshot(output_dir: str, world_label: str, tick: int,
                  snapshot: dict) -> str:
    """Write snapshot to disk and return the file path."""
    fname = f"world_{world_label}_snapshot_tick{tick:07d}.json"
    path = os.path.join(output_dir, fname)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(snapshot, f, indent=2, default=str)
    return path


def save_checkpoint(output_dir: str, world_label: str, tick: int,
                    checkpoint: dict) -> str:
    """Write checkpoint to disk and return the file path."""
    fname = f"checkpoint_{world_label}_tick{tick:07d}.json"
    path = os.path.join(output_dir, "checkpoints", fname)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(checkpoint, f, indent=2, default=str)
    return path


def build_checkpoint(
    world_label: str,
    kernel: Any,
    entity_ids: list,
    entity_names: list,
    tick: int,
    run_id: str,
    llm_accounting: Any,
    field_trajectory: list,
) -> dict:
    """Build a checkpoint dict containing enough state to resume inspection."""
    snapshot = build_world_snapshot(
        world_label, kernel, entity_ids, entity_names, tick, run_id, llm_accounting
    )
    snapshot["checkpoint"] = True
    snapshot["field_trajectory_len"] = len(field_trajectory)
    snapshot["field_trajectory_last10"] = field_trajectory[-10:]
    return snapshot
