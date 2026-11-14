# GMS_ADVERSARIAL_AUDIT.md
## Operational Test of Gapless Minimal-Support Selection in Cubic Silicon

**Date:** 2026-10-10
**Status:** REVISED -- ELASTIC SPEED COUNTEREXAMPLE; FULL GMS TEST INCOMPLETE
**Result:** `ELASTIC_MODE_SPEED_NONUNIQUENESS`
**Microscopic model:** long-wavelength linear elasticity of cubic silicon.
**Numerical validation:** `04_validations/gms_adversarial_validation.py`

**Scope correction (2026-10-10):** The numerical calculation diagonalizes the
Christoffel matrix and verifies distinct acoustic velocities. It does not itself
prove distinguishability preservation, minimal support, or a microscopic PRW
reversal process. The G2/G3 and PRW statements below are conditional analytical
assumptions, not direct outputs of that script.

---

## 1. Question and Scope

The question is deliberately narrow:

> Does GMS, stated only as gaplessness, distinguishability preservation, and
> minimal support, select one carrier sector and therefore one PRW speed?

The monatomic one-dimensional FPUT chain used in the earlier projection audit
has only one acoustic branch. It cannot test branch uniqueness for silicon.
This audit instead uses the continuum limit appropriate to a cubic elastic
silicon crystal. It has three acoustic branches for every propagation direction:
one longitudinal (LA) and two transverse (TA1, TA2).

Optical lattice modes are not included in the admissible set because their
long-wavelength frequency is nonzero. Defect modes and externally imposed PRW
carriers are not eigenbranches of the specified elastic model and therefore are
not candidates in this test.

---

## 2. Operational GMS Tests

Let `D(k)` be the mass-normalized microscopic dynamical matrix. In the elastic
limit for wave vector `k n`, where `|n| = 1`, its eigenproblem is

```text
Gamma(n) e_b(n) = rho v_b(n)^2 e_b(n),
omega_b(k n) = v_b(n)|k| + O(|k|^2).
```

For a cubic elastic medium, `Gamma` is the Christoffel matrix. A candidate
carrier sector is a branch bundle `b` over an open set of directions.

### G1. Gaplessness

`b` passes G1 iff

```text
lim_(k -> 0) omega_b(k n) = 0
and
0 < v_b(n) = lim_(k -> 0) omega_b(k n)/|k| < infinity.
```

This excludes optical branches, whose `omega_b(0) > 0`, and any zero-velocity
sector.

### G2. Distinguishability preservation

Let `P_b(n)` be the spectral projector of `Gamma(n)` onto branch `b`. A branch
passes G2 iff there is an open directional neighbourhood `U` on which:

```text
P_b(n) P_b'(n) = 0  for every b' != b,
rank P_b(n) is constant,
and a local strain/velocity observable L_b obeys
L_b P_b != 0,   L_b P_b' = 0  for b' != b.
```

Equivalently, the branch-resolved coarse-grained energy density
`E_b(x,t)` remains a separately measurable hydrodynamic field rather than
collapsing into an indistinguishable scalar total. At generic directions the
three cubic-silicon acoustic eigenvalues are distinct, so their spectral
projectors establish the mathematical separation part of this test. A physical
local observable `L_b` and its C2 coupling still require a separate derivation.

### G3. Minimal support

For a fixed branch and a chosen ray coordinate `s = n dot x`, define the
smallest directional transport state as

```text
X_b = (n_b^+(s,t), n_b^-(s,t)).
```

`b` passes G3 iff its branch-projected linear dynamics closes on this pair up to
the reversal/scattering operator, and no extra massive mode or hidden carrier
label is required. The branch label `b` and propagation direction `n` specify
the sector; they are fixed indices, not added dynamical state variables.

This is intentionally a structural test. A rule that rejects transverse modes
solely because they have polarization would be an additional axiom, not a
consequence of the three stated GMS criteria.

### GMS selection rule tested

```text
Admissible_GMS = { b : G1(b) and G2(b) and G3(b) }.
```

Uniqueness requires `|Admissible_GMS| = 1` after the material and propagation
geometry are specified.

---

## 3. Silicon Mode Enumeration

The validation uses approximate room-temperature silicon constants:

| Quantity | Value |
|---|---:|
| `C11` | `165.7 GPa` |
| `C12` | `63.9 GPa` |
| `C44` | `79.6 GPa` |
| `rho` | `2330 kg/m^3` |

For direction `n = (l,m,p)`, the Christoffel matrix is

```text
Gamma_ii = C11 n_i^2 + C44 (1 - n_i^2)
Gamma_ij = (C12 + C44) n_i n_j,  i != j.
```

Its three positive eigenvalues give the acoustic velocities. Every acoustic
branch passes G1. Away from accidental symmetry degeneracies, each eigenvector
has its own projector; this is necessary but not sufficient for G2. The
two-direction state `X_b` is a candidate kinetic state, not a derived G3 result.

| Direction | TA1 (m/s) | TA2 (m/s) | LA (m/s) |
|---|---:|---:|---:|
| `[100]` | 5844.920 | 5844.920 | 8433.023 |
| `[110]` | 4673.916 | 5844.920 | 9134.193 |
| `[111]` | 5094.248 | 5094.248 | 9356.246 |
| `generic_[123]` | 4893.090 | 5626.044 | 9156.820 |

The high-symmetry transverse degeneracies are not used for the proof below.
The generic direction has three distinct eigenvalues.

---

## 4. Counterexample to Uniqueness

Choose the same silicon material and the same generic direction
`n = (1,2,3)/sqrt(14)`. Two distinct sectors pass the elastic G1 test and are
candidates for G2/G3 under the stated analytical closure assumptions:

| Sector | G1 | G2 | G3 | Long-wavelength speed |
|---|---|---|---|---:|
| `TA1` | derived | conditional | conditional | `4893.090 m/s` |
| `LA` | derived | conditional | conditional | `9156.820 m/s` |

They are distinct because their Christoffel eigenvalues and polarization
projectors differ. The speeds differ by a factor of approximately `1.871`.

Therefore, if the G2/G3 assumptions are independently established for both
branches,

```text
|Admissible_GMS| >= 2
```

in the specified, physically motivated silicon model. The stated GMS criteria
would not select a unique carrier sector and would not determine `c`.

This is a constructive elastic-mode counterexample conditional on G2/G3. It is
not yet a complete microscopic proof that both sectors satisfy GMS.

---

## 5. PRW Mapping for a Selected Branch

Fix any one admissible branch `b` and ray direction `n`. The branch-resolved
kinetic populations `f_b^+(s,t)` and `f_b^-(s,t)` propagate at the group speed

```text
v_b(n) = lim_(k -> 0) d omega_b(k n)/d|k|.
```

With a reciprocal branch-preserving reversal rate `gamma_b`, coarse-graining
over a narrow long-wavelength packet gives

```text
partial_t n_b^+ + v_b partial_s n_b^+ = -gamma_b n_b^+ + gamma_b n_b^-
partial_t n_b^- - v_b partial_s n_b^- = +gamma_b n_b^+ - gamma_b n_b^-.
```

Define

```text
s_b = n_b^+ + n_b^-
J_b = v_b (n_b^+ - n_b^-).
```

Then

```text
partial_t s_b + partial_s J_b = 0
partial_t J_b + v_b^2 partial_s s_b = -2 gamma_b J_b
partial_t^2 s_b + 2 gamma_b partial_t s_b = v_b^2 partial_s^2 s_b.
```

Thus the PRW speed is exactly the selected branch's long-wavelength velocity:

```text
c_eff = v_b(n),     tau_B = 1/(2 gamma_b),
xi_b = 2 v_b(n) tau_B.
```

This equality needs the following explicit assumptions: a narrow
long-wavelength packet, a single branch, group velocity approximately constant
over the packet, and branch-preserving reciprocal scattering. It does not hold
automatically for a mixture of branches. A mixture has multiple fluxes and
multiple characteristic speeds; reducing it to one PRW requires a further
closure or equilibration hypothesis.

---

## 6. Separate Bound Audit

Elasticity derives branch velocities. It does not derive a universal C2 speed
bound unless the carrier is first identified with an elastic branch.

For a selected branch, the mapping above gives the identity

```text
c_eff = v_b(n).
```

If an independent finite-signal postulate defines

```text
v_max = sup_(b,n) v_b(n),
```

then the elastic carrier assumption implies

```text
c_eff <= v_max.
```

The scalar notation `c <= v_s` is ambiguous in anisotropic silicon because
there is no single sound speed. In the sampled directions here,
`4673.916 <= v_b(n) <= 9356.246 m/s`; the maximum sampled value is the `[111]`
longitudinal speed. A global `v_max` requires maximization over all directions,
or an independently specified front-velocity model.

Verdict:

```text
c <= v_s is an independent C3-style constraint unless v_s is explicitly
defined as v_max and the carrier is assumed to be an elastic branch.
GMS alone neither derives the bound nor promotes it to equality.
```

---

## 7. Material Predictions Recomputed

The monatomic-chain estimate `a sqrt(K/m) ~= 6000 m/s` is not a complete silicon
dispersion relation. The branch-resolved prediction is instead

```text
xi_b(n) = 2 v_b(n) tau_B.
```

At `tau_B = 1 microsecond`, the sampled silicon sectors predict:

| Candidate speed | `xi_b` |
|---:|---:|
| `4673.916 m/s` | `9.348 mm` |
| `4893.090 m/s` (generic TA1) | `9.786 mm` |
| `5626.044 m/s` (generic TA2) | `11.252 mm` |
| `8433.023 m/s` (`[100]` LA) | `16.866 mm` |
| `9156.820 m/s` (generic LA) | `18.314 mm` |
| `9356.246 m/s` (`[111]` LA) | `18.712 mm` |

Hence even holding `tau_B` fixed, the physically justified model yields a range
of spatial predictions rather than one material-locked coherence length.

---

## 8. Final Result

```text
Elastic mode speeds: NOT UNIQUE.

Established outcome: two non-degenerate silicon acoustic sectors have unequal
long-wavelength speeds. Their use as PRW sectors remains conditional on a
branch-resolved kinetic reduction and a coarse-grained observable map.

Consequences:
  Existing C2 + Giga:              c remains free.
  + finite-speed postulate:        c <= v_max, conditionally.
  + current GMS:                   not fully tested from microscopic coupling.
```

To recover a unique `c`, the project needs an additional selection assumption,
such as a demonstrated scalar-density coupling that excludes transverse modes,
a longitudinal-only coupling theorem, a specified propagation geometry, or a
derived interbranch equilibration rule. Each would be new theory content and
must be audited independently.
