# KILL_LOG
## Gate 5 — Kill Test Results for All Candidates

**Status:** Part III — Kill tests applied to all 25 candidates from CANDIDATE_REGISTER.md
**Authority:** DERIVATION_REQUIREMENTS.md, ASSUMPTION_FIREWALL.md, ONTOLOGY_PROHIBITION.md
**Date:** August 2026

---

## The Six Kill Tests

**T1 — CONCLUSION ENCODING:** Does the primitive definition contain homogeneity, isotropy, FLRW, low Weyl curvature, smoothness, low gravitational entropy, near-equilibrium, small phase-space volume, or special initial condition? Kill if yes and cannot be reformulated without encoding the conclusion.

**T2 — BACKGROUND DEPENDENCE:** Can it be defined on arbitrary (h_ij, K_ij) without assuming FLRW, de Sitter, Minkowski, or another preferred background? Kill if no.

**T3 — TRIVIALITY:** Does it merely impose an arbitrary constraint or boundary condition without independent motivation? Kill if yes.

**T4 — RENAMING:** Is it mathematically equivalent to an already-killed mechanism? Kill as duplicate.

**T5 — EXISTING-PHYSICS CLOSURE:** Is it already provided by known physics? Kill as non-new, record which theory provides it.

**T6 — UNDEFINED MEASURE:** Does it depend on 'typical,' 'generic,' 'natural,' 'simple,' 'probable,' or 'small phase space' without defining the measure? Kill.

---

## P01 — UV Fixed-Point Gravitational-Coupling Restriction (Asymptotic Safety)

**Class:** O (Renormalization/coarse-graining)

**T1 — CONCLUSION ENCODING:**
The primitive is defined as: initial data lies on a renormalized trajectory emanating from the UV fixed point G* of the gravitational RG flow. This definition does not contain homogeneity, isotropy, FLRW, low Weyl curvature, or smoothness. The UV fixed point is defined in theory space (coupling constants), not in initial-data space. There is no a priori reason the UV critical manifold contains only smooth or low-Weyl configurations — this is an open question. The definition is clean.
**Result: PASS**

**T2 — BACKGROUND DEPENDENCE:**
The asymptotic safety RG flow is defined on theory space using the functional renormalization group equation ∂_t Γ_k = ½ Tr[(Γ_k^{(2)} + R_k)^{-1} ∂_t R_k], where Γ_k is the effective average action, R_k is the infrared regulator, and t = log(k/k_0). This can in principle be applied to arbitrary background geometries (background-independent formulations exist: Reuter-Weyer 2009, Percacci-Perini 2003). The primitive does not explicitly require FLRW or Minkowski. However, in practice all calculations are done expanding around a specific background (typically S^4 or flat space). The background-independent formulation exists but is technically incomplete.
**Charitable ruling:** The concept is definable on general initial data in principle; the practical limitation is not a conceptual prohibition. 
**Result: PASS (with reservation — full background-independent computation not available)**

**T3 — TRIVIALITY:**
Asymptotic safety is independently motivated as the UV completion of quantum gravity — it arose from the Weinberg (1979) asymptotic safety conjecture, motivated by the need to make quantum gravity well-defined without string theory. It is not postulated specifically to close R1. The fixed-point structure is an independently derived mathematical property.
**Result: PASS**

**T4 — RENAMING:**
The asymptotic safety UV fixed-point restriction is mathematically distinct from the killed mechanisms: it is not the no-boundary proposal (path-integral boundary condition), not the Vilenkin proposal, not entropy maximization, not BKM shape dynamics, not ekpyrosis. There is no equivalent killed mechanism.
**Result: PASS**

**T5 — EXISTING-PHYSICS CLOSURE:**
Asymptotic safety is a proposed extension of GR, not a completed theory. The Reuter fixed point is not an established result of standard QFT or GR — it is a research program with supporting evidence in truncations. The mechanism is not provided by standard GR, QFT, inflation, or any mechanism in the closure audit. It is new.
**Result: PASS**

**T6 — UNDEFINED MEASURE:**
The primitive does not invoke typicality, genericity, or naturalness. It invokes "renormalized trajectories" — a precisely defined concept in the RG flow on theory space. The measure issue is not the primary concern here. There is no appeal to undefined measure.
**Result: PASS**

**OVERALL VERDICT: SURVIVES**
P01 passes all six kill tests.

**Remaining concerns:**
1. The connection between the UV critical manifold in theory space and the space of classical initial data (h_ij, K_ij) is not established. P01 restricts theory space; whether this translates into a restriction on initial-data phase space remains to be derived.
2. All quantitative calculations are in truncated theory space or on specific background geometries — whether the result holds in the full theory is unknown.
3. The critical question — whether the UV critical manifold selects low-Weyl configurations specifically — is unanswered. P01 may restrict the initial state without selecting the low-Weyl sector.

---

## P02 — Local-Rindler-Horizon Thermodynamic Constraint

**Class:** B/J (Variational / Nonequilibrium dynamical)

**T1 — CONCLUSION ENCODING:**
The primitive is: for any local Rindler horizon, entropy flux satisfies δS/δA ≤ 1/4G. This is a local thermodynamic consistency condition. It does not mention homogeneity, isotropy, FLRW, or low Weyl curvature directly. However, the proposed R1 mechanism relies on: "high-Weyl initial data produces rapid focusing of null geodesics, creating caustics where thermodynamic entropy accounting breaks down." This identifies a connection to Weyl curvature, but the primitive itself does not encode low Weyl as input — it requires universal thermodynamic consistency.
**Result: PASS**

**T2 — BACKGROUND DEPENDENCE:**
The thermodynamic identity δQ = TdS with T = ℏa/2π (Unruh temperature, local Rindler) and S = A/4G can be applied in any curved spacetime with a well-defined local Rindler horizon. No preferred background is required. The Unruh effect is a QFT-in-curved-spacetime result that applies in any locally flat neighborhood.
**Result: PASS**

**T3 — TRIVIALITY:**
This is not an arbitrary constraint. It is derived from (a) Jacobson's (1995) derivation showing the Einstein equation follows from this thermodynamic identity, and (b) the Unruh effect (independently established). The thermodynamic identity is not postulated for R1 — it is an independently motivated consistency condition.
**Result: PASS**

**T4 — RENAMING:**
The thermodynamic constraint as a selection principle is distinct from the killed GSL-in-cosmology argument (which applies the second law to global cosmological evolution). This applies to local Rindler horizons everywhere in spacetime including at the initial data surface. It is not equivalent to the Hartle-Hawking proposal (which is a global path integral), ekpyrosis (which is a dynamical attractor from a scalar field), or entropic gravity (which derives the force law, not the initial state).
**Result: PASS**

**T5 — EXISTING-PHYSICS CLOSURE:**
Jacobson's (1995) result derives the Einstein equation from this thermodynamic identity. But that is the equation of motion, not an initial-state selection principle. The application of this thermodynamic identity as a constraint on which initial data is physically realizable is not established in existing physics. The mechanism is new.
**Result: PASS**

**T6 — UNDEFINED MEASURE:**
No appeal to typicality or genericity. The constraint is a sharp inequality (δS/δA ≤ 1/4G) applied everywhere.
**Result: PASS**

**OVERALL VERDICT: SURVIVES**
P02 passes all six kill tests.

**Remaining concerns:**
1. Jacobson's derivation derives the equations of motion, not initial conditions. Extending the thermodynamic identity from a constraint on dynamics to a selection principle on initial data requires a non-trivial argument.
2. Whether thermodynamic consistency of all local Rindler horizons actually excludes high-Weyl initial data (as opposed to merely constraining extreme configurations) is not demonstrated. The causal focusing argument needs a quantitative calculation.
3. The thermodynamic identity applies in the semi-classical regime (ℏ appears through the Unruh temperature). The pre-big-bang, pre-inflationary epoch may be in a regime where this approximation breaks down.

---

## P03 — Causal-Diamond Quantum-Channel Capacity Bound

**Class:** H/K (Quantum-information / Causal structures)

**T1 — CONCLUSION ENCODING:**
The primitive is: the channel capacity of causal diamonds containing the initial Cauchy surface must meet a minimum. The proposed R1 mechanism is: high-Weyl initial data → small causal diamonds (rapid geodesic focusing) → low channel capacity → violates the minimum capacity requirement. Examine the definition of "minimum capacity requirement": it is defined as "C_min for physical realizability" or alternatively "sufficient capacity for decoherence and classical structure formation to proceed."

**CRITICAL:** The phrase "sufficient capacity for classical structure formation to proceed" encodes the output. If the minimum capacity is defined as "enough for the observed universe to form," then the constraint is: initial data must be consistent with the observed universe — which is circular. This is assumption laundering.

Can it be reformulated? The raw channel capacity bound C ≤ A/4G is a theorem (from holographic bounds), not specific to cosmology. But the minimum capacity C_min requires independent specification without reference to the desired output.

**FATAL:** As defined, the lower bound C_min encodes "compatible with the observed universe" unless C_min is independently derived from a non-cosmological principle.
**Result: KILL — T1 violation: the minimum capacity requirement encodes the desired output unless C_min is independently derived.**

**OVERALL VERDICT: KILLED**
**Exact reason:** T1 — The "minimum channel capacity for physical realizability" requirement encodes the desired output (compatibility with observed classical universe) unless C_min is independently derived from non-cosmological principles. As stated in the candidate register, C_min is not independently derived; the candidate proposes it as "sufficient for decoherence and classical structure formation." This is circular — it requires the initial state to be compatible with classical structure formation, which is the conclusion.

---

## P04 — Lyapunov-Stability Restriction on Initial Data

**Class:** J/T (Nonequilibrium dynamical / Dynamical attractors)

**T1 — CONCLUSION ENCODING:**
The primitive is: Γ_stable = {(h_{ij}, K_{ij}) | λ_max[h,K] < λ_c}. The Lyapunov exponent λ_max measures exponential growth of perturbations under GR evolution. The definition does not mention homogeneity, FLRW, or low Weyl curvature directly. However, examine T6 below for the λ_c problem.
**Result: PASS**

**T2 — BACKGROUND DEPENDENCE:**
Lyapunov exponents can be defined on any dynamical system — GR evolution from arbitrary initial data (h_ij, K_ij). The definition does not require a preferred background.
**Result: PASS**

**T3 — TRIVIALITY:**
The stability requirement has independent motivation: unstable configurations cannot be prepared or maintained. However, this motivation is not airtight — cosmological initial conditions are not "prepared" by any external agent, so the argument "unstable configurations cannot be prepared" does not apply in the same way. The deeper question is whether there is a physical principle (not merely aesthetic preference) for stability. In dynamical systems, Lyapunov stability is defined, but it does not select physical states — unstable states exist physically all the time (inverted pendulum, Lagrange points L1,2,3).

**ASSESSMENT:** The stability requirement as a selection principle lacks independent physical motivation for the cosmological case. There is no known physical principle that says "the universe must have started in a Lyapunov-stable initial state." BKL oscillations describe what happens to unstable initial data — it evolves chaotically. But that does not mean it is physically excluded. The stability restriction is not derived; it is asserted.
**Result: KILL — T3 violation: stability requirement is not independently motivated as a physical selection principle for cosmological initial data. The assertion "unstable configurations cannot be physically realized" is not a derived result.**

**OVERALL VERDICT: KILLED**
**Exact reason:** T3 — The Lyapunov stability requirement lacks independent physical motivation as a cosmological selection principle. Lyapunov-unstable initial data (BKL, mixmaster) is not physically excluded in GR — it simply evolves chaotically. No independent principle requires the initial state to be stable in the Lyapunov sense. The restriction is imposed by assertion, not derived.

---

## P05 — Consistent-Histories Decoherence-Functional Restriction

**Class:** G (Quantum principles)

**T1 — CONCLUSION ENCODING:**
The primitive is: only histories for which a consistent decoherence functional exists are physically realizable. Examining the R1 mechanism: "high-Weyl configurations have rapidly oscillating quantum amplitudes that prevent decoherence." This identifies a mechanism but the primitive definition itself does not encode low Weyl as input.
**Result: PASS**

**T2 — BACKGROUND DEPENDENCE:**
The decoherence functional D(C_α, C_β) = Tr(C_α ρ_0 C_β†) requires a specification of ρ_0 — the initial quantum state of the universe. The decoherence functional cannot be defined without ρ_0. ρ_0 is precisely what needs to be determined — it encodes the initial quantum state, which in the semiclassical limit corresponds to the initial classical geometry. The condition is not evaluable on arbitrary (h_ij, K_ij) without choosing ρ_0.

**FATAL:** The decoherence functional requires the initial quantum state ρ_0 as an input. The physical initial state is what we are trying to derive. This is circular.
**Result: KILL — T2 violation: requires ρ_0 as input, which is precisely the object to be determined.**

**T3 — TRIVIALITY (applied regardless):**
Even if T2 is waived, the candidate faces the ASSUMPTION_FIREWALL violation documented in Section C: "Starting from decoherence and promoting to cosmological selection — Decoherence is a local quantum process. It does not select cosmological initial states." The firewall explicitly prohibits this failure mode.

**T4 — RENAMING:**
The ASSUMPTION_FIREWALL explicitly documents decoherence-based selection as a killed failure mode. While consistent histories is a more sophisticated framework than simple decoherence, the underlying mechanism (decoherence of histories) is functionally equivalent to what the firewall killed.
**Result: KILL — T4 violation: functionally equivalent to killed decoherence-based selection mechanism documented in ASSUMPTION_FIREWALL.**

**OVERALL VERDICT: KILLED**
**Exact reason:** T2 — requires the initial quantum state ρ_0 as input, which is the object to be determined (circular dependency). Additionally, T4 — consistent histories selection via decoherence functional is functionally equivalent to the decoherence-based selection mechanism explicitly killed in ASSUMPTION_FIREWALL §C.

---

## P06 — Constraint-Algebra Anomaly-Freedom Restriction

**Class:** C/G (Hamiltonian/phase-space / Quantum principles)

**T1 — CONCLUSION ENCODING:**
The primitive is: physical states are those annihilated by all constraints without anomaly — the kernel of the quantum constraint operators. This does not encode homogeneity, FLRW, or low Weyl curvature directly. The constraint algebra is derived from the GR action and is independent of the cosmological state.
**Result: PASS**

**T2 — BACKGROUND DEPENDENCE:**
The gravitational constraint algebra {H[N], H_i[N^i]} is defined canonically on any Cauchy surface (h_ij, π^{ij}) — it is the foundation of the ADM formalism and applies to arbitrary initial data. Anomaly-freedom is a condition on the quantum theory, not on a specific background.
**Result: PASS**

**T3 — TRIVIALITY:**
Anomaly cancellation has genuine independent motivation: anomalous gauge theories are mathematically inconsistent (the Ward identities are violated, unitarity is lost). In string theory, anomaly cancellation in the Virasoro algebra forces D=26 for bosonic strings — it is a rigorous, non-trivial constraint that the theory discovered independently of the desired outcome. Applied to the gravitational constraint algebra, anomaly freedom is a hard requirement for a consistent quantum theory.
**Result: PASS**

**T4 — RENAMING:**
Constraint-algebra anomaly-freedom is different from: no-boundary proposal (a path integral), Vilenkin (tunneling wave function), ekpyrosis (classical attractor), BKM shape dynamics (adds conformal constraint), all of which are killed. Anomaly-freedom of the quantized constraint algebra has not been applied to cosmological initial-state selection in this way before.
**Result: PASS**

**T5 — EXISTING-PHYSICS CLOSURE:**
Anomaly-freedom of the full (non-minisuperspace) gravitational constraint algebra is not established. LQC studies anomaly-free representations in minisuperspace, but the full-theory result is absent. This is an open research question, not a result of existing physics. The mechanism is new.
**Result: PASS**

**T6 — UNDEFINED MEASURE:**
No appeal to typicality, genericity, or natural measures. The constraint is a hard algebraic condition: the quantum state must lie in the kernel of all constraint operators without anomaly.
**Result: PASS**

**OVERALL VERDICT: SURVIVES**
P06 passes all six kill tests.

**Remaining concerns:**
1. Anomaly-freedom in full (non-minisuperspace) quantum GR is not achieved in any existing framework. P06 requires results that do not yet exist.
2. The connection between anomaly-freedom and geometric properties of the initial-data configuration (specifically, low Weyl curvature) is not established. The mechanism is speculative — it is not known whether the anomaly-free sector favors low-Weyl or high-Weyl configurations.
3. This is a quantum-gravity-level constraint. It requires a completed quantum theory of gravity to evaluate, which is unavailable.

---

## P07 — BMS/Asymptotic-Symmetry Vacuum Condition

**Class:** D/K (Symmetry / Causal structures)

**T1 — CONCLUSION ENCODING:**
The primitive is: initial data must be compatible with BMS-vacuum structure at asymptotic null infinity I^+. The BMS vacuum is defined by the Bondi mass aspect m(u, θ, φ) = m_0 (constant). No encoding of FLRW, homogeneity, or low Weyl curvature in the definition. But examine the proposed mechanism: the BMS vacuum excludes initial data that produces large BMS memory. Large BMS memory is generated by gravitational wave emission from inhomogeneous mass distributions. If the BMS vacuum condition selects against large gravitational wave emission, it may constrain large-scale curvature.
**Result: PASS**

**T2 — BACKGROUND DEPENDENCE:**
**FATAL:** BMS symmetry is defined at asymptotic null infinity I^+ — a structure that requires an asymptotically flat spacetime. The early universe is not asymptotically flat: cosmological spacetimes do not have a null infinity I^+ in the standard sense (the universe has a finite-lifetime past). Extension of BMS to cosmological spacetimes (de Sitter has a different conformal boundary structure) is not established.

The primitive cannot be evaluated on arbitrary cosmological (h_ij, K_ij) — it requires an asymptotically flat setting.
**Result: KILL — T2 violation: BMS is defined on asymptotically flat spacetimes; the early cosmological universe is not asymptotically flat. The primitive cannot be stated on the relevant cosmological initial-data space.**

**OVERALL VERDICT: KILLED**
**Exact reason:** T2 — BMS symmetry requires asymptotic null infinity (asymptotic flatness). The early universe is not asymptotically flat (no I^+ in de Sitter or closed FRW cosmology). The primitive cannot be defined on the relevant class of cosmological initial data without a major (unestablished) extension to non-asymptotically-flat settings.

---

## P08 — Spin-Foam Vertex-Amplitude Curvature Suppression

**Class:** R (Quantum gravity)

**T1 — CONCLUSION ENCODING:**
The primitive is: classical geometries are the dominant saddle points of the spin-foam path integral W(s,s') = ∑_σ ∏_v A_v(σ) ∏_f A_f(σ). The vertex amplitude A_v contains curvature (dihedral angles θ_f) and the stationary-phase approximation selects geometries with small curvature. The definition does not encode FLRW or homogeneity — it selects based on the stationary-phase condition of the spin-foam amplitude, which is independently derived from the Palatini action.
**Result: PASS**

**T2 — BACKGROUND DEPENDENCE:**
Spin-foam amplitudes are defined on abstract spin networks and spin foams — they are manifestly background-independent (no preferred metric is input). The boundary states |s⟩ are spin-network states, which encode quantum geometry without reference to a background.
**Result: PASS**

**T3 — TRIVIALITY:**
The EPRL vertex amplitude is not postulated for R1 — it is derived from the Palatini action discretized on a 4-simplex (Engle-Pereira-Rovelli-Livine 2008). The derivation is independent of any cosmological consideration. The amplitude suppression of large-curvature configurations follows from the stationary-phase approximation of the independently derived amplitude.
**Result: PASS**

**T4 — RENAMING:**
Spin-foam amplitude suppression is different from: CDT (different discretization scheme and physical content, P09), LQC minisuperspace (P08 is explicitly non-minisuperspace), no-boundary path integral (different formalism and different saddle). Not equivalent to any killed mechanism.
**Result: PASS**

**T5 — EXISTING-PHYSICS CLOSURE:**
The EPRL spin-foam model is a research program, not established physics. The full non-perturbative result and continuum limit are not established. This is new, not provided by standard GR, QFT, or any mechanism in the closure audit.
**Result: PASS**

**T6 — UNDEFINED MEASURE:**
The spin-foam path integral W(s,s') is a precisely defined sum with explicitly specified amplitudes (vertex amplitude A_v, face amplitude A_f). The stationary-phase argument applies in the large-j limit — this is a controlled approximation, not an appeal to undefined typicality. The Immirzi parameter γ appears but is a single free parameter, not an undefined measure.
**Result: PASS**

**OVERALL VERDICT: SURVIVES**
P08 passes all six kill tests.

**Remaining concerns:**
1. All spin-foam calculations are in discrete, simplicial geometries. The continuum limit — where connection to classical GR initial data can be made — is not rigorously established.
2. The large-j (semiclassical) approximation is required for the saddle-point suppression argument. At Planck scale, this approximation fails — j ~ 1 is the relevant regime for cosmological initial conditions.
3. The Immirzi parameter γ is a free parameter. If the curvature suppression depends sensitively on γ, the mechanism has an underdetermined parameter.
4. The connection between spin-foam saddle points and low Weyl curvature specifically (as opposed to low total curvature) needs to be made explicit. The stationary-phase argument suppresses high total curvature; whether it specifically selects near-vanishing Weyl curvature is not established.

---

## P09 — CDT de-Sitter-Phase Dominance

**Class:** R (Quantum gravity)

**T1 — CONCLUSION ENCODING:**
The primitive is: in CDT, phase C dominates the path integral, and the ground state in phase C is de Sitter-like. The definition invokes "de Sitter-like geometry" as the selected state. De Sitter geometry is maximally symmetric — it has low Weyl curvature. Examine: is "de Sitter geometry" encoding the conclusion?

**FATAL ANALYSIS:** The CDT phase-C result is that the ground state is an S^3 × R topology with a de Sitter-like volume profile. De Sitter spacetime is conformally flat (Weyl = 0). By declaring that CDT selects "de Sitter-like" geometries, P09 is asserting that CDT selects low-Weyl initial states — because de Sitter is low-Weyl by definition (conformally flat, Weyl = 0 exactly). The question is whether this is a derived result or an encoded input.

The CDT phase-C result is a computational/numerical finding — the de Sitter geometry emerges from the lattice simulation. It is not imposed as an input. However, the topology is fixed (S^3 × R) from the outset in CDT simulations — this is a topological input. Given this topological input, the dominant geometry is de Sitter-like.

**The mechanism relies on:** CDT topology (S^3) + phase-C coupling constants → de Sitter ground state.
- "de Sitter ground state" = low Weyl (since de Sitter is conformally flat)
- The topology S^3 is an input (T1 concern: is a smooth S^3 topology itself an encoded assumption?)
- The coupling constants (κ_0, κ_4, Δ) being in the phase-C region is a free-parameter input

**T1 result:** The primitive does not directly encode FLRW or homogeneity. However, it does rely on the topological input (S^3) and phase-C coupling, which are not derived from first principles. The phase-C structure is a computational finding, not a derivation. The "de Sitter-like geometry" output encodes smooth initial conditions if the topology is assumed. This is not a strict T1 kill (de Sitter-like is not assumed as input; it emerges from the CDT simulation), but it relies on T3-level inputs (phase-C region, S^3 topology).
**Result: BORDERLINE PASS — the de Sitter geometry is not assumed as input; it emerges. But this emergence depends on inputs (topology, phase-C coupling) that are not derived.**

**T2 — BACKGROUND DEPENDENCE:**
CDT simulations are performed with fixed causal structure and S^3 spatial topology. The initial-data space is restricted from the outset. The mechanism cannot be evaluated on "arbitrary (h_ij, K_ij)" — the CDT path integral is a sum over simplicial causal complexes with fixed topology, not a computation on arbitrary continuous GR initial data.
**Result: KILL — T2 violation: CDT requires fixed causal structure and spatial topology (S^3). It cannot be defined on arbitrary cosmological initial data with general topology.**

**OVERALL VERDICT: KILLED**
**Exact reason:** T2 — CDT requires the spatial topology to be fixed (S^3) and the causal structure to be of simplicial form. The mechanism cannot be stated or evaluated on arbitrary (h_ij, K_ij) with general spatial topology. This is a background dependence — the topological background S^3 is assumed.

---

## P10 — Pre-Bounce Viscous Dissipation Attractor

**Class:** J/V (Nonequilibrium dynamical / New matter sectors)

**T1 — CONCLUSION ENCODING:**
The primitive is: pre-bounce dissipation via shear viscosity η damps anisotropies (Weyl curvature ~ shear) exponentially if η/s exceeds a threshold. The definition does not directly encode homogeneity or low Weyl — it proposes a dynamical mechanism. However, examine the mechanism: the attractor state is "FRW solution (zero shear, zero Weyl)." While this is the output (not the input), the mechanism requires a specific viscous matter sector with specific η/s. That sector is assumed as an input.
**Result: PASS (output is low Weyl, not input)**

**T2 — BACKGROUND DEPENDENCE:**
Viscous GR cosmology is defined in any spacetime with a matter sector satisfying imperfect-fluid equations. The shear tensor σ_μν is defined covariantly. The bulk/shear viscosity damping equations apply on any Bianchi-type background. In principle, the viscous dissipation equation dσ_{μν}/dt ~ -η/ρ · σ_{μν} can be evaluated on arbitrary (h_ij, K_ij). However, the result that η damps Weyl curvature effectively (before bounce/singularity) requires a contraction phase — the mechanism is defined in the context of a contracting phase (θ < 0). It is not a restriction on all initial data; it is a claim about the dynamics in a contracting phase.
**Result: PASS — the formalism is covariant and applicable to general initial data in the context of contraction.**

**T3 — TRIVIALITY:**
The viscous damping mechanism is not postulated for R1 — viscous cosmology has been studied since Weinberg (1971) and Misner (1968) for independent reasons (isotropization, galaxy formation). The KSS bound (η/s ≥ ℏ/4πk_B) is independently derived from AdS/CFT for strongly coupled plasma. The mechanism has genuine independent motivation.
**Result: PASS**

**T4 — RENAMING:**
P10 is structurally similar to the ekpyrotic attractor (P01 mechanism class T/J) — both are dynamical attractors in a contracting phase that drive toward low Weyl. But P10's attractor mechanism is shear viscosity rather than a scalar field potential. This is a distinct physical mechanism, not a renaming.
**Result: PASS**

**T5 — EXISTING-PHYSICS CLOSURE:**
Misner's chaotic cosmology (1968) proposed viscous damping (neutrino viscosity) as an isotropization mechanism — but this was for radiation-dominated post-bang cosmology, not the pre-bang epoch. The specific application to pre-bounce viscous damping as a selection mechanism for R1 is new. However, the mechanism is built entirely from standard GR + classical fluid dynamics. It is "existing physics" in the sense that all ingredients are known.

**CRITICAL:** The mechanism does not claim new physics — it assembles known physics. But does existing physics already provide this mechanism? No existing analysis has demonstrated that viscous cosmology in the pre-bounce phase provides an attractor with a wide enough basin to close R1. The claim is new, even though the tools are standard.
**Result: PASS (the mechanism is new even though the tools are standard)**

**T6 — UNDEFINED MEASURE:**
**FATAL:** The candidate claims the mechanism works "over a wide basin" of initial conditions. What defines "wide"? The candidate states: "Over a long enough contraction with sufficient η/s, the shear is driven to zero." This requires: (a) a contraction phase of sufficient duration, (b) η/s above a threshold. Neither the basin size nor the required η/s are derived — they are free parameters. The claim that the mechanism "works from a wide basin" is an appeal to genericity without a defined measure.
**Result: KILL — T6 violation: the wide-basin claim is an undefined typicality appeal. The contraction duration and η/s threshold are free parameters; whether "most" initial data is in the basin is not established without a measure.**

**OVERALL VERDICT: KILLED**
**Exact reason:** T6 — The wide-basin attractor claim appeals to "generic" or "wide" initial conditions without defining a measure on the initial-data space. The key parameters (η/s threshold, required contraction duration) are free. Without a derived measure, the claim that the mechanism works "from a wide basin" is undefined genericity.

---

## P11 — Tomita-Takesaki Modular-Flow Geometric Restriction

**Class:** M/H (Algebraic / Quantum-information)

**T1 — CONCLUSION ENCODING:**
The primitive is: physical initial states are those for which the modular Hamiltonian K_Σ generates a geometric flow (corresponding to a Killing or conformal Killing vector). No direct encoding of FLRW, homogeneity, or low Weyl. However, examine the mechanism: "high-Weyl initial data corresponds to quantum states with highly non-geometric modular structure." This assumes a connection between Weyl curvature and non-geometric modular flow — is this derived or assumed?

The connection between geometric modular flow and smooth spacetime is established via the Bisognano-Wichmann theorem (for Rindler wedge in Minkowski) and Hislop-Longo (for diamonds in conformal QFT). But these results apply in specific backgrounds (Minkowski, de Sitter). Extension to general geometries is not established.
**Result: PASS (the definition itself does not encode the conclusion, even if the connection to Weyl curvature is not established)**

**T2 — BACKGROUND DEPENDENCE:**
**FATAL:** The geometric modular flow condition is established in specific backgrounds:
- Bisognano-Wichmann: Minkowski spacetime, Rindler wedge
- Hislop-Longo: de Sitter, conformal field theories

For a general Riemannian 3-manifold (h_ij, K_ij), the modular Hamiltonian K_Σ is not computable without knowing the quantum state and the field theory on the manifold. The condition "K_Σ generates a geometric flow" cannot be evaluated on arbitrary (h_ij, K_ij) without specifying the quantum state ρ_Σ (which is part of what we're trying to determine) and the quantum theory.

More fundamentally: the modular Hamiltonian is K = -log ρ_Σ where ρ_Σ is the reduced density matrix of the quantum state on Σ. Without knowing ρ_Σ, K is undefined. ρ_Σ depends on the full quantum state of the universe — precisely what R1 asks about.
**Result: KILL — T2 violation: requires the quantum state ρ_Σ to define the modular Hamiltonian; this quantum state is the object under investigation (circular dependency). The condition cannot be evaluated on bare classical initial data (h_ij, K_ij).**

**OVERALL VERDICT: KILLED**
**Exact reason:** T2 — The modular Hamiltonian K_Σ = -log ρ_Σ requires the quantum state ρ_Σ as input. The quantum state on the initial Cauchy surface is precisely what needs to be determined. This creates a circular dependency: the primitive requires the initial quantum state to be defined, which is the object the primitive is supposed to select.

---

## P12 — Second-Law-Constrained Contraction Phase Restriction

**Class:** F/I (Conservation laws / Entropic)

**T1 — CONCLUSION ENCODING:**
The primitive is: initial Weyl curvature must be below the level at which backward evolution would violate the GSL. The definition directly involves Weyl curvature (W²) as a gravitational entropy proxy. **CRITICAL:** Using W² as a gravitational entropy proxy is explicitly listed in the ONTOLOGY_PROHIBITION §C as a "prohibited equivalence": "Gravitational entropy = Weyl curvature (Penrose) — Contested in literature; counterexamples published; not a theorem." The candidate acknowledges this: "S_grav ~ W² is not a rigorously defined gravitational entropy (Penrose's proposal is contested)."

Crucially, the candidate also says "This candidate must not assume the Weyl=gravitational entropy identification; it must derive the connection from the GSL." But the definition AS STATED uses S_grav ~ W² as the primitive definition. This encodes the Penrose identification as an input.

Can it be reformulated to not use S_grav ~ W²? The mechanism would then need a different definition of gravitational entropy — one that is rigorously defined. Without that, the primitive is undefined or uses a prohibited proxy.

**FATAL:** The mechanism as stated defines S_grav ~ W² — using the contested Penrose gravitational entropy identification. This is a prohibited input per ONTOLOGY_PROHIBITION §C.
**Result: KILL — T1 violation: the primitive definition uses S_grav ~ W² (the Penrose Weyl-entropy identification), which is explicitly listed as a prohibited equivalence in ONTOLOGY_PROHIBITION §C. It cannot be used as input.**

**OVERALL VERDICT: KILLED**
**Exact reason:** T1 — The primitive requires defining S_grav ~ W² (gravitational entropy proportional to Weyl curvature squared), which is the Penrose Weyl curvature hypothesis — explicitly listed as a prohibited equivalence in ONTOLOGY_PROHIBITION §C. This identification is contested in the literature (counterexamples exist) and is not a theorem. Using it as input encodes the conclusion: requiring S_grav to be small via the GSL is equivalent to requiring W² to be small, which is the conclusion we are trying to derive.

---

## P13 — EFT-Validity Domain Restriction

**Class:** G/O (Quantum / Renormalization)

**T1 — CONCLUSION ENCODING:**
The primitive is: Γ_EFT = {(h_ij, K_ij) | R_max[h,K] ≤ M_UV²}. This does not encode homogeneity, FLRW, or low Weyl directly — it restricts total curvature to be below the UV cutoff. Low Weyl curvature is a stronger condition than R_max ≤ M_UV².
**Result: PASS**

**T2 — BACKGROUND DEPENDENCE:**
The EFT validity condition R_max ≤ M_UV² is covariant and can be evaluated on any (h_ij, K_ij). The curvature eigenvalue R_max is a coordinate-independent quantity (related to eigenvalues of the Riemann tensor). No background is required.
**Result: PASS**

**T3 — TRIVIALITY:**
EFT validity is independently motivated: it is a necessary condition for any EFT description to be applicable. When R^{1/2} ~ M_UV, the EFT breaks down and new physics is required. This is a universal constraint from any UV-complete theory.
**Result: PASS**

**T4 — RENAMING:**
EFT validity restriction is different from: no-boundary proposal, Vilenkin, ekpyrosis, or any killed mechanism. It is a standard physical requirement, not a new proposal.
**Result: PASS**

**T5 — EXISTING-PHYSICS CLOSURE:**
**FATAL:** EFT validity (R_max ≤ M_UV²) is indeed provided by existing physics. Every UV-complete theory of gravity (string theory, LQG, asymptotic safety) imposes that the EFT description breaks down at the UV cutoff. This is not a new selection principle — it is a standard, universally acknowledged requirement. The candidate's own register acknowledges: "This is a consequence of any UV-complete theory." As a selection principle, it is weaker than required for R1 (it restricts to sub-Planckian curvature, not specifically to low Weyl curvature). As a necessary condition, it is already provided by existing physics.

Furthermore, the candidate's register explicitly states: "This is a necessary condition, not a sufficient selection principle." A necessary but insufficient condition that is already provided by existing physics does not advance the problem.
**Result: KILL — T5 violation: EFT validity (R_max ≤ M_UV²) is already provided by every existing UV-complete theory of gravity. It is a necessary but not sufficient condition, and it does not specifically select the low-Weyl sector of the initial-data space.**

**OVERALL VERDICT: KILLED**
**Exact reason:** T5 — The EFT validity restriction (R_max ≤ M_UV²) is already provided by all existing UV-complete theories of gravity (string theory, LQG, asymptotic safety). It is a standard necessary condition, not a new selection principle. Moreover, it does not specifically restrict to the low-Weyl sector — it only requires sub-Planckian total curvature, which allows moderately high-Weyl initial data.

---

## P14 — Stochastic-Gravitational-Wave Coherence Constraint

**Class:** F (Conservation laws / Observational)

**T1 — CONCLUSION ENCODING:**
The primitive is: Γ_coherent = {(h_ij, K_ij) | Ω_{GW}(f) ≤ Ω_{GW}^{obs}(f) for all f}. This uses observational constraints directly. "Ω_{GW}^{obs}" encodes actual measurements of the SGWB spectrum.

**FATAL:** This is an observational constraint — it requires the initial state to be consistent with observed SGWB measurements. But the observed SGWB reflects the universe as it evolved, including all post-big-bang processing (inflation, reheating, etc.). Using current observations as a constraint on the initial data encodes the entire history of the universe as a premise. Moreover, the question of which initial conditions are consistent with observations is precisely the question R1 asks — this is circular.
**Result: KILL — T1 violation: the primitive encodes observed SGWB constraints, which are outcomes of the cosmological evolution we are trying to derive. This is circular — it requires the initial data to be consistent with the observed universe, which is the conclusion.**

**T3 — TRIVIALITY (also applicable):**
Requiring consistency with observations is not a derived physical principle — it is a boundary condition imposed on the problem. It is a consistency check, not a selection mechanism.
**Result: KILL — T3 violation: requiring consistency with observations is an empirical boundary condition, not a derived dynamical selection principle.**

**OVERALL VERDICT: KILLED**
**Exact reason:** T1 + T3 — The primitive requires the initial state to be consistent with observed SGWB measurements. This is circular (observed outcomes are being used to constrain the initial state that produces them) and it is an empirical boundary condition rather than a derived selection principle.

---

## P15 — Unitarity-Preserving Phase-Space Restriction

**Class:** G (Quantum principles)

**T1 — CONCLUSION ENCODING:**
The primitive is: Γ_unitary = U†(Γ_final) — the set of initial states compatible with unitarity, given a final state Γ_final. The definition does not encode homogeneity or FLRW. But it requires specifying Γ_final (the final state of the universe).

**CRITICAL:** The R1 mechanism states: "if the late-time final state is approximately thermal with specific Page-curve properties, the initial state must have been in a specific sector (low entropy, small Weyl)." This assumes the final state has "Page-curve properties" — i.e., it assumes the observed cosmological evolution (thermalization, entropy increase) as input to the final state. This is circular: the final state encodes the cosmological evolution we are trying to derive.

Furthermore: "Unitarity constrains the initial state by the final state. If the final state of the universe is approximately thermal..." — this requires specifying the final state to constrain the initial state. The final state is unknown and itself requires derivation.
**Result: KILL — T1 violation: requires specifying the final state Γ_final, which must encode the desired cosmological evolution; this is circular assumption laundering through the final condition rather than the initial condition.**

**T3 — TRIVIALITY (also applicable):**
The candidate's own register states: "Final-state projections are highly speculative and not established physics." A speculative, unestablished final-state condition is an arbitrary constraint — it is not independently motivated.
**Result: KILL — T3 violation: final-state projection is not established physics; it is an arbitrary constraint lacking independent motivation.**

**OVERALL VERDICT: KILLED**
**Exact reason:** T1 + T3 — The primitive requires specifying the final state Γ_final, which must encode the desired cosmological evolution to produce the claimed restriction on initial states. This is assumption laundering through the final condition. The final-state projection mechanism is also not established physics.

---

## P16 — Non-Commutative Geometry Spectral-Triple Restriction

**Class:** M (Algebraic)

**T1 — CONCLUSION ENCODING:**
The primitive is: physical initial data corresponds to spectral triples where S[D] = Tr f(D/Λ) is extremized or satisfies a specific eigenvalue bound. The definition does not encode homogeneity, FLRW, or low Weyl directly.
**Result: PASS**

**T2 — BACKGROUND DEPENDENCE:**
A spectral triple (A, H, D) can be defined for any Riemannian manifold (h_ij, φ) where φ is a spinor field. The Dirac operator D is constructed from the metric and spin connection — both of which are derivable from (h_ij). In principle, the spectral action can be evaluated on any 3-manifold with a spin structure.
**Result: PASS (with caveat: requires a spin structure — topological assumption)**

**T3 — TRIVIALITY:**
The spectral action principle (Connes-Chamseddine 1997) is independently motivated by deriving the Standard Model + GR from a purely algebraic input. It is not postulated for R1. The motivation is unification, not cosmological selection.
**Result: PASS**

**T4 — RENAMING:**
The spectral action is not mathematically equivalent to any killed mechanism. It is not a holographic bound, not a no-boundary condition, not an entropy functional in the standard sense. It is a distinct mathematical structure.
**Result: PASS**

**T5 — EXISTING-PHYSICS CLOSURE:**
The spectral action is not established as a complete theory of quantum gravity. Its application to cosmological initial-state selection is new. The candidate's register acknowledges: "The spectral action selects the equations of motion, not specific solutions." This is the critical issue.

**FATAL:** The candidate's register explicitly acknowledges the key objection: "The spectral action selects the equations of motion (equations of motion = Einstein's equations in the classical limit), not specific solutions. It does not select initial data." This is correct. The spectral action principle ∂S/∂D = 0 yields the equations of motion (Einstein's equations in the classical limit plus Standard Model equations). It does not select among solutions to these equations. Initial data is a space of solutions — the spectral action does not discriminate between different initial data satisfying the same equations.
**Result: KILL — T5 violation (and T3): the spectral action is a variational principle that yields equations of motion, not initial data. Using it as an initial-state selection principle requires a further step that is not established. The mechanism does not exist in current physics.**

**T3 (re-application):** The extension from "spectral action selects equations of motion" to "spectral action selects initial data" is not independently motivated — it is an assumed step.

**OVERALL VERDICT: KILLED**
**Exact reason:** T5/T3 — The spectral action principle selects equations of motion (Einstein's equations + Standard Model in the classical limit), not specific initial data. The candidate register explicitly acknowledges this. There is no mechanism from the spectral action that discriminates between different initial-data configurations satisfying the same equations.

---

## P17 — Superradiant-Instability Exclusion

**Class:** T (Dynamical attractors)

**T1 — CONCLUSION ENCODING:**
The primitive is: Γ_stable^{sr} = {(h_ij, K_ij) | no superradiant instability exists for the evolved spacetime}. The definition does not encode FLRW, homogeneity, or low Weyl directly. However, the connection to the magnetic Weyl tensor B_ij is proposed but not derived.
**Result: PASS**

**T2 — BACKGROUND DEPENDENCE:**
**FATAL:** Superradiant instability requires rotating black holes (Kerr metric specifically) and reflective boundary conditions (in an AdS background or a compact Cauchy surface). Neither condition holds generically in a cosmological setting. Specifically: (a) The early universe does not consist of rotating black holes. (b) There is no reflective boundary in the early universe. (c) The connection between cosmological Weyl curvature (which includes electric and magnetic parts) and the specific instability of Kerr black holes with reflective boundaries requires a mathematical argument that has not been made.

The stability condition as defined is specific to rotating-black-hole spacetimes with reflective boundaries — not to arbitrary cosmological initial data (h_ij, K_ij).
**Result: KILL — T2 violation: superradiant instability requires Kerr black holes and reflective boundaries — structures absent from cosmological initial data. The primitive cannot be defined on general cosmological (h_ij, K_ij).**

**OVERALL VERDICT: KILLED**
**Exact reason:** T2 — Superradiant instability is specific to rotating black holes with reflective boundaries. This structure is absent from general cosmological initial data. The primitive cannot be defined or evaluated on the relevant cosmological initial-data space.

---

## P18 — Null-Geodesic-Completeness Restriction

**Class:** K (Causal structures)

**T1 — CONCLUSION ENCODING:**
The primitive is: Γ_complete = {(h_ij, K_ij) | backward-evolved spacetime is null-geodesically complete (no trapped surfaces in the past)}. No encoding of FLRW, homogeneity, or low Weyl directly. However, the mechanism is: "initial data with large Weyl curvature may have trapped surfaces in the backward direction."
**Result: PASS**

**T2 — BACKGROUND DEPENDENCE:**
Null geodesic completeness and the absence of trapped surfaces are covariant, background-independent conditions on a spacetime evolved from (h_ij, K_ij). They can be evaluated on any GR initial data. No preferred background.
**Result: PASS**

**T3 — TRIVIALITY:**
The absence of a past singularity (or a resolved past singularity) is a standard assumption in cosmology. The Penrose theorem provides the rigorous connection between trapped surfaces and geodesic incompleteness. However, the condition "no trapped surfaces in the past" is not independently motivated as a physical selection principle — it is what needs to be explained. The Borde-Guth-Vilenkin theorem (2003) shows that any past-eternal inflationary spacetime must have been past incomplete — but this does not provide a derivation of why the initial state avoided trapped surfaces.

**CRITICAL:** The candidate's register states: "This formalizes the ekpyrotic gap condition but does not close it — it restates the requirement rather than deriving it from an independent principle." This is the decisive assessment. P18 restates R1 in causal language without providing a new explanatory mechanism.
**Result: KILL — T3 violation: the null-geodesic-completeness condition restates the ekpyrotic gap condition (why was the pre-contraction state below the black-hole-formation threshold?) without deriving it from an independent principle. It formalizes the problem but does not solve it.**

**OVERALL VERDICT: KILLED**
**Exact reason:** T3 — The null-geodesic-completeness condition reformulates R1 in causal language ("no trapped surfaces in the past") but provides no independent derivation of why this condition holds. As explicitly acknowledged in the candidate register, it "formalizes the ekpyrotic gap condition but does not close it." A primitive that restates the residual without deriving it is not a primitive — it is a description of the problem.

---

## P19 — Scale-Factor Duality Restriction (String Cosmology)

**Class:** V/D (New matter sectors / Symmetry)

**T1 — CONCLUSION ENCODING:**
The primitive is: initial data must lie in the duality-invariant sector under a(t) → 1/a(t). The R1 mechanism: since the post-big-bang state is smooth (observed), and the duality maps it to the pre-big-bang state, the pre-big-bang state is also constrained. **FATAL:** This requires the post-big-bang state to be smooth — which is the observed smoothness we are trying to derive. The duality argument is: smooth post-bang → smooth pre-bang (via duality). But it assumes the post-bang is smooth. This is circular — the smoothness of the post-bang state is part of what requires explanation.

More precisely: the duality maps the specific post-big-bang trajectory to a specific pre-big-bang trajectory. If the post-bang state is smooth (known from observation), the duality predicts the pre-bang state. But the smoothness of the post-bang state is not derived from the primitive — it is observed. So P19 says: "we observe smoothness after the bang, therefore (by duality) there was smoothness before the bang." This is retroactive reasoning using the observation as input — not a derivation of why the universe was smooth.
**Result: KILL — T1 violation: the duality argument requires the smooth post-big-bang state as input; this is the observation we are trying to explain, not an independent input.**

**T2 (also applicable):**
Scale-factor duality is derived for homogeneous FRW backgrounds (the Gasperini-Veneziano action is an FRW truncation). Extension to full inhomogeneous GR initial data is not established.
**Result: KILL — T2 violation: scale-factor duality is derived for FRW backgrounds, not for general (h_ij, K_ij).**

**OVERALL VERDICT: KILLED**
**Exact reason:** T1 + T2 — (T1) The duality argument requires the observed smooth post-big-bang state as input, making it circular. (T2) Scale-factor duality is derived for the homogeneous FRW setting — extension to arbitrary GR initial data is not established.

---

## P20 — Topological Censorship Restriction

**Class:** L (Topological)

**T1 — CONCLUSION ENCODING:**
No encoding of FLRW, homogeneity, or low Weyl in the topological censorship definition.
**Result: PASS**

**T2 — BACKGROUND DEPENDENCE:**
Topological censorship applies to asymptotically flat or asymptotically AdS spacetimes. The early cosmological universe is neither. The theorem requires a simply connected conformal boundary — a structure absent from compact cosmological spacetimes or spacetimes with compact Cauchy surfaces.
**Result: KILL — T2 violation: topological censorship requires asymptotically flat or AdS spacetimes. The early cosmological universe lacks the required asymptotic structure.**

**T3 (also applicable):**
The candidate's own register acknowledges: "Simple topology (S^3) does not imply low Weyl curvature. A Bianchi IX model on S^3 can have high Weyl curvature." A mechanism that restricts topology but not curvature cannot close R1 (which is about suppression of Weyl curvature, not about topological simplicity).
**Result: KILL — T3: the mechanism restricts topology, not Weyl curvature. Even if topological simplicity is established, it does not imply low Weyl curvature — the two are independent.**

**OVERALL VERDICT: KILLED**
**Exact reason:** T2 + T3 — (T2) Topological censorship requires asymptotic flatness/AdS, which is absent in the early cosmological setting. (T3) Even if applicable, topology restriction does not imply Weyl curvature restriction — the two degrees of freedom are independent.

---

## P21 — QEC Bulk-Reconstruction Restriction

**Class:** H/P (Quantum-information / Holographic)

**T4 — RENAMING:**
**FATAL:** The QEC holographic approach is a variant of holographic cosmology — a class that was fully killed in the closure audit (FINAL_GATE4_STATUS.md, Mechanism 7, 04_RESIDUAL_PROBLEM/CLOSURE_EXHAUSTION_AUDIT.md). The candidate register itself acknowledges: "This is essentially another holographic approach — the class P (holographic) was killed in the closure audit." The QEC framework (Almheiri-Dong-Harlow 2015) is an AdS/CFT-specific construction. All AdS/CFT-based approaches are killed: the early universe is not AdS. The candidate's own register acknowledges this under "Known objections."
**Result: KILL — T4 violation: mathematically equivalent to (a variant of) holographic cosmology, which was fully audited and killed in CLOSURE_EXHAUSTION_AUDIT.md Mechanism 7.**

**T2 (also applicable):**
QEC holography requires AdS geometry and a boundary theory — both absent from cosmological (de Sitter / flat) spacetimes.
**Result: KILL — T2 violation: requires AdS geometry and holographic boundary theory.**

**OVERALL VERDICT: KILLED**
**Exact reason:** T4 + T2 — QEC bulk-reconstruction is a variant of holographic cosmology, which was killed in the closure exhaustion audit. It additionally requires AdS geometry (T2 violation), absent from the early cosmological setting.

---

## P22 — Quantum-Darwinism Redundancy Condition

**Class:** H/G (Quantum-information / Quantum)

**T4 — RENAMING:**
The candidate register acknowledges: "This is a restatement of decoherence in a different language — decoherence is killed as a selection mechanism." Quantum Darwinism explains how classical objectivity emerges through environmental monitoring — it is a refined version of einselection/decoherence. The ASSUMPTION_FIREWALL §C explicitly kills decoherence-based selection: "Starting from decoherence and promoting to cosmological selection — Decoherence is a local quantum process. It does not select cosmological initial states." Quantum Darwinism shares the same fundamental mechanism (environmental interaction → classical stability) and the same fatal flaw (requires a pre-existing quantum state and environment).
**Result: KILL — T4 violation: quantum Darwinism is a restatement of decoherence-based selection, which is explicitly killed in ASSUMPTION_FIREWALL §C.**

**T3 (also applicable):**
The candidate's register: "Quantum Darwinism explains how classicality is perceived by observers, not which states are physically realized. It requires a pre-existing quantum state." This is a fundamental flaw — the mechanism explains observer perception of classicality, not physical selection of the initial state.
**Result: KILL — T3: quantum Darwinism selects perceived-classical states, not physically realized initial states; applying it to cosmological initial-state selection lacks independent motivation.**

**OVERALL VERDICT: KILLED**
**Exact reason:** T4 + T3 — Quantum Darwinism is a restatement of decoherence-based selection (killed in ASSUMPTION_FIREWALL §C). It explains perceived classicality, not physical selection of the initial state, and requires a pre-existing quantum state and environment.

---

## P23 — Weyl-Tensor Petrov-Type Stability Restriction

**Class:** A (Geometric)

**T1 — CONCLUSION ENCODING:**
**FATAL:** The primitive is: Γ_Petrov = {(h_ij, K_ij) | the Weyl tensor is algebraically special (Type D, N, or O)}. Type O means C_{αβγδ} = 0. Requiring Type O as a restriction is literally "Weyl = 0" stated in Petrov classification language. This is the desired conclusion, stated as input. Even requiring Type D is a restriction on the Weyl tensor — it says the Weyl tensor has a specific algebraic structure, which is a constraint on the Weyl tensor's magnitude and form.

The candidate register acknowledges this: "Requiring Type O is equivalent to requiring low Weyl — assumption laundering."

Can it be reformulated? The Goldberg-Sachs theorem connects algebraic specialness to shear-free geodesic null congruences. But requiring shear-free null congruences is another way of requiring smooth geometry — the same conclusion encoded differently.
**Result: KILL — T1 violation: requiring algebraically special Petrov type (especially Type O = Weyl=0) directly encodes the desired conclusion as input. The candidate register explicitly acknowledges this is assumption laundering.**

**OVERALL VERDICT: KILLED**
**Exact reason:** T1 — Requiring algebraically special Petrov type encodes the desired low-Weyl (or zero-Weyl for Type O) condition as input. Petrov type is a classification of the Weyl tensor's algebraic structure — restricting to special Petrov types is a restriction on the Weyl tensor, not an independent principle. The candidate register explicitly acknowledges this is assumption laundering.

---

## P24 — Holographic-Complexity Bound

**Class:** H/P (Quantum-information / Holographic)

**T4 — RENAMING:**
Like P21, this is a holographic mechanism — the complexity conjectures (Susskind 2014, Brown et al. 2016) are formulated in AdS/CFT. All holographic approaches were killed in the closure audit. The candidate register acknowledges: "This is essentially a holographic mechanism — class P is killed."
**Result: KILL — T4 violation: holographic-complexity bound is a variant of holographic cosmology (class P), which was fully killed in the closure exhaustion audit.**

**T2 (also applicable):**
Holographic complexity conjectures are formulated in AdS geometries (AdS-Schwarzschild). The early universe is not AdS.
**Result: KILL — T2 violation: formulated in AdS geometry, absent from cosmological setting.**

**OVERALL VERDICT: KILLED**
**Exact reason:** T4 + T2 — Holographic complexity is a variant of holographic cosmology (class P, fully killed). It additionally requires AdS geometry, which is absent from the early cosmological setting.

---

## P25 — Gravitational Decoherence Pointer-State Restriction

**Class:** G (Quantum principles)

**T4 — RENAMING:**
The candidate register explicitly acknowledges: "This is another decoherence-based approach — decoherence is killed as a selection mechanism." The Diósi-Penrose gravitational decoherence model proposes that quantum superpositions of mass distributions collapse due to gravitational interaction — this is a decoherence mechanism. The ASSUMPTION_FIREWALL §C explicitly kills decoherence-based selection. Gravitational decoherence pointer-state selection is a specific instance of decoherence-based selection.
**Result: KILL — T4 violation: gravitational decoherence pointer-state restriction is an instance of decoherence-based selection, explicitly killed in ASSUMPTION_FIREWALL §C.**

**T3 (also applicable):**
The candidate register: "Gravitational decoherence selects classical states from quantum superpositions, but does not select which classical state is realized." This is the decisive objection — decoherence selects pointer states (classically stable states) but does not determine which pointer state is actually occupied. For cosmological initial states, this means decoherence explains why the geometry is classical but not why it is smooth and low-Weyl.
**Result: KILL — T3: gravitational decoherence selects pointer states from superpositions but does not select which pointer state is realized. It does not address the cosmological initial-state problem.**

**OVERALL VERDICT: KILLED**
**Exact reason:** T4 + T3 — Gravitational decoherence pointer-state selection is an instance of the killed decoherence-based selection mechanism (ASSUMPTION_FIREWALL §C). It selects classical states from quantum superpositions but does not select which classical state (smooth vs. inhomogeneous) is realized — leaving R1 unaddressed.

---

## KILL LOG SUMMARY TABLE

| ID | Candidate | T1 | T2 | T3 | T4 | T5 | T6 | Verdict |
|----|-----------|----|----|----|----|----|----|---------|
| P01 | UV Fixed-Point Restriction (Asymptotic Safety) | PASS | PASS | PASS | PASS | PASS | PASS | **SURVIVES** |
| P02 | Local-Rindler Thermodynamic Constraint | PASS | PASS | PASS | PASS | PASS | PASS | **SURVIVES** |
| P03 | Causal-Diamond Channel Capacity | KILL | — | — | — | — | — | KILLED |
| P04 | Lyapunov-Stability Restriction | PASS | PASS | KILL | — | — | — | KILLED |
| P05 | Consistent-Histories Decoherence-Functional | PASS | KILL | — | KILL | — | — | KILLED |
| P06 | Constraint-Algebra Anomaly-Freedom | PASS | PASS | PASS | PASS | PASS | PASS | **SURVIVES** |
| P07 | BMS Vacuum Condition | PASS | KILL | — | — | — | — | KILLED |
| P08 | Spin-Foam Vertex-Amplitude Suppression | PASS | PASS | PASS | PASS | PASS | PASS | **SURVIVES** |
| P09 | CDT de-Sitter Phase Dominance | PASS | KILL | — | — | — | — | KILLED |
| P10 | Pre-Bounce Viscous Dissipation Attractor | PASS | PASS | PASS | PASS | PASS | KILL | KILLED |
| P11 | Modular-Flow Geometric Restriction | PASS | KILL | — | — | — | — | KILLED |
| P12 | Second-Law Contraction Restriction (W²) | KILL | — | — | — | — | — | KILLED |
| P13 | EFT-Validity Domain Restriction | PASS | PASS | PASS | PASS | KILL | — | KILLED |
| P14 | Stochastic-GW Coherence Constraint | KILL | — | KILL | — | — | — | KILLED |
| P15 | Unitarity/Page-Curve Final-State Projection | KILL | — | KILL | — | — | — | KILLED |
| P16 | Non-Commutative Geometry Spectral-Triple | PASS | PASS | PASS | PASS | KILL | — | KILLED |
| P17 | Superradiant-Instability Exclusion | PASS | KILL | — | — | — | — | KILLED |
| P18 | Null-Geodesic-Completeness Restriction | PASS | PASS | KILL | — | — | — | KILLED |
| P19 | Scale-Factor Duality Restriction | KILL | KILL | — | — | — | — | KILLED |
| P20 | Topological Censorship Restriction | PASS | KILL | KILL | — | — | — | KILLED |
| P21 | QEC Bulk-Reconstruction Restriction | — | KILL | — | KILL | — | — | KILLED |
| P22 | Quantum-Darwinism Redundancy Condition | — | — | KILL | KILL | — | — | KILLED |
| P23 | Weyl-Tensor Petrov-Type Restriction | KILL | — | — | — | — | — | KILLED |
| P24 | Holographic-Complexity Bound | — | KILL | — | KILL | — | — | KILLED |
| P25 | Gravitational Decoherence Pointer-State | — | — | KILL | KILL | — | — | KILLED |

---

## KILL TALLY

- **Total candidates:** 25
- **Killed:** 21
- **Surviving:** 4

---

## SURVIVING CANDIDATES

The following candidates passed all 6 kill tests and proceed to Stage 4 (Adversarial Initial Data):

| ID | Name | Class | Kill Tests Passed | Remaining Concerns |
|----|------|-------|-------------------|--------------------|
| **P01** | UV Fixed-Point Gravitational-Coupling Restriction | O (Asymptotic Safety) | T1–T6 all PASS | Map from theory-space restriction to initial-data restriction not established; whether UV critical manifold selects low-Weyl configurations unknown |
| **P02** | Local-Rindler-Horizon Thermodynamic Constraint | B/J | T1–T6 all PASS | Extension from equation-of-motion constraint to initial-data selection not established; quantitative argument for Weyl exclusion not demonstrated |
| **P06** | Constraint-Algebra Anomaly-Freedom | C/G | T1–T6 all PASS | Requires non-minisuperspace quantum GR (unavailable); connection between anomaly-free sector and low-Weyl geometry not established |
| **P08** | Spin-Foam Vertex-Amplitude Curvature Suppression | R | T1–T6 all PASS | Continuum limit not established; large-j approximation may fail at Planck scale; connection between saddle-point suppression and specifically low Weyl tensor not explicit |

---

## KILL ANALYSIS — PATTERNS IN FAILURES

**Most common kill reason:**
- T2 (Background dependence): 8 kills — P07, P09, P11, P17, P19, P20, P21, P24. Many candidates are defined in specific geometric settings (asymptotically flat, AdS, FRW) that do not apply to general cosmological initial data.
- T1 (Conclusion encoding): 6 kills — P03, P12, P14, P15, P19, P23. These candidates either use the target state (smoothness, low Weyl) as input under a different name, or use observations of the outcome as constraints on the input.
- T3 (Triviality): 6 kills — P04, P10, P14, P15, P18, P20, P22. These candidates impose conditions without deriving them from an independent physical principle.
- T4 (Renaming): 4 kills — P05, P21, P22, P24, P25. Several candidates are variants of already-killed mechanisms (decoherence, holography).
- T5 (Existing physics): 3 kills — P13, P16. These either use already-known results or fail to provide a genuine selection mechanism.
- T6 (Undefined measure): 1 kill — P10. Only one candidate failed T6 specifically, but many more have T6 concerns noted in their remaining-concerns lists.

**Structural insight:**
The 21 killed candidates fail for three fundamental reasons:
1. Wrong geometric domain (T2 failures): proposed in AdS, asymptotically flat, or FRW-only settings.
2. Assumption laundering (T1 failures): encoding the smooth initial state under a different name or using the observed outcome as a constraint.
3. Mechanism without derivation (T3 failures): imposing a condition (stability, completeness, consistency-with-observations) without deriving it from an independent physical principle.

The 4 survivors avoid all three problems but face a common challenge: they operate at the level of quantum gravity (asymptotic safety, constraint algebra quantization, spin foams) where the connection to classical initial-data restriction is not yet established.

---

*Document status: KILL TESTS COMPLETE*
*25 candidates tested; 21 killed; 4 surviving*
*Next: ADVERSARIAL_INITIAL_DATA_RESULTS.md — test P01, P02, P06, P08 against 7 adversarial initial-data classes*
*Date: August 2026*
