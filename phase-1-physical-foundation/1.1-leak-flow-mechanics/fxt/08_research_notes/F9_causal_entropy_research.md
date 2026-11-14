# F9 — CCA Causal Entropy Non-Decrease: Research Program
**Frontier Problem:** F9 from C2_FRONTIER_MAP.md  
**Date:** 2026-07-24  
**Protocol:** 5-Phase Mathematical Research Program  
**Status at close:** FAILED (independent of Ax1–Ax5)  
**Source authority:** C2_FOUNDATIONS.md (all established results treated as fixed)

---

## Phase 1 — Problem Statement and Classification

### 1.1 Frontier Problem: Precise Restatement

**Conjecture CCA-C2 (C2_FOUNDATIONS.md, Subsystem 6):**

> For any causal morphism m: A → B in a CCA (meaning A ≤ B in the causal order), the causal entropy satisfies H_c(B) ≥ H_c(A).

**Unpacked form:**

Let (O, M, ⊗, ≤, †, ε) be a CCA satisfying Ax1–Ax5. For any m ∈ M with src(m) = A, tgt(m) = B, and A ≤ B in (M, ≤):

    H_c(B) ≥ H_c(A)

where

    H_c(X) = H(X) + λ · r(X)
    H(X)   = − Σ_{s ∈ Hom(I,X)} ε(s) log ε(s)
    r(X)   = max{ r(m) : tgt(m) = X }   (causal depth of X)
    λ > 0  is a free parameter

This is the claim that causal entropy — Shannon entropy plus a weighted causal depth — is non-decreasing along every causal morphism. Its physical meaning would be: the second law of thermodynamics is an internal mathematical theorem of the CCA, not an additional postulate.

---

### 1.2 All Definitions Involved

**D1 — CCA (Causal-Compositional Algebra):**
A tuple (O, M, ⊗, ≤, †, ε) where:
- O: finite set of objects (state labels)
- M: morphisms with src, tgt ∈ O; finite hom-sets Hom(A,B) for all A,B ∈ O
- ⊗: symmetric monoidal composition satisfying Ax1
- ≤: locally finite partial order on M satisfying Ax2
- †: involution on M with (†)² = id, satisfying Ax3
- ε: M → [0,1] satisfying Ax4

**D2 — Axioms (Ax1–Ax5):**
- Ax1: (O, M, ⊗) is a symmetric monoidal category with finite hom-sets and unit I
- Ax2: (M, ≤) is a locally finite partial order (transitive, acyclic, finite intervals)
- Ax3: † reverses causal order: m ≤ m' ⟹ m'† ≤ m†
- Ax4: ε: M → [0,1] with Σ_{m: A→B} ε(m) = 1 for every ordered pair (A,B)
- Ax5: (≤, ε) makes each Hom(I,A) a probability simplex ordered by causal depth

**D3 — Shannon entropy of object A:**
    H(A) = − Σ_{s ∈ Hom(I,A)} ε(s) log ε(s)
Well-defined by CCA Theorem 1.5 (finite hom-sets, ε a probability distribution).

**D4 — Rank function:**
    r(m) = length of longest chain below m in (M, ≤)
Well-defined by CCA Theorem 1.3 (local finiteness of Ax2 ensures finite chains).

**D5 — Rank of an object:**
    r(A) = max{ r(m) : tgt(m) = A }
(Maximum causal depth among all morphisms terminating at A.)

**D6 — Causal entropy:**
    H_c(A) = H(A) + λ · r(A),   λ > 0 (free parameter)

**D7 — Causal morphism:**
m: A → B is causal if A ≤ B in (M, ≤), i.e., B is in the causal future of A.

**D8 — Transition matrix T_m:**
For m: A → B, the map m_*: Hom(I,A) → Hom(I,B) defined by s ↦ m ∘ s (categorical
post-composition). The induced matrix [T_m]_{j,i} is the conditional probability that
input state s_i maps to output state t_j under m.

**D9 — Doubly stochastic matrix:**
A matrix T (not necessarily square) is doubly stochastic if:
- All entries ≥ 0
- Each column sums to 1 (column-stochastic = every input maps to a distribution)
- Each row sums to 1 (row-stochastic = every output has total inflow = 1)

**D10 — Data processing inequality (DPI):**
For stochastic T and distribution p: if T is doubly stochastic then H(Tp) ≥ H(p).
(Entropy does not decrease under doubly stochastic maps.)
Reference: Cover & Thomas, Elements of Information Theory, Theorem 2.8.1.

---

### 1.3 Relevant C2 Theorems

**[T] CCA Theorem 1.1:** Hom(I,A) is a well-defined probability simplex under ε for each A.

**[T] CCA Theorem 1.3:** Rank r(m) is well-defined; finite by local finiteness of Ax2.

**[T] CCA Theorem 1.5:** H(A) = −Σ ε(s) log ε(s) is well-defined and non-negative.

**[T] CCA Theorem 1.6:** H_c(A) = H(A) + λ·r(A) is well-defined for each A.

**[T] C2_FOUNDATIONS Theorem 2.18 (Rank monotonicity):**
The rank function r is non-decreasing along causal order:
    m ≤ m'  ⟹  r(m) ≤ r(m')
This is proved from Ax2 alone and constitutes an internal arrow of time.

**[T] C2-Hthm:** For finite ergodic Markov chains (candidate C2), H(μ_t) is non-decreasing.
Note: this is for the C2 candidate (stochastic matrices), not for the CCA itself.

**[T] CCA Theorem CCA-10:** Classical coarse-graining recovers classical stochastic mechanics.
The quotient by diagonal morphisms gives a classical Markov process.

**[OBS] Obstruction 2.21a:** Probability is a primitive in CCA (built into Ax4), not derived.

---

### 1.4 Relevant External Theorems

**[KR] Data Processing Inequality:**
For doubly stochastic T: H(Tp) ≥ H(p) for all distributions p.
For arbitrary stochastic T: H(Tp) ≤ H(p) in general.
(Cover & Thomas, Ch. 2)

**[KR] Birkhoff–von Neumann theorem:**
Every doubly stochastic matrix is a convex combination of permutation matrices.
(Horn & Johnson, Matrix Analysis, Thm 8.7.2)

**[KR] H-theorem (finite-state Markov):**
For a doubly stochastic transition matrix T on a finite state space:
H(T^n p) is non-decreasing in n, converging to the uniform distribution.
(Levin–Peres–Wilmer, Markov Chains and Mixing Times, Ch. 4)

**[KR] Uhlmann's theorem (classical majorization):**
p ≺ q (p is majorized by q) iff q = Dp for some doubly stochastic D.
Equivalently: H(q) ≥ H(p) iff q is "more uniform" than p.
(Marshall–Olkin–Arnold, Inequalities: Theory of Majorization, Ch. 2)

**[KR] Detailed balance implies doubly stochastic (for equal marginals):**
If T satisfies detailed balance π_i T_{ij} = π_j T_{ji} and π is the stationary distribution,
then T is doubly stochastic with respect to the uniform distribution iff π is uniform.

---

### 1.5 Classification of F9

**Is F9 equivalent to an existing theorem?**
No. The DPI gives H(Tp) ≥ H(p) for doubly stochastic T, but requires doubly stochasticity
as a hypothesis. Whether Ax4 forces doubly stochasticity is the open question — so F9 is not
immediately reducible to the DPI.

**Is F9 weaker than existing theorems?**
Weaker than the full H-theorem (which also requires ergodicity). F9 does not require the
causal morphism chain to be ergodic or to have a unique invariant measure.

**Is F9 stronger than existing theorems?**
No. It is a specialization of the DPI to the CCA setting.

**Is F9 independent of Ax1–Ax5?**
YES — this is the conclusion of the analysis. The rank part (r(B) ≥ r(A)) is already proved
(Theorem 2.18). The entropy part (H(B) ≥ H(A)) is independent: both H(B) < H(A) and
H(B) ≥ H(A) are consistent with Ax1–Ax5, as shown by explicit counterexample in Phase 4.

**Classification: F9-H (the Shannon entropy sub-claim) is INDEPENDENT of Ax1–Ax5.**
F9 as a whole (including the rank term) is independent if and only if λ is insufficiently large.

---

## Phase 2 — Smallest Missing Lemma

### 2.1 Decomposition of F9

F9 asserts H_c(B) ≥ H_c(A) for causal m: A → B. Since H_c = H + λ·r:

    H_c(B) − H_c(A) = [H(B) − H(A)] + λ[r(B) − r(A)]

**Part 1 — Rank term:** λ[r(B) − r(A)] ≥ 0.
Follows from Theorem 2.18 (r non-decreasing along causal order) and λ > 0.
STATUS: ALREADY PROVED. No lemma needed.

**Part 2 — Entropy term:** H(B) − H(A) ≥ 0.
This is the open part. It is the sub-claim:

    F9-H:  For any causal morphism m: A → B,  H(B) ≥ H(A).

F9 reduces entirely to proving F9-H.

### 2.2 What Would Prove F9-H

F9-H follows from the Data Processing Inequality if and only if the map
T_m: Δ(Hom(I,A)) → Δ(Hom(I,B)) induced by the causal morphism m is doubly stochastic.

This leads directly to the key missing lemma:

---

**Lemma L1 (Doubly Stochastic Transitions):**
> For any causal morphism m: A → B in a CCA satisfying Ax1–Ax5, the transition matrix
> T_m induced by m on the state spaces Hom(I,A) → Hom(I,B) is doubly stochastic.

If L1 holds: DPI gives H(B) ≥ H(A) immediately. F9-H follows. F9 follows.
If L1 fails: F9-H is not provable by this route; must seek counterexample.

---

### 2.3 Candidate Lemmas (Ranked)

Three candidates, in order of minimality and tractability:

**L1 (Doubly Stochastic):** T_m is doubly stochastic for all causal m: A → B.
- Most direct path to F9-H via DPI
- Requires checking whether Ax4's normalization implies row normalization of T_m
- ATTACK FIRST

**L2 (Marginal Consistency):** The pushforward of ε_A through m equals the marginal of
ε_B, i.e., Σ_s ε(s) · 1[m∘s = t] = ε(t) for all t ∈ Hom(I,B).
- Weaker than L1 (does not require full doubly stochastic)
- Sufficient for a weaker entropy inequality via concavity arguments
- ATTACK SECOND if L1 fails

**L3 (Majorization):** ε_A ≺ ε_B in the majorization order, i.e., ε_B is "more uniform"
than ε_A.
- Equivalent to L1 when state spaces have equal cardinality
- Requires extending majorization to distributions over sets of different sizes when
  |Hom(I,A)| ≠ |Hom(I,B)|
- ATTACK THIRD if L1 and L2 fail

**Verdict: L1 is the smallest missing lemma. Proceed to Phase 3.**

---

## Phase 3 — Proof Attempt for Lemma L1

### 3.1 Setup

Let n_A = |Hom(I,A)|, n_B = |Hom(I,B)|.
Label states: Hom(I,A) = {s_1, …, s_{n_A}},  Hom(I,B) = {t_1, …, t_{n_B}}.

By Ax4 (applied to pair (I,A)): Σ_i ε(s_i) = 1.
By Ax4 (applied to pair (I,B)): Σ_j ε(t_j) = 1.

For a causal morphism m: A → B, categorical composition (Ax1) gives a map:
    m_*: Hom(I,A) → Hom(I,B),   s ↦ m ∘ s

This map is well-defined since m ∘ s ∈ Hom(I,B) for every s ∈ Hom(I,A).

Define the transition matrix T_m (n_B × n_A matrix) by:
    [T_m]_{j,i} = ε(t_j | s_i)  =  probability of arriving at t_j given source s_i

In the purely deterministic (functional) case:
    [T_m]_{j,i} = 1  if t_j = m ∘ s_i,  else 0

### 3.2 Verification of Column Stochasticity

Column i of T_m: Σ_j [T_m]_{j,i} = Σ_j 1[t_j = m ∘ s_i] = 1 (exactly one t_j equals m∘s_i).

Column-stochasticity holds. JUSTIFICATION: Ax1 guarantees m∘s_i is a unique element of
Hom(I,B). Each source state maps to exactly one target state. ✓

### 3.3 Attempt to Verify Row Stochasticity

Row j of T_m: Σ_i [T_m]_{j,i} = Σ_i 1[t_j = m ∘ s_i] = |{s_i : m ∘ s_i = t_j}|

For this to equal 1 for every j, we need: every target state t_j ∈ Hom(I,B) is the image
of exactly one source state s_i ∈ Hom(I,A) under the map m_*.

This requires m_* to be a BIJECTION from Hom(I,A) to Hom(I,B).

### 3.4 Does Ax4 Force This Bijection?

Ax4 states: Σ_{m: A→B} ε(m) = 1 for each pair (A,B).

This normalizes ε over all morphisms between A and B. It says NOTHING about the map m_*
on state spaces. Specifically:

- Ax4 does not require m_* to be injective (two source states may map to the same target).
- Ax4 does not require m_* to be surjective (some target states may have no preimage).
- Ax4 does not require n_A = n_B (state space sizes may differ freely).

None of Ax1, Ax2, Ax3, Ax5 provides any additional constraint on m_* either:
- Ax1 only ensures m∘s_i ∈ Hom(I,B) is well-defined (existence of composition).
- Ax2 orders morphisms causally but places no constraint on action on state spaces.
- Ax3 reverses causal order for the dagger but does not imply symmetric normalization.
- Ax5 requires each Hom(I,X) to be a probability simplex — satisfied independently of m.

### 3.5 Exact Point of Failure

The proof of L1 fails at row stochasticity. The exact obstruction:

    Ax4 normalizes ε over Hom(A,B) for each pair (A,B).
    Row stochasticity requires normalization over preimages of each t_j under m_*.
    These are DIFFERENT normalization conditions.
    Ax4 is ASYMMETRIC: it fixes target-wise sums, not source-wise sums.
    Doubly stochastic requires SYMMETRIC normalization in both directions.
    No axiom in Ax1–Ax5 provides source-wise normalization.

The proof cannot be patched within Ax1–Ax5. No additional manipulation of the existing
axioms closes this gap — the gap is a genuine logical absence.

VERDICT: Proof of L1 FAILS at Step 3.3. Proceed to Phase 4.

---

## Phase 4 — Counterexample and Obstruction Classification

### 4.1 Explicit Counterexample

Construct the smallest CCA in which F9-H fails.

**Objects:** O = {A, B}

**State spaces:**
- Hom(I, A) = {s_1, s_2}      (two states)
- Hom(I, B) = {t_1, t_2}      (two states)
- One causal morphism m: A → B

**Weight assignments (Ax4):**

    ε(s_1) = 1/2,  ε(s_2) = 1/2      [on Hom(I,A); sum = 1 ✓]
    ε(t_1) = 9/10, ε(t_2) = 1/10     [on Hom(I,B); sum = 1 ✓]
    ε(m)   = 1                         [on Hom(A,B); sum = 1 ✓]

**Axiom verification:**
- Ax1: Symmetric monoidal category with unit I, identity morphisms, composition ✓
- Ax2: Causal order A ≤ B; locally finite (two-element poset) ✓
- Ax3: Dagger m†: B → A reverses order (B ≤ A in the dagger direction) ✓
- Ax4: Each hom-set sums to 1 (verified above) ✓
- Ax5: Each Hom(I,X) is a probability simplex; causal depth r(A)=0, r(B)=1 ✓

All axioms Ax1–Ax5 are satisfied.

**Entropy computation:**

    H(A) = −(1/2)log(1/2) − (1/2)log(1/2) = log 2 ≈ 0.693 nats

    H(B) = −(9/10)log(9/10) − (1/10)log(1/10)
         = −0.9·(−0.10536) − 0.1·(−2.30259)
         ≈ 0.09482 + 0.23026
         ≈ 0.325 nats

**Result:**

    H(B) ≈ 0.325 < 0.693 ≈ H(A)

F9-H fails: causal entropy decreases from A to B in this valid CCA.

**Causal entropy check (for F9 itself):**

    H_c(A) = H(A) + λ·r(A) = 0.693 + λ·0 = 0.693
    H_c(B) = H(B) + λ·r(B) = 0.325 + λ·1

For F9 to hold: 0.325 + λ ≥ 0.693  ⟹  λ ≥ 0.368

Since λ is a free unconstrained parameter (it appears in Definition D6 and Theorem 1.6
with no axiom fixing its value), F9 holds in this example ONLY IF λ ≥ 0.368.
The axioms do not force this.

**Summary of the counterexample:**
A valid CCA satisfying Ax1–Ax5 exists in which H(B) < H(A) for a causal morphism A → B.
F9-H is falsified in this CCA. F9 is falsified unless λ is sufficiently large, but λ is
not constrained by any axiom.

---

### 4.2 Obstruction Classification

Three independent obstructions are identified:

**Obstruction O-F9-1 — Mathematical (Asymmetric Normalization):**
Ax4 normalizes ε over each hom-set Hom(A,B) in the TARGET direction (fixed source A,
fixed target B, sum over morphisms between them). This is ONE-DIRECTIONAL normalization.
Doubly stochastic requires SYMMETRIC normalization: both column sums and row sums equal 1.
The transition matrix T_m is column-stochastic (from Ax4 applied to Hom(I,A)) but not
necessarily row-stochastic. No axiom in Ax1–Ax5 supplies the missing row normalization.
Type: MATHEMATICAL. The axiom system is logically insufficient to prove L1.

**Obstruction O-F9-2 — Logical (Independence):**
The counterexample shows a CCA with H(B) < H(A), and a different CCA (uniform ε_B) has
H(B) ≥ H(A). Both satisfy Ax1–Ax5. Therefore:
- F9-H is not provable from Ax1–Ax5 (counterexample exists)
- F9-H is not disprovable from Ax1–Ax5 (models satisfying it also exist)
F9 is LOGICALLY INDEPENDENT of Ax1–Ax5 in the model-theoretic sense.
Type: LOGICAL. Not a proof gap — a genuine independence result.

**Obstruction O-F9-3 — Parameter (Unconstrained λ):**
Even when H(B) < H(A), the rank term λ·[r(B)−r(A)] can compensate if λ is large enough.
But λ > 0 is not pinned by any axiom (Theorem 1.6 explicitly notes λ is a free parameter).
Furthermore, the required lower bound on λ depends on the specific CCA instance:
    λ ≥ [H(A) − H(B)] / [r(B) − r(A)]
The right-hand side is unbounded across all CCAs (H(A)−H(B) can be arbitrarily large with
r(B)−r(A)=1). So no finite λ satisfies F9 universally.
Type: MATHEMATICAL. λ is underdetermined by the axiom system.

**Summary of obstruction types:**

| ID     | Name                     | Type        | Removable by |
|--------|--------------------------|-------------|--------------|
| O-F9-1 | Asymmetric normalization | Mathematical| New axiom Ax4* |
| O-F9-2 | Logical independence     | Logical     | New axiom Ax4* |
| O-F9-3 | Unconstrained λ          | Mathematical| New axiom fixing λ or Ax4* |

None of these obstructions are PHYSICAL. They arise from the internal algebraic structure
of the axioms. There is no physical law being violated; rather, the axioms simply do not
say enough to force entropy increase.

---

### 4.3 What Removes the Obstruction

The three options below are ALTERNATIVES (not simultaneous requirements):

**Option A — Add Ax4* (Symmetric Normalization Axiom):**
    Ax4*: For every causal morphism m: A → B, the transition matrix T_m is doubly stochastic.

This directly postulates L1. With Ax4*, the DPI gives H(B) ≥ H(A) for all causal m,
and F9 follows from the rank monotonicity already proved (Theorem 2.18).
Ax4* is independent of Ax1–Ax5 — it is a new axiom, not a consequence.

**Option B — Source normalization condition (equivalent form of Ax4*):**
    For every B, every t ∈ Hom(I,B), and every causal m: A → B:
    Σ_{s ∈ Hom(I,A)} [T_m]_{t,s} = 1

When |Hom(I,A)| = |Hom(I,B)|, this is equivalent to Ax4*. In general it requires
a suitable measure-theoretic extension.

**Option C — Fix λ from detailed balance (partial rescue):**
If Ax3 (dagger structure) combined with Ax4 implies detailed balance
    ε(s) · [T_m]_{t,s} = ε(t) · [T_{m†}]_{s,t}
and if the stationary distribution is uniform (ε uniform on each hom-set), then T_m is
doubly stochastic and F9 follows. But this requires both detailed balance AND uniform ε,
neither of which is forced by Ax3 + Ax4 alone.

**Recommended resolution: Option A (Add Ax4*).**
It is minimal (one axiom), non-degenerate, and physically motivated by the interpretation
that causal evolution should not destroy information faster than causal structure creates it.

---

## Phase 5 — Status and Next Problem

### 5.1 Current Status of F9

**STATUS: FAILED**

F9 (CCA Causal Entropy Non-Decrease) is not provable from Ax1–Ax5 alone.

Evidence:
1. Proof of L1 fails at row stochasticity (Phase 3, Step 3.3).
   Ax4 provides only target-normalization; row normalization is not forced.

2. Explicit counterexample (Phase 4):
   CCA with O={A,B}, ε_A=(1/2,1/2), ε_B=(9/10,1/10), single causal m: A→B.
   Satisfies Ax1–Ax5. Gives H(B) ≈ 0.325 < 0.693 ≈ H(A). F9-H is false.

3. F9 is logically independent of Ax1–Ax5 (Obstruction O-F9-2):
   Both H(B)<H(A) and H(B)≥H(A) are consistent with the axioms.

4. Three independent obstructions identified:
   O-F9-1 (asymmetric normalization), O-F9-2 (logical independence),
   O-F9-3 (unconstrained λ).

5. No patch within Ax1–Ax5 exists. Removal requires a new axiom (Ax4*).

**Revised classification of F9:**
F9 is INDEPENDENT of Ax1–Ax5.

**Consequence:**
The second law of thermodynamics (entropy non-decrease) cannot be derived as a theorem
of the CCA framework with the current five axioms. It would need to be added as an
additional physical postulate (Ax4*) or derived from a physical principle that implies
Ax4* — which is the subject of the next problem.

---

### 5.2 Recommended Next Problem: F9-A

**F9-A — Physical Justification of Ax4* (Symmetric Normalization)**

**Precise statement:**

> Does any combination of physical requirements already accepted in the C2 program
> (U1–U6, R1–R7, Ax1–Ax5) imply the symmetric normalization condition:
>
>     For every causal m: A → B and every t_j ∈ Hom(I,B):
>     Σ_{s_i ∈ Hom(I,A)} [T_m]_{j,i} = 1
>
> i.e., does Ax4* follow from existing C2 foundations without being postulated independently?

**Why F9-A is the right next step:**
- Smaller than F9 (which requires the full entropy inequality)
- Smaller than F7, F4, F1 (which require new mathematical fields or continuum limits)
- Has a clear binary answer: YES (Ax4* is derivable) or NO (it is a new independent axiom)
- If YES → F9 is provable; status upgrades from FAILED to PASS
- If NO → this is itself a new obstruction theorem (second law is independent of C2)
- Does not require redesigning C2

**Three concrete sub-questions for F9-A (in order of tractability):**

**Sub-question F9-A.1 — Does detailed balance follow from Ax3 + Ax4?**

Detailed balance for causal morphism m: A → B reads:
    ε(s_i) · [T_m]_{j,i} = ε(t_j) · [T_{m†}]_{i,j}

If ε is uniform (ε(s_i) = 1/n_A for all i, ε(t_j) = 1/n_B for all j), detailed balance
implies T_m is doubly stochastic (when n_A = n_B). Ax3 provides the dagger m†; Ax4
provides ε. But Ax3 says only that m† reverses causal order — it does not constrain the
numerical relationship between ε(m) and ε(m†). So detailed balance is NOT forced by
Ax3 + Ax4 directly. This sub-question likely answers NO.

**Sub-question F9-A.2 — Does U4 (reproducibility) force symmetric normalization?**

U4 states that physical processes are reproducible: the same input reliably produces the
same output distribution. If a causal morphism m: A → B is reproducible, then the
backward transition (under m†) must also be well-defined and reproducible. The question
is whether reproducibility in both directions forces the joint (m, m†) system to be
doubly stochastic. This requires constructing the argument precisely within the C2
operational framework.

**Sub-question F9-A.3 — Does the C2 Gibbs structure (Theorem C2-Gibbs) force Ax4*?**

Theorem C2-Gibbs states: for the C2 candidate (finite ergodic Markov chains), the unique
maximum-entropy distribution is the Gibbs distribution. For this to hold in the CCA, the
transition matrices restricted to causal morphisms must be doubly stochastic with respect
to the Gibbs measure. Whether this pins Ax4* in the CCA context is the question.

**Ranking of F9-A against other near-term frontiers:**

| Problem   | Scientific Importance | Tractability | Dependencies   | Recommended order |
|-----------|-----------------------|--------------|----------------|-------------------|
| F9-A      | High (closes 2nd law) | High         | None beyond C2 | 1st               |
| F8 (GNS)  | Medium                | Medium-high  | None           | 2nd               |
| F11 (NM)  | Medium                | Very high    | M1, M2 needed  | 3rd               |
| F1 (PA1)  | Very high             | Medium       | None           | 4th (longer term) |

**F9-A is the recommended next problem.**

---

## Summary Table

| Phase | Question | Result |
|-------|----------|--------|
| 1 | What is F9 exactly? | H_c(B) ≥ H_c(A) for causal m:A→B; H_c = H + λr |
| 1 | Classification | INDEPENDENT of Ax1–Ax5 |
| 2 | Smallest missing lemma | L1: T_m is doubly stochastic |
| 3 | Can L1 be proved? | NO — fails at row stochasticity (Ax4 asymmetric) |
| 4 | Counterexample | ε_A=(½,½), ε_B=(9/10,1/10): H(B)<H(A), Ax1–Ax5 satisfied |
| 4 | Obstruction type | Mathematical + Logical (not physical) |
| 5 | F9 status | FAILED |
| 5 | Next problem | F9-A: Does Ax3+Ax4+U4/R7 imply Ax4* (doubly stochastic)? |

---

## Appendix: Precise Statement of Ax4*

**Proposed Axiom Ax4* (Symmetric Normalization for Causal Morphisms):**

> For every causal morphism m: A → B (i.e., m ∈ M with A ≤ B in (M,≤)), the
> transition matrix T_m defined by [T_m]_{j,i} = ε(t_j | s_i) (conditional probability
> of arriving at state t_j ∈ Hom(I,B) given input state s_i ∈ Hom(I,A) under m)
> is doubly stochastic:
>
>     Σ_j [T_m]_{j,i} = 1  for all i    (column-stochastic; follows from Ax4)
>     Σ_i [T_m]_{j,i} = 1  for all j    (row-stochastic; NEW requirement)

This axiom is:
- Consistent with Ax1–Ax5 (the uniform example satisfies it)
- Independent of Ax1–Ax5 (the counterexample violates it while satisfying Ax1–Ax5)
- Sufficient to prove F9 (via DPI + rank monotonicity)
- Not necessary for the CCA to be well-defined (all internal structures of Subsection 1
  of C2_FOUNDATIONS remain valid without Ax4*)

Whether Ax4* is physically motivated is the content of problem F9-A.

---

*Document compiled: 2026-07-24*  
*All C2 results treated as established per C2_FOUNDATIONS.md.*  
*No C2 results were modified or extended in this document.*
