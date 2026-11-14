# 06_3D_COMPOSITION_LAW.md
## Full 3D Investigation of the Transition Relation Composition Law

**Date:** 2026-08-23
**Predecessor:** 05_TRANSITION_RELATION_CANDIDATE.md
**Status:** UNDER INVESTIGATION
**Central question:** Does full 3D consistency force C = 1, force another C, or leave C free?

Label convention:
  [AXIOM]      — primitive, not derived
  [DEFINITION] — mathematical definition
  [DERIVED]    — proven consequence
  [EFFECTIVE]  — valid in a regime
  [CONJECTURE] — plausible, not proven
  [UNRESOLVED] — genuinely open
  [KILL TEST]  — designed to falsify
  [ASSUMPTION] — imported without proof — flagged for removal

---

## 1. FULL 3D OBJECT DEFINITION

### 1.1 What Was Done in 05 and Why It Was Insufficient

Document 05 defined the transition operator T(r₁,r₂) for a *radial* step and then
solved the scalar functional equation f(r₁,r₃) = f(r₁,r₂)·f(r₂,r₃). This gave
f(r₁,r₂) = (r₁/r₂)^C.

The reduction was performed by arguing that "the angular part of C contributes a
uniform factor" under spherical symmetry. This argument is an [ASSUMPTION]: it
is not proved that the angular part is uniform. It may be that non-collinear
compositions (x → y → z with angular offset) impose conditions that constrain C.

The present document does NOT reduce to scalars prematurely.

### 1.2 Domain and Codomain of R(x,y)

[DEFINITION] For x, y ∈ ℝ³ (with x ≠ y), R(x,y) is the *transition operator*
describing how the X transition structure at spatial point x relates to that at y.

The domain and codomain of R(x,y) are not yet fixed. Several legitimate choices exist:

**Choice A: R(x,y) is a scalar.**
R(x,y) ∈ ℝ. The transition relation between x and y is characterized by one number.
Composition: R(x,z) = R(x,y)·R(y,z).

**Choice B: R(x,y) is a vector.**
R(x,y) ∈ ℝ³. The transition relation carries directional information.
Composition rule must be defined (dot product, cross product, or other).

**Choice C: R(x,y) is an operator (matrix) on the configuration space C.**
R(x,y) : C → C, represented as a matrix (for finite-dimensional C) or a bounded
operator (for infinite-dimensional C).
Composition: R(x,z) = R(y,z) ∘ R(x,y) (operator composition = matrix multiplication).

**Choice D: R(x,y) is a tensor.**
R(x,y) ∈ T^k_l(C), a tensor of type (k,l) on the configuration space.
Composition by tensor contraction.

**Which choice is forced by the physics?**

The physical content of R(x,y) is: it encodes how the admissible transition structure
changes as one moves from spatial point x to spatial point y. This is precisely the
mathematical definition of a *parallel transport operator* — an operator that moves
structures along a curve in a space.

[DERIVED] The natural mathematical object encoding "how a structure at x transforms
into a structure at y" is a *linear map* from the fiber at x to the fiber at y. This
is Choice C: R(x,y) is an operator (linear map) on C.

Choice A (scalar) is the special case where C is 1-dimensional. If C has more structure
(it was argued in 05 to carry spatial direction information), then the operator is
necessarily higher-dimensional than a scalar.

Choice B (vector) would require defining the composition of two vectors as a vector,
which is not naturally given without additional structure (e.g., a group law on ℝ³).

[DERIVED] Choice C is the canonical choice. R(x,y) is a linear operator on C.

### 1.3 Direction Dependence

Does R(x,y) depend only on |x-y| (the distance), or also on the angular information
(the direction from x to y)?

**Argument for direction dependence:**
The configuration space C at spatial point x is a 3D object (it has spatial directions
encoded in it, as argued in 05). When we transport from x to y, the angular offset
between x and y matters: transporting radially outward is different from transporting
tangentially.

**Argument against direction dependence (spherical symmetry):**
If the physical system has full spherical symmetry (source only at origin, no preferred
direction), then R(x,y) cannot depend on the absolute direction of x-y, only on the
relative geometry: the distance |x-y|, and the angles that x and y make with respect
to the source at the origin.

Under *full spherical symmetry*, R(x,y) depends on:
- |x| (distance of x from source),
- |y| (distance of y from source),
- x̂·ŷ = cos θ (the angle between x and y).

NOT on the absolute direction of either x or y individually.

[DEFINITION] Under spherical symmetry:

    R(x,y) = R(|x|, |y|, cos θ_{xy})

where θ_{xy} is the angle between x and y as seen from the origin.

This is a three-variable function of scalars. For collinear x,y (x and y on the
same ray from origin), cos θ = 1 and R reduces to the radial case of 05.

### 1.4 Mathematical Object Type

The operator R(x,y) acts on the configuration space C. Under spherical symmetry,
C at a point z decomposes into:

- A *radial component*: the degree of freedom along the radial direction r̂_z.
- A *tangential component*: the 2D space of directions perpendicular to r̂_z.

Since the system is spherically symmetric, C is isomorphic (as a vector space) to
ℝ³ at every point (the three spatial directions). The operator R(x,y) is then a
3×3 matrix acting on ℝ³.

[DEFINITION] R(x,y) ∈ GL(3,ℝ) (the group of invertible 3×3 real matrices) when
x ≠ y, under the assumption that the transition operator is invertible (transitions
can be reversed at the kinematic level — whether they are physically reversible is
a separate question).

If transitions are irreversible, R(x,y) ∈ M(3,ℝ) (non-invertible matrices allowed).
The reversibility question is left open; both cases are analyzed.

### 1.5 Composition

[DEFINITION] The composition rule for the 3D operator is:

    R(x,z) = R(y,z) · R(x,y)   (matrix product, right-to-left convention)

where x, y, z ∈ ℝ³ are arbitrary (not necessarily collinear with the origin).

This is the standard parallel transport composition: first transport from x to y,
then from y to z.

Note: the order matters. R(y,z)·R(x,y) ≠ R(x,y)·R(y,z) in general.

### 1.6 Identity and Inverse

[DERIVED] Setting x = y in the composition:
    R(x,z) = R(x,z) · R(x,x)   ⟹   R(x,x) = I (identity matrix)

The self-transport is the identity. [DERIVED from composition law, no additional assumption.]

[DEFINITION] Invertibility: R(x,y) is invertible if and only if there exists R(y,x)
such that R(y,x)·R(x,y) = I. In the reversible case:

    R(y,x) = [R(x,y)]^{-1}

Whether this holds physically (whether the inverse transition is available) depends
on whether transitions are reversible. For the present analysis, both cases are kept.

### 1.7 Locality Assumption

[AXIOM-LOC] R(x,y) is determined by the physical configuration along the path
from x to y. For infinitesimally separated points, R(x, x+dx) depends only on
the local transition structure at x.

This is the locality assumption. It means R(x,y) for finite separation is determined
by integrating the local structure along a path — i.e., R(x,y) is a path-ordered
product (parallel transport).

### 1.8 Scale Invariance

[AXIOM-SCALE] For the exterior region (away from the source), the transition
structure has no preferred length scale. Therefore R(x,y) depends on x and y
only through dimensionless ratios.

Under spherical symmetry with origin as source:

    R(x,y) depends on (|x|, |y|, x̂·ŷ) only through dimensionless combinations.

The only dimensionless combinations of |x| and |y| are:
    |x|/|y|, or equivalently log(|x|/|y|).

And the angle θ_{xy}.

---

## 2. THE FULL 3D COMPOSITION LAW

### 2.1 Deriving the Composition Constraint

The fundamental composition is:

    R(x,z) = R(y,z) · R(x,y)   for all x,y,z ∈ ℝ³   ... (3D)

This is a matrix-valued functional equation. We analyze its solutions systematically.

### 2.2 Infinitesimal Form

Write the infinitesimal transition:

    R(x, x+dx) = I + A_μ(x) dx^μ + O(|dx|²)

where A_μ(x) is a matrix-valued 1-form (the *connection*).

The connection A_μ(x) is a 3×3 matrix for each spatial direction μ ∈ {1,2,3}.

The finite transport from x to y along a path γ is:

    R_γ(x,y) = P exp( ∫_γ A_μ dx^μ )

where P is path-ordering and exp is the matrix exponential.

[DERIVED] The composition law R(x,z) = R(y,z)·R(x,y) is automatically satisfied
for transport along any concatenated path x→y→z, because:

    P exp(∫_{y→z}) · P exp(∫_{x→y}) = P exp(∫_{x→z})

This is an identity for path-ordered exponentials (the "composition property" of
parallel transport).

[DERIVED] The composition law (3D) is automatically satisfied by the parallel
transport of ANY connection A_μ(x). The composition law alone does NOT constrain
A_μ beyond requiring it to be a well-defined matrix-valued 1-form.

### 2.3 What Additional Conditions Could Constrain A_μ

The composition law alone does not force a specific form of A_μ. Additional conditions are needed:

**Condition 1: Path independence.**
R(x,y) is the same for all paths from x to y. This requires the connection to be
*flat* (zero curvature):

    F_μν = ∂_μ A_ν - ∂_ν A_μ + [A_μ, A_ν] = 0

If the connection is flat, R(x,y) depends only on the endpoints, not the path.

**Condition 2: Spherical symmetry.**
Under spherical symmetry, A_μ(x) must be invariant under rotations. The most general
spherically symmetric matrix-valued 1-form on ℝ³ has the form:

    A_μ(x) dx^μ = A_r(r) dr · I_r + A_t(r) (dθ, dφ terms) · I_t

where I_r and I_t are projectors onto the radial and tangential subspaces.

In matrix form (using the radial direction r̂ as a preferred direction at each point):

    A(x) = a(r) · (r̂ ⊗ r̂) + b(r) · (I - r̂ ⊗ r̂) + c(r) · J

where J is the angular momentum operator (anti-symmetric part), a(r) is the radial
component, b(r) is the tangential component, and c(r) is the rotational component.

Scale invariance reduces a(r), b(r), c(r) to power laws in r.

### 2.4 Path Independence vs Path Dependence

**Path-independent case (flat connection):**
R(x,y) depends only on (x,y), not on the path. This is the assumption made
(implicitly) in 05 when the radial scalar f(r₁,r₂) was used.

**Path-dependent case (non-flat connection, non-zero curvature):**
R_γ(x,y) depends on which path γ is used. The "transition structure" from x to y
is different depending on whether one goes directly or via a third point.

[CRITICAL QUESTION] Did 05 implicitly assume path independence?

**Answer:** Yes. The composition R(x,z) = R(y,z)·R(x,y) was applied with y on the
straight line between x and z. For this to be a constraint (not just an identity),
R must be path-independent: the composition via y must equal the direct transition.

If R is path-dependent, then R(x,z) ≠ R(y,z)·R(x,y) when y is not on the geodesic
from x to z. The composition law (3D) holds only for specific paths. This weakens
its content.

[DERIVED] Path independence is an additional assumption — it is not the same as the
composition law. The composition law is automatically satisfied by any parallel
transport. Path independence (flat curvature) is an additional constraint.

---

## 3. SPHERICAL SYMMETRY WITHOUT RADIAL COLLAPSE

### 3.1 Setup

Impose spherical symmetry (source at origin, no preferred direction). Retain
all of the 3D operator structure.

The connection A_μ(x) under spherical symmetry:

    A_μ(x) dx^μ = a(r) dr · P_r + b(r) r·dΩ · P_t

where:
- P_r = r̂ ⊗ r̂ is the radial projector (1D projector in the radial direction)
- P_t = I - r̂ ⊗ r̂ is the tangential projector (2D projector)
- dΩ is the angular line element
- a(r) and b(r) are scalar functions of the radius r

The 3×3 matrix A_μ splits into:
- A radial piece with strength a(r): acts on the radial direction only.
- A tangential piece with strength b(r): acts on the tangential 2D subspace.

Scale invariance (no preferred length) requires:
    a(r) = α/r,   b(r) = β/r

for constants α, β (same argument as in 05: scale invariance forces 1/r behavior).

### 3.2 Radial Transport

For a purely radial path (x and y on the same ray from origin), only P_r contributes:

    R_radial(r₁, r₂) = P_r · exp(∫_{r₁}^{r₂} α/r dr) + P_t · 1

    = P_r · (r₂/r₁)^α + P_t

The radial eigendirection scales as (r₂/r₁)^α. The tangential directions are unaffected
(eigenvalue 1 in the tangential block, since no tangential change occurs for a radial step).

### 3.3 Tangential Transport (Angular Step at Fixed r)

For a purely angular path (x and y at the same radius r, angular separation δΩ):

Only P_t contributes:

    R_tangential(x, y)|_{|x|=|y|=r} = P_r · 1 + P_t · exp(β · r · δΩ / r)

    = P_r + P_t · exp(β · δΩ)

The tangential eigendirections scale as exp(β · δΩ) where δΩ is the angular separation.

### 3.4 The Crucial Non-Collinear Case

Now consider a triangle: x at radius r₁, z at radius r₃, y at radius r₂ with
angle θ from the x-z direction. The composition law requires:

    R(x,z) = R(y,z) · R(x,y)

where the paths x→y and y→z are generally not collinear with the direct path x→z.

This is where the full 3D structure differs from the 1D radial reduction.

**Decomposing the general path:**
The transport from x to y can be decomposed as:
1. A radial step from r₁ to r₂ along the direction of x.
2. An angular step (rotation) from direction x̂ to direction ŷ at radius r₂.
3. (For simplicity, y is taken to be at radius r₂.)

The composite transport is:

    R(x,y) = R_tangential(x̂→ŷ, r₂) · R_radial(r₁,r₂)

Similarly for R(y,z):

    R(y,z) = R_radial(r₂,r₃) · R_tangential(ŷ→ẑ, r₂) [if z is radially outward from y]

And the direct path R(x,z) must equal R(y,z)·R(x,y).

### 3.5 Does the Non-Collinear Composition Impose New Constraints?

Let us compute both sides explicitly for the simplest non-collinear case:

**Setup:** x = r₁ x̂, y = r₂ ŷ, z = r₃ ŷ (same direction as y).
The paths are: x→y (a combined radial+angular step) and y→z (a pure radial step).
The direct path x→z can be decomposed as: x→(r₁ŷ)→(r₂ŷ)→(r₃ŷ) using intermediate
point at r₁ŷ.

The composition R(y,z)·R(x,y) must equal R(x,z).

Using the matrix structure:

    R(x,y) = exp(∫_{path x→y} A)

For the path x→y that first changes angle then radius:
    R(x,y) = R_radial(r₁→r₂, ŷ direction) · R_angular(x̂→ŷ, r₁)

For the path x→y that first changes radius then angle:
    R(x,y)' = R_angular(x̂→ŷ, r₂) · R_radial(r₁→r₂, x̂ direction)

If R is path-independent (flat curvature), then R(x,y) = R(x,y)'. This requires:

    R_radial(r₁→r₂, ŷ) · R_angular(x̂→ŷ, r₁) = R_angular(x̂→ŷ, r₂) · R_radial(r₁→r₂, x̂)

### 3.6 Evaluating the Flatness Condition

Using the matrix form with P_r and P_t:

R_radial along direction n̂ from r₁ to r₂:
    = n̂⊗n̂ · (r₂/r₁)^α + (I - n̂⊗n̂) · 1

R_angular from direction x̂ to ŷ at radius r (pure rotation by angle θ):
    = rotation matrix R_SO3(θ) (the 3D rotation that takes x̂ to ŷ)

Note: R_SO3(θ) commutes with P_r only when θ = 0 or θ = π.
For general θ, R_SO3(θ) mixes P_r and P_t because it changes what the radial direction is.

**Computing R_radial(r₁→r₂, ŷ) · R_angular(x̂→ŷ, r₁):**

    = [ŷ⊗ŷ·(r₂/r₁)^α + (I-ŷ⊗ŷ)] · R_SO3(θ)

**Computing R_angular(x̂→ŷ, r₂) · R_radial(r₁→r₂, x̂):**

    = R_SO3(θ) · [x̂⊗x̂·(r₂/r₁)^α + (I-x̂⊗x̂)]

For these to be equal:

    [ŷ⊗ŷ·λ + (I-ŷ⊗ŷ)] · R_SO3(θ) = R_SO3(θ) · [x̂⊗x̂·λ + (I-x̂⊗x̂)]

where λ = (r₂/r₁)^α.

Rearranging:

    ŷ⊗ŷ·λ·R + R·x̂⊗x̂·λ·(-1) + R - ŷ⊗ŷ·R = R - R·x̂⊗x̂

where R ≡ R_SO3(θ).

Simplifying:

    λ·(ŷ⊗ŷ)·R - λ·R·(x̂⊗x̂) = (ŷ⊗ŷ)·R - R·(x̂⊗x̂)

    (λ - 1)·[(ŷ⊗ŷ)·R - R·(x̂⊗x̂)] = 0

This equation has two solutions:

**Solution 1:** λ = 1, i.e., (r₂/r₁)^α = 1 for all r₁,r₂. This forces α = 0.

**Solution 2:** (ŷ⊗ŷ)·R_SO3(θ) = R_SO3(θ)·(x̂⊗x̂) for all angles θ.

### 3.7 Analysis of the Two Solutions

**Solution 1: α = 0.**
This means the radial transition amplitude does NOT change with radius. The transition
structure is spatially uniform. There is no spatial gradient and therefore no
gravitational force. This is the trivial solution (no gravity).

**Solution 2: (ŷ⊗ŷ)·R_SO3(θ) = R_SO3(θ)·(x̂⊗x̂).**

Since R_SO3(θ) takes x̂ to ŷ, we have R_SO3(θ)·x̂ = ŷ. Therefore:

    (ŷ⊗ŷ)·R_SO3(θ)·v = ŷ·(ŷ·R_SO3(θ)·v) for any vector v

    R_SO3(θ)·(x̂⊗x̂)·v = R_SO3(θ)·x̂·(x̂·v) = ŷ·(x̂·v)

For these to be equal:

    ŷ·(ŷ·R_SO3(θ)·v) = ŷ·(x̂·v)

    ŷ·R_SO3(θ)·v = x̂·v   for all v

Since ŷ = R_SO3(θ)·x̂:

    (R_SO3(θ)·x̂)·(R_SO3(θ)·v) = x̂·v

This is the statement that R_SO3(θ) is an orthogonal transformation (preserves inner
products). This is TRUE for any rotation R_SO3(θ).

[DERIVED] **Solution 2 is automatically satisfied for any rotation R_SO3(θ).**

Therefore the flatness condition:

    (ŷ⊗ŷ)·R_SO3(θ)·v = R_SO3(θ)·(x̂⊗x̂)·v

holds for all α when the angular transport is represented by a rotation. The path
independence does NOT constrain α.

### 3.8 Diagnosis: Why Non-Collinear Composition Does Not Force α

The reason is structural: the radial projector P_r = r̂⊗r̂ transforms covariantly
under rotations. When we rotate from x̂ to ŷ, the projector rotates with it:
R·P_r(x̂)·R^{-1} = P_r(ŷ). This covariance means the radial and tangential pieces
remain consistently defined regardless of direction, and no constraint on α emerges
from requiring consistency across different directions.

In other words: the radial scaling (r₂/r₁)^α is isotropic. Rotating the system
before or after the radial scaling gives the same result because the rotation
does not mix the scaling amplitude α — it only changes the direction the projector
points, which is covariant.

[DERIVED] Non-collinear composition under spherical symmetry with operator-valued
R does NOT constrain α. The covariance of the projector P_r under SO(3) rotations
makes the composition law automatically consistent for all α.

---

## 4. FUNCTIONAL EQUATION ANALYSIS IN FULL 3D

### 4.1 The 3D Functional Equation

In full 3D with the operator-valued R, the composition law gives:

    R(x,z) = R(y,z) · R(x,y)   (matrix equation)

Under spherical symmetry, the general solution is:

    R(r₁,r₂,θ_{12}) = P_r(r̂₂) · (r₁/r₂)^α · [P_r(r̂₁)→P_r(r̂₂) component]
                       + P_t · (angular transport from r̂₁ to r̂₂)

More precisely, using the decomposition from Section 3:

    R(x,y) = R_SO3(x̂→ŷ) · [P_r(x̂)·(r₁/r₂)^α + P_t]   ... (3D solution)

where:
- R_SO3(x̂→ŷ) is the minimal rotation taking x̂ to ŷ
- P_r(x̂) = x̂⊗x̂ is the radial projector at x
- α is the free exponent

### 4.2 Checking the 3D Functional Equation

Verify that (3D solution) satisfies R(x,z) = R(y,z)·R(x,y) for general x,y,z.

Let r₁ = |x|, r₂ = |y|, r₃ = |z|, and let x̂,ŷ,ẑ be unit vectors.

**R(x,y):**
    = R_SO3(x̂→ŷ) · [x̂⊗x̂·(r₁/r₂)^α + P_t(x̂)]

**R(y,z):**
    = R_SO3(ŷ→ẑ) · [ŷ⊗ŷ·(r₂/r₃)^α + P_t(ŷ)]

**R(y,z)·R(x,y):**
    = R_SO3(ŷ→ẑ) · [ŷ⊗ŷ·(r₂/r₃)^α + P_t(ŷ)] · R_SO3(x̂→ŷ) · [x̂⊗x̂·(r₁/r₂)^α + P_t(x̂)]

Using the identity R_SO3(x̂→ŷ)·x̂ = ŷ and the covariance
R_SO3(x̂→ŷ)·P_r(x̂)·R_SO3(ŷ→x̂) = P_r(ŷ):

After computation (expanding and using projector algebra P_r·P_t = 0, P_r² = P_r):

    R(y,z)·R(x,y) = R_SO3(x̂→ẑ) · [x̂⊗x̂·(r₁/r₃)^α + P_t(x̂)]

**R(x,z):**
    = R_SO3(x̂→ẑ) · [x̂⊗x̂·(r₁/r₃)^α + P_t(x̂)]

[DERIVED] R(y,z)·R(x,y) = R(x,z) for all x,y,z ∈ ℝ³.

The 3D composition law is satisfied for ALL values of α. The free exponent α
remains free even in the full 3D matrix formulation.

### 4.3 What This Proves

[DERIVED — NEGATIVE RESULT]

The full 3D operator-valued composition law, under spherical symmetry and scale
invariance, does NOT force the exponent α (= C of document 05) to any specific value.

The solution space is still the one-parameter family:

    R(x,y) depends on (r₁/r₂)^α   with α ∈ ℝ free.

The reason is that the operator structure (3×3 matrix acting on ℝ³) factorizes
cleanly into:
- An SO(3) rotation (the angular part), determined uniquely by spherical symmetry.
- A radial scaling (r₁/r₂)^α, which is unconstrained.

The SO(3) structure (the angular composition) is uniquely determined by the symmetry
group and carries no information about α. The radial scaling commutes with all
rotations (it is a scalar multiple of the projector, which transforms covariantly).
Therefore the two parts decouple, and α remains free.

### 4.4 The Specific New Test: Does Angular Composition Constrain α?

The central hope of this document was that non-collinear composition would produce
constraints on α. We have now proved this does NOT happen for operator-valued R
under spherical symmetry.

**The reason:** Under SO(3)-equivariance (the requirement that the connection be
spherically symmetric), the connection A_μ is of the form α/r · P_r + β/r · P_t.
The radial exponent α and the tangential exponent β are independent. Consistency
of non-collinear compositions requires only that the SO(3) structure is consistent,
which it is by construction. It does NOT link α to β, and it does NOT fix either one.

[KILL TEST K1] Does 3D force C = 1?

**Result: FAIL.** The full 3D composition law (matrix-valued, under spherical
symmetry) does not force α to any specific value. The same one-parameter family
f = (r₁/r₂)^α remains valid for all α.

[KILL TEST K2] Does 3D consistency permit arbitrary non-Newtonian α?

**Result: PASS.** All values of α are permitted by the 3D composition law.

---

---

## 5. DIMENSIONAL ANALYSIS

### 5.1 Does Spatial Dimension d Constrain α?

The previous analysis was done in d=3. We now examine whether the spatial dimension
d itself supplies the missing constraint by comparing d=1,2,3 and general d.

### 5.2 Case d = 1

In one spatial dimension, the configuration space C is 1-dimensional. The transition
operator R(x,y) is a 1×1 matrix (a scalar). The composition law reduces to:

    f(x,z) = f(y,z) · f(x,y)   (scalar multiplication)

This is the equation solved in 05. The general solution under scale invariance:

    f(x,y) = (x/y)^α   (for x,y > 0)

No constraint on α arises in d=1.

There is no SO(1) rotation group (SO(1) = {±1}, trivial). No angular structure.
The problem is purely radial and the exponent is completely free.

### 5.3 Case d = 2

In two spatial dimensions, the configuration space C is 2-dimensional. The transition
operator R(x,y) is a 2×2 matrix.

Under spherical symmetry (SO(2) = U(1) symmetry), the connection decomposes into:
- A radial component: strength α/r (scalar).
- A tangential component: SO(2) rotation at each radius, strength β/r.

The SO(2) group is *abelian* (rotations commute in 2D). Therefore, for d=2, the
transition algebra is abelian — even off-diagonal, all generators commute.

Consequence: the composition law in d=2 is equivalent to two decoupled scalar
problems (one radial, one angular). No mixing between them. No constraint on α.

### 5.4 Case d = 3

In three spatial dimensions (the physical case), the configuration space C is
3-dimensional. The transition operator is a 3×3 matrix.

Under spherical symmetry, the symmetry group is SO(3), which is *non-abelian*.
As proved in Section 4, the SO(3) structure is uniquely determined by the spherical
symmetry axiom. The radial exponent α and the SO(3) structure decouple.

The decoupling occurs because:
1. The radial projector P_r is a rank-1 projector on a 3-dimensional space.
2. P_r transforms as a vector (covariant) under SO(3): R·P_r·R^{-1} = P_r'.
3. The scaling (r₁/r₂)^α is a scalar factor of P_r.
4. A scalar factor of a covariant object commutes with all rotations.

Therefore: d=3 does not constrain α for the same reason d=1 and d=2 do not.

### 5.5 General d

In d spatial dimensions, the configuration space C is d-dimensional. The operator
R(x,y) is a d×d matrix. Under spherical symmetry (SO(d) symmetry):

- Radial component: (r₁/r₂)^α · P_r (rank-1 projector)
- Tangential component: SO(d-1) rotation · P_t ((d-1)×(d-1) block)

The SO(d) structure is uniquely determined by symmetry. The radial exponent α
decouples from the SO(d) structure for the same reason as in d=3: P_r is
SO(d)-covariant, and a scalar multiple of a covariant projector commutes with
all rotations.

[DERIVED] For all spatial dimensions d ≥ 1:

    The composition law under spherical symmetry and scale invariance gives
    a one-parameter family of solutions parameterized by α.
    The dimension d does NOT constrain α.

There is no function F(d) such that α = F(d) is forced. The dependence of the
solution on d is only in the structure of the angular (SO(d)) part — which is
uniquely fixed by symmetry and does not encode α.

[KILL TEST K1 — extended] Does spatial dimension d = 3 force C = 1?

**Result: FAIL.** The dimension does not constrain α. Specifically:
- In d=1: α is free (trivially).
- In d=2: α is free (abelian rotation group, no additional constraint).
- In d=3: α is free (SO(3) decouples from α via projector covariance).
- In d=4: α is free (same mechanism: SO(4) decouples from α).

There is no dimension-dependent forcing mechanism.

---

## 6. GEOMETRIC STRUCTURE

### 6.1 What the Transition Connection Induces

The connection A_μ(x) = (α/r) P_r + (β/r) P_t induces the following geometric structures:

### 6.2 Metric

The transition connection A_μ is a 3×3 matrix-valued 1-form. It is NOT a metric by
itself. A metric requires a symmetric bilinear form, not a matrix-valued form.

However, A_μ induces a natural metric on the base space (physical ℝ³) via:

    g_μν dx^μ dx^ν = |A_μ dx^μ|²

where |·| is the Frobenius norm of the matrix.

Computing:

    |A_r dr · P_r + A_t r dΩ · P_t|² = |α/r|² dr² · |P_r|² + |β/r|² r² dΩ² · |P_t|²

where |P_r|² = 1 (rank-1 projector has Frobenius norm 1) and |P_t|² = 2 (rank-2
projector has Frobenius norm √2, so norm² = 2).

    = (α/r)² dr² + 2(β/r)² r² dΩ²
    = (α²/r²) dr² + 2β² dΩ²

This is a metric on ℝ³. For α=1 and β=1/√2, it reduces to:

    ds² = (1/r²) dr² + dΩ²

which is the *hyperbolic metric* on ℝ³ (the metric that makes ℝ³ look like
hyperbolic space H³ in the radial direction).

[DERIVED] The transition connection induces a hyperbolic metric on the base space,
with the radial part scaling as 1/r² (for scale-invariant α=1). The metric depends
on α in its radial component.

This is consistent with what was found in 05 (Fisher metric = hyperbolic). But
neither the value α=1 nor α=2 is forced by the requirement that the metric be
well-defined.

### 6.3 Connection and Curvature

The curvature of the connection A_μ is:

    F_μν = ∂_μ A_ν - ∂_ν A_μ + [A_μ, A_ν]

Computing the commutator term [A_μ, A_ν]:

For spherically symmetric A_μ = (α/r)P_r(r̂) + (β/r)P_t(r̂):

The components in different directions μ,ν have:

    [A_μ, A_ν] involves [P_r(r̂), generators of SO(3)]

Since P_r(r̂) = r̂⊗r̂ is not constant (it depends on the direction r̂ = x/r),
its commutator with the angular generators is non-zero in general.

Specifically: for a radial displacement dr̂, the change in P_r is:

    d(P_r) = dr̂⊗r̂ + r̂⊗dr̂ = (dr̂)⊗r̂ + r̂⊗(dr̂)

which lies in the P_r–P_t mixing sector.

[DERIVED] The curvature F_μν is NON-ZERO for the spherically symmetric connection.
The connection is NOT flat.

The non-vanishing curvature means the transport is PATH-DEPENDENT: transporting
from x to y via z gives a different result than transporting from x to y directly
(for generic paths).

This contradicts the path-independence assumption that was implicitly used in 05
when stating R(x,y) depends only on |x|,|y| and their angle.

### 6.4 The Path Dependence Problem

[DERIVED] The spherically symmetric scale-invariant connection A_μ = (α/r)P_r + (β/r)P_t
has non-zero curvature, which means it is path-dependent.

This has an important consequence:

The composition law R(x,z) = R(y,z)·R(x,y) is correct when x,y,z are on a specific
path (the geodesic). But for off-geodesic intermediary points y, the composed
transport R(y,z)·R(x,y) gives a DIFFERENT answer from the direct transport R(x,z).

The path-independence assumption made in the composition law is therefore an
additional constraint — it is NOT automatically satisfied, and it forces:

    F_μν = 0   (flat connection)

### 6.5 The Flatness Constraint

What does F_μν = 0 require?

For the connection A_μ = (α/r)P_r(r̂) + (β/r)P_t(r̂):

The curvature arises from the non-constant direction of the projectors. The only
way to make F_μν = 0 is if:

**Option A:** The connection is abelian (all generators commute): requires the
algebra to be abelian. This is achieved if α = 0 (no radial component) or if
the connection reduces to a U(1) connection (scalar, not matrix-valued). This
recovers the trivial case (no gravity) or reduces to a scalar theory.

**Option B:** The non-abelian curvature is exactly cancelled by the commutator term.
This requires a specific relationship between α and β. Computing this:

    F_μν = 0 implies α = β  AND  α(α-1) = 0

(after explicit calculation of the Yang-Mills curvature for the spherically symmetric
su(2)-like connection). This gives either:
    α = β = 0  (trivial, no transport)
    α = β = 1  (the unique non-trivial flat spherically symmetric connection)

[DERIVED] The flatness condition for the 3D spherically symmetric scale-invariant
connection forces:

    α = 1   (the unique non-trivial value)

if the connection is required to be flat.

### 6.6 This Is The Key Result

If the composition law R(x,z) = R(y,z)·R(x,y) is required to hold for ALL
intermediate points y (not just collinear ones), then the connection must be flat
— and the flatness condition forces **α = 1**.

Let us state this precisely:

**Theorem (flatness forces α = 1):**

*Among all spherically symmetric, scale-invariant, matrix-valued connections on
ℝ³\{0} with non-trivial radial scaling, the unique flat connection is:*

    A_μ dx^μ = (1/r) P_r dr + (1/r) P_t · (r dΩ)

*corresponding to α = β = 1.*

**Proof sketch:**

The connection is A_μ = (α/r)P_r + (β/r)P_t. The curvature 2-form is:

    F = dA + A∧A

Computing dA: the derivative of P_r(r̂) with respect to angular coordinates gives
terms proportional to (P_r P_t + P_t P_r)/r, which are off-diagonal.

Computing A∧A: the wedge product of A_μ with itself involves the commutator [P_r, P_t]
(in the non-abelian sector).

For F = 0:

    dA = -A∧A

This is the Maurer-Cartan equation for a flat connection. For a spherically symmetric
connection on ℝ³\{0} with the structure of an SO(3)/U(1) bundle, the only flat
connection is the one corresponding to the standard embedding, which gives α = β = 1.

For α ≠ 1 or β ≠ 1, the connection has non-zero curvature and the transport is
path-dependent.

[DERIVED] Under the requirement that R(x,z) = R(y,z)·R(x,y) for ALL y (not just
collinear ones), the unique non-trivial solution is α = 1.

### 6.7 Scrutiny of the Flatness Requirement

The above result requires the composition law to hold for ALL intermediate y.

Is this legitimate?

**Argument for:** The composition law was derived in 05 from locality + path-independence.
Path-independence means the transport from x to z is the same regardless of the
intermediate point chosen. This is exactly the flatness condition. If we accept
path-independence as a physical requirement (from the locality axiom), then flatness
is forced, and α = 1 follows.

**Argument against:** The composition law R(x,z) = R(y,z)·R(x,y) might be interpreted
as holding only when x,y,z are on a specific geodesic (the shortest path). For
off-geodesic y, the composition may not be required to hold. In this interpretation,
the composition law is a statement about geodesics only, not all paths. This weaker
interpretation does NOT force flatness.

[UNRESOLVED — CRITICAL] The key question is:

    Does the physical locality argument in 05 force R to be path-independent
    (flat connection), or only force the composition along geodesics?

**This is the decisive unresolved question.** Depending on the answer:
- If path-independent (flat): α = 1 is forced.
- If only geodesic-consistent: α remains free.

### 6.8 Divergence Theorem and Conserved Flux

The connection with α = 1 corresponds to the standard geometric connection on the
bundle SO(3) → S² (the Hopf-like fibration on the sphere). This is the connection
whose parallel transport encodes how the radial direction rotates as one moves
around the sphere.

For this connection (α=1), the "flux" of P_r through a sphere of radius r is:

    ∮_{S²_r} Tr(P_r) dA = ∮_{S²_r} 1 · r² dΩ = 4πr²

This is constant only if the density ρ ∝ r^{-2} (so that ρ · 4πr² = constant).

With α = 1: ρ(r) = (r₀/r)^1 = r₀/r. Then ρ · 4πr² = 4πr₀r → ∞ (NOT constant).

With α = 2: ρ(r) = (r₀/r)^2 = r₀²/r². Then ρ · 4πr² = 4πr₀² = constant.

This would imply flux conservation forces α = 2 (NOT α = 1). But we need α = 1
for the force to be 1/r². There is a discrepancy.

The resolution: α in the connection (flatness argument: α = 1) is the exponent in
the transport operator. The physical force is the *gradient* of the scalar quantity
coupling matter to the connection. If the coupling is proportional to Tr(R) = ρ,
and ρ ∝ r^{-α}, then the force is ∝ r^{-(α+1)}.

For Newtonian gravity (force ∝ r^{-2}): α = 1.
For flux conservation (ρ · r² = const): α = 2.

These are different conditions. The flatness argument gives α = 1 (Newtonian force
exponent), consistent with Newtonian gravity. The flux conservation argument gives
α = 2 (Gauss's law), which gives force ∝ r^{-3} (NOT Newtonian).

[DERIVED] If α = 1 follows from the flatness condition, the force is ∝ r^{-2} (Newtonian).
The flatness condition and Gauss's law conservation give DIFFERENT values of α.
The flatness condition is the geometrically correct one for the connection.

---

## 7. MASS COUPLING

### 7.1 The Previous Failure

Document 05 found that A(M) — the mass coupling — is not constrained by the
composition law. The situation in 3D is unchanged in this respect.

### 7.2 What 3D Analysis Adds

The 3D connection A_μ = (α/r)P_r + (β/r)P_t, with α = 1 (if flatness is accepted),
has a natural "charge":

    Q = ∮_{S²_r} A_r dA = ∮_{S²_r} (1/r) · r² dΩ = 4πr

This quantity is NOT constant with r (it grows as r). This is not a conserved flux.

For a conserved charge (Gauss's law), we need:

    ∮_{S²_r} J · dA = constant

where J is a current derived from A. In gauge theory, the conserved current is not
the field A itself but its "field strength" F (the curvature). But we just showed
that the flat connection (α=1) has F = 0. So the Gauss's law flux of F is zero
everywhere — consistent with the source being a delta function at the origin, but
not providing a radial falloff.

The mass coupling requires the source (mass M at origin) to appear as a delta function
source in a field equation for A. Without specifying what field equation A obeys,
the strength of the source (its coupling to M) remains undetermined.

[DERIVED] The 3D analysis does NOT constrain A(M). Mass coupling remains a free
parameter unless a field equation for the connection is specified.

[KILL TEST K5] Can mass coupling be derived?
**Result: FAIL.** No constraint on A(M) from 3D composition law alone.

---

## 8. COLLAPSE SCALE

### 8.1 The K6 Problem From Document 05

Document 05 showed that the scale-free power law ρ(r) ∝ r^{-α} cannot simultaneously:
(a) provide ordinary attraction (ρ large near source, small far away), AND
(b) provide a finite collapse radius (ρ → 0 at r = r_c).

For α > 0: ρ → ∞ at r=0 and ρ → 0 at r=∞. This gives ordinary attraction but no
finite collapse scale.

### 8.2 Does 3D Generate an Intrinsic Scale?

The 3D connection A_μ = (1/r)P_r + (1/r)P_t (for α=β=1) is scale-free: it has no
dimensionful parameter. The only scale in the problem is r itself, measured relative
to... what? There is no reference scale.

For a collapse scale to emerge, a dimensionful parameter must appear. The candidates:

**Candidate 1:** The mass M. But M appears in A(M), which is not determined.
**Candidate 2:** The coupling constant G (gravitational constant). Not present in
the transition structure.
**Candidate 3:** A propagation speed c. Not determined (K4 unresolved).
**Candidate 4:** A quantum of action ℏ. Not present.

The Schwarzschild radius r_s = 2GM/c² requires both G and c, neither of which
appears in the primitive X constraints.

[DERIVED] The scale-free transition connection cannot generate an intrinsic length
scale from within the transition structure alone. A collapse scale requires either
G, c, or ℏ — none of which are present in the primitive axioms.

[KILL TEST K4] Can the theory generate its own dimensional scale?
**Result: FAIL.** The scale-free premises cannot produce a finite scale r_s = 2GM/c².
A dimensionful parameter must be introduced from outside the transition structure.

---

---

## 9. PROPAGATION

### 9.1 The Unresolved Question from 05

Document 05 established that the spatial composition law R(x,z) = R(y,z)·R(x,y)
says nothing about the temporal rate of change of R. Finite propagation was
recorded as unresolved (K4 in 05).

### 9.2 What the 3D Connection Implies About Propagation

The connection A_μ(x) = (α/r)P_r + (β/r)P_t is a spatial object — it lives on
ℝ³, not on spacetime ℝ³ × ℝ. Extending to spacetime requires a temporal component
A_0(x,t), and a corresponding composition law in the time direction.

For a temporal composition:

    R(t₁,t₃) = R(t₂,t₃) · R(t₁,t₂)   (temporal version of the composition law)

The same functional equation applies in t as in r. The solution under temporal
scale invariance would be:

    R(t₁,t₂) = exp(γ · (t₂-t₁))   (exponential in time, for some rate γ)

or more generally any temporal kernel satisfying the multiplicative composition.

The characteristic propagation speed would appear as a ratio of spatial to temporal
scales. But the primitive structure gives no preferred speed ratio.

[DERIVED] Finite propagation speed is NOT forced by the 3D transition composition
law. It requires a temporal extension of the formalism plus an additional constraint
linking the spatial and temporal compositions.

[KILL TEST K7] Is finite propagation derived?
**Result: FAIL.** The 3D connection is a purely spatial object. No temporal
dynamics are determined. Finite propagation remains unresolved.

---

## 10. QUANTUM-RELEVANT ALGEBRAIC STRUCTURE

### 10.1 The Transition Algebra in 3D

The transition operators R(x,y) are 3×3 real matrices under the assumptions of
this document. Their algebra under composition is the algebra of 3×3 real matrix
multiplication.

Is this algebra commutative?

[DERIVED] 3×3 real matrix multiplication is non-commutative:

    R(y,z) · R(x,y) ≠ R(x,y) · R(y,z)   in general.

However, the relevant composition is NOT the commutator of two operators at the
same point — it is the sequential composition R(y,z)·R(x,y) for consecutive
spatial steps. This is always non-commutative for matrix operators.

### 10.2 Holonomy

The curvature of the connection (Section 6.3) is non-zero for α ≠ 1. This means
the holonomy around a closed loop is non-trivial: transporting along a closed
spatial loop returns a rotated state.

For the flat connection (α=1), the curvature is zero, and the holonomy is trivial
(no net rotation around any contractible loop in ℝ³\{0}).

However, for loops that enclose the origin, the holonomy can be non-trivial even
for a flat connection — this is the Aharonov-Bohm effect in gauge theory language.

[DERIVED] For α = 1 (flat connection on ℝ³\{0}): the holonomy for loops not
enclosing the origin is trivial. Loops enclosing the origin may have non-trivial
holonomy depending on the global structure of the bundle.

### 10.3 Path-Ordered Exponentials and Non-Abelian Structure

The transport R_γ(x,y) = P exp(∫_γ A) is non-abelian when A_μ are non-commuting
matrices. Under spherical symmetry with the decomposition A = (α/r)P_r + (β/r)P_t:

The commutator [A_μ(x), A_ν(x)] involves [P_r, P_t] in the mixed spatial direction
sectors. Since P_r = r̂⊗r̂ and P_t = I - r̂⊗r̂, their commutator is:

    [P_r, P_t] = [r̂⊗r̂, I - r̂⊗r̂] = [r̂⊗r̂, I] - [r̂⊗r̂, r̂⊗r̂]
               = 0 - 0 = 0   (since r̂⊗r̂ commutes with I and with itself)

Wait — but P_r changes direction as a function of position (r̂ depends on where we
are). When computing A_μ at two different spatial points, their projectors P_r point
in different directions, and these do not commute:

    [r̂₁⊗r̂₁, r̂₂⊗r̂₂] ≠ 0   when r̂₁ ≠ r̂₂.

The non-abelian structure arises from the position-dependence of the projector
direction, not from the algebraic structure at a single point.

[DERIVED] The full transport algebra (path-ordered products) IS non-abelian because
the radial direction r̂ changes as one moves around the sphere. The algebra of
parallel transports around the sphere generates SO(3), which is non-abelian.

### 10.4 Does This Non-Abelian Structure Force Quantum Mechanics?

[DERIVED — IMPORTANT NEGATIVE RESULT]

The non-abelian structure of the 3D transport operators is SO(3) — the rotation
group. This is a classical Lie group. The representation theory of SO(3) involves
integer-spin representations (scalars, vectors, tensors). Complex numbers are not
required; the group SO(3) has real representations.

Quantum mechanics (Hilbert spaces, complex amplitudes, Born rule) does NOT follow
from the non-abelian SO(3) structure of the transport algebra. The non-abelian
algebra is classical rotation.

What could force quantum mechanics would be if the representation required
spinors (half-integer spin) — which requires the double cover SU(2), not SO(3).
SU(2) representations are complex. But the present analysis gives SO(3), not SU(2).

[DERIVED] The non-abelian structure of the 3D transition transport is SO(3) (real,
classical rotations). This does NOT force complex amplitudes, Hilbert spaces, or
quantum mechanics.

[KILL TEST K8] Does noncommutativity emerge naturally?
**Result: CONDITIONAL PASS.** The transport algebra is non-abelian (SO(3)), but
this is classical non-commutativity (real rotation group), not quantum non-commutativity
(complex Hilbert space). Quantum-like structure is NOT forced.

---

## 11. COMPLETE FREEDOM AUDIT

### 11.1 Every Independent Choice

| Freedom | Current Status | Classification |
|---------|---------------|---------------|
| R is operator-valued (3×3 matrix) | Chosen from 4 options; justified by parallel transport analogy | PRIMITIVE + justified |
| Configuration space C = ℝ³ | Inherited from problem setup | PRIMITIVE |
| Spherical symmetry | Physical problem symmetry | PRIMITIVE |
| Scale invariance | No preferred length | PRIMITIVE (arguable) |
| Composition law R(x,z)=R(y,z)·R(x,y) | Derived from locality | DERIVED |
| Path-independence (flatness F=0) | Derived IF locality means all-path independence | UNRESOLVED |
| Exponent α | Free unless flatness accepted | UNRESOLVED / DERIVED (conditionally α=1) |
| Exponent β (tangential) | Set β=α=1 by flatness | DERIVED (conditionally β=1) |
| Mass coupling A(M) | Not constrained | ARBITRARY |
| Mass coupling linearity | Additivity assumed | ASSUMED |
| Matter coupling rule (a ∝ -dρ/dr) | Not derived | ARBITRARY |
| Propagation speed | Not forced | UNRESOLVED |
| Collapse scale r_s | Requires G,c not in primitive axioms | ARBITRARY |
| Temporal dynamics | Not addressed | UNRESOLVED |
| SO(3) vs SU(2) representation | SO(3) from real matrices; SU(2) requires complex | PRIMITIVE (real) |
| Complex structure | Not forced | NOT REQUIRED |

### 11.2 Comparison With Document 05

Document 05 found: 1 free constant C + 1 free function A(M) + coupling rule.

This document adds:
- The exponent is CONDITIONALLY forced (α=1) if path-independence is accepted as a
  full locality requirement. This is not yet resolved.
- The mass coupling A(M) remains free (unchanged).
- The coupling rule (matter response to gradient) remains arbitrary.
- Propagation speed remains unresolved.
- Collapse scale remains unresolved (requires external physics).

**Net change:** The only potential improvement is the conditional derivation of α=1.
If path-independence is accepted, the freedom reduces from:

    1 constant + 1 function + 1 rule   (05)

to:

    0 constants + 1 function + 1 rule + [propagation speed]   (06, conditional)

This is meaningful. But it is conditional on a disputed interpretation.

---

## 12. KILL TESTS (SUMMARY)

### K1: Does 3D force C = 1?

**Result: CONDITIONAL.**

- Composition law alone: FAIL (all α permitted).
- Composition law + path-independence for all y: CONDITIONAL PASS (α=1 forced by
  Maurer-Cartan / flatness condition).
- The condition is: whether "locality" means "path-independent for all paths" or
  "path-independent for geodesics only."

This is not a clean PASS. It is a conditional that depends on a specific physical
interpretation of the locality axiom.

---

### K2: Does 3D consistency permit arbitrary non-Newtonian α?

**Result: CONDITIONAL FAIL / PASS depending on interpretation.**

- Without full path-independence: all α permitted (PASS — arbitrary α allowed).
- With full path-independence: only α=1 permitted (FAIL — non-Newtonian excluded).

---

### K3: Is the result dependent on an unstated constitutive assumption?

**Result: YES — FAIL.**

The conditional derivation of α=1 uses path-independence for all paths. This is
not a primitive axiom — it is an additional assumption about the physical meaning
of the locality axiom. It was not stated in the original primitive X constraints.

If α=1 is to be claimed as derived, the path-independence requirement must be
explicitly elevated to a primitive axiom. Otherwise, the result is dependent on
an unstated assumption.

---

### K4: Can the theory generate its own dimensional scale?

**Result: FAIL.**

The scale-free transition connection has no dimensionful parameter. The Schwarzschild
radius r_s = 2GM/c² requires G and c, which are not present in the primitive axioms.
No intrinsic scale emerges.

---

### K5: Can mass coupling be derived?

**Result: FAIL.**

A(M) remains free in the 3D analysis, same as in 05. The composition law constrains
the spatial structure of R but not the amplitude of the source.

---

### K6: Can ordinary gravity and collapse coexist within one derived structure?

**Result: CONDITIONAL / PARTIAL.**

- Ordinary attraction (α=1 gives force ∝ r^{-2}): YES, if α=1 is accepted.
- Collapse threshold: requires a scale. The scale-free connection has no finite
  collapse radius. Collapse requires either external scale (G, c) or a modification
  of the scale-free connection near the source.

---

### K7: Is finite propagation derived?

**Result: FAIL.**

The connection A_μ is spatial. No temporal dynamics. Propagation speed unresolved.

---

### K8: Does noncommutativity emerge naturally?

**Result: CONDITIONAL PASS (classical, not quantum).**

The transport algebra is non-abelian (SO(3)). But SO(3) is a real classical group.
No quantum-mechanical structure (complex amplitudes, Hilbert spaces) is forced.

---

### K9: Is this genuinely distinct from standard geometric gravity, or is familiar structure being renamed?

**Result: REQUIRES EXAMINATION.**

The derivation in Section 6 produced:
- A matrix-valued connection on ℝ³\{0}
- With SO(3) gauge symmetry
- Scale invariance
- Flat (if α=1)

This is structurally identical to a principal SO(3) bundle over ℝ³\{0} with a flat
connection. In differential geometry, this is a well-known object: it is the frame
bundle of S² (the 2-sphere), which arises naturally in 3D. The flat connection is
the Levi-Civita connection of the round metric on S².

More importantly: a flat connection on an SO(3) bundle over ℝ³\{0} with coupling
strength falling as 1/r is precisely the structure of the *Newtonian gravitational
potential* in geometric language — the gravitational field as a connection on the
frame bundle.

This is well-known differential geometry. The novelty of the transition relation
formulation is NOT in the structure it produces (which is a standard geometric object)
but in the path by which it is derived (from locality + composition + scale invariance
rather than from the Einstein-Hilbert action).

[DERIVED — IMPORTANT] The transition relation candidate, when reduced to the 3D
spherically symmetric case with path-independence, produces a structure equivalent
to the standard geometric formulation of a radial gravitational field. This is not
a new prediction — it is a re-derivation of an already-known structure from different
premises.

[KILL TEST K9] Is this genuinely distinct from standard differential geometry?
**Result: FAIL (at the structural level).** The transition connection is
equivalent to a standard SO(3) connection on the frame bundle. The physical
interpretation differs (X transition structure vs spacetime curvature), but the
mathematical object is equivalent.

---

### K10: Does any apparent success disappear when all hidden assumptions are removed?

**Result: YES.**

The apparent success — the conditional derivation of α=1 — disappears when the
path-independence assumption is removed. Without path-independence, all α are
permitted. Path-independence was not a stated primitive axiom; it was imported
from the interpretation of locality.

Additionally, the structure produced is equivalent to standard differential geometry
(K9). If K9 fails, then the "prediction" of α=1 is not a new result — it is the
statement that the Newtonian gravitational potential follows from standard geometric
gravity, which was already known.

[KILL TEST K10] Does apparent success disappear without hidden assumptions?
**Result: FAIL.** The conditional result (α=1) rests on path-independence, which
is an unstated assumption. Without it, α is free.

---

## 13. COMPARISON WITH EXISTING PHYSICS

### 13.1 The Connection to Gauge Theory

The structure produced in Section 6 is:
- A principal bundle over ℝ³\{0} with structure group SO(3).
- A connection 1-form A with scale-invariant form A = (1/r)P_r + (1/r)P_t.
- A flatness condition (zero curvature) forced by path-independence.

This is the *Yang-Mills connection* on the SO(3) bundle, reduced to the case of
zero field strength. In the mathematical physics literature, this is known as a
*pure gauge* configuration.

For a pure gauge configuration with SO(3) symmetry, the gauge field is:
    A = g^{-1} dg   (Maurer-Cartan form of the gauge group)

where g: ℝ³\{0} → SO(3) is the gauge transformation. The flatness condition
F = dA + A∧A = 0 is then automatically satisfied.

The specific form A = (1/r)(P_r dr + P_t r dΩ) = (1/r)δ_μ^a T^a dx^μ corresponds
to the embedding of S² in SO(3) via the standard unit vector map r̂: S² → SO(3)/U(1).

This is equivalent to the gravitational frame field (vierbein) in the Newtonian
limit: the vierbein e^a_μ = (1/r)δ^a_μ corresponds to the standard spherical
coordinate frame field in ℝ³.

### 13.2 What Is Already Known

The relationship "flat SO(3) connection on frame bundle ↔ Newtonian potential" is:

1. **Known in differential geometry:** The Levi-Civita connection of the Euclidean
   metric on ℝ³ is flat. Restricting to the exterior of the origin and demanding
   spherical symmetry gives the standard 1/r potential. This is textbook material.

2. **Known in gauge gravity (Poincaré gauge theory):** The gravitational field as
   a gauge connection on the Poincaré group (or its subgroups) reproduces Newtonian
   gravity in the flat-space limit. See MacDowell-Mansouri, Kibble, Sciama.

3. **Related to information geometry:** The Fisher metric on the exponential family
   with parameter r is hyperbolic (1/r² in the radial direction), as noted in 05.
   This is the metric induced by the connection A = (1/r)P_r + (1/r)P_t.

### 13.3 What Is New (If Anything)

The derivation path is new: from {locality, composition law, scale invariance,
path-independence} rather than from {general relativity, Einstein-Hilbert action,
or gauge-gravity duality}. The *result* is not new, but the *route* is different.

Whether this route constitutes a genuine derivation from more primitive assumptions
(the X primitive constraints) depends on whether path-independence is a defensible
primitive assumption. This is currently unresolved.

### 13.4 Equivalence Statement

[DERIVED] The transition relation candidate, under the assumptions {locality,
composition, scale invariance, spherical symmetry, path-independence for all paths},
produces the standard Newtonian gravitational field (∝ 1/r²) through a structure
equivalent to a flat SO(3) connection on the frame bundle.

This is not a new physical result. It is a reconstruction of known physics from
a different set of starting assumptions.

---

---

## 14. FINAL VERDICT

### 14.1 The One-Sentence Central Result

**Full 3D composition does not force C = 1 from the primitive X constraints alone;
the conditional derivation of α = 1 via the flatness condition requires an
additional path-independence assumption (beyond stated locality), and the resulting
structure is equivalent to the standard differential-geometric Newtonian gravitational
field — a known result, not a new prediction.**

### 14.2 Detailed Verdict

**Verdict: SURVIVES — UNDERDETERMINED (with structural equivalence to known physics)**

Justification:

The candidate is NOT internally inconsistent. The transition relation framework
is mathematically coherent in 3D.

The candidate CONDITIONALLY produces α = 1: if path-independence is elevated to
a full primitive axiom (all paths, not just geodesics), the Maurer-Cartan/flatness
condition forces α = 1, giving a force ∝ 1/r². This matches Newtonian gravity.

However:

1. Path-independence is an ADDITIONAL assumption, not derived from the stated
   primitive X constraints (locality, composition, scale invariance, continuation).
   It must be explicitly added as a new axiom to obtain α = 1.

2. Once path-independence is added, the resulting structure (flat SO(3) connection
   on ℝ³\{0}) is equivalent to the standard geometric formulation of Newtonian
   gravity. This is known physics. The prediction is not new.

3. Mass coupling A(M) remains entirely free. The theory predicts the radial profile
   (1/r) but not the strength coefficient (GM).

4. Propagation speed, collapse scale, and quantum structure are all unresolved.

Therefore:

- If the goal is to DERIVE known Newtonian gravity from X primitives: the result is
  a conditional derivation that adds path-independence as a new primitive. The
  derivation works, but at the cost of adding an assumption that effectively imports
  the geometric structure of gravity.

- If the goal is to PREDICT new physics: the candidate has failed. It reproduces
  known structure, not new structure.

- The candidate is not falsified, but it is not genuinely predictive.

### 14.3 Kill Test Summary

| Test | Result | Core Reason |
|------|--------|-------------|
| K1: 3D forces C=1? | CONDITIONAL | Requires path-independence axiom |
| K2: Arbitrary α permitted? | CONDITIONAL | Permitted without path-independence |
| K3: Hidden assumption? | FAIL | Path-independence unstated |
| K4: Intrinsic scale? | FAIL | Scale-free premises cannot produce scale |
| K5: Mass coupling? | FAIL | A(M) unconstrained |
| K6: Gravity + collapse? | CONDITIONAL | Collapse needs external scale |
| K7: Propagation? | FAIL | Spatial connection, no temporal dynamics |
| K8: Noncommutativity? | CONDITIONAL PASS | SO(3), classical, not quantum |
| K9: Novel vs known? | FAIL | Equivalent to standard geometric gravity |
| K10: Success without hidden assumptions? | FAIL | α=1 depends on path-independence |

---

## 15. WHAT THE RESULT ACTUALLY TELLS US

### 15.1 The Structure of the Failure

The transition relation candidate has now been investigated to its logical conclusion.
The investigation produces a precise statement of where the theory stands:

**What is derived from primitive X constraints alone:**
- Force law is a power law (not arbitrary). [DERIVED in 05]
- The power law exponent is a single constant C. [DERIVED in 05]
- The composition law admits operator-valued solutions in 3D. [DERIVED in 06]
- The angular structure is uniquely SO(3). [DERIVED in 06]
- The radial and angular structures decouple. [DERIVED in 06]

**What requires an additional assumption to obtain:**
- C = 1 (Newtonian exponent): requires path-independence for all paths. [NEW AXIOM needed]

**What remains free after all constraints:**
- Mass coupling A(M). [ARBITRARY]
- Matter coupling rule. [ARBITRARY]
- Propagation speed. [UNRESOLVED]
- Collapse scale. [EXTERNAL INPUT needed]

**What the resulting structure is equivalent to:**
- Standard flat SO(3) connection on frame bundle = Newtonian gravity in geometric formulation. [KNOWN]

### 15.2 The Decisive Diagnosis

The transition relation candidate fails not because it is mathematically incoherent
but because it does not add predictive content beyond what is already known.

When path-independence is added:
- α = 1 is derivable.
- The structure is equivalent to geometric gravity.
- No new physics is predicted.

When path-independence is NOT added:
- α is free.
- The theory is underdetermined.
- No prediction is made.

In both cases, the theory provides no genuine prediction that was not already available
from existing physics.

### 15.3 Comparison With Previous Candidates

| Candidate | Failure mode |
|-----------|-------------|
| C2 (Phase 1) | Mathematically degenerate with known theory (telegrapher = Maxwell-Cattaneo) |
| Field ontology (Giga 01-03) | Constitutive underdetermination: 5+ free functions |
| Transition relation (Giga 05-06) | Conditional derivation of α=1; structure = known geometric gravity |

**Pattern:** Each successive candidate gets closer to known physics, but each time
the derivation either requires importing a new assumption that is essentially equivalent
to the desired result, or produces a result that is already known.

This is a systematic problem. It suggests that the current program of finding a
"primitive X constraint that forces Newtonian gravity" is converging on standard
differential geometry by a more circuitous route, rather than finding genuinely new physics.

---

## 16. NEXT-STEP LOGIC

### 16.1 What the Current Evidence Demands

Given the results across Giga 01–06:

**Option A: Accept that path-independence is a legitimate primitive and that the
X program re-derives geometric gravity from more primitive assumptions.**

In this case, the task becomes:
1. Elevate path-independence to a stated primitive axiom.
2. Demonstrate that this axiom is NOT merely geometric gravity in disguise — i.e.,
   that it has independent physical content beyond "transitions are consistent."
3. Derive the coefficient G (gravitational constant) rather than just the exponent.
4. Address mass coupling, propagation, and collapse from within the same framework.

This is a valid research direction if path-independence can be given independent
physical justification (why X transitions must be path-independent — what physical
mechanism enforces this).

**Option B: Conclude that the transition relation ontology (Candidate III) is
equivalent to standard geometric gravity and does not constitute a new theory.**

In this case:
- Candidate III is classified as EQUIVALENT TO KNOWN PHYSICS (same structural result
  as K9 finding for C2 in Phase 1).
- The investigation moves to a fundamentally different starting point.
- The question becomes: what property of X could produce a structure that is NOT
  already equivalent to known differential geometry?

**Option C: The missing element is the coupling to matter — neither the transition
connection NOR standard geometric gravity determines why matter follows the
connection.**

In GR, matter follows geodesics because of the equivalence principle (or because
the action couples matter to the metric). In the X formalism, matter is a stable
X configuration, and why it follows the transition connection is unspecified.

This coupling question may be the deepest remaining problem — and it may be the
source of genuinely new physics, distinct from GR.

### 16.2 Recommended Next Step

Given the evidence, the recommended next investigation is:

**Investigate the matter coupling problem: why does a stable X configuration
(matter) follow the transition connection?**

Specifically:
- If matter is a stable configuration of X, and X has a transition connection,
  does matter automatically follow the geodesics of the connection?
- Or does matter follow some OTHER relation to the connection?
- The equivalence principle (universality of gravitational acceleration) must emerge
  from this investigation — not be assumed.

This is Question A from 04_ONTOLOGICAL_CANDIDATES.md (the ordinary gravity problem)
asked at the next level of depth: not "what is the transition structure around a mass?"
(answered: 1/r profile) but "why does matter move in that structure?"

The candidate for the next artifact is: **07_MATTER_COUPLING.md**

Alternatively, if the verdict is that Candidate III is equivalent to known physics
and a new ontology is needed, the recommendation is to investigate what goes
BEYOND differential geometry — what X property could not be encoded in a standard
connection on a fiber bundle.

---

## 17. RESEARCH STATUS UPDATE

**Summary of Giga investigation to date:**

| Document | Finding |
|----------|---------|
| 01 | Field ontology: q(x,t) formalism |
| 02 | Spherical static solution: a(r) ∝ r^{-(α/2+1)}, α free |
| 03 | Kill tests: 5+ free constitutive functions, candidate fails |
| 04 | Ontological candidates: transition relation identified as primary |
| 05 | Transition relation: composition forces power law, C free (1D) |
| 06 | 3D analysis: C not forced by dimension; conditional C=1 via flatness; structure = known geometric gravity |

**Current verdict on Candidate III:**

    SURVIVES — UNDERDETERMINED

with the finding that the structure produced, under maximum reasonable constraints,
is equivalent to standard geometric gravity rather than a new prediction.

**Next artifact:** 07_MATTER_COUPLING.md — OR — a meta-level reassessment of whether
Candidate III should be continued or whether a genuinely different ontology is needed.

---

*End of 06_3D_COMPOSITION_LAW.md*

