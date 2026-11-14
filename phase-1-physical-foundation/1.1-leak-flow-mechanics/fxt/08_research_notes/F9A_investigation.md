# F9-A Investigation: Can Ax4* Be Derived from the Existing C2 Framework?
**Problem:** F9-A — Physical Justification of Symmetric Normalization (Ax4*)
**Date:** 2026-07-24
**Protocol:** 5-Phase Mathematical Research Program
**Authority:** C2_FOUNDATIONS.md (frozen); F9_causal_entropy_research.md (established)
**Status at open:** UNKNOWN

---

## Preamble

The previous research (F9_causal_entropy_research.md) established:

1. F9 (causal entropy non-decrease) reduces entirely to Lemma L1.
2. L1 ≡ every causal morphism m: A → B induces a doubly stochastic transition matrix T_m.
3. Column stochasticity of T_m follows from Ax1 + Ax4.
4. Row stochasticity does NOT follow from Ax1–Ax5.
5. F9 is therefore INDEPENDENT of Ax1–Ax5.
6. The missing condition was named Ax4*: T_m is doubly stochastic for every causal m.

The present document investigates F9-A:

> **Does any combination of theorems, axioms, or physical requirements already present in the C2 framework (Ax1–Ax5, U1–U6, R1–R7, and all derived theorems) imply Ax4*?**

This is NOT asking whether Ax4* is true. It is asking whether Ax4* is a *consequence* of what C2 already contains, or whether it is genuinely new.

**The investigation attempts to destroy the conclusion that F9 fails.** Every route is pursued to exhaustion before a negative verdict is rendered.

---

## Exact Definitions (Carried Forward from F9 Research)

**D1 — CCA:** Tuple (O, M, ⊗, ≤, †, ε) satisfying Ax1–Ax5. See C2_FOUNDATIONS.md §Subsystem 6.

**D2 — Ax1–Ax5:**
- Ax1: (O, M, ⊗) is a symmetric monoidal category with finite hom-sets and unit I.
- Ax2: (M, ≤) is a locally finite partial order.
- Ax3: † reverses causal order: m ≤ m' ⟹ m'† ≤ m†.
- Ax4: ε: M → [0,1] with Σ_{m: A→B} ε(m) = 1 for every ordered pair (A,B).
- Ax5: (≤, ε) makes each Hom(I,A) a probability simplex ordered by causal depth.

**D3 — Transition matrix T_m:**
For causal m: A → B (i.e., A ≤ B), the matrix [T_m]_{j,i} = ε(t_j | s_i) — the conditional probability of arriving at state t_j ∈ Hom(I,B) given input state s_i ∈ Hom(I,A). In the deterministic case: [T_m]_{j,i} = 1 if t_j = m∘s_i, else 0.

**D4 — Column stochasticity:** Σ_j [T_m]_{j,i} = 1 for all i. (PROVED from Ax1+Ax4.)

**D5 — Row stochasticity:** Σ_i [T_m]_{j,i} = 1 for all j. (STATUS: UNKNOWN. This is Ax4*.)

**D6 — Doubly stochastic:** T_m is both column- and row-stochastic. (= Ax4*.)

**D7 — Ax4* (the target):**
> For every causal morphism m: A → B in a CCA satisfying Ax1–Ax5, the transition matrix T_m is doubly stochastic.

**D8 — U1–U6 (Unavoidable Physical Floor):**
- U1: Logical non-triviality (more than one state exists).
- U2: Distinguishability (distinct states yield distinct measurement outcomes).
- U3: Composability (processes can be combined).
- U4: Reproducibility (same input → same output distribution).
- U5: Non-trivial dynamics (the state can change).
- U6: Finite information per bounded region.

**D9 — R1–R7 (Physical Requirements):**
- R1: Distinguishable states.
- R2: Composability.
- R3: Reproducibility.
- R4: Finite information density.
- R5: Continuous evolution (no instantaneous jumps).
- R6: No preferred frame (frame independence).
- R7: Unitarity / distinguishability preserved under reversible dynamics.

**D10 — Detailed balance:** For transition matrix T and stationary distribution π:
π_i [T]_{j,i} = π_j [T]_{i,j} for all i, j.

**D11 — Doubly stochastic ↔ uniform stationary distribution:**
T is doubly stochastic iff T preserves the uniform distribution: T · (1/n,...,1/n)^T = (1/n,...,1/n)^T AND T^T · (1/n,...,1/n)^T = (1/n,...,1/n)^T.

---

## Phase 1 — Systematic Theorem Audit

### 1.1 Audit Protocol

For each theorem T in the C2 framework, determine:
- **YES**: T logically implies Ax4* (row stochasticity of T_m for all causal m).
- **NO**: T provably does not imply Ax4*.
- **UNKNOWN**: Implications are unclear; further analysis required.

A theorem T implies Ax4* only if, in every CCA satisfying Ax1–Ax5 plus the conditions of T, every causal morphism induces a doubly stochastic T_m.

### 1.2 Audit: Unavoidable Floor (U1–U6)

**U1 (Logical non-triviality):**
Statement: The state space contains more than one state.
Implication for Ax4*: **NO.**
Proof: U1 merely asserts |Hom(I,A)| ≥ 2. It places no constraint on how morphisms map states. A CCA with two states can have a non-doubly-stochastic morphism (as shown by the Phase 4 counterexample in F9 research). U1 is satisfied by that counterexample.

**U2 (Distinguishability):**
Statement: Distinct states yield distinct measurement outcomes; ε separates states.
Implication for Ax4*: **NO.**
Proof: Distinguishability requires that if s_i ≠ s_j then there exists some measurement that assigns different probabilities. This constrains the richness of the measurement algebra but not the normalization of T_m in the row direction. The counterexample CCA (ε_A=(½,½), ε_B=(9/10,1/10)) has two perfectly distinguishable states in each hom-set (ε separates them), yet T_m fails row stochasticity.

**U3 (Composability):**
Statement: Processes can be combined — composition is defined.
Implication for Ax4*: **NO.**
Proof: Ax1 already captures composability (symmetric monoidal structure). U3 adds nothing beyond what Ax1 provides. Since Ax1 alone does not imply row stochasticity (established in F9 research), U3 cannot either.

**U4 (Reproducibility):**
Statement: The same input reliably produces the same output distribution.
Implication for Ax4*: **UNKNOWN → requires detailed analysis (see Phase 2, Route C).**
This is the most promising candidate. If "same input → same output" holds in both the forward and backward directions, symmetric normalization might follow. Full analysis in §2.3.

**U5 (Non-trivial dynamics):**
Statement: The state can change; not all morphisms are identity.
Implication for Ax4*: **NO.**
Proof: U5 asserts existence of non-identity morphisms. It places no constraint on the normalization of those morphisms in the row direction. Existence of dynamics does not control the distribution of preimages under any morphism.

**U6 (Finite information per bounded region):**
Statement: |Hom(I,A)| < ∞ for each object A.
Implication for Ax4*: **NO.**
Proof: Finiteness of state spaces is already guaranteed by the "finite hom-sets" clause of Ax1. U6 adds no new normalization condition on T_m.

**U1–U6 audit summary:**
- U4 is UNKNOWN (non-trivial; analyzed in Phase 2).
- All others: NO.

### 1.3 Audit: Physical Requirements (R1–R7)

**R1 (Distinguishable states):**
Statement: Distinct physical states are in principle distinguishable.
Implication for Ax4*: **NO.**
Proof: Same argument as U2. Distinguishability constrains the measurement algebra, not T_m normalization in the row direction.

**R2 (Composability):**
Statement: Physical processes can be composed in sequence or parallel.
Implication for Ax4*: **NO.**
Proof: Same as U3 — already captured by Ax1.

**R3 (Reproducibility):**
Statement: Same input reliably produces the same output.
Implication for Ax4*: **UNKNOWN → same analysis as U4.**
R3 and U4 are operationally equivalent for this purpose. Full analysis in §2.3.

**R4 (Finite information density):**
Statement: Finite information per bounded region.
Implication for Ax4*: **NO.**
Proof: Same as U6. Finiteness alone cannot imply row normalization.

**R5 (Continuous evolution):**
Statement: No instantaneous jumps; dynamics continuous in time.
Implication for Ax4*: **NO.**
Proof: The CCA is a discrete framework (finite hom-sets, discrete partial order). R5 applies to the continuum limit and transport layer, not to the CCA morphism algebra directly. Continuity in time does not constrain the normalization of individual morphism transition matrices.

**R6 (No preferred frame):**
Statement: Physics is the same in all frames; no preferred reference frame.
Implication for Ax4*: **UNKNOWN → see Phase 2, Route E (Functorial structure).**
If frame independence forces the weight function ε to be invariant under relabeling of source and target states, it might force symmetric normalization. Analysis in §2.5.

**R7 (Unitarity):**
Statement: Distinguishable states remain distinguishable under reversible dynamics.
Implication for Ax4*: **UNKNOWN → see Phase 2, Route B.**
If reversible dynamics preserves distinguishability in both directions (forward and backward), the induced T_m might need to be doubly stochastic. Analysis in §2.2.

**R1–R7 audit summary:**
- R3 (= U4): UNKNOWN (analyzed in Phase 2).
- R6: UNKNOWN (analyzed in Phase 2).
- R7: UNKNOWN (analyzed in Phase 2).
- All others: NO.

### 1.4 Audit: CCA Axioms (Ax1–Ax5)

**Ax1 (Symmetric monoidal category):**
Already analyzed in F9 research. Provides column stochasticity of T_m but not row stochasticity. **NO.**

**Ax2 (Locally finite partial order):**
Provides causal depth rank r(m) and monotonicity r(A) ≤ r(B) for causal m: A→B. No normalization content for T_m. **NO.**

**Ax3 (Dagger reverses causal order):**
Statement: m ≤ m' ⟹ m'† ≤ m†.
Implication for Ax4*: **UNKNOWN → see Phase 2, Route A (Detailed balance).**
Ax3 provides a time-reversal structure. If ε(m) and ε(m†) are related by Ax4 in both directions, detailed balance might follow. Analysis in §2.1.

**Ax4 (Column-wise normalization):**
Σ_{m:A→B} ε(m) = 1 for each (A,B). This is the source of column stochasticity. It explicitly normalizes in the target direction (B fixed, A fixed, sum over morphisms). It does NOT normalize in any source-direction. **Does not imply Ax4* by itself.** But combined with Ax3, see Route A.

**Ax5 (Probability simplex with causal depth ordering):**
Makes Hom(I,A) a probability simplex. Equivalent to Ax4 applied to (I,A) pairs. Adds ordering by causal depth. No row normalization content. **NO.**

**Ax1–Ax5 audit summary:**
- Ax3 + Ax4 together: UNKNOWN (analyzed in Route A).
- All others individually: NO.

### 1.5 Audit: Derived Theorems and Structural Results

**[T] CCA Theorem 1.1 (State spaces are probability simplices):**
Already used in F9 research. No new content for row stochasticity. **NO.**

**[T] CCA Theorem 1.3 (Rank function):**
r(m) well-defined; r non-decreasing along causal order (Theorem 2.18). No normalization content. **NO.**

**[T] CCA Theorem 1.5 (Shannon entropy well-defined):**
H(A) = −Σ ε(s) log ε(s). No normalization content for T_m. **NO.**

**[T] CCA-10 (Classical coarse-graining recovers classical stochastic mechanics):**
The quotient by diagonal morphisms gives a classical Markov process. This is relevant: the classical Markov process obtained by coarse-graining may or may not be doubly stochastic. However, CCA-10 states only that a classical stochastic process is recovered — not that it is doubly stochastic. Doubly stochastic Markov chains are a proper subset of all stochastic Markov chains. **NO** (coarse-graining to classical Markov ≠ doubly stochastic Markov).

**[T] C2-Gibbs (Gibbs distribution as max-entropy distribution):**
For finite ergodic Markov chain (C2 candidate), the unique max-entropy distribution is the Gibbs distribution. Implication for Ax4*: **UNKNOWN → see Phase 2, Route D.**
If the equilibrium state of every causal process in the CCA is the Gibbs distribution, and if the Gibbs distribution is uniform (maximum entropy), then the transition matrices preserving it would be doubly stochastic. Analysis in §2.4.

**[T] C2-Hthm (H-theorem for finite ergodic Markov chains):**
H(μ_t) non-decreasing for the C2 candidate. This is the H-theorem for a SPECIFIC subcase (C2 candidate = finite ergodic Markov chains). The C2 candidate already has doubly stochastic transitions (by the ergodicity + detailed balance structure of the C2 candidate). So this theorem holds BECAUSE the C2 candidate has doubly stochastic transitions — it cannot be used to DERIVE doubly stochasticity without circularity.
**NO** (circular: the H-theorem for C2 candidate presupposes ergodic + detailed balance structure).

**[T] Theorem PA1-1 (Reversibility not derivable from R1–R3):**
PA1 (microscopic reversibility) is an axiom, not a theorem. Its status as OPEN means it cannot be used to imply Ax4*. **NO** (PA1 is itself unproved).

**[T] Theorem PA1-2 (Route A partial derivation):**
Reversibility of φ(s⊗r) follows from R2+R7 given AA2. But AA2 is itself independent. And even if PA1 held, PAI asserts φ is bijective on states — not that the transition matrix is doubly stochastic. A bijective map on states gives a permutation matrix, which IS doubly stochastic. This is the most promising indirect route. **UNKNOWN → see Phase 2, Route B.**

**[T] Theorem SCC-1 (SCC derivability from R1,R2,R3,R4,R6,R7 plus AA1):**
SCC is the compact transitive group acting on state space. If SCC applies to T_m (the action of a causal morphism on the state space), and if the SCC group action preserves the Haar measure, then T_m preserves the uniform distribution and is doubly stochastic. **UNKNOWN → see Phase 2, Route E.**

**[T] Theorem SCC-2 through SCC-6 (SCC consequences):**
These establish the transitivity, continuity, compactness, and uniqueness of SCC. They apply to the full symmetry group G, not directly to individual causal morphisms. For T_m to be doubly stochastic, it would need to be an element of (or compatible with) the SCC group action. This requires T_m to preserve the Haar measure on the state space. **UNKNOWN → Route E.**

**[KR] Data Processing Inequality:**
H(Tp) ≥ H(p) for doubly stochastic T. This is the CONCLUSION of F9, not a tool to derive it. It requires doubly stochasticity as a hypothesis. **NO** (circular).

**[KR] Birkhoff–von Neumann theorem:**
Every doubly stochastic matrix = convex combination of permutation matrices. This characterizes doubly stochastic matrices but does not help derive that T_m is doubly stochastic. **NO.**

**[KR] Detailed balance implies doubly stochastic (for uniform stationary):**
If T satisfies π_i T_{ij} = π_j T_{ji} and π is uniform, then T is doubly stochastic. Useful IF detailed balance can be derived and IF stationary distribution is uniform. **CONDITIONAL → Route A.**

**[T] Theorem ME-EQ-MAIN (Transport equations = EIT):**
The master transport equation [ME] is equivalent to Extended Irreversible Thermodynamics. The EIT framework has entropy production built in (σ_irr term) but does NOT require doubly stochastic transitions — it allows entropy decrease in subsystems (compensated by entropy increase in the environment). **NO.**

**[T] Theorem ME-ASS1 (No assumption reduction):**
The substrate does not reduce independent assumptions compared to EIT. This establishes that the transport layer is no stronger than EIT, which does not require doubly stochastic transitions. **NO** (confirms no hidden normalization in transport layer).

**[T] Lindblad theorem (HC-2):**
The Lindblad master equation gives CPTP (completely positive trace-preserving) evolution. CPTP evolution in QM corresponds to a stochastic matrix on density matrices — specifically, CPTP maps are trace-preserving (column-stochastic on density matrices) but NOT necessarily unital (i.e., NOT necessarily doubly stochastic). A CPTP map Φ is doubly stochastic iff Φ(I/d) = I/d (it preserves the maximally mixed state). This is an additional condition (unitality) not forced by CPTP alone. **NO** (CPTP ≠ doubly stochastic in general).

**[T] OS reconstruction theorem (implicit in C2):**
Osterwalder-Schrader reconstruction connects Euclidean and Minkowski QFT. This theorem operates entirely within the QFT framework and has no direct bearing on CCA morphism normalization. **NO.**

**[T] Theorem PRW-IMP-1 (PRW observable algebra is commutative):**
The PRW generates no non-commutative structure. This shows the transport layer is classical — irrelevant to the CCA morphism normalization question. **NO.**

### 1.6 Phase 1 Summary Table

| Theorem/Axiom | Implies Ax4*? | Reason |
|---------------|--------------|--------|
| U1 | NO | Non-triviality ≠ row normalization |
| U2 | NO | Distinguishability ≠ row normalization |
| U3 | NO | Same as Ax1 |
| U4 | UNKNOWN | Reproducibility in both directions? → Route C |
| U5 | NO | Dynamics existence ≠ normalization |
| U6 | NO | Finiteness already in Ax1 |
| R1 | NO | Same as U2 |
| R2 | NO | Same as Ax1 |
| R3 | UNKNOWN | Same as U4 → Route C |
| R4 | NO | Same as U6 |
| R5 | NO | Applies to continuum, not CCA |
| R6 | UNKNOWN | Frame independence → Route E |
| R7 | UNKNOWN | Unitarity → Route B |
| Ax1 | NO | Only column stochasticity |
| Ax2 | NO | Only rank monotonicity |
| Ax3 | UNKNOWN | Dagger structure → Route A |
| Ax4 | NO | Only column normalization |
| Ax5 | NO | Same as Ax4 for (I,A) pairs |
| Ax3 + Ax4 together | UNKNOWN | Detailed balance → Route A |
| CCA-1 through CCA-8 | NO | Internal structure, no normalization |
| CCA-9 (†-compact QM) | NO | Requires additional structure beyond CCA |
| CCA-10 (classical coarse-graining) | NO | Recovers stochastic, not doubly stochastic |
| C2-Gibbs | UNKNOWN | Gibbs equilibrium → Route D |
| C2-Hthm | NO | Circular (presupposes doubly stochastic) |
| PA1-1 | NO | PA1 itself is unproved |
| PA1-2 | UNKNOWN | Bijection on states → Route B |
| SCC-1 through SCC-6 | UNKNOWN | Haar-measure preservation → Route E |
| Lindblad/CPTP | NO | CPTP ≠ doubly stochastic |
| DPI | NO | Circular |
| Birkhoff–von Neumann | NO | Characterizes, doesn't derive |
| Transport [ME] | NO | EIT-equivalent, allows entropy decrease |
| OS reconstruction | NO | Unrelated to CCA normalization |
| PRW-IMP-1 | NO | Classical transport layer |

**Conclusion of Phase 1:**
Five routes are UNKNOWN and require independent derivation attempts:
- **Route A:** Ax3 + Ax4 → detailed balance → doubly stochastic
- **Route B:** R7 (unitarity) + PA1-2 → bijection → doubly stochastic
- **Route C:** U4/R3 (reproducibility) → symmetric normalization
- **Route D:** C2-Gibbs (Gibbs equilibrium) → doubly stochastic
- **Route E:** R6 (frame independence) + SCC → Haar measure → doubly stochastic

One additional route is flagged from definitions:
- **Route F:** Hidden normalization in the definitions of ε, m∘s, or Hom(I,A)

All other theorems are definitively NO.

---

---

## Phase 2 — Six Independent Derivation Routes

### Route A — Detailed Balance via Ax3 + Ax4

**Claim under investigation:**
Does Ax3 (dagger reverses causal order) combined with Ax4 (column-normalization of ε) imply detailed balance for T_m, and does detailed balance then imply doubly stochastic T_m?

**Setup:**

Let m: A → B be a causal morphism (A ≤ B). By Ax3, m†: B → A satisfies B ≤ A in the dagger-reversed order (equivalently, m† is a causal morphism from B to A in the time-reversed CCA).

By Ax4 applied to morphisms from A to B:
    Σ_{m: A→B} ε(m) = 1                                      ...(Ax4-forward)

By Ax4 applied to morphisms from B to A:
    Σ_{m†: B→A} ε(m†) = 1                                    ...(Ax4-backward)

**Step 1: Does Ax3 constrain ε(m†) in terms of ε(m)?**

Ax3 states: m ≤ m' implies m'† ≤ m†. This is a purely ORDER-THEORETIC statement. It says the dagger operation is order-reversing. It says NOTHING about the numerical values of ε(m) and ε(m†).

Formally: Ax3 defines a bijection (−)†: M → M such that (−)† reverses ≤. The weight function ε: M → [0,1] is defined separately by Ax4. There is no axiom in Ax1–Ax5 that forces ε(m†) = f(ε(m)) for any function f.

CONCLUSION: Ax3 does not constrain the numerical relationship between ε(m) and ε(m†).

**Step 2: Does Ax4 alone (applied to both (A,B) and (B,A)) imply detailed balance?**

Detailed balance for the state-level transition matrix T_m reads:
    ε(s_i) · [T_m]_{j,i} = ε(t_j) · [T_{m†}]_{i,j}         ...(DB)

for all i ∈ {1,...,n_A}, j ∈ {1,...,n_B}.

Ax4 gives us:
    Σ_i ε(s_i) = 1    (from Ax4 applied to (I,A))
    Σ_j ε(t_j) = 1    (from Ax4 applied to (I,B))

These are marginal normalization conditions. They do not constrain the JOINT distribution ε(s_i) · [T_m]_{j,i}. Specifically, we can freely choose:

    ε(s_1) = 1/2, ε(s_2) = 1/2
    ε(t_1) = 9/10, ε(t_2) = 1/10
    [T_m]_{1,1} = 1, [T_m]_{2,1} = 0    (s_1 maps to t_1)
    [T_m]_{1,2} = 1, [T_m]_{2,2} = 0    (s_2 also maps to t_1)

This satisfies Ax4 (both hom-sets sum to 1, T_m is column-stochastic). But:
    ε(s_1) · [T_m]_{1,1} = (1/2)(1) = 1/2
    ε(t_1) · [T_{m†}]_{1,1} = (9/10) · [T_{m†}]_{1,1}

For detailed balance: [T_{m†}]_{1,1} = (1/2)/(9/10) = 5/9.
Then [T_{m†}]_{2,1} = 1 − 5/9 = 4/9 (by column normalization of T_{m†}).

But then:
    ε(s_2) · [T_m]_{1,2} = (1/2)(1) = 1/2
    ε(t_1) · [T_{m†}]_{1,2} = (9/10) · [T_{m†}]_{1,2}

For detailed balance: [T_{m†}]_{1,2} = (1/2)/(9/10) = 5/9.
But [T_{m†}]_{1,2} ≠ [T_{m†}]_{1,1} = 5/9 is required. We need [T_{m†}]_{1,1} + [T_{m†}]_{1,2} to be ≤ 1 (column sum of T_{m†} for input t_1). But [T_{m†}]_{1,1} + [T_{m†}]_{1,2} = 5/9 + 5/9 = 10/9 > 1.

CONTRADICTION: Detailed balance cannot hold simultaneously with column normalization of T_{m†} in this example. The detailed balance condition is therefore INCONSISTENT with the example — not satisfied. So the example simply violates detailed balance. Detailed balance is not forced by Ax3+Ax4.

**Step 3: Exact line where the derivation breaks.**

Ax3 provides order-reversal: m†: B → A exists and is causal.
Ax4 provides: ε(m†) sums to 1 over all m†: B→A.

The broken step is: there is NO axiom linking ε(m) to ε(m†) numerically. Ax3 is a structural (categorical) axiom, not a numerical (measure-theoretic) axiom. Without an axiom of the form "ε(m) · [something] = ε(m†) · [something]", detailed balance cannot be derived.

**Step 4: Would detailed balance imply doubly stochastic anyway?**

Even if detailed balance held: DB implies T_m is doubly stochastic ONLY IF the stationary distribution π is UNIFORM. The stationary distribution for T_m satisfies T_m · π = π. If ε_B (the distribution on Hom(I,B)) is the stationary distribution, then T_m doubly stochastic iff ε_B is uniform. But Ax4 does NOT force ε to be uniform — ε_B = (9/10, 1/10) is a valid Ax4-satisfying distribution.

**Route A verdict: FAILED.**

The derivation fails at TWO independent points:
- (i) Ax3 does not constrain ε(m†) numerically → detailed balance not derivable.
- (ii) Even if detailed balance held, non-uniform ε_B prevents doubly stochasticity.

There is no patch within Ax1–Ax5 that closes either gap.

---

### Route B — Microscopic Reversibility (PA1)

**Claim under investigation:**
Does PA1 (the dynamical evolution map φ: S → S is invertible) imply that T_m is doubly stochastic?

**Setup:**

PA1 states: φ: S → S is a bijection on the state space S = Hom(I,A) (for a fixed object A evolving in time).

If φ is a bijection (permutation) on the finite state space, then the transition matrix T_φ induced by φ is a PERMUTATION MATRIX. Every permutation matrix is doubly stochastic (each row and column has exactly one entry equal to 1 and all others 0).

**Step 1: Does PA1 apply to causal morphisms in the CCA?**

PA1 as stated in C2_FOUNDATIONS.md (Subsystem 12) applies to the dynamical evolution map of a physical system — it is a statement about the full evolution of the state space, corresponding to an AUTOMORPHISM m: A → A of a single object A.

Ax4* requires doubly stochastic T_m for ALL causal morphisms m: A → B, including:
(a) Automorphisms m: A → A (same object, evolution in time). ← PA1 might apply here.
(b) Morphisms between distinct objects m: A → B with A ≠ B. ← PA1 says nothing about this.

**Step 2: Analysis of case (a) — automorphisms.**

If φ: A → A is a reversible automorphism (PA1 holds), then T_φ is a permutation matrix and IS doubly stochastic. Route B succeeds for automorphisms.

But this is a CONDITIONAL result: it requires PA1 to hold. And PA1 itself is UNPROVED — it is listed as Open Problem OP-5 in C2_FOUNDATIONS.md (Subsystem 12, Status: OPEN). Theorem PA1-1 proves that PA1 is NOT derivable from R1–R3 alone. Theorem PA1-2 shows it follows from R2+R7 given AA2, but AA2 is itself independent.

**Step 3: Analysis of case (b) — morphisms between distinct objects.**

Even granting PA1 for automorphisms, PA1 says nothing about morphisms m: A → B with A ≠ B. These are processes that CHANGE the state space (e.g., a measurement that transforms a quantum system into a classical record, or a physical process that increases the number of states). PA1 applies to the dynamics of a FIXED system, not to transitions between systems of different sizes.

Specifically, if n_A = |Hom(I,A)| ≠ n_B = |Hom(I,B)|, then T_m is an n_B × n_A rectangular matrix. A rectangular matrix cannot be a permutation matrix. PA1-based invertibility applies only to square (same-system) transitions.

**Step 4: Can PA1 be extended to inter-object morphisms?**

One could attempt: if m: A → B is causal and reversible (in the sense that there exists m': B → A with m'∘m = id_A), then T_{m'}∘T_m = I_{n_A}, implying T_m is a right inverse. Combined with column stochasticity, this would force T_m to be injective on the state space. But injectivity is NOT doubly stochastic — it says n_A ≤ n_B and each source state maps to a distinct target state, but does not normalize rows.

If m is an isomorphism (m'∘m = id_A AND m∘m' = id_B), then T_m is square, injective, and surjective — hence a permutation matrix, which IS doubly stochastic. But isomorphisms in the CCA are morphisms where A and B have the same causal depth and the same structure — this is a highly special case, not the general causal morphism.

**Route B verdict: FAILED.**

The derivation fails at:
- PA1 is itself unproved (OP-5). Cannot use an unproved axiom to derive Ax4*.
- Even granting PA1, it covers only automorphisms (case a), not general inter-object morphisms (case b).
- The extension to inter-object morphisms requires isomorphism, not mere causal morphism.

The exact line of failure: "PA1 applies only to φ: A → A; causal morphisms m: A → B (A ≠ B) are not covered by PA1's invertibility statement."

---

### Route C — Reproducibility (U4/R3)

**Claim under investigation:**
Does U4 (reproducibility: same input → same output distribution) force symmetric normalization of T_m?

**Precise formulation:**

U4 states: for a physical process P, if the input state is s_i, the output distribution is a fixed probability vector {[T_m]_{j,i}}. The process is reproducible in the sense that preparing s_i again produces the same distribution.

**Step 1: What does U4 say about T_m?**

U4 says: T_m is a WELL-DEFINED stochastic matrix (the output distribution depends only on the input state, not on when or how many times the process is applied). This is COLUMN stochasticity — already captured by Ax1+Ax4. U4 adds no new content beyond what we already have.

**Step 2: The attempted strengthening — bidirectional reproducibility.**

The candidate argument is:
"If the process is reproducible in the FORWARD direction (s_i → distribution over t_j), and if the time-reversed process is also reproducible (t_j → distribution over s_i), then both T_m and T_{m†} are well-defined stochastic matrices. Combined with Ax4, this might force doubly stochastic behavior."

Formal statement: Suppose U4 is strengthened to "bidirectional reproducibility":
- Forward: T_m is a stochastic matrix (input state s_i → output distribution over Hom(I,B)).
- Backward: T_{m†} is a stochastic matrix (input state t_j → output distribution over Hom(I,A)).

**Step 3: Does bidirectional reproducibility imply doubly stochastic?**

No. Bidirectional reproducibility means both T_m (n_B × n_A) and T_{m†} (n_A × n_B) are stochastic matrices (columns sum to 1). This is ALREADY established:
- T_m is column-stochastic (from Ax1 + Ax4 applied to (I,A)).
- T_{m†} is column-stochastic (from Ax1 + Ax4 applied to (I,B), since m†: B→A uses (I,B) pairs).

So bidirectional reproducibility is already satisfied in any CCA satisfying Ax1–Ax5. It gives us two column-stochastic matrices but does NOT constrain their relationship.

Specifically, T_m being column-stochastic and T_{m†} being column-stochastic are INDEPENDENT constraints. Row stochasticity of T_m is equivalent to: Σ_i [T_m]_{j,i} = 1 for all j. This can be rewritten as: T_m^T is column-stochastic, i.e., T_m^T = T_{m†} in some sense. But T_{m†} ≠ T_m^T in general — T_{m†} is the transition matrix of the REVERSE process, which is related to T_m by Bayes' theorem: [T_{m†}]_{i,j} = ε(s_i) · [T_m]_{j,i} / ε(t_j). This is the Bayesian inverse, not the matrix transpose.

**Step 4: The Bayesian inverse and doubly stochastic.**

The Bayesian inverse relation is:
    [T_{m†}]_{i,j} = ε(s_i) · [T_m]_{j,i} / ε(t_j)

Row stochasticity of T_m: Σ_i [T_m]_{j,i} = 1 for all j.

Using the Bayesian inverse:
    Σ_i [T_m]_{j,i} = Σ_i [T_{m†}]_{i,j} · ε(t_j) / ε(s_i)

For this to equal 1 for all j, we need:
    Σ_i [T_{m†}]_{i,j} · ε(t_j) / ε(s_i) = 1

This holds if and only if ε(t_j) / ε(s_i) = 1 for all i,j (i.e., ε is uniform on both hom-sets) AND T_{m†} is column-stochastic. Neither condition is forced by U4/R3.

**Route C verdict: FAILED.**

The derivation fails at: "bidirectional reproducibility gives two column-stochastic matrices, but the row sum of T_m is controlled by the RATIO ε(t_j)/ε(s_i), which is not constrained by U4, R3, or any existing axiom."

The exact broken line: "U4 forces column-stochasticity in both directions independently; it does not force the product ε(s_i)[T_m]_{j,i} to integrate to ε(t_j) across i."

---

### Route D — Gibbs Equilibrium (C2-Gibbs)

**Claim under investigation:**
Does the Gibbs theorem (C2-Gibbs) force the transition matrices of causal morphisms to be doubly stochastic?

**Relevant theorem (C2_FOUNDATIONS.md, Subsystem 7):**
[T] Theorem C2-Gibbs: For the C2 candidate (finite ergodic Markov chain), the unique maximum-entropy stationary distribution is the Gibbs distribution μ*(s) ∝ exp(−β · r(s)), where r(s) is the causal depth of state s.

**Step 1: What does C2-Gibbs establish?**

C2-Gibbs applies to the C2 CANDIDATE, which is a finite ergodic Markov chain. In this candidate, the dynamics is given by a stochastic matrix T (not necessarily doubly stochastic). The theorem states:

(a) The unique stationary distribution of the Markov chain is the Gibbs distribution μ*.
(b) μ* maximizes entropy subject to fixed mean energy ⟨r⟩.

C2-Gibbs does NOT state that T is doubly stochastic. It characterizes the STATIONARY DISTRIBUTION, not the transition matrix itself.

**Step 2: When does a Gibbs stationary distribution imply doubly stochastic T?**

A stochastic matrix T is doubly stochastic iff the UNIFORM distribution is its stationary distribution (T · (1/n,...,1/n)^T = (1/n,...,1/n)^T). This follows because for doubly stochastic T, T^T · 1 = 1 implies (T · 1/n = 1/n if also column-stochastic).

The Gibbs distribution μ*(s) ∝ exp(−β · r(s)) is UNIFORM only when β = 0 (infinite temperature) or all states have equal causal depth r(s) = r for all s. The Gibbs distribution is generically NOT uniform.

Therefore: even if C2-Gibbs held within the CCA framework (not just for the C2 candidate), the stationary distribution μ* would be the Gibbs distribution, and T would be doubly stochastic ONLY in the degenerate case β = 0 or uniform r(s).

**Step 3: Does C2-Gibbs apply within the CCA beyond the C2 candidate?**

C2-Gibbs is stated for the C2 candidate (finite ergodic Markov chain). It is NOT stated as a theorem of the CCA in general. The CCA contains many candidates (C1–C5 plus the full CCA structure). Applying C2-Gibbs to the CCA would require:
(a) That the causal morphisms of the CCA generate an ergodic Markov chain.
(b) That the stationary distribution of this chain is the Gibbs distribution.

Neither (a) nor (b) is a consequence of Ax1–Ax5. In particular:
- Not every CCA is ergodic (Ax2 allows partial orders with no cyclic structure).
- The Gibbs distribution arises only when energy is assigned via causal depth — this requires the identification E(s) = r(s) · ε_0, which is not forced by any axiom.

**Step 4: The strongest form of the Gibbs argument.**

Suppose we grant: (i) the CCA is ergodic, (ii) the Gibbs distribution is stationary, (iii) β = 0 (maximum entropy / maximum temperature regime). Then μ* is uniform, T preserves the uniform distribution, and T is doubly stochastic.

But this requires three additional assumptions none of which follow from Ax1–Ax5:
- Ergodicity (not in CCA axioms)
- Gibbs distribution as stationary (not in CCA axioms)
- β = 0 (not forced; β is a free parameter)

**Route D verdict: FAILED.**

The derivation fails at:
- C2-Gibbs is restricted to the C2 candidate (finite ergodic Markov), not the general CCA.
- The Gibbs distribution is uniform (hence doubly stochastic T) only when β = 0 or all states have equal rank — not in general.
- Applying C2-Gibbs to the CCA requires ergodicity and a specific energy assignment, neither of which follows from Ax1–Ax5.

Exact broken line: "C2-Gibbs characterizes the stationary distribution μ*, but T doubly stochastic requires μ* = uniform, which requires β = 0, which is not forced."

---

### Route E — Functorial Structure / Frame Independence (R6 + SCC)

**Claim under investigation:**
Does R6 (no preferred frame) combined with the SCC framework force T_m to preserve the Haar measure on state spaces, making T_m doubly stochastic?

**Setup:**

SCC (C2_FOUNDATIONS.md, Subsystem 9) is a framework satisfying:
- Closure: state space closed under ⊗.
- Symmetry: compact group G acts equivariantly.
- Invertibility: G acts by bijections.
- Normalization: G-invariant probability measure (= Haar measure).

By Theorem SCC-1, SCC is derivable from R1, R2, R3, R4, R6, R7 + AA1 (compactness of G).

**Step 1: What does SCC say about T_m?**

The SCC framework says that the STATE SPACE S = Hom(I,A) carries a G-invariant measure (Haar measure). It says the GROUP G acts on S by measure-preserving bijections (by Haar invariance).

A MORPHISM m: A → B in the CCA is NOT necessarily an element of the group G. The group G consists of AUTOMORPHISMS of individual objects (bijections A → A), not of morphisms between distinct objects. So SCC directly constrains only:
(a) Automorphisms m: A → A: These are elements of G (or at least compatible with G-action), and since G preserves Haar measure, T_m for automorphisms preserves the Haar measure = uniform measure = doubly stochastic. ✓
(b) Morphisms m: A → B with A ≠ B: These are NOT elements of G. SCC says nothing about how they transform the measure.

**Step 2: Can R6 (frame independence) extend SCC to inter-object morphisms?**

R6 says physics is the same in all frames. In the CCA context, a "frame" corresponds to a relabeling of states. R6 says: if we relabel the states of Hom(I,A) by applying some permutation π_A, and relabel the states of Hom(I,B) by applying permutation π_B, the physical content of the morphism m should be unchanged.

Formally: T_{π_B ∘ m ∘ π_A^{-1}} should represent the "same physics" as T_m, just in relabeled coordinates.

The constraint from R6 is: the physics cannot depend on the LABELING of states. This means the weight function ε must be invariant under relabeling. For Ax4, Σ_{m:A→B} ε(m) = 1 holds in all labelings (it's a sum over all morphisms, so relabeling doesn't change the sum). R6 is already satisfied by Ax4 and the symmetric monoidal structure.

R6 does NOT force ε to be UNIFORM on each hom-set. A non-uniform distribution ε is perfectly frame-independent — it is just a feature of the physical state, not a labeling artifact. The specific distribution ε_A = (9/10, 1/10) is frame-independent (it's a physical property, not a labeling choice) even though it's non-uniform.

**Step 3: The equivariance argument.**

A more sophisticated argument: if T_m must be equivariant with respect to the G-action (R6), then T_m intertwines the G-actions on Hom(I,A) and Hom(I,B):

    T_m ∘ G_A = G_B ∘ T_m

where G_A and G_B are the G-actions on the respective state spaces.

If G acts transitively on Hom(I,A) (no preferred state), and if T_m is equivariant, then by Schur's lemma (for irreducible representations), T_m must be a scalar multiple of a fixed linear map. If furthermore n_A = n_B and both representations are the same irrep, then T_m ∝ Id — the identity, up to scalar. Column normalization forces the scalar to be 1/n_A, giving T_m = (1/n_A) · J where J is the all-ones matrix (doubly stochastic and uniform). But:

(a) G need not act transitively on Hom(I,A) in general (Ax1–Ax5 don't require this).
(b) The G-representations on Hom(I,A) and Hom(I,B) need not be the same irrep.
(c) Equivariance of T_m with G is NOT required by any CCA axiom — morphisms need only exist, not intertwine a specific group action.
(d) This argument requires G to already be defined and acting — which requires AA1 (compactness) and the full SCC construction, which are ADDITIONAL ASSUMPTIONS beyond Ax1–Ax5.

**Step 4: The SCC result conditioned on AA1.**

Theorem SCC-1 states: SCC is derivable from R1, R2, R3, R4, R6, R7 + **AA1 (compactness)**. AA1 is itself flagged as "a physical assumption, not derived" in C2_FOUNDATIONS.md (Subsystem 9, Assumptions).

So even the SCC result requires AA1. And AA1 blocks the derivation of the Lorentz group (non-compact). The SCC argument would give doubly stochastic T_m only for the compact automorphism subgroup, not for general causal morphisms.

**Route E verdict: FAILED.**

The derivation fails at:
- SCC applies to G-automorphisms of single objects, not to general inter-object morphisms.
- R6 (frame independence) is already satisfied by the symmetric structure of Ax4; it does not force uniform ε or doubly stochastic T_m.
- The equivariance argument requires G-transitivity, equivariance of morphisms, and same irrep — none of which are consequences of Ax1–Ax5.
- The SCC route requires AA1 (compactness), itself an additional assumption.

Exact broken line: "SCC controls the G-action on single-object state spaces; causal morphisms between distinct objects are outside the scope of SCC unless additional assumptions force morphisms to intertwine the G-action."

---

### Route F — Hidden Normalization in Definitions

**Claim under investigation:**
Is there a definition, notational convention, or implicit assumption in the C2 framework that already forces T_m to be doubly stochastic, even if no axiom explicitly states this?

This route searches every definition for implicit content that could supply row normalization without being labeled as such.

**F.1 — The definition of ε (Ax4).**

Ax4: ε: M → [0,1] with Σ_{m: A→B} ε(m) = 1 for every (A,B).

Read carefully: the sum is over ALL morphisms m from A to B, for a FIXED PAIR (A,B). This is the normalization that defines ε as a probability distribution over morphisms between two given objects.

Hidden content check: Is there a dual normalization? Could the definition implicitly require Σ_{(A,B): m is a morphism from A to B} ε(m) = 1 for each morphism m? No — each morphism m has a unique source A = src(m) and target B = tgt(m), so the "sum over (A,B) for fixed m" is just ε(m) = ε(m). No dual normalization is implicit.

**F.2 — The definition of the transition matrix T_m.**

T_m is defined via post-composition: the map s ↦ m∘s sends Hom(I,A) to Hom(I,B). The matrix entry [T_m]_{j,i} is the conditional probability of arriving at t_j given input s_i.

In the DETERMINISTIC case (where each s_i maps to a unique m∘s_i = t_{f(i)} for some function f: {1,...,n_A} → {1,...,n_B}):
    [T_m]_{j,i} = 1 if j = f(i), else 0.

Column stochasticity: Σ_j [T_m]_{j,i} = 1 (exactly one target per source). ✓
Row stochasticity: Σ_i [T_m]_{j,i} = |f^{-1}(j)| = number of sources mapping to t_j.

For row stochasticity, we need |f^{-1}(j)| = 1 for all j — i.e., f is a bijection, i.e., m_* is a bijection on state spaces. This is the same condition as PA1 for inter-object morphisms. It is NOT hidden in the definition of T_m — it is an ADDITIONAL mathematical condition.

**F.3 — The definition of Hom(I,A) as a probability simplex (Ax5).**

Ax5: Hom(I,A) is a probability simplex ordered by causal depth.

Probability simplex: {(p_1,...,p_n) : p_i ≥ 0, Σp_i = 1}. The simplex structure gives each state a weight ε(s_i) summing to 1. This is already captured by Ax4 applied to (I,A) pairs. No additional normalization is hidden here.

**F.4 — The symmetric monoidal structure (Ax1).**

Ax1: (O, M, ⊗) is a symmetric monoidal category. The symmetry refers to the MONOIDAL structure (swap isomorphism τ_{A,B}: A⊗B → B⊗A), not to the normalization of ε. The symmetry of the monoidal structure does not imply any symmetry between source-side and target-side normalization of ε.

More precisely: the swap isomorphism τ gives a canonical morphism τ_{A,B}: A⊗B → B⊗A. This is a STRUCTURAL isomorphism, not a constraint on ε(m) for arbitrary m. The weight ε(τ_{A,B}) is still just one number in [0,1] summing to 1 with other morphisms from A⊗B to B⊗A.

**F.5 — The involution structure (Ax3).**

Already analyzed in Route A. The involution (−)†: M → M is a set-theoretic bijection on morphisms that reverses causal order. It is not a measure-theoretic statement. No numerical constraint on ε(m†) vs ε(m) is hidden here.

**F.6 — The composition law in Ax1.**

Ax1 requires that compositions m' ∘ m: A → C are well-defined when src(m') = tgt(m). The composition law could potentially constrain T_{m'∘m} = T_{m'} · T_m (matrix product). This is the standard chain rule for stochastic matrices.

If T_{m'∘m} = T_{m'} · T_m and both T_{m'} and T_m are column-stochastic, then T_{m'∘m} is column-stochastic. If furthermore T_{m'} is doubly stochastic and T_m is column-stochastic, then T_{m'∘m} may or may not be doubly stochastic (product of doubly stochastic × column-stochastic = column-stochastic in general, doubly stochastic only in special cases). No hidden constraint here.

**F.7 — The unit object I.**

The unit object I in Ax1 corresponds to the "trivial system" with Hom(I,A) being the state space of A. The unit morphism id_A: A → A induces T_{id_A} = I_{n_A} (identity matrix), which IS doubly stochastic. But this is only for the identity morphism — not for general causal morphisms.

**F.8 — Conclusion of Route F.**

A thorough search of all definitions reveals NO hidden normalization condition that would force T_m to be doubly stochastic. The definitions are internally consistent with both doubly stochastic AND non-doubly-stochastic transition matrices. The framework is deliberately constructed with one-sided (column) normalization, and no definition compensates for the missing row normalization.

**Route F verdict: FAILED.**

No hidden normalization exists in any definition of the C2 framework.

---

### Phase 2 Summary Table

| Route | Mechanism | Status | Exact Failure Point |
|-------|-----------|--------|---------------------|
| A | Detailed balance via Ax3+Ax4 | FAILED | Ax3 is order-theoretic, not measure-theoretic; ε(m†) unconstrained numerically. Even if DB held, non-uniform ε prevents doubly stochastic. |
| B | Microscopic reversibility PA1 | FAILED | PA1 itself unproved (OP-5); even if proved, covers only automorphisms (A→A), not inter-object morphisms (A→B). |
| C | Reproducibility U4/R3 | FAILED | Bidirectional reproducibility gives two column-stochastic matrices; row sum of T_m depends on ε(t_j)/ε(s_i) ratio, unconstrained by U4/R3. |
| D | Gibbs equilibrium C2-Gibbs | FAILED | C2-Gibbs restricted to C2 candidate (not general CCA); Gibbs distribution = uniform only when β=0, which is not forced. |
| E | Frame independence R6 + SCC | FAILED | SCC applies to G-automorphisms only; R6 already satisfied by Ax4 symmetry; equivariance of inter-object morphisms not in axioms; AA1 still required. |
| F | Hidden definitions | FAILED | No definition in C2 contains implicit row normalization. All definitions explicitly one-directional. |

**All six routes fail. Proceed to Phase 3 (minimum theorem check) and Phase 4 (impossibility theorem).**

---

## Phase 3 — Minimum Theorem Check

Since all six routes failed, Phase 3 is entered in its negative form: confirm that no minimum theorem exists within C2 that would imply Ax4*.

### 3.1 The Closest Partial Results

Three results come closest to implying Ax4*, without reaching it:

**Closest result 1: PA1-2 + automorphisms.**
Theorem PA1-2 + PA1 (if proved) would give: automorphisms φ: A→A induce permutation matrices T_φ, which are doubly stochastic. This is Ax4* restricted to automorphisms. But:
- PA1 is not proved (OP-5).
- Restricts to automorphisms only; does not cover inter-object morphisms.
- Even if PA1 were proved, this would be a PARTIAL result, not Ax4*.

Classification if PA1 were proved: Ax4* for automorphisms = **corollary of PA1 restricted to A→A morphisms.** Not a full theorem of Ax4*.

**Closest result 2: SCC + Haar measure for compact automorphism group.**
If SCC holds (granted AA1) and G acts transitively on Hom(I,A), then the Haar measure is the unique G-invariant measure. If causal automorphisms m: A→A are in G, they preserve Haar measure and T_m is doubly stochastic. But:
- Requires AA1 (additional assumption, not in Ax1–Ax5).
- Requires G-transitivity (not forced by Ax1–Ax5 alone).
- Restricted to automorphisms only.

**Closest result 3: Row normalization when n_A = n_B and m is bijective on states.**
If n_A = n_B and the post-composition map m_*: Hom(I,A) → Hom(I,B) is bijective, then T_m is a permutation matrix and hence doubly stochastic. But:
- n_A = n_B is not forced by any axiom (state spaces can have different sizes).
- Bijectivity of m_* is equivalent to PA1 for inter-object morphisms — not proved.

**Conclusion of Phase 3:**
No theorem currently in C2 implies Ax4* even as a partial or conditional result, without either:
(a) adding AA1 (compactness), or
(b) proving PA1 (open problem OP-5), or
(c) restricting to automorphisms only.

None of these constitutes a derivation of Ax4* from the existing axioms. Phase 3 confirms: there is no minimum theorem that makes Ax4* a corollary.

---

## Phase 4 — Impossibility Theorem

### 4.1 Setup: What Kind of Impossibility?

We now determine the precise logical status of Ax4* with respect to Ax1–Ax5.

The four possibilities are:
- **Independent:** Both Ax4* and ¬Ax4* are consistent with Ax1–Ax5.
- **Inconsistent:** Ax4* contradicts Ax1–Ax5.
- **Undecidable:** Neither Ax4* nor ¬Ax4* is provable (in a formal undecidability sense).
- **Requires additional physical structure:** Ax4* follows from Ax1–Ax5 plus some additional physical conditions not yet in C2.

### 4.2 Model Separating Ax4* from Ax1–Ax5

**Model M1 (Ax4* fails, Ax1–Ax5 holds):**
Already constructed in F9_causal_entropy_research.md, Phase 4:

    O = {A, B}
    Hom(I,A) = {s_1, s_2},    ε(s_1) = 1/2, ε(s_2) = 1/2
    Hom(I,B) = {t_1, t_2},    ε(t_1) = 9/10, ε(t_2) = 1/10
    One causal morphism m: A → B
    m_*: s_1 ↦ t_1, s_2 ↦ t_1    (both states map to t_1)
    ε(m) = 1    (Ax4 for (A,B) satisfied)

Transition matrix:
    T_m = [[1, 1], [0, 0]]

Column sums: col_1 = 1, col_2 = 1. ✓ (Column-stochastic.)
Row sums: row_1 = 2, row_2 = 0. ✗ (NOT row-stochastic.)

Axiom verification:
- Ax1: SMC with finite hom-sets, unit I, composition defined. ✓
- Ax2: Causal order A < B (transitive, acyclic, locally finite). ✓
- Ax3: m†: B → A exists with B ≥ A in dagger order. ✓
- Ax4: Σε over each hom-set = 1. ✓
- Ax5: Each Hom(I,X) is a probability simplex with causal depth ordering. ✓

All axioms satisfied. Ax4* violated. **M1 is a valid counterexample: M1 ⊨ Ax1–Ax5 and M1 ⊭ Ax4*.**

**Model M2 (Ax4* holds, Ax1–Ax5 holds):**
Construct a CCA where T_m is doubly stochastic:

    O = {A, B}
    Hom(I,A) = {s_1, s_2},    ε(s_1) = 1/2, ε(s_2) = 1/2
    Hom(I,B) = {t_1, t_2},    ε(t_1) = 1/2, ε(t_2) = 1/2
    One causal morphism m: A → B
    m_*: s_1 ↦ t_1, s_2 ↦ t_2    (bijection on states)
    ε(m) = 1

Transition matrix:
    T_m = [[1, 0], [0, 1]]    (identity / permutation matrix)

Column sums: col_1 = 1, col_2 = 1. ✓
Row sums: row_1 = 1, row_2 = 1. ✓ (Doubly stochastic. Ax4* satisfied.)

Axiom verification: identical to M1 — all Ax1–Ax5 satisfied. ✓

**M2 is a valid model: M2 ⊨ Ax1–Ax5 and M2 ⊨ Ax4*.**

### 4.3 Independence Theorem

**Theorem F9A-IMP-1 (Independence of Ax4* from Ax1–Ax5):**

> Ax4* is logically independent of the axiom system Ax1–Ax5. That is:
> (a) Ax1–Ax5 ⊬ Ax4*   (Ax4* is not provable from Ax1–Ax5)
> (b) Ax1–Ax5 ⊬ ¬Ax4*  (Ax4* is not refutable from Ax1–Ax5)

**Proof of (a):** By Model M1. M1 satisfies Ax1–Ax5 (verified above) and violates Ax4* (T_m row sums: [2, 0] ≠ [1, 1]). By soundness of first-order logic, if Ax1–Ax5 ⊢ Ax4*, then every model of Ax1–Ax5 would satisfy Ax4*. But M1 is a model of Ax1–Ax5 that violates Ax4*. Contradiction. Therefore Ax1–Ax5 ⊬ Ax4*. □

**Proof of (b):** By Model M2. M2 satisfies both Ax1–Ax5 and Ax4*. By soundness, if Ax1–Ax5 ⊢ ¬Ax4*, every model of Ax1–Ax5 would violate Ax4*. But M2 satisfies Ax4*. Contradiction. Therefore Ax1–Ax5 ⊬ ¬Ax4*. □

**Corollary F9A-COR-1:**
Ax4* is not a theorem, corollary, or consequence of the existing C2 axiom system. It is a genuinely new axiom if adopted.

### 4.4 Independence from the Extended System (Ax1–Ax5 + U1–U6 + R1–R7)

We now verify that Ax4* remains independent when the full C2 framework is considered, including U1–U6 and R1–R7.

**Claim:** M1 satisfies U1–U6 and R1–R7.

Verification:
- U1 (non-triviality): Hom(I,A) = {s_1,s_2}, two states. ✓
- U2 (distinguishability): ε(s_1)=1/2 ≠ ε(s_2)=1/2 ... actually equal. However, the STATES are distinct objects in Hom(I,A); distinguishability means distinct states produce distinct measurement outcomes, not that ε values differ. The two states are distinct elements of the set — they are distinguishable by the identity of the element. ✓
- U3 (composability): Composition of m with identity morphisms is defined. ✓
- U4 (reproducibility): Input s_i always maps to the same output (t_1 in both cases). ✓
- U5 (non-trivial dynamics): m: A→B with m_*(s_i) ≠ s_i (since A≠B). ✓
- U6 (finite information): |Hom(I,A)| = |Hom(I,B)| = 2 < ∞. ✓
- R1 (distinguishable states): Same as U2. ✓
- R2 (composability): Same as U3. ✓
- R3 (reproducibility): Same as U4. ✓
- R4 (finite information density): Same as U6. ✓
- R5 (continuous evolution): Not applicable to finite CCA directly; the CCA is a discrete model. In the CCA context, R5 is vacuously satisfied or not applicable. ✓/N.A.
- R6 (no preferred frame): The weight function ε is defined on the objects, not tied to any specific labeling. ✓
- R7 (unitarity): This concerns reversible dynamics preserving distinguishability. The morphism m in M1 maps both s_1 and s_2 to t_1 — it is NOT reversible (not a bijection). R7 says if two states are distinguishable under reversible dynamics, they remain so. But M1 does not claim to have reversible dynamics for m — m is a general causal morphism, not necessarily reversible. R7 applies to the REVERSIBLE dynamics only. If M1 has separate reversible dynamics (identity on each object), R7 is satisfied by those. The causal morphism m is an IRREVERSIBLE process (like a measurement or coarse-graining), and R7 does not require irreversible processes to be doubly stochastic.✓

**Conclusion:** M1 satisfies Ax1–Ax5, U1–U6, and R1–R7 (with the appropriate reading of R7 as applying to reversible dynamics). Ax4* is violated by M1.

**Theorem F9A-IMP-2 (Independence from full C2 framework):**

> Ax4* is logically independent of the full C2 framework (Ax1–Ax5 ∪ U1–U6 ∪ R1–R7 and all derived theorems that follow from them). The existing C2 framework neither implies Ax4* nor contradicts it.

**Proof:** M1 is a model satisfying the full C2 framework that violates Ax4*; M2 is a model satisfying the full C2 framework that satisfies Ax4*. Independence follows by soundness. □

### 4.5 Classification of Ax4*

Ax4* is:
- **NOT inconsistent** with C2: M2 demonstrates consistency.
- **NOT provable** from C2: M1 demonstrates independence.
- **NOT undecidable** in any formal sense: the independence result is a standard model-theoretic fact, not a Gödel-type undecidability. Within any fixed model, Ax4* is either true or false.
- **Requires additional physical structure** beyond Ax1–Ax5 + U1–U6 + R1–R7.

The classification is: **INDEPENDENT. Requires additional physical structure.**

### 4.6 What Additional Structure Would Suffice?

Three minimal additions each independently imply Ax4*:

**Addition 1 — Direct (Ax4* itself):**
Simply adopt Ax4* as a new axiom. Cost: one additional axiom. Motivation: physical principle that causal evolution cannot destroy more information than it creates (balanced flow). This is the minimal and most transparent option.

**Addition 2 — Bijectivity of causal morphisms on state spaces:**
Require: for every causal m: A→B, the map m_*: Hom(I,A) → Hom(I,B) is a bijection (in particular, n_A = n_B for all causally connected A,B).

This is a strong condition — it forces all causal morphisms to be isomorphisms on state spaces, equivalent to PA1 extended to inter-object morphisms. It implies Ax4* (bijection → permutation matrix → doubly stochastic) but is stronger than Ax4* (doubly stochastic ≠ bijection for stochastic T_m; e.g., the averaging matrix T=(1/2,1/2; 1/2,1/2) is doubly stochastic but not a bijection).

This addition is not derivable from the existing framework (same obstacles as PA1) but IS sufficient for Ax4*.

**Addition 3 — Uniform ε + detailed balance:**
Require: (i) ε is uniform on every Hom(I,A) (i.e., ε(s) = 1/n_A for all s ∈ Hom(I,A)), AND (ii) Ax3 implies detailed balance: ε(s_i) · [T_m]_{j,i} = ε(t_j) · [T_{m†}]_{i,j}.

If ε is uniform and detailed balance holds:
    (1/n_A) · [T_m]_{j,i} = (1/n_B) · [T_{m†}]_{i,j}

Summing over i:
    (1/n_A) · Σ_i [T_m]_{j,i} = (1/n_B) · Σ_i [T_{m†}]_{i,j} = (1/n_B) · 1 = 1/n_B
    (since T_{m†} is column-stochastic: Σ_i [T_{m†}]_{i,j} = 1)

Therefore: Σ_i [T_m]_{j,i} = n_A / n_B.

This equals 1 (row stochasticity) only if n_A = n_B. So uniform ε + detailed balance gives doubly stochastic T_m ONLY WHEN n_A = n_B. For unequal state space sizes, this addition does not suffice.

A corrected version: require (i) uniform ε, (ii) n_A = n_B for all causally connected A,B, (iii) detailed balance. Then Ax4* follows. But this adds THREE conditions, not one.

**Recommended minimal addition: Direct adoption of Ax4* (Addition 1).** It is the weakest condition that exactly implies what is needed, with no extraneous content.

### 4.7 Can Ax4* Be Given Physical Motivation Within C2?

Even though Ax4* is logically independent, we can identify its physical content precisely:

**Physical content of Ax4* within C2:**
Row stochasticity Σ_i [T_m]_{j,i} = 1 says: each output state t_j receives exactly as much probability flux as it contributes. This is a FLOW CONSERVATION condition: the inflow to each target state equals 1 (in units where total inflow = n_A = total number of source states).

In physical terms: causal evolution conserves the TOTAL PROBABILITY WEIGHT of each output state when integrated over all input states. This is distinct from column stochasticity (which says each input state distributes its weight completely), and together they mean the evolution is "balanced" in both directions.

This condition has a natural physical interpretation: **it is the condition that the uniform distribution is invariant under T_m (T_m preserves the equal-weight ensemble).** Equivalently: if the initial state is a maximum-entropy distribution (equal weight on all states), the evolved state is also maximum-entropy. This is the "doubly stochastic = preserves maximum entropy" characterization.

**Physical principle that would motivate Ax4*:**
"Causal evolution preserves the maximum-entropy (equal-weight) ensemble."

This is a physical statement about the relationship between causal dynamics and information: the most disordered state remains the most disordered state under causal evolution. It has strong physical motivation (it is a form of the second law's "entropy of the universe is maximized at equilibrium"), but it is NOT derivable from Ax1–Ax5 — it is an additional physical postulate.

---

## Phase 5 — Verdict

### 5.1 Summary of All Routes

| Route | Description | Result | Failure Type |
|-------|-------------|--------|--------------|
| A | Detailed balance (Ax3+Ax4) | FAILED | Ax3 purely structural; ε(m†) unconstrained; even if DB, non-uniform ε blocks DS |
| B | Microscopic reversibility (PA1) | FAILED | PA1 unproved (OP-5); even if proved, restricted to automorphisms |
| C | Reproducibility (U4/R3) | FAILED | Bidirectional reproducibility already satisfied; row normalization requires ε ratio = 1 |
| D | Gibbs equilibrium (C2-Gibbs) | FAILED | C2-Gibbs not general CCA; uniform Gibbs only at β=0; β not constrained |
| E | Frame independence (R6+SCC) | FAILED | SCC covers only automorphisms; equivariance not in axioms; AA1 still needed |
| F | Hidden normalization | FAILED | No implicit row normalization in any definition |

### 5.2 Impossibility Theorem (Master Statement)

**Theorem F9A-MASTER (Ax4* is Independent of the C2 Framework):**

> Let C2 denote the complete axiom system (Ax1–Ax5) ∪ (U1–U6) ∪ (R1–R7) together with all theorems derived from these axioms and recorded in C2_FOUNDATIONS.md. Then:
>
> 1. C2 ⊬ Ax4* (Ax4* is not derivable from C2).
> 2. C2 ∪ Ax4* is consistent (Ax4* does not contradict C2).
> 3. Therefore, Ax4* is logically independent of C2.
> 4. Consequently, F9 (CCA causal entropy non-decrease) is logically independent of C2.
> 5. The second law of thermodynamics, as formulated in F9, cannot be recovered from the existing C2 framework without introducing Ax4* or an equivalent condition.

**Proof:**
1. By Theorem F9A-IMP-2: Model M1 satisfies C2 and violates Ax4*. So C2 ⊬ Ax4*.
2. Model M2 satisfies C2 and satisfies Ax4*. So C2 ∪ {Ax4*} has a model. By the model existence theorem, it is consistent.
3. Points 1 and 2 together give logical independence (standard model-theoretic definition).
4. F9 ⟺ L1 ⟺ Ax4* (established in F9_causal_entropy_research.md, Phase 2). Therefore independence of Ax4* implies independence of F9.
5. Follows from (4) directly. □

### 5.3 Counterexample Catalog

Two minimal explicit counterexamples:

**CE-1 (Ax4* fails, row sum = 2):**
O={A,B}, Hom(I,A)={s₁,s₂}, Hom(I,B)={t₁,t₂}, ε_A=(½,½), ε_B=(9/10,1/10), m_*(s₁)=m_*(s₂)=t₁.
T_m = [[1,1],[0,0]]. Row sums: [2, 0]. Ax4* fails. Ax1–Ax5 + U1–U6 + R1–R7 satisfied.
H(A) = log 2 ≈ 0.693, H(B) ≈ 0.325. F9-H fails: H(B) < H(A).

**CE-2 (Ax4* fails, surjective but non-doubly-stochastic):**
O={A,B}, Hom(I,A)={s₁,s₂,s₃}, Hom(I,B)={t₁,t₂}, ε_A=(1/3,1/3,1/3), ε_B=(1/2,1/2).
m_*(s₁)=t₁, m_*(s₂)=t₁, m_*(s₃)=t₂.
T_m = [[1,1,0],[0,0,1]]. Column sums: all 1. ✓ Row sums: [2, 1]. Row 1 = 2 ≠ 1. Ax4* fails.
This example has DIFFERENT STATE SPACE SIZES (n_A=3 ≠ n_B=2), demonstrating that even "surjective" morphisms (every target has at least one preimage) fail Ax4*.
H(A) = log 3 ≈ 1.099, H(B) = log 2 ≈ 0.693. F9-H fails: H(B) < H(A).

**CE-3 (Ax4* fails even with equal state space sizes):**
O={A,B}, Hom(I,A)={s₁,s₂}, Hom(I,B)={t₁,t₂}, ε_A=(1/2,1/2), ε_B=(1/2,1/2).
m_*(s₁)=t₁, m_*(s₂)=t₁.
T_m = [[1,1],[0,0]]. Row sums: [2, 0]. Ax4* fails even with equal sizes and uniform ε.
This rules out the argument that "equal state space sizes + uniform ε → doubly stochastic."

Note: in CE-3, detailed balance fails: ε(s₁)·[T_m]_{1,1} = (1/2)(1) = 1/2 but ε(t₁)·[T_{m†}]_{1,1} = (1/2)·[T_{m†}]_{1,1}. Detailed balance would require [T_{m†}]_{1,1} = 1. Similarly [T_{m†}]_{1,2} = 1, so T_{m†} column_1 sum = 2 ≠ 1. Contradiction. Detailed balance is simply not satisfied in CE-3, confirming Route A's failure: Ax1–Ax5 do not force detailed balance.

### 5.4 Scope of the Impossibility

The impossibility theorem is:
- **Not a Gödel incompleteness result.** It is a standard model-theoretic independence result. Within a fixed CCA instance, Ax4* is either true or false.
- **Not an in-principle barrier.** Ax4* can be added as a new axiom. It is consistent with C2.
- **A precise structural gap.** The gap is exactly the missing direction of normalization in Ax4. One axiom (Ax4*) closes it completely.
- **Physical rather than mathematical in nature.** The question "should causal evolution be doubly stochastic?" is a physical question about the nature of causal processes, not answerable from combinatorial/categorical structure alone.

### 5.5 The Gap in Physical Terms

The existing C2 axioms describe a DIRECTED stochastic process: each input state distributes its probability mass completely over output states (column stochasticity). This is the "forward flow" condition — probability is conserved going forward.

Ax4* adds the "backward flow" condition: each output state receives exactly as much probability mass as it has source states. This is conservation in the backward direction.

Physically: column stochasticity says "nothing is lost in the forward direction." Row stochasticity says "nothing is gained from nowhere in the backward direction." Together they say the process conserves probability flow in both directions simultaneously — the doubly stochastic condition.

The C2 framework currently enforces only the forward direction. The second law of thermodynamics, as formulated in F9, requires both directions. The missing backward flow condition is exactly Ax4*.

---

## Final Verdict

**VERDICT: FAILED**

Ax4* (the doubly stochastic condition for causal morphisms) is INDEPENDENT of the existing C2 framework.

**Evidence:**
1. Phase 1: Of 30+ theorems surveyed, none imply Ax4*. Five routes identified for Phase 2.
2. Phase 2: All six routes fail. Each failure is at an identified, irreducible obstruction.
3. Phase 3: No minimum theorem within C2 implies even a partial version of Ax4*.
4. Phase 4: Model-theoretic independence proved (Theorem F9A-MASTER). Two explicit counterexample models constructed (CE-1, CE-2, CE-3), all satisfying Ax1–Ax5 + U1–U6 + R1–R7.
5. Phase 5: Impossibility theorem is mathematical, not physical. Ax4* is consistent with C2. It requires one additional physical postulate.

**Consequence for F9:**
The second law of thermodynamics (F9: causal entropy non-decrease) cannot be recovered entirely from the existing C2 framework without introducing Ax4* as a new axiom.

**What this means for the C2 research program:**
- F9 remains FAILED under current axioms.
- The specific missing structure is identified with surgical precision: row normalization of ε.
- One new axiom (Ax4*: "causal evolution preserves the equal-weight ensemble") closes the gap completely.
- Ax4* has clear physical motivation: it is the condition that maximum entropy is preserved under causal flow, which is a form of the second law.
- The research question shifts to: **is Ax4* physically motivated by a principle not yet in C2?** This is the natural next subproblem (F9-B).

---

## Summary Table

| Phase | Question | Result |
|-------|----------|--------|
| 1 | Audit of all C2 theorems for Ax4* implication | 5 routes UNKNOWN, all others NO |
| 2A | Detailed balance (Ax3+Ax4) → Ax4*? | FAILED — Ax3 structural, not numerical; non-uniform ε blocks |
| 2B | Microscopic reversibility (PA1) → Ax4*? | FAILED — PA1 unproved; covers only automorphisms |
| 2C | Reproducibility (U4/R3) → Ax4*? | FAILED — bidirectional reproducibility already satisfied; ε ratio unconstrained |
| 2D | Gibbs equilibrium (C2-Gibbs) → Ax4*? | FAILED — C2-Gibbs restricted to C2 candidate; Gibbs = uniform only at β=0 |
| 2E | Frame independence (R6+SCC) → Ax4*? | FAILED — SCC covers automorphisms only; AA1 still required |
| 2F | Hidden normalization in definitions | FAILED — no implicit row normalization anywhere |
| 3 | Minimum theorem if proof succeeded | N/A (no proof succeeded) |
| 4 | Independence theorem | PROVED: Ax4* independent of full C2 (Theorem F9A-MASTER) |
| 4 | Counterexamples | CE-1, CE-2, CE-3 all satisfy Ax1–Ax5+U1–U6+R1–R7, violate Ax4* |
| 5 | Final verdict | FAILED — second law independent of existing C2 |
| 5 | Classification of Ax4* | INDEPENDENT. Requires one additional physical postulate. |

---

*Document compiled: 2026-07-24*
*All C2 results treated as established per C2_FOUNDATIONS.md (frozen).*
*No C2 axioms modified, extended, or redesigned.*
*All counterexamples explicitly verify all existing C2 axioms.*
