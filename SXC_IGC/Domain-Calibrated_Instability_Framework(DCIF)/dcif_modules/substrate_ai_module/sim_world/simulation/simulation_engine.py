from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable, Mapping, Sequence

from .action_executor import ActionExecutor
from .action_validator import ActionValidator
from ..core.contracts import TransitionProposal, freeze_value
from .scheduler import ActionScheduler
from .simulation_context import ActionRequest, PhaseDiagnostics, ScheduledAction, SimulationContext, SimulationDiagnostics
from .world_rules import WorldRules


@dataclass(frozen=True, slots=True)
class SimulationResult:
    proposals: tuple[TransitionProposal, ...]
    diagnostics: SimulationDiagnostics


DomainHook = Callable[["SimulationEngine", SimulationContext], tuple[TransitionProposal, ...]]


@dataclass
class SimulationEngine:
    action_validator: ActionValidator = field(default_factory=ActionValidator)
    action_executor: ActionExecutor = field(default_factory=ActionExecutor)
    scheduler: ActionScheduler = field(default_factory=ActionScheduler)
    world_rules: WorldRules = field(default_factory=WorldRules)
    last_diagnostics: SimulationDiagnostics | None = field(default=None, init=False, repr=False)
    domain_hooks: dict[str, DomainHook] = field(default_factory=dict)

    def advance(
        self,
        context: SimulationContext,
        *,
        transition_proposals: Sequence[TransitionProposal] | None = None,
        scheduled_actions: Sequence[ActionRequest | ScheduledAction | TransitionProposal] | None = None,
    ) -> SimulationResult:
        direct = tuple(context.transition_proposals if transition_proposals is None else transition_proposals)
        scheduled = tuple(context.scheduled_actions if scheduled_actions is None else scheduled_actions)
        due = self.scheduler.due_actions(context.tick_number)
        phase_reports: list[PhaseDiagnostics] = []
        proposals: list[TransitionProposal] = []
        rejected: list[Mapping[str, Any]] = []
        executed_ids: list[str] = []

        phase_reports.append(PhaseDiagnostics("environment", 0, metadata=self._phase_metadata(context, "environment")))
        phase_reports.append(PhaseDiagnostics("resources", 0, metadata=self._phase_metadata(context, "resources")))
        phase_reports.append(PhaseDiagnostics("entities", 0, metadata=self._phase_metadata(context, "entities")))
        phase_reports.append(PhaseDiagnostics("relationships", 0, metadata=self._phase_metadata(context, "relationships")))

        action_requests: list[tuple[ActionRequest, str | None]] = self._coerce_requests(scheduled)
        action_requests.extend((scheduled_action.request, scheduled_action.action_id) for scheduled_action in due)

        action_phase_proposals, action_rejections, executed = self._execute_actions(context, action_requests)
        proposals.extend(action_phase_proposals)
        rejected.extend(action_rejections)
        executed_ids.extend(executed)
        phase_reports.append(PhaseDiagnostics("scheduled_actions", len(action_phase_proposals), rejected_count=len(action_rejections)))

        domain_proposals = self._run_domain_hooks(context)
        proposals.extend(domain_proposals)
        phase_reports.append(PhaseDiagnostics("domains", len(domain_proposals), metadata=self._phase_metadata(context, "domains")))

        all_proposals = tuple((*direct, *proposals))
        resolved, conflict_violations = self._resolve_conflicts(all_proposals)
        rule_violations = self.world_rules.evaluate(context, resolved)
        diagnostics = SimulationDiagnostics(
            world_id=context.world_id,
            tick_id=context.tick_context.tick_id,
            tick_number=context.tick_number,
            committed_revision=context.committed_revision,
            phase_reports=tuple(phase_reports),
            executed_actions=tuple(executed_ids),
            rejected_actions=tuple(rejected),
            conflicts=tuple((*rule_violations, *conflict_violations)),
            metadata={"direct_proposals": len(direct), "scheduled_requests": len(action_requests)},
        )
        self.last_diagnostics = diagnostics
        return SimulationResult(proposals=resolved, diagnostics=diagnostics)

    def register_domain(self, name: str, hook: DomainHook) -> None:
        self.domain_hooks[str(name)] = hook

    def run_environment_update(self, context: SimulationContext) -> tuple[TransitionProposal, ...]:
        return ()

    def run_resource_update(self, context: SimulationContext) -> tuple[TransitionProposal, ...]:
        return ()

    def run_entity_update(self, context: SimulationContext) -> tuple[TransitionProposal, ...]:
        return ()

    def run_relationship_update(self, context: SimulationContext) -> tuple[TransitionProposal, ...]:
        return ()

    def run_scheduled_actions(
        self,
        context: SimulationContext,
        scheduled_actions: Sequence[ActionRequest | ScheduledAction | TransitionProposal],
    ) -> tuple[TransitionProposal, ...]:
        result = self.advance(context, scheduled_actions=scheduled_actions)
        return result.proposals

    def _run_domain_hooks(self, context: SimulationContext) -> tuple[TransitionProposal, ...]:
        proposals: list[TransitionProposal] = []
        for name, hook in sorted(self.domain_hooks.items()):
            proposals.extend(hook(self, context))
        return tuple(proposals)

    def _coerce_requests(
        self,
        scheduled: Sequence[ActionRequest | ScheduledAction | TransitionProposal],
    ) -> list[tuple[ActionRequest, str | None]]:
        requests: list[tuple[ActionRequest, str | None]] = []
        for item in scheduled:
            if isinstance(item, ActionRequest):
                requests.append((item, None))
            elif isinstance(item, ScheduledAction):
                requests.append((item.request, item.action_id))
            elif isinstance(item, TransitionProposal):
                continue
            else:
                payload = dict(item)  # type: ignore[arg-type]
                actor_id = payload.get("actor_id")
                action = payload.get("action")
                if actor_id is not None and action is not None:
                    requests.append(
                        (
                            ActionRequest(
                                actor_id=actor_id,
                                action=str(action),
                                target_id=payload.get("target_id"),
                                item_id=payload.get("item_id"),
                                destination_room=payload.get("destination_room"),
                                quantity=payload.get("quantity"),
                                parameters=dict(payload.get("parameters", {})),
                                priority=int(payload.get("priority", 0)),
                                correlation_id=str(payload.get("correlation_id", "")),
                                metadata=dict(payload.get("metadata", {})),
                            ),
                            None,
                        )
                    )
        return requests

    def _execute_actions(
        self,
        context: SimulationContext,
        requests: Sequence[tuple[ActionRequest, str | None]],
    ) -> tuple[list[TransitionProposal], list[Mapping[str, Any]], list[str]]:
        accepted: list[TransitionProposal] = []
        rejected: list[Mapping[str, Any]] = []
        executed: list[str] = []
        for request, scheduled_id in sorted(requests, key=lambda item: (item[0].priority, item[0].correlation_id, str(item[0].actor_id.value), item[0].action)):
            validation = self.action_validator.validate(request, context)
            if not validation.valid:
                rejected.append(
                    {
                        "action": request.action,
                        "actor_id": str(request.actor_id.value),
                        "failures": [
                            {"code": failure.code, "message": failure.message, "details": dict(failure.details)}
                            for failure in validation.failures
                        ],
                    }
                )
                continue
            proposals = self.action_executor.execute(validation, context)
            if not proposals:
                continue
            accepted.extend(proposals)
            executed.append(request.action)
            if scheduled_id is not None:
                self.scheduler.mark_executed(scheduled_id, tick_number=context.tick_number)
        return accepted, rejected, executed

    def _phase_metadata(self, context: SimulationContext, phase: str) -> Mapping[str, Any]:
        return freeze_value(
            {
                "phase": phase,
                "tick_number": context.tick_number,
                "entity_count": len(dict(context.world_state.get("entities", {}))),
            }
        )

    @staticmethod
    def _proposal_write_paths(proposal: TransitionProposal) -> set[tuple[str, ...]]:
        """Enumerate the leaf-most write paths a proposal will mutate.

        Conflict granularity is per (entity, component/sub-key / field) path,
        NOT per entity or per whole top-level key. This is what lets several
        writers of DIFFERENT slices of the same entity co-exist in one tick:
          * the needs-domain writes NeedsComponent (+ metadata.status) while a
            Walk/Talk/Sleep action writes TransformComponent/metadata of the
            SAME villager;
          * the agriculture domain advances growth for every field while a
            plant/harvest/water ACTION writes the single field it owns.
        Treating these atomically silently dropped entire proposals -> needs
        frozen at static equilibrium, or fields never planted -> starvation.
        """
        paths: set[tuple[str, ...]] = set()
        patch = dict(proposal.patch)
        entities = patch.get("entities", {})
        if isinstance(entities, Mapping):
            for eid, body in entities.items():
                if not isinstance(body, Mapping):
                    paths.add(("entities", str(eid)))
                    continue
                for key, value in body.items():
                    if key == "metadata" and isinstance(value, Mapping):
                        for subkey in value:
                            paths.add(("entities", str(eid), "metadata", str(subkey)))
                    elif key == "components" and isinstance(value, Mapping):
                        for comp in value:
                            paths.add(("entities", str(eid), "components", str(comp)))
                    elif isinstance(value, Mapping):
                        paths.add(("entities", str(eid), key))
                    else:
                        paths.add(("entities", str(eid), key))
        # non-entity top-level keys (time, weather, ...) are global single-writer,
        # EXCEPT agriculture.fields which is a per-field namespace.
        for key in patch:
            if key == "entities":
                continue
            value = patch.get(key)
            if key == "agriculture" and isinstance(value, Mapping) and isinstance(value.get("fields"), Mapping):
                for fid in value["fields"]:
                    paths.add(("agriculture", "fields", str(fid)))
            else:
                paths.add((key,))
        return paths

    @staticmethod
    def _is_status_path(path: tuple[str, ...]) -> bool:
        return (
            len(path) == 4
            and path[0] == "entities"
            and path[2] == "metadata"
            and path[3] == "status"
        )

    @staticmethod
    def _is_agri_field_path(path: tuple[str, ...]) -> bool:
        return (
            len(path) == 3
            and path[0] == "agriculture"
            and path[1] == "fields"
        )

    def _resolve_conflicts(
        self,
        proposals: tuple[TransitionProposal, ...],
    ) -> tuple[tuple[TransitionProposal, ...], tuple[Mapping[str, Any], ...]]:
        accepted: list[TransitionProposal] = []
        conflicts: list[Mapping[str, Any]] = []
        seen_paths: set[tuple[str, ...]] = set()
        for index, proposal in enumerate(proposals):
            write_paths = self._proposal_write_paths(proposal)
            colliding = write_paths & seen_paths
            if colliding:
                # (a) DOMAIN-status prevails: the needs-domain is the sole
                # authoritative writer of a villager's active status; actions
                # preserve a *stale copy* and must yield.
                if self._domain_status_prevails(proposal, colliding):
                    reduced_old: list[TransitionProposal] = []
                    changed = False
                    for acc in accepted:
                        acc_paths = self._proposal_write_paths(acc)
                        acc_status = {
                            p for p in acc_paths
                            if self._is_status_path(p) and p in colliding
                        }
                        if acc_status and not str(acc.subject).startswith("domain."):
                            stripped = self._strip_status(acc, acc_status)
                            if stripped is not None:
                                reduced_old.append(stripped)
                                changed = True
                                continue
                        reduced_old.append(acc)
                    if changed:
                        accepted = reduced_old
                        seen_paths = set()
                        for acc in accepted:
                            seen_paths.update(self._proposal_write_paths(acc))
                        accepted.append(proposal)
                        seen_paths.update(write_paths)
                        continue
                # (b) ACTION-field prevails: a plant/harvest/water action owns
                # the field it acts on; the domain's growth-write for that same
                # field this tick is a stale "before" value and must yield.
                agri_fields = {p for p in colliding if self._is_agri_field_path(p)}
                if agri_fields and not str(proposal.subject).startswith("domain."):
                    reduced_old = []
                    changed = False
                    affected = {p[2] for p in agri_fields}
                    for acc in accepted:
                        acc_paths = self._proposal_write_paths(acc)
                        acc_fields = {
                            p[2] for p in acc_paths
                            if self._is_agri_field_path(p) and p in colliding
                        }
                        if acc_fields and str(acc.subject).startswith("domain."):
                            stripped = self._strip_agri_fields(acc, acc_fields)
                            if stripped is not None:
                                reduced_old.append(stripped)
                                changed = True
                                continue
                        reduced_old.append(acc)
                    if changed:
                        accepted = reduced_old
                        seen_paths = set()
                        for acc in accepted:
                            seen_paths.update(self._proposal_write_paths(acc))
                        accepted.append(proposal)
                        seen_paths.update(write_paths)
                        continue
                # (c) MERGE non-colliding paths rather than dropping the whole
                # proposal (dropping froze needs -> static equilibrium).
                reduced = self._without_colliding_paths(proposal, colliding)
                if reduced is None:
                    conflicts.append(
                        {
                            "code": "conflict",
                            "message": "proposal conflicts with an earlier write",
                            "index": index,
                            "subject": proposal.subject,
                            "paths": sorted(map(".".join, colliding)),
                        }
                    )
                    continue
                accepted.append(reduced)
                seen_paths.update(self._proposal_write_paths(reduced))
                continue
            accepted.append(proposal)
            seen_paths.update(write_paths)
        return tuple(accepted), tuple(conflicts)

    def _domain_status_prevails(
        self,
        proposal: TransitionProposal,
        colliding: set[tuple[str, ...]],
    ) -> bool:
        """True if this proposal is a domain that authoritatively writes status
        and the collision includes status + this should win over earlier actions."""
        if not str(proposal.subject).startswith("domain."):
            return False
        return any(self._is_status_path(p) for p in write_paths_of(proposal)) and any(
            self._is_status_path(p) for p in colliding
        )

    @staticmethod
    def _strip_status(
        proposal: TransitionProposal,
        status_paths: set[tuple[str, ...]],
    ) -> TransitionProposal | None:
        """Return a copy with metadata.status sub-keys removed."""
        patch = dict(proposal.patch)
        entities = patch.get("entities")
        status_eids = {p[1] for p in status_paths if len(p) >= 2}
        if isinstance(entities, Mapping):
            entities = dict(entities)
            for eid in status_eids:
                body = entities.get(str(eid))
                if not isinstance(body, Mapping):
                    continue
                body = dict(body)
                meta = body.get("metadata")
                if isinstance(meta, Mapping):
                    meta = dict(meta)
                    meta.pop("status", None)
                    if meta:
                        body["metadata"] = meta
                    else:
                        body.pop("metadata", None)
                entities[str(eid)] = body if body else None
            entities = {e: b for e, b in entities.items() if b is not None}
            patch["entities"] = entities
        if not patch.get("entities"):
            return None
        return TransitionProposal(
            world_id=proposal.world_id,
            tick_id=proposal.tick_id,
            state_revision=proposal.state_revision,
            correlation_id=proposal.correlation_id,
            subject=proposal.subject,
            patch=patch,
            remove_paths=proposal.remove_paths,
            description=proposal.description,
            metadata=proposal.metadata,
        )

    @staticmethod
    def _strip_agri_fields(proposal: TransitionProposal, fields: set[str]) -> TransitionProposal | None:
        """Return a copy with the given field-ids removed from
        patch['agriculture']['fields']. Returns None if nothing remains."""
        patch = dict(proposal.patch)
        agri = patch.get("agriculture")
        if not isinstance(agri, Mapping):
            return proposal
        agri = dict(agri)
        fields_map = agri.get("fields")
        if not isinstance(fields_map, Mapping):
            return proposal
        kept = {fid: fv for fid, fv in fields_map.items() if str(fid) not in fields}
        if not kept:
            return None
        agri["fields"] = kept
        patch["agriculture"] = agri
        return TransitionProposal(
            world_id=proposal.world_id,
            tick_id=proposal.tick_id,
            state_revision=proposal.state_revision,
            correlation_id=proposal.correlation_id,
            subject=proposal.subject,
            patch=patch,
            remove_paths=proposal.remove_paths,
            description=proposal.description,
            metadata=proposal.metadata,
        )

    @staticmethod
    def _without_colliding_paths(
        proposal: TransitionProposal,
        colliding_paths: set[tuple[str, ...]],
    ) -> TransitionProposal | None:
        """Return a copy with colliding entity sub-keys removed.

        Colliding metadata paths are ("entities", eid, "metadata", subkey);
        colliding component paths are ("entities", eid, key); agriculture
        fields collide at ("agriculture","fields",fid). Non-entity top-level
        keys (time, weather...) are dropped only if they collide. Returns None
        if nothing remains to write.
        """
        def collides(eid: str, key: str, subkey: str | None = None) -> bool:
            base = ("entities", eid, key)
            if subkey is not None:
                return (*base, subkey) in colliding_paths
            return base in colliding_paths

        patch = dict(proposal.patch)
        entities = patch.get("entities")
        new_entities: dict[str, Any] = {}
        if isinstance(entities, Mapping):
            for eid, body in entities.items():
                eid = str(eid)
                kept_body: dict[str, Any] = {}
                if isinstance(body, Mapping):
                    for key, value in body.items():
                        if key == "metadata" and isinstance(value, Mapping):
                            kept_meta: dict[str, Any] = {}
                            for subkey, subval in value.items():
                                if not collides(eid, key, subkey):
                                    kept_meta[str(subkey)] = subval
                            if kept_meta:
                                kept_body["metadata"] = kept_meta
                        elif key == "components" and isinstance(value, Mapping):
                            kept_comps: dict[str, Any] = {}
                            for comp, compval in value.items():
                                if not collides(eid, "components", comp):
                                    kept_comps[str(comp)] = compval
                            if kept_comps:
                                kept_body["components"] = kept_comps
                        elif isinstance(value, Mapping):
                            if not collides(eid, key):
                                kept_body[key] = value
                        else:
                            if not collides(eid, key):
                                kept_body[key] = value
                else:
                    if ("entities", eid, "@value") not in colliding_paths:
                        kept_body = body  # type: ignore[assignment]
                if kept_body:
                    new_entities[eid] = kept_body

        new_patch: dict[str, Any] = {}
        for key, value in patch.items():
            if key == "entities":
                if new_entities:
                    new_patch["entities"] = new_entities
            elif key == "agriculture" and isinstance(value, Mapping) and isinstance(value.get("fields"), Mapping):
                # per-field: keep only non-colliding fields
                colliding_fids = {p[2] for p in colliding_paths if self_is_agri(p)}
                kept_fields = {fid: fv for fid, fv in value["fields"].items() if str(fid) not in colliding_fids}
                if kept_fields:
                    new_patch["agriculture"] = {**value, "fields": kept_fields}
            elif (key,) not in colliding_paths:
                new_patch[key] = value

        if not new_patch:
            return None
        return TransitionProposal(
            world_id=proposal.world_id,
            tick_id=proposal.tick_id,
            state_revision=proposal.state_revision,
            correlation_id=proposal.correlation_id,
            subject=proposal.subject,
            patch=new_patch,
            remove_paths=proposal.remove_paths,
            description=proposal.description,
            metadata=proposal.metadata,
        )


_CACHE_GLOBALS = None
def write_paths_of(proposal) -> set[tuple[str, ...]]:
    """Collect write paths of a proposal, descending into metadata/components."""
    global _CACHE_GLOBALS
    if _CACHE_GLOBALS is None:
        _CACHE_GLOBALS = SimulationEngine._proposal_write_paths
    return set(_CACHE_GLOBALS(proposal))


def self_is_agri(p: tuple[str, ...]) -> bool:
    return len(p) == 3 and p[0] == "agriculture" and p[1] == "fields"
