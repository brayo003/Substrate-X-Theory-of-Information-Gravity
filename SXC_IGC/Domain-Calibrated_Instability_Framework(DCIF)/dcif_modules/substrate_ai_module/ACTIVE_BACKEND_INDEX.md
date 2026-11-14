# ACTIVE BACKEND INDEX

**Purpose:** Shortest possible document to understand the backend.
**Date:** 2025-01-22

---

## ENTRY POINTS

### Simulation Backend (sim_world)
- **File:** `sim_world/kernel/world_kernel.py`
- **Entry:** `WorldKernel.execute_cycle()`
- **Purpose:** Social simulation with entity-driven goal achievement

### CognitiveGovernor (main.py)
- **File:** `main.py`
- **Entry:** `CognitiveGovernor.process_question()`
- **Purpose:** Separate cognitive system (not sim_world backend)

---

## KERNEL

**File:** `sim_world/kernel/world_kernel.py`

**Role:** Central simulation coordinator

**Key Methods:**
- `execute_cycle()` - Full cycle (plan → simulate → render → verify → govern)
- `advance_tick()` - Single tick execution
- `commit_state()` - State projection and observable extraction

**Authoritative File:** `sim_world/kernel/world_kernel.py`

---

## SIMULATION ENGINE

**File:** `sim_world/simulation/simulation_engine.py`

**Role:** Tick execution, action scheduling, domain hooks

**Key Methods:**
- `advance()` - Execute tick
- `register_domain()` - Register domain hooks

**Authoritative File:** `sim_world/simulation/simulation_engine.py`

---

## ACTIVE DOMAINS

**Registry:** `sim_world/domains/__init__.py`

**Active Domains:**
1. **Physical Field** - `sim_world/domains/physical_field/`
2. **Time** - `sim_world/domains/time/`
3. **Population** - `sim_world/domains/population/`

**Dormant Domains:** agriculture, economy, production, learning, resources, relationships, conversation, needs, health, society, terrain, weather (commented out in registration)

**Authoritative File:** `sim_world/domains/__init__.py`

---

## PHYSICAL FIELD

**Files:**
- `sim_world/domains/physical_field/physical_field_domain.py` - Domain interface
- `sim_world/domains/physical_field/physical_field_dynamics.py` - Telegraph solver, spectral analysis
- `sim_world/domains/physical_field/physical_field_models.py` - Data structures

**Equation:** Telegraph equation `τ ∂²s/∂t² + ∂s/∂t = c²τ∇²s + S`

**Observable:** `SpectralTransportObservable` (computed via FFT, reaches kernel)

**Status:** ACTIVE (registered in domains/__init__.py)

---

## SPECTRAL TRANSPORT

**File:** `sim_world/domains/physical_field/physical_field_dynamics.py`

**Function:** `compute_spectral_transport_observable()`

**Fundamental Quantity:** `D(k) = 4c²τ²k² - 1`

**Regimes:**
- D(k) > 0 → coherent/propagating
- D(k) = 0 → critical
- D(k) < 0 → overdamped

**Data Flow:**
```
Field state → FFT → D(k) → SpectralTransportObservable → Kernel
```

**Consumers:** Tests only (no production consumers)

**Status:** ONE-WAY (dead-end at kernel)

---

## STATE-TRANSITION TRANSPORT

**Files:**
- `sim_world/transport/transport_engine.py` - Main engine
- `sim_world/transport/q_observation.py` - Data structure
- `sim_world/transport/q_metrics.py` - Metric computation
- `sim_world/transport/q_calibrator.py` - Calibration

**Basis:** Entity state transition metrics (state-distance, identity-preservation, etc.)

**Data Flow:**
```
Entity state → RenderSnapshot → QObservation → Kernel/LLM/Governor
```

**Consumers:** Kernel, Governor, LLM Reasoning

**Relation to Spectral Transport:** Mathematically independent (no data flow)

**Status:** ACTIVE closed-loop (Entity ↔ Q ↔ LLM ↔ Entity)

---

## ENTITIES

**File:** `sim_world/entities/registry.py`

**Role:** Entity registry, components, relationships

**State Location:** `kernel.current_state["entities"]`

**Status:** ACTIVE

---

## PLANNER / REASONING

**Files:**
- `sim_world/planner/planner_engine.py` - Goal-driven planning
- `sim_world/reasoning/reasoning_coordinator.py` - LLM intention generation

**Data Flow:**
```
Entity state → QObservation → LLM Reasoning → Goals → Plans → Actions → Entity state
```

**Status:** ACTIVE

---

## LLM

**File:** `sim_world/reasoning/reasoning_coordinator.py`

**Service:** `sim_world/reasoning/llm_service.py`

**Consumes:** QObservation (state-transition transport)

**Does NOT Consume:** SpectralTransportObservable (current disconnect)

**Status:** ACTIVE

---

## CALIBRATION

**File:** `sim_world/transport/q_calibrator.py`

**Calibrates:** QObservation metrics

**Does NOT Calibrate:** Spectral observable

**Status:** ACTIVE (state-transition only)

---

## TESTS

**Active Tests:**
- `q_capability_experiment/test_spectral_integration.py` - Spectral unit tests
- `q_capability_experiment/test_q_regression.py` - Q deprecation regression
- `q_capability_experiment/test_kernel_spectral_integration.py` - Kernel integration
- `q_capability_experiment/test_controlled_kernel_validation.py` - Controlled validation
- `q_capability_experiment/test_coupled_kernel_smoke.py` - 100-tick coupled test
- `q_capability_experiment/test_causal_coupling.py` - Causal coupling experiment
- `sim_world/domains/physical_field/test_physical_field.py` - Field unit tests

**Status:** ACTIVE

---

## IMPORTANT NON-ACTIVE SYSTEMS

**SubstrateCoupling:**
- File: `sim_world/domains/physical_field/substrate_coupling.py`
- Status: DORMANT (not called by kernel)
- Purpose: Entity-field coupling interface (not integrated)

**Most Domains:**
- agriculture, economy, production, etc.
- Status: DORMANT (progressive integration)
- Purpose: Future domain expansion

---

## ARCHIVE

**Location:** `_archive/`

**Contents:**
- `generated/` - Generated execution artifacts (e.g., causal_coupling_results.json)

**Purpose:** Preserve non-source artifacts without cluttering production tree

---

## ARCHITECTURE DOCUMENTATION

**Backend Audit:** `FULL_BACKEND_ARCHITECTURAL_AUDIT.md`
**File Classification:** `BACKEND_FILE_CLASSIFICATION.md`
**Architecture Map:** `BACKEND_ARCHITECTURE_MAP.md` (to be created)
**Consolidation Report:** `BACKEND_CONSOLIDATION_REPORT.md` (to be created)

---

## KEY ARCHITECTURAL FACTS

1. **Two Independent Transport Systems:**
   - Spectral transport (field-level, D(k))
   - State-transition transport (entity-level, QObservation)
   - No data flow between them

2. **No Field-Entity Coupling:**
   - SubstrateCoupling exists but not integrated
   - Field and entity systems are architecturally independent

3. **Spectral Observable Dead-End:**
   - Computed and reaches kernel
   - No production consumers
   - LLM receives QObservation, not spectral observable

4. **Active Closed Loop:**
   - Entity state ↔ QObservation ↔ LLM ↔ Entity actions

5. **One-Way Path:**
   - Field → Spectral observable → Kernel (no feedback)
