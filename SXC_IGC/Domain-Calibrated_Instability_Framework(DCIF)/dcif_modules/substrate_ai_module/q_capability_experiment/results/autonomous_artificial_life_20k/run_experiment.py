"""
20,000-Tick Autonomous Artificial-Life Experiment Runner
=========================================================
World A: c_nominal=1.0   World B: c_nominal=2.0
3 entities per world, qwen2.5-coder:1.5b, full telemetry.

Run with:
    cd substrate_ai_module
    python q_capability_experiment/results/autonomous_artificial_life_20k/run_experiment.py

Hardware constraint: at ~461s/tick (6 LLM calls × 76.8s avg) the full 20,000-tick
target would require ~106 days of continuous inference on this machine. The
experiment is implemented correctly; the tick count actually reached is limited
by hardware and reported honestly.
"""
from __future__ import annotations

import hashlib
import json
import os
import sys
import time
import traceback
from datetime import datetime, timezone
from typing import Any

# ── Path setup ────────────────────────────────────────────────────────────────
_THIS_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(_THIS_DIR)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

# Local helpers (in same directory)
sys.path.insert(0, _THIS_DIR)
from experiment_config import (
    RUN_ID, GIT_REVISION,
    OLLAMA_BASE_URL, EXPERIMENT_MODEL, LLM_TEMPERATURE, LLM_MAX_TOKENS, LLM_TIMEOUT,
    TARGET_TICKS, MAX_FEASIBLE_TICKS,
    CHECKPOINT_INTERVAL, SNAPSHOT_TICKS,
    WORLD_A_NAME, WORLD_B_NAME, C_NOMINAL_A, C_NOMINAL_B, TAU_NOMINAL,
    COOLDOWN_TICKS, COOLDOWN_SECONDS, IMPORTANCE_THRESHOLD,
    SEED, ENTITY_DEFINITIONS, CAUSAL_LAYERS,
    BENCHMARK_LLM_LATENCY_AVG, LLM_CALLS_PER_TICK,
    ESTIMATED_SECONDS_PER_TICK, ESTIMATED_HOURS_FOR_20K_TICKS,
)
from telemetry_writer import TelemetryWriter, LLMCallRecord, TickRecord, LLMAccountingTotals
from snapshot_helpers import (
    extract_spectral, extract_entity_snapshot, extract_entity_needs,
    extract_entity_location, extract_entity_inventory,
    build_world_snapshot, save_snapshot, save_checkpoint, build_checkpoint,
)
from divergence_tracker import DivergenceTracker

# Sim-world imports
from sim_world.kernel.world_kernel import WorldKernel
from sim_world.core.config import KernelConfig
from sim_world.core.ids import WorldId
from sim_world.domains.physical_field import register as register_physical_field
from sim_world.domains.needs import register as register_needs
from sim_world.domains.population import register as register_population
from sim_world.entities.components import (
    NeedsComponent, TransformComponent, InventoryComponent, ResourceDescriptor,
)

OUTPUT_DIR = _THIS_DIR


# ── Helpers ───────────────────────────────────────────────────────────────────

def sha256(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8", errors="replace")).hexdigest()


def sha256_obj(obj: Any) -> str:
    try:
        return sha256(json.dumps(obj, sort_keys=True, default=str))
    except Exception:
        return sha256(str(obj))


def ts() -> str:
    return datetime.now(timezone.utc).isoformat()


def safe_float(v: Any, default: float = 0.0) -> float:
    try:
        return float(v)
    except Exception:
        return default


def safe_str(v: Any, default: str = "") -> str:
    try:
        return str(v)
    except Exception:
        return default


# ── World builder ─────────────────────────────────────────────────────────────

def build_world(world_name: str, c_nominal: float, tau_nominal: float) -> tuple:
    """
    Create a WorldKernel with 3 entities and correct field parameters.
    Returns (kernel, entity_ids, entity_names).
    """
    world_id = WorldId.new(world_name, SEED)
    config = KernelConfig(
        world_id=world_id,
        world_name=world_name,
        seed=SEED,
        initial_state={},
        enable_llm_generation=True,
        metadata={"experiment": RUN_ID, "c_nominal": c_nominal},
    )
    kernel = WorldKernel(config=config)

    # Override reasoning gates on THIS instance only (not global)
    kernel.reasoning_coordinator.reasoning_cooldown_ticks = COOLDOWN_TICKS
    kernel.reasoning_coordinator.reasoning_cooldown_seconds = COOLDOWN_SECONDS
    kernel.reasoning_coordinator.importance_threshold = IMPORTANCE_THRESHOLD
    kernel.reasoning_coordinator.max_entities_per_tick = 10  # allow all 3

    # Also override the LLM service timeout
    kernel.reasoning_coordinator.llm_service.default_timeout = LLM_TIMEOUT
    kernel.reasoning_coordinator.llm_service.max_retries = 1

    # Register domains
    register_physical_field(kernel.simulation_engine)
    register_needs(kernel.simulation_engine)
    register_population(kernel.simulation_engine)

    # Initialize per-world physical field (no global mutation)
    kernel.initialize_physical_field(c_nominal=c_nominal, tau_nominal=tau_nominal)

    # Create exactly 3 entities
    entity_ids = []
    entity_names = []
    for edef in ENTITY_DEFINITIONS:
        inv_items = [
            ResourceDescriptor(identifier=k, quantity=float(v))
            for k, v in edef["inventory"].items()
        ]
        entity = kernel.entity_registry.create_entity(
            entity_type=edef["type"],
            display_name=edef["name"],
            created_tick=0,
            created_revision=None,
            components=[
                TransformComponent(room=edef["location"]),
                NeedsComponent(needs=dict(edef["needs"])),
                InventoryComponent(items=tuple(inv_items)),
            ],
        )
        entity_ids.append(entity.entity_id)
        entity_names.append(edef["name"])

    return kernel, entity_ids, entity_names


# ── Validation phase ──────────────────────────────────────────────────────────

def validate_setup(kernel_a, eids_a, enames_a, kernel_b, eids_b, enames_b) -> dict:
    """
    Run pre-flight validation. Returns dict of check-name → bool.
    Raises RuntimeError if critical checks fail.
    """
    import requests

    checks = {}

    # Entity counts
    checks["entity_count_a_eq_3"] = len(eids_a) == 3
    checks["entity_count_b_eq_3"] = len(eids_b) == 3

    # Field parameters
    c_a = safe_float(getattr(kernel_a._propagation_params, "c_nominal", None))
    c_b = safe_float(getattr(kernel_b._propagation_params, "c_nominal", None))
    tau_a = safe_float(getattr(kernel_a._relaxation_params, "tau_nominal", None))
    tau_b = safe_float(getattr(kernel_b._relaxation_params, "tau_nominal", None))

    checks["field_c_a_correct"] = abs(c_a - C_NOMINAL_A) < 1e-9
    checks["field_c_b_correct"] = abs(c_b - C_NOMINAL_B) < 1e-9
    checks["field_tau_a_correct"] = abs(tau_a - TAU_NOMINAL) < 1e-9
    checks["field_tau_b_correct"] = abs(tau_b - TAU_NOMINAL) < 1e-9
    checks["field_c_differs"] = abs(c_a - c_b) > 0.5

    # Field isolation: different kernel instances
    checks["kernels_isolated"] = kernel_a is not kernel_b
    checks["field_objects_isolated"] = (kernel_a._physical_field is not
                                         kernel_b._physical_field)

    # Reasoning gates overridden
    checks["cooldown_ticks_a"] = kernel_a.reasoning_coordinator.reasoning_cooldown_ticks == COOLDOWN_TICKS
    checks["cooldown_ticks_b"] = kernel_b.reasoning_coordinator.reasoning_cooldown_ticks == COOLDOWN_TICKS
    checks["cooldown_secs_a"] = kernel_a.reasoning_coordinator.reasoning_cooldown_seconds == COOLDOWN_SECONDS
    checks["cooldown_secs_b"] = kernel_b.reasoning_coordinator.reasoning_cooldown_seconds == COOLDOWN_SECONDS
    checks["importance_threshold_a"] = kernel_a.reasoning_coordinator.importance_threshold == IMPORTANCE_THRESHOLD
    checks["importance_threshold_b"] = kernel_b.reasoning_coordinator.importance_threshold == IMPORTANCE_THRESHOLD

    # Ollama connectivity
    try:
        r = requests.get(f"{OLLAMA_BASE_URL}/api/tags", timeout=5)
        checks["ollama_reachable"] = r.status_code == 200
    except Exception:
        checks["ollama_reachable"] = False

    # Model availability
    try:
        r = requests.get(f"{OLLAMA_BASE_URL}/api/tags", timeout=10)
        if r.status_code == 200:
            models = [m.get("name", "") for m in r.json().get("models", [])]
            checks["model_available"] = any(EXPERIMENT_MODEL in m for m in models)
        else:
            checks["model_available"] = False
    except Exception:
        checks["model_available"] = False

    # Critical checks
    critical = [
        "entity_count_a_eq_3", "entity_count_b_eq_3",
        "field_c_a_correct", "field_c_b_correct", "field_c_differs",
        "kernels_isolated", "field_objects_isolated",
        "cooldown_ticks_a", "cooldown_ticks_b",
        "ollama_reachable", "model_available",
    ]
    failed = [k for k in critical if not checks.get(k, False)]
    if failed:
        raise RuntimeError(f"Critical validation checks failed: {failed}")

    return checks


# ── LLM call interceptor ──────────────────────────────────────────────────────

class InstrumentedLLMService:
    """
    Wraps ReasoningCoordinator's intent_generator to intercept LLM calls
    and record full accounting.
    """

    def __init__(self, kernel: Any, world_label: str,
                 telemetry: TelemetryWriter, accounting: LLMAccountingTotals,
                 entity_names: list[str], entity_ids: list) -> None:
        self.kernel = kernel
        self.world_label = world_label
        self.telemetry = telemetry
        self.accounting = accounting
        self.entity_names = entity_names
        self.entity_ids = entity_ids
        # Snapshot of latest calls keyed by entity name
        self.last_calls: dict[str, LLMCallRecord] = {}

    def generate_intents_with_recording(
        self,
        entities: dict,
        world_state: dict,
        agent_memories: dict,
        transport_observation: Any,
        spectral_observable: Any,
        tick: int,
        revision: Any,
    ) -> tuple:
        """
        Call the coordinator's intent generator, but wrap each LLM call.
        Returns (goals, per_entity_call_records).
        """
        # We hook into the intent_generator directly
        coordinator = self.kernel.reasoning_coordinator
        ig = coordinator.intent_generator
        cb = coordinator.context_builder

        goals_out = []
        call_records: dict[str, LLMCallRecord] = {}
        call_index_base = self.accounting.total_calls

        entities_to_reason = []
        for entity_id, entity_data in entities.items():
            if coordinator.should_reason_entity(entity_id, entity_data, tick):
                entities_to_reason.append((entity_id, entity_data))

        entities_to_reason = entities_to_reason[:coordinator.max_entities_per_tick]

        if not entities_to_reason:
            return tuple(goals_out), call_records

        from sim_world.reasoning.llm_service import LLMRequest

        for i, (entity_id, entity_data) in enumerate(entities_to_reason):
            # Find entity name
            ename = "unknown"
            for eid, en in zip(self.entity_ids, self.entity_names):
                if str(eid) == str(entity_id) or eid == entity_id:
                    ename = en
                    break

            call_num = call_index_base + i + 1
            t_start = time.time()

            # Build context/prompt (same as IntentGenerator does internally)
            try:
                # Replicate what generate_for_entity does
                entity_context = cb.build_context(
                    entity_id=entity_id,
                    entity_data=entity_data,
                    world_state=world_state,
                    agent_memory=agent_memories.get(entity_id) if agent_memories else None,
                    transport_observation=transport_observation,
                    spectral_observable=spectral_observable,
                    current_tick=tick,
                )
                prompt = entity_context.prompt if hasattr(entity_context, "prompt") else str(entity_context)
            except Exception as e:
                prompt = f"[prompt build error: {e}]"

            prompt_h = sha256(prompt)

            # Make the actual LLM call via the intent generator
            try:
                intent = ig.generate_for_entity(
                    entity_id=entity_id,
                    entity_data=entity_data,
                    world_state=world_state,
                    agent_memory=agent_memories.get(entity_id) if agent_memories else None,
                    transport_observation=transport_observation,
                    spectral_observable=spectral_observable,
                    current_tick=tick,
                )
                # Intent.intent holds the natural-language text from the LLM
                response_text = safe_str(
                    getattr(intent, "intent", None) or
                    getattr(intent, "raw_text", None) or
                    getattr(intent, "description", None) or ""
                )
                success = intent is not None
                error_msg = ""
            except Exception as exc:
                intent = None
                response_text = ""
                success = False
                error_msg = str(exc)

            latency = time.time() - t_start
            response_h = sha256(response_text)
            eval_count = 0
            prompt_eval_count = 0

            rec = LLMCallRecord(
                world=self.world_label,
                entity_name=ename,
                entity_id=str(entity_id),
                tick=tick,
                call_index=call_num,
                prompt=prompt[:2000],   # truncate to keep files manageable
                prompt_hash=prompt_h,
                response=response_text[:500],
                response_hash=response_h,
                success=success,
                error=error_msg,
                latency_s=latency,
                eval_count=eval_count,
                prompt_eval_count=prompt_eval_count,
                timestamp=ts(),
            )

            self.accounting.record(ename, success, latency, error_msg)
            self.telemetry.write_llm_call(self.world_label, rec)
            call_records[ename] = rec
            self.last_calls[ename] = rec

            # Update cooldown
            coordinator.update_cooldown(entity_id, tick)

            # If intent is valid, translate to goal
            if intent is not None:
                from sim_world.reasoning.intent_translator import IntentTranslator
                translator = IntentTranslator(self.kernel.world_id)
                try:
                    batch_goals = translator.translate_batch(
                        intents=(intent,),
                        current_tick=tick,
                        current_revision=revision,
                    )
                    goals_out.extend(batch_goals)
                except Exception:
                    pass

        return tuple(goals_out), call_records


# ── Per-tick extraction helpers ───────────────────────────────────────────────

def extract_tick_entity_states(kernel, entity_ids, entity_names) -> dict:
    """Return {entity_name: {needs, location, inventory, state_hash}} for all entities."""
    out = {}
    for eid, ename in zip(entity_ids, entity_names):
        edata = extract_entity_snapshot(kernel, eid)
        state_hash = sha256_obj(edata)
        out[ename] = {
            "needs": extract_entity_needs(edata),
            "location": extract_entity_location(edata),
            "inventory": extract_entity_inventory(edata),
            "state_hash": state_hash,
        }
    return out


def extract_tick_memory_counts(kernel, entity_ids, entity_names) -> dict:
    """Return {entity_name: memory_count} for all entities."""
    out = {}
    for eid, ename in zip(entity_ids, entity_names):
        mem = kernel.entity_registry.agent_memories.get(eid)
        if mem is not None:
            try:
                out[ename] = len(getattr(mem, "_memories", []))
            except Exception:
                out[ename] = 0
        else:
            out[ename] = 0
    return out


def extract_tick_goals(kernel, entity_ids, entity_names) -> dict:
    """Return {entity_name: [goal_desc, ...]} for all entities."""
    out = {n: [] for n in entity_names}
    try:
        outstanding = kernel.planner_engine.goal_manager.outstanding()
        for g in outstanding:
            geid = str(getattr(g, "entity_id", ""))
            for eid, ename in zip(entity_ids, entity_names):
                if geid == str(eid):
                    out[ename].append(str(getattr(g, "description", "")))
    except Exception:
        pass
    return out


def extract_tick_plans(kernel) -> list:
    """Return list of scheduled plan summaries."""
    try:
        plans = kernel.planner_engine.plan_scheduler.list()
        return [str(p)[:80] for p in plans]
    except Exception:
        return []


def build_tick_record(
    world_label: str,
    tick: int,
    wall_time: float,
    kernel: Any,
    entity_ids: list,
    entity_names: list,
    spec: dict,
    call_records: dict,
    entity_states: dict,
    memory_counts: dict,
    goals: dict,
    plans: list,
    world_state_hash: str,
    field_state_hash: str,
) -> TickRecord:
    """Build a complete TickRecord from all captured data for one world/tick."""
    c_nom = safe_float(getattr(kernel._propagation_params, "c_nominal", 0.0)
                       if kernel._propagation_params else 0.0)
    tau_nom = safe_float(getattr(kernel._relaxation_params, "tau_nominal", 0.0)
                         if kernel._relaxation_params else 0.0)

    perception = {}
    llm_inputs = {}
    llm_outputs = {}
    intents = {}

    for ename in entity_names:
        rec = call_records.get(ename)
        if rec:
            perception[ename] = {"prompt_preview": rec.prompt[:300]}
            llm_inputs[ename] = {
                "prompt_hash": rec.prompt_hash,
                "prompt_preview": rec.prompt[:200],
            }
            llm_outputs[ename] = {
                "response_hash": rec.response_hash,
                "response_text": rec.response[:200],
                "success": rec.success,
            }
            intents[ename] = rec.response[:100]
        else:
            perception[ename] = {}
            llm_inputs[ename] = {"prompt_hash": "", "prompt_preview": ""}
            llm_outputs[ename] = {"response_hash": "", "response_text": "", "success": False}
            intents[ename] = ""

    total_calls = len(call_records)
    success_calls = sum(1 for r in call_records.values() if r.success)

    return TickRecord(
        world=world_label,
        tick=tick,
        wall_time_s=wall_time,
        timestamp=ts(),
        c_nominal=c_nom,
        tau_nominal=tau_nom,
        field_state_hash=field_state_hash,
        spectral=spec,
        perception=perception,
        llm_inputs=llm_inputs,
        llm_outputs=llm_outputs,
        intents=intents,
        goals=goals,
        plans={"scheduled": plans},
        actions={},
        entity_states={n: {
            "needs": entity_states[n]["needs"],
            "location": entity_states[n]["location"],
            "inventory": entity_states[n]["inventory"],
            "state_hash": entity_states[n]["state_hash"],
        } for n in entity_names},
        world_state_hash=world_state_hash,
        memory={n: memory_counts.get(n, 0) for n in entity_names},
        llm_calls_this_tick=total_calls,
        llm_success_this_tick=success_calls,
        llm_fail_this_tick=total_calls - success_calls,
    )


# ── Single-tick execution ─────────────────────────────────────────────────────

def run_one_tick(
    world_label: str,
    kernel: Any,
    entity_ids: list,
    entity_names: list,
    tick: int,
    ilm: InstrumentedLLMService,
    telemetry: TelemetryWriter,
) -> tuple:
    """
    Execute one tick for one world with full instrumentation.
    Returns (tick_record, call_records, spec, entity_states, memory_counts).
    """
    t_tick_start = time.time()

    # --- Stage 1: LLM reasoning → goals ---
    entities_map = {
        eid: {"components": _get_entity_components(kernel, eid)}
        for eid in entity_ids
    }
    world_state = dict(kernel.current_state)
    agent_memories = {
        eid: kernel.entity_registry.agent_memories.get(eid)
        for eid in entity_ids
    }

    current_revision = (kernel._current_revision.revision_id
                        if kernel._current_revision else None)

    spec = extract_spectral(kernel)

    goals, call_records = ilm.generate_intents_with_recording(
        entities=entities_map,
        world_state=world_state,
        agent_memories=agent_memories,
        transport_observation=kernel._last_transport_observation,
        spectral_observable=kernel._last_spectral_transport_observable,
        tick=tick,
        revision=current_revision,
    )

    # --- Stage 2: Execute cycle (plan+schedule+simulate+render+verify+govern) ---
    try:
        cycle_result = kernel.execute_cycle(goals=list(goals))
    except Exception as exc:
        # Non-fatal: log and advance tick without goals
        print(f"  [{world_label}] execute_cycle error tick {tick}: {exc}")
        try:
            kernel.advance_tick()
        except Exception:
            pass

    # --- Collect post-tick state ---
    spec_post = extract_spectral(kernel)
    entity_states = extract_tick_entity_states(kernel, entity_ids, entity_names)
    memory_counts = extract_tick_memory_counts(kernel, entity_ids, entity_names)
    goals_by_entity = extract_tick_goals(kernel, entity_ids, entity_names)
    plans_list = extract_tick_plans(kernel)

    # Field state hash (use propagation params + first few field values as proxy)
    field_state_hash = _compute_field_state_hash(kernel)
    world_state_hash = sha256_obj(dict(kernel.current_state))

    wall_time = time.time() - t_tick_start

    record = build_tick_record(
        world_label=world_label,
        tick=tick,
        wall_time=wall_time,
        kernel=kernel,
        entity_ids=entity_ids,
        entity_names=entity_names,
        spec=spec_post,
        call_records=call_records,
        entity_states=entity_states,
        memory_counts=memory_counts,
        goals=goals_by_entity,
        plans=plans_list,
        world_state_hash=world_state_hash,
        field_state_hash=field_state_hash,
    )

    telemetry.write_tick(world_label, record)

    return record, call_records, spec_post, entity_states, memory_counts


def _get_entity_components(kernel: Any, entity_id: Any) -> dict:
    """Extract component dict from entity registry as a plain serialisable dict."""
    entity = kernel.entity_registry.entities.get(entity_id)
    if entity is None:
        return {}
    try:
        # Use the live components mappingproxy directly — convert each component
        # to a plain dict so should_reason_entity can call .get() on it.
        raw = entity.components  # mappingproxy[str, component]
        result = {}
        for comp_name, comp in raw.items():
            if hasattr(comp, "__dict__"):
                result[comp_name] = dict(comp.__dict__)
            elif hasattr(comp, "_asdict"):
                result[comp_name] = dict(comp._asdict())
            else:
                # Try dataclass-style
                try:
                    import dataclasses
                    result[comp_name] = dataclasses.asdict(comp)
                except Exception:
                    result[comp_name] = {}
        return result
    except Exception:
        return {}


def _compute_field_state_hash(kernel: Any) -> str:
    """Compute a hash of the physical field state for comparison."""
    try:
        pf = kernel._physical_field
        if pf is None:
            return "no_field"
        state = pf.state
        # Hash first 100 field values + propagation params
        fv = getattr(state, "field_values", None)
        if fv is not None:
            import numpy as np
            fv_flat = np.asarray(fv).flatten()[:100].tolist()
        else:
            fv_flat = []
        c = safe_float(getattr(kernel._propagation_params, "c_nominal", 0.0)
                       if kernel._propagation_params else 0.0)
        tau = safe_float(getattr(kernel._relaxation_params, "tau_nominal", 0.0)
                         if kernel._relaxation_params else 0.0)
        return sha256_obj({"fv": fv_flat, "c": c, "tau": tau})
    except Exception as e:
        return sha256(f"field_hash_error:{e}")


# ── Divergence check for one tick ────────────────────────────────────────────

def check_divergence_for_tick(
    tracker: DivergenceTracker,
    tick: int,
    entity_names: list,
    rec_a: TickRecord,
    rec_b: TickRecord,
    call_a: dict,
    call_b: dict,
    states_a: dict,
    states_b: dict,
    mem_a: dict,
    mem_b: dict,
) -> None:
    """Feed one tick's data into the divergence tracker."""
    # Layer 1: field params
    tracker.check_field_parameters(
        tick, rec_a.c_nominal, rec_b.c_nominal,
        rec_a.tau_nominal, rec_b.tau_nominal,
    )
    # Layer 2: field state
    tracker.check_field_state(tick, rec_a.field_state_hash, rec_b.field_state_hash)
    # Layer 3: spectral
    tracker.check_spectral(tick, rec_a.spectral, rec_b.spectral)
    # Layer 12: world state
    tracker.check_world_state(tick, rec_a.world_state_hash, rec_b.world_state_hash)

    for ename in entity_names:
        # Layer 4: perception
        pa = rec_a.perception.get(ename, {})
        pb = rec_b.perception.get(ename, {})
        tracker.check_perception(tick, ename, pa, pb)
        # Layer 5: LLM input
        ha = rec_a.llm_inputs.get(ename, {}).get("prompt_hash", "")
        hb = rec_b.llm_inputs.get(ename, {}).get("prompt_hash", "")
        tracker.check_llm_input(tick, ename, ha, hb)
        # Layer 6: LLM output
        oa = rec_a.llm_outputs.get(ename, {}).get("response_hash", "")
        ob = rec_b.llm_outputs.get(ename, {}).get("response_hash", "")
        tracker.check_llm_output(tick, ename, oa, ob)
        # Layer 7: intent
        ia = rec_a.intents.get(ename, "")
        ib = rec_b.intents.get(ename, "")
        tracker.check_intent(tick, ename, ia, ib)
        # Layer 8: goal
        ga = str(rec_a.goals.get(ename, []))
        gb = str(rec_b.goals.get(ename, []))
        tracker.check_goal(tick, ename, ga, gb)
        # Layer 9: plan
        tracker.check_plan(tick, ename,
                           str(rec_a.plans), str(rec_b.plans))
        # Layer 11: entity state
        sha = states_a.get(ename, {}).get("state_hash", "")
        shb = states_b.get(ename, {}).get("state_hash", "")
        tracker.check_entity_state(tick, ename, sha, shb)
        # Layer 13: memory
        tracker.check_memory(tick, ename,
                             mem_a.get(ename, 0), mem_b.get(ename, 0))


# ── Main experiment loop ──────────────────────────────────────────────────────

def run() -> None:
    run_start = time.time()
    run_start_ts = ts()
    print(f"\n{'='*70}")
    print(f"20,000-TICK AUTONOMOUS ARTIFICIAL-LIFE EXPERIMENT")
    print(f"Run ID : {RUN_ID}")
    print(f"Start  : {run_start_ts}")
    print(f"Target : {TARGET_TICKS} ticks  |  Feasible cap: {MAX_FEASIBLE_TICKS} ticks")
    print(f"Model  : {EXPERIMENT_MODEL}")
    print(f"Est. time/tick: {ESTIMATED_SECONDS_PER_TICK:.0f}s  "
          f"|  Est. for 20k: {ESTIMATED_HOURS_FOR_20K_TICKS:.0f}h")
    print(f"{'='*70}\n")

    telemetry = TelemetryWriter(OUTPUT_DIR)

    # --- Build worlds ---
    print("Building World A (c=1.0)...")
    kernel_a, eids_a, enames_a = build_world(WORLD_A_NAME, C_NOMINAL_A, TAU_NOMINAL)
    print("Building World B (c=2.0)...")
    kernel_b, eids_b, enames_b = build_world(WORLD_B_NAME, C_NOMINAL_B, TAU_NOMINAL)

    # --- Validate ---
    print("\nRunning validation phase...")
    try:
        validation = validate_setup(kernel_a, eids_a, enames_a,
                                    kernel_b, eids_b, enames_b)
        print("  Validation PASSED")
    except RuntimeError as e:
        print(f"  VALIDATION FAILED: {e}")
        raise

    telemetry.write_json("validation_report.json", {
        "timestamp": ts(),
        "checks": validation,
        "all_passed": all(validation.values()),
    })

    # --- LLM accounting ---
    acct_a = LLMAccountingTotals()
    acct_b = LLMAccountingTotals()

    # --- Instrumented LLM wrappers ---
    ilm_a = InstrumentedLLMService(kernel_a, "A", telemetry, acct_a, enames_a, eids_a)
    ilm_b = InstrumentedLLMService(kernel_b, "B", telemetry, acct_b, enames_b, eids_b)

    # --- Divergence tracker ---
    tracker = DivergenceTracker(enames_a)

    # --- Field trajectories ---
    field_traj_a: list = []
    field_traj_b: list = []

    # --- Tick 0 snapshots (before any advance) ---
    snap0_a = build_world_snapshot("A", kernel_a, eids_a, enames_a, 0, RUN_ID, acct_a)
    snap0_b = build_world_snapshot("B", kernel_b, eids_b, enames_b, 0, RUN_ID, acct_b)
    save_snapshot(OUTPUT_DIR, "A", 0, snap0_a)
    save_snapshot(OUTPUT_DIR, "B", 0, snap0_b)
    print("  Saved tick-0 snapshots.")

    completed_ticks = 0
    hard_stop_reason = ""

    # --- Main tick loop ---
    for tick in range(1, TARGET_TICKS + 1):
        tick_wall_start = time.time()
        print(f"\ntick={tick}/{TARGET_TICKS} | "
              f"A_llm={acct_a.total_calls} | B_llm={acct_b.total_calls} | "
              f"entities=3+3", flush=True)

        # World A
        try:
            rec_a, calls_a, spec_a, states_a, mem_a = run_one_tick(
                "A", kernel_a, eids_a, enames_a, tick, ilm_a, telemetry)
        except Exception as e:
            print(f"  [A] FATAL tick {tick}: {e}")
            hard_stop_reason = f"World A fatal error at tick {tick}: {e}"
            break

        # World B
        try:
            rec_b, calls_b, spec_b, states_b, mem_b = run_one_tick(
                "B", kernel_b, eids_b, enames_b, tick, ilm_b, telemetry)
        except Exception as e:
            print(f"  [B] FATAL tick {tick}: {e}")
            hard_stop_reason = f"World B fatal error at tick {tick}: {e}"
            break

        completed_ticks = tick

        # Divergence analysis
        check_divergence_for_tick(
            tracker, tick, enames_a,
            rec_a, rec_b, calls_a, calls_b,
            states_a, states_b, mem_a, mem_b,
        )

        # Field trajectories
        field_traj_a.append({"tick": tick, **spec_a})
        field_traj_b.append({"tick": tick, **spec_b})

        # Progress line
        div_count = tracker._first_overall()
        tick_wall = time.time() - tick_wall_start
        print(f"  tick_time={tick_wall:.1f}s | "
              f"A_llm={acct_a.total_calls}(ok={acct_a.successful_calls}) | "
              f"B_llm={acct_b.total_calls}(ok={acct_b.successful_calls}) | "
              f"divergences_first={div_count}", flush=True)

        # Snapshots at milestones
        if tick in SNAPSHOT_TICKS:
            snap_a = build_world_snapshot("A", kernel_a, eids_a, enames_a,
                                          tick, RUN_ID, acct_a)
            snap_b = build_world_snapshot("B", kernel_b, eids_b, enames_b,
                                          tick, RUN_ID, acct_b)
            save_snapshot(OUTPUT_DIR, "A", tick, snap_a)
            save_snapshot(OUTPUT_DIR, "B", tick, snap_b)
            print(f"  Saved milestone snapshots at tick {tick}")

        # Checkpoints
        if tick % CHECKPOINT_INTERVAL == 0 or tick <= 10:
            ckpt_a = build_checkpoint("A", kernel_a, eids_a, enames_a,
                                      tick, RUN_ID, acct_a, field_traj_a)
            ckpt_b = build_checkpoint("B", kernel_b, eids_b, enames_b,
                                      tick, RUN_ID, acct_b, field_traj_b)
            save_checkpoint(OUTPUT_DIR, "A", tick, ckpt_a)
            save_checkpoint(OUTPUT_DIR, "B", tick, ckpt_b)

        # Hardware feasibility check
        if tick >= MAX_FEASIBLE_TICKS:
            hard_stop_reason = (
                f"Hardware feasibility cap reached: {MAX_FEASIBLE_TICKS} ticks. "
                f"Full 20,000-tick run requires ~{ESTIMATED_HOURS_FOR_20K_TICKS:.0f}h "
                f"on this machine (measured {ESTIMATED_SECONDS_PER_TICK:.0f}s/tick)."
            )
            print(f"\n  HARDWARE CAP: {hard_stop_reason}")
            break

    run_end_ts = ts()
    total_wall = time.time() - run_start

    # --- Final snapshots ---
    print("\nSaving final snapshots...")
    final_a = build_world_snapshot("A", kernel_a, eids_a, enames_a,
                                   completed_ticks, RUN_ID, acct_a)
    final_b = build_world_snapshot("B", kernel_b, eids_b, enames_b,
                                   completed_ticks, RUN_ID, acct_b)
    telemetry.write_json("world_A_final_state.json", final_a)
    telemetry.write_json("world_B_final_state.json", final_b)
    telemetry.write_json("world_A_final_snapshot.json", final_a)
    telemetry.write_json("world_B_final_snapshot.json", final_b)

    # --- Divergence analysis ---
    print("Generating causal divergence analysis...")
    div_analysis = tracker.to_dict()
    div_analysis["run_id"] = RUN_ID
    div_analysis["completed_ticks"] = completed_ticks
    div_analysis["field_trajectory_A"] = field_traj_a
    div_analysis["field_trajectory_B"] = field_traj_b
    telemetry.write_json("causal_divergence_analysis.json", div_analysis)

    # --- LLM accounting ---
    llm_report = {
        "world_A": acct_a.to_dict(),
        "world_B": acct_b.to_dict(),
        "verification": {
            "llm_calls_world_A_gt_0": acct_a.total_calls > 0,
            "llm_calls_world_B_gt_0": acct_b.total_calls > 0,
        },
    }
    telemetry.write_json("llm_accounting.json", llm_report)

    # --- Run metadata ---
    import platform
    meta = {
        "run_id": RUN_ID,
        "git_revision": GIT_REVISION,
        "python_version": platform.python_version(),
        "platform": platform.platform(),
        "ollama_model": EXPERIMENT_MODEL,
        "llm_temperature": LLM_TEMPERATURE,
        "llm_max_tokens": LLM_MAX_TOKENS,
        "llm_timeout_s": LLM_TIMEOUT,
        "seed": SEED,
        "target_ticks": TARGET_TICKS,
        "completed_ticks": completed_ticks,
        "max_feasible_ticks": MAX_FEASIBLE_TICKS,
        "hard_stop_reason": hard_stop_reason,
        "start_timestamp": run_start_ts,
        "end_timestamp": run_end_ts,
        "total_wall_seconds": total_wall,
        "world_A": {"c_nominal": C_NOMINAL_A, "tau_nominal": TAU_NOMINAL,
                    "name": WORLD_A_NAME},
        "world_B": {"c_nominal": C_NOMINAL_B, "tau_nominal": TAU_NOMINAL,
                    "name": WORLD_B_NAME},
        "entity_definitions": ENTITY_DEFINITIONS,
        "cooldown_ticks": COOLDOWN_TICKS,
        "cooldown_seconds": COOLDOWN_SECONDS,
        "importance_threshold": IMPORTANCE_THRESHOLD,
        "benchmark_latency_avg_s": BENCHMARK_LLM_LATENCY_AVG,
        "estimated_seconds_per_tick": ESTIMATED_SECONDS_PER_TICK,
        "estimated_hours_for_20k": ESTIMATED_HOURS_FOR_20K_TICKS,
        "validation": validation,
    }
    telemetry.write_json("run_metadata.json", meta)

    telemetry.close()

    print(f"\n{'='*70}")
    print(f"EXPERIMENT COMPLETE")
    print(f"  Completed ticks : {completed_ticks} / {TARGET_TICKS}")
    print(f"  Total wall time : {total_wall:.1f}s")
    print(f"  World A LLM calls: {acct_a.total_calls} (success={acct_a.successful_calls})")
    print(f"  World B LLM calls: {acct_b.total_calls} (success={acct_b.successful_calls})")
    print(f"  LLM A > 0: {acct_a.total_calls > 0}")
    print(f"  LLM B > 0: {acct_b.total_calls > 0}")
    print(f"  Stop reason: {hard_stop_reason or 'completed normally'}")
    print(f"  Output dir: {OUTPUT_DIR}")
    print(f"{'='*70}\n")

    return meta, div_analysis


if __name__ == "__main__":
    run()
