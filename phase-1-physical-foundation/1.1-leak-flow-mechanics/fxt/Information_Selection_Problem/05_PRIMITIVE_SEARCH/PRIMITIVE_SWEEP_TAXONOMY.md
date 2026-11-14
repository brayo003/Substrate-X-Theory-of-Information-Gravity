# PRIMITIVE_SWEEP_TAXONOMY
## Gate 5 Exhaustive Primitive Sweep — Taxonomy of Candidate Classes

**Status:** Gate 5 — Primitive generation phase
**Basis:** FINAL_GATE4_STATUS.md Branch C; DERIVATION_REQUIREMENTS.md
**Date:** August 2026

R1 (precise): There is no derivation, from independent premises, of why the gravitational degrees of freedom of the early universe occupied an extremely small region of their available initial-data phase space. The post-ekpyrotic residual is specifically: why was the pre-contraction state within the attractor basin (below the black-hole-formation Weyl threshold, with the scalar field in the required state)?

For each class the six taxonomy questions are answered:
1. What is the independently motivated mathematical object?
2. What known physics motivates it?
3. Can it act on general GR initial data?
4. Could it restrict Γ_GR without specifying the desired state?
5. Is there an existing literature mechanism?
6. Has the mechanism already been killed by the closure audit?

---

## Class A — Geometric Principles

**Mathematical object:** Curvature invariants, tensor concomitants, and covariant differential conditions on (M, g): e.g., conditions on the Weyl tensor C_{αβγδ}, the Bach tensor B_{μν} = ∇^α∇^β C_{αμβν} + ½ R^{αβ} C_{αμβν}, or the Cotton tensor in 3D. These are purely geometric objects with no physical inputs beyond the metric.
**Known physics motivation:** GR is a theory of geometry; every physical effect in GR is encoded in curvature. Curvature conditions appear in singularity theorems (Hawking-Penrose), in the positive mass theorem (Schoen-Yau), and in the definition of asymptotically flat spacetimes. They are the natural language for initial-data constraints.
**Acts on general GR initial data?** Yes — curvature conditions can be evaluated on any (h_{ij}, K_{ij}) satisfying the GR constraint equations without any background assumption.
**Could restrict Γ_GR without specifying the desired state?** Potentially yes, if the geometric condition is derived from an independent physical requirement (e.g., a stability or existence condition) rather than stated as "Weyl ≈ 0." A condition such as "existence of a globally smooth solution to the constraint equations satisfying a prescribed isoperimetric inequality" would restrict Γ_GR without explicitly naming the smooth state.
**Existing literature mechanism?** No single mechanism closes R1 through a derived geometric condition. The positive-energy theorem (Witten 1981) restricts GR initial data but does not select small-Weyl states. Geometric flow (Ricci flow, mean curvature flow) does not select cosmological initial states.
**Already killed?** No — not specifically examined in the closure audit. The audit killed boundary-condition proposals (Hartle-Hawking, Vilenkin) and holographic bounds, but not pure geometric restriction principles.

---

## Class B — Variational Principles

**Mathematical object:** An action functional S[g, φ, ...] on the space of field configurations, whose variation δS/δg^{μν} = 0 selects a subset of configurations. The Euler-Lagrange equations are the restriction; the relevant quantity for R1 is whether the action's saddle-point structure in the initial-data sector selects low-Weyl configurations.
**Known physics motivation:** Variational principles are the foundation of all of modern physics. The Einstein-Hilbert action, the Standard Model action, and their extensions all determine which field configurations are dynamically selected. Less-explored: actions that are extremized not just over spacetime histories but over the space of initial data.
**Acts on general GR initial data?** Yes, through the canonical formulation: the Arnowitt-Deser-Misner (ADM) action evaluated on a Cauchy surface defines a Hamiltonian structure on the space of initial data.
**Could restrict Γ_GR without specifying the desired state?** Yes, if a variational principle with an independently motivated action selects a low-dimensional submanifold of the initial-data phase space as its constraint surface. The question is whether any independently motivated action does this.
**Existing literature mechanism?** The no-boundary proposal is a path-integral variational principle — killed by the closure audit. Modified gravity actions (f(R), Gauss-Bonnet) have been studied but do not select cosmological initial states. The asymptotic safety program (Reuter-Saueressig) proposes a UV fixed-point action — not killed, not yet applied to initial-data selection.
**Already killed?** Partially — the specific no-boundary variational approach is killed. The broader class of variational principles is open.

---

## Class C — Hamiltonian/Phase-Space Constraints

**Mathematical object:** Constraints on the gravitational phase space Γ = {(h_{ij}, π^{ij})} arising from the canonical structure of GR. The GR Hamiltonian and diffeomorphism constraints H = 0, H_i = 0 already reduce the full phase space to the constraint surface. Additional constraints — derived from a new principle — would further restrict to a submanifold Γ_phys ⊊ Γ_{GR}.
**Known physics motivation:** The constraint structure of GR (Dirac's analysis) defines the reduced phase space. In loop quantum gravity, additional quantum constraints (spin-foam amplitude, physical inner product) further restrict which states are kinematically allowed. In shape dynamics, an additional conformal constraint restricts the GR phase space further. All of these are well-motivated from canonical quantization and relational mechanics.
**Acts on general GR initial data?** Yes — phase-space constraints are background-independent by construction in the canonical formulation.
**Could restrict Γ_GR without specifying the desired state?** Yes — an additional constraint derived from, e.g., a new symmetry principle or an independently derived consistency requirement would cut the phase space without encoding the desired state.
**Existing literature mechanism?** Shape dynamics (Barbour-Koslowski-Mercati) adds a conformal constraint — killed (wrong domain, Newtonian). LQG adds quantum constraints — no established derivation of low-Weyl initial states from them.
**Already killed?** Shape dynamics is killed. LQG-based constraints are not killed but have not been shown to select low-Weyl initial data.

---

## Class D — Symmetry Principles

**Mathematical object:** A symmetry group G acting on the space of initial data, where the G-invariant subspace has lower dimensionality than the full space. If G is independently motivated (e.g., as a gauge symmetry, a residual symmetry from a higher-dimensional theory, or a fundamental discrete symmetry), then restricting to the G-invariant sector is a non-circular restriction.
**Known physics motivation:** Symmetry reduction is ubiquitous: isometries of black hole solutions, conformal symmetry in CFT, CPT symmetry. Asymptotic symmetry groups (BMS group) constrain the behavior of spacetimes at infinity. Weyl invariance constrains conformal gravity theories. T-duality and U-duality in string theory relate geometries with ostensibly different curvature properties.
**Acts on general GR initial data?** Yes — if the symmetry group acts on the full space of initial data, the invariant subspace is a restriction on the general space.
**Could restrict Γ_GR without specifying the desired state?** Yes, IF the symmetry group is independently motivated and the G-invariant subspace coincides with low-Weyl states. The danger is defining G to be exactly the FLRW isometry group — this would encode the desired state. An independently motivated symmetry that happens to select low-Weyl states would be non-circular.
**Existing literature mechanism?** BMS symmetry restricts asymptotic states, not initial data. Conformal symmetry in conformal cyclic cosmology is killed (Penrose CCC). No existing mechanism uses a derived symmetry principle to select initial data.
**Already killed?** Not specifically — no pure symmetry-based restriction on initial data has been proposed and killed.

---

## Class E — Gauge Constraints

**Mathematical object:** Gauge conditions (diffeomorphism and local Lorentz gauge freedom in GR) reduce the space of field configurations by quotienting out physically equivalent configurations. Fixing a gauge is a choice; the gauge-invariant physical phase space is the relevant object. A mechanism in this class would derive that the gauge-invariant physical phase space is smaller than usually assumed.
**Known physics motivation:** The Gribov problem in non-Abelian gauge theories shows that naive gauge fixing is incomplete; there exist Gribov copies. In GR, the analogous problem (large diffeomorphisms) is not fully resolved. If the physical Hilbert space of quantum gravity is smaller than the kinematic space due to gauge constraints, that could restrict the physical initial states.
**Acts on general GR initial data?** Yes — gauge constraints are part of the structure of GR on any initial-data surface.
**Could restrict Γ_GR without specifying the desired state?** Possibly — if the physical (gauge-invariant) phase space has a non-trivial structure that excludes high-Weyl configurations. No known result of this type exists.
**Existing literature mechanism?** Not specifically applied to the cosmological initial state. The Gribov problem in gravity is studied but no connection to the initial state is established.
**Already killed?** No — not examined in the closure audit.

---

## Class F — Conservation Laws

**Mathematical object:** Conserved currents J^μ with ∂_μ J^μ = 0 (or covariant divergence ∇_μ J^μ = 0), derived from Noether's theorem applied to a symmetry of the action. In GR, the relevant conserved quantities are the ADM mass/momentum, angular momentum, and charge. Covariant conservation of the stress-energy tensor T^{μν} is not a restriction on initial data.
**Known physics motivation:** Conservation laws are the most robust constraints in physics. The positive mass theorem (Schoen-Yau, Witten) is effectively a conservation law result applied to GR initial data — it restricts the sign of the ADM mass. Are there other conservation law constraints on the full initial-data space that have not been identified?
**Acts on general GR initial data?** Yes — ADM energy and momentum are defined on any asymptotically flat GR initial-data surface.
**Could restrict Γ_GR without specifying the desired state?** The known conservation laws (ADM mass, momentum) do not select low-Weyl initial states. A new conservation law — motivated by a new symmetry — would be needed. This would require identifying a new symmetry of GR or its extension.
**Existing literature mechanism?** None that selects the cosmological initial state. Conservation of ADM energy is not a selection principle for Weyl curvature.
**Already killed?** No mechanism in this class has been proposed for R1.

---

## Class G — Quantum Principles

**Mathematical object:** Conditions derived from the quantum mechanical structure of the relevant system: unitarity, the uncertainty principle, the spectrum of a Hamiltonian, or the requirement that the classical limit be well-defined. In a quantum gravity context, the condition that a classical spacetime be a valid semi-classical limit of a quantum state is a restriction on which classical geometries are physically realizable.
**Known physics motivation:** The correspondence principle, the WKB approximation, and decoherence all provide conditions under which quantum states reduce to classical ones. In quantum cosmology, the requirement that a classical universe emerge from a quantum state is a restriction on the quantum state — and therefore on the classical geometry that emerges.
**Acts on general GR initial data?** In principle yes, but only after a theory of quantum gravity is specified. The restriction operates at the quantum-to-classical transition.
**Could restrict Γ_GR without specifying the desired state?** Yes, if the condition for a valid classical limit (e.g., the WKB condition being satisfied, or decoherence operating efficiently) independently selects a subset of classical geometries. But decoherence has been audited and killed for this purpose — it is a local process that does not select cosmological initial states.
**Existing literature mechanism?** Decoherence-based selection: killed (ASSUMPTION_FIREWALL). The no-boundary wave function: killed. Tunneling proposals: killed. The class is not dead — but specific mechanisms in it are.
**Already killed?** Specific mechanisms (no-boundary, Vilenkin, decoherence) are killed. The general class is open if a new quantum condition can be specified.

---

## Class H — Quantum-Information Structures

**Mathematical object:** Quantum information quantities — von Neumann entropy S(ρ) = -Tr(ρ log ρ), mutual information I(A:B) = S(A) + S(B) - S(AB), entanglement negativity, quantum discord, quantum channel capacity — applied to quantum states associated with cosmological configurations. A restriction would require that physically realizable states satisfy a specific quantum information condition.
**Known physics motivation:** The Ryu-Takayanagi formula connects entanglement entropy to geometric area in AdS/CFT. The ER=EPR conjecture connects entanglement to geometry. The Page curve and island formula for black holes establish quantum information principles relevant to spacetime. Quantum channel capacity of gravitational interactions has been studied (Danielson-Satishchandran-Wald 2022, 2023).
**Acts on general GR initial data?** Possibly — but quantum information conditions require a quantum state, not just a classical initial-data set. Extension to arbitrary GR initial data requires either a canonical quantization or a path-integral framework.
**Could restrict Γ_GR without specifying the desired state?** Potentially — a condition on the entanglement structure of the quantum state of geometry could select low-Weyl classical configurations as dominant semi-classical contributions. But the Zheng (2026) attempt in this class is killed: the emergence step is unproven.
**Existing literature mechanism?** Entanglement spacetime emergence (Van Raamsdonk, ER=EPR): killed (AdS-specific, kinematic). Zheng (2026): killed. Entanglement Past Hypothesis: killed (circular). The class is not exhausted.
**Already killed?** Specific mechanisms are killed; the general class is not.

---

## Class I — Entropic/Statistical Principles

**Mathematical object:** A measure μ on the space of initial data Γ_GR, and an entropy functional S[μ] or S[ρ] (for some probability distribution or quantum state ρ). A selection principle in this class would derive that the physically realized measure concentrates on a specific subregion of Γ_GR.
**Known physics motivation:** Statistical mechanics explains thermodynamic behavior from a uniform measure on phase space (Liouville measure). Jaynes's maximum entropy principle selects probability distributions given constraints. For cosmology, the question is whether an analogue of the microcanonical measure, applied to the space of cosmological initial data, concentrates on low-Weyl states.
**Acts on general GR initial data?** Yes — a measure can be defined on the full space of GR initial data, at least formally.
**Could restrict Γ_GR without specifying the desired state?** Yes, IF the measure can be derived from independent principles and IF the maximum-entropy (or dominant-measure) state is demonstrably the low-Weyl state rather than the high-Weyl state. But Penrose's argument suggests the opposite: the Liouville measure on Γ_GR gives vastly more weight to high-Weyl states. A mechanism in this class would need to invert this — using an independently derived measure that gives more weight to low-Weyl states.
**Existing literature mechanism?** Penrose's argument establishes that the standard Liouville measure gives overwhelming weight to high-Weyl states — this is precisely why R1 exists. Entropic gravity (Verlinde): killed (does not select initial states). No entropic/statistical mechanism closes R1.
**Already killed?** All audited entropic mechanisms are killed. The class is open to genuinely new measure proposals.

---

## Class J — Nonequilibrium Dynamical Principles

**Mathematical object:** Attractor structures in the dynamical system defined by GR evolution: stable fixed points, limit cycles, or strange attractors in the phase space of cosmological solutions. The ekpyrotic attractor is the primary example. A mechanism in this class would identify a dynamical attractor that, operating before or at the big bang epoch, drives trajectories toward the low-Weyl sector.
**Known physics motivation:** The ekpyrotic slow-contraction attractor (Ijjas-Steinhardt 2024) is numerically demonstrated in full GR. RG flow attractors in QFT (UV and IR fixed points) are independently established. Dynamical systems theory provides rigorous attractor theorems.
**Acts on general GR initial data?** Yes — attractor arguments apply to the full space of initial data, not just to FLRW perturbations. Ekpyrosis is demonstrated from non-perturbative initial conditions.
**Could restrict Γ_GR without specifying the desired state?** Yes — this is exactly how ekpyrosis works: the attractor is derived from the dynamics, not postulated. The restriction is to the basin of attraction, which is a derived subset of Γ_GR.
**Existing literature mechanism?** Ekpyrotic attractor: partially closes R1 but leaves the pre-contraction state unresolved. Other attractor mechanisms (inflation): do not work from non-perturbative initial conditions (demonstrated in 2404.00867). This class is the most advanced in the existing literature.
**Already killed?** Ekpyrosis is partially surviving. The class is the strongest existing mechanism class. Not killed.

---

## Class K — Causal Structures

**Mathematical object:** The causal structure of spacetime: the conformal structure (M, [g]), the causal past and future J^±(p), achronal sets, and the causal constraint that physical information cannot propagate outside the light cone. A mechanism in this class would derive that causally consistent initial data must lie in a restricted subset of Γ_GR.
**Known physics motivation:** Causality is a fundamental constraint on physical theories. Penrose's singularity theorem uses causal structure directly. The existence of a Cauchy surface is a causal requirement. Global hyperbolicity — required for a well-posed initial value problem in GR — is a causal condition.
**Acts on general GR initial data?** Yes — causal conditions are covariant and can be evaluated on any initial-data surface.
**Could restrict Γ_GR without specifying the desired state?** Possibly — the requirement of global hyperbolicity already restricts the space of initial data (some initial-data sets do not lead to globally hyperbolic spacetimes). A stronger causal condition might further restrict. Causal sets provide a discrete causal framework whose continuum limit may select specific geometric states.
**Existing literature mechanism?** Causal sets: audited and killed (no quantitative derivation of Weyl suppression). Global hyperbolicity conditions: standard GR, does not select low-Weyl states. Not fully exhausted.
**Already killed?** Causal sets killed. General causal structure conditions not specifically killed.

---

## Class L — Topological Structures

**Mathematical object:** Topological invariants of the 3-manifold (Σ, h_{ij}): the Euler characteristic χ, the first Betti number b_1, the Chern-Simons functional, the linking number of handles, or the Thurston geometric structure. A mechanism in this class would derive that physically realizable universes have a specific topology — or that the topology constrains the curvature.
**Known physics motivation:** 3-manifold topology (Thurston's geometrization theorem, proved by Perelman's Ricci flow) connects topology to geometry. In loop quantum gravity, spin-foam amplitudes are topological. In string theory, the topology of compactification manifolds determines low-energy physics. Topological quantum field theories (Witten 1988, Chern-Simons theory) are physically motivated.
**Acts on general GR initial data?** Yes — topological conditions on the Cauchy surface are well-defined and background-independent.
**Could restrict Γ_GR without specifying the desired state?** Possibly — but topology alone does not determine curvature. A flat 3-torus (T^3) can carry any smooth Riemannian metric. The topology → curvature connection via Thurston only works in specific dimensions and topological sectors. A highly inhomogeneous metric on a topologically simple manifold (S^3) is not excluded by topology.
**Existing literature mechanism?** Topological censorship theorems (Friedman-Schleich-Witt) restrict the topology of regions outside black holes but not the initial topology. Chern-Simons state in LQG is related to the vacuum state but connection to R1 is not established.
**Already killed?** No mechanism in this class has been specifically audited for R1.

---

## Class M — Algebraic/Category-Theoretic Structures

**Mathematical object:** Algebraic structures underlying the space of physical states: C*-algebras (algebraic QFT), operator algebras, von Neumann algebras with specific type classification (Type II₁, Type III₁), or category-theoretic structures (functors, natural transformations in the category of spacetimes). A mechanism in this class would derive that the algebraic structure of the physical theory restricts which states are in the physical Hilbert space.
**Known physics motivation:** Tomita-Takesaki modular theory (modular Hamiltonians, modular flow) establishes geometric content of algebraic QFT. Haag duality and the split property constrain the algebra of observables in QFT. Connes's noncommutative geometry provides an algebraic description of spacetime. The type classification of von Neumann algebras in QFT has physical implications (Witten 2021 on gravitational algebras being Type II).
**Acts on general GR initial data?** Indirectly — algebraic conditions constrain the Hilbert space of states, which corresponds to constraints on classical initial data in the semi-classical limit.
**Could restrict Γ_GR without specifying the desired state?** Possibly — if the algebraic structure of the physical Hilbert space in quantum gravity has a specific modular structure that corresponds (in the semi-classical limit) to low-Weyl geometries. Witten's (2021) observation that the gravitational algebra in de Sitter is Type II (rather than Type III as in ordinary QFT) may be relevant.
**Existing literature mechanism?** Algebraic QFT restrictions on cosmological initial states: not established. Witten's de Sitter gravitational algebra: not connected to R1. No mechanism in this class has been proposed for R1.
**Already killed?** No.

---

## Class N — Complexity/Computability Principles

**Mathematical object:** Computational complexity measures applied to physical states: Kolmogorov complexity K(x) (algorithmic information content), circuit complexity C(|ψ⟩) (minimal quantum circuit depth to prepare a state from a reference), or computational depth. A mechanism in this class would derive that physically realizable early-universe states must have low complexity by some computable measure.
**Known physics motivation:** Susskind's complexity-volume/action conjecture (2014-2016) relates circuit complexity of a boundary quantum state to the volume or action of the Einstein-Rosen bridge in the bulk. Wheeler-DeWitt complexity arguments connect quantum cosmological states to computational depth. Algorithmic probability (Solomonoff, Kolmogorov, Chaitin) assigns measure to programs.
**Acts on general GR initial data?** Kolmogorov complexity is not computable and not covariant. Circuit complexity requires a reference state and a gate set — these choices are arbitrary. Complexity is not a covariant physical quantity.
**Could restrict Γ_GR without specifying the desired state?** Complexity bounds do not give physical equations of motion. They are descriptions of states, not derivations of which states are physically realized. Killed in the prior audit: algorithmic/complexity approaches are non-falsifiable, not computable, and domain-restricted.
**Existing literature mechanism?** Algorithmic cosmology: killed (non-falsifiable, not physical derivation). Susskind complexity: applies to AdS black holes (wrong domain for R1). Constructor theory: not connected to R1.
**Already killed?** All audited complexity mechanisms are killed. The class is essentially exhausted.

---

## Class O — Renormalization/Coarse-Graining Principles

**Mathematical object:** The renormalization group (RG) flow on the space of theories or the space of states: a coarse-graining operation that maps microscale physics to macroscale effective physics. Fixed points of the RG flow are scale-invariant theories. UV fixed points (as in asymptotic safety) constrain the high-energy behavior of the theory and may restrict the physically realizable initial states to those consistent with UV completion.
**Known physics motivation:** The asymptotic safety program (Reuter 1998, Reuter-Saueressig 2019) proposes that quantum gravity has a non-Gaussian UV fixed point (the Reuter fixed point). If this is correct, the UV-complete theory of gravity selects specific renormalized coupling constants — and potentially specific initial states as the UV fixed point is approached. The multiscale entanglement renormalization ansatz (MERA) relates RG flow to holography. ERG (exact renormalization group) is a rigorous framework.
**Acts on general GR initial data?** Yes — the RG flow is defined on the theory space, which maps to the space of geometries in the semi-classical limit. The UV fixed point is background-independent in the asymptotic safety framework.
**Could restrict Γ_GR without specifying the desired state?** Possibly — if the UV fixed point of quantum gravity corresponds to a specific class of semi-classical geometries (near-Gaussian fluctuations around a smooth background), then requiring UV completion restricts the initial state. The Reuter fixed point has specific scaling dimensions that constrain the values of G and Λ at Planck scale — but connection to specific initial data geometry (small Weyl) is not established.
**Existing literature mechanism?** Asymptotic safety cosmology (Bonanno-Reuter): modifies the early universe through running coupling constants. Some running-G scenarios suppress structure formation at Planck scale — potentially relevant to Weyl suppression. Not killed; not fully developed for R1.
**Already killed?** MERA/tensor networks: killed (kinematic tools). Asymptotic safety: not killed, not fully assessed for R1.

---

## Class P — Holographic Principles

**Mathematical object:** Holographic bounds and dualities: the Bousso covariant entropy bound S(L) ≤ A(∂L)/4G on light sheets L, the holographic principle asserting that a (d+1)-dimensional bulk has a d-dimensional boundary description, or specifically AdS/CFT (Maldacena 1997) providing a bulk/boundary duality.
**Known physics motivation:** The Bekenstein-Hawking black hole entropy S = A/4G is the most robustly derived result connecting geometry and entropy. The Bousso bound is derived from black hole thermodynamics and the GSL. AdS/CFT is the most precisely established quantum gravity framework.
**Acts on general GR initial data?** The Bousso bound is covariant and applies to any spacetime satisfying the null energy condition. AdS/CFT is restricted to AdS geometries.
**Could restrict Γ_GR without specifying the desired state?** The Bousso bound, applied to the initial Cauchy surface, constrains total entropy but does not select smooth over inhomogeneous geometries — killed in CANDIDATE_KILL_TESTS.md as a standalone selection principle. AdS holographic approaches: wrong geometry for early cosmology.
**Existing literature mechanism?** McFadden-Skenderis holographic cosmology: shifts R1 to dual CFT state. Bousso bound applied to initial state: killed as standalone. All holographic approaches killed in the closure audit.
**Already killed?** Yes — all holographic approaches (AdS/CFT, McFadden-Skenderis, Bousso bound as standalone) are killed by the closure audit.

---

## Class Q — Emergent-Spacetime Mechanisms

**Mathematical object:** A pre-geometric structure (e.g., a quantum many-body system, a tensor network, a random matrix ensemble, a spin foam) from which classical spacetime geometry emerges as a coarse-grained description. A mechanism in this class would derive that the specific emergent classical geometry is low-Weyl because the pre-geometric degrees of freedom are in a specific state.
**Known physics motivation:** Van Raamsdonk (2010): spatial connectivity emerges from entanglement. Maldacena-Susskind ER=EPR conjecture. Tensor network / MERA models of holography (Swingle 2012). Random matrix models of quantum gravity. Group field theory (Oriti) proposes spacetime as a condensate of pre-geometric quanta.
**Acts on general GR initial data?** No — these approaches do not start from classical GR initial data; they derive spacetime from more primitive structures. The question of "acting on Γ_GR" is not well-posed in this class.
**Could restrict Γ_GR without specifying the desired state?** Only indirectly: if the pre-geometric state has a natural "ground state" or "vacuum" that corresponds to a smooth classical geometry, and this ground state is independently selected by the pre-geometric dynamics, then the emergent classical geometry is smooth. But this requires deriving both the pre-geometric dynamics and the identification of its ground state with the cosmological initial state — two unresolved steps.
**Existing literature mechanism?** Van Raamsdonk, ER=EPR, MERA, tensor networks: killed (AdS-specific, kinematic, wrong domain). Zheng (2026): killed (emergence step unproven). Group field theory cosmology: not yet connected to Weyl suppression quantitatively.
**Already killed?** All specific mechanisms killed. The class is open only if a genuinely new pre-geometric framework is identified.

---

## Class R — Quantum-Gravity Mechanisms

**Mathematical object:** Specific predictions from candidate theories of quantum gravity — loop quantum gravity (LQG), spin foams, causal dynamical triangulations (CDT), string theory — about the quantum state of the pre-big-bang universe. A mechanism in this class would use the quantum gravity theory to derive that the semi-classical initial state has low Weyl curvature.
**Known physics motivation:** All candidate quantum gravity theories predict modifications to GR at Planck scale. LQG predicts a quantum bounce (loop quantum cosmology — LQC). CDT simulations give de Sitter-like geometries in 4D. String theory predicts a landscape with many vacua. These are well-motivated frameworks.
**Acts on general GR initial data?** In the semi-classical limit, yes — LQC in particular makes claims about the quantum state at the bounce and the emerging classical state.
**Could restrict Γ_GR without specifying the desired state?** LQC claims the quantum bounce naturally produces a near-homogeneous post-bounce state — but this claim is made in a minisuperspace truncation. CDT simulations restrict to specific simplicial configurations. None of the full (non-minisuperspace) quantum gravity calculations produces a specific classical initial-data state.
**Existing literature mechanism?** LQC: bounce + Weyl suppression claimed but only in minisuperspace. CDT: de Sitter geometry emerges from statistical ensemble of simplicial geometries — potentially relevant but not demonstrated beyond the lattice. String landscape: selection problem worse than R1.
**Already killed?** Not fully — LQC and CDT are not in the primary closure audit but share the minisuperspace truncation problem with H-H and Vilenkin. Not specifically killed.

---

## Class S — Modified Initial-Data Measures

**Mathematical object:** A non-Liouville measure μ on the gravitational phase space Γ_GR that assigns greater probability to low-Weyl initial data than the standard Liouville measure. If such a measure can be derived from independent physical principles (not just postulated), it would constitute a selection mechanism.
**Known physics motivation:** In quantum statistical mechanics, the Gibbs measure is the physically correct measure at thermal equilibrium — it is not the Liouville measure but is derived from the canonical ensemble and the Hamiltonian. If gravity has an analogue of the Gibbs measure that weights states by some gravitational Hamiltonian, it could assign greater weight to low-energy (low-Weyl) states. The Hartle-Hawking wave function is formally a non-Liouville measure on the space of 3-geometries — but killed by assumption laundering.
**Acts on general GR initial data?** Yes — a measure is defined on the full phase space.
**Could restrict Γ_GR without specifying the desired state?** Yes — if the measure is derived from independent principles and its dominant contribution is demonstrably in the low-Weyl sector. The challenge is deriving the measure without encoding the desired answer in the derivation.
**Existing literature mechanism?** Hartle-Hawking: killed. DeWitt measure, Misner measure on superspace: not established as selecting low-Weyl states. This class is genuinely open to new approaches.
**Already killed?** Specific proposals (Hartle-Hawking) killed. The general class is open.

---

## Class T — Dynamical Attractor Mechanisms

**Mathematical object:** A stable attractor A ⊊ Γ_GR in the dynamical system defined by GR + matter evolution, such that trajectories from a wide basin of initial conditions converge to A. If A coincides with the low-Weyl sector, then any initial state in the basin is driven to the low-Weyl state. The basin must be large enough to be "generic" in some independently defined sense.
**Known physics motivation:** Ekpyrosis (Ijjas-Steinhardt 2024) is the leading example: the slow-contraction attractor is demonstrated from non-perturbative initial conditions in full GR. Inflationary attractors are claimed but disputed for non-perturbative initial conditions. RG fixed-point attractors in QFT are robust examples of the mechanism in a non-gravitational context.
**Acts on general GR initial data?** Yes — ekpyrosis acts on non-perturbative GR initial data (demonstrated numerically).
**Could restrict Γ_GR without specifying the desired state?** Yes — the attractor state is derived from the dynamics, not postulated. This is the class where ekpyrosis lives and it is the most advanced.
**Existing literature mechanism?** Ekpyrosis: PARTIAL SURVIVOR — shifts R1 to pre-contraction state. Inflation: killed as attractor mechanism (non-perturbative initial conditions not handled). RG attractors in gravity (asymptotic safety running): partially relevant. This class has active, live mechanisms.
**Already killed?** Ekpyrosis is not killed; it shifts R1. The class as a whole is not killed.

---

## Class U — Modified Gravitational Dynamics

**Mathematical object:** A modification to the Einstein field equations — f(R) gravity, Gauss-Bonnet gravity, Hořava-Lifshitz gravity, massive gravity, or a derivation of GR from a more primitive structure (Sakharov 1967 induced gravity, Jacobson 1995 thermodynamics of spacetime) — that changes the space of solutions and potentially restricts the physical initial states.
**Known physics motivation:** Higher-derivative gravity theories (arising as string corrections) modify GR at high curvature. Hořava-Lifshitz gravity modifies GR at high energies with better UV behavior. Jacobson's derivation of the Einstein equation from thermodynamics of local Rindler horizons provides an independent motivation for GR and suggests extensions.
**Acts on general GR initial data?** Modified gravity theories have their own initial-data problem, which may be more or less restrictive than GR's. Higher-derivative theories generically have more degrees of freedom (Ostrogradski instability) — their initial-data space is larger, not smaller.
**Could restrict Γ_GR without specifying the desired state?** Possibly — if a specific modified gravity theory has a restricted space of stable initial data (due to stability conditions that kill high-Weyl states). But known modified gravity theories do not restrict to low-Weyl initial data.
**Existing literature mechanism?** Modified gravity cosmology is extensively studied. None of the standard f(R), Gauss-Bonnet, Hořava-Lifshitz cosmologies specifically derives low-Weyl initial states. Not directly audited for R1.
**Already killed?** No specific modified gravity mechanism has been proposed and killed for R1 in this program.

---

## Class V — New Matter Sectors

**Mathematical object:** A new matter field or sector — a scalar field φ with specific potential, a gauge field, a higher-spin field, a topological field theory sector, a condensate — whose existence and dynamics restrict which gravitational initial states are physical. The ekpyrotic scalar field is the primary example of this class.
**Known physics motivation:** New matter fields are ubiquitous in beyond-Standard-Model physics: axions (motivated by the strong CP problem), moduli fields (string theory), dark energy scalar fields, inflaton. These fields have independent motivation from particle physics or string theory.
**Acts on general GR initial data?** A new matter field modifies the GR constraint equations and the space of initial data. The physical initial-data space is the set of (h_{ij}, K_{ij}, φ, π_φ) satisfying the modified constraint equations.
**Could restrict Γ_GR without specifying the desired state?** Yes — if the new matter field has dynamics that drive the system toward a specific attractor (as the ekpyrotic scalar does), and if the field's existence and potential are independently motivated. The restriction on the gravitational sector comes from the matter field's dynamics. The danger is that the matter field's potential is constructed specifically to produce the desired result.
**Existing literature mechanism?** Ekpyrotic scalar: PARTIAL SURVIVOR — shifts R1 to pre-contraction state. Inflation: killed as selection mechanism. Axion monodromy and other string-motivated fields: not specifically applied to R1.
**Already killed?** Ekpyrosis (Class V + Class T) is partially surviving. Other new matter fields not killed.

---

## Class W — Other Classes Discovered During Search

**Mathematical object:** Any class not captured by A–V. In the course of the search, candidate mechanisms may emerge from combinations of the above classes, from novel mathematical structures, or from physical considerations not anticipated in this taxonomy.
**Known physics motivation:** N/A at taxonomy stage — this class is a placeholder for genuine novelty.
**Acts on general GR initial data?** To be determined per candidate.
**Could restrict Γ_GR without specifying the desired state?** To be determined per candidate.
**Existing literature mechanism?** By definition, mechanisms in Class W are not covered by the existing literature in any of the A–V categories.
**Already killed?** No — cannot kill what has not yet been identified. Candidates entering Class W must pass the full kill test battery.

---

## Summary Assessment

| Class | Status | Action |
|---|---|---|
| A — Geometric | Open | Generate candidates |
| B — Variational | Partially killed (no-boundary); open otherwise | Generate candidates |
| C — Hamiltonian/phase-space | Partially killed (shape dynamics); open otherwise | Generate candidates |
| D — Symmetry | Open | Generate candidates |
| E — Gauge | Open | Generate candidates |
| F — Conservation laws | Open but thin | Generate if new symmetry found |
| G — Quantum | Partially killed (H-H, Vilenkin, decoherence); open for new quantum conditions | Generate candidates |
| H — Quantum-information | Partially killed (Van Raamsdonk, Zheng 2026, EPH); open | Generate candidates |
| I — Entropic/statistical | All audited mechanisms killed; open for new measure proposals | Generate candidates |
| J — Nonequilibrium dynamical | LIVE — ekpyrosis is partial survivor | Generate and extend candidates |
| K — Causal | Partially killed (causal sets); open | Generate candidates |
| L — Topological | Open | Generate candidates |
| M — Algebraic/category | Open | Generate candidates |
| N — Complexity/computability | KILLED — all mechanisms killed, class essentially exhausted | Do not generate new candidates |
| O — Renormalization/coarse-graining | Open (asymptotic safety not killed) | Generate candidates |
| P — Holographic | KILLED — all holographic mechanisms killed | Do not generate new candidates |
| Q — Emergent spacetime | All specific mechanisms killed; open only for new pre-geometric frameworks | Generate with extreme caution |
| R — Quantum gravity | Not killed; minisuperspace problem must be avoided | Generate candidates (non-minisuperspace only) |
| S — Modified initial-data measures | Partially killed; open | Generate candidates |
| T — Dynamical attractors | LIVE — ekpyrosis is partial survivor | Extend and generate |
| U — Modified gravitational dynamics | Open | Generate candidates |
| V — New matter sectors | LIVE — ekpyrotic scalar partially surviving | Extend and generate |
| W — Other | Open by definition | Generate if discovered |

**Classes producing the most promising candidates:** J (dynamical attractors), T (same), V (new matter sectors), O (asymptotic safety), R (quantum gravity, non-minisuperspace), A (geometric conditions), C (phase-space constraints), S (modified measures).

---

*Document status: COMPLETE — Taxonomy written; Candidate generation to proceed*
*Next document: CANDIDATE_REGISTER.md*
