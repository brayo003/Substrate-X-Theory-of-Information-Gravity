from __future__ import annotations

from typing import Any, Mapping, Sequence

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
    FACILITY_OCCUPATION_MATRIX,
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
    make_job_id,
)


DEFAULT_RESERVATION_MATRIX: dict[str, tuple[str, ...]] = FACILITY_OCCUPATION_MATRIX


def check_facility_for_recipe(
    recipe: ProductionRecipe,
    facility: ProductionFacility,
) -> bool:
    if recipe.facility != facility.facility_type:
        return False
    if recipe.recipe_id not in facility.supported_recipes:
        return False
    return len(facility.active_jobs) < max(1, facility.capacity)


def check_worker_can_cook(
    recipe: ProductionRecipe,
    worker_id: str,
    occupation_map: Mapping[str, str] | None = None,
) -> bool:
    if not worker_id:
        return False
    if occupation_map is None:
        return True
    worker_occ = str(occupation_map.get(str(worker_id), ""))
    allowed = DEFAULT_RESERVATION_MATRIX.get(recipe.facility, (recipe.occupation,))
    if not worker_occ:
        return True
    return worker_occ in allowed or worker_occ == recipe.occupation


def check_tools_available(
    recipe: ProductionRecipe,
    available_tools: Sequence[str],
) -> tuple[bool, tuple[str, ...]]:
    available_set = {str(t) for t in available_tools}
    missing: list[str] = []
    for required in recipe.tools_required:
        if required not in available_set:
            missing.append(str(required))
    return (len(missing) == 0, tuple(missing))


def check_inputs_available(
    recipe: ProductionRecipe,
    inventory: Sequence[Mapping[str, Any]],
) -> tuple[bool, tuple[tuple[str, float, float], ...]]:
    inventory_map: dict[str, float] = {}
    for row in inventory:
        if isinstance(row, Mapping):
            ident = str(row.get("identifier", row.get("resource_type", "")))
            qty = float(row.get("quantity", 0.0))
            if ident:
                inventory_map[ident] = inventory_map.get(ident, 0.0) + qty
    report: list[tuple[str, float, float]] = []
    ok = True
    for ident, need in recipe.inputs_dict.items():
        have = inventory_map.get(ident, 0.0)
        if have < need:
            ok = False
        report.append((ident, need, have))
    return (ok, tuple(report))


def _deduct_from_inventory(
    inventory: Sequence[Mapping[str, Any]],
    deductions: Mapping[str, float],
) -> tuple[list[dict[str, Any]], dict[str, float]]:
    dst = [dict(row) for row in inventory]
    actually_consumed: dict[str, float] = {}
    for ident, qty_needed in deductions.items():
        remaining = max(0.0, float(qty_needed))
        idx = 0
        while remaining > 0.0 and idx < len(dst):
            row = dst[idx]
            row_ident = str(row.get("identifier", row.get("resource_type", "")))
            if row_ident == ident:
                row_qty = float(row.get("quantity", 0.0))
                take = min(row_qty, remaining)
                row_qty -= take
                remaining -= take
                actually_consumed[ident] = actually_consumed.get(ident, 0.0) + take
                if row_qty <= 0.0:
                    dst.pop(idx)
                    continue
                row["quantity"] = row_qty
            idx += 1
    return dst, actually_consumed


def _add_to_inventory(
    inventory: Sequence[Mapping[str, Any]],
    additions: Mapping[str, float],
    capacity: float = 500.0,
) -> tuple[list[dict[str, Any]], dict[str, float]]:
    dst = [dict(row) for row in inventory]
    current_total = sum(float(r.get("quantity", 0.0)) for r in dst)
    available_capacity = max(0.0, float(capacity) - current_total)
    actually_added: dict[str, float] = {}
    for ident, qty_wanted in additions.items():
        qty = float(qty_wanted)
        qty = min(qty, available_capacity)
        available_capacity -= qty
        if qty <= 0.0:
            continue
        found = False
        for row in dst:
            row_ident = str(row.get("identifier", row.get("resource_type", "")))
            if row_ident == ident:
                row["quantity"] = float(row.get("quantity", 0.0)) + qty
                actually_added[ident] = actually_added.get(ident, 0.0) + qty
                found = True
                break
        if not found:
            dst.append({
                "identifier": ident,
                "quantity": qty,
                "properties": {},
            })
            actually_added[ident] = actually_added.get(ident, 0.0) + qty
    return dst, actually_added


def reserve_inputs(
    recipe: ProductionRecipe,
    inventory: Sequence[Mapping[str, Any]],
    source_id: str,
    job_id: str,
    tick: int,
) -> tuple[list[dict[str, Any]], dict[str, float], list[Any]]:
    ok, report = check_inputs_available(recipe, inventory)
    if not ok:
        missing_parts = ";".join(
            f"{ident}: need {need}, have {have}"
            for ident, need, have in report
            if have < need
        )
        raise ValueError(f"Insufficient inputs to reserve for {recipe.recipe_id}: {missing_parts}")
    deductions = dict(recipe.inputs_dict)
    new_inv, consumed = _deduct_from_inventory(inventory, deductions)
    events = [InputsReserved(
        job_id=job_id,
        inputs=tuple(consumed.items()),
        source_id=source_id,
        tick=tick,
    )]
    return new_inv, consumed, events


def create_production_job(
    recipe: ProductionRecipe,
    facility: ProductionFacility,
    worker_id: str,
    inputs_reserved: Mapping[str, float],
    tools: Sequence[str],
    tick: int,
) -> tuple[ProductionJob, ProductionFacility, list[Any]]:
    if not check_facility_for_recipe(recipe, facility):
        raise ValueError(f"Facility {facility.facility_id} cannot run {recipe.recipe_id}")
    if not worker_id:
        raise ValueError("Production job requires a worker")
    job_id = make_job_id(facility.facility_id, recipe.recipe_id, worker_id, tick)
    job = ProductionJob(
        job_id=job_id,
        worker_id=str(worker_id),
        facility_id=facility.facility_id,
        recipe_id=recipe.recipe_id,
        inputs_reserved=tuple(sorted((k, v) for k, v in inputs_reserved.items())),
        progress=0.0,
        start_tick=tick,
        completion_tick=0,
        duration=max(1, recipe.duration_ticks),
        status="Reserved",
        outputs_produced=(),
        tools_used=tuple(tools),
    )
    updated_facility = ProductionFacility(
        facility_id=facility.facility_id,
        facility_type=facility.facility_type,
        location=facility.location,
        workers=tuple(sorted(set(facility.workers + (str(worker_id),)))),
        supported_recipes=facility.supported_recipes,
        active_jobs=facility.active_jobs + (job_id,),
        capacity=facility.capacity,
    )
    events: list[Any] = [
        ProductionStarted(
            job_id=job_id,
            recipe_id=recipe.recipe_id,
            facility_id=facility.facility_id,
            worker_id=str(worker_id),
            tick=tick,
        )
    ]
    return job, updated_facility, events


def advance_production(
    job: ProductionJob,
    current_tick: int,
    recipe: ProductionRecipe | None = None,
) -> tuple[ProductionJob, list[Any], bool]:
    if job.status == "Cancelled":
        return job, [], False
    if job.is_completed:
        return job, [], False
    duration = max(1, job.duration)
    before = job.progress
    per_tick = 1.0 / float(duration)
    new_progress = min(1.0, before + per_tick)
    new_status = job.status
    events: list[Any] = []
    if new_status == "Reserved":
        new_status = "Active"
    if new_status == "Active":
        new_status = "Progressing"
    progressed = ProductionProgressed(
        job_id=job.job_id,
        progress_before=before,
        progress_after=new_progress,
        duration_ticks=duration,
        tick=current_tick,
    )
    events.append(progressed)
    if recipe is not None and len(recipe.tools_required) > 0:
        for tool in recipe.tools_required:
            events.append(ToolUsed(
                tool_type=tool,
                user_id=job.worker_id,
                job_id=job.job_id,
                uses_incremented=1,
                durability_delta=-(1.0 / float(max(1, duration * 5))),
                tick=current_tick,
            ))
    finished = new_progress >= 1.0
    completion_tick = job.completion_tick
    status = new_status
    if finished:
        status = "Completed"
        completion_tick = current_tick
    updated_job = ProductionJob(
        job_id=job.job_id,
        worker_id=job.worker_id,
        facility_id=job.facility_id,
        recipe_id=job.recipe_id,
        inputs_reserved=job.inputs_reserved,
        progress=new_progress,
        start_tick=job.start_tick,
        completion_tick=completion_tick,
        duration=duration,
        status=status,
        outputs_produced=job.outputs_produced,
        tools_used=job.tools_used,
        cancel_reason=job.cancel_reason,
    )
    return updated_job, events, finished


def complete_production(
    job: ProductionJob,
    recipe: ProductionRecipe,
    inventory: Sequence[Mapping[str, Any]],
    destination_id: str,
    tick: int,
    inventory_capacity: float = 500.0,
) -> tuple[ProductionJob, list[dict[str, Any]], dict[str, float], list[Any], ProductionFacility | None]:
    if not job.is_completed and job.progress < 1.0:
        raise ValueError(f"Job {job.job_id} not finished; cannot complete")
    produced = dict(recipe.outputs_dict)
    new_inv, actually_added = _add_to_inventory(inventory, produced, capacity=inventory_capacity)
    completed_job = ProductionJob(
        job_id=job.job_id,
        worker_id=job.worker_id,
        facility_id=job.facility_id,
        recipe_id=job.recipe_id,
        inputs_reserved=job.inputs_reserved,
        progress=1.0,
        start_tick=job.start_tick,
        completion_tick=tick if job.completion_tick <= 0 else job.completion_tick,
        duration=job.duration,
        status="Deposited",
        outputs_produced=tuple(sorted(actually_added.items())),
        tools_used=job.tools_used,
        cancel_reason="",
    )
    events: list[Any] = [
        ProductionCompleted(
            job_id=job.job_id,
            recipe_id=recipe.recipe_id,
            outputs=tuple(sorted(actually_added.items())),
            tick=tick,
        ),
        RecipeExecuted(
            recipe_id=recipe.recipe_id,
            facility_id=job.facility_id,
            worker_id=job.worker_id,
            inputs=job.inputs_reserved,
            outputs=tuple(sorted(actually_added.items())),
            duration_ticks=recipe.duration_ticks,
            tick=tick,
        ),
        GoodsDeposited(
            job_id=job.job_id,
            destination_id=destination_id,
            goods=tuple(sorted(actually_added.items())),
            tick=tick,
        ),
    ]
    return completed_job, new_inv, actually_added, events, None


def cancel_production(
    job: ProductionJob,
    inventory: Sequence[Mapping[str, Any]],
    destination_id: str,
    tick: int,
    reason: str = "",
    inventory_capacity: float = 500.0,
) -> tuple[ProductionJob, list[dict[str, Any]], dict[str, float], list[Any]]:
    if job.is_completed:
        raise ValueError(f"Job {job.job_id} already completed; cannot cancel")
    return_inputs = dict(job.inputs_dict)
    new_inv, returned = _add_to_inventory(inventory, return_inputs, capacity=inventory_capacity)
    cancelled_job = ProductionJob(
        job_id=job.job_id,
        worker_id=job.worker_id,
        facility_id=job.facility_id,
        recipe_id=job.recipe_id,
        inputs_reserved=job.inputs_reserved,
        progress=job.progress,
        start_tick=job.start_tick,
        completion_tick=tick,
        duration=job.duration,
        status="Cancelled",
        outputs_produced=(),
        tools_used=job.tools_used,
        cancel_reason=str(reason),
    )
    events: list[Any] = [
        ProductionCancelled(
            job_id=job.job_id,
            reason=str(reason),
            inputs_returned=tuple(sorted(returned.items())),
            tick=tick,
        )
    ]
    return cancelled_job, new_inv, returned, events


def apply_tool_use_effects(
    tools: Sequence[ToolState],
    events: Sequence[Any],
) -> tuple[list[ToolState], list[Any]]:
    updated: list[ToolState] = [ToolState.from_dict(t.to_dict()) for t in tools]
    emitted: list[Any] = []
    for evt in events:
        if not isinstance(evt, ToolUsed):
            continue
        for i, tool in enumerate(updated):
            if tool.tool_type != evt.tool_type:
                continue
            new_uses = tool.uses + max(0, int(evt.uses_incremented))
            new_dur = max(0.0, min(1.0, tool.durability + float(evt.durability_delta)))
            updated[i] = ToolState(
                tool_id=tool.tool_id,
                tool_type=tool.tool_type,
                owner_id=tool.owner_id,
                durability=new_dur,
                uses=new_uses,
            )
            if new_dur <= 0.0:
                emitted.append(ToolBroken(
                    tool_type=tool.tool_type,
                    owner_id=tool.owner_id,
                    job_id=evt.job_id,
                    tick=evt.tick,
                ))
    return updated, emitted


def compute_state_summary(
    jobs: Mapping[str, ProductionJob],
) -> ProductionState:
    active = 0
    reserved = 0
    completed = 0
    cancelled = 0
    deposited = 0
    phase = "Idle"
    for job in jobs.values():
        if job.status == "Reserved":
            reserved += 1
            phase = "Scheduled"
        elif job.status in ("Active", "Progressing"):
            active += 1
            phase = "Active"
        elif job.status == "Completed":
            completed += 1
            phase = "PendingDeposit" if phase != "Active" else phase
        elif job.status == "Deposited":
            deposited += 1
        elif job.status == "Cancelled":
            cancelled += 1
    return ProductionState(
        phase=phase,
        active_job_count=active,
        completed_count=completed,
        cancelled_count=cancelled,
        reserved_count=reserved,
        deposited_count=deposited,
    )


def lookup_jobs_by_worker(
    jobs: Mapping[str, ProductionJob],
    worker_id: str,
) -> list[ProductionJob]:
    needle = str(worker_id)
    return [
        jobs[k] for k in sorted(jobs.keys())
        if jobs[k].worker_id == needle
    ]


def lookup_jobs_by_facility(
    jobs: Mapping[str, ProductionJob],
    facility_id: str,
) -> list[ProductionJob]:
    needle = str(facility_id)
    return [
        jobs[k] for k in sorted(jobs.keys())
        if jobs[k].facility_id == needle
    ]


def lookup_jobs_by_status(
    jobs: Mapping[str, ProductionJob],
    status: str,
) -> list[ProductionJob]:
    needle = str(status) if status in JOB_STATUSES else "Active"
    return [
        jobs[k] for k in sorted(jobs.keys())
        if jobs[k].status == needle
    ]


def lookup_recipes_for_output(
    recipes: Mapping[str, ProductionRecipe],
    output_resource: str,
) -> list[ProductionRecipe]:
    needle = str(output_resource)
    matches: list[ProductionRecipe] = []
    for rid in sorted(recipes.keys()):
        r = recipes[rid]
        if needle in r.outputs_dict:
            matches.append(r)
    return matches


def summarize_production_delta(
    job: ProductionJob,
) -> tuple[dict[str, float], dict[str, float]]:
    inputs = dict(job.inputs_dict)
    outputs = dict(job.outputs_dict)
    return inputs, outputs
