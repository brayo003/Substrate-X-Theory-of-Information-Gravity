from __future__ import annotations

from dataclasses import dataclass, field, replace
from datetime import datetime, timezone
from typing import TYPE_CHECKING, Any, Iterable, Mapping, Sequence

if TYPE_CHECKING:
    from ..reasoning.reasoning_coordinator import ReasoningCoordinator

from ..core.config import KernelConfig
from ..core.contracts import RenderSnapshot, TickContext, TransitionProposal, freeze_value
from ..core.contracts import GovernanceDecision
from ..core.errors import ConflictError, RollbackError, ValidationError, VerificationError
from ..core.events import StateEvent
from ..core.ids import EntityId, RevisionId, SnapshotId, TickId, WorldId
from ..planner.planner import PlanProposal, PlannerContext, PlannerEngine, ScheduledPlan
from ..planner.planner_context import Goal
from ..renderer.renderer_context import RendererContext
from ..renderer.renderer_engine import RendererEngine
from ..renderer.render_result import RenderResult
from ..renderer.render_profiles import RenderProfile
from ..core.contracts import VerificationReport
from ..governor.governor_context import GovernorContext
from ..governor.governor_engine import GovernorEngine
from ..transport.transport import QObservation, TransportContext, TransportEngine
from ..domains.physical_field.physical_field_models import SpectralTransportObservable
from ..verifier.verifier_context import VerifierContext
from ..verifier.verifier_engine import VerifierEngine
from ..simulation.simulation_context import SimulationContext, SimulationDiagnostics
from ..simulation.simulation_engine import SimulationEngine
from ..core.revision import Revision
from ..core.snapshot import SnapshotService
from ..entities.registry import EntityRegistry
from ..core.storage import InMemoryStorage
from ..memory.world_memory import WorldMemory
from ..core.tick import TickClock


@dataclass(frozen=True, slots=True)
class ValidationOutcome:
    valid: bool
    reason: str
    normalized: TransitionProposal


@dataclass
class CycleResult:
    revision: Revision
    plans: tuple[PlanProposal, ...]
    verification_report: VerificationReport | None
    governance_decision: GovernanceDecision | None
    render_result: RenderResult | None


@dataclass
class WorldKernel:
    config: KernelConfig = field(default_factory=KernelConfig)
    storage: InMemoryStorage = field(default_factory=InMemoryStorage)
    entity_registry: EntityRegistry = field(init=False, repr=False)
    world_memory: WorldMemory = field(init=False, repr=False)
    simulation_engine: SimulationEngine = field(init=False, repr=False)
    planner_engine: PlannerEngine = field(init=False, repr=False)
    transport_engine: TransportEngine = field(init=False, repr=False)
    renderer_engine: RendererEngine = field(init=False, repr=False)
    verifier_engine: VerifierEngine = field(init=False, repr=False)
    governor_engine: GovernorEngine = field(init=False, repr=False)
    reasoning_coordinator: "ReasoningCoordinator" = field(init=False, repr=False)
    _state: dict[str, Any] = field(init=False, repr=False)
    _current_revision: Revision | None = field(default=None, init=False, repr=False)
    _snapshot_service: SnapshotService = field(default_factory=SnapshotService, init=False, repr=False)
    _clock: TickClock = field(init=False, repr=False)
    _last_simulation_diagnostics: SimulationDiagnostics | None = field(default=None, init=False, repr=False)
    _last_planning_diagnostics: Any = field(default=None, init=False, repr=False)
    _last_transport_observation: QObservation | None = field(default=None, init=False, repr=False)
    _last_spectral_transport_observable: SpectralTransportObservable | None = field(default=None, init=False, repr=False)
    _last_render_result: RenderResult | None = field(default=None, init=False, repr=False)
    _last_verification_report: VerificationReport | None = field(default=None, init=False, repr=False)
    _last_governance_decision: GovernanceDecision | None = field(default=None, init=False, repr=False)

    def __post_init__(self) -> None:
        self.world_memory = WorldMemory(self.config.world_id, storage=self.storage, initial_state=self.config.initial_state)
        self.entity_registry = EntityRegistry(self.config.world_id)
        self.entity_registry.bind_world_memory(self.world_memory)
        self.entity_registry.bind_change_listener(self._sync_entity_state)
        self.simulation_engine = SimulationEngine()
        self.planner_engine = PlannerEngine(self.config.world_id)
        self.transport_engine = TransportEngine()
        self.renderer_engine = RendererEngine()
        self.verifier_engine = VerifierEngine()
        self.governor_engine = GovernorEngine()
        # Lazy import to avoid circular dependency
        from ..reasoning.reasoning_coordinator import ReasoningCoordinator
        self.reasoning_coordinator = ReasoningCoordinator(self.config.world_id)
        self._state = dict(self.config.initial_state)
        self._sync_entity_state()
        self._clock = TickClock(self.config.world_id)
        
        # Per-world physical field state (for isolation between kernels)
        self._physical_field = None
        self._propagation_params = None
        self._relaxation_params = None
        self._reaction_params = None

    @property
    def world_id(self) -> WorldId:
        return self.config.world_id

    @property
    def state(self) -> Mapping[str, Any]:
        return freeze_value(dict(self._state))

    @property
    def current_state(self) -> Mapping[str, Any]:
        return freeze_value(dict(self._state))

    @property
    def current_revision(self) -> Revision | None:
        if self._current_revision is not None:
            return self._current_revision
        return self._genesis_revision()
    
    def initialize_physical_field(self, c_nominal: float = 1.0, tau_nominal: float = 1.0) -> None:
        """Initialize physical field state for this kernel instance.
        
        This creates per-world field state to ensure isolation between kernels.
        
        Args:
            c_nominal: Nominal propagation speed (m/s)
            tau_nominal: Nominal relaxation time (s)
        """
        from ..domains.physical_field.physical_field_models import (
            PropagationParameters,
            RelaxationParameters,
            NonlinearReactionParameters,
        )
        from ..domains.physical_field.physical_field_dynamics import initialize_field_state
        from ..domains.physical_field.physical_field_models import InformationDensityField
        
        # Initialize field state
        state = initialize_field_state(
            x_range=(0.0, 100.0),
            y_range=(0.0, 100.0),
            nx=50,
            ny=50,
            initial_value=1.0,
            dt=0.1,
        )
        
        # Calculate physical volume
        physical_volume = 100.0 * 100.0 * 1.0
        
        # Create information density field
        self._physical_field = InformationDensityField(
            state=state,
            information_quantity=1.0,
            physical_volume=physical_volume,
            information_units="bits",
            spatial_units="m",
            density_units="bits/m³",
        )
        
        # Set parameters
        self._propagation_params = PropagationParameters(c_nominal=float(c_nominal))
        self._relaxation_params = RelaxationParameters(tau_nominal=float(tau_nominal))
        # Keep existing reaction params if already set, otherwise default to linear
        if self._reaction_params is None:
            self._reaction_params = NonlinearReactionParameters()
    
    def set_nonlinear_reaction_parameters(
        self,
        r: float = 0.0,
        a: float = 0.0,
        b: float = 0.0,
    ) -> None:
        """Set nonlinear reaction coefficients for this kernel's physical field.

        The active solver will use:
            τ ∂²s/∂t² + ∂s/∂t = c²τ ∇²s + r·s + a·s² − b·s³

        Setting r=a=b=0 (the defaults) restores the linear telegraph equation.

        Args:
            r: Linear reaction coefficient (s⁻¹).
            a: Quadratic coefficient. Must be ≥ 0.
            b: Cubic saturation coefficient. Must be ≥ 0.
        """
        from ..domains.physical_field.physical_field_models import NonlinearReactionParameters
        self._reaction_params = NonlinearReactionParameters(r=r, a=a, b=b)
    
    def set_field_parameters(self, c_nominal: float | None = None, tau_nominal: float | None = None) -> None:
        """Set field parameters for this kernel instance.
        
        Args:
            c_nominal: Nominal propagation speed (m/s). If None, current value is preserved.
            tau_nominal: Nominal relaxation time (s). If None, current value is preserved.
        """
        from ..domains.physical_field.physical_field_models import (
            PropagationParameters,
            RelaxationParameters,
        )
        
        if c_nominal is not None:
            self._propagation_params = PropagationParameters(c_nominal=float(c_nominal))
        
        if tau_nominal is not None:
            self._relaxation_params = RelaxationParameters(tau_nominal=float(tau_nominal))

    @property
    def latest_revision(self) -> Revision | None:
        return self.storage.latest_revision()

    @property
    def current_tick_number(self) -> int:
        return self._clock.tick_number

    @property
    def last_planning_diagnostics(self) -> Any:
        return self._last_planning_diagnostics

    @property
    def last_transport_observation(self) -> QObservation | None:
        return self._last_transport_observation

    @property
    def last_spectral_transport_observable(self) -> SpectralTransportObservable | None:
        return self._last_spectral_transport_observable

    @property
    def transport_history(self) -> tuple[QObservation, ...]:
        return self.transport_engine.history()

    @property
    def last_render_result(self) -> RenderResult | None:
        return self._last_render_result

    @property
    def render_history(self) -> tuple[RenderResult, ...]:
        return self.renderer_engine.history()

    @property
    def last_verification_report(self) -> VerificationReport | None:
        return self._last_verification_report

    @property
    def verification_history(self) -> tuple[VerificationReport, ...]:
        return self.verifier_engine.history()

    @property
    def last_governance_decision(self) -> GovernanceDecision | None:
        return self._last_governance_decision

    @property
    def governance_history(self) -> tuple[Any, ...]:
        return self.governor_engine.history()

    def validate_action(self, action: TransitionProposal | Mapping[str, Any]) -> ValidationOutcome:
        proposal = self._coerce_transition(action)
        if proposal.world_id != self.world_id:
            return ValidationOutcome(False, "world_id mismatch", proposal)
        if not proposal.subject:
            return ValidationOutcome(False, "subject is required", proposal)
        if not proposal.patch and not proposal.remove_paths:
            return ValidationOutcome(False, "transition must contain a patch or removal path", proposal)
        if self._current_revision is None:
            if proposal.state_revision is not None:
                return ValidationOutcome(False, "state_revision mismatch", proposal)
        elif proposal.state_revision is not None and proposal.state_revision != self._current_revision.revision_id:
            return ValidationOutcome(False, "state_revision mismatch", proposal)
        normalized = replace(
            proposal,
            world_id=self.world_id,
            state_revision=self._current_revision.revision_id if self._current_revision else None,
        )
        return ValidationOutcome(True, "validated", normalized)

    def commit_state(
        self,
        tick_context: TickContext,
        transition_proposals: Sequence[TransitionProposal] | None = None,
        metadata: Mapping[str, Any] | None = None,
    ) -> Revision:
        previous_snapshot = self.create_snapshot()
        proposals = tuple(transition_proposals or ())
        normalized: list[TransitionProposal] = []

        for proposal in proposals:
            if proposal.world_id != self.config.world_id:
                print("=" * 80)
                print("WORLD ID MISMATCH")
                print("Kernel   :", self.config.world_id)
                print("Proposal :", proposal.world_id)
                print("Metadata :", dict(proposal.metadata))
                print("Patch keys:", proposal.patch.keys())
                raise AssertionError("world_id mismatch")

            outcome = self.validate_action(proposal)
            if not outcome.valid:
                raise ValidationError(outcome.reason)

            normalized.append(outcome.normalized)

        next_state = dict(self.current_state)
        events: list[StateEvent] = []
        for index, proposal in enumerate(normalized):
            event = self._event_from_proposal(
                proposal,
                world_id=self.world_id,
                revision_id=None,
                tick_id=tick_context.tick_id,
                state_before=next_state,
                index=index,
                metadata=metadata,
            )
            next_state = event.apply_to(next_state)
            events.append(event)

        revision_sequence = self._clock.tick_number if self._clock.tick_number else len(self.storage.list_history()) + 1
        revision = Revision(
            world_id=self.world_id,
            revision_id=RevisionId.new(
                self.world_id,
                tick_context.tick_id,
                revision_sequence,
                {"events": [str(event.event_id.value) for event in events], "state_hash": repr(freeze_value(next_state))},
            ),
            tick_id=tick_context.tick_id,
            timestamp=tick_context.timestamp,
            parent_revision=None if self._current_revision is None or self._is_genesis_revision(self._current_revision) else self._current_revision.revision_id,
            events=tuple(events),
            state=next_state,
            metadata={} if metadata is None else dict(metadata),
        )
        self._state = next_state
        self._current_revision = self.world_memory.record_revision(
            revision,
            entity_refs=self.entity_registry.agent_memory_references(),
        )
        
        # PROJECTION STAGE: Merge domain-specific transaction buffers into canonical entities
        self._project_domain_namespaces_into_entities()
        
        # Extract spectral transport observable from physical field domain
        self._extract_spectral_transport_observable(next_state)
        
        # Transport observation - Q as causal component (state-transition analysis)
        try:
            self._publish_transport_observation(
                previous_snapshot=previous_snapshot,
                current_snapshot=self.create_snapshot(),
                previous_revision=revision.parent_revision,
                current_revision=revision.revision_id,
                tick_number=tick_context.tick_id,
                transition_proposals=normalized,
                correlation_id=tick_context.correlation_id,
                representation_type="committed_transition",
            )
        except Exception as e:
            # Transport observation failure should not prevent simulation tick completion
            import traceback
            print(f"Transport observation failed (non-critical): {e}")
            traceback.print_exc()
        
        # FIELD STATE UPDATE STAGE: Update kernel's field state from domain proposals
        # This ensures per-world field state isolation is maintained
        try:
            for proposal in normalized:
                if proposal.subject == "domain.physical_field":
                    proposal_patch = dict(proposal.patch)
                    propagation_params = proposal_patch.get("propagation_parameters", {})
                    relaxation_params = proposal_patch.get("relaxation_parameters", {})
                    
                    # Update kernel's field parameters from domain evolution
                    from ..domains.physical_field.physical_field_models import (
                        PropagationParameters,
                        RelaxationParameters,
                    )
                    
                    if propagation_params:
                        self._propagation_params = PropagationParameters(
                            c_nominal=float(propagation_params.get("c_nominal", 1.0)),
                            c_measured=float(propagation_params.get("c_measured", 0.0)),
                            c_uncertainty=float(propagation_params.get("c_uncertainty", 0.0)),
                        )
                    
                    if relaxation_params:
                        self._relaxation_params = RelaxationParameters(
                            tau_nominal=float(relaxation_params.get("tau_nominal", 1.0)),
                            tau_measured=float(relaxation_params.get("tau_measured", 0.0)),
                            tau_uncertainty=float(relaxation_params.get("tau_uncertainty", 0.0)),
                            relaxation_law=relaxation_params.get("relaxation_law", "exponential"),
                        )
        except Exception as field_update_error:
            # Field state update failure should not prevent simulation tick completion
            import traceback
            print(f"Field state update failed (non-critical): {field_update_error}")
            traceback.print_exc()
        
        # MEMORY WRITE STAGE: Write action outcomes to agent memory
        # This closes the memory loop - agents can now learn from past actions
        try:
            for proposal in normalized:
                # Extract entity IDs from the proposal patch
                proposal_patch = dict(proposal.patch)
                entities_patch = proposal_patch.get("entities", {})
                
                if not entities_patch:
                    continue
                
                # Write memory for each affected entity
                for entity_id_str, entity_patch in entities_patch.items():
                    try:
                        entity_id = EntityId.from_uuid(entity_id_str)
                        memory = self.entity_registry.agent_memories.get(entity_id)
                        
                        if memory:
                            memory.remember(
                                kind="action_outcome",
                                content={
                                    "action": proposal.subject,
                                    "state_change": entity_patch,
                                    "tick_id": str(tick_context.tick_id),
                                    "revision_id": str(revision.revision_id),
                                },
                                tick_id=tick_context.tick_id,
                                revision_id=revision.revision_id,
                                tags=("tick_context", "state_change"),
                            )
                    except Exception as entity_memory_error:
                        # Memory write failure for a single entity should not block the tick
                        print(f"Memory write failed for entity {entity_id_str}: {entity_memory_error}")
        except Exception as memory_error:
            # Memory system failure should not prevent simulation tick completion
            import traceback
            print(f"Memory write stage failed (non-critical): {memory_error}")
            traceback.print_exc()
        
        return revision

    def _genesis_revision(self) -> Revision:
        tick_id = TickId.new(self.world_id, 0)
        revision_id = RevisionId.new(self.world_id, tick_id, 0, {"genesis": True})
        return Revision(
            world_id=self.world_id,
            revision_id=revision_id,
            tick_id=None,
            timestamp=datetime(2000, 1, 1, tzinfo=timezone.utc),
            parent_revision=None,
            events=(),
            state=self.current_state,
            metadata={"genesis": True},
        )

    @staticmethod
    def _is_genesis_revision(revision: Revision | None) -> bool:
        return bool(revision is not None and dict(revision.metadata).get("genesis"))

    def advance_tick(
        self,
        transition_proposals: Sequence[TransitionProposal] | None = None,
        *,
        metadata: Mapping[str, Any] | None = None,
        correlation_id: str | None = None,
    ) -> Revision:
        tick_context = self._clock.create_context(
            state_revision=self._current_revision.revision_id if self._current_revision else None,
            parent_revision=self._current_revision.revision_id if self._current_revision else None,
            correlation_id=correlation_id,
            metadata=metadata,
        )
        simulation_context = SimulationContext(
            world_id=self.world_id,
            tick_context=tick_context,
            tick_number=self._clock.tick_number,
            world_state=self.current_state,
            committed_revision=self._current_revision.revision_id if self._current_revision else None,
            transition_proposals=tuple(transition_proposals or ()),
            scheduled_actions=(),
            metadata={} if metadata is None else dict(metadata),
            physical_field_state={
                "physical_field": self._physical_field,
                "propagation_params": self._propagation_params,
                "relaxation_params": self._relaxation_params,
                "reaction_params": self._reaction_params,
            },
        )
        simulation_result = self.simulation_engine.advance(
            simulation_context,
            transition_proposals=transition_proposals,
            scheduled_actions=(),
        )
        self._last_simulation_diagnostics = simulation_result.diagnostics
        return self.commit_state(tick_context, transition_proposals=simulation_result.proposals, metadata=metadata)

    def execute_cycle(
        self,
        *,
        goals: Sequence[Goal] | None = None,
        metadata: Mapping[str, Any] | None = None,
        correlation_id: str | None = None,
    ) -> CycleResult:
        """Execute one complete simulation cycle: plan → schedule → simulate → render → verify → govern."""
        # Stage 1: Goal generation and planning
        plans = self.plan(goals=goals)
        
        # Stage 2: Plan scheduling
        if plans:
            self.schedule_plans(plans)
        
        # Stage 3: Simulation and state commit
        revision = self.advance_tick(transition_proposals=None, metadata=metadata, correlation_id=correlation_id)
        
        # Stage 4: Rendering (must happen before verification)
        render_result = self.render()
        
        # Stage 5: Verification (requires render result)
        verification_report = self.verify()
        
        # Stage 6: Governance (uses all diagnostics)
        governance_decision = self.govern()
        
        return CycleResult(
            revision=revision,
            plans=tuple(plans),
            verification_report=verification_report,
            governance_decision=governance_decision,
            render_result=render_result,
        )

    def create_snapshot(self) -> RenderSnapshot:
        if self._current_revision is None:
            synthetic_tick = TickId.new(self.world_id, 0)
            synthetic_revision = RevisionId.new(self.world_id, synthetic_tick, 0, {"snapshot": "initial"})
            return self._snapshot_service.create_from_state(
                world_id=self.world_id,
                tick_id=synthetic_tick,
                state_revision=synthetic_revision,
                parent_revision=None,
                state=self.current_state,
                events=(),
                metadata={
                    "state_hash": repr(freeze_value(dict(self.current_state))),
                    "memory_refs": self.world_memory.snapshot_references(),
                },
            )
        return self._snapshot_service.create_from_state(
            world_id=self.world_id,
            tick_id=self._current_revision.tick_id,
            state_revision=self._current_revision.revision_id,
            parent_revision=self._current_revision.parent_revision,
            state=self.current_state,
            events=self._current_revision.events,
            metadata={
                "state_hash": self._current_revision.state_hash,
                "memory_refs": self.world_memory.snapshot_references(),
            },
        )

    def planner_context(
        self,
        *,
        goals: Sequence[Goal] | None = None,
        metadata: Mapping[str, Any] | None = None,
    ) -> PlannerContext:
        snapshot = self.create_snapshot()
        return PlannerContext(
            world_id=self.world_id,
            snapshot=snapshot,
            current_tick=TickId.new(self.world_id, self.current_tick_number),
            current_tick_number=self.current_tick_number,
            committed_revision=self._current_revision.revision_id if self._current_revision else None,
            entity_registry=self.entity_registry,
            world_memory=self.world_memory,
            outstanding_goals=tuple(goals or self.planner_engine.goal_manager.outstanding()),
            scheduled_plans=self.planner_engine.plan_scheduler.list(),
            spectral_observable=self._last_spectral_transport_observable,
            metadata={} if metadata is None else dict(metadata),
        )

    def plan(self, goals: Sequence[Goal] | None = None) -> tuple[PlanProposal, ...]:
        effective_goals: Sequence[Goal] | None = goals
        if effective_goals is None:
            generated_goals = list(self.planner_engine.goal_manager.outstanding())
            
            # LLM-based goal generation
            try:
                llm_goals = self._generate_llm_goals()
                print(f"[LLM_GOALS] Generated {len(llm_goals)} LLM goals")
                for goal in llm_goals:
                    print(f"[LLM_GOALS] Submitting goal: {goal.goal_id}, kind={goal.kind}, subject={goal.subject}")
                    self.planner_engine.goal_manager.submit_goal(goal)
                    generated_goals.append(goal)
            except Exception as e:
                # LLM generation failure should not block planning
                print(f"LLM goal generation failed: {e}")
            
            # Existing rule-based goal generation
            try:
                from ..domains.needs import generate_needs_driven_goals

                generated_goals.extend(generate_needs_driven_goals(self))
            except Exception:
                pass
            try:
                # generate_population_driven_goals is the real goal generator
                # (generate_daily_life_goals was renamed and no longer exists;
                # stale callers silently swallowed population movement goals).
                from ..domains.population import generate_population_driven_goals

                generated_goals.extend(generate_population_driven_goals(self))
            except Exception:
                pass
            # Emergent-production goal generators. Without these the sim can
            # only spend starting resources: once a villager eats/drinks their
            # fixed food/water they starve and the world degrades to static
            # equilibrium (the "finite resources" freeze). Wiring the domain
            # generators lets farmers plant/water/harvest and workshops/economy
            # produce/trade so food & water become self-sustaining and needs
            # keep firing forever.
            try:
                from ..domains.agriculture import generate_agriculture_goals
                generated_goals.extend(generate_agriculture_goals(self))
            except Exception:
                pass
            try:
                from ..domains.economy import generate_economy_goals
                generated_goals.extend(generate_economy_goals(self))
            except Exception:
                pass
            effective_goals = tuple(generated_goals)
        context = self.planner_context(goals=effective_goals)
        plans = self.planner_engine.plan(context, goals=effective_goals)
        self._last_planning_diagnostics = self.planner_engine.last_diagnostics
        return plans

    def _generate_llm_goals(self) -> tuple[Goal, ...]:
        """
        Generate goals using LLM reasoning.
        
        This method coordinates LLM-based intention generation and translation
        into Goal objects. The Planner remains authoritative - these goals
        must pass through the normal planning pipeline.
        
        Returns:
            Tuple of Goals generated from LLM intentions
        """
        # Check if LLM generation is enabled
        if not self.config.enable_llm_generation:
            return ()
        
        # Get all human entities
        human_entities = self.entity_registry.find_by_type("human")
        
        if not human_entities:
            return ()
        
        # Build entity data mapping
        entity_data_map = {}
        agent_memory_map = {}
        
        for entity in human_entities:
            entity_data_map[entity.entity_id] = entity.serialize()
            agent_memory_map[entity.entity_id] = self.entity_registry.agent_memories.get(entity.entity_id)
        
        # Generate intentions using reasoning coordinator
        llm_goals = self.reasoning_coordinator.generate_intents_for_tick(
            entities=entity_data_map,
            world_state=self.current_state,
            agent_memories=agent_memory_map,
            transport_observation=self._last_transport_observation,
            spectral_observable=self._last_spectral_transport_observable,
            current_tick=self.current_tick_number,
            current_revision=self._current_revision.revision_id if self._current_revision else None,
        )
        
        return llm_goals
    
    def renderer_context(
        self,
        *,
        render_profile: RenderProfile | str | None = None,
        renderer_type: str | None = None,
        requested_output: str = "",
        configuration: Mapping[str, Any] | None = None,
        user_parameters: Mapping[str, Any] | None = None,
        metadata: Mapping[str, Any] | None = None,
        snapshot: RenderSnapshot | None = None,
    ) -> RendererContext:
        return RendererContext(
            world_id=self.world_id,
            snapshot=self.create_snapshot() if snapshot is None else snapshot,
            render_profile=render_profile,
            renderer_type=renderer_type,
            requested_output=requested_output,
            configuration={} if configuration is None else dict(configuration),
            user_parameters={} if user_parameters is None else dict(user_parameters),
            correlation_id=str(self.current_revision.revision_id if self.current_revision else self.world_id.value),
            metadata={} if metadata is None else dict(metadata),
        )

    def render(
        self,
        *,
        render_profile: RenderProfile | str | None = None,
        renderer_type: str | None = None,
        requested_output: str = "",
        configuration: Mapping[str, Any] | None = None,
        user_parameters: Mapping[str, Any] | None = None,
        metadata: Mapping[str, Any] | None = None,
        snapshot: RenderSnapshot | None = None,
    ) -> RenderResult:
        context = self.renderer_context(
            render_profile=render_profile,
            renderer_type=renderer_type,
            requested_output=requested_output,
            configuration=configuration,
            user_parameters=user_parameters,
            metadata=metadata,
            snapshot=snapshot,
        )
        result = self.renderer_engine.render(context)
        self._last_render_result = result
        return result

    def verifier_context(
        self,
        *,
        render_output: Any | None = None,
        render_result: RenderResult | None = None,
        render_proposal: Any | None = None,
        target_snapshot: RenderSnapshot | None = None,
        render_profile: Any = None,
        renderer_type: str = "",
        asset_versions: Mapping[str, Any] | None = None,
        sensor_scope: Mapping[str, Any] | None = None,
        extraction_hints: Mapping[str, Any] | None = None,
        configuration: Mapping[str, Any] | None = None,
        correlation_id: str | None = None,
        metadata: Mapping[str, Any] | None = None,
    ) -> VerifierContext:
        snapshot = self.create_snapshot() if target_snapshot is None else target_snapshot
        output = render_output
        if output is None and render_result is not None:
            output = render_result
        if output is None and render_proposal is not None:
            output = render_proposal
        if output is None:
            output = self.last_render_result
        if output is None:
            raise VerificationError("verification requires a render output, render result, or prior render result")
        effective_render_result = render_result if render_result is not None else (output if isinstance(output, RenderResult) else self.last_render_result)
        effective_render_profile = render_profile
        if effective_render_profile is None and effective_render_result is not None:
            effective_render_profile = effective_render_result.profile
        effective_renderer_type = renderer_type
        if not effective_renderer_type and effective_render_result is not None:
            effective_renderer_type = effective_render_result.renderer_type
        return VerifierContext(
            world_id=self.world_id,
            target_snapshot=snapshot,
            render_output=output,
            renderer_type=effective_renderer_type,
            render_profile=effective_render_profile,
            asset_versions={} if asset_versions is None else dict(asset_versions),
            sensor_scope={} if sensor_scope is None else dict(sensor_scope),
            extraction_hints={} if extraction_hints is None else dict(extraction_hints),
            configuration={} if configuration is None else dict(configuration),
            correlation_id=str(correlation_id if correlation_id is not None else (self.current_revision.revision_id if self.current_revision else self.world_id.value)),
            metadata={} if metadata is None else dict(metadata),
            render_result=effective_render_result if isinstance(effective_render_result, RenderResult) else render_result,
            render_proposal=render_proposal,
            target_revision=snapshot.state_revision,
        )

    def verify(
        self,
        *,
        render_output: Any | None = None,
        render_result: RenderResult | None = None,
        render_proposal: Any | None = None,
        target_snapshot: RenderSnapshot | None = None,
        render_profile: Any = None,
        renderer_type: str = "",
        asset_versions: Mapping[str, Any] | None = None,
        sensor_scope: Mapping[str, Any] | None = None,
        extraction_hints: Mapping[str, Any] | None = None,
        configuration: Mapping[str, Any] | None = None,
        correlation_id: str | None = None,
        metadata: Mapping[str, Any] | None = None,
    ) -> VerificationReport:
        # If no render result provided, generate one using JSON renderer for verification
        # JSON renderer produces structurally compatible output with RenderSnapshot
        if render_result is None and render_output is None and render_proposal is None:
            render_result = self.render(renderer_type="json")
        
        context = self.verifier_context(
            render_output=render_output,
            render_result=render_result,
            render_proposal=render_proposal,
            target_snapshot=target_snapshot,
            render_profile=render_profile,
            renderer_type=renderer_type or (render_result.renderer_type if render_result else "json"),
            asset_versions=asset_versions,
            sensor_scope=sensor_scope,
            extraction_hints=extraction_hints,
            configuration=configuration,
            correlation_id=correlation_id,
            metadata=metadata,
        )
        report = self.verifier_engine.verify(context)
        self._last_verification_report = report
        return report

    def governor_context(
        self,
        *,
        simulation_diagnostics: SimulationDiagnostics | None = None,
        planner_diagnostics: Any = None,
        transport_observation: QObservation | None = None,
        verification_report: VerificationReport | None = None,
        renderer_report: RenderResult | None = None,
        kernel_status: Mapping[str, Any] | None = None,
        policy_version: str | None = None,
        correlation_id: str | None = None,
        metadata: Mapping[str, Any] | None = None,
    ) -> GovernorContext:
        revision = self._current_revision.revision_id if self._current_revision is not None else None
        tick_id = self._current_revision.tick_id if self._current_revision is not None else TickId.new(self.world_id, self.current_tick_number)
        status = {
            "revision": None if revision is None else str(revision.value),
            "tick_number": self.current_tick_number,
            "state_hash": repr(freeze_value(dict(self.current_state))),
            "checkpoint_revision": None,
        }
        if kernel_status is not None:
            status.update(dict(kernel_status))
        return GovernorContext(
            world_id=self.world_id,
            tick_id=tick_id,
            revision=revision,
            policy_version=policy_version or self.governor_engine.policy_version,
            simulation_diagnostics=self._last_simulation_diagnostics if simulation_diagnostics is None else simulation_diagnostics,
            planner_diagnostics=self._last_planning_diagnostics if planner_diagnostics is None else planner_diagnostics,
            transport_observation=self._last_transport_observation if transport_observation is None else transport_observation,
            verification_report=self._last_verification_report if verification_report is None else verification_report,
            renderer_report=self._last_render_result if renderer_report is None else renderer_report,
            kernel_status=status,
            correlation_id=str(correlation_id or (revision.value if revision is not None else self.world_id.value)),
            metadata={} if metadata is None else dict(metadata),
        )

    def govern(
        self,
        *,
        simulation_diagnostics: SimulationDiagnostics | None = None,
        planner_diagnostics: Any = None,
        transport_observation: QObservation | None = None,
        verification_report: VerificationReport | None = None,
        renderer_report: RenderResult | None = None,
        kernel_status: Mapping[str, Any] | None = None,
        policy_version: str | None = None,
        correlation_id: str | None = None,
        metadata: Mapping[str, Any] | None = None,
    ) -> GovernanceDecision:
        context = self.governor_context(
            simulation_diagnostics=simulation_diagnostics,
            planner_diagnostics=planner_diagnostics,
            transport_observation=transport_observation,
            verification_report=verification_report,
            renderer_report=renderer_report,
            kernel_status=kernel_status,
            policy_version=policy_version,
            correlation_id=correlation_id,
            metadata=metadata,
        )
        decision = self.governor_engine.evaluate(context)
        self._last_governance_decision = decision
        if decision.disposition == "ROLLBACK":
            status = dict(context.kernel_status)
            checkpoint = status.get("checkpoint_revision") or status.get("rollback_target_revision")
            checkpoint_revision = self._coerce_revision_id(checkpoint)
            if checkpoint_revision is not None:
                self.rollback(checkpoint_revision)
        return decision

    def schedule_plans(
        self,
        plans: Sequence[PlanProposal],
        *,
        execute_tick: int | None = None,
    ) -> tuple[Any, ...]:
        scheduled: list[Any] = []
        base_tick = self.current_tick_number + 1 if execute_tick is None else int(execute_tick)
        for plan in plans:
            plan_start = int(plan.metadata.get("estimated_start_tick", base_tick))
            plan_scheduled = self._scheduled_plan_for(plan.plan_id)
            if plan_scheduled is None:
                plan_scheduled = self.planner_engine.plan_scheduler.schedule_future(
                    plan,
                    execute_tick=plan_start,
                    tick_number=self.current_tick_number,
                )
            self.planner_engine.goal_manager.mark_from_state(plan.goal_id, "active", tick=self.current_tick_number, reason="plan scheduled")
            for offset, request in enumerate(plan.action_requests):
                scheduled.append(
                    self.simulation_engine.scheduler.schedule_future_tick(
                        request,
                        execute_tick=plan_start + offset,
                        tick_number=self.current_tick_number,
                        metadata={
                            "plan_id": plan.plan_id,
                            "goal_id": plan.goal_id,
                            "scheduled_plan_id": plan_scheduled.scheduled_plan_id,
                            "step_index": offset,
                        },
                    )
                )
        # Cleanup old completed plans to prevent memory explosion
        removed_plans = self.planner_engine.plan_scheduler.cleanup(current_tick=self.current_tick_number)
        removed_goals = self.planner_engine.goal_manager.cleanup(current_tick=self.current_tick_number)
        # Silently cleanup - don't print to reduce noise
        return tuple(scheduled)

    def rollback(self, revision_id: RevisionId) -> Revision:
        if not self.config.allow_rollback:
            raise RollbackError("rollback is disabled by configuration")
        target = self.storage.load_revision(revision_id)
        if self._current_revision is not None and target.revision_id == self._current_revision.revision_id:
            return self._current_revision
        previous_snapshot = self.create_snapshot()
        previous_revision = self._current_revision
        tick_context = self._clock.create_context(
            state_revision=target.revision_id,
            parent_revision=previous_revision.revision_id if previous_revision else None,
            correlation_id=f"rollback:{target.revision_id}",
            metadata={"rollback_to": str(target.revision_id)},
        )
        rollback_event = StateEvent.from_transition(
            world_id=self.world_id,
            revision_id=None,
            tick_id=tick_context.tick_id,
            subject="rollback",
            patch=target.state,
            remove_paths=(),
            state_before=self.current_state,
            index=0,
            metadata={"rollback_to": str(target.revision_id)},
        )
        revision_sequence = self._clock.tick_number if self._clock.tick_number else len(self.storage.list_history()) + 1
        revision = Revision(
            world_id=self.world_id,
            revision_id=RevisionId.new(self.world_id, tick_context.tick_id, revision_sequence, {"rollback_to": str(target.revision_id)}),
            tick_id=tick_context.tick_id,
            timestamp=datetime.now(timezone.utc),
            parent_revision=self._current_revision.revision_id if self._current_revision else None,
            events=(rollback_event,),
            state=dict(target.state),
            metadata={"rollback_to": str(target.revision_id)},
        )
        self._state = dict(target.state)
        self._restore_entity_state(target.state.get("entities", {}))
        self._state = dict(target.state)
        self._current_revision = self.world_memory.record_revision(
            revision,
            entity_refs=self.entity_registry.agent_memory_references(),
        )
        self.world_memory.rollback_reference(
            target.revision_id,
            from_revision_id=previous_revision.revision_id if previous_revision else None,
            reason="rollback",
        )
        self._publish_transport_observation(
            previous_snapshot=previous_snapshot,
            current_snapshot=self.create_snapshot(),
            previous_revision=previous_revision.revision_id if previous_revision else None,
            current_revision=revision.revision_id,
            tick_number=tick_context.tick_id,
            transition_proposals=(),
            correlation_id=tick_context.correlation_id,
            representation_type="rollback_transition",
        )
        return revision

    def replay_history(self, upto_revision_id: RevisionId | None = None) -> dict[str, Any]:
        state = dict(self.config.initial_state)
        for revision in self.storage.list_history():
            state = revision.replay(state)
            if upto_revision_id is not None and revision.revision_id == upto_revision_id:
                break
        return state

    def _coerce_transition(self, action: TransitionProposal | Mapping[str, Any]) -> TransitionProposal:
        if isinstance(action, TransitionProposal):
            return action
        return TransitionProposal(
            world_id=action.get("world_id", self.world_id),
            tick_id=action.get("tick_id"),
            state_revision=action.get("state_revision"),
            correlation_id=str(action.get("correlation_id", "")),
            subject=str(action.get("subject", "")),
            patch=dict(action.get("patch", {})),
            remove_paths=tuple(tuple(path) for path in action.get("remove_paths", ())),
            description=str(action.get("description", "")),
            metadata=dict(action.get("metadata", {})),
        )

    def _event_from_proposal(
        self,
        proposal: TransitionProposal,
        *,
        world_id: WorldId,
        revision_id: RevisionId | None,
        tick_id: TickId | None,
        state_before: Mapping[str, Any],
        index: int,
        metadata: Mapping[str, Any] | None,
    ) -> StateEvent:
        return StateEvent.from_transition(
            world_id=world_id,
            revision_id=revision_id,
            tick_id=tick_id,
            subject=proposal.subject,
            patch=proposal.patch,
            remove_paths=proposal.remove_paths,
            state_before=state_before,
            index=index,
            metadata=metadata,
            entity_id=self._extract_entity_id(proposal.metadata),
        )

    def _extract_entity_id(self, metadata: Mapping[str, Any] | None):
        if not metadata:
            return None
        entity_id = metadata.get("entity_id")
        if isinstance(entity_id, str):
            return EntityId.from_uuid(entity_id)
        return entity_id

    def _scheduled_plan_for(self, plan_id: str) -> ScheduledPlan | None:
        for record in self.planner_engine.plan_scheduler.records.values():
            if record.plan.plan_id == plan_id:
                return record
        return None

    def _publish_transport_observation(
        self,
        *,
        previous_snapshot: RenderSnapshot | None,
        current_snapshot: RenderSnapshot | None,
        previous_revision: RevisionId | None,
        current_revision: RevisionId | None,
        tick_number: TickId,
        transition_proposals: Sequence[TransitionProposal],
        correlation_id: str,
        representation_type: str,
    ) -> QObservation:
        context = TransportContext(
            world_id=self.world_id,
            previous_snapshot=previous_snapshot,
            current_snapshot=current_snapshot,
            previous_revision=previous_revision,
            current_revision=current_revision,
            transition_proposals=tuple(transition_proposals),
            configuration={"kernel_mode": "committed"},
            calibration_profile="default",
            representation_type=representation_type,
            domain_adapter_id="kernel",
            correlation_id=correlation_id,
            tick_number=self.current_tick_number,
            metadata={"tick_id": str(tick_number.value)},
        )
        observation = self.transport_engine.observe(context)
        self._last_transport_observation = observation
        return observation

    def _extract_spectral_transport_observable(self, state: Mapping[str, Any]) -> None:
        """Extract spectral transport observable from physical field domain state.
        
        This retrieves the validated SpectralTransportObservable computed by the
        physical field domain and makes it available at the kernel level for
        entity/environment coupling.
        """
        try:
            # Spectral observable is at top-level state (from physical_field domain patch)
            spectral_data = state.get("spectral_transport_observable")
            
            if spectral_data is not None:
                # Reconstruct SpectralTransportObservable from serialized data
                # Determine dominant_regime — accept "unknown" for backward compat,
                # but coerce to a valid value so the dataclass __post_init__ passes.
                raw_regime = str(spectral_data.get("dominant_regime", "overdamped"))
                if raw_regime not in ("coherent", "overdamped", "critical"):
                    raw_regime = "overdamped"

                # Reconstruct power fractions and ensure they sum to 1.
                fp = float(spectral_data.get("propagating_power_fraction", 0.0))
                fo = float(spectral_data.get("overdamped_power_fraction", 1.0))
                fc = float(spectral_data.get("critical_power_fraction", 0.0))
                fsum = fp + fo + fc
                if fsum > 0 and abs(fsum - 1.0) > 1e-6:
                    fp, fo, fc = fp/fsum, fo/fsum, fc/fsum

                observable = SpectralTransportObservable(
                    physical_time=float(spectral_data.get("physical_time", 0.0)),
                    dominant_k=float(spectral_data.get("dominant_k", 0.0)),
                    dominant_D=float(spectral_data.get("dominant_D", -1.0)),
                    dominant_regime=raw_regime,
                    propagating_power_fraction=fp,
                    overdamped_power_fraction=fo,
                    critical_power_fraction=fc,
                    weighted_D=float(spectral_data.get("weighted_D", -1.0)),
                    spectral_entropy=float(spectral_data.get("spectral_entropy", 0.0)),
                    c_spectral=float(spectral_data.get("c_spectral", fp - fo)),
                    c_nominal=float(spectral_data.get("c_nominal", 1.0)),
                    tau_nominal=float(spectral_data.get("tau_nominal", 1.0)),
                    k_critical=float(spectral_data.get("k_critical", 0.5)),
                    spectral_resolution=float(spectral_data.get("spectral_resolution", 1.0)),
                    domain_size=float(spectral_data.get("domain_size", 100.0)),
                    num_modes=int(spectral_data.get("num_modes", 0)),
                    metadata=dict(spectral_data.get("metadata", {})),
                )
                self._last_spectral_transport_observable = observable
        except Exception as e:
            # Spectral observable extraction failure should not prevent simulation tick completion
            print(f"Spectral transport observable extraction failed (non-critical): {e}")

    def _sync_entity_state(self) -> None:
        self._state["entities"] = self.entity_registry.serialize()

    def _restore_entity_state(self, serialized_entities: Mapping[str, Any]) -> None:
        self.entity_registry.restore(serialized_entities)
        self._sync_entity_state()

    def _project_domain_namespaces_into_entities(self) -> None:
        """Merge domain-specific transaction buffers into canonical entities.
        
        This implements the projection stage that ensures exactly one canonical
        observable entity state exists. Domain namespaces are internal transaction
        buffers and are discarded after successful projection.
        """
        namespace_projections = {
            "entity_needs_components": "NeedsComponent",
            "entity_health_components": "HealthComponent",
            "entity_inventory_components": "InventoryComponent",
            "entity_transform_components": "TransformComponent",
            "entity_production_components": "ProductionComponent",
            "entity_society_component": "SocietyComponent",
        }
        
        for namespace, component_name in namespace_projections.items():
            if namespace not in self._state:
                continue
                
            domain_patches = dict(self._state[namespace])
            
            if not domain_patches:
                del self._state[namespace]
                continue
            
            entities = dict(self._state.get("entities", {}))
            
            for entity_id, entity_patch in domain_patches.items():
                if entity_id not in entities:
                    continue
                    
                entity = dict(entities[entity_id])
                components = dict(entity.get("components", {}))
                
                if "components" in entity_patch:
                    component_patch = dict(entity_patch["components"])
                    if component_name in component_patch:
                        components[component_name] = dict(component_patch[component_name])
                        entity["components"] = components
                        entities[entity_id] = entity
            
            self._state["entities"] = entities
            del self._state[namespace]

    def _coerce_revision_id(self, value: Any) -> RevisionId | None:
        if value is None:
            return None
        if isinstance(value, RevisionId):
            return value
        if hasattr(value, "revision_id"):
            candidate = getattr(value, "revision_id")
            if isinstance(candidate, RevisionId):
                return candidate
            return RevisionId.from_uuid(candidate)
        if hasattr(value, "value"):
            return RevisionId.from_uuid(getattr(value, "value"))
        return RevisionId.from_uuid(value)
