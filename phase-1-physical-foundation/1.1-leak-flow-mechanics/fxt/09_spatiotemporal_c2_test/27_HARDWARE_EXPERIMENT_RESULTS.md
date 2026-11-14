# Document 27 — Hardware Experiment Results
## Phase 9: Frequency-Domain Experiment

**Date:** 2026-08-21

---

## Hardware Attempt: BLOCKED

No hardware experiment was executed. This document records the exact blocker.

### Blocker 1: No QPU credentials

- IBM Quantum: no `~/.qiskit/qiskit-ibm.json`, no env var
- AWS Braket: no `~/.aws/credentials`, SDK not installed
- IonQ: not installed, no API key
- Rigetti: not installed, no API key
- Quantinuum: not installed, no API key

All non-IBM providers were checked. None are accessible.

### Blocker 2: Simulation is pre-determined to be non-diagnostic

The frequency-domain simulation (Document 25) established that the CSD experiment
cannot distinguish C2 from OU at d << ξ_c. Even if QPU access were available, running
it on real hardware would not produce a diagnostic result given the chip geometry.

Running the experiment on real hardware would add:
- Gate errors (~0.1–1% per gate)
- Readout errors (~1–5%)
- Calibration drift over 10ms acquisition windows
- Unknown crosstalk

These additional noise sources would further obscure the already-absent spatial signal.

### Blocker 3: The decisive test requires hardware not yet manufactured

The joint test c_C2 = d_c/τ_B requires qubit separations of order ξ_c ~ 10 cm.
No existing superconducting QPU has qubits at centimeter-scale separations.

---

## What Would Be Required for a Hardware Experiment

| Requirement | Status |
|-------------|--------|
| QPU with d ~ ξ_c (several cm qubit spacing) | Not available anywhere |
| IBM/Braket/IonQ credentials | Not available in this environment |
| Qiskit Aer for noise-model simulation | Not installed |
| Alternative: cold atoms / NV centers with tunable geometry | Not accessible |

---

## Honest Statement

No hardware data exists. No hardware experiment was attempted (credentials absent).
No simulation result is labelled as hardware evidence.

The project status from Documents 19–25 stands:

**C2 QUANTUM LAYER: COMPATIBLE / UNDERDETERMINED**

The frequency-domain simulation confirms this verdict is unchanged by the new
experiment design: the observable is non-diagnostic, regardless of hardware access.
