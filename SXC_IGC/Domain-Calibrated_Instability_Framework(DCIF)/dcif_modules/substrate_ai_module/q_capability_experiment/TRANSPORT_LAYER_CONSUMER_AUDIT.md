# Transport Layer Consumer Audit

## Executive Summary

The audit reveals a **fundamental architectural mismatch** between the physical field layer and the transport layer. They are designed for **completely different purposes**:

1. **Physical Field Layer**: Telegraph equation field dynamics with spectral transport analysis
2. **Transport Layer**: State transition analysis for sim_world snapshots using Q-based metrics

These are **NOT the same system** and cannot be directly migrated without architectural redesign.

## Detailed Architecture Analysis

### Physical Field Layer

**Location:** `sim_world/domains/physical_field/`

**Purpose:** Telegraph equation field dynamics

**Components:**
- `physical_field_models.py`: SpectralTransportObservable (validated)
- `physical_field_dynamics.py`: compute_spectral_transport_observable() (validated)
- `substrate_coupling.py`: Entity-field coupling (not actively using Q)

**Mathematical Foundation:**
- Telegraph equation: τ ∂²s/∂t² + ∂s/∂t = c²τ ∇²s
- Modal discriminant: D(k) = 4c²τ²k² - 1
- Spectral analysis: FFT-based

**Integration Status:** ✅ VALIDATED

---

### Transport Layer

**Location:** `sim_world/transport/`

**Purpose:** State transition analysis for sim_world snapshots

**Components:**
- `q_observation.py`: QObservation (different from physical field Q)
- `q_calibrator.py`: QCalibrator, CalibrationProfile
- `q_metrics.py`: QMetrics, state snapshot analysis
- `transport_engine.py`: TransportEngine
- `transport_context.py`: TransportContext

**Mathematical Foundation:**
- NOT the telegraph equation
- State transition metrics (entity changes, component signatures, relationship signatures)
- Q-based calibration system
- Snapshot comparison analysis

**Integration Status:** ❌ NOT RELATED TO PHYSICAL FIELD TRANSPORT

---

### Main Kernel

**Location:** `sim_world/kernel/world_kernel.py`

**Purpose:** Main simulation orchestration

**Import:** `from ..transport.transport import QObservation, TransportContext, TransportEngine`

**Transport Layer Use:** Uses transport layer for state transition analysis

**Physical Field Use:** Appears to be separate/independent

---

## Critical Finding: Architectural Mismatch

### The Transport Layer is NOT Physical Field Transport

The transport layer's Q system is designed for:

1. **State snapshot comparison** (previous vs current)
2. **Entity state analysis** (component signatures, relationships)
3. **Transition proposal evaluation**
4. **RenderSnapshot analysis**

It does NOT:
- Access the physical field's telegraph equation solver
- Perform FFT analysis on field data
- Compute spectral transport properties
- Use the telegraph equation's dispersion relation

### The Physical Field Layer is NOT State Transition Analysis

The physical field layer is designed for:

1. **Telegraph equation field evolution**
2. **Spectral transport analysis**
3. **Entity-field physical coupling**

It does NOT:
- Analyze state snapshots
- Compare entity state transitions
- Evaluate transition proposals
- Use QCalibrator or QMetrics

---

## Dependency Graph

### Current Architecture

```
world_kernel.py
    ↓
transport/transport_engine.py
    ↓
transport/q_observation.py (QObservation)
    ↓
transport/q_calibrator.py
    ↓
transport/q_metrics.py
    ↓
RenderSnapshot analysis
    ↓
entity state metrics
```

### Physical Field Architecture (Separate)

```
physical_field_models.py
    ↓
physical_field_dynamics.py
    ↓
compute_spectral_transport_observable()
    ↓
telegraph field evolution
    ↓
entity-field coupling
```

### Key Finding: NO PATH BETWEEN THEM

There is **NO execution path** from the physical field layer to the transport layer. They are **independent systems**:

- The transport layer works with RenderSnapshots of sim_world state
- The physical field layer works with the telegraph equation field solver
- They operate on **different data structures** and **different mathematical foundations**

---

## Q System Comparison

### Physical Field QObservation

**Location:** `sim_world/domains/physical_field/physical_field_models.py`

**Status:** DEPRECATED

**Definition:**
```python
QObservation(
    coordinate: PhysicalCoordinate,
    physical_time: float,
    s_value: float,
    gradient_magnitude: float,  # |∇ln s|
    c_value: float,
    tau_value: float,
    q_value: float,  # 4c²τ²|∇ln s|² - 1
    regime: str,
)
```

**Purpose:** Local pointwise transport measurement (falsified)

---

### Transport Layer QObservation

**Location:** `sim_world/transport/q_observation.py`

**Status:** ACTIVE (different purpose)

**Definition:**
```python
QObservation(
    world_id: WorldId,
    tick_id: TickId,
    previous_revision: RevisionId,
    current_revision: RevisionId,
    observation_time: datetime,
    observation_id: str,
    metric_values: Mapping[str, float],  # State transition metrics
    calibration_profile: str,
    calibration_version: str,
    representation_type: str,
    confidence: float,
    q_value: float,  # Calibrated state transition metric
    regime: str,  # Calibrated regime classification
    uncertainty: float,
    thresholds: Mapping[str, float],
    observed_pair: Mapping[str, Any],  # Snapshot comparison
    calibration_metadata: CalibrationMetadata,
)
```

**Purpose:** State transition analysis and calibration

---

## Consumer Analysis

### Transport Layer Consumers

**Active Consumers:**
1. `transport_engine.py` - Uses QObservation for state transition tracking
2. `world_kernel.py` - Uses transport engine for orchestration
3. Likely entity/planner systems - Use transport observables for decision-making

**Consumers of Physical Field:**
1. `substrate_coupling.py` - Entity-field coupling (does NOT use Q actively)
2. Controlled experiments - Validation only

### No Cross-Consumption

There is **NO consumer** that uses both:
- The physical field's telegraph equation solver
- The transport layer's Q system

They are **independent architectural layers**.

---

## Integration Barrier

### Cannot Simply Migrate

The migration from transport layer QObservation to SpectralTransportObservable is **NOT a simple interface change** because:

1. **Different data structures**: Transport uses RenderSnapshots, physical field uses field arrays
2. **Different mathematics**: Transport uses state transition metrics, physical field uses telegraph dispersion
3. **Different purposes**: Transport analyzes state changes, physical field analyzes field dynamics
4. **No data flow**: There is no path from physical field to transport layer

### Architectural Redesign Required

To integrate the spectral transport observable into the main kernel, one of two approaches would be needed:

**Option A: Extend Transport Layer**
- Add physical field integration to transport layer
- Add spectral analysis capabilities to transport context
- Redesign transport engine to handle both state transitions and field transport

**Option B: New Physical Field Transport Layer**
- Create new transport layer specifically for physical field
- Integrate with world_kernel alongside existing transport layer
- Maintain separation of concerns

## Conclusion

**ARCHITECTURAL BLOCKER**

The transport layer and physical field layer are **fundamentally different systems** designed for different purposes. The transport layer's Q system is for state transition analysis, NOT physical field transport analysis.

The migration is **NOT a simple interface change** - it requires **architectural redesign** to either:
1. Extend the transport layer to handle physical field transport, OR
2. Create a new physical field transport layer alongside the existing one

**The simple migration approach is not feasible without architectural redesign.**
