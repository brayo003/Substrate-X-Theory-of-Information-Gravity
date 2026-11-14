# 03_LITERATURE_SEARCH
## Adversarial Literature Search: What Do Frameworks Actually Do to Initial-Data Space?

**Date:** August 2026

For each framework: WHAT MATHEMATICAL OPERATION DOES IT ACTUALLY PERFORM ON THE SPACE OF INITIAL DATA?

---

## Asymptotic Safety (covered in Gate 6)

Operation: Weights path-integral measure via exp(−β∫C²√g).
Effect on Γ_GR: O(1) weighting of Kasner; no restriction.
Verdict: Killed.

---

## Loop Quantum Gravity / LQC

Operation: Quantizes the GR constraint algebra; physical Hilbert space = kernel of quantum constraints.
Effect on Γ_GR: In minisuperspace (LQC), all Bianchi models have physical Hilbert spaces. In full theory, the physical Hilbert space corresponds semiclassically to all of Γ_GR.
Relevant papers: Thiemann (2007) "Modern Canonical Quantum General Relativity"; Ashtekar-Singh (2011) Class.Quant.Grav. 28, 213001.
**What it does to initial-data space: Nothing.** The physical Hilbert space contains semiclassical states corresponding to all of Γ_GR.

---

## Spin Foams / EPRL Model

Operation: Sums over spin-foam amplitudes; stationary-phase approximation selects GR saddle points.
Effect on Γ_GR: All GR solutions are saddle points (killed, P08).
Relevant papers: Engle-Pereira-Rovelli-Livine (2008); Perez (2013) Living Rev.Rel. 16:3.
**What it does to initial-data space: Selects GR solutions. Does not restrict within GR solutions.**

---

## Causal Set Theory

Operation: Discretizes the causal order. Physical spacetimes are those corresponding to Lorentzian manifolds from which causal sets can be obtained by sprinkling.
Effect on Γ_GR: Every Lorentzian manifold (including Kasner) admits a sprinkling. No restriction on initial data.
Relevant papers: Bombelli et al. (1987) Phys.Rev.Lett. 59, 521; Surya (2019) Living Rev.Rel. 22:5.
**What it does to initial-data space: Nothing for continuous Lorentzian manifolds.**

One possible restriction: the causal set dynamics (CSG model, Benincasa-Dowker 2010) has a specific action. The path integral over causal sets might weight certain causal structures more than others. But: this has been studied only in 2D (CTSL model). Extension to 4D initial-data selection is not established.

---

## Causal Dynamical Triangulations (CDT)

Operation: Sums over causal simplicial complexes with fixed topology.
Effect on Γ_GR: In phase C, produces de Sitter-like ground state. But topology is fixed (S³) — killed (P09, failure class F).
Relevant papers: Ambjørn-Jurkiewicz-Loll (2004) Phys.Rev.Lett. 93, 131301.
**What it does to initial-data space: Within fixed S³ topology, weights toward de Sitter. No general restriction.**

---

## Group Field Theory (GFT) Condensate Cosmology

Operation: The universe is a condensate of GFT quanta. The condensate state satisfies a mean-field equation that reduces to Friedmann equations in specific limits.
Effect on Γ_GR: The condensate state is a specific quantum state of the GFT field. The Friedmann equations follow from the mean-field approximation of this state. The initial state of the condensate is a free parameter of the theory — the GFT equation of motion produces FLRW as a consequence of the condensate ansatz, but the condensate state itself is not derived.
Relevant papers: Oriti et al. (2016) Phys.Rev.Lett. 116, 211301; Gielen-Sindoni (2016) SIGMA 12, 082.
**What it does to initial-data space: Produces FLRW dynamics from a condensate state — but the condensate state is assumed (failure class C).**

---

## Twistor Theory

Operation: Reformulates GR and QFT in terms of complex null geodesic congruences (twistors). Penrose transform: left-handed and right-handed gravitons encoded in different twistor objects.
Effect on Γ_GR: Twistor theory does not restrict which spacetimes are physical — it reformulates GR in new variables. The Weyl tensor decomposes into Ψ_{ABCD} (anti-self-dual, left-handed) and Ψ̄_{Ȧ'Ḃ'Ċ'Ḋ'} (self-dual, right-handed) in spinor notation.
Possible R1 connection: Penrose's original Weyl curvature hypothesis was motivated by twistor theory — the initial singularity has Ψ_{ABCD} = 0 (only one helicity). This is a restriction on the twistor structure. But this IS the Penrose Weyl curvature hypothesis, which encodes the conclusion directly (failure class I).
Relevant papers: Penrose (1967) J.Math.Phys. 8, 345; Penrose-Rindler (1984) "Spinors and Space-Time" vol. 2.
**What it does to initial-data space: Reformulates it in spinor/twistor variables. No new restriction follows without imposing Ψ = 0 as an input.**

---

## Shape Dynamics

Operation: ADM gravity reformulated with a new gauge invariance (conformal invariance of the 3-metric). The conformal constraint added to GR.
Effect on Γ_GR: Shape dynamics is classically equivalent to GR in many settings. The conformal constraint identifies conformally equivalent initial data configurations as physically equivalent — it reduces the physical degrees of freedom but does not exclude high-Weyl configurations.
Relevant papers: Barbour et al. (2013) Phys.Rev.Lett. 111, 241301; Gomes-Gryb-Koslowski (2011) Class.Quant.Grav. 28, 045005.
**What it does to initial-data space: Quotients by conformal transformations. Does not select low-Weyl over high-Weyl — conformally related metrics include high-Weyl representatives.**

---

## Penrose Conformal Cyclic Cosmology

Operation: Maps the final conformal geometry of one aeon to the initial geometry of the next. Killed in Gate 4 (infinite regression + observationally unsupported).
**What it does to initial-data space: Relocates the initial data question to the previous aeon. Killed.**

---

## Global Analysis / Topological Results

Relevant results:
- Positive mass theorem (Schoen-Yau 1979; Witten 1981): the ADM mass of an asymptotically flat initial-data set with matter satisfying DEC is non-negative. This restricts the space of physical initial data to M_ADM ≥ 0. Does not restrict Weyl curvature.
- Geroch topological censorship (Chrusciel-Galloway 1994): killed (P20, failure class G).
- Gromov-Lawson positive scalar curvature theorems: restrict which 3-manifolds admit metrics with positive Ricci scalar. Kasner slice has zero Ricci scalar (vacuum) — not restricted.

**What global analysis does to initial-data space: Restricts some geometric properties (ADM mass sign, topology in specific settings) but not Weyl curvature.**

---

## Mathematical Relativity — Initial Value Formulation

The standard result: Choquet-Bruhat (1952) proves local existence and uniqueness for the Cauchy problem. The conformal method (York 1973, Isenberg 1995) shows that free initial data is (conformal class of 3-metric, transverse-traceless extrinsic curvature). Given free data, the Lichnerowicz equation determines the conformal factor.

**New structural observation:** In Isenberg's classification (1995), the Lichnerowicz equation has a positive solution if and only if the Yamabe class of the conformal metric is positive or zero, with specific conditions on the extrinsic curvature. The Yamabe class is a conformal invariant.

Kasner vacuum: the spatial slice is conformally flat (the 3-metric is conformally equivalent to flat R³ under appropriate scaling). The Yamabe class of flat R³ is positive. So Kasner does have a positive Lichnerowicz solution — it is in Γ_GR.

For closed manifolds with large Weyl curvature: if the conformal class has negative Yamabe number AND the extrinsic curvature is too small, the Lichnerowicz equation may not have a positive solution. This would exclude some closed high-Weyl configurations from Γ_GR even in the classical theory.

**This is a genuine restriction on Γ_GR from functional analysis — but it applies to closed manifolds with negative Yamabe class, not to the cosmologically relevant Kasner/Bianchi class (which has positive Yamabe class).**

---

## Singularity Theorems and Extensions

The Hawking-Penrose theorems give conditions for geodesic incompleteness. The Borde-Guth-Vilenkin theorem (2003) shows that any past-eternal inflating region must have been geodesically incomplete in the past. These are existence results for singularities, not selection principles for initial data.

**Converse direction:** If we require that the initial state can be "prepared" (in some sense) from a well-defined earlier state, what constraints does this place on (h,K)? This requires specifying what "earlier state" means — which is precisely the infinite regression problem that motivated R1.

---

## Noncommutative Geometry (Connes)

Operation: Replaces the smooth manifold with a spectral triple (A, H, D). The smooth manifold is recovered when A is commutative. The spectral action S[D] = Tr f(D²/Λ²) derives Standard Model + GR equations.
Effect on Γ_GR: The spectral action produces equations of motion (EOM), not initial data. As established (P16, failure class L), it selects EOMs, not solutions.
**What it does to initial-data space: Nothing. The spectral action selects which theory is physical (GR + SM), not which solution of that theory is realized.**

---

## Penrose Weyl Curvature Hypothesis in Conformal Geometry

The Weyl curvature hypothesis: Ψ_{ABCD} = 0 at the initial singularity. This is a boundary condition on the conformal structure of the initial singularity, not a derived result.

Todd (2003) and Conformal Cyclic Cosmology argue that the conformal structure at the initial singularity is smooth (Weyl = 0) because of specific properties of conformal rescaling at t=0. However, this requires: (a) a specific conformal completion of the spacetime, (b) specific properties of the singularity that are assumed rather than derived.

**What it does to initial-data space: Imposes Ψ = 0 as a condition on the conformal structure. This IS the conclusion, not a derivation of it.**

---

## Summary: What No Framework Does

After surveying the literature, no existing framework performs the following operation on Γ_GR:

**Derives Γ_phys ⊊ Γ_GR by a mathematical condition that (a) is independently motivated, (b) does not encode low Weyl, (c) specifically excludes Kasner/Bianchi I/Bianchi IX vacuum initial data, (d) does not require importing a quantum state.**

The closest existing result is the Lichnerowicz / Yamabe constraint, which excludes some high-Weyl closed manifolds — but not the relevant Kasner/Bianchi class.

The gap is not simply "no one has tried." Multiple sophisticated frameworks have been developed for quantum gravity and mathematical relativity. The gap reflects a structural feature: the space of vacuum Ricci-flat solutions is large, and no known mathematical property distinguishes the low-Weyl sector of this space without using low Weyl as an input.

---

*Document status: LITERATURE SEARCH COMPLETE*
*No framework performs the required operation on Γ_GR.*
*Closest result: Yamabe/Lichnerowicz constraint (excludes some high-Weyl closed manifolds but not Kasner).*
*Date: August 2026*
