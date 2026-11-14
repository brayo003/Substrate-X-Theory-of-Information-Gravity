# Microscopic C2 Current–Substrate Coupling: Derivation Attempt Audit

**Date:** 2026-10-10  
**Status:** COMPLETE — OUTCOME D  
**Executable validation:** `04_validations/microscopic_coupling_derivation.py`  
**Machine-readable output:** `04_validations/outputs/microscopic_coupling_derivation.json`  
**GAP-7 status:** NOT CLOSED — double obstruction precisely characterized  
**Prior audits preserved:** `C2_ELASTIC_COUPLING_AUDIT.md`, `GMS_ADVERSARIAL_AUDIT.md`

---

## 1. Executive Verdict

The existing SXC-IGC theory cannot derive a unique propagation speed `c` from its
current assumptions. This audit advances beyond the prior negative result by:

1. **Identifying four candidate elastic observables** as possible microscopic realizations
   of `J_C2`, deriving their explicit mode-coupling matrix elements, and testing all of them.

2. **Precisely locating the double obstruction** to closure:
   - Obstruction A: all four candidates couple to multiple acoustic branches at
     generic propagation directions in cubic silicon.
   - Obstruction B: even if branch selection were exact, the selected branch speed
     `v_LA(n)` varies by a factor of 1.109 across directions (8435–9355 m/s) because
     silicon is anisotropic.

3. **Isolating the minimal missing postulate** through an isotropic-limit calculation:
   in an isotropic elastic medium, scalar-dilatation coupling gives exactly zero
   transverse weight at every direction, and the longitudinal speed is direction-independent.
   The specific additional physics needed is therefore precisely stated: the substrate
   must behave as an isotropic elastic medium at the spatial scale relevant to the qubit.

4. **Characterizing the PRW kinetic reduction** as a conditional sequence of six steps,
   each requiring assumptions not present in the C2 axioms.

The result is not "c is still undetermined." It is: **the two-part obstruction is now
exactly characterized, the minimal closure postulate is identified, and its physical
content is made explicit.**

---

## 2. Equations Traced from the Existing Theory

### 2.1 PRW Transport (DERIVED from Goldstein-Kac process)

```
dn+/dt = -c dn+/dx - lambda n+ + lambda n-       [M1+]
dn-/dt = +c dn-/dx + lambda n+ - lambda n-       [M1-]
```

Adding: `ds/dt + dJ_C2/dx = 0` (continuity)  
Subtracting and eliminating J: `tau d²s/dt² + ds/dt = c² tau d²s/dx²`

Parameter identification: `tau = 1/(2 lambda)`, `c = v` (microscopic walker speed).  
Source: `02_derivations/microscopic_derivation.md` §1.3–1.5. Status: **DERIVED.**

### 2.2 C2 Current (DEFINED, not mapped to physical substrate)

```
J_C2 = c (n+ - n-)         [units: info/(m^2 s) in 1D]
```

`J_C2` is defined only within the PRW as the net directional flux of information
quanta. No existing document maps `J_C2` to a mechanical field `u(x,t)`,
`epsilon_ij(x,t)`, `p_i(x,t)`, or any elastic observable.
Source: `02_derivations/substrate_transport_derivation.md`. Status: **POSTULATED as PRW quantity; elastic map ABSENT.**

### 2.3 Interaction Hamiltonian (POSTULATED)

```
H_int = g J_C2(x_q, t) sigma_z
```

`sigma_z` is selected because it gives pure Ramsey dephasing without T1 relaxation
(shown by comparing cases A=sigma_z vs A=sigma_x,y in `interaction_hamiltonian_derivation.md`).
`g` has units `J m^2 s / info` by dimensional analysis. Neither `g` nor the map from
`J_C2` to a physical bath operator is derived.  
Source: `02_derivations/interaction_hamiltonian_derivation.md` §1–2. Status: **POSTULATED.**

### 2.4 Christoffel Eigenproblem (DERIVED from linear elasticity)

```
Gamma(n) e_b(n) = rho v_b(n)^2 e_b(n)
Gamma_ij(n) = C_ijkl n_k n_l
omega_b(k,n) = v_b(n) |k| + O(|k|^2 a^2)
```

For cubic silicon (C11, C12, C44), this gives three branches per direction: LA, TA1, TA2.
Source: standard elastic wave theory; numerically verified in `gms_adversarial_validation.py`.
Status: **DERIVED** from stated elastic model and material constants.

### 2.5 GAP-7 (CONFIRMED by prior 25-route re-derivation)

```
M1 = (v, lambda)   and   M1' = (alpha*v, lambda)   give identical Gamma_phi
```

for any `alpha > 0`. Therefore `c` is structurally free.
Source: `GAP7_REDERIVATION.md`. Status: **CONFIRMED ABSENT — 25 routes failed.**

---

## 3. Dependency Map and Assumption Ledger

| Item | Status | Source |
|------|--------|--------|
| PRW balance equations | **DERIVED** (Goldstein-Kac) | `microscopic_derivation.md` |
| Telegrapher equation from PRW | **DERIVED** (exact) | `microscopic_derivation.md` §1.5 |
| `J_C2 = c(n+ - n-)` | **DERIVED** within PRW | `substrate_transport_derivation.md` |
| `H_int = g J_C2 sigma_z` | **POSTULATED** | `interaction_hamiltonian_derivation.md` |
| `A = sigma_z` (not sigma_x/y) | **DERIVED** from dephasing requirement | `interaction_hamiltonian_derivation.md` §2 |
| `g` coupling constant value | **FREE PARAMETER** | `C2_FRONTIER_MAP.md` F10 |
| `J_C2` → elastic field map | **ABSENT** | This audit |
| Branch matrix elements `G_b(k,n)` | **ABSENT** | This audit |
| Branch PRW equations | **CONDITIONAL** (6 additional steps) | This audit §6 |
| Unique `c` from C2 axioms | **ABSENT** | `GAP7_REDERIVATION.md`, this audit |

---

## 4. Candidate Microscopic Mappings

Four physically motivated candidates were derived and tested. All are **new constitutive
assumptions** — none follows from existing C2 equations. The classification is explicit.

### 4.1 M0 — Existing C2 Coupling (baseline)

```
H_int = g J_C2(x_q, t) sigma_z
```

**Status:** No elastic map defined.  
**Branch matrix elements:** Undefined — cannot be calculated.  
**Unit obstruction:** `[J_C2] = info/(m^2 s)`. No elastic observable has these units
without introducing a conversion factor that carries units `[info/(mechanical unit)]`,
which is itself a new free parameter.  
**Unique speed:** No.

### 4.2 M1 — Scalar Dilatation

```
B(x,t) = -kappa rho div(u(x,t))     [new assumption]
H_int^(1) = g_1 B(x_q, t) sigma_z
```

For plane wave `u_b = e_b q_b exp(i(k n·x - omega_b t))`:

```
B_b = -i k kappa rho (n · e_b) q_b
|G_b|^2 ∝ (n · e_b)^2     [spectral weight w_b(n)]
```

**Derivation status:** New constitutive identification. Not from C2.  
**Physical basis:** Compression wave `div(u)` is the mechanical analogue of a scalar
density fluctuation — closest to the C2 information density `s`.  
**Dimensional check:** `kappa` must carry `[info s^3/m^2]` — new free parameter.  
**Numerical result at generic [123]:**

| Branch | Speed (m/s) | `w_b` |
|--------|------------|-------|
| TA1 | 4893.09 | 0.005316 |
| TA2 | 5626.04 | 0.001829 |
| LA  | 9156.82 | 0.992856 |

**Unique speed:** No. TA1 and TA2 have nonzero coupling because `n · e_TA != 0`
in anisotropic cubic silicon at generic directions (Zener ratio = 1.564).  
**High-symmetry exception:** At `[100]`, `[110]`, `[111]`, TA weights = 0 by symmetry.
This is geometry-specific, not a material-wide selection theorem.

### 4.3 M2 — Elastic Energy Flux (Poynting-like)

```
B(x,t) = n_i sigma_ij(x,t) du_j/dt     [new assumption]
```

For plane wave with `sigma_ij = C_ijkl (ik n_k e_l) q_b`:

```
B_b = -k^2 rho v_b^3 (n · e_b) q_b
|G_b|^2 ∝ (rho v_b^3)^2 (n · e_b)^2
```

**Derivation status:** New constitutive identification.  
**Key property:** Same angular factor `(n · e_b)^2` as M1, weighted by `v_b^6`.  
This gives stronger LA suppression of TA branches but does NOT eliminate them.  
**Numerical result at generic [123]:**

| Branch | Speed (m/s) | `w_b` |
|--------|------------|-------|
| TA1 | 4893.09 | 0.000125 |
| TA2 | 5626.04 | 0.000099 |
| LA  | 9156.82 | 0.999776 |

**Unique speed:** No. TA weights are smaller (~0.0002 total) but nonzero.
The mathematical obstruction is identical to M1.

### 4.4 M3 — Phonon Momentum Density

```
B(x,t) = rho n · (du/dt)     [new assumption]
```

For plane wave:

```
B_b = -i omega_b rho (n · e_b) q_b = -i k rho v_b (n · e_b) q_b
|G_b|^2 ∝ v_b^2 (n · e_b)^2
```

**Derivation status:** New constitutive identification.  
**Key property:** Same angular factor as M1, weighted by `v_b^2`.  
**Numerical result at generic [123]:**

| Branch | Speed (m/s) | `w_b` |
|--------|------------|-------|
| TA1 | 4893.09 | 0.001525 |
| TA2 | 5626.04 | 0.000694 |
| LA  | 9156.82 | 0.997781 |

**Unique speed:** No. Obstruction identical to M1.

### 4.5 M4 — Acoustic Intensity via Christoffel Contraction

```
B(x,t) = e_b^T Gamma(n) e_b = rho v_b^2     [new assumption]
```

For plane wave, the Christoffel eigenvalue contraction gives the acoustic
energy density. This is the same for all modes of the same branch
by definition. The branch coupling discriminates only by speed, not
polarization — **all three branches remain active at all directions.**

```
|G_b|^2 ∝ (rho v_b^3)^2     (no angular factor)
```

**Numerical result at generic [123]:**

| Branch | Speed (m/s) | `w_b` |
|--------|------------|-------|
| TA1 | 4893.09 | 0.0216 |
| TA2 | 5626.04 | 0.0499 |
| LA  | 9156.82 | 0.9284 |

**Unique speed:** No. This candidate cannot select any branch by polarization.

---

## 5. The Double Obstruction

### Obstruction A: Branch coupling is not unique at generic directions

For all candidates M1–M3 (the only ones with polarization sensitivity), the
coupling amplitude is proportional to `(n · e_b(n))`. For transverse branches,
this is zero in isotropic elasticity but nonzero in anisotropic cubic silicon
because the Christoffel eigenvectors deviate from pure transverse polarization.

**Quantitatively:** At generic direction `[1,2,3]/sqrt(14)`:
- `|n · e_TA1| = 0.0729`,  `|n · e_TA2| = 0.0428`
- These are 7.3% and 4.3% of the longitudinal projection `|n · e_LA| = 0.9964`
- They are nonzero because silicon's Zener anisotropy ratio = 1.564, deviation
  from isotropic of 56.4%.

**Mathematical statement of Obstruction A:**  
For cubic silicon with `C44 != (C11-C12)/2`, and for generic propagation direction `n`,
`n · e_TA(n) != 0`. Therefore `w_TA(n) = |n · e_TA(n)|^2 != 0`.
No candidate M1–M3 achieves exact branch decoupling at generic `n`.

### Obstruction B: LA speed is direction-dependent

Even if a hypothetical coupling perfectly selected the LA branch (`w_LA = 1`), the
resulting PRW speed would be `c = v_LA(n)`, which depends on `n`.

**Quantitatively:** Over 2000 random unit vectors, the LA speed ranges from
8435 m/s (near `[100]`) to 9355 m/s (near `[111]`), a ratio of **1.109**.
A unique `c` cannot follow from LA-branch selection alone unless:
- (i) the substrate is isotropic (making `v_LA` direction-independent), or
- (ii) propagation is restricted to one fixed direction, or  
- (iii) angular averaging over all directions produces a well-defined effective speed
  (this would require a separate derivation of the angular distribution of PRW rays).

---

## 6. Coherent-Mode to PRW Kinetic Reduction

Deriving PRW transport equations from Christoffel eigenmodes requires the
following six steps, each with explicit assumptions.

| Step | Physics | Status | New assumptions required |
|------|---------|--------|--------------------------|
| 1 | Christoffel eigenvalue → phase speed | **DERIVED** | linear elasticity, cubic symmetry |
| 2 | Phase speed → group speed (packet) | **DERIVED** (for long-wavelength packet) | narrow bandwidth, no O(k²) dispersion |
| 3 | Coherent mode → coarse-grained population | **ASSUMED** | coarse-graining length/time scales, incoherent-phonon approximation |
| 4 | 3D population → 1D PRW pair (n⁺, n⁻) | **ASSUMED** | fixed direction n OR angular average, no perpendicular coupling |
| 5 | Scattering reversal mechanism | **ASSUMED** | branch-preserving backscattering, Markovian approximation |
| 6 | PRW pair → telegrapher equation | **DERIVED** from PRW equations (exact) | prerequisite: steps 3–5 |

**New free parameters introduced:** scattering rate `gamma_b` per active branch,
coarse-graining scale, angular weighting if 3D→1D projection.

**Key point:** Step 6 is exact once steps 3–5 are granted. The telegrapher PRW
derivation is rigorous. The problem is entirely upstream: steps 3–5 introduce
assumptions not in C2, and step 4's angular-averaging problem re-introduces
the direction-dependence of Obstruction B.

---

## 7. Isotropic Limit: The Closure-Revealing Calculation

To isolate the minimum missing physics, the calculation was repeated in the
isotropic elastic limit where `C44_iso = (C11-C12)/2 = 50.9 GPa` (replacing
silicon's actual `C44 = 79.6 GPa`).

**Result:** At generic direction `[1,2,3]/sqrt(14)`:
- Isotropic TA weights: `|n · e_TA| ~ 5e-17` (machine-zero, exactly zero)
- Isotropic LA weight: `w_LA = 1.000000` (exact)
- Isotropic LA speed: `sqrt((C11 + 2*C12 + 4*C44_iso)/(3*rho)) = 8433 m/s` (same in all directions)

**Conclusion from the isotropic limit calculation:**  
In an isotropic elastic substrate, M1 (scalar dilatation) gives:
- Exact transverse decoupling at every direction (Obstruction A is removed)
- A direction-independent LA speed (Obstruction B is removed)
- A unique PRW speed `c = v_LA_iso = 8433 m/s`

This identifies the minimum missing postulate precisely: **the substrate must
behave as an isotropic elastic medium at the relevant spatial scale.**

This postulate is not derivable from the existing C2 axioms. It is a new
physical identification — a constitutive relation between the abstract C2
substrate and the mechanical properties of the chip material.

---

## 8. Multi-Branch Bath Correlator Structure

When multiple branches contribute with weights `w_b`, the bath spectral density
is a sum of branch-specific Lorentzians:

```
S_BB(omega) = sum_b w_b * (2 S_0 tau_b) / (1 + omega^2 tau_b^2)
```

This has multiple poles and multiple relaxation times. The spatial correlator becomes:

```
C_Gamma(r) = sum_b w_b * K_0(r / xi_b) / K_0(a / xi_b)
```

with `xi_b = 2 v_b(n) tau_b`, a multi-scale function not reducible to a single `K_0`.

**Observable consequence:** Fitting a single `K_0` to data from a multi-branch bath
extracts an effective `xi` that is a weighted geometric mean of branch `xi_b` values.
The ratio `c = xi / (2 tau)` extracted this way is not directly `v_LA` or any single
branch speed. It conflates branch weights, speeds, and scattering rates.

**This is the precise statement of why multi-branch coupling does not advance GAP-7:**
The P3 ratio `c = xi_c / (2 tau_B)` remains measurable from data but is not
theoretically predicted — it is now not predicted to equal any single branch speed either.

---

## 9. Closure Classification

**Outcome D:** A specific missing physical postulate would close the system, but that
postulate is not derivable from the current framework.

**Evidence for D over C:**
- All four candidates are well-defined physically and dimensionally consistent (up to
  a conversion-factor free parameter, which all require in the same way).
- All four produce the same qualitative failure: multi-branch coupling at generic
  cubic directions.
- The isotropic limit calculation identifies a single specific additional axiom that
  eliminates both obstructions simultaneously.
- This is not a choice among multiple possible closures — there is one natural closure
  (isotropic elastic substrate) that removes both obstructions with one postulate.

**Evidence against E (inconsistency):**  
All weight normalizations sum to 1.000000 ± 1e-8 (verified across 12 direction-candidate
pairs). No internal contradiction was found. The multi-branch coupling is physically
sensible — it just does not close the theory.

**Evidence against A (existing theory closes it):**  
The existing C2 coupling has no elastic map at all (M0). The four candidates M1–M4
are all new assumptions. None is derivable from `H_int = g J_C2 sigma_z`.

**Evidence against B (coupling determined, multiple speeds follow):**  
The existing coupling does not determine any elastic mapping; B requires at minimum
that the coupling is determined, which it is not.

---

## 10. What This Task Establishes and What It Does Not

### Established by this task:

1. The existing C2 current `J_C2` has no microscopic map to any elastic observable.
   This was asserted in prior audits; this audit provides the formal reason:
   unit incompatibility, polarity mismatch, and missing information ontology.

2. Four specific candidate mappings were derived and their mode-coupling matrix
   elements were computed explicitly. None produces a unique speed at generic
   cubic silicon directions.

3. The obstruction is **double**: (A) multi-branch coupling from anisotropy,
   (B) direction-dependent LA speed. Branch selection solves A but not B.

4. The minimum closure postulate is **isotropic elastic substrate**. This is
   a single well-defined addition. It would remove both obstructions simultaneously.

5. The kinetic reduction from Christoffel eigenmodes to PRW equations requires
   six explicit steps. Four of those steps introduce new physics not in C2.
   The derivation is conditional, not exact.

6. Numerical evidence: Zener anisotropy ratio = 1.564. Silicon deviates from
   isotropic by 56.4%. TA polarization projections at generic `[1,2,3]`:
   `|n · e_TA1| = 0.0729`, `|n · e_TA2| = 0.0428`. LA speed range: 1.109×.

### Not established by this task:

1. Whether the silicon substrate seen by a superconducting qubit effectively behaves
   as isotropic at the relevant phonon wavelengths. This is an empirical question
   requiring knowledge of the relevant phonon wavelengths and the isotropy of the
   actual chip geometry.

2. Whether any of the four candidate mappings is physically preferred. M1–M3
   all have the same angular structure; M4 does not. Physical preference requires
   a microscopic Hamiltonian of the qubit-substrate interaction, which does not
   exist in the current framework.

3. Whether the multi-branch bath correlator can be reduced to a single scale through
   some effective-medium argument. Such an argument would need to be derived, not assumed.

---

## 11. GAP-7 Status Update

**Previous status (2026-08-22):** NOT CLOSED. `c` is structurally free. All 25 derivation
routes failed. The substrate speed cannot be determined from existing C2 axioms.

**Current status (2026-10-10):** NOT CLOSED. The double obstruction (branch coupling
anisotropy + direction-dependent speed) is now precisely characterized. The minimum
missing postulate (isotropic elastic substrate or equivalent) is explicitly identified.

**What has advanced:** The obstruction is no longer just "c is undetermined." It is:
"The substrate must be described as isotropic elastic at the relevant scale, and
J_C2 must be identified with the scalar dilatation field with a specific conversion
factor. Given those two additions, M1 would select the LA branch at every direction
and give a unique c = v_LA_iso. Those additions are not derivable from C2."

**No change to T2 classification.** The theory remains structurally underdetermined.

---

## 12. Minimum Additional Physics Required for Progress

Ordered by logical necessity:

1. **A microscopic Hamiltonian** of the qubit-phonon interaction derived from
   the CCA axioms. This would fix the form of the bath operator (which candidate
   M applies), the projection direction, and the conversion factor. Without this,
   the choice among M1–M4 is arbitrary.

2. **An isotropy/geometry specification** for the substrate. Either:
   (a) Justify that the relevant phonon wavelengths see an effectively isotropic
       medium (e.g., at GHz frequencies in amorphous substrate layers), or
   (b) Fix a single propagation direction `n` and restrict the theory to that geometry,
       or (c) Derive the angular distribution of PRW rays and compute the effective speed.

3. **A kinetic reduction mechanism**: Specify the phonon backscattering process
   responsible for the PRW reversal rate `gamma`. This sets `tau_B` and closes
   the theory's remaining free parameter.

---

## 13. Next Single Most Valuable Research Task

**Determine the effective elastic isotropy of the substrate at the phonon frequency
relevant to qubit dephasing.**

The relevant phonon wavelength for dephasing is `lambda_ph ~ v_s / Gamma_phi`.
For `v_s ~ 9000 m/s` and `Gamma_phi ~ 1 kHz` (typical superconducting qubit),
`lambda_ph ~ 9 mm`. At this scale, the crystalline anisotropy of the silicon
wafer (macroscopic grain structure) may effectively average to an isotropic medium.
If it does, Obstruction A is removed by physical argument, and the isotropic
closure M1 becomes defensible without being ad hoc.

This is an empirical and order-of-magnitude question, not a pure theory question.
It could be addressed by measuring the angular dependence of qubit coherence
times in devices with different crystal orientations relative to the chip layout.

---

## 14. Reproducible Commands

```bash
# Run the microscopic coupling derivation
cd phase-1-physical-foundation/1.1-leak-flow-mechanics/fxt
python 04_validations/microscopic_coupling_derivation.py

# Run the existing scalar-dilatation coupling audit (for cross-check)
python 04_validations/coupling_mode_audit.py

# Run the GMS adversarial validation (elastic speed uniqueness)
python 04_validations/gms_adversarial_validation.py
```

Expected output files:
- `04_validations/outputs/microscopic_coupling_derivation.json`
- `04_validations/outputs/coupling_mode_audit.json`
- `04_validations/outputs/gms_adversarial_validation.json`

All three scripts complete without errors and produce machine-readable JSON.

---

*Audit completed 2026-10-10. Does not revise or overwrite prior audits.*  
*Prior audits: `C2_ELASTIC_COUPLING_AUDIT.md` (M1 scalar-dilatation only, generic direction),*  
*`GMS_ADVERSARIAL_AUDIT.md` (elastic speed non-uniqueness), `THEORY_CLOSURE_AUDIT.md` (T2 state).*
