# Interaction Hamiltonian Uniqueness Audit
## Can H_int = g J σ_z Be Derived from the Substrate Theory?

**Status:** Mathematical audit — no new physics introduced  
**Source documents read:** microscopic_derivation.md, substrate_transport_derivation.md,
interaction_hamiltonian_derivation.md, effective_master_equation_derivation.md,
decoherence_chain_summary.md  
**Task:** Determine uniqueness or non-uniqueness. Report the mathematics.

Every step is labelled:
- **[D]** Exact derivation — follows from previous steps by logic or algebra alone
- **[I]** Mathematical identity — no physical content
- **[A]** Constitutive assumption — new physical input, not forced by the theory
- **[P]** Phenomenological postulate — physically motivated but not derived

---

## Part I — The Substrate Theory: What It Contains

### Section 1: Complete Inventory of Established Variables

The substrate theory, as established in microscopic_derivation.md and
substrate_transport_derivation.md, defines the following variables. These are
all the variables the theory has. No others are available.

**Microscopic (PRW) level:**

| Variable | Type | Domain | Definition |
|----------|------|--------|------------|
| n⁺(x,t) | real scalar field | ℝ × ℝ⁺ | density of right-moving information quanta |
| n⁻(x,t) | real scalar field | ℝ × ℝ⁺ | density of left-moving information quanta |
| v | real positive constant | — | PRW particle speed = c |
| λ | real positive constant | — | direction-reversal rate |

**Macroscopic (transport) level — derived from PRW:**

| Variable | Type | Domain | Derivation |
|----------|------|--------|-----------|
| s(x,t) = n⁺+n⁻ | real scalar field | ℝ × ℝ⁺ | [D] sum of PRW densities |
| J(x,t) = v(n⁺−n⁻) | real scalar field | ℝ × ℝ⁺ | [D] net flux |
| τ = 1/(2λ) | real positive constant | — | [D] mean free time |
| c = v | real positive constant | — | [D] wave speed |

**Derived composite quantities:**

| Variable | Definition | Status |
|----------|-----------|--------|
| E_sub = ½c²s²+½J² | energy-like density | [D] from (s,J) |
| P_sub = sJ | momentum-like density | [D] from (s,J) |

**Established transport equations:**

```
∂s/∂t + ∂J/∂x = 0                          [C-s]   (continuity, exact)
∂J/∂t + c²∂s/∂x = −(1/τ)J                  [C-J]   (flux equation, exact)
```

**What is NOT in the substrate theory:**

The substrate theory contains no:
- Qubit Hilbert space ℂ²
- Pauli operators σ_x, σ_y, σ_z, I
- Qubit density matrix ρ_S
- Planck constant ℏ (it does not appear anywhere in [C-s] or [C-J])
- Coupling constant g
- Any operator acting on a 2-level system

This inventory is complete and exhaustive. The audit proceeds from this inventory alone.

---

### Section 2: Mathematical Nature of the Substrate Variables

Each substrate variable is examined for its mathematical type and transformation properties. These properties will constrain which qubit operators a coupling can be consistent with, if any constraints exist at all.

**s(x,t):** real scalar field.
- Dimensions: [info/m³]
- Sign: s ≥ 0 (it is a sum of non-negative densities)
- Time-reversal T: under T, right-movers and left-movers are exchanged, so n⁺ ↔ n⁻ and s → s. **s is T-even.**
- Spatial parity P (x → −x): n⁺(x) → n⁻(−x), n⁻(x) → n⁺(−x), so s(x) → s(−x). **s is P-even (a scalar).**

**J(x,t):** real scalar field (in 1D; vector field in 3D).
- Dimensions: [info/(m²·s)]
- Sign: J can be positive or negative
- Time-reversal T: under T, right-movers become left-movers: n⁺ → n⁻, n⁻ → n⁺, so J = v(n⁺−n⁻) → v(n⁻−n⁺) = −J. **J is T-odd.**
- Spatial parity P: J(x) → −J(−x). **J is a pseudovector component (P-odd in 1D).**

**E_sub = ½c²s²+½J²:**
- Dimensions: [info²·c²/m⁶] (not energy until multiplied by a coupling)
- T: c²s² is T-even; J² is T-even (square). **E_sub is T-even.**
- P: E_sub(x) → E_sub(−x). **E_sub is P-even.**

**P_sub = sJ:**
- T: s is T-even, J is T-odd, so P_sub is **T-odd.**
- P: P_sub(x) → −P_sub(−x). **P_sub is P-odd.**

**Summary of transformation properties:**

| Variable | T-parity | P-parity | Sign-definite? |
|----------|----------|----------|---------------|
| s | even (+1) | even (+1) | yes (≥ 0) |
| J | odd (−1) | odd (−1) | no |
| E_sub | even (+1) | even (+1) | yes (≥ 0) |
| P_sub | odd (−1) | odd (−1) | no |

---

## Part II — The Qubit Hilbert Space

### Section 3: Complete Basis of Hermitian Operators on ℂ²

The qubit lives in ℂ². Every Hermitian operator on ℂ² is a real linear combination of
{I, σ_x, σ_y, σ_z}. This is a mathematical identity — it is the complete basis of the
real vector space of 2×2 Hermitian matrices, which has dimension 4.

**[I] Basis theorem:** Every Hermitian A ∈ M₂(ℂ) can be written uniquely as:

```
A = a₀ I + a₁ σ_x + a₂ σ_y + a₃ σ_z,    a₀,a₁,a₂,a₃ ∈ ℝ
```

The most general Hermitian interaction Hamiltonian that is linear in a single classical
scalar field F(x,t) is therefore:

```
H_int = F(x_q, t) · (a₀ I + a₁ σ_x + a₂ σ_y + a₃ σ_z)
```

where (a₀, a₁, a₂, a₃) ∈ ℝ⁴ are four real coefficients.

**[I] Simplification:** The identity component a₀ I contributes only a global phase to the
qubit wavefunction. It shifts the energy of both |0⟩ and |1⟩ equally and has no effect
on any observable (density matrix or expectation value). It is physically unobservable and
can be dropped without loss of generality.

After dropping a₀ I, the general traceless Hermitian qubit operator is:

```
A = a₁ σ_x + a₂ σ_y + a₃ σ_z,    a₁²+a₂²+a₃² > 0
```

Normalising: writing **n** = (a₁, a₂, a₃)/|**a**|, the operator is:

```
A = |**a**| (**n** · **σ**)
```

where **n** is a unit vector on S² and |**a**| > 0 is an overall scale (absorbed into g).

**[D] Conclusion:** The family of admissible traceless Hermitian qubit operators is
parametrised by a unit vector **n** ∈ S², a 2-sphere. This family is continuous and
infinite. No element of the substrate theory selects a preferred **n**.

### Section 4: Transformation Properties of Pauli Operators

Under the standard quantum-mechanical transformation rules:

**Time reversal T** (antiunitary, T = iσ_y K where K is complex conjugation):
```
T σ_x T⁻¹ = −σ_x
T σ_y T⁻¹ = −σ_y          [I: standard QM result]
T σ_z T⁻¹ = −σ_z
```
All three Pauli operators are T-odd in quantum mechanics.

**Note on T-parity matching:** Since J is T-odd and all Pauli operators are T-odd, the
coupling J · (**n** · **σ**) is T-even (odd × odd = even) for any **n** ∈ S².
Similarly, since s is T-even and all Pauli operators are T-odd, the coupling
s · (**n** · **σ**) is T-odd for any **n**.

This shows that T-parity, while relevant if T-invariance is imposed, does not by itself
select σ_z over σ_x or σ_y. It only discriminates between s-coupling and J-coupling:

- J · (**n** · **σ**): T-even — compatible with a T-invariant H
- s · (**n** · **σ**): T-odd — would violate T-invariance

**[A] Note:** T-invariance of H_int is an additional assumption, not a consequence of the
substrate transport equations. The substrate equations [C-s] and [C-J] are themselves
T-invariant only after including the source terms; the damping term −J/τ in [C-J] is
T-odd (it involves the first power of J), making the substrate dynamics T-non-invariant
in general. Therefore T-invariance cannot be used to constrain H_int without introducing
a separate assumption.

---

## Part III — Constraint Analysis

### Section 5: Layer-by-Layer Constraint Application

We now systematically apply every constraint that the established substrate theory imposes
on a candidate interaction Hamiltonian, tracking precisely what is derived and what
requires additional input.

**The candidate H_int must satisfy:**
1. It is an observable (Hermitian operator on the total Hilbert space ℋ_S ⊗ ℋ_B)
2. It couples the qubit ℋ_S to the substrate bath ℋ_B
3. It has units of energy [J]

These three requirements follow from the definition of a Hamiltonian. They are physical
requirements, not derived from the substrate transport equations.

#### Constraint Layer 0: Mathematical structure of H_int

The most general bilinear coupling between a qubit and a classical field F is:

```
H_int = F(x_q, t) ⊗ A_S                                    [GEN-0]
```

where F is a real classical function of substrate variables evaluated at the qubit
location x_q, and A_S is a Hermitian operator on ℂ².

**[D] From Section 3:** A_S = a₀I + a₁σ_x + a₂σ_y + a₃σ_z with a_i ∈ ℝ.

**Admissible family at Layer 0:**

```
F_0 = { H_int = F(x_q,t)·A_S :  F ∈ C(substrate variables),  A_S ∈ Herm(ℂ²) }
```

This is infinite-dimensional. The substrate theory imposes no restriction on F or A_S
beyond the requirements of Layer 0.

#### Constraint Layer 1: F must depend only on established substrate variables

The substrate theory has only {s, J} as independent fields (E_sub and P_sub are
functions of s and J). Therefore F must be a function F(s(x_q,t), J(x_q,t)).

**[D] Admissible family at Layer 1:**

```
F_1 = { H_int = F(s, J) · A_S :  F: ℝ≥0 × ℝ → ℝ smooth,  A_S ∈ Herm(ℂ²) }
```

This is still infinite-dimensional. Neither F nor A_S is constrained beyond what
was already required by Layer 0.

#### Constraint Layer 2: Dimensional analysis

H_int must have units of energy [J = kg·m²/s²]. The substrate variables have units:

```
[s] = info/m³
[J] = info/(m²·s)
[c] = m/s
[τ] = s
```

The qubit operators are dimensionless. The coupling constant g must supply the
dimensional factor. There is no constraint on the functional form of F from
dimensional analysis alone — any monomial or combination can be made dimensionally
consistent by choosing g with appropriate units.

For a coupling linear in J: [g] = J·m²·s/info, as established in
interaction_hamiltonian_derivation.md.
For a coupling linear in s: [g_s] = J·m³/info.
For a coupling in E_sub = ½c²s²+½J²: [g_E] = J·m⁶/info².

**[D] Dimensional analysis does not select the functional form of F.** It only
constrains the units of g given F. The admissible family remains F_1.

#### Constraint Layer 3: [A-lin-coupling] — Linearity in J

The existing derivation (interaction_hamiltonian_derivation.md, Section 1) introduces:

> **Assumption [A-lin-coupling]:** The coupling between qubit and substrate is linear
> in J. This is the minimal (lowest-order) coupling.

This assumption is explicitly labelled as an **assumption** in the source document.
It is **not derived** from the transport equations or the PRW. It is justified by
the argument that it is the "minimal" or "lowest-order" coupling, which is a
convenience postulate (analogous to minimal coupling in electromagnetism), not a
mathematical necessity.

Under [A-lin-coupling], F(s,J) is restricted to be linear in J:

```
F(s, J) = g · J    (leading linear term)
```

**[A] Status:** Constitutive assumption, explicitly labelled as such in the source.

**Admissible family at Layer 3 (given [A-lin-coupling]):**

```
F_3 = { H_int = g · J(x_q, t) · A_S :  g ∈ ℝ\{0},  A_S ∈ Herm(ℂ²) }
```

The family has now been reduced to a 4-parameter family: g and the three components
of A_S (in the traceless basis after dropping the identity). However, A_S is still
completely free — any direction **n** ∈ S² is admissible.

**[D] Non-uniqueness proof at Layer 3:**

Let H₁ = g J σ_z and H₂ = g J σ_x. Both satisfy all constraints of Layers 0–3.
Both are Hermitian, linear in J, local, and dimensionally consistent. Therefore the
coupling is **not unique** after [A-lin-coupling] alone.

#### Constraint Layer 4: [A-local] — Local coupling at x_q

The existing derivation introduces:

> **Assumption [A-local]:** The qubit couples to the substrate current at the qubit's
> location x_q. This is the electric-dipole approximation.

This assumption is also explicitly labelled as such. It restricts F to be evaluated
at a single point x_q. It does not constrain A_S.

**Admissible family at Layer 4 (given [A-lin-coupling] and [A-local]):**

```
F_4 = { H_int = g · J(x_q, t) · A_S :  g ∈ ℝ,  A_S = n₁σ_x+n₂σ_y+n₃σ_z,
         (n₁,n₂,n₃) ∈ S² }
```

The family is still a continuous 2-parameter family (the sphere S²). No substrate
variable constrains which direction **n** is preferred.

---

### Section 6: What the Substrate Theory Contributes to Operator Selection

This section examines whether any property of the substrate variables {s, J, E_sub, P_sub}
selects a preferred qubit operator direction.

**Question:** Is there any mathematical mapping from the substrate theory to a preferred
direction **n** ∈ S²?

**Observation 1:** The substrate fields s(x,t) and J(x,t) are real scalar (or vector in
3D) classical fields. They are elements of an infinite-dimensional function space
C(ℝ, ℝ). There is no natural algebraic structure in this function space that maps
onto the Lie algebra su(2) (which contains {σ_x/2, σ_y/2, σ_z/2}).

**[D] Proof of absence of natural map:**

The substrate theory operates entirely within the category of real commutative algebras
(pointwise multiplication of real-valued functions). The qubit operators belong to the
non-commutative algebra M₂(ℂ). A map between these two algebraic structures requires
additional structure not present in the transport equations. Specifically:

- The transport equations [C-s] and [C-J] are linear PDEs over ℝ. Their solution
  space is a real vector space with no preferred basis in ℝ⁴.
- The Hermitian matrices Herm(ℂ²) form a 4-dimensional real vector space with a
  Lie bracket [A,B] = i(AB−BA) that gives it the structure of su(2) ⊕ ℝ.
- The commutator structure of su(2) — the fact that [σ_z, σ_x] = 2iσ_y — has no
  analogue in the scalar transport theory.
- Therefore no canonical map from {F(s,J)} → Herm(ℂ²) exists within the substrate
  theory. Any such map requires external input specifying the alignment.

**Observation 2:** The substrate theory provides a preferred **spatial** direction (the
direction of J in 3D), but not a preferred **Hilbert-space** direction.

In 3D, J is a vector field: **J**(x,t). If the qubit has a preferred spin-quantisation
axis ẑ (defined by the free Hamiltonian H_S = ½ℏω_q σ_z), then there is a kinematic
identification: **J** · ẑ gives a scalar with the same T-parity as J. This produces a
coupling H_int = g (J·ẑ) σ_z. But this identification requires knowing ẑ — the
qubit's energy quantisation axis — which is input from the qubit's internal structure,
not from the substrate.

**[D] Conclusion:** The substrate theory provides no mechanism to select **n** ∈ S².
The selection of σ_z requires an additional physical criterion not present in the
substrate transport equations.

---

### Section 7: The Physical Criterion Used in interaction_hamiltonian_derivation.md

Section 2 of interaction_hamiltonian_derivation.md selects A = σ_z by imposing the
criterion: **"pure Ramsey dephasing"** — decay of ρ₀₁ without population transfer.

This criterion is examined here for its logical status.

**[A] Pure Ramsey dephasing criterion:** The interaction Hamiltonian must produce
decay of coherences ρ₀₁(t) = ρ₀₁(0)e^{−Γt} without altering populations
ρ₀₀(t) = ρ₀₀(0), ρ₁₁(t) = ρ₁₁(0).

**Status of this criterion:** This is a **phenomenological postulate** — it selects
H_int to match the observed behaviour of a Ramsey experiment. It is NOT derived from:
- The substrate transport equations
- The PRW microscopic rules
- Any property of s, J, E_sub, or P_sub

It is derived from the observation that the experiment shows pure dephasing. This makes
it an empirical input, not a theoretical derivation from the substrate.

**[D] Derivation: σ_z is necessary and sufficient for pure dephasing**

Given the assumption of linearity in J and locality, H_int = g J A_S for some
traceless Hermitian A_S = n₁σ_x + n₂σ_y + n₃σ_z.

Under the Born-Markov master equation, the populations evolve as:

```
dρ₀₀/dt = −(g²/ℏ²) · (∫C_JJ dτ) · [A_S, [A_S, ρ]]₀₀
```

**[I] Algebraic computation:** For A_S = n₁σ_x + n₂σ_y + n₃σ_z:

```
[A_S, [A_S, ρ]]₀₀ = 2(A_S²)₀₀ · ρ₀₀ − 2(A_S)₀₀² · ρ₀₀ − 2|(A_S)₀₁|² · ρ₀₀
                   + 2[(A_S)₀₁(A_S)₁₀ · ρ₁₁] + ...
```

More precisely, expanding the double commutator:

```
[A_S, [A_S, ρ]] = A_S²ρ − 2A_SρA_S + ρA_S²
```

The (0,0) element:

```
[A_S,[A_S,ρ]]₀₀ = (A_S²)₀₀ρ₀₀ + (A_S²)₀₁ρ₁₀ − 2(A_S)₀₀(A_S ρ)₀₀ − 2(A_S)₀₁(A_S ρ)₁₀ + ...
```

Evaluating for the general A_S = n₁σ_x + n₂σ_y + n₃σ_z:

Using σ_i² = I and {σ_i, σ_j} = 2δ_{ij}I:

```
A_S² = (n₁²+n₂²+n₃²)I = |n|²I = I    (for unit n)
```

Therefore:

```
[A_S,[A_S,ρ]]₀₀ = ρ₀₀ + 0 − 2[(A_S)₀₀(A_Sρ)₀₀ + (A_S)₀₁(A_Sρ)₁₀ + ...]₀₀
```

For the population equation:

```
dρ₀₀/dt ∝ (A_S ρ A_S − ρ)₀₀ = (A_S ρ A_S)₀₀ − ρ₀₀
```

```
(A_S ρ A_S)₀₀ = Σ_{k,l} (A_S)₀k ρ_{kl} (A_S)_{l0}
```

For A_S = n₃σ_z (pure σ_z case, n₁=n₂=0, n₃=1):

```
(σ_z)₀₀ = 1, (σ_z)₀₁ = 0, (σ_z)₁₀ = 0, (σ_z)₁₁ = −1
(σ_z ρ σ_z)₀₀ = (σ_z)₀₀ ρ₀₀ (σ_z)₀₀ = 1·ρ₀₀·1 = ρ₀₀
```

Therefore dρ₀₀/dt ∝ ρ₀₀ − ρ₀₀ = 0. ✓ Pure dephasing.

For A_S = σ_x (n₁=1, n₂=n₃=0):

```
(σ_x ρ σ_x)₀₀ = (σ_x)₀₁ ρ₁₀ (σ_x)₀₁* + (σ_x)₀₀ ρ₀₀ (σ_x)₀₀* + ...
              = 1·ρ₁₁·1 = ρ₁₁
```

Therefore dρ₀₀/dt ∝ ρ₁₁ − ρ₀₀ ≠ 0 in general. Population transfer occurs. ✗

**[D] General result:** Population transfer vanishes if and only if (A_S ρ A_S)₀₀ = ρ₀₀.
This requires (A_S)₀₁ = 0 (no off-diagonal entries in the qubit's energy basis),
i.e., A_S must be diagonal in the {|0⟩,|1⟩} basis. The only traceless diagonal
2×2 Hermitian matrix (up to scale) is σ_z.

**[D] Uniqueness under pure-dephasing criterion:**

```
A_S produces pure dephasing  ⟺  A_S ∝ σ_z
```

**Proof:**

(⟸) If A_S = n₃σ_z: shown above, dρ₀₀/dt = 0. ✓

(⟹) If A_S = n₁σ_x + n₂σ_y + n₃σ_z with (n₁,n₂) ≠ (0,0):

```
(A_S)₀₁ = n₁(σ_x)₀₁ + n₂(σ_y)₀₁ + n₃(σ_z)₀₁ = n₁ − in₂ ≠ 0
```

So (A_S ρ A_S)₀₀ contains |(A_S)₀₁|² ρ₁₁ = (n₁²+n₂²) ρ₁₁.

This contributes to dρ₀₀/dt a term proportional to ρ₁₁ − ρ₀₀, which is non-zero
for a general initial state. Therefore A_S does NOT produce pure dephasing unless
n₁ = n₂ = 0, i.e., A_S ∝ σ_z. ∎

**Status of the uniqueness proof:**

The proof in Section 7 shows that **given [A-lin-coupling], [A-local], and the
phenomenological requirement of pure dephasing**, the operator A_S = σ_z is
the unique (up to sign) traceless Hermitian operator.

However, the pure-dephasing requirement is a **[P] phenomenological postulate** —
it is not derivable from the substrate variables. The substrate theory does not
predict what type of dephasing occurs; it only supplies the field J that enters
the coupling.

---

## Part IV — The Full Admissible Family

### Section 8: Family Without Any External Constraints

**Without** any assumptions beyond the existence of a qubit-substrate coupling, the
full admissible family is:

```
F_full = { H_int = F(s(x_q,t), J(x_q,t)) · (a₁σ_x + a₂σ_y + a₃σ_z) :
            F: ℝ²→ℝ smooth,  a₁,a₂,a₃ ∈ ℝ,  (a₁,a₂,a₃) ≠ 0 }
```

This family is infinite-dimensional (F ranges over all smooth functions of two variables)
and has a continuous 2-sphere of operator directions. The dimension counting:

- Substrate field component: ∞ (all smooth functions of s and J)
- Operator direction: 2 real parameters (S²)
- Overall scale: 1 real parameter (g, absorbed from above)

**F_full is infinite-dimensional.** The substrate theory alone does not restrict it.

### Section 9: Family After [A-lin-coupling] Only

Restricting F to be linear in J (and not involving s at leading order):

```
F_lin = { H_int = g · J(x_q,t) · A_S :
           g ∈ ℝ\{0},  A_S = n₁σ_x+n₂σ_y+n₃σ_z,  (n₁,n₂,n₃) ∈ S² }
```

This is a **3-parameter family** (one S², one scale g). The direction **n** is
unconstrained. Multiple distinct Hamiltonians are admissible.

**Explicit admissible examples:**

| H_int | Operator | Physical effect | Admissible? |
|-------|----------|----------------|------------|
| g J σ_z | longitudinal | pure dephasing (T₁=∞) | Yes |
| g J σ_x | transverse x | relaxation + dephasing | Yes |
| g J σ_y | transverse y | relaxation + dephasing | Yes |
| g J (σ_x+σ_z)/√2 | mixed | partial relaxation | Yes |
| g J (σ_y+σ_z)/√2 | mixed | partial relaxation | Yes |

All five examples satisfy [A-lin-coupling] and [A-local] exactly. No mathematical
argument within the substrate theory excludes any of them.

### Section 10: Family After [A-lin-coupling] + [A-local] + Pure-Dephasing Criterion

Adding the phenomenological requirement that the coupling produces pure dephasing:

```
F_pd = { H_int = g · J(x_q,t) · σ_z :  g ∈ ℝ\{0} }
```

This is a **1-parameter family** (the coupling strength g). The direction is fixed
to σ_z. The family is now parametrised by g alone.

**[D] Non-uniqueness at this level:** The family F_pd still contains H_int = +g J σ_z
and H_int = −g J σ_z (opposite signs of g). These are physically distinct — they
predict the same dephasing rate Γ ∝ g² (since Γ depends on g², not g), so the
sign of g is unobservable from decoherence measurements alone. The magnitude |g|
remains a free parameter.

### Section 11: Constraint on g

The coupling constant g is examined here. The question is whether the substrate
theory constrains, determines, or leaves free the value of g.

**[D] g does not appear in any substrate equation.**

The transport equations:
```
∂s/∂t + ∂J/∂x = 0
∂J/∂t + c²∂s/∂x = −(1/τ)J
```

contain the parameters {c, τ} (or equivalently {v, λ}). The constant g appears
nowhere in these equations. The substrate theory is a classical field theory; g is
the quantum-classical coupling, which lives at the interface between the classical
field and the quantum Hilbert space.

**[D] Dimensional argument:** From interaction_hamiltonian_derivation.md:

```
[g] = J·m²·s/info
```

This unit involves Joules (energy) and is not expressible in terms of the substrate
parameters alone:
- [c] = m/s, [τ] = s, [v] = m/s, [λ] = s⁻¹, [s₀] = info/m³, [J₀] = info/(m²·s)

No combination of these produces a quantity with units J·m²·s/info = kg·m⁴/s·info.
In particular, ℏ = J·s is not in the substrate theory. The quantity g/ℏ (which
appears in k_rot = 8g²s₀²r_q²τ/(3ℏ²)) requires ℏ, which is external to the
substrate theory.

**[D] Theorem (g is free):** The value of g cannot be derived from or constrained
by the substrate transport equations {[C-s], [C-J]} and the PRW parameters {v, λ}.

**Proof:** The substrate equations are a pair of linear PDEs in s and J. Their
solution space is determined entirely by the boundary/initial conditions and the
parameters {c, τ}. The quantity g plays no role in any of these equations. The
equations are consistent and well-posed for any value of g (including g = 0, which
corresponds to no coupling). Therefore the substrate theory is equally valid for
any g ∈ ℝ. g is a free parameter. ∎

**[D] Corollary:** The coupling coefficient k_rot = 8g²s₀²r_q²τ/(3ℏ²) is also
undetermined by the substrate theory, since it depends on g and ℏ, neither of
which is in the substrate theory.

---

## Part V — The Three Obstructions

### Section 12: Precise Statement of Each Obstruction

Three distinct mathematical obstructions prevent the derivation of H_int = g J σ_z
from the substrate theory. Each is identified precisely.

---

**Obstruction OB-A: The qubit Hilbert space is not in the substrate theory.**

The substrate theory operates on classical fields s(x,t) and J(x,t) over ℝ.
The qubit is a 2-level quantum system with Hilbert space ℂ². The mathematical
objects are in different categories:

```
Substrate theory: C∞(ℝ, ℝ) — smooth real-valued functions on space
Qubit theory:     M₂(ℂ) — 2×2 complex matrices
```

There is no morphism between these two structures that is derivable from the substrate
transport equations alone. The identification of the qubit Hilbert space requires
introducing ℂ² as additional input — it is not generated by the substrate theory.

**Type:** Categorical gap (classical ↔ quantum). Cannot be bridged without additional
physical input specifying the quantum system.

**What is needed to close OB-A:** A specification of the quantum system that couples
to the substrate — its Hilbert space, its free Hamiltonian H_S, and the principle
by which it couples. None of these follow from [C-s] and [C-J].

---

**Obstruction OB-B: Even with a qubit Hilbert space, the operator direction is undetermined.**

After introducing ℂ² (closing OB-A by assumption) and accepting [A-lin-coupling]
and [A-local], the admissible family is still F_4 = {g J (**n**·**σ**) : **n** ∈ S²}.
The direction **n** is a continuous free parameter.

The substrate theory provides no preferred direction in ℂ². The fields s and J are
real-valued; they carry no information about the internal structure of the qubit.
The coupling direction **n** must be specified by:

(a) The alignment of the qubit's energy axis (ẑ, the direction that diagonalises H_S)
    with the physical direction of J — this requires knowledge of H_S, which is
    external to the substrate theory. OR

(b) A phenomenological criterion such as pure dephasing — also external to the
    substrate theory (see Section 7).

**Type:** Operator selection ambiguity. The substrate theory has no su(2) structure
that would select a preferred direction in Herm(ℂ²).

**What is needed to close OB-B:** Either (a) knowledge of the qubit's energy axis
and its relation to J, OR (b) the pure-dephasing phenomenological criterion.
Criterion (b) is not derivable from the substrate theory; it is an empirical
characterisation of the experiment.

---

**Obstruction OB-C: The coupling constant g is not determined.**

After closing OB-A and OB-B (by assumption + phenomenology), the remaining family is
F_pd = {g J σ_z : g ∈ ℝ\{0}}. The value of g is a free parameter.

The substrate theory has no equation involving g. The constant g encodes the
quantum-classical coupling strength — the amount by which a unit substrate current
perturbation shifts the qubit energy. This is analogous to the elementary charge e
in electrodynamics (which is not derivable from Maxwell's equations alone).

**Type:** Coupling constant underdetermination. Standard in any classical-quantum
interface theory.

**What is needed to close OB-C:** Experimental measurement of the dephasing rate at
known ω_rot, from which k_rot = 8g²s₀²r_q²τ/(3ℏ²) can be extracted, and then g
inferred given s₀, r_q, τ, ℏ. This is purely empirical.

---

### Section 13: Summary Table of All Constraints

| Constraint | Source | Type | Narrows family? | Residual freedom |
|------------|--------|------|----------------|-----------------|
| H_int Hermitian | Definition of observable | [D] | Yes: excludes non-Hermitian | A_S ∈ Herm(ℂ²) |
| H_int linear in substrate | None | — | No: all F(s,J) remain | ∞-dim family |
| [A-lin-coupling]: F = J | interaction_hamiltonian_derivation.md | [A] | Partial: restricts F to J | S² × ℝ family |
| [A-local]: point x_q | interaction_hamiltonian_derivation.md | [A] | Partial: point evaluation | S² × ℝ family |
| Pure dephasing | Experiment / phenomenology | [P] | Yes: fixes A_S = σ_z | ℝ\{0} (one parameter) |
| Determine g | None in substrate | — | No | g free |

**Counting the residual degrees of freedom:**

After all constraints of the substrate theory (Layers 0–4): **3 free parameters** (S² direction + scale g).

After adding the phenomenological pure-dephasing criterion: **1 free parameter** (scale |g|, sign unobservable).

After empirical calibration of k_rot: **0 free parameters**.

The substrate theory alone leaves a **3-parameter family of admissible Hamiltonians**.

---

## Part VI — Mandatory Conclusion

### Section 14: Evaluation Against Each Possible Conclusion

**Conclusion A: "The interaction Hamiltonian is fully derivable from the substrate."**

This would require that the substrate variables {s, J, E_sub, P_sub, n⁺, n⁻} and
the transport equations [C-s, C-J] uniquely determine H_int = g J σ_z — including
the operator direction σ_z, the coupling form J, and the constant g — with no
external input.

**This is FALSE.**

Proof: OB-A shows the substrate theory contains no qubit Hilbert space (the theory
is classical), OB-B shows that even introducing ℂ² as input does not select σ_z
from the substrate variables alone, and OB-C shows g is undetermined. At minimum
three pieces of external input are required:
(1) The qubit Hilbert space ℂ²,
(2) The operator direction (via [A-lin-coupling] + pure-dephasing criterion or equivalent),
(3) The numerical value of g.
None of these follows from [C-s] and [C-J].

**Conclusion A is rejected.**

---

**Conclusion B: "The interaction Hamiltonian is unique up to an overall coupling constant."**

This would require that the substrate variables select the coupling form J and the
operator direction σ_z uniquely, with only the scale g remaining free.

**This is FALSE.**

Proof: Under the substrate theory alone (no [A-lin-coupling], no pure-dephasing
criterion), the admissible family is F_1 = {F(s,J)·A_S}. This contains:
- Couplings in s: g_s s σ_z (equally admissible with coupling to J)
- Couplings in J: g_J J σ_z
- Couplings in E_sub: g_E E_sub σ_z
- Couplings in P_sub: g_P P_sub σ_z
- All transverse couplings: g J σ_x, g J σ_y, etc.

None of these is excluded by [C-s] and [C-J]. The family is not "unique up to a
coupling constant" — it contains different functional forms and different operator
directions.

Even after imposing [A-lin-coupling] (an explicit assumption in the source documents),
the family F_lin = {g J (**n**·**σ**)} contains a continuous S² of directions. It is
not unique.

**Conclusion B is rejected.**

---

**Conclusion C: "Multiple Hamiltonians are mathematically admissible."**

This states that the constraints derivable from the substrate theory admit more than
one distinct H_int.

**This is TRUE.**

Proof: Exhibit two distinct admissible families:

1. H_int^(1) = g J σ_z — satisfies [A-lin-coupling], [A-local], Hermitian, dimensionally
   consistent.

2. H_int^(2) = g J σ_x — satisfies [A-lin-coupling], [A-local], Hermitian, dimensionally
   consistent.

3. H_int^(3) = g_s s σ_z — satisfies [A-local], Hermitian, dimensionally consistent (with
   different unit coupling g_s).

4. H_int^(4) = g_E E_sub σ_z — satisfies [A-local], Hermitian, dimensionally consistent
   (nonlinear in substrate variables, with different unit coupling g_E).

5. H_int^(5) = g (J σ_z + ε s σ_x) — satisfies [A-local], Hermitian (for any ε ∈ ℝ).

All five are distinct elements of the admissible family F_full. No equation in the
substrate theory excludes any of them. The family is not only non-unique — it is
infinite-dimensional.

**Conclusion C is TRUE.**

---

**Conclusion D: "The current theory lacks sufficient information to derive the
interaction Hamiltonian."**

This states that the substrate theory is incomplete as a derivational basis for H_int.

**This is also TRUE**, and it is the stronger statement.

Specifically, the theory lacks:
1. The quantum system itself (no Hilbert space in the substrate)
2. The coupling principle (no mechanism in [C-s, C-J] that generates a Hamiltonian)
3. The operator selection criterion (no pure-dephasing condition in the substrate)
4. The coupling magnitude (g is absent from all substrate equations)

Conclusion D is compatible with Conclusion C: the reason multiple Hamiltonians are
admissible is precisely because the theory lacks the information needed to select one.

---

### Section 15: MANDATORY CONCLUSION

**The correct conclusion is:**

```
╔══════════════════════════════════════════════════════════════════╗
║                                                                  ║
║  CONCLUSION C: Multiple Hamiltonians are mathematically          ║
║  admissible.                                                     ║
║                                                                  ║
║  The established substrate theory (PRW → telegrapher equation    ║
║  → transport equations {∂_t s + ∂_x J = 0,                     ║
║  ∂_t J + c²∂_x s = −J/τ} and the derived variables              ║
║  {E_sub, P_sub}) imposes no constraint on:                       ║
║                                                                  ║
║  (a) the functional form of the coupling F(s,J),                 ║
║  (b) the operator direction (n₁σ_x + n₂σ_y + n₃σ_z), or        ║
║  (c) the coupling constant g.                                    ║
║                                                                  ║
║  The admissible family is:                                       ║
║                                                                  ║
║  H_int ∈ { F(s,J) · (n₁σ_x + n₂σ_y + n₃σ_z) :                  ║
║             F smooth, (n₁,n₂,n₃) ∈ S², F ≠ 0 }                 ║
║                                                                  ║
║  which is infinite-dimensional.                                  ║
║                                                                  ║
║  H_int = g J σ_z is a MEMBER of this family. It becomes the     ║
║  UNIQUE member (up to sign of g) only after imposing THREE       ║
║  additional constraints not derivable from the substrate:        ║
║                                                                  ║
║  [A-lin-coupling]:  F(s,J) = g·J  (minimal coupling postulate)  ║
║  [A-local]:         point evaluation at x_q  (dipole approx.)   ║
║  [P-pure-dephasing]: A_S ∝ σ_z  (empirical criterion)          ║
║                                                                  ║
║  None of these three constraints is derivable from the           ║
║  established substrate equations.                                ║
║                                                                  ║
╚══════════════════════════════════════════════════════════════════╝
```

**Selecting Conclusion C over D:** Conclusion D is also logically valid ("the theory
lacks sufficient information"). The choice of C over D reflects that the question
asks for the full admissible family: C exhibits it explicitly. D is a corollary of C.

---

## Part VII — Derivation Status of H_int = g J σ_z

### Section 16: What Is Derived and What Is Assumed in the Existing Chain

| Claim | Logical status | Source |
|-------|---------------|--------|
| Substrate has fields s, J | [D] from PRW | microscopic_derivation.md |
| s is T-even, J is T-odd | [I] from PRW definitions | Section 2 this document |
| A_S must be Hermitian | [D] from definition of observable | Section 3 this document |
| A_S = n₁σ_x+n₂σ_y+n₃σ_z spans all options | [I] Basis theorem | Section 3 this document |
| Substrate has no preferred **n** ∈ S² | [D] from algebraic structure | Section 6 this document |
| F = g·J is minimal | [A] constitutive assumption | interaction_hamiltonian_derivation.md |
| Point coupling at x_q | [A] constitutive assumption | interaction_hamiltonian_derivation.md |
| A_S = σ_z given pure dephasing | [D] conditional on [P] | Section 7 this document |
| Pure dephasing is correct | [P] phenomenological postulate | empirical observation |
| g is free | [D] from absence in substrate equations | Section 11 this document |
| g is determined | [E] empirical calibration | decoherence_prediction.py |

### Section 17: The Exact Mathematical Obstruction to Uniqueness

The unique mathematical obstruction to the derivation of H_int = g J σ_z from the
substrate theory is the following:

**The substrate theory is a classical field theory over a commutative real algebra.
The qubit operator A_S lives in a non-commutative *-algebra M₂(ℂ). There is no
canonical functor from the former to the latter derivable from the transport
equations alone.**

More concretely: the substrate equations [C-s] and [C-J] determine the dynamics of
s and J but contain no information about:
- Which abstract quantum system is placed in the substrate
- How that system's internal degrees of freedom (σ_x, σ_y, σ_z) align with
  the substrate field directions
- What energy scale connects the classical current J (units: info/(m²·s)) to
  the quantum energy splitting ℏω_q (units: J)

These are three independent pieces of missing information. Filling them requires
three independent external inputs, not one. The fact that the resulting H_int ends
up having a single free parameter g after these inputs are provided does not make
it "unique up to g" — it makes it a determined member of a family that was otherwise
unconstrained.

---

## Appendix: Assumptions Required to Arrive at H_int = g J σ_z

Listed in logical order. Each must be accepted for the derivation to proceed.

```
[A1]  The qubit is a 2-level quantum system with Hilbert space ℂ².
      Status: external input, not in substrate theory.

[A2]  The free qubit Hamiltonian H_S = ½ℏω_q σ_z, defining the
      computational basis {|0⟩, |1⟩}.
      Status: external input, not in substrate theory.

[A-lin-coupling]  H_int is linear in J.
      Status: constitutive assumption (explicitly labelled in source).

[A-local]  H_int involves J evaluated at a single point x_q.
      Status: constitutive assumption (explicitly labelled in source).

[P-pure-dephasing]  The coupling must produce pure Ramsey dephasing
      (T₁ = ∞).
      Status: phenomenological postulate from experiment.
      This criterion is NOT derivable from {s, J, E_sub, P_sub, n⁺, n⁻}.

[A3]  Given [A1]–[A-local]–[P-pure-dephasing], A_S = σ_z follows.
      Status: derived (conditional on all prior assumptions).

[A4]  g is a free real parameter determined by calibration.
      Status: empirical input.
```

Only [A3] is a true derivation. Steps [A1], [A2], [A-lin-coupling], [A-local],
[P-pure-dephasing], and [A4] are all external inputs that cannot be derived from
the substrate transport equations.
