# 6. Planner

## Role

The Planner proposes intended future events. It does not advance time, mutate the world, render, or guarantee feasibility. The Simulation Engine and Kernel decide whether a proposed step is physically, socially, legally, and resource-wise possible.

## Plan model

A goal contains subject, desired predicate or target state, priority, utility/rationale, deadline/window, constraints, horizon, provenance, and confidence. A plan is a directed task graph: nodes are intended actions or subgoals; edges are temporal, causal, resource, or contingency dependencies. Nodes carry preconditions, expected effects, reservation requests, estimated cost, interruption policy, and validation checkpoint.

The planner may express the example `wake → eat → travel to work → work → return home → sleep` as a graph, not a script. Travel may branch to alternate routes; a missing meal can activate a food-acquisition subgoal; all steps remain subject to Kernel admission.

## Horizon, priority, and replanning

The planner maintains a rolling horizon with a committed near-term frontier and speculative long-term branches. Priorities are policy-defined and explainable: survival/safety, contractual obligations, resource preservation, social commitments, preferences, then aesthetics. It replans when state invalidates a precondition, an action fails, a higher-priority goal arrives, a resource changes, an agent receives new knowledge, or the horizon expires.

Interruption is explicit: suspend, cancel, compensate, or continue-to-safe-point. A plan produces diagnostics including unsatisfied constraints, search budget, conflicts, stale assumptions, and confidence. These diagnostics inform the Governor but cannot cause an autonomous mutation by the Planner.

## Public Interfaces

- Provides: goal submission, plan generation, task graph emission, replanning triggers, interruption handling, and planning diagnostics.
- Consumes: world state summaries, agent memory, simulation diagnostics, and policy constraints relevant to feasible future actions.
- Emits: goals, task graphs, action candidates, confidence values, and replanning notices.

## Dependencies

- Depends on: Kernel state summaries, Entity System facts, Memory, and Simulation feedback about feasibility and state change.
- Does NOT depend on: Renderer output or Transport Q as an authority for planning decisions.
- Must preserve: proposal-only behavior with no direct world mutation.

## Acceptance Criteria

- Plans represent intended future events rather than simulated truth.
- Every plan node carries a clear horizon, priority, and interruption policy.
- Replanning occurs when preconditions fail or new information invalidates a branch.
- Diagnostics are sufficient for the Governor to evaluate policy without the Planner mutating state.
