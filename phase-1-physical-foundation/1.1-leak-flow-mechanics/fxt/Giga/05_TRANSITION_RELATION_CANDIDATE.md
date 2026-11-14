# 05_TRANSITION_RELATION_CANDIDATE.md
## Candidate III — Transition Relation Ontology

**Date:** 2026-08-23
**Predecessor:** 04_ONTOLOGICAL_CANDIDATES.md
**Status:** UNDER INVESTIGATION
**Central question:** Does the composition law of a transition relation force the radial exponent,
or does it remain free?

Label key:
  [AXIOM]      — primitive, not derived
  [DEFINITION] — mathematical definition
  [DERIVED]    — follows from above by proof or calculation
  [EFFECTIVE]  — holds in a regime, not the full story
  [CONJECTURE] — plausible but unproved
  [UNRESOLVED] — genuinely open
  [KILL TEST]  — designed to falsify the candidate

---

## PART I — THE FUNDAMENTAL OBJECT

### I.1 Why Not a Field

The previous candidate (Giga 01–03) was, at bottom, a constrained field theory.
The field q(x,t) is a map from spacetime to R^n. The dynamics q̇ ∈ K_X was then a
constraint on this map. This structure failed because:

1. The field q selects one value per spacetime point.
2. The constraint K_X was a separate object, specified independently.
3. Five constitutive functions remained free after the primitive constraints were applied.

The field ontology cannot eliminate this freedom because a field value, by itself,
carries no information about what transitions are available from that value. The
transition structure had to be supplied separately — and that supply was the source
of freedom.

[DERIVED] If the fundamental object is a field value, then the transition structure
is always a second independent object. Constitutive freedom of the transition structure
is therefore unavoidable in the field ontology.

This is not a criticism of a particular field theory. It is a structural observation:
field value and transition rule are different things, and the field ontology cannot
fuse them.

### I.2 The Proposed Fundamental Object

[AXIOM-R] The fundamental object of X is not a field value but a *transition relation*:
a specification of which local X configurations can be directly reached from which others.

Notation: Let C be the set of possible local X configurations at a point (x,t).

[DEFINITION] A *transition relation* at (x,t) is a directed binary relation

    R(x,t) ⊆ C × C

where (A, B) ∈ R(x,t) means: "from configuration A, configuration B is directly
accessible."

A physical event at (x,t) changes R(x,t). The primitive X hypothesis is then:
the fundamental description of local physical reality is not which configuration is
occupied, but which transitions are currently available.

### I.3 Why This Structure and Not Others

The mission instruction lists eight possible structures. Each is examined:

**Binary relation R ⊆ C × C**
Chosen as the starting point. Records which pairs (A,B) are permitted. Directed
(order matters: A→B need not imply B→A). Makes no assumption about probability,
weight, or rate. Minimal.

**Directed graph**
Equivalent to a binary relation. A graph over vertex set C with an edge A→B if and
only if (A,B) ∈ R. This notation is chosen when visualizing the global structure.

**Category**
A category adds three requirements to a directed graph:
(i) composition: if A→B and B→C then A→C,
(ii) associativity of composition,
(iii) identity morphisms: each object A has A→A.
Whether these hold is a question to be investigated in Parts III–IV, not assumed.

**Groupoid**
A category where every morphism is invertible: A→B implies B→A.
Whether the transition relation is invertible is a physical question. In general,
transitions may be irreversible (see fxt history: irreversibility is a physical
requirement from the C2 era). Groupoid structure is not assumed.

**Semigroup**
A set with an associative binary operation but no identity element and no inverses.
The transition relation can generate a semigroup under composition. This is
investigated in Part IV.

**Path category / rewriting system / state-transition algebra**
These are all more elaborate structures that add additional axioms. None is adopted
as primitive. If the binary relation R, under the physical constraints, generates
one of these structures, that is a derived result.

**Transition kernel (probabilistic)**
A transition kernel assigns a probability measure to the set of successors of A.
This requires more structure than a binary relation. Whether probabilities are
required or emerge is deferred to Part XVI. Not assumed at this stage.

**Verdict:**

[DEFINITION] The fundamental object is taken to be a directed binary relation R on C.
More structure (category, semigroup, etc.) is added only if the physical hypothesis
forces it. The guiding rule is: use the simplest structure that can express the
physical hypothesis.

### I.4 The Physical Content of R

What does R physically mean?

[AXIOM-R] says: the local physical reality at (x,t) is the transition relation R(x,t),
not a field value.

The physical content of R is:

1. R encodes which changes to the local X configuration are physically permitted.
2. A physical event (presence of mass, energy, force) modifies R — removes or adds
   permitted transitions.
3. X evolves by following permitted transitions. A configuration A "at time t" can
   move to B at the next moment only if (A,B) ∈ R(x,t).
4. The history of R at a point (its sequence of modifications) is the physical history.

Note: this does not yet say whether there is a unique actual configuration, a probability
distribution over configurations, or something else. The transition relation specifies
what is possible. What actually happens is a further question.

### I.5 What R Is Not

R is not:
- A probability amplitude. No complex numbers yet. No Hilbert space.
- A density matrix.
- A Lagrangian or Hamiltonian.
- A scalar, vector, or tensor field.
- A constraint on a field value.

These may emerge. They are not assumed.

---

## PART II — CONFIGURATION

### II.1 The Problem with the Previous Definition

In the previous candidate, "configuration" was used loosely. The state q(x,t) ∈ R^n
was introduced without specifying what the components of q represent. This was then
patched by constitutive choice (n = 4 was chosen; the components were called
"magnitude-like" and "vector-like" without derivation).

The transition relation ontology requires a cleaner definition because R ⊆ C × C
depends on what C is.

### II.2 Defining Configuration

[DEFINITION] An *X configuration* at point (x,t) is a complete specification of the
locally distinguishable state of X at that point — meaning: the minimal description
needed to determine which transitions are available.

This definition is circular if taken alone, but it is made concrete by the following:

[AXIOM-C1] Two X configurations A and B at (x,t) are *distinct* if and only if there
exists some transition T such that T is available from A but not from B (or vice versa).

This is a purely operational definition: configurations are distinguished by their
transition structure, not by any intrinsic property.

Consequence: if A and B have exactly the same set of available transitions (and the
same successors for those transitions), they are the same configuration.

This is a strong constraint on C. It says C is not a free parameter. The set of
configurations is exactly as large as it needs to be to distinguish different transition
structures. No finer.

[DERIVED] C inherits the topology and geometry of the transition structure R. Two
configurations that are "close" in C are configurations whose available transitions
are nearly identical.

### II.3 Separating Layers

We distinguish:

**Instantaneous X state:** The configuration A ∈ C currently occupied at (x,t).
This is what a "snapshot" would record.

**Accessible future states:** The set {B : (A,B) ∈ R(x,t)} — the direct successors
of A under the current transition relation.

**Transition history:** The sequence R(x,t₁), R(x,t₂), ... of transition relations
that have been active at (x,t) over time. This encodes memory (from see.txt:
"K(t) = K[q(t), H(t)]").

**Local vs global configuration:** Local configuration is A ∈ C at a single point.
Global configuration is the assignment of a configuration to every point in space.
The transition relation at each point may depend on the global configuration (long-range
interactions), but the primitive object is local.

**Spatial location vs configuration-space coordinate:** Spatial location (x,t) is a
label. Configuration-space coordinate is the position of A within C. These are
independent: two spatial points can be in the same configuration (identical C-values)
but at different locations.

**Physical distinguishability:** The operational content of configuration. Two spatial
regions are physically distinguishable if they have different configurations — which,
by [AXIOM-C1], means they have different transition structures.

### II.4 Is q(x,t) Emergent?

The previous candidate used q(x,t) ∈ R^n as the fundamental object. Is this emergent?

[CONJECTURE] The field representation q(x,t) is an effective description valid when:
(i) the configuration space C has smooth structure near the occupied configuration,
(ii) the transition relation R is approximately described by a tangent-space constraint,
(iii) no discontinuous changes to R occur.

When these conditions hold, q can be chosen as a coordinate on C near the current
configuration, and R appears as a cone constraint on the tangent space (reproducing the
previous candidate's K_X).

The previous candidate was therefore not wrong. It was the effective description of a
smooth transition relation. Its constitutive freedom arose because the smooth effective
description has more freedom than the underlying transition relation — information about
the global structure of R was lost in the local, smooth approximation.

[DERIVED] The field description q(x,t) is a local chart on C, not the fundamental object.
The transition relation R is the fundamental object.

---

## PART III — TRANSITION COMPOSITION

### III.1 The Composition Question

Suppose the transition relation includes:

    (A, B) ∈ R   and   (B, C) ∈ R

Must (A, C) ∈ R?

This is the question of whether R is *transitively closed* — whether every path of
length 2 in the transition graph is also reachable in one step.

This is not obviously true. It must be investigated as a physical requirement.

### III.2 What Composition Would Mean Physically

If (A,B) ∈ R and (B,C) ∈ R and (A,C) ∈ R:
- The system can reach C from A either directly (A→C) or via B (A→B→C).
- Both pathways are available.

If (A,B) ∈ R and (B,C) ∈ R but (A,C) ∉ R:
- The system can reach C only via B, not directly.
- The path A→B→C requires two steps.
- The direct transition A→C is forbidden.

The physical question is: does the primitive X constraint permit this second scenario?

### III.3 Does Physical Reasoning Force Composition?

[AXIOM-R] says that a physical event changes R. It does not say R must be transitively
closed.

Scenario where closure is violated: Suppose configuration A is a "low-energy" X state,
B is a "medium-energy" state, and C is a "high-energy" state. The transition A→B might
be permitted (small step), B→C might be permitted (another small step), but A→C might
be forbidden (too large a step at once). This would be a physically meaningful scenario
without transitive closure.

Therefore:

[DERIVED] Transitive closure of R is *not* forced by the primitive X constraints alone.

However, composition can be forced by a *different* requirement — the requirement that
the transition relation be consistent under *composition of physical constraints*.

Specifically: if a physical constraint P₁ changes R in a specific way, and a second
constraint P₂ (applied to the result) changes R in another way, and there exists a
combined constraint P₁₂ that directly produces the same final R, then the composition
of physical constraints corresponds to composition in R.

This is what would force a category structure.

### III.4 The Composition Law as a Physical Requirement

[AXIOM-COMP] The following is investigated as a physical hypothesis (not yet axiom):

> If the transition relation at spatial point x₁ can reach point x₂ in one step, and
> the relation at x₂ can reach x₃ in one step, then there is a well-defined composite
> transition from x₁ to x₃.

This is a *spatial* composition requirement, not a configuration-space one. It says
that the radial transition structure must be self-consistent over spatial intervals.

In notation: if R(x₁,x₂) denotes the transition relation for the spatial step x₁→x₂,
then:

    R(x₁,x₃) = R(x₂,x₃) ∘ R(x₁,x₂)

where ∘ is composition of transition relations.

This is a constraint on how the transition structure varies in space, not on whether
configuration-space transitions are transitively closed.

### III.5 Why This Composition Law Is Physically Defensible

The physical interpretation:

- The transition relation R(x₁,x₂) encodes what changes to X configuration are
  permitted as one moves from spatial point x₁ to x₂.
- The transition relation R(x₂,x₃) encodes the same for x₂ to x₃.
- Consistency requires that the combined transition x₁→x₃ be determined by the
  product of the two.

This is not assumed for purely mathematical reasons. It has a physical basis:
*X has no memory of how a spatial path was divided*. The transition structure from
x₁ to x₃ cannot depend on whether one travels via x₂ or via some other intermediate
point x₂'. This is a locality + consistency condition.

If the transition structure depended on the choice of intermediate point, X would
"know about" the intermediate positions, implying nonlocal information about the
path. The primitive hypothesis that X is a local field (R is a local object at each
point) prevents this.

[DERIVED] Under locality of R and path-independence of the composition, the relation:

    R(x₁,x₃) = R(x₂,x₃) ∘ R(x₁,x₂)

follows from the primitive X constraints + locality.

This is a *genuine derivation*, not a mathematical convenience. The key assumption
used is locality: R(x,t) depends only on the physical configuration at (x,t), not
on the state at distant points.

### III.6 What Type of Object is R(x₁,x₂)?

For the composition law to be well-defined, R(x₁,x₂) must be a mathematical object
that can be composed. Several candidates:

**Option A: R(x₁,x₂) is a relation on C**
Composition of relations: (A,C) ∈ R₂ ∘ R₁ iff ∃B: (A,B) ∈ R₁ and (B,C) ∈ R₂.
This is well-defined and is the relational composition. It is the most general.

**Option B: R(x₁,x₂) is a map C→C**
A function from configurations to configurations. Composition is function composition.
This is more restrictive than Option A (requires R to be a function, not just a relation).

**Option C: R(x₁,x₂) is a matrix (transition matrix)**
For a finite or countable C, R can be represented as a 0/1 matrix. Composition is
matrix multiplication. This recovers Boolean matrix algebra.

**Option D: R(x₁,x₂) is a linear map (positive matrix)**
For a continuous C with a measure, R can be a linear operator (Markov kernel).
Composition is operator composition. This introduces measure-theoretic structure.

The minimal choice is Option A. Options B-D add structure that is not yet required.

[DEFINITION] For the remainder of this document, R(x₁,x₂) denotes a binary relation
on C, and ∘ denotes relational composition:

    (A,C) ∈ R₂ ∘ R₁   iff   ∃B ∈ C: (A,B) ∈ R₁ and (B,C) ∈ R₂.

---

## PART IV — ASSOCIATIVITY

### IV.1 The Associativity Question

Given three spatial positions x₁, x₂, x₃, x₄, does:

    (R₃₄ ∘ R₂₃) ∘ R₁₂ = R₃₄ ∘ (R₂₃ ∘ R₁₂)

hold?

### IV.2 Proof of Associativity for Relational Composition

Relational composition is associative. This is a theorem of set theory, not an
additional physical assumption.

**Proof:**
Let R₁ ⊆ C×C, R₂ ⊆ C×C, R₃ ⊆ C×C.

(A,D) ∈ (R₃ ∘ R₂) ∘ R₁
  ⟺ ∃B: (A,B) ∈ R₁ and (B,D) ∈ R₃ ∘ R₂
  ⟺ ∃B,C: (A,B) ∈ R₁ and (B,C) ∈ R₂ and (C,D) ∈ R₃

(A,D) ∈ R₃ ∘ (R₂ ∘ R₁)
  ⟺ ∃C: (A,C) ∈ R₂ ∘ R₁ and (C,D) ∈ R₃
  ⟺ ∃B,C: (A,B) ∈ R₁ and (B,C) ∈ R₂ and (C,D) ∈ R₃

Both conditions are identical. □

[DERIVED] Associativity of the transition composition follows automatically from the
choice of relational composition. No additional physical assumption is required.

### IV.3 Physical Meaning of Associativity

Associativity means: the order of composition does not matter when composing three
or more spatial steps. This is exactly what locality + path-independence require.

If associativity failed, it would mean that the transition structure somehow "knew"
how a spatial path was grouped into substeps — an implausible nonlocal effect.

[DERIVED] Non-associativity would require X to have information about the decomposition
of paths into substeps, which violates the locality axiom.

### IV.4 What Associativity Does and Does Not Give

Associativity + the spatial composition law means the collection of transition
relations {R(x,y) : x,y ∈ space} forms a *semigroupoid* — a directed graph of
objects (spatial positions) with morphisms (transition relations) that compose
associatively whenever the composition is defined (when the codomain of one equals
the domain of the next).

If we also have identity morphisms (a transition relation R(x,x) = identity that
leaves all configurations unchanged), this becomes a *category*.

[UNRESOLVED] Whether identity morphisms exist: whether there is a "trivial transition"
R(x,x) that leaves C unchanged. The physical content would be: a spatial loop
(going from x to x) induces no net change to configuration. This is a parallel
transport condition, and it need not hold in general.

---

## PART V — COMMUTATIVITY

### V.1 The Commutativity Question

Suppose transitions T_A (in "direction A") and T_B (in "direction B") are both
available from configuration X. Does it matter in which order they are applied?

    T_B ∘ T_A = T_A ∘ T_B ?

This is asked for transitions within configuration space C (not for spatial
composition, which was the subject of Parts III–IV).

### V.2 Commutative Possibility

If T_A ∘ T_B = T_B ∘ T_A for all available transitions, the transition algebra
is commutative. The physical meaning: the result of applying two configuration
changes is independent of their order.

In this case, the configuration space C behaves like a commutative space — the
changes to X configuration from two different physical influences combine
additively or in an order-independent way.

Consequence: the algebra of observables derived from this transition structure
would be commutative. This is the classical case.

### V.3 Noncommutative Possibility

If T_A ∘ T_B ≠ T_B ∘ T_A for some pair of transitions, the transition algebra
is noncommutative. The physical meaning: the order in which configuration changes
are applied matters.

This is not an exotic assumption. In three spatial dimensions, rotations do not
commute (SO(3) is noncommutative). If X transitions "in different spatial directions"
correspond to elements of a noncommutative group, the noncommutativity arises
naturally.

### V.4 What Selects Between Them

Three possible selection mechanisms are identified:

**Mechanism 1: Spatial dimension**
In 1D, all transitions are along the single axis. There is no ordering question.
The algebra is trivially commutative in 1D.
In 3D, transitions can be in different directions. If the transition relation has
any rotational structure, noncommutativity can arise from the spatial geometry.

**Mechanism 2: Physical constraint type**
If a physical constraint (e.g., presence of mass M) acts symmetrically in all
directions, it may force the transition algebra to be spherically symmetric —
which in 3D is the rotation group SO(3), which is noncommutative.
If the constraint acts only along one axis (anisotropic), the algebra may remain
abelian in the directions transverse to the constraint.

**Mechanism 3: Information content of transitions**
If two transitions T_A and T_B encode genuinely independent physical information,
their composition is more likely to be commutative. If they encode complementary
information (information gained from T_A is relevant to the outcome of T_B), their
composition is more likely to be noncommutative.

### V.5 Status for the Spherical Static Problem

For the minimal spherical static problem (Part VII), we impose spherical symmetry.
This reduces the spatial problem to one dimension (radial direction only). In this
reduction, transitions are along r only, and the composition law R(r₁,r₃) = R(r₂,r₃)
∘ R(r₁,r₂) is a composition of radial steps.

Radial compositions commute trivially because r₁ → r₂ → r₃ is the same as any
reordering in the radial sense (there is only one direction: outward).

[DERIVED] For the spherically symmetric static problem, the transition composition
is effectively commutative as a consequence of the symmetry reduction — not as an
additional assumption.

[UNRESOLVED] For the full 3D problem with broken spherical symmetry, the transition
algebra may be noncommutative. This is investigated in Part XVI.

### V.6 Recording the Bifurcation

COMMUTATIVE POSSIBILITY:
  If T_A ∘ T_B = T_B ∘ T_A for all A,B, the transition algebra is abelian.
  Physical consequence: classical (order-independent) observable algebra.
  Mathematical structure: commutative monoid or abelian group (if inverses exist).

NONCOMMUTATIVE POSSIBILITY:
  If T_A ∘ T_B ≠ T_B ∘ T_A for some A,B, the transition algebra is non-abelian.
  Physical consequence: order-dependent observable algebra.
  Mathematical structure: noncommutative monoid or non-abelian group.

WHAT WOULD SELECT BETWEEN THEM:
  The physical dimension and the symmetry group of the configuration space C.
  For the spherical static problem: commutativity follows from symmetry reduction.
  For the full 3D problem: the symmetry group SO(3) acts on C, and SO(3) is
  noncommutative. Whether X's transition algebra reflects this depends on whether
  C has a non-trivial SO(3) action — which is a question for Part XVI.

---

---

## PART VI — INVARIANTS

### VI.1 The Search for Rigidity

The previous candidate failed because the geometry of the admissible set was free.
The radial profile function h(r) = r^{-α} was chosen, not derived.

The transition relation formulation has a potential advantage: the structure of R
may have *natural invariants* — quantities preserved under all physically permitted
transitions. If such invariants exist and they are determined by the primitive X
constraints (not by constitutive choice), they can force the geometry of R and
thereby force the radial profile.

This is the most important section so far. We are looking for the missing rigidity.

### VI.2 Candidate Invariant 1: Transition Count (Out-Degree)

[DEFINITION] The *out-degree* of a configuration A at (x,t) is the cardinality of
the set {B : (A,B) ∈ R(x,t)} — the number of configurations directly accessible
from A.

Is out-degree preserved under transition composition?

**Analysis:** Consider R(r₁,r₂) ∘ R(r₀,r₁). The out-degree of a configuration A
in the composite relation is the number of C such that ∃B: (A,B) ∈ R(r₀,r₁) and
(B,C) ∈ R(r₁,r₂). This equals the sum over all B of the out-degree of B in R(r₁,r₂),
weighted by how many paths reach B. This is not preserved in general.

[DERIVED] Out-degree is not a natural invariant of transition composition.

### VI.3 Candidate Invariant 2: Causal Ordering

[DEFINITION] The transition relation R defines a *partial order* on C if:
(i) (A,A) ∈ R for all A (reflexive),
(ii) (A,B) ∈ R and (B,A) ∈ R implies A = B (antisymmetric),
(iii) (A,B) ∈ R and (B,C) ∈ R implies (A,C) ∈ R (transitive).

Is the causal ordering preserved under composition?

**Analysis:** If R is a partial order (satisfies transitivity), then the composition
R ∘ R ⊆ R (since any path of length 2 in the order is also a direct step). The
partial order structure is preserved under composition.

[DERIVED] If R is required to be a partial order, the partial order structure is
invariant under composition.

Physical interpretation: a partial order means transitions are irreversible —
A→B is permitted but B→A is not (unless A=B). The C2 era established that
irreversibility is a physical requirement for X. This is a candidate invariant
that follows from a physical requirement, not a mathematical convenience.

### VI.4 Candidate Invariant 3: Connectivity Structure

[DEFINITION] The *reachability set* of configuration A under relation R is
R*(A) = {B : A = B or (A,B) ∈ R or (A,C) ∈ R and (C,B) ∈ R or ...},
i.e., all configurations reachable from A by any finite path in R.

Is reachability preserved under composition?

**Analysis:** Under composition R₂ ∘ R₁, the reachability from A is
{B : ∃C accessible from A in R₁ and B is accessible from C in R₂}.
This is a subset of the reachability in R₂ ∘ R₁, so it is preserved in the
sense that if B is accessible in the composite, there is a path in both R₁ and R₂.

[DERIVED] The *connected components* of the transition graph are an invariant
of the composition if R₁ and R₂ act within the same connected components.

Physical interpretation: if a physical constraint splits C into disconnected
components (isolated configurations), the composition law preserves that split.
This is relevant to the collapse regime (Part XIV).

### VI.5 Candidate Invariant 4: Rank of the Transition Space

[DEFINITION] For a continuous configuration space C with a smooth manifold structure,
the *transition rank* at configuration A is the dimension of the tangent space to C
at A that is accessible under R — the dimension of the set of allowed infinitesimal
transitions.

Can the transition rank be forced by the composition law?

**Key observation:** In the spherical static problem, the composition law
R(r₁,r₃) = R(r₂,r₃) ∘ R(r₁,r₂) constrains how the transition relation changes
with r. If the transition rank changes with r, the composition law constrains *how*
it changes. This is investigated in Part VIII.

### VI.6 Candidate Invariant 5: Distinguishability Measure

[DEFINITION] The *distinguishability* between configurations A and B under R is
a measure of how different their transition structures are:

    δ(A,B) = |{T : T available from A but not B}| + |{T : T available from B but not A}|

(For continuous C, this would be a measure-theoretic version.)

Is distinguishability preserved under composition?

**Analysis:** Not in general. The composition changes which configurations are
accessible, so the transition structures of the resulting configurations may differ
from those of the source.

[UNRESOLVED] Whether a natural distinguishability measure is preserved under
composition — and whether such preservation forces the geometry of C — is an
open question related to the Candidate II (configuration-space geometry) track.

### VI.7 The Key Invariant Candidate: Path Equivalence

[DEFINITION] Two paths in configuration space γ₁ and γ₂ from A to B are *R-equivalent*
if for every configuration C on γ₁, there is a configuration C' on γ₂ with the same
transition structure, and vice versa.

If R forces all paths between two points to be R-equivalent (parallel transport is
flat), the transition structure is integrable and the space C has no intrinsic curvature
from the transition relation.

If R forces non-trivial path-dependence (parallel transport is curved), then C has
intrinsic curvature determined by R. The curvature of C is then not a free parameter
— it is forced by the physical constraints that determine R.

[CONJECTURE] The physical constraint imposed by a localized mass M forces a specific
curvature in C, and this curvature is what we call the gravitational field. The
gravitational radial profile would then be the radial curvature of C under the
transition structure forced by M.

This is the deepest candidate invariant and the clearest path from transition structure
to geometry to observable physics. It is investigated in Parts VII–VIII.

---

## PART VII — SPHERICAL SYMMETRY

### VII.1 Setup

We now impose the minimal problem constraints:

- One localized stable X configuration (mass M at origin).
- No time dependence: ∂R/∂t = 0.
- Spherical symmetry: R(x,y) depends only on |x| and |y|, not on angles.
- Asymptotically unrestricted: as r → ∞, the transition relation approaches the
  unconstrained relation R₀ (all transitions permitted).

Under spherical symmetry, the transition relation at radius r is:

    R(r) ≡ R(x,t) for all x with |x| = r

The spatial composition law becomes:

    R(r₁,r₃) = R(r₂,r₃) ∘ R(r₁,r₂)   for all r₁ < r₂ < r₃

where now r is a radial coordinate and R(rᵢ,rⱼ) means "the transition relation for
moving outward from radius rᵢ to radius rⱼ."

### VII.2 Reduction of Configuration Space

Under spherical symmetry, the full configuration space C at any point is a sphere S²
times the radial degree of freedom. But we are interested in the *radial* transition
structure — how R changes as r changes.

[DEFINITION] The *radial transition structure* is the family {R(r) : r > 0} of
transition relations at each radius, and the composition relations R(r₁,r₂) between them.

The spherical symmetry forces R(r₁,r₂) to be spherically symmetric in its action
on C. It cannot prefer any particular angular direction.

### VII.3 Reduction to a One-Parameter Family

Under spherical symmetry, the most general transition structure compatible with the
symmetry is parameterized by the radial coordinate r alone.

[DEFINITION] Represent the radial transition structure by a real-valued function

    ρ(r) : R⁺ → R

where ρ(r) is a quantity characterizing the "strength" or "density" of available
transitions at radius r. The precise meaning of ρ is to be determined by the
derivation below — we do not assume it is a field value.

The physical requirements on ρ(r):

- ρ(r) → ρ₀ (constant) as r → ∞: asymptotically unrestricted.
- ρ(r) modified near r → 0 by the presence of mass M.
- ρ(r) is determined by the composition law, not chosen freely.

### VII.4 What the Composition Law Constrains

The composition law R(r₁,r₃) = R(r₂,r₃) ∘ R(r₁,r₂) must be translated into a
constraint on ρ(r).

For this we need to specify how the composition of two radial transition relations
acts on ρ. The general possibilities are:

**Multiplicative composition:**
    ρ(r₁,r₃) = ρ(r₁,r₂) · ρ(r₂,r₃)

This holds if the transition "strength" at each step multiplies: the overall
transition strength is the product of the strengths of each sub-step.

**Additive composition:**
    ρ(r₁,r₃) = ρ(r₁,r₂) + ρ(r₂,r₃)

This holds if the transition "log-strength" adds: the overall log-strength is
the sum of the log-strengths of each sub-step.

**Neither:** Some more complex combination.

The physical question: which composition rule is forced by the transition relation
structure?

[DERIVED] For relational composition of binary relations on a set C, the composition
acts multiplicatively in terms of Boolean matrix products (if C is finite). This means
the effective "transmission probability" through two steps is the product of transmission
probabilities through each step. This favors the multiplicative rule.

For the continuous case, the natural representation of a transition relation is a
positive operator T(r₁,r₂) on a function space over C, and composition is operator
multiplication. This is also multiplicative.

[DERIVED] The multiplicative rule,

    T(r₁,r₃) = T(r₂,r₃) · T(r₁,r₂)

(where T represents the transition operator, with matrix product the composition),
is the natural form forced by the relational composition structure.

---

## PART VIII — FUNCTIONAL EQUATION

### VIII.1 Setting Up the Equation

Under spherical symmetry, represent the transition operator for the step from
radius r to radius r + dr as:

    T(r, r+dr)

The composition law requires:

    T(r₁, r₃) = T(r₂, r₃) · T(r₁, r₂)   for all r₁ < r₂ < r₃   ... (*)

This is a functional equation on T. We now solve it.

### VIII.2 Reduction to a Scalar Problem

Under spherical symmetry, the transition operator T(r₁,r₂) acts on the configuration
space C. For the spherical problem, all angular directions are equivalent, so the
angular part of C contributes a uniform factor. The non-trivial part of T is its
*radial component*.

[DEFINITION] The *radial transition amplitude* f(r₁,r₂) is the scalar representing
how T(r₁,r₂) acts on the radial degree of freedom of C.

The composition law (*) reduces to:

    f(r₁, r₃) = f(r₂, r₃) · f(r₁, r₂)   for all r₁ < r₂ < r₃   ... (**)

This is the scalar functional equation to be solved.

### VIII.3 Solving the Functional Equation

Equation (**) states: f(r₁,r₃) = f(r₂,r₃) · f(r₁,r₂) for all r₁ < r₂ < r₃.

Define: let r₁ = a, r₂ = b, r₃ = c. Then f(a,c) = f(b,c) · f(a,b).

Setting b = c gives: f(a,c) = f(c,c) · f(a,c), so f(c,c) = 1 (the identity).

Setting a = b gives: f(b,c) = f(b,c) · f(b,b) = f(b,c) · 1 ✓.

Now set r₁ = a, r₂ = a+s, r₃ = a+s+t for small s,t > 0:
    f(a, a+s+t) = f(a+s, a+s+t) · f(a, a+s)

If f is differentiable, write f(r, r+ε) = 1 + ε·g(r) + O(ε²) for some function g.

Then:
    f(a, a+s+t) = exp(∫ₐᵃ⁺ˢ⁺ᵗ g(r) dr)

because the multiplicative property of f translates to the additive property of
∫g(r)dr via logarithm. This is the standard derivation of exponential/Lie group
structure from a multiplicative cocycle condition.

**General solution:**

    f(r₁, r₂) = exp( ∫_{r₁}^{r₂} g(r) dr )

where g(r) is an *arbitrary* locally integrable function.

The functional equation (**) is satisfied for *any* g(r). The freedom is the choice
of g.

### VIII.4 Applying Additional Constraints to Determine g

The functional equation alone admits a one-parameter family of solutions (for each
choice of g). We now apply the remaining physical constraints.

**Constraint A: Asymptotic condition**
As r → ∞, the transition structure approaches the unconstrained limit R₀. This means
T(r, r+dr) → identity as r → ∞, which means g(r) → 0 as r → ∞.

**Constraint B: Dimensional analysis / scaling**
The only length scale in the spherical static problem is the location of the source.
At large r, the only natural quantity is r itself. If g must be built from r alone
(no other scale), then by dimensional analysis:

    g(r) ∝ r^{-β}   for some β

for r in the asymptotic region. This gives:

    f(r₁, r₂) = exp( C · ∫_{r₁}^{r₂} r^{-β} dr )

For β ≠ 1:
    f(r₁, r₂) = exp( (C/(1-β)) · [r₂^{1-β} - r₁^{1-β}] )

For β = 1:
    f(r₁, r₂) = exp( C · ln(r₂/r₁) ) = (r₂/r₁)^C

**Constraint C: Scale invariance**
The problem of a point mass in otherwise empty space has no preferred length scale.
Newtonian gravity is scale-free (the law F ∝ 1/r² has no dimensionful parameter
other than GM). For the transition relation to also be scale-free (no preferred
radius), f(r₁,r₂) must depend only on the ratio r₂/r₁, not on r₁ and r₂ separately.

This is an extremely strong constraint. Let us check which forms satisfy it:

For β ≠ 1:
    f(r₁,r₂) = exp( (C/(1-β)) · [r₂^{1-β} - r₁^{1-β}] )
This depends on r₁ and r₂ separately (not only on r₂/r₁), unless 1-β = 0, i.e., β = 1.

For β = 1:
    f(r₁,r₂) = (r₂/r₁)^C
This depends only on r₂/r₁. ✓

[DERIVED] **Scale invariance forces β = 1.** Among all power-law forms of g(r), only
β = 1 (i.e., g(r) = C/r) produces a transition amplitude that depends only on the
ratio r₂/r₁.

The unique scale-invariant solution to the functional equation is:

    f(r₁, r₂) = (r₂/r₁)^C = (r₁/r₂)^{|C|}   (if C < 0, transition weakens outward)

where C is a single real constant.

### VIII.5 From Transition Amplitude to Radial Profile

The transition amplitude f(r₁,r₂) = (r₁/r₂)^{|C|} describes how the transition
structure weakens as one moves outward from the source.

The *local* transition amplitude at radius r (relative to infinity) is:

    f(r, ∞) = lim_{R→∞} f(r, R) = lim_{R→∞} (r/R)^{|C|}

This limit is zero for |C| > 0, which means the transition structure vanishes at
infinity — consistent with the asymptotic condition that R → R₀ at large r.

More usefully, the transition amplitude relative to a reference radius r₀ is:

    f(r, r₀) = (r/r₀)^{|C|}

This increases as r increases (moving outward from the source), meaning the
transition structure becomes richer (more transitions available) farther from the source.

The *radial X profile* — the quantity that plays the role of |q(r)| in the previous
candidate — is characterized by how the transition amplitude varies with r:

    ρ(r) ∝ f(r₀, r) = (r₀/r)^{|C|}

This is a power law with exponent |C|.

Comparing with the previous candidate's q(r) ∝ r^{-α/2}, we identify:

    α/2 = |C|   ⟹   α = 2|C|

### VIII.6 Counting Remaining Freedom

The functional equation, under scale invariance, reduces the free functions g(r) to
a single constant C.

Freedom before applying constraints:
- g(r) was an arbitrary function — infinite-dimensional freedom.

Freedom after applying asymptotic condition: g(r) → 0 at infinity — still infinite-
dimensional.

Freedom after applying scale invariance: g(r) = C/r — one real constant C.

**This is a dramatic reduction.** The previous candidate had at least five free
functions. After scale invariance of the transition relation, we have exactly one
free constant C.

[DERIVED] The radial transition structure of X under spherical symmetry is

    f(r₁, r₂) = (r₁/r₂)^C

up to the single constant C. Scale invariance is not assumed as an axiom — it follows
from the requirement that X introduce no preferred length scale (since X is postulated
to exist everywhere, in the absence of mass, it has no preferred scale; the mass M
sets a preferred scale in strength, but not in radius).

### VIII.7 The Central Question: Does C = 1?

The radial profile is ρ(r) ∝ r^{-C}. For Newtonian gravity, the effective
acceleration from the previous candidate's analysis requires α = 2, which here means
C = 1 (since α = 2|C|).

Does the transition relation formalism force C = 1?

**What we have:** C is the exponent of the power-law transition amplitude. Scale
invariance forced C to be a constant (rather than a function), but did not fix its value.

**What would force C = 1:**
We need an additional invariant or constraint that is specific to the value C = 1.

**Three possibilities:**

**Possibility 1: Gauss's law / area scaling**
In 3D Euclidean space, the area of a sphere at radius r scales as r². If the
transition relation must be *flux-preserving* — if the total number of available
transitions per unit area is conserved — then:

    ρ(r) · 4πr² = constant

    ρ(r) ∝ r^{-2}

This gives C = 2, not C = 1.

Wait — let us be careful. The radial profile ρ(r) ~ r^{-C} means the transition
*amplitude per unit volume* falls as r^{-C}. The *total* transition capacity through
a spherical shell at radius r is:

    ρ(r) · 4πr² dr ∝ r^{2-C} dr

For this to be *constant per unit dr* (uniform flux), we need 2 - C = 0, so C = 2.
For this to be *constant per unit d(ln r)* (logarithmic flux conservation), we need
r · r^{2-C} = constant, so 3 - C = 0, C = 3.

For the *field* (amplitude, not intensity) to fall as 1/r (analogous to the
gravitational potential), we need C = 1.
For the *force* (gradient of field) to fall as 1/r², we need d/dr(r^{-C}) ∝ r^{-(C+1)} = r^{-2},
so C + 1 = 2, C = 1.

[DERIVED] **If the effective force is the radial gradient of the transition amplitude,
then F ∝ 1/r² forces C = 1.**

But this is still circular — we would be requiring C = 1 because we want F ∝ 1/r².

**Possibility 2: Dimensional forcing**
In d spatial dimensions, the Gauss's law / area element scales as r^{d-1}. For
flux conservation of a scalar quantity through spheres:

    ρ(r) · r^{d-1} = constant   ⟹   ρ(r) ∝ r^{-(d-1)}   ⟹   C = d-1

In 3 spatial dimensions: C = 2.

This gives a(r) = -d(ρ)/dr ∝ r^{-(C+1)} = r^{-3}, which is NOT Newtonian (1/r³).

**Possibility 3: Transition amplitude is the potential, not the density**
If ρ(r) is identified with the *potential* Φ(r) (rather than with the field
strength), then:

    a(r) = -dΦ/dr = -d(ρ)/dr ∝ r^{-(C+1)}

For a(r) ∝ 1/r², we need C + 1 = 2, so C = 1.
For Newtonian gravity, Φ(r) ∝ 1/r, which is ρ(r) ∝ r^{-1}, so C = 1. ✓

The question becomes: is the radial transition amplitude f(r₀,r) the *potential* of
the gravitational field?

This identification is not forced by the transition relation formalism alone. It
requires a coupling law between the transition amplitude and the acceleration of matter.
That coupling law is a constitutive choice — exactly the type of choice that killed
the previous candidate.

### VIII.8 Critical Finding: C Is Not Forced

[DERIVED — NEGATIVE RESULT]

The functional equation, under the constraints applied:
- Asymptotic condition (g → 0 at infinity),
- Scale invariance (no preferred length scale),

reduces the radial profile to a one-parameter family:

    f(r₁, r₂) = (r₁/r₂)^C

with C a free real constant.

The value of C is not forced by:
- The composition law alone,
- The asymptotic condition alone,
- Scale invariance alone,
- Any combination of the above.

To force C = 1 (or any specific value), we would need an additional constraint
that picks out a specific value of C from the one-parameter family.

### VIII.9 What Is and Is Not an Advance

Compared to the previous candidate:

**Previous candidate:** Five free functions (α, g(M), constraint form, G_ij, c).
**This candidate:** One free constant (C), after applying composition law +
scale invariance.

**This is genuine progress.** The transition relation ontology with the composition
law and scale invariance reduces the freedom from five free functions to one free
constant.

However, the resulting situation is:

    Transition relation + composition + scale invariance → ρ(r) ∝ r^{-C}

with C undetermined. This is analogous to the previous candidate's:

    Field ontology → a(r) ∝ r^{-(α/2+1)}

with α undetermined. The reduction is real, but the fundamental difficulty persists.

### VIII.10 What Could Still Force C

The following possibilities remain open:

**Option A: Flux conservation**
If the total "transition flux" through any sphere must be constant (a conservation law
for the transition structure), and if we identify this with the Gauss's law of gravity,
then C = 2 is forced. This gives a(r) ∝ r^{-3}, which is NOT Newtonian.

**Option B: A coupling law from information geometry**
If the coupling between ρ(r) and matter acceleration is determined by Candidate II's
distinguishability metric (Part XVIII), the specific exponent connecting ρ to a
might force C = 1 via the Fisher information structure.

**Option C: C is a physical constant, not a free parameter**
Perhaps C is the value forced by the 3D spatial geometry alone — a topological or
geometric invariant. In 3D, the fundamental group of R³\{0} is trivial, but the second
cohomology class of the sphere S² is non-trivial. If C is related to a topological
invariant of the sphere S², it might be forced to an integer. The smallest positive
integer giving Newtonian-like behavior via a(r) ∝ r^{-(C+1)} and F ∝ 1/r² is C = 1.

**Option D: C is forced by consistency with black hole thermodynamics**
The Bekenstein-Hawking entropy of a black hole scales as area ∝ r². If the
transition structure at the horizon must be consistent with this entropy scaling,
and if entropy is measured by the number of available transitions, then the transition
density at the horizon scales as r^{-2}, forcing C = 2. (Note: this gives C = 2,
not C = 1, and leads to a(r) ∝ r^{-3}, which is again not Newtonian gravity.)

**Option E: Two-component coupling**
The effective force is not just the gradient of ρ but involves a product of ρ with
the spatial volume element. In 3D:
    a(r) ∝ -d/dr [ρ(r)] / (4πr²)^{some power}
For specific exponent combinations, C = 1 can emerge. But this introduces the
combination rule as a new free choice.

None of Options A–E forces C = 1 without an additional assumption.

[KILL TEST K1] Does the composition law force the radial exponent?

**Result: PARTIALLY.** The composition law + scale invariance reduces infinite
freedom to one free constant C. But it does not force C to any specific value.
The candidate PARTIALLY passes K1: it reduces but does not eliminate the freedom.

---

---

## PART IX — NEWTONIAN LIMIT

### IX.1 What the Theory Currently Predicts

From Part VIII, the transition amplitude is:

    f(r₀, r) = (r₀/r)^C

The effective radial profile (what plays the role of the "X configuration magnitude"
in the previous candidate) is:

    ρ(r) ∝ r^{-C}

The effective acceleration, under the assumption that matter responds to the gradient
of ρ, is:

    a(r) ∝ -dρ/dr ∝ r^{-(C+1)}

For Newtonian gravity:

    a(r) ∝ -1/r²   ⟹   C + 1 = 2   ⟹   C = 1

### IX.2 What Newtonian Gravity Requires From This Formalism

The conditions for Newtonian gravity:

1. **Radial exponent:** C = 1, so ρ(r) ∝ r^{-1} and a(r) ∝ r^{-2}.
2. **Mass dependence:** The coefficient of r^{-2} must scale linearly with M.
3. **Universal coupling:** All test masses must respond to ρ(r) the same way.

Condition 1 is not forced by the current formalism (C is free).
Condition 2 is addressed in Part X.
Condition 3 is addressed in Part XI.

### IX.3 Does C = 1 Follow From Any Structural Argument?

The deepest structural argument available is this:

In 3 spatial dimensions, the fundamental solution of the Laplace equation ∇²Φ = 0
(in the region exterior to a point source) is Φ(r) ∝ 1/r. The gravitational potential
IS this fundamental solution. It arises because:

    ∇²(1/r) = -4πδ³(x)

and in the region r > 0, the potential solves the Laplace equation.

Now: does the transition relation formalism produce, from its composition law, the
fundamental solution of a Laplace-type equation?

[CONJECTURE] If the transition amplitude f(r₀,r) satisfies the composition law AND
the transition relation is "harmonically extended" (meaning it satisfies a discrete
or continuous Laplace equation on the configuration space), then C = 1 follows from
the Laplace equation in 3D.

**Argument:** The composition law f(r₁,r₃) = f(r₁,r₂) · f(r₂,r₃) is equivalent
to saying that log f(r₁,r₂) = ∫_{r₁}^{r₂} g(r) dr with g(r) = C/r. The function
∫g(r) dr = C·ln(r) is the fundamental harmonic function in 1D (the composition has
reduced the 3D problem to 1D). The 3D harmonic function is C/r. The passage from
the 1D reduced problem (log f) to the 3D harmonic function requires the 1D integral
of g(r) = C/r to correspond to the 3D potential C/r, which requires a specific
normalization/identification.

This argument is [CONJECTURE] and not rigorous. It suggests that a deeper connection
between the transition relation and harmonic analysis may exist, but it does not
constitute a derivation of C = 1.

### IX.4 The Non-Newtonian Prediction

If C ≠ 1, the transition relation formalism predicts a power-law force:

    a(r) ∝ r^{-(C+1)}

For C = 2 (Gauss's law argument from Part VIII): a(r) ∝ r^{-3}.
For C = 1 (Newtonian): a(r) ∝ r^{-2}.
For C = 1/2: a(r) ∝ r^{-3/2}.

The formalism makes a genuine prediction: the force law must be a power law with
exponent C+1. What it does not determine is the specific value of C.

[DERIVED] The transition relation formalism predicts a power-law force law, not
an arbitrary force law. This is progress over the field candidate (which could
reproduce any force law). But it does not uniquely predict the Newtonian exponent.

### IX.5 Empirical Viability of Non-Newtonian Values

Could C ≠ 1 be empirically viable?

For large departures (C = 2: force ∝ r^{-3}), the prediction is falsified by
solar system observations. The force law 1/r³ gives non-Keplerian orbits.

For small departures from C = 1: Modified gravity theories (MOND, f(R) gravity)
allow corrections to Newtonian gravity at very large scales. If C = 1 exactly in
the Newtonian regime but C shifts at cosmological scales, the formalism could be
consistent. But this would require the transition relation to change character at
large scales, which introduces a new free function.

[DERIVED] For the transition relation prediction a(r) ∝ r^{-(C+1)} to be empirically
viable at solar system scales, C must be close to 1. The exact value C = 1 is
required for exact Newtonian gravity.

---

## PART X — MASS

### X.1 Mass in the Previous Candidate

The previous candidate left g(M) — the coupling between source mass M and X
configuration strength — as a completely free function. This was a major failure.

The present candidate must do better. Either mass is determined by the transition
structure, or it remains a free parameter.

### X.2 Can Mass Be Defined From the Transition Structure?

[AXIOM from see.txt] Matter is a stable localized X configuration.

If matter is a stable configuration of X, then mass M should be measurable as
a property of that configuration — not as an external label.

Proposal: define mass M operationally as the integrated "charge" of the transition
relation around the localized configuration.

Specifically: if the transition amplitude at large r falls as:

    f(r₀, r) = (r₀/r)^C  ·  M^σ   (for some exponent σ)

then M is determined by the asymptotic amplitude of the transition structure.
This is analogous to how mass in general relativity is determined by the asymptotic
behavior of the metric.

### X.3 What the Composition Law Says About Mass Dependence

The composition law f(r₁,r₃) = f(r₁,r₂) · f(r₂,r₃) constrains the radial
dependence of f but says nothing directly about the mass dependence.

The reason: the composition law is a statement about how f varies as we move
radially. The mass M sets the *strength* of the configuration — how far the
transition structure deviates from R₀ — but not the radial profile.

[DERIVED] The composition law constrains the radial profile (giving C) but leaves
the mass coupling σ as a separate free parameter.

### X.4 Gauss's Law Argument for Mass Dependence

In electrostatics, Gauss's law ∮ E·dA = Q/ε₀ relates the flux of the electric field
through any closed surface to the enclosed charge Q. This forces E ∝ Q/r² (the
Coulomb law), with Q linear in the source charge.

The analogous argument for the transition relation: if the total "transition flux"
through a sphere of radius r is proportional to the enclosed source (mass M), then:

    ρ(r) · 4πr² = const · M

    ρ(r) = const · M / r²

This gives both C = 2 AND linear mass dependence. But as established in Part VIII,
C = 2 gives a(r) ∝ r^{-3}, not Newtonian gravity.

The Gauss's law argument cannot simultaneously give Newtonian exponent (C = 1) and
linear mass coupling. It gives C = 2 and linear mass coupling, which is not
Newtonian.

### X.5 Newtonian Mass Coupling Requires

For a(r) ∝ M/r², the previous candidate analysis showed g(M) ∝ M² was required
(because the acceleration was proportional to the square root of g(M), so g(M) ∝ M²
gives a ∝ M). In the present formalism:

    a(r) ∝ -dρ/dr ∝ -d/dr[A(M) · r^{-C}] ∝ A(M) · r^{-(C+1)}

For a ∝ M, we need A(M) ∝ M. This is the mass amplitude: the overall scaling of
ρ(r) with the source mass M. For the transition formalism, A(M) is determined by
how the localized X configuration (the "mass") generates the transition structure.

If mass is identified with the transition-structure charge (the asymptotic flux),
and if this charge is additive (two masses together generate twice the flux),
then A(M) ∝ M and linear mass coupling follows.

[CONJECTURE] If mass is defined as the additive charge of the transition structure,
then linear mass coupling A(M) ∝ M follows from additivity. This is not derived
from the composition law but from the definition of mass.

### X.6 Status

Mass dependence is not forced by the transition relation formalism:

- The composition law forces the radial profile (one constant C).
- It does not force the overall amplitude A(M).
- A(M) ∝ M follows from additivity of mass, which is an additional assumption.

[KILL TEST K2] Does the transition structure determine how source strength enters?
**Result: FAILS.** The composition law constrains radial behavior but not mass
coupling. Mass coupling requires a separate assumption (additivity of mass charge).

---

## PART XI — UNIVERSALITY OF FALL

### XI.1 The Equivalence Principle

The equivalence principle states that all test masses fall with the same acceleration
in a gravitational field, independent of their internal structure. This is not
trivial — it requires that the coupling between matter and the gravitational field
is universal.

In general relativity, universality follows from the geometric interpretation:
all matter follows geodesics of spacetime, and the geodesics are determined by
the metric alone (not by any property of the test matter).

Does the transition relation formalism produce universality?

### XI.2 The Universality Question in This Formalism

In the present formalism, matter accelerates because it responds to the transition
structure ρ(r). The acceleration of a test matter configuration A is:

    a_A(r) = coupling(A) · (-dρ/dr)

where coupling(A) is how the test matter A couples to ρ. If coupling(A) depends
on the internal structure of A, universality fails.

### XI.3 When Does Universality Hold?

Universality holds if the coupling is the same for all configurations A:

    coupling(A) = coupling (independent of A)

When is this forced by the transition relation?

[DERIVED] If matter is a stable configuration of X (from the axiom in see.txt),
and if all stable X configurations respond to the same transition structure ρ(r),
then the coupling depends only on ρ(r) and on the structure of the *stable*
configuration — not on any additional label.

This is promising but incomplete: if different stable configurations have different
internal transition structures, they may couple differently to ρ(r).

**Condition for universality:** If the coupling between matter and the external
transition structure is mediated by the *same compositional rule* for all matter
configurations — if all matter follows the same composition law — then universality
holds.

[CONJECTURE] If all stable X configurations (matter) evolve according to the same
transition composition law as the external field, universality follows as a geometric
consequence: all matter follows the same "geodesics" of the transition structure.

This is analogous to the GR argument, but it is [CONJECTURE], not [DERIVED]. It
requires that the transition structure of matter and the transition structure of the
external field be governed by the same composition rule — which is natural but not
automatically guaranteed.

### XI.4 Non-Universal Terms

If two stable configurations A and B have different internal transition structures
(different "sizes" of configuration space), they may experience different effective
forces from ρ(r):

    a_A(r) = coupling_A · r^{-(C+1)}
    a_B(r) = coupling_B · r^{-(C+1)}

For universality (a_A = a_B), we need coupling_A = coupling_B. This is not guaranteed
by the composition law alone.

[KILL TEST K5] Does the same geometry act universally on different matter configurations?
**Result: UNRESOLVED.** Universality is a consequence if the coupling between matter
and the external transition structure is compositional (uses the same rule). This is
physically natural but not derived from the composition law alone.

---

## PART XII — STATIC GRAVITY VS COLLAPSE

### XII.1 The Two Problems (From 04_ONTOLOGICAL_CANDIDATES, Section 5)

These two questions are kept separate:

**Question A (Ordinary gravity):**
Why does a stable mass M produce a specific surrounding X transition structure
that causes nearby matter to accelerate as r^{-(C+1)}?

**Question B (Collapse):**
What happens when the X transition structure becomes so restricted that the
ordinary mode cannot continue?

The previous candidate incorrectly tried to derive Question A from the continuation
principle, which is the mechanism for Question B. This is the error to avoid.

### XII.2 How Question A Is Addressed by Candidate III

Question A is answered, partially, by the composition law analysis:

- The composition law forces the radial profile to be a power law r^{-C}.
- The asymptotic condition and scale invariance pin this to one free constant C.
- The transition structure ρ(r) ∝ r^{-C} exists in the static state, not as a
  response to continuation failure.

This is correct: for a stationary spherical configuration, the X transition structure
simply *is* weaker at larger r, and this weakness causes matter to accelerate inward.
The continuation principle is NOT invoked to generate this.

[DERIVED] The ordinary gravitational attraction from Candidate III arises from the
*radial gradient of the transition amplitude* ρ(r) ∝ r^{-C}, which exists in the
static state. The continuation principle is not required for ordinary gravity.

This is an improvement over the previous candidate, where the continuation principle
was the primary (and inert) mechanism.

### XII.3 The Mechanism for Question A

More carefully: why does the transition structure ρ(r) ∝ r^{-C} cause matter to
accelerate inward?

The physical argument: matter (a stable X configuration) exists in a region where
the transition structure weakens with distance from the source. The configuration
can make transitions in both directions (toward and away from the source). But the
transitions toward the source are "richer" (more options, higher ρ), while
transitions away from the source are "poorer" (fewer options, lower ρ).

If matter preferentially follows transitions toward higher ρ (toward richer transition
structure), it accelerates inward. This preference must come from a principle — it
is not automatic.

[UNRESOLVED] The mechanism by which a gradient in transition amplitude produces
directed motion of matter requires a coupling law. This is still a constitutive
choice — it parallels the coupling a ∝ -∇ρ in the previous candidate.

However, there is a candidate for a non-arbitrary coupling: if matter follows the
*most accessible path* in configuration space (the transition analog of a geodesic),
and if higher ρ means more accessible paths in a specific direction, then the inward
acceleration follows from the extremal principle.

This reduces the coupling law question to: what does "most accessible path" mean
for the transition relation? This is a question about the geometry induced by R
on the configuration space C, which connects to Candidate II (configuration-space
geometry). It is addressed in Part XVIII.

### XII.4 How Question B Is Addressed by Candidate III

Question B (collapse) arises when ρ(r) → 0 — when the available transitions at some
radius approach zero. In this limit, the system at that radius runs out of available
transitions.

This is precisely when the continuation principle becomes active: X cannot remain
at a configuration with zero available transitions, so it must reorganize.

[DERIVED] The continuation principle is active precisely in the regime where ρ(r) → 0,
which corresponds to very strong gravitational fields (small r near a massive source,
or extreme densities). This is the black hole / gravitational collapse regime.

[DERIVED] The separation between ordinary gravity (Question A) and collapse
(Question B) is naturally made in Candidate III:
- Ordinary gravity: ρ(r) > 0, matter responds to -dρ/dr.
- Collapse: ρ(r) → 0, continuation principle activates, reorganization occurs.

The continuation principle is NOT trivially satisfied in the collapse regime — it
has genuine content there. This resolves the failure of the previous candidate.

### XII.5 The Critical Threshold

[DEFINITION] The *gravitational critical threshold* is the condition:

    ρ(r_c) = ρ_min

where ρ_min is the minimum transition amplitude compatible with existence of
non-trivial transitions. Below ρ_min, the transition structure collapses.

For the power-law profile ρ(r) ∝ r^{-C}, the critical radius where ρ = ρ_min is:

    r_c ∝ (ρ₀/ρ_min)^{1/C}

This radius depends on C and on the ratio of the asymptotic to the minimum transition
amplitude. For the Schwarzschild case, r_c should correspond to the Schwarzschild
radius r_s = 2GM/c².

[UNRESOLVED] The connection between the transition critical threshold r_c and the
Schwarzschild radius requires additional work. It depends on how M enters the
transition amplitude (Part X) and on the physical meaning of ρ_min (Part XIV).

---

---

## PART XIII — CONTINUATION

### XIII.1 Formalizing the Continuation Principle

The primitive hypothesis from see.txt: "a transition cannot simply terminate. When
the current continuation becomes impossible, X must reorganize within the remaining
allowed configuration space."

This must be made mathematically precise. The following candidates are examined:

**Candidate 1:** Every state has at least one successor.
Mathematical form: ∀A ∈ C, ∃B ∈ C: (A,B) ∈ R.
This says: R has no terminal nodes. Every configuration has at least one available
transition.

**Candidate 2:** Every finite path can be extended.
Mathematical form: for every finite sequence A₀→A₁→...→Aₙ in R, there exists
Aₙ₊₁ with (Aₙ, Aₙ₊₁) ∈ R.
This is equivalent to Candidate 1 (no terminal nodes), stated at the path level.

**Candidate 3:** Transition probability sums to one.
Mathematical form: Σ_B P(A→B) = 1 for all A.
This is a probabilistic formulation. It requires a probability measure on C, which
is additional structure not yet assumed.

**Candidate 4:** R has no terminal nodes (directed graph version of Candidate 1).
Same as Candidate 1.

**Candidate 5:** Flux conservation.
Mathematical form: for every region Ω ⊆ C, the net transition flux out of Ω equals
the net transition flux into Ω (in steady state).
This is a continuity equation for the transition relation.

### XIII.2 Which Candidate is Correct?

The physical content of the hypothesis is: X cannot "stop." There is always some
available transition.

The simplest formalization is Candidate 1:

[AXIOM-CONT] ∀A ∈ C, ∃B ∈ C: (A,B) ∈ R.   (No terminal nodes in R.)

This has clear physical meaning: no configuration is a dead end. There is always
a way forward.

Candidates 3 and 5 require additional structure (probability measure or flow
measure) that is not yet established. They are not chosen as primitive.

### XIII.3 Consequences of No Terminal Nodes

[DERIVED] Under [AXIOM-CONT], every configuration has at least one successor.

Does this constrain the radial profile ρ(r)?

**Analysis:** For the spherical static problem, ρ(r) ∝ r^{-C} gives:

    ρ(r) → ∞ as r → 0 (for C > 0)
    ρ(r) → 0 as r → ∞ (for C > 0)

At large r, ρ(r) → 0. This means the number of available transitions per unit
volume decreases at large r. But ρ = 0 would mean no transitions available — a
terminal node.

[DERIVED] [AXIOM-CONT] requires ρ(r) > 0 for all finite r. This is satisfied by the
power-law profile ρ(r) ∝ r^{-C} for C > 0 (since r^{-C} > 0 for all finite r > 0).

The continuation principle is satisfied in the asymptotic region. However, at
r → 0 near a massive source, ρ(r) → ∞ — an infinite number of transitions. This is
the regime where the composition law description breaks down (the profile diverges,
signaling a breakdown of the smooth approximation). The continuation principle is
NOT violated here, but the formalism may lose validity.

### XIII.4 When is the Continuation Principle Active?

The critical insight from the failure of the previous candidate: the continuation
principle was trivially satisfied for the stationary solution (q̇ = 0 was always
in K_X). The principle must be ACTIVE — it must actually constrain behavior.

In Candidate III:

- For ρ(r) > 0 (ordinary gravity regime): every configuration has successors.
  The continuation principle is satisfied trivially. It does NOT constrain the
  ordinary gravitational profile. This is correct behavior — ordinary gravity
  should not depend on the continuation principle.

- For ρ(r) → 0 (approaching the critical threshold): the number of available
  transitions shrinks. The continuation principle forces: "find another direction."
  This is where the principle becomes active and physically meaningful.

[DERIVED] The continuation principle is non-trivially active only in the collapse
regime (ρ → 0). In the ordinary gravity regime (ρ > 0 everywhere), it is satisfied
trivially. This is the correct separation of mechanisms.

### XIII.5 The Active Continuation Regime

When ρ(r) falls to ρ_min, the system has only a minimum number of available
transitions. At this point:

- If the system continues inward (r decreases), ρ would fall below ρ_min.
- This would violate [AXIOM-CONT] (terminal node).
- Therefore X must reorganize: transitions must redirect.

The reorganization forces the effective "flow" to redirect — either outward or
tangentially. This is the physical mechanism for the critical behavior near a
gravitational collapse threshold.

[DERIVED] The continuation principle produces an effective "bounce" or "redirect"
at the critical threshold ρ_min. The direction of the redirect depends on which
non-radial transitions are available (this requires analysis of the 3D transition
structure, not done here).

---

## PART XIV — CRITICAL CONFIGURATION / COLLAPSE

### XIV.1 Mathematical Definition of Collapse

Collapse is not assumed to involve dimensional reduction to "2D." Instead it is
defined operationally through the transition structure.

[DEFINITION] A *gravitational collapse configuration* is one where the radial
transition amplitude ρ(r) drops below the critical threshold ρ_min at some
radius r_c, forcing the continuation principle to activate.

### XIV.2 Defining Effective Dimensionality

The previous candidate used "dimensional reduction 3→2" without a precise
mathematical definition of dimension. We provide one.

[DEFINITION] The *local effective dimension* of the transition structure at
radius r is:

    d_eff(r) = (number of independent accessible transition directions at r)

For a 3D spatial configuration with full spherical symmetry broken by the
radial concentration of mass:

- In the asymptotic region: d_eff = 3 (all spatial directions have equal transitions).
- Near the critical threshold: radial transitions become restricted. If radial
  transitions ρ_radial(r) → 0 while tangential transitions ρ_tangential(r) remain
  finite, then d_eff: 3 → 2.

[DERIVED] If the radial transition amplitude falls to zero (ρ_radial → 0) while
tangential transitions survive, the effective dimension drops:

    d_eff: 3 → 2

This is not assumed but follows from the transition structure: radial transitions
become unavailable (no successors in the radial direction), so the effective
dimension of accessible configuration space decreases.

### XIV.3 Is This Dimensional Reduction Derived?

The previous candidate failed to derive dimensional reduction — it required assuming
metric degeneracy. Does Candidate III do better?

[DERIVED] In Candidate III, d_eff: 3 → 2 occurs when ρ_radial → 0. This is a
consequence of the profile ρ(r) ∝ r^{-C} combined with the critical threshold
ρ_min: there exists a radius r_c where ρ_radial = ρ_min.

However, this derivation assumes that:
(a) ρ_radial and ρ_tangential behave differently near the critical threshold.
(b) ρ_radial hits zero while ρ_tangential remains non-zero.

Assumption (a) is physically reasonable (the radial direction is special near a
spherical mass concentration) but is not derived from the composition law.
Assumption (b) is an additional condition.

[EFFECTIVE] Dimensional reduction d_eff: 3 → 2 is an effective description that
holds when ρ_radial → 0 while ρ_tangential > 0. Whether this differential behavior
is forced by the primitive X constraints is [UNRESOLVED].

---

## PART XV — BLACK-HOLE-LIKE REGIME

### XV.1 What is Being Asked

We are NOT assuming black holes contain no information. We are NOT assuming X becomes
informationless. We ask: does the transition structure admit a critical regime where
ordinary information-bearing transitions become inaccessible?

### XV.2 Possible Mathematical Signatures

**Signature 1: Transition graph loses connectivity**
At radius r < r_c, the configuration A in the interior can no longer be reached from
configurations B in the exterior (R_interior ∩ R_exterior = ∅). This is an event
horizon in transition-structure language.

**Signature 2: Reachable-state set collapses**
For configurations inside r_c, R*(A) (the reachability set) shrinks — fewer
configurations are accessible. At the extreme, R*(A) = {A} (only self-transition).
This is a fixed point / static state.

**Signature 3: Effective dimension changes**
d_eff → 0 in the extreme limit. This means X in the interior has no accessible
transitions at all. This would correspond to a "frozen" configuration.

**Signature 4: Causal transition cone closes**
In a spacetime picture, the accessible transitions from A form a "cone" in the
space of future configurations. As constraints increase, this cone narrows. At the
event horizon, the cone closes entirely in the outward direction: no outward
transitions are available.

### XV.3 Which Signature Is Forced by the Transition Structure?

From the profile ρ(r) ∝ r^{-C} and the composition law:

At r < r_c (below the critical threshold), ρ(r) < ρ_min. The continuation
principle requires X to not have zero transitions — but the profile forces ρ → 0
as r → 0. This is a contradiction for the smooth profile.

Resolution: the smooth power-law profile is an approximation valid for r > r_c.
Inside r_c, the profile must deviate from the power law. The transition structure
enters a qualitatively different regime.

[CONJECTURE] The transition structure inside r_c is qualitatively different from
the power-law profile outside. The specific form inside r_c depends on how the
composition law generalizes in the non-smooth regime. The signature that most
naturally emerges from the relational composition is Signature 4 (causal cone
closes), since the radial transitions becoming unavailable in one direction
(inward → no outward transition allowed by the energy constraint) while tangential
transitions survive is exactly a "cone closure" in the radial direction.

### XV.4 Information Content Inside the Critical Radius

[CONJECTURE] Inside r_c, the transition relation R still exists (X exists
everywhere by [AXIOM-R]), but the transitions available are restricted to tangential
directions. This means the information content (distinguishability between
configurations) is non-zero but has lower effective dimension.

The configurations inside r_c are distinguishable from each other via their
tangential transitions, even though they cannot communicate outward. This is
not the same as "no information inside a black hole." It is: information inside
is inaccessible to outside, but exists.

[DERIVED] The transition structure naturally admits an interior regime where
information is present but causally isolated from the exterior. This is the
transition-structure analog of a black hole horizon — not assumed, but arising
from the profile + continuation principle.

---

## PART XVI — CLASSICAL / QUANTUM QUESTION

### XVI.1 This Section Is Exploratory Only

The gravitational derivation is not modified here. The question is whether the
transition relation naturally generates noncommutative structure.

### XVI.2 Commutativity of the Radial Transition

From Part V, for the spherically symmetric static problem, the radial composition
is commutative because there is only one direction. Confirmed.

For the full 3D problem, transitions can be in different spatial directions. The
composition of two transitions in different directions:

    T_AB (transition in direction A then direction B)
    vs.
    T_BA (transition in direction B then direction A)

In Euclidean 3D space, translations commute: going 1m north then 1m east reaches
the same point as 1m east then 1m north. So spatial transitions on a flat background
COMMUTE.

However, the transition relation R is not a transition in space — it is a transition
in *configuration space C*. If C has a non-Euclidean geometry (curved), transitions
in different directions may not commute.

[UNRESOLVED] Whether the configuration space C, as induced by the transition relation
R of a spherical mass configuration, is flat or curved. If C is curved (non-zero
curvature from the X constraints), then transitions in different directions may not
commute.

### XVI.3 The Curvature-Noncommutativity Connection

In differential geometry, parallel transport of a vector around a closed loop in a
curved space returns a rotated vector. The rotation angle is proportional to the
curvature enclosed. This is the holonomy of the connection.

If the transition structure R induces a connection on C, and if this connection has
non-zero curvature, then the holonomy is non-trivial, and transitions in different
directions do not commute (their composition around a closed loop is non-trivial).

This would produce a noncommutative transition algebra:

    T_A T_B ≠ T_B T_A

in general (for transitions in non-parallel directions).

### XVI.4 The Correct Research Sequence

Following the instruction from Part XXI (do not add QM to justify noncommutativity):

    Transition relation (current status)
        ↓ [require derivation]
    Composition law → induced connection on C
        ↓ [calculate]
    Curvature of C
        ↓ [check]
    Commutativity/noncommutativity of transition algebra
        ↓ [if noncommutative]
    Algebraic structure of the transition algebra
        ↓ [representation theory]
    Possible representation as operators on a Hilbert space
        ↓ [if so]
    Complex amplitudes as natural representation field

**NOT DERIVED YET.** Each arrow is a step that requires its own analysis.

Classification of current status:
- "transition relation → composition law": [DERIVED] (Part III)
- "composition law → induced connection on C": [UNRESOLVED]
- "curvature of C": [UNRESOLVED]
- "commutativity of transition algebra": [UNRESOLVED for full 3D]
- All subsequent steps: [NOT DERIVED]

### XVI.5 Classical Limit

If the transition algebra is noncommutative, does a classical limit exist?

Classical physics has commutative observables. If X's transition algebra is
noncommutative, the classical limit must be the commutative sector — the
sub-algebra of commuting transitions.

[CONJECTURE] The classical (Newtonian) gravitational limit corresponds to the
commutative sector of the transition algebra. Noncommutative corrections are
sub-leading in some expansion parameter (possibly ℏ/S where S is an action scale).

This is [CONJECTURE] — it follows the same logic as the correspondence principle
in quantum mechanics, but has not been derived here.

---

## PART XVII — COMPLEX NUMBERS

### XVII.1 Status Investigation

Do complex numbers appear in this formalism?

**Investigation:**

The transition relation R is defined on C (a set). The composition is relational
composition. The transition amplitude f(r₁,r₂) is a real positive number (a ratio
of radii raised to a power). The radial profile ρ(r) is a real positive function.

At no point in the derivation of Parts I–XVI has any complex number appeared.

**Classification:** Complex numbers are [STATUS: UNNECESSARY at this stage].

### XVII.2 Where Complex Numbers Could Enter

**Route 1: Representation of noncommutative algebra**
If the transition algebra is noncommutative (Part XVI), its representations may
require complex matrix algebras. The simplest noncommutative algebra with positive
Hermitian structure is M_n(C) — n×n complex matrices. Complex numbers would enter
as the representation field of the noncommutative transition algebra.

This is the only legitimate route: complex numbers are [FORCED ONLY AFTER representation
theorem for noncommutative transition algebra], which is not yet derived.

**Route 2: Phase structure**
If transitions carry a phase (an angle, not just a magnitude), complex numbers
represent transitions as f = |f|·e^{iθ}. This would require:
- That f is not just a magnitude but has a direction in some internal space.
- That this direction cannot be represented by a real number.

Neither condition has been established here.

**Route 3: Interference**
If two paths A→B→C and A→D→C can interfere (their contributions add with a phase),
complex numbers are required to represent the phase of each path.

Interference requires a superposition structure on the set of paths — a further
layer of structure not present in the binary relation R. It is not derived here.

### XVII.3 Verdict on Complex Numbers

A. UNNECESSARY — at the current stage (Parts I–XVI).
B. OPTIONAL REPRESENTATION — if one wishes to use complex matrices for the
   transition operators on C (Option D from Part III). This is a choice, not a requirement.
C. MATHEMATICALLY FORCED — NOT YET, pending derivation of noncommutative algebra.
D. FORCED AFTER REPRESENTATION THEOREM — POSSIBLE, if noncommutativity is derived.
E. NOT YET DECIDABLE — Correct for the noncommutative route.

**Current answer: A and E.** Complex numbers are not needed now. Whether they are
eventually forced depends on whether the full 3D transition algebra is noncommutative,
which is unresolved.

The instruction is followed: complex numbers are not inserted because quantum
mechanics uses them. They are absent from the formalism at this stage.

---

---

## PART XVIII — FISHER / INFORMATION GEOMETRY

### XVIII.1 Candidate II as a Secondary Track

This section investigates whether the transition relation R naturally induces a
metric on the configuration space C. If it does, and if this metric is uniquely
determined (not a free choice), it would provide additional constraints on C — and
potentially force C = 1 by connecting the transition structure to information geometry.

### XVIII.2 The Key Question

Can geometry be *derived* from transition relations?
Not: can we choose a useful geometry on the transition space?

The distinction is critical because the previous candidate failed precisely by
choosing G_ij (the configuration metric) independently of the transition structure.

### XVIII.3 A Natural Metric from R

Given the transition relation R on C, a natural distance function can be constructed:

[DEFINITION] The *transition distance* between configurations A and B is:

    d_R(A, B) = min{n : ∃ path A = A₀ → A₁ → ... → Aₙ = B in R}

This is the shortest path length in the transition graph from A to B.

This is a well-defined discrete metric on the connected component of R. For a
continuous C, the limiting version would be:

    d_R(A, B) = inf{ length of a path from A to B along R-permitted directions }

where "length" is measured in C.

### XVIII.4 Does d_R Force a Geometry?

For a continuous smooth C with a transition amplitude ρ(r), the natural line element
induced by the transition structure is:

    ds²_R = (1/ρ(r))² dr² + r² dΩ²

where the factor 1/ρ(r) reflects that transitions are "more expensive" (cost more
distance) where ρ is small. This is analogous to a conformally rescaled metric.

Substituting ρ(r) ∝ r^{-C}:

    ds²_R = r^{2C} dr² + r² dΩ² = r^{2C} dr² + r² dΩ²

The effective radial metric component is g_rr = r^{2C}. The effective radial
distance element is:

    d(r) = ∫₀ʳ r'^C dr' = r^{C+1} / (C+1)   (for C ≠ -1)

This is the "transition distance" from the origin to radius r.

### XVIII.5 Fisher Information Geometry Connection

The Fisher information metric is defined for probability distributions over a
parameter space. For a transition kernel P(B|A, r) (probability of transitioning
from A to B at radius r), the Fisher metric with respect to r is:

    G_F(r) = E[ (∂ log P(B|A,r)/∂r)² ]

For the scale-invariant transition amplitude f(r₁,r₂) = (r₁/r₂)^C, interpreting
f as a (unnormalized) transition kernel:

    log f(r₁, r₂) = C · log(r₁/r₂)

    ∂/∂r₂ log f(r₁, r₂) = -C/r₂

    G_F(r₂) ∝ (C/r₂)² = C²/r₂²

This gives a Fisher metric on the radial parameter space with:

    ds²_Fisher = (C/r)² dr²

The Fisher metric on the radial coordinate r is proportional to r^{-2} (hyperbolic
metric). This is not the flat Euclidean metric.

### XVIII.6 Does Information Geometry Force C?

The Fisher metric (C/r)² dr² depends on C only through the overall factor C².
This factor does not force the value of C — it is a free scale.

However, there is a deeper observation: the Fisher metric (1/r)² dr² (C=1) is
exactly the metric on the *hyperbolic plane* H² (in the upper half-plane model
with r as the "height" coordinate). Hyperbolic geometry has a constant negative
curvature K = -1.

For C = 2: the metric (2/r)² dr² has curvature K = -1 as well (it's just a
rescaling, which doesn't change the curvature sign).

The curvature of the metric C²/r² dr² is K = -1 (hyperbolic) for all C ≠ 0.
The specific value of C does not change the qualitative geometry — only the
scale of distances.

[DERIVED] The Fisher metric induced by the scale-invariant transition amplitude
is hyperbolic for any C ≠ 0. The hyperbolic geometry is determined by the transition
structure, not freely chosen. However, the scale C remains free.

[DERIVED] The Candidate II metric (configuration-space geometry) is NOT an
independent object from Candidate III in the spherical case: it is induced by the
transition amplitude. This merges Candidate II and Candidate III in the spherical
reduction.

However, merging them does not force C. The hyperbolic geometry is produced for
any C ≠ 0.

### XVIII.7 What Would Force C From Information Geometry

The Fisher information metric becomes independent of C only if the transition
amplitude is normalized (a proper probability kernel). For a normalized kernel,
the Fisher metric determines the intrinsic geometry of the parameter space.

If we require the transition amplitude to be a *proper probability distribution*
(normalizable), then:

    ∫₀^∞ f(r₀, r) dr = 1

For f(r₀, r) = (r₀/r)^C dr:
    ∫₀^∞ (r₀/r)^C dr diverges for all C > 0.

A normalized version requires a cutoff (either at r_min or via a decay factor).
If a cutoff is introduced, it brings a new scale — and the problem is no longer
scale-invariant.

[DERIVED] In the scale-invariant regime, the Fisher metric does not force C.
Normalization of the transition kernel requires departing from scale invariance,
introducing a new parameter.

---

## PART XIX — FREEDOM AUDIT

### XIX.1 Mandatory Accounting

Every independent choice in the model is listed. For each:

    DERIVED   — follows from primitive constraints
    PRIMITIVE — taken as an axiom
    EFFECTIVE — holds in a regime
    ARBITRARY — not constrained
    UNRESOLVED — status unclear

### XIX.2 The Complete List

| Choice | Classification | Reason |
|--------|---------------|--------|
| R is a directed binary relation | PRIMITIVE ([AXIOM-R]) | The ontological choice |
| Configurations defined by transition structure | PRIMITIVE ([AXIOM-C1]) | Operational definition |
| Locality: R(x,t) depends only on local P | PRIMITIVE | Standard field-theoretic locality |
| Composition R(x1,x3) = R(x2,x3)∘R(x1,x2) | DERIVED | From locality + path-independence |
| Associativity of composition | DERIVED | Theorem: relational composition |
| Radial amplitude form f(r1,r2) | DERIVED (given g) | From functional equation |
| Scale invariance: f depends only on r2/r1 | PRIMITIVE (no preferred scale) | Requires justification (see below) |
| Power-law profile f=(r1/r2)^C | DERIVED | From scale invariance + functional equation |
| Exponent C | ARBITRARY | NOT FORCED. This is the surviving free constant. |
| Asymptotic condition: ρ→0 at r→∞ | EFFECTIVE | Requires C > 0 |
| No terminal nodes [AXIOM-CONT] | PRIMITIVE | Continuation principle |
| Mass coupling A(M) | ARBITRARY | Not constrained by composition law |
| Additivity of mass charge | PRIMITIVE (if assumed) | Separate assumption needed |
| Matter coupling to -dρ/dr | ARBITRARY or UNRESOLVED | Not derived from R |
| Universality of coupling | UNRESOLVED | Requires compositional coupling argument |
| ρ_min (critical threshold) | UNRESOLVED | Physical meaning not fully determined |
| Full 3D transition algebra (commutativity) | UNRESOLVED | Requires 3D analysis |
| Complex number structure | NOT REQUIRED | No evidence of necessity |
| Metric on C (geometry) | DERIVED from R | Via Fisher/transition distance |
| Value of C from geometric argument | UNRESOLVED | Hyperbolic geometry holds for any C |

### XIX.3 Counting the Freedom

**Previous candidate (field ontology):**
Free functions: α, g(M), constraint form f(q,M,r), speed c(q,r), matter coupling.
Total: 5+ free functions. Dimensional freedom: infinite.

**This candidate (transition relation ontology) after applying all derived constraints:**
Free constants: C (one real number), A(M) (one function of M), matter coupling rule.
Total: 1 free constant + 1 free function + 1 coupling rule.
Dimensional freedom: finite (1 number) + one function.

**Reduction achieved:**
From 5+ free functions (infinite-dimensional freedom) to 1 free constant + 1 free
function + 1 coupling rule.

This is a genuine reduction. However, the surviving freedom is still non-trivial.
The candidate is not fully determined.

### XIX.4 The Status of Scale Invariance

Scale invariance was used as a constraint in Part VIII. But is it a legitimate
constraint?

The argument: in the absence of matter, X has no preferred length scale. The
presence of mass M sets a preferred scale in *strength* but not in the radial
profile. Therefore the radial profile is scale-free.

This argument has a weakness: the mass M has dimensions. Any combination of M and
fundamental constants (G, c) can produce a length scale (e.g., the Schwarzschild
radius r_s = 2GM/c²). If the transition structure knows about G and c (through
the coupling to matter), then scale invariance is broken by the coupling constants.

[UNRESOLVED] Whether scale invariance of the radial profile is legitimately derived
from the primitive X constraints, or whether it is a convenient assumption that
hides the freedom in a different form (the freedom of choosing the coupling constants
G and c).

If scale invariance is not a legitimate constraint, then g(r) = C/r is just one of
many possible forms, and C is not the only freedom. This would push the situation
back toward the previous candidate's failure mode.

### XIX.5 Summary of Freedom Audit

The candidate has achieved:
- Formal reduction from arbitrary field ontology to transition relation ontology.
- Derivation of composition law from locality.
- Reduction of radial profile freedom from arbitrary function to power law r^{-C}.
- Natural separation of ordinary gravity and collapse.
- Active continuation principle only in the collapse regime.

The candidate has NOT achieved:
- Determination of the exponent C.
- Derivation of mass coupling.
- Derivation of matter coupling rule.
- Full 3D analysis.
- Proof that scale invariance is a derived constraint.

**Net verdict on freedom:** One free constant C (the exponent) and one free function
A(M) (mass coupling) survive after all derived constraints are applied. The coupling
rule (how -dρ/dr produces acceleration) is an additional constitutive choice.

---

## PART XX — KILL TESTS

### K1: Radial Exponent Freedom

**Question:** Does spherical symmetry plus composition force the exponent?

**Test:** Derive C from the functional equation and physical constraints alone.

**Result:** PARTIAL PASS.
- The composition law + scale invariance reduces infinite freedom to one constant C.
- C is not fixed to any specific value.
- Newtonian gravity requires C = 1, which is not derived.

**Assessment:** The candidate reduces but does not eliminate exponent freedom.
This is progress but not full success.

---

### K2: Coupling Freedom

**Question:** Does the transition structure determine how source strength enters?

**Test:** Derive the mass amplitude A(M) from the composition law or primitive constraints.

**Result:** FAILS.
- The composition law constrains radial dependence only.
- A(M) is a free function.
- Additivity of mass requires a separate assumption.

**Assessment:** Mass coupling is not determined by the transition structure. This
is a surviving failure analogous to g(M) in the previous candidate.

---

### K3: Metric Freedom

**Question:** Can geometry be derived from the transition structure or must it be supplied?

**Test:** Construct the metric on C from R and check whether it is unique.

**Result:** PARTIAL PASS.
- The Fisher metric / transition distance is derived from R (not freely chosen).
- The metric is hyperbolic with factor C²/r² — derived but depends on C.
- C itself is not determined (see K1).

**Assessment:** The metric is derivable given C, but since C is free, the metric
retains one free parameter.

---

### K4: Propagation Freedom

**Question:** Does finite propagation follow from the transition structure?

**Test:** Determine whether the composition law or continuation principle implies
a finite propagation speed.

**Result:** UNRESOLVED.
- The composition law R(r₁,r₃) = R(r₂,r₃) ∘ R(r₁,r₂) is spatial, not temporal.
- It says nothing directly about the speed of change of R.
- Finite propagation would require: R at point x cannot change before the modification
  arrives from the source at speed v_max.
- The primitive X constraint says X evolves through admissible transitions, but the
  temporal rate of evolution is not constrained by the composition law.
- The previous C2 era established that finite propagation (the telegrapher equation)
  arose from a relaxation time τ — which was itself a free parameter.

**Assessment:** Finite propagation is NOT forced by the transition composition law.
It would require an additional constraint on the time-dependent transition dynamics.
This is a surviving gap.

---

### K5: Universality

**Question:** Does the same geometry act universally on different matter configurations?

**Test:** Check whether matter of different internal structure experiences the same
acceleration from ρ(r) ∝ r^{-C}.

**Result:** UNRESOLVED.
- Universality follows if all matter uses the same coupling rule a ∝ -dρ/dr.
- The coupling rule is not derived from the transition structure.
- If the coupling is through geodesics of the induced metric, and if all matter
  follows geodesics of the same metric, universality follows.
- Whether matter follows geodesics of the transition metric is unresolved.

**Assessment:** Universality is plausible but unproved. It requires the coupling
rule to be derived from the transition structure, which has not been done.

---

### K6: Collapse

**Question:** Does the same structure naturally generate a critical regime?

**Test:** Show that ρ(r) → 0 produces a qualitatively different transition regime.

**Result:** PASSES.
- ρ(r) ∝ r^{-C} → 0 as r → 0 (for C > 0) is NOT the correct direction.
  Actually, ρ(r) ∝ r^{-C} → ∞ as r → 0.
  CORRECTION: The transition amplitude f(r₀,r) = (r₀/r)^C measures transitions
  relative to a reference r₀. Moving inward (r < r₀), f increases — more transitions
  available. This is the wrong direction for collapse.

**Critical re-analysis:**
The issue is direction. Near the source (r → 0), ρ(r) = ρ₀·r^{-C} → ∞, meaning
more transitions near the source. But for collapse, we need FEWER transitions inside
some critical radius.

This requires the effective gravitational potential to *reduce* available transitions
at small r, not increase them. For the profile ρ ∝ r^{-C} to cause collapse, C must
be negative (ρ → 0 as r → 0), which contradicts the asymptotic condition (we need
ρ → 0 at r → ∞, not r → 0).

**Diagnosis:** There is an inconsistency in the direction of the profile. The profile
ρ ∝ r^{-C} cannot simultaneously satisfy:
(a) ρ → 0 at large r (asymptotic freedom), AND
(b) ρ → 0 at small r (collapse condition).

It satisfies (a) OR (b), depending on the sign of C.

For C > 0: ρ → ∞ at r → 0 and ρ → 0 at r → ∞. This gives ordinary attraction
(matter attracted inward toward higher ρ) but no collapse at small r.

For C < 0: ρ → 0 at r → 0 and ρ → ∞ at r → ∞. This would push matter outward
(repulsion) and produce "collapse" at large r — which is cosmological expansion,
not gravitational collapse.

This is a GENUINE FAILURE of the profile analysis.

**Resolution attempt:** The collapse regime requires a different physical input —
the mass M must set a scale at which the transition profile changes character. The
pure power law (scale-free) cannot describe both ordinary attraction AND collapse
within the same functional form.

[DERIVED — NEGATIVE] The scale-free power-law profile ρ(r) ∝ r^{-C} cannot
describe both ordinary gravitational attraction and gravitational collapse within
the same model. A scale is needed.

**Revised assessment of K6:** The transition structure as developed in Part VIII
(scale-free, power-law) naturally generates ordinary attraction. Collapse requires
a scale — either from the mass M setting a characteristic radius (Schwarzschild
radius), or from a breakdown of scale invariance at strong fields.

**K6 Result:** CONDITIONAL PASS.
- The same transition structure generates ordinary attraction (C > 0, ρ large near source).
- For collapse to occur, a scale (set by M) must break the power-law profile.
- This scale is the Schwarzschild radius r_s = 2GM/c².
- The collapse regime is where r ≈ r_s, and the power-law approximation breaks down.

---

### K7: Noncommutativity

**Question:** Does noncommutative structure emerge from the transition relation?

**Test:** Derive whether the transition algebra is commutative or not.

**Result:** UNRESOLVED (for full 3D).
- For spherical symmetric reduction: commutative (radial steps commute).
- For full 3D: depends on curvature of C, which is unresolved.
- No noncommutative structure has been forced.

**Assessment:** Neither commutative nor noncommutative structure has been forced.
The question is genuinely open for the full 3D case.

---

### K8: Information Measure

**Question:** Can distinguishability be derived without arbitrarily choosing an entropy formula?

**Test:** Construct the distinguishability between configurations A and B from R alone.

**Result:** PARTIAL PASS.
- The transition distance d_R(A,B) (Part XVIII) is derived from R.
- The Fisher metric on the radial parameter space is derived from R.
- However, both depend on C.
- A unique, C-independent distinguishability measure is not produced.

**Assessment:** Distinguishability is derivable in principle from R, but retains C
as a free parameter.

---

### K9: Classical Limit

**Question:** If noncommutative structure exists, does a classical limit emerge?

**Test:** Not applicable yet — noncommutative structure has not been derived.

**Result:** CANNOT TEST.

---

### K10: Overfitting

**Question:** Can the formalism reproduce essentially any radial law by choosing
an unconstrained function?

**Test:** Count independent structural choices and determine whether the radial
law is arbitrary.

**Result:** PARTIAL FAIL.
- The transition relation formalism with scale invariance is constrained to
  power-law radial profiles.
- The exponent C is free — infinitely many power laws are possible (each C
  gives a different law).
- But not all functional forms are achievable: only power laws. Exponential,
  logarithmic, or oscillatory force laws cannot be produced.

**Assessment:** The candidate cannot reproduce arbitrary force laws (unlike the
previous candidate which could reproduce any form). But it can reproduce any
power-law force law. Since we are comparing to a power law (Newtonian), the
candidate must force the specific exponent C = 1. It does not.

K10 is a PARTIAL FAIL: not completely empty (only power laws), but not unique (C free).

---

### Kill Test Summary

| Test | Result | Status |
|------|--------|--------|
| K1: Radial exponent | Freedom reduced to one C | PARTIAL PASS |
| K2: Coupling freedom | A(M) not determined | FAILS |
| K3: Metric freedom | Metric derived but depends on C | PARTIAL PASS |
| K4: Propagation | Not forced by composition law | UNRESOLVED |
| K5: Universality | Plausible but not derived | UNRESOLVED |
| K6: Collapse | Ordinary attraction yes; collapse requires scale | CONDITIONAL PASS |
| K7: Noncommutativity | Not derived, not forced | UNRESOLVED |
| K8: Information measure | Derived but depends on C | PARTIAL PASS |
| K9: Classical limit | Cannot test yet | N/A |
| K10: Overfitting | Only power laws; but C free | PARTIAL FAIL |

---

---

## PART XXI — MATHEMATICAL CONSISTENCY vs PREDICTIVE CONSTRAINT

### XXI.1 The Previous Candidate's Failure Mode

The previous candidate (field ontology, Giga 01–03) was mathematically consistent
but predictively empty. It could reproduce Newtonian gravity by choosing α = 2,
but the choice was not derived. The theory was not falsifiable by the radial law
because any radial law could be reproduced.

The instruction is explicit: do not stop at "mathematically coherent."

### XXI.2 Assessment for Candidate III

**Mathematical consistency:**
The transition relation R is a well-defined mathematical object. The composition law
is derived from locality (not assumed). Associativity is a theorem. The functional
equation has well-defined solutions. The continuation principle (no terminal nodes)
is a consistent constraint on R. No mathematical contradictions arise.

**Verdict:** MATHEMATICALLY CONSISTENT. ✓

**Predictive constraint:**
The candidate predicts:
1. The force law is a power law (not an arbitrary function). This is a constraint.
2. The power-law exponent is C (a free constant). This is NOT a prediction.
3. The force law could be r^{-1.5} or r^{-2} or r^{-3} — all are equally allowed.

**Verdict:** PARTIALLY CONSTRAINED.

The candidate constrains the *form* (power law) but not the *exponent*. Compared
to the field ontology (which could produce any functional form), this is an
improvement. But compared to the goal (unique prediction), it falls short.

**Empirical success:**
The candidate does not uniquely predict Newtonian gravity. C = 1 is required but
not derived. The candidate is consistent with Newtonian gravity but also with
many non-Newtonian power-law gravity theories.

**Verdict:** EMPIRICALLY CONSISTENT (for correct C) BUT NOT EMPIRICALLY FORCED.

### XXI.2 The Specific Gains Over the Previous Candidate

| Property | Field Candidate | Transition Candidate |
|----------|----------------|---------------------|
| Force form | Arbitrary | Power law only |
| Free functions | 5+ (infinite dim) | 1 constant + 1 function |
| Ordinary gravity mechanism | Continuation (wrong) | Gradient of ρ (correct) |
| Collapse mechanism | Trivially satisfied | Active at ρ→0 (correct) |
| Geometry from structure | Not derived | Derived (hyperbolic, C-dependent) |
| Mass coupling | Free function | Free function (unchanged) |

The transition candidate is strictly better than the field candidate in every
dimension except mass coupling (which remains equally unconstrained).

---

## PART XXII — EXISTING PHYSICS AS TESTS, NOT AXIOMS

### XXII.1 Newtonian Gravity as a Test

Newtonian gravity predicts a(r) ∝ M/r². The transition candidate predicts
a(r) ∝ A(M) · r^{-(C+1)}.

**Does the theory produce Newtonian gravity?**
Only if C = 1 AND A(M) ∝ M. Neither is derived.

**Is this consistent with Newtonian gravity?**
Yes, for C = 1 and A(M) ∝ M.

**Is it falsified by Newtonian gravity?**
Not yet — because C is free. But if further constraints force C ≠ 1, the theory
would be falsified.

### XXII.2 General-Relativistic Weak-Field Behavior

In the Newtonian limit of GR, the gravitational potential is Φ = -GM/r, giving
a(r) = -GM/r². The transition candidate reproduces this only for C = 1.

The GR correction to Newtonian gravity is at order (v/c)² and (GM/rc²). The
transition candidate currently has no causal speed built in (K4 failed). Without
a propagation speed, the GR limit cannot be analyzed.

### XXII.3 Gravitational Collapse

Gravitational collapse in GR occurs when a mass is compressed inside its
Schwarzschild radius r_s = 2GM/c². The transition candidate predicts a qualitative
change in the transition structure at some critical radius r_c. Whether r_c = r_s
requires connecting A(M) and C to the specific combination 2GM/c² — which requires
knowing G and c, neither of which appears in the transition structure.

**Status:** Collapse is qualitatively present but quantitatively unconnected to
the Schwarzschild radius. The specific scale r_s requires additional physics input.

### XXII.4 Information Theory

The previous C2 candidate (Giga's predecessor) used information-theoretic quantities
(entropy, decoherence). The transition candidate connects to information theory
through the Fisher metric (Part XVIII): the metric on the transition parameter space
is hyperbolic, which is a known result in information geometry (the Fisher metric
for exponential families is hyperbolic).

**Status:** The connection to information geometry is natural and derived — not inserted.
The Fisher metric is produced by the transition amplitude structure, not assumed.
This is a genuine link between the transition ontology and information theory.

### XXII.5 Phase-1 fxt Laws — Classification

From the fxt COMPLETE_MASTER_EQUATION.md, the C2-era predictions:

| Old Law | Status in Candidate III |
|---------|------------------------|
| τ ∂²s/∂t² + ∂s/∂t = c²τ∇²s (telegrapher) | SUPERSEDED FORMULATION — different ontology |
| Γ_φ ∝ ω_rot² (decoherence) | EMPIRICAL REGULARITY — not yet derivable |
| C_Γ(r) = K₀(r/ξ_c)/K₀(a/ξ_c) (spatial correlator) | EMPIRICAL REGULARITY — not yet derivable |
| Finite propagation speed c | UNSUPPORTED ASSUMPTION in Candidate III (K4 fails) |
| Irreversibility/decay | DERIVABLE TARGET — follows from partial order structure of R |
| Non-pairwise interactions | UNRESOLVED — requires multi-point R analysis |
| Saturation at ω_max | UNSUPPORTED ASSUMPTION — no ω_max in Candidate III |

The transition candidate does not yet recover the C2 predictions. However:
- The irreversibility is a natural consequence of the partial-order structure of R
  (transitions are directional, with no guaranteed inverses).
- The decoherence prediction Γ_φ ∝ ω² and spatial correlator are empirical
  regularities that belong to the experimental layer, not the ontological layer.
  Candidate III does not contradict them; it simply does not yet derive them.

---

## PART XXIII — RELATION TO PHASE 1

### XXIII.1 What Phase-1 Established

Phase 1 (the C2 / SXC-IGC era) produced:

1. A mathematical model of X as an information density s(x,t) with telegrapher dynamics.
2. A decoherence prediction Γ_φ = k_rot · ω_rot².
3. A spatial correlator C_Γ(r) = K₀(r/ξ_c)/K₀(a/ξ_c).
4. The finding that the telegrapher model is parameter-degenerate with conventional
   physics — it does not make unique predictions beyond conventional models.
5. A surviving empirical regularity: the spatial decoherence correlator.

Phase-1 was formally closed because C2 was shown to be mathematically equivalent
to known physics in the observationally accessible regime.

### XXIII.2 What Candidate III Does With Phase-1 Results

The transition relation candidate does not replace Phase-1 results. It operates
at a deeper ontological level.

The C2 telegrapher equation is:

    τ ∂²s/∂t² + ∂s/∂t = c²τ ∇²s + (coupling terms)

This is a partial differential equation on a field s(x,t). If the transition
candidate is correct, this equation should be DERIVABLE as the effective behavior
of the transition relation in some limit.

[CONJECTURE] The telegrapher equation emerges from the transition relation dynamics
as the linearized, continuous limit of the composition law, when:
(i) The transition relation is nearly uniform (small deviations from R₀).
(ii) The propagation speed c enters as the characteristic speed of changes to R.
(iii) The relaxation time τ enters as the decay time of a localized perturbation in R.

This derivation has NOT been performed. It is a target for subsequent work.

### XXIII.3 The Phase-1 Connection Is a Derivable Target

The status of Phase-1 laws in Candidate III:

**Finite propagation speed:** This is in K4 (unresolved). The composition law does
not force finite propagation. But finite propagation might emerge from a time-dependent
extension of the spatial composition law. This is a derivable target.

**Irreversibility:** The partial order structure of R (Part VI.3) naturally produces
irreversibility. If A → B is a permitted transition and B → A is not, then the
transition relation is directional — time-irreversible. This is consistent with the
C2 era's treatment of irreversibility as a physical requirement.

**Decoherence:** The decoherence prediction Γ_φ ∝ ω² was derived in C2 from the
information-energy coupling α·E. In Candidate III, the energy-coupling term would
emerge from how the transition relation responds to rotational energy. This is a
derivable target but has not been derived.

---

## PART XXIV — FINAL VERDICT

### XXIV.1 What Was Done

This document investigated Candidate III — the transition relation ontology — as
a replacement for the field ontology that failed in Giga 01–03.

The investigation:
1. Defined R as a directed binary relation on a configuration space C.
2. Derived the spatial composition law from locality.
3. Solved the functional equation for the spherical static case.
4. Applied scale invariance to reduce freedom to one constant C.
5. Examined Newtonian limit, mass coupling, universality, collapse, and continuation.
6. Performed a complete freedom audit and ten kill tests.

### XXIV.2 What Was Found

**Genuine gains:**
- Freedom reduced from 5+ free functions to 1 free constant C + 1 free function A(M).
- Ordinary gravity and collapse are naturally separated (previous candidate failed here).
- Continuation principle is active only in collapse regime (previous candidate: trivially satisfied).
- Fisher metric is derived from R, not freely chosen.
- The force form is constrained to power laws (not arbitrary).
- The scale-free power law ρ(r) ∝ r^{-C} naturally attracts matter inward.

**Surviving failures:**
- C is not forced. Newtonian gravity requires C = 1, which is not derived.
- A(M) (mass coupling) is not forced. Additivity requires a separate assumption.
- The matter coupling rule (a ∝ -dρ/dr) is not derived from R.
- Finite propagation speed is not forced by the composition law.
- The scale needed for collapse (Schwarzschild radius) is not generated internally.

**New problem revealed in K6:**
The scale-free profile ρ(r) ∝ r^{-C} cannot simultaneously generate:
(a) Ordinary gravitational attraction (needs ρ large near source, small far away).
(b) Gravitational collapse threshold (needs ρ → 0 at some finite r_c).

These require ρ to have opposite behavior at small r in the two regimes. The
resolution is that collapse requires a mass-dependent scale r_c ~ r_s = 2GM/c²
where the power-law approximation breaks down. This scale is external to the
transition relation as formulated.

### XXIV.3 The Verdict

**VERDICT: PROMISING BUT UNDERDETERMINED**

**Justification:**

The candidate is NOT mathematically incoherent.
The candidate is NOT predictively empty (it rules out non-power-law force laws).
The candidate IS a genuine improvement over the previous field candidate.
The candidate is NOT a complete theory — one free constant C and one free function
A(M) survive, and the coupling rule requires derivation.

The candidate does not fail on any definitive kill test, but it does not succeed
on the decisive one (K1: exponent determination).

### XXIV.4 The Precise Remaining Problem

The precise remaining problem is:

> The transition relation formalism produces a one-parameter family of power-law
> force laws {r^{-(C+1)} : C ∈ R⁺}. Newtonian gravity is the member C = 1.
> Nothing in the primitive X constraints (locality, composition, scale invariance,
> continuation) forces C = 1.

This is the same fundamental problem as before, but now located with much greater
precision. The previous candidate had five free functions. This candidate has one
free constant. The progress is real. The problem is not gone.

### XXIV.5 What the Next Investigation Must Ask

The failure points at a missing constraint. There must be a property of X that
forces C = 1 specifically. The candidate natural constraints are:

**Option A: Three-dimensional consistency**
The composition law was solved in the radial reduction. The full 3D composition law
may impose additional constraints that, in 3D specifically, force C = 1. This requires
solving the functional equation on R³ rather than R⁺.

**Option B: Energy conservation**
If the total "transition energy" integrated over all radii is conserved (an integral
constraint on the transition structure), and if this conservation law is connected
to the mass M, the combination might force C = 1.

**Option C: Coupling-derived exponent**
The exponent C may be forced by the specific rule by which the transition amplitude
couples to matter acceleration. If the coupling is not a → -dρ/dr but something
more structured (e.g., a → -Δ_R ρ where Δ_R is the Laplace-Beltrami operator of
the hyperbolic metric induced by R), the exponent may be forced by the geometry.

**Option D: Information conservation**
If the total number of distinguishable configurations (information capacity) is
conserved through any sphere at any radius, this is a Gauss's law for the transition
structure. In 3D, this would give ρ(r) · r² = constant, forcing ρ ∝ r^{-2} and
C = 2 — NOT Newtonian. This is already ruled out as giving a(r) ∝ r^{-3}.

**Option E: A deeper primitive**
The transition relation with composition + scale invariance may not be the deepest
structure. A more primitive structure may determine C. What that structure is remains
unknown.

### XXIV.6 Research Status Update

**Previous candidate (field ontology):** SUPERSEDED. Formally closed.
**This candidate (transition relation):** PROMISING BUT UNDERDETERMINED.

**Status for next investigation:**

The next investigation should focus on **Option A: the full 3D composition law**.

The spherical reduction collapsed the problem to one dimension (radial), which lost
the information about spatial dimension. The 3D composition law is:

    R(x, z) = R(y, z) ∘ R(x, y)   for all spatial points x, y, z in R³

Under spherical symmetry, but without collapsing to the radial coordinate alone,
this may produce stronger constraints. Specifically, the composition in different
angular directions may interact with the radial composition in a way that forces C.

The key test: **does the 3D functional equation force C = 1?**

If yes: the transition relation ontology predicts Newtonian gravity without additional
assumptions.

If no: the candidate is FAILS (REQUIRES NEW ONTOLOGY), and the investigation must
identify what deeper structure determines C.

---

## Summary Table

| Section | Key Result | Status |
|---------|-----------|--------|
| I: Fundamental object | R = directed binary relation | PRIMITIVE |
| II: Configuration | Defined by transition structure | PRIMITIVE |
| III: Composition | Derived from locality | DERIVED |
| IV: Associativity | Theorem | DERIVED |
| V: Commutativity | Trivial in spherical reduction; open in 3D | PARTIAL |
| VI: Invariants | Partial order (irreversibility) is invariant | DERIVED |
| VII: Spherical symmetry | Reduces to one-parameter family | DERIVED |
| VIII: Functional equation | f=(r₁/r₂)^C, C free | PARTIAL (freedom reduced) |
| IX: Newtonian limit | Requires C=1, not derived | FAILS |
| X: Mass | A(M) not forced | FAILS |
| XI: Universality | Plausible, not derived | UNRESOLVED |
| XII: Gravity vs collapse | Naturally separated | DERIVED |
| XIII: Continuation | Active only in collapse regime | DERIVED |
| XIV: Collapse | d_eff: 3→2 when ρ_radial→0 | EFFECTIVE |
| XV: Black holes | Causal cone closure natural | CONJECTURE |
| XVI: Classical/quantum | Noncommutativity unresolved | UNRESOLVED |
| XVII: Complex numbers | Not required | DERIVED (absence) |
| XVIII: Fisher geometry | Hyperbolic, derived from R | DERIVED |
| XIX: Freedom audit | 1 const + 1 func + coupling | ACCOUNTING |
| XX: Kill tests | K1 partial, K2 fails, K6 new structural problem | MIXED |
| XXI: Consistency | Mathematically consistent, not empirically forced | VERDICT |
| XXII: Physics tests | Power law predicted; Newtonian not forced | PARTIAL |
| XXIII: Phase-1 relation | Telegrapher derivable target; not yet derived | TARGET |
| XXIV: Final verdict | PROMISING BUT UNDERDETERMINED | VERDICT |

---

*End of 05_TRANSITION_RELATION_CANDIDATE.md*

