# CANDIDATE_REGISTER
## Gate 5 Exhaustive Primitive Sweep — Candidate Mechanisms

**Status:** Generation only — no candidate declared successful at this stage.
**Date:** August 2026

All candidates are named by mathematical properties only. No candidate inherits prohibited terminology. Each must pass 6 kill tests and 7 adversarial initial-data tests in subsequent documents.

---

## P01 — Asymptotic-Safety UV Fixed-Point Restriction

**ID:** P01
**Name:** UV-fixed-point gravitational-coupling restriction
**Mathematical definition:** In the asymptotic safety program (Reuter 1998), the gravitational renormalization group flow on theory space T = {G(k), Λ(k), ...} has a non-Gaussian UV fixed point G* at cutoff scale k → ∞. The physical requirement is that the trajectory G(k) → G* as k → ∞. This imposes a constraint: the initial-data configuration must be consistent with being approached from the UV fixed point along a renormalized trajectory. Formally, the physical phase space is Γ_phys = {x ∈ Γ_GR | x lies on a renormalized trajectory emanating from the UV fixed point G*}. The critical exponents at G* (typically two relevant directions) restrict the effective dimensionality of Γ_phys.
**Independent motivation:** Asymptotic safety is independently motivated by the need for UV completion of quantum gravity without string theory. The fixed point existence is supported by truncated functional RG calculations in 4D (Reuter-Saueressig 2019, Living Reviews). It applies to all gravitational systems, not only cosmology.
**Relevant literature:** Reuter (1998) Phys.Rev.D 57:971; Reuter-Saueressig (2019) Living Rev.Rel. 22:1; Bonanno-Reuter (2002) Phys.Rev.D 65:043508; Platania (2020) Universe 6:159.
**Physical domain:** Quantum gravity / Planck-scale regime; applies to all gravitational systems.
**Expected action on Γ_GR:** Restricts Γ_GR to the finite-dimensional critical surface (UV critical manifold). The number of free parameters equals the number of relevant couplings at G* (typically 2-3). This is a radical reduction from the infinite-dimensional Γ_GR.
**Potential R1 mechanism:** If the UV critical manifold preferentially contains low-Weyl initial data — because high-Weyl configurations require irrelevant couplings that are suppressed at G* — then Γ_phys from asymptotic safety would automatically restrict to the low-Weyl sector.
**Known objections:** (1) UV fixed point existence is proven only in truncations of theory space — full non-perturbative proof is lacking. (2) The critical surface is defined in theory space (coupling constants), not in initial-data space (h_ij, K_ij) — the map from the former to the latter is not established. (3) Asymptotic safety cosmology has been studied but no derivation of Weyl suppression specifically exists. (4) Whether the UV critical manifold selects low-Weyl states is not known.

---

## P02 — Gravitational Thermodynamic Stability Bound

**ID:** P02
**Name:** Local-Rindler-horizon thermodynamic constraint
**Mathematical definition:** Jacobson (1995) derived the Einstein equation from the thermodynamic identity δQ = T dS applied to local Rindler horizons, with S = A/4G (Bekenstein-Hawking) and T = ℏa/2π (Unruh temperature). This derivation assumes the Clausius relation holds for all local causal horizons. The constraint: for any local Rindler horizon in spacetime, the entropy flux through the horizon satisfies δS/δA ≤ 1/4G. A mechanism in this class would demand that this thermodynamic consistency condition hold everywhere, at all times including the initial slice, and derive that it restricts the allowed initial curvature.
**Independent motivation:** Jacobson's result establishes a deep connection between spacetime thermodynamics and the Einstein equation. The Unruh effect (Fulling-Davies-Unruh) is an independent QFT result. The generalized second law (GSL) is supported by multiple lines of evidence.
**Relevant literature:** Jacobson (1995) Phys.Rev.Lett. 75:1260; Padmanabhan (2010) Rep.Prog.Phys. 73:046901; Verlinde (2011) JHEP 04:029; Wall (2012) Phys.Rev.D 85:104049.
**Physical domain:** Any spacetime with local Rindler horizons — applies universally in GR.
**Expected action on Γ_GR:** The thermodynamic consistency condition applied to the initial slice requires that the entropy flux through any local horizon be bounded by A/4G. For high-Weyl initial data, local caustics and focusing of null geodesics may violate this bound.
**Potential R1 mechanism:** High-Weyl initial data produces rapid focusing of null geodesics (Raychaudhuri equation: θ̇ = -θ²/2 - σ_{ab}σ^{ab} - R_{ab}l^al^b). If the Weyl tensor is large, the expansion θ of a null congruence goes negative quickly, producing a caustic. At a caustic, the thermodynamic entropy accounting breaks down. Requiring everywhere-valid thermodynamic consistency may exclude initial data with large Weyl tensor.
**Known objections:** (1) Jacobson's derivation applies to local patches, not global cosmological evolution — extending it to initial-data selection requires work. (2) The Raychaudhuri argument applies inside trapped surfaces but not generically. (3) This is a thermodynamic bound, not a dynamical selection principle — it may only exclude the most extreme configurations, not restrict to the observed state.

---

## P03 — Causal-Diamond Quantum-Capacity Bound

**ID:** P03
**Name:** Causal-diamond quantum-channel capacity restriction
**Mathematical definition:** For a causal diamond D(p,q) = J^+(p) ∩ J^-(q) in a spacetime with metric g, the quantum channel capacity C(D) is bounded by the area of the maximal cross-section: C(D) ≤ A_max(D)/4G (from holographic entropy bounds). Define a capacity functional on the initial-data surface: C[h_{ij}, K_{ij}] = inf_{D containing Σ} C(D). The constraint is C[h_{ij}, K_{ij}] ≥ C_min for physical realizability. Alternatively, the channel capacity must exceed the number of degrees of freedom being processed, yielding an upper bound on the information content of the initial data.
**Independent motivation:** Danielson-Satishchandran-Wald (2022, 2023) establish that the gravitational interaction functions as a quantum channel with a capacity determined by the geometry. This is independently motivated by quantum information theory and does not require cosmological inputs.
**Relevant literature:** Danielson-Satishchandran-Wald (2022) Phys.Rev.D 105:086001; (2023) Int.J.Mod.Phys.D 32:2342007; Bousso (2002) Rev.Mod.Phys. 74:825.
**Physical domain:** Any spacetime with a well-defined causal structure.
**Expected action on Γ_GR:** The capacity bound restricts the information content that can propagate through causal diamonds. High-Weyl initial data has smaller causal diamonds (rapid focusing) and thus lower capacity — imposing a capacity requirement may exclude high-Weyl states.
**Potential R1 mechanism:** If the early universe must have supported sufficient quantum channel capacity for decoherence and classical structure formation to proceed (a requirement from consistency with the observed universe), high-Weyl initial states with micro-causal diamonds cannot satisfy this capacity requirement.
**Known objections:** (1) This mixes a capacity requirement with the desired output — circular if "sufficient capacity for classical structure" encodes "low Weyl." (2) The Danielson-Satishchandran-Wald result is for specific interaction settings, not cosmological geometry. (3) Connecting channel capacity to the initial-data Weyl tensor requires a calculation not yet done.

---

## P04 — Weyl-Tensor Stability Under Forward Evolution

**ID:** P04
**Name:** Lyapunov-stability restriction on initial data
**Mathematical definition:** For GR initial data (h_{ij}, K_{ij}), define the linearized stability operator L[h,K]: it maps perturbations δ(h_{ij}, K_{ij}) to their rate of change under GR evolution. The Lyapunov exponent λ_max[h,K] = sup{λ : ||δ(t)|| ~ e^{λt}} measures the exponential growth rate of perturbations. Define Γ_stable = {(h_{ij}, K_{ij}) ∈ Γ_GR | λ_max[h,K] < λ_c} for some critical value λ_c. Physical realizability requires stability: Γ_phys ⊆ Γ_stable.
**Independent motivation:** Stability is a standard physical requirement: unstable configurations cannot be prepared or maintained. In dynamical systems, Lyapunov stability is the standard measure. BKL (Belinski-Khalatnikov-Lifshitz) oscillations show that highly anisotropic, high-Weyl initial data near a singularity exhibit chaotic (Lyapunov-unstable) behavior.
**Relevant literature:** BKL (1970) Adv.Phys. 19:525; Misner (1969) Phys.Rev.Lett. 22:1071; Barrow (1982) Phys.Rep. 85:1; Uggla et al. (2003) Phys.Rev.D 68:103502.
**Physical domain:** GR cosmology, particularly near-singularity regime.
**Expected action on Γ_GR:** BKL analysis shows that highly anisotropic Bianchi IX initial data exhibits chaotic mixmaster oscillations — high Lyapunov exponents. FLRW-like initial data is stable or has zero Lyapunov exponents. Stability restriction Γ_stable may substantially reduce Γ_GR.
**Potential R1 mechanism:** The requirement that the pre-big-bang state be Lyapunov-stable (non-chaotic) may restrict to the subset of initial data that does not exhibit BKL oscillations — which is precisely the low-Weyl, near-homogeneous sector. The BKL attractor is chaotic for high-Weyl data; the ekpyrotic attractor suppresses the chaos. Stability requirement may select ekpyrotic-compatible initial data.
**Known objections:** (1) Lyapunov stability is a mathematical property of solutions, not a physical selection principle — why should unstable initial data be excluded? (2) The restriction to stable initial data requires justification from a higher principle. (3) BKL oscillations are a feature of evolution near singularities, not necessarily of the initial data itself.

---

## P05 — Quantum-Gravitational Decoherence Functional Selection

**ID:** P05
**Name:** Consistent-histories decoherence-functional restriction
**Mathematical definition:** In the consistent histories (decoherent histories) formulation (Griffiths 1984, Gell-Mann-Hartle 1990), a set of histories {C_α} is consistent if the decoherence functional D(C_α, C_β) = Tr(C_α ρ_0 C_β†) ≈ 0 for α ≠ β, where ρ_0 is the initial quantum state. Physical histories are those belonging to a consistent set. The selection principle: only histories for which a consistent-set decomposition exists (i.e., the decoherence functional approximately vanishes off-diagonal) are physically realizable. Formally, Γ_phys = {x ∈ Γ_GR | ∃ consistent set S such that x belongs to a history in S and D(x, y) ≈ 0 ∀y ≠ x in S}.
**Independent motivation:** Consistent histories is an independently motivated interpretation of quantum mechanics that does not require a preferred observer. The decoherence functional is well-defined for any quantum system. Gell-Mann-Hartle applied it to quantum cosmology, deriving that classical spacetime is a quasiclassical realm.
**Relevant literature:** Griffiths (1984) J.Stat.Phys. 36:219; Gell-Mann-Hartle (1990) in "Complexity, Entropy and the Physics of Information"; Halliwell (1993) Phys.Rev.D 48:4785; Hartle-Srednicki (2007) Phys.Rev.D 75:123523.
**Physical domain:** Quantum cosmology — any quantum system with a large number of degrees of freedom.
**Expected action on Γ_GR:** Quasiclassical realms require suppressed off-diagonal elements of the decoherence functional. This requires that the initial quantum state ρ_0 have specific properties. If ρ_0 is fixed by independent principles, the classical histories that decohere form a restricted set.
**Potential R1 mechanism:** If the quasiclassical realm that decoheres from a generic quantum state of geometry is preferentially the low-Weyl sector — because high-Weyl configurations have rapidly oscillating quantum amplitudes that prevent decoherence — then the consistent-histories framework would select low-Weyl classical spacetimes.
**Known objections:** (1) This requires specifying ρ_0 — the initial quantum state of the universe — which is part of the problem. (2) Decoherence has been killed as a selection mechanism (ASSUMPTION_FIREWALL §C) — it is a local process. The consistent-histories application is different but shares the problem of requiring a prior quantum state. (3) The quasiclassical realm is not unique: many consistent sets exist.

---

## P06 — Gravitational Constraint Algebra Anomaly Cancellation

**ID:** P06
**Name:** Constraint-algebra anomaly-freedom restriction
**Mathematical definition:** The GR constraint algebra {H[N], H[M]} = H[N^μ∂_μM - M^μ∂_μN] + (Kij terms), {H_i[N^i], H[M]} = H[£_N M], {H_i[N^i], H_j[M^j]} = H_i[£_N M^i] is a first-class constraint algebra with structure functions (not structure constants). Quantization of this algebra is anomalous in general — the quantum commutator [Ĥ[N], Ĥ[M]] may not equal the quantum version of the right-hand side. Anomaly cancellation requires specific restrictions on the quantum state. Formally, the physical Hilbert space H_phys = ker(Ĥ[N]) ∩ ker(Ĥ_i[N^i]) is the space of states annihilated by all constraints without anomaly.
**Independent motivation:** Anomaly cancellation is a fundamental requirement in gauge theories — anomalous gauge theories are inconsistent. In string theory, anomaly cancellation in the Virasoro algebra (critical dimension D=26 or D=10 for superstrings) selects the spacetime dimension. The gravitational constraint algebra anomaly is an independent, well-defined mathematical object.
**Relevant literature:** Dirac (1958) Proc.Roy.Soc. A246:333; Thiemann (2007) "Modern Canonical QGR"; Fleischhack-Lewandowski (2006) Comm.Math.Phys. 269:687; Bojowald (2012) Ann.Phys. 524:895 (anomaly-free LQC).
**Physical domain:** Canonical quantum gravity — any quantization of GR.
**Expected action on Γ_GR:** Anomaly-free quantization of the constraint algebra restricts the physical Hilbert space. In the semi-classical limit, this corresponds to a restriction on classical initial data. If anomaly cancellation requires specific geometric configurations, Γ_phys is a subset of Γ_GR.
**Potential R1 mechanism:** In LQC and other quantizations of GR, anomaly-free representations of the constraint algebra have been studied. If the anomaly-free sector corresponds preferentially to low-Weyl initial data — because large Weyl curvature generates anomalous contributions to the quantum constraint algebra — then anomaly cancellation restricts to the low-Weyl sector.
**Known objections:** (1) Anomaly cancellation in quantum gravity is not established in the full non-minisuperspace theory. (2) The connection between anomaly cancellation and geometric properties of initial data is not worked out. (3) This approach requires quantum gravity inputs that are not yet available.

---

## P07 — Conformal Factor Decoupling at Spatial Infinity

**ID:** P07
**Name:** Asymptotic-flatness conformal-class restriction
**Mathematical definition:** For asymptotically flat initial data (h_{ij}, K_{ij}), the conformal structure at spatial infinity i^0 is characterized by the Geroch tensor hierarchy (mass multipoles). Asymptotically flat initial data decomposes as h_{ij} = (1 + 2φ/r)δ_{ij} + O(r^{-2}) near i^0. The BMS group acts on the space of such data. A mechanism in this class: require that the initial data be compatible with a specific BMS supertranslation vacuum — i.e., the Bondi mass aspect m(u, θ, φ) satisfies a specific constraint derived from soft graviton theorems. Define Γ_BMS = {(h_{ij}, K_{ij}) | m(u,θ,φ) = m_0 (const) on I^+}, i.e., initial data whose future is BMS-vacuum-compatible.
**Independent motivation:** Soft graviton theorems (Weinberg 1965, Strominger 2014) relate BMS symmetry to conservation laws. The celestial holography program (Strominger et al.) establishes BMS as a fundamental symmetry. Asymptotic symmetry groups are independently motivated from the S-matrix perspective.
**Relevant literature:** Strominger (2014) JHEP 07:152; Bondi-van der Burg-Metzner (1962) Proc.Roy.Soc. A269:21; Sachs (1962) Phys.Rev. 128:2851; Compère-Long (2016) JHEP 07:137.
**Physical domain:** Asymptotically flat spacetimes; gravitational scattering problems.
**Expected action on Γ_GR:** BMS-vacuum compatibility restricts initial data to configurations whose gravitational radiation emission is consistent with the BMS vacuum structure. Highly inhomogeneous initial data produces large mass multipoles and nontrivial BMS memory — potentially incompatible with BMS-vacuum restriction.
**Potential R1 mechanism:** If BMS vacuum state is independently selected as the initial state by a soft-graviton / memory effect argument, then initial data with large Weyl tensor (which generates large BMS memory) is excluded. This is background-independent and applies to general GR initial data.
**Known objections:** (1) BMS symmetry applies to asymptotically flat spacetimes — the early universe is not asymptotically flat (it is closed or de Sitter-like). Extension to cosmological settings is not established. (2) BMS-vacuum restriction is a condition on asymptotic behavior, not on bulk initial data. (3) This is likely a restriction on the asymptotic structure rather than the bulk Weyl curvature.

---

## P08 — Spin-Foam Amplitude Suppression of High-Curvature Data

**ID:** P08
**Name:** Spin-foam vertex-amplitude curvature suppression
**Mathematical definition:** In the EPRL/FK spin-foam model (Engle-Pereira-Rovelli-Livine 2008), the transition amplitude between spin-network states |s⟩ and |s'⟩ is W(s, s') = ∑_σ ∏_v A_v(σ) ∏_f A_f(σ) where σ sums over spin-foam configurations, A_v is the vertex amplitude, and A_f is the face amplitude. The vertex amplitude is A_v = ∫ dg_e ∏_f e^{iγ·area_f·θ_f} where θ_f is the dihedral angle (curvature) associated to face f, and γ is the Immirzi parameter. For large curvature (large θ_f), the vertex amplitude oscillates rapidly and its modulus is suppressed by the stationary-phase approximation. Define Γ_phys^{SF} = {classical geometries that are dominant saddle points of the spin-foam path integral}.
**Independent motivation:** Loop quantum gravity / spin foams is an independently motivated quantum gravity program. The EPRL model is derived from first-principle discretization of the Palatini action. The large-j asymptotics (Conrady-Freidel 2008, Barrett et al. 2010) recover Regge calculus, independently supporting the model.
**Relevant literature:** Engle-Pereira-Rovelli-Livine (2008) Phys.Rev.Lett. 99:161301; Barrett et al. (2010) J.Math.Phys. 51:122501; Conrady-Freidel (2008) Phys.Rev.D 78:104023; Perez (2013) Living Rev.Rel. 16:3.
**Physical domain:** Planck-scale quantum gravity / LQG.
**Expected action on Γ_GR:** The stationary phase of the spin-foam path integral selects flat or slowly-varying curvature geometries (Regge curvature small). High-curvature configurations have rapidly oscillating phases and are suppressed in the large-j limit. This is a quantitative, derived suppression mechanism.
**Potential R1 mechanism:** If the spin-foam amplitude suppresses high-Weyl initial data at the quantum gravity scale, the semi-classical limit automatically produces low-Weyl configurations as the dominant classical histories. This would be a derivation of Weyl suppression from the quantum gravity amplitude — not assumed.
**Known objections:** (1) All spin-foam calculations are in discrete simplicial geometries — the continuum limit is not established. (2) The large-j approximation assumes large spins (semiclassical limit) but the early-universe state may be in the Planck regime where this approximation fails. (3) The Immirzi parameter γ is a free parameter — a suppression result that depends on γ is underdetermined.

---

## P09 — Causal Dynamical Triangulation Phase-Structure Selection

**ID:** P09
**Name:** CDT de-Sitter-phase dominance mechanism
**Mathematical definition:** In causal dynamical triangulations (CDT), the path integral over spacetime geometries is approximated as Z = ∑_T e^{-S_{Regge}[T]} where the sum is over causal simplicial complexes T with fixed causal structure, and S_{Regge}[T] = -κ_0 N_0 + κ_4 N_4 + Δ(N_{4,1} - 6N_{1,4}) where N_i are simplex counts and κ_0, κ_4, Δ are coupling constants. In 4D CDT (Ambjørn-Jurkiewicz-Loll), numerical simulations show a phase structure with four phases (A, B, C, C_b). In phase C, the ground state of the quantum geometry is a de Sitter-like universe — compact, smooth, with suppressed spatial fluctuations at large scales.
**Independent motivation:** CDT is independently motivated as a path integral over geometries that respects causal structure (unlike Euclidean dynamical triangulations). The emergence of de Sitter geometry in phase C from a purely combinatorial input (simplex counts and coupling constants) is a non-trivial result.
**Relevant literature:** Ambjørn-Jurkiewicz-Loll (2004) Phys.Rev.Lett. 93:131301; (2005) Phys.Rev.D 72:064014; Ambjørn et al. (2012) Phys.Rev.D 85:124044; Loll (2019) Class.Quant.Grav. 37:013002.
**Physical domain:** Planck-scale quantum geometry / non-perturbative quantum gravity.
**Expected action on Γ_GR:** In the phase-C region of CDT parameter space, the dominant configurations in the path integral are smooth, compact, de Sitter-like geometries with suppressed large-scale fluctuations. High-curvature, inhomogeneous configurations are not dominant saddle points.
**Potential R1 mechanism:** If the CDT phase structure can be extended beyond the lattice approximation and connected to the continuum GR initial-data problem, the phase-C dominance of smooth geometries provides a derivation of Weyl suppression from the statistical weight of geometries in the quantum gravity path integral. The smoothness emerges from the combinatorics, not from an assumed boundary condition.
**Known objections:** (1) CDT results are lattice simulations — continuum limit is not rigorously established. (2) The phase diagram depends on the coupling constants (κ_0, κ_4, Δ) — why the universe is in phase C is not explained. (3) The de Sitter geometry emerges for a spatial sphere topology S^3 — this is a topological input. (4) Extension to full initial-data problem (arbitrary (h_{ij}, K_{ij})) not done.

---

## P10 — Weyl-Curvature Dissipation via Bulk Viscosity

**ID:** P10
**Name:** Pre-bounce viscous dissipation attractor
**Mathematical definition:** In imperfect-fluid GR cosmology, the stress-energy tensor T_{μν} = (ρ+p)u_μu_ν + pg_{μν} + π_{μν} includes a bulk viscous pressure ζ θ (where θ = ∇_μ u^μ is the expansion rate and ζ is bulk viscosity coefficient) and shear viscous stress η σ_{μν} (where σ_{μν} is the shear tensor and η is shear viscosity). For a contracting universe (θ < 0), viscous dissipation produces entropy and damps anisotropies: dσ_{μν}/dt ~ -η/ρ · σ_{μν}. If η/s (viscosity-to-entropy ratio) exceeds a critical value during a contraction phase, anisotropies (and hence Weyl curvature, since W_{μνρσ} ~ σ_{μν} in spatially homogeneous models) are exponentially damped before the bounce.
**Independent motivation:** Viscous cosmology is studied in the context of early-universe heavy-ion physics analogues (quark-gluon plasma with η/s ~ ℏ/4πk_B, the KSS bound). Bulk and shear viscosity appear in any interacting medium. The KSS bound (Kovtun-Son-Starinets 2005) is an independently motivated lower bound on η/s from AdS/CFT.
**Relevant literature:** Weinberg (1971) Astrophys.J. 168:175; Misner (1968) Astrophys.J. 151:431 (chaotic cosmology); Barrow (1988) Nucl.Phys.B 310:743; Kovtun-Son-Starinets (2005) Phys.Rev.Lett. 94:111601.
**Physical domain:** Classical GR with viscous matter; pre-bounce cosmology.
**Expected action on Γ_GR:** Shear viscosity damps the Weyl-curvature-generating modes. Over a long enough contraction with sufficient η/s, the shear is driven to zero and the Weyl tensor is suppressed. The attractor is the FRW solution (zero shear, zero Weyl).
**Potential R1 mechanism:** If a specific matter sector (e.g., a strongly-coupled plasma near the bounce) has η/s above the threshold for complete Weyl damping, then the pre-bounce universe is driven to near-zero Weyl regardless of initial conditions — over a wide basin. This supplements or replaces the ekpyrotic scalar with a viscous matter sector.
**Known objections:** (1) Requires assuming a specific viscous matter sector with the right η/s — this is an assumed input analogous to the ekpyrotic scalar potential. (2) The bounce is still unresolved. (3) Viscous cosmology at high density and temperature involves poorly understood matter physics. (4) The wide-basin property depends on the ratio η/s, which is a free parameter.

---

## P11 — Modular Hamiltonian Geometry Selection

**ID:** P11
**Name:** Tomita-Takesaki modular-flow geometric restriction
**Mathematical definition:** For a von Neumann algebra M and a cyclic and separating state ω, the Tomita-Takesaki theory defines the modular operator Δ_ω and the modular Hamiltonian K_ω = -log Δ_ω. The modular flow σ_t^ω(a) = Δ_ω^{it} a Δ_ω^{-it} is a one-parameter automorphism of M. For quantum fields in a region R of spacetime, the modular Hamiltonian is K_R = -log ρ_R where ρ_R = Tr_{R^c}|ψ⟩⟨ψ| is the reduced density matrix. For the Minkowski vacuum in a Rindler wedge, K_R = 2π ∫ dx x T_{00}(x) (the boost generator). The proposal: physical initial states are those for which the modular Hamiltonian K_Σ of the initial Cauchy surface Σ generates a flow that is geometric (i.e., K_Σ corresponds to a Killing vector or conformal Killing vector of the metric h_{ij}). Non-geometric modular flow signals a state inconsistent with semi-classical geometry.
**Independent motivation:** Witten (2021) showed that the algebra of gravitational observables in de Sitter space is Type II₁ — different from the Type III₁ algebra of QFT in flat space. This has physical consequences for the modular structure. Modular Hamiltonians connect entanglement to geometry (Bisognano-Wichmann theorem).
**Relevant literature:** Tomita (1967); Takesaki (1970); Bisognano-Wichmann (1975) J.Math.Phys. 16:985; Witten (2021) J.Geom.Phys. 162:104055; Casini-Huerta-Myers (2011) JHEP 05:036.
**Physical domain:** Algebraic QFT; quantum gravity in de Sitter.
**Expected action on Γ_GR:** Requires that the modular Hamiltonian of the cosmological state be geometric. Non-geometric modular Hamiltonians correspond to states with entanglement structure inconsistent with a smooth background geometry — this restricts to states where geometry is well-defined.
**Potential R1 mechanism:** High-Weyl initial data corresponds to quantum states with highly non-geometric modular structure (large deviations from the Bisognano-Wichmann theorem). Requiring geometric modular flow may select the low-Weyl sector.
**Known objections:** (1) Modular Hamiltonians are generally non-local and hard to compute. (2) The geometric modular flow condition requires a quantum state, not just classical initial data. (3) The connection between non-geometric modular flow and Weyl curvature is not established quantitatively.

---

## P12 — Gravitational Entropy Production Bound in Contraction

**ID:** P12
**Name:** Second-law-constrained contraction phase restriction
**Mathematical definition:** Define the Weyl curvature scalar W² = C_{αβγδ}C^{αβγδ}. Define a gravitational entropy proxy S_grav ~ ∫_Σ √h · W² d³x (covariant, background-independent). Under GR evolution in a contracting phase, if matter obeys the dominant energy condition, the GSL (Generalized Second Law) requires dS_total/dt ≥ 0, where S_total = S_matter + S_grav. For a contracting phase with fixed matter entropy (S_matter ~ const), the GSL constrains the rate of change of S_grav. The proposal: the GSL applied to the pre-bounce phase implies that W² cannot grow without bound in the past — i.e., the initial state must have had W² below the threshold where backward evolution would violate the GSL.
**Independent motivation:** The GSL is the most robustly established result connecting gravity and thermodynamics. Wall (2012) proved the GSL in linearized gravity. The question of whether the GSL constrains cosmological initial conditions is open.
**Relevant literature:** Wall (2012) Phys.Rev.D 85:104049; Wald (1993) Phys.Rev.D 48:R3427 (dynamical black hole entropy); Penrose (1979) in "General Relativity" (Weyl curvature hypothesis); Davies-Ford-Samuel (1988) on GSL in cosmology.
**Physical domain:** Classical GR with matter satisfying DEC.
**Expected action on Γ_GR:** If backward-in-time evolution of high-Weyl initial data produces GSL violation (entropy decrease), then such initial data is physically excluded by the GSL. This restricts Γ_GR to configurations whose backward evolution is GSL-consistent.
**Potential R1 mechanism:** High-Weyl initial data, evolved backward, would require decreasing gravitational entropy (W² → larger values in the past) while matter entropy is approximately constant — violating the GSL. The constraint S_grav(t_initial) ≤ S_grav(t_Planck) under GSL-constrained backward evolution selects the low-Weyl sector at t_initial.
**Known objections:** (1) S_grav ~ W² is not a rigorously defined gravitational entropy (Penrose's proposal is contested — this is on the ONTOLOGY_PROHIBITION list as a prohibited equivalence). This candidate must not assume the Weyl=gravitational entropy identification; it must derive the connection from the GSL. (2) The GSL in cosmological settings (non-stationary, no Killing horizon) is not fully established. (3) Backward evolution of GR is time-reversal symmetric — what singles out the backward direction?

---

## P13 — Effective Field Theory Validity Constraint

**ID:** P13
**Name:** EFT-validity domain restriction on initial data
**Mathematical definition:** Effective field theory (EFT) is valid when the relevant curvature scale R^{1/2} ≪ M_UV (the UV cutoff). When R^{1/2} ~ M_UV (Planck scale or string scale), EFT breaks down. Define the EFT-valid region of initial-data space: Γ_EFT = {(h_{ij}, K_{ij}) | R_{max}[h,K] ≤ M_UV²} where R_{max} is the maximum curvature eigenvalue on the initial slice. For high-Weyl initial data, R_{max} may exceed M_UV², placing the data outside the EFT-valid region. Physical realizability requires data in the EFT-valid region: Γ_phys ⊆ Γ_EFT.
**Independent motivation:** EFT validity is a standard physical requirement. String theory, loop quantum gravity, and asymptotic safety all impose a UV cutoff beyond which the EFT description breaks down. This is not a new principle — it is a consequence of any UV-complete theory.
**Relevant literature:** Burgess (2004) Ann.Phys. 313:383; Cohen-Kaplan-Nelson (1999) Phys.Rev.Lett. 82:4971 (EFT and holography); Reuter-Saueressig (2019) on asymptotic safety EFT; Donoghue (1994) Phys.Rev.D 50:3874.
**Physical domain:** Any EFT of gravity; universal.
**Expected action on Γ_GR:** Restricts to initial data with curvature below the UV cutoff. Since the Weyl tensor contributes to curvature invariants, high-Weyl initial data may have R_max > M_UV² and be excluded from the EFT-valid region.
**Potential R1 mechanism:** If the big bang singularity is resolved by UV physics and the post-resolution state (the physical initial state at the Planck epoch) must lie in the EFT-valid region of the UV-complete theory, then the initial data cannot have Weyl curvature above M_UV². This is a necessary but potentially not sufficient condition — it establishes an upper bound on Weyl curvature, but not specifically the very small Weyl curvature observed.
**Known objections:** (1) The EFT validity condition restricts to R_max ≤ M_UV² but does not select specifically the low-Weyl sector — all EFT-valid initial data satisfies it, including moderately high-Weyl states. (2) This is a necessary condition, not a sufficient selection principle. (3) The UV cutoff M_UV is itself a free parameter without a derived value.

---

## P14 — Gravitational Wave Background Coherence Condition

**ID:** P14
**Name:** Stochastic-gravitational-wave coherence restriction
**Mathematical definition:** In linearized GR, gravitational waves are spin-2 perturbations h_{μν} of a background metric. For a stochastic gravitational wave background (SGWB), the power spectral density Ω_{GW}(f) = (1/ρ_c)(dρ_{GW}/d log f) characterizes the energy density. The coherence condition: the primordial SGWB must be consistent with the observed upper bounds and the causal coherence length. More precisely, on superhorizon scales (k ≪ aH), gravitational wave modes are frozen — their amplitude is set by initial conditions. For a state with large Weyl curvature on superhorizon scales, the frozen GW modes would produce a SGWB exceeding the observed bounds. Define: Γ_coherent = {(h_{ij}, K_{ij}) | the implied Ω_{GW}(f) ≤ Ω_{GW}^{obs}(f) for all f}.
**Independent motivation:** The SGWB is directly observable (LIGO/LISA/PTA). The observed upper bounds on Ω_{GW}(f) are real observational constraints. The connection between large-scale Weyl curvature and GW amplitude is established through linearized GR.
**Relevant literature:** Allen-Romano (1999) Phys.Rev.D 59:102001; Maggiore (2000) Phys.Rep. 331:283; LIGO-Virgo (2021) Phys.Rev.D 104:022004; Caprini-Figueroa (2018) Class.Quant.Grav. 35:163001.
**Physical domain:** Linearized GR; cosmological perturbation theory.
**Expected action on Γ_GR:** Restricts the power spectrum of superhorizon GW modes. High-Weyl initial data implies large frozen GW modes on superhorizon scales — excluded by observed bounds.
**Potential R1 mechanism:** The observational constraint Ω_{GW}(f) ≤ Ω_{GW}^{obs} imposes an upper bound on the Weyl curvature of the initial state. If this bound is tight enough, it restricts to the low-Weyl sector.
**Known objections:** (1) This uses observational constraints as a selection principle — it is empirical, not derived from first principles. (2) The bound applies to modes in the observable window; superhorizon modes (relevant to R1) are not directly observed. (3) This is a consistency constraint, not a derivation of why the state was smooth.

---

## P15 — Gravitational Entropy Cone from Unitarity

**ID:** P15
**Name:** Unitarity-preserving phase-space restriction
**Mathematical definition:** In quantum gravity, time evolution is unitary: |ψ(t)⟩ = U(t)|ψ(0)⟩ with U†U = 1. Unitarity requires that the von Neumann entropy of the full state is conserved: S(ρ(t)) = S(ρ(0)). For a system initialized in a pure state, S = 0 always. For a mixed state, S is constant. The proposal: unitarity, combined with the Page curve for the full cosmological state, constrains which classical initial geometries are consistent with unitary quantum evolution. Specifically, if the final state of the universe (at late times, after black hole evaporation) is a specific quantum state consistent with unitary S-matrix, the initial state must be in the pre-image of that final state under U†. The set of compatible initial states Γ_unitary = U†(Γ_final) may be restricted if Γ_final is small.
**Independent motivation:** Unitarity is the fundamental consistency requirement of quantum mechanics. The Page curve (Page 1993) establishes how entanglement entropy evolves unitarily. Hawking information paradox resolution via unitarity is a major active area.
**Relevant literature:** Page (1993) Phys.Rev.Lett. 71:1291; Penington (2020) JHEP 09:002; Almheiri et al. (2019) JHEP 09:073; Hawking-Perry-Strominger (2016) Phys.Rev.Lett. 116:231301.
**Physical domain:** Quantum gravity — the full quantum cosmological state.
**Expected action on Γ_GR:** If the late-time final state is restricted (e.g., by the constraint that black holes have fully evaporated and the state is a Page-scrambled state of Hawking radiation), then the set of initial states consistent with this final state under unitary evolution is a specific subset of Γ_GR.
**Potential R1 mechanism:** Unitarity constrains the initial state by the final state. If the final state of the universe is approximately thermal with specific Page-curve properties, the initial state must have been in a specific sector (low entropy, small Weyl) for the unitary evolution to reproduce the observed entropy increase. This is a constraint from the future, not the past — a final-state projection mechanism.
**Known objections:** (1) Final-state projections are highly speculative and not established physics. (2) The final state of the universe is unknown. (3) Unitarity constrains which initial states are compatible with a given final state, but does not select a unique initial state unless the final state is uniquely specified. (4) This essentially assumes the desired final state, which may hide assumption laundering in the final condition rather than the initial condition.

---

## P16 — Non-Commutative Geometry Initial-Data Restriction

**ID:** P16
**Name:** Non-commutative-geometry spectral-triple restriction
**Mathematical definition:** In Connes's non-commutative geometry (NCG), a spectral triple (A, H, D) replaces the classical manifold (M, g): A is a C*-algebra, H is a Hilbert space, D is the Dirac operator. The metric information is encoded in D: d(p,q) = sup{|f(p)-f(q)| : ||[D,f]|| ≤ 1}. For a classical Riemannian manifold, D is the Dirac operator on the spinor bundle and the spectral triple recovers the full metric. The proposal: physical cosmological initial data must correspond to spectral triples with a specific property — e.g., that the spectrum of D² (the spectral action S[D] = Tr f(D²/Λ²)) is extremized or satisfies a specific eigenvalue bound. The Connes-Chamseddine spectral action S[D] = Tr f(D/Λ) gives, in the classical limit, the Einstein-Hilbert action plus corrections.
**Independent motivation:** NCG provides an algebraic, background-independent description of geometry. The spectral action principle (Connes-Chamseddine 1997) derives the Standard Model Lagrangian + GR from a purely spectral input — independently motivated by unification goals.
**Relevant literature:** Connes (1994) "Noncommutative Geometry"; Connes-Chamseddine (1997) Comm.Math.Phys. 186:731; Chamseddine-Connes-Marcolli (2007) Adv.Theor.Math.Phys. 11:991; Devastato et al. (2018) J.Geom.Phys. 132:228.
**Physical domain:** Planck-scale geometry / quantum gravity unification.
**Expected action on Γ_GR:** The spectral action extremization selects specific geometries. If the extremum of Tr f(D/Λ) over all geometries compatible with the Cauchy data corresponds to low-Weyl configurations, then the spectral action principle selects Γ_phys.
**Potential R1 mechanism:** The Dirac spectrum of high-Weyl geometries may differ systematically from low-Weyl geometries in a way that the spectral action disfavors. If f(D/Λ) is a decreasing function of eigenvalues and high-Weyl geometries have larger Dirac eigenvalues, the spectral action principle would select low-Weyl initial data.
**Known objections:** (1) The spectral action selects the equations of motion (equations of motion = Einstein's equations in the classical limit), not specific solutions. It does not select initial data. (2) The connection between Weyl curvature and the Dirac spectrum is not straightforwardly inverse — the spectrum depends on the full curvature, not just Weyl. (3) This approach requires a spin structure on the 3-manifold, which is an additional topological assumption.

---

## P17 — Penrose-Process Energy Extraction Instability Kill

**ID:** P17
**Name:** Superradiant-instability exclusion of high-angular-momentum initial data
**Mathematical definition:** In GR, rotating black holes (Kerr metric) exhibit superradiance: waves with frequency ω < mΩ_H (m = azimuthal mode number, Ω_H = horizon angular velocity) are amplified on scattering, extracting energy from the ergoregion (Penrose process). In a spacetime with a reflective boundary (e.g., AdS, or a compact Cauchy surface), superradiant modes grow exponentially — a superradiant instability. Define: Γ_stable^{sr} = {(h_{ij}, K_{ij}) | no superradiant instability exists for the evolved spacetime}. Initial data with large angular momentum density (related to large Weyl magnetic part B_{ij} = ½ε_{ikl}C^{kl}{}_{j0}) may be superradiantly unstable.
**Independent motivation:** Superradiant instability is an established GR effect (Press-Teukolsky 1972, Brito-Cardoso-Pani 2015). It is independently motivated by black hole physics, not cosmology. The connection between superradiance and initial-data restriction is novel.
**Relevant literature:** Press-Teukolsky (1972) Nature 238:211; Brito-Cardoso-Pani (2015) Lect.Notes Phys. 906; Dolan (2007) Phys.Rev.D 76:084001.
**Physical domain:** GR in rotating spacetimes; black hole physics.
**Expected action on Γ_GR:** Excludes initial data that would lead to superradiantly unstable spacetimes. This is a stability-based restriction.
**Potential R1 mechanism:** Initial data with large magnetic Weyl tensor (B_{ij}) corresponds to large gravitomagnetic fields — related to large angular momentum density. Superradiant instability of such configurations would exclude them from the set of long-lived physical states. Over cosmological time, only superradiantly stable configurations survive.
**Known objections:** (1) Superradiant instability applies to specific geometries (Kerr) and boundary conditions (reflective walls) — not cosmological initial data in general. (2) The connection between cosmological Weyl curvature and superradiance is not established. (3) This is an instability argument, not a selection principle for the initial state.

---

## P18 — Gravitational Focusing Theorem Restriction

**ID:** P18
**Name:** Null-geodesic-completeness restriction on initial curvature
**Mathematical definition:** The Penrose singularity theorem states: if (M,g) has a non-compact Cauchy surface and contains a trapped surface (θ < 0 on a null surface), then M is geodesically incomplete. The focusing theorem: for a null congruence with expansion θ, dθ/dλ = -θ²/2 - σ_{ab}σ^{ab} - R_{ab}l^al^b ≤ -θ²/2 under the null energy condition R_{ab}l^al^b ≥ 0. Define: Γ_complete = {(h_{ij}, K_{ij}) | the maximally extended spacetime evolved from (h,K) is null-geodesically complete (no trapped surfaces in the past)}. Initial data that would require a past singularity (from Penrose's theorem applied backward) to be physically accessible must have come from a non-trapped state.
**Independent motivation:** Null geodesic completeness is independently motivated as a condition for globally well-posed physics. The Penrose theorem is a rigorous GR result. The requirement of no past singularity (or a resolved past singularity) is a standard assumption in cosmology.
**Relevant literature:** Penrose (1965) Phys.Rev.Lett. 14:57; Hawking-Penrose (1970) Proc.Roy.Soc. A314:529; Borde (1994) Phys.Rev.D 50:3392; Borde-Guth-Vilenkin (2003) Phys.Rev.Lett. 90:151301.
**Physical domain:** Classical GR; global causal structure.
**Expected action on Γ_GR:** Restricts to initial data whose backward evolution does not immediately produce trapped surfaces. Initial data with large Weyl curvature may have trapped surfaces in the backward direction — violating null geodesic completeness.
**Potential R1 mechanism:** The condition that the past evolution is free of trapped surfaces for a sufficiently long duration (enough for the ekpyrotic attractor to operate) restricts the initial Weyl curvature to be below the black-hole-formation threshold — precisely the ekpyrotic gap condition. This formalizes the "pre-contraction state below black-hole-formation threshold" requirement.
**Known objections:** (1) This formalizes the ekpyrotic gap condition but does not close it — it restates the requirement rather than deriving it from an independent principle. (2) Null geodesic completeness in the past is assumed in many cosmological models but not derived. (3) This is a necessary condition, not a derivation.

---

## P19 — Scale-Factor Duality and Pre-Big-Bang State

**ID:** P19
**Name:** String-cosmology scale-factor duality restriction
**Mathematical definition:** In string cosmology (Veneziano 1991, Gasperini-Veneziano 1993), the low-energy effective action S = ∫d^4x √(-g) e^{-φ} [R + (∇φ)² + ...] is invariant under the scale-factor duality: a(t) → 1/a(t), φ(t) → φ(t) - 6 log a(t), t → -t (for flat FRW). This duality relates a contracting, string-coupling-growing phase (pre-big-bang) to an expanding, coupling-decreasing phase (post-big-bang). The duality constraint: physical initial data must be in the duality-invariant sector — i.e., the pre-big-bang state is the dual of the post-big-bang state. Since the post-big-bang state is smooth (observed), the pre-big-bang state (its dual) is also constrained by duality.
**Independent motivation:** Scale-factor duality is a consequence of T-duality in string theory, which is independently established in the string theory context. The pre-big-bang scenario (Gasperini-Veneziano) provides an alternative to inflation.
**Relevant literature:** Veneziano (1991) Phys.Lett.B 265:287; Gasperini-Veneziano (1993) Astropart.Phys. 1:317; Gasperini-Veneziano (2003) Phys.Rep. 373:1; Buonanno-Damour-Veneziano (1999) Nucl.Phys.B 543:275.
**Physical domain:** String cosmology / low-energy string effective action.
**Expected action on Γ_GR:** The duality maps post-big-bang initial data to pre-big-bang initial data. Since the post-big-bang state has low Weyl curvature (observed), the duality constraint requires the pre-big-bang state to be in a specific sector determined by the duality transformation.
**Potential R1 mechanism:** If duality maps the observed (smooth) post-big-bang state to the pre-big-bang state, and if the map is smooth and unique, then the pre-big-bang state is also in the low-Weyl sector — derived from the duality, not assumed.
**Known objections:** (1) Scale-factor duality is derived for the homogeneous FRW background — extension to full inhomogeneous GR initial data is not established. (2) The pre-big-bang scenario has its own graceful exit problem (the bounce). (3) String cosmology assumes string theory; the string coupling dilaton must be in the weak-coupling regime for the duality to apply. (4) This is restricted to string theory, not a model-independent result.

---

## P20 — Topological Censorship of High-Genus Initial Data

**ID:** P20
**Name:** Topological-censorship restriction on initial 3-manifold topology
**Mathematical definition:** The topological censorship theorem (Friedman-Schleich-Witt 1993, Chrusciel-Galloway 1994): in a spacetime satisfying the null energy condition with a simply connected conformal boundary, any causal curve connecting boundary points must be homotopic to a curve through the trivial topology region. In other words, non-trivial topology (handles, wormholes) in the spatial section is "censored" — it cannot propagate or be observed by a distant observer within the theorem's hypotheses. Define: Γ_TC = {(h_{ij}, K_{ij}) | the 3-manifold Σ has topology consistent with topological censorship in the evolved spacetime}.
**Independent motivation:** Topological censorship is derived from the null energy condition and causal structure — independently motivated without cosmological assumptions. It is a theorem, not a hypothesis.
**Relevant literature:** Friedman-Schleich-Witt (1993) Phys.Rev.Lett. 71:1486; Chrusciel-Galloway (1994) Class.Quant.Grav. 11:L147; Galloway et al. (1999) Phys.Rev.D 60:104039.
**Physical domain:** Classical GR; asymptotically flat or asymptotically AdS spacetimes.
**Expected action on Γ_GR:** Restricts the topology of the physical Cauchy surface. Non-trivial topologies (large genus, multiple handles) are censored. This is a topological restriction, not a curvature restriction.
**Potential R1 mechanism:** Topological restriction to simple topology (S^3 or T^3) does not directly restrict Weyl curvature. A flat T^3 can carry arbitrarily large Weyl curvature in its metric. Topological censorship restricts topology but not the metric within a topology class — insufficient to restrict Γ_GR to low-Weyl states alone.
**Known objections:** (1) Topology ≠ curvature: simple topology (S^3) does not imply low Weyl curvature. A Bianchi IX model on S^3 can have high Weyl curvature. (2) The theorem applies to the evolved spacetime's asymptotic structure, not to the initial data per se. (3) This restricts topological degrees of freedom but not curvature degrees of freedom — insufficient for R1.

---

## P21 — Quantum Error Correction Structure of Spacetime

**ID:** P21
**Name:** Quantum-error-correction bulk-reconstruction restriction
**Mathematical definition:** The holographic quantum error correction (QEC) framework (Almheiri-Dong-Harlow 2015) proposes that the bulk spacetime is reconstructed from the boundary via a quantum error correcting code: the bulk algebra A_bulk is encoded in the boundary algebra A_boundary via an isometric embedding V: H_bulk → H_boundary such that for any bulk operator O, there exists a boundary operator O_∂ with V†O_∂V = O. The Ryu-Takayanagi formula follows. The proposal: physical initial data (semi-classical geometries) must be "reconstructible" from a lower-dimensional holographic description — i.e., they must correspond to codewords in a quantum error correcting code. Define Γ_QEC = {(h_{ij}, K_{ij}) | ∃ a QEC encoding from a (d-1)-dimensional Hilbert space}.
**Independent motivation:** QEC structure of holography is derived from AdS/CFT and independently motivated from the structure of operator algebras in quantum gravity. It is not specific to the cosmological initial state.
**Relevant literature:** Almheiri-Dong-Harlow (2015) JHEP 04:163; Pastawski-Yoshida-Harlow-Preskill (2015) JHEP 06:149; Harlow (2017) Comm.Math.Phys. 354:865.
**Physical domain:** AdS/CFT; holographic quantum gravity.
**Expected action on Γ_GR:** Restricts bulk geometries to those reconstructible from a lower-dimensional code. In AdS, reconstructible geometries are the smooth, near-classical ones. High-Weyl bulk geometries may not be reconstructible from a unitary code.
**Potential R1 mechanism:** If the physical initial data must be QEC-reconstructible, and if QEC reconstruction preferentially selects low-Weyl geometries (because the code distance is large for smooth geometries and zero for geometries with deep entanglement wedge degeneracies), then QEC structure provides a selection mechanism.
**Known objections:** (1) QEC holography is established for AdS, not for cosmological (de Sitter or flat FRW) spacetimes. (2) The mechanism requires a boundary theory whose state determines the bulk — the boundary theory's state is not specified, relocating the problem. (3) This is essentially another holographic approach — the class P (holographic) was killed in the closure audit.

---

## P22 — Quantum Darwinism Redundancy Condition

**ID:** P22
**Name:** Quantum-Darwinism redundancy restriction on initial geometry
**Mathematical definition:** Quantum Darwinism (Zurek 2009) proposes that objective classical reality emerges when a quantum state |ψ_S⟩ imprints many redundant copies of information about observable S into the environment: for each environmental fragment E_k, the mutual information I(S:E_k) ≈ H(S) (the classical limit). The redundancy R_δ = N_frag is the number of fragments each carrying a 1-δ fraction of H(S). The proposal: the classical geometry of the early universe is objective only if it satisfies the quantum Darwinism redundancy condition — i.e., the gravitational degrees of freedom imprint redundant records in the matter degrees of freedom. Define: Γ_QD = {(h_{ij}, K_{ij}) | R_δ[h,K] ≥ R_min for some independently motivated R_min}.
**Independent motivation:** Quantum Darwinism is independently motivated as an explanation of classicality in quantum mechanics. It is a non-cosmological concept with laboratory applications (pointer states, einselection).
**Relevant literature:** Zurek (2009) Nature Physics 5:181; Blume-Kohout-Zurek (2008) Phys.Rev.A 73:062310; Riedel-Zurek-Zwolak (2010) New J.Phys. 12:083020.
**Physical domain:** Quantum measurement theory; open quantum systems.
**Expected action on Γ_GR:** Requires that the initial geometry be observable (in the quantum Darwinist sense) — that it imprint records in its environment. Highly quantum, high-Weyl geometries near the Planck scale may not satisfy the redundancy condition — they do not imprint classical records.
**Potential R1 mechanism:** The classicality condition R_δ ≥ R_min may select the low-Weyl sector because smooth geometries are pointer states (they are stable under environmental monitoring) while high-Weyl configurations are fragile (monitoring destroys them). The initial state must be classical-enough to imprint records — selecting the stable, low-Weyl sector.
**Known objections:** (1) Quantum Darwinism explains how classicality is perceived by observers, not which states are physically realized. It requires a pre-existing quantum state. (2) Applying quantum Darwinism to the initial geometry requires a theory of quantum gravity and an environment — neither is specified. (3) This is a restatement of decoherence in a different language — decoherence has been killed as a selection mechanism.

---

## P23 — Weyl-Tensor Algebraic-Type Restriction

**ID:** P23
**Name:** Weyl-tensor Petrov-type stability restriction
**Mathematical definition:** The Weyl tensor C_{αβγδ} is classified by its Petrov type (I, II, III, D, N, O) based on the algebraic multiplicity of its principal null directions (PNDs). Type O: C_{αβγδ} = 0 (conformally flat). Type N, III: one PND of higher multiplicity. Type D: two double PNDs (Schwarzschild, Kerr). Type I (general): four distinct PNDs. The Petrov type of the Weyl tensor is a covariant, background-independent classification. The proposal: physical initial data has a restricted Petrov type — specifically, the "algebraically special" types (D, N, III, O) are stable under perturbation in a specific sense, while algebraically general Type I configurations are unstable. Define: Γ_Petrov = {(h_{ij}, K_{ij}) | the Weyl tensor of the evolved spacetime is algebraically special (type D, N, or O) at leading order}.
**Independent motivation:** The Goldberg-Sachs theorem (1962) connects algebraic specialness (Petrov type D or better) to the existence of a shear-free geodesic null congruence. Kerr and Schwarzschild metrics are Type D. Gravitational radiation has Petrov type N asymptotically (peeling property, Penrose 1965). Algebraic specialness is an independently motivated concept in GR.
**Relevant literature:** Petrov (1954); Goldberg-Sachs (1962) Acta Phys.Polon. 22:13; Penrose (1965) Proc.Roy.Soc. A284:159 (peeling); Stewart-Walker (1974) Proc.Roy.Soc. A341:49.
**Physical domain:** Classical GR; exact solutions.
**Expected action on Γ_GR:** Restricts initial data to configurations whose Weyl tensor is algebraically special. The algebraically special subspace of Γ_GR has smaller dimension than the full space (Type I is the generic case). Type O (C=0) is the most restricted.
**Potential R1 mechanism:** If physical initial data is restricted to algebraically special Petrov types (e.g., Type O or D) by a stability condition, then Γ_phys is a proper subset of Γ_GR. Type O means C_{αβγδ} = 0 at the initial time — precisely the low-Weyl condition. But requiring Type O from the start encodes the desired conclusion (low Weyl).
**Known objections:** (1) Algebraic specialness at the initial time requires the Weyl tensor to have a specific algebraic form — this is a constraint on Weyl, not independent of it. Requiring Type O is equivalent to requiring low Weyl — assumption laundering. (2) Algebraic stability results (Wald 1984) show Type I is generic and stable — algebraically special solutions are non-generic. (3) This does not provide an independent reason for algebraic specialness; it merely classifies the desired state.

---

## P24 — Maximum Holographic Complexity Bound

**ID:** P24
**Name:** Holographic-complexity bound on initial data
**Mathematical definition:** Susskind's complexity-volume conjecture: the quantum complexity C(|ψ⟩) of the boundary state equals the volume of the maximal Cauchy slice in the bulk: C = V_max / (GN ℓ). The complexity-action conjecture: C = S_{WdW} / π ℏ where S_{WdW} is the gravitational action of the Wheeler-DeWitt patch. Define: Γ_C = {(h_{ij}, K_{ij}) | C[h,K] ≤ C_max} for some maximum complexity C_max. High-complexity initial data (complex, inhomogeneous geometries) violates the complexity bound; low-complexity initial data (smooth, homogeneous) satisfies it.
**Independent motivation:** Holographic complexity conjectures are independently motivated by the need to explain the linear growth of the Einstein-Rosen bridge volume behind a black hole horizon. The conjectures relate bulk geometry to boundary quantum circuit complexity.
**Relevant literature:** Susskind (2014) Fortsch.Phys. 64:44; Brown-Roberts-Susskind-Swingle-Zhao (2016) Phys.Rev.Lett. 116:191301; Chapman-Marrochio-Myers (2018) Phys.Rev.Lett. 120:121602.
**Physical domain:** AdS/CFT; black hole physics.
**Expected action on Γ_GR:** Restricts to initial data with bounded geometric complexity. Low-complexity (smooth) initial data satisfies the bound; high-complexity (inhomogeneous) initial data may exceed it.
**Potential R1 mechanism:** If physical initial states must have complexity below some Planck-scale maximum (because higher complexity cannot be prepared by any physical process in finite time), then the physical initial data is restricted to the low-complexity, low-Weyl sector.
**Known objections:** (1) Holographic complexity conjectures are formulated in AdS — wrong geometry for cosmology. (2) The conjectures are not proven; they are motivated by specific gravity/gauge duality results. (3) This is essentially a holographic mechanism — class P is killed. (4) Complexity bounds do not directly constrain Weyl curvature.

---

## P25 — Gravitational Decoherence Time-Scale Hierarchy

**ID:** P25
**Name:** Gravitational-decoherence pointer-state restriction
**Mathematical definition:** Anastopoulos-Hu (2008) and Blencowe (2013) derive the gravitational decoherence rate Γ_{dec} ~ (GE²)/(ℏ c^5) for a superposition of mass distributions separated by distance d. For a cosmological geometry in a quantum superposition of configurations, the decoherence time τ_{dec} ~ ℏ/Γ_{dec} ~ (ℏ c^5)/(G E²) where E is the energy stored in the geometric configuration difference. Pointer states — configurations stable under gravitational decoherence — satisfy: δE_{geom} ≤ (ℏ c^5 / G τ_H)^{1/2} where τ_H is the Hubble time. Define: Γ_pointer = {(h_{ij}, K_{ij}) | δE_{geom}[h,K] ≤ (ℏ c^5 / G τ_H)^{1/2}}.
**Independent motivation:** Gravitational decoherence is an independently predicted consequence of combining QM and GR. It is studied in precision measurement contexts (Diósi-Penrose model). The concept of pointer states is independently motivated from quantum measurement theory.
**Relevant literature:** Diósi (1987) Phys.Lett.A 120:377; Penrose (1996) Gen.Rel.Grav. 28:581; Anastopoulos-Hu (2008) New J.Phys. 10:083006; Blencowe (2013) Phys.Rev.Lett. 111:021302.
**Physical domain:** Non-relativistic quantum gravity; precision measurement.
**Expected action on Γ_GR:** Restricts initial geometries to those stable under gravitational decoherence — the "pointer geometry" sector. Highly quantum, high-Weyl configurations decohere rapidly and are not stable classical states.
**Potential R1 mechanism:** The early universe must have decohered into a classical geometry. The pointer geometries — those stable under gravitational decoherence — are the smooth, near-homogeneous configurations. High-Weyl initial data would decohere into lower-Weyl states rapidly, but then the selection question is why the decohered state was low-Weyl, not why the initial quantum state was.
**Known objections:** (1) Gravitational decoherence selects classical states from quantum superpositions, but does not select which classical state is realized. (2) The Diósi-Penrose model applies to non-relativistic systems; extension to cosmological GR is not established. (3) This is another decoherence-based approach — decoherence is killed as a selection mechanism in the ASSUMPTION_FIREWALL.

---

*Document status: GENERATION COMPLETE — 25 candidates generated*
*Next: KILL_LOG.md — apply all 6 kill tests to every candidate*
