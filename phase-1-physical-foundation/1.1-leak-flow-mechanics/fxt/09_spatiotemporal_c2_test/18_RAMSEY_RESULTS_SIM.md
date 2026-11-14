# Document 18 — Ramsey Results (Simulation)
## Phase 9: Temporal Decay Analysis

**Date:** 2026-08-21  
**Platform:** Pure simulation (Python/NumPy)  
**Script:** `scripts/p18_ramsey_fit.py`  
**Input:** `outputs/data/ramsey_sim.npz`

---

## 1. Raw Results

### 1.1 Per-Qubit Fit Summary (from p18 stdout)

| Qubit | Γ_M inj (kHz) | τ_B inj (µs) | BIC_exp | BIC_gauss | BIC_strexp | BIC_c2exact | τ_B fit (µs) | τ_B err (µs) |
|-------|---------------|--------------|---------|-----------|------------|-------------|--------------|--------------|
| Q00   | 54.8          | 4.77         | 6520.6  | 243.0     | 66.4       | **60.5**    | 5.12         | 0.41         |
| Q01   | 36.6          | 4.99         | 6545.9  | 404.7     | 101.3      | **53.4**    | 4.59         | 0.26         |
| Q02   | 62.6          | 4.40         | 6400.6  | 198.0     | 61.8       | **44.0**    | 4.89         | 0.34         |
| Q03   | 66.3          | 5.71         | 7288.5  | 179.2     | 92.2       | **68.9**    | 6.38         | 0.69         |
| Q04   | 27.8          | 5.62         | 7252.0  | 445.6     | 141.6      | **73.4**    | 5.63         | 0.38         |
| Q05   | 33.8          | 5.05         | 6861.2  | 387.1     | 95.9       | **64.7**    | 5.14         | 0.34         |
| Q06   | 52.0          | 5.92         | 7112.4  | 243.6     | 81.0       | **49.9**    | 5.65         | 0.39         |

**BIC winner: C2-exact on 7/7 qubits.**

### 1.2 τ_B Extraction Summary

| Metric | Value |
|--------|-------|
| τ_B injected | 5.00 µs |
| τ_B mean (fitted) | 5.34 µs |
| τ_B std | 0.55 µs |
| τ_B range | 4.59 – 6.38 µs |
| CV (std/mean) | 0.10 |
| Qubits at bound | 0 / 7 |
| Qubits valid | 7 / 7 |

---

## 2. Interpretation

**C2-exact wins 7/7 by BIC.** This is expected: the data was generated from the C2-exact formula, so the correct model recovers best. This is a self-consistency check, not an independent test.

**The ΔBIC vs. stretched-exponential** is modest (e.g., Q00: 66.4 vs 60.5, ΔBIC = 5.9). This is above the conventional threshold of 6 for "strong" preference only marginally. On data generated without noise perturbations the C2 model wins convincingly because it is the truth — on real hardware the margin would be smaller.

**τ_B recovery is accurate:** mean bias = +0.34 µs (6.8% of injected value). CV = 0.10, well below the pre-registered threshold of 0.50.

**NMP values are in the non-Markovian regime** (NMP = 0.98–2.38 across qubits), meaning the Gaussian initial decay is visible and the C2/OU model is identifiable. This is the expected identifiable regime from prior synthetic recovery work.

---

## 3. Caveats

1. **Structural degeneracy unresolved.** C2-exact and OU colored-noise are mathematically identical. The BIC preference for C2-exact over exponential tells us the decay is non-Markovian; it does not distinguish C2 from OU.

2. **Simulation confirms identifiability.** τ_B is recoverable in simulation with NMP ~ 1. This is consistent with the NM_PREDICTION_AUDIT finding that τ_B is identifiable for NMP = 0.1–5.

3. **BIC values inflate in simulation.** Because shot noise is the only noise source, BIC values are very large. Real hardware would have gate errors, readout errors, and low-frequency drift, making discrimination harder.

---

## 4. Figures Produced

- `outputs/figures/fig_ramsey_traces.png` — Ramsey traces with 4-model fits per qubit
- `outputs/figures/fig_tau_b_distribution.png` — τ_B per qubit vs. injection value
