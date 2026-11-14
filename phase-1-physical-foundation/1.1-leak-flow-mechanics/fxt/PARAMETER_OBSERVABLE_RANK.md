# PARAMETER_OBSERVABLE_RANK.md
## C2/SXC-IGC Parameter-to-Observable Matrix and Rank Analysis

**Date:** 2026-08-22
**Sources:** C2_FOUNDATIONS.md, substrate_transport_derivation.md,
  00_THEORY_AUDIT.md, THEORY_CLOSURE_AUDIT.md, GAP7_REDERIVATION.md

---

## 1. Complete Parameter List

All free parameters of the C2 theory relevant to the decoherence/spatial
prediction program. Quantum layer parameters require ≥10 additional
assumptions (M1, M2, A-HC1–A-HC6).

| ID | Symbol | Description | Layer | Type | Constrained by |
|----|--------|-------------|-------|------|----------------|
| P1 | v (= c) | PRW particle speed | Transport | FREE | Nothing in C2 |
| P2 | λ | PRW reversal rate | Transport | FREE | Nothing in C2 |
| P3 | g | Quantum-classical coupling | Quantum | FREE | F10 open problem |
| P4 | s₀ | Substrate information density | Transport | FREE | Nothing in C2 |
| P5 | r_q | Qubit coupling radius | Quantum | EMPIRICAL | Chip geometry |
| P6 | ℏ | Planck constant | Quantum | IMPORTED | Conventional physics |

**Derived (not free):**

| Symbol | Expression | Depends on |
|--------|-----------|------------|
| τ_B | 1/(2λ) | P2 |
| ξ_c | v/λ = 2cτ_B | P1, P2 |
| D | c²τ_B | P1, P2 |
| S₀ | (2/3)s₀²ω_rot²r_q² | P4, P5, external ω_rot |
| k_rot | 8g²S₀r_q²τ_B/(3ℏ²) | P3, P4, P5, P2, P6 |

---

## 2. Complete Observable List

| ID | Observable | Measurement method | C2 prediction |
|----|-----------|-------------------|---------------|
| O1 | Γ_φ(ω_rot) | Single-qubit Ramsey vs. rotation frequency | k_rot · ω_rot² |
| O2 | S_JJ(ω) | Ramsey frequency sweep, PSD | 2S₀τ_B / (1+ω²τ_B²) |
| O3 | NM Ramsey curvature (G) | Short-time Ramsey deviation | Γ_Markov · τ_B [t/τ_B − 1 + exp(−t/τ_B)] |
| O4 | C_Γ(r) | Spatial decoherence correlation | K₀(r/ξ_c)/K₀(a/ξ_c) |
| O5 | τ_B | Extracted from O2 or O3 | 1/(2λ) |
| O6 | ξ_c | Extracted from O4 fit | v/λ |
| O7 | c = ξ_c/(2τ_B) | Computed from O5, O6 | v (substrate speed) |

---

## 3. Parameter-to-Observable Matrix

Each cell: which parameters enter observable Oi, and how.

|    | O1: Γ_φ(ω_rot) | O2: S_JJ(ω) | O3: NM curvature | O4: C_Γ(r) | O5: τ_B | O6: ξ_c | O7: c |
|----|----------------|-------------|-----------------|------------|---------|---------|-------|
| P1 (v) | — | — | — | **YES** (via ξ_c) | — | **YES** | **YES** |
| P2 (λ) | YES (via τ_B) | YES (via τ_B) | YES (via τ_B) | YES (via ξ_c) | YES | YES | YES |
| P3 (g) | YES (via k_rot) | YES (via S₀) | YES (via Γ_Markov) | — | — | — | — |
| P4 (s₀) | YES (via k_rot) | YES (via S₀) | YES (via S₀) | — | — | — | — |
| P5 (r_q) | YES (via k_rot) | YES (via S₀) | YES (via S₀) | — | — | — | — |
| P6 (ℏ) | YES (via k_rot) | — | YES (via k_rot) | — | — | — | — |

Key: YES = parameter enters this observable; — = parameter does not enter.

---

## 4. Observable Constraints on Parameters

Reading the matrix column-by-column: what does measuring each observable constrain?

**O1 (Γ_φ vs ω_rot):**
Constrains the combination k_rot = 8g²S₀r_q²τ_B/(3ℏ²).
One measurement → one constraint on {g, s₀, r_q, λ, ℏ}.
With r_q and ℏ known: constrains g²s₀²τ_B.
Does NOT constrain v at all.

**O2 (S_JJ(ω)):**
Constrains (S₀, τ_B) jointly.
S₀ = g²s₀²(2/3)ω_rot²r_q² (depends on g, s₀, r_q, ω_rot).
τ_B = 1/(2λ).
Two parameters constrained: (S₀, τ_B) → gives g²s₀² and λ.
Does NOT constrain v.

**O3 (NM curvature):**
Constrains τ_B (same as O2) and Γ_Markov (same as O1).
No new information beyond O1+O2 combined.
Does NOT constrain v.

**O4 (C_Γ(r)):**
Constrains ξ_c = v/λ.
Given λ from O2/O5: constrains v = ξ_c · λ.
This is the ONLY observable that constrains v.
But: K₀/power-law shape degeneracy (ADVERSARIAL_NULL_AUDIT.md) means
ξ_c cannot currently be measured reliably on Brisbane (SNR ≈ 2).

**O5 (τ_B):** Constrains λ = 1/(2τ_B). Independent of v.

**O6 (ξ_c):** Constrains v/λ. Requires O4 to measure. Gives v given λ.

**O7 (c = ξ_c/(2τ_B)):** Requires both O5 and O6. Gives v directly.
Not theoretically predicted — it is a derived measurement, not a C2 prediction.

---

## 5. Rank Analysis

### 5.1 Counting Independent Constraints

From the matrix:
- O1 provides 1 constraint on {g, s₀, λ} (assuming r_q, ℏ known)
- O2 provides 2 constraints: (S₀, τ_B), which gives (g²s₀², λ)
- O3 provides 0 new constraints (same as O1+O2)
- O4 provides 1 new constraint: ξ_c = v/λ

Total independent observable constraints: 3 (from O1, O2, O4).

### 5.2 Free Parameters Remaining After All Measurements

Start with 4 free parameters: {v, λ, g, s₀} (treating r_q, ℏ as known).

After O1+O2: constrained → {g²s₀², λ}. Free: v, and the ratio g/s₀.
After O4: constrained → ξ_c = v/λ. With λ known: v is determined.
After all measurements: λ, v, g²s₀² are determined from data.
Still free: g and s₀ individually (only their product g²s₀² is measured).

**Result: Even with all measurements, g and s₀ individually remain undetermined.**
The theory has one remaining degeneracy that cannot be resolved by decoherence
measurements alone: the decomposition of g²s₀² into individual g and s₀.

### 5.3 Rank of the Prediction Map

The C2 prediction map f: {v, λ, g, s₀} → {O1, O2, O3, O4} has:

- Image dimension: 3 (combinations: g²s₀²·τ_B, τ_B, ξ_c)
- Domain dimension: 4 ({v, λ, g, s₀})
- Null space dimension: 1 (the direction g → αg, s₀ → s₀/α, i.e., g·s₀ scale)

**Rank = 3. Null space = 1.**

The null direction is: {g → αg, s₀ → s₀/α} for any α > 0.
Under this transformation: g²s₀² → α²g²·s₀²/α² = g²s₀² (unchanged).
All observables are invariant. Therefore g and s₀ are not individually
observable — only their product g·s₀ (or g²s₀²) is.

This is a genuine physical degeneracy: the coupling strength and the
substrate amplitude cannot be separately determined from decoherence
observables alone. An independent measurement constraining g alone
(e.g., from gravitational effects if those were predicted) would break
this degeneracy — but no such measurement exists in current C2.

---

## 6. Summary Table

| Parameter | Observable from decoherence? | Independent constraint? |
|-----------|------------------------------|------------------------|
| v | Only via ξ_c (needs spatial O4) | No — degenerate with λ until O4 |
| λ | Yes — from τ_B (O2/O3/O5) | Yes (given O2 measurement) |
| g | No — only g²s₀² measurable | No — degenerate with s₀ |
| s₀ | No — only g²s₀² measurable | No — degenerate with g |
| g²s₀² | Yes — from O1/O2 combined | Yes |
| ξ_c = v/λ | Yes — from O4 (if SNR sufficient) | Partially (shape degeneracy) |
| c = v | Yes — computed from O4/O5 | No — empirical, not predicted |

---

## 7. Conclusion

The C2 prediction map for the decoherence sector has rank 3 over a 4-dimensional
free parameter space. One degeneracy exists (g vs. s₀). The parameter v (= c)
is in principle resolvable from combining O4 and O5 measurements — but this
is an empirical determination, not a theory prediction. The theory provides
no independent constraint on v prior to measurement.

The critical practical blocker: O4 (spatial covariance) cannot be reliably
measured on Brisbane due to the K₀/power-law shape degeneracy (SNR ≈ 2,
ADVERSARIAL_NULL_AUDIT.md). Until O4 is measurable, v remains undetermined
even empirically.

**No parameter-free observable prediction exists in C2.**
All C2 predictions require at least one free parameter to be fixed from data.
