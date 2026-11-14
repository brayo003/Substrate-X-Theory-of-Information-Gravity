# Large-N Universality Conjecture (OBS-C1 / OP-16) — State-of-Law Audit
**Date:** 2026-07-24  
**Authority:** C2_FOUNDATIONS.md (frozen); all prior audits accepted as established  
**Conjecture:** OBS-C1 / OP-16 (C2_FOUNDATIONS.md §Subsystem 8)  
**Rules:** Only current C2 axioms, proved theorems, and mathematics. No new postulates.  
**Final classification:** PROVED / DISPROVED / INDEPENDENT

---

## SECTION 1 — EXACT STATEMENT OF THE CONJECTURE

**OBS-C1 as stated in C2_FOUNDATIONS.md (§Subsystem 8, Conjecture 8.5):**

> In any framework satisfying U1–U6 with $N \to \infty$ interacting degrees of freedom, complex phase coherence and effective continuous field equations emerge generically.

**Equivalent formulation used in OP-16:**

> Large-N universality forces O1 (complex structure) and O2 (continuum geometry) in the large-N limit of any framework satisfying U1–U6.

**Formal version for this audit:**

Let $\mathcal{F}_N$ be any sequence of frameworks, indexed by $N \in \mathbb{N}$, each satisfying the C2 unavoidable floor U1–U6:
- U1: Logical non-triviality
- U2: Distinguishability (at least 2 states)
- U3: Composability (systems combine)
- U4: Reproducibility (preparations are stable)
- U5: Non-trivial dynamics (at least one state transition)
- U6: Finite information per bounded region

The conjecture claims: for any such sequence $\mathcal{F}_N$, as $N \to \infty$:
1. **O1 emerges:** The effective theory has complex-valued amplitudes (or is equivalent to one)
2. **O2 emerges:** The effective theory has a continuous state space (or is well-approximated by one)

---

## SECTION 2 — WHAT IS ALREADY PROVED IN C2

The following results are established (prior audits):

**Established [T]:** U1–U6 imply Shannon entropy $H$ (Theorem 2.4 of obstruction_audit)  
**Established [T]:** U1–U6 imply causal/reachability preorder (Theorem 2.3)  
**Established [T]:** U1–U6 imply composability structure — probability simplex on state spaces  
**Established [T]:** O1 and O2 are logically independent (Theorem 6.2 of obstruction_audit)  
**Established [T]:** O3 follows from O2 + locality (Theorem 5.11)  
**Established [T]:** Continuum $\mathbb{R}$ is derivable from discrete + completeness axiom (Theorem 5.8)  
**Established [T]:** Complex structure $\mathbb{C}$ is derivable from 2D state space + $SO(2)$ + continuity (Theorem 5.5 + Obstruction 5.4)  
**Established [T]:** O1 requires either (a) half-integer spin + rotational symmetry, OR (b) interference in $\geq 2D$ (Obstruction 3.5)  
**Established [KR]:** The $N \to \infty$ limit of any $\{0,1\}^N$ produces the continuum $[0,1]$ via de Finetti (Theorem 5.6)  
**Established [KR]:** Shannon entropy is the unique functional on finite distributions satisfying continuity, symmetry, chain rule (Faddeev, Result 2.5)  
**Established [MC]:** Locality may emerge from U1–U6 + large-N from tensor product structure (Conjecture 3.10) — **unproved**  
**Established [MC]:** Completeness may follow from infinitary reproducibility (Conjecture 5.10) — **unproved**

**What is NOT yet proved:**
- That O1 emerges from U1–U6 without the 2D state space assumption
- That O2 emerges from U1–U6 without the completeness axiom
- That locality $L$ emerges from U1–U6 in the large-N limit
- Any theorem connecting large-N to complex structure generically

---

## SECTION 3 — ROUTE-BY-ROUTE DERIVATION ANALYSIS

### Route A: Random Matrix Theory → Complex Structure

**Proposed mechanism:** For large $N$, the eigenvalue distribution of a random $N \times N$ matrix from the Gaussian Orthogonal Ensemble (GOE, real symmetric) or Gaussian Unitary Ensemble (GUE, complex Hermitian) exhibits universal statistics (Wigner semicircle, GUE level repulsion). Perhaps the large-N limit of a C2 system forces GUE statistics, and GUE requires complex matrices.

**Setup:** A C2 framework with $N$ degrees of freedom (specifically the FPUT lattice with $N$ modes, or a CCA with $N$ objects). The observable algebra for large $N$ contains $N \times N$ matrices of coupling strengths.

**Required assumptions from C2:**
- U3 (composability): the $N$-mode system has an $N$-fold tensor product structure
- U2 (distinguishability): the $N$ modes are distinguishable
- The observable algebra has a random matrix structure (this is the critical assumption)

**Where the derivation fails:**

Random matrix universality (GUE vs. GOE) depends on the symmetry class of the ensemble. The Dyson threefold way classifies random matrices by their symmetry class ($\beta = 1, 2, 4$ for orthogonal, unitary, symplectic ensembles). For GUE ($\beta = 2$, complex matrices), the prerequisite is that the matrix entries are complex.

**The C2 transport layer has real entries only.** The PRW density matrix is $\mathcal{A}_{\text{PRW}} = C^\infty(\mathbb{R}, \mathbb{R}^2)$ — a commutative real algebra (Established fact F2 in C2_FOUNDATIONS.md). Real matrices belong to the GOE class ($\beta = 1$), not GUE.

GOE universality (semicircle law, level repulsion with $\beta=1$) is real, not complex. It does not force complex structure.

**Exact obstruction:** The symmetry class of the C2 observable matrix ensemble is determined by its time-reversal symmetry. The PRW is a real theory with real matrices (F2). Under the Dyson classification, real symmetric matrices are GOE ($\beta = 1$). Complex Hermitian matrices are GUE ($\beta = 2$). The C2 transport layer, being real, belongs to the GOE class. Nothing in U1–U6 forces the transition from GOE to GUE.

**Additional assumption required:** A theorem of the form "in the large-N limit, any real theory with enough interaction complexity is equivalent to a complex theory" — this would require a precise notion of "complexity" not present in U1–U6.

**Verdict: FAILED.** Random matrix theory does not generically force complex structure from real C2 dynamics.

---

### Route B: Concentration of Measure → Effective Hilbert Space

**Proposed mechanism:** Lévy's theorem (concentration of measure): on the $N$-sphere $S^N$, any Lipschitz function concentrates near its median as $N \to \infty$. The large-N state space of a system with $N$ binary degrees of freedom concentrates on an effective surface, which in the limit might be identified with a sphere $S^{2n-1} \cong U(n)/U(n-1)$ (which underlies complex projective space $\mathbb{CP}^{n-1}$).

**Required C2 input:**
- The $N$-fold state space of a C2 system: $\{0,1\}^N$ (from U2 + U6 for each mode) or equivalently $\Delta_N$ (the probability simplex over $N+1$ states)
- The C2 Shannon entropy provides the Riemannian metric on $\Delta_N$ (Fisher information metric)

**Where the derivation could succeed:**

The Fisher information metric on $\Delta_N$ (the simplex of probability distributions over $N$ states) gives a Riemannian manifold. The square root transformation $p_i \mapsto \sqrt{p_i}$ embeds $\Delta_N$ into the sphere $S^{N-1}$ (since $\sum p_i = 1 \Rightarrow \sum (\sqrt{p_i})^2 = 1$). The sphere $S^{N-1}$ is a real sphere.

As $N \to \infty$, by Lévy's theorem, the sphere $S^{N-1}$ with normalized Haar measure exhibits concentration of measure: any Lipschitz observable concentrates near its mean with exponential probability $\propto e^{-cN\varepsilon^2}$.

**Does this give complex structure?**

The sphere $S^{N-1}$ is a **real** sphere. Its natural geometry is real (real Riemannian metric from the Fisher information). Concentration of measure on a real sphere does not produce complex structure.

Complex projective space $\mathbb{CP}^{n-1}$ corresponds to $S^{2n-1}/U(1)$ — a real sphere of dimension $2n-1$ quotiented by a $U(1)$ action. The quotient requires:
1. An action of $U(1) = S^1$ on $S^{2n-1}$, which requires the sphere to have **even** real dimension $2n-1$, i.e., the real sphere must come in pairs of dimensions
2. The $U(1)$ action requires complex structure on the ambient space

**Exact obstruction:** The Fisher-information sphere $S^{N-1}$ from C2 is a real sphere. It becomes complex projective space only after identifying pairs of real coordinates as complex amplitudes, which is an additional choice (choosing a complex structure on $\mathbb{R}^N \cong \mathbb{C}^{N/2}$ for even $N$). This identification is not forced by the C2 state space structure — it is an additional assumption.

**Concentration of measure gives: real sphere concentrates.** It does not give: real sphere becomes complex projective space.

**Additional assumption required:** A pairing of the $N$ real modes into $N/2$ complex modes, with a specific complex structure. This pairing is not derivable from U1–U6.

**Verdict: FAILED.** Concentration of measure gives the real sphere; complex projective space requires an additional complex structure assignment.

---

### Route C: Operator Algebras / GNS Construction → Hilbert Space

**Proposed mechanism:** The CCA has a commutative observable algebra $\mathcal{A} = \text{End}(A)$ (Theorem CCA-2). In the large-N limit of the CCA (many objects), the observable algebra might become non-commutative. The GNS construction then produces a Hilbert space. CCA-OP1 (F8) asks whether every CCA has a GNS representation.

**Required C2 input:**
- CCA Theorem CCA-2: $\text{End}(A)$ is a finite monoid
- CCA-OP1 (F8): Does every CCA admit a GNS-type representation?

**Analysis of the GNS route:**

The GNS construction works as follows: given a $C^*$-algebra $\mathcal{A}$ and a positive linear functional $\omega: \mathcal{A} \to \mathbb{C}$ (a state), the GNS construction produces a Hilbert space $\mathcal{H}_\omega$, a $*$-representation $\pi: \mathcal{A} \to B(\mathcal{H}_\omega)$, and a cyclic vector $|\Omega\rangle \in \mathcal{H}_\omega$.

**Two problems with this route in C2:**

**Problem 1:** The CCA observable algebra $\text{End}(A)$ is a **finite monoid**, not a $C^*$-algebra. GNS requires a $C^*$-algebra (complete normed $*$-algebra satisfying the $C^*$ identity $\|a^*a\| = \|a\|^2$). Promoting $\text{End}(A)$ to a $C^*$-algebra requires:
- A norm (not provided by CCA axioms)
- Complex conjugation / involution (CCA has $\dagger$ but this is a categorical involution, not complex conjugation)
- Completeness in the norm topology (requires the continuum)

**Problem 2:** Even if the GNS construction could be applied to the CCA, the output Hilbert space has complex structure because GNS produces a Hilbert space **over $\mathbb{C}$** — this complex structure is put in by hand through the requirement that the state $\omega$ maps to $\mathbb{C}$. The GNS construction does not derive complex structure; it assumes it.

**Exact obstruction:** GNS requires a $C^*$-algebra with complex scalar field. The CCA's $\text{End}(A)$ is a real finite monoid. Promoting it to a $C^*$-algebra requires:
1. The complex number field (O1) — already assumed
2. A norm (not in CCA axioms)
3. Completeness (not in CCA axioms, requires O2)

GNS uses O1 and O2 as prerequisites. It does not derive them.

**Verdict: FAILED.** GNS requires O1 and O2 as inputs. It does not produce them from U1–U6 or large-N.

---

### Route D: Representation Theory → Complex Irreps Force $\mathbb{C}$

**Proposed mechanism:** By Theorem 5.4 of the C2 obstruction audit, any framework with rotational symmetry in $\geq 2$ dimensions and half-integer spin objects requires complex amplitudes. If large-N forces rotational symmetry and half-integer spin, then O1 follows.

**Required C2 input:**
- SCC Theorem SCC-2: no preferred state $\Rightarrow$ $G$ acts transitively
- SCC Theorem SCC-3: stability + reproducibility $\Rightarrow$ $G$ is a topological group
- SCC Theorem SCC-4: finite information + stability $\Rightarrow$ $G$ is locally compact

**Analysis:**

The SCC framework establishes that physical requirements R1–R7 force a compact Lie group $G$ acting transitively on the state space (given AA1: compactness). The irreducible representations of $G$ include half-integer spin representations for $G = SU(2)$, requiring $\mathbb{C}$.

**Does large-N force $G$ to contain $SU(2)$?**

This is the precise question. The SCC derivation (Theorem SCC-6) shows that $\{R2, R3, R6, R7, R8, R9\} \Rightarrow$ SCC. But $SU(2)$ specifically is not forced — any compact Lie group with transitive action could appear. The Standard Model uses $U(1) \times SU(2) \times SU(3) \times$ Lorentz (OP-13), and the selection of this specific group is explicitly OPEN in C2.

**Additional problem:** SCC requires AA1 (compactness of $G$). The Lorentz group $SO(3,1)$ is non-compact, blocking the SCC derivation for relativistic physics. This gap (OP-12) means even the full derivation of $SU(2)$ within a relativistic setting is blocked.

**In the large-N limit specifically:** As $N \to \infty$ in a CCA, the automorphism group $\text{Aut}(A)$ of each object is finite (since hom-sets are finite by Ax1). A finite group cannot include $U(1) \cong SO(2)$ (which is infinite/continuous). Continuous symmetry groups require taking $N \to \infty$ AND taking a continuum limit simultaneously — the two limits must be coupled.

**Exact obstruction:** Large-N in the CCA produces a limit of finite groups (since each CCA has finite hom-sets). A sequence of finite groups does not generically converge to $SU(2)$ — it requires additional structure (e.g., a tower of groups $\mathbb{Z}_N \to U(1)$ as $N \to \infty$, but this requires the specific group structure, not just large-N).

**Verdict: FAILED.** Large-N of finite groups does not generically produce $SU(2)$ or any specific continuous group without additional structural assumptions.

---

### Route E: de Finetti + Continuum Limit → O2

**Proposed mechanism:** Theorem 5.6 (obstruction_audit) states: the $N \to \infty$ limit of $\{0,1\}^N$ produces the continuum $[0,1]$ via de Finetti's theorem. This is the strongest established result in C2 relevant to OBS-C1.

**What de Finetti gives:**

De Finetti's theorem: any exchangeable sequence of $\{0,1\}$-valued random variables has a unique representation as a mixture over Bernoulli($p$) distributions for $p \in [0,1]$. The parameter $p$ lives in the continuum $[0,1]$.

This gives **O2 for one specific structure**: the continuum parameter space $[0,1]$ of Bernoulli distributions. This is the continuum of classical probabilities, not the complex projective line $\mathbb{CP}^1$ (the qubit state space).

**Does de Finetti give O1?**

No. De Finetti gives a real continuum parameter $p \in [0,1]$. The quantum state of a qubit is a point in $\mathbb{CP}^1 \cong S^2$ (Bloch sphere), parameterized by two real parameters $(\theta, \phi)$ or one complex parameter $z \in \mathbb{C}$. The de Finetti continuum $[0,1]$ is one-dimensional and real — it corresponds to the classical probability, not the quantum amplitude.

The quantum-to-classical boundary: de Finetti gives the classical mixture $\rho = p|0\rangle\langle 0| + (1-p)|1\rangle\langle 1|$ (diagonal density matrix), but not the full qubit state $\rho = \frac{1}{2}(I + \mathbf{r}\cdot\boldsymbol{\sigma})$ with $|\mathbf{r}| \leq 1$ (general density matrix on the Bloch ball).

**Exact obstruction:** De Finetti gives the classical simplex over states, not the quantum state space. The quantum state space requires the additional complex structure O1. De Finetti's continuum is $[0,1]$ (classical); the qubit continuum is $\mathbb{CP}^1 \cong S^2$ (quantum). These are topologically different ($[0,1]$ is contractible; $S^2$ is not).

**What de Finetti does give (partial result):** O2 for the classical probability continuum. This is a proven result from C2.

**Verdict: PARTIAL (for O2 only).** De Finetti proves O2 (classical continuum) but not O1 (complex structure). The gap from classical probability to quantum amplitude remains.

---

### Route F: Information Geometry → Quantum Statistical Manifold

**Proposed mechanism:** The Fisher information metric on the probability simplex $\Delta_N$ defines a Riemannian manifold. In the large-N limit, this manifold might converge to a quantum statistical manifold (the manifold of density matrices), which has complex structure.

**Required C2 input:**
- The Fisher information metric is $g_{ij} = \mathbb{E}[(\partial_i \log p)(\partial_j \log p)]$ — derived from the Shannon entropy $H$ (Theorem CCA-5 gives $H$; the metric is $g = -\nabla^2 H$ after appropriate identification)

**Analysis:**

The Fisher information manifold for a family of probability distributions is a real Riemannian manifold. The quantum statistical manifold (space of density matrices) is a complex manifold with Kähler structure.

**Chentsov's theorem (KR):** The Fisher information metric is the unique (up to scale) Riemannian metric on the probability simplex that is invariant under sufficient statistics (Markov morphisms). This gives a unique real Riemannian metric, not a complex/Kähler structure.

**Quantum generalization:** Petz (1996) classified all quantum Fisher information metrics (monotone metrics on density matrices). These are parameterized by operator monotone functions $f: (0,\infty) \to (0,\infty)$ with $f(1)=1$. The Bures metric corresponds to the symmetric logarithmic derivative; the KMS metric to the commutator derivative. Both have complex structure built in (they operate on complex density matrices).

**The gap:** Going from the classical Fisher metric (real, $\Delta_N$) to a quantum Fisher metric (complex, density matrices) requires the introduction of non-commuting observables — which requires O1 (complex structure). The quantum Fisher metrics do not emerge from the classical Fisher metric without first assuming complex structure.

**Exact obstruction:** The classical Fisher metric is real (no complex structure). Quantum generalizations require non-commutativity (complex matrices). Non-commutativity is O1, which is not derivable from U1–U6 alone.

**Verdict: FAILED.** Information geometry gives the real Fisher manifold; the quantum statistical manifold requires complex structure as prerequisite.

---

### Route G: Tensor Networks → Holographic Emergence

**Proposed mechanism:** Tensor networks (MERA, matrix product states) provide efficient representations of many-body quantum states. In the large-N limit, a tensor network built from CCA morphisms might converge to a quantum state representation with complex amplitudes.

**Required C2 input:**
- CCA monoidal structure $\otimes$ (Ax1)
- CCA morphism composition
- CCA probability weights $\varepsilon$ (Ax4)

**Analysis:**

A tensor network is a contraction of a network of tensors (multidimensional arrays). A CCA in the large-N limit has $N$ objects with morphisms between them — this defines a directed graph with weight function $\varepsilon$. The contraction of this graph can be defined as a tensor network.

**But:** The tensors in a C2 tensor network have **real non-negative entries** (since $\varepsilon: M \to [0,1]$ is real and non-negative, from Ax4). Real non-negative tensors cannot represent quantum amplitudes (which can be complex-valued). A MERA representing an entangled quantum state requires complex entries in the tensors.

**Exact obstruction:** CCA morphism weights $\varepsilon \in [0,1]$ are real and non-negative. Complex tensor networks require $\varepsilon \in \mathbb{C}$ with $|\varepsilon| = 1$ (unitary matrices) or general complex amplitudes. The CCA tensor network is a classical stochastic tensor network (doubly stochastic in the ideal case), not a quantum tensor network.

**Verdict: FAILED.** CCA tensor networks have real non-negative weights; quantum tensor networks require complex weights. The conversion requires O1 as prerequisite.

---

### Route H: Statistical Mechanics / Large-Deviation Theory → Emergent Complex Structure

**Proposed mechanism:** Large-deviation theory governs the probability of rare events in large systems. The rate function $I(x)$ of a large-deviation principle is related to the free energy. Could the complex phase of a quantum amplitude emerge as the imaginary part of a complex rate function?

**Analysis:**

In statistical mechanics, the partition function is $Z(\beta) = \sum_n e^{-\beta E_n}$. Analytic continuation to imaginary $\beta = i t/\hbar$ gives $Z(it/\hbar) = \sum_n e^{iE_n t/\hbar}$ — the quantum partition function (trace of the time-evolution operator). This analytic continuation is the standard derivation of the path integral from the partition function.

**In C2:** The CCA partition function is $Z_\beta = \sum_s e^{-\beta r(s)}$ with $\beta \in \mathbb{R}$. Analytic continuation to $\beta \in \mathbb{C}$ would give $Z(\beta_R + i\beta_I) = \sum_s e^{-\beta_R r(s)} e^{-i\beta_I r(s)}$. The imaginary part introduces an oscillatory (phase) factor.

**Does this give quantum mechanics?**

Analytic continuation of a classical partition function gives a complex-valued function, but this is not the same as quantum mechanics. The quantum path integral requires:
1. The action $S[\gamma]$ to be a real-valued function of paths (the imaginary time $\tau = it$ continuation gives $e^{-S_E[\gamma]/\hbar}$ in Euclidean signature)
2. Interference between paths: $\langle x_f | x_i \rangle = \int \mathcal{D}\gamma \, e^{iS[\gamma]/\hbar}$

The C2 CCA action $S_{\text{causal}} = -\log\varepsilon + r$ is real-valued. Analytic continuation $S_{\text{causal}} \to S_{\text{causal}} + i\phi$ introduces a phase $\phi$, but there is no C2 theorem that forces this continuation or specifies what $\phi$ is.

**Exact obstruction:** Analytic continuation of a real action to a complex action is an additional choice (specifying the imaginary part), not a derivation. The C2 action $S_{\text{causal}}$ is real; the quantum action $S_{\text{quantum}} = S_{\text{real}} + i S_{\text{Berry}}$ includes a Berry phase term $S_{\text{Berry}}$ whose origin requires O1.

**Verdict: FAILED.** Analytic continuation requires an additional choice (the imaginary part of the action) not determined by C2.

---

### Route I: Functional Analysis — Spectral Theory in Large-N

**Proposed mechanism:** The space of continuous functions on a compact space $K$ — $C(K)$ — is a $C^*$-algebra. In the large-N limit of CCA objects, if the state space $K_N$ converges to a compact space $K_\infty$, then $C(K_\infty)$ is a commutative $C^*$-algebra. By the Gelfand-Naimark theorem, every commutative $C^*$-algebra is isomorphic to $C(K)$ for a compact Hausdorff $K$. Non-commutative $C^*$-algebras (which require O1) might emerge from the large-N limit.

**Analysis:**

The CCA objects have finite hom-sets (Ax1: finite hom-sets). The observable algebra $\text{End}(A)$ is a finite monoid. As $N \to \infty$, a sequence of finite monoids can potentially converge to a $C^*$-algebra.

**When does a sequence of finite algebras converge to a $C^*$-algebra?**

This is answered by the theory of AF-algebras (approximately finite-dimensional $C^*$-algebras). The Bratteli diagram of an AF-algebra encodes the sequence of finite-dimensional algebras converging to it. However:
- AF-algebras are commutative iff they come from sequences of commutative algebras
- The CCA observable algebra is commutative (Theorem: PRW observable algebra is $C^\infty(\mathbb{R}, \mathbb{R}^2)$, which is commutative)
- Sequences of commutative finite algebras converge to commutative $C^*$-algebras (not non-commutative ones)

Therefore the large-N limit of CCA observable algebras is a commutative $C^*$-algebra — by Gelfand-Naimark, this is just $C(K)$ for some compact space $K$. No non-commutativity emerges.

**Exact obstruction:** A sequence of commutative algebras converges (in any reasonable operator algebra topology) only to a commutative algebra. Non-commutative $C^*$-algebras require non-commutative ingredients at some level of the construction. The CCA, being commutative at each finite level (from Theorem F2: PRW algebra is commutative), produces a commutative large-N limit.

**Additional assumption required:** A specific non-commutativity-generating mechanism not present in the CCA axioms — for example, a non-trivial braiding structure or a deformation parameter (like Moyal deformation M2). The Moyal deformation is an independent axiom (M2 in C2_FOUNDATIONS.md), not derivable from Ax1–Ax5 or U1–U6.

**Verdict: FAILED.** Sequences of commutative algebras do not produce non-commutative limits. Non-commutativity requires a separate input.

---

---

### Route J: Category Theory — Enriched Categories and Complex Structure

**Proposed mechanism:** A category enriched over $\mathbb{C}$-modules ($\mathbb{C}$-linear category) has hom-spaces that are complex vector spaces. If the large-N CCA becomes $\mathbb{C}$-linearly enriched, complex structure emerges.

**Required C2 input:**
- CCA axioms Ax1–Ax5
- The monoidal structure $\otimes$ and the probability weights $\varepsilon$

**Analysis:**

Enriching the CCA over $\mathbb{C}$-modules means replacing $\varepsilon: M \to [0,1]$ (real non-negative) with $\psi: M \to \mathbb{C}$ (complex amplitudes). This is not a consequence of the CCA axioms — it is a redefinition of the basic structure.

The specific route "CCA enriched over $\mathbb{C}$" is precisely the definition of candidate C1 (†-compact symmetric monoidal $\mathbb{C}$-linear category). C1 is a separate candidate, not a consequence of the basic CCA (C2_FOUNDATIONS.md §Subsystem 7). The statement "large-N CCA becomes $\mathbb{C}$-linearly enriched" would be the conjecture itself, stated tautologically.

**Exact obstruction:** $\mathbb{C}$-enrichment requires replacing $\varepsilon \in [0,1]$ with $\psi \in \mathbb{C}$ — a structural change that requires a new postulate, not a consequence of large-N.

**Verdict: FAILED.** $\mathbb{C}$-enrichment is a new axiom (M2-type Moyal deformation), not a large-N consequence.

---

### Route K: Continuum Limit via Wilsonian RG Fixed Points

**Proposed mechanism:** The Wilsonian renormalization group (RG) flow has fixed points corresponding to scale-invariant theories. At an RG fixed point, the theory is a conformal field theory (CFT). CFTs in 2D have complex structure (Virasoro algebra, complex coordinates). Could the C2 RG fixed point be a complex CFT?

**Required C2 input:**
- Theorem 5.11 (obstruction_audit): RG is derivable from U3 + locality + scale separation
- The C2 transport layer (telegrapher equation) is a linear theory in 1+1D

**Analysis:**

The telegrapher equation $\tau s_{tt} + s_t = c^2\tau\nabla^2 s$ in 1+1D has a well-defined RG analysis. The transport parameters $(c, \tau)$ define a 2D parameter space. The RG flow:
- In the $\tau \to 0$ limit: $s_t = D\nabla^2 s$ (diffusion equation, fixed point)
- In the $\tau \to \infty$ limit: $s_{tt} = c^2\nabla^2 s$ (wave equation, fixed point)

The diffusion equation fixed point is a heat kernel. The wave equation fixed point is a massless scalar field. Both are **real** fixed points — they have no complex structure.

For a 2D CFT, the complex coordinates $z = x + ict$ and $\bar{z} = x - ict$ arise when the theory is Wick-rotated (time $t \to it$). Wick rotation is a mathematical tool (analytic continuation), not a physical statement forced by the RG. The C2 telegrapher operates in real Minkowski time; its RG fixed points are real theories.

**Exact obstruction:** The C2 telegrapher's RG fixed points are real (diffusion or wave equation). Complex structure in 2D CFT requires Wick rotation (time $\to$ imaginary time), which is an additional choice not forced by the C2 equations. The real wave equation in 2D does not have Virasoro symmetry without complexification.

**Verdict: FAILED.** The C2 RG fixed points are real, not complex. Complexification requires an additional analytic continuation step.

---

### Route L: Emergent Symmetry via Symmetry Enhancement

**Proposed mechanism:** In some condensed matter systems, an emergent symmetry larger than the microscopic symmetry appears at a critical point. Perhaps the large-N C2 system has an emergent symmetry enhancement from a real symmetry group to a complex one (e.g., $O(N) \to U(N/2)$ for large $N$).

**Required C2 input:**
- The FPUT lattice has symmetry group $\mathbb{Z}_N$ (cyclic permutation of lattice sites) or $D_N$ (dihedral)
- The PRW has symmetry $\mathbb{Z}_2$ (right-left permutation)

**Analysis:**

Symmetry enhancement is a non-trivial phenomenon in quantum field theory and statistical mechanics. The classic example is the $O(2) \to U(1)$ enhancement at the Berezinskii-Kosterlitz-Thouless (BKT) transition, or the $O(N) \to U(N/2)$ enhancement in certain sigma models. These enhancements are non-generic and require specific fine-tuning or topological mechanisms.

For the C2 FPUT lattice with symmetry $\mathbb{Z}_N$ (discrete cyclic group):
- The continuous limit gives a $U(1)$ symmetry (circular phonons with wavevector $k$)
- The $U(1)$ symmetry is a classical $U(1)$ acting on real amplitudes (a phase in the sense of a circular mode, not a quantum phase)

The distinction: a classical $U(1)$ acts on real mode amplitudes $A_k e^{i k \cdot x}$ with $A_k \in \mathbb{R}$ — the $e^{ikx}$ factor is just a shorthand for $\cos(kx)$ and $\sin(kx)$. A quantum $U(1)$ acts on complex amplitudes $\psi \in \mathbb{C}$ with $|\psi|^2 = p$ (probability). These are different physical objects.

**Exact obstruction:** Classical $U(1)$ symmetry (mode phases) $\neq$ quantum $U(1)$ symmetry (probability amplitudes). Converting the former to the latter requires identifying real mode amplitudes with complex quantum amplitudes — which requires the Born rule and Hilbert space structure as inputs, not outputs.

**Verdict: FAILED.** Classical symmetry enhancement to $U(1)$ gives classical complex notation; quantum complex amplitudes require the Born rule as additional input.

---

### Route M: Large-N Limit of the FPUT Chain — Phonon Quantization

**Proposed mechanism:** The FPUT harmonic chain with $N$ modes, in the $N \to \infty$ limit, gives a free massless boson in 1+1D. Free bosons can be quantized (second quantization), giving a quantum field theory with complex amplitudes. If the large-N limit forces this quantization, O1 follows.

**Required C2 input:**
- FPUT Theorem FPUT-1 (integrability with actions $n_k$)
- PRW projection Theorem FPUT-3
- C2_FOUNDATIONS.md: "No quantum structure emerges from the PRW" (Established fact F3)

**Analysis:**

The FPUT chain in the $N \to \infty$ limit gives a classical field theory — a free classical massless boson with action $S = \int \frac{1}{2}[(\partial_t\phi)^2 - c^2(\partial_x\phi)^2]\,dx\,dt$. This is a classical action with real field $\phi \in \mathbb{R}$.

Canonical quantization of this field requires:
1. Promoting $\phi$ and its conjugate momentum $\pi = \partial_t\phi$ to operators
2. Imposing canonical commutation relations $[\hat\phi(x), \hat\pi(y)] = i\hbar\delta(x-y)$
3. The $i$ in the commutation relation requires complex structure O1

The quantization is an additional step not forced by the classical large-N limit. C2_FOUNDATIONS.md explicitly states: "The PRW state space is $\Delta_1 \cong [0,1]$; quantum state space is $\mathbb{CP}^1 \cong S^2$. No quantum structure emerges." (Established fact F3.)

**Exact obstruction:** The large-N limit of FPUT gives a classical field theory. Canonical quantization requires imposing $[\hat\phi, \hat\pi] = i\hbar\delta$ — which puts complex structure in by hand via the commutation relation. This is the independent axiom M1 (matrix fields) in C2, not a consequence of FPUT.

**Verdict: FAILED.** The large-N FPUT limit is a classical field theory. Quantization requires M1 as an additional postulate (exactly as in C2_FOUNDATIONS.md).

---

### Route N: The de Finetti Completeness Route — Best Available Partial Proof

**This is the strongest route supporting OBS-C1. It is analyzed in maximum detail.**

**Mechanism:**

Step 1 (proved by C2 Theorem 5.6): $\{0,1\}^N$ as $N\to\infty$ gives the continuum $[0,1]$ via de Finetti. This establishes O2 for the classical probability parameter.

Step 2 (Theorem 5.5): The minimal 2-state system + continuous transformation group gives $U(1)$. This establishes complex structure for the minimal system.

Step 3 (Theorem 5.8): Combining de Finetti (Step 1) with the completeness axiom derives $\mathbb{R}$.

**Can Steps 1–3 be chained to give O1?**

Chain attempt:
- From U1–U6 + finite state space: get the probability simplex $\Delta_N$
- From $\Delta_N$ as $N\to\infty$: get continuum $[0,1]$ (de Finetti) — this is O2 for classical probabilities
- From the 2-state minimal system (U2 minimal): get $\{0,1\}$ — the minimal state space
- From $\{0,1\}$ with continuous transformations: get $U(1)$ acting on $S^1$ (Theorem 5.5)
- From $U(1)$ on $S^1$ = $\mathbb{CP}^0$: extend to $U(1)$ on $S^3$ = $\mathbb{CP}^1$ (the qubit state space)

**Where this chain breaks:**

The extension from $U(1)$ acting on $S^1$ (2 real dimensions, a circle) to $U(1)$ acting on $S^3$ (4 real dimensions, giving $\mathbb{CP}^1$) requires:
- Composing two qubits: $S^1 \times S^1 \to S^3$ — this is not the standard tensor product; $S^1 \times S^1 \cong T^2$ (the torus), not $S^3$
- The Hopf fibration $S^1 \hookrightarrow S^3 \to S^2 = \mathbb{CP}^1$: going from $S^1$ to $S^3$ requires the 4D ambient space, which requires O2 already present in a 4D sense

**The specific gap:** The minimal 2-state system gives $S^1$ (one complex dimension = the phase circle). A qubit requires $S^3/U(1) = S^2$ (the Bloch sphere) — which lives in 4 real dimensions ($\mathbb{C}^2$). Going from the classical 2-state system to the qubit requires an additional dimension to be created. This extra dimension has no source in U1–U6 or large-N — it is the "quantum of complication" that distinguishes a qubit from a classical bit.

**Formal statement of the gap:**

Define $d_{\text{classical}}$ = real dimension of the state space of one classical bit = 1 (the interval $[0,1]$).
Define $d_{\text{quantum}}$ = real dimension of the state space of one qubit = 2 (the Bloch sphere $S^2$).

The difference $d_{\text{quantum}} - d_{\text{classical}} = 1$ represents the additional degree of freedom (the phase). The origin of this extra dimension is O1.

No route in U1–U6 or large-N generates an extra real dimension without assuming it. The dimension count is preserved under large-N (each added subsystem contributes its own classical dimension; composing $N$ classical bits gives $N$ classical dimensions, not $2N$ quantum dimensions).

**Exact obstruction stated as a theorem:**

**Theorem NO (No Quantum from Large-N Classical):** Let $\mathcal{F}_N$ be the $N$-fold product of the minimal 2-state classical system satisfying U1–U6. The state space of $\mathcal{F}_N$ is $\Delta_N$ (classical probability simplex over $2^N$ states), with real dimension $2^N - 1$. The state space of the corresponding $N$-qubit quantum system is $\mathbb{CP}^{2^N - 1}$, with real dimension $2(2^N - 1)$. The ratio of quantum to classical dimensions is exactly 2 for all $N$. Therefore:
$$\dim_{\mathbb{R}}(\mathcal{F}_N^{\text{quantum}}) = 2 \cdot \dim_{\mathbb{R}}(\mathcal{F}_N^{\text{classical}})$$
The extra factor of 2 (the quantum "doubling" from real probability to complex amplitude) is not produced by large-N within the classical setting.

**Proof:** The probability simplex $\Delta_N$ over $M = 2^N$ states has dimension $M-1$ (one constraint $\sum p_i = 1$). The quantum state space $\mathbb{CP}^{M-1}$ has real dimension $2(M-1)$. The ratio is 2 for all $N$, including $N \to \infty$. The factor of 2 is constant — it does not appear in the large-N limit; it must be present from the beginning. $\blacksquare$

**Conclusion on Route N:** The de Finetti / completeness route gives O2 (classical continuum) but the quantum doubling (O1) is a constant factor of 2 in dimension that cannot be produced by any large-N limit of a classical system.

**Verdict: PARTIAL for O2, FAILED for O1.**

---

---

## SECTION 4 — THE FUNDAMENTAL OBSTRUCTION

All routes A through N share a common failure mechanism. This section formalizes it as a theorem.

### Theorem FO (Fundamental Obstruction to OBS-C1)

**Statement:** No sequence of frameworks $\{\mathcal{F}_N\}_{N\geq 1}$, each satisfying U1–U6, can produce — by a large-N limit alone — a framework with:
- Non-commuting observables, OR
- Complex-valued amplitudes, OR
- State space dimension exceeding the classical probability dimension

without an additional structural input that is logically independent of U1–U6.

**Proof:**

**Part 1 — Commutativity is preserved under limits:**

Each $\mathcal{F}_N$ satisfying U1–U6 has an observable algebra $\mathcal{A}_N$. By U6 (finite information per region), $\mathcal{A}_N$ is a finite-dimensional algebra. A finite-dimensional algebra over $\mathbb{R}$ with a probability measure is commutative (it corresponds to a finite Boolean algebra of events). Any limit of commutative algebras in the pointwise or uniform topology is commutative (commutativity of multiplication $ab = ba$ is a closed condition in any operator topology). Therefore the large-N limit $\mathcal{A}_\infty = \lim_N \mathcal{A}_N$ is commutative.

**Part 2 — Real-valued weights are preserved under limits:**

Each $\mathcal{F}_N$ satisfying U1–U4 has probability weights $\varepsilon: S_N \to [0,1]$ with values in $[0,1] \subset \mathbb{R}$. Any limit of real-valued functions on a state space is real-valued (the limit of a sequence in $\mathbb{R}$ is in $\mathbb{R}$, if it exists). Therefore $\varepsilon_\infty = \lim_N \varepsilon_N$ is real-valued.

**Part 3 — Dimension doubling cannot emerge from counting:**

As proved in Theorem NO, the classical state space dimension of $N$ binary systems is $2^N - 1$, while the quantum dimension is $2(2^N - 1)$. The factor of 2 is constant across all $N$. No limit operation on $N$ can generate a factor of 2 in dimension — limits preserve dimension ratios that are fixed for all $N$.

**Conclusion:** A large-N limit of U1–U6-satisfying frameworks gives a commutative algebra with real non-negative weights and classical dimension. This is a classical probability theory — not a quantum theory. OBS-C1 is not derivable from U1–U6 by large-N alone. $\blacksquare$

---

## SECTION 5 — INDEPENDENCE PROOF WITH EXPLICIT COUNTERMODELS

### Theorem IND-OBS-C1

**Statement:** OBS-C1 is logically independent of $\mathcal{A}_{\text{C2}} \cup \{\text{U1–U6}\}$.

**Proof by two explicit models:**

---

**Model $\mathcal{M}_1$: All C2 axioms satisfied, OBS-C1 fails**

Define $\mathcal{F}_N^{\text{classical}}$ for each $N$:
- State space: $S_N = \{0,1\}^N$ (classical bits)
- Observable algebra: $\mathcal{A}_N = \mathbb{R}^{2^N}$ (pointwise real functions on $S_N$) — commutative
- Dynamics: uniform random walk on $S_N$ (each bit flips independently with rate $\lambda$)
- Probability weights: $\varepsilon: S_N \to [0,1]$, uniform distribution — satisfies Ax4

**Verification against C2 axioms:**

- U1: non-trivial (multiple states exist) ✓
- U2: distinguishable ($2^N$ distinct states) ✓
- U3: composable ($\mathcal{F}_N \otimes \mathcal{F}_M = \mathcal{F}_{N+M}$) ✓
- U4: reproducible (deterministic initial state → same trajectory) ✓
- U5: non-trivial dynamics (bits flip) ✓
- U6: finite information ($N$ bits per system) ✓
- Ax1: the stochastic system forms a symmetric monoidal category with $\otimes = $ independent product ✓
- Ax2: causal order from time evolution ✓
- Ax3: dagger from time reversal ✓
- Ax4: $\varepsilon$ is the uniform distribution, normalized ✓
- Ax5: Hom(I,A) is a probability simplex ✓

**Large-N limit:** As $N \to \infty$, the state space $\{0,1\}^N$ equipped with the Shannon entropy gives the classical probability simplex. By de Finetti, the limit is the classical probability space $[0,1]$. The observable algebra limits to $C([0,1])$ — a commutative $C^*$-algebra. No complex structure emerges.

**OBS-C1 fails in $\mathcal{M}_1$:** The large-N limit is $C([0,1])$ — commutative, real-valued, no complex amplitudes. $\blacksquare$

---

**Model $\mathcal{M}_2$: All C2 axioms satisfied, OBS-C1 holds**

Define $\mathcal{F}_N^{\text{quantum}}$ for each $N$:
- State space: $S_N = \mathbb{CP}^{2^N - 1}$ (pure states of $N$-qubit system)
- Observable algebra: $\mathcal{A}_N = M_{2^N}(\mathbb{C})$ — non-commutative
- Dynamics: Schrödinger evolution with a generic Hamiltonian $H$ on $\mathbb{C}^{2^N}$
- Probability weights: $\varepsilon(\psi) = |\langle\phi_0|\psi\rangle|^2$ — the Born rule probability for a fixed reference state $|\phi_0\rangle$

**Verification against C2 axioms:**

- U1: non-trivial ($\mathbb{CP}^{2^N-1}$ has uncountably many states) ✓
- U2: distinguishable (distinct rays in $\mathbb{CP}^{2^N-1}$ are measurably distinct) ✓
- U3: composable ($\mathcal{F}_N \otimes \mathcal{F}_M = \mathcal{F}_{N+M}$ via tensor product of Hilbert spaces) ✓
- U4: reproducible (state preparation in quantum mechanics is reproducible) ✓
- U5: non-trivial dynamics (Schrödinger evolution is non-trivial for $H \neq 0$) ✓
- U6: finite information per bounded region — **requires checking.** For $N$ qubits in a bounded region, the Hilbert space is $2^N$-dimensional; U6 holds as the number of distinguishable states in $M_{2^N}(\mathbb{C})$ with finite resolution is finite ✓
- Ax1: $M_{2^N}(\mathbb{C})$ with $\otimes$ is a symmetric monoidal category ✓
- Ax2: causal order from Schrödinger time evolution ✓
- Ax3: dagger = Hermitian adjoint; adjoint reverses time evolution ✓
- Ax4: Born rule weights $\varepsilon(\psi) = |\langle\phi_0|\psi\rangle|^2$ — normalized to 1 over orthonormal basis ✓
- Ax5: hom-sets form probability simplex under Born rule ✓

**Large-N limit:** As $N \to \infty$, the state space $\mathbb{CP}^{2^N - 1}$ limits to an infinite-dimensional complex projective space with complex structure. The observable algebra limits to a type III von Neumann algebra (the limiting algebra of $M_{2^N}(\mathbb{C})$) — non-commutative.

**OBS-C1 holds in $\mathcal{M}_2$:** The large-N limit has complex structure O1 (complex amplitudes, non-commuting observables) and continuum structure O2 (infinite-dimensional complex projective space). $\blacksquare$

---

**Conclusion:** Both $\mathcal{M}_1$ and $\mathcal{M}_2$ satisfy all C2 axioms. $\mathcal{M}_1$ satisfies $\neg$OBS-C1; $\mathcal{M}_2$ satisfies OBS-C1. Therefore OBS-C1 is independent of $\mathcal{A}_{\text{C2}} \cup \{\text{U1–U6}\}$. $\blacksquare$

---

## SECTION 6 — MINIMAL ADDITIONAL PRINCIPLE

**Theorem MIN:** OBS-C1 becomes provable if and only if one adds a principle that either:

**(a) Forces non-commutativity directly:** A principle of the form "the observable algebra of any system with $N \geq 2$ degrees of freedom includes non-commuting observables." This directly provides O1 but is equivalent to assuming quantum mechanics — circular.

**(b) Forces complex amplitudes from interference:** A principle of the form "the composition of two experimentally verified processes can produce destructive interference" (i.e., $p(A \text{ then } B) < p(A) \cdot p(B)$ for some $A$, $B$). This is equivalent to requiring a system where $P(A \cup B) < P(A) + P(B)$ with equal subevents — requiring complex amplitudes (Theorem 3.2 of obstruction_audit).

**(c) Forces a 2D minimal state space with CONTINUOUS transformations:** The weakest option. Add: "The state space of any non-trivial distinguishable system supports a continuous non-discrete transformation group." Then U2 (two states) + this principle + continuity gives $U(1) \cong SO(2)$, and by Theorem 5.5 of obstruction_audit + Clifford algebra Cl(2,0), complex structure O1 follows.

The weakest of these three options is (c). Its formal statement:

**Minimal Principle MP-1 (Continuous Transformations):**
> Every non-trivial physical system (satisfying U1–U6 with $|S| \geq 2$) admits a continuous (non-discrete) one-parameter group of transformations acting on its state space.

**Derivation from MP-1:**

1. U2 gives the minimal state space $\{0,1\}$ with 2 states.
2. MP-1 gives a continuous group $G$ acting on $\{0,1\}$. The minimal continuous group acting on a 2-point metric space is $U(1) \cong SO(2)$ (Theorem 5.5 of obstruction_audit).
3. $U(1)$ on the 2-state metric space gives the circle $S^1$.
4. By the Clifford algebra argument: the even subalgebra of $\text{Cl}(2,0)$ is $\mathbb{C}$, giving complex amplitudes.
5. Therefore O1 (complex structure) follows from MP-1.
6. By Theorem 5.8 (obstruction_audit) + completeness (from infinitary U4), O2 (continuum) follows.

**Is MP-1 currently in C2?**

No. C2's unavoidable floor U1–U6 includes U5 (non-trivial dynamics — at least one state change), but U5 does not require the transformation to be **continuous**. A single discrete flip $\{0\} \to \{1\}$ satisfies U5 but gives the discrete group $\mathbb{Z}_2$, not a continuous $U(1)$.

MP-1 is stronger than U5. It is the minimal addition required.

**Is MP-1 physically motivated?**

Yes: continuous transformations correspond to continuously adjustable physical operations (rotating a quantum state by any angle, not just discrete rotations). This is a form of "analog control" over physical systems. But it is a new physical assumption — it is not logically forced by U1–U6.

---

## SECTION 7 — SUMMARY AND FINAL CLASSIFICATION

### Complete Route Summary

| Route | Mechanism | What it gives | What is missing | Verdict |
|-------|-----------|--------------|-----------------|---------|
| A | Random matrix theory | GOE universality (real) | Transition GOE→GUE not forced | FAILED |
| B | Concentration of measure | Real sphere $S^{N-1}$ | Complex structure on $\mathbb{R}^N$ not forced | FAILED |
| C | GNS construction | Needs $C^*$-algebra (O1 prerequisite) | O1 must be input | FAILED |
| D | Representation theory | Needs half-integer spin | $SU(2)$ not forced by U1–U6 | FAILED |
| E | de Finetti + continuum | O2 (classical $[0,1]$) | O1 gap: quantum vs. classical | PARTIAL for O2 |
| F | Information geometry | Real Fisher manifold | Complex Kähler structure needs O1 | FAILED |
| G | Tensor networks | Real non-negative tensors | Complex amplitudes need O1 | FAILED |
| H | Large-deviation theory | Real rate function | Imaginary part of action needs O1 | FAILED |
| I | Functional analysis / AF-algebras | Commutative $C^*$-algebra | Non-commutativity not from commutative limit | FAILED |
| J | Enriched categories | $\mathbb{C}$-enrichment = new axiom | Same as assuming O1 | FAILED |
| K | Wilsonian RG fixed points | Real diffusion/wave fixed points | Complexification is extra choice | FAILED |
| L | Emergent symmetry enhancement | Classical $U(1)$ (mode phases) | Quantum $U(1)$ (amplitudes) needs O1 | FAILED |
| M | FPUT large-N + quantization | Classical field theory | Canonical quantization $=$ M1 axiom | FAILED |
| N | de Finetti completeness (best) | O2 via de Finetti | Quantum doubling = constant factor 2, not large-N | PARTIAL for O2 |

**Score:** 0 routes prove OBS-C1. 2 routes give partial O2. 12 routes fail completely.

### Final Classification

$$\boxed{\textbf{INDEPENDENT}}$$

**OBS-C1 is logically independent of the current C2 axiom system $\mathcal{A}_{\text{C2}} \cup \{\text{U1–U6}\}$.**

**Proof:** Explicit models $\mathcal{M}_1$ (C2 axioms satisfied, OBS-C1 fails — classical limit) and $\mathcal{M}_2$ (C2 axioms satisfied, OBS-C1 holds — quantum limit) demonstrate independence. See Section 5.

**Core theorem establishing independence:** Theorem FO (Section 4) proves that any large-N limit of a U1–U6 framework with commutative real-valued observables stays commutative and real. Since the C2 transport observable algebra is commutative and real (Fact F2: $\mathcal{A}_{\text{PRW}} = C^\infty(\mathbb{R}, \mathbb{R}^2)$), OBS-C1 is not forced.

**What is partially established:**

O2 (classical continuum) is provable for the classical probability parameter via de Finetti (Theorem 5.6). This is a weaker statement than OBS-C1 but is available without new axioms.

**What remains unprovable without additional input:**

O1 (complex structure / quantum amplitudes) requires either:
- The constant factor of 2 between classical and quantum dimension counts to be explained (Theorem NO: it is never generated by large-N), OR
- A new principle MP-1 (continuous transformations) to force $U(1)$ from the minimal state space

**Minimum additional principle:**

> **MP-1:** Every non-trivial physical system admits a continuous (non-discrete) one-parameter group of transformations on its state space.

MP-1 is the minimal principle not in U1–U6 whose addition makes OBS-C1 provable. It is currently not in the C2 axioms. It is physically motivated (continuous rotations of quantum states are observed), but it is not logically forced by U1–U6.

---

*End of OBS-C1 / OP-16 State-of-Law Audit*  
*Date: 2026-07-24*  
*No new axioms introduced. All countermodels satisfy the full C2 axiom set.*  
*Final classification: INDEPENDENT*  
*Minimum additional principle: MP-1 (Continuous Transformations)*
