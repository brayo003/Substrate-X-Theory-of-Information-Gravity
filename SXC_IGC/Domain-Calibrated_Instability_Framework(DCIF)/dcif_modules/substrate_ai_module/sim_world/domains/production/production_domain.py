from __future__ import annotations

from typing import Any, Mapping, Sequence

from ...core.contracts import TransitionProposal
from ...simulation.simulation_engine import SimulationEngine
from .production_events import (
    GoodsDeposited,
    InputsReserved,
    ProductionCancelled,
    ProductionCompleted,
    ProductionProgressed,
    ProductionStarted,
    RecipeExecuted,
    ToolBroken,
    ToolUsed,
)
from .production_models import (
    FACILITY_TYPES,
    JOB_STATUSES,
    OCCUPATIONS,
    PRODUCTION_TOOLS,
    ProductionFacility,
    ProductionJob,
    ProductionRecipe,
    ProductionState,
    ToolState,
    build_default_facilities,
    build_default_recipes,
    make_facility_id,
    make_job_id,
)
from .production_rules import (
    advance_production,
    apply_tool_use_effects,
    cancel_production,
    check_facility_for_recipe,
    check_inputs_available,
    check_tools_available,
    check_worker_can_cook,
    complete_production,
    compute_state_summary,
    create_production_job,
    lookup_jobs_by_facility,
    lookup_jobs_by_status,
    lookup_jobs_by_worker,
    lookup_recipes_for_output,
    reserve_inputs,
    summarize_production_delta,
)


def register(engine: SimulationEngine) -> None:
    engine.register_domain("production", lambda engine, context: apply(context))


def _extract_context(ctx: Any) -> tuple[dict[str, Any], Any, int]:
    state = dict(getattr(ctx, "current_state", None) or getattr(ctx, "world_state", {}))
    world_id = getattr(ctx, "world_id", None)
    tick_number = int(getattr(ctx, "current_tick_number", None) or getattr(ctx, "tick_number", 0))
    return state, world_id, tick_number


def _id_str(entity_or_id: Any) -> str:
    if hasattr(entity_or_id, "value"):
        return str(entity_or_id.value)
    return str(entity_or_id)


def _to_proposal(
    world_id: Any,
    tick_context: Any,
    revision: Any,
    correlation_id: str,
    subject: str,
    patch: Mapping[str, Any],
    description: str,
    metadata: Mapping[str, Any],
) -> TransitionProposal:
    return TransitionProposal(
        world_id=world_id,
        tick_id=getattr(tick_context, "tick_id", None) if tick_context is not None else None,
        state_revision=revision,
        correlation_id=correlation_id,
        subject=subject,
        patch=dict(patch),
        description=str(description),
        metadata=dict(metadata),
    )


def _empty_patch(world_id: Any, tick_context: Any, revision: Any, correlation_id: str, subject: str, reason: str, metadata_extra: Mapping[str, Any] | None = None) -> TransitionProposal:
    md: dict[str, Any] = {"domain": "production", "events": [], "reason": reason}
    if metadata_extra:
        md.update(dict(metadata_extra))
    return _to_proposal(world_id, tick_context, revision, correlation_id, subject, {}, subject, md)


def initialize_valley_production(kernel: Any) -> dict[str, Any]:
    recipes = build_default_recipes()
    facilities = build_default_facilities()
    tools: dict[str, ToolState] = {}
    jobs: dict[str, ProductionJob] = {}
    state = compute_state_summary({})
    if hasattr(kernel, "_state") and isinstance(kernel._state, dict):
        if "production_facilities" not in kernel._state:
            kernel._state["production_facilities"] = {k: f.to_dict() for k, f in facilities.items()}
        if "production_recipes" not in kernel._state:
            kernel._state["production_recipes"] = {k: r.to_dict() for k, r in recipes.items()}
        if "production_tools" not in kernel._state:
            kernel._state["production_tools"] = {}
        if "production_jobs" not in kernel._state:
            kernel._state["production_jobs"] = {}
        if "production_state" not in kernel._state:
            kernel._state["production_state"] = state.to_dict()
    return {
        "recipes": recipes,
        "facilities": facilities,
        "tools": tools,
        "jobs": jobs,
        "state": state,
    }


def _load_production_section(state: Mapping[str, Any], key: str) -> dict[str, Any]:
    raw = state.get(key, {})
    if raw is None:
        return {}
    if isinstance(raw, Mapping):
        return dict(raw)
    return {}


def _load_recipes(state: Mapping[str, Any]) -> dict[str, ProductionRecipe]:
    d = _load_production_section(state, "production_recipes")
    if not d:
        return build_default_recipes()
    result: dict[str, ProductionRecipe] = {}
    for rid, rdata in d.items():
        if isinstance(rdata, Mapping) and "recipe_id" in rdata:
            result[str(rid)] = ProductionRecipe.from_dict(rdata)
    return result or build_default_recipes()


def _load_facilities(state: Mapping[str, Any]) -> dict[str, ProductionFacility]:
    d = _load_production_section(state, "production_facilities")
    result: dict[str, ProductionFacility] = {}
    for fid, fdata in d.items():
        if isinstance(fdata, Mapping) and "facility_id" in fdata:
            result[str(fid)] = ProductionFacility.from_dict(fdata)
    return result or build_default_facilities()


def _load_jobs(state: Mapping[str, Any]) -> dict[str, ProductionJob]:
    d = _load_production_section(state, "production_jobs")
    result: dict[str, ProductionJob] = {}
    for jid, jdata in d.items():
        if isinstance(jdata, Mapping) and "job_id" in jdata:
            result[str(jid)] = ProductionJob.from_dict(jdata)
    return result


def _load_tools(state: Mapping[str, Any]) -> dict[str, ToolState]:
    d = _load_production_section(state, "production_tools")
    result: dict[str, ToolState] = {}
    for tid, tdata in d.items():
        if isinstance(tdata, Mapping) and "tool_id" in tdata:
            result[str(tid)] = ToolState.from_dict(tdata)
    return result


def apply(context: Any) -> tuple[TransitionProposal, ...]:
    world_state = dict(context.world_state)
    tick = int(getattr(context, "tick_number", 0))
    tick_context = getattr(context, "tick_context", None)
    world_id = getattr(context, "world_id", None)
    revision = getattr(context, "committed_revision", None)

    recipes = _load_recipes(world_state)
    facilities = _load_facilities(world_state)
    jobs = _load_jobs(world_state)
    tools = _load_tools(world_state)
    events: list[dict[str, Any]] = []
    tool_events_list: list[Any] = []

    updated_jobs: dict[str, ProductionJob] = {}
    modified = False

    for jid in sorted(jobs.keys()):
        job = jobs[jid]
        if job.status in ("Active", "Progressing", "Reserved"):
            recipe = recipes.get(job.recipe_id)
            new_job, prog_events, finished = advance_production(job, tick, recipe)
            for ev in prog_events:
                events.append(ev.to_dict())
                if isinstance(ev, ToolUsed):
                    tool_events_list.append(ev)
            if new_job.status != job.status or new_job.progress != job.progress:
                modified = True
            updated_jobs[jid] = new_job
        else:
            updated_jobs[jid] = job

    if tool_events_list:
        tool_list = list(tools.values())
        updated_tools_list, extra_break_events = apply_tool_use_effects(tool_list, tool_events_list)
        for bev in extra_break_events:
            events.append(bev.to_dict())
        tools = {t.tool_id: t for t in updated_tools_list}
        modified = True

    summary = compute_state_summary(updated_jobs)

    if not modified and (not events):
        return ()

    patch: dict[str, Any] = {
        "production_jobs": {jid: j.to_dict() for jid, j in updated_jobs.items()},
        "production_state": summary.to_dict(),
        "production_tools": {tid: t.to_dict() for tid, t in tools.items()},
    }
    metadata: dict[str, Any] = {"domain": "production", "events": events}
    correlation_id = getattr(tick_context, "correlation_id", f"production:advance:{tick}") if tick_context is not None else f"production:advance:{tick}"
    return (
        _to_proposal(
            world_id, tick_context, revision,
            correlation_id,
            "domain.production",
            patch,
            f"advance production at tick {tick}",
            metadata,
        ),
    )


def _read_inv_for(state: Mapping[str, Any], entity_id: str) -> tuple[list[dict[str, Any]], float]:
    entities = dict(state.get("entities", {}))
    ent = dict(entities.get(str(entity_id), {}))
    components = dict(ent.get("components", {}))
    inv = dict(components.get("InventoryComponent", {}))
    items = [dict(r) for r in inv.get("items", ())]
    capacity = float(inv.get("capacity", 500.0))
    return items, capacity


def _write_inv_patch(
    entity_patches: dict[str, Any],
    entity_id: str,
    items: Sequence[Mapping[str, Any]],
    capacity: float,
) -> None:
    entity_patches[str(entity_id)] = {
        "components": {
            "InventoryComponent": {
                "items": tuple(dict(r) for r in items),
                "capacity": float(capacity),
                "component_type": "InventoryComponent",
            }
        }
    }


def reserve_inputs_action(
    ctx: Any,
    recipe_id: str,
    source_entity_id: Any,
) -> TransitionProposal:
    world_state, world_id, tick = _extract_context(ctx)
    tick_context = getattr(ctx, "tick_context", None)
    revision = getattr(ctx, "committed_revision", None) or None
    recipes = _load_recipes(world_state)
    recipe = recipes.get(str(recipe_id))
    src_key = _id_str(source_entity_id)
    if recipe is None:
        return _empty_patch(world_id, tick_context, revision, f"prod:reserve:missing:{recipe_id}", "Production:ReserveInputs:MissingRecipe", f"recipe {recipe_id} not found", {"recipe_id": recipe_id})
    inv, cap = _read_inv_for(world_state, src_key)
    try:
        new_inv, consumed, events = reserve_inputs(recipe, inv, src_key, f"pending:{src_key}:{recipe.recipe_id}:{tick}", tick)
    except ValueError as exc:
        return _empty_patch(world_id, tick_context, revision, f"prod:reserve:short:{recipe_id}", "Production:ReserveInputs:Shortage", str(exc), {"recipe_id": recipe_id, "source": src_key})
    entity_patches: dict[str, Any] = {}
    _write_inv_patch(entity_patches, src_key, new_inv, cap)
    # DOMAIN-LOCKED PROPERTY OWNERSHIP: Production domain only mutates ProductionComponent
    # Never mutate entire entities dict - only owned component patches
    patch = {"entity_production_components": entity_patches}
    metadata = {
        "domain": "production",
        "recipe_id": recipe.recipe_id,
        "source_id": src_key,
        "consumed": consumed,
        "events": [e.to_dict() for e in events],
    }
    return _to_proposal(
        world_id, tick_context, revision,
        f"prod:reserve:{recipe.recipe_id}:{src_key}",
        f"Production:ReserveInputs:{recipe.facility}",
        patch,
        f"reserve inputs for {recipe.name} from {src_key}",
        metadata,
    )


def begin_production_action(
    ctx: Any,
    recipe_id: str,
    facility_id: str,
    worker_id: Any,
    source_entity_id: Any,
    storage_entity_id: Any | None = None,
    occupation_map: Mapping[str, str] | None = None,
    available_tools: Sequence[str] | None = None,
) -> TransitionProposal:
    world_state, world_id, tick = _extract_context(ctx)
    tick_context = getattr(ctx, "tick_context", None)
    revision = getattr(ctx, "committed_revision", None) or None
    recipes = _load_recipes(world_state)
    facilities = _load_facilities(world_state)
    jobs = _load_jobs(world_state)
    tools = _load_tools(world_state)
    rid = str(recipe_id)
    fid = str(facility_id)
    wid = _id_str(worker_id)
    src_key = _id_str(source_entity_id)
    storage_key = _id_str(storage_entity_id) if storage_entity_id is not None else src_key
    recipe = recipes.get(rid)
    facility = facilities.get(fid)
    if recipe is None:
        return _empty_patch(world_id, tick_context, revision, f"prod:begin:missing:recipe:{rid}", "Production:Begin:MissingRecipe", f"recipe {rid} not found", {"recipe_id": rid})
    if facility is None:
        return _empty_patch(world_id, tick_context, revision, f"prod:begin:missing:facility:{fid}", "Production:Begin:MissingFacility", f"facility {fid} not found", {"facility_id": fid})
    if not check_facility_for_recipe(recipe, facility):
        return _empty_patch(world_id, tick_context, revision, f"prod:begin:recipe:mismatch:{rid}", "Production:Begin:FacilityMismatch", f"recipe {rid} incompatible with facility {fid}", {"recipe_id": rid, "facility_id": fid})
    if not check_worker_can_cook(recipe, wid, occupation_map):
        return _empty_patch(world_id, tick_context, revision, f"prod:begin:worker:mismatch:{wid}", "Production:Begin:WorkerMismatch", f"worker {wid} cannot operate {recipe.facility}", {"worker_id": wid, "recipe_id": rid})
    provided_tools = list(available_tools) if available_tools is not None else [t.tool_type for t in tools.values()]
    tools_ok, missing = check_tools_available(recipe, provided_tools)
    if not tools_ok:
        return _empty_patch(world_id, tick_context, revision, f"prod:begin:tools:short:{rid}", "Production:Begin:ToolsMissing", f"missing tools {list(missing)}", {"recipe_id": rid, "missing_tools": list(missing)})
    inv, cap = _read_inv_for(world_state, src_key)
    try:
        new_inv, consumed, reserve_events = reserve_inputs(recipe, inv, src_key, f"pending:{src_key}:{rid}:{tick}", tick)
    except ValueError as exc:
        return _empty_patch(world_id, tick_context, revision, f"prod:begin:inputs:short:{rid}", "Production:Begin:InputsShort", str(exc), {"recipe_id": rid, "source": src_key})
    job, updated_facility, begin_events = create_production_job(recipe, facility, wid, consumed, provided_tools, tick)
    jobs[job.job_id] = job
    facilities[fid] = updated_facility

    entity_patches: dict[str, Any] = {}
    _write_inv_patch(entity_patches, src_key, new_inv, cap)

    patch: dict[str, Any] = {
        "entities": entity_patches,
        "production_jobs": {jid: j.to_dict() for jid, j in jobs.items()},
        "production_facilities": {k: f.to_dict() for k, f in facilities.items()},
        "production_state": compute_state_summary(jobs).to_dict(),
    }
    all_events = [e.to_dict() for e in reserve_events + begin_events]
    metadata = {
        "domain": "production",
        "job_id": job.job_id,
        "recipe_id": rid,
        "facility_id": fid,
        "worker_id": wid,
        "storage_id": storage_key,
        "consumed": consumed,
        "events": all_events,
    }
    return _to_proposal(
        world_id, tick_context, revision,
        f"prod:begin:{job.job_id}",
        f"Production:BeginProduction:{recipe.facility}",
        patch,
        f"begin {recipe.name} at {fid} by {wid}",
        metadata,
    )


def advance_production_action(
    ctx: Any,
    job_id: str,
) -> TransitionProposal:
    world_state, world_id, tick = _extract_context(ctx)
    tick_context = getattr(ctx, "tick_context", None)
    revision = getattr(ctx, "committed_revision", None) or None
    recipes = _load_recipes(world_state)
    jobs = _load_jobs(world_state)
    tools = _load_tools(world_state)
    jid = str(job_id)
    if jid not in jobs:
        return _empty_patch(world_id, tick_context, revision, f"prod:advance:missing:{jid}", "Production:Advance:MissingJob", f"job {jid} not found", {"job_id": jid})
    job = jobs[jid]
    recipe = recipes.get(job.recipe_id)
    new_job, prog_events, finished = advance_production(job, tick, recipe)
    tool_events = [e for e in prog_events if isinstance(e, ToolUsed)]
    updated_tools_list, break_events = apply_tool_use_effects(list(tools.values()), tool_events)
    tools = {t.tool_id: t for t in updated_tools_list}
    all_events = prog_events + break_events
    jobs[jid] = new_job
    patch: dict[str, Any] = {
        "production_jobs": {k: j.to_dict() for k, j in jobs.items()},
        "production_tools": {tid: t.to_dict() for tid, t in tools.items()},
        "production_state": compute_state_summary(jobs).to_dict(),
    }
    metadata = {
        "domain": "production",
        "job_id": jid,
        "finished": finished,
        "progress": new_job.progress,
        "status": new_job.status,
        "events": [e.to_dict() for e in all_events],
    }
    return _to_proposal(
        world_id, tick_context, revision,
        f"prod:advance:{jid}",
        f"Production:AdvanceProduction:{new_job.status}",
        patch,
        f"advance production job {jid} ({new_job.status})",
        metadata,
    )


def complete_production_action(
    ctx: Any,
    job_id: str,
    destination_entity_id: Any,
) -> TransitionProposal:
    world_state, world_id, tick = _extract_context(ctx)
    tick_context = getattr(ctx, "tick_context", None)
    revision = getattr(ctx, "committed_revision", None) or None
    recipes = _load_recipes(world_state)
    facilities = _load_facilities(world_state)
    jobs = _load_jobs(world_state)
    jid = str(job_id)
    dest_key = _id_str(destination_entity_id)
    if jid not in jobs:
        return _empty_patch(world_id, tick_context, revision, f"prod:complete:missing:{jid}", "Production:Complete:MissingJob", f"job {jid} not found", {"job_id": jid})
    job = jobs[jid]
    recipe = recipes.get(job.recipe_id)
    if recipe is None:
        return _empty_patch(world_id, tick_context, revision, f"prod:complete:missing:recipe:{job.recipe_id}", "Production:Complete:MissingRecipe", f"recipe {job.recipe_id} not found", {"recipe_id": job.recipe_id})
    if not job.is_completed and job.progress < 1.0:
        return _empty_patch(world_id, tick_context, revision, f"prod:complete:not-ready:{jid}", "Production:Complete:NotReady", f"job {jid} progress {job.progress:.2f} < 1", {"job_id": jid, "progress": job.progress})
    inv, cap = _read_inv_for(world_state, dest_key)
    try:
        completed_job, new_inv, produced, complete_events, _ = complete_production(job, recipe, inv, dest_key, tick, cap)
    except ValueError as exc:
        return _empty_patch(world_id, tick_context, revision, f"prod:complete:fail:{jid}", "Production:Complete:Failed", str(exc), {"job_id": jid})
    jobs[jid] = completed_job
    facility = facilities.get(job.facility_id)
    if facility is not None:
        new_jobs = tuple(j for j in facility.active_jobs if j != jid)
        new_workers = tuple(w for w in facility.workers if w != completed_job.worker_id)
        facilities[job.facility_id] = ProductionFacility(
            facility_id=facility.facility_id,
            facility_type=facility.facility_type,
            location=facility.location,
            workers=new_workers,
            supported_recipes=facility.supported_recipes,
            active_jobs=new_jobs,
            capacity=facility.capacity,
        )
    entity_patches: dict[str, Any] = {}
    _write_inv_patch(entity_patches, dest_key, new_inv, cap)
    patch: dict[str, Any] = {
        "entities": entity_patches,
        "production_jobs": {k: j.to_dict() for k, j in jobs.items()},
        "production_facilities": {k: f.to_dict() for k, f in facilities.items()},
        "production_state": compute_state_summary(jobs).to_dict(),
    }
    metadata = {
        "domain": "production",
        "job_id": jid,
        "recipe_id": recipe.recipe_id,
        "destination_id": dest_key,
        "produced": produced,
        "status": completed_job.status,
        "events": [e.to_dict() for e in complete_events],
    }
    return _to_proposal(
        world_id, tick_context, revision,
        f"prod:complete:{jid}",
        "Production:CompleteProduction",
        patch,
        f"complete production job {jid} into {dest_key}",
        metadata,
    )


def deposit_products_action(
    ctx: Any,
    job_id: str,
    source_entity_id: Any,
    destination_entity_id: Any,
) -> TransitionProposal:
    world_state, world_id, tick = _extract_context(ctx)
    tick_context = getattr(ctx, "tick_context", None)
    revision = getattr(ctx, "committed_revision", None) or None
    jobs = _load_jobs(world_state)
    jid = str(job_id)
    src_key = _id_str(source_entity_id)
    dst_key = _id_str(destination_entity_id)
    if jid not in jobs:
        return _empty_patch(world_id, tick_context, revision, f"prod:deposit:missing:{jid}", "Production:Deposit:MissingJob", f"job {jid} not found", {"job_id": jid})
    job = jobs[jid]
    if job.status == "Completed":
        jobs[jid] = ProductionJob(
            job_id=job.job_id,
            worker_id=job.worker_id,
            facility_id=job.facility_id,
            recipe_id=job.recipe_id,
            inputs_reserved=job.inputs_reserved,
            progress=job.progress,
            start_tick=job.start_tick,
            completion_tick=job.completion_tick or tick,
            duration=job.duration,
            status="Deposited",
            outputs_produced=job.outputs_produced,
            tools_used=job.tools_used,
            cancel_reason="",
        )
    goods = dict(job.outputs_dict)
    src_inv, src_cap = _read_inv_for(world_state, src_key)
    dst_inv, dst_cap = _read_inv_for(world_state, dst_key)

    from .production_rules import _deduct_from_inventory, _add_to_inventory

    mid_inv, moved_goods = _deduct_from_inventory(src_inv, goods)
    if not moved_goods:
        return _empty_patch(world_id, tick_context, revision, f"prod:deposit:empty:{jid}", "Production:Deposit:EmptyGoods", f"no matching goods in {src_key}", {"job_id": jid})
    dst_new, actually_stored = _add_to_inventory(dst_inv, moved_goods, capacity=dst_cap)
    entity_patches: dict[str, Any] = {}
    _write_inv_patch(entity_patches, src_key, mid_inv, src_cap)
    _write_inv_patch(entity_patches, dst_key, dst_new, dst_cap)
    events = [GoodsDeposited(
        job_id=jid,
        destination_id=dst_key,
        goods=tuple(sorted(actually_stored.items())),
        tick=tick,
    )]
    patch: dict[str, Any] = {
        "entities": entity_patches,
        "production_jobs": {k: j.to_dict() for k, j in jobs.items()},
        "production_state": compute_state_summary(jobs).to_dict(),
    }
    metadata = {
        "domain": "production",
        "job_id": jid,
        "source_id": src_key,
        "destination_id": dst_key,
        "moved": actually_stored,
        "events": [e.to_dict() for e in events],
    }
    return _to_proposal(
        world_id, tick_context, revision,
        f"prod:deposit:{jid}",
        "Production:DepositProducts",
        patch,
        f"deposit products of {jid} {src_key}->{dst_key}",
        metadata,
    )


def cancel_production_action(
    ctx: Any,
    job_id: str,
    destination_entity_id: Any,
    reason: str = "cancelled",
) -> TransitionProposal:
    world_state, world_id, tick = _extract_context(ctx)
    tick_context = getattr(ctx, "tick_context", None)
    revision = getattr(ctx, "committed_revision", None) or None
    facilities = _load_facilities(world_state)
    jobs = _load_jobs(world_state)
    jid = str(job_id)
    dest_key = _id_str(destination_entity_id)
    if jid not in jobs:
        return _empty_patch(world_id, tick_context, revision, f"prod:cancel:missing:{jid}", "Production:Cancel:MissingJob", f"job {jid} not found", {"job_id": jid})
    job = jobs[jid]
    inv, cap = _read_inv_for(world_state, dest_key)
    try:
        cancelled_job, new_inv, returned, cancel_events = cancel_production(job, inv, dest_key, tick, reason=reason, inventory_capacity=cap)
    except ValueError as exc:
        return _empty_patch(world_id, tick_context, revision, f"prod:cancel:fail:{jid}", "Production:Cancel:Failed", str(exc), {"job_id": jid})
    jobs[jid] = cancelled_job
    facility = facilities.get(job.facility_id)
    if facility is not None:
        new_jobs = tuple(j for j in facility.active_jobs if j != jid)
        new_workers = tuple(w for w in facility.workers if w != cancelled_job.worker_id)
        facilities[job.facility_id] = ProductionFacility(
            facility_id=facility.facility_id,
            facility_type=facility.facility_type,
            location=facility.location,
            workers=new_workers,
            supported_recipes=facility.supported_recipes,
            active_jobs=new_jobs,
            capacity=facility.capacity,
        )
    entity_patches: dict[str, Any] = {}
    _write_inv_patch(entity_patches, dest_key, new_inv, cap)
    patch: dict[str, Any] = {
        "entities": entity_patches,
        "production_jobs": {k: j.to_dict() for k, j in jobs.items()},
        "production_facilities": {k: f.to_dict() for k, f in facilities.items()},
        "production_state": compute_state_summary(jobs).to_dict(),
    }
    metadata = {
        "domain": "production",
        "job_id": jid,
        "destination_id": dest_key,
        "reason": reason,
        "returned": returned,
        "events": [e.to_dict() for e in cancel_events],
    }
    return _to_proposal(
        world_id, tick_context, revision,
        f"prod:cancel:{jid}",
        "Production:CancelProduction",
        patch,
        f"cancel production job {jid} (reason: {reason})",
        metadata,
    )


def repair_tool_action(
    ctx: Any,
    tool_id: str,
    cost_source_entity_id: Any,
    repair_resource: str = "iron",
    repair_quantity: float = 1.0,
) -> TransitionProposal:
    world_state, world_id, tick = _extract_context(ctx)
    tick_context = getattr(ctx, "tick_context", None)
    revision = getattr(ctx, "committed_revision", None) or None
    tools = _load_tools(world_state)
    tid = str(tool_id)
    src_key = _id_str(cost_source_entity_id)
    tool = tools.get(tid)
    if tool is None:
        return _empty_patch(world_id, tick_context, revision, f"prod:repair:missing:{tid}", "Production:RepairTool:MissingTool", f"tool {tid} not found", {"tool_id": tid})
    inv, cap = _read_inv_for(world_state, src_key)
    from .production_rules import _deduct_from_inventory

    new_inv, spent = _deduct_from_inventory(inv, {repair_resource: repair_quantity})
    if not spent:
        return _empty_patch(world_id, tick_context, revision, f"prod:repair:short:{tid}", "Production:RepairTool:Shortage", f"need {repair_quantity} {repair_resource}", {"tool_id": tid, "resource": repair_resource})
    new_tool = ToolState(
        tool_id=tool.tool_id,
        tool_type=tool.tool_type,
        owner_id=tool.owner_id,
        durability=1.0,
        uses=tool.uses,
    )
    tools[tid] = new_tool
    entity_patches: dict[str, Any] = {}
    _write_inv_patch(entity_patches, src_key, new_inv, cap)
    patch: dict[str, Any] = {
        "entities": entity_patches,
        "production_tools": {k: t.to_dict() for k, t in tools.items()},
    }
    events = [ToolUsed(
        tool_type=tool.tool_type,
        user_id=tool.owner_id,
        job_id=f"repair:{tid}",
        uses_incremented=0,
        durability_delta=1.0 - tool.durability,
        tick=tick,
    )]
    metadata = {
        "domain": "production",
        "tool_id": tid,
        "tool_type": tool.tool_type,
        "source_id": src_key,
        "spent": spent,
        "events": [e.to_dict() for e in events],
    }
    return _to_proposal(
        world_id, tick_context, revision,
        f"prod:repair:{tid}",
        "Production:RepairTool",
        patch,
        f"repair tool {tid} using {src_key}",
        metadata,
    )


def find_worker_jobs(kernel_or_state: Any, worker_id: Any) -> list[ProductionJob]:
    state, _, _ = _extract_context(kernel_or_state)
    jobs = _load_jobs(state)
    return lookup_jobs_by_worker(jobs, _id_str(worker_id))


def find_facility_jobs(kernel_or_state: Any, facility_id: str) -> list[ProductionJob]:
    state, _, _ = _extract_context(kernel_or_state)
    jobs = _load_jobs(state)
    return lookup_jobs_by_facility(jobs, str(facility_id))


def find_status_jobs(kernel_or_state: Any, status: str) -> list[ProductionJob]:
    state, _, _ = _extract_context(kernel_or_state)
    jobs = _load_jobs(state)
    return lookup_jobs_by_status(jobs, str(status))


def find_recipes_for_output(kernel_or_state: Any, output: str) -> list[ProductionRecipe]:
    state, _, _ = _extract_context(kernel_or_state)
    recipes = _load_recipes(state)
    return lookup_recipes_for_output(recipes, str(output))


def find_idle_facilities(kernel_or_state: Any) -> list[ProductionFacility]:
    state, _, _ = _extract_context(kernel_or_state)
    facilities = _load_facilities(state)
    return sorted(
        (f for f in facilities.values() if len(f.active_jobs) < max(1, f.capacity)),
        key=lambda f: f.facility_id,
    )


def get_production_summary(kernel_or_state: Any) -> ProductionState:
    state, _, _ = _extract_context(kernel_or_state)
    jobs = _load_jobs(state)
    return compute_state_summary(jobs)


def generate_production_goals(kernel: Any) -> list[TransitionProposal]:
    world_state, world_id, tick = _extract_context(kernel)
    recipes = _load_recipes(world_state)
    tool_candidates = lookup_recipes_for_output(recipes, "tools")
    planner_engine = getattr(kernel, "planner_engine", None)
    created: list[TransitionProposal] = []
    if planner_engine is not None and tool_candidates:
        goal_manager = getattr(planner_engine, "goal_manager", None)
        if goal_manager is not None and hasattr(goal_manager, "create_goal"):
            recipe = tool_candidates[0]
            try:
                g = goal_manager.create_goal(
                    owner_id="village_planner",
                    goal_type="BeginProduction",
                    target_value=str(recipe.recipe_id),
                    priority=0.6,
                    description=f"Schedule production of {recipe.name}",
                    metadata={"recipe_id": recipe.recipe_id, "facility": recipe.facility},
                )
                correlation_id = f"prod:goal:{tick}:{recipe.recipe_id}"
                revision = getattr(kernel, "current_revision", None)
                rev_id = getattr(revision, "revision_id", None) if revision is not None else None
                created.append(TransitionProposal(
                    world_id=world_id,
                    tick_id=None,
                    state_revision=rev_id,
                    correlation_id=correlation_id,
                    subject="Production:PlannerGoal",
                    patch={},
                    description=f"planner proposed production goal for {recipe.name}",
                    metadata={"domain": "production", "goal": getattr(g, "to_dict", lambda: {"goal_id": str(g)})()},
                ))
            except Exception:
                pass
    return created
