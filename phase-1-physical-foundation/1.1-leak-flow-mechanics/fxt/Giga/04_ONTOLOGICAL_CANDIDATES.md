# 04_ONTOLOGICAL_CANDIDATES.md
## What Mathematical Structure Can Replace Arbitrary Constitutive Freedom?

**Date:** 2026-08-23
**Predecessor:** 03_KILL_TESTS.md (FAILS PREDICTIVE TEST verdict)
**Status:** ONTOLOGICAL INVESTIGATION STAGE
**Core question:** What is X, more fundamentally — before choosing how to represent it?

---

## 1. Why the Formalism Failed — The Missing Layer

### 1.1 The Exact Point of Failure

The previous candidate did not fail because X is mathematically inconsistent.
It did not fail because attraction is impossible.
It failed at a more precise location.

The original promise was:

```
microscopic constraint → observable
```

What was actually delivered:

```
microscopic constraint + chosen constitutive law → observable
```

The constitutive law was not derived. It was selected to produce a desired result.

This is not a minor calibration problem. A theory that can produce any radial law by
choosing its constitutive functions is not a theory of gravity. It is a parameterization
of radial laws written in the notation of a theory of gravity.

### 1.2 The Two-Layer Confusion

The primitive hypothesis of the previous candidate was:

> X cannot evolve through unavailable configurations and must reorganize when
> continuation becomes impossible.

This hypothesis concerns *what is allowed* — the admissible set.

But the mathematical work required specifying *how the allowed set is shaped* — the
geometry of the admissible set.

These are different questions.

The first was hypothesized.
The second was supplied by hand, through the constitutive choices α, g(M), and K_X form.

What the candidate discovered, precisely, is:

```
constraint ≠ geometry of constraint
```

The first was there from the beginning.
The second was missing throughout.

### 1.3 The Exact Form of the Gap

The candidate derived:

```
q(r) ∝ r^{-α/2}
a(r) ∝ r^{-(α/2 + 1)}
```

To recover Newtonian gravity:

```
a(r) ∝ 1/r²   requires   α = 2
```

To recover correct mass scaling:

```
g(M) ∝ M²
```

Neither α = 2 nor g(M) ∝ M² follows from the primitive constraints X1–X4.
They were inserted by observational demand.

This means the question for the next investigation is not:

> "What additional equation fixes α?"

It is:

> "What property of X could uniquely determine the geometry of its admissible
> configurations — so that α is not a free parameter but a consequence?"

### 1.4 What the Failure Tells Us

The failure is informative. It points at a specific missing ingredient.

The previous candidate told X *what it cannot do*.
It did not tell X *how the remaining possibilities are organized geometrically*.

The distinction matters because the geometry of the admissible set is exactly what
determines the radial law. To derive the radial law, one needs the geometry. To derive
the geometry, one needs something more primitive than "some states are forbidden."

The target is therefore:

```
primitive invariant → K_X → α = 2
```

rather than:

```
K_X(α)  and  choose α = 2
```

---

## 2. What the Free Parameters Actually Are — An Accounting

Before asking what should replace the old formalism, we need to count exactly what
freedom was silently assumed. The following are not parameters to be fit — they are
ontological decisions that were made implicitly.

### 2.1 The Radial Profile Exponent α

**What it encodes:** The rate at which the X constraint strength falls off with distance
from a gravitating mass.

**What was assumed:** That K_X has the form f(q, M, r) ≤ c₀ · g(M) · h(r) with
h(r) ∝ r^{-α}. The form of h was not derived.

**Why it matters:** α controls everything downstream. α = 2 gives Newtonian gravity.
α = 1 gives a different force law. α = 3 gives another. All are internally consistent
with the primitive constraints. None is preferred by them.

**What a genuine theory requires:** A reason why a specific α must follow from more
basic structure. Not a reason to prefer α = 2 observationally — that is already known.
A reason why any physical system satisfying the primitive X constraints is *forced* to
produce a specific α.

### 2.2 The Mass-Coupling Function g(M)

**What it encodes:** How the strength of the X constraint scales with the amount of
mass producing it.

**What was assumed:** g(M) is a free function. Setting g(M) ∝ M² gives the correct
mass proportionality of Newtonian gravity.

**Why it matters:** The mass dependence F ∝ M is one of the most fundamental empirical
facts about gravity. If the theory cannot derive it, it has no explanatory content
regarding gravity at all.

**What a genuine theory requires:** Either a derivation of g(M) ∝ M² from the
structure of X, or — more interestingly — a demonstration that M itself is defined
as a quantity of X configuration, from which the scaling emerges automatically.

### 2.3 The Constraint Form f(q, M, r)

**What it encodes:** The precise mathematical relationship between X state q, source
mass M, and position r that determines which configurations are admissible.

**What was assumed:** A specific inequality form was chosen for tractability. Other
forms are equally compatible with the primitive constraints.

**Why it matters:** The constraint form determines the topology of the admissible set.
Different topologies produce qualitatively different behavior — not just different
exponents.

**What a genuine theory requires:** Either a derivation of the constraint form from
something more primitive, or a demonstration that a unique constraint form is forced
by consistency requirements (e.g., compositionality, locality, symmetry).

### 2.4 The Configuration-Space Metric G_ij

**What it encodes:** The geometry of the X configuration space — specifically, how
distances between configurations are measured, and therefore which directions count
as independent.

**What was assumed:** G_ij = diag(1, 1, 1) initially, with dimensional reduction
introduced by setting one eigenvalue to zero. Neither the initial form nor the
reduction mechanism was derived.

**Why it matters:** G_ij determines the effective dimension of the configuration space.
Without it, dimensional reduction has no content beyond an assertion.

**What a genuine theory requires:** Either a derivation of G_ij from the structure of
X itself, or a demonstration that G_ij has a unique form compatible with the primitive
constraints.

### 2.5 The Propagation Law c(q, r)

**What it encodes:** The speed at which changes in X configuration propagate through
space.

**What was assumed:** c(q, r) is a free function. The candidate was never tested on
propagation behavior because c was never specified.

**Why it matters:** The propagation speed determines the causal structure of X dynamics.
If c is a free function, the theory has no predictions about signal propagation.

**What a genuine theory requires:** Either a derivation of c from the transition
structure of X, or a demonstration that some finite c is forced by consistency.

### 2.6 Summary: The Freedom Is Ontological

The five free parameters/functions above are not numerical parameters like coupling
constants in an effective theory. They are ontological choices — each one reflects a
decision about what kind of mathematical object X fundamentally is.

This is the deeper problem. One cannot fix α by observational input and call it
a derivation. The freedom exists because the underlying ontology was not specified
precisely enough.

The question is not: which values of the free parameters reproduce gravity?
The question is: which ontology leaves no free parameters before gravity is calculated?

---

## 3. The Four Candidate Fundamental Objects

We now investigate four distinct answers to the question: what is X?

Each candidate is a genuinely different mathematical starting point. They are not
parameterizations of each other. For each, we specify the mathematical definition,
what it determines uniquely, what remains free, and the simplest spherical system
it implies.

---

### Candidate I: Field Value

**Mathematical definition:**
X is a field φ(x, t) valued in some space V (scalar, vector, tensor, or section of
a bundle). The local state of X is completely characterized by φ(x, t).

**Natural dynamics:** Field equation of the form Dφ = F[φ, P, ∂φ, ...] for some
differential operator D and source F.

**What this uniquely determines:** Given a field equation and boundary conditions,
the radial solution is determined. Different field equations give different α.

**What remains free:** The choice of field equation. Infinitely many field equations
are compatible with the primitive constraints. This reproduces exactly the freedom
we found in the previous candidate — because the previous candidate was, at bottom,
a constrained field theory.

**Simplest spherical system:** Any power-law radial solution φ(r) ∝ r^n is achievable
by appropriate choice of field equation. No canonical spherical solution exists without
a canonical field equation.

**Critical assessment:** Candidate I is the existing failed structure in a different
uniform. A field theory is ontologically no different from a constitutive law — it is
a prescription for field evolution, and the prescription is exactly what is underdetermined.
Unless something forces the field equation, this candidate has inherited all the freedom
of the previous candidate.

**Kill criterion:** If no principle forces a unique field equation from the primitive
X constraints, Candidate I dies on contact with the existing analysis.

---

### Candidate II: Configuration-Space Geometry

**Mathematical definition:**
X is not a field value but a geometric structure on the space of possible physical
configurations. Specifically, X is a Riemannian (or pseudo-Riemannian) metric

```
G : C × C → R
```

on the configuration space C of the physical system, where C is the set of all
physically realizable configurations.

The local state of X at a point x is not a value but a local geometry of C at x:
which directions in configuration space are available, how far configurations are
from each other, which paths through C are geodesics.

**What this uniquely determines:** The geometry G determines preferred paths through
configuration space (geodesics). The geodesic equation determines dynamics without
needing a separate field equation. If the metric is uniquely determined by the
primitive constraints, the dynamics are uniquely determined.

**What remains free:** The metric G itself. Unless something forces a specific form
of G from the primitive X constraints, we have traded the freedom of the field
equation for the freedom of the metric. The question becomes: is there a principle
that forces G?

**Critical observation:** This is potentially more constrained than Candidate I,
because metrics must satisfy consistency conditions (positive semi-definiteness,
compatibility with the topology of C, and potentially a specific curvature condition).
A metric is not a free function — it is a tensor with algebraic constraints.

**Simplest spherical system:** For a spherically symmetric physical configuration
(central mass M), the configuration space C reduces to configurations parameterized
by r. The metric on this reduced space is a scalar function G(r). The geodesic
equation on C then produces the effective radial dynamics.

**Key question:** Is there a natural metric on C that is *forced* by the requirement
that X cannot distinguish between physically indistinguishable configurations? This
is the informational content of X: it is the structure through which physical
distinctions propagate. A metric that is forced by this requirement would not be a
free choice.

**Preliminary direction:** If G is defined as the metric of physical distinguishability
(the Fisher information metric, or a natural analogue), it may be uniquely determined
by the physical configuration P. This direction is worth investigating.

**Kill criterion:** Show that no canonical metric on C is forced by the primitive
X constraints. If G remains arbitrary, Candidate II reduces to Candidate I in
disguise.

---

### Candidate III: Transition Relation

**Mathematical definition:**
X is not a field value, not a metric on configuration space, but a *relation* between
possible configurations:

```
R ⊆ C × C
```

where R(A, B) means: configuration A can directly transition to configuration B.

The local state of X is not a value φ(x) or a geometry G, but the current set of
allowed transitions at each point. Physical events do not merely change a field value.
They change the transition relation itself.

**More precisely:** Let C be the space of local physical configurations. The transition
structure at (x, t) is a directed graph Γ(x, t) whose vertices are configurations in
C and whose edges are the permitted transitions.

A trajectory of the physical system is a path through C that only follows permitted
transitions. The primitive X constraints determine which transitions are permitted.

**What this uniquely determines:** If R is determined by the primitive constraints and
R is a sufficiently constrained object (e.g., if it must satisfy local composition
laws), then the radial behavior may be forced. Specifically: if R must be a *partial
order* (transitions compose transitively), or a *groupoid* (transitions can be composed
and inverted), then the structure of R is tightly constrained by algebraic requirements.

**What remains free:** The specific form of R. However, R is a significantly more
constrained object than a field value or a metric, because:
- R must be locally consistent (if A → B and B → C, what is required about A → C?)
- R must be compatible with the physical constraint P
- R may be required to satisfy a locality condition

**Critical advantage over Candidates I and II:** The transition relation R carries
natural information about *time* and *irreversibility*. A field value is atemporal;
a metric is atemporal. But R(A, B) is inherently directional — the arrow matters.
This means Candidate III can naturally encode irreversibility, memory, and the
difference between past and future, without additional assumptions.

**Simplest spherical system:** Around a central mass M, the transition relation R
at radius r defines which X configurations at radius r can transition to which
configurations at radius r + dr. The radial dynamics is exactly the structure of R
as a function of r.

If R(r) is required to satisfy a local composition law — that is, if transitioning
from radius r₁ to r₃ must be consistent with transitioning from r₁ to r₂ to r₃ —
then R(r) must satisfy a functional equation of the form:

```
R(r₁, r₃) = R(r₂, r₃) ∘ R(r₁, r₂)
```

This is a strong constraint. The simplest solution satisfying this composition law
is a one-parameter group or semigroup, which would *force* exponential or power-law
radial dependence — not as a free parameter, but as the unique solution.

**This is the key insight:** If the composition law is primitive (not added by hand),
then α is not a free parameter. It is the exponent of the unique solution to the
composition equation.

**Kill criterion:** Show that the composition law either cannot be primitive (requires
additional assumptions itself), or produces infinitely many solutions (as with
ordinary differential equations). If so, Candidate III reduces to a constrained
version of Candidate I.

---

### Candidate IV: Dynamical Network of Possible Configurations

**Mathematical definition:**
X is a weighted directed graph (possibly infinite) whose:
- Vertices are possible local configurations of the physical system
- Edges represent possible transitions between configurations
- Edge weights represent the relative "accessibility" of transitions

```
N = (V, E, w)
```

where V is a set of configurations, E ⊆ V × V, and w: E → R⁺.

The local X state is not a field value but the current subgraph of N that is
accessible at (x, t). Physical constraint P restricts the accessible subgraph.
X dynamics is the evolution of this accessible subgraph.

**Relationship to Candidate III:** Candidate IV is a discrete, weighted version of
Candidate III. The transition relation R becomes the adjacency structure of N, with
weights replacing binary accessibility.

**What this uniquely determines:** The spectrum of the adjacency or Laplacian matrix
of the accessible subgraph. Physical observables emerge from spectral properties
rather than from field equations.

**Critical structural difference from Candidates I and II:** The network structure
of N is a global object, not a local field. Physical effects arise from the global
connectivity of accessible configurations — not from local field gradients. This
is a fundamentally different causal mechanism.

**What remains free:** The specific network N. However, natural constraints on N may
force its structure:
- Locality: only nearby configurations (in physical space) can be adjacent
- Symmetry: spherical symmetry forces N to have a specific quotient structure
- Scale invariance: if N must be scale-free (which is forced by certain universality
  arguments), the degree distribution is power-law, forcing power-law radial behavior

**Simplest spherical system:** Under spherical symmetry, N reduces to a one-dimensional
network: a weighted graph on the positive real line (parameterized by r). The weight
function w(r) is the accessible transition density at radius r.

If the network must be scale-free (no preferred scale), then w(r) must be a power law:

```
w(r) ∝ r^{-β}
```

for some β. The effective force from this network structure would then be:

```
a(r) ∝ -∇w(r) ∝ r^{-(β+1)}
```

For Newtonian gravity, β = 1. The question is whether β = 1 can be derived from
network primitives or is again a free parameter.

**Potential advantage:** Scale-free networks arise from a *single* mechanism —
preferential attachment or related processes. If the primitive X rule generates
a preferential-attachment dynamic for configuration accessibility, β = 1 may
follow as the unique fixed point.

**Kill criterion:** Show that either no scale-free structure is forced by the primitive
X constraints, or that the specific exponent β remains free even given scale-free
structure.

---

### Summary Table: Four Candidates

| Property | I: Field | II: Config. Geometry | III: Transition Relation | IV: Network |
|----------|----------|---------------------|--------------------------|-------------|
| Fundamental object | φ(x,t) | G on C | R ⊆ C × C | N = (V,E,w) |
| Encodes direction of time? | No | No | Yes | Partially |
| Natural composition law? | No | No | Yes | Partially |
| Algebraic constraints on object | None | Positivity | Composition | Adjacency |
| Freedom before gravity calculated | High | Medium | Low–Medium | Medium |
| Natural path to α = 2 | No | Possible | Possible | Possible |
| Relation to failed candidate | IS the failed candidate | Extension | Genuinely different | Extension |

Candidate I is eliminated on contact. The failed candidate was already a constrained
field theory; returning to the same ontology produces the same freedom.

Candidates II, III, and IV each have mechanisms that might reduce or eliminate the
constitutive freedom. Each requires a specific investigation.

---

## 4. The Criterion for Selecting Among Candidates

### 4.1 The Wrong Criterion

The wrong criterion is:

> Which candidate can reproduce Newtonian gravity with the fewest parameter adjustments?

This is wrong because it allows the correct outcome to guide the ontological choice.
If we select the candidate that reproduces gravity, we have not derived gravity —
we have retrodicted it.

The previous candidate already demonstrated this failure. It can reproduce Newtonian
gravity by choosing α = 2. Choosing α = 2 is not a derivation.

### 4.2 The Right Criterion

The right criterion is:

> Which candidate has the least freedom *before* gravity is calculated?

Formally: let D(C) be the number of independent choices required to completely
specify the dynamics of candidate C, given only the primitive X constraints.

The winner is argmin D(C) over all candidates.

If D(C) = 0 for some candidate — meaning the primitive constraints alone uniquely
determine all dynamical behavior — then gravity is a prediction, not a parameter.

If D(C) > 0 for all candidates, the investigation should continue until a
sub-candidate with D = 0 is found, or until it can be proven that D > 0 is
inevitable (which would constitute a no-go theorem for the entire X program).

### 4.3 Operationalizing the Criterion

To measure D(C) concretely:

**Step 1:** Write down the minimal spherical symmetric X system for candidate C.

**Step 2:** Count the number of free functions and parameters required to specify
the system completely.

**Step 3:** Apply the primitive constraints X1–X4. Count how many degrees of freedom
they eliminate.

**Step 4:** D(C) = (number of free choices after applying primitive constraints).

For the failed candidate (Candidate I):
- Free choices before primitive constraints: field equation, constraint form, metric,
  propagation speed, coupling law = 5+
- Degrees eliminated by X1–X4: 0 (the primitive constraints were satisfied by
  everything)
- D(failed) = 5+

**Target:** Find a candidate with D = 0 or D = 1.

### 4.4 The Additional Requirement: Active Constraints

There is a second requirement, independent of D:

> The primitive constraints must become *active* in the regime being tested.

This is the lesson from the continuation principle failure. The principle "X cannot
terminate" is trivially satisfied for any stationary solution. It contributed nothing
to the gravitational calculation.

A constraint that is trivially satisfied is not a constraint. It is a narrative.

Therefore the second criterion is:

> For each candidate, identify the regime where each primitive constraint becomes
> active — where it actually restricts possible behavior rather than being automatically
> satisfied.

If a primitive constraint is never active in any physically testable regime, it is
not a physical constraint. It is an unfalsifiable hypothesis about a situation that
never occurs.

---

## 5. The Ordinary Gravity Problem vs the Collapse Problem

### 5.1 The Incorrect Unification

The previous candidate implicitly treated ordinary gravity and gravitational collapse
as a single phenomenon, to be explained by a single mechanism (continuation under
constraint).

This was incorrect, and the analysis exposed it. The continuation principle is relevant
for collapse — a situation where the preferred configuration genuinely becomes
unavailable. But ordinary Newtonian gravity, the 1/r² force at large distances from
a moderate mass, does not involve any configuration becoming unavailable. A test
particle at r = 10⁶ m from the Sun is not in any danger of running out of accessible
configurations.

The error was expecting the continuation principle to explain both phenomena.

### 5.2 Two Separate Questions

These are two separate physical questions that require separate mechanisms:

**Question A — Ordinary gravitational configuration:**

> Why does a persistent mass M produce a specific surrounding X geometry that causes
> nearby matter to accelerate inward as 1/r²?

This question does not involve continuation, collapse, or critical thresholds. It is
a question about the *static geometry* that X takes in the presence of a mass. The
answer must produce:

```
M → unique X geometry → a(r) = GM/r²
```

without inserting the inverse square. The mechanism is: mass deforms the X transition
structure, and that deformation is what we call gravity.

**Question B — Critical gravitational configuration:**

> What happens when the X geometry around a mass becomes so constrained that the
> ordinary gravitational mode cannot continue?

This question is where continuation and reorganization are relevant. It is the question
about black holes, event horizons, and the transition between ordinary gravitational
behavior and collapsed states. The answer must produce:

```
X geometry → critical condition → new configuration regime
```

### 5.3 The Previous Failure Location

The previous candidate attempted to derive Question A from the mechanism designed
for Question B. This is why:

1. The continuation principle was trivially satisfied for stationary states (no
   Question B behavior in the Question A regime).

2. The radial geometry α was free (there was no mechanism for Question A at all —
   the machinery was entirely about Question B).

3. The mass coupling g(M) was free (same reason).

### 5.4 What the Next Investigation Must Do

The next investigation must address Questions A and B separately.

For Question A, the candidate formalism must answer:

> What is it about having mass M at the origin that forces the X transition structure
> to take a specific radial form, without any additional constitutive choice?

For Question B, the candidate formalism must answer:

> What condition on the X transition structure constitutes a "critical threshold" in
> the Question B sense, and what reorganization follows?

Question A is the harder and more fundamental problem. It is the question the previous
candidate never even engaged. The mechanism for Question A may have nothing to do
with continuation. It may be a question of geometry, algebra, or invariants — something
about the structure of R or G that is forced by the presence of a configuration we
call "mass."

---

## 6. The Noncommutativity Question

### 6.1 The Origin of the Question

When the fundamental object is a transition relation R(A, B), a natural question
arises about the composition of transitions.

Consider two transitions from configuration A:

```
A → B   (transition T_B)
A → C   (transition T_C)
```

When these transitions are applied in sequence, two orderings are possible:

```
T_C ∘ T_B:  apply T_B first, then T_C
T_B ∘ T_C:  apply T_C first, then T_B
```

If the resulting configurations differ — if

```
(T_C ∘ T_B)(A) ≠ (T_B ∘ T_C)(A)
```

then the transition algebra is *noncommutative*.

### 6.2 Why This Is Interesting

Noncommutativity of transitions is not a hypothesis that needs to be added to X.
It is a property that may or may not follow from the structure of R.

The interesting question is: *does it follow?*

Specifically: if R is defined as the set of configurations accessible from A under
the primitive X constraints, and if two distinct constraint directions are both active
simultaneously, does the order of constraint application matter?

If yes, then the transition algebra is naturally noncommutative, and complex-number
structure may emerge from this noncommutativity — not as an assumption but as a
mathematical consequence.

This matters because quantum mechanics is characterized, at bottom, by noncommutative
transition amplitudes. If X's transition structure is naturally noncommutative, quantum
mechanics may be a consequence of X rather than an additional postulate.

But this is a conclusion that cannot be introduced now. It can only be verified after
the transition algebra of a specific candidate is worked out.

### 6.3 The Legitimate Investigation

The legitimate path to the noncommutativity question is:

**Step 1:** Choose a specific candidate (most naturally Candidate III or IV).

**Step 2:** Define the transition algebra — the set of operations on configurations,
with composition as the product.

**Step 3:** Ask whether this algebra is commutative.

- If always commutative: no noncommutativity. The algebra is classical, and quantum
  behavior (if it exists) must have a different origin.

- If sometimes noncommutative: identify the conditions. What physical situation
  forces the noncommutative regime?

- If necessarily noncommutative: this is the most interesting case. If the primitive
  X constraints force T_B ∘ T_C ≠ T_C ∘ T_B in general, then a representation
  of this algebra requires matrices or operators rather than scalars. Complex numbers
  then emerge as the natural representation field for unitary operators, not as a
  postulate.

### 6.4 Complex Numbers: The Only Legitimate Route

Complex numbers should appear in the X formalism only via the following route:

```
Primitive X constraints
→ Transition algebra is noncommutative
→ Algebra requires operator representation
→ Unitary operators in Hilbert space are the natural representation
→ Complex amplitudes emerge
```

Any other route — adding complex numbers to the field φ, assuming complex-valued
amplitudes, or postulating a wavefunction — is the same mistake as inserting α = 2.
It reproduces a result by assumption rather than deriving it.

### 6.5 Status: Not to Be Investigated Now

The noncommutativity question is important but premature. The current investigation
must first determine whether any candidate can derive ordinary Newtonian gravity
(Question A) without free parameters.

If no candidate can derive ordinary gravity, the noncommutativity question is moot.
If a candidate can derive ordinary gravity, then the transition algebra of that
candidate can be examined for commutativity, and the quantum question can be addressed.

The noncommutativity question is recorded here as a downstream target, not an
immediate task.

---

## 7. Research Directions and Kill Criteria for Each Candidate

### 7.1 Candidate II: Configuration-Space Geometry

**Research direction:**
The key question is whether a natural metric G on the configuration space C can be
forced by the primitive X constraints.

The most promising lead is the *distinguishability metric*: the metric that measures
the distance between two configurations A and B by how physically distinguishable they
are. This is related to Fisher information geometry.

Specifically, if X is the structure through which physical distinctions propagate,
then the natural metric on C is the metric in which distance between A and B equals
the difficulty of distinguishing A from B using local observations. This metric
is not a free choice — it is determined by the physical content of the configurations.

**Research task for Candidate II:**
1. Define the configuration space C for a spherically symmetric mass M.
2. Define distinguishability distance d(A, B) from first principles.
3. Show that d defines a unique metric G on C (or show it does not).
4. Derive the geodesic equation on (C, G).
5. Compute the effective radial force from the geodesic equation.
6. Check whether α = 2 emerges.

**Kill criterion:**
- Kill 1: The distinguishability metric is not uniquely determined by C alone —
  it requires additional structure (e.g., a probability distribution over configurations)
  that is itself a free choice.
- Kill 2: The geodesic equation on (C, G) does not produce a radial force (it produces
  no dynamics, or the dynamics are everywhere trivial).
- Kill 3: The radial force has α ≠ 2 and no principle forces α = 2.

If Candidate II survives all three kills, it is worth pursuing further.

---

### 7.2 Candidate III: Transition Relation

**Research direction:**
The most promising direction is the composition law.

Formally, define R as a category whose:
- Objects are possible X configurations at a point
- Morphisms are permitted transitions between configurations

If R is required to be a *category* (composition is associative and identities exist),
then the algebra of transitions is tightly constrained. If R is required to be a
*groupoid* (every transition has an inverse), the constraint is even tighter.

The spherical case reduces to: what is the unique groupoid structure on the positive
real line R⁺ that is:
(a) locally consistent with the primitive X constraints
(b) compatible with spherical symmetry
(c) compatible with the scale structure of physical space?

**Research task for Candidate III:**
1. Define R formally as a category or groupoid on the space of X configurations.
2. Specialize to spherical symmetry: reduce R to a one-parameter family.
3. Apply the composition law: R(r₁, r₃) = R(r₂, r₃) ∘ R(r₁, r₂).
4. Solve the resulting functional equation for R(r).
5. Derive the effective radial dynamics from R(r).
6. Check whether α = 2 is the unique solution.

**Composition law analysis (preliminary):**
The functional equation

```
R(r₁, r₃) = R(r₂, r₃) ∘ R(r₁, r₂)
```

under spherical symmetry and translation invariance (invariance under r → r + c)
has exponential solutions. Under scale invariance (invariance under r → λr) it
has power-law solutions:

```
R(r₁, r₂) ~ (r₂/r₁)^β
```

The question is whether β = 1 (corresponding to Newtonian gravity, since α = 2β) is
forced by some primitive requirement, or whether β is arbitrary.

A natural constraint: if the transition structure must be *dimensionless* (no preferred
scale is introduced by X itself), then β is the *only* free parameter of the system.
This does not eliminate the freedom, but reduces it from multiple free functions to a
*single exponent*.

If an additional invariance (or uniqueness principle on the groupoid structure) forces
β = 1, α = 2 follows.

**Kill criterion:**
- Kill 1: The composition law does not produce a well-posed functional equation (too
  many solutions, or no solutions).
- Kill 2: The composition law has solutions but the exponent β remains completely free.
- Kill 3: β is forced to a specific value, but that value is not β = 1 (not α = 2).

Kill 3 is the most interesting outcome: it would mean X *does* predict a specific
radial law, but it is not Newtonian gravity. This would be a genuine prediction —
and a genuine test.

---

### 7.3 Candidate IV: Dynamical Network

**Research direction:**
Networks with natural scale-free structure. The question is whether the primitive X
constraints force the accessible configuration network to be scale-free, and if so,
whether the degree distribution exponent is uniquely determined.

**Research task for Candidate IV:**
1. Define the network N for a spherically symmetric mass M.
2. Apply primitive constraints: what do X1–X4 say about the structure of N?
3. Determine whether X1–X4 force scale-free structure.
4. If yes, determine the degree exponent.
5. Derive the effective radial dynamics from the network structure.
6. Check whether α = 2 emerges.

**Kill criterion:**
- Kill 1: X1–X4 do not force scale-free structure. Many network types are compatible.
- Kill 2: X1–X4 force scale-free structure but not a specific exponent.
- Kill 3: Network dynamics do not produce a well-defined radial force law.

---

### 7.4 Priority Order

Based on current analysis, the priority order for investigation is:

**First: Candidate III (Transition Relation)**

Reason: The composition law provides the strongest mechanism for eliminating free
parameters. The functional equation R(r₁, r₃) = R(r₂, r₃) ∘ R(r₁, r₂) is concrete
and solvable. The investigation is mathematically well-posed. This is the candidate
that most naturally encodes the difference between forward and backward in time,
which is relevant to Question A (directional gravity) and Question B (collapse).

**Second: Candidate II (Configuration-Space Geometry)**

Reason: The distinguishability metric direction is physically well-motivated (X is
the structure through which distinctions propagate). Fisher information geometry is
a rich and established mathematical subject. However, it requires additional work to
connect to the primitive X constraints without introducing free choices.

**Third: Candidate IV (Dynamical Network)**

Reason: The network direction is less mathematically immediate. Scale-free behavior
is an interesting property, but its connection to the primitive X constraints is
speculative at this stage.

**Eliminated: Candidate I (Field)**

Reason: Already investigated. The field ontology is the previous failed candidate.
Returning to it does not resolve the problem.

---

## 8. Updated Research Status

### 8.1 Status of Previous Candidate

**Previous candidate:** (q, Ω_X, K_X, projection/continuation) with constitutive freedom

**Verdict:** SUPERSEDED

**Reason:** Mathematically coherent but predictively empty. The constitutive freedom
is not a parameter to be fixed but an ontological gap — the formalism was not
primitive enough to determine the geometry of its own constraint structure.

**What was learned:** The failure was precise and informative:
- "Constraint" and "geometry of constraint" are distinct — the second was missing.
- The continuation principle did not engage the ordinary gravity regime.
- Ordinary gravity and gravitational collapse require separate mechanisms.
- The field ontology cannot eliminate constitutive freedom.
- The transition relation ontology may be able to.

### 8.2 Status of New Investigation

**Current status:** ONTOLOGICAL INVESTIGATION STAGE

**Active candidates:**
| Candidate | Object | Status | Next task |
|-----------|--------|--------|-----------|
| I: Field | φ(x,t) | ELIMINATED | N/A |
| II: Config. Geometry | G on C | ACTIVE — SECOND PRIORITY | Define distinguishability metric |
| III: Transition Relation | R ⊆ C × C | ACTIVE — FIRST PRIORITY | Derive composition law, solve functional equation |
| IV: Network | N = (V,E,w) | ACTIVE — THIRD PRIORITY | Test scale-free forcing |

### 8.3 The Next Artifact

The next research artifact (05) should investigate Candidate III in detail.

Specifically it should attempt:

1. A rigorous definition of R as a category on X configurations.
2. Reduction to spherical symmetry.
3. Application of the composition law as a functional equation.
4. Solution of the functional equation and extraction of the radial profile.
5. Comparison of the derived profile with Newtonian gravity.

The question to be answered by 05:

> Does the composition law, applied to the X transition relation under spherical
> symmetry, force a specific radial exponent — or does the exponent remain free?

If it forces α = 2: Candidate III survives and becomes the primary track.
If it forces α ≠ 2: Candidate III makes a non-Newtonian prediction. This is also
a result — it must be examined to determine if there is a regime where this prediction
is consistent with observation, or whether the prediction is falsified.
If α remains free: Candidate III fails the D criterion and should be abandoned.

### 8.4 Open Questions Carried Forward

The following questions are recorded as open. They are not to be answered prematurely.

**OQ-1:** Can the distinguishability metric on configuration space be defined without
a prior probability measure, and if not, is that measure forced by the X constraints?

**OQ-2:** Is the transition algebra of Candidate III commutative or noncommutative?
(Not to be investigated until ordinary gravity is settled.)

**OQ-3:** Does Candidate III naturally separate Question A (static geometry) from
Question B (collapse)? Or does it require two independent mechanisms?

**OQ-4:** What is the correct definition of "mass" in Candidate III? Is mass the
source of a constraint on R, or is it definable from the structure of R itself?

**OQ-5:** If β = 1 follows from the composition law, does the overall coefficient
reproduce GM (not just the radial dependence), or does G remain a free parameter?

---

## 9. Summary of the Transition

The move from the previous investigation to the current one is not a retreat. It is
a more precise targeting of the same original objective.

The original objective was:

```
microscopic constraint → observable
```

The previous attempt produced:

```
microscopic constraint + constitutive freedom → observable
```

The current investigation asks whether a different ontological choice — specifically,
treating X as a transition relation rather than a field — can eliminate the
constitutive freedom:

```
primitive invariant → unique transition structure → observable
```

If Candidate III succeeds: we have the first genuinely predictive X formalism.
If Candidate III fails: the failure will be informative, exactly as the previous
failure was informative, and will narrow the space of viable candidates further.

The investigation continues.

---

*End of 04_ONTOLOGICAL_CANDIDATES.md*
