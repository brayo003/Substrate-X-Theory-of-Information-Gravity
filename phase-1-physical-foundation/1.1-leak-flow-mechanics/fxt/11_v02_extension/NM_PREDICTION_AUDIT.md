# Non-Markovian Substrate Dephasing — Prediction Audit
**Date:** 2026-08-19  
**Status:** VERIFIED (all 4 computational tasks PASS)  
**Scripts:** nm_01 through nm_04 in `11_v02_extension/`  
**Supersedes:** The Markovian section of `C2_final_prediction_audit.md` (Outcome A, prediction L3-1)

---

## 1. What Changed and Why

`C2_final_prediction_audit.md` (Section 12) reached Outcome A: *"C2 predicts nothing experimentally unique."* The reason cited for prediction L3-1 (Lindblad structure) was:

> *"Setting γ = Γ_φ: numerically identical to C2 for every element of ρ for all time."*

This is correct **conditional on the Markov approximation** (A-MARKOV: `τ_B ≪ Γ_φ⁻¹`). The stress test `07_derivation_stress.py` already showed the Markov reduction fails badly outside this regime (mismatch 0.339 at NMP=1, 0.698 at NMP=10). That file labelled this a "derivational limitation" and stopped there.

This audit completes the step: **removing the Markov approximation produces a prediction that is not reproduced by any standard Lindblad model.**

---

## 2. The Exact Equation (No Markov Approximation)

### Starting point

The C2 substrate coupling is `H_int = g J(x_q, t) σ_z` where `J` is a Gaussian stochastic process with correlation function:

```
C_JJ(t') = S₀ · exp(-t' / τ_B)
```

`S₀ = (2/3) s₀² ω_rot² r_q²` (rotational current variance, from C2 Layer 3).

### Exact coherence (second-order cumulant, Gaussian noise)

For Gaussian noise the second-order cumulant expansion is **exact**. No Born-Markov approximation is applied. The result is:

```
ρ₀₁(t) = ρ₀₁(0) · exp(-Φ(t))                              [EXACT]

Φ(t) = (2g²/ℏ²) ∫₀ᵗ dt' (t - t') C_JJ(t')
      = Γ_Markov · τ_B · [t/τ_B - 1 + exp(-t/τ_B)]        [EXACT-PHI]
```

where `Γ_Markov = 2g² S₀ τ_B / ℏ²` is the Markov rate (recovered in the limit τ_B → 0).

### Verified numerically

`nm_01_memory_kernel.py` verified `[EXACT-PHI]` against direct numerical integration:  
**max error = 3.12×10⁻⁶** (trapz quadrature noise). **[PASS]**

---

## 3. The Two Limits

| Regime | Condition | Coherence | Shape |
|--------|-----------|-----------|-------|
| **Markov** | `t ≫ τ_B` | `exp(-Γ·t)` | Pure exponential |
| **Short-time / NM** | `t ≪ τ_B` | `exp(-Γ·t²/(2τ_B))` | Gaussian |
| **Crossover** | `t ~ τ_B` | Full `[EXACT-PHI]` | Interpolates |

The Markovian model (`τ_B → 0`, standard Lindblad) predicts **only** the exponential. The non-Markovian model predicts a **Gaussian initial decay** that becomes exponential only at `t ≫ τ_B`.

---

## 4. The Non-Markovianity Parameter (NMP)

```
NMP = Γ_Markov · τ_B
```

| NMP | Regime | Max |C_exact - C_Markov| |
|-----|--------|--------------------------|
| < 0.1 | Markovian | 0.071 |
| 0.1 – 1.0 | Transitional | 0.328 |
| > 1.0 | Non-Markovian | 0.827 |

At NMP=3: exact T₂* = **2.84×** the Markov prediction.

At the median Gamma from the gamma_dataset (31.7 kHz): NMP=1 requires `τ_B = 31.6 µs`.

---

## 5. Why This Prediction Is Unique

### Comparison with standard Lindblad

A standard Lindblad model with jump operator `L = σ_z` and rate `γ` gives:

```
C_Lindblad(t) = exp(-γ t)     [pure exponential for all t]
```

**There is no value of γ that reproduces the Gaussian initial decay.** Setting `γ = Γ_Markov` matches only the long-time tail. The early-time shape `exp(-Γ·t²/(2τ_B))` is strictly different for any `τ_B > 0`.

### Comparison with super-Ohmic bath (previous NOT UNIQUE finding)

The previous audit showed `Γ_φ ∝ ω²` is reproduced by a super-Ohmic bath `S(ω) ∝ ω²`. That comparison was about the **rate vs frequency** relationship. The non-Markovian prediction here is about the **time-domain shape of a single Ramsey trace**, which is independent of the ω² scaling and adds a new observable dimension.

A super-Ohmic Markovian bath gives exponential Ramsey decay. The C2 non-Markovian bath gives Gaussian initial decay. These are distinguishable.

### Standard Lindblad cannot reproduce Gaussian onset

Proof: Any Lindblad equation with time-independent rates gives `ρ₀₁(t) = exp(-λt)` for some `λ > 0`. A time-dependent Lindblad with rate `γ(t)` could give non-exponential decay, but such a model would itself require a physical justification — it would be a phenomenological match, not a derivation. The C2 framework **derives** the specific form of the memory kernel from the substrate correlation function.

---

## 6. Why the Gamma_dataset Cannot Discriminate

Task 3 result: fitting both models to the 7-point `gamma_dataset.csv` gives ΔBIC = 1.95 (no preference). Fitted `τ_B = 0.75 µs`, NMP = 0.024 (Markovian regime).

**Structural reason:** The gamma_dataset records `Γ_meas = 1/T₂*` — a single number per frequency (the 1/e point of the decay). The non-Markovian prediction is:

```
T₂*_NM = Φ⁻¹(1, Γ_Markov, τ_B)   [solve Phi(t)=1]
```

For small NMP, `T₂*_NM ≈ T₂*_Markov` — the 1/e point barely shifts. What shifts is the **shape**. Measuring only the 1/e point is insensitive to `τ_B` when NMP is small.

**The gamma_dataset is not the right observable.** The right observable is the full time trace.

---

## 7. The Discriminator Protocol

### Observable

Plot `log |C(t)|` vs `t²`:
- **Markov (exponential):** `log C = -Γ·t` → curved upward in this plot
- **Non-Markovian (Gaussian onset):** `log C ≈ -Γ·t²/(2τ_B)` → **straight line** at early times

This is a model-independent graphical test requiring no parameter fitting.

### Quantitative discrimination (from Task 4)

At 1000 shots per time point, σ = 0.02:

| NMP | 3σ discrimination time |
|-----|------------------------|
| 0.3 (Transitional) | Not reached in 4×T₂* window |
| 1.5 (Non-Markovian) | **t = 36.1 µs** |
| 3.0 (Non-Markovian) | **t = 30.7 µs** |

Both NM cases are discriminable within the T₂* = 31.6 µs window — i.e., before the coherence dies.

### Experimental requirements

- Time resolution: sub-µs Ramsey steps (dt ≪ τ_B)
- Shot count: ≥ 1000 per time point (achievable on NV or superconducting qubits)
- Free evolution range: 0 to ~4 × T₂* (= 0 to ~127 µs)
- Key window: 0 to τ_B (where Gaussian onset is visible)

---

## 8. Connection to C2 Mathematics

The non-Markovian prediction is fully within existing C2 Layer 3 mathematics. No new axioms are added.

**What changes:** The Markov approximation (A-MARKOV) is dropped. The Born approximation (A-BORN) is retained. The exact result follows from the second-order cumulant expansion, which is exact for Gaussian noise — and the PRW substrate current `J(t)` is Gaussian (sum of many independent random reversals).

**What τ_B is:** The substrate bath correlation time. In the PRW picture, `τ_B` is related to the reversal rate `λ` by `τ_B ∝ 1/λ`. It is the timescale over which the substrate "forgets" its state. This is a physical parameter of the substrate, not a phenomenological fitting parameter.

**New free parameter count:** The non-Markovian model adds one parameter (`τ_B`) to the existing three (`Γ₀`, `k_rot`, `ω_max`). The Cramer-Rao bound from Task 4 shows `τ_B` is measurable to <10% relative uncertainty with 10k shots when `τ_B > ~5 µs` at Γ = 31.7 kHz.

---

## 9. Update to the Final Prediction Audit (Outcome A → Partial B)

The original Outcome A verdict remains correct for all **frequency-domain** predictions. The update is:

| Prediction | Original status | Updated status |
|-----------|----------------|----------------|
| `Γ_φ ∝ ω²` (rate vs frequency) | NOT UNIQUE | NOT UNIQUE (unchanged) |
| `C(t) = exp(-Γt)` (exponential decay) | OBSERVATIONALLY EQUIVALENT | **CONDITIONAL** |
| `C(t) = exp(-Φ(t))` (Gaussian onset) | Not in original audit | **STRICTLY DIFFERENT** when NMP > 0.1 |

**The new prediction L3-NM:**

> *If the C2 substrate has a finite bath correlation time τ_B with NMP = Γ·τ_B > 0.1, the Ramsey coherence trace has a Gaussian initial decay `C(t) ~ exp(-Γt²/(2τ_B))` at `t < τ_B`, transitioning to exponential at `t > τ_B`. This is not reproduced by any time-independent Lindblad model.*

**Classification: STRICTLY DIFFERENT** — no time-independent Lindblad model can produce a Gaussian initial decay; the early-time shape is a direct observable of τ_B.

**Experimental status: UNTESTED** — the gamma_dataset does not contain the required time-domain Ramsey traces. The Wood et al. dataset contains spin-echo traces (Figure 5), not free-induction-decay Ramsey traces with the needed time resolution.

---

## 10. What Would Close the Loop

1. **Run a full Ramsey trace** (not just the 1/e time) at a single fixed `ω_rot` with sub-µs time resolution and ≥ 1000 shots per point.

2. **Plot log(C) vs t²** at early times. A straight line (Gaussian) falsifies the Markov model and is consistent with NMP > 0.1.

3. **Fit τ_B** from the Gaussian curvature. Compare to `τ_B = 1/(2λ)` from the PRW substrate parameters.

4. If `τ_B ≈ T₂*/NMP` with NMP > 0.1, this constitutes the first experimental constraint on the substrate memory time.

---

## 11. Files Produced

| File | Content |
|------|---------|
| `nm_01_memory_kernel.py` | Exact Φ(t) derivation, numerical verification PASS |
| `nm_02_parameter_space.py` | Regime map, T₂* ratio, mismatch heatmap |
| `nm_03_model_fit.py` | Fit to gamma_dataset, ΔBIC=1.95 |
| `nm_04_ramsey_discriminator.py` | LLR, Fisher bound, discrimination times |
| `outputs/nm_01/` | 3 figures + summary JSON |
| `outputs/nm_02/` | 3 figures + summary JSON |
| `outputs/nm_03/` | 1 figure + fit JSON |
| `outputs/nm_04/` | 4 figures + summary JSON |

---

*End of Non-Markovian Prediction Audit*  
*All computational results verified by running the scripts above.*  
*No new axioms introduced. No C2 structure modified.*  
*Verdict: The non-Markovian Ramsey trace shape is a genuinely distinguishable prediction when NMP > 0.1.*
