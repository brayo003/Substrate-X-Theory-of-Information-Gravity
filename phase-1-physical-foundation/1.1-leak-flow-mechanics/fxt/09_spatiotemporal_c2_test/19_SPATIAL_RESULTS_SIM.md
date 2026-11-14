# Document 19 — Spatial Correlation Results (Simulation)
## Phase 9: Spatial Decay Analysis

**Date:** 2026-08-21  
**Platform:** Pure simulation  
**Script:** `scripts/p19_spatial_correlator.py`

---

## 1. Raw Results

### 1.1 Pearson Correlation Matrix (all off-diagonal near 0.997)

All inter-qubit phase-noise correlations are in range **0.9949 – 0.9985**. The correlation matrix is nearly uniform — no visible spatial decay across the chip.

### 1.2 Pair Correlations vs. Distance

| Separation | Pairs | Mean corr |
|------------|-------|-----------|
| 200 µm (NN) | 7 | 0.9982 |
| 283 µm | 6 | 0.9976 |
| 400 µm | 3 | 0.9966 |
| 447 µm | 3 | 0.9962 |
| 566 µm | 1 | 0.9951 |
| 632 µm (max) | 1 | 0.9949 |

Trend: correlation decreases by ~0.003 from NN to max. This is a 0.3% variation over a factor of 3 in distance.

### 1.3 Model Fits (CM-subtracted)

| Model | AIC | SSE |
|-------|-----|-----|
| Exponential | -276.27 | 3.4 × 10⁻⁵ |
| **Null (flat)** | **-286.15** | **2.3 × 10⁻⁵** |

**ΔAIC(null − exp) = −9.88:** Null model preferred over exponential by ΔAIC > 2.

### 1.4 d_c Extraction

- Exponential fit converged: ξ_c = 22.7 ± **436.1 µm**
- d_c = 11.3 ± **218.1 µm**
- d_c injected (= ξ_c/2): 50,000 µm
- **d_c is off by factor ~4,400 from injection value**

---

## 2. Why Spatial Extraction Failed

The fundamental problem is geometric: **ξ_c = 100,000 µm, chip size = 632 µm.**

The ratio d_max/ξ_c = 0.006. At this ratio, the exponential `exp(-d/ξ_c)` varies by only:

```
exp(-0) - exp(-0.006) = 1 - 0.994 = 0.006  (0.6%)
```

This 0.6% variation is swamped by:
1. Common-mode noise (~0.998 mean correlation — nearly perfectly correlated)
2. Statistical noise in the correlation estimate
3. The null model (flat correlation) fits better because the residuals are dominated by noise, not spatial structure

The null model is preferred not because there is no spatial correlation — there clearly is high correlation — but because the **variation** with distance is too small to detect over common-mode noise.

---

## 3. Structural Diagnosis

This result is not a failure of the analysis pipeline. It is a physical constraint:

> On a 7-qubit chip (max 632 µm), the C2 spatial coherence length ξ_c = 2 × c × τ_B must be comparable to the chip size for d_c to be measurable.

With c = 10⁴ m/s and τ_B = 5 µs: ξ_c = 0.1 m = 100,000 µm — **158× the chip size.**

To make d_c measurable, one of:
- c must be ~100 m/s (not predicted by C2)
- τ_B must be ~0.03 µs (much faster, changes identifiability of temporal fit)
- Chip size must be >> 1 cm (not available on current QPUs)

**This is a fundamental limitation, not an experimental error.**

---

## 4. Figures Produced

- `outputs/figures/fig_spatial_corr_matrix.png` — Pearson correlation heatmap
- `outputs/figures/fig_spatial_corr_vs_dist.png` — Correlation vs. distance with fits
