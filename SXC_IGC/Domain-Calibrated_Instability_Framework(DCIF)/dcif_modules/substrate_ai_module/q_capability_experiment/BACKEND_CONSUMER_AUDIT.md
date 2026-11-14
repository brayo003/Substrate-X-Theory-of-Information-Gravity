# Backend Consumer Audit Report

## PHASE 1: Full Consumer Audit of Q References

### Executive Summary

A comprehensive audit of the Substrate X / DCIF backend has identified all consumers of the theoretical Q quantity. The audit reveals that Q is primarily used in:

1. **Physical field models** - QObservation dataclass definition
2. **Physical field dynamics** - compute_theoretical_q() function
3. **Controlled experiments** - Q validation experiments
4. **Substrate coupling** - Entity-field coupling (commented but not active)
5. **Legacy isolation** - legacy_q_isolation.py module
6. **Test files** - Various test files referencing Q

### Detailed Consumer Map

#### 1. Physical Field Models

**File:** `sim_world/domains/physical_field/physical_field_models.py`

**Location:** Lines 177-198

**Purpose:** Defines QObservation dataclass

```python
@dataclass(frozen=True, slots=True)
class QObservation:
    """Single observation of theoretical Q at a physical location."""
    coordinate: PhysicalCoordinate
    physical_time: float
    s_value: float  # Information density
    gradient_magnitude: float  # |∇ln s|
    c_value: float  # Propagation speed
    tau_value: float  # Relaxation time
    q_value: float  # Theoretical Q
    regime: str  # "coherent", "critical", "overdamped"
    metadata: Mapping[str, Any] = field(default_factory=dict)
```

**Status:** PRODUCER - Defines the data structure for Q observations

---

#### 2. Physical Field Dynamics

**File:** `sim_world/domains/physical_field/physical_field_dynamics.py`

**Location:** Lines 473-528

**Purpose:** Computes theoretical Q at physical coordinates

```python
def compute_theoretical_q(
    field: InformationDensityField,
    propagation_params: PropagationParameters,
    relaxation_params: RelaxationParameters,
    coordinate: PhysicalCoordinate,
) -> QObservation:
    """Compute theoretical Q at a physical coordinate.
    
    Q = 4c²τ²|∇ln s|² - 1
    """
    # Implementation uses gradient magnitude
    q_value = 4.0 * (c**2) * (tau**2) * (gradient_magnitude**2) - 1.0
```

**Status:** PRODUCER - Computes Q values from field state

---

#### 3. Substrate Coupling

**File:** `sim_world/domains/physical_field/substrate_coupling.py`

**Location:** Line 98 (comment only)

**Purpose:** Entity-field coupling mentions Q in comments

```python
def couple_field_to_entity_state(
    self,
    entity_id: str,
) -> Dict[str, float]:
    """Couple field state back to entity as environmental influence.
    
    Field Q values influence entity behavior parameters.
    """
```

**Status:** COMMENTED - Q mentioned in comments but not actively used in coupling logic

**Note:** The actual coupling function does NOT use Q. It returns:
```python
influences = {
    "field_intensity": float(field_value),
    "information_availability": min(1.0, field_value / 2.0),
    "environmental_pressure": max(0.0, (field_value - 1.0) / 2.0),
}
```

---

#### 4. Controlled Experiments

**File:** `sim_world/domains/physical_field/controlled_experiments.py`

**Location:** Lines 184-272

**Purpose:** Q validation experiments comparing Q to independent observables

```python
def run_q_validation_experiment(
    field: InformationDensityField,
    propagation_params: PropagationParameters,
    relaxation_params: RelaxationParameters,
    test_coordinates: List[PhysicalCoordinate],
    perturbation_amplitude: float = 2.0,
    perturbation_width: float = 5.0,
) -> Dict[str, Any]:
    """Run Q validation experiment comparing Q to independent observables."""
```

**Status:** VALIDATION - Uses Q for experimental validation only

---

#### 5. Legacy Q Isolation

**File:** `sim_world/domains/physical_field/legacy_q_isolation.py`

**Location:** Full file

**Purpose:** Contains legacy Q code for backward compatibility

**Status:** ISOLATED - Legacy code isolated from main backend

---

#### 6. Test Files

**Files:**
- `test_physical_field.py` - 21 Q references
- `artificial_life_testbed.py` - 4 Q references
- Various audit result files

**Status:** TESTING - Q used in test files only

---

### Dependency Map

```
QObservation (dataclass)
    ↓
compute_theoretical_q() (function)
    ↓
run_q_validation_experiment() (validation)
    ↓
test_physical_field.py (testing)
```

**Key Finding:** Q is NOT actively used in:
- Entity-field coupling (only mentioned in comments)
- Backend agent logic
- Domain coupling
- Production entity interactions

**Active Q Usage:**
1. QObservation dataclass definition
2. compute_theoretical_q() function
3. Validation experiments
4. Test files

**Non-Active Q Usage:**
1. Substrate coupling (commented only)

### Integration Strategy

Based on the audit, the integration plan is:

1. **Replace QObservation** with SpectralTransportObservable
2. **Replace compute_theoretical_q()** with compute_spectral_transport_observable()
3. **Update validation experiments** to use spectral observable
4. **Update test files** to use spectral observable
5. **Substrate coupling** does not require changes (Q not actively used)

### Critical Finding

The backend does NOT currently use Q for entity-field coupling in production. The coupling function uses field intensity, information availability, and environmental pressure - all derived from field values, not Q.

This significantly simplifies the integration task. The main work is:
1. Define SpectralTransportObservable dataclass
2. Implement spectral analysis function
3. Update validation experiments
4. Update test files

### Q Reference Summary

| File | Lines | Purpose | Status |
|------|-------|---------|--------|
| physical_field_models.py | 177-198 | QObservation dataclass | Producer |
| physical_field_dynamics.py | 473-528 | compute_theoretical_q() | Producer |
| substrate_coupling.py | 98 | Comment only | Not active |
| controlled_experiments.py | 184-272 | Validation experiments | Validation |
| legacy_q_isolation.py | Full file | Legacy isolation | Isolated |
| test_physical_field.py | Multiple | Testing | Testing |
| artificial_life_testbed.py | Multiple | Testing | Testing |

### Conclusion

The audit reveals that Q is primarily a **validation/testing construct** rather than an active production backend component. The main integration work involves replacing the validation/testing infrastructure with the spectral observable approach.
