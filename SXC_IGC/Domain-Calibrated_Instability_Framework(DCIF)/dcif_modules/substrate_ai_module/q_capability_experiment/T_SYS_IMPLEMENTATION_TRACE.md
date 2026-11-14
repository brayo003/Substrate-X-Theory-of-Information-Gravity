# T_sys IMPLEMENTATION TRACE

**Analysis Date:** 2026-08-09  
**Component:** SXCOmegaEngine  
**File:** substrate_ai/components/sxc_omega_v12.py  
**Lines:** 1-38

---

## EXACT IMPLEMENTATION ANALYSIS

### Class Definition
```python
class SXCOmegaEngine:
    def __init__(self):
        self.T_sys = 0.0
        self.phase = "NOMINAL"
        self.gamma_max = 0.8
        self.gamma = self.gamma_max
        self.beta = 3.5
        self.dt = 0.05
        self.decay_rate = 0.0005 
```

**State Variables:**
- `T_sys`: System temperature (float, initialized to 0.0)
- `phase`: Operating regime (string, "NOMINAL" or "FIREWALL")
- `gamma`: Transport coefficient (float, initialized to 0.8)
- `gamma_max`: Maximum gamma (float, constant 0.8)

**Parameters:**
- `beta`: Excitation coefficient (float, constant 3.5)
- `dt`: Integration timestep (float, constant 0.05)
- `decay_rate`: Gamma decay rate (float, constant 0.0005)

---

## EXACT ODE EQUATIONS

### Step Function (lines 25-38)
```python
def step(self, signal):
    self.gamma *= (1 - self.decay_rate)
    E = self.excitation_flux(signal)
    gamma_eff = 2.2 if self.phase == "FIREWALL" else 1.0
    inflow = E * self.beta
    outflow = gamma_eff * self.gamma * self.T_sys
    self.T_sys += (inflow - outflow) * self.dt
    
    if self.T_sys > 1.0:
        self.phase = "FIREWALL"
    elif self.phase == "FIREWALL" and self.T_sys < 0.4:
        self.phase = "NOMINAL"
        
    return self.T_sys, self.phase
```

**Mathematical Form:**
```
γ(t+dt) = γ(t) × (1 - decay_rate)
E(t) = excitation_flux(signal(t))
γ_eff(t) = 2.2 if phase = "FIREWALL" else 1.0
inflow(t) = E(t) × β
outflow(t) = γ_eff(t) × γ(t) × T_sys(t)
T_sys(t+dt) = T_sys(t) + (inflow(t) - outflow(t)) × dt
```

### Excitation Flux Function (lines 13-16)
```python
def excitation_flux(self, signal):
    if signal < 45:
        return 1 - np.exp(-signal / 40.0)
    return 0.675 + ((signal - 45.0) / 20.0)
```

**Mathematical Form:**
```
E(signal) = 1 - exp(-signal/40)    if signal < 45
E(signal) = 0.675 + (signal-45)/20  if signal ≥ 45
```

**Behavior:**
- Sigmoidal saturation for low signals (0 < E < 1)
- Linear growth for high signals (E > 0.675)
- Continuous at signal = 45 (both give E ≈ 0.675)

---

## PHASE TRANSITION LOGIC

### NOMINAL → FIREWALL (lines 33-34)
```python
if self.T_sys > 1.0:
    self.phase = "FIREWALL"
```

**Threshold:** T_sys > 1.0

### FIREWALL → NOMINAL (lines 35-36)
```python
elif self.phase == "FIREWALL" and self.T_sys < 0.4:
    self.phase = "NOMINAL"
```

**Threshold:** T_sys < 0.4 (only when already in FIREWALL)

**Hysteresis:** 0.4 < T_sys < 1.0 maintains current phase

---

## INTERVENTION MECHANISM

### Apply Intervention Function (lines 18-23)
```python
def apply_intervention(self, type="MICRO"):
    if type == "DEEP":
        self.gamma = min(self.gamma_max, self.gamma * 1.15)
        self.T_sys *= 0.60 # The 40% MED Flush
    else:
        self.gamma = min(self.gamma_max, self.gamma * 1.05)
```

**Types:**
- `DEEP`: Increases gamma by 15%, reduces T_sys by 40%
- `MICRO`: Increases gamma by 5%

**Effects:**
- Higher gamma increases outflow term in ODE
- Direct T_sys reduction in DEEP intervention
- Gamma bounded by gamma_max (0.8)

---

## INPUT/OUTPUT ANALYSIS

### Inputs
- `signal`: Numeric value (typically word count from LLM response)
- `type`: String for intervention type ("MICRO" or "DEEP")

### Outputs
- `T_sys`: Current system temperature (float)
- `phase`: Current operating regime (string)

### Internal State
- `gamma`: Transport coefficient (evolves over time)
- All parameters (constants)

---

## DYNAMICAL PROPERTIES

### Memory/State Persistence
- T_sys carries history through ODE integration
- Gamma decays over time (memory of interventions)
- Phase has hysteresis (different thresholds for transitions)

### Temporal Behavior
- Integration timestep: dt = 0.05
- Gamma decay rate: 0.0005 per step
- Phase response threshold: T_sys > 1.0
- Recovery threshold: T_sys < 0.4

### Non-linearity
- Excitation flux: sigmoidal + linear piecewise
- Outflow: quadratic in T_sys (through gamma × T_sys)
- Intervention: multiplicative effects

---

## EXACT PARAMETER VALUES

| Parameter | Value | Meaning |
|-----------|-------|---------|
| T_sys_init | 0.0 | Initial temperature |
| gamma_max | 0.8 | Maximum transport coefficient |
| gamma_init | 0.8 | Initial transport coefficient |
| beta | 3.5 | Excitation coefficient |
| dt | 0.05 | Integration timestep |
| decay_rate | 0.0005 | Gamma decay per step |
| firewall_threshold | 1.0 | T_sys threshold for FIREWALL |
| recovery_threshold | 0.4 | T_sys threshold for recovery |
| excitation_knee | 45.0 | Signal value for flux piecewise change |
| gamma_eff_firewall | 2.2 | Enhanced outflow in FIREWALL phase |

---

## COMPUTATIONAL INTERPRETATION

**T_sys represents:**
- Accumulated excitation from input signals over time
- Temporally smoothed measure of system stress
- Memory of past interventions through gamma decay
- Phase-based response amplification (FIREWALL increases outflow)

**Mathematical category:**
- First-order nonlinear ODE with piecewise excitation
- Hysteretic phase transitions
- Bounded state (implicitly through outflow term)

**Control characteristics:**
- Integrates input signal over time
- Has built-in phase classification
- Supports intervention mechanisms
- Exhibits memory and hysteresis

---

## INTEGRATION POINTS

**Where T_sys is used:**
- UnifiedGovernor: `self._sxc.T_sys` as sensor input
- Decision logic: Phase classification for control decisions
- Cognitive state: `T_sys` field in cognitive_state dict

**Signal source:**
- Typically word count from LLM response
- Can be any numeric excitation signal

**Control outputs:**
- Phase (NOMINAL/FIREWALL) for governor decisions
- T_sys value for continuous control signals
- Intervention capability through apply_intervention()

---

## IMPLEMENTATION TRACE SUMMARY

**File:** substrate_ai/components/sxc_omega_v12.py  
**Lines:** 1-38  
**Complexity:** Low (single class, 3 methods)  
**Dependencies:** numpy only  
**State dimension:** 2 (T_sys, phase) + 1 hidden (gamma)  
**External inputs:** 1 (signal)  
**External controls:** 1 (intervention type)

**Mathematical form:**
```
dT_sys/dt = β×E(signal) - γ_eff×γ×T_sys
dγ/dt = -decay_rate×γ
phase = f(T_sys, phase_history)
```

**Key dynamical features:**
1. Temporal integration (ODE accumulation)
2. Non-linear excitation (sigmoidal + linear)
3. Phase-dependent response (FIREWALL amplification)
4. Hysteresis (different up/down thresholds)
5. Intervention mechanism (gamma modification + direct T_sys reduction)

---

**Trace Status:** COMPLETE  
**Implementation Verified:** YES  
**Mathematical Form:** EXACT  
**Parameters:** EXACT  
**Dynamics:** FULLY CHARACTERIZED
