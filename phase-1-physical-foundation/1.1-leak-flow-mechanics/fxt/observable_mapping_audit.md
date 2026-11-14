# OBSERVABLE MAPPING AUDIT
## Does C_Γ(r) Actually Map to a Measurable Qubit Observable?

**Date:** 2026-08-22
**Purpose:** Rigorously derive the chain from theoretical C_Γ(r) to the
proposed experimental observable C_ij(t). Classify every arrow.
**Rule:** If the mapping fails, STOP. Do not repair it.

---

## 1. Theoretical Quantity Being Tested

From 02_2D_CORRELATION_DERIVATION.md [D NEW]:

```
S_JJ^{2D}(r, ω=0) = (S₀ / πξ_c) · K₀(r/ξ_c)

Normalized spatial correlator:
C_Γ(r) = K₀(r/ξ_c) / K₀(a/ξ_c)
```

where the normalization K₀(a/ξ_c) is evaluated at the UV cutoff a (lattice spacing).

**Physical meaning:** C_Γ(r) is the normalized zero-frequency cross-spectral
density of the substrate current J at two spatial points separated by r.

---

## 2. Connection to Qubit Dephasing Rate

The dephasing rate for a qubit at position x_q is:

```
Γ_φ(x_q) = (4g²/ℏ²) · S_JJ(ω=0; x_q)   [from Born-Markov, DERIVED]
```

where S_JJ(ω=0; x_q) is the LOCAL zero-frequency PSD at the qubit's position.

For two qubits at x_i and x_j, the CORRELATED dephasing arises from the
cross-spectral density:

```
Corr(Γ_φ,i, Γ_φ,j) = (4g²/ℏ²)² · S_JJ^{cross}(x_i, x_j, ω=0) / [Γ_φ,i · Γ_φ,j]^{1/2}
```

This equals C_Γ(|x_i − x_j|) when the substrate is spatially stationary (same S₀
everywhere). This step is DERIVED from the Gaussian noise assumption and spatial
stationarity.

**Classification:** DERIVED (given Gaussian substrate, spatial stationarity, Born-Markov)

---

## 3. Connection to Density Matrix

Under pure dephasing by a Gaussian, spatially correlated substrate field:

```
ρ_{01,i}(t) = ρ_{01,i}(0) · exp[−Γ_φ,i · t]
```

(single-qubit, DERIVED for Gaussian noise)

For two qubits:
```
⟨ρ_{01,i}(t) · ρ_{01,j}(t)*⟩ = ρ_{01,i}(0)·ρ_{01,j}(0)* · exp[−(Γ_φ,i + Γ_φ,j)t/2]
                                  × exp[+C_Γ(r_ij) · √(Γ_φ,i·Γ_φ,j) · t]
```

(for identical qubits, Γ_φ,i = Γ_φ,j = Γ_φ, and C_Γ(r) < 1)

This is the JOINT coherence decay with cross-correlation. It reduces to:

```
⟨ρ_{01,i}(t) · ρ_{01,j}(t)*⟩ = |ρ_{01}(0)|² · exp[−Γ_φ(1 − C_Γ(r_ij)) · t]
```

**Classification:** DERIVED under: Gaussian substrate noise, Born-Markov, pure
dephasing (T₁ = ∞), spatial stationarity, identical qubit parameters.

---

## 4. Connection to Proposed Experimental Observable

The proposed experimental observable is:

```
C_ij(t) = ⟨σ_{x,i}(t) · σ_{x,j}(t)⟩ / (⟨σ_{x,i}(t)⟩ · ⟨σ_{x,j}(t)⟩)
```

From the density matrix:
```
⟨σ_{x,i}(t)⟩ = 2·Re[ρ_{01,i}(t)] = 2·Re[ρ_{01,i}(0)]·exp(−Γ_φ t)
```

For the two-qubit expectation value:
```
⟨σ_{x,i}(t)·σ_{x,j}(t)⟩ = 4·Re[⟨ρ_{01,i}(t)·ρ_{01,j}(t)*⟩]
```

ONLY if the qubits are entangled or correlated by a common noise source.
If they evolve under INDEPENDENT noise: ⟨σ_{x,i}·σ_{x,j}⟩ = ⟨σ_{x,i}⟩·⟨σ_{x,j}⟩.
The numerator equals the denominator and C_ij = 1. No signal.

For CORRELATED noise (substrate model):
```
C_ij(t) = exp[C_Γ(r_ij)·Γ_φ·t] · exp[−C_Γ(r_ij)·Γ_φ·t]
         ≠ C_Γ(r_ij)   directly
```

**The proposed observable C_ij(t) is NOT directly equal to C_Γ(r_ij).**

The mapping is:
```
C_ij(t) = exp{[C_Γ(r_ij) − 1] · Γ_φ · t}   [for identical qubits, Gaussian noise]
```

To extract C_Γ(r_ij) from the measured C_ij(t):
```
C_ij(t) = exp[C_Γ(r_ij) · Γ_φ · t]
=> C_Γ(r_ij) = ln[C_ij(t)] / (Γ_φ · t)
```
Note: the "+1" form (1 + ln/Γt) was an error in previous documents and is
corrected here. C_ij(t) = exp(C_Γ·Γ·t), not exp((C_Γ-1)·Γ·t).

This mapping IS valid but requires:
1. Knowing Γ_φ independently (must be pre-measured) [EXPERIMENTAL ASSUMPTION]
2. Choosing t such that Γ_φ·t is measurable but not too large (SNR) [EXPERIMENTAL ASSUMPTION]
3. Gaussian noise assumption (holds for large N substrate, breaks for small N) [DERIVED condition]
4. Pure dephasing (T₁ = ∞ effectively; needs T₁ >> T₂) [EXPERIMENTAL ASSUMPTION, check from data]

**Classification of the full mapping C_ij(t) → C_Γ(r):**
DERIVED with 4 stated approximations. Not invalid, but not assumption-free.

---

## 5. Critical Failure Modes

**Failure mode 1 — Simultaneous measurement introduces correlations:**
Measuring σ_{x,i} and σ_{x,j} simultaneously on a quantum processor can introduce
spurious correlations via measurement crosstalk. IBM heavy-hex architecture
uses simultaneous readout; readout crosstalk at the 1-3% level is documented
in the calibration data. This crosstalk ADDS spurious C_ij > 0 even under M0.
Classification: **UNCONTROLLED systematic at current hardware level.**

**Failure mode 2 — Electrical/circuit crosstalk:**
Physical proximity of qubits creates electromagnetic coupling (ZZ coupling,
residual controlled-Z terms) that induces correlated single-qubit errors.
This mimics substrate correlation and has similar spatial decay length (~mm scale).
Classification: **PRIMARY CONFOUND. Must be characterized independently.**

**Failure mode 3 — Common-mode control-line noise:**
All qubits on the same chip share power supplies and control electronics.
Low-frequency noise on control lines appears as correlated Γ_φ fluctuations
with long spatial range. This is not a substrate effect.
Classification: **PRIMARY CONFOUND. Especially dangerous for temporal averaging.**

---

## 6. Mapping Verdict

The theoretical quantity C_Γ(r) IS mathematically mappable to the proposed
observable C_ij(t), subject to four stated approximations and three identified
failure modes.

The mapping is:
```
C_Γ(r_ij) = 1 + ln[C_ij(t)] / (Γ_φ · t)
```

This is valid when:
- t is in the range 0.1·T₂ to 0.5·T₂ (SNR window)
- T₁ > 5·T₂ (pure dephasing condition — CHECK from IBM data: satisfied for median qubits)
- Readout crosstalk is subtracted using a dedicated calibration measurement
- Electrical crosstalk is bounded using non-co-dephasing qubit pairs

**The observable mapping is mathematically VALID but requires:**
- Pre-measurement of Γ_φ for each qubit
- Readout crosstalk calibration circuit
- Crosstalk control experiment
