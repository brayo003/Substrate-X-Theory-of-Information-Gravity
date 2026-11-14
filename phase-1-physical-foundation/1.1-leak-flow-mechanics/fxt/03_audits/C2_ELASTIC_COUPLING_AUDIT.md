# C2_ELASTIC_COUPLING_AUDIT.md
## Does the Existing C2 Coupling Select a Silicon Acoustic Branch?

**Date:** 2026-10-10
**Status:** COMPLETE -- NO BRANCH SELECTION DERIVED
**Executable check:** `04_validations/coupling_mode_audit.py`
**Result:** `NO_UNIQUE_C_FROM_EXISTING_COUPLING`

---

## 1. Scope Correction to the GMS Audit

`gms_adversarial_validation.py` diagonalizes the cubic-silicon Christoffel
matrix. It establishes that distinct gapless acoustic eigenmodes have unequal
long-wavelength velocities. It does not establish:

1. a microscopic coarse-graining criterion for GMS distinguishability;
2. a minimal-support kinetic closure; or
3. reciprocal right/left PRW reversals.

Those are not consequences of a Christoffel eigenvalue calculation. The former
GMS result is therefore an elastic speed non-uniqueness result, with a
conditional PRW mapping, not a complete microscopic GMS validation.

The present audit asks the stronger and physically relevant question: can the
already stated C2 substrate-to-qubit coupling select a branch without adding a
branch-selection rule?

---

## 2. Existing Coupling: What Is and Is Not Defined

The existing interaction derivation states

```text
H_int = g J_C2(x_q,t) sigma_z.
```

Here `J_C2` is the C2 information current. In the one-dimensional PRW it is

```text
J_C2 = c (n^+ - n^-),
partial_t s + partial_x J_C2 = 0.
```

The coupling derivation explicitly treats `J_C2` as a real classical substrate
field. It does not define a map from silicon displacement `u`, strain
`epsilon_ij`, momentum density, elastic energy current, or any Christoffel
eigenmode to `J_C2`.

Therefore the branch matrix element

```text
G_b(k,n) = < J_C2 | e_b(k,n) >
```

is undefined in the existing theory. The values `G_LA`, `G_TA1`, and `G_TA2`
are not constrained by `H_int` alone. In particular, neither exact transverse
decoupling nor longitudinal selection follows from current C2 assumptions.

There is a second dimensional issue: in three dimensions `J_C2` is a vector
flux, while `H_int` contains a scalar bath operator. A sensor direction or
another scalar contraction, for example `a dot J_C2`, is also not specified.

**Existing-coupling verdict:** no branch is selected; the requested calculation
cannot start until a microscopic constitutive map for `J_C2` is supplied.

---

## 3. Conditional Scalar-Density Completion

To test the most favorable plausible selection mechanism without presenting it
as existing C2 content, introduce the new constitutive identification

```text
B(x,t) = kappa delta_rho(x,t) = -kappa rho div(u(x,t)),
H_int^rho = g_rho B(x_q,t) sigma_z.
```

This is a new assumption. It replaces the abstract C2 current bath operator by
a scalar elastic-density observable. It is not derived from `H_int = g J_C2
sigma_z`.

For a Christoffel plane wave

```text
u_b(x,t) = e_b(n) q_b exp(i(k n dot x - omega_b t)),
```

the matrix element is

```text
B_b proportional to -i k kappa rho [n dot e_b(n)] q_b,
w_b(n) = |n dot e_b(n)|^2.
```

Thus an exact transverse decoupling would require `n dot e_T(n) = 0` for every
allowed direction. That identity holds in isotropic elasticity and on some
high-symmetry crystal directions, but it does not hold generally for anisotropic
cubic silicon.

---

## 4. Cubic-Silicon Test

Using the same room-temperature elastic constants as the GMS audit:

| Constant | Value |
|---|---:|
| `C11` | `165.7 GPa` |
| `C12` | `63.9 GPa` |
| `C44` | `79.6 GPa` |
| `rho` | `2330 kg/m^3` |

For the generic direction `n = (1,2,3)/sqrt(14)`, the executable calculation
gives:

| Branch | Speed (m/s) | Scalar-density weight `w_b` |
|---|---:|---:|
| `TA1` | 4893.090 | 0.00531579 |
| `TA2` | 5626.044 | 0.00182850 |
| `LA` | 9156.820 | 0.99285570 |

The longitudinal branch dominates, but neither transverse weight is zero. The
conditional scalar-density completion therefore produces three coupled
long-wavelength velocities at a generic direction.

On the sampled `[100]`, `[110]`, and `[111]` directions, transverse weights
vanish by symmetry in this model. That is a geometry-specific decoupling, not a
material-wide theorem. A C2 prediction cannot select one universal speed by
silently restricting the experiment to those directions.

---

## 5. Consequences for Transport

The elastic equation is

```text
rho partial_t^2 u_i = C_ijkl partial_j partial_l u_k.
```

Projecting onto a branch gives

```text
partial_t^2 q_b + omega_b(k,n)^2 q_b = 0,
omega_b(k,n) = v_b(n)|k| + O(k^2).
```

This is a wave equation for a coherent normal mode. It is not a PRW equation.
To obtain branch-resolved PRW populations requires the additional kinetic
assumptions: narrow packets, coarse-grained populations `n_b^+`, `n_b^-`, and
reciprocal branch-preserving scattering at rate `gamma_b`. Only then does one
obtain

```text
partial_t n_b^+ + v_b partial_s n_b^+ = -gamma_b(n_b^+ - n_b^-)
partial_t n_b^- - v_b partial_s n_b^- = +gamma_b(n_b^+ - n_b^-)
```

and hence

```text
partial_t^2 s_b + 2 gamma_b partial_t s_b = v_b(n)^2 partial_s^2 s_b.
```

For the scalar-density observable, the bath correlator has the branch sum

```text
C_BB(t) = sum_b integral d^3k |G_b(k,n)|^2 C_b(k,t),
|G_b|^2 proportional to k^2 w_b(n).
```

At generic direction all three terms are present. The observable therefore has
multiple characteristic velocities and, generally, multiple scattering times.
It does not close to a one-speed telegrapher equation without another reduction
such as exact transverse decoupling, spectral filtering, or fast interbranch
equilibration. Each of those is additional physics to be derived or assumed.

---

## 6. Relationship to a C2 Density-to-Flux Map

Suppose one additionally identifies C2 density with elastic compression,
`s = -kappa rho div(u)`. The C2 continuity equation fixes only the longitudinal
divergence of a flux:

```text
partial_t s + div(J_C2) = 0.
```

It does not uniquely determine `J_C2`: any solenoidal vector may be added. The
choice of an irrotational, local `J_C2` is another constitutive assumption. With
that choice, the scalar flux channel has the same `n dot e_b` weights above and
thus still has generic transverse leakage in cubic silicon.

Consequently, even the strongest natural scalar completion does not provide a
universal unique speed in the anisotropic material model.

---

## 7. Assumption Ledger and Verdict

| Claim | Status |
|---|---|
| Silicon has distinct LA/TA Christoffel eigenmodes | derived from elastic model |
| Existing `H_int = g J_C2 sigma_z` gives elastic mode matrix elements | absent |
| Transverse modes exactly decouple under existing C2 coupling | not derived |
| Scalar-density coupling weights are `|n dot e_b|^2` | derived conditional on `B = -kappa rho div(u)` |
| Generic cubic-silicon scalar coupling contains TA1, TA2, LA | derived in that conditional model |
| Branch PRW equations | conditional kinetic reduction |
| A unique C2 `c` follows | no |

```text
Success criterion: a unique c must follow from an existing coupling and dynamics.

Result: FAILED.
The existing C2 current coupling has no microscopic silicon map. The tested
scalar-density completion is new physics and yields multiple coupled branches
at generic direction. No branch-selection theorem, and no unique c, follows.
```

The next legitimate advance is not a branch rule. It is an explicit microscopic
derivation of the C2 current operator and its qubit matrix element, followed by
the same projection calculation. Until then the coupling cannot close GAP-7.

