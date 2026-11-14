# HARDWARE FEASIBILITY REPORT
## IBM Brisbane — Spatial Correlation Experiment

**Date:** 2026-08-22
**Device:** ibm_brisbane (127 qubits, heavy-hex topology)
**Data source:** 06_datasets/conf_brisbane.json, props_brisbane.json
**QPU budget:** ~10 minutes

---

## 1. Device Summary

| Property | Value |
|----------|-------|
| Qubit count | 127 |
| Topology | Heavy-hex lattice |
| Nearest-neighbor spacing | ~200 µm (a) |
| T1 (median) | 232 µs |
| T1 (range) | 9.9 – 425 µs |
| T2 (median) | 150 µs |
| T2 (range) | 17.1 – 412 µs |
| T1/T2 (median) | ~1.5 — CRITICAL WARNING: not >> 1 |
| Readout error (median) | 2.0% |
| Readout error (max) | 24% |
| Frequencies | 4.61 – 5.12 GHz |
| Coupling map pairs | 144 pairs |
| Max physical separation | 3688 µm |
| Min physical separation | 200 µm |

---

## 2. Spatial Coverage

Physical qubit separation distribution on Brisbane:

| Range (µm) | Pairs | Fraction |
|------------|-------|---------|
| 200–250 | 144 | 1.8% |
| 250–500 | 509 | 6.4% |
| 500–1000 | 1373 | 17.2% |
| 1000–2000 | 3816 | 47.7% |
| 2000–3688 | 2159 | 27.0% |

Unique separation bins (50 µm resolution): 60

For the K₀ vs exp shape test to be informative, the experiment needs separations
spanning ~0.2ξ_c to ~5ξ_c.

**Required ξ_c:** The chip covers 200–3688 µm, so:
```
Good coverage: 0.2·ξ_c ≈ 200 µm  →  ξ_c ≈ 1000 µm
Good coverage: 5·ξ_c ≈ 3688 µm  →  ξ_c ≈ 738 µm
```
These are INCONSISTENT: no single ξ_c gives both bounds simultaneously.

The broadest achievable test spans ~0.2–3.7 in units of ξ_c if ξ_c ≈ 1000 µm.

---

## 3. The ξ_c Problem — CRITICAL

The existing discrimination test (p25, test3) computed:

```
Required ξ_c for 5% shape difference between K₀ and exp: 1200 µm
Required substrate speed c for this: 120 m/s (given τ_B = 5 µs)
```

The C2 theory does NOT independently predict c. It is a free parameter (GAP-7
in 00_THEORY_AUDIT.md). The current simulation was run with ξ_c = 10 cm = 100,000 µm.

On the Brisbane chip, max separation = 3688 µm. The ratio d_max/ξ_c = 0.037.

**At ξ_c = 10 cm, every qubit pair sees r/ξ_c << 1.** In this limit:
```
K₀(r/ξ_c) ≈ −ln(r/ξ_c)   [logarithmic, slowly varying]
exp(−r/ξ_c) ≈ 1 − r/ξ_c  [also slowly varying]
```
Both models predict nearly flat spatial correlation across the chip. They are
indistinguishable. The AUC from p25 test11 = 0.5 at current geometry.

For the test to work, ξ_c must be ≤ 2·d_max = 7376 µm. With τ_B = 5 µs,
this requires c ≤ 7376/(2 × 5×10⁻⁶) = 0.74 m/s.

**A substrate speed of c < 1 m/s is physically implausible for an information
substrate that should propagate at something near the speed of sound or light.**

---

## 4. T1/T2 Ratio Assessment

The pure dephasing model requires T₁ >> T₂ (so that relaxation does not
contaminate the dephasing measurement).

Brisbane median: T₁ = 232 µs, T₂ = 150 µs → ratio = 1.55.

This violates the pure dephasing assumption (T₁/T₂ >> 1 required; ratio of 1.55
means T₁ and T₂ are comparable). The measured Γ_φ will contain substantial T₁
contamination. The pure-dephasing formula W(t) = exp(−Γ_φ·t) is not valid at this
ratio — the correct formula is:

```
W(t) = exp(−Γ_φ·t) × exp(−t/(2T₁))
```

This changes the fitted Γ_φ and invalidates the direct comparison to the theory.

**Some qubits have T₁ > 5·T₂ (suitable). Most do not. Qubit selection is required.**

---

## 5. Readout Crosstalk Assessment

Median readout error = 2%, maximum = 24%. Simultaneous readout of nearby qubits
introduces readout crosstalk at the ~1-3% level (IBM documentation).

The substrate spatial correlation signal at realistic separations:

If ξ_c = 1000 µm and r = 1000 µm:
```
C_Γ(1) = K₀(1)/K₀(a/ξ_c) ≈ 0.42 / K₀(0.0002) ≈ 0.42 / 8.5 ≈ 0.05
```

The expected correlation signal is ~5%, comparable to readout crosstalk.
**The signal is at the noise floor of readout crosstalk even under optimistic
ξ_c assumptions.**

---

## 6. Circuit Runtime Estimate

Single Ramsey circuit (one qubit, one time point):
- State prep: X/2 gate (~35 ns)
- Delay: t (variable, 0 to ~300 µs)
- Read: meas (~700 ns)
- Total: ~1 µs per shot

For 20 qubits, 20 time points, 10,000 shots per point:
```
Total measurements: 20 × 20 × 10,000 = 4,000,000
Time per circuit: ~1 µs × 10,000 shots = 10 ms per circuit
Total circuits: 20 × 20 = 400
Total time: 400 × 10 ms + overhead ≈ 4 s measurement + ~50s overhead ≈ 1 min
```

Cross-correlation circuits add ~50% overhead. Total: ~2 min for core measurement.
Calibration circuits: ~5 min. Total with 10 min budget: feasible in principle.

However, IBM Open Plan often has queue times of hours to days. The 10 min
refers to QPU execution time, not wall-clock time.

---

## 7. Feasibility Summary

| Criterion | Status | Notes |
|-----------|--------|-------|
| Spatial range | ❌ INSUFFICIENT | ξ_c must be ~1 mm; theory gives ~10 cm |
| ξ_c independently predicted | ❌ NO | c is free parameter (GAP-7) |
| T₁/T₂ ratio | ❌ MARGINAL | Most qubits T₁/T₂ < 3; need > 10 |
| Readout crosstalk < signal | ❌ NO | Signal ~5% at best; crosstalk ~2-3% |
| K₀ vs exp distinguishable | ❌ NO | AUC = 0.5 at current parameters |
| Circuit runtime | ✓ OK | Fits in 10 min budget |
| Physical coordinates available | ✓ YES | Heavy-hex grid, 200 µm spacing |
| Observable mapping valid | ✓ YES (with caveats) | See observable_mapping_audit.md |

**HARDWARE FEASIBILITY: NOT FEASIBLE given current parameter values.**

The fundamental blocker is that ξ_c is not independently predicted by the
theory, and at any physically plausible value of c, ξ_c >> chip size.
