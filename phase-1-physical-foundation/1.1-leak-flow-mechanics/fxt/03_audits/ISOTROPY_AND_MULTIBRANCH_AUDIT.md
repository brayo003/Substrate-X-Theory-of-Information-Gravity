# Isotropy, Silicon's Role, and Multi-Branch Reformulation Audit

**Date:** 2026-10-10  
**Status:** COMPLETE  
**Executable validation:** `04_validations/multibranch_prw_test.py`  
**Output:** `04_validations/outputs/multibranch_prw_test.json`  
**Preceding audit:** `MICROSCOPIC_C2_COUPLING_DERIVATION_AUDIT.md`

---

## 1. Executive Summary

The previous audit concluded that the missing physics is "isotropic elastic substrate"
and "J_C2 identified with scalar dilatation." The present audit examines whether those
conclusions stand up as requirements, or whether the theory permits alternatives.

Four questions are answered:

1. **Does SXC-IGC require its fundamental substrate to be isotropic?**  
   No. The abstract C2/PRW substrate has no material symmetry requirement.
   Isotropy was an implicit consequence of the single-speed PRW postulate A-PRW1,
   not a physical requirement on any material.

2. **Is silicon the proposed substrate, or the experimental medium?**  
   Silicon is the experimental platform. The C2 foundational documents (01_foundations,
   02_derivations) contain zero references to silicon, phonons, or elastic media.
   Silicon enters only in the 03_audits layer, through an unnamed implicit assumption
   "[PHON]" that was already present before the current audit series.

3. **Can isotropy be justified from the theory's existing symmetries?**  
   No. The PRW axiom A-PRW1 (uniform speed v) is a postulate, not a theorem.
   There is no derivation of v from the CCA axioms, from FPUT dynamics, or from
   any other existing C2 structure. The single-speed constraint is definitionally
   imposed, not derived.

4. **Does multi-branch reformulation produce a distinct prediction?**  
   No. Multi-branch C2 is internally consistent but produces observational predictions
   identical to a conventional multi-component Lorentzian bath. It erases the
   only surviving C2 discriminator (the P3 ratio) without replacing it with
   anything new.

**Central finding:** Imposing isotropy to obtain a unique speed is not justified by
the theory. The theory must either derive a unique speed from its own axioms, or accept
that it cannot make branch-specific predictions and reformulate accordingly. The
reformulation is internally consistent but scientifically empty without a first-principles
derivation of the branch speeds and coupling weights.

---

## 2. Where Isotropy Actually Comes From in C2

The C2/PRW transport layer imposes a single speed `c = v` via assumption **A-PRW1:**

> "Walker speed v and flip rate λ are constant (spatially and temporally uniform)."

Source: `C2_FOUNDATIONS.md`, Subsystem 1, Assumptions.

This is a postulate about the abstract PRW process, not a statement about any physical
material. It says the information quanta all travel at the same speed in all directions.
It is operationally equivalent to requiring isotropic propagation at the level of the
abstract substrate — but it achieves this by definitional fiat, not by physical reasoning.

The 3D generalization of the PRW is listed as an **open problem** in `C2_FOUNDATIONS.md`:

> "Multi-dimensional generalization of the PRW (1D result only)."  
> "Open problem: does the 3D PRW also project uniquely to the 3D telegrapher equation?"

Therefore the claim that "the C2 substrate is isotropic" is not a theorem. It is a
consequence of accepting A-PRW1 without question in 1D and not yet having a 3D derivation.

**Tracing A-PRW1 further back:** A-PRW1 is not derived from the CCA axioms Ax1–Ax5.
The CCA layer has no metric, no speed, and no propagation. Speed enters C2 only when
the PRW is constructed as a specific model on top of CCA. It enters as a free parameter.

**Conclusion:** The C2 theory does not require its substrate to be isotropic. It
*assumes* it via A-PRW1. That assumption is not forced by anything deeper.

---

## 3. Silicon's Actual Role in the Theory

Tracing silicon through the document hierarchy:

| Layer | Documents | Silicon mentioned? |
|-------|-----------|-------------------|
| CCA axioms | `C2_FOUNDATIONS.md` §CCA | No |
| PRW/telegrapher | `C2_FOUNDATIONS.md` §1–3, `02_derivations/` | No |
| Quantum coupling | `interaction_hamiltonian_derivation.md` | No |
| Experimental design | `GAP7_REDERIVATION.md`, `THEORY_CLOSURE_AUDIT.md` | Brief reference to chip |
| Substrate candidate | `SUBSTRATE_SELECTION_BRIDGE_AUDIT.md` | Yes, as GMS candidate |
| Elastic calculation | `GMS_ADVERSARIAL_AUDIT.md`, `C2_ELASTIC_COUPLING_AUDIT.md` | Yes, as test case |

Silicon is the **experimental platform** — the physical material in which superconducting
qubits are fabricated. It was introduced as a substrate candidate via the implicit
assumption `[PHON]` (silicon acoustic phonons carry the C2 substrate), which the
`SUBSTRATE_SELECTION_BRIDGE_AUDIT.md` names explicitly and classifies as unproven.

The C2 theory makes no claim that silicon *is* the fundamental substrate. The theory
proposes an abstract information substrate that may *couple* to silicon. Those are
different claims. The acoustic phonon calculation tests what would happen *if* the
C2 substrate were silicon phonons — it is a conditional test, not a verification of
an existing derivation.

---

## 4. Can Isotropy Be Derived from Existing Structure?

Three routes were checked:

**Route 1: From CCA symmetries.**  
The CCA axioms Ax1–Ax5 define a category of objects, morphisms, and a probability weight.
They have no spatial metric, no propagation speed, and no isotropy constraint.
Isotropy cannot be derived from a structure that has no spatial content.
**Result: BLOCKED.**

**Route 2: From FPUT projection.**  
The FPUT harmonic chain (1D) gives a single acoustic branch with speed `v_s = a√(K/m)`.
The projection theorem (FPUT-3) selects the PRW as the unique coarse-grained description.
This gives one speed — but only because the 1D chain has one acoustic mode.
A 3D FPUT lattice with cubic symmetry has three acoustic branches (LA, TA1, TA2) and
does not give a unique speed. The 3D projection theorem has not been derived.
**Result: 1D gives unique speed trivially; 3D is open and expected to give multiple speeds.**

**Route 3: From the admissibility constraints C1–C6.**  
Constraint C3 (finite signal speed) gives `c ≤ v_s`, a bound. It does not select a
specific speed and does not require isotropy.
**Result: BLOCKED.**

No route within the existing theory derives isotropy or a unique speed in 3D.

---

## 5. Multi-Branch PRW: Consistency and Predictions

### 5.1 Internal Consistency

A multi-branch PRW with B branches, each having speed `v_b` and reversal rate `λ_b`,
satisfies B independent telegrapher equations:

```
τ_b ∂²s_b/∂t² + ∂s_b/∂t = v_b² τ_b ∂²s_b/∂x²     (b = 1,...,B)
```

Each branch is internally consistent. Conservation `Q_b = ∫ s_b dx` holds per branch.

**However:** The total density `S = Σ_b w_b s_b` satisfies a **6th-order PDE** for 3
branches (product of three telegrapher operators), not the single telegrapher equation
that is the structural core of C2. This contradicts A-PRW1 at the level of the total
field observable.

Verified numerically: `transport['_total_field_status']['S_is_single_telegrapher'] = False`  
PDE order for S with 3 branches: **6**.

### 5.2 Observable Predictions vs Conventional Phonon Bath

The per-branch C2 spectral density is:

```
S_b(ω) = 2 S₀ τ_b / (1 + ω² τ_b²)     [Lorentzian]
```

A conventional Ornstein-Uhlenbeck (Drude) bath spectral density is:

```
S_Drude(ω) = 2 η Ω_c / (ω² + Ω_c²) = 2 η τ / (1 + ω² τ²)
```

with `τ = 1/Ω_c`. These are **algebraically identical** with `S₀ = η`.

Multi-branch C2:

```
S_total(ω) = Σ_b w_b S_b(ω) = Σ_b w_b * 2 S₀ τ_b / (1 + ω² τ_b²)
```

Multi-component Drude bath:

```
S_Drude_multi(ω) = Σ_b w_b * 2 η_b τ_b / (1 + ω² τ_b²)
```

Verified numerically: `multibranch_C2_PSD_equals_conventional_Drude = True`  
(Maximum absolute difference: < 10⁻¹²)

**The temporal spectral density of multi-branch C2 is algebraically identical
to a conventional multi-component Drude bath. They are observationally
indistinguishable from any temporal measurement.**

### 5.3 Spatial Correlator

Multi-branch C2 spatial correlator:

```
C_multi(r) = Σ_b w_b K₀(r/ξ_b) / K₀(a/ξ_b)
```

with `ξ_b = 2 v_b τ_b`. This differs in shape from a single K₀ if the `ξ_b` values
are well-separated. Tested numerically: for equal `τ_b = 1 μs`, the ratio of
multi-branch to single-branch correlator varies by only **0.12%** across 0.1–20 mm.

A conventional bath with two timescales produces the same K₀ sum with the same
functional form. No spatial measurement can distinguish multi-branch C2 from a
conventional bath with the same `(w_b, ξ_b)` parameters, because those parameters
are fitted, not predicted.

### 5.4 The P3 Ratio

The only surviving C2 discriminator (from `THEORY_CLOSURE_AUDIT.md`) is the P3
consistency ratio `c = ξ_c / (2 τ_B) = const`.

For multi-branch C2, the per-branch ratio is `ξ_b / (2 τ_b) = v_b`, which varies
by **65%** across the three silicon acoustic branches (4893–9157 m/s).

There is no unique P3 ratio in multi-branch C2. The reformulation erases the only
observable that distinguished C2 from a generic bath model.

---

## 6. The Core Structural Problem

The foundational C2 issue is a level-of-description mismatch:

**Level 1 (abstract substrate):** The CCA and PRW describe an abstract information
transport process. At this level the substrate has one speed `c`, which is a free
parameter with no material identity.

**Level 2 (physical substrate):** Any physical realization couples the abstract
substrate to a material. If that material is silicon, it has three acoustic branches.
The coupling must specify which branch (or which mixture) corresponds to the abstract
C2 carrier.

**The mismatch:** The existing theory writes `H_int = g J_C2 σ_z` and treats `J_C2`
as a classical bath field. But the theory never specifies what physical field `J_C2` is.
It is not a silicon displacement field, not a strain, not a momentum density. It is
an abstract information flux with units `[info/(m² s)]` that have no direct counterpart
in any known physical observable.

Without resolving this mismatch — deriving what `J_C2` *is* in terms of a physical field
— the question "isotropic or anisotropic substrate?" has no answer inside the theory.
The theory simply doesn't reach that level.

---

## 7. What This Means for the Forward Path

**The theory cannot impose isotropy as a requirement** because:
- Isotropy at the abstract PRW level is a postulate (A-PRW1), not a derivation.
- Isotropy at the physical material level is a property of the material, not of C2.
- The two levels are not yet connected by any existing equation.

**The theory cannot accommodate multi-branch propagation productively** because:
- Multi-branch C2 is observationally equivalent to a conventional phonon bath.
- It erases the P3 discriminator.
- It adds free parameters without adding predictive power.

**The actual missing step is earlier than either of these:**  
The theory needs to specify what physical observable `J_C2` represents *before* asking
whether the substrate is isotropic. Without that specification, neither isotropy nor
multi-branch structure is a well-posed question.

---

## 8. What Would Be a Productive Next Step

The experiment of measuring orientation-dependent coherence times in silicon would
test a phonon-bath model. It would discriminate C2 from conventional phonon physics
only under a specific condition:

> C2 predicts a `c = ξ_c/(2 τ_B)` ratio that is **independent of crystal orientation**,
> because the abstract PRW speed `c` is a property of the information substrate, not of
> the silicon crystal. If the silicon crystal determines `c`, then `c` would be
> direction-dependent (varying 8435–9355 m/s), which would be conventional phonon behavior.
> If `c` is a universal information-substrate constant, it should be the same for all
> crystal orientations — which would be anomalous relative to conventional elasticity.

**This is a genuine discriminating prediction** — but it requires that:

1. The C2 coupling be strong enough to produce a measurable dephasing signal.
2. The P3 ratio be measurable with precision better than ~10% (the LA speed anisotropy).
3. The crystal orientation be varied independently of other qubit parameters.

None of these conditions is currently satisfied experimentally, and the theory cannot
yet predict the magnitude of the coupling, only its angular structure.

**The minimum prior task** (before any experiment) remains: identify the physical
observable that `J_C2` represents. Without it, there is no prediction to test.

---

## 9. Closure Classification Update

This audit does not change the theory's state **T2 (structurally underdetermined)**
from `THEORY_CLOSURE_AUDIT.md`.

The prior audit's conclusion ("missing physics = isotropic elastic substrate") is
partially revised: isotropy is not the missing postulate, it is a symptom of
the deeper missing element — the identification of `J_C2` with a specific physical
observable. Until that identification is made, all questions about branch selection,
isotropy, and unique speed are premature.

The gap hierarchy from most to least fundamental:

1. **Gap 0 (new, most fundamental):** Identify what physical observable `J_C2` is.
   Without this, neither branch selection nor isotropy can be addressed.

2. **GAP-7 (confirmed):** Derive `c` from the theory's axioms. Blocked until Gap 0 is resolved.

3. **Gap-kinetic (conditional):** Derive the kinetic reduction from coherent modes to PRW.
   Conditional on Gap 0.

4. **Gap-g (existing):** Derive the coupling constant `g`. Conditional on Gap 0.

---

## 10. Reproducible Commands

```bash
cd phase-1-physical-foundation/1.1-leak-flow-mechanics/fxt
python 04_validations/multibranch_prw_test.py
# Output: 04_validations/outputs/multibranch_prw_test.json
```

All assertions verified. Script exits with status 0.
