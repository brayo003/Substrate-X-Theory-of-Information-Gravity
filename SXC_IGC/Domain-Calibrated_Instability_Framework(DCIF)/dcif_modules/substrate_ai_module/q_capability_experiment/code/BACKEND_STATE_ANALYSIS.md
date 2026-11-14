================================================================================
BACKEND STATE VARIABLE ANALYSIS
================================================================================

## BACKEND COMPONENT SCAN

### unified_governor
Variables found: 4
- Q: Transport regime classifier Q = 4c²τ²|∇ln s|² - 1
- tension: Problem difficulty/complexity metric
- regime: Operating regime classification
- T_sys: System temperature from V12 ODE

### cognitive_governor
Variables found: 2
- tension: Problem difficulty/complexity metric
- regime: Operating regime classification

### problem_analyzer
Variables found: 2
- Q: Transport regime classifier Q = 4c²τ²|∇ln s|² - 1
- tension: Problem difficulty/complexity metric

### substrate_core
Variables found: 2
- tension: Problem difficulty/complexity metric
- regime: Operating regime classification

### substrate_ai
Variables found: 2
- tension: Problem difficulty/complexity metric
- regime: Operating regime classification

### adaptive_thinker
Variables found: 1
- tension: Problem difficulty/complexity metric

### q_field
Variables found: 3
- Q: Transport regime classifier Q = 4c²τ²|∇ln s|² - 1
- tension: Problem difficulty/complexity metric
- regime: Operating regime classification

## CANDIDATE Q-LIKE VARIABLES

### Candidate 1: Q_from_QField
Source: QField
Type: continuous
Range: [-1, 3] (theoretical) or varies (implementation)
Update Frequency: Per inference cycle
Theoretical Meaning: Transport regime classifier Q = 4c²τ²|∇ln s|² - 1
Actual Meaning: Semantic distance between text embeddings (proven by previous audit)
Control Potential: Low - proven to be semantic distance, not transport dynamics

### Candidate 2: T_sys
Source: SXCOmegaEngine
Type: continuous
Range: [0, 1] (normalized)
Update Frequency: Per ODE timestep
Theoretical Meaning: System temperature from V12 transport equation
Actual Meaning: Dynamic state variable from ODE system
Control Potential: High - dynamic, temporal, has physical basis

### Candidate 3: tension
Source: ProblemAnalyzer
Type: continuous
Range: [0, 1] (normalized)
Update Frequency: Per query
Theoretical Meaning: Problem difficulty/complexity metric
Actual Meaning: Heuristic based on keyword detection and feature extraction
Control Potential: Medium - heuristic but potentially useful

### Candidate 4: regime
Source: SubstrateDynamics
Type: categorical
Range: {'narrative_ok', 'transitional', 'formal_required'}
Update Frequency: Per query
Theoretical Meaning: Operating regime classification
Actual Meaning: Threshold-based classification on tension
Control Potential: Medium - categorical but potentially useful

### Candidate 5: Q_synthetic
Source: UnifiedGovernor (potential)
Type: continuous
Range: To be determined
Update Frequency: Per inference cycle
Theoretical Meaning: Composite state variable combining multiple signals
Actual Meaning: Could combine T_sys, tension, Q from QField
Control Potential: High - could leverage multiple information sources

## PRELIMINARY ASSESSMENT

High Control Potential: 2
  - T_sys (SXCOmegaEngine)
  - Q_synthetic (UnifiedGovernor (potential))

Medium Control Potential: 2
  - tension (ProblemAnalyzer)
  - regime (SubstrateDynamics)

Low Control Potential: 1
  - Q_from_QField (QField)

## PRELIMINARY RECOMMENDATIONS

PRIORITY: Test high-control-potential variables first:
  - T_sys: Focus experimental effort here
  - Q_synthetic: Focus experimental effort here

SECONDARY: Test medium-control-potential variables:
  - tension: Test if high-potential variables fail
  - regime: Test if high-potential variables fail

DEPRIORATE: Low-control-potential variables:
  - These are unlikely to provide the required autonomous control function
  - Only test if all higher-potential options fail

================================================================================