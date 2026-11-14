from __future__ import annotations

import unittest
from datetime import datetime, timezone
from types import MappingProxyType
from typing import Any

from sim_world import KernelConfig, WorldKernel
from sim_world.core.contracts import TickContext, TransitionProposal
from sim_world.core.ids import TickId
from sim_world.domains import register_all
from sim_world.domains.agriculture import initialize_valley_agriculture
from sim_world.domains.economy import initialize_valley_economy
from sim_world.domains.population import initialize_valley_population
from sim_world.domains.production import (
    FACILITY_OCCUPATION_MATRIX,
    FACILITY_TYPES,
    JOB_STATUSES,
    OCCUPATIONS,
    PRODUCTION_EVENT_TYPES,
    PRODUCTION_TOOLS,
    GoodsDeposited,
    InputsReserved,
    ProductionCancelled,
    ProductionCompleted,
    ProductionFacility,
    ProductionJob,
    ProductionProgressed,
    ProductionRecipe,
    ProductionStarted,
    ProductionState,
    RecipeExecuted,
    ToolBroken,
    ToolState,
    ToolUsed,
    advance_production,
    advance_production_action,
    apply_tool_use_effects,
    begin_production_action,
    build_default_facilities,
    build_default_recipes,
    cancel_production,
    cancel_production_action,
    check_facility_for_recipe,
    check_inputs_available,
    check_tools_available,
    check_worker_can_cook,
    complete_production,
    complete_production_action,
    compute_state_summary,
    create_production_job,
    deposit_products_action,
    find_facility_jobs,
    find_idle_facilities,
    find_recipes_for_output,
    find_status_jobs,
    find_worker_jobs,
    initialize_valley_production,
    lookup_jobs_by_facility,
    lookup_jobs_by_status,
    lookup_jobs_by_worker,
    lookup_recipes_for_output,
    make_facility_id,
    make_job_id,
    repair_tool_action,
    reserve_inputs,
    reserve_inputs_action,
    summarize_production_delta,
)
from sim_world.domains.relationships import initialize_valley_relationships
from sim_world.domains.resources import initialize_valley_resources
from sim_world.domains.terrain import initialize_valley_terrain


class Loop4ProductionTests(unittest.TestCase):
    def setUp(self) -> None:
        self.config = KernelConfig(
            world_name="valley_world_production",
            seed="production-seed-004",
            initial_state={"mode": "valley_production_simulation"},
        )
        self.kernel = WorldKernel(self.config)
        register_all(self.kernel.simulation_engine)
        self.terrain_entities = initialize_valley_terrain(self.kernel)
        self.villager_entities = initialize_valley_population(self.kernel)
        self.building_entities = initialize_valley_resources(self.kernel)
        self.crop_fields = initialize_valley_agriculture(self.kernel)
        self.economy_state = initialize_valley_economy(self.kernel)
        self.relationships_state = initialize_valley_relationships(self.kernel)
        self.production_state = initialize_valley_production(self.kernel)

    def _create_tick_context(self, correlation_id: str = "test_prod_correlation") -> TickContext:
        tick_id = TickId.new(self.kernel.world_id, self.kernel.current_tick_number)
        rev = self.kernel.current_revision.revision_id if self.kernel.current_revision else None
        return TickContext(
            world_id=self.kernel.world_id,
            tick_id=tick_id,
            state_revision=rev,
            parent_revision=rev,
            timestamp=datetime.now(timezone.utc),
            correlation_id=correlation_id,
        )

    def test_facility_creation_and_registration(self) -> None:
        for expected in ("Farm", "Barn", "Blacksmith", "Workshop", "Kitchen", "Storage"):
            self.assertIn(expected, FACILITY_TYPES)
        self.assertEqual(len(FACILITY_TYPES), 6)

        for tool in ("Hammer", "Axe", "Hoe", "Oven", "Forge", "Mill"):
            self.assertIn(tool, PRODUCTION_TOOLS)

        for occ in ("Farmer", "Miller", "Blacksmith", "Cook", "Carpenter"):
            self.assertIn(occ, OCCUPATIONS)

        facs = build_default_facilities()
        self.assertGreaterEqual(len(facs), 6)
        for f in facs.values():
            self.assertIsInstance(f, ProductionFacility)
            self.assertIn(f.facility_type, FACILITY_TYPES)
            self.assertIsInstance(f.to_dict(), dict)
            restored = ProductionFacility.from_dict(f.to_dict())
            self.assertEqual(restored.facility_id, f.facility_id)
            self.assertEqual(restored.facility_type, f.facility_type)
            self.assertEqual(restored.location, f.location)
            self.assertEqual(restored.supported_recipes, f.supported_recipes)
            self.assertEqual(restored.capacity, f.capacity)

    def test_recipe_registration_and_properties(self) -> None:
        recipes = build_default_recipes()
        self.assertGreaterEqual(len(recipes), 8)

        required_names = {
            "Grow Wheat": ("Farm", 5),
            "Chop Firewood": ("Workshop", 2),
            "Bake Bread": ("Kitchen", 3),
            "Forge Iron Tools": ("Blacksmith", 6),
            "Mill Grain into Flour": ("Barn", 2),
        }
        for name, (fac, dur) in required_names.items():
            matches = [r for r in recipes.values() if r.name == name]
            self.assertEqual(len(matches), 1, f"recipe '{name}' should be registered exactly once")
            r = matches[0]
            self.assertEqual(r.facility, fac)
            self.assertEqual(r.duration_ticks, dur)
            self.assertGreaterEqual(len(r.inputs), 1)
            self.assertGreaterEqual(len(r.outputs), 1)
            self.assertIsInstance(r.to_dict(), dict)
            restored = ProductionRecipe.from_dict(r.to_dict())
            self.assertEqual(restored.recipe_id, r.recipe_id)
            self.assertEqual(restored.inputs, r.inputs)
            self.assertEqual(restored.outputs, r.outputs)

        for rid, r in recipes.items():
            output_names = [k for k, v in r.outputs]
            for tool in r.tools_required:
                self.assertIn(tool, PRODUCTION_TOOLS, f"recipe {rid} tool {tool} invalid")
            for ident, qty in r.inputs:
                self.assertGreater(qty, 0)
            for ident, qty in r.outputs:
                self.assertGreater(qty, 0)

    def test_input_reservation_and_availability_checks(self) -> None:
        recipes = build_default_recipes()
        r = next(r for r in recipes.values() if r.name == "Forge Iron Tools")

        ok, report = check_inputs_available(r, [
            {"identifier": "iron", "quantity": 1.0, "properties": {}},
            {"identifier": "fuel", "quantity": 0.5, "properties": {}},
        ])
        self.assertFalse(ok)
        low_idents = {ident for ident, need, have in report if have < need}
        self.assertTrue(low_idents & {"iron", "fuel", "wood"})

        full_inv = [
            {"identifier": "iron", "quantity": 10.0, "properties": {}},
            {"identifier": "fuel", "quantity": 10.0, "properties": {}},
            {"identifier": "wood", "quantity": 10.0, "properties": {}},
        ]
        ok, report = check_inputs_available(r, full_inv)
        self.assertTrue(ok, f"inputs should be available: {report}")

        inv_before = [dict(x) for x in full_inv]
        inv_after, consumed, events = reserve_inputs(r, full_inv, "Storage", "job:1", tick=1)
        for ident, need in r.inputs_dict.items():
            self.assertAlmostEqual(consumed[ident], need, places=3)
        totals_after: dict[str, float] = {}
        for row in inv_after:
            totals_after[str(row["identifier"])] = totals_after.get(str(row["identifier"]), 0.0) + float(row["quantity"])
        for ident, need in r.inputs_dict.items():
            expected = 10.0 - need
            self.assertAlmostEqual(totals_after.get(ident, 0.0), expected, places=3)
        self.assertEqual([dict(x) for x in full_inv], inv_before)
        ev_types = [e.event_type for e in events]
        self.assertIn("InputsReserved", ev_types)

        shortage_inv = [{"identifier": "iron", "quantity": 0.01, "properties": {}}]
        with self.assertRaises((ValueError, Exception)):
            reserve_inputs(r, shortage_inv, "X", "job:2", tick=2)

    def test_production_jobs_creation_and_status(self) -> None:
        recipes = build_default_recipes()
        facilities = build_default_facilities()
        r = next(r for r in recipes.values() if r.name == "Bake Bread")
        f = next(f for f in facilities.values() if check_facility_for_recipe(r, f))

        inv = [
            {"identifier": "food", "quantity": 20.0, "properties": {}},
            {"identifier": "fuel", "quantity": 10.0, "properties": {}},
            {"identifier": "water", "quantity": 10.0, "properties": {}},
        ]
        new_inv, consumed, rev = reserve_inputs(r, inv, "Src", "j", tick=0)

        f_before = f.to_dict()
        job, new_f, evs = create_production_job(r, f, "Mira", consumed, list(r.tools_required), tick=0)
        self.assertEqual(f.to_dict(), f_before)
        self.assertIn(job.job_id, new_f.active_jobs)
        self.assertEqual(job.status, "Reserved")
        self.assertIn(job.status, JOB_STATUSES)
        self.assertEqual(job.recipe_id, r.recipe_id)
        self.assertEqual(job.worker_id, "Mira")
        self.assertEqual(job.start_tick, 0)
        self.assertGreater(job.duration, 0)
        self.assertEqual([(k, v) for k, v in job.inputs_reserved], sorted(consumed.items()))
        ev_types = [e.event_type for e in evs]
        self.assertIn("ProductionStarted", ev_types)
        self.assertEqual(len([e for e in evs if isinstance(e, ProductionStarted)]), 1)

        d = job.to_dict()
        self.assertIsInstance(d, dict)
        restored = ProductionJob.from_dict(d)
        self.assertEqual(restored.job_id, job.job_id)
        self.assertEqual(restored.status, job.status)
        self.assertEqual(restored.progress, job.progress)
        self.assertEqual(restored.inputs_reserved, job.inputs_reserved)

    def test_worker_assignment_and_occupation_rules(self) -> None:
        recipes = build_default_recipes()

        cook_job = next(r for r in recipes.values() if r.name == "Cook Meal")
        farmer_job = next(r for r in recipes.values() if r.name == "Grow Wheat")
        smith_job = next(r for r in recipes.values() if r.name == "Smelt Iron Ingots")

        self.assertTrue(check_worker_can_cook(cook_job, "X", {"X": "Cook"}))
        self.assertTrue(check_worker_can_cook(farmer_job, "Y", {"Y": "Farmer"}))
        self.assertTrue(check_worker_can_cook(smith_job, "Z", {"Z": "Blacksmith"}))

        self.assertFalse(check_worker_can_cook(cook_job, "A", {"A": "Farmer"}))
        self.assertFalse(check_worker_can_cook(smith_job, "B", {"B": "Cook"}))

        self.assertTrue(check_worker_can_cook(cook_job, "NoOcc", {}))

        for ftype, allowed in FACILITY_OCCUPATION_MATRIX.items():
            for occ in allowed:
                self.assertIn(occ, OCCUPATIONS)

    def test_progress_advancement_and_completion(self) -> None:
        recipes = build_default_recipes()
        facilities = build_default_facilities()
        r = next(r for r in recipes.values() if r.name == "Mill Planks")
        f = next(f for f in facilities.values() if check_facility_for_recipe(r, f))
        inv = [{"identifier": "wood", "quantity": 10.0, "properties": {}}]
        ni, consumed, _ = reserve_inputs(r, inv, "S", "j", tick=0)
        job, nf, _ = create_production_job(r, f, "Mira", consumed, list(r.tools_required), tick=0)

        tick = 0
        current = job
        prog_events: list[ProductionProgressed] = []
        tool_events: list[ToolUsed] = []
        for _ in range(100):
            tick += 1
            before = current.to_dict()
            new_job, evs, done = advance_production(current, tick, r)
            self.assertEqual(current.to_dict(), before)
            if new_job is not current:
                self.assertGreater(new_job.progress, current.progress - 1e-9)
            for ev in evs:
                if isinstance(ev, ProductionProgressed):
                    prog_events.append(ev)
                if isinstance(ev, ToolUsed):
                    tool_events.append(ev)
            current = new_job
            if done:
                break
        self.assertGreaterEqual(current.progress, 1.0)
        self.assertEqual(current.status, "Completed")
        self.assertGreater(len(prog_events), 0)
        self.assertEqual(len(tool_events), len(r.tools_required) * len(prog_events))
        self.assertTrue(current.is_completed)

    def test_output_deposition_and_resource_conservation(self) -> None:
        recipes = build_default_recipes()
        facilities = build_default_facilities()
        flows = [
            ("Bake Bread", "food"),
            ("Chop Firewood", "fuel"),
            ("Grow Wheat", "food"),
            ("Forge Iron Tools", "tools"),
        ]
        for rname, expected_output in flows:
            r = next(r for r in recipes.values() if r.name == rname)
            f = next(f for f in facilities.values() if check_facility_for_recipe(r, f))
            inv_in: list[dict[str, Any]] = []
            totals_before: dict[str, float] = {}
            for ident, qty in r.inputs_dict.items():
                inv_in.append({"identifier": ident, "quantity": qty * 5.0, "properties": {}})
                totals_before[ident] = qty * 5.0
            ni, consumed, _ = reserve_inputs(r, inv_in, "S", "j", tick=0)
            totals_after_reserve: dict[str, float] = {}
            for row in ni:
                totals_after_reserve[str(row["identifier"])] = totals_after_reserve.get(str(row["identifier"]), 0.0) + float(row["quantity"])
            for ident, need in consumed.items():
                self.assertAlmostEqual(totals_before.get(ident, 0.0) - totals_after_reserve.get(ident, 0.0), need, places=3)
            job, _, _ = create_production_job(r, f, "M", consumed, list(r.tools_required), tick=0)
            tick = 0
            cur = job
            done = False
            while not done:
                tick += 1
                cur, evs, done = advance_production(cur, tick, r)
            dst_inv: list[dict[str, Any]] = []
            cjob, new_dst, produced, cevents, _ = complete_production(cur, r, dst_inv, "Dest", tick=tick)
            self.assertEqual(cjob.status, "Deposited")
            self.assertIn(expected_output, produced)
            self.assertGreater(produced[expected_output], 0.0)
            self.assertAlmostEqual(produced[expected_output], r.outputs_dict[expected_output], places=3)
            names = [type(e).__name__ for e in cevents]
            self.assertIn("ProductionCompleted", names)
            self.assertIn("RecipeExecuted", names)
            self.assertIn("GoodsDeposited", names)
            input_res, output_res = summarize_production_delta(cjob)
            self.assertEqual(input_res, consumed)

    def test_tool_requirements_and_missing_tools(self) -> None:
        recipes = build_default_recipes()
        forge_tools = next(r for r in recipes.values() if r.name == "Forge Iron Tools")
        self.assertIn("Forge", forge_tools.tools_required)
        self.assertIn("Hammer", forge_tools.tools_required)

        ok, missing = check_tools_available(forge_tools, [])
        self.assertFalse(ok)
        self.assertIn("Forge", missing)
        self.assertIn("Hammer", missing)

        ok, missing = check_tools_available(forge_tools, ["Forge", "Hammer", "Axe"])
        self.assertTrue(ok)
        self.assertEqual(len(missing), 0)

        for tool in PRODUCTION_TOOLS:
            t = ToolState(
                tool_id=f"tool:{tool}:Mira",
                tool_type=tool,
                owner_id="Mira",
                durability=1.0,
                uses=0,
            )
            self.assertEqual(t.tool_type, tool)
            self.assertIsInstance(t.to_dict(), dict)
            restored = ToolState.from_dict(t.to_dict())
            self.assertEqual(restored.tool_id, t.tool_id)
            self.assertEqual(restored.durability, 1.0)

        use_ev = ToolUsed(tool_type="Hammer", user_id="Mira", job_id="X", uses_incremented=1, durability_delta=-0.05, tick=1)
        tools = [ToolState(tool_id="t1", tool_type="Hammer", owner_id="Mira", durability=1.0, uses=0)]
        updated, extra = apply_tool_use_effects(tools, [use_ev])
        self.assertEqual(updated[0].uses, 1)
        self.assertAlmostEqual(updated[0].durability, 0.95)
        self.assertEqual(len([e for e in extra if isinstance(e, ToolBroken)]), 0)

        break_ev = ToolUsed(tool_type="Hammer", user_id="Mira", job_id="Y", uses_incremented=100, durability_delta=-1.0, tick=2)
        updated2, extra2 = apply_tool_use_effects(tools, [break_ev])
        broken = [e for e in extra2 if isinstance(e, ToolBroken)]
        self.assertGreaterEqual(len(broken), 1)
        self.assertEqual(broken[0].tool_type, "Hammer")

    def test_planner_production_lookup_queries(self) -> None:
        recipes = build_default_recipes()
        facilities = build_default_facilities()
        jobs_map: dict[str, ProductionJob] = {}

        wheat_r = next(r for r in recipes.values() if r.name == "Grow Wheat")
        bread_r = next(r for r in recipes.values() if r.name == "Bake Bread")
        tools_r = next(r for r in recipes.values() if r.name == "Forge Wooden Tools")

        def make_job(r, worker, tick_start):
            f = next(f for f in facilities.values() if check_facility_for_recipe(r, f))
            inv = [{"identifier": ident, "quantity": 50.0 * need, "properties": {}} for ident, need in r.inputs_dict.items()]
            ni, consumed, _ = reserve_inputs(r, inv, "S", worker, tick=tick_start)
            job, nf, evs = create_production_job(r, f, worker, consumed, list(r.tools_required), tick=tick_start)
            return job

        j1 = make_job(wheat_r, "Mira", 0)
        j2 = make_job(bread_r, "Mira", 0)
        j3 = make_job(tools_r, "Joren", 0)
        for j in (j1, j2, j3):
            jobs_map[j.job_id] = j

        by_mira = lookup_jobs_by_worker(jobs_map, "Mira")
        self.assertEqual(len(by_mira), 2)
        for j in by_mira:
            self.assertEqual(j.worker_id, "Mira")
        by_joren = lookup_jobs_by_worker(jobs_map, "Joren")
        self.assertEqual(len(by_joren), 1)

        fac_jobs = lookup_jobs_by_facility(jobs_map, j1.facility_id)
        self.assertGreaterEqual(len(fac_jobs), 1)
        reserved_jobs = lookup_jobs_by_status(jobs_map, "Reserved")
        self.assertEqual(len(reserved_jobs), 3)

        tool_recipes = lookup_recipes_for_output(recipes, "tools")
        self.assertGreaterEqual(len(tool_recipes), 1)
        for r in tool_recipes:
            self.assertIn("tools", r.outputs_dict)

        state = compute_state_summary(jobs_map)
        self.assertEqual(state.reserved_count, 3)
        self.assertIn(state.phase, ("Idle", "Scheduled", "Active"))

        idle = [f.facility_id for f in find_idle_facilities({"production_facilities": {k: v.to_dict() for k, v in facilities.items()}})]
        self.assertGreaterEqual(len(idle), 1)

    def test_simulation_proposal_generation(self) -> None:
        recipes = build_default_recipes()
        r = next(r for r in recipes.values() if r.name == "Bake Bread")

        villager_ids = sorted(self.villager_entities.keys())
        storage_ids = sorted(self.building_entities.keys())
        kitchen_building = next((bid for bid in storage_ids if "Storage" in bid or "Kitchen" in bid or "Tavern" in bid), storage_ids[0])

        ctx1 = type("Ctx", (), {
            "current_state": dict(self.kernel.current_state),
            "world_id": self.kernel.world_id,
            "current_tick_number": int(self.kernel.current_tick_number),
            "tick_context": self._create_tick_context(),
            "committed_revision": self.kernel.current_revision.revision_id if self.kernel.current_revision else None,
        })()
        prop = reserve_inputs_action(ctx1, r.recipe_id, kitchen_building)
        self.assertIsInstance(prop, TransitionProposal)
        self.assertEqual(type(prop.patch), MappingProxyType)

        if prop.patch:
            result = self.kernel.commit_state((prop,))
            self.assertIsNotNone(result)

        facilities = build_default_facilities()
        f = next(f for f in facilities.values() if check_facility_for_recipe(r, f))
        tools_list = list(r.tools_required)

        ctx2 = type("Ctx", (), {
            "current_state": dict(self.kernel.current_state),
            "world_id": self.kernel.world_id,
            "current_tick_number": int(self.kernel.current_tick_number),
            "tick_context": self._create_tick_context(),
            "committed_revision": self.kernel.current_revision.revision_id if self.kernel.current_revision else None,
        })()
        worker = villager_ids[0]
        occupation_map = {str(worker.value) if hasattr(worker, "value") else str(worker): "Cook"}
        begin = begin_production_action(
            ctx2, r.recipe_id, f.facility_id, worker,
            kitchen_building, kitchen_building,
            occupation_map=occupation_map, available_tools=tools_list,
        )
        self.assertIsInstance(begin, TransitionProposal)
        md = dict(begin.metadata)
        self.assertIn("recipe_id", md)
        self.assertIn("events", md)
        self.assertTrue(
            isinstance(md.get("events"), list) or isinstance(md.get("events"), tuple),
            f"events metadata should be sequence, got {type(md.get('events'))}"
        )

    def test_replay_determinism(self) -> None:
        recipes = build_default_recipes()
        facilities = build_default_facilities()
        r = next(r for r in recipes.values() if r.name == "Bake Bread")
        f = next(f for f in facilities.values() if check_facility_for_recipe(r, f))
        inv = [
            {"identifier": "food", "quantity": 200.0, "properties": {}},
            {"identifier": "fuel", "quantity": 100.0, "properties": {}},
            {"identifier": "water", "quantity": 100.0, "properties": {}},
        ]

        def run_once(seed_label: str) -> tuple[str, list[float]]:
            ni, consumed, _ = reserve_inputs(r, list(inv), "S", f"j_{seed_label}", tick=0)
            job, nf, _ = create_production_job(r, f, "M", consumed, list(r.tools_required), tick=0)
            tick = 0
            cur = job
            progresses: list[float] = []
            for _ in range(20):
                tick += 1
                cur, evs, done = advance_production(cur, tick, r)
                progresses.append(round(cur.progress, 6))
                if done:
                    break
            cjob, new_dst, produced, cevents, _ = complete_production(cur, r, [], "Dest", tick=tick)
            return cjob.job_id[:10] + ":" + cjob.status + ":" + ",".join(f"{k}={v}" for k, v in sorted(produced.items())), progresses

        rA1, pA1 = run_once("a1")
        rA2, pA2 = run_once("a1")
        rB, pB = run_once("b1")

        self.assertEqual(rA1, rA2, "identical seeds must replay identical job state + output")
        self.assertEqual(pA1, pA2, "identical seeds must replay identical progress sequence")
        rB_id = rB.split(":", 1)[1]
        rA_id = rA1.split(":", 1)[1]
        self.assertEqual(rA_id, rB_id, "outputs should be deterministic even with different ids if inputs equal")

    def test_no_direct_world_mutation(self) -> None:
        recipes = build_default_recipes()
        facilities = build_default_facilities()
        r = next(r for r in recipes.values() if r.name == "Chop Firewood")
        f = next(f for f in facilities.values() if check_facility_for_recipe(r, f))

        inv = [{"identifier": "wood", "quantity": 10.0, "properties": {}}]
        inv_snap = [dict(x) for x in inv]
        fac_snap = f.to_dict()
        job, nf, evs = create_production_job(r, f, "M", {"wood": 1.0}, list(r.tools_required), tick=0)
        self.assertEqual([dict(x) for x in inv], inv_snap)
        self.assertEqual(f.to_dict(), fac_snap)

        job_snap = job.to_dict()
        job2, evs2, done = advance_production(job, 1, r)
        self.assertEqual(job.to_dict(), job_snap)

        r2 = next(r for r in recipes.values() if r.name == "Bake Bread")
        inv2 = [
            {"identifier": "food", "quantity": 20.0, "properties": {}},
            {"identifier": "fuel", "quantity": 10.0, "properties": {}},
            {"identifier": "water", "quantity": 10.0, "properties": {}},
        ]
        inv2_snap = [dict(x) for x in inv2]
        ri2, consumed2, evs3 = reserve_inputs(r2, inv2, "S", "j", tick=0)
        self.assertEqual([dict(x) for x in inv2], inv2_snap)

    def test_events_immutability_and_types(self) -> None:
        self.assertEqual(len(PRODUCTION_EVENT_TYPES), 9)
        for name in ("ProductionStarted","InputsReserved","ProductionProgressed",
                     "ProductionCompleted","ProductionCancelled","ToolUsed",
                     "ToolBroken","GoodsDeposited","RecipeExecuted"):
            self.assertIn(name, PRODUCTION_EVENT_TYPES)

        samples = [
            ProductionStarted(job_id="j", recipe_id="r", facility_id="f", worker_id="w", tick=1),
            InputsReserved(job_id="j", inputs=(("x", 1.0),), source_id="s", tick=1),
            ProductionProgressed(job_id="j", progress_before=0.0, progress_after=0.5, duration_ticks=2, tick=1),
            ProductionCompleted(job_id="j", recipe_id="r", outputs=(("y", 1.0),), tick=2),
            ProductionCancelled(job_id="j", reason="X", inputs_returned=(("x", 1.0),), tick=3),
            ToolUsed(tool_type="Hoe", user_id="M", job_id="j", tick=2),
            ToolBroken(tool_type="Axe", owner_id="J", job_id="j", tick=3),
            GoodsDeposited(job_id="j", destination_id="D", goods=(("food", 5.0),), tick=4),
            RecipeExecuted(recipe_id="r", facility_id="f", worker_id="w", inputs=(("x",1.0),), outputs=(("y",1.0),), duration_ticks=1, tick=5),
        ]
        for idx, ev in enumerate(samples):
            d = ev.to_dict()
            self.assertEqual(d["event_type"], PRODUCTION_EVENT_TYPES[idx])
            self.assertIn("tick", d)
            self.assertIsInstance(d["tick"], int)

    def test_all_recipes_have_valid_facility_worker_tool_config(self) -> None:
        recipes = build_default_recipes()
        facilities = build_default_facilities()
        for rid, r in recipes.items():
            self.assertIn(r.facility, FACILITY_TYPES, f"recipe {rid}: invalid facility")
            self.assertIn(r.occupation, OCCUPATIONS, f"recipe {rid}: invalid occupation")
            found = False
            for f in facilities.values():
                if f.facility_type == r.facility and rid in f.supported_recipes:
                    found = True
                    break
            self.assertTrue(found, f"recipe {rid} not in any facility of type {r.facility}")
            for tool in r.tools_required:
                self.assertIn(tool, PRODUCTION_TOOLS, f"recipe {rid}: invalid tool '{tool}'")
            self.assertGreaterEqual(r.duration_ticks, 1, f"recipe {rid}: duration must be >=1")
            self.assertGreaterEqual(len(r.inputs), 1, f"recipe {rid}: inputs missing")
            self.assertGreaterEqual(len(r.outputs), 1, f"recipe {rid}: outputs missing")

    def test_cancel_production_returns_reserved_inputs(self) -> None:
        recipes = build_default_recipes()
        facilities = build_default_facilities()
        r = next(r for r in recipes.values() if r.name == "Smelt Iron Ingots")
        f = next(f for f in facilities.values() if check_facility_for_recipe(r, f))
        inv = [
            {"identifier": "iron", "quantity": 20.0, "properties": {}},
            {"identifier": "fuel", "quantity": 10.0, "properties": {}},
        ]
        ni, consumed, _ = reserve_inputs(r, inv, "Src", "j", tick=0)
        job, nf, evs = create_production_job(r, f, "M", consumed, list(r.tools_required), tick=0)
        cur = job
        for tick in (1, 2):
            cur, _, _ = advance_production(cur, tick, r)
        empty_dst: list[dict[str, Any]] = []
        cancelled, dst_inv, returned, cevs = cancel_production(cur, empty_dst, "Storage", tick=3, reason="cancelled")
        self.assertEqual(cancelled.status, "Cancelled")
        self.assertEqual(cancelled.cancel_reason, "cancelled")
        for ident, need in consumed.items():
            self.assertAlmostEqual(returned.get(ident, 0.0), need, places=3)
        self.assertTrue(any(isinstance(e, ProductionCancelled) for e in cevs))

        self.assertFalse(cur.is_completed)
        cancelled2, _, _, _ = cancel_production(job, [], "X", tick=1, reason="early")
        self.assertEqual(cancelled2.status, "Cancelled")

    def test_progress_never_skips_duration(self) -> None:
        recipes = build_default_recipes()
        facilities = build_default_facilities()
        for rname in ("Grow Wheat", "Mill Planks", "Bake Bread", "Forge Iron Tools"):
            r = next(r for r in recipes.values() if r.name == rname)
            f = next(f for f in facilities.values() if check_facility_for_recipe(r, f))
            inv = [{"identifier": ident, "quantity": 100.0 * need, "properties": {}} for ident, need in r.inputs_dict.items()]
            ni, consumed, _ = reserve_inputs(r, inv, "S", "j", tick=0)
            job, _, _ = create_production_job(r, f, "M", consumed, list(r.tools_required), tick=0)
            tick = 0
            cur = job
            steps = 0
            done = False
            while not done:
                tick += 1
                steps += 1
                before = cur.progress
                cur, _, done = advance_production(cur, tick, r)
                after = cur.progress
                per_step = 1.0 / float(r.duration_ticks)
                self.assertLessEqual(after - before, per_step + 1e-9,
                    f"{rname}: progress step too large ({after-before} vs max {per_step})")
                if steps > 1000:
                    break
            self.assertGreaterEqual(steps, r.duration_ticks,
                f"{rname}: completed in {steps} ticks but duration={r.duration_ticks}")
            self.assertEqual(cur.status, "Completed")
