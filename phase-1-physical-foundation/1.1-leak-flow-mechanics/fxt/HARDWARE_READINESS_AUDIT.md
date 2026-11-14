# HARDWARE READINESS AUDIT
## IBM Brisbane — SXC-IGC Spatial Correlation Experiment

**Date:** 2026-08-22
**Conclusion:** NOT READY — statistical gate fails before hardware questions arise

---

## 1. Statistical Gate (Primary Blocker)

The experiment fails the statistical gate before hardware readiness becomes
relevant. See FINAL_DESIGN_SEARCH.md and TWO_STAGE_STATISTICS_AUDIT.md.

The core issue is shape non-identifiability: K0 Bessel covariance cannot be
distinguished from power-law (M7) or two-bath (M9) spatial covariance over
the Brisbane geometry at acceptable false-positive rates.

All hardware questions below are moot unless the statistical gate is resolved.
They are documented here for completeness.

---

## 2. Device: IBM Brisbane

| Property | Value | Assessment |
|----------|-------|------------|
| Qubit count | 127 | Sufficient |
| Topology | Heavy-hex | Suitable |
| Nearest-neighbor spacing | 200 µm | Defines UV cutoff |
| T1 median | 232 µs | Marginal (T1/T2 ≈ 1.5) |
| T2 median | 150 µs | Sufficient for Ramsey |
| Readout error median | 2.0% | Acceptable with calibration |
| Readout error max | 24% | Some qubits must be excluded |
| Qubit frequency range | 4.61–5.12 GHz | Normal range |
| Max physical separation | 3688 µm | Limits ξ_c reach |

---

## 3. T1/T2 Ratio Assessment

The pure dephasing formula W(t) = exp(−Γ_φ·t) requires T₁ >> T₂.

Brisbane median: T₁ = 232 µs, T₂ = 150 µs → T₁/T₂ = 1.55.

**This violates the pure dephasing assumption for most qubits.**

Impact: the correct Ramsey formula includes T₁ relaxation:
```
W(t) = exp(−Γ_φ·t) × exp(−t/(2T₁))
```
This changes the extracted Γ_φ by approximately T₂/(2T₁) ≈ 32%, which
introduces a systematic offset in the C_Gamma extraction.

**Mitigation:** Select only qubits where T₁ > 5·T₂. From Brisbane calibration
data, approximately 10–20% of qubits satisfy this criterion. This severely
limits the usable qubit count.

The current simulation uses T₁ = 300 µs, T₂ = 150 µs (T₁/T₂ = 2.0) as a
best-case selection. In practice fewer qubits satisfy this condition.

---

## 4. Physical Qubit Coordinates

Brisbane coordinates are available (conf_brisbane.json, heavy-hex grid).
Physical separations span 200–3688 µm.

For K0 discrimination to be feasible (requires 0.2–5 ξ_c range):
- At ξ_c = 0.5 mm: need 100–2500 µm → Brisbane covers this
- At ξ_c = 1.0 mm: need 200–5000 µm → Brisbane partially covers this
- At ξ_c = 2.0 mm: need 400–10000 µm → Brisbane misses the >3688 µm region

This geometric limitation is separate from the shape-similarity failure.
Even if the shape were discriminable, ξ_c > ~750 µm would leave only
partial coverage of the required spatial range.

---

## 5. Spatial Correlation Scale Availability

The 12-qubit linear chain (200-2200 µm) provides:
- 11 unique separation bins (200, 400, ..., 2200 µm)
- All within 0.2–2.2 ξ_c for ξ_c = 1 mm
- Insufficient range to resolve K0 vs power-law curvature (SNR ≈ 2)

The full 127-qubit Brisbane chip provides more separations (up to 3688 µm),
but the additional pairs at large r are not on a linear chain — they involve
multi-hop paths that add circuit depth and gate errors. These were not simulated.

---

## 6. Circuit Runtime Estimate

For the proposed design (12 qubits, 8192 shots, 10 time points):
- 66 pairs × 10 time points × 8192 shots = 5.4M shots
- Per-shot time at IBM (realistic): ~5 µs
- Circuit execution: 5.4M × 5 µs = 27 s
- Plus calibration: 60 s
- Total: **87 s ≈ 1.5 minutes**

This fits comfortably within the 10-minute budget. Runtime is not the blocker.

---

## 7. Correlated Readout Error

IBM simultaneous readout has documented cross-talk at 0.5–1% between adjacent
qubits. This introduces spurious correlations in C_ij that do not cancel
in the ratio estimator if they are correlated across both qubits simultaneously.

**Impact on C_Gamma:** ~0.01 additive systematic at nearest-neighbor pairs.
This is below the signal level at sub_frac = 0.15 but not negligible.

**Required:** Dedicated calibration circuit measuring C_ij with qubits prepared
in |0⟩ (no dephasing, no signal) to quantify and subtract the readout
cross-talk contribution. This circuit takes ~10 seconds.

Not implemented in the current simulation. Adds ~10 s overhead to runtime.

---

## 8. Gate Error

IBM two-qubit gate error ~0.1–0.3%. The proposed experiment uses only
single-qubit gates (Hadamard + wait + X-basis measurement). Gate error
for single-qubit operations: ~0.05%. This is negligible.

No CNOT or two-qubit entangling gates are used. The experiment is purely
Ramsey measurement — the simplest possible IBM circuit type.

---

## 9. Queue Time and Open Plan Constraints

IBM Quantum Open Plan provides ~10 minutes of QPU execution time but typical
queue times are hours to days. The 10 minutes refers to execution time only.

This is a practical constraint but does not affect the scientific validity
of the proposed experiment.

---

## 10. Hardware Readiness Summary

| Criterion | Status | Notes |
|-----------|--------|-------|
| Statistical gate | ❌ FAIL | Shape non-identifiable vs M7/M9 |
| T1/T2 ratio | ⚠️ MARGINAL | Need qubit selection T1 > 5T2 |
| Spatial range | ⚠️ PARTIAL | OK for ξ_c ≤ 1mm; miss large r |
| Readout crosstalk | ⚠️ UNTESTED | Needs calibration circuit |
| Circuit runtime | ✓ OK | ~1.5 min, well within budget |
| Gate error | ✓ OK | Single-qubit only, negligible |
| Physical coordinates | ✓ OK | Available from conf_brisbane.json |
| QPU access | ✓ OK | Open Plan allocation available |

**Hardware readiness is moot. The statistical gate fails first.**
**FINAL STATUS: NOT READY — STOP**
