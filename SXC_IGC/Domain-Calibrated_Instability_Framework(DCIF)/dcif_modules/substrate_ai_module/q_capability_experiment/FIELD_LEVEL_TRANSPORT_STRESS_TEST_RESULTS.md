# Field-Level Transport Stress Test Results

**Test Date:** 2026-08-09

**Telegraph Equation:** τ ∂²s/∂t² + ∂s/∂t = c²τ ∇²s

**Modal Discriminant:** D(k) = 4c²τ²k² - 1

**Conclusion:** CASE_B: STRUCTURED SPECTRAL OBSERVABLE REQUIRED

---

## Phase Results

### Phase 1: Modal Baseline

- k=0.2500: overdamped, D=-0.7500
- k=0.4000: overdamped, D=-0.3600
- k=0.5000: critical, D=0.0000
- k=0.6000: coherent, D=0.4400
- k=0.7500: coherent, D=1.2500
- k=1.0000: coherent, D=3.0000
- k=1.2566: coherent, D=5.3162

### Phase 2: Amplitude Invariance

Amplitude independent: True

### Phase 3: Two-Mode Mixtures

- A1=0.80, A2=0.20: k_dom=0.2467, f_prop=0.013
- A1=0.50, A2=0.50: k_dom=0.2467, f_prop=0.089
- A1=0.20, A2=0.80: k_dom=0.7401, f_prop=0.216

### Phase 4: Multimode Spectra

- Dominant k: 0.9901
- Propagating power fraction: 0.185
- Overdamped power fraction: 0.815
- Weighted D: -0.3246
- Spectral entropy: 1.351

### Phase 5: 2D Generalization

Agreement: True

### Phase 6: Noise Robustness

- SNR=40dB: k_dom=0.7491
- SNR=20dB: k_dom=0.7491
- SNR=10dB: k_dom=0.7491
- SNR=5dB: k_dom=0.7491

### Phase 7: Resolution Convergence

k_dominant std: 0.000600

### Phase 8: Parameter Sweep

- c=0.5, τ=0.5: k_dom=3.9747
- c=0.5, τ=1.0: k_dom=1.9937
- c=0.5, τ=2.0: k_dom=0.9984
- c=1.0, τ=0.5: k_dom=1.9937
- c=1.0, τ=1.0: k_dom=0.9984
- c=1.0, τ=2.0: k_dom=0.4996
- c=2.0, τ=0.5: k_dom=0.9984
- c=2.0, τ=1.0: k_dom=0.4996
- c=2.0, τ=2.0: k_dom=0.2499

## Decision Criteria

- amplitude_independence: True
- two_mode_stability: True
- multimode_meaningful: True
- 2d_validity: True
- noise_robustness: True
- resolution_convergence: True
- parameter_validity: True

---

## Final Decision

**CASE_B: STRUCTURED SPECTRAL OBSERVABLE REQUIRED**

