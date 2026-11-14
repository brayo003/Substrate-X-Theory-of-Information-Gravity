# Coupled Experiment Consumer Audit

## Executive Summary

The audit reveals a critical architectural finding: the Substrate X backend has TWO separate transport observation systems that are NOT currently integrated:

1. **Physical Field Layer** (`sim_world/domains/physical_field/`)
   - Contains: QObservation (deprecated), SpectralTransportObservable (newly integrated)
   - Used by: Controlled experiments, validation tests
   - Status: SpectralTransportObservable integrated here

2. **Transport Layer** (`sim_world/transport/`)
   - Contains: QObservation (different class), QCalibrator, QMetrics
   - Used by: Main backend kernel (world_kernel.py)
   - Status: Still uses old Q system

## Architectural Separation

### Physical Field Layer

**Location:** `sim_world/domains/physical_field/`

**Components:**
- `physical_field_models.py`: QObservation (deprecated), SpectralTransportObservable (new)
- `physical_field_dynamics.py`: compute_theoretical_q() (deprecated), compute_spectral_transport_observable() (new)
- `substrate_coupling.py`: Entity-field coupling (does NOT use Q actively)

**Integration Status:** ✅ SpectralTransportObservable integrated and validated

**Backend Reach:** Limited to physical field domain only, does NOT reach main kernel

---

### Transport Layer

**Location:** `sim_world/transport/`

**Components:**
- `q_observation.py`: QObservation (different class), QDiagnostics, CalibrationMetadata
- `q_calibrator.py`: QCalibrator, CalibrationProfile
- `q_metrics.py`: QMetrics
- `transport_engine.py`: TransportEngine
- `transport_context.py`: TransportContext

**Integration Status:** ❌ Uses old Q system, NOT updated with SpectralTransportObservable

**Backend Reach:** ✅ This is what the main kernel actually uses

---

### Main Kernel

**Location:** `sim_world/kernel/world_kernel.py`

**Key Import:**
```python
from ..transport.transport import QObservation, TransportContext, TransportEngine
```

**Usage:** The main kernel imports QObservation from the transport layer, NOT the physical field layer

---

## Execution Path Analysis

### Current Execution Path

```
world_kernel.py
    ↓
transport/q_observation.py (QObservation)
    ↓
transport/transport_engine.py
    ↓
entity updates
```

### Integrated Path (Physical Field Only)

```
physical_field_models.py (SpectralTransportObservable)
    ↓
physical_field_dynamics.py (compute_spectral_transport_observable)
    ↓
physical field domain
    ↓
❌ DOES NOT REACH MAIN KERNEL
```

---

## Search Results

### SpectralTransportObservable References

Found in 6 locations:
- `sim_world/domains/physical_field/physical_field_models.py` (definition)
- `sim_world/domains/physical_field/physical_field_dynamics.py` (implementation)
- Test files (q_capability_experiment)

**Key Finding:** SpectralTransportObservable is NOT referenced by:
- `sim_world/kernel/world_kernel.py`
- `sim_world/transport/`
- Main backend execution path

---

### QObservation References

**Physical Field Layer:**
- `sim_world/domains/physical_field/physical_field_models.py` (deprecated)

**Transport Layer:**
- `sim_world/transport/q_observation.py` (different class)
- `sim_world/transport/transport.py` (exports)
- `sim_world/kernel/world_kernel.py` (imports from transport)

**Key Finding:** The main kernel uses the transport layer's QObservation, not the physical field's

---

## Active Production Consumers

### Main Backend Kernel

**Consumer:** `world_kernel.py`

**Observable Used:** `transport.q_observation.QObservation`

**Status:** ❌ NOT updated with SpectralTransportObservable

---

### Physical Field Domain

**Consumer:** Controlled experiments, validation tests

**Observable Used:** `physical_field_models.SpectralTransportObservable`

**Status:** ✅ Updated and validated

---

## Architectural Blocker

### Critical Finding

The newly integrated SpectralTransportObservable exists ONLY in the physical field layer. The main backend kernel (`world_kernel.py`) uses a COMPLETELY DIFFERENT Q system from the transport layer.

This means:

1. ✅ SpectralTransportObservable is correctly integrated into the physical field layer
2. ❌ SpectralTransportObservable does NOT reach the main backend entity coupling path
3. ❌ The main backend still uses the old Q system from the transport layer
4. ❌ A coupled experiment using the main kernel would NOT use SpectralTransportObservable

---

## Required Next Steps

To complete the spectral observable integration, TWO integrations are required:

### 1. Physical Field Layer ✅ (COMPLETED)
- ✅ SpectralTransportObservable defined
- ✅ compute_spectral_transport_observable() implemented
- ✅ QObservation deprecated
- ✅ Tests passing

### 2. Transport Layer ❌ (NOT STARTED)
- ❌ SpectralTransportObservable must be integrated into transport layer
- ❌ transport/q_observation.py must be updated
- ❌ transport/transport_engine.py must be updated
- ❌ world_kernel.py must be updated to use spectral observable
- ❌ Transport layer QObservation must be deprecated

---

## Conclusion

**ARCHITECTURAL GATE FAIL**

The physical field layer integration is complete, but the MAIN BACKEND KERNEL uses a separate transport layer that has NOT been updated with SpectralTransportObservable.

A coupled experiment using the main kernel would NOT validate the spectral observable integration because the main kernel does not use it.

**The transport layer must be updated before a valid coupled experiment can be performed.**
