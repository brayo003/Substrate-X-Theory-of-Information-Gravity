# Document 17 — Preregistered Experiment Design
## Phase 9: Joint d_c + τ_B C2 Spatiotemporal Test

**Date preregistered:** 2026-08-20  
**Platform:** SIMULATION (pure Python/NumPy — no IBM QPU access available)  
**Rationale for simulation:** IBM free-tier QPU access is blocked (confirmed constraint).  
The simulation uses the exact C2 coherence formula [EXACT-PHI] and a realistic heavy-hex  
qubit geometry. All parameters are set BEFORE script execution. Results are not modified post-hoc.

**Preregistration commitment:** This document is written before any scripts are run.  
Any deviation from this plan is flagged explicitly in the results documents.

---

## 1. Scientific Objective

Test the C2 consistency relation:

```
c_C2 = d_c / τ_B
```

where:
- `d_c` is measured from the spatial decay length of inter-qubit phase-noise correlations
- `τ_B` is measured from the temporal shape of Ramsey coherence decay on each qubit
- `c_C2` is the substrate propagation speed, independently predicted by C2 to be ~c_light × some factor

These two quantities are measured from **different observables** (temporal vs. spatial) but must  
converge to a single value of c_C2 if C2 is correct. This is the decisive test that prior  
Ramsey-shape-only experiments could not perform.

---

## 2. Platform Specification

| Parameter | Value |
|-----------|-------|
| Platform | Pure simulation (Python 3.10, NumPy, SciPy) |
| QPU model | Simulated IBM heavy-hex 7-qubit (Falcon r5 geometry) |
| Qubit count | 7 qubits (Q00–Q06) |
| Shots per Ramsey point | 8192 (shot noise included via binomial sampling) |
| Delay points | 50 log-spaced from 100 ns to 500 µs |
| Spatial repetitions | 200 independent noise realizations per qubit pair |
| Noise realizations | 500 per qubit (for correlation matrix estimation) |

**Why 7 qubits:** Standard IBM Falcon heavy-hex minimum. Provides 6 nearest-neighbor pairs,  
3 next-nearest pairs — enough to fit a spatial decay length d_c.

---

## 3. Qubit Geometry (Heavy-Hex, Simulated)

IBM Falcon r5 heavy-hex layout (7 qubits, simplified):

```
Q00 --- Q01 --- Q02
        |
        Q03 --- Q04 --- Q05
                |
                Q06
```

Physical coordinates (µm, from IBM calibration data in 06_datasets/):

| Qubit | x (µm) | y (µm) |
|-------|---------|---------|
| Q00   | 0       | 0       |
| Q01   | 200     | 0       |
| Q02   | 400     | 0       |
| Q03   | 200     | 200     |
| Q04   | 400     | 200     |
| Q05   | 600     | 200     |
| Q06   | 400     | 400     |

Nearest-neighbor spacing: `a = 200 µm` (standard IBM heavy-hex pitch).

---

## 4. C2 Parameters Used for Simulation (Pre-set, Not Fitted)

These are the **injection values** for the synthetic data. Recovery of these values is the test.

| Parameter | Symbol | Injection value | Source |
|-----------|--------|-----------------|--------|
| Substrate speed | c_C2 | 1.0 × 10⁴ m/s | C2 theory order-of-magnitude |
| Bath correlation time | τ_B | 5.0 µs | Mid-range of C2-compatible regime |
| Spatial coherence length | ξ_c = 2c·τ_B | 0.1 m = 100,000 µm | Derived |
| Dephasing amplitude | Γ_M | 2π × 50 kHz | Typical IBM T2* = ~3 µs |
| NMP = Γ_M · τ_B | NMP | 1.57 | Non-Markovian regime |
| Common-mode fraction | f_cm | 0.20 | 20% correlated environmental noise |

**Critical note:** At ξ_c = 100,000 µm and qubit spacing 200–800 µm, all qubit pairs have  
d/ξ_c < 0.01. This means inter-qubit correlations are measurable but require accurate  
background subtraction. The experiment is sensitive at the correct scale.

---

## 5. Exact C2 Coherence Formula [EXACT-PHI]

From `11_v02_extension/NM_PREDICTION_AUDIT.md`, verified by `nm_01_memory_kernel.py`:

```
ρ₀₁(t) = exp(-Φ(t))

Φ(t) = Γ_M · τ_B · [t/τ_B - 1 + exp(-t/τ_B)]
```

where `Γ_M = 2g² S₀ τ_B / ℏ²` (Markov rate).

**Single-qubit decay (no spatial correlation):**  
```
C_Ramsey(t) = cos(Ω·t) · exp(-Φ(t))
```

**Cross-qubit phase correlation (C2 prediction, from 02_2D_CORRELATION_DERIVATION.md):**
```
Corr(i,j) = exp(-d_ij / ξ_c) · [spatial decay from PRW Green's function]
```

where `d_ij = |r_i - r_j|` and `ξ_c = 2c·τ_B = 2·d_c·τ_B/τ_B = 2·d_c`.

**Structural degeneracy:** The C2 non-Markovian coherence formula is mathematically identical  
to an OU-process (Ornstein-Uhlenbeck / colored noise) coherence function. This is a known  
identifiability limitation. The temporal data alone cannot distinguish them. Only the joint  
test (c_C2 = d_c/τ_B converging from two independent observables) provides additional leverage.

---

## 6. Analysis Plan (Pre-specified)

### 6.1 Temporal Analysis (p18_ramsey_fit.py)

For each qubit q_i, fit four models to the Ramsey trace `C(t)`:

| Model | Function | Free params | k |
|-------|----------|-------------|---|
| Exponential | exp(-Γ·t) | Γ | 2 (Γ + A) |
| Gaussian | exp(-(t/T_G)²) | T_G | 2 |
| Stretched-exp | exp(-(t/T_S)^β) | T_S, β | 3 |
| C2-exact [EXACT-PHI] | exp(-Φ(t; Γ_M, τ_B)) | Γ_M, τ_B | 3 |

Model selection via AIC = 2k - 2·ln(L) and BIC = k·ln(n) - 2·ln(L).

**Extract:** τ_B_q with 1σ uncertainty from the C2-exact fit profile likelihood.

### 6.2 Spatial Analysis (p19_spatial_correlator.py)

Construct phase-noise correlation matrix C_ij from Ramsey residuals.  
Fit three models to C_ij vs. d_ij:

| Model | Function | Free params |
|-------|----------|-------------|
| K0 (PRW 2D) | K₀(d/ξ_c) · A | ξ_c, A |
| Exponential | exp(-d/d_c) · A | d_c, A |
| Null | A (constant) | A |

**Extract:** d_c with 1σ uncertainty.

### 6.3 Joint Test (p20_joint_c2_test.py)

Compute per-pair:
```
c_C2_measured(i,j) = d_c_ij / τ_B_mean
```

Test:
1. Stability: coefficient of variation of c_C2 across pairs < 30%
2. Consistency with injection value: within 2σ of c_C2_injected = 1.0×10⁴ m/s
3. Subset stability: randomly split qubits, check c_C2 consistent across halves

### 6.4 Null Tests (p21_null_tests.py)

Fit conventional OU (Lorentzian noise) model to all data.  
Compare AIC/BIC against C2 models.  
Extract common-mode fraction.  
**Decision rule:** if ΔIC < 2 for OU vs. C2 on any observable, that observable provides no  
discriminatory power. Report honestly.

### 6.5 Synthetic Recovery (p22_synthetic_recovery.py)

Inject c_C2 ∈ {10², 10³, 10⁴, 10⁵, 10⁶} m/s.  
Inject τ_B/T2* ∈ {0.01, 0.1, 0.5, 1.0, 5.0, 10.0}.  
Attempt blind recovery using the analysis pipeline.  
Report recovery fraction and bias.

---

## 7. Decision Criteria (Pre-specified)

### C2 JOINTLY SUPPORTED — requires ALL of:
- [ ] C2-exact fit preferred over exponential AND Gaussian by ΔBIC > 6 on ≥ 5/7 qubits
- [ ] d_c extracted with CV < 50%
- [ ] τ_B extracted from Ramsey with CV < 50% across qubits
- [ ] c_C2 = d_c/τ_B within factor 3 of C2 prediction
- [ ] c_C2 stable across ≥ 2 independent subset splits
- [ ] OU model explains worse than C2 by ΔBIC > 4

### COMPATIBLE / UNDERDETERMINED — requires:
- C2 fits are not rejected, but criteria above not all met
- OR OU model explains equally well (ΔIC < 2)

### DISFAVORED — requires:
- C2-exact fit significantly worse than simpler model (ΔBIC > 6 for simpler)
- OR c_C2 from joint test differs from injection by > 5σ

### TECHNICALLY INCONCLUSIVE — if:
- τ_B parameter is unbounded (hits prior limits)
- OR d_c cannot be extracted from spatial data
- OR SNR < 3 on spatial correlations

---

## 8. Conventional Null Tests

The following alternative hypotheses must be tested and reported honestly:

1. **Pure quasistatic (Gaussian decay):** τ_B → ∞, Gaussian shape. Compatible with C2 slow-bath regime AND with 1/f noise.
2. **OU/Lorentzian:** Mathematically identical to C2 [EXACT-PHI]. Cannot be distinguished from temporal data alone.
3. **Uncorrelated noise:** Spatial C_ij = δ_ij × σ². Tests whether any spatial signal exists.
4. **Common-mode:** All qubits see the same bath fluctuation. Mimics spatial correlation.

---

## 9. Known Limitations and Honest Caveats

1. **Structural degeneracy:** C2 [EXACT-PHI] ≡ OU colored noise under Ramsey. This is fundamental, not experimental. The temporal data alone cannot resolve it.

2. **Simulation is not hardware:** The synthetic data is generated from the exact injection model. This guarantees recovery in the identifiable regime. Hardware would add unknown systematics, crosstalk, gate errors. **Simulation results cannot be treated as hardware evidence.**

3. **Spatial signal at d/ξ_c ≪ 1:** All qubit pairs have d << ξ_c at the injected parameters. This means spatial correlation is nearly flat — d_c will have large uncertainty unless ξ_c < chip size. This is a fundamental limitation of 7-qubit chips for this test.

4. **c_C2 theory value:** The C2 theory does not give a sharp numerical prediction for c_C2. The "prediction" is that c_C2 is consistent across conditions. Matching the injection value is a self-consistency check, not an independent test.

---

## 10. Files to Be Produced

| Document | Content |
|----------|---------|
| `scripts/p17_ramsey_sim.py` | Synthetic data generator |
| `scripts/p18_ramsey_fit.py` | Temporal model fitting |
| `scripts/p19_spatial_correlator.py` | Spatial correlation analysis |
| `scripts/p20_joint_c2_test.py` | Joint c_C2 computation |
| `scripts/p21_null_tests.py` | Conventional null model comparison |
| `scripts/p22_synthetic_recovery.py` | Blind recovery mapping |
| `outputs/data/ramsey_sim.npz` | Raw simulated Ramsey traces |
| `outputs/data/spatial_corr.npz` | Phase-noise correlation matrices |
| `outputs/figures/` | All figures |
| `18_RAMSEY_RESULTS_SIM.md` | Temporal fit results |
| `19_SPATIAL_RESULTS_SIM.md` | Spatial analysis results |
| `20_JOINT_C2_TEST_SIM.md` | Joint test results |
| `21_CONVENTIONAL_NULL_TESTS_SIM.md` | Null model comparison |
| `22_SYNTHETIC_RECOVERY_SIM.md` | Recovery map |
| `23_DECISION_AND_VERDICT.md` | 20-question verdict |
| `SESSION_CHECKPOINT.md` | Hard verdict |

---

*End of preregistration. Scripts will be executed in order p17→p22. No modifications to the analysis plan after execution begins.*
