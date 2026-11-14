# Document 26 — Provider and Hardware Audit
## Phase 9: Frequency-Domain Experiment

**Date:** 2026-08-21  
**Auditor:** adversarial (all claims verified against shell output)

---

## 1. Environment Scan Results

### 1.1 Installed Quantum Packages

| Package | Version | Status |
|---------|---------|--------|
| qiskit | 2.3.1 | Installed |
| qiskit-ibm-runtime | 0.45.1 | Installed, NO credentials |
| qiskit-aer | — | **NOT INSTALLED** |
| amazon-braket-sdk | — | **NOT INSTALLED** |
| pennylane | — | **NOT INSTALLED** |
| pyquil (Rigetti) | — | **NOT INSTALLED** |
| pytket-quantinuum | — | **NOT INSTALLED** |
| ionq-cli | — | **NOT INSTALLED** |
| qibo | — | **NOT INSTALLED** |

### 1.2 Available Qiskit Primitives

```
qiskit.primitives.StatevectorSampler   — available (exact statevector simulation)
qiskit.primitives.StatevectorEstimator — available (exact expectation values)
qiskit_aer.AerSimulator               — NOT available (ModuleNotFoundError)
```

### 1.3 Credentials and API Keys

| Service | Credential | Status |
|---------|-----------|--------|
| IBM Quantum | ~/.qiskit/qiskit-ibm.json | **NOT FOUND** |
| IBM Quantum | Environment variable | **NOT SET** |
| AWS Braket | ~/.aws/credentials | **NOT FOUND** |
| AWS Braket | ~/.aws/config | **NOT FOUND** |
| IonQ | Config file | **NOT FOUND** |
| Rigetti | Config file | **NOT FOUND** |
| Quantinuum | Config file | **NOT FOUND** |
| HuggingFace | HF_TOKEN env var | Present (not quantum) |

### 1.4 Verdict

**No real QPU access is available.**

The only executable quantum simulation path is:
- `qiskit.primitives.StatevectorSampler` — exact statevector simulation with shot sampling
- `qiskit.primitives.StatevectorEstimator` — exact expectation values
- Pure NumPy/SciPy noise simulation (no quantum circuit overhead)

---

## 2. Assessment Against Provider Requirements

| Requirement | Available? | Notes |
|-------------|-----------|-------|
| Real QPU access | ✗ NO | No credentials for any service |
| Terminal/Python API | ✓ YES | StatevectorSampler available |
| Repeated circuit execution | ✓ YES | In simulation |
| Enough shots for correlation | ✓ YES | Unlimited in simulation |
| Multiple qubits | ✓ YES | Up to ~20 in statevector sim |
| Frequency-domain capability | ✓ YES | Via repeated Ramsey at varied delays |
| Cross-qubit noise correlation | Partial | Requires correlated noise injection |

---

## 3. What Can Be Done Without Real QPU

### 3.1 The Frequency-Domain Protocol (Simulation-Only)

A frequency-domain cross-noise experiment can be simulated by:

1. Generating a time series of repeated Ramsey phase measurements at fixed short delay τ
2. Fourier-transforming the time series to obtain a noise power spectrum S(f)
3. Computing the cross-spectral density (CSD) between qubit pairs: S_ij(f)
4. Fitting the spectrum shape to extract τ_B = 1/(2πf_0) where f_0 is the Lorentzian corner

This requires no QPU — it is a noise spectroscopy protocol executable with StatevectorSampler.

### 3.2 Critical Degeneracy Question (addressed in Doc 24)

Before executing: determine whether S_ij(f) under C2 differs from S_ij(f) under OU.

If they are identical: the experiment is non-diagnostic before hardware execution.

---

## 4. Decision

**STOP before claiming hardware experiment.**

Since no real QPU is accessible:
- Document 27 will record this blocker honestly
- The simulation in Document 25 will test whether the frequency-domain observable is
  diagnostic (distinguishes C2 from OU) at all
- If non-diagnostic: the correct result is EXPERIMENT NON-DIAGNOSTIC
- If diagnostic: document the hardware requirement precisely

No hardware data will be presented, fabricated, or substituted with simulation.
