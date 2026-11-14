# OP-3 Research Report: Can g Be Derived from First Principles?
**Date:** 2026-07-24  
**Problem:** OP-3 — Derivation of the quantum-classical coupling constant g  
**Authority:** C2_FOUNDATIONS.md (frozen); all prior audits accepted as established  
**Mandate:** Search every existing component of C2 for a hidden derivation of g.  
**Rules:** No new postulates. No redefinition of g. No experimental values. No phenomenological fitting.  
**Final verdict form:** PASS / PARTIAL / FAILED

---

## PHASE 1 — COMPLETE INVENTORY OF EVERY EQUATION CONTAINING g

### Definition of g

From interaction_hamiltonian_derivation.md, Section 1:

> g is a real coupling constant with units fixed by dimensional analysis:
> $$[g] = \text{J} \cdot \text{m}^2 \cdot \text{s} / \text{info}$$

This unit assignment is the unique dimensional choice that makes $H_{\text{int}} = g \cdot J \cdot \sigma_z$ have units of energy [J], given $[J_{\text{field}}] = \text{info}/(\text{m}^2 \cdot \text{s})$ and $[\sigma_z] = \text{dimensionless}$.

### Every equation in C2 that contains g

A systematic scan of all C2 documents yields the following complete list:

| Eq. ID | Equation | Source document |
|--------|----------|----------------|
| [H-INT] | $H_{\text{int}} = g \cdot J(x_q, t) \cdot \sigma_z$ | interaction_hamiltonian_derivation.md |
| [DEPH-RATE] | $\Gamma_\phi = (4g^2/\hbar^2)\int_0^\infty C_{JJ}(\tau)\,d\tau$ | interaction_hamiltonian_derivation.md |
| [DEPH-PSD] | $\Gamma_\phi = (2g^2/\hbar^2) S_{JJ}(0)$ | interaction_hamiltonian_derivation.md |
| [GAMMA-ROT-FULL] | $\Gamma_\phi = (8g^2 s_0^2 r_q^2 \tau)/(3\hbar^2) \cdot \omega_{\text{rot}}^2$ | interaction_hamiltonian_derivation.md |
| [DEF-KROT] | $k_{\text{rot}} = 8g^2 s_0^2 r_q^2 \tau / (3\hbar^2)$ | interaction_hamiltonian_derivation.md |
| [KROT-EXPLICIT] | $k_{\text{rot}} = 8g^2 s_0^2 r_q^2 / (6\hbar^2\lambda)$ | interaction_hamiltonian_derivation.md |
| [KAPPA-FROM-G] | $\kappa = 4g^2 s_0^2 r_q^2 \tau / \hbar$ | interaction_hamiltonian_uniqueness.md |
| [JUMP-RATE] | $\gamma = (2g^2/\hbar^2)\langle(\delta J)^2\rangle\tau$ | effective_master_equation_derivation.md |
| [A-BORN] | $g^2 \ll \hbar^2/\tau^2$ (self-consistency condition) | interaction_hamiltonian_derivation.md |
| [DIM-g] | $[g] = \text{J}\cdot\text{m}^2\cdot\text{s}/\text{info}$ | interaction_hamiltonian_derivation.md |

**Total appearances of g:** 10 equations across 3 documents.

### What g controls in each equation

| Equation | Role of g |
|----------|-----------|
| [H-INT] | Sets the energy scale of the qubit-substrate interaction |
| [DEPH-RATE] | Appears as $g^2/\hbar^2$ — the dimensionless coupling strength |
| [DEF-KROT] | Appears as compound $g^2 s_0^2 r_q^2 \tau / \hbar^2$ — the prefactor of the Ramsey $\omega^2$ law |
| [A-BORN] | Self-consistency: g must be small enough that Born approximation holds |

### Key observation from the inventory

g appears **exclusively** in Layer 3 (quantum coupling layer). It does not appear in:
- Layer 1 (transport equations [C-s], [C-J], [TEL])
- Layer 2 (Q diagnostic)
- Layer 4 (CCA / Gibbs)
- Layer 5 (SCC / reconstruction)
- Layer 6 (obstructions O1, O2, O3)

g is a **boundary constant** — it sits at the interface between the classical substrate (which has no g) and the quantum system (which has no substrate). It is the single parameter that translates between the two layers.

---

## PHASE 2 — ALL INDEPENDENT DERIVATION PATHS

Each path is attempted independently. For each: full derivation, stopping point, exact missing lemma, verdict.

---

### Path 2-A: Derive g from the Transport Layer [C-s], [C-J]

**Attempt:** The substrate transport equations are:
$$\partial_t s + \partial_x J = 0, \quad \partial_t J + c^2\partial_x s + J/\tau = 0$$

These equations contain only the parameters $c$ (substrate wave speed) and $\tau$ (relaxation time). Their units are $[c] = \text{m/s}$, $[\tau] = \text{s}$. 

**Can g be constructed from c and τ?**

The units of g are $\text{J}\cdot\text{m}^2\cdot\text{s}/\text{info}$. Attempt to construct this from $c$ and $\tau$:

$$[g] = \text{J}\cdot\text{m}^2\cdot\text{s}/\text{info}$$

From $c$ and $\tau$ alone, the only dimensionful combinations are:
- $c\tau$ with units m (length)
- $c^2\tau^2$ with units m² (area)
- $\tau^n c^m$ with units $\text{m}^m \text{s}^{n-m}$

No combination of $c^m \tau^n$ produces units of J (energy) without introducing an additional energy scale (mass × velocity² or force × length). The transport layer contains no energy scale — $s$ has units info/m³ and $J$ has units info/(m²·s); there is no quantity with units of energy anywhere in the transport equations.

**Stopping point:** The transport layer has no energy unit. g requires J (joules) as part of its units. No combination of transport-layer quantities produces joules.

**Exact missing lemma:** An identification of the form
$$E_{\text{substrate}} = \alpha \cdot E_{\text{quantum}}$$
where $\alpha$ is a dimensionless number. Such an identification would require knowing which substrate energy scale (e.g., $k_B T$, $\hbar\omega$) corresponds to one quantum of substrate action. This is not available from [C-s] and [C-J].

**Is this gap implied elsewhere in C2?** No. The transport equations are dimensionless in structure — the telegrapher equation $\tau s_{tt} + s_t = c^2\tau\nabla^2 s$ involves only the ratio $c\tau/L$ when written in dimensionless form. No energy scale enters.

**Verdict: FAILED.** The transport layer does not contain the energy unit [J] required for g.

---

### Path 2-B: Derive g from the PRW Microscopic Rules

**Attempt:** The PRW is defined by: walker speed $v$ (units m/s), flip rate $\lambda$ (units s⁻¹), and information quantum $\sigma_0$ (units info). The PRW parameters map to transport parameters as $c = v$, $\tau = 1/(2\lambda)$.

**Can g be constructed from $v$, $\lambda$, $\sigma_0$?**

$$[g] = \text{J}\cdot\text{m}^2\cdot\text{s}/\text{info}$$

From the PRW: $[v] = \text{m/s}$, $[\lambda] = \text{s}^{-1}$, $[\sigma_0] = \text{info}$.

Attempt:
$$g \stackrel{?}{=} \alpha \cdot v^a \lambda^b \sigma_0^c$$

Dimensional equation:
$$\text{J}\cdot\text{m}^2\cdot\text{s}\cdot\text{info}^{-1} = (\text{m/s})^a \cdot (\text{s}^{-1})^b \cdot \text{info}^c$$

From info: $c = -1$.
From m: $a = 2$.
From s: $-a - b = 1 \Rightarrow b = -3$.
From J: impossible — the right side has no J (energy) unit no matter what $a, b, c$ are.

**Stopping point:** Same as Path 2-A. The PRW has no energy unit in its primitive parameters.

**Exact missing lemma:** An identification between the PRW's information quantum $\sigma_0$ (units: info) and a physical energy scale (units: J). Such an identification would require knowing "how much energy is one information quantum of substrate" — a constitutive relation not present in the PRW axioms.

**Verdict: FAILED.** The PRW contains no energy scale.

---

### Path 2-C: Derive g from the Interaction Hamiltonian Derivation Chain

**Attempt:** The document interaction_hamiltonian_derivation.md explicitly states (Section 1, final conclusion):

> "No further constraint on g comes from the substrate transport theory. g is the single new parameter introduced by the quantum coupling. It is analogous to the electric charge e in QED — it sets the magnitude of the interaction."

And Section 10 (What Is Derived vs What Requires Input):

| Claim | Status |
|-------|--------|
| g (coupling constant) | **Not derivable** from classical transport | Must be measured or from QFT |

**Derivation stops here:** The source document itself explicitly identifies g as a free parameter that "must be measured or from QFT."

**Stopping point:** The authors of the derivation document explicitly concluded that g requires external input.

**Exact missing lemma:** A derivation of the energy scale from the substrate information field — specifically: what is the energy associated with one information quantum flowing at speed c across area $r_q^2$ per unit time? There is no theorem in C2 that answers this.

**Verdict: FAILED.** Explicitly identified as undetermined in the source document.

---

### Path 2-D: Derive g from the Interaction Hamiltonian Uniqueness Theorem

**Attempt:** Theorem HC-3 (interaction_hamiltonian_uniqueness.md) proves that given [A-lin-coupling] + [A-local] + the pure-dephasing criterion, the Lindblad operator is uniquely $A = \sigma_z$. Does the uniqueness proof also fix g?

**Analysis:** The uniqueness proof (Section 7 of uniqueness document) derives:
$$A_S \text{ produces pure dephasing} \iff A_S \propto \sigma_z$$

The proportionality constant is absorbed into g: $H_{\text{int}} = g \cdot J \cdot (\alpha\sigma_z) = (g\alpha) \cdot J \cdot \sigma_z$. Redefining $g' = g\alpha$, the operator is normalized to $\sigma_z$ with coupling $g'$.

**The uniqueness theorem fixes the direction of the qubit operator** ($A_S = \sigma_z$) but does **not** fix the magnitude of $g$. The proof explicitly operates with $g$ as a free real parameter throughout. Every equation in the proof holds for any nonzero $g$.

**Stopping point:** The uniqueness theorem is a statement about the qubit operator direction, not the coupling magnitude.

**Exact missing lemma:** A normalization condition on $g$ — for example, a requirement that the energy perturbation from one substrate information quantum equals $\hbar\omega_q/2$ (one qubit energy gap). No such condition exists in C2.

**Verdict: FAILED.** Operator uniqueness does not fix g.

---

### Path 2-E: Derive g from the Bloch-Redfield Derivation

**Attempt:** The Bloch-Redfield master equation [BR] (interaction_hamiltonian_derivation.md, Section 3) gives:
$$\frac{d\rho_S}{dt} = -\frac{g^2}{\hbar^2}\int_0^\infty C_{JJ}(\tau)\,d\tau \cdot [σ_z, [σ_z, \rho_S]]$$

g appears as $g^2/\hbar^2$ — a dimensionless combination (after appropriate unit conversion). The Bloch-Redfield equation is parameterized by this combination. Its value is set by the experimental Ramsey measurement.

**Can the Bloch-Redfield structure itself determine $g^2/\hbar^2$?**

The equation $\Gamma_\phi = (4g^2/\hbar^2)\int C_{JJ}d\tau$ has two unknowns: $g$ and $\int C_{JJ}d\tau$. Both are unknown from C2 alone ($\int C_{JJ}d\tau = \langle(\delta J)^2\rangle\tau$ requires knowing $s_0$, $r_q$, $\tau$, none of which are given by the quantum layer). Therefore there is no additional constraint from the master equation structure.

**Stopping point:** The Bloch-Redfield structure gives $\Gamma_\phi$ as a function of $g^2\cdot\int C_{JJ}d\tau$, but both factors are free.

**Verdict: FAILED.** Bloch-Redfield does not fix g.

---

---

## PHASE 3 — DIMENSIONAL ANALYSIS

Can the units of g be used to fix g numerically?

### What dimensional analysis can and cannot do

Dimensional analysis can:
1. Determine the units of g given the units of the other quantities in $H_{\text{int}}$ — this is done and gives $[g] = \text{J}\cdot\text{m}^2\cdot\text{s}/\text{info}$.
2. Determine which combinations of known constants have the same units as g.
3. Identify which additional physical constant would be needed to fix g.

Dimensional analysis cannot fix the **numerical value** of g — only its units.

### Dimensional construction from known constants

The known C2 parameters are:
$$c\ [\text{m/s}], \quad \tau\ [\text{s}], \quad \hbar\ [\text{J}\cdot\text{s}], \quad k_B\ [\text{J/K}], \quad s_0\ [\text{info/m}^3], \quad r_q\ [\text{m}]$$

Attempt to construct g from these:
$$[g] = \text{J}\cdot\text{m}^2\cdot\text{s}/\text{info} = \frac{\hbar \cdot [g]_{\text{info-free}}}{\text{info}}$$

The info unit is not a standard SI unit. It is introduced by the C2 framework as the unit of substrate density. Its conversion to SI energy is precisely what g encodes:

$$g \cdot J_{\text{field}} = \text{energy} \implies g \times \frac{\text{info}}{\text{m}^2\cdot\text{s}} = \text{J}$$

Therefore $g$ is the **conversion factor between substrate information current and physical energy**. Dimensional analysis tells us this is what g is, but not its numerical value. The numerical value requires knowing how much physical energy corresponds to one unit of substrate information current.

### Attempt: fix g using $\hbar$, $c$, $s_0$, $r_q$, $\tau$

From these five quantities, construct something with units of g:

$$g \stackrel{?}{=} \frac{\hbar}{s_0 \cdot r_q^2 \cdot \tau}$$

Check:
$$\frac{[\hbar]}{[s_0][r_q]^2[\tau]} = \frac{\text{J}\cdot\text{s}}{(\text{info}/\text{m}^3)(\text{m})^2(\text{s})} = \frac{\text{J}\cdot\text{s}\cdot\text{m}^3}{\text{info}\cdot\text{m}^2\cdot\text{s}} = \frac{\text{J}\cdot\text{m}}{\text{info}}$$

Not the right units (off by m²·s/m = m·s).

Another attempt: $g \stackrel{?}{=} \hbar c / (s_0 r_q^4 \tau)$... this requires exhaustive search. The general form is $g = \alpha \cdot \hbar^a c^b s_0^c r_q^d \tau^e$ where $\alpha$ is a dimensionless number.

The dimensional equation is:
$$\text{J}\cdot\text{m}^2\cdot\text{s}/\text{info} = (\text{J}\cdot\text{s})^a \cdot (\text{m/s})^b \cdot (\text{info/m}^3)^c \cdot \text{m}^d \cdot \text{s}^e$$

From J: $a = 1$.
From info: $c = -1$.
From s: $a - b + e = 1 \Rightarrow 1 - b + e = 1 \Rightarrow e = b$.
From m: $b - 3c + d = 2 \Rightarrow b + 3 + d = 2 \Rightarrow d = -1 - b$.

So: $g = \alpha \cdot \hbar \cdot c^b \cdot s_0^{-1} \cdot r_q^{-1-b} \cdot \tau^b$ for any real $b$.

The free exponent $b$ and the dimensionless coefficient $\alpha$ are both undetermined. Dimensional analysis does not fix $g$ — it only constrains it to a one-parameter family of possible forms.

The physically natural choice is $b = 0$ (no dependence on $c$ or $\tau$):
$$g \stackrel{?}{=} \frac{\alpha\hbar}{s_0 r_q}$$

But there is no C2 theorem that selects $b = 0$ or fixes $\alpha$.

**Verdict: FAILED.** Dimensional analysis constrains the units of g but does not fix its numerical value. There is a one-parameter family of dimensionally consistent expressions for g, and no C2 theorem selects among them.

---

## PHASE 4 — SYMMETRY DERIVATIONS

### Path 4-A: Lorentz Symmetry

**Attempt:** Lorentz symmetry constrains the form of couplings in relativistic quantum field theory. In QED, the minimal coupling $e A_\mu J^\mu$ is forced by gauge invariance. Does an analogous argument apply in C2?

**Status of Lorentz symmetry in C2:** The Lorentz group derivation is OP-12 in C2_FOUNDATIONS.md — explicitly OPEN. C2 does not currently derive the Lorentz group. The transport equations are non-relativistic (the substrate speed $c$ is a material parameter, not the speed of light).

**Stopping point:** Lorentz symmetry is not available in current C2. The argument cannot be applied.

**Verdict: FAILED.** Lorentz symmetry is an unproved open problem in C2.

---

### Path 4-B: Gauge Symmetry

**Attempt:** In QED, the electric charge $e$ is fixed by gauge invariance: the coupling $e\bar\psi\gamma^\mu\psi A_\mu$ is the unique gauge-invariant minimal coupling. If C2's substrate current $J$ plays the role of a gauge field, gauge invariance might fix g.

**Status of gauge symmetry in C2:** The gauge group derivation is OP-13 in C2_FOUNDATIONS.md — explicitly OPEN. C2 does not derive U(1) gauge symmetry for the substrate field $J$. The substrate current $J$ is a classical scalar field with no gauge transformation property.

Moreover, the SCC framework derives a $U(1)$ phase symmetry for quantum amplitudes (from $SO(2) \cong U(1)$ acting on the minimal state space), but this is the quantum $U(1)$ acting on qubits — not a gauge symmetry of the substrate field $J$.

**Stopping point:** No gauge symmetry exists for the substrate field $J$ in current C2.

**Verdict: FAILED.** Gauge symmetry of the substrate field is not established in C2.

---

### Path 4-C: SCC Symmetry (Compact Group Acting on State Space)

**Attempt:** SCC requires a compact group $G$ acting transitively on the state space $S$. For the qubit, $G = SU(2)$ acting on $S = S^2$ (Bloch sphere). The coupling $H_{\text{int}} = gJ\sigma_z$ breaks the $SU(2)$ symmetry of the qubit (it selects a preferred axis $z$). Does the SCC framework constrain how $SU(2)$ can be broken?

**Analysis:** The SCC framework (Theorem SCC-6) derives that $G$ must be compact, transitive, and act by isometries. It says nothing about the coupling to an external field. The qubit's $SU(2)$ symmetry is explicitly broken by the free Hamiltonian $H_S = (\hbar\omega_q/2)\sigma_z$ (which also selects the $z$-axis). The additional breaking by $H_{\text{int}} = gJ\sigma_z$ is along the same axis. SCC determines the structure of the symmetry group of the unperturbed system; it does not constrain the magnitude of symmetry-breaking couplings.

**Stopping point:** SCC determines the symmetry group $G$ of the unperturbed qubit but not the magnitude of couplings that break this symmetry.

**Verdict: FAILED.** SCC symmetry does not constrain g.

---

### Path 4-D: CCA Symmetry (Automorphism Group of Causal Algebra)

**Attempt:** The CCA automorphism group $\text{Aut}(A)$ acts on the morphism space. Does this constrain the coupling between a CCA causal morphism and a quantum system?

**Analysis:** The CCA operates at the abstract level of causal morphisms with probability weights. The coupling $H_{\text{int}} = gJ\sigma_z$ is a statement about a specific physical system (qubit coupled to substrate current) that must be embedded in the CCA language. The embedding requires specifying how the CCA objects correspond to physical states and how the CCA morphisms correspond to physical processes. This embedding is not fixed by the CCA axioms (Ax1–Ax5) — it requires additional physical input (specifically, identifying which CCA morphisms correspond to qubit energy eigenstates, and which correspond to substrate current quanta). 

**Stopping point:** The CCA axioms fix the abstract structure but not the concrete physical embedding. g is part of the embedding (the "size" of the coupling), not part of the abstract structure.

**Verdict: FAILED.** CCA automorphism symmetry does not constrain g.

---

### Path 4-E: Conservation Laws

**Attempt:** All conservation laws in C2 are:
- Total information $Q = \int s\,dx$ conserved ([CONS-1]) — scalar, no energy
- PRW particle number — conserved by reversals
- CCA causal rank $r$ is non-decreasing along causal chains — monotonicity, not conservation in the usual sense

None of these conservation laws involve energy. The only energy-like quantity in C2 is $E_{\text{sub}} = \tfrac{1}{2}c^2s^2 + \tfrac{1}{2}J^2$, which has units info²·m/s² (not Joules). Its conservation (from the continuity equation for energy) gives the substrate's own energy balance, but does not link substrate energy to quantum energy without g.

**Stopping point:** No conservation law relates substrate quantities to quantum energy without invoking g as the conversion factor.

**Verdict: FAILED.** Conservation laws do not fix g.

---

### Phase 4 Verdict

No symmetry argument in C2 — Lorentz, gauge, SCC, CCA, or conservation laws — fixes the value of g. Every symmetry-based path fails because either (a) the relevant symmetry is not yet derived in C2 (Lorentz, gauge), or (b) the symmetry constrains structure but not the magnitude of symmetry-breaking couplings (SCC, CCA).

---

## PHASE 5 — EMERGENCE DERIVATIONS

### Path 5-A: Thermodynamic Limit / Large-N

**Attempt:** In statistical mechanics, the thermodynamic limit $N \to \infty$ can sometimes fix coupling constants via universality (e.g., the critical exponent $\nu$ is fixed at a renormalization group fixed point). Can the large-N limit of the FPUT chain or the CCA fix g?

**FPUT large-N:** The FPUT harmonic chain in the thermodynamic limit $N \to \infty$ produces the telegrapher equation with parameters $c = v_{\text{acoustic}}$ and $\tau = 1/(2\lambda)$. These are dimensionful parameters (m/s and s), not energy scales. The information density $s$ has units info/m³. No energy scale appears in the $N \to \infty$ limit — the system remains classical with no $\hbar$.

**CCA large-N:** The conjecture OBS-C1/OP-16 states that in the large-N limit of a CCA structure, O1 (complex structure) and O2 (continuum geometry) might emerge. If this conjecture were proved, it would derive $\hbar$ as the quantum of action. But:
1. OBS-C1 is an **unproved conjecture**.
2. Even if O1 emerged, the conjecture derives the complex structure — not the coupling between the complex (quantum) layer and the real (classical) layer. g is precisely this inter-layer coupling.

**Stopping point:** Large-N gives the classical transport layer and (conjecturally) the quantum structure, but not the coupling between them.

**Verdict: FAILED.** Thermodynamic limit does not produce g.

---

### Path 5-B: Coarse-Graining

**Attempt:** When the FPUT chain is coarse-grained to produce the PRW/telegrapher, the coarse-graining procedure projects out degrees of freedom. Does any information about the energy scale survive in the projected description?

**Analysis:** The projection theorem (Theorem FPUT-3) shows that the PRW is the unique local projection of the FPUT harmonic chain satisfying admissibility constraints C1–C6. The projection projects onto action variables $n_k = |A_k|^2$ and discards phase information $\phi_k$. The action variables have units of energy ($n_k = \hbar\omega_k N_k$ in quantum mechanics, or energy/(unit frequency) in classical mechanics). However, the C2 coarse-graining works with dimensionless information densities — it does not track the physical energy of FPUT modes.

The coarse-graining is a projection from the FPUT phase space (with units energy) to the information density field $s$ (with units info/m³). The conversion between energy and information ($\text{J} \leftrightarrow \text{info}$) is precisely what g encodes. The coarse-graining procedure discards this conversion by working with the dimensionless information ratio.

**Stopping point:** The coarse-graining deliberately strips the energy unit from the substrate description. g is the inverse of this stripping — it is the energy-per-information scale that the coarse-graining throws away.

**Verdict: FAILED.** Coarse-graining discards the energy scale that g encodes.

---

### Path 5-C: Renormalization Group

**Attempt:** At a renormalization group (RG) fixed point, coupling constants take specific values fixed by the fixed-point equation. Can an RG analysis of the C2 system fix g?

**Analysis:** RG in the C2 context would require a UV theory (a microscopic model with a short-distance cutoff) that renormalizes to the C2 effective theory. The C2 transport layer has a built-in UV cutoff: the PRW mean free path $\ell = c\tau$ acts as a lattice spacing. However:
- The C2 transport layer is a linear theory (no self-coupling of $s$ or $J$). Linear theories do not run under RG — there is no renormalization of the coupling constant $g$ in the transport sector.
- The quantum coupling $H_{\text{int}} = gJ\sigma_z$ is a bilinear coupling between classical field $J$ and quantum operator $\sigma_z$. In an RG treatment of such a coupling (the spin-boson model), the effective coupling runs with energy scale, but the UV value of $g$ must be specified as an initial condition for the RG flow. The RG tells us how $g$ runs, not what it starts at.

**Stopping point:** RG analysis of C2 would give the flow of g with scale, but the initial (UV) value of g must be input.

**Verdict: FAILED.** RG analysis does not fix the UV value of g.

---

### Path 5-D: Microscopic Candidates C1–C5

**Attempt:** For each candidate:

**C1 (†-compact SMC):** Generates finite-dimensional QM via Coecke-Abramsky. The coupling $g$ between the QM system and a classical field is external to the categorical framework — it requires specifying the Hilbert space representation and the coupling operator. C1 fixes the algebraic structure of the quantum system, not its coupling to a classical bath.

**C2 (Finite-state channel category):** Generates Gibbs distribution and classical statistical mechanics. No quantum structure. No g.

**C3 (Dependent type theory):** Provides internal models of gauge fields. In principle, the gauge coupling constant could be defined internally. But C3 has not been developed to the point of generating quantum-classical cross-couplings in C2. This path requires OP-14 (QFT emergence) to be solved first.

**C4 (Finite partial order):** Generates Lorentzian geometry from causal order. Does not produce coupling constants.

**C5 (σ-finite measure algebra):** Generates classical Hamiltonian mechanics. No quantum structure. No g.

**Stopping point:** None of the five microscopic candidates generates the quantum-classical interface where g lives.

**Verdict: FAILED (all five candidates).** None of C1–C5 generates g.

---

### Phase 5 Verdict

No emergence argument — thermodynamic limit, coarse-graining, renormalization, or microscopic candidates — produces g. The root cause is structural: g lives at the interface between the classical substrate layer (which has no $\hbar$) and the quantum system layer (which has no substrate). Every emergence argument that starts from the classical substrate produces classical objects only. Every emergence argument that starts from the quantum structure produces quantum objects only. g is the bridge between the two, and no current C2 theorem builds that bridge.

---

---

## PHASE 6 — INDEPENDENCE THEOREM

All derivation paths in Phases 2–5 have failed. This phase proves, by explicit logical construction, that g is genuinely independent of the current C2 axioms.

---

### Theorem G-IND: The coupling constant g is logically independent of the current C2 axiom system.

**Formal statement:**

Let $\mathcal{A}_{\text{C2}}$ denote the complete axiom set of the current C2 framework:
$$\mathcal{A}_{\text{C2}} = \{\text{Ax1–Ax5 (CCA)},\ \text{A-PRW1–3},\ \text{A-FPUT1–3},\ \text{A1–A8 (ME)},\ \text{AA1, AA2 (SCC)},\ \text{A-HC1–HC6},\ \text{M1, M2}\}$$

Let $g \in \mathbb{R}_{>0}$ be the quantum-classical coupling constant.

**Theorem G-IND:** For any value $g_1 \neq g_2$ with $g_1, g_2 > 0$, both $g = g_1$ and $g = g_2$ are consistent with $\mathcal{A}_{\text{C2}}$. Therefore $\mathcal{A}_{\text{C2}}$ does not determine g.

**Proof by explicit model construction:**

Construct two models $\mathcal{M}_1$ and $\mathcal{M}_2$ that both satisfy every axiom in $\mathcal{A}_{\text{C2}}$ but differ in g.

**Model $\mathcal{M}_1$:** Take any specific consistent realization of C2 with coupling constant $g_1$. By assumption, C2 is internally consistent (established). So $\mathcal{M}_1$ exists.

**Model $\mathcal{M}_2$:** Define $\mathcal{M}_2$ to be identical to $\mathcal{M}_1$ in all respects except replace $g_1 \to g_2 = \alpha g_1$ for any $\alpha > 0$, $\alpha \neq 1$.

**Verify that $\mathcal{M}_2$ satisfies all C2 axioms:**

- *Ax1–Ax5 (CCA):* These axioms govern the structure of $(O, M, \otimes, \leq, \dagger, \varepsilon)$. None of these axioms contain g. $\mathcal{M}_2$ satisfies Ax1–Ax5. ✓
- *A-PRW1–3 (PRW):* These axioms govern the PRW speed $v$, flip rate $\lambda$, and Markov property. None contain g. $\mathcal{M}_2$ satisfies A-PRW1–3. ✓
- *A-FPUT1–3 (FPUT):* These axioms govern the FPUT lattice. None contain g. ✓
- *A1–A8 (Master Equation):* These axioms govern the substrate transport. None contain g. ✓
- *AA1, AA2 (SCC):* These axioms govern the compactness of G and the commutativity of evolution with composition. Neither contains g. ✓
- *A-HC1–HC6 (Quantum coupling):* A-HC1 (Born): $g_2^2 \ll \hbar^2/\tau^2$. For any fixed $\tau$ and $\hbar$, this is satisfied for sufficiently small $g_2$, and for large $g_2$ it fails — but the axiom is a condition on g, not a derivation of g. We choose $g_2$ small enough that A-HC1 holds. ✓  
  A-HC2 (Markov): $\tau \ll \Gamma_\phi^{-1}$. Since $\Gamma_\phi \propto g_2^2$, reducing $g_2$ makes $\Gamma_\phi$ smaller and $\Gamma_\phi^{-1}$ larger, making the Markov condition easier to satisfy. ✓  
  A-HC3 (Secular): Requires $\omega_q \gg \Gamma_\phi$. Again satisfied for small $g_2$. ✓  
  A-HC4 (Stationarity): Independent of g. ✓  
  A-HC5 (Linear coupling): States that H_int is linear in J. This holds for both $g_1$ and $g_2$. ✓  
  A-HC6 (Local coupling): States that H_int is evaluated at $x_q$. Independent of g. ✓  
- *M1 (Matrix fields):* Independent of g. ✓  
- *M2 (Moyal deformation):* Independent of g. ✓

**Conclusion:** $\mathcal{M}_2$ satisfies all axioms of $\mathcal{A}_{\text{C2}}$ for any $g_2 > 0$ sufficiently small. Therefore $\mathcal{A}_{\text{C2}}$ is consistent with any value of $g > 0$ in some neighborhood of 0.

Since both $\mathcal{M}_1$ (with $g_1$) and $\mathcal{M}_2$ (with $g_2 \neq g_1$) satisfy $\mathcal{A}_{\text{C2}}$, the axiom system does not determine the value of g. $\blacksquare$

---

### Corollary G-CON: g is a free parameter of the same logical status as the elementary charge e in QED.

**Proof sketch:** In QED, the Lagrangian $\mathcal{L} = \bar\psi(i\gamma^\mu D_\mu - m)\psi - \tfrac{1}{4}F_{\mu\nu}F^{\mu\nu}$ with $D_\mu = \partial_\mu + ieA_\mu$ contains the electric charge $e$ as a free parameter. The QED axioms (Lorentz invariance, gauge invariance, locality, unitarity, renormalizability) constrain the structure of the theory but not the value of $e$. The value $e \approx 0.303$ (in natural units, $\alpha = e^2/(4\pi) \approx 1/137$) is measured experimentally.

In C2, g plays the same role: it sets the energy scale of the quantum-classical coupling. The C2 axioms constrain the structure of the coupling ($H_{\text{int}} = gJ\sigma_z$, uniquely) but not the numerical value of $g$. The value of g must be extracted from experimental data (currently: $g^2 = 3\hbar^2 k_{\text{rot}}/(8s_0^2 r_q^2\tau)$, where $k_{\text{rot}}$ is fitted from IBM Ramsey data). $\blacksquare$

---

### The exact missing structure

The independence theorem shows that g is free. But what **would** determine g, if anything?

**Formally, g would be fixed by any one of the following (none of which currently exists in C2):**

**(i) An energy-information equivalence principle:**  
A theorem of the form $E = \eta \cdot I$ where $E$ is physical energy, $I$ is substrate information, and $\eta$ is a universal constant with units J/info. Given $\eta$, we would have:
$$g = \frac{\eta \cdot c^2 \tau}{r_q^2} \quad \text{(one possible form)}$$
No such theorem exists in C2.

**(ii) A derivation of $\hbar$ from C2:**  
If the Planck constant $\hbar$ were derived from C2 (C2_MISSING_PRINCIPLES.md Problem 2 — currently admits no solution), and if $\hbar$ could be expressed in terms of substrate quantities $c$, $\tau$, $s_0$, then g might be fixed.  
Current status: $\hbar$ is independent of the transport layer (OP in C2_MISSING_PRINCIPLES.md).

**(iii) A proof of the large-N universality conjecture (OBS-C1/OP-16):**  
If it were proved that in the large-N limit of any C2-compatible framework, complex quantum mechanics emerges with a specific action scale $\hbar_{\text{eff}} = f(c, \tau, \text{info parameters})$, this would give $\hbar$ as a derived quantity and potentially fix $g$ through a quantum-classical matching condition.  
Current status: OBS-C1 is an unproved conjecture.

**(iv) A QFT derivation in the C3/C1 sector:**  
Candidate C3 (dependent type theory) in principle allows the derivation of gauge field theories with specific coupling constants. If C3 were developed to produce an interacting quantum field theory containing the substrate-qubit coupling, the coupling constant might be fixed by renormalizability or by a quantum anomaly condition.  
Current status: QFT emergence (OP-14) is completely open.

---

## SUMMARY OF ALL PATHS

| Phase | Path | Starting point | Stopping point | Verdict |
|-------|------|---------------|----------------|---------|
| 2-A | Transport layer | [C-s], [C-J] | No energy unit in transport | FAILED |
| 2-B | PRW microscopic | $v$, $\lambda$, $\sigma_0$ | No energy unit in PRW | FAILED |
| 2-C | H_int derivation chain | Full derivation doc | Explicitly identified as free | FAILED |
| 2-D | HC-3 uniqueness theorem | Operator selection proof | Fixes direction, not magnitude | FAILED |
| 2-E | Bloch-Redfield structure | Born-Markov master eq. | $g^2\times\int C_{JJ}$ has two unknowns | FAILED |
| 3 | Dimensional analysis | All C2 parameters | One-parameter family; $\alpha$ undetermined | FAILED |
| 4-A | Lorentz symmetry | SCC + OP-12 | Lorentz derivation is open | FAILED |
| 4-B | Gauge symmetry | SCC U(1) | No gauge symmetry for substrate J | FAILED |
| 4-C | SCC symmetry | SCC theorems | Constrains structure, not magnitude | FAILED |
| 4-D | CCA automorphism | CCA axioms | Abstract structure, not embedding | FAILED |
| 4-E | Conservation laws | [CONS-1], rank monotonicity | No energy conservation in transport layer | FAILED |
| 5-A | Thermodynamic limit / large-N | FPUT, CCA | Classical only; OBS-C1 unproved | FAILED |
| 5-B | Coarse-graining | FPUT → PRW projection | Energy scale is discarded in projection | FAILED |
| 5-C | Renormalization group | C2 linear theory | No UV initial condition; linear theory doesn't run | FAILED |
| 5-D-C1 | C1 (†-compact SMC) | Categorical QM | Algebraic structure only; no coupling | FAILED |
| 5-D-C2 | C2 (Channel category) | Classical stat mech | No quantum; no g | FAILED |
| 5-D-C3 | C3 (Type theory) | HoTT gauge | OP-14 (QFT) unresolved | FAILED |
| 5-D-C4 | C4 (Causal poset) | Lorentzian geometry | No coupling constants | FAILED |
| 5-D-C5 | C5 (Measure algebra) | Classical Hamiltonian | No quantum; no g | FAILED |
| 6 | Independence theorem | All C2 axioms | Two models with different g both satisfy all axioms | **PROVED INDEPENDENT** |

**All 19 paths FAILED. Independence proved by explicit model construction.**

---

## FINAL VERDICT

$$\boxed{\textbf{FAILED}}$$

**The current C2 mathematics does not determine g. g is a genuinely free parameter.**

**Proof:** Theorem G-IND (Phase 6) explicitly constructs two models $\mathcal{M}_1$, $\mathcal{M}_2$ satisfying all C2 axioms but with different values of g. Therefore no C2 axiom determines g.

**Supporting evidence from exhaustive search:** 19 independent derivation paths were attempted across the transport layer, PRW, FPUT, interaction Hamiltonian, Bloch-Redfield, dimensional analysis, Lorentz symmetry, gauge symmetry, SCC, CCA, conservation laws, large-N limits, coarse-graining, renormalization, and all five microscopic candidates. Every path failed at an identifiable stopping point:
- Paths through the classical substrate fail because the transport layer has no energy unit.
- Paths through symmetry fail because the relevant symmetries (Lorentz, gauge) are unproved in C2.
- Paths through emergence fail because the large-N conjecture is unproved and coarse-graining discards the energy scale.
- Paths through structure fail because symmetry constrains the form of the coupling, not its magnitude.

**The structural reason:** g is the conversion factor between substrate information units (info) and physical energy units (Joules). This conversion cannot be derived from within a framework that operates entirely in information units on one side (transport layer) and entirely in Joule units on the other (quantum layer), without a bridge theorem. No bridge theorem exists in current C2.

**What would convert FAILED to PASS:**

The minimum additional mathematical structure required to fix g is one of:

1. **An energy-information equivalence $E = \eta I$** with $\eta$ derived from C2 (not available)
2. **A derivation of $\hbar$ from substrate parameters** via the large-N universality conjecture OBS-C1 (unproved)
3. **QFT emergence from candidate C3** producing a renormalizable coupling with a fixed value (OP-14, completely open)

Until one of these three structures is established, g remains a free parameter, and the C2 prediction $\Gamma_\phi = k_{\text{rot}}\omega_{\text{rot}}^2$ remains a one-parameter family of predictions, not a parameter-free prediction.

---

*End of OP-3 Research Report*  
*Date: 2026-07-24*  
*No new postulates introduced. No g redefined. No experimental values assumed.*  
*Verdict: FAILED — g is independent of the current C2 axioms.*
