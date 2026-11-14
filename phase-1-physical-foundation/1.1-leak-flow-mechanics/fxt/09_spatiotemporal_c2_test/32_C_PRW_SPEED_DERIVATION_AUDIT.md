# 32 — C / PRW Speed Derivation Audit

**Phase 9e — C2 Quantum Layer Theoretical Audit**
**Date:** 2026-08-21
**Script:** `scripts/p27_c_prw_speed_audit.py`
**Data:** `outputs/data/c_prw_speed_audit.json`

---

## Purpose

Determine, from the **existing theory only**, whether C2 actually derives

    c = v_PRW = v_s = a√(K/m)

or merely assumes/uses this equality. Every logical step is classified
with exactly one label from: DERIVED / CONDITIONALLY DERIVED / ASSUMED /
DEFINITION / EMPIRICAL INPUT / UNRESOLVED.

---

## 1. What FPUT-3 Actually Proves

**Source:** `C2_FOUNDATIONS.md`, Theorem FPUT-3 (Main Theorem IV.3)

> "The only admissible projection satisfying C1–C6 that retains only
> the action variables nₖ is the coarse-grained density
> s(x,t) = (1/N) Σₖ nₖ e^{ikx}, whose evolution is the
> telegrapher equation."

### What FPUT-3 establishes:

| Claim | Status |
|-------|--------|
| The projection type is PRW / telegrapher | ✓ DERIVED |
| The projected variable is s(x,t) = (1/N)Σₖ nₖ e^{ikx} | ✓ DERIVED |
| The value of c in τ∂²s/∂t² + ∂s/∂t = c²τ∇²s | ✗ UNRESOLVED |
| c = v_s | ✗ NOT PROVED by FPUT-3 |
| c ≤ v_s | ✗ NOT proved by FPUT-3 (comes from C3 separately) |

**FPUT-3 classification for c: UNRESOLVED**

FPUT-3 selects the *form* of the evolution equation but leaves the
propagation speed c as an unspecified parameter of that form.

---

## 2. P1 Governing Equations — Construction vs. Derivation

**Source:** `projection_classification_audit.md`, Section P1

### P1 Definition (verbatim):

    n⁺(x) = Σₖ nₖ w⁺ₖ(x)    "right-moving phonon density at x"
    n⁻(x) = Σₖ nₖ w⁻ₖ(x)    "left-moving phonon density at x"

### P1 Governing Equations (verbatim):

    ∂ₜn⁺ + v_s ∂ₓn⁺ = −γ(n⁺ − n⁻)
    ∂ₜn⁻ − v_s ∂ₓn⁻ = +γ(n⁻ − n⁺)

### Critical question

Are these equations DERIVED from the nₖ microscopic dynamics, or
STATED as the transport model consistent with the phonon interpretation?

### Finding

The individual mode actions satisfy ṅₖ = 0 exactly on the harmonic
chain (harmonic integrability). This equation describes per-mode
constants of motion. The P1 transport equations describe the *spatial
flow of action density* — a different, coarser level of description.

Within the existing project files, no derivation is given that takes
ṅₖ = 0 as input and derives the P1 transport PDEs as output. The
transport equations are **constructed** as the natural phonon-gas drift
equations for a density of right/left-moving particles.

The appearance of v_s in those equations reflects the **definition** of
n± as acoustic phonon densities — particles whose characteristic speed
is the phonon group velocity v_s. This is a model construction, not a
mathematical theorem.

**Status of v_s in P1: DEFINITIONAL**
The P1 governing equations are consistent with FPUT but not derived
from it within the existing documents.

---

## 3. C3 Admissibility Constraint — Bound or Equality?

**Source:** `projection_classification_audit.md`, C3 row

| Location | Statement | Type |
|----------|-----------|------|
| C3 definition (line 84) | "finite signal speed v_signal ≤ v_s" | INEQUALITY |
| P1 constraint table, C3 row | "Signal speed = v_s (sound speed)" | EQUALITY for P1 specifically |
| Main Theorem IV.3, step 3 | "signal speed ≤ v_s" | INEQUALITY |

### Analysis

C3 as an **admissibility constraint** imposes only an upper bound:

    c ≤ v_s   [DERIVED from C3 + FPUT acoustics]

P1 as a **construction** uses the equality c = v_s because n± are
defined to move at v_s. P1 satisfies C3 trivially (v_s ≤ v_s).

The Main Theorem uses the informal word "minimal" to describe the PRW
telegrapher as the simplest admissible system. Informally, the minimal
choice saturates the bound (c = v_s). But "minimal" is not proved to
be a theorem of uniqueness — it is a heuristic justification.

**C3 verdict:**

- C3 establishes: `c ≤ v_s` — **DERIVED** from C3 + FPUT acoustics
- Equality `c = v_s`: **NOT proved** — requires an additional identification
- Status of equality: **CONDITIONALLY DERIVED** (condition = [PHON])

---

## 4. Complete Derivation Chain

```
FPUT Hamiltonian H = Σₖ ωₖ nₖ
        ↓  ASSUMED  [substrate model, postulate A-FPUT1]
ωₖ = 2√(K/m)|sin(πk/N)|
        ↓  DERIVED  [Fourier diagonalization of harmonic chain]
v_s = a√(K/m) = (∂ωₖ/∂k)|_{k→0}
        ↓  DERIVED  [long-wavelength (acoustic) limit of dispersion]
Actions nₖ = |Aₖ|² = const
        ↓  DERIVED  [harmonic chain integrability, exact]
C3 admissibility: signal speed ≤ v_s
        ↓  DERIVED  [C3 + FPUT acoustics; inequality only]
FPUT-3: evolution of s(x,t) is the telegrapher equation
        ↓  DERIVED  [C1 locality + action-variable uniqueness]
c = ? in telegrapher   ← UNRESOLVED — FPUT-3 does not specify c
        ↓
[PHON] identification: n± are acoustic phonon densities at speed v_s
        ↓  ASSUMED / DEFINITIONAL  [physical identification, not theorem]
P1 governing equations embed v_s
        ↓  DEFINITIONAL  [follows from [PHON]]
c = v_s in C2 PRW
        ↓  CONDITIONALLY DERIVED  [holds IF [PHON] is accepted]
τ_B = 1/(2γ)
        ↓  DERIVED  [PRW relaxation, telegrapher algebra]
ξ_c = 2c · τ_B
        ↓  DERIVED  [given c — numerically determined once c is fixed]
```

### Key gap

Between "FPUT-3 proves telegrapher" and "c = v_s" there is a missing
derivation. The P1 construction fills this gap by defining n± as phonon
densities with speed v_s, but that definition is a **physical
identification** ([PHON]), not a theorem proved from FPUT alone.

---

## 5. The [PHON] Identification Assumption

**[PHON]:** *The PRW particles in the C2 coarse-grained theory are
identified with the acoustic phonons of the FPUT substrate, whose
long-wavelength group velocity is v_s = a√(K/m).*

| Property | Status |
|----------|--------|
| Physically natural | YES — acoustic phonons are the long-wavelength excitations |
| Consistent with P1 construction | YES |
| Used implicitly throughout the project | YES |
| Stated as an explicit postulate in any project document | **NO** |
| Proved as a theorem from FPUT-3 | **NO** |

Without [PHON]: c is bounded by v_s from C3 but is otherwise a free
parameter → verdict **C_PARAMETER_DEPENDENT**.

With [PHON] explicitly accepted: c = v_s = a√(K/m) → verdict
**C_CONDITIONALLY_PREDICTED**.

---

## 6. Numerical Audit

Parameters justified by the project (Si substrate FPUT model):

| Parameter | Value | Source |
|-----------|-------|--------|
| a (lattice constant) | 0.543 nm | Si crystal |
| K (effective spring constant) | 5.696 N/m | FPUT fit |
| m (Si atom mass) | 4.665 × 10⁻²⁶ kg | atomic mass |
| **v_s = a√(K/m)** | **6000 m/s** | DERIVED |

### Strongest justified bounds for c

```
C3 alone:   0 < c ≤ 6000 m/s  (upper bound only)
With [PHON]: c = 6000 m/s     (conditional equality)
```

Any value c > v_s has **no derivation** and violates C3 (inadmissible).
A previously cited c ~ 10⁴ m/s is invalid under the current theory.

### ξ_c = 2c·τ_B at c = v_s = 6000 m/s

| τ_B | ξ_c | Status vs chips |
|-----|-----|-----------------|
| 0.05 µs | 0.06 cm | << 7-qubit 632 µm — blocked |
| 0.75 µs | 0.90 cm | < Heron 12 mm — conditionally accessible |
| 1.00 µs | 1.20 cm | ~ Heron 12 mm |
| 1.17 µs | 1.40 cm | ~ Eagle 14 mm — conditionally accessible |
| 5.00 µs | 6.00 cm | >> all chips — blocked |

### τ_B required for ξ_c to match specific distances

| Target ξ_c | τ_B required |
|------------|-------------|
| 632 µm (7-qubit sim) | 0.053 µs |
| 1 mm | 0.083 µs |
| 10 mm (1 cm) | 0.833 µs |
| 12 mm (Heron) | 1.000 µs |
| 14 mm (Eagle) | 1.167 µs |

---

## 7. Three Equalities — Audit Summary

| Equality | Status | Basis |
|----------|--------|-------|
| v_s = a√(K/m) | **DERIVED** | long-wavelength limit of FPUT dispersion |
| v_PRW = v_s | **CONDITIONALLY DERIVED** | requires [PHON] identification |
| c = v_PRW | **CONDITIONALLY DERIVED** | requires P1 construction + [PHON] |
| Combined c = v_s = a√(K/m) | **CONDITIONALLY DERIVED** | condition = [PHON] |

---

## 8. Final Verdict

```
B. C_CONDITIONALLY_PREDICTED

c = v_s = a√(K/m) ≈ 6000 m/s (Si)

Condition: [PHON] — PRW particles identified with FPUT acoustic phonons.

This condition is:
  - Physically natural
  - Implicitly used throughout the project
  - NOT stated as an explicit postulate
  - NOT proved as a theorem

Without [PHON]: C_PARAMETER_DEPENDENT (c ∈ (0, v_s], otherwise free)
With    [PHON]: C_CONDITIONALLY_PREDICTED (c = 6000 m/s)
```

The verdict **C_PREDICTED** (unconditional) is **not supported** by the
existing theory. A complete derivation would require either:

1. A proof that FPUT-3 uniquely identifies the PRW speed as v_s, or
2. Explicit postulation of [PHON] as a named axiom.

Neither is present in the existing files.

---

*Script:* `scripts/p27_c_prw_speed_audit.py`
*Output:* `outputs/data/c_prw_speed_audit.json`
