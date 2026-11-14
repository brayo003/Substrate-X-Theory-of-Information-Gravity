# 05_ADVERSARIAL_TESTS
## Adversarial Initial-Data Tests for New Mechanism Classes

**Date:** August 2026

Testing NC-1 through NC-5 against the seven adversarial initial-data classes. Detailed derivations in 04_NEW_CLASS_REGISTER.md.

---

## NC-1 — Constraint-Propagation Closure (Cotton-York)

| Data class | Admitted? | Reason |
|------------|-----------|--------|
| FLRW (C=0) | YES | Cotton-York = 0 automatically (conformally flat) |
| Bianchi I / Kasner | YES | K_ij diagonal, constant → ∇_k K^j_l = 0 → Y^{ij} = 0 |
| Bianchi IX | YES | Homogeneous, Cotton-York evaluates to zero for diagonal K |
| Large-Weyl inhomogeneous | UNKNOWN | Depends on specific configuration |
| Gravitational waves | UNKNOWN | GW data has non-diagonal K; may have Y ≠ 0 |
| Schwarzschild slice | YES | Time-symmetric slice K_ij = 0 → Y = 0 |
| Multi-BH | YES | Same as Schwarzschild |

**Adversarial test result: FAILS for Kasner.** The proposed constraint is automatically satisfied by all vacuum Kasner initial data. Cannot distinguish FLRW from Kasner.

**Underlying reason:** Kasner is conformally flat in 3D (spatial slices) and has diagonal, spatially uniform extrinsic curvature. Any constraint built from the Cotton-York tensor or the 3D Cotton tensor vanishes on Kasner by these symmetries.

**Structural observation:** This is the 3D version of the same problem that killed P01: Kasner's special symmetry properties (Ricci-flatness in 4D, conformal flatness in 3D, uniform K_ij) make it satisfy many natural constraints automatically. A constraint that excludes Kasner must target the Weyl curvature explicitly or target a property that Kasner lacks — but the only property Kasner specifically lacks relative to FLRW is C ≠ 0, and targeting C directly is assumption laundering.

---

## NC-2 — Quantum Extension Completeness

| Data class | Admitted? | Reason |
|------------|-----------|--------|
| FLRW | YES | LQC extends FLRW through bounce |
| Kasner | YES | LQC bounces Kasner; post-bounce state is Kasner-like |
| Bianchi IX | UNKNOWN | Bianchi IX bounce in LQC not fully established |
| Large-Weyl vacuum | UNKNOWN | Full quantum gravity extension unknown |
| Schwarzschild | UNKNOWN | Full quantum extension unknown |
| Multi-BH | UNKNOWN | Full quantum extension unknown |

**Adversarial test result: FAILS for Kasner.** Kasner admits a quantum extension in LQC. The post-bounce state is also Kasner-like. NC-2 does not exclude Kasner.

---

## NC-3 — Relational Consistency

All adversarial classes have finite relational observables. Kasner shape observables p₁:p₂:p₃ are finite. **KILLED.**

---

## NC-4 — Conformal Completion Existence

**KILLED by firewall** (encodes Weyl=0). Not tested adversarially.

---

## NC-5 — Global Hamiltonian Flow

FLRW is excluded (big bang singularity). Kasner is excluded. **Both excluded equally — no discrimination between low-Weyl and high-Weyl cosmological initial data.** KILLED.

---

## Key Pattern Across All New Classes

The Kasner metric continues to pass or trivially satisfy every natural constraint because of its specific mathematical properties:
1. Ricci-flat (R_{μν} = 0)
2. Conformally flat spatial slices
3. Uniform diagonal extrinsic curvature
4. Finite relational observables
5. Admits quantum extensions in LQC

Any mechanism targeting these properties either targets ALL vacuum data (not selective) or targets FLRW and Kasner equally (not discriminating). A mechanism that specifically targets C ≠ 0 encodes the conclusion.

This is the Kasner resistance pattern: Kasner is the minimal adversarial example that survives every constraint not encoding low Weyl explicitly.

---

*Document status: ADVERSARIAL TESTS COMPLETE*
*All new classes fail on Kasner (NC-1, NC-2) or are killed before reaching adversarial test (NC-3, NC-4, NC-5).*
*Date: August 2026*
