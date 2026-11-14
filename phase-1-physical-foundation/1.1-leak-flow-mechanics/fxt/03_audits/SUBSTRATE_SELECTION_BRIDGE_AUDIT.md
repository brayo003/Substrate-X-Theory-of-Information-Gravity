# SUBSTRATE_SELECTION_BRIDGE_AUDIT.md
## Cross-Audit: Can Information Selection Close the C2/Giga Substrate Gap?

**Date:** 2026-10-10
**Status:** SUPERSEDED -- GMS IS NON-UNIQUE WITHOUT A FURTHER BRANCH RULE
**Scope:** C2 transport, Giga transition-relation ontology, and the Information
Selection Problem firewall.

---

## Subsequent adversarial result (2026-10-10)

This document introduced GMS as a candidate bridge. The elastic calculation in
`GMS_ADVERSARIAL_AUDIT.md` shows non-degenerate transverse and longitudinal
acoustic branches with different long-wavelength velocities. Whether both pass
the GMS coarse-graining and kinetic tests remains conditional. Accordingly, the
conditional `c = v_s` conclusion below is superseded as a general claim. GMS
remains unvalidated until its coupling and kinetic premises are derived.

---

## 1. Purpose

The current project contains three partially separate mathematical tracks:

1. **C2/PRW transport:** derives telegrapher dynamics once a carrier speed `c`
   and reversal rate `lambda` are supplied.
2. **Giga transition ontology:** replaces field values by admissible transition
   relations `R`, but leaves temporal propagation and source coupling unresolved.
3. **Information Selection Problem:** demands that any selection principle be
   non-circular: it must not encode the desired answer in its premises.

This audit asks whether the information-selection track can close a real C2
substrate gap: the free PRW propagation speed.

Short answer:

> The existing mathematics cannot derive `c`. A new selection principle can
> conditionally fix `c = v_s`, but only if it independently selects the
> gapless acoustic carrier sector. This is a new named bridge principle, not
> a theorem already present in the repository.

---

## 2. The Gap Being Targeted

From `THEORY_CLOSURE_AUDIT.md` and
`09_spatiotemporal_c2_test/32_C_PRW_SPEED_DERIVATION_AUDIT.md`:

```text
tau_B = 1/(2 lambda)
xi_c  = c/lambda = 2 c tau_B
c     = xi_c/(2 tau_B)
```

The PRW equations derive the relations above, but not the numerical value of
`c`. Without an independent rule for `c`, the temporal and spatial sectors remain
jointly measurable but not theoretically predicted.

Current classification:

| Claim | Status |
|-------|--------|
| PRW/telegrapher form | DERIVED from the chosen PRW projection |
| `tau_B = 1/(2 lambda)` | DERIVED |
| `xi_c = 2 c tau_B` | DERIVED given `c` |
| `c <= v_s` | DERIVED if C3 finite-signal constraint is accepted |
| `c = v_s` | CONDITIONAL on `[PHON]` |
| `[PHON]` itself | ASSUMED / DEFINITIONAL |

The open mathematical question is therefore:

> Can `[PHON]` be replaced by a non-circular selection theorem or at least by a
> precise selection principle compatible with the Information Selection firewall?

---

## 3. No-Go: Transition Composition Alone Cannot Select `c`

### Theorem S1 - Spatial transition relations do not determine a speed

Let `R(x,y)` be any Giga-style spatial transition relation satisfying local
composition along admissible paths:

```text
R(x,z) = R(y,z) R(x,y)
```

for path-consecutive `x -> y -> z`. Let `c > 0` be any finite constant. Define
a spacetime admissibility cone:

```text
K_c(x,t) = { (dx,dt) : dt >= 0 and |dx| <= c dt }.
```

Then `(R, K_c)` satisfies finite local continuation for every positive `c`.
Changing `c` changes the temporal parametrization of admissible histories but
does not change the spatial transition composition law.

### Proof

The relation `R(x,y)` constrains spatial transport between configurations. The
cone `K_c` constrains the allowed spacetime tangent vectors. The composition
law for `R` contains no temporal unit and no ratio `|dx|/dt`; hence replacing
`c` by `alpha c` with `alpha > 0` leaves all spatial compositions unchanged.
For every `c > 0`, `K_c` is a valid local cone and permits continuation along
curves whose tangent lies inside the cone. Therefore spatial transition
composition plus continuation determines at most the existence of a finite cone,
not its slope.

**Result:** transition-relation ontology can justify a finite-speed *form*, but
not a finite-speed *value*.

This matches Giga's own conclusion that finite propagation remains unresolved:
spatial connection structure is not temporal dynamics.

---

## 4. No-Go: Finite Signal Speed Gives a Bound, Not Equality

Let `v_s` be the long-wavelength acoustic speed of the material substrate:

```text
v_s = a sqrt(K/m).
```

If C3 is accepted as an admissibility constraint, then:

```text
0 < c <= v_s.
```

But the interval `(0, v_s]` is still infinite. For every `beta` with
`0 < beta <= 1`, the choice `c = beta v_s` satisfies the bound.

Therefore:

```text
C3 + FPUT acoustics  =>  c <= v_s
C3 + FPUT acoustics  !=> c = v_s
```

The equality requires one more premise.

---

## 5. Candidate Bridge Principle

### GMS - Gapless Minimal-Support Selection

**Principle GMS:**

> The physically realized information carrier sector is the gapless,
> long-wavelength sector with minimal microscopic support that preserves
> distinguishability under coarse-graining.

More explicitly, among candidate substrate modes `M_i`, select the sector that
satisfies:

1. **Gapless propagation:** `omega(k) -> 0` as `k -> 0`.
2. **Long-wavelength distinguishability:** coarse-grained density perturbations
   remain distinguishable at macroscopic scale.
3. **Minimal support:** no additional internal labels, hidden sectors, or massive
   branches are introduced unless required by 1-2.
4. **Finite-speed compatibility:** the selected sector respects the C3 bound.

In an FPUT/harmonic-chain substrate, the sector satisfying these criteria is the
acoustic branch. Its group speed is:

```text
v_s = (d omega/dk)|_{k -> 0} = a sqrt(K/m).
```

If the PRW carriers are selected by GMS, then the right/left carrier densities
`n+` and `n-` are acoustic carrier densities. Their characteristic speed is
therefore fixed:

```text
c = v_s = a sqrt(K/m).
```

### Classification

| Step | Status |
|------|--------|
| FPUT acoustic dispersion | DERIVED from harmonic-chain diagonalization |
| `v_s = a sqrt(K/m)` | DERIVED in the long-wavelength limit |
| GMS selects the acoustic branch | NEW PRINCIPLE, not derived |
| PRW carrier speed equals selected branch speed | DERIVED conditional on GMS |
| `c = v_s` | CONDITIONALLY DERIVED |

GMS is therefore not a closure theorem. It is a candidate missing principle that
turns `[PHON]` from an implicit identification into an explicit selection rule.

---

## 6. Information-Selection Firewall Check

The Information Selection Problem requires that a principle must not smuggle the
target answer into its premises.

### Does GMS encode `c = v_s` directly?

No. GMS does not mention `v_s`, sound, phonons, silicon, or the target value of
`c`. It selects a mode class by structural criteria: gapless, long-wavelength,
minimal support, distinguishability preserving.

### Does GMS indirectly encode the target?

Partially. In an FPUT substrate, the gapless long-wavelength branch is already
known to be acoustic. Thus GMS is close to `[PHON]`; it does not invent a new
derivation from nothing. Its value is that it gives a non-circular reason for
choosing `[PHON]` over arbitrary slower carriers.

### Firewall verdict

```text
GMS passes the weak firewall:
    It does not state c = v_s as a premise.

GMS does not pass the strong theorem standard:
    It is an added selection principle, not a result forced by C2/Giga alone.
```

---

## 7. Consequences If GMS Is Accepted

For a silicon substrate with the existing project values:

```text
a = 0.543 nm
K = 5.696 N/m
m = 4.665e-26 kg
v_s = a sqrt(K/m) ~= 6000 m/s
```

The C2 spatial length becomes:

```text
xi_c = 2 v_s tau_B.
```

Representative values:

| `tau_B` | `xi_c` if `c = 6000 m/s` |
|---------|--------------------------|
| 0.05 microseconds | 0.60 mm |
| 0.75 microseconds | 9.0 mm |
| 1.00 microseconds | 12.0 mm |
| 1.17 microseconds | 14.0 mm |
| 5.00 microseconds | 60.0 mm |

This converts the theory from "free speed" to "material-locked speed" under GMS.

---

## 8. New Falsifiable Predictions Under GMS

If GMS is true, `c` is not a universal arbitrary substrate constant. It is locked
to the selected material carrier sector.

### P-GMS1: Material dependence

Changing substrate material changes the predicted spatial coherence length:

```text
xi_c(material) = 2 v_s(material) tau_B.
```

At fixed `tau_B`, two materials with different acoustic speeds must show different
`xi_c` in the same ratio as their `v_s`.

### P-GMS2: Isotopic mass dependence

If the effective spring constant `K` is held fixed but atomic mass changes:

```text
c proportional to 1/sqrt(m).
```

Thus isotopic substitution should shift the inferred `xi_c/tau_B` ratio.

### P-GMS3: Defect/strain dependence

If defects or strain modify the acoustic branch, the inferred C2 speed should
track the modified long-wavelength group velocity, not remain fixed.

### P-GMS4: Exclusion of super-acoustic fits

Any inferred value

```text
c_inferred = xi_c/(2 tau_B) > v_s
```

falsifies C3 + GMS for that substrate.

---

## 9. What GMS Does Not Fix

GMS only targets the speed-selection gap. It does not fix:

| Remaining gap | Status after GMS |
|----------------|------------------|
| Reversal rate `lambda` | still free / empirical |
| Coupling constant `g` | still free |
| Background substrate density `s0` | still free |
| Planck constant `hbar` | still imported |
| Quantum state-space origin | unchanged |
| Giga mass coupling `A(M)` | unchanged |
| Giga collapse scale | unchanged |
| R1 cosmological initial data sector | unchanged |

So the result is narrow but real: it removes one free parameter only if the new
selection principle is accepted.

---

## 10. Final Verdict

```text
Existing C2 + Giga:
    c is not derived.

Existing C2 + Giga + finite-speed admissibility:
    0 < c <= v_s.

Existing C2 + Giga + GMS:
    c = v_s = a sqrt(K/m), conditionally.
```

### Scientific status

**STATE S1 - CONDITIONAL SPEED CLOSURE**

The math now says exactly where the substrate theory can be strengthened:

1. The old implicit `[PHON]` assumption should be replaced by the explicit GMS
   selection principle if the project wants `c = v_s`.
2. GMS is not yet derived, but it is cleaner and more falsifiable than `[PHON]`.
3. The next mathematical task is to prove or kill GMS:
   classify all FPUT coarse-grained sectors satisfying gaplessness,
   distinguishability preservation, and minimal support.

If that classification has a unique winner, `[PHON]` becomes a theorem.
If it has multiple winners, `c` remains free.

---

## 11. Next Work Item

Build a finite classification table of candidate carrier sectors:

| Sector | Gapless | Distinguishable after coarse-grain | Minimal support | Speed fixed? |
|--------|---------|-------------------------------------|-----------------|--------------|
| Acoustic phonon branch | yes | yes | yes | `v_s` |
| Optical branch | no | conditional | no | no |
| Defect hopping mode | no/gapped | local only | no | rate-dependent |
| Arbitrary PRW carrier | assumed | assumed | no | free |
| Transition-relation holonomy | spatial only | yes | no temporal scale | no |

This table is the shortest route to determining whether the substrate theory can
turn GMS from a candidate principle into a theorem.
