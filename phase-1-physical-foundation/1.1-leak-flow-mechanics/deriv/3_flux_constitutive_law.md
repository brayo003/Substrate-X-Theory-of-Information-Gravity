# 3. Flux Constitutive Law

Information flux describes how information moves through space.

The total flux is modeled as the sum of several mechanisms.

---

## Diffusion

Information spreads from high density to low density.

\[
J_{diff} = -D \nabla s
\]

Where:

D = information diffusivity.

---

## Advection

If the substrate moves with velocity \(v_{sub}\), it carries information with it.

\[
J_{adv} = s v_{sub}
\]

---

## Coherent Transport

Directed propagation of coherent information:

\[
J_{coh} = \chi s u
\]

Where:

| Symbol | Meaning |
|------|------|
| χ | coherence transport speed |
| u | unit direction vector |

---

## Total Flux

Combining all mechanisms:

\[
J = -D\nabla s + s v_{sub} + \chi s u
\]

---

## Substitution into Conservation Law

Using:

\[
\frac{\partial s}{\partial t} + \nabla\cdot J = S
\]

gives:

\[
\frac{\partial s}{\partial t}
=
D\nabla^2 s
-
\nabla\cdot(s v_{sub})
-
\nabla\cdot(\chi s u)
+
S
\]

This is the **diffusion–advection equation for information transport**.
