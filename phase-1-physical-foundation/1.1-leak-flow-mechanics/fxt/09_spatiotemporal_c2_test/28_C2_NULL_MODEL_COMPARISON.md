# Document 28 — C2 vs Null Model Comparison
## Phase 9: Full Model Comparison Including Mathematical Degeneracy

**Date:** 2026-08-21

---

## 1. The Core Degeneracy (Proven)

The C2 quantum coherence prediction and the OU colored-noise prediction are
**mathematically identical** at every level of analysis attempted in Phase 9:

### 1.1 Temporal coherence (proven in NM_PREDICTION_AUDIT.md, confirmed in p18)

```
C_C2(t) = exp(-Γ_M·τ_B·[t/τ_B - 1 + exp(-t/τ_B)])
C_OU(t) = exp(-Γ_ou·τ_ou·[t/τ_ou - 1 + exp(-t/τ_ou)])
```
Same formula. BIC preference of C2 over OU = 0 (when optimizer converges).

### 1.2 Single-qubit PSD (proven in Doc 24, confirmed in p24)

Both produce Lorentzian: `S(f) = A/(f² + f_c²)` with f_c = 1/(2πτ_B).
No frequency-domain observable distinguishes them.

### 1.3 Cross-spectral coherence at d << ξ_c (proven in Doc 24, confirmed in p24)

C2: γ_ij = exp(-d/ξ_c) ≈ 1 for d/ξ_c = 0.006  
OU: γ_ij = f_cm ≈ any constant  
Indistinguishable when both ≈ 1.

### 1.4 Cross-spectral phase delay (proven in Doc 24)

C2 phase lag = ω·d/c_C2 = 12.6 mrad at corner frequency.
Shot noise floor at 8192 shots = ~11 mrad.
SNR = 1.1 — undetectable.

---

## 2. Model Comparison Table

| Observable | C2 | OU | Quasistatic | White | Common-mode | Distinguishable |
|------------|----|----|-------------|-------|-------------|-----------------|
| Ramsey shape | Non-Markovian | **Identical** | Gaussian | Exponential | — | C2 ≠ exp, gauss |
| τ_B (temporal) | Yes | Same τ_ou | τ_B→∞ | τ_B→0 | Any | No C2 vs OU |
| S_ii(f) | Lorentzian | **Identical** | 1/f² | Flat | Lorentzian | No |
| S_ij(f)/S_ii(f) | exp(-d/ξ_c) | f_cm (const) | Similar | ~0 | 1.0 | Only if d~ξ_c |
| Phase(S_ij) | ω·d/c | 0 or ω·d/c | — | — | 0 | Not at SNR~1 |
| Higher cumulants | Non-Gaussian? | Gaussian | Non-Gaussian | Gaussian | — | Not measured |

---

## 3. What the Evidence Establishes

### Established by Phase 9 simulation:
- Non-Markovian decay is the correct shape (ΔBIC > 6000 vs exponential) ✓
- τ_B is recoverable at NMP ~ 1–2 (bias < 7%, CV = 0.10) ✓
- C2-exact wins by BIC vs all other temporal models ✓ (in simulation — trivial)

### Not established:
- C2 is not OU: **impossible with Ramsey or CSD on any platform** ✗
- d_c is not measurable at d << ξ_c ✗
- c_C2 is not constrained ✗
- Phase delay is not detectable ✗

---

## 4. The Decisive Test That Has Not Been Run

The only observable with potential C2-specific content:

```
c_C2 = d_c / τ_B   where d_c and τ_B measured independently, same conditions
```

This test requires d ~ ξ_c. At c = 10⁴ m/s and τ_B = 5µs, ξ_c = 10 cm.
No available hardware provides this. The test is **physically blocked**, not
merely experimentally difficult.

---

## 5. Verdict

The complete model comparison yields:

**The frequency-domain cross-spectral experiment is NON-DIAGNOSTIC.**

C2 is COMPATIBLE with all data. OU is equally compatible.
The data does not discriminate between them.
This is not a new finding — it is a quantitative confirmation of the structural
degeneracy established mathematically in Document 24.
