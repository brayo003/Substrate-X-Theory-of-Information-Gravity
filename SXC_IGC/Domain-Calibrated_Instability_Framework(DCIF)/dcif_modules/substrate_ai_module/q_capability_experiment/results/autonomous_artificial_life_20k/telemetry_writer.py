"""
Telemetry writer: structured JSONL disk persistence for the 20k-tick experiment.

Writes one record per tick per world. Each record contains the full 13-layer
causal chain snapshot, LLM accounting, and entity states.
"""
from __future__ import annotations

import hashlib
import json
import os
import time
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from typing import Any


# ─── Hash helpers ─────────────────────────────────────────────────────────────

def sha256(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8", errors="replace")).hexdigest()


def sha256_obj(obj: Any) -> str:
    try:
        return sha256(json.dumps(obj, sort_keys=True, default=str))
    except Exception:
        return sha256(str(obj))


# ─── LLM call record ──────────────────────────────────────────────────────────

@dataclass
class LLMCallRecord:
    world: str
    entity_name: str
    entity_id: str
    tick: int
    call_index: int          # global call sequence number for this world
    prompt: str
    prompt_hash: str
    response: str
    response_hash: str
    success: bool
    error: str
    latency_s: float
    eval_count: int          # output tokens
    prompt_eval_count: int   # input tokens
    timestamp: str


# ─── Tick telemetry record ────────────────────────────────────────────────────

@dataclass
class TickRecord:
    world: str
    tick: int
    wall_time_s: float               # wall time for this tick
    timestamp: str

    # Layer 1 – field parameters
    c_nominal: float
    tau_nominal: float

    # Layer 2 – physical field state (summary hash)
    field_state_hash: str

    # Layer 3 – spectral observable
    spectral: dict

    # Layer 4 – agent perception (per entity: what the context builder provided)
    perception: dict   # entity_name → perception dict

    # Layer 5 – LLM inputs (per entity: prompt hash + preview)
    llm_inputs: dict   # entity_name → {prompt_hash, prompt_preview}

    # Layer 6 – LLM outputs (per entity: response hash + text)
    llm_outputs: dict  # entity_name → {response_hash, response_text, success}

    # Layer 7 – intent (per entity)
    intents: dict

    # Layer 8 – goal (per entity)
    goals: dict

    # Layer 9 – plan
    plans: dict

    # Layer 10 – action
    actions: dict

    # Layer 11 – entity state (per entity)
    entity_states: dict

    # Layer 12 – world state hash
    world_state_hash: str

    # Layer 13 – memory (per entity: write count, total count)
    memory: dict

    # LLM accounting for this tick
    llm_calls_this_tick: int
    llm_success_this_tick: int
    llm_fail_this_tick: int


# ─── World-level running totals ───────────────────────────────────────────────

@dataclass
class LLMAccountingTotals:
    total_calls: int = 0
    successful_calls: int = 0
    failed_calls: int = 0
    timeout_calls: int = 0
    latencies: list = field(default_factory=list)
    calls_per_entity: dict = field(default_factory=dict)  # entity_name → count

    @property
    def avg_latency(self) -> float:
        return sum(self.latencies) / len(self.latencies) if self.latencies else 0.0

    @property
    def min_latency(self) -> float:
        return min(self.latencies) if self.latencies else 0.0

    @property
    def max_latency(self) -> float:
        return max(self.latencies) if self.latencies else 0.0

    def record(self, entity_name: str, success: bool, latency: float,
               error: str = "") -> None:
        self.total_calls += 1
        self.latencies.append(latency)
        if success:
            self.successful_calls += 1
        else:
            self.failed_calls += 1
            if "timed out" in error.lower():
                self.timeout_calls += 1
        self.calls_per_entity[entity_name] = (
            self.calls_per_entity.get(entity_name, 0) + 1
        )

    def to_dict(self) -> dict:
        return {
            "total_calls": self.total_calls,
            "successful_calls": self.successful_calls,
            "failed_calls": self.failed_calls,
            "timeout_calls": self.timeout_calls,
            "avg_latency_s": self.avg_latency,
            "min_latency_s": self.min_latency,
            "max_latency_s": self.max_latency,
            "calls_per_entity": dict(self.calls_per_entity),
        }


# ─── TelemetryWriter ─────────────────────────────────────────────────────────

class TelemetryWriter:
    """
    Writes experiment telemetry to disk in JSONL format.

    Files produced:
      world_A_telemetry.jsonl   – one record per tick (World A)
      world_B_telemetry.jsonl   – one record per tick (World B)
      world_A_llm_calls.jsonl   – one record per LLM call (World A)
      world_B_llm_calls.jsonl   – one record per LLM call (World B)
    """

    def __init__(self, output_dir: str) -> None:
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)

        self._tick_files: dict[str, Any] = {}
        self._llm_files: dict[str, Any] = {}

    def _tick_fh(self, world: str):
        if world not in self._tick_files:
            path = os.path.join(self.output_dir, f"world_{world}_telemetry.jsonl")
            self._tick_files[world] = open(path, "a", encoding="utf-8")
        return self._tick_files[world]

    def _llm_fh(self, world: str):
        if world not in self._llm_files:
            path = os.path.join(self.output_dir, f"world_{world}_llm_calls.jsonl")
            self._llm_files[world] = open(path, "a", encoding="utf-8")
        return self._llm_files[world]

    def write_tick(self, world: str, record: TickRecord) -> None:
        fh = self._tick_fh(world)
        fh.write(json.dumps(asdict(record), default=str) + "\n")
        fh.flush()

    def write_llm_call(self, world: str, record: LLMCallRecord) -> None:
        fh = self._llm_fh(world)
        fh.write(json.dumps(asdict(record), default=str) + "\n")
        fh.flush()

    def write_json(self, filename: str, obj: Any) -> None:
        path = os.path.join(self.output_dir, filename)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(obj, f, indent=2, default=str)

    def append_jsonl(self, filename: str, obj: Any) -> None:
        path = os.path.join(self.output_dir, filename)
        with open(path, "a", encoding="utf-8") as f:
            f.write(json.dumps(obj, default=str) + "\n")

    def close(self) -> None:
        for fh in self._tick_files.values():
            fh.close()
        for fh in self._llm_files.values():
            fh.close()
        self._tick_files.clear()
        self._llm_files.clear()
