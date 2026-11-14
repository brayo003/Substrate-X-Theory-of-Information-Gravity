# 34 — Variance-to-c Decoherence Audit

**Phase 9e — C2 Quantum Layer Theoretical Audit**
**Date:** 2026-08-21
**Script:** `scripts/p29_variance_coupling_audit.py`
**Data:** `outputs/data/variance_coupling_audit.json`
**Depends on:** 32_C_PRW_SPEED_DERIVATION_AUDIT.md

---

## Purpose

Determine whether the established variance result

    <|δJ|²> = (2/3) s₀² ω_rot² r²

provides any independent constraint on c, and whether the CA-3
coupling postulate contains any hidden dependence on c, v_s, τ_B,
or spatial correlation length ξ_c.

---

## 1. Variance Derivation Chain

### Step 1: Current fluctuation δJ

**Source:** `substrate_transport_derivation.md` [ESTABLISHED-DJ]

    δJ = s₀ (ω_rot × r)

**Derivation:** The substrate current density is J = s · v_sub.
In the rotating frame, the substrate velocity field acquires a
frame-drag term: v_sub|rot = −ω_rot × r.

**Classification: DERIVED** — pure kinematic identity, no model
assumptions beyond the current definition.

**Contains c?** NO — δJ depends only on s₀ (substrate density),
ω_rot (rotation rate), and r (coupling radius).

---

### Step 2: Variance

**Source:** [ESTABLISHED-VAR]

    <|δJ|²> = (2/3) s₀² ω_rot² r²

**Derivation:**

    |ω_rot × r|² = ω_rot² r² sin²θ

Isotropic angular average:

    <sin²θ>_sphere = (1/4π) ∫ sin²θ dΩ = 2/3

Therefore:

    <|δJ|²> = s₀² ω_rot² r² · (2/3)

**Classification: DERIVED** — isotropic angular average, no model
assumptions beyond isotropy.

**Contains c?** NO — the variance parameters are {s₀, ω_rot, r}.
None of {c, v_s, τ_B, ξ_c, λ} appear.

---

### Step 3: Decoherence coupling

**Source:** CA-3 (constitutive postulate)

    Γφ ∝ <|δJ|²>

**Classification: ASSUMED [CA-3]** — explicitly labeled as a
constitutive postulate in the project. It is not derived from the
C2 Lagrangian, from the PRW telegrapher equation, or from any other
first-principles calculation within the project files.

**Contains c?** NO — the proportionality constant k_rot absorbs
all microscopic parameters. The ratio Γφ / <|δJ|²> = k_rot
encodes the coupling strength but is not determined by c.

---

### Step 4: Decoherence rate

Combining Steps 2 and 3:

    Γφ = k_rot · ω_rot²

where:

    k_rot = (8 g² s₀² r_q² τ_B) / (3 ℏ²)

**Classification: DERIVED (conditional on CA-3)**

**Does k_rot contain c?**

| Parameter | Physical meaning | Contains c? |
|-----------|-----------------|-------------|
| g | coupling constant | NO |
| s₀ | substrate density | NO |
| r_q | qubit coupling radius | NO |
| τ_B = 1/(2γ) | bath correlation time | **τ_B is related to c via ξ_c = 2cτ_B**, but τ_B itself does not contain c — it is the relaxation time of the PRW, determined by γ alone |

**k_rot contains τ_B but does NOT contain c.**

The spatial correlation length ξ_c = 2cτ_B requires both c and τ_B
independently. k_rot has τ_B through the decay rate; c enters only
when spatial structure is probed.

---

## 2. Does the Variance Chain Constrain c?

**Direct answer: NO.**

The complete chain

    δJ → <|δJ|²> → [CA-3] → Γφ = k_rot ω_rot²

contains:

- Spatial parameters: {s₀, r} — substrate density and qubit radius
- Kinematic parameters: {ω_rot} — rotation frequency
- Coupling parameters: {g, τ_B} — coupling constant and bath correlation time

None of these are c, v_s, or ξ_c. The variance derivation is
**logically independent** of the speed derivation.

The ω_rot² scaling test (Γφ ∝ ω_rot²) was confirmed computationally
in prior phases. This confirms the variance structure but provides **no
information about c** because c does not appear in that scaling relation.

---

## 3. CA-3 Hidden Dependence Check

**CA-3:** Γφ ∝ <(δJ)²>

Explicit check of the proportionality constant:

    k_rot = 8 g² s₀² r_q² τ_B / (3 ℏ²)

| Term | Depends on c? | Depends on v_s? | Depends on ξ_c? | Depends on τ_B? |
|------|------------|-------------|-------------|-------------|
| g | NO | NO | NO | NO |
| s₀ | NO | NO | NO | NO |
| r_q | NO | NO | NO | NO |
| τ_B | NO (τ_B is not c) | NO | NO | YES (is τ_B) |
| ℏ | NO | NO | NO | NO |

**Conclusion: CA-3 has NO hidden dependence on c, v_s, or ξ_c.**

τ_B appears in k_rot as the bath correlation timescale (PRW relaxation),
not combined with c. The combination 2cτ_B = ξ_c does not appear in
k_rot or in any expression derived from CA-3 alone.

---

## 4. Variance-to-c Dependency Map

```
<|δJ|²> = (2/3)s₀²ω_rot²r²
        ↓  DERIVED (isotropic average)
        ↓  → NO c dependence

        ↓  [CA-3]  ASSUMED
Γφ ∝ <|δJ|²>
        ↓
k_rot = 8g²s₀²r_q²τ_B / (3ℏ²)
        ↓  → contains τ_B, NOT c
        ↓  → NO c dependence

Separately:
ξ_c = 2 c τ_B   ← requires c independently (from speed chain)
        ↓
Spatial correlator C_C2(r) ~ K₀(r/ξ_c)
        ↓  → requires c (from speed derivation)
        ↓  → NOT obtained from variance chain alone
```

The two chains are **independent**:
- Variance chain → {Γφ, k_rot} → does not constrain c
- Speed chain → {c, ξ_c} → does not constrain <|δJ|²>

They share only τ_B as a common parameter, and even that coupling
does not allow one chain to constrain the other's distinctive
quantities.

---

## 5. Independent Test Routes from Variance (Without c)

### Route A: ω_rot² scaling
**Status: DONE, confirmed** in prior phases.
The test confirms the variance structure but is NOT C2-specific —
any bath with <J²> ∝ ω_rot² produces the same scaling.

### Route B: Lorentzian high-frequency rolloff
The full frequency-dependent decoherence rate (beyond the low-ω
limit) is:

    Γφ(ω_rot) = k_rot · ω_rot² / (1 + ω_rot² τ_B²)

The Lorentzian rolloff at ω_rot ~ 1/τ_B is C2-consistent.
However, this is also the prediction of any exponentially-correlated
(OU) bath. **Not C2-specific.**

### Route C: Decoherence anisotropy
δJ = s₀(ω_rot × r) is a vector. If the qubit coupling to the
substrate is direction-specific (coupling to a particular component
of J), the decoherence rate would be orientation-dependent:

    Γφ(θ) ∝ |ω_rot × r|² · sin²θ_coupling

This **could** be C2-specific via the geometric structure of the
PRW propagation direction vs. the qubit orientation.

**Status: CONJECTURE — not yet derived from C2 first principles
within the project files.**

If this anisotropy were derived, it would provide a C2-specific
prediction from the variance chain, independent of c.

---

## 6. CA-3 Status

```
<|δJ|²> = (2/3) s₀² ω_rot² r²     DERIVED  (supports)
Γφ ∝ <|δJ|²>                        ASSUMED [CA-3]  (constitutive postulate)
```

CA-3 **remains an unresolved constitutive postulate**. It has not been:
- Derived from a Lindblad master equation
- Derived from a spin-boson model with C2 bath spectral function
- Derived from first principles of the PRW telegrapher coupling

CA-3 is a plausible and economical assumption (Kubo-type coupling of
decoherence rate to flux variance) but it is an assumption.

---

## 7. Final Audit Verdicts

| Claim | Classification | Notes |
|-------|---------------|-------|
| <\|δJ\|²> = (2/3)s₀²ω_rot²r² | DERIVED | No CA-3 needed |
| Variance chain constrains c | **FALSE** | c absent from all variance expressions |
| CA-3 has hidden c dependence | **FALSE** | k_rot contains τ_B, not c |
| CA-3 is a proved theorem | **FALSE** | ASSUMED constitutive postulate |
| ω_rot² test discriminates C2 from OU | **FALSE** | Not C2-specific |
| Variance provides independent path to ξ_c | **FALSE** | ξ_c requires c from speed chain |
| Anisotropy route (Route C) is viable | CONJECTURE | Not yet derived |

---

*Script:* `scripts/p29_variance_coupling_audit.py`
*Output:* `outputs/data/variance_coupling_audit.json`
