# Q Physical Construction Specification

**Specification Date:** 2026-08-09  
**Purpose:** Derive the smallest legitimate construction of the missing physical layer from existing SXC-IGC substrate  
**Authority:** q_define.txt (theoretical Q = 4c²τ²|∇ln s|² − 1)  
**Scope:** Construction specification only - no implementation

---

## 1. Executive Verdict

**NOT CONSTRUCTIBLE FROM EXISTING SUBSTRATE WITHOUT NEW PHYSICAL ASSUMPTIONS**

**Classification:** **C - CONSTRUCTIBLE ONLY WITH SUBSTANTIAL NEW PHYSICAL ASSUMPTIONS**

**Critical Distinction:** The existing substrate contains discrete entity dynamics, categorical locations, and numerical state equations, but does not contain continuous physical field dynamics, propagation mechanisms, or relaxation processes that could be legitimately extended into the required theoretical objects.

**Required New Assumptions:**
- Continuous physical spatial domain with metric structure
- Information density field definition and units
- Propagation dynamics from which c can be measured
- Physical relaxation mechanism from which τ can be measured
- Coupling between existing discrete substrate and continuous field

These are not derivable from existing substrate dynamics - they constitute new physical theory disguised as implementation.

---

## 2. Existing Substrate Inventory

### 2.1 Spatial Structures

**Grid Coordinate System**
- **File:** sim_world/itemz/dcif_observatory/world/coordinate_transform.gd
- **Representation:** 2D integer grid coordinates (x, y)
- **Units:** None (unitless integers)
- **Physical Interpretation:** Village locations (plaza, houses, forest, river)
- **Contribution to Theoretical Construction:** **NO** - Discrete lattice, not continuous physical space
- **Why:** No metric structure, no physical distance, no continuous coordinates

**Terrain Domain**
- **File:** sim_world/domains/terrain/__init__.py
- **Representation:** Discrete location entities (forest, river, farmland, village_square)
- **Units:** None (categorical)
- **Physical Interpretation:** Navigation locations and building placement
- **Contribution to Theoretical Construction:** **NO** - Categorical locations, not continuous field
- **Why:** No scalar field, no spatial continuity, no gradient computation

**Entity Transform Components**
- **File:** sim_world/entities/components.py
- **Representation:** TransformComponent with position (tuple[float, float, float]), room (str)
- **Units:** None (position is tuple, room is string)
- **Physical Interpretation:** Entity positioning in room-based navigation
- **Contribution to Theoretical Construction:** **NO** - Discrete entity positions, not continuous field
- **Why:** No scalar field over space, no information density

### 2.2 Temporal Structures

**Time Domain**
- **File:** sim_world/domains/time/__init__.py
- **Representation:** tick_number (int), hour (tick_number % 24), phase (night/morning/afternoon/evening)
- **Units:** None (numerical tick count)
- **Physical Interpretation:** Simulation time progression
- **Contribution to Theoretical Construction:** **PROXY** - Numerical time exists but no physical units
- **Why:** No physical seconds, no physical time measurement

**Numerical Timestep**
- **Representation:** Tick-based progression (tick_number increments by 1)
- **Units:** None (dimensionless)
- **Physical Interpretation:** Discrete simulation steps
- **Contribution to Theoretical Construction:** **PRIMITIVE** - Time stepping exists but no physical time
- **Why:** No conversion to physical seconds, no physical duration

### 2.3 State Dynamics

**Needs Domain (Entity Metabolism)**
- **File:** sim_world/SIMULATOR_STATE_EQUATIONS.md
- **Representation:** hunger(t+1) = min(1.0, hunger(t) + 0.02 × traits.hunger_decay_mult)
- **Units:** None (normalized 0-1 range)
- **Physical Interpretation:** Entity hunger decay and recovery
- **Contribution to Theoretical Construction:** **NO** - Discrete entity needs, not field
- **Why:** No spatial field, no propagation, no physical relaxation

**Weather Domain**
- **File:** sim_world/domains/weather/weather_domain.py
- **Representation:** WeatherState with temperature, moisture, season, weather_type
- **Units:** None (categorical states)
- **Physical Interpretation:** Environmental conditions affecting entities
- **Contribution to Theoretical Construction:** **NO** - Global environmental state, not field
- **Why:** No spatial field variation, no propagation, no gradient

**Relationship Domain**
- **File:** sim_world/domains/relationships/relationships_domain.py
- **Representation:** Social relationships with familiarity, affinity, interaction_history
- **Units:** None (normalized values)
- **Physical Interpretation:** Social network dynamics
- **Contribution to Theoretical Construction:** **NO** - Discrete relationships, not field
- **Why:** No spatial field, no physical propagation

### 2.4 Transport Metrics

**Transport Engine**
- **File:** sim_world/transport/transport_engine.py
- **Representation:** QMetrics with state_distance, representation_distance, topology_preservation
- **Units:** None (normalized 0-1 range)
- **Physical Interpretation:** Structural change classification
- **Contribution to Theoretical Construction:** **NO** - Structural metrics, not physical field
- **Why:** No spatial field, no physical propagation, no gradient

---

## 3. Constructibility Matrix

| Required object | Existing substrate basis | Classification | Required extension | New assumption? | Scientific risk |
|---|---|---|---|---|---|
| x (physical spatial coordinates) | Grid coordinates (integer lattice) | D | Continuous physical coordinates with metric | YES | HIGH |
| metric g_ij / g^ij | No metric structure | D | Physical distance definition and coordinate invariance | YES | HIGH |
| t (physical time) | Numerical tick count | B | Physical time units (seconds) | YES | MEDIUM |
| s(x,t) (information density field) | No scalar field | D | Field definition over physical space | YES | HIGH |
| ∇ (spatial gradient) | np.gradient (numerical) | D | Physical spatial gradient operator | YES | HIGH |
| c (propagation speed) | No propagation mechanism | D | Propagation dynamics and measurement | YES | HIGH |
| τ (damping time constant) | Numerical decay_rate = 0.0005 | D | Physical relaxation mechanism and measurement | YES | HIGH |
| Q (theoretical) | Engineered proxy Q | D | Physical field calculation with measured parameters | YES | HIGH |

**Classification Legend:**
- A = Already present and directly usable
- B = Present in primitive form and legitimately extensible
- C = Derivable from existing substrate dynamics
- D = Requires a minimal new physical mechanism
- E = Cannot be constructed without introducing a new theoretical assumption

**Result:** All required objects are classified as D - requiring new physical mechanisms

---

## 4. Minimum Physical Field Specification

### 4.1 Domain

**Domain Type:** Continuous 2D physical space

**Dimensionality:** 2 spatial dimensions + 1 temporal dimension

**Coordinates:** Physical coordinates (x, y) with metric structure

**Justification:** Theoretical Q requires continuous physical coordinates with metric structure for coordinate-invariant gradient computation. Existing grid coordinates are discrete and lack metric structure.

### 4.2 Coordinates

**Coordinate System:** Cartesian coordinates (x, y)

**Metric Structure:** Euclidean metric g_{ij} = δ_{ij} (identity matrix)

**Coordinate Range:** Physical dimensions to be defined (e.g., village size in meters)

**Boundary Conditions:** To be specified (e.g., Neumann, Dirichlet, periodic)

**Justification:** Coordinate invariance requires metric structure. Euclidean metric is the simplest assumption but constitutes a new physical assumption not present in existing substrate.

### 4.3 Field Value

**Field Type:** Scalar field s(x,t)

**Physical Units:** Information density (units to be defined, e.g., bits/m³ or info/m³)

**Value Range:** Positive (required for ln(s))

**Justification:** Theoretical Q requires s(x,t) as information density field. No existing substrate variable has this physical meaning.

### 4.4 Discretization

**Numerical Representation:** Lattice approximation (e.g., finite difference grid)

**Spacing:** Physical spacing Δx, Δy (to be defined)

**Time Step:** Physical time step Δt (to be defined)

**Justification:** If discrete implementation is required, the lattice must be explicitly a numerical representation of physical space, not claiming the discrete grid itself is automatically physical.

### 4.5 Boundary Conditions

**Type:** To be specified (e.g., reflecting, absorbing, periodic)

**Physical Meaning:** How information density behaves at domain boundaries

**Justification:** Boundary conditions are required for field evolution but constitute new physical assumptions.

### 4.6 Temporal Update

**Governing Equation:** To be specified (e.g., telegraph equation, diffusion equation)

**Time Integration Scheme:** To be specified (e.g., explicit Euler, Crank-Nicolson)

**Stability Conditions:** To be specified (e.g., CFL condition)

**Justification:** Field evolution equation is required but constitutes new physical theory.

### 4.7 Interpolation Requirements

**Spatial Interpolation:** For gradient computation between lattice points

**Temporal Interpolation:** For c and τ measurement

**Justification:** Interpolation required for continuous field approximation from discrete lattice.

### 4.8 Gradient Calculation

**Method:** Finite difference or spectral methods

**Coordinate Invariance:** Must use metric structure g^{ij}

**Numerical Accuracy:** To be specified (first-order, second-order, etc.)

**Justification:** Gradient computation requires metric structure for coordinate invariance.

### 4.9 Coordinate Transformation Requirements

**Invariance:** |∇ln s|² must be coordinate-invariant

**Transformation Rules:** g^{ij}(∂_i ln s)(∂_j ln s) must be preserved

**Justification:** Coordinate invariance is required for physical meaning but constitutes new assumption about metric structure.

---

## 5. Information Density Specification

### 5.1 Information Definition

**What Constitutes Information:** **NOT DEFINED**

**Critical Gap:** The existing substrate does not contain a theoretical definition of "information" that can be quantified as a physical density.

**Existing Variables:**
- Entity needs (hunger, thirst, etc.) - not information
- Entity inventory - not information
- Social relationships - not information
- Weather state - not information
- Terrain types - not information

**Conclusion:** Information density cannot be legitimately defined from existing substrate variables.

### 5.2 Information Quantification

**Quantification Method:** **NOT DEFINED**

**Required:** Physical measure of information content (e.g., Shannon entropy, Kolmogorov complexity)

**Existing Quantification:** None in existing substrate

**Conclusion:** Information quantification requires new physical theory.

### 5.3 Spatial Localization

**Localization Method:** **NOT DEFINED**

**Required:** Method to localize information spatially (e.g., information per unit volume)

**Existing Localization:** Entity positions exist but not information density

**Conclusion:** Spatial localization of information requires new assumption.

### 5.4 Units

**Required Units:** Information per physical volume (e.g., bits/m³, info/m³)

**Existing Units:** None (all existing variables are dimensionless)

**Conclusion:** Physical units for information density must be introduced as new assumption.

### 5.5 Measurement

**Measurement Method:** **NOT DEFINED**

**Required:** Operational procedure to measure s(x,t)

**Existing Measurement:** No field measurement in existing substrate

**Conclusion:** Information density measurement requires new physical theory.

### 5.6 Zero/Near-Zero Handling

**Requirement:** s > 0 where ln(s) is evaluated

**Handling Method:** To be specified (e.g., regularization, positivity constraint)

**Existing Handling:** No relevant handling in existing substrate

**Conclusion:** Zero/near-zero handling requires new assumption.

### 5.7 Measurement Noise

**Noise Model:** To be specified

**Effect on ∇ln s:** To be analyzed

**Existing Noise Analysis:** None in existing substrate

**Conclusion:** Noise analysis requires new assumption.

---

## 6. Propagation Specification

### 6.1 Governing Equation

**Equation:** **NOT DEFINED**

**Required:** Propagation equation (e.g., wave equation, telegraph equation, diffusion equation)

**Existing Propagation:** None in existing substrate

**Conclusion:** Propagation equation must be introduced as new physical theory.

### 6.2 Local State Variables

**Variables:** To be specified (e.g., field amplitude, field velocity)

**Existing Variables:** No field variables in existing substrate

**Conclusion:** Field state variables must be introduced as new assumption.

### 6.3 Coupling Mechanism

**Coupling:** To be specified (e.g., how field couples to entity states)

**Existing Coupling:** No field-entity coupling in existing substrate

**Conclusion:** Coupling mechanism must be introduced as new assumption.

### 6.4 Perturbation Experiment

**Protocol:** To be specified (e.g., localized Gaussian perturbation)

**Existing Experiments:** No perturbation experiments in existing substrate

**Conclusion:** Perturbation protocol must be designed as new assumption.

### 6.5 Propagation Observable

**Observable:** To be specified (e.g., field amplitude at different locations)

**Existing Observables:** No field observables in existing substrate

**Conclusion:** Propagation observable must be introduced as new assumption.

### 6.6 Distance Measurement

**Method:** To be specified (e.g., physical distance between points)

**Existing Measurement:** No physical distance measurement in existing substrate

**Conclusion:** Physical distance measurement requires new assumption.

### 6.7 Time Measurement

**Method:** To be specified (e.g., physical time between perturbation and arrival)

**Existing Measurement:** No physical time measurement in existing substrate

**Conclusion:** Physical time measurement requires new assumption.

### 6.8 Estimator for c

**Estimator:** To be specified (e.g., c = distance/time)

**Existing Estimator:** None in existing substrate

**Conclusion:** Propagation speed estimator must be introduced as new assumption.

### 6.9 Uncertainty/Error Measurement

**Method:** To be specified (e.g., bootstrap confidence intervals)

**Existing Measurement:** No uncertainty analysis in existing substrate

**Conclusion:** Uncertainty measurement requires new assumption.

### 6.10 c Properties

**Constancy:** To be determined from proposed dynamics

**State Dependence:** To be determined from proposed dynamics

**Direction Dependence:** To be determined from proposed dynamics

**Spatial Variation:** To be determined from proposed dynamics

**Conclusion:** These properties depend on the chosen propagation equation, which is not defined by existing substrate.

---

## 7. Relaxation Specification

### 7.1 Governing Equation

**Equation:** **NOT DEFINED**

**Required:** Relaxation equation (e.g., exponential decay, viscoelastic relaxation)

**Existing Relaxation:** Numerical decay in SXCOmegaEngine but not physical relaxation

**Conclusion:** Physical relaxation equation must be introduced as new physical theory.

### 7.2 Physical State Being Damped

**State:** To be specified (e.g., field amplitude, field velocity)

**Existing State:** No field state in existing substrate

**Conclusion:** Damped state must be introduced as new assumption.

### 7.3 Perturbation Protocol

**Protocol:** To be specified (e.g., initial displacement from equilibrium)

**Existing Protocol:** No relaxation experiments in existing substrate

**Conclusion:** Perturbation protocol must be designed as new assumption.

### 7.4 Relaxation Observable

**Observable:** To be specified (e.g., field amplitude over time)

**Existing Observable:** No field observables in existing substrate

**Conclusion:** Relaxation observable must be introduced as new assumption.

### 7.5 Estimator for τ

**Estimator:** To be specified (e.g., exponential fit to relaxation curve)

**Existing Estimator:** None in existing substrate

**Conclusion:** Relaxation time estimator must be introduced as new assumption.

### 7.6 Units

**Required Units:** Seconds (s)

**Existing Units:** None (numerical decay_rate is dimensionless)

**Conclusion:** Physical units must be introduced as new assumption.

### 7.7 Uncertainty/Error Measurement

**Method:** To be specified (e.g., fitting error, bootstrap confidence)

**Existing Measurement:** No uncertainty analysis in existing substrate

**Conclusion:** Uncertainty measurement requires new assumption.

### 7.8 Relaxation Law

**Law:** To be determined (e.g., exponential, power-law, stretched exponential)

**Existing Law:** Numerical decay exists but not physical relaxation law

**Conclusion:** Physical relaxation law must be introduced as new assumption.

---

## 8. Metric Specification

### 8.1 Metric Structure

**Metric Tensor:** g_{ij} = δ_{ij} (Euclidean metric)

**Inverse Metric:** g^{ij} = δ^{ij}

**Justification:** Euclidean metric is the simplest assumption but constitutes new physical assumption not present in existing substrate.

### 8.2 Physical Distance

**Definition:** ds² = g_{ij} dx^i dx^j

**Measurement:** To be specified (e.g., physical distance between grid points)

**Existing Measurement:** No physical distance measurement in existing substrate

**Conclusion:** Physical distance definition requires new assumption.

### 8.3 Coordinate Invariance

**Requirement:** |∇ln s|² = g^{ij}(∂_i ln s)(∂_j ln s) must be coordinate-invariant

**Verification:** To be specified (e.g., test under coordinate transformations)

**Existing Verification:** None in existing substrate

**Conclusion:** Coordinate invariance verification requires new assumption.

---

## 9. Dimensional Analysis

### 9.1 Required Units

**c:** [c] = m/s (propagation speed)

**τ:** [τ] = s (damping time constant)

**∇ln s:** [∇ln s] = 1/m (spatial gradient of logarithmic field)

**Q:** [Q] = 1 (dimensionless)

### 9.2 Dimensional Consistency

**Verification:**
```
[4c²τ²|∇ln s|²] = (m/s)² × s² × (1/m)² = 1 ✓
```

**Current Status:** Cannot be verified because no physical units exist in existing substrate.

### 9.3 Violation Points

**Potential Violations:**
- c assigned arbitrary value without physical units
- τ assigned arbitrary value without physical units
- ∇ computed on wrong domain (feature space vs physical space)
- s defined without physical units
- Metric structure missing for coordinate invariance

**Conclusion:** Dimensional consistency cannot be established without introducing physical units.

---

## 10. Legacy Q Mapping

### 10.1 Transport Engine Q

**File:** sim_world/transport/transport_engine.py

**Equation:** Not theoretical Q form

**Inputs:** State distance metrics, topology signatures

**Domain:** Entity state space

**Classification:** **UNRELATED METRIC**

**Justification:** Measures structural change, not transport regime; not theoretical Q form.

### 10.2 Substrate AI Q Field

**File:** substrate_ai/components/q_field.py

**Equation:** Q = 4c²τ²(cosine_distance)² − 1

**Inputs:** Semantic embeddings, text features

**Domain:** Embedding space, feature space

**Classification:** **ENGINEERING PROXY**

**Justification:** Same mathematical form but different objects (cosine distance vs spatial gradient, semantic embeddings vs information density field).

### 10.3 Feature-Space Q (Phase Experiments)

**File:** q_capability_experiment/code/phase2_q_calculation.py

**Equation:** Q = 4c²τ²(feature_gradient)² − 1

**Inputs:** Text features (5 dimensions)

**Domain:** Feature space

**Classification:** **ENGINEERING PROXY**

**Justification:** Same mathematical form but different objects (feature gradient vs spatial gradient, feature space vs physical space).

---

## 11. Artificial-Life Relevance

### 11.1 Substrate Dynamical Ingredients

**Existing Ingredients:**
- Local state (entity needs, inventory, position)
- Spatial organization (grid coordinates, terrain locations)
- **No propagation**
- **No dissipation** (only numerical decay)
- Feedback (needs drive actions, actions affect needs)
- Persistent structures (entities, buildings)
- Local/global coupling (entity-entity interactions)
- **No regime transitions**
- Information transport (conversation, relationships)
- Self-maintenance (needs satisfaction)
- Adaptive behavior (goal-directed actions)
- Emergent organization (social networks)

**Missing Ingredients:**
- Continuous field dynamics
- Propagation mechanisms
- Physical dissipation
- Regime transitions in field dynamics

### 11.2 Q Contribution Analysis

**Q as Diagnostic/Classifier:**
- Could classify field transport regimes if field exists
- Currently no field exists to classify

**Q as Control Variable:**
- Not causal - diagnostic only
- Would require control theory extension

**Q as Causal Mechanism:**
- Not causal - derived from field dynamics
- Does not create dynamics

**Q as Phase-Transition Indicator:**
- Could indicate regime transitions in field dynamics
- Currently no field dynamics exist

### 11.3 Artificial-Life Potential

**Conclusion:** The existing substrate has artificial-life-like ingredients (entities, needs, actions, social networks) but lacks the continuous field dynamics required for Q. Q could contribute to field-based artificial life if the field layer were added, but this requires new physical assumptions.

---

## 12. Minimum Architecture

### 12.1 Architecture Diagram

```
Existing Substrate (Entity Dynamics)
    ↓
Physical Domain (NEW)
    ↓
s(x,t) Information Density Field (NEW)
    ↓
Propagation + Relaxation Dynamics (NEW)
    ↓
Measured c and τ (NEW)
    ↓
Physical Gradient ∇ (NEW)
    ↓
Q(x,t) = 4c²τ²|∇ln s|² − 1 (NEW)
    ↓
Independent Transport-Regime Observables (NEW)
    ↓
Validation (NEW)
```

### 12.2 Layer Specifications

**Existing Substrate:**
- Components: Entity registry, needs domain, weather domain, terrain domain
- State Variables: Entity needs, positions, inventory, relationships
- Dynamics: Discrete state updates, action execution
- Coupling: None to field layer (new coupling required)

**Physical Domain (NEW):**
- Components: Continuous coordinate system, metric structure
- State Variables: Physical coordinates (x, y), metric tensor g_{ij}
- Dynamics: None (static domain)
- Coupling: Maps entity positions to physical coordinates

**s(x,t) Field (NEW):**
- Components: Field representation, discretization, boundary conditions
- State Variables: Field values s(x,t) at lattice points
- Dynamics: Governing equation (to be specified)
- Coupling: Coupled to entity states (mechanism to be specified)

**Propagation + Relaxation (NEW):**
- Components: Propagation mechanism, relaxation mechanism
- State Variables: Field velocity, field derivatives
- Dynamics: Propagation equation, relaxation equation
- Coupling: Field dynamics coupled to entity states

**Measured c and τ (NEW):**
- Components: Perturbation experiments, measurement protocols
- State Variables: c(x,t), τ(x,t) or global constants
- Dynamics: Measurement updates
- Coupling: Measured from field dynamics

**Physical Gradient (NEW):**
- Components: Gradient operator, metric structure
- State Variables: ∇ln s values
- Dynamics: Computed from field
- Coupling: None (diagnostic)

**Q Calculation (NEW):**
- Components: Q computation, regime classification
- State Variables: Q(x,t) values, regime labels
- Dynamics: Computed from field and parameters
- Coupling: None (diagnostic)

**Independent Observables (NEW):**
- Components: Transport regime measurement, validation
- State Variables: Independent regime classifications
- Dynamics: Measured from field dynamics
- Coupling: Independent of Q calculation

**Validation (NEW):**
- Components: Statistical tests, regime comparison
- State Variables: Validation metrics
- Dynamics: Comparison of Q vs independent observables
- Coupling: None (diagnostic)

---

## 13. Assumption Budget

### 13.1 INHERITED Assumptions

**From Existing Substrate:**
- Discrete entity dynamics are valid
- Grid coordinates represent spatial organization
- Time stepping represents temporal progression
- Entity needs represent physiological states
- Action execution represents behavior

**Status:** These are inherited from existing substrate theory.

### 13.2 DERIVED Assumptions

**From Inherited Assumptions:**
- Entity positions can be mapped to physical coordinates (requires mapping assumption)
- Discrete time can be mapped to physical time (requires time unit assumption)
- Entity states can influence field dynamics (requires coupling assumption)

**Status:** These require additional assumptions beyond what is inherited.

### 13.3 NEW Assumptions

**Critical New Assumptions:**

1. **Physical Spatial Domain**
   - **Why Necessary:** Theoretical Q requires continuous physical coordinates with metric structure
   - **What Changes:** Introduces continuous physical space not present in existing substrate
   - **Changes Q Definition:** NO (Q definition requires physical space)
   - **Falsification:** Test coordinate invariance of Q under coordinate transformations

2. **Information Density Field**
   - **Why Necessary:** Theoretical Q requires s(x,t) as information density field
   - **What Changes:** Introduces field representation not present in existing substrate
   - **Changes Q Definition:** NO (Q definition requires s(x,t))
   - **Falsification:** Test whether field evolution matches theoretical transport equation

3. **Propagation Dynamics**
   - **Why Necessary:** c must be measured from propagation, not assigned
   - **What Changes:** Introduces wave/transport equation not present in existing substrate
   - **Changes Q Definition:** NO (Q definition requires measurable c)
   - **Falsification:** Test whether measured c is consistent across perturbations

4. **Relaxation Dynamics**
   - **Why Necessary:** τ must be measured from relaxation, not assigned
   - **What Changes:** Introduces physical relaxation mechanism not present in existing substrate
   - **Changes Q Definition:** NO (Q definition requires measurable τ)
   - **Falsification:** Test whether relaxation law is exponential and τ is consistent

5. **Metric Structure**
   - **Why Necessary:** Coordinate invariance requires metric structure
   - **What Changes:** Introduces physical distance definition not present in existing substrate
   - **Changes Q Definition:** NO (Q definition requires coordinate invariance)
   - **Falsification:** Test whether |∇ln s|² is invariant under coordinate transformations

6. **Physical Units**
   - **Why Necessary:** c and τ require physical units (m/s, s)
   - **What Changes:** Introduces physical units not present in existing substrate
   - **Changes Q Definition:** NO (Q definition requires physical units)
   - **Falsification:** Test dimensional consistency of Q calculation

7. **Field-Entity Coupling**
   - **Why Necessary:** Field must couple to existing substrate dynamics
   - **What Changes:** Introduces coupling mechanism not present in existing substrate
   - **Changes Q Definition:** NO (Q definition does not specify coupling)
   - **Falsification:** Test whether coupling produces coherent field evolution

**Assumption Count:** 7 major new physical assumptions

**Scientific Risk:** HIGH - multiple independent new assumptions required

---

## 14. Validation Strategy

### 14.1 Transport Regime Validation

**Ground Truth:** Independent observables of transport regimes

**Measurement Protocol:**
- Construct controlled field states representing distinct regimes
- Measure independent transport observables (e.g., oscillation frequency, damping rate)
- Compare Q classification against independent observables
- Statistical testing with repeated trials

**Validation Criteria:**
- Q > 0 should correspond to coherent/oscillatory regime
- Q < 0 should correspond to overdamped regime
- Q = 0 should correspond to critical regime
- Classification accuracy above chance level

### 14.2 Parameter Validation

**c Validation:**
- Measure c from independent perturbation experiments
- Test consistency across different perturbations
- Test whether c is constant or state-dependent
- Quantify measurement uncertainty

**τ Validation:**
- Measure τ from independent relaxation experiments
- Test whether relaxation law is exponential
- Test consistency across different perturbations
- Quantify measurement uncertainty

### 14.3 Coordinate Invariance Validation

**Test:** Apply coordinate transformations to field

**Expected Result:** |∇ln s|² should be invariant

**Validation Criterion:** Invariance within numerical tolerance

### 14.4 Dimensional Consistency Validation

**Test:** Verify units in Q calculation

**Expected Result:** Q should be dimensionless

**Validation Criterion:** Dimensional analysis should confirm [Q] = 1

---

## 15. Stop Conditions

**Implementation MUST NOT proceed if:**

1. **s(x,t) cannot be physically defined**
   - No legitimate definition of information density
   - No physical units for information density
   - No operational measurement procedure

2. **No legitimate propagation equation exists**
   - No physically justified propagation equation
   - No way to measure c from dynamics
   - Propagation equation is arbitrary

3. **c cannot be measured**
   - No propagation mechanism to measure
   - c must be assigned arbitrary value
   - No uncertainty quantification for c

4. **τ cannot be measured**
   - No relaxation mechanism to measure
   - τ must be assigned arbitrary value
   - No uncertainty quantification for τ

5. **Metric cannot be defined**
   - No physical distance definition
   - No coordinate invariance
   - Metric structure is arbitrary

6. **Dimensions cannot be made consistent**
   - No physical units for c and τ
   - No dimensional consistency in Q calculation
   - Units are arbitrary

7. **Construction requires redefining Q**
   - Proposed s(x,t) changes theoretical meaning
   - Proposed ∇ changes theoretical meaning
   - Proposed c or τ change theoretical meaning

8. **Construction requires treating semantic features as physical quantities**
   - Text features used as s(x,t)
   - Embedding space used as physical space
   - Cosine distance used as spatial gradient

9. **Proposed dynamics are arbitrary and unsupported**
   - Propagation equation chosen for convenience
   - Relaxation equation chosen for convenience
   - No theoretical justification for equations

---

## 16. Final Classification

**Classification:** **C - CONSTRUCTIBLE ONLY WITH SUBSTANTIAL NEW PHYSICAL ASSUMPTIONS**

**Distinction from "Minimal Extension":**

**Minimal Extension of Existing Substrate:**
- Would require that existing substrate dynamics naturally extend into field dynamics
- Would require that propagation and relaxation mechanisms are implicit in existing equations
- Would require that information density is already present in existing state variables
- Would require that physical coordinates are already present in existing spatial structures

**Actual Situation:**
- Existing substrate contains discrete entity dynamics, not continuous field dynamics
- Existing substrate contains numerical decay, not physical relaxation
- Existing substrate contains no propagation mechanisms
- Existing substrate contains no information density definition
- Existing substrate contains no physical metric structure

**Conclusion:** The missing layer is **NOT** a minimal extension of the existing substrate. It requires introducing **substantial new physical assumptions** that constitute new theory disguised as implementation.

**Required New Assumptions:**
1. Physical spatial domain with metric structure
2. Information density field definition and units
3. Propagation dynamics and equation
4. Physical relaxation mechanism and equation
5. Physical units for c and τ
6. Field-entity coupling mechanism
7. Independent validation observables

**Risk Assessment:**
- **Engineering Risk:** HIGH (complete new layer required)
- **Mathematical Risk:** LOW (theoretical Q is mathematically coherent)
- **Physical-Assumption Risk:** HIGH (7 major new assumptions)
- **Validation Risk:** HIGH (no ground truth for transport regimes)

**Scientific Integrity:** Maintained - no theoretical compromise, clear distinction between extension vs new theory

---

**Specification Status:** COMPLETE  
**Classification:** C - CONSTRUCTIBLE ONLY WITH SUBSTANTIAL NEW PHYSICAL ASSUMPTIONS  
**New Assumptions Required:** 7 major physical assumptions  
**Risk Level:** HIGH  
**Implementation Readiness:** NOT READY - requires theoretical specification of field dynamics before implementation
