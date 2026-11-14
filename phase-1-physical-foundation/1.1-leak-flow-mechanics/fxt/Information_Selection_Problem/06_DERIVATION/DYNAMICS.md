# DYNAMICS
## Gate 6 — Deriving Cosmological Dynamics from the Primitive

---

### Status Notice

**This file is a TEMPLATE/PLACEHOLDER.** Gate 5 not yet passed.

This file records what must be derived — the dynamical content that transforms a structural selection principle into a physical theory.

---

## Section 1: Why Dynamics Is Required

A structural selection principle (e.g., "only smooth initial states are physically realizable") is not a complete physical theory. It specifies which states are allowed but does not specify how they evolve, nor does it predict any observable that differs from standard cosmology.

To pass Gate 6, the primitive must produce:
1. An evolution equation (or a modification to the GR evolution equations) that follows from the primitive
2. Cosmological dynamics consistent with the observed CMB and LSS (the standard picture must be recovered as a limit)
3. At least one deviation from standard GR + ΛCDM evolution that is in principle observable

If the primitive produces only selection without dynamics, it is equivalent to postulating the initial condition — which is not an explanation but a restatement of the problem.

---

## Section 2: Three Types of Dynamical Content

### Type 1 — Constraint on Initial Data Only
The primitive restricts the initial data but does not modify the evolution. The subsequent dynamics is standard GR.

**Consequence:** No dynamical deviation from standard cosmology. The observable signature, if any, would be in the structure of the initial conditions themselves — not in the subsequent evolution.

**This is the July 2026 paper's level.** Selection principle only; no dynamics.

**Is this sufficient for Gate 6?** Only if a unique prediction about the initial power spectrum (or some other initial-data observable) follows that differs from the standard parametrization.

### Type 2 — Modified Evolution Equation
The primitive is expressed as an additional term in the equations of motion (or a modification to the GR action).

**Consequence:** The universe evolves differently from standard GR. The deviation would be most prominent at early times (near the Planck scale or inflationary epoch) but might leave imprints in the CMB or gravitational wave background.

**This is the stronger version.** A modified evolution equation + selection would be a genuine new theory.

### Type 3 — Emergent Dynamics from Primitive Alone
The primitive does not modify the GR evolution equations but defines an effective dynamics in the space of possible initial conditions.

**Consequence:** The universe's trajectory through configuration space is constrained by the primitive, but the point-by-point evolution is standard GR. The primitive acts as a superselection rule on the ensemble of possible universes, not on the dynamics of any single universe.

**This is the multiverse/ensemble level.** Hard to test directly; may be unfalsifiable.

---

## Section 3: The Ideal Dynamical Output

For this program, the ideal output from Gate 6 is Type 2: a modified evolution equation that:
- Reduces to GR in the standard post-inflationary regime (passes known tests)
- Produces a specific deviation at high curvature / early times
- Predicts an observable feature in: the primordial gravitational wave spectrum, CMB non-Gaussianity, the tensor-to-scalar ratio r, or the primordial power spectrum tilt at extreme scales

The observable feature must be outside: `{predictions of GR + standard ΛCDM}`.

---

## Section 4: Template for Dynamical Derivation

When a primitive P is cleared:

**Step 1 — Derive the effective action:**
```
S_eff = S_GR + S_P[g, matter, ...]
```
where S_P is the contribution from the primitive. The derivation must show S_P follows from P, not the reverse.

**Step 2 — Derive the equations of motion:**
```
δS_eff / δg^μν = 0  →  G_μν + Λg_μν = 8πG T_μν + T^P_μν
```
where T^P_μν encodes the contribution of the primitive to the gravitational dynamics.

**Step 3 — Take the cosmological limit:**
```
Apply to FLRW background (as a test, not an assumption):
a(t) evolution → modified Friedmann equations
```
Verify the modification is small at late times (standard cosmology recovered).

**Step 4 — Identify the deviation:**
```
At what epoch does T^P_μν become significant?
What observable is affected?
```

**Step 5 — Compute the prediction:**
```
Predicted observable O = O_standard + δO(P)
δO must be nonzero and measurable.
```

---

## Section 5: Kill Conditions for Dynamics

The dynamics step is killed if:
- No deviation from standard GR follows (Type 1 only — no prediction)
- The deviation is indistinguishable from existing ΛCDM parameters
- The equations of motion are mathematically ill-defined (non-renormalizable, acausal, etc.)
- The GR limit is not recovered (conflicts with established tests of GR)

---

*Document status: TEMPLATE — awaiting Gate 5 clearance*
