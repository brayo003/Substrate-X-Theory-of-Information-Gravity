# PRE-HARDWARE EXPERIMENT VALIDATION
## Complete Audit: Is the SXC-IGC Spatial Correlation Experiment Scientifically Executable?

**Date:** 2026-08-22
**Verdict: D — INCONCLUSIVE at physically motivated parameters; CORRECT required**

---

## 1. Derivation Chain Audit

```
SXC-IGC equations
    ↓ [DERIVED] 2D PRW telegrapher equation
substrate current J(x,t)
    ↓ [DERIVED] Wiener-Khinchin + 2D IFT
S_JJ^{2D}(r, ω=0) = (S₀/πξ_c)·K₀(r/ξ_c)
    ↓ [DERIVED] Born-Markov, Gaussian noise
Γ_φ(x_q) = (4g²/ℏ²)·S_JJ(ω=0; x_q)
    ↓ [DERIVED] spatial stationarity + identical qubits
C_Γ(r) = K₀(r/ξ_c)/K₀(a/ξ_c)
    ↓ [DERIVED with 4 approximations] Gaussian noise, pure dephasing
C_ij(t) = exp{[C_Γ(r_ij)−1]·Γ_φ·t}
    ↓ [EXPERIMENTAL ASSUMPTION] pre-measure Γ_φ
ln[C_ij(t)]/(Γ_φ·t) = C_Γ(r_ij) − 1  ← measured value
    ↓ [CIRCUIT] simultaneous σ_x readout, IBM heavy-hex
Classical bitstring correlation → C_ij estimate
```

Every arrow classified. The chain is valid. No undefined steps.

---

## 2. Critical Unresolved Issues

### Issue 1: ξ_c is a free parameter (BLOCKER)

ξ_c = 2c·τ_B. The substrate speed c is not predicted by C2 (GAP-7,
00_THEORY_AUDIT.md). At τ_B = 5 µs and any physically plausible c
(sound speed ~ 300–10,000 m/s):

```
c = 300 m/s  →  ξ_c = 3 mm   (minimum; DISCRIMINABLE on chip)
c = 5000 m/s →  ξ_c = 5 cm   (NOT discriminable on chip)
c = 3×10⁸ m/s→  ξ_c >> 1 m  (definitively not discriminable)
```

The theory is consistent with any of these. The experiment is only
informative in the narrow range ξ_c ≤ 3 mm (c ≤ 300 m/s).

**Consequence:** The experiment cannot be pre-registered as a test of the
substrate theory without first measuring ξ_c. It must be redesigned as a
two-phase measurement + test.

### Issue 2: Temporal channel non-discriminating

Proved in p25 test1: C2 and OU colored-noise bath give mathematically
identical Ramsey decay. The temporal Γ_φ ∝ ω² test cannot distinguish
substrate physics from any exponentially correlated bath.

### Issue 3: T₁/T₂ ratio on Brisbane

Median T₁/T₂ = 1.55 on Brisbane. The pure dephasing formula W(t) = exp(−Γ_φ·t)
requires T₁ >> T₂. This is violated for most qubits. Qubit selection is
required, limiting the effective qubit count.

### Issue 4: Readout crosstalk

Simultaneous readout on IBM introduces crosstalk at ~1–3% level. The spatial
correlation signal at r > ξ_c is < 5%. Signal-to-crosstalk ratio ≈ 1–3.
A dedicated crosstalk calibration circuit is required.

---

## 3. Simulation Results Summary

From pre_hardware_experiment_simulation.py:

| ξ_c | Chip ratio | Shape diff | SNR | Power | FP | Status |
|-----|-----------|-----------|-----|-------|-----|--------|
| 1 mm | 3.8 | 22.8% | 6.4 | 100% | 0.2% | DISCRIM |
| 3 mm | 1.3 | 13.1% | 3.7 | 99.5% | 0.2% | DISCRIM |
| 100 mm | 0.04 | 7.2% | 2.0 | ~100% | ~0% | NOT DISCRIM |

The test is powered correctly IF ξ_c ≤ 3 mm. At ξ_c = 10 cm (p25 default),
the test fails because all qubit pairs are at r << ξ_c.

---

## 4. Overall Classification

**D — INCONCLUSIVE / NOT IDENTIFIABLE**

The measurement is physically legitimate, the observable mapping is valid, the
circuits are implementable, and the statistical power is adequate — but only
if ξ_c ≤ 3 mm.

The theory does not independently predict whether ξ_c ≤ 3 mm. Therefore the
experiment cannot be executed as a blind test of the substrate theory.

**Required correction before hardware:** Redesign as Phase 1 (measure ξ_c) +
Phase 2 (conditional shape test). If Phase 1 yields ξ_c ≤ 3 mm, proceed.
If not, stop.

See FINAL_PRE_HARDWARE_GATE.md for the complete go/no-go decision.
